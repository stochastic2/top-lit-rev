"""Construct and audit a local cup product on the finite C4-Helix complex.

No external dependencies. Bit masks represent cochains. The construction
retracts the 20-qubit complex onto the 10-edge toric complex, triangulates
its square faces, and transfers the Alexander--Whitney cup product back.
It proves ideal algebraic applicability, not noisy-circuit fault tolerance.
"""

from pathlib import Path
from itertools import combinations
import re
import argparse
import json


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def bits(vector):
    return [i for i in range(vector.bit_length()) if vector >> i & 1]


def span(generators):
    values = {0}
    for g in generators:
        values |= {v ^ g for v in values}
    return values


def rank(columns):
    pivots = {}
    for col in columns:
        while col:
            pivot = col.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = col
                break
            col ^= pivots[pivot]
    return len(pivots)


root = Path(__file__).resolve().parent.parent
source = (root / "arXiv-2609.03194v1/appendix.tex").read_text()
table = source.split(r"\begin{minipage}{0.6\textwidth}")[1].split(r"\end{minipage}")[0]
rows = []
for line in table.splitlines():
    symbols = re.findall(r"\$(X|Z|\\cdot)\$", line)
    if len(symbols) == 20:
        rows.append(sum(1 << q for q, s in enumerate(symbols) if s != r"\cdot"))
M = rows[:10]
assert M == rows[10:20]
d = [M, [sum(1 << i for i in range(10) if M[i] >> q & 1)
          for q in range(20)], [0] * 10]
dims = [10, 20, 10]
mu = sum(1 << i for i in range(5, 10))
assert apply(d[0], mu) == 0
assert all((mu & column).bit_count() % 2 == 0 for column in d[1])

# Cochain retraction P: full -> outer; section I: outer -> full.
# In each physical four-qubit block the degree-one basis is
# (1111, X-logical-0=1001, X-logical-1=0011, 0100).
# Logical coordinates are (b2+b3, b0+b3).
P = [[0] * 5 + [1 << j for j in range(5)], [], []]
for j in range(5):
    P[1] += [1 << (j + 5), 0, 1 << j, (1 << j) | (1 << (j + 5))]
P[2] = [sum(1 << i for i in range(5) if M[5+i] >> (4*j+1) & 1)
        for j in range(5)] + [1 << j for j in range(5)]
I = [[], [], [1 << (5+j) for j in range(5)]]
for i in range(5):
    correction = sum(
        (((M[5+i] >> (4*j)) ^ (M[5+i] >> (4*j+2)) ^
          (M[5+i] >> (4*j+3))) & 1) << j for j in range(5)
    )
    I[0].append((1 << (5+i)) | correction)
I[1] = [(1 << (4*j)) | (1 << (4*j+3)) for j in range(5)] + [
    (1 << (4*j+2)) | (1 << (4*j+3)) for j in range(5)]
odims = [5, 10, 5]
od = [[apply(P[p+1], apply(d[p], column)) for column in I[p]]
      for p in range(2)] + [[0] * 5]

for p in range(3):
    assert all(apply(P[p], column) == 1 << j for j, column in enumerate(I[p]))
for p in range(2):
    assert all(apply(P[p+1], apply(d[p], 1 << j)) == apply(od[p], P[p][j])
               for j in range(dims[p]))
    assert all(apply(d[p], I[p][j]) == apply(I[p+1], od[p][j])
               for j in range(odims[p]))
assert apply(I[0], 31) == mu
assert all(apply(od[1], col) == 0 for col in od[0])
assert [rank(d[p]) for p in range(2)] == [9, 9]
assert [rank(od[p]) for p in range(2)] == [4, 4]

# The outer cellulation has 5 vertices, 10 edges, and 5 quadrilateral faces.
ends = [bits(sum(1 << v for v in range(5) if od[0][v] >> e & 1))
        for e in range(10)]
assert all(len(pair) == 2 for pair in ends)
edge_for = {tuple(pair): e for e, pair in enumerate(ends)}
assert len(edge_for) == 10
face_edges = [bits(sum(1 << e for e in range(10) if od[1][e] >> f & 1))
              for f in range(5)]
assert all(len(boundary) == 4 for boundary in face_edges)
cycles = []
for boundary in face_edges:
    adj = {}
    for e in boundary:
        u, v = ends[e]
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    assert len(adj) == 4 and all(len(ns) == 2 for ns in adj.values())
    start = min(adj)
    cycle = [start, min(adj[start])]
    while len(cycle) < 4:
        cycle.append(next(v for v in adj[cycle[-1]] if v != cycle[-2]))
    assert start in adj[cycle[-1]]
    cycles.append(cycle)

# Verify that the cellulation is a surface, not just an Euler-count match:
# each edge is in two faces and the link of each vertex is a single cycle.
assert all(sum(e in fs for fs in face_edges) == 2 for e in range(10))
for v in range(5):
    link = {e: set() for e, uv in enumerate(ends) if v in uv}
    for fs in face_edges:
        corner = [e for e in fs if v in ends[e]]
        if corner:
            assert len(corner) == 2
            link[corner[0]].add(corner[1])
            link[corner[1]].add(corner[0])
    assert all(len(ns) == 2 for ns in link.values())
    reached, pending = set(), [next(iter(link))]
    while pending:
        e = pending.pop()
        if e not in reached:
            reached.add(e)
            pending.extend(link[e] - reached)
    assert reached == set(link)

# Triangulate each face with its own diagonal, even where an original
# edge has the same endpoints. AW is well-defined on these ordered cells.
tends = ends + [sorted([cycle[0], cycle[2]]) for cycle in cycles]
triangles, triangle_edges = [], []
for f, (v0, v1, v2, v3) in enumerate(cycles):
    diag = 10 + f
    for verts, epairs in (
        ([v0, v1, v2], [(v0,v1), (v1,v2)]),
        ([v0, v2, v3], [(v2,v3), (v3,v0)]),
    ):
        local_edges = [edge_for[tuple(sorted(pair))] for pair in epairs] + [diag]
        triangles.append(sorted(verts))
        triangle_edges.append({tuple(tends[e]): e for e in local_edges})
tdims = [5, 15, 10]
td = [
    [sum(1 << e for e, uv in enumerate(tends) if v in uv) for v in range(5)],
    [sum(1 << t for t, emap in enumerate(triangle_edges) if e in emap.values())
     for e in range(15)],
    [0] * 10,
]
TI = [[1 << v for v in range(5)], [], [1 << (2*f+1) for f in range(5)]]
for e in range(10):
    column = 1 << e
    for f, cycle in enumerate(cycles):
        path = [edge_for[tuple(sorted([cycle[0], cycle[1]]))],
                edge_for[tuple(sorted([cycle[1], cycle[2]]))]]
        if e in path:
            column |= 1 << (10+f)
    TI[1].append(column)
TP = [[1 << v for v in range(5)], [1 << e for e in range(10)] + [0] * 5,
      [1 << (t // 2) for t in range(10)]]
for p in range(3):
    assert all(apply(TP[p], col) == 1 << j for j, col in enumerate(TI[p]))
for p in range(2):
    assert all(apply(TP[p+1], apply(td[p], 1 << j)) == apply(od[p], TP[p][j])
               for j in range(tdims[p]))
    assert all(apply(td[p], TI[p][j]) == apply(TI[p+1], od[p][j])
               for j in range(odims[p]))


def aw(p, a, q, b):
    if p+q > 2:
        return 0
    result = 0
    cells = ([ [v] for v in range(5)] if p+q == 0 else tends
             if p+q == 1 else triangles)
    for c, verts in enumerate(cells):
        if p == 0:
            left = (a >> verts[0]) & 1
        elif p == 1:
            e = c if p+q == 1 else triangle_edges[c][tuple(verts[:2])]
            left = (a >> e) & 1
        else:
            left = (a >> c) & 1
        if q == 0:
            right = (b >> verts[-1]) & 1
        elif q == 1:
            e = c if p+q == 1 else triangle_edges[c][tuple(verts[-2:])]
            right = (b >> e) & 1
        else:
            right = (b >> c) & 1
        result |= (left * right) << c
    return result


def cup(p, a, q, b):
    if p+q > 2:
        return 0
    ta = apply(TI[p], apply(P[p], a))
    tb = apply(TI[q], apply(P[q], b))
    outer_result = apply(TP[p+q], aw(p, ta, q, tb))
    return apply(I[p+q], outer_result)


def differential(p, a):
    return apply(d[p], a) if p < 2 else 0


# Bilinearity makes basis-pair testing exhaustive, including non-cocycles.
leibniz_tests = 0
for p in range(3):
    for q in range(3-p):
        for i in range(dims[p]):
            for j in range(dims[q]):
                a, b = 1 << i, 1 << j
                lhs = differential(p+q, cup(p, a, q, b))
                rhs = cup(p+1, differential(p, a), q, b) if p < 2 else 0
                rhs ^= cup(p, a, q+1, differential(q, b)) if q < 2 else 0
                assert lhs == rhs, (p, q, i, j)
                leibniz_tests += 1


def integral(a):
    return (a & mu).bit_count() % 2


# Poincare pairings in all three degrees: nondegenerate on cohomology.
a, b = rows[20], rows[21]
top = 1 << 5
assert integral(cup(0, mu, 2, top)) == 1
assert integral(cup(2, top, 0, mu)) == 1
assert sum(integral(cup(2, 1 << f, 0, mu)) << f for f in range(10)) == mu
pairing = [[integral(cup(1, x, 1, y)) for y in (a, b)] for x in (a, b)]
assert pairing == [[0, 1], [1, 0]], pairing

# Integrated cup matrix and the actual homological enrichment tensor.
CZ = [sum(integral(cup(1, 1 << e, 1, 1 << f)) << f for f in range(20))
      for e in range(20)]
T = []
for v in range(10):
    T.append([sum(integral(cup(0, 1 << v, 2, cup(1, 1 << e, 1, 1 << f))) << f
                  for f in range(20)) for e in range(20)])
assert [__import__('functools').reduce(int.__xor__, (T[v][e] for v in bits(mu)), 0)
        for e in range(20)] == CZ
stabilizer_supports = span(M)
for check in M:
    assert apply(CZ, check) in stabilizer_supports
    assert sum(((row & check).bit_count() % 2) << e for e, row in enumerate(CZ)) in stabilizer_supports
assert [[(apply(CZ, x) & y).bit_count() % 2 for y in (a,b)] for x in (a,b)] == pairing

# Check signed logical phases, not just the binary logical Clifford action.
# Enumerate all allowed bit strings in B and one representative for each
# sector in C. Invariance under C stabilizers follows from the checks above.
perp = span(M + [a, b])
assert len(perp) == 2048
for bB in perp:
    lB0, lB1 = (bB & b).bit_count() % 2, (bB & a).bit_count() % 2
    for bC in (0, a, b, a ^ b):
        lC0, lC1 = (bC & b).bit_count() % 2, (bC & a).bit_count() % 2
        assert (apply(CZ, bB) & bC).bit_count() % 2 == (lB0*lC1) ^ (lB1*lC0)

# Locality audit: count nonzero tensor entries incident on each register.
entries = [(v,e,f) for v in range(10) for e in range(20) for f in bits(T[v][e])]
degrees = [max(sum(entry[k] == j for entry in entries) for j in range([10,20,20][k]))
           for k in range(3)]
print('Full/outer and outer/triangulated maps: chain-map identities and P I = identity verified.')
print('Toric cellulation: V=5, E=10, F=5; all faces are four-edge cycles.')
print('Strict Leibniz rule: all', leibniz_tests, 'basis pairs passed.')
print('Poincare pairings: degrees 0/2 nonzero; degree 1 matrix', pairing)
print('Global cup gate: CZ count', sum(row.bit_count() for row in CZ))
print('Homological enrichment: CCZ count', len(entries), '; max gate participation a/B/C', degrees)
print('Zero inner-check controls:', all(not any(T[v]) for v in range(5)))
print('All cocycle enrichment identities verified; induced logical gate = CZ(B0,C1) CZ(B1,C0).')
print('Local face cycles:', cycles)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, help='Save maps and the explicit gate list as JSON.')
args = parser.parse_args()
if args.output:
    report = {
        'scope': 'Finite-code ideal homological gauging; no circuit-noise/fault-tolerance claim.',
        'construction': 'Local cochain retract to outer toric code, face triangulation, transferred Alexander-Whitney product.',
        'check_supports': [bits(row) for row in M],
        'full_to_outer_columns': P,
        'outer_to_full_columns': I,
        'outer_to_triangulated_columns': TI,
        'triangulated_to_outer_columns': TP,
        'outer_face_cycles': cycles,
        'fundamental_class_check_labels': bits(mu),
        'ancilla_cocycle_check_labels': bits(mu),
        'logical_pairing': pairing,
        'leibniz_basis_tests': leibniz_tests,
        'cz_pairs_B_C': [(e,f) for e in range(20) for f in bits(CZ[e])],
        'ccz_triples_a_B_C': entries,
        'max_ccz_participation_a_B_C': degrees,
        'signed_logical_action': 'CZ(B0,C1) CZ(B1,C0)',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('Saved explicit maps and gate list to', args.output)
