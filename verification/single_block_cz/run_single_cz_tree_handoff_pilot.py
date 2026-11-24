"""Benchmark local tree-bit handoff with compact13 chords or the four-edge tree."""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
from unittest.mock import patch

import run_single_cz_short_gauss_pilot as short
from single_cz_tree_handoff_pilot import TreeHandoffPilot

base = short.base


def controller(backend, arm=None, recover_outer=False, *, graph):
    return TreeHandoffPilot(backend, tree_only=graph == "tree4", **base.OPTIONS)


def trial(request):
    graph, *shot = request
    with patch.object(short, "controller", partial(controller, graph=graph)):
        return short.trial(shot)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphs", nargs="+", choices=("compact13", "tree4"), default=("compact13", "tree4"))
    parser.add_argument("--shots", type=int, default=200)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--output-dir", type=Path, required=True)
    for key, value in base.RATES.items():
        parser.add_argument("--" + key.replace("_", "-"), default=value)
    args = parser.parse_args()
    if min(args.shots, args.workers, args.timeout) < 1 or len(set(args.graphs)) != len(args.graphs):
        parser.error("Use positive shots, workers and timeout, with distinct graphs")
    rates = {key: getattr(args, key) for key in base.RATES}
    args.output_dir.mkdir(parents=True, exist_ok=False)
    sources = (Path(__file__), Path(short.__file__), Path(base.__file__),
               Path(TreeHandoffPilot.__init__.__code__.co_filename), Path(short.ShortGaussPilot.check.__code__.co_filename),
               Path(base.DirectPilot.gauging.__code__.co_filename))
    base.write_json(args.output_dir / "manifest.json", {
        "shots_per_graph": args.shots, "seed": args.seed, "graphs": args.graphs,
        "timeout_seconds_per_shot": args.timeout, "noise": base.NoiseModel(**rates).manifest(), "options": base.OPTIONS,
        "schedule": "compact short votes, reported tree-bit byproducts and compact terminal screen",
        "V_pair_only_in_triggered_recovery": True, "experimental_no_global_fault_certificate": True,
        "source_sha256": {str(p.relative_to(base.ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources},
    })
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        for graph in args.graphs:
            folder = args.output_dir / graph
            folder.mkdir()
            recorder = base.RecordBackend()
            assert controller(recorder, graph=graph).run()["accepted"]
            clean = Counter(op for op, _ in recorder.ops)
            base.write_json(folder / "clean-gates.json", clean)
            print(graph, "clean CX", clean["CX"], "T/T†", clean["T"] + clean["TDG"], flush=True)
            requests = ((graph, j, args.seed + j, rates, args.timeout) for j in range(args.shots))
            rows = []
            with (folder / "shots.jsonl").open("x") as stream:
                for row in pool.map(trial, requests):
                    rows.append(row)
                    stream.write(json.dumps(row) + "\n")
                    if len(rows) % 10 == 0 or len(rows) == args.shots:
                        stream.flush()
                        info = base.arm_summary(rows)
                        base.write_json(folder / "summary.json", info)
                        print(graph, info["accepted"], "/", len(rows), "accepted,",
                              info["accepted_within_target_tolerance"], "matches,", info["unresolved"], "unresolved", flush=True)


if __name__ == "__main__":
    main()
