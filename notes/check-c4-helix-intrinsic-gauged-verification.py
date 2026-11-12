"""Finite certificates for single-cycle, postselected gauged verification.

The companion Markdown contains the analytical fault-composition proof.
This script checks its finite code, graph, and Clifford-algebra ingredients;
it does not enumerate physical circuit fault pairs or estimate acceptance.
Python standard library only.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json
import re
import c4_helix_intrinsic_decoder as decoder

ROOT = Path(__file__).resolve().parent.parent
source = (ROOT / 'arXiv-2609.03194v1/appendix.tex').read_text()
table = source.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
rows = []
for line in table.splitlines():
    symbols = re.findall(r'\$(X|Z|\\cdot)\$', line)
    if len(symbols) == 20:
        rows.append([q for q, s in enumerate(symbols) if s != r'\cdot'])
assert len(rows) == 24 and rows[:10] == rows[10:20]
R = rows[:10]
V = 'abcde'
edges = {q: tuple(v for v, s in zip(V, R[5:]) if q in s) for q in range(20)}
pair_edges = {p: [q for q in edges if edges[q] == p] for p in combinations(V, 2)}
tree = {1: 7, 2: 11, 3: 3, 4: 0}  # inner group -> gauge-edge index
rho = {edge: group for group, edge in tree.items()}


def mask(qs):
    return sum(1 << q for q in qs)


def parity(x):
    return x.bit_count() % 2


def span(gs):
    out = {0}
    for g in gs:
        out |= {x ^ g for x in out}
    return out


def groups(x):
    return {q // 4 for q in range(20) if x >> q & 1}


C = span(map(mask, R))
perp = span(list(map(mask, R)) + list(map(mask, rows[20:22])))
assert len(C) == 512 and len(perp) == 2048
assert all(not parity(x & mask(r)) for x in perp for r in R)
assert min(x.bit_count() for x in perp - C) == 6
assert min(len(groups(x)) for x in perp - C) == 3
assert len(span(map(mask, R[:9]))) == 512
relative_normalizer_cases = 0
for width in (1, 2):
    for region in combinations(range(5), width):
        region_mask = mask(q for group in region for q in range(4*group, 4*group+4))
        local_normalizers = [x for x in perp if not x & ~region_mask]
        # A^dagger B has X/Z components in this restricted normalizer.
        # Both are stabilizers, so its paired copy belongs to <N_s>.
        for x, z in product(local_normalizers, repeat=2):
            assert x in C and z in C
            assert not parity(x & z)
            relative_normalizer_cases += 1
assert relative_normalizer_cases == 180

cycles = list(pair_edges.values()) + [
    [pair_edges[('a', u)][0], pair_edges[(u, v)][0], pair_edges[('a', v)][0]]
    for u, v in combinations(V[1:], 2)]
assert len(span(map(mask, cycles))) == 2**16


def cut(t):
    return mask(q for q, (u, v) in edges.items()
                if ((t >> V.index(u)) ^ (t >> V.index(v))) & 1)


words = {cut(t): t for t in range(32) if not t & 1}
assert len(words) == 16 and min(w.bit_count() for w in words if w) == 8
errors = [mask(qs) for w in range(3) for qs in combinations(range(20), w)]
for w in words:
    for e in errors:
        candidates = [c for c in words if (c ^ w ^ e).bit_count() <= 2]
        assert candidates == [w]
        decoded = decoder.decode_gauge_z(tuple((w ^ e) >> q & 1 for q in range(20)))
        assert decoded['corrected_cut_bits'] == tuple(w >> q & 1 for q in range(20))
        assert decoded['swap_pair_labels'] == tuple(q for q in range(20) if words[w] >> (q // 4) & 1)

# Common root: all D_s use the same path p(q), even for a root outside
# the original support. Every X/Z commutator is identically trivial.
path = {q: 0 if q // 4 == 0 else 1 << tree[q // 4] for q in range(20)}
for s in R[:9]:
    for t in R[:9]:
        assert len(set(s) & set(t)) % 2 == 0
        for gauge in range(16):
            sb = mask(q for q in s if not parity(path[q] & cut(gauge << 1)))
            sc = mask(s) ^ sb
            tb = mask(q for q in t if not parity(path[q] & cut(gauge << 1)))
            tc = mask(t) ^ tb
            assert not (parity(sb & tb) ^ parity(sc & tc))

# Paulis on B(0..19), C(20..39), A(40..59); phases are immaterial to
# support closure. Gauss and D_s conjugations below are Clifford maps.
def gauss(pauli, group):
    x, z = pauli
    for q in range(4*group, 4*group+4):
        b, c = 1 << q, 1 << (20+q)
        if bool(x & b) != bool(x & c):
            x ^= b | c
        if bool(z & b) != bool(z & c):
            z ^= b | c
    return x, z


def dressed(pauli, support, ptype):
    x, z = pauli
    for q in support:
        if q // 4 == 0:
            continue
        g = 1 << (40 + tree[q // 4])
        for target in (1 << q, 1 << (20+q)):
            if ptype == 'X':  # CNOT(gauge -> matter)
                if x & g:
                    x ^= target
                if z & target:
                    z ^= g
            else:  # CZ(gauge, matter)
                if x & g:
                    z ^= target
                if x & target:
                    z ^= g
    return x, z


def charge(pauli):
    x, z = pauli
    matter = (x | z) & ((1 << 40)-1)
    result = {q // 4 for q in range(20)
              if matter & ((1 << q) | (1 << (20+q)))}
    result |= {rho[e] for e in rho if x & (1 << (40+e))}
    return result


checks = [('G', i) for i in range(5)] + [(p, s) for p in 'XZ' for s in R[:9]]
closure_cases = 0
for q in range(60):
    for p in [(1 << q, 0), (0, 1 << q)]:
        for kind, support in checks:
            after = gauss(p, support) if kind == 'G' else dressed(p, support, kind)
            assert charge(after) <= charge(p)
            assert (after[0] >> 40) == (p[0] >> 40)
            closure_cases += 1

# Exact 4-qubit identity for each dressed-factor measurement circuit:
# F(g;B,C) C(P)(leaf;B) F(g;B,C) = C_leaf(Q_q^P).
def fredkin(bits):
    leaf, g, b, c = bits
    return [leaf, g, c, b] if g else [leaf, g, b, c]


for word in range(16):
    bits = [(word >> i) & 1 for i in range(4)]
    for ptype in 'XZ':
        out = fredkin(bits)
        sign = 1
        if out[0]:
            if ptype == 'X':
                out[2] ^= 1
            else:
                sign = (-1)**out[2]
        out = fredkin(out)
        target = 3 if bits[1] else 2
        expected = bits.copy()
        expected_sign = 1
        if bits[0]:
            if ptype == 'X':
                expected[target] ^= 1
            else:
                expected_sign = (-1)**bits[target]
        assert out == expected and sign == expected_sign

# Logical readout: all possible <=2 X components with the same syndrome
# give the same logical-Z parity. General Pauli corrections use distance 6.
by_syndrome = {}
for e in errors:
    syndrome = tuple(parity(e & mask(r)) for r in R[:9])
    flip = parity(e & mask(rows[22]))
    if syndrome in by_syndrome:
        old_e, old_flip = by_syndrome[syndrome]
        assert flip == old_flip and (e ^ old_e) in C
    by_syndrome[syndrome] = e, flip
for f in range(3):
    for bad in combinations(range(9), f):
        assert any(not set(range(start, start+3)) & set(bad) for start in range(7))

# Exercise the actual recovery lookup on every <=2-qubit Pauli error on
# forty data qubits, using a true syndrome triple. Corrections may differ
# physically but must differ from the error only by a stabilizer.
recovery_cases = 0
for weight in range(3):
    for positions in combinations(range(40), weight):
        for labels in product(((1, 0), (0, 1), (1, 1)), repeat=weight):
            x = sum(a << q for q, (a, b) in zip(positions, labels))
            z = sum(b << q for q, (a, b) in zip(positions, labels))
            xb, xc = x & ((1 << 20)-1), x >> 20
            zb, zc = z & ((1 << 20)-1), z >> 20
            s = decoder.syndrome(xb, zb) + decoder.syndrome(xc, zc)
            correction = decoder.recovery_from_reports([s, s, s])
            for inp, key in [((xb, zb), 'B_XZ_masks'), ((xc, zc), 'C_XZ_masks')]:
                rx, rz = correction[key]
                assert (rx ^ inp[0]) in C and (rz ^ inp[1]) in C
            recovery_cases += 1
assert recovery_cases == 7141
# Repeating G alone admits the two-fault sector-leakage counterexample in
# the note. The cross term X_B3 X_C3 is rejected by the original code,
# leaving the wrong negative-sector reference; N_Z0 would reject X_B3.
assert any(parity((1 << 3) & mask(r)) for r in R[:9])
psi = {0: 1, 4: 1}  # B0,B1,C0,C1, with C0 in +
def logical_swap(word):
    return ((word & 3) << 2) | (word >> 2)
negative = Counter(psi)
for word, amplitude in psi.items():
    negative[logical_swap(word)] -= amplitude
negative = {word: a for word, a in negative.items() if a}
assert negative == {1: -1, 4: 1}
assert {word >> 2: a for word, a in negative.items() if not word & 1} == {1: 1}
true = (0,)*36
wrong = (1,) + (0,)*35
assert decoder.recovery_from_reports([wrong, wrong]) is None
assert decoder.recovery_from_reports([wrong, wrong, true, true, true])['rounds_used'] == 5
readout_cases = 0
for codeword in (0, mask(rows[20]), mask(rows[21]), mask(rows[20]) ^ mask(rows[21])):
    for e in errors:
        result = decoder.decode_B_readout(tuple((codeword ^ e) >> q & 1 for q in range(20)))
        assert result['logical_Z0_bit'] == parity(codeword & mask(rows[22]))
        readout_cases += 1
decoder.require_three_gauged_sweeps([(0,)*39]*3)
decoder.require_three_gauged_sweeps([(0,)*57]*3, include_dressed=True)
decoder.require_three_original_sweeps([(0,)*36]*3)
for i in range(117):
    records = [[0]*39 for _ in range(3)]
    records[i // 39][i % 39] = 1
    try:
        decoder.require_three_gauged_sweeps(records)
    except decoder.RejectAttempt:
        pass
    else:
        raise AssertionError('Negative verification report was accepted')

gauss_fredkins = 20
dressed_fredkins = 2 * 2 * sum(q // 4 != 0 for s in R[:9] for q in s)
assert dressed_fredkins == 168
report = {
    'scope': 'Finite ingredients for the analytical postselected two-fault proof; not exhaustive circuit fault enumeration',
    'optional_dressed_check_root': 'a for every dressed check',
    'independent_check_indices': list(range(9)),
    'optional_dressed_gauge_error_assignment': {str(e): V[v] for e, v in rho.items()},
    'base_code_distance': 6,
    'minimum_inner_groups_in_nontrivial_Pauli_logical': 3,
    'relative_normalizer_cases_on_one_or_two_groups': relative_normalizer_cases,
    'Gauss_only_two_fault_counterexample_checked': True,
    'gauge_cut_distance': 8,
    'gauge_words': len(words),
    'radius_two_gauge_records_verified': len(words)*len(errors),
    'Pauli_generator_check_conjugation_cases': closure_cases,
    'all_common_root_dressed_checks_commute_globally': True,
    'dressed_factor_basis_identities': 32,
    'implemented_recovery_lookup_Pauli_cases': recovery_cases,
    'implemented_readout_lookup_cases': readout_cases,
    'negative_gauged_report_rejection_cases': 117,
    'central_Pauli_checks_per_gauged_sweep': 34,
    'Gauss_checks_per_gauged_sweep': 5,
    'dressed_checks_per_gauged_sweep': 0,
    'optional_full_check_variant_dressed_checks_per_sweep': 18,
    'complete_gauging_ungauging_cycles': 1,
    'gauged_verification_sweeps': 3,
    'terminal_original_code_sweeps': 3,
    'enrichment_Fredkins': 20,
    'Gauss_measurement_Fredkins_per_sweep': gauss_fredkins,
    'dressed_measurement_Fredkins_per_sweep': 0,
    'total_primitive_Fredkins': 20 + 3*gauss_fredkins,
    'optional_full_check_variant_Fredkins': 20 + 3*(gauss_fredkins+dressed_fredkins),
    'peak_physical_qubits_with_serial_reset_reuse': 77,
    'independent_whole_block_SWAP_measurements': 0,
    'recovery_round_limit': 9,
    'postselection_required': True,
    'optimality_or_noisy_yield_claim': False,
    'circuit_level_claim_basis': 'Analytical invariant and clean-sweep proof in the companion note, under its explicit fault model',
}
out = ROOT / 'output/c4-helix-intrinsic-gauged-verification.json'
out.write_text(json.dumps(report, indent=2) + '\n')
print('Code: distance 6; any nontrivial Pauli logical occupies >=3 inner groups.')
print('Common-root Clifford conjugation closure:', closure_cases, 'generator/check cases.')
print('Gauge decoder:', len(words)*len(errors), 'radius-two records pass.')
print('Local dressed-factor circuits: 32 basis/sign identities pass.')
print('One genuine cycle; three intrinsic sweeps; primitive Fredkins:', report['total_primitive_Fredkins'])
print('Saved', out)
