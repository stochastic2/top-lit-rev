"""Forward binary audit of the physical GHZ prefix, before the W ports."""
from collections import Counter
from itertools import combinations_with_replacement
import json

from trace_audit import HERE, ScreenCat, trace

FULL = (1 << 20) - 1


def ghz_prefix(cls=ScreenCat, settings=None):
    clean, _ = trace(cls, settings)
    gates = [tuple(gate) for context, gate in clean["gates"] if context == "terminal/0/U"]
    # Verification finishes before the first controlled-W basis change.
    split = next(j for j, (op, roles) in enumerate(gates) if op in ("T", "TDG"))
    assert gates[split + 1] == ("CX", ("L0", "D0"))
    return gates[:split]


def signatures(program):
    live = set()
    locations = []
    for j, (op, roles) in enumerate(program):
        for q in sorted(live - set(roles)):
            locations.append((j, "idle", (q,)))
        if op == "PREP":
            live.add(roles[0])
        if op == "MZ":
            live.remove(roles[0])
        locations.append((j, "report" if op == "MZ" else "after", roles))
    labels = {f"L{q}": q for q in range(20)} | {"w": 20}
    output = {(0, 0): None}
    for j, timing, roles in locations:
        for code in range(1, 1 << len(roles)):
            wires = tuple(q for i, q in enumerate(roles) if code >> i & 1)
            mask = sum(1 << labels[q] for q in wires) if timing != "report" else 0
            reports = 0
            readout = 0
            for k, (op, qs) in enumerate(program):
                if op == "MZ":
                    if k > j or (k == j and timing in ("idle", "report")):
                        bit = int(k == j and timing == "report") | (mask >> labels[qs[0]] & 1)
                        reports |= bit << readout
                        mask &= ~(1 << labels[qs[0]])
                    readout += 1
                elif k > j or (k == j and timing == "idle"):
                    if op == "CX":
                        c, t = map(labels.__getitem__, qs)
                        mask ^= (mask >> c & 1) << t
                    elif op == "H":
                        # An X after prep or before the initial H becomes phase.
                        # The equally available Z basis component becomes X.
                        # The two signatures are represented by 0 and this bit.
                        assert qs == ("L0",)
            witness = {"timing": timing, "context": "terminal/0/U", "operation": program[j][0],
                       "targets": program[j][1], "paulis": {q: "X" for q in wires} if timing != "report" else {},
                       "flip_report": timing == "report", "prefix_gate_index": j}
            h = next(k for k, (op, _) in enumerate(program) if op == "H")
            if j < h and "L0" in wires:
                witness["paulis"]["L0"] = "Z"
            output.setdefault((mask, reports), witness)
    return output, len(locations)


def block_weight(mask):
    return sum(bool(mask & (15 << (4*v))) for v in range(5))


def syndrome_certificate(program):
    sig, locations = signatures(program)
    bounds = {}
    for size, cases in ((1, [((x, f), (0, 0)) for x, f in sig]),
                        (2, combinations_with_replacement(sig, 2))):
        dist = Counter()
        largest = None
        for (x, f), (y, g) in cases:
            if f != g:
                continue
            mask = x ^ y
            wt = min(mask.bit_count(), (mask ^ FULL).bit_count())
            blocks = min(block_weight(mask), block_weight(mask ^ FULL))
            dist[(wt, blocks)] += 1
            if largest is None or (wt, blocks) > (largest["site_cost"], largest["block_cost"]):
                largest = dict(site_cost=wt, block_cost=blocks, mask=mask, faults=[sig[x, f], sig[y, g]])
        bounds[size] = dict(distribution={str(k): count for k, count in sorted(dist.items())}, largest=largest,
                            max_blocks=max(k[1] for k in dist), max_sites=max(k[0] for k in dist))
    return dict(locations=locations, signatures=len(sig), bounds=bounds)


if __name__ == "__main__":
    result = syndrome_certificate(ghz_prefix())
    print(json.dumps(result, indent=2))
    (HERE / "cat_envelope.json").write_text(json.dumps(result, indent=2) + "\n")
