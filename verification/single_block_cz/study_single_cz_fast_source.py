"""Paired holdout for a certified one-scan zero-source fast path."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_shared_source import WindowCat, FilterWindowTree
from study_single_cz_source_windows import BudgetPilot, SourceWindowPilot, cat, noisy
from check_single_cz_fast_source import audit, envelope
from check_single_cz_short_gauss_witnesses import shot, report


class ZeroSourceScan:
    def acquire(self, name, measure, initial=None):
        if name != "known_source":
            return super().acquire(name, measure, initial)
        assert initial is None
        first = list(measure(0))
        if not any(first):
            self.record.append({"history": name, "zero_source_fast_path": True})
            return first
        return super().acquire(name, measure, initial=first)


class FastTree(ZeroSourceScan, SourceWindowPilot):
    pass


class FastFilteredTree(ZeroSourceScan, FilterWindowTree):
    pass


class FastCat(ZeroSourceScan, WindowCat):
    pass


def trial(seed):
    rows = {}
    for cls in (BudgetPilot, FastTree, FastFilteredTree):
        with patch.object(noisy, "controller", lambda b,*_: cls(b, **noisy.OPTIONS)):
            rows[cls.__name__] = noisy.trial((None, seed, seed, noisy.RATES, False))
    for cls in (cat.FiveParityCat, FastCat):
        b = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed), model=noisy.NoiseModel(**noisy.RATES))
        run = cls(b, **cat.MATCHED, **cat.DIRECT).run()
        row = {"seed": seed, "execution_status": "completed", "accepted": run["accepted"],
               "reason": run.get("reason"), "metrics": b.metrics()}
        if row["accepted"]:
            row["diagnostics"] = noisy.diagnose(*b.state.sparse_output(b.data_labels))
            if not row["diagnostics"]["decoded_target_within_tolerance"]:
                row.update(noise_events=b.noise_events, controller_record=run["record"])
        rows[cls.__name__] = row
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=95000)
    parser.add_argument("--shots", type=int, default=400)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    cert = audit(list(range(20)), *envelope())
    assert not cert["bad_one"] and not cert["bad_two"]
    clean = {}
    for cls in (BudgetPilot, FastTree, FastFilteredTree, cat.FiveParityCat, FastCat):
        rec = noisy.RecordBackend()
        opts = (cat.MATCHED | cat.DIRECT) if issubclass(cls, cat.FiveParityCat) else noisy.OPTIONS
        assert cls(rec, **opts).run()["accepted"]
        clean[cls.__name__] = Counter(op for op,_ in rec.ops)
    w = {"clean": shot(2, [], FastTree), "nonzero_source_fallback": shot(2, [report("source/certify/0/Z/0","s")], FastTree)}
    assert all(r["accepted"] for r in w.values()) and w["nonzero_source_fallback"]["cx"] > w["clean"]["cx"]
    (args.folder / "certification.json").write_text(json.dumps({"source_zero": cert, "clean_gates": clean,
                                                                 "witnesses": w}, indent=2) + "\n")
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for group in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(group) + "\n")
            out.flush()
