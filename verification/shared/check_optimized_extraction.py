"""Finite Clifford/Pauli locality certificates for the optimized gadgets.

Standard library only. All nonidentity Pauli faults on each operation's
participants, and single-qubit idles, are propagated. Equal signatures
are merged; all pairs of signatures are tested, including an overestimate
that permits two faults at the same location. Not a whole-factory audit.
"""

from collections import defaultdict
from itertools import product
from pathlib import Path
import argparse
import json


def source_program(blocks, positions_per_block, axis):
    n = blocks * positions_per_block
    ops = [("PREP", (n+j,)) for j in range(blocks)] + [("H", (n,))]
    ops += [("CX", (n, n+j)) for j in range(1, blocks)]
    ops += [("CX" if axis == "X" else "CZ", (n+j, j*positions_per_block + i))
            for i in range(positions_per_block) for j in range(blocks)]
    ops += [("CX", (n, n+j)) for j in reversed(range(1, blocks))]
    ops += [("MZ", (n+j,)) for j in range(1, blocks)]
    return ops + [("H", (n,)), ("MZ", (n,))]


def verified_cat_program(m):
    w = m
    ops = [("PREP", (j,)) for j in range(m)] + [("H", (0,))]
    ops += [("CX", (j, j+1)) for j in range(m-1)]
    for _ in range(2):
        for j in range(m-1):
            ops += [("PREP", (w,)), ("CX", (j, w)), ("CX", (j+1, w)), ("MZ", (w,))]
    return ops


def propagate(x, z, ops, start):
    """Ignore global Pauli phase, retaining every measured X-bit flip."""
    reports = 0
    meter_index = sum(name == "MZ" for name, _ in ops[:start])
    for name, qs in ops[start:]:
        if name == "H":
            q = qs[0]
            if ((x >> q) ^ (z >> q)) & 1:
                x ^= 1 << q
                z ^= 1 << q
        elif name == "CX":
            c, t = qs
            x ^= ((x >> c) & 1) << t
            z ^= ((z >> t) & 1) << c
        elif name == "CZ":
            c, t = qs
            z ^= (((x >> t) & 1) << c) | (((x >> c) & 1) << t)
        elif name == "PREP":
            q = qs[0]
            x &= ~(1 << q)
            z &= ~(1 << q)
        elif name == "MZ":
            q = qs[0]
            reports |= ((x >> q) & 1) << meter_index
            meter_index += 1
            x &= ~(1 << q)
            z &= ~(1 << q)
    return x, z, reports


def signatures(ops, initially_live, retain_mask, report_mask):
    live = set(initially_live)
    result = set()
    locations = 0
    for i, (name, qs) in enumerate(ops):
        # Idles belong to the interval immediately before the operation.
        for q in live.difference(qs):
            locations += 1
            for a, b in ((1, 0), (0, 1), (1, 1)):
                x, z, reports = propagate(a << q, b << q, ops, i)
                result.add((x & retain_mask, z & retain_mask, reports & report_mask))
        locations += 1
        for ps in product(range(4), repeat=len(qs)):
            if not any(ps):
                continue
            x = sum((p & 1) << q for p, q in zip(ps, qs))
            z = sum((p >> 1) << q for p, q in zip(ps, qs))
            # A destructive meter's quantum/report error acts BEFORE it.
            # A report flip is equivalent to an X here and is included.
            start = i if name == "MZ" else i+1
            x, z, reports = propagate(x, z, ops, start)
            result.add((x & retain_mask, z & retain_mask, reports & report_mask))
        if name == "PREP":
            live.update(qs)
        elif name == "MZ":
            live.difference_update(qs)
    return result, locations


def source_certificate(blocks, k, axis):
    n = blocks*k
    full = (1 << n) - 1
    ops = source_program(blocks, k, axis)
    cases, locations = signatures(ops, range(n), full, (1 << (blocks-1)) - 1)

    def cost(x, z):
        def occupied(a, b):
            return sum(bool(((a | b) >> (j*k)) & ((1 << k)-1)) for j in range(blocks))
        return min(occupied(x, z), occupied(x ^ full if axis == "X" else x,
                                           z ^ full if axis == "Z" else z))

    assert all(flags or cost(x, z) <= 1 for x, z, flags in cases)
    same_flags = defaultdict(list)
    for x, z, flags in cases:
        same_flags[flags].append((x, z))
    checked_pairs = 0
    for group in same_flags.values():
        for a, b in product(group, repeat=2):
            assert cost(a[0] ^ b[0], a[1] ^ b[1]) <= 2
            checked_pairs += 1
    return {"blocks": blocks, "positions_per_block": k, "axis": axis,
            "physical_and_idle_locations": locations, "single_fault_signatures": len(cases),
            "zero_flag_pair_combinations": checked_pairs,
            "zero_flag_single_fault_block_bound": 1, "zero_flag_two_fault_block_bound": 2}


def two_scan_certificate(m):
    ops = verified_cat_program(m)
    full = (1 << m) - 1
    cases, locations = signatures(ops, (), full, (1 << (2*(m-1))) - 1)
    # Phase errors do not affect this bit-spread certificate. They remain
    # explicitly allowed in aI+bQ in the analytical proof.
    cases = {(x, reports) for x, _, reports in cases}
    assert all(reports or min(x.bit_count(), m-x.bit_count()) <= 1 for x, reports in cases)
    same_reports = defaultdict(list)
    for x, reports in cases:
        same_reports[reports].append(x)
    pairs = 0
    for group in same_reports.values():
        for a, b in product(group, repeat=2):
            x = a ^ b
            assert min(x.bit_count(), m-x.bit_count()) <= 2
            pairs += 1
    return {"leaves": m, "physical_and_idle_locations": locations,
            "bit_report_signatures": len(cases), "zero_report_pair_combinations": pairs,
            "accepted_single_fault_leaf_bound": 1, "accepted_two_fault_leaf_bound": 2}


def audit():
    return {"scope": "Gadget-local Pauli/Clifford certificates, not exhaustive factory fault enumeration",
            "source_shapes": [source_certificate(m, k, axis) for m, k in ((1, 4), (3, 2), (4, 2))
                              for axis in "XZ"],
            "two_initial_zero_scans": [two_scan_certificate(m) for m in range(2, 17)]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] /
                        "output/c4-helix-optimized-extraction-certificates.json")
    args = parser.parse_args()
    report = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Verified {len(report['source_shapes'])} flagged-source shapes and "
          f"{len(report['two_initial_zero_scans'])} two-scan cat sizes; saved {args.output}")
