"""Freeze and execute the fixed matched-seed fairness study."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

from candidates import ARMS, settings
from trace_audit import HERE, noisy

ROOT = HERE.parents[1]
PLAN = HERE / "holdout_plan.json"
OUT = HERE / f"holdout_{json.loads(PLAN.read_text())['seed_start']}"


def json_write(path, obj):
    with path.open("x") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dependencies():
    paths = {Path(mod.__file__).resolve() for mod in sys.modules.copy().values()
             if getattr(mod, "__file__", None)}
    paths.update(HERE.glob("*.py"))
    paths.update((PLAN, HERE / "local_checks.json", HERE / "baseline_traces.json", HERE / "forced_checks.json",
                  HERE.parent / "tree4_flag_repair" / "composition.json"))
    return {str(path.relative_to(ROOT)): digest(path)
            for path in sorted(paths) if path.is_relative_to(ROOT)}


def run_arm(cls, seed, rates, injections=()):
    backend = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed), model=noisy.NoiseModel(**rates),
                                   injections=injections)
    controller = cls(backend, **settings(cls))
    row = {"seed": seed, "status": "completed", "accepted": False}
    try:
        result = controller.run()
        row.update(accepted=result["accepted"], reason=result.get("reason"))
        if row["accepted"]:
            row["diagnostics"] = noisy.diagnose(*backend.state.sparse_output(backend.data_labels))
    except (MemoryError, ArithmeticError) as exc:
        row.update(status="unresolved", detail=str(exc), failure_kind=type(exc).__name__,
                   pending_accepted=row["accepted"], accepted=False)
    row.update(metrics=backend.metrics(), retries=controller.retries, record=controller.record,
               noise_events=backend.noise_events, injected_events=backend.injected_events,
               terminal_screen_outcome=controller.terminal_screen_outcome)
    return row


def trial(task):
    seed, rates = task
    return {"seed": seed, "arms": {cls.__name__: run_arm(cls, seed, rates) for cls in ARMS}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("freeze", "run"))
    args = p.parse_args()
    plan = json.loads(PLAN.read_text())
    assert plan["arms"] == [cls.__name__ for cls in ARMS]
    assert plan["noise"] == noisy.RATES
    manifest = {"plan": plan, "hashes": dependencies(),
                "options": {cls.__name__: settings(cls) for cls in ARMS},
                "noise_model": noisy.NoiseModel(**plan["noise"]).manifest(),
                "python_version": sys.version}
    if args.action == "freeze":
        OUT.mkdir()
        json_write(OUT / "manifest.json", manifest)
        print(f"Frozen {plan['attempts_per_arm']} attempts per arm in {OUT}")
        return
    assert manifest == json.loads((OUT / "manifest.json").read_text())
    assert (HERE / "forced_checks.json").exists(), "Run the forced checks before starting the holdout."
    tasks = ((seed, plan["noise"]) for seed in range(plan["seed_start"], plan["seed_start"] + plan["attempts_per_arm"]))
    with gzip.open(OUT / "shots.jsonl.gz", "xt", compresslevel=4) as stream, ProcessPoolExecutor(plan["workers"]) as pool:
        for i, group in enumerate(pool.map(trial, tasks), 1):
            stream.write(json.dumps(group, separators=(",", ":")) + "\n")
            stream.flush()
            if i % 64 == 0:
                print(f"Recorded {i} of {plan['attempts_per_arm']} matched-seed groups", flush=True)


if __name__ == "__main__":
    main()
