"""Noiseless sparse-wavefunction simulation of the reduced-rejection procedure.

Every cat, parity helper, source check, Gauss Fredkin, physical correction,
and measurement is executed. The gauge register is not sampled early.
There is deliberately no realistic-noise model or noise-rate CLI option.

Default extraction is cost-optimized: block-local source flags, grouped
preterminal controls, and two initially zero cat scans. --extraction
verified_cat retains the previous individual-port, three-scan circuit.

Default: the existing twenty-edge graph. --graph compact13 selects only
the explicitly described gauging/ungauging appendix variant.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from time import perf_counter

from c4_helix_noiseless import CHECK_SUPPORTS, CONTROLLERS, LOGICAL_X0, preparation_schedule
from c4_helix_magic_y import (
    MAGIC_OUTPUTS, logical_y_ports, corrected_y_bit, output_frame, exact_raw_y_target,
    ideal_success_probability,
)
from c4_helix_fault_runtime import RejectAttempt
from c4_helix_compact_terminal import (
    TERMINAL_EXTRACTIONS, TerminalFlagRecovery, compact_terminal_cost, measure_compact_terminal,
)
from c4_helix_gadget_decoders import decode_b_readout
from c4_helix_reduced_decoders import (
    CURRENT_GRAPH, GRAPHS, GaugeGraph, KnownStateDecoder, ReducedRejection,
    HISTORY_POLICIES, record_history, history_metadata, decode_gauged, decode_gauge_word, decode_joint,
)
from c4_helix_reduced_gadgets import (
    NoiselessRuntime, SourceFlag, measure_repaired_cat, measure_flagged_source,
    measure_grouped_protected_cat, clean_check_cost,
)
from simulate_c4_helix_gadgets import VERTICES, original_family, pauli_ports, source_family
from simulate_c4_helix_sparse import output_diagnostics, process_peak_rss_bytes
from sparse_wavefunction import SparseState


def graph_family(graph):
    family = []
    for v, name in enumerate("abcde"):
        star = tuple(q for q, edge in enumerate(graph.edges) if v in edge)
        family.append((f"vertex/{name}", (("X", (VERTICES[v],)),) + pauli_ports("A", "X", star)))
    for q, (u, v) in enumerate(graph.edges):
        family.append((f"edge/{q}", (("Z", (VERTICES[u],)), ("Z", (f"A_{q}",)),
                                    ("Z", (VERTICES[v],)))))
    return tuple(family)


def gauged_family(graph):
    family = []
    for axis in "XZ":
        for s, support in enumerate(CHECK_SUPPORTS):
            family.append((f"paired/{axis}/{s}",
                           pauli_ports("B", axis, support) + pauli_ports("C", axis, support)))
    for s, cycle in enumerate(graph.cycles):
        family.append((f"cycle/{s}", pauli_ports("A", "Z", cycle)))
    for v, name in enumerate("abcde"):
        star = tuple(q for q, endpoints in enumerate(graph.edges) if v in endpoints)
        ports = pauli_ports("A", "X", star) + tuple(
            ("SWAP", (f"B_{q}", f"C_{q}")) for q in range(4*v, 4*v + 4))
        family.append((f"gauss/{name}", ports))
    return tuple(family)


def exact_magic_target(magic_output="z", y_outcome=None):
    """Independent target from stabilizer supports, not the source encoder."""
    if magic_output == "y":
        return exact_raw_y_target(y_outcome)
    words = {"0" * 20}

    def toggle(word, support):
        return "".join(str(int(bit) ^ (q in support)) for q, bit in enumerate(word))

    for support in CHECK_SUPPORTS:
        words |= {toggle(w, support) for w in words}
    weights = {w: 2 for w in words}
    weights.update({toggle(w, LOGICAL_X0): 1 for w in words})
    return SparseState(tuple(f"C_{q}" for q in range(20)), weights)


def clean_resource_plan(graph, extraction, source_mode="encoded", include_terminal=True,
                        terminal_extraction="protected", magic_output="y"):
    """Counts every clean check in one cycle; selected ungauging SWAPs are extra."""
    families = [("source", source_family(copy)) for copy in "BC"]
    families += [("graph", graph_family(graph)), ("gauged", gauged_family(graph))]
    if include_terminal:
        family = tuple(original_family())
        if magic_output == "y":
            family = family+(("B/logical_Y0", logical_y_ports()),)
        families.append(("terminal", family))
    stages = {}
    total_gates = Counter()
    scans = flags = terminal_flags = checks = 0
    max_leaves = {}
    for stage, family in families:
        gates = Counter()
        for name, ports in family:
            cost = (compact_terminal_cost(ports) if stage == "terminal" and terminal_extraction == "compact_flagged" and name != "B/logical_Y0"
                    else clean_check_cost(ports, stage, extraction))
            gates.update({k: 3*v for k, v in cost["gates"].items()})
            scans += 3*cost["cat_scans"]
            if stage == "terminal" and terminal_extraction == "compact_flagged":
                terminal_flags += 3*cost["flags"]
            else:
                flags += 3*cost["flags"]
            max_leaves[stage] = max(max_leaves.get(stage, 0), cost["leaves"])
        checks += 3*len(family)
        stages.setdefault(stage, Counter()).update(gates)
        total_gates.update(gates)
    encoder = sum(len(preparation_schedule(CHECK_SUPPORTS + ((LOGICAL_X0,) if c == "C" else ()))[1])
                  for c in "BC") if source_mode == "encoded" else 0
    total_gates.update(CX=encoder + 2*len(graph.edges), FREDKIN=20)
    peak = max(40 + len(graph.edges) + 5 + max_leaves["graph"] + 1,
               40 + len(graph.edges) + max_leaves["gauged"] + 1)
    return {"two_qubit_gates_before_ungauging_swaps": total_gates["CX"] + total_gates["CZ"],
            "gate_counts": dict(total_gates), "stages": {k: dict(v) for k, v in stages.items()},
            "check_gadgets": checks, "cat_scans": scans, "flag_bits": flags,
            "terminal_flag_bits": terminal_flags, "peak_live_qubits": peak}


class ReducedRejectionSimulator:
    """One attempt with exact sparse quantum state and reported-bit control.

    The public runner is noiseless. The separate depolarizing runner acts at
    the runtime's named physical operations, retaining this controller.
    No synthetic syndrome or forced measurement outcome is used here.
    """

    def __init__(self, seed=0, graph: GaugeGraph = CURRENT_GRAPH, source_mode="encoded",
                 trace=None, observer=None, rng=None, max_terms=4096, extraction="optimized",
                 history_policy="triple", terminal_extraction="protected", magic_output="y"):
        if source_mode not in ("encoded", "projected"):
            raise ValueError("Source preparation is encoded or projected")
        if extraction not in ("optimized", "verified_cat"):
            raise ValueError("Extraction is optimized or verified_cat")
        graph.validate()
        self.seed, self.graph, self.source_mode = seed, graph, source_mode
        self.extraction = extraction
        self.history_policy = history_policy
        if terminal_extraction not in TERMINAL_EXTRACTIONS:
            raise ValueError("Terminal extraction is protected or compact_flagged")
        self.terminal_extraction = terminal_extraction
        if magic_output not in MAGIC_OUTPUTS:
            raise ValueError("Magic output is y or z")
        self.magic_output = magic_output
        self.runtime = NoiselessRuntime(rng if rng is not None else Random(seed), trace, max_terms, history_policy)
        self.observer = observer
        self._started = False
        self.result = {"schema_version": 2, "procedure": "reduced_rejection", "noise_model": "none",
                       "seed": seed, "graph": graph.name, "source_preparation": source_mode,
                       "extraction": extraction, "history_policy": history_policy,
                       "terminal_extraction": terminal_extraction,
                       "terminal_flag_policy": "repair_then_protected" if terminal_extraction == "compact_flagged" else None,
                       "magic_output": magic_output, "b_y": None, "output_clifford_frame": None,
                       "accepted": False, "rejection_code": None, "rejection_reason": None,
                       "sources": {}, "cycles": [], "b_z": None, "b_decoding": None,
                       "c_state": None}

    def observe(self, stage):
        self.runtime.decision("stage", stage, live_qubits=len(self.runtime.live),
                              coherent_terms=len(self.runtime.state.terms))
        if self.observer is not None:
            self.observer(stage, self.runtime)

    def acquire_record(self, prefix, family, destination, absorb_copy=None, stage="terminal"):
        history = record_history(len(family), prefix, self.history_policy)
        destination["records"] = history.records
        destination["history_policy"] = self.history_policy
        for round_index in range(history.max_rounds):
            reports = []
            for name, ports in family:
                location = f"{prefix}/round/{round_index}/{name}"
                if stage == "terminal" and self.terminal_extraction == "compact_flagged" and name != "B/logical_Y0":
                    report = measure_compact_terminal(self.runtime, location, ports)
                elif self.extraction == "verified_cat":
                    report = measure_repaired_cat(self.runtime, location, ports)
                elif stage == "source":
                    report = measure_flagged_source(self.runtime, location, ports)
                else:
                    report = measure_grouped_protected_cat(self.runtime, location, ports,
                                                          grouped=stage == "gauged")
                reports.append(report)
                if absorb_copy is not None:
                    labels = tuple(f"{absorb_copy}_{q}" for q in range(20))
                    self.runtime.state = self.runtime.state.absorb_local_sum(labels)
            self.runtime.decision("syndrome_round", prefix, round=round_index, reported_bits=reports)
            common = history.add(reports)
            if common is not None:
                destination.update(rounds_used=len(history.records), stopping_record=common, **history_metadata(history))
                self.runtime.decision("stable_record", prefix, rounds_used=len(history.records),
                                      stopping_record=common, **history_metadata(history))
                return common
        raise AssertionError("Complete-record acquisition must return or raise by its round limit")

    def apply_axes(self, prefix, labels, axes):
        if len(labels) != len(axes):
            raise ValueError("Correction labels and Pauli factors have different lengths")
        for q, (label, axis) in enumerate(zip(labels, axes)):
            if axis != "I":
                self.runtime.gate(f"{prefix}/{q}", axis, label)

    def prepare_inputs(self):
        rt = self.runtime
        for copy in "BC":
            rt.reserve_data(tuple(f"{copy}_{q}" for q in range(20)))
        for copy in "BC":
            for q in range(20):
                rt.prepare(f"source/{copy}/prepare/{q}", f"{copy}_{q}")
        for copy in "BC":
            labels = tuple(f"{copy}_{q}" for q in range(20))
            family = source_family(copy)
            source = self.result["sources"][copy] = {"attempts": []}
            for attempt in range(3):
                prefix = f"source/{copy}" if attempt == 0 else f"source/{copy}/retry/{attempt}"
                current = {"attempt_index": attempt}
                source["attempts"].append(current)
                if attempt:
                    # A flagged source has not yet touched the other copy or
                    # the gauge circuit. Discard/reprepare only these qubits.
                    for q, label in enumerate(labels):
                        rt.measure_z(f"{prefix}/discard/{q}", label)
                    rt.reserve_data(labels)
                    for q, label in enumerate(labels):
                        rt.prepare(f"{prefix}/prepare/{q}", label)
                if self.source_mode == "encoded":
                    supports = CHECK_SUPPORTS + ((LOGICAL_X0,) if copy == "C" else ())
                    hadamards, cnots = preparation_schedule(supports)
                    for q in hadamards:
                        rt.gate(f"{prefix}/encode/H/{q}", "H", f"{copy}_{q}")
                    for j, (c, t) in enumerate(cnots):
                        rt.gate(f"{prefix}/encode/CX/{j}", "CX", f"{copy}_{c}", f"{copy}_{t}")
                try:
                    common = self.acquire_record(prefix, family, current, absorb_copy=copy, stage="source")
                except SourceFlag as flag:
                    current.update(outcome="flag_retry", flag=flag.details)
                    rt.decision("source_local_retry", prefix, flag_location=flag.details["location"],
                                flags=flag.details["flags"], syndrome=flag.details["syndrome"])
                    if attempt == 2:
                        raise ReducedRejection("source_retry_limit", "Three local source builds flagged", flag.details)
                    continue
                current["correction"] = KnownStateDecoder(labels, family).decode(common)
                current["outcome"] = "prepared"
                rt.decision("known_state_correction", prefix, labels=labels, paulis=current["correction"])
                self.apply_axes(prefix + "/correction", labels, current["correction"])
                source.update({k: v for k, v in current.items() if k != "attempt_index"})
                break
        self.observe("inputs_prepared")

    def prepare_graph(self, cycle):
        rt = self.runtime
        prefix = f"cycle/{cycle['index']}/graph"
        for label in VERTICES:
            rt.prepare(f"{prefix}/prepare/{label}", label)
        for q in range(len(self.graph.edges)):
            rt.prepare(f"{prefix}/prepare/A_{q}", f"A_{q}")
        for label in VERTICES:
            rt.gate(f"{prefix}/H/{label}", "H", label)
        for q, endpoints in enumerate(self.graph.edges):
            for j, v in enumerate(endpoints):
                rt.gate(f"{prefix}/edge/{q}/endpoint/{j}", "CX", VERTICES[v], f"A_{q}")
        family = graph_family(self.graph)
        labels = VERTICES + tuple(f"A_{q}" for q in range(len(self.graph.edges)))
        common = self.acquire_record(prefix, family, cycle["graph_source"], stage="graph")
        axes = KnownStateDecoder(labels, family).decode(common)
        cycle["graph_source"]["correction"] = axes
        rt.decision("known_state_correction", prefix, labels=labels, paulis=axes)
        self.apply_axes(prefix + "/correction", labels, axes)
        self.observe(prefix + "/prepared")

    def enrich_and_frame(self, cycle):
        rt = self.runtime
        prefix = f"cycle/{cycle['index']}"
        for q, v in enumerate(CONTROLLERS):
            rt.gate(f"{prefix}/enrichment/fredkin/{q}", "FREDKIN", VERTICES[v], f"B_{q}", f"C_{q}")
        self.observe(prefix + "/enriched")
        for v, label in enumerate(VERTICES):
            rt.gate(f"{prefix}/vertex/{v}/H", "H", label)
        reports = tuple(rt.measure_z(f"{prefix}/vertex/{v}/measure", label)
                        for v, label in enumerate(VERTICES))
        cycle["vertex_x"] = reports
        cycle["vertex_reported_parity"] = sum(reports) % 2
        cycle["vertex_word_probability"] = str(rt.vertex_word_probabilities[prefix])
        rt.decision("vertex_selection_deferred", prefix + "/vertex", reported_bits=reports,
                    reported_parity=sum(reports) % 2)
        for q, v in sorted((q, v) for v, q in enumerate(self.graph.tree_edges, 1)):
            if reports[v]:
                rt.gate(f"{prefix}/vertex/frame/{q}", "Z", f"A_{q}")
        self.observe(prefix + "/vertex_feedforward")

    def check_and_repair_gauged(self, cycle):
        prefix = f"cycle/{cycle['index']}/gauged"
        common = self.acquire_record(prefix, gauged_family(self.graph), cycle["gauged"], stage="gauged")
        try:
            decoded = decode_gauged(common, self.graph)
        except ReducedRejection as rejection:
            cycle["gauged"]["decoding"] = rejection.details
            raise
        cycle["gauged"]["decoding"] = decoded
        self.runtime.decision("gauged_decoding", prefix, **decoded)
        for axis, key in (("X", "cycle_x_edges"), ("Z", "gauss_z_edges")):
            for q in sorted(decoded[key]):
                self.runtime.gate(f"{prefix}/correction/{axis}/{q}", axis, f"A_{q}")
        self.observe(prefix + "/repaired")
        return decoded["certified"]

    def ungauge(self, cycle):
        rt = self.runtime
        prefix = f"cycle/{cycle['index']}"
        reports = tuple(rt.measure_z(f"{prefix}/gauge/readout/{q}", f"A_{q}")
                        for q in range(len(self.graph.edges)))
        cycle["gauge_z"] = reports
        decoded = cycle["gauge_decoding"] = decode_gauge_word(reports, self.graph)
        rt.decision("gauge_decoding", prefix + "/gauge", **decoded)
        for q in range(20):
            if decoded["offsets"][q // 4]:
                rt.gate(f"{prefix}/ungauge/swap/{q}", "SWAP", f"B_{q}", f"C_{q}")
        self.observe(prefix + "/ungauged")

    def recover_original(self, cycle):
        prefix = f"cycle/{cycle['index']}/terminal"
        section = cycle["terminal"]
        final_y = self.magic_output == "y" and cycle["gauged"]["decoding"]["certified"]
        family = tuple(original_family())+((("B/logical_Y0", logical_y_ports()),) if final_y else ())
        section["includes_logical_y"] = final_y
        try:
            common = self.acquire_record(prefix, family, section)
            section["extraction_used"] = self.terminal_extraction
        except TerminalFlagRecovery as recovery:
            compact_history = dict(section)
            section.clear()
            section.update(compact_history=compact_history, flag_recovery=recovery.details,
                           extraction_used="protected_fallback", includes_logical_y=final_y)
            self.runtime.decision("terminal_protected_fallback", prefix, recovery=recovery.details)
            common = self.acquire_record(prefix+"/protected_fallback", family, section,
                                         stage="terminal_protected")
        try:
            decoded = decode_joint(common[:36])
        except ReducedRejection as rejection:
            cycle["terminal"]["decoding"] = rejection.details
            raise
        cycle["terminal"]["decoding"] = decoded
        self.runtime.decision("joint_decoding", prefix, **decoded)
        if final_y:
            bit = corrected_y_bit(common[36], decoded["B"])
            reading = {"reported_word_bit": common[36], "logical_bit": bit,
                       "eigenvalue": 1 if bit == 0 else -1, "both_outcomes_kept": True,
                       "source": "joint terminal clean-reference record"}
            section["logical_y_decoding"] = reading
            self.result["b_y"] = reading
            self.result["output_clifford_frame"] = output_frame(bit)
            self.runtime.decision("logical_y_decoding", prefix, **reading)
        for copy in "BC":
            self.apply_axes(f"{prefix}/correction/{copy}", tuple(f"{copy}_{q}" for q in range(20)),
                            decoded[copy])
        self.observe(prefix + "/recovered")

    def read_b(self):
        rt = self.runtime
        reports = tuple(rt.measure_z(f"B/readout/{q}", f"B_{q}") for q in range(20))
        self.result["b_z"] = reports
        if self.magic_output == "y":
            if self.result["b_y"] is None:
                raise ArithmeticError("Y extraction needs a decoded joint terminal Y record")
            self.result["b_decoding"] = {"basis": "Y", "logical_bit": self.result["b_y"]["logical_bit"],
                                         "keep": True, "z_reports_used_only_for_discard": True}
        else:
            self.decode_final_z(reports)
        self.finish_output()

    def decode_final_z(self, reports):
        try:
            decoded = self.result["b_decoding"] = decode_b_readout(reports)
        except RejectAttempt as rejection:
            raise ReducedRejection("b_readout", str(rejection)) from rejection
        self.runtime.decision("B_decoding", "B/readout", **decoded)
        if not decoded["keep"]:
            raise ReducedRejection("logical_B_one", "Decoded B logical Z0 selected one")

    def finish_output(self):
        rt = self.runtime
        if rt.live != {f"C_{q}" for q in range(20)}:
            raise ArithmeticError("An accepted state must contain only the twenty quantum C coordinates")
        state = rt.state.to_sparse()
        self.result["c_state"] = state
        self.result["accepted"] = True
        # This independent diagnostic does not control the acceptance decision.
        self.result["physical_C_diagnostics"] = output_diagnostics(state)
        self.result["exact_magic_target_match"] = state.canonical_payload() == exact_magic_target(
            self.magic_output, None if self.result["b_y"] is None else self.result["b_y"]["logical_bit"]).canonical_payload()
        self.observe("accepted_C")

    def run(self):
        if self._started:
            raise ValueError("Create a fresh simulator for each physical attempt")
        self._started = True
        started = perf_counter()
        try:
            self.prepare_inputs()
            for cycle_index in range(3):
                cycle = {"index": cycle_index, "graph_source": {}, "vertex_x": None,
                         "gauged": {}, "gauge_z": None, "gauge_decoding": None,
                         "terminal": {}, "next_action": None}
                self.result["cycles"].append(cycle)
                self.prepare_graph(cycle)
                self.enrich_and_frame(cycle)
                certified = self.check_and_repair_gauged(cycle)
                self.ungauge(cycle)
                self.recover_original(cycle)
                if certified:
                    cycle["next_action"] = "extract"
                    self.read_b()
                    break
                if cycle_index == 2:
                    cycle["next_action"] = "reject_cycle_limit"
                    raise ReducedRejection("cycle_limit", "Three gauging/ungauging cycles did not certify a positive resource")
                cycle["next_action"] = "regauge"
                self.runtime.decision("regauge", f"cycle/{cycle_index}", next_cycle=cycle_index + 1)
        except ReducedRejection as rejection:
            self.result.update(rejection_code=rejection.code, rejection_reason=str(rejection),
                               rejection_details=rejection.details)
            self.runtime.decision("rejection", "attempt", code=rejection.code, reason=str(rejection),
                                  details=rejection.details)
        rt = self.runtime
        self.result["metrics"] = {
            "elapsed_seconds": perf_counter() - started, "process_peak_rss_bytes": process_peak_rss_bytes(),
            "physical_events": rt.events, "implicit_single_qubit_idles": rt.idle_locations,
            "idle_locations_by_register": dict(rt.idle_locations_by_register),
            "idle_locations_by_operation": dict(rt.idle_locations_by_operation),
            "check_gadgets_completed": rt.check_gadgets_completed,
            "cat_scans_completed": rt.cat_scans, "cats_prepared": rt.cats_prepared,
            "flagged_source_checks": rt.flagged_source_checks, "flag_bits_measured": rt.flag_bits_measured,
            "grouped_protected_checks": rt.grouped_protected_checks,
            "flagged_terminal_checks": rt.flagged_terminal_checks,
            "terminal_flag_bits_measured": rt.terminal_flag_bits_measured,
            "peak_live_qubits": rt.peak_live, "peak_coherent_terms": rt.state.peak_terms,
            "interned_sparse_factors": len(rt.state.store.factors),
            "fallback_overlaps": rt.state.store.fallback_overlaps, "gate_counts": dict(rt.gate_counts),
            "gauging_cycles_started": len(self.result["cycles"]),
        }
        self.result["global_i_power"] = rt.state.global_i_power
        self.result["terminal_flag_records"] = rt.terminal_flag_records
        return self.result


def save_result(result, directory, shot_index):
    """Stream records and deduplicate exact C states without retaining attempts."""
    record = dict(result)
    state = record.pop("c_state")
    record["shot_index"] = shot_index
    record["c_state_reference"] = None
    if state is not None:
        payload = json.dumps(state.canonical_payload(), sort_keys=True, separators=(",", ":"))
        digest = sha256(payload.encode()).hexdigest()
        reference = f"states/{digest}.json"
        path = directory / reference
        path.parent.mkdir(exist_ok=True)
        if not path.exists():
            path.write_text(payload + "\n")
        record["c_state_reference"] = reference
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=1, help="Physical attempts, including intrinsic rejections")
    parser.add_argument("--seed", type=int, default=0, help="Attempt k uses seed + k")
    parser.add_argument("--graph", choices=tuple(GRAPHS), default="current20")
    parser.add_argument("--source-mode", choices=("encoded", "projected"), default="encoded")
    parser.add_argument("--extraction", choices=("optimized", "verified_cat"), default="optimized",
                        help="Optimized physical gadgets, or the retained three-scan baseline")
    parser.add_argument("--history-policy", choices=HISTORY_POLICIES, default="triple",
                        help="Adaptive clean-reference certificate, or the former consecutive triple rule")
    parser.add_argument("--terminal-extraction", choices=TERMINAL_EXTRACTIONS, default="protected")
    parser.add_argument("--magic-output", choices=MAGIC_OUTPUTS, default="y",
                        help="Y keeps both outcomes with a Clifford output frame; z retains the previous target")
    parser.add_argument("--output-dir", type=Path, default=Path("output/c4-helix-reduced-noiseless"))
    parser.add_argument("--trace", action="store_true", help="Record every physical operation and adaptive decision")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--max-terms", type=int, default=4096, help="Checked exact-state limit; never truncates amplitudes")
    args = parser.parse_args()
    if args.shots < 1 or args.max_terms < 1:
        parser.error("shots and max-terms must be positive")
    if args.output_dir.exists():
        parser.error("Choose a new output directory; existing runs are never overwritten")
    args.output_dir.mkdir(parents=True)
    graph = GRAPHS[args.graph]
    manifest = {"schema_version": 2, "procedure": "reduced_rejection", "noise_model": "none",
                "graph": {"name": graph.name, "edges": graph.edges, "cycles": graph.cycles,
                          "tree_edges": graph.tree_edges}, "source_preparation": args.source_mode,
                "extraction": args.extraction, "history_policy": args.history_policy,
                "terminal_extraction": args.terminal_extraction,
                "terminal_flag_policy": "repair_then_protected" if args.terminal_extraction == "compact_flagged" else None,
                "magic_output": args.magic_output,
                "seed": args.seed, "attempt_seed_rule": "seed + shot_index", "attempts_requested": args.shots,
                "max_terms": args.max_terms, "fredkin_implementation": "atomic_three_qubit",
                "schedule": "serial; one idle per live nonparticipant at every physical operation",
                "ideal_success_probability": ideal_success_probability(args.magic_output), "noise_study_enabled": False}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    started = perf_counter()
    accepted = 0
    rejections = Counter()
    total_counts = Counter()
    trace_file = (args.output_dir / "events.jsonl").open("x") if args.trace else None
    shot_index = 0

    def trace(event):
        trace_file.write(json.dumps({"shot_index": shot_index, **event}) + "\n")

    def progress(stage, runtime):
        if not args.quiet:
            print(f"attempt {shot_index}: {stage}; {runtime.events} physical operations", flush=True)

    try:
        with (args.output_dir / "shots.jsonl").open("x") as records:
            for shot_index in range(args.shots):
                simulator = ReducedRejectionSimulator(
                    seed=args.seed + shot_index, graph=graph, source_mode=args.source_mode,
                    trace=trace if trace_file else None, observer=progress, max_terms=args.max_terms,
                    extraction=args.extraction, history_policy=args.history_policy,
                    terminal_extraction=args.terminal_extraction, magic_output=args.magic_output)
                result = simulator.run()
                if result["accepted"] and not result["exact_magic_target_match"]:
                    raise ArithmeticError("Noiseless output does not match the independent exact magic target")
                record = save_result(result, args.output_dir, shot_index)
                records.write(json.dumps(record) + "\n")
                records.flush()
                accepted += record["accepted"]
                if not record["accepted"]:
                    rejections[record["rejection_code"]] += 1
                total_counts.update(record["metrics"]["gate_counts"])
                del simulator, result, record
        summary = {"completed": True, "noise_model": "none", "graph": graph.name, "extraction": args.extraction,
                   "history_policy": args.history_policy,
                   "terminal_extraction": args.terminal_extraction,
                   "terminal_flag_policy": "repair_then_protected" if args.terminal_extraction == "compact_flagged" else None,
                   "magic_output": args.magic_output,
                   "attempts": args.shots, "accepted": accepted, "rejected": args.shots - accepted,
                   "rejection_counts": dict(rejections), "ideal_success_probability": ideal_success_probability(args.magic_output),
                   "observed_noiseless_acceptance_fraction": str(Fraction(accepted, args.shots)),
                   "accepted_states_exactly_validated": accepted, "gate_counts": dict(total_counts),
                   "elapsed_seconds": perf_counter() - started,
                   "process_peak_rss_bytes": process_peak_rss_bytes()}
        (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
    finally:
        if trace_file is not None:
            trace_file.close()


if __name__ == "__main__":
    main()
