"""Separate full-gadget sparse simulator with named, injectable Pauli faults.

Implements integrated V2: verified sources and graph; twenty enrichment
Fredkins; vertex feedforward; three paired/cycle/Gauss rounds; full gauge
decoding; three original-code filters; repeated-syndrome recovery; decoded
B readout. Every check executes its physical verified-cat circuit.

Default source preparation uses the unitary-encoding alternative allowed
in integrated V2 Section 5, followed by the full three verified source
rounds. --source-mode projected instead executes the literal raw-zero
postselected sources of that section (ideal source yield 2^-19).
The previous noiseless Guppy and sparse simulators are unchanged.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import json
from pathlib import Path
from random import Random
from time import perf_counter

from c4_helix_noiseless import (
    CHECK_SUPPORTS, CONTROLLERS, EDGES, LOGICAL_X0, LOGICAL_Z0, LOGICAL_Z1,
    TREE_EDGES, preparation_schedule,
)
from c4_helix_fault_runtime import PauliFault, PhysicalRuntime, RejectAttempt, measure_verified_cat
from c4_helix_gadget_decoders import decode_b_readout, decode_gauge, recovery_from_history
from simulate_c4_helix_sparse import output_diagnostics, process_peak_rss_bytes


CYCLE_SUPPORTS = (
    (7, 15), (11, 12), (3, 6), (0, 10), (8, 19), (14, 16), (4, 9), (2, 13),
    (1, 18), (5, 17), (7, 8, 11), (7, 14, 3), (7, 4, 0), (11, 2, 3),
    (11, 1, 0), (3, 5, 0),
)
VERTICES = tuple(f"V_{name}" for name in "abcde")


def pauli_ports(copy, axis, support):
    return tuple((axis, (f"{copy}_{q}",)) for q in support)


def source_family(copy):
    checks = [(f"{axis}/{s}", pauli_ports(copy, axis, support))
              for axis in "XZ" for s, support in enumerate(CHECK_SUPPORTS)]
    checks += [("logical/0", pauli_ports(copy, "Z" if copy == "B" else "X",
                                       LOGICAL_Z0 if copy == "B" else LOGICAL_X0)),
               ("logical/1", pauli_ports(copy, "Z", LOGICAL_Z1))]
    return checks


def original_family():
    """Section 14 ordering: B-X, B-Z, C-X, C-Z; increasing support index."""
    return [(f"{copy}/{axis}/{s}", pauli_ports(copy, axis, support))
            for copy in "BC" for axis in "XZ" for s, support in enumerate(CHECK_SUPPORTS)]


def gauged_family():
    """Sections 9--11: eighteen paired, sixteen cycles, then five Gauss checks."""
    family = []
    for axis in "XZ":
        for s, support in enumerate(CHECK_SUPPORTS):
            family.append((f"paired/{axis}/{s}",
                           pauli_ports("B", axis, support) + pauli_ports("C", axis, support)))
    for s, cycle in enumerate(CYCLE_SUPPORTS):
        family.append((f"cycle/{s}", pauli_ports("A", "Z", cycle)))
    for v, name in enumerate("abcde"):
        star = tuple(q for q, endpoints in enumerate(EDGES) if v in endpoints)
        ports = pauli_ports("A", "X", star) + tuple(
            ("SWAP", (f"B_{q}", f"C_{q}")) for q in range(4 * v, 4 * v + 4))
        family.append((f"gauss/{name}", ports))
    return family


class GadgetSimulator:
    """One serial attempt, carrying actual states and reported-bit histories.

    max_terms is a checked resource limit, not a truncation. An overflow
    raises rather than producing an approximate or spuriously accepted state.
    trace receives each gate and each check record; stream it rather than
    storing the entire trace in memory for large fault sweeps.
    """

    def __init__(self, seed=0, faults=(), trace=None, max_terms=4096, observer=None, probes=None,
                 source_mode="encoded", rng=None):
        if source_mode not in ("encoded", "projected"):
            raise ValueError("Source mode is encoded or projected")
        self.source_mode = source_mode
        self.runtime = PhysicalRuntime(rng if rng is not None else Random(seed), faults, trace, max_terms)
        self.observer = observer
        self.probes = probes or {}
        self.checks = 0
        self.history = []
        self.result = {"accepted": False, "source_preparation": source_mode,
                       "vertex_x": None, "gauge_z": None, "b_z": None,
                       "recovery_records": self.history, "c_state": None}
        self.result["probe_history"] = []

    def observe(self, stage):
        if self.probes:
            values = {name: (str(self.runtime.state.expectation_pauli(paulis))
                             if set(paulis) <= self.runtime.live else None)
                      for name, paulis in self.probes.items()}
            self.result["probe_history"].append({"stage": stage, "expectations": values})
        if self.observer is not None:
            self.observer(stage, self.runtime)

    def family(self, prefix, family, positive=True):
        reports = []
        for name, ports in family:
            report = measure_verified_cat(self.runtime, prefix + "/" + name, ports, positive)
            if prefix.startswith("source/"):
                copy = prefix.split("/")[1]
                self.runtime.state = self.runtime.state.absorb_local_sum(tuple(f"{copy}_{q}" for q in range(20)))
            self.checks += 1
            reports.append(report)
        return tuple(reports)

    def prepare_inputs(self):
        rt = self.runtime
        for copy in "BC":
            labels = tuple(f"{copy}_{q}" for q in range(20))
            rt.reserve_data(labels)
        for copy in "BC":
            for q in range(20):
                rt.prepare(f"source/{copy}/prepare/{q}", f"{copy}_{q}")
        for copy in "BC":
            if self.source_mode == "encoded":
                generators = CHECK_SUPPORTS + ((LOGICAL_X0,) if copy == "C" else ())
                hadamards, cnots = preparation_schedule(generators)
                for q in hadamards:
                    rt.gate(f"source/{copy}/encode/H/{q}", "H", f"{copy}_{q}")
                for index, (control, target) in enumerate(cnots):
                    rt.gate(f"source/{copy}/encode/CX/{index}", "CX", f"{copy}_{control}", f"{copy}_{target}")
            for round_index in range(3):
                self.family(f"source/{copy}/round/{round_index}", source_family(copy))
        self.observe("verified_inputs")

    def prepare_graph(self):
        rt = self.runtime
        for label in VERTICES:
            rt.prepare(f"graph/prepare/{label}", label)
        for q in range(20):
            rt.prepare(f"graph/prepare/A_{q}", f"A_{q}")
        for label in VERTICES:
            rt.gate(f"graph/H/{label}", "H", label)
        for q, endpoints in enumerate(EDGES):
            for endpoint_index, v in enumerate(endpoints):
                rt.gate(f"graph/edge/{q}/endpoint/{endpoint_index}", "CX", VERTICES[v], f"A_{q}")
        checks = []
        for v, name in enumerate("abcde"):
            star = tuple(q for q, edge in enumerate(EDGES) if v in edge)
            checks.append((f"vertex/{name}", (("X", (VERTICES[v],)),) + pauli_ports("A", "X", star)))
        for q, (u, v) in enumerate(EDGES):
            checks.append((f"edge/{q}", (("Z", (VERTICES[u],)), ("Z", (f"A_{q}",)), ("Z", (VERTICES[v],)))))
        for round_index in range(3):
            self.family(f"graph/round/{round_index}", checks)
        self.observe("verified_graph")

    def enrich_and_frame(self):
        rt = self.runtime
        for q, v in enumerate(CONTROLLERS):
            rt.gate(f"enrichment/fredkin/{q}", "FREDKIN", VERTICES[v], f"B_{q}", f"C_{q}")
        self.observe("enriched")
        # Match the Guppy source's all-H-before-any-vertex-meter ordering.
        for v, label in enumerate(VERTICES):
            rt.gate(f"vertex/{v}/H", "H", label)
        bits = tuple(rt.measure_z(f"vertex/{v}/measure", label) for v, label in enumerate(VERTICES))
        self.result["vertex_x"] = bits
        if sum(bits) % 2:
            raise RejectAttempt("Reported vertex parity selected the negative SWAP branch")
        for v, q in enumerate(TREE_EDGES, 1):
            if bits[v]:
                rt.gate(f"vertex/frame/{q}", "Z", f"A_{q}")
        self.observe("vertex_feedforward")

    def ungauge(self):
        rt = self.runtime
        reports = tuple(rt.measure_z(f"gauge/readout/{q}", f"A_{q}") for q in range(20))
        self.result["gauge_z"] = reports
        decoded = decode_gauge(reports)
        self.result["gauge_decoding"] = decoded
        for q in range(20):
            if decoded["offsets"][q // 4]:
                rt.gate(f"ungauge/swap/{q}", "SWAP", f"B_{q}", f"C_{q}")
        self.observe("ungauged")

    def recover(self):
        rt = self.runtime
        for round_index in range(9):
            reports = self.family(f"recovery/round/{round_index}", original_family(), positive=False)
            self.history.append(reports)
            decoded = recovery_from_history(self.history)
            if decoded is not None:
                self.result["recovery_decoding"] = decoded
                for copy in "BC":
                    for q, pauli in enumerate(decoded[copy]):
                        if pauli != "I":
                            rt.gate(f"recovery/correction/{copy}/{q}", pauli, f"{copy}_{q}")
                self.observe("recovered")
                return

    def read_b(self):
        rt = self.runtime
        reports = tuple(rt.measure_z(f"B/readout/{q}", f"B_{q}") for q in range(20))
        self.result["b_z"] = reports
        decoded = decode_b_readout(reports)
        self.result["b_decoding"] = decoded
        if not decoded["keep"]:
            raise RejectAttempt("Decoded B logical Z0 selected one")
        self.result["c_state"] = rt.state.to_sparse()
        self.result["accepted"] = True
        self.observe("accepted_C")

    def run(self):
        started = perf_counter()
        try:
            self.prepare_inputs()
            self.prepare_graph()
            self.enrich_and_frame()
            for round_index in range(3):
                self.family(f"gauged/round/{round_index}", gauged_family())
                self.observe(f"gauged_round_{round_index}")
            self.ungauge()
            for round_index in range(3):
                self.family(f"filter/round/{round_index}", original_family())
            self.observe("filtered")
            self.recover()
            self.read_b()
        except RejectAttempt as rejection:
            self.result["rejection_reason"] = str(rejection)
        rt = self.runtime
        self.result["metrics"] = {"elapsed_seconds": perf_counter() - started,
                                  "process_peak_rss_bytes": process_peak_rss_bytes(),
                                  "physical_events": rt.events, "check_gadgets_completed": self.checks,
                                  "peak_live_qubits": rt.peak_live,
                                  "peak_coherent_terms": rt.state.peak_terms,
                                  "interned_sparse_factors": len(rt.state.store.factors),
                                  "fallback_overlaps": rt.state.store.fallback_overlaps,
                                  "gate_counts": rt.gate_counts}
        self.result["applied_fault_indices"] = sorted(rt.applied)
        self.result["unreached_fault_indices"] = sorted(set(range(len(rt.faults))) - rt.applied)
        self.result["global_i_power"] = rt.state.global_i_power
        return self.result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--faults", type=Path, help="JSON list of PauliFault dictionaries")
    parser.add_argument("--probes", type=Path, help="JSON mapping of probe names to {qubit: Pauli}")
    parser.add_argument("--output-dir", type=Path, default=Path("output/c4-helix-gadgets"))
    parser.add_argument("--trace", action="store_true", help="Stream every physical location to events.jsonl")
    parser.add_argument("--max-terms", type=int, default=4096)
    parser.add_argument("--source-mode", choices=("encoded", "projected"), default="encoded")
    args = parser.parse_args()
    faults = [PauliFault(**entry) for entry in json.loads(args.faults.read_text())] if args.faults else []
    probes = json.loads(args.probes.read_text()) if args.probes else None
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    if result_path.exists():
        parser.error("Choose a new output directory; result.json already exists")
    trace_file = (args.output_dir / "events.jsonl").open("x") if args.trace else None

    def trace(event):
        trace_file.write(json.dumps(event) + "\n")

    def progress(stage, runtime):
        print(f"{stage}: {len(runtime.state.terms)} coherent terms, {runtime.events} physical locations", flush=True)

    try:
        simulator = GadgetSimulator(args.seed, faults, trace if trace_file else None,
                                    args.max_terms, progress, probes, args.source_mode)
        result = simulator.run()
        state = result.pop("c_state")
        if state is not None:
            (args.output_dir / "c_state.json").write_text(json.dumps(state.canonical_payload()) + "\n")
            result["c_state_reference"] = "c_state.json"
            result["physical_C_diagnostics"] = output_diagnostics(state)
        result["requested_faults"] = [asdict(fault) for fault in faults]
        result_path.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"accepted": result["accepted"], **result["metrics"]}, indent=2))
    finally:
        if trace_file is not None:
            trace_file.close()


if __name__ == "__main__":
    main()
