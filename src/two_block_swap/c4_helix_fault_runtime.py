"""Named physical locations, Pauli injections, actual/reported bits, and trace.

Default gate faults apply a Pauli product after the ideal operation, on its
participants. ``idle`` faults act on live nonparticipants before that
operation (the following serial interval). Measurement Pauli faults use
``before``; classical report faults use ``report`` and flip only the report.
All lists are deterministic experiments, not a stochastic noise model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from random import Random
from typing import Callable

from sparse_gadget_state import FactorStore, SparseProductState


@dataclass(frozen=True)
class PauliFault:
    location: str
    paulis: dict[str, str] = field(default_factory=dict)
    when: str = "after"
    flip_report: bool = False

    def __post_init__(self):
        if self.when not in ("before", "after", "idle", "report"):
            raise ValueError("Fault timing is before, after, idle, or report")
        if not self.location or any(p not in ("X", "Y", "Z") for p in self.paulis.values()):
            raise ValueError("Each fault needs a location and X/Y/Z labels")
        if self.when == "report":
            if not self.flip_report or self.paulis:
                raise ValueError("A report fault flips a report and has no quantum Pauli")
        elif self.flip_report or not self.paulis:
            raise ValueError("A quantum fault needs Pauli targets and cannot flip a report")
        if self.when == "idle" and len(self.paulis) != 1:
            raise ValueError("One idle fault is one single-qubit waiting location")


class RejectAttempt(ValueError):
    """A required report, decoder, or stopping criterion rejects this attempt."""


class PhysicalRuntime:
    def __init__(self, rng: Random, faults=(), trace: Callable[[dict], None] | None = None,
                 max_terms=4096):
        self.rng = rng
        self.state = SparseProductState(FactorStore(), max_terms=max_terms)
        self.faults = tuple(faults)
        self.applied: set[int] = set()
        self.trace = trace
        self.events = 0
        self.live: set[str] = set()
        self.peak_live = 0
        self.gate_counts: dict[str, int] = {}
        self.measurement_probability = Fraction(1)

    def reserve_data(self, labels):
        """Mathematical zero factor; qubits become live at their PREP events."""
        self.state = self.state.add_zero_factor(tuple(labels))

    def _apply(self, location, when, targets, measurement=False):
        used = []
        for index, fault in enumerate(self.faults):
            if index in self.applied or fault.location != location or fault.when != when:
                continue
            if when == "report":
                if not measurement:
                    raise ValueError(f"Report fault targets a non-measurement: {location}")
            else:
                requested = set(fault.paulis)
                if not requested <= self.live:
                    raise ValueError(f"Fault at {location} targets non-live qubits")
                if when == "idle":
                    if requested & set(targets):
                        raise ValueError("An idle fault must target live nonparticipants")
                elif not requested <= set(targets):
                    raise ValueError("An operation fault must target its participants")
                if measurement and when == "after":
                    raise ValueError("A destructive measurement needs before/report timing")
                for label, pauli in fault.paulis.items():
                    self.state = self.state.gate(pauli, label)
            self.applied.add(index)
            used.append(index)
        return used

    def _event(self, location, operation, targets, fault_indices, **details):
        self.events += 1
        self.gate_counts[operation] = self.gate_counts.get(operation, 0) + 1
        self.peak_live = max(self.peak_live, len(self.live))
        if self.trace is not None:
            self.trace({"index": self.events - 1, "location": location,
                        "operation": operation, "targets": list(targets),
                        "live_qubits": len(self.live), "coherent_terms": len(self.state.terms),
                        "applied_fault_indices": fault_indices, **details})

    def prepare(self, location, label):
        if label in self.live:
            raise ValueError("Helpers must be measured/discarded before reuse")
        if any(f.location == location and f.when in ("before", "report") for f in self.faults):
            raise ValueError("Preparation faults use after; waiting faults use idle")
        used = self._apply(location, "idle", (label,))
        if label not in self.state.quantum_labels():
            self.state = self.state.allocate(label)
        self.live.add(label)
        used += self._apply(location, "after", (label,))
        self._event(location, "PREP", (label,), used)

    def gate(self, location, operation, *targets):
        if not set(targets) <= self.live:
            raise ValueError(f"Gate at {location} targets non-live qubits")
        if any(f.location == location and f.when == "report" for f in self.faults):
            raise ValueError("Report flips require a measurement location")
        used = self._apply(location, "idle", targets)
        used += self._apply(location, "before", targets)
        self.state = self.state.gate(operation, *targets)
        used += self._apply(location, "after", targets)
        self._event(location, operation, targets, used)

    def measure_z(self, location, label):
        if label not in self.live:
            raise ValueError("Measurement targets an absent qubit")
        used = self._apply(location, "idle", (label,))
        used += self._apply(location, "before", (label,), measurement=True)
        # Diagnose an invalid after-measurement request instead of silently
        # leaving it pending forever after the measured qubit is removed.
        if any(f.location == location and f.when == "after" for f in self.faults):
            raise ValueError("Use before/report for a destructive measurement fault")
        self.state, actual, probability = self.state.measure_z(label, self.rng)
        report_faults = self._apply(location, "report", (label,), measurement=True)
        used += report_faults
        reported = (actual + len(report_faults)) % 2
        self.live.remove(label)
        self.measurement_probability *= probability
        self._event(location, "MZ", (label,), used, actual=actual, reported=reported,
                    probability=str(probability))
        return reported

    def measure_x(self, location, label):
        """The physical H and Z meter have separate injectable locations."""
        self.gate(location + "/H", "H", label)
        return self.measure_z(location + "/measure", label)

    def log_check(self, location, raw_bits, parity):
        if self.trace is not None:
            self.trace({"kind": "check", "location": location,
                        "leaf_reports": list(raw_bits), "reported_parity": parity,
                        "coherent_terms": len(self.state.terms)})


def measure_verified_cat(runtime: PhysicalRuntime, location: str, ports,
                         require_positive=True) -> int:
    """Integrated V2 Section 4, executed gate by gate with fresh helpers.

    ports = [('X',(target,)), ('Z',(target,)), ('SWAP',(left,right)), ...].
    Prepare (|0^m>+|1^m>)/sqrt(2), verify every adjacent ZZ three times,
    couple each leaf to one port, then read all leaves in X.

    Ideal only: K_lambda(Q)=2^(-(m+1)/2)(I+(-1)^y Q), y=sum(lambda) mod 2.
    The implementation does not replace the faulty gadget by this projector.
    """
    ports = tuple(ports)
    targets = [label for _, labels in ports for label in labels]
    if not ports or len(set(targets)) != len(targets):
        raise ValueError("Check ports must be nonempty and disjoint")
    leaves = tuple(f"L_{j}" for j in range(len(ports)))
    for j, label in enumerate(leaves):
        runtime.prepare(f"{location}/cat/prepare/{j}", label)
    runtime.gate(location + "/cat/H", "H", leaves[0])
    for j in range(len(leaves) - 1):
        runtime.gate(f"{location}/cat/chain/{j}", "CX", leaves[j], leaves[j + 1])
    for scan in range(3):
        for j in range(len(leaves) - 1):
            prefix = f"{location}/verify/{scan}/{j}"
            runtime.prepare(prefix + "/prepare", "w")
            runtime.gate(prefix + "/left", "CX", leaves[j], "w")
            runtime.gate(prefix + "/right", "CX", leaves[j + 1], "w")
            if runtime.measure_z(prefix + "/measure", "w"):
                raise RejectAttempt(f"Cat verification failed at {prefix}")
    for j, (operator, targets) in enumerate(ports):
        gate = {"X": "CX", "Z": "CZ", "SWAP": "FREDKIN"}[operator]
        runtime.gate(f"{location}/couple/{j}", gate, leaves[j], *targets)
    reports = tuple(runtime.measure_x(f"{location}/readout/{j}", label)
                    for j, label in enumerate(leaves))
    parity = sum(reports) % 2
    runtime.log_check(location, reports, parity)
    if require_positive and parity:
        raise RejectAttempt(f"Required positive check failed at {location}")
    return parity
