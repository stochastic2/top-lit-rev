"""Exact sparse wavefunctions for the C4-Helix circuit.

Representation (simulation plan V2, Section 4)::

    |psi> = sum_x weights[x] |x> / sqrt(N),  N = sum_x weights[x]**2.

Keys are ordinary strings of '0' and '1', in ``labels`` order. Weights and
Born probabilities use Python integers and Fraction; NumPy/SciPy conversion
is an explicit, floating-point export. No amplitudes are truncated.

Treat ``weights`` as read-only: gates and selected projections return new
states. A state contains actual basis amplitudes, not a mixture of branches.

The legacy SparseState uses real integer weights. GaussianSparseState
adds exact complex Gaussian-integer weights for logical-Y extraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd, sqrt
from random import Random
from typing import Iterator, Mapping, Sequence

import numpy as np
from scipy import sparse


def sample_binary(norm_zero: int, norm_one: int, rng: Random) -> int:
    """Draw s with Pr(s) = norm_s / (norm_zero + norm_one), exactly.

    ``randrange`` samples an integer; there is no conversion to float.
    This also handles a deterministic measurement without drawing a number.
    """
    if norm_zero < 0 or norm_one < 0 or norm_zero + norm_one == 0:
        raise ValueError("Measurement norms must be nonnegative with positive sum")
    if norm_zero == 0:
        return 1
    if norm_one == 0:
        return 0
    return int(rng.randrange(norm_zero + norm_one) >= norm_zero)


def _add_weight(output: dict[str, int], key: str, contribution: int) -> None:
    """Add amplitudes at a colliding key, including exact cancellation."""
    total = output.get(key, 0) + contribution
    if total:
        output[key] = total
    else:
        output.pop(key, None)


def _exchange_characters(key: str, left: int, right: int) -> str:
    if left > right:
        left, right = right, left
    if key[left] == key[right]:
        return key
    return key[:left] + key[right] + key[left + 1:right] + key[left] + key[right + 1:]


@dataclass
class SparseState:
    """Integer amplitudes on named quantum coordinates.

    ``SparseState(('q0', 'q1'), {'00': 1, '11': 1})`` represents a Bell state.
    Keep absent amplitudes out of the dictionary and never store zero weights.
    ``validate()`` checks these invariants explicitly; it is not repeated at
    every million-entry permutation gate.
    """

    labels: tuple[str, ...]
    weights: dict[str, int]

    def __post_init__(self) -> None:
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("Quantum coordinate labels must be unique")
        if not self.weights:
            raise ValueError("A normalized state cannot have zero support")

    @classmethod
    def zeros(cls, labels: Sequence[str]) -> SparseState:
        return cls(tuple(labels), {"0" * len(labels): 1})

    def validate(self) -> None:
        for key, weight in self.weights.items():
            if len(key) != len(self.labels) or any(bit not in "01" for bit in key):
                raise ValueError(f"Invalid basis key: {key!r}")
            if type(weight) is not int or weight == 0:
                raise ValueError("Weights must be nonzero Python integers")

    def norm_squared(self) -> int:
        """N = sum_x w(x)^2, the norm of the unnormalized integer vector."""
        return sum(weight * weight for weight in self.weights.values())

    def _positions(self, *labels: str) -> tuple[int, ...]:
        if len(set(labels)) != len(labels):
            raise ValueError("Gate coordinates must be distinct")
        return tuple(self.labels.index(label) for label in labels)

    def hadamard(self, label: str) -> SparseState:
        """Apply H with a common sqrt(2) factor absorbed in normalization.

        For old bit z and weight c: add c to the bit-0 output and (-1)^z c
        to the bit-1 output. Thus w' = sqrt(2) H w and N(w') = 2 N(w).
        Only use this expansion on small sources. Use measure_x on vertices.
        """
        (q,) = self._positions(label)
        output: dict[str, int] = {}
        for key, weight in self.weights.items():
            _add_weight(output, key[:q] + "0" + key[q + 1:], weight)
            sign = 1 if key[q] == "0" else -1
            _add_weight(output, key[:q] + "1" + key[q + 1:], sign * weight)
        return SparseState(self.labels, output)

    def cnot(self, control: str, target: str) -> SparseState:
        """CX|c,t> = |c,t+c mod 2>; a bijective permutation of keys."""
        c, t = self._positions(control, target)
        output = {}
        for key, weight in self.weights.items():
            if key[c] == "1":
                replacement = "1" if key[t] == "0" else "0"
                key = key[:t] + replacement + key[t + 1:]
            output[key] = weight  # Bijective: distinct inputs cannot collide.
        return SparseState(self.labels, output)

    def toffoli(self, control1: str, control2: str, target: str) -> SparseState:
        """CCX, used to independently check the Guppy Fredkin decomposition."""
        c1, c2, t = self._positions(control1, control2, target)
        output = {}
        for key, weight in self.weights.items():
            if key[c1] == key[c2] == "1":
                replacement = "1" if key[t] == "0" else "0"
                key = key[:t] + replacement + key[t + 1:]
            output[key] = weight
        return SparseState(self.labels, output)

    def swap(self, left: str, right: str) -> SparseState:
        """SWAP|l,r> = |r,l>; exchange physical values, not coordinate names."""
        l, r = self._positions(left, right)
        return SparseState(self.labels, {
            _exchange_characters(key, l, r): weight
            for key, weight in self.weights.items()
        })

    def fredkin(self, control: str, left: str, right: str) -> SparseState:
        """F|0,l,r>=|0,l,r>, F|1,l,r>=|1,r,l>; both controls stay coherent."""
        c, l, r = self._positions(control, left, right)
        output = {}
        for key, weight in self.weights.items():
            if key[c] == "1":
                key = _exchange_characters(key, l, r)
            output[key] = weight
        return SparseState(self.labels, output)

    def global_sign(self, sign: int) -> SparseState:
        """Retain the explicit +/- sign from gauge-Z feedforward."""
        if sign not in (-1, 1):
            raise ValueError("The global sign must be +1 or -1")
        if sign == 1:
            return self
        return SparseState(self.labels, {key: -value for key, value in self.weights.items()})

    def _x_pairs(self, q: int) -> Iterator[tuple[str, int, int]]:
        """Visit (remaining key y, a0(y), a1(y)) once, without a large key set.

        A bit-1 key is skipped when its bit-0 partner exists. If its partner
        is absent, the bit-1 key itself owns the pair. Missing weights are zero.
        """
        for key, weight in self.weights.items():
            if key[q] == "0":
                partner = key[:q] + "1" + key[q + 1:]
                yield key[:q] + key[q + 1:], weight, self.weights.get(partner, 0)
            else:
                partner = key[:q] + "0" + key[q + 1:]
                if partner not in self.weights:
                    yield key[:q] + key[q + 1:], 0, weight

    def x_measurement_norms(self, label: str) -> tuple[int, int]:
        """N_b = sum_y (a0(y) + (-1)^b a1(y))^2; N0+N1 = 2N."""
        (q,) = self._positions(label)
        norm_zero = norm_one = 0
        for _, a0, a1 in self._x_pairs(q):
            norm_zero += (a0 + a1) ** 2
            norm_one += (a0 - a1) ** 2
        return norm_zero, norm_one

    def _select_x(self, label: str, outcome: int) -> SparseState:
        (q,) = self._positions(label)
        sign = 1 if outcome == 0 else -1
        output = {}
        for remaining, a0, a1 in self._x_pairs(q):
            value = a0 + sign * a1
            if value:
                output[remaining] = value
        labels = self.labels[:q] + self.labels[q + 1:]
        return SparseState(labels, output)

    def project_x(self, label: str, outcome: int) -> tuple[SparseState | None, Fraction]:
        """Select a specified X outcome; return (conditional state, probability).

        <b_X|z> = (-1)^(bz)/sqrt(2), so Pr(b)=N_b/(2N).
        A zero-probability outcome returns (None, 0). No random sampling occurs.
        """
        if outcome not in (0, 1):
            raise ValueError("Measurement outcomes are 0 or 1")
        norms = self.x_measurement_norms(label)
        probability = Fraction(norms[outcome], sum(norms))
        return (self._select_x(label, outcome) if probability else None), probability

    def measure_x(self, label: str, rng: Random) -> tuple[SparseState, int, Fraction]:
        """Compute both norms, sample b, then build only the selected dictionary."""
        norms = self.x_measurement_norms(label)
        outcome = sample_binary(*norms, rng)
        return self._select_x(label, outcome), outcome, Fraction(norms[outcome], sum(norms))

    def z_measurement_norms(self, label: str) -> tuple[int, int]:
        """N_s = sum_{x: x[q]=s} w(x)^2; N0+N1 = N."""
        (q,) = self._positions(label)
        norms = [0, 0]
        for key, weight in self.weights.items():
            norms[int(key[q])] += weight * weight
        return norms[0], norms[1]

    def _select_z(self, label: str, outcome: int) -> SparseState:
        (q,) = self._positions(label)
        output = {
            key[:q] + key[q + 1:]: weight
            for key, weight in self.weights.items() if key[q] == str(outcome)
        }
        return SparseState(self.labels[:q] + self.labels[q + 1:], output)

    def project_z(self, label: str, outcome: int) -> tuple[SparseState | None, Fraction]:
        """Select Z outcome s with Pr(s)=N_s/N; impossible outcomes return None."""
        if outcome not in (0, 1):
            raise ValueError("Measurement outcomes are 0 or 1")
        norms = self.z_measurement_norms(label)
        probability = Fraction(norms[outcome], sum(norms))
        return (self._select_z(label, outcome) if probability else None), probability

    def measure_z(self, label: str, rng: Random) -> tuple[SparseState, int, Fraction]:
        norms = self.z_measurement_norms(label)
        outcome = sample_binary(*norms, rng)
        return self._select_z(label, outcome), outcome, Fraction(norms[outcome], sum(norms))

    def expectation_pauli(self, x_support: Sequence[int] = (),
                          z_support: Sequence[int] = ()) -> Fraction:
        """Exact expectation of P = i^k X(s)Z(z), k=|s intersect z|.

        A position in both supports denotes physical Y. The numerator before
        i^k is sum_x (-1)^(z.x) w(x) w(x+s). Real states have zero expectation
        for any Pauli with an odd number of Ys. No physical measurement is added.
        """
        xs, zs = set(x_support), set(z_support)
        if any(q < 0 or q >= len(self.labels) for q in xs | zs):
            raise ValueError("Pauli support is outside the state")
        numerator = 0
        for key, weight in self.weights.items():
            changed = list(key)
            for q in xs:
                changed[q] = "1" if key[q] == "0" else "0"
            other = self.weights.get("".join(changed), 0)
            sign = (-1) ** (sum(int(key[q]) for q in zs) % 2)
            numerator += sign * weight * other
        phase_power = len(xs & zs) % 4
        if phase_power in (1, 3):
            if numerator != 0:
                raise ArithmeticError("A Hermitian odd-Y Pauli must have zero expectation on a real state")
            return Fraction(0)
        sign = 1 if phase_power == 0 else -1
        return Fraction(sign * numerator, self.norm_squared())

    def canonical_payload(self) -> dict:
        """JSON-ready exact state, removing an irrelevant common scale and sign."""
        divisor = 0
        for weight in self.weights.values():
            divisor = gcd(divisor, abs(weight))
        if self.weights[min(self.weights)] < 0:
            divisor = -divisor
        weights = {key: self.weights[key] // divisor for key in sorted(self.weights)}
        return {"labels": list(self.labels), "weights": weights,
                "norm_squared": sum(value * value for value in weights.values())}

    @classmethod
    def from_payload(cls, payload: Mapping) -> SparseState:
        if payload.get("amplitude_type") == "gaussian_integer":
            return GaussianSparseState.from_payload(payload)
        state = cls(tuple(payload["labels"]), dict(payload["weights"]))
        state.validate()
        if state.norm_squared() != payload["norm_squared"]:
            raise ValueError("Stored normalization does not match the integer weights")
        return state

    def to_scipy_column(self) -> sparse.csc_array:
        """Export normalized floating amplitudes; the first label is the MSB.

        CSC stores only nonzero entries and a two-element column pointer.
        It does not allocate 2**n amplitudes. Export supports at most 62 labels
        so basis indices and the shape fit SciPy's signed integer indexing.
        """
        if len(self.labels) > 62:
            raise ValueError("SciPy export supports at most 62 coordinates")
        indices = np.fromiter((int(key, 2) if key else 0 for key in self.weights), dtype=np.int64)
        amplitudes = np.fromiter(self.weights.values(), dtype=np.float64) / sqrt(self.norm_squared())
        columns = np.zeros(len(indices), dtype=np.int64)
        return sparse.coo_array((amplitudes.astype(np.complex128), (indices, columns)),
                                shape=(2 ** len(self.labels), 1)).tocsc()

    def to_numpy(self, max_qubits: int = 20) -> np.ndarray:
        """Explicit dense export for small independent comparison tests only."""
        if len(self.labels) > max_qubits:
            raise ValueError("Dense export exceeds max_qubits")
        return self.to_scipy_column().toarray().ravel()


class GaussianSparseState(SparseState):
    """Exact complex sparse amplitudes, without floating-point evolution."""

    def validate(self):
        from gaussian_integer import parts
        for key, weight in self.weights.items():
            if len(key) != len(self.labels) or any(bit not in "01" for bit in key) or not weight:
                raise ValueError("Invalid Gaussian sparse entry")
            parts(weight)

    def norm_squared(self):
        from gaussian_integer import abs_squared
        return sum(abs_squared(w) for w in self.weights.values())

    @staticmethod
    def _complex_state(state):
        return GaussianSparseState(state.labels, state.weights)

    def hadamard(self, label):
        return self._complex_state(super().hadamard(label))

    def cnot(self, control, target):
        return self._complex_state(super().cnot(control, target))

    def toffoli(self, control1, control2, target):
        return self._complex_state(super().toffoli(control1, control2, target))

    def swap(self, left, right):
        return self._complex_state(super().swap(left, right))

    def fredkin(self, control, left, right):
        return self._complex_state(super().fredkin(control, left, right))

    def global_sign(self, sign):
        return self._complex_state(super().global_sign(sign))

    def _select_x(self, label, outcome):
        return self._complex_state(super()._select_x(label, outcome))

    def _select_z(self, label, outcome):
        return self._complex_state(super()._select_z(label, outcome))

    def x_measurement_norms(self, label):
        from gaussian_integer import abs_squared
        q, = self._positions(label)
        pairs = list(self._x_pairs(q))
        return (sum(abs_squared(a+b) for _, a, b in pairs),
                sum(abs_squared(a-b) for _, a, b in pairs))

    def z_measurement_norms(self, label):
        from gaussian_integer import abs_squared
        q, = self._positions(label)
        result = [0, 0]
        for word, weight in self.weights.items():
            result[int(word[q])] += abs_squared(weight)
        return tuple(result)

    def expectation_pauli(self, x_support=(), z_support=()):
        from gaussian_integer import conjugate, phase, real_part, imag_part
        xs, zs = set(x_support), set(z_support)
        if any(q < 0 or q >= len(self.labels) for q in xs | zs):
            raise ValueError("Pauli support is outside the state")
        numerator = 0
        for key, weight in self.weights.items():
            other = "".join(str(int(b) ^ (q in xs)) for q, b in enumerate(key))
            sign = (-1)**sum(int(key[q]) for q in zs)
            numerator += conjugate(self.weights.get(other, 0))*weight*sign
        numerator = phase(numerator, len(xs & zs))
        if imag_part(numerator):
            raise ArithmeticError("A Hermitian Pauli expectation must be real")
        return Fraction(real_part(numerator), self.norm_squared())

    def canonical_payload(self):
        from gaussian_integer import gaussian_gcd, exact_divide, parts, phase, abs_squared
        divisor = 0
        for w in self.weights.values():
            divisor = gaussian_gcd(divisor, w)
        weights = {key: exact_divide(self.weights[key], divisor) for key in sorted(self.weights)}
        first = weights[min(weights)]
        rotation = next(p for p in range(4) if (lambda ab: ab[0] > 0 and ab[1] >= 0)(parts(phase(first, p))))
        weights = {k: phase(w, rotation) for k, w in weights.items()}
        from gaussian_integer import imag_part, real_part
        if not any(imag_part(w) for w in weights.values()):
            return SparseState(self.labels, {k: real_part(w) for k, w in weights.items()}).canonical_payload()
        return {"amplitude_type": "gaussian_integer", "labels": list(self.labels),
                "weights": {k: list(parts(w)) for k, w in weights.items()},
                "norm_squared": sum(abs_squared(w) for w in weights.values())}

    @classmethod
    def from_payload(cls, payload):
        from gaussian_integer import gaussian
        state = cls(tuple(payload["labels"]), {k: gaussian(*w) for k, w in payload["weights"].items()})
        state.validate()
        if state.norm_squared() != payload["norm_squared"]:
            raise ValueError("Stored normalization does not match Gaussian weights")
        return state

    def to_scipy_column(self):
        from gaussian_integer import to_complex
        if len(self.labels) > 62:
            raise ValueError("SciPy export supports at most 62 coordinates")
        indices = np.fromiter((int(k, 2) if k else 0 for k in self.weights), dtype=np.int64)
        amplitudes = np.fromiter((to_complex(w) for w in self.weights.values()), dtype=np.complex128)/sqrt(self.norm_squared())
        return sparse.coo_array((amplitudes, (indices, np.zeros(len(indices), dtype=np.int64))),
                                shape=(2**len(self.labels), 1)).tocsc()


def exact_sparse_state(labels, weights):
    from gaussian_integer import imag_part, real_part
    if any(imag_part(w) for w in weights.values()):
        return GaussianSparseState(tuple(labels), weights)
    return SparseState(tuple(labels), {k: real_part(w) for k, w in weights.items()})
