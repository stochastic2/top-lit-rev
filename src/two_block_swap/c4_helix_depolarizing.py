"""Sampled Pauli depolarization at the physical runtime's operation boundaries.

Rates on quantum gates are AVERAGE GATE INFIDELITIES. A nonidentity
n-qubit Pauli is applied with total probability p=(2**n+1)/2**n * r,
uniformly among 4**n-1 choices. Noise draws and Born draws use separate
RNGs. No fault-count cap or ideal-syndrome oracle is used.
"""

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

from c4_helix_reduced_gadgets import NoiselessRuntime


def probability(value):
    if isinstance(value, bool):
        raise ValueError("A probability must be a number, not a boolean")
    try:
        value = Fraction(str(value)) if isinstance(value, float) else Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("Expected a finite rational probability") from error
    if not 0 <= value <= 1:
        raise ValueError("A probability must lie between zero and one")
    return value


def nonidentity_probability(infidelity, qubits):
    if qubits not in (1, 2, 3):
        raise ValueError("Supported depolarizing arities are one, two, and three")
    p = probability(infidelity) * Fraction(2**qubits + 1, 2**qubits)
    if p > 1:
        raise ValueError(f"Infidelity exceeds the Pauli-channel maximum for {qubits} qubits")
    return p


def coin(rng, p):
    """Exact rational Bernoulli draw; zero rates consume no random numbers."""
    return bool(p == 1 or (p and rng.randrange(p.denominator) < p.numerator))


def nonidentity_pauli(rng, qubits):
    """Target 0 is the least-significant base-four digit; all non-I words uniform."""
    if qubits not in (1, 2, 3):
        raise ValueError("Supported Pauli arities are one, two, and three")
    code = 1 + rng.randrange(4**qubits - 1)
    return tuple("IXYZ"[(code >> (2*j)) & 3] for j in range(qubits))


@dataclass(frozen=True)
class DepolarizingModel:
    two_qubit_infidelity: Fraction = Fraction(1, 10000)
    one_qubit_infidelity: Fraction = Fraction(0)
    three_qubit_infidelity: Fraction = Fraction(0)
    idle_infidelity: Fraction = Fraction(0)
    preparation_flip_probability: Fraction = Fraction(0)
    readout_flip_probability: Fraction = Fraction(0)

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, probability(getattr(self, name)))
        for n in (1, 2, 3):
            nonidentity_probability(self.gate_infidelity(n), n)
        nonidentity_probability(self.idle_infidelity, 1)

    def gate_infidelity(self, n):
        return {1: self.one_qubit_infidelity, 2: self.two_qubit_infidelity,
                3: self.three_qubit_infidelity}[n]

    def gate_probability(self, n):
        return nonidentity_probability(self.gate_infidelity(n), n)

    def manifest(self):
        return {"name": "pauli_depolarizing", "gate_rate_convention": "average_gate_infidelity",
                "rates": {k: str(getattr(self, k)) for k in self.__dataclass_fields__},
                "nonidentity_gate_probabilities": {str(n): str(self.gate_probability(n)) for n in (1, 2, 3)},
                "idle_nonidentity_probability": str(nonidentity_probability(self.idle_infidelity, 1)),
                "quantum_noise_timing": "gate: after ideal operation; idle: before operation",
                "preparation_noise": "X after zero preparation",
                "readout_noise": "classical report flip after actual destructive Z measurement",
                "fredkin_implementation": "atomic_three_qubit",
                "idle_interval": "one interval per serial physical operation, no calibrated duration",
                "noise_correlations": "independent channel draws; joint Pauli within a gate",
                "fault_count_cap": None}


class DepolarizingRuntime(NoiselessRuntime):
    """Same sparse physical runtime, with channels sampled only on executed operations."""

    def __init__(self, rng, noise_rng, model=None, trace=None, max_terms=4096, history_policy="triple"):
        super().__init__(rng, trace, max_terms, history_policy)
        self.noise_rng = noise_rng
        self.model = model if model is not None else DepolarizingModel()
        self.noise_events = []
        self.channel_opportunities = Counter()
        self.channel_event_counts = Counter()
        self.pauli_factor_counts = Counter()
        self._operation = None

    def _noise_event(self, location, timing, channel, targets, axes=()):
        paulis = {q: p for q, p in zip(targets, axes) if p != "I"}
        for label, pauli in paulis.items():
            # A noise update is not an additional recursively noisy gate.
            self.state = self.state.gate(pauli, label)
            self.pauli_factor_counts[pauli] += 1
        index = len(self.noise_events)
        event = {"id": index, "physical_event_index": self.events, "location": location,
                 "timing": timing, "channel": channel, "operation": self._operation,
                 "targets": list(targets), "paulis": paulis,
                 "flip_report": channel == "readout_flip"}
        self.noise_events.append(event)
        self.channel_event_counts[channel] += 1
        if self.trace is not None:
            self.trace({"kind": "noise", **event})
        return index

    def _apply(self, location, when, targets, measurement=False):
        if self._operation is None:
            raise RuntimeError("Noise must be sampled inside a physical operation")
        used = []
        if when == "idle":
            waiting = self.live.difference(targets)
            self.channel_opportunities["idle"] += len(waiting)
            p = nonidentity_probability(self.model.idle_infidelity, 1)
            if p:
                for label in sorted(waiting):
                    if coin(self.noise_rng, p):
                        used.append(self._noise_event(location, when, "idle_depolarizing", (label,),
                                                      nonidentity_pauli(self.noise_rng, 1)))
        elif when == "after":
            if self._operation == "PREP":
                self.channel_opportunities["preparation"] += 1
                if coin(self.noise_rng, self.model.preparation_flip_probability):
                    used.append(self._noise_event(location, when, "preparation_flip", targets, ("X",)))
            else:
                n = len(targets)
                self.channel_opportunities[f"gate_{n}q"] += 1
                if coin(self.noise_rng, self.model.gate_probability(n)):
                    used.append(self._noise_event(location, when, f"gate_{n}q_depolarizing", targets,
                                                  nonidentity_pauli(self.noise_rng, n)))
        elif when == "report":
            self.channel_opportunities["readout"] += 1
            if coin(self.noise_rng, self.model.readout_flip_probability):
                used.append(self._noise_event(location, when, "readout_flip", targets))
        return used

    def _event(self, location, operation, targets, fault_indices, **details):
        # PhysicalRuntime uses the return list of report hooks to flip the
        # report, but stochastic events have their own namespace in the trace.
        super()._event(location, operation, targets, [], noise_event_indices=fault_indices, **details)

    def prepare(self, location, label):
        self._operation = "PREP"
        try:
            return super().prepare(location, label)
        finally:
            self._operation = None

    def gate(self, location, operation, *targets):
        self._operation = operation
        try:
            return super().gate(location, operation, *targets)
        finally:
            self._operation = None

    def measure_z(self, location, label):
        self._operation = "MZ"
        try:
            return super().measure_z(location, label)
        finally:
            self._operation = None

    def noise_summary(self):
        hazards = sum((self.channel_opportunities[f"gate_{n}q"] * self.model.gate_probability(n)
                       for n in (1, 2, 3)), Fraction(0))
        hazards += self.channel_opportunities["idle"] * nonidentity_probability(self.model.idle_infidelity, 1)
        hazards += self.channel_opportunities["preparation"] * self.model.preparation_flip_probability
        hazards += self.channel_opportunities["readout"] * self.model.readout_flip_probability
        return {"sampled_events": len(self.noise_events), "channel_opportunities": dict(self.channel_opportunities),
                "event_counts_by_channel": dict(self.channel_event_counts),
                "pauli_factor_counts": dict(self.pauli_factor_counts),
                "sum_of_executed_channel_probabilities": str(hazards), "events": self.noise_events}
