"""Syndrome-and-flag programs without a separately prepared cat resource.

The rolling circuit keeps two flags active during each target port. Between
ports it opens a fresh flag before closing the oldest. There are m+1 flag
reports but at most three live flags, plus one syndrome qubit. Flags are
temporarily entangled; there is no cat fanout/verification stage.
"""


def flagged_program(axes,signs=None):
    axes=tuple(axes);n=len(axes)
    if not n or any(a not in ("X","Z","W") for a in axes):
        raise ValueError("Nonempty X/Z/W ports required")
    signs=tuple(signs or (1,)*n)
    if len(signs)!=n or any(s not in (-1,1) for s in signs):
        raise ValueError("One W sign per port required")
    syndrome=n
    ops=[("PREP",(syndrome,)),("H",(syndrome,))]
    def port(j):
        axis=axes[j]
        if axis=="X":return [("CX",(syndrome,j))]
        if axis=="Z":return [("H",(j,)),("CX",(syndrome,j)),("H",(j,))]
        first,last=("T","TDG") if signs[j]==1 else ("TDG","T")
        return [(first,(j,)),("CX",(syndrome,j)),(last,(j,))]
    if n==4 and len(set(axes))==1 and axes[0] in ("X","Z"):
        # One flag brackets the two dangerous middle ports.
        flag=n+1
        ops.insert(1,("PREP",(flag,)))
        ops+=port(0)+[("CX",(syndrome,flag))]+port(1)+port(2)
        ops += [("CX",(syndrome,flag))]+port(3)+[("MZ",(flag,))]
    else:
        for j in (0,1):
            ops += [("PREP",(n+1+j,)),("CX",(syndrome,n+1+j))]
        for j in range(n):
            ops+=port(j)
            if j<n-1:
                ops += [("PREP",(n+1+j+2,)),("CX",(syndrome,n+1+j+2)),
                        ("CX",(syndrome,n+1+j)),("MZ",(n+1+j,))]
        for j in (n-1,n):
            ops += [("CX",(syndrome,n+1+j)),("MZ",(n+1+j,))]
    return ops+[("H",(syndrome,)),("MZ",(syndrome,))]


def flag_count(axes):
    axes=tuple(axes)
    return 1 if len(axes)==4 and len(set(axes))==1 and axes[0] in ("X","Z") else len(axes)+1


def active_trace(n):
    """Ideal active-flag sets along the rolling circuit's syndrome worldline."""
    active=set();trace=[(frozenset(),0)]
    for j in (0,1):
        active.add(j);trace.append((frozenset(active),0))
    for j in range(n):
        trace.append((frozenset(active),j+1))
        if j<n-1:
            active.add(j+2);trace.append((frozenset(active),j+1))
            active.remove(j);trace.append((frozenset(active),j+1))
    for j in (n-1,n):
        active.remove(j);trace.append((frozenset(active),n))
    return trace
