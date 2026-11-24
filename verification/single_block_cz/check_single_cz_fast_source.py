"""Two-location audit of raw encoding plus zero-report source screening."""
import argparse
from collections import defaultdict
from functools import lru_cache
from itertools import combinations_with_replacement, product
import json
from pathlib import Path

from study_single_cz_source_windows import generators, source_meter, code
from check_optimized_extraction import signatures

CHECKS = list(generators())
GENS = code.source_generators()


def program(indices):
    pivots, cx = code.rref_encoder()
    ops = [("PREP", (q,)) for q in range(20)] + [("H", (q,)) for q in pivots]
    ops.extend(("CX", pair) for pair in cx)
    ops.append(("BOUNDARY", ()))
    for i in indices:
        axis, _, support = CHECKS[i]
        for op, qs in source_meter(axis, support):
            ops.append((op, tuple(20 if q == "s" else 21 if q == "f0" else int(q[1:]) for q in qs)))
    return ops + [("BOUNDARY", ())]


@lru_cache(None)
def syndrome(x,z):
    return sum((((x & gz).bit_count() + (z & gx).bit_count()) % 2) << j
               for j,(gx,gz) in enumerate(GENS))


def envelope():
    groups = [{syndrome(x << (4*v), z << (4*v)) for x,z in product(range(16), repeat=2)} for v in range(5)]
    single = set.union(*groups)
    return single, {a ^ b for a in single for b in single}


def audit(indices, one, two):
    ops = program(indices)
    nreports = sum(op == "MZ" for op,_ in ops)
    sigs, nloc = signatures(ops, (), (1 << 20)-1, (1 << nreports)-1)
    groups = defaultdict(set)
    for x,z,reports in sigs:
        groups[reports].add(syndrome(x,z))
    bad_one = sorted(groups[0] - one)
    pairs = 0
    bad_two = set()
    for group in groups.values():
        for a,b in combinations_with_replacement(group,2):
            pairs += 1
            if (a ^ b) not in two:
                bad_two.add(a ^ b)
    return {"checks": indices, "locations": nloc, "physical_signatures": len(sigs),
            "readout_words": len(groups), "equal_word_syndrome_pairs": pairs,
            "bad_one": bad_one, "bad_two": sorted(bad_two)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    single, two = envelope()
    history = []
    indices = list(range(20))
    while True:
        info = audit(indices, single, two)
        history.append(info)
        if not info["bad_one"] and not info["bad_two"]:
            break
        # Choose the next existing generator that detects most residual
        # syndromes missed by equal-word faults in the preceding circuit.
        bad = info["bad_one"] + info["bad_two"]
        j = max(range(20), key=lambda i: sum((s >> i) & 1 for s in bad))
        indices = indices + [j]
        if len(indices) > 40:
            raise AssertionError("Source screen search failed")
    args.output.write_text(json.dumps(history, indent=2) + "\n")
