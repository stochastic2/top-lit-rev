"""Replicate the other selectively filtered arms on the same fixed seed set."""
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import sys

from run_replication import HERE, ROOT, RATES, SEEDS, PRIOR_PLAN
from run import Cat, Compact, run_arm
from budget import BudgetCat


class SelectiveCompact(Compact):
    hard_stop = "moderate"


class SelectiveCat(Cat):
    hard_stop = "moderate"


ARMS = (SelectiveCompact, SelectiveCat, BudgetCat)


def trial(seed):
    results = {}
    for cls in ARMS:
        row = run_arm(cls, seed, RATES)
        keep = ("seed", "status", "accepted", "reason", "detail", "metrics", "diagnostics")
        result = {key: row[key] for key in keep if key in row}
        if row["accepted"] and not row["diagnostics"]["decoded_target_within_tolerance"]:
            result.update(noise_events=row["noise_events"], record=row["record"])
        results[cls.__name__] = result
    return results


if __name__ == "__main__":
    paths = {m.__file__ for m in list(sys.modules.values()) if getattr(m, "__file__", None)}
    hashes = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
              for p in sorted({HERE.joinpath(path).resolve() for path in paths})
              if p.is_relative_to(ROOT) and p.suffix == ".py"}
    manifest = dict(seed_range_inclusive=[SEEDS.start, SEEDS.stop - 1], attempts_per_arm=len(SEEDS),
                    rates=RATES, shared_policy=PRIOR_PLAN["primary_rule"],
                    budget_cat="same selective veto plus stop before a 121st physical T/Tdg gate",
                    arms=[c.__name__ for c in ARMS], source_sha256=hashes)
    with (HERE / "additional_arms_manifest.json").open("x") as f:
        json.dump(manifest, f, indent=2)
    with (HERE / "additional_arms_shots.jsonl").open("x") as f, ProcessPoolExecutor(5) as pool:
        for index, row in enumerate(pool.map(trial, SEEDS), 1):
            f.write(json.dumps(row) + "\n")
            f.flush()
            if index % 500 == 0:
                print(f"{index}/{len(SEEDS)} additional paired seeds completed", flush=True)
