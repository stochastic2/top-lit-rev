"""Check for a common output block support for all Pauli components at fixed faulty locations."""
import argparse
from collections import Counter, defaultdict
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path

from check_single_cz_fast_source import program, syndrome


def location_classes(ops):
    # Columns map a Pauli at this time to the final source syndrome (low
    # 20 bits) and measured flips (high bits). Pull them backwards once.
    xs = [syndrome(1 << q,0) if q < 20 else 0 for q in range(22)]
    zs = [syndrome(0,1 << q) if q < 20 else 0 for q in range(22)]
    readouts = sum(op == "MZ" for op,_ in ops)
    live = set(range(20))
    classes = Counter()

    def add(wires):
        effects = {0}
        for q in wires:
            effects = {a ^ b for a in effects for b in (0, xs[q], zs[q], xs[q]^zs[q])}
        classes[tuple(sorted(effects))] += 1

    for op,qs in reversed(ops):
        if op == "MZ":
            q, = qs
            readouts -= 1
            xs[q],zs[q] = 1 << (20+readouts),0
            live.add(q)
        add(qs)
        if op == "H":
            q, = qs
            xs[q],zs[q] = zs[q],xs[q]
        elif op == "CX":
            c,t = qs
            xs[c] ^= xs[t]
            zs[t] ^= zs[c]
        elif op == "PREP":
            q, = qs
            xs[q] = zs[q] = 0
            live.remove(q)
        for q in live.difference(qs):
            add((q,))
    assert not live and readouts == 0
    return classes


def support_tables():
    singles = [{syndrome(x << (4*v), z << (4*v)) for x,z in product(range(16),repeat=2)} for v in range(5)]
    masks = defaultdict(int)
    for j,(a,b) in enumerate(combinations(range(5),2)):
        for x in singles[a]:
            for y in singles[b]:
                masks[x ^ y] |= 1 << j
    return singles, masks


def certify(indices, singles, masks):
    low = (1 << 20) - 1
    classes = location_classes(program(indices))
    zero_words = []
    for location in classes:
        group = defaultdict(list)
        for e in location:
            group[e >> 20].append(e & low)
        if not any(set(group[0]) <= s for s in singles):
            return {"all_have_common_support": False, "single_failure": group[0]}
        zero_words.append(group)
    count = 0
    failure = None
    for a,b in combinations_with_replacement(zero_words,2):
        allowed = 1023
        for w in a.keys() & b.keys():
            for x in a[w]:
                for y in b[w]:
                    allowed &= masks[x ^ y]
        count += 1
        if not allowed:
            failure = [a,b]
            break
    return {"physical_locations":sum(classes.values()), "location_classes":len(classes),
                                      "tested_location_class_pairs":count, "all_have_common_support": failure is None,
                                      "first_common_support_failure":failure}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = certify(list(range(20)), *support_tables())
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
