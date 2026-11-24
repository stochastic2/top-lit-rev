"""Noisy pilot for the shortened Gauss schedule with compact meters."""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
import signal
from unittest.mock import patch

import run_single_cz_direct_outer_pilot as base
from single_cz_short_gauss_pilot import ShortGaussPilot


def controller(backend, arm=None, recover_outer=False):
    return ShortGaussPilot(backend, **base.OPTIONS)


def timed_out(*_):
    raise TimeoutError("prototype shot timeout")


def trial(request):
    index, seed, rates, timeout = request
    signal.signal(signal.SIGALRM, timed_out)
    signal.alarm(timeout)
    try:
        with patch.object(base, "controller", controller):
            return base.trial((None, index, seed, rates, False))
    except TimeoutError as error:
        return {"shot_index": index, "seed": seed, "execution_status": "unresolved",
                "failure_kind": "timeout", "detail": str(error)}
    finally:
        signal.alarm(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--output-dir", type=Path, required=True)
    for key, value in base.RATES.items():
        parser.add_argument("--" + key.replace("_", "-"), default=value)
    args = parser.parse_args()
    if min(args.shots, args.workers, args.timeout) < 1:
        parser.error("Use positive shots, workers, and timeout")
    rates = {key: getattr(args, key) for key in base.RATES}
    args.output_dir.mkdir(parents=True, exist_ok=False)
    sources = (Path(__file__), Path(base.__file__), Path(ShortGaussPilot.check.__code__.co_filename),
               Path(base.DirectPilot.gauging.__code__.co_filename))
    base.write_json(args.output_dir / "manifest.json", {
        "shots": args.shots, "seed": args.seed, "graph": "compact13", "timeout_seconds_per_shot": args.timeout,
        "noise": base.NoiseModel(**rates).manifest(), "options": base.OPTIONS,
        "schedule": "entry vote, nine data Z, five inner X parity, compact local Gauss, compact terminal screen",
        "V_pair_only_in_triggered_recovery": True, "experimental_no_global_fault_certificate": True,
        "source_sha256": {str(p.relative_to(base.ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources},
    })
    rec = base.RecordBackend()
    assert controller(rec).run()["accepted"]
    clean = Counter(op for op, _ in rec.ops)
    base.write_json(args.output_dir / "clean-gates.json", clean)
    print("compact short vote clean CX", clean["CX"], "T/T†", clean["T"] + clean["TDG"], flush=True)
    requests = ((j, args.seed + j, rates, args.timeout) for j in range(args.shots))
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        with (args.output_dir / "shots.jsonl").open("x") as stream:
            for row in pool.map(trial, requests):
                rows.append(row)
                stream.write(json.dumps(row) + "\n")
                if len(rows) % 10 == 0 or len(rows) == args.shots:
                    stream.flush()
                    info = base.arm_summary(rows)
                    base.write_json(args.output_dir / "summary.json", info)
                    print(info["accepted"], "/", len(rows), "accepted,", info["accepted_within_target_tolerance"],
                          "matches,", info["unresolved"], "unresolved", flush=True)


if __name__ == "__main__":
    main()
