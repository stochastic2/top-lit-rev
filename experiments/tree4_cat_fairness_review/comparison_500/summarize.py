"""Validate the ledger and summarize completed shots and seed-paired yield differences."""
from collections import Counter
import json
from math import comb, sqrt
from statistics import fmean, stdev

from run import OUT, SEEDS, noisy


def wilson(k, n):
    z = 1.95996398454
    p = k / n
    a = p + z*z / (2*n)
    b = z * sqrt(p*(1-p)/n + z*z/(4*n*n))
    return [(a-b)/(1+z*z/n), (a+b)/(1+z*z/n)]


def summarize():
    groups = [json.loads(line) for line in (OUT / "shots.jsonl").read_text().splitlines()]
    assert len(groups) == len(SEEDS)
    arms = ("BareInnerTree", "LeanResourceCat", "BlockCat", "PostBlockCat")
    for seed, group in zip(SEEDS, groups):
        assert set(group) == set(arms)
        assert all(r["seed"] == seed and r["status"] == "completed" for r in group.values())

    result = {"seed_range_inclusive": [SEEDS.start, SEEDS.stop-1], "noise": noisy.RATES, "arms": {}, "vs_tree": {}}
    for arm in arms:
        rows = [g[arm] for g in groups]
        diag = [r["diagnostics"] for r in rows if r["accepted"]]
        k, n = len(diag), len(rows)
        fidelity = [d["decoded_target_fidelity"] for d in diag]
        matches = sum(d["decoded_target_within_tolerance"] for d in diag)
        gates = Counter()
        for row in rows:
            gates.update(row["metrics"]["gate_counts"])
        result["arms"][arm] = dict(attempts=n, accepted=k, acceptance=k/n, acceptance_wilson95=wilson(k,n),
            accepted_matches=matches, mean_decoded_fidelity=fmean(fidelity), min_decoded_fidelity=min(fidelity),
            mean_raw_physical_fidelity=fmean(d["raw_physical_target_fidelity"] for d in diag),
            cx_per_accept=gates["CX"]/k, t_per_accept=(gates["T"]+gates["TDG"])/k,
            mismatches=[r["seed"] for r in rows if r["accepted"] and not r["diagnostics"]["decoded_target_within_tolerance"]])
        if arm != arms[0]:
            diffs = [int(g[arm]["accepted"]) - int(g[arms[0]]["accepted"]) for g in groups]
            wins, losses = diffs.count(1), diffs.count(-1)
            m = wins + losses
            p = min(1, 2*sum(comb(m,i) for i in range(min(wins,losses)+1)) / 2**m)
            delta, half = fmean(diffs), 1.96 * stdev(diffs) / sqrt(n)
            result["vs_tree"][arm] = dict(difference=delta, paired_normal95=[delta-half,delta+half],
                                         cat_only=wins, tree_only=losses, exact_mcnemar_p=p)
    return result


if __name__ == "__main__":
    report = json.dumps(summarize(), indent=2)
    (OUT / "summary.json").write_text(report+"\n")
    print(report)
