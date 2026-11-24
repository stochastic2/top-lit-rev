"""Finite CSS-sector and compact meter checks for the shortened Gauss vote."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src/single_block_cz"), str(ROOT / "verification/shared")]

import c4_helix_single_block_cz as m
import check_single_cz_terminal_screen as terminal
from check_optimized_extraction import signatures
from single_cz_compact_checks import compact_pauli_program
from single_cz_hybrid_faults import row_basis


def sector_certificate():
    checks = tuple(map(m.mask, m.SUPPORTS))
    assert sum(checks[:5]) == (1 << 20) - 1
    pairs = list(combinations(range(5), 2))
    tested = 0
    zero = 0
    cones = []
    for v, w in pairs:
        block = (15 << (4 * v)) | (15 << (4 * w))
        possible_x = [x << (4 * v) | y << (4 * w) for x, y in product(range(16), repeat=2)]
        allowed_x = [x for x in possible_x if terminal.syndrome(x, 0) == 0]
        assert set(allowed_x) == {0, checks[v], checks[w], block}
        tested += len(possible_x)
        for x in allowed_x:
            for z in possible_x:
                inner_x_parity = (terminal.syndrome(x, z) >> 9 & 31).bit_count() % 2
                assert inner_x_parity == z.bit_count() % 2
                # Right-multiplying by the X stabilizer cancels x up to a scalar.
                assert x in terminal.STABILIZERS
                zero += 1
        cones.append(block)
    subset_count = Counter()
    for size in range(6, 10):
        for subset in combinations(checks, size):
            if all(len(row_basis(check & cone for check in subset)) == 6 for cone in cones):
                subset_count[str(size)] += 1
    assert subset_count == {"9": 1}
    return {"tested_x_masks_on_fixed_block_pairs": tested,
            "tested_zero_z_syndrome_x_z_pairs": zero,
            "original_Z_subsets_preserving_each_pair_kernel": dict(subset_count),
            "scope": "a clean vote on Pauli terms supported on up to two inner blocks in diagnostic coordinates"}


def compact_screen(order=None):
    order = terminal.screen_checks() if order is None else order
    ops = []
    readouts = []
    measured = 0
    for axis, j in order:
        support = m.SUPPORTS[j]
        roles = [*support, 20, 21, 22, 23, 24]
        for op, qs in compact_pauli_program(axis, len(support)):
            targets = tuple(roles[q] for q in qs)
            ops.append((op, targets))
            if op == "MZ":
                if targets == (20,):
                    readouts.append((axis, j, measured))
                measured += 1
    return ops + [("BOUNDARY", ())], tuple(readouts)


def compact_root_opaque_certificate():
    # The first eight ports are root data and its four tree edges. Chords
    # are after all flag windows. A W port is an opaque local involution.
    helper = 10
    labels = list(range(8)) + [helper, 11, 12, 13, 14]
    program = [(op, tuple(labels[q] for q in qs)) for op, qs in compact_pauli_program("X", 8)]
    assert program[-2:] == [("H", (helper,)), ("MZ", (helper,))]
    program[-2:-2] = [("CX", (helper, 8)), ("CX", (helper, 9))]
    sigs, locations = signatures(program, range(10), (1 << 10) - 1, 15)
    unflagged = 0
    pair_count = 0
    for x, z, f in sigs:
        if not f:
            weight = min(((x | z) & 255).bit_count(), (((x ^ 255) | z) & 255).bit_count())
            assert weight <= 1
            unflagged += 1
    for x, z, f in sigs:
        for a, b, g in sigs:
            if f == g:
                xx, zz = x ^ a, z ^ b
                weight = min(((xx | zz) & 255).bit_count(), (((xx ^ 255) | zz) & 255).bit_count())
                assert weight <= 2
                pair_count += 1
    return {"locations_in_opaque_Clifford_projection": locations, "zero_flag_signatures": unflagged,
            "equal_flag_pairs": pair_count, "scope": "support on eight protected ports modulo full measured product, arbitrary chord support"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"shortened_vote": sector_certificate(), "compact_root": compact_root_opaque_certificate()}
    try:
        with patch.object(terminal, "screen_program", compact_screen):
            screen = terminal.audit()
    except AssertionError as error:
        screen = {"verified": False, "counterexample": error.args}
    result["compact_terminal_screen"] = screen
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
