"""Exact ideal checks for the companion ungauging and magic-state note.

All arithmetic is binary or rational. No circuit-noise or fault-tolerance
claim is made. Read the graph from the previous note's saved audit.
"""
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
graph = json.loads((ROOT / 'output/c4-helix-five-vertex-gauging.json').read_text())
V = graph['vertices']
edges = {int(q): tuple(pair) for q, pair in graph['edges'].items()}
controls = graph['controls']
phi = {q: v for v, qs in controls.items() for q in qs}
ALL = (1 << 20) - 1

def parity(n):
    return n.bit_count() % 2

def mask(qs):
    return sum(1 << q for q in qs)

def field(t):
    return mask(q for q, (u, v) in edges.items()
                if (t >> V.index(u) ^ t >> V.index(v)) & 1)

def swaps(t):
    return mask(q for q in range(20) if t >> V.index(phi[q]) & 1)

def decode(g):
    # Fix t_a=0 and use the four edges of the a-centred spanning tree.
    t = sum((g >> q & 1) << V.index(v)
            for v, q in [('b', 7), ('c', 11), ('d', 3), ('e', 0)])
    assert field(t) == g, 'Record violates ideal flux constraints'
    return t

flat = {field(t): t for t in range(32) if not t & 1}
assert len(flat) == 16
assert all(decode(g) == t for g, t in flat.items())
assert all(swaps(t ^ 31) == (swaps(t) ^ ALL) for t in range(32))

# Operators are formal sums of products of disjoint physical SWAPs.
# A 20-bit mask records which data pairs are exchanged. This retains
# coherent operator sums; faults or swaps are not treated as Pauli errors.
for record in range(32):
    r = (-1) ** parity(record)
    for g, offset in flat.items():
        raw = {}
        for t in range(32):
            if field(t) == g:
                raw[swaps(t)] = (-1) ** parity(record & t)
        phase = (-1) ** parity(record & offset)
        corrected = {word ^ swaps(offset): coefficient for word, coefficient in raw.items()}
        assert corrected == {0: phase, ALL: phase * r}
        # Using the other solution leaves an irrelevant global phase r.
        complement = {word ^ swaps(offset ^ 31): coefficient for word, coefficient in raw.items()}
        assert complement == {0: phase * r, ALL: phase}

        # Independently check the retained-vertex paper route. After the
        # inverse cluster circuit, t=s+offset (or its global complement).
        # X_offset maps s to s+offset; inverse enrichment removes its swaps.
        for s in range(32):
            words = {}
            for k in (0, 31):
                t = s ^ offset ^ k
                assert field(t ^ s) == g
                coefficient = (-1) ** (parity(record & s) ^ parity(record & t))
                word = swaps(t) ^ swaps(s ^ offset)
                words[word] = coefficient
            assert words == {0: phase, ALL: phase * r}

# Check that every dressed check is restored by the data SWAP correction.
for g, t in flat.items():
    for i, support in enumerate(graph['table_I_supports']):
        root = V.index(graph['check_roots'][i])
        for block in (0, 1):
            restored = []
            for q, path in zip(support, graph['dressing_paths'][i]):
                path_bit = parity(g & mask(path))
                assert path_bit == ((t >> V.index(phi[q]) ^ t >> root) & 1)
                destination = block ^ path_bit ^ (t >> V.index(phi[q]) & 1)
                restored.append(q + 20 * destination)
            expected = [q + 20 * (block ^ (t >> root & 1)) for q in support]
            assert restored == expected

source = (ROOT / 'arXiv-2609.03194v1/appendix.tex').read_text()
table = source.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
rows = []
for line in table.splitlines():
    symbols = re.findall(r'\$(X|Z|\\cdot)\$', line)
    if len(symbols) == 20:
        rows.append(mask(q for q, symbol in enumerate(symbols) if symbol != r'\cdot'))
x0, x1, z0, z1 = rows[20:]
assert [[parity(x & z) for z in (z0, z1)] for x in (x0, x1)] == [[1, 0], [0, 1]]
assert [q for q in range(20) if z0 >> q & 1] == [0, 3, 6, 7, 18, 19]

# Four logical qubits in order (B0,B1,C0,C1). The input has an omitted
# common factor 1/sqrt(2). Projected vectors below have factor 1/(2sqrt(2)).
initial = {(0, 0, 0, 0): 1, (0, 0, 1, 0): 1}
branches = {}
for sign in (1, -1):
    out = defaultdict(int)
    for bits, amplitude in initial.items():
        out[bits] += amplitude
        out[bits[2:] + bits[:2]] += sign * amplitude
    out = {bits: a for bits, a in out.items() if a}
    branches[sign] = out
    assert all(bits[1] == bits[3] == 0 for bits in out)
    prob = Fraction(sum(a*a for a in out.values()), 8)
    assert prob == (Fraction(3, 4) if sign == 1 else Fraction(1, 4))
assert branches[1] == {(0, 0, 0, 0): 2, (0, 0, 1, 0): 1, (1, 0, 0, 0): 1}
assert branches[-1] == {(0, 0, 1, 0): 1, (1, 0, 0, 0): -1}
success = {bits: a for bits, a in branches[1].items() if bits[0] == 0}
assert Fraction(sum(a*a for a in success.values()), 6) == Fraction(5, 6)
assert Fraction(3, 4) * Fraction(5, 6) == Fraction(5, 8)
bloch = [Fraction(4, 5), Fraction(0), Fraction(3, 5)]
assert sum(v*v for v in bloch) == 1
assert sum(v != 0 for v in bloch) == 2  # not one of the six Pauli eigenstates

example_t = (1 << V.index('b')) | (1 << V.index('d'))
example_g = field(example_t)
report = {
    'scope': 'Exact ideal ungauging and magic-state extraction; fault tolerance deferred.',
    'outcome_records_checked': 32, 'flat_gauge_records_checked': 16,
    'direct_ungauging_record_pairs_checked': 512,
    'retained_vertex_components_checked': 16384,
    'decoding_tree': {'b': 7, 'c': 11, 'd': 3, 'e': 0},
    'example_offset_bits': [example_t >> i & 1 for i in range(5)],
    'example_negative_edges': [q for q in range(20) if example_g >> q & 1],
    'example_swap_correction': [q for q in range(20) if swaps(example_t) >> q & 1],
    'logical_Z0_support': [q for q in range(20) if z0 >> q & 1],
    'swap_plus_probability': '3/4', 'swap_minus_probability': '1/4',
    'single_qubit_success_given_plus': '5/6',
    'single_qubit_success_per_trial': '5/8',
    'single_qubit_magic_state': '(2|0_L>+|1_L>)/sqrt(5)',
    'bloch_vector': [str(v) for v in bloch],
    'corrected_Kraus_operator': 'phase * (I+r*U)/32 = phase * Pi_r/16'}
dest = ROOT / 'output/c4-helix-ungauging-and-magic.json'
dest.write_text(json.dumps(report, indent=2) + '\n')
print('All 512 (vertex, gauge) record pairs yield the intended corrected projector.')
print('All 16384 retained-vertex components independently give the same projector.')
print('All 16 gauge records: dressed checks return to original code constraints.')
print('Table I logical operators and logical-Z0 readout support verified.')
print('Magic branches: p+=3/4, p-=1/4; extraction p=5/6; total success=5/8.')
print('Single-qubit output Bloch vector: (4/5,0,3/5), a pure non-stabilizer state.')
print('Saved', dest)
