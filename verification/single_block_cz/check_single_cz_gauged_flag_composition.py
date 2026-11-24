"""Replay a two-location tree4 fault and audit a conservative flag-recovery guard."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_screened_source import ScreenTree, noisy
from run_single_block_cz_controller import Reject
from single_cz_recovery import data_table, syndrome, remainder, m
from single_cz_flag_recovery import recovery_table

FAULTS = (
    {"context": "direct/vote/0/Z/5/block_Z", "operation": "CX", "targets": ["D3", "s"], "paulis": {"s": "Z"}},
    {"context": "direct/vote/0/X/1", "operation": "CX", "targets": ["s", "f0"], "paulis": {"s": "X"}},
)


class GuardedTree(ScreenTree):
    def direct_reference(self, prefix, flagged):
        row = super().direct_reference(prefix, flagged)
        if flagged:
            syn = sum(bit << i for i, bit in enumerate(row[:18]))
            if data_table().get(syn, {}).get("correction") is None:
                raise Reject("gauged_flag_ambiguous_two_block_class")
        return row


def shot(cls, subset):
    b = noisy.QuantumBackend(seed=4, model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES, "0")),
                             injections=[FAULTS[i] for i in subset])
    p = cls(b, **noisy.OPTIONS)
    r = p.run()
    assert len(b.injected_events) == len(subset)
    row = {"subset": subset, "faults": b.injected_events, "accepted": r["accepted"],
           "reason": r.get("reason"), "record": r["record"]}
    if r["accepted"]:
        row["diagnostic"] = noisy.diagnose(*b.state.sparse_output(b.data_labels))
    return row


def audit():
    # Every actual flag passed to direct_reference on this tree is an inner
    # data flag. Outer block-Z and root flags reject at the meter.
    counts = {}
    for axis in ("X","Z"):
        for j,support in enumerate(m.SUPPORTS[:5]):
            tab = recovery_table(axis,support,1,"compact_flags")
            agree = veto = 0
            for syn, old in tab.items():
                if old["correction"] is None:
                    continue
                full = data_table().get(syn, {}).get("correction")
                if full is None:
                    veto += 1
                    continue
                assert all(remainder(a ^ b) == 0 for a,b in zip(old["correction"], full))
                agree += 1
            counts[f"{axis}/{j}"] = {"old_unique_entries_kept": agree, "vetoed": veto}
    return counts


def noisy_pair(seed):
    rows = {}
    for cls in (ScreenTree,GuardedTree):
        with patch.object(noisy,"controller",lambda b,*_: cls(b,**noisy.OPTIONS)):
            rows[cls.__name__] = noisy.trial((None,seed,seed,noisy.RATES,False))
    old,new = rows.values()
    assert old["execution_status"] == new["execution_status"] == "completed"
    if new["reason"] != "gauged_flag_ambiguous_two_block_class":
        assert old["accepted"] == new["accepted"] and old.get("diagnostics") == new.get("diagnostics")
        assert old["metrics"]["gate_counts"] == new["metrics"]["gate_counts"]
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--shots", type=int, default=64)
    parser.add_argument("--seed", type=int, default=101000)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    runs = {cls.__name__: [shot(cls, sub) for n in range(3) for sub in combinations(range(2),n)]
            for cls in (ScreenTree,GuardedTree)}
    pair = runs["ScreenTree"][-1]
    assert pair["accepted"] and abs(pair["diagnostic"]["decoded_target_fidelity"] - 1/9) < 1e-12
    assert all(not r["accepted"] or r["diagnostic"]["decoded_target_within_tolerance"] for r in runs["ScreenTree"][:-1])
    assert runs["GuardedTree"][-1]["reason"] == "gauged_flag_ambiguous_two_block_class"
    reference = next(r["selected"] for r in pair["record"] if "direct_reference" in r)
    syn = sum(bit << i for i,bit in enumerate(reference[:18]))
    true_x, true_z = 224,233
    assert syndrome(true_x,true_z) == syn
    corr = next(r["correction"] for r in pair["record"] if "direct_recovery" in r)
    residual = (corr[1] & ((1 << 20)-1)) ^ true_z
    assert corr[0] == true_x and syndrome(0,residual) == 0 and remainder(residual) != 0
    assert [(residual & m.mask(x)).bit_count() % 2 for x in (m.X0,m.X1)] == [1,0]
    result = {"seed":4,"shots":runs,"full_syndrome":syn,"two_block_decision":data_table()[syn],
              "data_residual_Z_sites":[i for i in range(20) if residual >> i & 1],"table_audit":audit()}
    (args.folder / "witness.json").write_text(json.dumps(result,indent=2)+"\n")
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(6) as pool:
        for group in pool.map(noisy_pair,range(args.seed,args.seed+args.shots)):
            out.write(json.dumps(group)+"\n")


if __name__ == "__main__":
    main()
