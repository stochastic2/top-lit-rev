"""Summarize four disjoint optimization cohorts, including all charged work."""
import argparse
from math import comb
import json
from random import Random
from pathlib import Path

from summarize_single_cz_vote_budget import stats, rows, ROOT
from study_single_cz_vote_budget import noisy


def pair(left, right):
    def matches(row):
        return row.get("diagnostics", {}).get("decoded_target_within_tolerance", False)
    wins = sum(matches(a) and not matches(b) for a,b in zip(left,right))
    losses = sum(matches(b) and not matches(a) for a,b in zip(left,right))
    discordant = wins + losses
    p = min(1, 2 * sum(comb(discordant,j) for j in range(min(wins,losses)+1)) / 2**discordant)
    return {"left_only_matches": wins, "right_only_matches":losses, "exact_two_sided_p":p}


def cost_intervals(arms, pairs):
    # Individual seeds are the independent units. Resample the entire row
    # to retain covariance both across arms and between gates and acceptance.
    rng = Random(20261123)
    n = len(next(iter(arms.values())))
    columns = {}
    for name in {k for pair_names in pairs for k in pair_names}:
        rs = arms[name]
        assert all(r["execution_status"] == "completed" for r in rs)
        gates = [r["metrics"]["gate_counts"] for r in rs]
        columns[name] = ([g["CX"] for g in gates],
                         [g.get("T",0) + g.get("TDG",0) for g in gates],
                         [int(r.get("diagnostics",{}).get("decoded_target_within_tolerance",False)) for r in rs])
    draws = {pair_names:[[],[]] for pair_names in pairs}
    for _ in range(4000):
        sample = rng.choices(range(n),k=n)
        costs = {}
        for name, (cx,t,matches) in columns.items():
            m = sum(matches[j] for j in sample)
            costs[name] = (sum(cx[j] for j in sample)/m, sum(t[j] for j in sample)/m)
        for a,b in pairs:
            for j in range(2):
                draws[(a,b)][j].append(100 * (1 - costs[a][j] / costs[b][j]))
    return {f"{a} vs {b}": {axis:[sorted(v)[99],sorted(v)[3899]] for axis,v in zip(("CX","T_TDG"), columns)}
            for (a,b),columns in draws.items()}


def unpack(source):
    return {k:[row[k] for row in source] for k in source[0]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=ROOT / "output", type=Path)
    args = parser.parse_args()
    def load(name):
        return rows(args.root / name / "shots.jsonl")
    pilot = unpack(load("cz-bare-inner-92000"))
    pilot.update(filtered=load("cz-entry-filter-92000"),cat=load("cz-bare-inner-cat-92000/cat-five-parity"))
    windows = unpack(load("cz-source-windows-93000")) | unpack(load("cz-common-source-93000"))
    fast = unpack(load("cz-fast-source-95000"))
    subset = unpack(load("cz-screened-source-96000"))
    subset["compact"] = load("cz-screened-compact-96000")
    cohorts = [(92000,200,pilot),(93000,400,windows),(95000,400,fast),(96000,240,subset)]
    report = {"rates":noisy.RATES, "cohorts":{}}
    for seed,n,arms in cohorts:
        report["cohorts"][seed] = {k:stats(rs,range(seed,seed+n)) for k,rs in arms.items()}
    comparisons = [(fast,"FastTree","BudgetPilot"), (fast,"FastCat","FiveParityCat"),
                   (subset,"ScreenTree","BudgetPilot"),(subset,"ScreenTree","FastTree"),
                   (subset,"ScreenCat","FiveParityCat"),(subset,"ScreenTree","ScreenCat")]
    tests = {f"{arms[a][0]['seed']} {a} vs {b}":pair(arms[a],arms[b]) for arms,a,b in comparisons}
    adjusted = 0
    for i,test in enumerate(sorted(tests.values(),key=lambda t:t["exact_two_sided_p"])):
        adjusted = max(adjusted,min(1,(len(tests)-i)*test["exact_two_sided_p"]))
        test["holm_p_six_match_comparisons"] = adjusted
    report["match_tests"] = tests
    report["percent_saving_per_decoded_match_bootstrap95_96000"] = cost_intervals(
        subset,[("ScreenTree","BudgetPilot"),("ScreenTree","FastTree"),("ScreenTree","ScreenCat"),
                ("FilterScreenTree","ScreenTree"),("ScreenTree","compact")])

    report["mismatches"] = {}
    for seed,n,arms in cohorts:
        for k,rs in arms.items():
            bad = [(r["seed"],r["metrics"]["sampled_noise_events"]) for r in rs if r.get("accepted")
                   and not r["diagnostics"]["decoded_target_within_tolerance"]]
            if bad:
                report["mismatches"][f"{seed} {k}"] = bad
    for arms,parent,filtered in ((pilot,"BareInnerPilot","filtered"),(windows,"source_window","filtered_tree"),
                                (fast,"FastTree","FastFilteredTree"),(subset,"ScreenTree","FilterScreenTree")):
        for a,b in zip(arms[parent],arms[filtered]):
            if b["reason"] != "negative_entry":
                assert a["accepted"] == b["accepted"] and a["metrics"]["gate_counts"] == b["metrics"]["gate_counts"]
                assert a.get("diagnostics") == b.get("diagnostics")
    report["compact_joint_lookups"] = [{"seed": r["seed"],"accepted":r.get("accepted"),"lookups":r["joint_lookups"]}
                                        for r in subset["compact"] if r.get("joint_lookups")]
    target = args.root / "cz-screened-source-96000/comparison.json"
    target.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
