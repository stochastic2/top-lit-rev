"""Exact sparse product sums for physical cat-state gadgets.

The represented (unnormalized) vector is

    |eta> = sum_(z,F) c[z,F] |z> tensor product_(f in F) |f>,
    |f> = sum_x f.weights[x] |x on f.labels>.

``z`` explicitly stores quantum basis values of V, A, and helpers. Each
data factor is an explicit sparse dictionary, not a stabilizer tableau.
Terms are coherent: their inner products, including cross terms, determine
every Born probability. SWAP changes physical labels of data factors;
it does not expand their tensor product into a million-entry dictionary.

Data factors remain real. Exact Gaussian-integer coherent coefficients
support S/SDG phases on explicit cat/basis qubits for logical-Y extraction.
Physical Y=iXZ uses a real XZ action plus a tracked global i phase.
No gauge measurement is moved across a Gauss gadget.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from itertools import product
from math import gcd
from random import Random

from sparse_wavefunction import SparseState, sample_binary, exact_sparse_state
from gaussian_integer import conjugate, abs_squared, real_part, imag_part, phase, content


@dataclass
class Factor:
    labels: tuple[str, ...]
    weights: dict[str, int]
    norm: int


class FactorStore:
    """Intern equivalent sparse factors and cache gate actions and overlaps."""

    def __init__(self):
        self.factors: list[Factor] = []
        self.identities: dict[tuple, int] = {}
        self.actions: dict[tuple, tuple[int, int]] = {}
        self.overlaps: dict[tuple, int] = {}
        self.fallback_overlaps = 0

    def intern(self, labels, weights) -> tuple[int, int]:
        """Return (factor id, integer scale), preserving the unnormalized ket."""
        entries = tuple(sorted((key, value) for key, value in weights.items() if value))
        if not entries:
            raise ValueError("Cannot intern a zero vector")
        scale = reduce(gcd, (abs(value) for _, value in entries))
        if entries[0][1] < 0:
            scale = -scale
        canonical = tuple((key, value // scale) for key, value in entries)
        signature = (tuple(labels), canonical)
        if signature not in self.identities:
            self.identities[signature] = len(self.factors)
            self.factors.append(Factor(tuple(labels), dict(canonical), sum(v * v for _, v in canonical)))
        return self.identities[signature], scale

    def action(self, factor_id: int, operation: str, targets: tuple[str, ...]) -> tuple[int, int]:
        """Sparse local gates; memoization is especially useful for repeated checks."""
        cache_key = (factor_id, operation, targets)
        if cache_key in self.actions:
            return self.actions[cache_key]
        factor = self.factors[factor_id]
        state = SparseState(factor.labels, factor.weights)
        if operation == "H":
            transformed = state.hadamard(targets[0])
        elif operation == "CX":
            transformed = state.cnot(*targets)
        elif operation in ("X", "Z"):
            q = factor.labels.index(targets[0])
            weights = {}
            for key, value in factor.weights.items():
                if operation == "X":
                    key = key[:q] + ("1" if key[q] == "0" else "0") + key[q + 1:]
                elif key[q] == "1":
                    value = -value
                weights[key] = value
            transformed = SparseState(factor.labels, weights)
        else:
            raise ValueError(f"Unsupported factor gate {operation}")
        answer = self.intern(transformed.labels, transformed.weights)
        self.actions[cache_key] = answer
        return answer

    def rename(self, factor_id: int, left: str, right: str) -> tuple[int, int]:
        cache_key = (factor_id, "rename", left, right)
        if cache_key not in self.actions:
            factor = self.factors[factor_id]
            labels = tuple(right if label == left else left if label == right else label
                           for label in factor.labels)
            self.actions[cache_key] = self.intern(labels, factor.weights)
        return self.actions[cache_key]

    def project_z(self, factor_id: int, target: str, outcome: int) -> tuple[int | None, int]:
        cache_key = (factor_id, "MZ", target, outcome)
        if cache_key not in self.actions:
            factor = self.factors[factor_id]
            q = factor.labels.index(target)
            selected = {key[:q] + key[q + 1:]: value for key, value in factor.weights.items()
                        if key[q] == str(outcome)}
            answer = (None, 0) if not selected else self.intern(
                factor.labels[:q] + factor.labels[q + 1:], selected)
            self.actions[cache_key] = answer
        return self.actions[cache_key]

    def inner_product(self, left_ids: tuple[int, ...], right_ids: tuple[int, ...]) -> int:
        """Exact overlap of sparse product kets, without flattening the full state.

        Matching partitions factorize into dictionary dot products. For
        differently partitioned data (possible after faulty partial SWAPs),
        enumerate one product ket and look up its amplitudes in the other.
        The slower fallback is cached; it is not an orthogonality assumption.
        """
        cache_key = tuple(sorted((left_ids, right_ids)))
        if cache_key in self.overlaps:
            return self.overlaps[cache_key]
        left = [self.factors[i] for i in left_ids]
        right = [self.factors[i] for i in right_ids]
        right_by_support = {frozenset(f.labels): f for f in right}
        if len(left) == len(right) and all(frozenset(f.labels) in right_by_support for f in left):
            result = 1
            for a in left:
                b = right_by_support[frozenset(a.labels)]
                positions = tuple(a.labels.index(label) for label in b.labels)
                if a.labels == b.labels:
                    value = sum(weight * b.weights.get(key, 0) for key, weight in a.weights.items())
                else:
                    value = sum(weight * b.weights.get("".join(key[q] for q in positions), 0)
                                for key, weight in a.weights.items())
                result *= value
                if result == 0:
                    break
        else:
            self.fallback_overlaps += 1
            labels = tuple(label for factor in left for label in factor.labels)
            lookups = [tuple(labels.index(label) for label in factor.labels) for factor in right]
            result = 0
            for entries in product(*(factor.weights.items() for factor in left)):
                word = "".join(key for key, _ in entries)
                value = 1
                for _, amplitude in entries:
                    value *= amplitude
                for factor, positions in zip(right, lookups):
                    value *= factor.weights.get("".join(word[q] for q in positions), 0)
                    if value == 0:
                        break
                result += value
        self.overlaps[cache_key] = result
        return result


class SparseProductState:
    """Coherent product sum with exact integer/Gaussian-integer weights."""

    def __init__(self, store: FactorStore, basis_labels=(), terms=None, max_terms=4096):
        self.store = store
        self.basis_labels = tuple(basis_labels)
        self.terms = terms if terms is not None else {("", ()): 1}
        self.max_terms = max_terms
        self.global_i_power = 0
        self.peak_terms = len(self.terms)

    def _combine(self, contributions, labels=None, reduce_common=False):
        terms = {}
        for basis, factors, weight in contributions:
            factors = tuple(sorted(factors))
            key = (basis, factors)
            terms[key] = terms.get(key, 0) + weight
            if terms[key] == 0:
                del terms[key]
        if len(terms) > self.max_terms:
            raise MemoryError(f"Coherent term limit exceeded: {len(terms)} > {self.max_terms}")
        if reduce_common and terms:
            divisor = content(terms.values())
            if divisor > 1:
                terms = {key: value // divisor for key, value in terms.items()}
        result = SparseProductState(self.store, self.basis_labels if labels is None else labels,
                                    terms, self.max_terms)
        result.global_i_power = self.global_i_power
        result.peak_terms = max(self.peak_terms, len(terms))
        return result

    def add_zero_factor(self, labels):
        fid, scale = self.store.intern(tuple(labels), {"0" * len(labels): 1})
        return self._combine((basis, factors + (fid,), weight * scale)
                             for (basis, factors), weight in self.terms.items())

    def absorb_local_sum(self, labels):
        """Exactly add source-projection branches into one explicit sparse factor.

        Terms with the same other factors and basis word differ only on this
        source register. Replace sum_j c_j |f_j> by the dictionary whose
        entries are sum_j c_j f_j(x). This keeps raw-zero source preparation
        from producing 512*1024 separate product terms. No approximation or
        encoded-state assumption is made.
        """
        labels = tuple(labels)
        groups = {}
        for (basis, factors), coefficient in self.terms.items():
            chosen = [fid for fid in factors if self.store.factors[fid].labels == labels]
            if len(chosen) != 1:
                raise ValueError("Local absorption requires one consistently ordered source factor")
            remaining = tuple(fid for fid in factors if fid != chosen[0])
            key = (basis, remaining)
            output = groups.setdefault(key, {})
            for word, weight in self.store.factors[chosen[0]].weights.items():
                output[word] = output.get(word, 0) + coefficient * weight
        contributions = []
        for (basis, remaining), weights in groups.items():
            weights = {word: value for word, value in weights.items() if value}
            if weights:
                fid, scale = self.store.intern(labels, weights)
                contributions.append((basis, remaining + (fid,), scale))
        return self._combine(contributions, reduce_common=True)

    def allocate(self, label):
        if label in self.quantum_labels():
            raise ValueError(f"Qubit {label} is already allocated")
        return self._combine(((basis + "0", factors, weight)
                              for (basis, factors), weight in self.terms.items()),
                             labels=self.basis_labels + (label,))

    def quantum_labels(self):
        if not self.terms:
            return self.basis_labels
        _, factors = next(iter(self.terms))
        return self.basis_labels + tuple(label for fid in factors for label in self.store.factors[fid].labels)

    def norm_squared(self):
        groups = {}
        for (basis, factors), weight in self.terms.items():
            groups.setdefault(basis, []).append((factors, weight))
        norm = 0
        for entries in groups.values():
            for i, (left, a) in enumerate(entries):
                norm += abs_squared(a) * self.store.inner_product(left, left)
                for right, b in entries[i + 1:]:
                    norm += 2 * real_part(conjugate(a)*b) * self.store.inner_product(left, right)
        if norm < 0:
            raise ArithmeticError("A coherent norm cannot be negative")
        return norm

    def inner_product(self, other):
        if self.store is not other.store or self.basis_labels != other.basis_labels:
            raise ValueError("Inner products need the same factor store and basis coordinates")
        groups = {}
        for (basis, factors), weight in other.terms.items():
            groups.setdefault(basis, []).append((factors, weight))
        return sum(conjugate(a) * b * self.store.inner_product(left, right)
                   for (basis, left), a in self.terms.items()
                   for right, b in groups.get(basis, ()))

    def expectation_pauli(self, paulis):
        """Read-only exact Pauli probe, including interference; no gadget is run."""
        transformed = self
        for label, axis in paulis.items():
            transformed = transformed.gate(axis, label)
        overlap = self.inner_product(transformed)
        phase = (transformed.global_i_power - self.global_i_power) % 4
        from gaussian_integer import phase as rotate_phase
        overlap = rotate_phase(overlap, phase)
        if imag_part(overlap):
            raise ArithmeticError("Hermitian Pauli expectation must be real")
        return Fraction(real_part(overlap), self.norm_squared())

    def _data_action(self, factors, operation, targets):
        positions = [i for i, fid in enumerate(factors)
                     if all(target in self.store.factors[fid].labels for target in targets)]
        if len(positions) != 1:
            raise ValueError(f"{operation}{targets} must act within one data factor")
        index = positions[0]
        fid, scale = self.store.action(factors[index], operation, targets)
        updated = list(factors)
        updated[index] = fid
        return tuple(updated), scale

    def gate(self, operation, *targets):
        """Physical H, CX, CZ, SWAP, Fredkin, and Pauli gates.

        All coherent controls of this procedure have an explicit basis value
        in each term. No control bit is sampled by this gate implementation.
        """
        if len(set(targets)) != len(targets):
            raise ValueError("Gate targets must be distinct")
        if any(target not in self.quantum_labels() for target in targets):
            raise ValueError(f"A gate targets an absent qubit: {targets}")
        if operation == "Y":
            result = self.gate("Z", *targets).gate("X", *targets)
            result.global_i_power = (self.global_i_power + 1) % 4
            return result
        contributions = []
        for (basis, factors), weight in self.terms.items():
            if operation in ("X", "Z", "H", "S", "SDG"):
                target = targets[0]
                if target in self.basis_labels:
                    q = self.basis_labels.index(target)
                    if operation == "X":
                        basis = basis[:q] + ("1" if basis[q] == "0" else "0") + basis[q + 1:]
                    elif operation == "Z":
                        weight *= (-1) ** int(basis[q])
                    elif operation in ("S", "SDG"):
                        if basis[q] == "1":
                            weight = phase(weight, 1 if operation == "S" else 3)
                    else:
                        contributions.append((basis[:q] + "0" + basis[q + 1:], factors, weight))
                        contributions.append((basis[:q] + "1" + basis[q + 1:], factors,
                                              weight * (-1) ** int(basis[q])))
                        continue
                else:
                    factors, scale = self._data_action(factors, operation, targets)
                    weight *= scale
            elif operation in ("CX", "CZ"):
                control, target = targets
                if control in self.basis_labels:
                    bit = int(basis[self.basis_labels.index(control)])
                    if bit:
                        axis = "X" if operation == "CX" else "Z"
                        if target in self.basis_labels:
                            q = self.basis_labels.index(target)
                            if axis == "X":
                                basis = basis[:q] + ("1" if basis[q] == "0" else "0") + basis[q + 1:]
                            else:
                                weight *= (-1) ** int(basis[q])
                        else:
                            factors, scale = self._data_action(factors, axis, (target,))
                            weight *= scale
                elif operation == "CX":
                    factors, scale = self._data_action(factors, operation, targets)
                    weight *= scale
                else:
                    raise ValueError("CZ requires a cat/basis control in this procedure")
            elif operation in ("SWAP", "FREDKIN"):
                left, right = targets[-2:]
                active = operation == "SWAP" or basis[self.basis_labels.index(targets[0])] == "1"
                if active:
                    renamed = []
                    for fid in factors:
                        factor = self.store.factors[fid]
                        if left in factor.labels or right in factor.labels:
                            fid, scale = self.store.rename(fid, left, right)
                            weight *= scale
                        renamed.append(fid)
                    factors = tuple(renamed)
            else:
                raise ValueError(f"Unsupported gate: {operation}")
            contributions.append((basis, factors, weight))
        return self._combine(contributions)

    def project_z(self, label, outcome):
        """Construct an unnormalized branch; sampling uses coherent norms."""
        contributions = []
        labels = self.basis_labels
        if label in labels:
            q = labels.index(label)
            labels = labels[:q] + labels[q + 1:]
            for (basis, factors), weight in self.terms.items():
                if int(basis[q]) == outcome:
                    contributions.append((basis[:q] + basis[q + 1:], factors, weight))
        else:
            for (basis, factors), weight in self.terms.items():
                updated = []
                for fid in factors:
                    if label in self.store.factors[fid].labels:
                        fid, scale = self.store.project_z(fid, label, outcome)
                        if fid is None:
                            weight = 0
                            break
                        weight *= scale
                    if self.store.factors[fid].labels:
                        updated.append(fid)
                if weight:
                    contributions.append((basis, tuple(updated), weight))
        return self._combine(contributions, labels=labels)

    def measure_z(self, label, rng: Random):
        candidates = [self.project_z(label, bit) for bit in (0, 1)]
        norms = [candidate.norm_squared() for candidate in candidates]
        bit = sample_binary(*norms, rng)
        selected = candidates[bit]
        selected = selected._combine(((basis, factors, weight)
                                      for (basis, factors), weight in selected.terms.items()),
                                     reduce_common=True)
        return selected, bit, Fraction(norms[bit], sum(norms))

    def to_sparse(self, max_entries=2_000_000):
        """Flatten a small final state or a test fixture, never the full gauged state."""
        labels = tuple(sorted(self.quantum_labels()))
        weights = {}
        for (basis, factors), coefficient in self.terms.items():
            all_labels = self.basis_labels + tuple(label for fid in factors for label in self.store.factors[fid].labels)
            positions = tuple(all_labels.index(label) for label in labels)
            for entries in product(*(self.store.factors[fid].weights.items() for fid in factors)):
                word = basis + "".join(key for key, _ in entries)
                value = coefficient
                for _, amplitude in entries:
                    value *= amplitude
                key = "".join(word[q] for q in positions)
                weights[key] = weights.get(key, 0) + value
                if weights[key] == 0:
                    del weights[key]
                if len(weights) > max_entries:
                    raise MemoryError("Explicit sparse export exceeds max_entries")
        # Restore natural numeric physical order, e.g. C_2 before C_10.
        ordered = tuple(sorted(labels, key=lambda name: (name.split('_')[0], int(name.split('_')[-1])
                                                        if name.split('_')[-1].isdigit() else 0)))
        indices = tuple(labels.index(label) for label in ordered)
        return exact_sparse_state(ordered, {"".join(key[q] for q in indices): value for key, value in weights.items()})
