"""Remove flags on block-confined routine inner meters; paired noisy comparison."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations_with_replacement
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_vote_budget import BudgetPilot, noisy
import c4_helix_single_block_cz as code
from check_single_cz_short_gauss_vote import signatures
from check_single_cz_short_gauss_witnesses import shot, idle_at_vote_start, report


def inner_program(axis, sites):
    ops = [("PREP", ("s",))]
    if axis == "X":
        ops.append(("H", ("s",)))
    for q in sites:
        ops.append(("CX", ("s", q) if axis == "X" else (q, "s")))
    if axis == "X":
        ops.append(("H", ("s",)))
    return ops + [("MZ", ("s",))]


class BareInnerPilot(BudgetPilot):
    def check(self, name, ports):
        fields = name.split("/")
        if (len(fields) == 5 and fields[:2] == ["direct", "vote"] and fields[2].isdigit()
                and fields[3] in ("X", "Z") and int(fields[4]) < 5):
            axis = fields[3]
            assert tuple(ports) == tuple((axis, f"D{q}") for q in code.SUPPORTS[int(fields[4])])
            return self.direct_meter(name, inner_program(axis, [q for _, q in ports]))
        return super().check(name, ports)

    def prep(self, q):
        super().prep(q)
        fields = self.b.context.split("/")
        if (q == "s" and len(fields) == 5 and fields[:2] == ["direct", "vote"]
                and fields[3] == "Z" and int(fields[4]) < 5 and hasattr(self.b, "absorb_parity_helper")):
            self.b.absorb_parity_helper(q)


def audit():
    audits = {}
    for axis in ("Z", "X"):
        for j, support in enumerate(code.SUPPORTS[:5]):
            program = [(op, tuple(20 if q == "s" else q for q in qs))
                       for op, qs in inner_program(axis, support)]
            sigs, locations = signatures(program, range(20), (1 << 20) - 1, 1)
            masks = {sum(1 << v for v in range(5) if (x | z) & (15 << (4*v))) for x,z,_ in sigs}
            assert all(mask.bit_count() <= 1 for mask in masks)
            assert all((a | b).bit_count() <= 2 for a,b in combinations_with_replacement(masks, 2))
            audits[f"{axis}/{j}"] = {"locations_with_data_idles": locations, "signatures": len(sigs)}
    # A single syndrome-qubit hook can corrupt two sites on one block.
    hook = {"context": "direct/vote/0/X/1", "operation": "CX", "targets": ["s", "D5"],
            "paulis": {"s": "X"}}
    witnesses = {"clean": shot(2, [], BareInnerPilot), "one_hook": shot(2, [hook], BareInnerPilot),
                 "sign": shot(2, [idle_at_vote_start("D0", "Z")], BareInnerPilot),
                 "tree_report": shot(2, [report("edge_readout", "A1")], BareInnerPilot)}
    assert witnesses["clean"]["accepted"] and witnesses["sign"]["accepted"]
    assert witnesses["tree_report"]["reason"] == "data_ambiguity"
    clean = {}
    for cls in (BudgetPilot, BareInnerPilot):
        rec = noisy.RecordBackend()
        assert cls(rec, **noisy.OPTIONS).run()["accepted"]
        clean[cls.__name__] = Counter(op for op, _ in rec.ops)
    assert clean["BudgetPilot"]["CX"] - clean["BareInnerPilot"]["CX"] == 40
    return {"meters": audits, "clean_gates": clean, "witnesses": witnesses}


def trial(seed):
    result = {}
    for cls in (BudgetPilot, BareInnerPilot):
        with patch.object(noisy, "controller", lambda backend, *_: cls(backend, **noisy.OPTIONS)):
            result[cls.__name__] = noisy.trial((None, seed, seed, noisy.RATES, False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=92000)
    parser.add_argument("--shots", type=int, default=200)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    (args.folder / "audit.json").write_text(json.dumps(audit(), indent=2) + "\n")
    with (args.folder / "shots.jsonl").open("x") as stream, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(trial, range(args.seed, args.seed + args.shots)):
            stream.write(json.dumps(row) + "\n")
            stream.flush()
