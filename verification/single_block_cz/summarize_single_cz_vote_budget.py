"""Summarize the fresh arms and compare the replay with the saved references."""
import argparse
from collections import Counter
import json
from pathlib import Path

from study_single_cz_vote_budget import noisy

ROOT = noisy.ROOT
OLD = ROOT / "output/cz-gauged-500-seed3000"


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def stats(records, seeds):
    assert [r["seed"] for r in records] == list(seeds)
    complete = [r for r in records if r["execution_status"] == "completed"]
    accepted = [r for r in complete if r["accepted"]]
    matches = sum(r["diagnostics"]["decoded_target_within_tolerance"] for r in accepted)
    gates = Counter()
    for r in complete:
        gates.update(r["metrics"]["gate_counts"])
    return {"attempts": len(records), "accepted": len(accepted), "rejected": len(complete) - len(accepted),
            "unresolved": len(records) - len(complete), "decoded_matches": matches,
            "cx": gates["CX"], "t_and_adjoint": gates["T"] + gates["TDG"],
            "cx_per_match": gates["CX"] / matches, "t_and_adjoint_per_match": (gates["T"] + gates["TDG"]) / matches,
            "peak_live": max(r["metrics"]["peak_live_qubits"] for r in complete)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "output/cz-tree-vote-budget")
    folder = parser.parse_args().results
    old_seeds = range(3000, 3500)
    new_seeds = range(81000, 81064)
    arms = json.loads((OLD / "comparison.json").read_text())["arms"]
    old = {k: rows((OLD / arm["summary"]).with_name("shots.jsonl")) for k, arm in arms.items()}
    replay = rows(folder / "replay.jsonl")
    old["budget"] = replay
    paired = rows(folder / "paired.jsonl")
    fresh = {k: [r[k] for r in paired] for k in paired[0]}
    fresh.update(majority=rows(folder / "majority.jsonl"), compact=rows(folder / "compact.jsonl"),
                 cat=rows(folder / "fresh-cat/cat-five-parity/shots.jsonl"))
    original = old["tree4_block_flags"]
    cut = [r["seed"] for l, r in zip(original, replay)
           if r["metrics"]["gate_counts"]["CX"] < l["metrics"]["gate_counts"]["CX"]]
    joint = [r for r in old["joint_fallback"] if r["joint_recovery_episodes"]]
    missed = [r["BudgetPilot"]["seed"] for r in paired if r["BudgetPilot"]["accepted"]
              and not r["NoSharedVPilot"]["accepted"]]
    assert all(r["execution_status"] == "completed" for rs in fresh.values() for r in rs)
    result = {"noise_rates": noisy.RATES, "controller_options": noisy.OPTIONS,
              "cohort_3000_3499": {k: stats(rs, old_seeds) for k, rs in old.items()},
              "cohort_81000_81063": {k: stats(rs, new_seeds) for k, rs in fresh.items()},
              "replay_seeds_spending_fewer_cx": cut, "no_shared_V_lost_accept_seeds": missed,
              "no_shared_V_rejected_at_exception": sum(r["reason"] == "exception_requires_shared_V"
                                                       for r in fresh["NoSharedVPilot"]),
              "round_trip_joint_trigger_seeds": [r["seed"] for r in joint],
              "round_trip_joint_recovered_accept_seeds": [r["seed"] for r in joint if r["accepted"]],
              "fresh_compact_joint_lookup_seeds": [r["seed"] for r in fresh["compact"] if r["ambiguous_data_joint_lookups"]],
              "majority_accept_only_seeds": [b["seed"] for a, b in zip(fresh["BudgetPilot"], fresh["majority"])
                                             if b["accepted"] and not a["accepted"]],
              "single_read_accept_only_seeds": [a["seed"] for a, b in zip(fresh["BudgetPilot"], fresh["majority"])
                                                if a["accepted"] and not b["accepted"]]}
    (folder / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
