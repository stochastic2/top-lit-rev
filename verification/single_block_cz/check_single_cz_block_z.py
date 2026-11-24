"""Certify the one-flag outer Z meter for the charged-block envelope."""

import argparse
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src/single_block_cz"), str(ROOT / "verification/shared")]

import c4_helix_single_block_cz as m
from check_optimized_extraction import signatures
from single_cz_block_z_pilot import block_z_program


def certificate(support):
    roles = [f"D{q}" for q in support] + ["s", "f0"]
    gates = block_z_program(support)
    gates = [(op, tuple(roles.index(q) for q in qs)) for op, qs in gates] + [("BOUNDARY", ())]
    cases, locations = signatures(gates, range(8), 255, 1)
    cases.add((0, 0, 0))

    def blocks(x, z):
        return min(sum(bool((x | phase) & (3 << j)) for j in range(0, 8, 2)) for phase in (z, z ^ 255))

    for x, z, flag in cases:
        assert flag or blocks(x, z) <= 1
    pairs = 0
    for (x, z, f), (a, b, g) in combinations(cases, 2):
        if f == g:
            assert blocks(x ^ a, z ^ b) <= 2
            pairs += 1
    return {"locations": locations, "signatures": len(cases), "equal_flag_distinct_signature_pairs": pairs,
            "CX": sum(op == "CX" for op, _ in gates), "basis_support": list(support)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = {"checks": [certificate(support) for support in m.SUPPORTS[5:]],
              "zero_flag_bound": "up to one charged inner block per fault modulo the measured stabilizer",
              "nonzero_flag_policy": "reject in the pilot"}
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
