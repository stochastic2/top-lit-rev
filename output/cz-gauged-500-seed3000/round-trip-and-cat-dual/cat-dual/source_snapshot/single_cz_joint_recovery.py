"""Joint code/cycle recovery in the existing V-coordinate round-trip circuit.

Conservative GLOBAL-two-fault operator envelope; no Pauli XOR through T.
One fault has an arbitrary data-block algebra correlated with its tree
edge, or a graph-only edge/star hook. Two such algebras are composed only
AFTER taking their full Pauli spans in the common coordinate frame.
Graph Z is unrestricted; later existing star measurements restore signs.
"""
from collections import defaultdict
from functools import lru_cache
from itertools import combinations_with_replacement
from single_cz_root_recovery import AffineSpan,external_cases,_shorten


@lru_cache(maxsize=None)
def families(graph):
    graph.validate()
    groups=defaultdict(set)
    cases=external_cases(graph)
    # external_cases includes identity, so this covers zero, one AND two faults.
    for (a,c),(b,d) in combinations_with_replacement(cases,2):
        blocks=tuple(sorted({v for v in (a,b) if v is not None}))
        groups[c ^ d].add(blocks)
    return {cycle:tuple(sorted(blocks)) for cycle,blocks in groups.items()}


@lru_cache(maxsize=None)
def data_space(blocks):
    generators=[]
    for v in blocks:
        for q in range(4*v,4*v+4):generators += [1 << q,1 << (20+q)]
    space=AffineSpan.create(0,generators)
    # Any TWO FIXED inner blocks are erasure-correctable. This is not the
    # claim that two unknown block faults are always correctable.
    if space.kernels:raise ArithmeticError('Known-block logical kernel')
    return space


def decision_word(graph,syndrome,cycle):
    if not 0<=syndrome<1 << 18 or not 0<=cycle<1 << len(graph.cycles):
        raise ValueError('Code/cycle record out of range')
    labels=set();best=None;matches=0
    for blocks in families(graph).get(cycle,()):
        row=data_space(blocks).solve(syndrome)
        if row is None:continue
        matches+=1;labels.add(row['logical'])
        p=row['pauli'];correction=(p & ((1 << 20)-1),p >> 20)
        if best is None or ((correction[0] | correction[1]).bit_count(),correction)<((best[0] | best[1]).bit_count(),best):best=correction
    unique=len(labels)==1
    if unique:best=_shorten(best[0] | (best[1] << 20))
    return dict(correction=best if unique else None,classes=len(labels),
                status='unique' if unique else 'ambiguous' if labels else 'absent',
                matching_families=matches,families_checked=len(families(graph).get(cycle,())))


def decision(graph,record):
    if len(record)!=18+len(graph.cycles) or any(b not in (0,1) for b in record):
        raise ValueError('Complete binary code/cycle record required')
    return decision_word(graph,sum(b << j for j,b in enumerate(record[:18])),
                         sum(b << j for j,b in enumerate(record[18:])))
