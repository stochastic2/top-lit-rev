"""Give the tuned cat the same source, and test the tree's negative-entry filter."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_source_windows import SourceWindowPilot, cat, noisy
from run_single_block_cz_controller import Reject
from single_cz_direct_outer_pilot import DirectPilot


class WindowCat(cat.FiveParityCat):
    direct_meter = DirectPilot.direct_meter
    source_code = SourceWindowPilot.source_code

    def prep(self, q):
        super().prep(q)
        if q == "s" and self.b.context.startswith("source/certify/") and "/Z/" in self.b.context:
            if hasattr(self.b, "absorb_parity_helper"):
                self.b.absorb_parity_helper(q)


class FilterWindowTree(SourceWindowPilot):
    def context(self, name):
        if name == "vertex_frame" and self.record[-1]["passes"] == 0:
            raise Reject("negative_entry")
        super().context(name)


def trial(seed):
    with patch.object(noisy, "controller", lambda b,*_: FilterWindowTree(b, **noisy.OPTIONS)):
        tree = noisy.trial((None, seed, seed, noisy.RATES, False))
    backend = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed), model=noisy.NoiseModel(**noisy.RATES))
    run = WindowCat(backend, **cat.MATCHED, **cat.DIRECT).run()
    row = {"seed": seed, "execution_status": "completed", "accepted": run["accepted"],
           "reason": run.get("reason"), "metrics": backend.metrics()}
    if row["accepted"]:
        row["diagnostics"] = noisy.diagnose(*backend.state.sparse_output(backend.data_labels))
    return {"filtered_tree": tree, "window_cat": row}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=93000)
    parser.add_argument("--shots", type=int, default=400)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(row) + "\n")
            out.flush()
