"""Finite isolated-meter fault distinguishability audit; NOT factory acceptance.

One/two faulty locations in one outer meter (including live idles/readouts),
then ideal commuting diagnostics in V coordinates. Current meter parity and
all flag reports are retained. Pauli-basis faults extend coherently by a conservative class-union
criterion. Full factory histories, recovery faults and multiple meters are
outside this certificate.
"""
from pathlib import Path
import argparse,json,sys,time
from collections import Counter
from hashlib import sha256

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"src/single_block_cz"),str(ROOT/"verification/single_block_cz")]
import c4_helix_single_block_cz as m
import single_cz_hybrid_faults as f
import single_cz_recovery as recovery_module
from single_cz_recovery import GRAPHS
from check_single_cz_hybrid_study import choose_basis


def mul(a,b):
    x,z,p=a;y,w,q=b
    return x ^ y,z ^ w,(p+q+2*(z & y).bit_count())%4


class Tableau:
    """Independent signed-Pauli stabilizer representation for reachable witnesses."""
    def __init__(self,generators,n):self.g=list(generators);self.n=n

    def normal(self,error):
        for q,l in enumerate(error.l):
            if l:
                self.g=[(x,z ^ (((x >> q)&1)*(l%2) << q),(p+l*((x >> q)&1))%4) for x,z,p in self.g]
        for q,row in enumerate(error.a):
            for j in f.bits(row & ((1 << q)-1)):
                self.g=[(x,z ^ (((x >> q)&1) << j) ^ (((x >> j)&1) << q),
                         (p+2*((x >> q)&1)*((x >> j)&1))%4) for x,z,p in self.g]
        self.pauli(error.x,0)

    def pauli(self,x,z):
        self.g=[(a,b,(p+2*((a & z).bit_count()+(b & x).bit_count()))%4) for a,b,p in self.g]

    def value(self,obs):
        rows={}
        for gen in self.g:
            row=gen
            while row[0] or row[1]:
                k=(row[0] | (row[1] << self.n)).bit_length()-1
                if k in rows:row=mul(row,rows[k])
                else:rows[k]=row;break
        row=obs
        for k,gen in sorted(rows.items(),reverse=True):
            if (row[0] | (row[1] << self.n)) >> k&1:row=mul(row,gen)
        assert row[0]==row[1]==0 and row[2] in (0,2)
        return row[2]//2

    def measure(self,obs,bit):
        anti=[j for j,(x,z,p) in enumerate(self.g) if ((x & obs[1]).bit_count()+(z & obs[0]).bit_count())%2]
        if not anti:return 0 if self.value(obs)==bit else None
        pivot=anti[0];old=self.g[pivot]
        for j in anti[1:]:self.g[j]=mul(self.g[j],old)
        self.g[pivot]=(obs[0],obs[1],(obs[2]+2*bit)%4)
        return 1 # log2 probability denominator


def initial_stabilizers(graph,n):
    target=[]
    for r in m.SUPPORTS:target.extend([(m.mask(r),0,0),(0,m.mask(r),0)])
    for j in range(2):
        target += [(m.mask((m.X0,m.X1)[j]) | (1 << (n+j)),0,0),
                   (0,m.mask((m.Z0,m.Z1)[j]) | (1 << (n+j)),0)]
    for c in graph.cycles:target.append((0,m.mask(c) << 20,0))
    for v in range(1,5):target.append((sum(1 << (20+e) for e,ends in enumerate(graph.edges) if v in ends),0,0))
    return target


def observables(graph):
    obs=[(0,m.mask(r),0) for r in m.SUPPORTS]+[(m.mask(r),0,0) for r in m.SUPPORTS]
    obs += [(0,m.mask(c) << 20,0) for c in graph.cycles]
    obs += [(sum(1 << (20+e) for e,ends in enumerate(graph.edges) if v in ends),0,0) for v in range(1,5)]
    return obs


def correction(word,graph):
    n=20+len(graph.edges);nc=18+len(graph.cycles)+4
    columns=[f.classword(1 << q,0,graph) for q in range(n)]+[f.classword(0,1 << q,graph) for q in range(n)]
    equations=[(sum(((v >> j)&1) << k for k,v in enumerate(columns)),(word >> j)&1) for j in range(nc+4)]
    result=f.solve_affine(equations,2*n)
    assert result is not None
    p=result[0]
    assert f.classword(p & ((1 << n)-1),p >> n,graph)==word
    return p & ((1 << n)-1),p >> n


def class_map_certificate(graph):
    n=20+len(graph.edges);nc=18+len(graph.cycles)+4
    cols=[f.classword(1 << q,0,graph) for q in range(n)]+[f.classword(0,1 << q,graph) for q in range(n)]
    assert len(f.row_basis(cols))==nc+4
    stabilizers=[]
    for r in m.SUPPORTS:stabilizers += [(m.mask(r),0),(0,m.mask(r))]
    for c in graph.cycles:stabilizers.append((0,m.mask(c) << 20))
    for v in range(1,5):stabilizers.append((sum(1 << (20+e) for e,ends in enumerate(graph.edges) if v in ends),0))
    assert len(f.row_basis(x | (z << n) for x,z in stabilizers))==nc
    assert all(f.classword(x,z,graph)==0 for x,z in stabilizers)
    assert 2*n-(nc+4)==nc
    return dict(pauli_dimension=2*n,class_map_rank=nc+4,stabilizer_kernel_rank=nc)


def physical_witness(error,report,labels,flags,graph,word):
    n=len(labels);np=18+len(graph.cycles)+4;nc=np+1;syndrome=word & ((1 << nc)-1)
    expected=initial_stabilizers(graph,n)
    helper=[(1 << labels.index("s"),0,0)]+[(0,1 << q,0) for q in flags]
    physicalword=(word & ((1 << np)-1)) | ((word >> nc) << np)
    cx,cz=correction(physicalword,graph)
    for actual_meter in (((syndrome >> np)&1) ^ ((report >> len(flags))&1),):
        state=Tableau(expected+helper,n+2);state.normal(error)
        power=0;possible=True
        measurements=[((0,1 << q,0),(error.x >> q)&1) for q in flags]
        measurements += [((1 << labels.index("s"),0,0),actual_meter)]
        measurements += [(obs,(syndrome >> j)&1) for j,obs in enumerate(observables(graph))]
        for obs,b in measurements:
            cost=state.measure(obs,b)
            if cost is None:possible=False;break
            power+=cost
        if possible:
            state.pauli(cx,cz)
            assert all(state.value(p)==0 for p in expected),"Correction failed on encoded logical Bell pairs"
            return dict(probability=f"1/{1 << power}",actual_meter_X_bit=actual_meter,
                        correction_X_sites=[labels[q] for q in f.bits(cx)],correction_Z_sites=[labels[q] for q in f.bits(cz)],
                        restored_encoded_Bell_pairs_and_graph=True)
    return None


def outside_envelope(events,labels,flags,graph):
    """Conditional ONE outside target fault, before IDEAL diagnostic readout.

    An explicit conservative assumption, not a certificate for the full new
    factory: arbitrary one-block action correlated with its tree edge, plus
    unflagged direct-Gauss block/star hooks. Graph Z and current meter sign
    are unrestricted. Only nonzero current-gadget flags use this extension.
    """
    nphys=18+len(graph.cycles)+4;nc=nphys+1;ncoarse=18+len(graph.cycles)+1
    cycle=lambda x:sum(((x & m.mask(c)).bit_count()%2) << j for j,c in enumerate(graph.cycles))
    cases={(None,0)} | {(v,0) for v in range(5)}
    cases |= {(v,cycle(1 << e)) for v,e in enumerate(graph.tree,1)}
    cases |= {(None,cycle(1 << e)) for e in range(len(graph.edges))}
    for v in range(1,5):
        edges=[e for e,ends in enumerate(graph.edges) if v in ends]
        for j in range(len(edges)+1):
            cases.add((v,cycle(m.mask(edges[j:]))))
            cases.add((None,cycle(m.mask(edges[j:]))))
    def augment(word):return (word & ((1 << nphys)-1)) | ((word >> nphys) << nc)
    def coarse(word):
        return (word & ((1 << (ncoarse-1))-1)) | (((word >> nphys)&1) << (ncoarse-1)) | ((word >> nc) << ncoarse)
    spaces=set()
    for event in events:
        (flag,base,rows),_=f.class_image(event['error'],event['report'],labels,flags,graph)
        if not flag:continue
        for block,cyc in cases:
            gens=list(rows)+[1 << nphys]
            if block is not None:
                for q in range(4*block,4*block+4):
                    gens += [augment(f.classword(1 << q,0,graph)),augment(f.classword(0,1 << q,graph))]
            generators=f.row_basis(coarse(g) for g in gens)
            origin=f.reduce_word(coarse(base ^ (cyc << 18)),generators)
            spaces.add((flag,origin,generators))
    table={};mask=(1 << ncoarse)-1
    for flag,base,rows in spaces:
        for word in f.image_words(base,rows):
            key=(flag,word & mask);table[key]=table.get(key,0) | (1 << (word >> ncoarse))
    data={}
    for (flag,s),values in table.items():
        key=(flag,(s & ((1 << 18)-1)) | (((s >> (ncoarse-1))&1) << 18))
        data[key]=data.get(key,0) | values
    return table,data,dict(typed_cases=len(cases),affine_class_images=len(spaces),coarse_report_queries=len(table),
                           scope='one current flagged-gadget fault plus one assumed block/edge/Gauss-cone target fault; ideal final diagnostics')


def audit(ds,graph,route,max_faults,include_outside=False):
    start=time.time();events,locations,labels,flags=f.enumerate_faults(ds,graph,route)
    nphys=18+len(graph.cycles)+4;nc=nphys+1;mask=(1 << nc)-1
    zero=f.Quadratic.pauli(len(labels),[])
    normals={(zero.key,0):(zero,0,[])}
    def remember(error,report,locations_witness):
        key=(error.key,report)
        if key not in normals or f.provenance_score(locations_witness)<f.provenance_score(normals[key][2]):
            normals[key]=(error,report,locations_witness)
    for e in events:remember(e['error'],e['report'],[e['noise_first'] or e['witness']])
    if max_faults==2:
        for i,left in enumerate(events):
            for right in events[i:]:
                orders=[]
                if left['first']<right['last']:orders.append((left,right))
                if left is not right and right['first']<left['last']:orders.append((right,left))
                for early,late in orders:
                    error=late['error'].after(early['error']);report=early['report'] ^ late['report']
                    first,last=early['noise_first'],late['noise_last']
                    locations_witness=([first,last] if first is not None and last is not None and first['location']<last['location']
                                       else [early['witness'],late['last_witness']])
                    remember(error,report,locations_witness)
    print(route,'normal forms',len(normals),flush=True)
    images={}
    for error,report,witness in normals.values():
        image,_=f.class_image(error,report,labels,flags,graph)
        if image not in images or f.provenance_score(witness)<f.provenance_score(images[image][2]):images[image]=(error,report,witness)
    full={}
    for flag,origin,rows in images:
        for word in f.image_words(origin,rows):
            key=(flag,word & mask);full[key]=full.get(key,0) | (1 << (word >> nc))
    data={};cycles={}
    project=lambda s,n:(s & ((1 << n)-1)) | (((s >> nphys)&1) << n)
    for (flag,s),values in full.items():
        for table,n in ((data,18),(cycles,18+len(graph.cycles))):
            key=(flag,project(s,n));table[key]=table.get(key,0) | values
    unique=lambda values:bool(values) and not values & (values-1)
    def stats(flagged):
        rows=[(flag,s,values) for (flag,s),values in full.items() if bool(flag)==flagged]
        d=sum(unique(data[flag,project(s,18)]) for flag,s,v in rows)
        c=sum(unique(cycles[flag,project(s,18+len(graph.cycles))]) for flag,s,v in rows)
        j=sum(unique(v) for flag,s,v in rows)
        return dict(full_report_queries=len(rows),unique_with_data=d,unique_with_cycles=c,unique_with_cycles_and_stars=j,
                    gained_by_cycles=c-d,gained_by_stars=j-c,ambiguous_even_with_graph=len(rows)-j)
    envelope_stats=None
    if include_outside:
        assert max_faults==2
        outside,outsidedata,envelope_stats=outside_envelope(events,labels,flags,graph)
        d=c=j=count=0
        for (flag,s),values in full.items():
            if not flag:continue
            dk=(flag,project(s,18));ck=(flag,project(s,18+len(graph.cycles)))
            dv=data[dk] | outsidedata.get(dk,0);cv=cycles[ck] | outside.get(ck,0);jv=values | outside.get(ck,0)
            d+=unique(dv);c+=unique(cv);j+=unique(jv);count+=1
        envelope_stats.update(full_internal_report_queries_scored=count,unique_with_data=d,
                              unique_with_cycles=c,unique_with_cycles_and_stars=j,
                              gained_by_cycles=c-d,gained_by_stars=j-c,ambiguous_even_with_graph=count-j,
                              outside_only_report_queries_not_scored=True)
    witnesses=[]
    for (flag,origin,rows),(error,report,locations_witness) in sorted(images.items(),key=lambda item:f.provenance_score(item[1][2])):
        if not flag:continue
        for word in f.image_words(origin,rows):
            s=word & mask;v=full[flag,s];blind=data[flag,project(s,18)]
            if include_outside:
                v |= outside.get((flag,project(s,18+len(graph.cycles))),0)
                blind |= outsidedata.get((flag,project(s,18)),0)
            if unique(v) and not unique(blind):
                physical=physical_witness(error,report,labels,flags,graph,word)
                if physical:
                    witnesses.append(dict(faults=locations_witness,reported_flags=flag,diagnostic_syndrome=s & ((1 << nphys)-1),
                                          reported_meter_bit=(s >> nphys)&1,
                                          faults_have_nonzero_gate_report_noise_weight=all(f.gate_report_noise_event(e) for e in locations_witness),
                                          unique_under_assumed_outside_envelope=include_outside,
                                          data_only_logical_classes=[j for j in range(16) if blind >> j&1],
                                          joint_logical_class=v.bit_length()-1,physical=physical))
                    break
        if len(witnesses)>=3:break
    clean=full.get((0,0),0)
    assert clean==1,"A clean-looking record admits a nontrivial logical class"
    # Seek two ACTUAL Pauli histories, not merely two terms of one coherent
    # operator. This distinguishes a real information ambiguity from a
    # conservative Pauli-span rejection that a Clifford correction might fix.
    seen={};ambiguity=None;target_n=20+len(graph.edges);retained=(1 << (target_n+1))-1
    for error,report,provenance in sorted(normals.values(),key=lambda item:f.provenance_score(item[2])):
        if not provenance or any(error.l[q]%2 or (error.a[q] & retained) for q in range(target_n)):continue
        (flag,base,rows),_=f.class_image(error,report,labels,flags,graph)
        if flag:continue
        for word in f.image_words(base,rows):
            s=word & mask;key=(flag,s);label=word >> nc
            if unique(full[key]):continue
            if key not in seen:seen[key]=(label,error,report,provenance,word);continue
            old,other,otherreport,otherprovenance,otherword=seen[key]
            if old==label:continue
            a=physical_witness(other,otherreport,labels,flags,graph,otherword)
            b=physical_witness(error,report,labels,flags,graph,word)
            if a and b:
                ambiguity=dict(reported_flags=flag,diagnostic_syndrome=s & ((1 << nphys)-1),reported_meter_bit=(s >> nphys)&1,
                               histories=[dict(logical_class=old,faults=otherprovenance,physical=a),
                                          dict(logical_class=label,faults=provenance,physical=b)],
                               distinct_actual_Pauli_histories=True)
                break
        if ambiguity:break
    result=dict(route=route,max_faulty_locations=max_faults,locations=locations,distinct_one_two_fault_normal_forms=len(normals),
                distinct_affine_class_images=len(images),unflagged=stats(False),flagged=stats(True),
                clean_zero_record_logical_classes=[j for j in range(16) if clean >> j&1],
                graph_information_witnesses=witnesses,remaining_Pauli_ambiguity_witness=ambiguity,
                assumed_outside_envelope=envelope_stats,elapsed_seconds=time.time()-start)
    f.phase_class_image.cache_clear();f.classword.cache_clear()
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--max-faults',type=int,choices=(1,2),default=2)
    p.add_argument('--checks',default='5,6,7,8')
    p.add_argument('--routes',default='hybrid,reference')
    p.add_argument('--graph',choices=tuple(GRAPHS),default='compact13')
    p.add_argument('--outside-envelope',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'output/single-cz-hybrid-fault-distinguishability.json')
    a=p.parse_args();graph=GRAPHS[a.graph];supports,basis=choose_basis()
    sourcepaths=[Path(__file__),Path(f.__file__),Path(f.h.__file__),Path(m.__file__),Path(recovery_module.__file__),
                 Path(choose_basis.__code__.co_filename),Path(f.compact_pauli_program.__code__.co_filename)]
    sourcehashes={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in sourcepaths}
    checks=[int(s) for s in a.checks.split(',')];routes=a.routes.split(',')
    if any(s not in range(5,9) for s in checks) or any(r not in ('hybrid','hybrid_two_flags','reference') for r in routes):p.error('Invalid checks/routes')
    if a.outside_envelope and a.max_faults!=2:p.error('Outside envelope requires global budget two')
    result=dict(scope='isolated outer meters followed by ideal commuting diagnostics; NOT full factory acceptance',
                arbitrary_local_fault_extension='Pauli expansion with coherent quadratic phases and conservative post-diagnostic logical class unions',
                diagnostic_faults_included=False,multiple_outer_meters_in_one_fault_budget_audited=False,
                factory_recovery_gates_certified=False,population_acceptance_prediction=False,
                graph=graph.name,class_map=class_map_certificate(graph),basis=basis,checks={})
    for s in checks:
        result['checks'][str(s)]={r:audit(supports[s-5],graph,r,a.max_faults,a.outside_envelope) for r in routes}
        for r,row in result['checks'][str(s)].items():
            print('check',s,r,'flagged',row['flagged'],'witnesses',len(row['graph_information_witnesses']),flush=True)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2)+'\n')
    assert sourcehashes=={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in sourcepaths},'Sources changed during audit'
    result['sources']=sourcehashes
    result['finite_isolated_audit_verified']=True
    a.output.write_text(json.dumps(result,indent=2)+'\n');print('Saved',a.output)


if __name__=='__main__':main()
