"""Local Pauli audit of compact terminal gadgets, including idle/report faults.

Checks PHYSICAL weight per fault modulo the measured check, rather than
only the inner-block bound used by the source gadgets. Nonzero flags are
not certified here. This is not a whole-factory fault-pair enumeration.
"""

import argparse
from collections import defaultdict
from itertools import product
import json
from pathlib import Path

from check_optimized_extraction import signatures
from c4_helix_compact_terminal import compact_terminal_program, flag_repair_pattern


def terminal_program(weight, axis):
    return compact_terminal_program(weight, axis)


def certificate(weight, axis):
    flags = 1 if weight == 4 else 5
    ops = terminal_program(weight, axis)
    full = (1 << weight)-1
    cases, locations = signatures(ops, range(weight), full, (1 << flags)-1)

    def cost(x, z):
        return min((x | z).bit_count(), ((x ^ full if axis == "X" else x) |
                                        (z ^ full if axis == "Z" else z)).bit_count())

    for x, z, f in cases:
        if not f and cost(x, z) > 1:
            raise AssertionError(("single", weight, axis, x, z, f, cost(x, z)))
    groups = defaultdict(list)
    for x, z, f in cases:
        groups[f].append((x, z))
    checked = 0
    for group in groups.values():
        for a, b in product(group, repeat=2):
            if cost(a[0]^b[0], a[1]^b[1]) > 2:
                raise AssertionError(("pair", weight, axis, a, b, cost(a[0]^b[0], a[1]^b[1])))
            checked += 1
    return {"weight": weight, "axis": axis, "single_fault_signatures": len(cases),
            "physical_and_idle_locations": locations, "zero_flag_pairs_checked": checked,
            "accepted_single_fault_physical_weight_bound": 1,
            "accepted_two_fault_physical_weight_bound": 2,
            "two_qubit_gates": sum(op in ("CX", "CZ") for op, _ in ops),
            "meters": sum(op == "MZ" for op, _ in ops)}


def audit():
    return {"verified": True, "scope": "Local zero-flag physical spread and flag-conditioned block repair",
            "shapes": [certificate(w, a) for w in (4, 8) for a in "XZ"],
            "flag_repairs": [repair_certificate(w, a) for w in (4, 8) for a in "XZ"]}


def repair_certificate(weight, axis):
    flag_count = 1 if weight == 4 else 5
    cases, _ = signatures(terminal_program(weight, axis), range(weight), (1 << weight)-1, (1 << flag_count)-1)
    paths = defaultdict(dict)
    for x, z, f in cases:
        paths[f][(x, z)] = 1
    for a, b in product(cases, repeat=2):
        f, e = a[2]^b[2], (a[0]^b[0], a[1]^b[1])
        paths[f][e] = min(paths[f].get(e, 2), 2)
    full = (1 << weight)-1

    def occupied(x, z):
        k = 4 if weight == 4 else 2
        return sum(bool(((x | z) >> (j*k)) & ((1 << k)-1)) for j in range(weight//k))

    rows = []
    for f, errors in sorted(paths.items()):
        flags = tuple((f >> j) & 1 for j in range(flag_count))
        positions = flag_repair_pattern(weight, flags)
        correction = sum(1 << q for q in positions)
        for (x, z), budget in errors.items():
            xx, zz = x ^ (correction if axis == "X" else 0), z ^ (correction if axis == "Z" else 0)
            cost = min(occupied(xx, zz), occupied(xx ^ full if axis == "X" else xx,
                                               zz ^ full if axis == "Z" else zz))
            if cost > budget:
                raise AssertionError(("flag repair", weight, axis, f, x, z, budget, cost))
        rows.append({"flag_word": f, "repair_positions": positions, "distinct_data_errors_checked": len(errors)})
    return {"weight": weight, "axis": axis, "reachable_flag_words": len(paths),
            "all_single_and_two_fault_pairs_checked": len(cases)**2,
            "repaired_block_bound_per_fault": 1, "flags": rows}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = audit()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({**result, "flag_repairs": [{k: v for k, v in c.items() if k != "flags"}
                                               for c in result["flag_repairs"]]}, indent=2))


if __name__ == "__main__":
    main()
