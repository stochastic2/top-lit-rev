"""Conservative joint graph/data recovery of a flagged Clifford-product check.

Root W hooks are expanded into a SPAN of Paulis with arbitrary complex
coefficients, not sampled or XOR-propagated as Paulis through T gates.
Each affine family represents every Pauli in that span modulo the code.
A correction is returned only if every compatible family has one common
logical class. Graph phases are unrestricted; cycles constrain graph X.
"""
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

import c4_helix_single_block_cz as m
from single_cz_flagged import flagged_program
from single_cz_recovery import syndrome

DATA=(1 << 20)-1
LOGICAL_MASKS=tuple(m.mask(s) for s in (m.X1,m.X0,m.X0,m.X1))


def _bits(mask):
    while mask:
        bit=mask & -mask
        yield bit.bit_length()-1
        mask^=bit


@lru_cache(maxsize=65536)
def _classword(p):
    x,z=p & DATA,p >> 20
    logical=sum(((word & mask).bit_count()%2) << j for j,(word,mask) in enumerate(zip((x,x,z,z),LOGICAL_MASKS)))
    return syndrome(x,z) | (logical << 18)


def _rref(values):
    pivots={}
    for value in values:
        for k,row in sorted(pivots.items(),reverse=True):
            if value >> k&1:value^=row
        if value:
            k=value.bit_length()-1
            for j,row in tuple(pivots.items()):
                if row >> k&1:pivots[j]=row ^ value
            pivots[k]=value
    return tuple(row for k,row in sorted(pivots.items(),reverse=True))


def _reduce(value,rows):
    for row in rows:
        if value >> (row.bit_length()-1)&1:value^=row
    return value


@dataclass(frozen=True)
class AffineSpan:
    base: int
    generators: tuple
    rows: tuple
    kernels: tuple
    key: tuple

    @classmethod
    def create(cls,base,generators):
        generators=tuple(generators)
        pivots={};kernels=[]
        for p in generators:
            word=_classword(p);s=word & ((1 << 18)-1);logical=word >> 18
            for k,(row,label,witness) in sorted(pivots.items(),reverse=True):
                if s >> k&1:s^=row;logical^=label;p^=witness
            if s:pivots[s.bit_length()-1]=(s,logical,p)
            elif logical:kernels.append((logical,p))
        rows=tuple(pivots[k] for k in sorted(pivots,reverse=True))
        image=_rref(_classword(p) for p in generators)
        key=(_reduce(_classword(base),image),image)
        return cls(base,generators,rows,tuple(kernels),key)

    def solve(self,reported):
        p=self.base;word=_classword(p)
        s=reported ^ (word & ((1 << 18)-1));logical=word >> 18
        for row,label,witness in self.rows:
            if s >> (row.bit_length()-1)&1:s^=row;logical^=label;p^=witness
        if s:return None
        return {"ambiguous":bool(self.kernels),"logical":logical,"pauli":p}


@lru_cache(maxsize=None)
def root_signatures(graph):
    """One physical-location support/flag signatures, INCLUDING T/Tdg.

    Helper Paulis propagate exactly. Target actions are opaque one-site
    algebras; controller X supplies the later local Clifford involutions.
    Syndrome reports are unrestricted; flag/readout flips remain explicit.
    """
    root_edges=tuple(e for e,ends in enumerate(graph.edges) if 0 in ends) if graph else ()
    nd=4 if graph else 20
    axes=("W",)*nd+("X",)*len(root_edges);n=len(axes);s=n
    ops=flagged_program(axes,m.SIGNS[:nd]+(1,)*len(root_edges))
    nf=sum(op=="MZ" for op,qs in ops)-1
    def tail(local,x,z,report,start):
        hook=0;meter=sum(op=="MZ" for op,qs in ops[:start])
        for op,qs in ops[start:]:
            if op=="CX":
                c,t=qs
                if t<n:hook^=((x >> s)&1) << t
                else:x^=((x >> c)&1) << t;z^=((z >> t)&1) << c
            elif op=="H":
                q=qs[0]
                if (x ^ z) >> q&1:x^=1 << q;z^=1 << q
            elif op=="PREP":
                q=qs[0];x&=~(1 << q);z&=~(1 << q)
            elif op=="MZ":
                q=qs[0];report^=((x >> q)&1) << meter;meter+=1
                x&=~(1 << q);z&=~(1 << q)
        return local,hook,report & ((1 << nf)-1)
    def fault(paulis,qs,flip,start):
        local=x=z=0
        for p,q in zip(paulis,qs):
            if q<n:
                if p:local|=1 << q
            else:x|=(p&1) << q;z|=(p >> 1) << q
        report=flip << sum(op=="MZ" for op,qs in ops[:start])
        return tail(local,x,z,report,start)
    sigs={(0,0,0)};live=set(range(n))
    for i,(op,qs) in enumerate(ops):
        for q in live-set(qs):
            for p in (1,2,3):sigs.add(fault((p,),(q,),0,i))
        for paulis in product(range(4),repeat=len(qs)):
            for flip in range(2 if op=="MZ" else 1):
                sigs.add(fault(paulis,qs,flip,i if op=="MZ" else i+1))
        if op=="PREP":live.update(qs)
        elif op=="MZ":live.difference_update(qs)
    return tuple(sorted(sigs))


def cycle_word(graph,mask):
    return sum((mask & m.mask(c)).bit_count()%2 << j for j,c in enumerate(graph.cycles)) if graph else 0


@lru_cache(maxsize=None)
def external_cases(graph):
    """One outside fault in V coordinates: typed data/graph-X cones.

    Arbitrary graph Z is always allowed. Pauli-data checks, source and
    coordinate locations are bounded by one data block, paired with its
    own tree edge if any. Bare star hooks are graph-only suffixes/singletons.
    Cut-equivalent graph X representatives have the same cycle word.
    """
    cases={(b,0) for b in range(5)} | {(None,0)}
    if graph:
        for b,e in enumerate(graph.tree,1):cases.add((b,cycle_word(graph,1 << e)))
        for e in range(len(graph.edges)):cases.add((None,cycle_word(graph,1 << e)))
        for v in range(1,5):
            edges=[e for e,ends in enumerate(graph.edges) if v in ends]
            for j in range(len(edges)+1):cases.add((None,cycle_word(graph,m.mask(edges[j:]))))
    return tuple(sorted(cases,key=lambda row:(-1 if row[0] is None else row[0],row[1])))


@lru_cache(maxsize=64)
def family_specs(graph,flags):
    """Complete overapproximation of one root + one outside, or two root faults."""
    sigs=root_signatures(graph)
    nf=(4+sum(0 in e for e in graph.edges)+1) if graph else 21
    if not 0<flags<1 << nf:raise ValueError("Nonzero in-range root flag word required")
    root_edges=tuple(e for e,ends in enumerate(graph.edges) if 0 in ends) if graph else ()
    nd=4 if graph else 20;data_mask=(1 << nd)-1
    specs=set()
    def add(local,hook,block,external_cycle):
        free=local & data_mask
        if block is not None:free|=15 << (4*block)
        graph_local=local >> nd
        choices=tuple(_bits(graph_local))
        for packed in range(1 << len(choices)):
            toggles=sum(((packed >> j)&1) << k for j,k in enumerate(choices))
            graph_ports=(hook >> nd) ^ toggles
            gx=sum(((graph_ports >> j)&1) << e for j,e in enumerate(root_edges))
            w=hook & data_mask
            if graph:
                for b,e in enumerate(graph.tree,1):
                    if gx >> e&1:w^=15 << (4*b)
            # Multiplication by the FULL measured product is an I/U source
            # branch choice; graph-star factors are absorbed in graph phases.
            if (DATA ^ w).bit_count()<w.bit_count():w^=DATA
            specs.add((cycle_word(graph,gx) ^ external_cycle,w,free))
    for local,hook,f in sigs:
        if f==flags:
            for block,c in external_cases(graph):add(local,hook,block,c)
    byflag=defaultdict(list)
    for local,hook,f in sigs:byflag[f].append((local,hook))
    for f,left in byflag.items():
        for a,h in left:
            for b,k in byflag.get(f ^ flags,()):add(a | b,h ^ k,None,0)
    return tuple(sorted(specs))


@lru_cache(maxsize=64)
def recovery_spaces(graph,flags,use_graph=True):
    groups=defaultdict(dict)
    for cycle,w,free in family_specs(graph,flags):
        generators=[1 << q for q in _bits(free)]+[1 << (20+q) for q in _bits(free | w)]
        space=AffineSpan.create(w,generators)
        groups[cycle if use_graph else 0].setdefault(space.key,space)
    return {c:tuple(rows.values()) for c,rows in groups.items()}


def _shorten(pauli):
    x,z=pauli & DATA,pauli >> 20
    for _ in range(3):
        changed=False
        for support in m.SUPPORTS:
            h=m.mask(support)
            choices=((x,z),(x ^ h,z),(x,z ^ h),(x ^ h,z ^ h))
            a,b=min(choices,key=lambda t:((t[0] | t[1]).bit_count(),t))
            if (a,b)!=(x,z):x,z=a,b;changed=True
        if not changed:break
    return x,z


def decision(graph,flags,data_bits,cycle_bits=(),use_graph=True):
    if len(data_bits)!=18 or any(b not in (0,1) for b in data_bits):raise ValueError("Eighteen data bits required")
    if len(cycle_bits)!=(len(graph.cycles) if graph else 0) or any(b not in (0,1) for b in cycle_bits):raise ValueError("Cycle vector mismatch")
    s=sum(b << j for j,b in enumerate(data_bits));c=sum(b << j for j,b in enumerate(cycle_bits)) if use_graph else 0
    spaces=recovery_spaces(graph,flags,use_graph).get(c,())
    label=None;best=None;matches=0
    for space in spaces:
        row=space.solve(s)
        if row is None:continue
        matches+=1
        if row["ambiguous"] or (label is not None and row["logical"]!=label):
            return {"correction":None,"status":"ambiguous","matching_families":matches,"families_checked":len(spaces)}
        label=row["logical"]
        correction=_shorten(row["pauli"])
        if best is None or ((correction[0] | correction[1]).bit_count(),correction)<((best[0] | best[1]).bit_count(),best):best=correction
    return {"correction":best,"status":"unique" if best is not None else "absent",
            "logical_class":label,"matching_families":matches,"families_checked":len(spaces)}
