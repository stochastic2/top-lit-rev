"""Compare both compact13 cohorts with the archived seed-matched 20-leaf cat."""
from collections import Counter
import json
from pathlib import Path
from statistics import fmean
import numpy as np

HERE = Path(__file__).resolve().parent
def load(name):
    return [json.loads(line) for line in name.read_text().splitlines()]

archive = HERE.parent / "tree4_cat_fairness_review/comparison_500"
rows = {"cat20": [r["LeanResourceCat"] for r in load(archive / "shots.jsonl")],
        "compact13": load(HERE / "shots.jsonl"), "compact13_full_scans": load(HERE/"full_scan_shots.jsonl")}
rng = np.random.default_rng(57)
idx = rng.integers(500, size=(10000,500))
result = {}
for arm, group in rows.items():
    assert [r["seed"] for r in group] == list(range(2610000,2610500))
    assert all(r["status"] == "completed" for r in group)
    accepts = np.array([int(r["accepted"]) for r in group])
    good = np.array([int(r.get("diagnostics",{}).get("decoded_target_within_tolerance",False)) for r in group])
    cx = np.array([r["metrics"]["gate_counts"]["CX"] for r in group])
    t = np.array([sum(r["metrics"]["gate_counts"].get(op,0) for op in ("T","TDG")) for r in group])
    def bootstrap_cost(cost, successes):
        return cost[idx].sum(axis=1)/successes[idx].sum(axis=1)
    boots = bootstrap_cost(cx, good)
    if arm == "cat20":
        ref_accepts, ref_cost = accepts, boots
    result[arm] = dict(accepted=int(accepts.sum()), acceptance=accepts.mean(), decoded_matches=int(good.sum()),
        accepted_fidelity=fmean(r["diagnostics"]["decoded_target_fidelity"] for r in group if r["accepted"]),
        cx_per_match=cx.sum()/good.sum(), t_per_match=t.sum()/good.sum(),
        peak_live=max(r["metrics"]["peak_live_qubits"] for r in group),
        paired_acceptance_difference_95=np.quantile((accepts-ref_accepts)[idx].mean(axis=1),[.025,.975]).tolist(),
        paired_cx_per_match_ratio_95=np.quantile(boots/ref_cost,[.025,.975]).tolist(),
        misses=[dict(seed=r["seed"], fidelity=r["diagnostics"]["decoded_target_fidelity"],
                     sampled_faults=r["metrics"]["sampled_noise_events"]) for r in group
                if r["accepted"] and not r["diagnostics"]["decoded_target_within_tolerance"]])
(HERE/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
