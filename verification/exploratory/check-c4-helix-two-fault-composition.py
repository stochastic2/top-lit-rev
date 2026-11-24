"""Small exact certificates used by the analytical composition proof.

This is not a simulation or enumeration of the complete circuit. The proof
in c4-helix-two-fault-composition-proof.md establishes circuit composition.
"""
from itertools import combinations, product
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
        rows.append(sum(1 << q for q, s in enumerate(symbols) if s != r'\cdot'))
assert len(rows) == 24

def span(gs):
    result = {0}
    for g in gs:
        result |= {v ^ g for v in result}
    return result

def parity(n):
    return n.bit_count() % 2

def mask(qs):
    return sum(1 << q for q in qs)

C = span(rows[:10])
perp = span(rows[:10] + rows[20:22])
assert len(C) == 512 and len(perp) == 2048
assert min(p.bit_count() for p in perp - C) == 6

# A four-bit syndrome is listed in order of upper checks R5,R6,R7,R8.
planes = []
all_nonzero = []
for i, vertex in enumerate('abcde'):
    basis = [mask([4*i, 4*i+3]), mask([4*i+2, 4*i+3])]
    syndromes = [''.join(str(parity(p & s)) for s in rows[15:19])
                 for p in [basis[0], basis[1], basis[0] ^ basis[1]]]
    planes.append({'vertex': vertex, 'nonzero_syndromes': syndromes})
    all_nonzero.extend(syndromes)
assert len(set(all_nonzero)) == 15
assert set(all_nonzero) == {format(i, '04b') for i in range(1, 16)}

# A pair of 20-qubit error supports of size <=2 has union of size <=4.
# No same-syndrome pair can differ by a nontrivial logical operation.
# For destructive Z readout only the X components matter.
errors = [mask(qs) for w in range(3) for qs in combinations(range(20), w)]
lookup = {}
for e in errors:
    syndrome = tuple(parity(e & s) for s in rows[10:19])
    logical_flip = parity(e & rows[22])
    if syndrome in lookup:
        old_e, old_flip = lookup[syndrome]
        assert old_flip == logical_flip
        assert old_e ^ e in C
    lookup[syndrome] = (e, logical_flip)

# Combinatorial upper bound for the recovery stopping rule. Mark a full
# round bad if any fault occurs in it; no other errors change a syndrome
# between successive good rounds without such a marked location.
max_rounds = 9
for f in range(3):
    for bad in combinations(range(max_rounds), f):
        assert any(not set(range(start, start+3)) & set(bad)
                   for start in range(max_rounds-2))

report = {
    'scope': 'Exact code and combinatorial certificates for the analytical proof; not full fault enumeration',
    'code_rank_per_Pauli_type': 9,
    'minimum_pure_X_or_Z_logical_weight': 6,
    'inner_block_syndrome_planes': planes,
    'all_15_nonzero_four_bit_syndromes_partitioned': True,
    'destructive_readout_error_patterns': len(errors),
    'readout_syndrome_classes': len(lookup),
    'recovery_equal_rounds_required': 3,
    'recovery_max_rounds': max_rounds,
    'recovery_bad_round_subsets_checked': sum(1 for f in range(3) for _ in combinations(range(max_rounds), f)),
}
dest = ROOT / 'output/c4-helix-two-fault-composition-certificates.json'
dest.write_text(json.dumps(report, indent=2) + '\n')
for plane in planes:
    print(plane['vertex'], ', '.join(plane['nonzero_syndromes']))
print('The five syndrome planes partition all fifteen nonzero four-bit vectors.')
print('All 211 weight <=2 readout-error patterns have logically unambiguous decoding.')
print('Every placement of <=2 bad rounds among nine contains three consecutive good rounds.')
print('Saved', dest)
