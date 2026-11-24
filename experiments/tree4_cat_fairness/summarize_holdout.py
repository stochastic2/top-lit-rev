"""Summarize complete matched seed groups using the frozen estimands."""
from collections import Counter
import gzip
import json
from math import sqrt
import statistics

import numpy as np

from holdout import OUT, digest, json_write

NAMES = ("accepted", "matches", "cx", "t", "raw_sum", "decoded_sum")
Z95 = statistics.NormalDist().inv_cdf(.975)


def wilson(k, n):
    p = k/n
    d = 1 + Z95*Z95/n
    center = (p + Z95*Z95/(2*n))/d
    radius = Z95*sqrt((p*(1-p) + Z95*Z95/(4*n))/n)/d
    return [max(0, center-radius), min(1, center+radius)]


def vector(row):
    diagnostic = row.get("diagnostics", {})
    counts = row["metrics"]["gate_counts"]
    return [int(row["accepted"]), int(diagnostic.get("decoded_target_within_tolerance", False)),
            counts.get("CX", 0), counts.get("T", 0) + counts.get("TDG", 0),
            diagnostic.get("raw_physical_target_fidelity", 0), diagnostic.get("decoded_target_fidelity", 0)]


def estimands(columns, n):
    a, m, cx, t, raw, decoded = columns
    return {"acceptance": a/n, "matches_per_attempt": m/n, "cx_per_match": cx/m,
            "t_per_match": t/m, "accepted_mean_raw": raw/a, "accepted_mean_decoded": decoded/a}


def arm_summary(rows, columns):
    n = len(rows)
    accepted, matched, cx, t, _, _ = columns
    unresolved = [r for r in rows if r["status"] == "unresolved"]
    mismatch = [r for r in rows if r["accepted"] and not r["diagnostics"]["decoded_target_within_tolerance"]]
    fault_histogram = {}
    for r in rows:
        k = str(r["metrics"]["sampled_noise_events"])
        group = fault_histogram.setdefault(k, Counter())
        counts = vector(r)
        group.update(attempts=1, accepted=counts[0], matches=counts[1])
    assert all(not r["accepted"] or r["metrics"]["sampled_noise_events"] > 2 or
               (r["diagnostics"]["decoded_target_within_tolerance"] and
                r["diagnostics"]["probability_in_weight_two_lookup"] > 1-1e-10) for r in rows)
    gate_totals = Counter()
    for r in rows:
        gate_totals.update(r["metrics"]["gate_counts"])
    return estimands(columns, n) | {
        "n": n, "accepted": int(accepted), "matches": int(matched),
        "rejected": n-int(accepted)-len(unresolved), "unresolved": len(unresolved),
        "unresolved_seeds": [r["seed"] for r in unresolved], "gate_totals": gate_totals,
        "cx_total": int(cx), "t_total": int(t), "peak_live": max(r["metrics"]["peak_live_qubits"] for r in rows),
        "acceptance_wilson_95": wilson(accepted, n), "matches_per_attempt_wilson_95": wilson(matched, n),
        "mismatch_seeds": [r["seed"] for r in mismatch],
        "mismatch_fault_counts": [r["metrics"]["sampled_noise_events"] for r in mismatch],
        "conditional_mismatch_one_sided_exact_95_upper_if_zero": 1-.05**(1/accepted) if not mismatch else None,
        "rejection_reasons": Counter(r["reason"] for r in rows if r["status"] == "completed" and not r["accepted"]),
        "retries": dict(attempts_with_retry=sum(r["retries"] > 0 for r in rows),
                        total_tokens=sum(r["retries"] for r in rows),
                        tokens_by_reason=Counter(e["retry"] for r in rows for e in r["record"] if "retry" in e)),
        "cat_fallbacks": sum("cat_fallback" in e for r in rows for e in r["record"]),
        "terminal_screen_outcomes": Counter(r["terminal_screen_outcome"] for r in rows if r["terminal_screen_outcome"]),
        "sampled_fault_count_histogram": fault_histogram,
    }


def interval(sample):
    return np.quantile(sample, (.025, .975)).tolist()


def main():
    manifest = json.loads((OUT / "manifest.json").read_text())
    plan = manifest["plan"]
    n = plan["attempts_per_arm"]
    shots_path = OUT / "shots.jsonl.gz"
    rows = {name: [] for name in plan["arms"]}
    with gzip.open(shots_path, "rt") as stream:
        for expected_seed, line in enumerate(stream, plan["seed_start"]):
            group = json.loads(line)
            assert group["seed"] == expected_seed and set(group["arms"]) == set(rows)
            for name, row in group["arms"].items():
                assert row["seed"] == expected_seed
                rows[name].append(row)
    assert all(len(r) == n for r in rows.values())
    matrices = {name: np.asarray([vector(r) for r in shots]) for name, shots in rows.items()}
    sums = {name: matrix.sum(axis=0) for name, matrix in matrices.items()}
    summary = {name: arm_summary(shots, sums[name]) for name, shots in rows.items()}
    bootstrap = np.random.default_rng(27711).multinomial(n, np.full(n, 1/n), 10000).astype(float)
    estimates = {name: estimands((bootstrap @ matrix).T, n) for name, matrix in matrices.items()}
    paired = {}
    for left, right in plan["paired_comparisons_right_minus_left"]:
        result = {"difference_right_minus_left": {}, "ratio_right_over_left": {}}
        for key, right_sample in estimates[right].items():
            left_sample = estimates[left][key]
            a, b = summary[left][key], summary[right][key]
            result["difference_right_minus_left"][key] = {
                "estimate": b-a, "interval_95": interval(right_sample - left_sample)}
            if key in ("cx_per_match", "t_per_match"):
                result["ratio_right_over_left"][key] = {
                    "estimate": b/a, "interval_95": interval(right_sample/left_sample)}
        for i, name in enumerate(NAMES[:2]):
            a, b = matrices[left][:,i].astype(bool), matrices[right][:,i].astype(bool)
            result[name + "_discordance"] = {"left_only": int(sum(a & ~b)), "right_only": int(sum(b & ~a))}
        paired[f"{left} -> {right}"] = result
    primary = paired["BareInnerTree -> LeanResourceCat"]
    noninferiority = {
        "cx": primary["ratio_right_over_left"]["cx_per_match"]["interval_95"][1] < 1.05,
        "t": primary["ratio_right_over_left"]["t_per_match"]["interval_95"][1] < 1.05,
        "matches": primary["difference_right_minus_left"]["matches_per_attempt"]["interval_95"][0] > -.02,
    }
    json_write(OUT / "summary.json", {"ledger_sha256": digest(shots_path), "arms": summary,
                                    "paired": paired, "prespecified_noninferiority": noninferiority})


if __name__ == "__main__":
    main()
