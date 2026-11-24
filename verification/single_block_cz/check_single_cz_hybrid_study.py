"""Exact finite design audit, not a two-fault factory certificate or simulator."""
from pathlib import Path
import argparse,json,sys
from hashlib import sha256
from itertools import product,combinations
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src/single_block_cz"))
import c4_helix_single_block_cz as m
import single_cz_hybrid_study as h
from single_cz_recovery import COMPACT13


def rank(words):
    pivots={}
    for w in words:
        while w:
            k=w.bit_length()-1
            if k in pivots:w ^= pivots[k]
            else:pivots[k]=w;break
    return len(pivots)


def choose_basis():
    candidates={};representatives=0
    for word in range(1,16):
        base=0
        for j in range(4):
            if word >> j&1:base ^= sum(1 << q for q in m.SUPPORTS[5+j])
        rows=[]
        for inner in range(32):
            mask=base
            for v in range(5):
                if inner >> v&1:mask ^= 15 << (4*v)
            ds=tuple(q for q in range(20) if mask >> q&1)
            if len(ds)!=8 or any(len(group)!=2 for v,group in h.blocks(ds)):continue
            representatives+=1
            c=h.counts(h.outer_program(ds,optimized=True))
            rows.append((c['CX'],c['T_TDG'],inner.bit_count(),inner,ds))
        candidates[word]=min(rows)
    bases=[words for words in combinations(range(1,16),4) if rank(words)==4]
    chosen=min(bases,key=lambda ws:(sum(candidates[w][0] for w in ws),
                                  sum(w not in (1,2,4,8) for w in ws),ws))
    cost=sum(candidates[w][0] for w in chosen)
    assert cost==124 and chosen==(1,3,4,8)
    return [candidates[w][4] for w in chosen],dict(
        outer_words=list(chosen),inner_multipliers=[candidates[w][3] for w in chosen],
        supports=[list(candidates[w][4]) for w in chosen],
        representatives_checked=representatives,independent_word_bases_checked=len(bases),
        minimum_outer_CX_in_this_compiler_family=cost)


def audit():
    # Independent dense verification of the sole nonmonomial macro contraction.
    H=np.array([[1,1],[1,-1]])/np.sqrt(2)
    CX=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
    assert np.allclose(np.kron(np.eye(2),H)@CX@np.kron(np.eye(2),H),np.diag([1,1,1,-1]))
    for a,b,c in product((0,1),repeat=3):
        out,phase=h.run_core(h.ccz("a","b","c"),dict(a=a,b=b,c=c))
        assert out==dict(a=a,b=b,c=c) and phase==4*a*b*c
    chosen,basis=choose_basis()
    certificates=[]
    variants=[(False,False,list(range(5,9))),(True,False,list(range(5,9))),
              (True,True,list(range(5,9))),(True,True,chosen)]
    for compressed,optimized,checks in variants:
        for s in checks:
            core=h.monomial_core(h.outer_program(s,compressed,optimized=optimized))
            ds=h.support(s)
            es=tuple(v-1 for v,qs in h.blocks(s) if v)
            tested=0
            for word in range(1 << (len(ds)+len(es)+1)):
                data=sum(((word >> j)&1) << q for j,q in enumerate(ds))
                edges=sum(((word >> (len(ds)+j))&1) << e for j,e in enumerate(es))
                control=word >> (len(ds)+len(es))
                bits={f"D{q}":(data >> q)&1 for q in ds}
                bits.update({f"A{e}":(edges >> e)&1 for e in es});bits.update(s=control,f=0)
                out,phase=h.run_core(core,bits)
                expected,p=h.full_physical_oracle(s,data,edges,control)
                assert phase==p
                assert all(out[f"D{q}"]==((expected >> q)&1) for q in ds)
                assert out["f"]==0 and out["s"]==control
                assert all(out[f"A{e}"]==bits[f"A{e}"] for e in es)
                # Unselected data cancel in V X V; check a complementary filling too.
                complement=((1 << 20)-1)^sum(1 << q for q in ds)
                _,other_phase=h.full_physical_oracle(s,data|complement,edges,control)
                assert other_phase==p
                tested+=1
            certificates.append(dict(check=s,compressed=compressed,optimized=optimized,basis_cases=tested,
                                     gates=h.counts(h.outer_program(s,compressed,optimized=optimized))))
    # Exact full-Hilbert-space inner identity: dressed X = X Z_edge^z,
    # z = actual inner-Z syndrome, not necessarily its noisy report.
    for v in range(1,5):
        for data in range(16):
            for edge in (0,1):
                full=data << (4*v);phase=0
                for j in (0,1):
                    if j:full ^= 15 << (4*v)
                    if edge:
                        for q in range(4*v,4*v+4):
                            phase+=m.SIGNS[q]*(2*((full >> q)&1)-1);full ^= 1 << q
                assert phase%8==4*edge*(data.bit_count()%2)
    baseline=h.reference_record_counts()
    assert baseline["CX"]==220 and baseline["T_TDG"]==64
    raw=h.record_counts(False);compressed=h.record_counts(True);unflagged=h.record_counts(True,False)
    assert compressed["CX"]==200+13*6 and compressed["T_TDG"]==13*7
    optimized=h.record_counts(optimized=True)
    best=h.record_counts(optimized=True,outer_supports=chosen)
    best_no_flags=h.record_counts(flags=False,optimized=True,outer_supports=chosen)
    assert optimized['CX']==255 and best['CX']==248 and best['T_TDG']==84
    assert best_no_flags['CX']==240
    assert best['CX']>baseline['CX'] and best['T_TDG']>baseline['T_TDG']
    # A genuinely gauged hybrid cannot retain bare graph-star extraction.
    # Verify direct G_v maps to the bare star under V, including all phases.
    gauss_ops=[];gauss_cases=0
    for v in range(1,5):
        program=h.bare_nonroot_gauss_program(COMPACT13,v);gauss_ops += program
        core=h.monomial_core(program)
        edges=[e for e,ends in enumerate(COMPACT13.edges) if v in ends]
        ds=list(range(4*v,4*v+4));tree=COMPACT13.tree[v-1]
        for word in range(1 << (len(ds)+len(edges)+1)):
            state={f'D{q}':(word >> j)&1 for j,q in enumerate(ds)}
            state.update({f'A{e}':(word >> (4+j))&1 for j,e in enumerate(edges)})
            state['s']=word >> (4+len(edges));original=dict(state);phase=0
            def V_local(state):
                p=0
                if state[f'A{tree}']:
                    for q in ds:
                        p+=m.SIGNS[q]*(2*state[f'D{q}']-1);state[f'D{q}'] ^= 1
                return p
            phase+=V_local(state);state,p=h.run_core(core,state);phase+=p;phase+=V_local(state)
            assert phase%8==0 and all(state[f'D{q}']==original[f'D{q}'] for q in ds)
            assert all(state[f'A{e}']==original[f'A{e}'] ^ original['s'] for e in edges)
            gauss_cases+=1
    gauss=h.counts(gauss_ops)
    assert gauss['CX']==36 and gauss['T_TDG']==32
    # Show wrong sector selection changes the quantum instrument, not just a label.
    # Bell+ data has Xpair=Zpair=+1. Wrong z=1 measures Xpair*Zedge,
    # collapsing an initially plus edge to |0> or |1>.
    X=np.array([[0,1],[1,0]]);Z=np.diag([1,-1]);I=np.eye(8)
    psi=np.kron(np.array([1,1])/np.sqrt(2),np.array([1,0,0,1])/np.sqrt(2))
    wrong=np.kron(Z,np.kron(X,X));edgeX=np.kron(X,np.eye(4))
    post=(I+wrong)@psi;post/=np.linalg.norm(post)
    assert np.vdot(psi,edgeX@psi).real>1-1e-12
    assert abs(np.vdot(post,edgeX@post))<1e-12
    return dict(verified=True,scope="ideal controlled instruments and candidate gate counts only",
                full_factory_fault_tolerance_proved=False,accepted_output_simulator_available=False,
                outer_certificates=certificates,inner_identity_basis_cases=128,
                baseline_record=baseline,raw_record=raw,compressed_record=compressed,
                compressed_even_without_outer_flags=unflagged,
                optimized_record=optimized,best_basis_record=best,best_without_outer_flags=best_no_flags,basis_search=basis,
                candidate_three_round_CX_excluding_changed_Gauss=1889+3*(best["CX"]-220),
                candidate_three_round_T_TDG_excluding_changed_Gauss=256+3*(best["T_TDG"]-64),
                direct_nonroot_Gauss_counts=gauss,direct_nonroot_Gauss_basis_cases=gauss_cases,
                reference_bare_graph_star_CX=20,
                candidate_three_round_CX=1889+3*(best["CX"]-220+gauss['CX']-20),
                candidate_three_round_T_TDG=256+3*(best["T_TDG"]-64+gauss['T_TDG']),
                candidates_are_not_certified_factories=True,
                faulty_inner_sector_report_changes_instrument=True,
                CCZ_cost_tradeoff="Best basis record CX=176+12*c, T=12*t, for CCZ cost (c CX,t T); excludes additional certification/fallback.",
                sources={p.name:sha256(p.read_bytes()).hexdigest() for p in (Path(h.__file__),Path(__file__))})


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"output/single-cz-hybrid-study.json")
    a=p.parse_args();result=audit()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("baseline_record","raw_record","compressed_record","optimized_record","best_basis_record","best_without_outer_flags","candidate_three_round_CX","candidate_three_round_T_TDG")},indent=2))
    print("Saved",a.output)
