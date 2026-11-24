"""Bare graph stars and terminal cycle flattening, without data operations.

The star meters run BETWEEN the existing coordinate passes. Their entire
error algebra acts on graph qubits, so a broad controller hook need not be
counted as several data faults. Cycle sectors are left unfixed until the
last Gauss round; a certified terminal cycle vector is then corrected using
NON-TREE edges only. Those corrections commute exactly with V.
"""
from functools import lru_cache
import c4_helix_single_block_cz as m


def bare_star_program(n):
    if not isinstance(n,int) or isinstance(n,bool) or n<1:
        raise ValueError("Nonempty graph star required")
    s=n
    return ([("PREP",(s,)),("H",(s,))] +
            [("CX",(s,j)) for j in range(n)] + [("H",(s,)),("MZ",(s,))])


def cycle_syndrome(graph,word):
    if not 0<=word<1 << len(graph.edges):
        raise ValueError("Invalid edge word")
    return sum(((word & m.mask(c)).bit_count()%2) << j for j,c in enumerate(graph.cycles))


@lru_cache(maxsize=None)
def chord_basis(graph):
    """Inverse of the cycle parity matrix restricted to non-tree edges."""
    graph.validate()
    pivots={}
    for edge in range(len(graph.edges)):
        if edge in graph.tree:
            continue
        column=cycle_syndrome(graph,1 << edge)
        correction=1 << edge
        while column:
            p=column.bit_length()-1
            if p in pivots:
                a,b=pivots[p]
                column^=a
                correction^=b
            else:
                pivots[p]=column,correction
                break
        if not column:
            raise ArithmeticError("Cycle/chord matrix is singular")
    if len(pivots)!=len(graph.cycles):
        raise ArithmeticError("Incomplete cycle/chord inverse")
    return tuple((p,*pivots[p]) for p in sorted(pivots,reverse=True))


def chord_correction(graph,bits):
    """All cycle syndromes are valid; no low-weight decoding assumption.

    Input is only the CERTIFIED REPORTED cycle vector. No actual edge word,
    fault log or quantum-state diagnostic is used.
    """
    if len(bits)!=len(graph.cycles) or any(b not in (0,1) for b in bits):
        raise ValueError("Expected complete binary cycle vector")
    syndrome=sum(b << j for j,b in enumerate(bits))
    correction=0
    for p,column,mask in chord_basis(graph):
        if syndrome & (1 << p):
            syndrome^=column
            correction^=mask
    if syndrome:
        raise ArithmeticError("Unsolved cycle syndrome")
    assert not correction & m.mask(graph.tree)
    return tuple(e for e in range(len(graph.edges)) if correction & (1 << e))
