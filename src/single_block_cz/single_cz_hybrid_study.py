"""Candidate direct gauged checks, for a design audit, NOT a factory controller.

Q_s=V X(R_s) V. Each nonroot block contributes X(J) C_e((-1)^h Z(J)),
h=sum(SIGNS[J])/2 mod 2. All intersections J have even size.
Gates are listed in execution order. CCZ is always expanded into CX/T/TDG.
"""
from collections import Counter
import c4_helix_single_block_cz as m
from single_cz_compact_checks import compact_pauli_program


def ccz(a,b,c):
    # 4abc = a+b+c -(b^c)+(a^b^c)-(a^c)-(a^b) mod 8.
    return [("T",(a,)),("T",(b,)),("T",(c,)),
            ("CX",(b,c)),("TDG",(c,)),("CX",(a,c)),("T",(c,)),
            ("CX",(b,c)),("TDG",(c,)),("CX",(a,c)),
            ("CX",(a,b)),("TDG",(b,)),("CX",(a,b))]


def cz(a,b):
    return [("H",(b,)),("CX",(a,b)),("H",(b,))]


def support(s):
    return m.SUPPORTS[s] if isinstance(s,int) else tuple(s)

def blocks(s):
    return [(v,tuple(q for q in support(s) if q//4==v))
            for v in range(5) if any(q//4==v for q in support(s))]


def controlled_block(s,v,compressed=True,optimized=False):
    group=dict(blocks(s))[v]
    assert len(group)%2==0
    ds=tuple(f"D{q}" for q in group)
    if v and optimized:
        assert len(ds)==2
        # A shared data parity basis maps X_i X_j to X_i and Z_i Z_j to Z_j.
        # Absorb the signed dressing by negating the CCZ target, not another CZ.
        edge=f"A{v-1}";a,b=ds
        h=(sum(m.SIGNS[q] for q in group)//2)%2
        ops=[("CX",(a,b)),("CX",("s",a))]
        if h:ops += [("X",(b,))]
        ops += ccz("s",edge,b)
        if h:ops += [("X",(b,))]
        return ops+[("CX",(a,b))]
    ops=[("CX",("s",q)) for q in ds]
    if v:
        edge=f"A{v-1}"
        if compressed:
            # Compute Z-parity into one EXISTING data wire and uncompute.
            anchor=ds[-1]
            ops += [("CX",(q,anchor)) for q in ds[:-1]]
            ops += ccz("s",edge,anchor)
            ops += [("CX",(q,anchor)) for q in reversed(ds[:-1])]
        else:
            for q in ds:ops += ccz("s",edge,q)
        h=(sum(m.SIGNS[q] for q in group)//2)%2
        if h:ops += cz("s",edge)
    return ops


def outer_program(s,compressed=True,flags=True,optimized=False):
    if isinstance(s,int) and s not in range(5,9):raise ValueError("Outer checks 5..8 only")
    assert len(support(s))==8
    groups=blocks(s)
    assert len(groups)==4
    ops=[("PREP",("s",)),("H",("s",))]
    if flags:ops += [("PREP",("f",))]
    for j,(v,_) in enumerate(groups):
        ops += controlled_block(s,v,compressed,optimized)
        if flags and j in (0,2):ops += [("CX",("s","f"))]
    if flags:ops += [("MZ",("f",))]
    return ops+[("H",("s",)),("MZ",("s",))]


def outer_two_flag_program(s):
    """Candidate overlapping block windows: (0,1) and (1,2), Z flags.

    This is an audited isolated-meter alternative, not a factory theorem.
    """
    groups=blocks(s);assert len(groups)==4
    ops=[("PREP",("s",)),("H",("s",)),("PREP",("f0",)),("PREP",("f1",)),("CX",("s","f1"))]
    for j,(v,_) in enumerate(groups):
        ops += controlled_block(s,v,optimized=True)
        if j==0:ops += [("CX",("s","f0"))]
        elif j==1:ops += [("CX",("s","f1")),("MZ",("f1",))]
        elif j==2:ops += [("CX",("s","f0")),("MZ",("f0",))]
    return ops+[("H",("s",)),("MZ",("s",))]


def bare_nonroot_gauss_program(graph,v):
    """Explicit direct G_v extraction; block hooks require a NEW recovery proof."""
    assert v in range(1,5)
    ops=[("PREP",("s",)),("H",("s",))]
    for q in range(4*v,4*v+4):
        first,last=("T","TDG") if m.SIGNS[q]==1 else ("TDG","T")
        ops += [(first,(f"D{q}",)),("CX",("s",f"D{q}")),(last,(f"D{q}",))]
    ops += [("CX",("s",f"A{e}")) for e,ends in enumerate(graph.edges) if v in ends]
    return ops+[("H",("s",)),("MZ",("s",))]


def counts(ops):
    result=Counter(op for op,qs in ops)
    result["T_TDG"]=result["T"]+result["TDG"]
    return dict(result)


def record_counts(compressed=True,flags=True,optimized=False,outer_supports=None):
    # Optimistic all-positive-sector record. Extra sector certification,
    # wrong reports and fallback work are deliberately NOT priced here.
    ops=[]
    for s in range(9):ops += compact_pauli_program("Z",len(m.SUPPORTS[s]))
    for s in range(5):ops += compact_pauli_program("X",4)
    for s in (range(5,9) if outer_supports is None else outer_supports):
        ops += outer_program(s,compressed,flags,optimized)
    return counts(ops)

def reference_record_counts():
    ops=[]
    for axis in ("Z","X"):
        for group in m.SUPPORTS:ops += compact_pauli_program(axis,len(group))
    for _ in range(2):
        for q in range(4,20):
            first,last=("T","TDG") if m.SIGNS[q]==1 else ("TDG","T")
            ops += [(first,(f"D{q}",)),("CX",(f"A{q//4-1}",f"D{q}")),(last,(f"D{q}",))]
    return counts(ops)


def full_physical_oracle(s,data,edges,control):
    """Independent elementary physical V -> X(R_s) -> V action, mod zeta8.

    Uses ALL twenty data bits, never the precomputed dressing formula.
    """
    if not control:return data,0
    phase=0
    for middle in (False,True):
        if middle:data ^= sum(1 << q for q in support(s))
        for q in range(4,20):
            if edges >> (q//4-1)&1:
                phase += m.SIGNS[q]*(2*((data >> q)&1)-1)
                data ^= 1 << q
    return data,phase%8


def monomial_core(ops):
    """Contract only exact H-CX-H CZ macros; omit preparation/readout.

    The audit separately verifies that contraction by dense matrices.
    """
    ops=list(ops);out=[];i=0
    while i<len(ops):
        op,qs=ops[i]
        if op=="H" and qs!=("s",):
            assert i+2<len(ops) and ops[i+1][0]=="CX" and ops[i+2]==ops[i]
            a,b=ops[i+1][1];assert qs==(b,)
            out.append(("CZ",(a,b)));i+=3;continue
        if op in ("CX","X","T","TDG"):out.append((op,qs))
        else:assert op in ("PREP","MZ") or (op=="H" and qs==("s",))
        i+=1
    return out


def run_core(core,bits):
    bits=dict(bits);phase=0
    for op,qs in core:
        if op=="CX":bits[qs[1]] ^= bits[qs[0]]
        elif op=="X":bits[qs[0]] ^= 1
        elif op=="CZ":phase += 4*bits[qs[0]]*bits[qs[1]]
        elif op in ("T","TDG"):phase += (1 if op=="T" else -1)*bits[qs[0]]
        else:raise ValueError(op)
    return bits,phase%8
