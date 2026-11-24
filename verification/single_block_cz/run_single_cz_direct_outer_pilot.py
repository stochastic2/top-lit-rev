"""Run the direct gauged and shortened vote circuits with the existing noisy backend."""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src" / name) for name in ("single_block_cz", "shared", "two_block_swap")]

import check_single_cz_direct_outer_ports as audit
from run_single_block_cz_controller import RecordBackend
from simulate_single_block_cz_depolarizing import noise_seed, summarize, write_json
from single_cz_diagnostics import diagnose
from single_cz_direct_outer_pilot import DirectPilot, OUTER_SUPPORTS
from single_cz_runtime import NoiseModel, QuantumBackend

ARMS = {"full": {}, "thin": {"thin": True}, "thin-entry": {"thin": True, "first_vote": True}}
OPTIONS = {"source_extraction": "decoded_flags", "data_checks": "compact_flags",
           "flag_recovery": "data", "conditional_checks": "dual_flags"}
RATES = {"two_qubit_infidelity": "1e-3", "readout_flip_probability": "1e-3",
         "one_qubit_infidelity": "1e-4", "t_infidelity": "1e-4", "idle_infidelity": "0",
         "preparation_flip_probability": "0"}


@lru_cache(maxsize=4)
def outer_table(check):
    """The isolated lookup union one conditional outside target cone."""
    from unittest.mock import patch

    graph = audit.COMPACT13
    support = OUTER_SUPPORTS[check - 5]
    with patch.object(audit.fault, "programs", audit.direct_route):
        events, _, labels, flags = audit.fault.enumerate_faults(support, graph, audit.ROUTE)
    internal, _, _, _ = audit.report_tables(events, labels, flags, graph)
    outside, _, _ = audit.prior.outside_envelope(events, labels, flags, graph)
    return {record: classes for record, classes in internal.items() if record[0]}, outside


def lookup(flag, syndrome):
    chk = int(flag.check.rsplit("/", 1)[1])
    if chk < 5:
        return None
    graph = audit.COMPACT13
    diag = sum(bit << i for i, bit in enumerate(syndrome))
    # The isolated verifier's diagnostic axes are the original nine X checks.
    # It receives the current meter separately, even for the replacement 6.
    assert len(syndrome) == 31 and chk in range(5, 9)
    internal, outside = outer_table(chk)
    graph_cycle_data_bits = 18 + len(graph.cycles)
    full = diag | (flag.parity << len(syndrome))
    coarse = (diag & ((1 << graph_cycle_data_bits) - 1)) | (flag.parity << graph_cycle_data_bits)
    classes = internal.get((flag.flags, full), 0) | outside.get((flag.flags, coarse), 0)
    if classes.bit_count() != 1:
        return None
    return audit.prior.correction(diag | ((classes.bit_length() - 1) << len(syndrome)), graph)


def controller(backend, arm, recover_outer):
    return DirectPilot(backend, **OPTIONS, **ARMS[arm], outer_lookup=lookup if recover_outer else None)


def trial(request):
    arm, index, seed, rates, recover_outer = request
    model = NoiseModel(**rates)
    backend = QuantumBackend(seed=seed, noise_seed=noise_seed(seed), model=model)
    pilot = controller(backend, arm, recover_outer)
    row = {"shot_index": index, "seed": seed, "execution_status": "completed"}
    try:
        run = pilot.run()
        row.update(accepted=run["accepted"], reason=run.get("reason"), metrics=backend.metrics(),
                   terminal_screen_outcome=pilot.terminal_screen_outcome,
                   direct_recovery_episodes=pilot.direct_recoveries,
                   successful_direct_recoveries=pilot.successful_direct_recoveries)
        if run["accepted"]:
            diagnostics = diagnose(*backend.state.sparse_output(backend.data_labels))
            row.update(diagnostics=diagnostics, diagnostic_status="completed")
            if not diagnostics["decoded_target_within_tolerance"]:
                row.update(controller_record=run["record"], noise_events=backend.noise_events)
    except (MemoryError, ArithmeticError) as error:
        row.update(execution_status="unresolved", failure_kind=type(error).__name__, detail=str(error),
                   metrics=backend.metrics(), controller_record=pilot.record, noise_events=backend.noise_events)
    return row


def arm_summary(rows):
    return summarize(rows) | {
        "direct_recovery_episodes": sum(row.get("direct_recovery_episodes", 0) for row in rows),
        "successful_direct_recoveries": sum(row.get("successful_direct_recoveries", 0) for row in rows),
        "accepted_after_direct_recovery": sum(bool(row.get("accepted") and row.get("successful_direct_recoveries"))
                                              for row in rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    parser.add_argument("--shots", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=1000)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--recover-outer", action="store_true")
    for key, value in RATES.items():
        parser.add_argument("--" + key.replace("_", "-"), default=value)
    args = parser.parse_args()
    if not args.shots > 0 or not args.workers > 0 or len(set(args.arms)) != len(args.arms):
        parser.error("Use positive attempts/workers and distinct arms")
    rates = {key: getattr(args, key) for key in RATES}
    args.output_dir.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), Path(audit.__file__), Path(audit.direct.__file__),
               Path(sys.modules[DirectPilot.__module__].__file__), Path(sys.modules[QuantumBackend.__module__].__file__)]
    write_json(args.output_dir / "manifest.json", {
        "arms": {arm: ARMS[arm] for arm in args.arms}, "shots_per_arm": args.shots, "seed": args.seed,
        "noise": NoiseModel(**rates).manifest(), "options": OPTIONS,
        "outer_flag_lookup_enabled": args.recover_outer, "graph": "compact13", "root_flags": "reject",
        "terminal_policy": "screen", "experimental_no_global_fault_certificate": True,
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in sources},
    })
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        for arm in args.arms:
            folder = args.output_dir / arm
            folder.mkdir()
            recorder = RecordBackend()
            assert controller(recorder, arm, args.recover_outer).run()["accepted"]
            clean = Counter(op for op, _ in recorder.ops)
            write_json(folder / "clean-gates.json", clean)
            print(arm, "clean CX", clean["CX"], "T/T†", clean["T"] + clean["TDG"], flush=True)
            requests = ((arm, j, args.seed + j, rates, args.recover_outer) for j in range(args.shots))
            rows = []
            with (folder / "shots.jsonl").open("x") as stream:
                for row in pool.map(trial, requests):
                    rows.append(row)
                    stream.write(json.dumps(row) + "\n")
                    if len(rows) % 10 == 0 or len(rows) == args.shots:
                        stream.flush()
                        result = arm_summary(rows)
                        write_json(folder / "summary.json", result)
                        print(arm, result["accepted"], "/", len(rows), "accepted,",
                              result["accepted_within_target_tolerance"], "matches,",
                              result["unresolved"], "unresolved", flush=True)


if __name__ == "__main__":
    main()
