"""Exact algebra audit of the five-vertex SWAP-gauging note.

No noise model or circuit-level fault-tolerance claim is made here.
Run with Python 3; this script needs only the standard library.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
source = (ROOT / 'arXiv-2609.03194v1/appendix.tex').read_text()
table = source.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
rows = []
for line in table.splitlines():
    symbols = re.findall(r'\$(X|Z|\\cdot)\$', line)
    if len(symbols) == 20:
        rows.append([q for q, symbol in enumerate(symbols) if symbol != r'\cdot'])
R = rows[:10]
assert R == rows[10:20]
V = list('abcde')
edges = {q: tuple(v for v, support in zip(V, R[5:]) if q in support)
         for q in range(20)}
assert all(len(pair) == 2 for pair in edges.values())
pair_edges = {pair: [q for q, endpoints in edges.items() if endpoints == pair]
              for pair in combinations(V, 2)}
assert all(len(qs) == 2 for qs in pair_edges.values())
controls = {'a': [0, 6, 11, 12], 'b': [7, 9, 15, 16],
            'c': [2, 8, 13, 19], 'd': [3, 5, 14, 17],
            'e': [1, 4, 10, 18]}
phi = {q: v for v, qs in controls.items() for q in qs}
assert sorted(phi) == list(range(20))
assert all(phi[q] in edges[q] for q in edges)
roots = V + V
paths = [[[] if phi[q] == roots[i] else
          [pair_edges[tuple(sorted((phi[q], roots[i])))][0]]
          for q in support] for i, support in enumerate(R)]
cycles = [qs for qs in pair_edges.values()]
cycles += [[pair_edges[('a', u)][0], pair_edges[(u, v)][0],
            pair_edges[('a', v)][0]] for u, v in combinations(V[1:], 2)]

def mask(qs):
    return sum(1 << q for q in qs)

def rank(vectors):
    basis = {}
    for x in vectors:
        while x:
            k = x.bit_length() - 1
            if k in basis:
                x ^= basis[k]
            else:
                basis[k] = x
                break
    return len(basis)

assert rank(map(mask, cycles)) == 16
assert all(not any(sum(v in edges[q] for q in cycle) % 2 for v in V)
           for cycle in cycles)
assert rank(map(mask, R)) == 9
assert all((mask(r) & mask(s)).bit_count() % 2 == 0 for r in R for s in R)

# Direct three-qubit basis checks of the Fredkin conjugations used in
# equations (3) and (4), including the X-type (off-diagonal) identity.
def fredkin(b):
    c, left, right = (b >> i & 1 for i in range(3))
    return c | ((right if c else left) << 1) | ((left if c else right) << 2)

def unconditional_swap(b):
    return (b & 1) | ((b >> 2 & 1) << 1) | ((b >> 1 & 1) << 2)

for b in range(8):
    assert fredkin(fredkin(b) ^ 1) == (unconditional_swap(b) ^ 1)
    assert fredkin(fredkin(b) ^ 2) == (b ^ (4 if b & 1 else 2))
    c, left, right = (b >> i & 1 for i in range(3))
    assert (fredkin(b) >> 1 & 1) == (left ^ (c & (left ^ right)))

flat_fields = {mask([q for q, (u, v) in edges.items()
                     if (t >> V.index(u) ^ t >> V.index(v)) & 1])
               for t in range(32)}
assert len(flat_fields) == 16
assert len(flat_fields) == 2 ** (20 - rank(map(mask, cycles)))

# All 32 outcome records: tree Z corrections put the parity at vertex a.
tree_to_a = {'b': 7, 'c': 11, 'd': 3, 'e': 0}
for record in range(32):
    negatives = {v for i, v in enumerate(V) if record >> i & 1}
    residual = set(negatives)
    for v, q in tree_to_a.items():
        if v in negatives:
            residual ^= set(edges[q])
    assert residual == ({'a'} if len(negatives) % 2 else set())
    for t in range(16):
        representative = t << 1  # t_a=0
        chi = (record & representative).bit_count() % 2
        complemented_chi = (record & (representative ^ 31)).bit_count() % 2
        assert complemented_chi == (chi ^ (record.bit_count() % 2))

# Every flat field has a unique representative with t_a=0. For every
# representative, the path dressing assigns each check factor to B or C
# exactly as the local SWAP circuit does, up to an entire-check exchange.
for record in range(16):
    t = {'a': 0, **{v: record >> i & 1 for i, v in enumerate(V[1:])}}
    z = {q: t[u] ^ t[v] for q, (u, v) in edges.items()}
    assert all(sum(z[q] for q in cycle) % 2 == 0 for cycle in cycles)
    distributed = []
    for i, support in enumerate(R):
        for which in (0, 1):
            destinations = []
            for q, path in zip(support, paths[i]):
                parity = sum(z[f] for f in path) % 2
                assert parity == t[phi[q]] ^ t[roots[i]]
                destinations.append(q + 20 * (which ^ parity))
            distributed.append(mask(destinations))
    assert all((r & s).bit_count() % 2 == 0
               for r in distributed for s in distributed)
    assert rank(distributed) == 18

# Controller flips are graph cuts. They preserve loops, and conjugate a
# dressed B-check to itself times its B*C pair check precisely at its root.
for i, support in enumerate(R):
    for v in V:
        for q, path in zip(support, paths[i]):
            path_flip = sum(v in edges[f] for f in path) % 2
            assert (int(phi[q] == v) ^ path_flip) == int(roots[i] == v)

weights = []
for support, dressing in zip(R, paths):
    dressed_qs = [q for q, path in zip(support, dressing) if path]
    weights.append(len(support) + len(dressed_qs) +
                   len({f for path in dressing for f in path}))
usage = Counter(f for dressing in paths for f in {q for path in dressing for q in path})
report = {
    'vertices': V,
    'edges': {str(q): list(pair) for q, pair in edges.items()},
    'pair_edges': {''.join(pair): qs for pair, qs in pair_edges.items()},
    'table_I_supports': R, 'controls': controls,
    'check_roots': roots, 'dressing_paths': paths,
    'cycle_basis': cycles, 'dressed_B_check_weights': weights,
    'edge_use_per_type': dict(sorted(usage.items())),
    'qubits_before_measurement': 65, 'qubits_after_measurement': 60,
    'all_plus_sector_dimension': 10, 'odd_sector_dimension': 6,
    'scope': 'Exact ideal algebra; no fault-tolerance claim.'}
dest = ROOT / 'output/c4-helix-five-vertex-gauging.json'
dest.write_text(json.dumps(report, indent=2) + '\n')
print('Table I supports and image incidence agree; graph is doubled K5.')
print('5 vertices, 20 edges, degree 8; 4 SWAP targets per controller.')
print('16 independent flux checks: ten 2-edge cycles, six triangles.')
print('Fredkin conjugation identities: all eight computational basis states pass.')
print('All 32 outcome records: global-parity projection and sign corrections pass.')
print('All 16 flat fields: every dressing identity and all X/Z commutations pass.')
print('All 50 check/root gauge-transformation identities pass.')
print('Dressed B-check weights:', weights, '; maximum:', max(weights))
print('Maximum edge use among ten checks of one type:', max(usage.values()))
print('Saved', dest)
