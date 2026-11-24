"""Direct outer-check experiment with one physical data site per port."""

import c4_helix_single_block_cz as m
from single_cz_compact_checks import compact_pauli_program


def dressed_port(q, tree):
    """Controlled V X_q V, with V restricted to the site of this port."""
    data = f"D{q}"
    read = [("CX", ("s", data))]
    if q < 4:
        return read
    edge = f"A{tree[q // 4 - 1]}"
    first, last = ("T", "TDG") if m.SIGNS[q] == 1 else ("TDG", "T")
    basis = [(first, (data,)), ("CX", (edge, data)), (last, (data,))]
    return basis + read + basis


def dressed_x_program(support, graph):
    """Lift a compact X meter site by site, in any actual Z sector."""
    support = tuple(support)
    if len(support) not in (4, 8) or len(set(support)) != len(support):
        raise ValueError("Expected a four- or eight-site check")
    labels = [f"D{q}" for q in support] + ["s", "f0", "f1", "f2", "f3"]
    ops = []
    for op, sites in compact_pauli_program("X", len(support)):
        if op == "CX" and sites[1] < len(support):
            ops.extend(dressed_port(support[sites[1]], graph.tree))
        else:
            ops.append((op, tuple(labels[q] for q in sites)))
    return ops
