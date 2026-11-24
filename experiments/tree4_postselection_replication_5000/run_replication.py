"""Run 5,000 fresh attempts using the original selective veto as a physical stop."""
import json
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = HERE.parent / "certified_postselection_6000"
sys.path.insert(0, str(PRIOR))
from run import Tree, noisy, run_arm

SEEDS = range(3300000, 3305000)
PRIOR_PLAN = json.loads((PRIOR / "plan.json").read_text())
RATES = PRIOR_PLAN["rates"]


class SelectiveTree(Tree):
    hard_stop = "moderate"


def trial(seed):
    row = run_arm(SelectiveTree, seed, RATES)
    keep = ("seed", "status", "accepted", "reason", "detail", "diagnostics", "metrics")
    result = {key: row[key] for key in keep if key in row}
    if row["accepted"] and not row["diagnostics"]["decoded_target_within_tolerance"]:
        result.update(noise_events=row["noise_events"], record=row["record"])
    return result


def main():
    assert RATES == noisy.RATES
    paths = {Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m, "__file__", None)}
    hashes = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
              for p in sorted(paths) if p.is_relative_to(ROOT) and p.suffix == ".py"}
    manifest = dict(seed_range_inclusive=[SEEDS.start, SEEDS.stop - 1], attempts=len(SEEDS), rates=RATES,
                    controller="Tree with hard_stop=moderate",
                    policy="reject on terminal syndrome fallback or a full recovery reference during a vote",
                    primary_endpoint="standalone one-sided 95% lower confidence bound on mean accepted decoded fidelity",
                    references={key: PRIOR_PLAN[key] for key in
                                ("native_rotation_reference", "heralded_clifford_T_reference")},
                    source_sha256=hashes)
    with (HERE / "manifest.json").open("x") as f:
        json.dump(manifest, f, indent=2)
    with (HERE / "shots.jsonl").open("x") as f, ProcessPoolExecutor(8) as pool:
        for index, row in enumerate(pool.map(trial, SEEDS), 1):
            f.write(json.dumps(row) + "\n")
            f.flush()
            if index % 500 == 0:
                print(f"{index}/{len(SEEDS)} attempts completed", flush=True)


if __name__ == "__main__":
    main()
