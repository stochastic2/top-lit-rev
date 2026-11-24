"""Find smallest reproducing subsets of sampled faults on a selected trajectory."""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from study_single_cz_bare_inner import BareInnerPilot
from study_single_cz_source_windows import SourceWindowPilot, BudgetPilot, cat, noisy
from study_single_cz_screened_source import ScreenTree, FilterScreenTree, ScreenCat, FastTree, FastCat
from study_single_cz_fast_source import FastFilteredTree
from study_single_cz_screened_compact import ScreenCompact


def reduce(cls, seed):
    count = Counter()
    locations = {}

    def trace(ev):
        if ev["kind"] == "physical":
            key = ev["context"], ev["operation"], tuple(ev["targets"])
            locations[ev["event"]] = key, count[key]
            count[key] += 1

    backend = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed),
                                   model=noisy.NoiseModel(**noisy.RATES), trace=trace)
    options = (cat.MATCHED | cat.DIRECT) if issubclass(cls, cat.FiveParityCat) else noisy.OPTIONS
    original = cls(backend, **options).run()
    assert original["accepted"] and not noisy.diagnose(*backend.state.sparse_output(backend.data_labels))["decoded_target_within_tolerance"]
    injections = []
    for ev in backend.noise_events:
        (context, op, targets), nth = locations[ev["event"]]
        injections.append({"context": context, "operation": op, "targets": targets, "occurrence": nth,
                           "timing": "report" if ev["flip_report"] else "after", "flip_report": ev["flip_report"],
                           "paulis": dict(zip(targets, ev["axes"]))})
    results = []
    for size in range(len(injections) + 1):
        found = False
        for subset in combinations(range(len(injections)), size):
            b = noisy.QuantumBackend(seed=seed, model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES, "0")),
                                     injections=[injections[j] for j in subset])
            run = cls(b, **options).run()
            row = {"subset": subset, "hits": len(b.injected_events), "accepted": run["accepted"], "reason": run.get("reason")}
            if run["accepted"]:
                d = noisy.diagnose(*b.state.sparse_output(b.data_labels))
                row["fidelity"] = d["decoded_target_fidelity"]
                if not d["decoded_target_within_tolerance"] and row["hits"] == size:
                    row["record"] = run["record"]
                    found = True
            results.append(row)
        if found:
            return {"pilot": cls.__name__, "seed": seed, "faults": injections, "smallest_reproducing_size": size,
                    "tested_subsets": results}
    raise AssertionError("Original mismatch did not replay")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    classes = {c.__name__: c for c in (BareInnerPilot, BudgetPilot, SourceWindowPilot, FastTree, FastCat,
                                      FastFilteredTree, ScreenTree, FilterScreenTree, ScreenCat, ScreenCompact, cat.FiveParityCat)}
    parser.add_argument("pilot", choices=classes)
    parser.add_argument("seed", type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(reduce(classes[args.pilot], args.seed), indent=2) + "\n")
