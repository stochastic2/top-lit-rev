"""Validate fixed cohorts and compare conditional fidelity, acceptance and T cost."""
from collections import Counter
from hashlib import sha256
import json
from math import fsum

from scipy.stats import binomtest

from run_replication import HERE, PRIOR, ROOT, SEEDS, SelectiveTree
from run_other_arms import ARMS


def read_ledger(filename, names=None):
    columns = {name: [] for name in names or (SelectiveTree.__name__,)}
    with (HERE / filename).open() as stream:
        for seed, line in zip(SEEDS, stream, strict=True):
            rows = json.loads(line)
            if names is None:
                rows = {SelectiveTree.__name__: rows}
            assert rows.keys() == columns.keys()
            for name, row in rows.items():
                assert row["seed"] == seed, (name, seed, row["seed"])
                assert row["status"] == "completed", (name, seed, row.get("detail"))
                assert row["accepted"] == ("diagnostics" in row)
                columns[name].append(row)
    return columns


def summarize(rows):
    accepted = [r for r in rows if r["accepted"]]
    matches = 0
    misses = []
    for row in accepted:
        diagnostic = row["diagnostics"]
        fidelity = diagnostic["decoded_target_fidelity"]
        matches_target = diagnostic["decoded_target_within_tolerance"]
        assert matches_target == (abs(1 - fidelity) <= 1e-10)
        if matches_target:
            matches += 1
        else:
            misses.append(dict(seed=row["seed"], fidelity=fidelity,
                               sampled_faults=row["metrics"]["sampled_noise_events"]))
    gates = Counter()
    for row in rows:
        gates.update(row["metrics"]["gate_counts"])
    t_total = gates["T"] + gates["TDG"]
    upper_miss = binomtest(len(misses), len(accepted), alternative="less").proportion_ci(.95).high
    acceptance_ci = binomtest(len(accepted), len(rows)).proportion_ci(.95, method="wilson")
    return dict(attempts=len(rows), accepted=len(accepted), matched=matches,
                acceptance=len(accepted)/len(rows), acceptance_wilson_95=[acceptance_ci.low, acceptance_ci.high],
                mean_decoded_fidelity=fsum(row["diagnostics"]["decoded_target_fidelity"] for row in accepted)/len(accepted),
                fidelity_conservative_lower_95=1-upper_miss-1e-10,
                T_total=t_total, T_per_match=t_total/matches, CX_per_match=gates["CX"]/matches,
                misses=misses, rejection_reasons=dict(Counter(r["reason"] for r in rows if not r["accepted"])))


def main():
    sources = ("manifest.json", "additional_arms_manifest.json")
    for name in sources:
        manifest = json.loads((HERE / name).read_text())
        for path, expected in manifest["source_sha256"].items():
            assert sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    names = tuple(cls.__name__ for cls in ARMS)
    rows = read_ledger("shots.jsonl") | read_ledger("additional_arms_shots.jsonl", names)
    for ordinary, capped in zip(rows["SelectiveCat"], rows["BudgetCat"], strict=True):
        counts = capped["metrics"]["gate_counts"]
        assert counts.get("T", 0) + counts.get("TDG", 0) <= 120
        if capped["reason"] == "postselection_T_budget":
            assert not capped["accepted"]
        else:
            assert (ordinary["accepted"], ordinary["reason"], ordinary.get("diagnostics")) == (
                capped["accepted"], capped["reason"], capped.get("diagnostics"))
            assert ordinary["metrics"]["gate_counts"] == counts
    prior_primary = json.loads((PRIOR / "summary.json").read_text())
    prior_budget = json.loads((PRIOR / "budget_summary.json").read_text())
    comparisons = {"SelectiveTree": (prior_primary["Tree"]["moderate"], 6000),
                   "SelectiveCompact": (prior_primary["Compact"]["moderate"], 6000),
                   "SelectiveCat": (prior_primary["Cat"]["moderate"], 6000),
                   "BudgetCat": (prior_budget["Cat"]["budget"], 4000)}
    output = {}
    for name, group in rows.items():
        current = summarize(group)
        old, size = comparisons[name]
        current["previous"] = {"attempts": size, **{
            key: old[key] for key in ("accepted", "matched", "acceptance", "mean_decoded_fidelity", "T_per_match", "misses")}}
        output[name] = current
        print(name, *(current[key] for key in ("accepted", "matched", "mean_decoded_fidelity",
                    "fidelity_conservative_lower_95", "T_per_match", "misses")))
    (HERE / "summary.json").write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
