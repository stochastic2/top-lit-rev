"""Sampled depolarizing trajectories for the optimized C4-Helix procedure.

The noiseless controller and physical circuit are reused without changing
their acceptance decisions. Default: average two-qubit gate infidelity
1e-4; other channels ideal. All rate assumptions are saved in a manifest.
Attempts run in isolated processes so resource failures stay separate from
circuit rejection. No noisy trajectory is truncated to two faults.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
import math
import multiprocessing as mp
from pathlib import Path
from random import Random
from time import monotonic, perf_counter
import traceback

from c4_helix_depolarizing import DepolarizingModel, DepolarizingRuntime
from c4_helix_compact_terminal import TERMINAL_EXTRACTIONS
from c4_helix_magic_y import MAGIC_OUTPUTS, ideal_success_probability
from c4_helix_logical_diagnostics import decoded_c_diagnostics
from c4_helix_reduced_decoders import CURRENT_GRAPH, GRAPHS, HISTORY_POLICIES
from simulate_c4_helix_reduced import ReducedRejectionSimulator, save_result
from simulate_c4_helix_sparse import process_peak_rss_bytes


def default_noise_seed(seed):
    return int.from_bytes(sha256(f"depolarizing-noise:{seed}".encode()).digest()[:8], "big")


class DepolarizingSimulator(ReducedRejectionSimulator):
    def __init__(self, seed=0, noise_seed=None, model=None, graph=CURRENT_GRAPH, source_mode="encoded",
                 extraction="optimized", trace=None, observer=None, max_terms=4096, history_policy="triple",
                 terminal_extraction="protected", magic_output="y"):
        super().__init__(seed=seed, graph=graph, source_mode=source_mode, trace=trace, observer=observer,
                         max_terms=max_terms, extraction=extraction, history_policy=history_policy,
                         terminal_extraction=terminal_extraction, magic_output=magic_output)
        self.noise_seed = default_noise_seed(seed) if noise_seed is None else noise_seed
        self.model = model if model is not None else DepolarizingModel()
        self.runtime = DepolarizingRuntime(Random(seed), Random(self.noise_seed), self.model, trace, max_terms, history_policy)
        self.result.update(noise_model="pauli_depolarizing", noise_seed=self.noise_seed)

    def run(self, diagnose=True):
        result = super().run()
        result["noise"] = self.runtime.noise_summary()
        if diagnose and result["accepted"]:
            result["decoded_C_diagnostics"] = decoded_c_diagnostics(result["c_state"], magic_output=self.magic_output,
                y_outcome=None if result["b_y"] is None else result["b_y"]["logical_bit"])
        return result


def write_json(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def _attempt_worker(connection, request):
    """One fresh factor store/process. Communicate physical completion before diagnosis."""
    directory = Path(request["directory"])
    attempt_dir = Path(request["attempt_dir"])
    trace_file = None
    simulator = None
    started = perf_counter()
    try:
        if request["trace"]:
            trace_file = (attempt_dir / "events.jsonl").open("x")

        def trace(event):
            trace_file.write(json.dumps({"shot_index": request["shot_index"], **event}) + "\n")

        def progress(stage, runtime):
            write_json(attempt_dir / "progress.json", {
                "stage": stage, "elapsed_seconds": perf_counter() - started,
                "physical_events": runtime.events, "coherent_terms": len(runtime.state.terms),
                "noise_events": len(runtime.noise_events), "process_peak_rss_bytes": process_peak_rss_bytes()})

        simulator = DepolarizingSimulator(
            seed=request["seed"], noise_seed=request["noise_seed"],
            model=DepolarizingModel(**request["model_rates"]), graph=GRAPHS[request["graph"]],
            source_mode=request["source_mode"], extraction=request["extraction"],
            trace=trace if trace_file else None, observer=progress, max_terms=request["max_terms"],
            history_policy=request.get("history_policy", "triple"),
            terminal_extraction=request.get("terminal_extraction", "protected"), magic_output=request.get("magic_output", "z"))
        result = simulator.run(diagnose=False)
        record = save_result(result, directory, request["shot_index"])
        record.update(execution_status="completed", diagnostic_status="pending" if result["accepted"] else "not_applicable")
        write_json(attempt_dir / "circuit_result.json", record)
        connection.send({"kind": "circuit_complete", "record": record})
        if result["accepted"]:
            try:
                record["decoded_C_diagnostics"] = decoded_c_diagnostics(result["c_state"],
                    magic_output=simulator.magic_output,
                    y_outcome=None if result["b_y"] is None else result["b_y"]["logical_bit"])
                record["diagnostic_status"] = "completed"
            except Exception as error:
                record["diagnostic_status"] = "error"
                record["diagnostic_error"] = f"{type(error).__name__}: {error}"
                record["diagnostic_traceback"] = traceback.format_exc()
        record["worker_elapsed_seconds"] = perf_counter() - started
        record["worker_peak_rss_bytes"] = process_peak_rss_bytes()
        write_json(attempt_dir / "result.json", record)
        connection.send({"kind": "complete", "record": record})
    except Exception as error:
        failure = {"kind": "failure", "failure_kind": "memory_limit" if isinstance(error, MemoryError) else "backend_error",
                   "error": f"{type(error).__name__}: {error}", "traceback": traceback.format_exc()}
        if simulator is not None:
            failure.update(noise_events_so_far=simulator.runtime.noise_summary(),
                           physical_events_so_far=simulator.runtime.events)
        try:
            write_json(attempt_dir / "failure.json", failure)
            connection.send(failure)
        except Exception:
            pass
    finally:
        if trace_file is not None:
            trace_file.close()
        connection.close()


def isolated_attempt(request, timeout_seconds):
    """A timeout is an unresolved computation, never an inferred rejection."""
    ctx = mp.get_context("spawn")
    receiving, sending = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_attempt_worker, args=(sending, request))
    started = monotonic()
    process.start()
    sending.close()
    completed_circuit = final = failure = None
    deadline = started + timeout_seconds
    try:
        while monotonic() < deadline:
            if receiving.poll(min(0.25, max(0, deadline - monotonic()))):
                try:
                    message = receiving.recv()
                except EOFError:
                    break
                if message["kind"] == "circuit_complete":
                    completed_circuit = message["record"]
                elif message["kind"] == "complete":
                    final = message["record"]
                    break
                else:
                    failure = message
                    break
            elif not process.is_alive():
                break
        timed_out = process.is_alive() and final is None and failure is None and monotonic() >= deadline
        if process.is_alive() and final is None:
            process.terminate()
        process.join(timeout=3)
        if process.is_alive():
            process.kill()
            process.join(timeout=3)
        if final is not None:
            final["attempt_wall_seconds"] = monotonic() - started
            return final
        attempt_dir = Path(request["attempt_dir"])
        # A physical decision may have been persisted just before IPC ended.
        if completed_circuit is None and (attempt_dir / "circuit_result.json").exists():
            completed_circuit = json.loads((attempt_dir / "circuit_result.json").read_text())
        if completed_circuit is not None:
            completed_circuit.update(diagnostic_status="timeout" if timed_out else "worker_error",
                                     attempt_wall_seconds=monotonic() - started)
            if not completed_circuit["accepted"]:
                completed_circuit["diagnostic_status"] = "not_applicable"
            return completed_circuit
        record = {"shot_index": request["shot_index"], "seed": request["seed"],
                  "noise_seed": request["noise_seed"], "noise_model": "pauli_depolarizing",
                  "graph": request["graph"], "extraction": request["extraction"],
                  "history_policy": request.get("history_policy", "triple"),
                  "terminal_extraction": request.get("terminal_extraction", "protected"),
                  "magic_output": request.get("magic_output", "z"),
                  "execution_status": "resource_failure", "accepted": None,
                  "rejection_code": None, "c_state_reference": None,
                  "failure_kind": "timeout" if timed_out else (failure or {}).get("failure_kind", "worker_exit"),
                  "attempt_wall_seconds": monotonic() - started, "worker_exitcode": process.exitcode}
        if failure:
            record["failure_details"] = failure
        if (attempt_dir / "progress.json").exists():
            record["last_progress"] = json.loads((attempt_dir / "progress.json").read_text())
        return record
    finally:
        receiving.close()
        if process.is_alive():
            process.terminate()
            process.join(timeout=3)


def wilson(successes, trials):
    if not trials:
        return None
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z*z/trials
    middle = (p + z*z/(2*trials)) / denominator
    half = z * math.sqrt(p*(1-p)/trials + z*z/(4*trials*trials)) / denominator
    return {"low": max(0, middle-half), "high": min(1, middle+half), "confidence": 0.95, "method": "Wilson"}


def summarize(records):
    total = len(records)
    resolved = [r for r in records if r["execution_status"] == "completed"]
    accepted = [r for r in resolved if r["accepted"]]
    rejected = [r for r in resolved if not r["accepted"]]
    unresolved = total - len(resolved)
    assessed = [r for r in accepted if r.get("diagnostic_status") == "completed"]
    fidelities = [Fraction(r["decoded_C_diagnostics"]["decoded_target_fidelity"]) for r in assessed]
    sum_fidelity = sum(fidelities, Fraction(0))
    mean = sum_fidelity/len(assessed) if assessed else None
    missing = len(accepted)-len(assessed)
    events = Counter()
    axes = Counter()
    for r in resolved:
        events.update(r["noise"]["event_counts_by_channel"])
        axes.update(r["noise"]["pauli_factor_counts"])
    violations = [r["shot_index"] for r in assessed if r["noise"]["sampled_events"] <= 2
                  and Fraction(r["decoded_C_diagnostics"]["decoded_target_fidelity"]) != 1]
    return {"attempts_requested": total, "circuit_attempts_completed": len(resolved),
            "accepted": len(accepted), "rejected": len(rejected), "unresolved_attempts": unresolved,
            "rejection_counts": dict(Counter(r["rejection_code"] for r in rejected)),
            "computational_failure_counts": dict(Counter(r["failure_kind"] for r in records
                                                          if r["execution_status"] != "completed")),
            "observed_rejection_fraction_among_completed": str(Fraction(len(rejected), len(resolved))) if resolved else None,
            "rejection_fraction_Wilson95_among_completed": wilson(len(rejected), len(resolved)),
            "rejection_fraction_bounds_over_all_requested": [str(Fraction(len(rejected), total)),
                                                              str(Fraction(len(rejected)+unresolved, total))] if total else None,
            "completed_subset_may_be_selection_biased": bool(unresolved),
            "ideal_noiseless_rejection_reference": "1/4" if records and records[0].get("magic_output", "z") == "y" else "3/8",
            "accepted_diagnostics_completed": len(assessed),
            "accepted_diagnostics_unavailable": missing,
            "accepted_decoded_exact": sum(f == 1 for f in fidelities),
            "accepted_decoded_imperfect": sum(f < 1 for f in fidelities),
            "mean_decoded_fidelity_among_assessed_accepted": str(mean) if mean is not None else None,
            "mean_decoded_infidelity_among_assessed_accepted": str(1-mean) if mean is not None else None,
            "decoded_fidelity_bounds_among_known_accepted": [str(sum_fidelity/len(accepted)),
                                                              str((sum_fidelity+missing)/len(accepted))] if accepted else None,
            "accepted_raw_exact_target_matches": sum(bool(r.get("exact_magic_target_match")) for r in accepted),
            "noise_event_counts_by_channel_completed": dict(events), "pauli_factor_counts_completed": dict(axes),
            "noise_events_per_completed_attempt": dict(Counter(str(r["noise"]["sampled_events"]) for r in resolved)),
            "max_worker_peak_rss_bytes": max((r.get("worker_peak_rss_bytes", r["metrics"]["process_peak_rss_bytes"])
                                               for r in resolved), default=0),
            "max_peak_coherent_terms_completed": max((r["metrics"]["peak_coherent_terms"] for r in resolved), default=0),
            "max_fallback_overlaps_completed": max((r["metrics"]["fallback_overlaps"] for r in resolved), default=0),
            "two_fault_prediction_violation_shots": violations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0, help="Born seed for attempt k: seed + k")
    parser.add_argument("--noise-seed", type=int, help="Noise seed for attempt k: noise-seed + k; otherwise hash of Born seed")
    parser.add_argument("--two-qubit-infidelity", default="1e-4")
    parser.add_argument("--one-qubit-infidelity", default="0")
    parser.add_argument("--three-qubit-infidelity", default="0", help="Noise on atomic Fredkins")
    parser.add_argument("--idle-infidelity", default="0", help="Per single-qubit serial waiting interval, not a duration")
    parser.add_argument("--preparation-flip-probability", default="0")
    parser.add_argument("--readout-flip-probability", default="0")
    parser.add_argument("--graph", choices=tuple(GRAPHS), default="current20")
    parser.add_argument("--extraction", choices=("optimized", "verified_cat"), default="optimized")
    parser.add_argument("--history-policy", choices=HISTORY_POLICIES, default="triple",
                        help="Use adaptive to try five-round reference certificates; triple retains the original rule")
    parser.add_argument("--terminal-extraction", choices=TERMINAL_EXTRACTIONS, default="protected")
    parser.add_argument("--magic-output", choices=MAGIC_OUTPUTS, default="y")
    parser.add_argument("--source-mode", choices=("encoded", "projected"), default="encoded")
    parser.add_argument("--max-terms", type=int, default=4096)
    parser.add_argument("--attempt-timeout", type=float, default=60, help="Worker wall-clock seconds, including diagnosis")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("output/c4-helix-depolarizing-pilot"))
    args = parser.parse_args()
    if args.shots < 1 or args.max_terms < 1 or not math.isfinite(args.attempt_timeout) or args.attempt_timeout <= 0:
        parser.error("shots, max-terms, and finite attempt-timeout must be positive")
    try:
        model = DepolarizingModel(**{k: getattr(args, k) for k in DepolarizingModel.__dataclass_fields__})
    except ValueError as error:
        parser.error(str(error))
    if args.output_dir.exists():
        parser.error("Choose a new output directory; existing runs are never overwritten")
    args.output_dir.mkdir(parents=True)
    directory = args.output_dir.resolve()
    graph = GRAPHS[args.graph]
    graph.validate()
    manifest = {"schema_version": 1, "procedure": "reduced_rejection", "noise_model": model.manifest(),
                "graph": {"name": graph.name, "edges": graph.edges, "cycles": graph.cycles, "tree_edges": graph.tree_edges},
                "extraction": args.extraction, "source_preparation": args.source_mode,
                "history_policy": args.history_policy,
                "terminal_extraction": args.terminal_extraction,
                "terminal_flag_policy": "repair_then_protected" if args.terminal_extraction == "compact_flagged" else None,
                "magic_output": args.magic_output, "ideal_success_probability": ideal_success_probability(args.magic_output),
                "seed": args.seed, "noise_seed_base": args.noise_seed, "attempts_requested": args.shots,
                "measurement_seed_rule": "seed + shot_index",
                "noise_seed_rule": "noise_seed_base + shot_index" if args.noise_seed is not None else
                "first 8 bytes of SHA256('depolarizing-noise:' + str(measurement_seed)), big endian",
                "attempt_timeout_seconds": args.attempt_timeout, "max_terms": args.max_terms,
                "workers": 1, "worker_lifetime": "one isolated process per attempt",
                "diagnostic_decoder": "ideal syndrome projection; fixed weight<=2 lookup; fixed GF2 fallback",
                "noise_study_enabled": True}
    write_json(directory / "manifest.json", manifest)
    records = []
    started = perf_counter()
    with (directory / "shots.jsonl").open("x") as stream:
        for index in range(args.shots):
            attempt_dir = directory / "attempts" / f"{index:06d}"
            attempt_dir.mkdir(parents=True)
            seed = args.seed + index
            request = {"directory": str(directory), "attempt_dir": str(attempt_dir), "shot_index": index,
                       "seed": seed, "noise_seed": default_noise_seed(seed) if args.noise_seed is None else args.noise_seed+index,
                       "model_rates": model.manifest()["rates"], "graph": graph.name,
                       "extraction": args.extraction, "source_mode": args.source_mode,
                       "history_policy": args.history_policy,
                       "terminal_extraction": args.terminal_extraction,
                       "magic_output": args.magic_output,
                       "max_terms": args.max_terms, "trace": args.trace}
            record = isolated_attempt(request, args.attempt_timeout)
            records.append(record)
            stream.write(json.dumps(record) + "\n")
            stream.flush()
            outcome = "accepted" if record.get("accepted") else record.get("rejection_code", "unresolved")
            if record["execution_status"] != "completed":
                outcome = "unresolved: " + record["failure_kind"]
            print(f"attempt {index}: {outcome}; {record['attempt_wall_seconds']:.2f}s", flush=True)
            snapshot = summarize(records)
            snapshot.update(completed=len(records) == args.shots, elapsed_seconds=perf_counter()-started,
                            noise_model=model.manifest(), graph=graph.name, extraction=args.extraction,
                            history_policy=args.history_policy, terminal_extraction=args.terminal_extraction,
                            terminal_flag_policy="repair_then_protected" if args.terminal_extraction == "compact_flagged" else None,
                            magic_output=args.magic_output)
            write_json(directory / "summary.json", snapshot)
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
