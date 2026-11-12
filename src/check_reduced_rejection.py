"""Exact algebraic certificates for the reduced-rejection gauging notes.

This is a finite code/graph audit and a reference terminal-syndrome decoder.
It does NOT simulate the modified quantum gadgets or enumerate circuit faults.
Uses only the Python standard library. Run from any directory.
"""

from collections import Counter
from functools import cache
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import re


ROOT = Path(__file__).resolve().parents[1]
SUPPORTS = (
    (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11),
    (12, 13, 14, 15), (16, 17, 18, 19),
    (0, 3, 6, 7, 10, 11, 12, 15),
    (4, 7, 8, 9, 14, 15, 16, 19),
    (1, 2, 8, 11, 12, 13, 18, 19),
    (2, 3, 5, 6, 13, 14, 16, 17),
)
EDGES = (
    (0, 4), (2, 4), (2, 3), (0, 3), (1, 4),
    (3, 4), (0, 3), (0, 1), (1, 2), (1, 4),
    (0, 4), (0, 2), (0, 2), (2, 3), (1, 3),
    (0, 1), (1, 3), (3, 4), (2, 4), (1, 2),
)
CYCLES = (
    (7, 15), (11, 12), (3, 6), (0, 10), (8, 19),
    (14, 16), (4, 9), (2, 13), (1, 18), (5, 17),
    (7, 8, 11), (7, 14, 3), (7, 4, 0),
    (11, 2, 3), (11, 1, 0), (3, 5, 0),
)
# Appendix variant: simple K5 plus an edge cover ab, cd, ae.
SMALL_EDGES = tuple(combinations(range(5), 2)) + ((0, 1), (2, 3), (0, 4))
SMALL_CYCLES = ((0, 1, 4), (0, 2, 5), (0, 3, 6),
                (1, 2, 7), (1, 3, 8), (2, 3, 9),
                (0, 10), (1, 2, 11), (3, 12))


def mask(positions):
    return sum(1 << q for q in positions)


H = tuple(map(mask, SUPPORTS))
X0 = mask((2, 3, 8, 11, 12, 15))
Z0 = mask((0, 3, 6, 7, 18, 19))
Z1 = X0


def binary_basis(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return tuple(sorted(basis.items(), reverse=True))


STAB_BASIS = binary_basis(H)


def remainder(word, basis=STAB_BASIS):
    for pivot, row in basis:
        if word >> pivot & 1:
            word ^= row
    return word


@cache
def binary_syndrome(word):
    return sum(((word & h).bit_count() & 1) << j for j, h in enumerate(H))


def syndrome(error):
    """18 bits: X-check signs first, then Z-check signs; bit 0 is R0."""
    x, z = error
    return binary_syndrome(z) | (binary_syndrome(x) << 9)


def coset(error):
    """Equality means equality modulo the full original stabilizer group."""
    return tuple(remainder(v) for v in error)


def error_key(error):
    x, z = error
    return (x | z).bit_count(), x, z


def pauli_string(error):
    x, z = error
    return "".join("IXZY"[((x >> q) & 1) | (((z >> q) & 1) << 1)]
                   for q in range(20))


def build_tables():
    """Enumerate every Pauli on each fixed two-block set, including I.

    For each F and syndrome, all errors MUST have the same stabilizer
    coset. This checks erasure correctability, not just detectability.
    Keep the minimum-weight representative for physical correction.
    """
    tables = {}
    union = {}
    for blocks in combinations(range(5), 2):
        positions = [q for b in blocks for q in range(4*b, 4*b + 4)]
        patterns = [mask(q for j, q in enumerate(positions) if v >> j & 1)
                    for v in range(256)]
        table = {}
        for x, z in product(patterns, repeat=2):
            error = (x, z)
            s, c = syndrome(error), coset(error)
            if s in table:
                assert coset(table[s]) == c, (blocks, s, error)
                if error_key(error) < error_key(table[s]):
                    table[s] = error
            else:
                table[s] = error
            union.setdefault(s, set()).add(c)
        assert len(table) == 4096
        tables[blocks] = table
    return tables, union


def decode_joint(s_b, s_c, tables):
    """Use only a reliable joint syndrome and the common-two-block bound.

    Return a physical Pauli pair, or None if absent/ambiguous. Do not call
    this on a single noisy report: the notes specify a repeated history.
    """
    candidates = []
    for table in tables.values():
        if s_b in table and s_c in table:
            candidates.append((table[s_b], table[s_c]))
    classes = {(coset(b), coset(c)) for b, c in candidates}
    if len(classes) != 1:
        return None
    return min(candidates, key=lambda pair: (
        error_key(pair[0])[0] + error_key(pair[1])[0], pair))


def symplectic(a, b):
    return ((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) & 1


def pure_error(generators, signs, n):
    """Solve [R, g_j] = signs_j by GF(2) elimination; free bits are zero."""
    rows = [(z | (x << n), s) for (x, z), s in zip(generators, signs)]
    pivots = []
    used = 0
    for col in range(2*n):
        found = next((i for i in range(used, len(rows)) if rows[i][0] >> col & 1), None)
        if found is None:
            continue
        rows[used], rows[found] = rows[found], rows[used]
        pivot_row, pivot_bit = rows[used]
        for i, (row, bit) in enumerate(rows):
            if i != used and row >> col & 1:
                rows[i] = (row ^ pivot_row, bit ^ pivot_bit)
        pivots.append(col)
        used += 1
        if used == len(rows):
            break
    assert not any(row == 0 and bit for row, bit in rows)
    solution = sum(rows[i][1] << col for i, col in enumerate(pivots))
    result = solution & ((1 << n) - 1), solution >> n
    assert [symplectic(result, g) for g in generators] == list(signs)
    return result


def check_known_state_generators(generators, n):
    assert len(generators) == n
    assert all(symplectic(a, b) == 0 for a, b in combinations(generators, 2))
    assert len(binary_basis(x | (z << n) for x, z in generators)) == n
    # Linearity certifies all 2**n syndromes using n unit right-hand sides.
    for j in range(n):
        pure_error(generators, [int(i == j) for i in range(n)], n)


def cut(t, edges):
    return sum((((t >> u) ^ (t >> v)) & 1) << q
               for q, (u, v) in enumerate(edges))


def graph_certificate(edges):
    cuts = {cut(t, edges) for t in range(32)}
    assert len(cuts) == 16
    return {"vertices": 5, "edges": len(edges),
            "resource_qubits": 5 + len(edges),
            "cut_code_distance": min(w.bit_count() for w in cuts if w),
            "cycle_rank": len(edges) - 4,
            "degrees": [sum(v in edge for edge in edges) for v in range(5)]}


def check_graph_resource(edges):
    generators = []
    for v in range(5):
        generators.append((1 << v | mask(5+q for q, edge in enumerate(edges) if v in edge), 0))
    for q, (u, v) in enumerate(edges):
        generators.append((0, (1 << u) | (1 << v) | (1 << (5+q))))
    check_known_state_generators(generators, 5 + len(edges))


def check_cut_decoding(edges, cycles):
    """All cuts and <=2 edge errors must produce distinct readout spheres."""
    cycle_masks = tuple(map(mask, cycles))
    assert len(binary_basis(cycle_masks)) == len(edges) - 4
    cuts = {cut(t, edges) for t in range(32)}
    reports = {}
    for c in cuts:
        assert all((c & h).bit_count() % 2 == 0 for h in cycle_masks)
        for weight in range(3):
            for qs in combinations(range(len(edges)), weight):
                report = c ^ mask(qs)
                assert report not in reports
                reports[report] = c
    return len(reports)


def main(output):
    source = (ROOT / 'arXiv-2609.03194v1/appendix.tex').read_text()
    table = source.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
    paper_rows = []
    for line in table.splitlines():
        symbols = re.findall(r'\$(X|Z|\\cdot)\$', line)
        if len(symbols) == 20:
            paper_rows.append(mask(q for q, symbol in enumerate(symbols) if symbol != r'\cdot'))
    assert tuple(paper_rows[:9]) == H
    assert (paper_rows[20], paper_rows[22], paper_rows[23]) == (X0, Z0, Z1)
    assert len(STAB_BASIS) == 9
    assert all((a & b).bit_count() % 2 == 0 for a, b in product(H, repeat=2))
    normalizer = [w for w in range(1 << 20) if binary_syndrome(w) == 0]
    assert min(w.bit_count() for w in normalizer if remainder(w)) == 6
    # The brute-force normalizer loop is bounded; release its memoized syndromes.
    binary_syndrome.cache_clear()

    original = [(h, 0) for h in H] + [(0, h) for h in H]
    check_known_state_generators(original + [(0, Z0), (0, Z1)], 20)
    check_known_state_generators(original + [(X0, 0), (0, Z1)], 20)
    check_graph_resource(EDGES)
    check_graph_resource(SMALL_EDGES)

    tables, union = build_tables()
    histogram = dict(sorted(Counter(map(len, union.values())).items()))
    assert histogram == {1: 23281, 4: 3675, 10: 180}
    assert union[0] == {(0, 0)}

    # Every possible fixed-F joint syndrome is admitted when F is provided.
    # The general decoder also admits cases where the two syndromes locate F.
    ex_b = (mask((2, 3)), 0)
    ex_c = (mask((0, 4)), 0)
    joint = decode_joint(syndrome(ex_b), syndrome(ex_c), tables)
    assert len(union[syndrome(ex_b)]) == 4
    assert joint is not None
    assert (coset(joint[0]), coset(joint[1])) == (coset(ex_b), coset(ex_c))
    assert decode_joint(syndrome(ex_b), 0, tables) is None
    single = decode_joint(syndrome((1, 0)), 0, tables)
    assert single is not None and coset(single[0]) == coset((1, 0))
    ambiguous = (mask((8, 11, 12, 15)), 0)
    assert syndrome(ex_b) == syndrome(ambiguous)
    assert coset(ex_b) != coset(ambiguous)
    assert ex_b[0] ^ ambiguous[0] == X0

    cycle_masks = tuple(map(mask, CYCLES))
    assert len(binary_basis(cycle_masks)) == 16
    cycle_table = {}
    for weight in range(3):
        for qs in combinations(range(20), weight):
            error = mask(qs)
            s = tuple((error & c).bit_count() & 1 for c in cycle_masks)
            assert s not in cycle_table
            cycle_table[s] = error
    assert len(cycle_table) == 211
    for t in range(32):
        assert all((cut(t, EDGES) & c).bit_count() % 2 == 0 for c in cycle_masks)
    def boundary(z, edges):
        return sum((sum((z >> q) & 1 for q, edge in enumerate(edges) if v in edge) % 2) << v
                   for v in range(5))

    for edges, tree in ((EDGES, (7, 11, 3, 0)), (SMALL_EDGES, (0, 1, 2, 3))):
        for g in range(32):
            if g.bit_count() % 2:
                continue
            z = mask(q for v, q in enumerate(tree, 1) if g >> v & 1)
            assert boundary(z, edges) == g
        # Arbitrary erroneous vertex reports cannot change the true U sign
        # by edge-Z feedforward. Later Gauss certification tests the true sign.
        for actual, reported in product(range(32), repeat=2):
            z = mask(q for v, q in enumerate(tree, 1) if reported >> v & 1)
            g = actual ^ boundary(z, edges)
            assert g.bit_count() % 2 == actual.bit_count() % 2

    # Pure cat bit-pattern repair; all lengths actually used, through 16 leaves.
    cat_cases = 0
    for m in range(1, 17):
        for bits in range(1 << m):
            d = [((bits >> j) ^ (bits >> (j+1))) & 1 for j in range(m-1)]
            r = 0
            for j, sign in enumerate(d):
                r |= (((r >> j) & 1) ^ sign) << (j+1)
            assert bits ^ r in (0, (1 << m) - 1)
            cat_cases += 1
    for f in range(3):
        for bad in combinations(range(9), f):
            assert any(not set(range(start, start+3)).intersection(bad) for start in range(7))

    baseline_graph, small_graph = graph_certificate(EDGES), graph_certificate(SMALL_EDGES)
    baseline_graph['radius_two_readout_words_checked'] = check_cut_decoding(EDGES, CYCLES)
    small_graph['radius_two_readout_words_checked'] = check_cut_decoding(SMALL_EDGES, SMALL_CYCLES)
    assert baseline_graph['cut_code_distance'] == 8
    assert small_graph['cut_code_distance'] == 5
    assert small_graph['edges'] == (5*5 + 1)//2  # degree lower bound for lambda >=5

    report = {
        "scope": "Exact algebraic certificates; not physical gadget simulation or exhaustive circuit-fault enumeration",
        "original_code_rank_each_type": 9,
        "pure_X_Z_logical_distance": 6,
        "source_full_rank_pure_error_solvers_checked": [20, 20, 25, 18],
        "fixed_two_block_sets": len(tables),
        "raw_Paulis_enumerated_per_fixed_set": 65536,
        "syndromes_per_fixed_set": 4096,
        "reachable_single_copy_syndromes": len(union),
        "stabilizer_cosets_per_syndrome_histogram": histogram,
        "joint_example": {
            "B_error": pauli_string(ex_b), "C_error": pauli_string(ex_c),
            "B_alone_cosets": 4, "joint_decoder_accepts": True,
            "chosen_B_correction": pauli_string(joint[0]),
            "chosen_C_correction": pauli_string(joint[1]),
        },
        "ambiguous_example_difference": "logical X0",
        "cycle_weight_at_most_two_masks_checked": len(cycle_table),
        "even_Gauss_sign_patterns_corrected": 16,
        "actual_reported_vertex_words_checked_per_graph": 1024,
        "cat_bit_patterns_checked": cat_cases,
        "nine_round_bad_subsets_checked": 46,
        "current_graph": baseline_graph,
        "appendix_graph": small_graph,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    print('Saved', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'output/c4-helix-reduced-rejection-certificates.json')
    main(parser.parse_args().output)
