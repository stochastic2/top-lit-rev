"""Independent integer-phase checks for the isolated hybrid fault audit."""
from itertools import product
import random
import single_cz_hybrid_faults as f


def phase(error,y):
    return (error.phase+2*sum(error.l[q] for q in f.bits(y))+
            4*sum((error.a[q] & y & ((1 << q)-1)).bit_count() for q in f.bits(y)))%8


def run(ops,y):
    p=0
    for op,qs in ops:
        if op=="CX":y ^= ((y >> qs[0])&1) << qs[1]
        elif op=="X":y ^= 1 << qs[0]
        elif op in ("T","TDG"):p+=(1 if op=="T" else -1)*((y >> qs[0])&1)
        else:raise ValueError(op)
    return y,p%8


def test_exact_conjugation_and_two_fault_composition_on_every_basis_input():
    rng=random.Random(17);n=5
    for case in range(40):
        ops=[]
        for _ in range(20):
            op=rng.choice(("CX","X","T","TDG"));qs=tuple(rng.sample(range(n),2 if op=="CX" else 1));ops.append((op,qs))
        inverse=[({"T":"TDG","TDG":"T"}.get(op,op),qs) for op,qs in reversed(ops)]
        p=f.Quadratic.pauli(n,[(q,rng.randrange(4)) for q in range(n)])
        e=p.conjugate(ops)
        q=f.Quadratic.pauli(n,[(j,rng.randrange(4)) for j in range(n)]).conjugate(list(reversed(ops)))
        combined=q.after(e)
        for y in range(1 << n):
            start,a=run(inverse,y);mid=start ^ p.x;b=phase(p,start);end,c=run(ops,mid)
            assert end==y ^ e.x and (a+b+c)%8==phase(e,y)
            assert phase(combined,y)==(phase(e,y)+phase(q,y ^ e.x))%8


def test_every_three_variable_quadratic_fourier_support_with_exact_gauss_sums():
    for linear in product(range(4),repeat=3):
        for couplings in range(8):
            a=[0]*3
            for k,(i,j) in enumerate(((0,1),(0,2),(1,2))):
                if couplings >> k&1:a[i] |= 1 << j;a[j] |= 1 << i
            e=f.Quadratic(0,linear,tuple(a))
            for variables in ((0,1,2),(0,2)):
                base,rows=e.fourier_support(variables)
                got=set(f.image_words(base,rows));expected=set()
                values=[sum(((y >> j)&1) << q for j,q in enumerate(variables)) for y in range(1 << len(variables))]
                for z in values:
                    real=imag=0
                    for y in values:
                        power=(phase(e,y)//2+2*((z & y).bit_count()%2))%4
                        real+=(1,0,-1,0)[power];imag+=(0,1,0,-1)[power]
                    if real or imag:expected.add(z)
                assert got==expected


def test_initial_helper_h_handles_signed_y():
    for p in range(4):
        e=f.Quadratic.pauli(1,[(0,p)]).conjugate([("H",(0,))])
        assert e.x==(p >> 1) and e.l==(2*(p&1),)
        if p==3:assert e.phase==6  # H Y H = -Y = -i XZ


def test_report_bit_is_not_silently_a_quantum_correction():
    from single_cz_recovery import COMPACT13
    labels=[f'D{q}' for q in range(20)]+[f'A{q}' for q in range(13)]+['s','f']
    zero=f.Quadratic.pauli(35,[])
    image,n=f.class_image(zero,2,labels,(34,),COMPACT13)
    assert n==32 and image==(0,1 << 31,())
    image,n=f.class_image(zero,1,labels,(34,),COMPACT13)
    assert image==(1,0,())


def test_signed_two_flag_program_on_all_involved_basis_inputs():
    import single_cz_hybrid_study as h
    from check_single_cz_hybrid_study import choose_basis
    supports,_=choose_basis()
    for ds in supports:
        edges=[v-1 for v,group in h.blocks(ds) if v]
        core=h.monomial_core(h.outer_two_flag_program(ds))
        for word in range(1 << (8+len(edges)+1)):
            data=sum(((word >> j)&1) << q for j,q in enumerate(ds))
            graph=sum(((word >> (8+j))&1) << e for j,e in enumerate(edges))
            meter=word >> (8+len(edges))
            state={f'D{q}':(data >> q)&1 for q in ds}
            state.update({f'A{e}':(graph >> e)&1 for e in edges});state.update(s=meter,f0=0,f1=0)
            out,phase=h.run_core(core,state);expected,p=h.full_physical_oracle(ds,data,graph,meter)
            assert phase==p and all(out[f'D{q}']==((expected >> q)&1) for q in ds)
            assert out['f0']==out['f1']==0 and out['s']==meter


def test_independent_bell_tableau_checks_both_coherent_s_branches():
    from single_cz_recovery import COMPACT13
    from check_single_cz_hybrid_faults import class_map_certificate,physical_witness
    assert class_map_certificate(COMPACT13)['class_map_rank']==35
    labels=[f'D{q}' for q in range(20)]+[f'A{q}' for q in range(13)]+['s','f']
    l=[0]*35;l[0]=1;error=f.Quadratic(0,tuple(l),(0,)*35)
    (flag,base,rows),nc=f.class_image(error,0,labels,(34,),COMPACT13)
    assert flag==0 and len(rows)==1
    for word in f.image_words(base,rows):
        witness=physical_witness(error,0,labels,(34,),COMPACT13,word)
        assert witness['probability']=='1/2' and witness['restored_encoded_Bell_pairs_and_graph']
