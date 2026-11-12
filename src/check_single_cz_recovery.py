"""Finite transfer certificates for the one-block simulation recovery profile.

Audits source flags WITH expanded physical H/CX/H Z ports, all two-block
Paulis against the unique-class decoder, commuting histories, passing-round
pigeonhole logic, and both graph decoders. Not a full noisy-circuit audit.
"""
from collections import defaultdict,Counter
from itertools import combinations,product
from math import comb
from pathlib import Path
from hashlib import sha256
import argparse
import json
import c4_helix_single_block_cz as m
from check_optimized_extraction import source_program,signatures,two_scan_certificate
from single_cz_recovery import GRAPHS,H,STABILIZERS,syndrome_component,data_table,cycle_table,clean_reference
from single_cz_controller import SimulationController
from run_single_block_cz_controller import RecordBackend
from simulate_single_block_cz_depolarizing import clean_costs
from check_single_cz_graph_parity import audit as graph_parity_audit
from check_single_cz_flags import audit as flags_audit


def program(blocks,k,axis):
    ops = []
    for name,qs in source_program(blocks,k,axis):
        if name == "CZ":
            ops.extend((("H",(qs[1],)),("CX",qs),("H",(qs[1],))))
        else:
            ops.append((name,qs))
    return ops


def source_audit(blocks,k,axis):
    n = blocks*k
    full = (1 << n)-1
    sigs,locations = signatures(program(blocks,k,axis),range(n),full,(1 << (blocks-1))-1)
    def cost(x,z):
        def occupied(a,b):
            return sum(bool(((a|b) >> (j*k)) & ((1 << k)-1)) for j in range(blocks))
        return min(occupied(x,z),occupied(x ^ full if axis=="X" else x,z ^ full if axis=="Z" else z))
    assert all(flags or cost(x,z)<=1 for x,z,flags in sigs)
    byflag = defaultdict(list)
    for x,z,f in sigs:
        byflag[f].append((x,z))
    pairs = 0
    for group in byflag.values():
        for a,b in product(group,repeat=2):
            assert cost(a[0]^b[0],a[1]^b[1])<=2
            pairs += 1
    return {"blocks":blocks,"ports_per_block":k,"axis":axis,"locations_with_idles":locations,
            "single_signatures":len(sigs),"accepted_pair_signatures":pairs,"physical_Z_decomposition":True}


def actual_source_programs():
    class Recorder(RecordBackend):
        def __init__(self):
            super().__init__();self.context="initial";self.bycontext=defaultdict(list)
        def prepare(self,q):
            self.bycontext[self.context].append(("PREP",(q,)));super().prepare(q)
        def gate(self,name,*qs):
            self.bycontext[self.context].append((name,qs));super().gate(name,*qs)
        def measure_z(self,q):
            self.bycontext[self.context].append(("MZ",(q,)));return super().measure_z(q)
    b = Recorder();c = SimulationController(b,source_extraction="decoded_flags")
    for q in range(20):c.prep(f"D{q}")
    c.source_code("source_program_test")
    checked = 0
    for row in c.record:
        if "source_flag" not in row:continue
        groups = row["block_groups"]
        flat = [q for g in groups for q in g]
        labels = {f"D{q}":j for j,q in enumerate(flat)}
        labels.update({f"L{j}":len(flat)+j for j in range(len(groups))})
        actual = [(name,tuple(labels[q] for q in qs)) for name,qs in b.bycontext[row["source_flag"]]]
        axis = row["source_flag"].split("/")[-2]
        assert actual==program(len(groups),len(groups[0]),axis)
        checked += 1
    assert checked==20
    return checked


def decoder_audit():
    table = data_table()
    tests = accepted = 0
    for blocks in combinations(range(5),2):
        sites = [q for b in blocks for q in range(4*b,4*b+4)]
        words = [sum(((w>>j)&1) << q for j,q in enumerate(sites)) for w in range(256)]
        syndromes = {w:syndrome_component(w) for w in words}
        for x,z in product(words,repeat=2):
            row = table[syndromes[x] | (syndromes[z] << 9)]
            tests += 1
            if row["correction"] is not None:
                a,b = row["correction"]
                assert x^a in STABILIZERS and z^b in STABILIZERS
                accepted += 1
    return {"all_two_block_Paulis":tests,"accepted_occurrences":accepted,
            "syndrome_class_counts":dict(Counter("unambiguous" if v["correction"] is not None else "ambiguous"
                                                 for v in table.values()))}


def equality_patterns(n,prefix=()):
    if not n:yield prefix
    else:
        for v in range(max(prefix,default=-1)+2):
            yield from equality_patterns(n-1,prefix+(v,))


def history_audit():
    patterns = placements = passing = 0
    for pattern in equality_patterns(5):
        patterns += 1
        for n in range(1,6):
            records = [(v,) for v in pattern[:n]]
            cert = clean_reference(records)
            if cert is not None:break
        assert cert is not None
        selected = records[cert["selected"]]
        for k in range(3):
            for bad in combinations(range(n),k):
                if any(records[j]!=records[j+1] and j not in bad and j+1 not in bad for j in range(n-1)):
                    continue
                assert any(row==selected and j not in bad for j,row in enumerate(records))
                placements += 1
    for record in product((False,True),repeat=5):
        if sum(record)<3:continue
        for k in range(3):
            for bad in combinations(range(5),k):
                assert any(ok and j not in bad for j,ok in enumerate(record))
                passing += 1
    return {"equality_patterns":patterns,"compatible_bad_round_placements":placements,
            "passing_round_fault_placements":passing,
            "hypothesis":"adaptive histories only on commuting QND subfamilies; passing rounds may be noncommuting"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parents[1]/"output/single-cz-simulation-certificates.json")
    args=parser.parse_args()
    graph_rows={}
    for g in GRAPHS.values():
        g.validate()
        tested=0
        for eta in range(0,32,2):
            for n in range(g.radius+1):
                for sites in combinations(range(len(g.edges)),n):
                    assert g.decode(g.cut(eta)^m.mask(sites))["eta"]==eta
                    tested+=1
        assert len(cycle_table(g))==sum(comb(len(g.edges),k) for k in range(g.radius+1))
        graph_rows[g.name]={"degrees":[sum(v in e for e in g.edges) for v in range(5)],
                           "edges":len(g.edges),"cycle_rank":len(g.cycles),"cut_distance":g.distance,
                           "decode_radius":g.radius,"readout_sphere_records":tested,
                           "cycle_corrections":len(cycle_table(g)),"gauged_distance":6}
    result={"verified":True,"full_factory_fault_pair_enumeration":False,
            "source_flag_audits":[source_audit(b,k,axis) for b,k in ((1,4),(3,2),(4,2)) for axis in "XZ"],
            "actual_source_gate_lists_matched":actual_source_programs(),
            "cat_two_zero_audits":[two_scan_certificate(n) for n in (2,3,4,5,6,7,8,9,10,12,20)],
            "single_block_decoder":decoder_audit(),"histories":history_audit(),"graphs":graph_rows,
            "graph_parity_verification":graph_parity_audit(),
            "flagged_extraction":flags_audit(),
            "clean_costs":clean_costs()}
    source_dir=Path(__file__).resolve().parent
    result["source_sha256"]={name:sha256((source_dir/name).read_bytes()).hexdigest() for name in
        ("single_cz_controller.py","single_cz_recovery.py","check_optimized_extraction.py",
         "c4_helix_single_block_cz.py","check_single_cz_recovery.py",
         "run_single_block_cz_controller.py","check_single_cz_graph_parity.py",
         "single_cz_flagged.py","check_single_cz_flags.py")}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("clean_costs","cat_two_zero_audits","source_flag_audits")},indent=2))


if __name__=="__main__":main()
