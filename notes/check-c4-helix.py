"""Exact binary checks for c4-helix-and-clifford-measurements.md.

Run with Python 3; no third-party packages are required. The 20-qubit
supports are read directly from Table I in the manuscript TeX source.
This is an ideal code/algebra audit, not a circuit-noise simulation.
"""

from itertools import combinations, product
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
source = (ROOT / "arXiv-2609.03194v1/appendix.tex").read_text()
table = source.split(r"\begin{minipage}{0.6\textwidth}")[1].split(
    r"\end{minipage}"
)[0]
rows = []
for line in table.splitlines():
    symbols = re.findall(r"\$(X|Z|\\cdot)\$", line)
    if len(symbols) == 20:
        rows.append(sum(1 << q for q, symbol in enumerate(symbols)
                        if symbol != r"\cdot"))
assert len(rows) == 24
M, ZM = rows[:10], rows[10:20]
x0, x1, z0, z1 = rows[20:]
assert M == ZM


def parity(x):
    return x.bit_count() % 2


def span(generators):
    result = {0}
    for g in generators:
        result |= {v ^ g for v in result}
    return result


C = span(M)
assert len(C) == 512
assert all(parity(r & s) == 0 for r in M for s in M)
assert all(parity(l & r) == 0 for l in (x0, x1, z0, z1) for r in M)
assert [[parity(x & z) for z in (z0, z1)] for x in (x0, x1)] == [[1, 0], [0, 1]]
assert M[5] ^ M[6] ^ M[7] ^ M[8] ^ M[9] == 0

# A ten-bit outer error has zero syndrome only if it commutes with
# the appropriate doubled checks. A C4 block carrying a nonzero logical
# Pauli needs at least two physical qubits. Check the outer block metric.
HX = [0b01001, 0b10010, 0b00101, 0b01010]
HZ = [0b00110, 0b01100, 0b11000, 0b10001]
outer_x = [a | (b << 5) for a, b in zip(HX, HZ)]
outer_z = [b | (a << 5) for a, b in zip(HX, HZ)]
outer_stabilizers = span(outer_x + [r << 10 for r in outer_z])
min_blocks = 5
for x, z in product(range(1024), repeat=2):
    if any(parity(x & r) for r in outer_z) or any(parity(z & r) for r in outer_x):
        continue
    if x | (z << 10) in outer_stabilizers:
        continue
    occupied = (x | z) & 31 | ((x | z) >> 5)
    min_blocks = min(min_blocks, occupied.bit_count())
assert min_blocks == 3

# Enumerating C-perp needs only 2^(20-rank M) = 2048 vectors:
# C plus the two independent logical-X supports generate all of it.
perp = span(M + [x0, x1])
assert len(perp) == 2048
assert all(all(parity(b & r) == 0 for r in M) for b in perp)
distance = min(b.bit_count() for b in perp - C)
assert distance == 6

block_pairs = [(4*j + r, 4*j + s) for j in range(5)
               for r, s in combinations(range(4), 2)]
for b in range(16):
    bits = [(b >> r) & 1 for r in range(4)]
    exponent = (-bits[0] + bits[1] + bits[2] - bits[3] - parity(b)) % 4
    real_phase = bits[0] ^ bits[3] ^ (
        sum(bits[r] * bits[s] for r, s in combinations(range(4), 2)) % 2
    )
    assert exponent == 2 * real_phase
endpoint_z = sum(1 << (4*j + r) for j in range(5) for r in (0, 3))
corrected_z = endpoint_z ^ z1
assert [q for q in range(20) if corrected_z >> q & 1] == [0, 2, 4, 7, 16, 19]

for b in perp:
    native_exponent = sum(
        (-1 if r in (0, 3) else 1) * ((b >> (4*j + r)) & 1)
        for j in range(5) for r in range(4)
    ) % 4
    l0, l1 = parity(b & z0), parity(b & z1)
    assert native_exponent == 2 * ((l0 * l1) ^ l1)
    corrected_phase = parity(b & corrected_z) ^ (
        sum(((b >> p) & 1) * ((b >> q) & 1) for p, q in block_pairs) % 2
    )
    assert corrected_phase == l0 * l1

for lB, lC in product(range(4), repeat=2):
    bB = (x0 if lB & 1 else 0) ^ (x1 if lB & 2 else 0)
    bC = (x0 if lC & 1 else 0) ^ (x1 if lC & 2 else 0)
    assert parity(bB & bC) == (((lB & 1) * (lC >> 1)) ^
                              ((lB >> 1) * (lC & 1)))

# Five-vertex path, all 32 X-records and all 16 possible edge records.
# After the offset correction, inverse enrichment leaves precisely
# (I + product(x_v) U)/2 on each logical computational basis state.
for record, edge_record in product(range(32), range(16)):
    preimages = [phi for phi in range(32)
                 if sum((((phi >> j) ^ (phi >> (j + 1))) & 1) << j
                        for j in range(4)) == edge_record]
    assert len(preimages) == 2 and preimages[0] ^ preimages[1] == 31
    offset = preimages[0]
    for b in (0, x0, x1, x0 ^ x1):
        local_phases = []
        for j in range(5):
            bits = [(b >> (4*j + r)) & 1 for r in range(4)]
            local_phases.append(parity(b & corrected_z & (15 << (4*j))) ^
                                (sum(bits[r]*bits[s] for r, s in combinations(range(4), 2)) % 2))
        coefficient = sum(
            (-1) ** (parity(record & phi) ^
                     sum(local_phases[j] * ((phi ^ offset) >> j & 1)
                         for j in range(5)) % 2)
            for phi in preimages
        )
        expected = (-1) ** parity(record & offset) * (
            1 + (-1) ** (parity(record) ^ (sum(local_phases) % 2))
        )
        assert coefficient == expected

print("Table I: self-dual 10x20 check matrix, rank 9, k=2, dX=dZ=6.")
print("Outer code: minimum nontrivial logical support uses 3 paired blocks.")
print("Logical commutation pairing: identity 2x2; both outer-row relations verified.")
print("All 2048 allowed bit strings: native phase = CZ Z1; corrected involution = CZ.")
print("Five-vertex path: all 512 measurement records give the claimed logical projector.")
