"""Persistent gauging coordinates and the transported root-Gauss gadget.

Only the data W ports need rolling flags; graph-X ports are appended after
the last data port. Arbitrary graph support is allowed in the new proof.
No cut decoding is used, so the connected four-edge root star is admissible.
"""
import c4_helix_single_block_cz as m
from single_cz_flagged import flagged_program
from single_cz_recovery import Graph,GRAPHS,rank

TREE4=Graph("tree4",((0,1),(0,2),(0,3),(0,4)),(),(0,1,2,3))
PERSISTENT_GRAPHS={**GRAPHS,"tree4":TREE4}


def validate_persistent_graph(graph):
    assert len(graph.tree)==4
    assert all(graph.edges[e]==(0,v) for v,e in enumerate(graph.tree,1))
    assert all(0<=a<b<5 for a,b in graph.edges)
    assert rank([graph.cut(1 << v) for v in range(1,5)])==4
    assert rank([m.mask(c) for c in graph.cycles])==len(graph.cycles)==len(graph.edges)-4
    assert all(not (graph.cut(t)&m.mask(c)).bit_count()%2 for t in range(32) for c in graph.cycles)


def transported_gauss_program(degree,signs=m.SIGNS):
    """Ports 0..19=data W, 20..20+degree-1=graph X, s=20+degree.

    Exactly 62+degree CX, 40 T/Tdg, 2 H, 22 PREP/MZ. Flag reports first,
    in the original W20 rolling order, syndrome last. At most 3 live flags.
    """
    if degree<1:raise ValueError("Nonempty root star required")
    n=20+degree
    def remap(q):return q if q<20 else q+degree
    ops=[(op,tuple(remap(q) for q in qs)) for op,qs in flagged_program(("W",)*20,signs)[:-2]]
    ops += [("CX",(n,20+j)) for j in range(degree)]
    return ops+[("H",(n,)),("MZ",(n,))]
