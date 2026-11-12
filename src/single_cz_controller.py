"""Graph-parameterized conservative and recovery profiles for one-block CZ.

Recovery: commuting cat/source/code/cycle histories; unique single-block
two-inner-block error-class recovery; three passing combined gauged rounds
in at most five, then certified terminal recovery. No global commuting-history
assumption for dressed checks. Direct-cat rounds combine code and U checks.
The original documented controller remains unchanged and is the superclass.
"""
import c4_helix_single_block_cz as m
from run_single_block_cz_controller import Controller,Reject
from single_cz_recovery import COMPACT13,clean_reference,data_table,cycle_table
from single_cz_flagged import flagged_program,single_fault_pauli_program,dual_single_fault_pauli_program


class KnownSourceFlag(Exception):
    pass


class DataCheckFlag(Exception):
    def __init__(self, record):
        self.record = record


class RootCheckFlag(Exception):
    def __init__(self,record):self.record=record


class SimulationController(Controller):
    def __init__(self,backend,route="gauging",graph=COMPACT13,profile="recovery",history_policy="triple",
                 source_extraction=None,verification_extraction=None,flag_recovery="reject",max_flag_recoveries=8,
                 graph_stars="flags",terminal_policy="certified",data_checks="rolling_flags",gauss_frame="round_trip",
                 conditional_checks="legacy",root_recovery="reject"):
        super().__init__(backend,route)
        if profile not in ("conservative","recovery"):
            raise ValueError(profile)
        if gauss_frame not in ("round_trip","persistent"):raise ValueError(gauss_frame)
        self.gauss_frame=gauss_frame
        if gauss_frame=="persistent":
            from single_cz_persistent import validate_persistent_graph
            validate_persistent_graph(graph)
        else:graph.validate()
        self.graph_choice,self.profile = graph,profile
        if history_policy not in ("triple","adaptive"):
            raise ValueError(history_policy)
        self.history_policy = history_policy
        self.verification_extraction=verification_extraction or ("flags" if profile=="recovery" else "cats")
        if self.verification_extraction not in ("flags","cats"):
            raise ValueError(self.verification_extraction)
        if profile=="conservative" and self.verification_extraction!="cats":
            raise ValueError("Conservative profile retains documented cat checks")
        default_source="rolling_flags" if self.verification_extraction=="flags" else "decoded_flags"
        self.source_extraction = source_extraction or (default_source if profile == "recovery" else "verified_cat")
        if self.source_extraction not in ("rolling_flags","decoded_flags","verified_cat"):
            raise ValueError(source_extraction)
        if profile == "conservative" and self.source_extraction != "verified_cat":
            raise ValueError("Conservative profile retains documented source gadgets")
        if self.verification_extraction=="flags" and self.source_extraction=="verified_cat":
            raise ValueError("Use rolling_flags or decoded_flags with flag verification")
        if flag_recovery not in ("reject", "data"):
            raise ValueError(flag_recovery)
        if flag_recovery == "data" and (profile != "recovery" or self.verification_extraction != "flags"):
            raise ValueError("Flag-dependent recovery requires recovery profile and flag extraction")
        self.flag_recovery = flag_recovery
        if isinstance(max_flag_recoveries,bool) or not isinstance(max_flag_recoveries,int) or not 1<=max_flag_recoveries<=32:
            raise ValueError("One to 32 bounded flag-recovery episodes required")
        self.max_flag_recoveries = max_flag_recoveries
        self.flag_recoveries = 0
        self.data_epoch = 0
        self._flag_fallback = False
        if graph_stars not in ("flags","bare"):
            raise ValueError(graph_stars)
        if graph_stars=="bare" and (route!="gauging" or profile!="recovery" or self.verification_extraction!="flags"):
            raise ValueError("Bare graph stars require gauging/recovery with flag data/root extraction")
        self.graph_stars=graph_stars
        if terminal_policy not in ("certified","screen","intrinsic"):
            raise ValueError(terminal_policy)
        if terminal_policy=="screen" and (route!="gauging" or profile!="recovery" or self.verification_extraction!="flags"):
            raise ValueError("Terminal screen requires gauging/recovery with flag extraction")
        self.terminal_policy=terminal_policy
        self.terminal_screen_outcome=None
        if data_checks not in ("rolling_flags","compact_flags"):
            raise ValueError(data_checks)
        if data_checks=="compact_flags" and (profile!="recovery" or self.verification_extraction!="flags"):
            raise ValueError("Compact data checks require recovery profile and flag extraction")
        self.data_checks=data_checks
        if conditional_checks not in ("legacy","dual_flags"):raise ValueError(conditional_checks)
        if root_recovery not in ("reject","data","joint"):raise ValueError(root_recovery)
        if (conditional_checks!="legacy" or root_recovery!="reject") and (profile!="recovery" or self.verification_extraction!="flags"):
            raise ValueError("Conditional/root recovery requires recovery profile with flag extraction")
        if root_recovery!="reject" and (gauss_frame!="round_trip" or (root_recovery=="joint" and route!="gauging")):
            raise ValueError("Joint root recovery requires local-Gauss gauging; data-only also supports direct flagged CZ")
        self.conditional_checks=conditional_checks
        self.root_recovery=root_recovery
        self.root_recoveries=0
        if gauss_frame=="persistent":
            if (route!="gauging" or profile!="recovery" or self.verification_extraction!="flags" or
                    graph_stars!="bare" or terminal_policy!="intrinsic"):
                raise ValueError("Persistent coordinates require gauging/recovery, flag extraction, bare stars and intrinsic tail")
        elif terminal_policy=="intrinsic":raise ValueError("Intrinsic tail requires persistent coordinates")

    def reference(self,records):
        if self.history_policy == "adaptive":
            return clean_reference(records)
        if len(records) >= 3 and records[-3:] == [records[-1]]*3:
            return {"selected":len(records)-1,"occurrences":list(range(len(records)-3,len(records))),
                    "kind":"three_identical_complete_records"}
        return None

    @property
    def history_limit(self):
        return 5 if self.history_policy == "adaptive" else 9

    def context(self,name):
        self.b.context = name

    def check(self,name,ports):
        self.context(name)
        ports=tuple(ports)
        if (self.graph_stars=="bare" and "/star/" in name and
                ports and all(axis=="X" and q.startswith("A") for axis,q in ports)):
            from single_cz_graph_stars import bare_star_program
            labels={j:q for j,(axis,q) in enumerate(ports)}
            labels[len(ports)]="s"
            bit=None
            for op,qs in bare_star_program(len(ports)):
                targets=tuple(labels[q] for q in qs)
                if op=="PREP":self.prep(targets[0])
                elif op=="MZ":bit=self.mz(targets[0])
                else:self.gate(op,*targets)
            self.record.append({"check":name,"extraction":"bare_graph_X_star",
                                "axes":[a for a,q in ports],"targets":[q for a,q in ports],
                                "reported_parity":bit})
            return bit
        if self.verification_extraction=="flags":
            if all(axis=="Z" and q.startswith("A") for axis,q in ports):
                self.prep("w")
                for axis,q in ports:self.gate("CX",q,"w")
                bit=self.mz("w")
                self.record.append({"check":name,"extraction":"bare_graph_Z",
                                    "axes":[a for a,q in ports],"targets":[q for a,q in ports],
                                    "reported_parity":bit})
                return bit
            return self.flagged_check(name,ports)
        return super().check(name,ports)

    def flagged_check(self,name,ports):
        axes=tuple(a for a,q in ports);n=len(ports)
        signs=tuple(m.SIGNS[int(q[1:])] if a=="W" else 1 for a,q in ports)
        labels={j:q for j,(a,q) in enumerate(ports)}
        labels[n]="s"
        labels.update({n+1+j:f"f{j%3}" for j in range(n+1)})
        reports=[]
        conditional=(self._flag_fallback and len(set(axes))==1 and axes[0] in ("X","Z") and
                     all(q.startswith("D") for a,q in ports))
        compact=(self.data_checks=="compact_flags" and not conditional and
                 not name.startswith(("source/","terminal_screen/")) and
                 len(set(axes))==1 and axes[0] in ("X","Z") and
                 all(q.startswith("D") for a,q in ports) and
                 tuple(int(q[1:]) for a,q in ports) in m.SUPPORTS)
        if compact:
            from single_cz_compact_checks import compact_pauli_program
            program=compact_pauli_program(axes[0],n)
            labels.update({n+1+j:f"f{j}" for j in range(4)})
        elif self.gauss_frame=="persistent" and name.endswith("/transported_Gauss"):
            from single_cz_persistent import transported_gauss_program
            program=transported_gauss_program(n-20)
        else:
            program=(dual_single_fault_pauli_program(axes[0],n) if self.conditional_checks=="dual_flags" else single_fault_pauli_program(axes[0],n)) if conditional else flagged_program(axes,signs)
        for op,qs in program:
            targets=tuple(labels[q] for q in qs)
            if op=="PREP":
                self.prep(targets[0])
                if (compact or (conditional and self.conditional_checks=="dual_flags")) and axes[0]=="Z" and targets==("s",) and hasattr(self.b,"absorb_parity_helper"):
                    self.b.absorb_parity_helper("s")
            elif op=="MZ":
                reports.append(self.mz(targets[0]))
            else:self.gate(op,*targets)
        flags,bit=reports[:-1],reports[-1]
        transported=self.gauss_frame=="persistent" and name.endswith("/transported_Gauss")
        record={"check":name,"extraction":"transported_Gauss" if transported else "single_fault_flag" if conditional else "compact_flags" if compact else "rolling_flags",
                "axes":list(axes),"targets":[q for a,q in ports],
                "flags":flags,"reported_parity":bit}
        if conditional:record["minimum_spent_faults"]=1
        if conditional:record["conditional_checks"]=self.conditional_checks
        self.record.append(record)
        if any(flags):
            if self.root_recovery!="reject" and (name.endswith("/root_Gauss") or (self.route=="direct_cat" and name.endswith("/U"))):
                raise RootCheckFlag(record)
            if (self.flag_recovery == "data" and not self._flag_fallback and
                    not name.startswith("source/") and len(set(axes)) == 1 and
                    axes[0] in ("X", "Z") and all(q.startswith("D") for a,q in ports) and
                    tuple(int(q[1:]) for a,q in ports) in m.SUPPORTS):
                raise DataCheckFlag(record)
            raise Reject("verification_flag:"+name)
        return bit

    def code(self,prefix,source=False,require_zero=False):
        while True:
            try:
                reports=super().code(prefix,source,require_zero)
                break
            except DataCheckFlag as flag:
                if source:
                    raise Reject("verification_flag:"+flag.record["check"])
                self.recover_data_flag(flag.record)
                # The partial row predates a physical correction. Restart the
                # WHOLE family, including checks preceding the flagged check.
        if hasattr(self.b,"compress_data"):
            self.b.compress_data()  # exact representation only; no quantum operation
        return reports

    def recover_data_flag(self, flagged):
        from single_cz_flag_recovery import decision
        if self.flag_recoveries+self.root_recoveries >= self.max_flag_recoveries:
            raise Reject("flag_recovery_limit")
        number = self.flag_recoveries
        self.flag_recoveries += 1
        flagged["flag_recovery_episode"] = number
        prefix=f"flag_recovery/{number}"
        records=[]
        self._flag_fallback=True
        try:
            for r in range(4):
                records.append(self.code(f"{prefix}/{r}"))
                # A nonzero flag has consumed >=1 of the GLOBAL two faults.
                # Two identical complete QND records therefore contain a clean
                # reference. This conditional bound is not a new fault budget.
                if len(records)>=2 and records[-1]==records[-2]:
                    break
            else:
                raise Reject("unstable_flag_recovery_history")
        finally:
            self._flag_fallback=False
        reference={"kind":"two_identical_after_nonzero_flag", "minimum_spent_faults":1,
                   "selected":len(records)-1,"occurrences":[len(records)-2,len(records)-1]}
        self.record.append({"flag_recovery_history":number,"records":records,
                            "reference":reference,"selected_record":records[-1]})
        support=tuple(int(q[1:]) for q in flagged["targets"])
        flags=sum(b << j for j,b in enumerate(flagged["flags"]))
        extraction=flagged["extraction"]
        row=decision(flagged["axes"][0],support,flags,records[-1],extraction)
        correction=row["correction"]
        self.record.append({"flag_data_recovery":number,"trigger":flagged["check"],
                            "axis":flagged["axes"][0],"support":list(support),"flag_word":flags,
                            "trigger_extraction":extraction,
                            "syndrome":records[-1],"candidate_classes":row["classes"],
                            "correction":list(correction) if correction is not None else None})
        if correction is None:
            raise Reject("flag_data_ambiguity" if row["classes"] else "flag_data_absent")
        self.context(prefix+"/correction")
        self.pauli_correction(*correction,[f"D{q}" for q in range(20)])
        self.data_epoch += 1
        self.record.append({"data_epoch":self.data_epoch,"cause":"flag_data_recovery",
                            "episode":number})

    def recover_root_flag(self,flagged):
        from single_cz_root_recovery import decision
        from single_cz_graph_stars import chord_correction
        if self.flag_recoveries+self.root_recoveries>=self.max_flag_recoveries:raise Reject("flag_recovery_limit")
        number=self.root_recoveries;self.root_recoveries+=1
        flagged["root_recovery_episode"]=number
        graph=self.graph_choice if self.route=="gauging" else None
        if graph:self.coordinates()
        prefix=f"root_recovery/{number}";records=[]
        self._flag_fallback=True
        try:
            for r in range(4):
                data=self.code(f"{prefix}/{r}/code")
                cycles=self.cycle_reports(f"{prefix}/{r}/cycle") if graph else []
                stars=[self.check(f"{prefix}/{r}/star/{v}",[("X",f"A{k}") for k,e in enumerate(graph.edges) if v in e]) for v in range(1,5)] if graph else []
                records.append(data+cycles+stars)
                # All these Paulis commute in V coordinates. No correction
                # is applied between records, and the observed flag spent >=1.
                if len(records)>=2 and records[-1]==records[-2]:break
            else:raise Reject("unstable_root_recovery_history")
        finally:self._flag_fallback=False
        selected=records[-1];nc=len(graph.cycles) if graph else 0
        word=sum(b << j for j,b in enumerate(flagged["flags"]))
        row=decision(graph,word,selected[:18],selected[18:18+nc],self.root_recovery=="joint")
        self.record.append({"root_recovery_history":number,"trigger":flagged["check"],"records":records,
                            "selected_record":selected,"reference":{"kind":"two_identical_after_nonzero_root_flag","minimum_spent_faults":1,
                            "selected":len(records)-1,"occurrences":[len(records)-2,len(records)-1]}})
        self.record.append({"root_data_recovery":number,"flag_word":word,"decoder":self.root_recovery,
                            "decision":row,"syndrome":selected,"trigger":flagged["check"]})
        if row["correction"] is None:raise Reject("root_data_"+row["status"])
        self.context(prefix+"/correction")
        self.pauli_correction(*row["correction"],[f"D{q}" for q in range(20)])
        gx=chord_correction(graph,selected[18:18+nc]) if graph else ()
        gz=[e for bit,e in zip(selected[18+nc:],graph.tree) if bit] if graph else []
        for e in gx:self.gate("X",f"A{e}")
        for e in gz:self.gate("Z",f"A{e}")
        self.record.append({"root_graph_recovery":number,"X_edges":list(gx),"Z_edges":gz,
                            "frame":"V" if graph else "data","faulty_root_vote_discarded":True})
        self.data_epoch+=1
        self.record.append({"data_epoch":self.data_epoch,"cause":"root_flag_recovery","episode":number})

    def acquire(self,name,measure,initial=None):
        records = [] if initial is None else [list(initial)]
        while True:
            cert = self.reference(records) if records else None
            if cert is not None:
                selected = records[cert["selected"]]
                self.record.append({"history":name,"records":records,"reference":cert,"selected_record":selected})
                return selected
            if len(records) == self.history_limit:
                raise Reject("unstable_commuting_history:"+name)
            epoch=self.data_epoch
            row=list(measure(len(records)))
            if self.data_epoch != epoch:
                self.record.append({"history_reset":name,"discarded_records":records,
                                    "old_epoch":epoch,"new_epoch":self.data_epoch})
                records=[]
            records.append(row)

    def cat(self,size,name):
        if self.profile == "conservative":
            return super().cat(size,name)
        leaves = [f"L{j}" for j in range(size)]
        for leaf in leaves:
            self.prep(leaf)
        self.gate("H",leaves[0])
        for j in range(size-1):
            self.gate("CX",leaves[j],leaves[j+1])
        records = []
        while True:
            row = []
            for j in range(size-1):
                self.prep("w")
                self.gate("CX",leaves[j],"w")
                self.gate("CX",leaves[j+1],"w")
                row.append(self.mz("w"))
            records.append(row)
            if len(records) == 2 and not any(any(r) for r in records):
                selected,certificate = row,{"kind":"two_initial_zero_scans"}
                break
            certificate = self.reference(records)
            if certificate is not None:
                selected = records[certificate["selected"]]
                break
            if len(records) == self.history_limit:
                raise Reject("unstable_cat_history")
        pattern,bit = [0],0
        for parity in selected:
            bit ^= parity
            pattern.append(bit)
        for j,bit in enumerate(pattern):
            if bit:
                self.gate("X",leaves[j])
        self.record.append({"cat":name,"flags":records,"repair_pattern":pattern,"reference":certificate})
        return leaves

    def pauli_correction(self,x,z,labels):
        for q,label in enumerate(labels):
            p = ((x >> q)&1) | (((z >> q)&1) << 1)
            if p:
                self.gate({1:"X",2:"Z",3:"Y"}[p],label)

    def source(self):
        self.context("source/raw")
        if self.profile == "conservative":
            return super().source()
        while True:
            self.context("source/raw")
            for q in range(20):
                self.prep(f"D{q}")
            pivots,gates = m.rref_encoder()
            for q in pivots:
                self.gate("H",f"D{q}")
            for a,b in gates:
                self.gate("CX",f"D{a}",f"D{b}")
            self.b.boundary()
            try:
                reports = self.acquire("known_source",lambda r:self.source_code(f"source/certify/{r}"))
            except (KnownSourceFlag,Reject) as exc:
                self.dispose([f"D{q}" for q in range(20)])
                self.retry("known_unused_source:"+str(exc))
                continue
            self.context("source/correction")
            correction = m.source_correction(reports)
            self.pauli_correction(*correction,[f"D{q}" for q in range(20)])
            self.record.append({"known_source_correction":list(correction),"syndrome":reports})
            self.b.boundary()
            return

    def source_code(self,name):
        if self.source_extraction == "rolling_flags":
            reports=[]
            for axis,supports in (("Z",m.SUPPORTS),("X",m.SUPPORTS+(m.X0,m.X1))):
                for j,support in enumerate(supports):
                    suffix=f"{axis}/{j}" if j<9 else f"logical_X/{j-9}"
                    prefix=f"{name}/{suffix}"
                    self.context(prefix)
                    reports.append(self.flagged_check(prefix,[(axis,f"D{q}") for q in support]))
            if hasattr(self.b,"compress_data"):self.b.compress_data()
            return reports
        if self.source_extraction == "verified_cat":
            return self.code(name,source=True)
        reports = []
        for axis,supports in (("Z",m.SUPPORTS),("X",m.SUPPORTS+(m.X0,m.X1))):
            for s,support in enumerate(supports):
                prefix = f"{name}/{axis}/{s}"
                self.context(prefix)
                groups = [[q for q in support if q//4 == v] for v in range(5)]
                groups = [group for group in groups if group]
                assert list(map(len,groups)) in ([4],[2,2,2],[2,2,2,2])
                leaves = [f"L{j}" for j in range(len(groups))]
                for leaf in leaves:
                    self.prep(leaf)
                self.gate("H",leaves[0])
                for leaf in leaves[1:]:
                    self.gate("CX",leaves[0],leaf)
                for port in range(len(groups[0])):
                    for leaf,group in zip(leaves,groups):
                        target = f"D{group[port]}"
                        if axis == "Z":
                            self.gate("H",target)
                        self.gate("CX",leaf,target)
                        if axis == "Z":
                            self.gate("H",target)
                for leaf in reversed(leaves[1:]):
                    self.gate("CX",leaves[0],leaf)
                flags = [self.mz(leaf) for leaf in leaves[1:]]
                self.gate("H",leaves[0])
                report = self.mz(leaves[0])
                self.record.append({"source_flag":prefix,"flags":flags,"reported_parity":report,
                                    "block_groups":groups})
                if any(flags):
                    raise KnownSourceFlag(prefix)
                reports.append(report)
        return reports

    def graph(self):
        self.prepare_parity_verified_graph(self.graph_choice.edges)

    def coordinates(self):
        self.context("coordinates/V")
        for v,e in enumerate(self.graph_choice.tree,1):
            for q in range(4*v,4*v+4):
                self.cw(f"A{e}",q)

    def data_recover(self,name,initial):
        record = self.acquire(name,lambda r:self.code(f"{name}/{r}"),initial)
        self.apply_data_reference(name,record)

    def apply_data_reference(self,name,record):
        s = sum(bit << j for j,bit in enumerate(record))
        row = data_table().get(s)
        correction = row["correction"] if row else None
        details = {"data_recovery":name,"syndrome":record,"candidate_classes":row["classes"] if row else 0,
                   "correction":list(correction) if correction is not None else None}
        self.record.append(details)
        if correction is None:
            raise Reject("data_ambiguity" if row else "data_absent")
        self.context(name+"/correction")
        self.pauli_correction(*correction,[f"D{q}" for q in range(20)])

    def cycle_reports(self,name):
        return self.family(name,[[('Z',f'A{e}') for e in cycle] for cycle in self.graph_choice.cycles])

    def flatten_final_cycles(self):
        from single_cz_graph_stars import chord_correction
        reference=self.acquire("final_cycles",lambda r:self.cycle_reports(f"final_cycles/{r}/cycle"))
        edges=chord_correction(self.graph_choice,reference)
        self.record.append({"final_cycle_flattening":True,"syndrome":reference,"X_edges":list(edges),
                            "correction_support":"non_tree_edges_only"})
        self.context("final_cycles/correction")
        for e in edges:
            self.gate("X",f"A{e}")

    def terminal_screen_syndrome_recovery(self):
        # Match the generic recovery used by the comparator. Only the
        # extra terminal verification stage is optimized in this mode.
        record=self.acquire("terminal_screen_recovery",lambda r:self.code(f"terminal_screen_recovery/{r}"))
        self.apply_data_reference("terminal_screen_recovery",record)

    def terminal_screen_sweep(self,sweep):
        from single_cz_terminal_screen import screen_checks
        order=screen_checks()
        self.record.append({"terminal_screen_begin":True,"sweep":sweep,"version":3,"order":[list(c) for c in order]})
        reports=[]
        for axis,j in order:
            name=f"terminal_screen/{sweep}/{axis}/{j}"
            try:
                bit=self.check(name,[(axis,f"D{q}") for q in m.SUPPORTS[j]])
            except DataCheckFlag as flag:
                self.record.append({"terminal_screen_result":"flag_recovery","sweep":sweep,"trigger":name,
                                    "completed_checks":len(reports)+1,"episode":self.flag_recoveries})
                return "flag_recovery",flag.record
            reports.append(bit)
            if bit:
                self.record.append({"terminal_screen_result":"syndrome_fallback","sweep":sweep,"trigger":name,
                                    "completed_checks":len(reports),"reported_parity":bit})
                return "syndrome_fallback",None
        self.record.append({"terminal_screen_result":"zero_accept","sweep":sweep,"syndrome_reports":reports,
                            "completed_checks":len(order)})
        return "zero_accept",None

    def terminal_screen(self):
        outcome,flag=self.terminal_screen_sweep(0)
        if outcome=="zero_accept":
            self.terminal_screen_outcome="zero_accept"
        elif outcome=="syndrome_fallback":
            self.terminal_screen_syndrome_recovery()
            self.terminal_screen_outcome="syndrome_certified"
        else:
            self.recover_data_flag(flag)
            # A fresh ordered screen checks late errors from the economical
            # conditional recovery. It adds no cost to the clean fast path.
            checked,flag=self.terminal_screen_sweep(1)
            if checked=="zero_accept":
                self.terminal_screen_outcome="flag_verified"
            else:
                if flag is not None:self.recover_data_flag(flag)
                record=self.acquire("terminal_screen_full",lambda r:self.code(f"terminal_screen_full/{r}"))
                self.apply_data_reference("terminal_screen_full",record)
                self.terminal_screen_outcome="full_fallback"
        self.record.append({"terminal_screen_finish":self.terminal_screen_outcome})

    def gauging_persistent(self):
        """One coherent coordinate/ungauging pass, then combined certificates.

        No later coordinate pass or graph-controlled data correction occurs.
        Cycles may remain arbitrary; graph readouts are untrusted disposal.
        """
        self.graph()
        g=self.graph_choice
        from single_cz_persistent import fused_initial_program
        self.context("persistent/fused_initial")
        for op,qs in fused_initial_program(g):self.gate(op,*qs)
        self.record.append({"persistent_coordinates_entered":True,"passes":1,"fused_with_enrichment":True})
        self.context("vertex_readout")
        bits=[]
        for v in range(5):
            self.gate("H",f"a{v}");bits.append(self.mz(f"a{v}"))
        self.record.append({"vertex_reports":bits,"parity_deferred":True})
        self.context("vertex_frame")
        for v,e in enumerate(g.tree,1):
            if bits[v]:self.gate("Z",f"A{e}")
        self.b.boundary()
        passed=0
        for r in range(5):
            reports=self.code(f"persistent/{r}/code")
            if any(reports):self.data_recover(f"persistent/{r}/data_recovery",reports)
            for v,e in enumerate(g.tree,1):
                bit=self.check(f"persistent/{r}/star/{v}",[("X",f"A{k}") for k,ends in enumerate(g.edges) if v in ends])
                if bit:self.gate("Z",f"A{e}")
            root=self.check(f"persistent/{r}/transported_Gauss",[("W",f"D{q}") for q in range(20)]+
                            [("X",f"A{e}") for e,ends in enumerate(g.edges) if 0 in ends])
            passed+=root==0
            self.record.append({"passing_persistent_round":r,"passing":root==0,"passes":passed,
                                "code_zero":not any(reports),"code_recovery_certified":any(reports),"root_report":root})
            self.b.boundary()
            if passed==3:break
            if passed+(4-r)<3:raise Reject("insufficient_positive_persistent_rounds")
        self.context("persistent/discard_graph")
        discarded=[self.mz(f"A{e}") for e in range(len(g.edges))]
        self.record.append({"persistent_graph_discard":True,"untrusted_reports":discarded,
                            "data_byproduct":"already_applied_coherently_by_initial_V","cut_decoding":False})

    def gauging(self):
        self.graph()
        g = self.graph_choice
        self.context("enrichment")
        for q in range(20):
            self.cw(f"a{q//4}",q)
        self.context("vertex_readout")
        bits = []
        for v in range(5):
            self.gate("H",f"a{v}")
            bits.append(self.mz(f"a{v}"))
        self.record.append({"vertex_reports":bits,"parity_deferred":self.profile == "recovery"})
        if self.profile == "conservative" and sum(bits)%2:
            raise Reject("reported_negative_vertex_parity")
        self.context("vertex_frame")
        for v,e in enumerate(g.tree,1):
            if bits[v]:
                self.gate("Z",f"A{e}")
        self.b.boundary()
        passed = 0
        in_coordinates=False
        for r in range(5 if self.profile == "recovery" else 3):
            if not in_coordinates:self.coordinates()
            in_coordinates=True
            reports = self.code(f"gauged/{r}/code",require_zero=self.profile == "conservative")
            code_ok = not any(reports)
            if not code_ok:
                self.data_recover(f"gauged/{r}/data_recovery",reports)
            cycles = self.cycle_reports(f"gauged/{r}/cycle") if self.graph_stars=="flags" else []
            cycles_ok = not any(cycles)
            if not cycles_ok:
                if self.profile == "conservative":
                    raise Reject("nonzero_cycle")
                reference = self.acquire(f"gauged/{r}/cycle_recovery",
                                         lambda k:self.cycle_reports(f"gauged/{r}/cycle_recovery/{k}"),cycles)
                edges = cycle_table(g).get(tuple(reference))
                self.record.append({"cycle_recovery":r,"syndrome":reference,"X_edges":edges})
                if edges is None:
                    raise Reject("cycle_absent")
                self.context(f"gauged/{r}/cycle_correction")
                for e in edges:
                    self.gate("X",f"A{e}")
            for v,e in enumerate(g.tree,1):
                bit = self.check(f"gauged/{r}/star/{v}",[("X",f"A{k}") for k,ends in enumerate(g.edges) if v in ends])
                if bit:
                    self.gate("Z",f"A{e}")
            self.coordinates()
            in_coordinates=False
            root_flag=None
            try:
                root = self.check(f"gauged/{r}/root_Gauss",[("W",f"D{q}") for q in range(4)]+
                                  [("X",f"A{e}") for e,ends in enumerate(g.edges) if 0 in ends])
            except RootCheckFlag as flag:
                self.recover_root_flag(flag.record)
                in_coordinates=True
                root_flag=flag.record["root_recovery_episode"]
                root=flag.record["reported_parity"]
            # A clean round may start with a nonzero syndrome. A certified,
            # unambiguous correction restores its code/graph sector before
            # the root measurement, so that round can also certify magic.
            success = (root_flag is None and root == 0) if self.profile == "recovery" else code_ok and cycles_ok and root == 0
            passed += success
            self.record.append({"passing_gauged_round":r,"code_zero":code_ok,
                                "cycle_zero":cycles_ok if self.graph_stars=="flags" else None,
                                "code_recovery_certified":not code_ok,"cycle_recovery_certified":not cycles_ok,
                                "cycle_policy":"deferred" if self.graph_stars=="bare" else "per_round",
                                "root_report":root,"passing":success,"passes":passed})
            if root_flag is not None:self.record[-1]["root_flag_recovery"]=root_flag
            self.b.boundary()
            if self.profile == "conservative" and root:
                raise Reject("negative_root_Gauss")
            if passed == 3:
                break
            if self.profile == "recovery" and passed+(4-r) < 3:
                raise Reject("insufficient_positive_gauged_rounds")
        if self.graph_stars=="bare":
            self.flatten_final_cycles()
        self.context("edge_readout")
        word = sum(self.mz(f"A{e}") << e for e in range(len(g.edges)))
        decoded = g.decode(word,2 if self.profile == "conservative" else None)
        self.record.append({"edge_reports":word,"decoded":decoded})
        if decoded is None:
            raise Reject("edge_cut_ambiguity_or_outside_radius")
        self.context("byproduct")
        for v in range(1,5):
            if decoded["eta"] >> v & 1:
                for q in range(4*v,4*v+4):
                    self.gate("S" if m.SIGNS[q] == 1 else "SDG",f"D{q}")
                    self.gate("X",f"D{q}")
        self.b.boundary()

    def run(self):
        if self.profile == "conservative":
            return super().run()
        try:
            self.source()
            if self.route == "gauging":
                if self.gauss_frame=="persistent":self.gauging_persistent()
                else:self.gauging()
                if self.terminal_policy=="intrinsic":pass
                elif self.terminal_policy=="screen":
                    self.terminal_screen()
                else:
                    record = self.acquire("terminal_recovery",lambda r:self.code(f"terminal/{r}"))
                    self.apply_data_reference("terminal_recovery",record)
                self.b.boundary()
                assert self.live == {f"D{q}" for q in range(20)}
                return {"accepted":True,"retries":self.retries,"record":self.record,
                        "output_roles":[f"D{q}" for q in range(20)]}
            passed = 0
            for r in range(5):
                reports = self.code(f"terminal/{r}")
                success = not any(reports)
                if not success:
                    self.data_recover(f"terminal/{r}/recovery",reports)
                    success = True
                root_flag=None
                if self.route == "direct_cat":
                    try:success &= self.check(f"terminal/{r}/U",[("W",f"D{q}") for q in range(20)]) == 0
                    except RootCheckFlag as flag:
                        self.recover_root_flag(flag.record)
                        root_flag=flag.record["root_recovery_episode"]
                        success=False
                passed += success
                self.record.append({"passing_terminal_round":r,"passing":bool(success),"passes":passed,
                                    "code_recovery_certified":any(reports)})
                if root_flag is not None:self.record[-1]["root_flag_recovery"]=root_flag
                self.b.boundary()
                if passed == 3:
                    break
                if passed+(4-r) < 3:
                    raise Reject("insufficient_terminal_rounds")
        except Reject as exc:
            self.context("rejected_disposal")
            self.dispose(sorted(self.live))
            return {"accepted":False,"reason":str(exc),"retries":self.retries,"record":self.record}
        assert self.live == {f"D{q}" for q in range(20)}
        return {"accepted":True,"retries":self.retries,"record":self.record,
                "output_roles":[f"D{q}" for q in range(20)]}
