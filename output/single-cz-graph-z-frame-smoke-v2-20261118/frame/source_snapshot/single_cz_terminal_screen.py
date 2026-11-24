"""Ordered, one-record terminal error-detection screen.

Outer Z checks, outer X checks, inner Z checks, inner X checks. Accept the
fast path only when EVERY syndrome and flag report is zero. Nonzero code
syndromes use fresh certified recovery; flags retain the existing policy.
No logical observable, data reset, T gate or graph coupling is introduced.
"""
import c4_helix_single_block_cz as m
from single_cz_flagged import flagged_program


def screen_checks():
    return tuple((axis,j) for indices in (range(5,9),range(5)) for axis in "ZX" for j in indices)


def screen_program(order=None):
    """Actual Clifford gate list on data 0..19, syndrome 20, flags 21..23.

    Returned readout positions identify syndrome bits in the full physical
    measurement stream. Flags have their own positions, including reused
    physical flag slots. This is used by the independent fault certificate.
    """
    ops=[]
    readouts=[]
    measured=0
    for axis,j in (screen_checks() if order is None else order):
        support=m.SUPPORTS[j]
        n=len(support)
        labels={k:q for k,q in enumerate(support)}
        labels[n]=20
        labels.update({n+1+k:21+k%3 for k in range(n+1)})
        for name,qs in flagged_program((axis,)*n):
            targets=tuple(labels[q] for q in qs)
            ops.append((name,targets))
            if name=="MZ":
                if targets==(20,):readouts.append((axis,j,measured))
                measured+=1
    ops.append(("BOUNDARY",()))
    return ops,tuple(readouts)
