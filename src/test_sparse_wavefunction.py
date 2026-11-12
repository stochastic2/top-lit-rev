"""Independent NumPy/SciPy matrix checks of the integer sparse backend."""

from fractions import Fraction
from random import Random

import numpy as np
import pytest
from scipy import sparse

from sparse_wavefunction import SparseState, sample_binary


def example_state():
    return SparseState(("a", "b", "c"),
                       {"000": 2, "001": -1, "011": 3, "101": -2, "110": 1})


@pytest.mark.parametrize("position", range(3))
def test_hadamard_against_scipy_matrix(position):
    state = example_state()
    h = sparse.csr_array(np.array([[1, 1], [1, -1]]) / np.sqrt(2))
    operator = sparse.kron(sparse.eye(2 ** position),
                           sparse.kron(h, sparse.eye(2 ** (2 - position))))
    actual = state.hadamard(state.labels[position])
    np.testing.assert_allclose(actual.to_numpy(), operator @ state.to_numpy(), atol=1e-14)
    assert actual.norm_squared() == 2 * state.norm_squared()
    assert actual.hadamard(state.labels[position]).canonical_payload() == state.canonical_payload()


def test_controlled_and_permutation_gates_against_dense_matrices():
    state = example_state()
    vector = state.to_numpy()
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    swap = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
    toffoli = np.eye(8)[[0, 1, 2, 3, 4, 5, 7, 6]]
    fredkin = np.eye(8)[[0, 1, 2, 3, 4, 6, 5, 7]]
    np.testing.assert_allclose(state.cnot("a", "b").to_numpy(), np.kron(cnot, np.eye(2)) @ vector)
    np.testing.assert_allclose(state.swap("b", "c").to_numpy(), np.kron(np.eye(2), swap) @ vector)
    np.testing.assert_allclose(state.toffoli("a", "b", "c").to_numpy(), toffoli @ vector)
    np.testing.assert_allclose(state.fredkin("a", "b", "c").to_numpy(), fredkin @ vector)
    for basis_index in range(8):
        basis = SparseState(("a", "b", "c"), {format(basis_index, "03b"): 1})
        direct = basis.fredkin("a", "b", "c")
        decomposed = basis.cnot("c", "b").toffoli("a", "b", "c").cnot("c", "b")
        assert direct.weights == decomposed.weights
        np.testing.assert_array_equal(direct.to_numpy(), fredkin[:, basis_index])
    direct = state.fredkin("a", "b", "c")
    decomposed = state.cnot("c", "b").toffoli("a", "b", "c").cnot("c", "b")
    assert direct.weights == decomposed.weights


@pytest.mark.parametrize("position", range(3))
@pytest.mark.parametrize("basis", ("X", "Z"))
def test_both_projection_branches_against_numpy(position, basis):
    state = example_state()
    # Bring the measured axis to the front; the other axes keep their order.
    tensor = np.moveaxis(state.to_numpy().reshape(2, 2, 2), position, 0)
    projector = state.project_x if basis == "X" else state.project_z
    total = Fraction(0)
    for outcome in (0, 1):
        selected, probability = projector(state.labels[position], outcome)
        dense = ((tensor[0] + (-1) ** outcome * tensor[1]) / np.sqrt(2)
                 if basis == "X" else tensor[outcome]).ravel()
        expected_probability = float(np.vdot(dense, dense).real)
        assert float(probability) == pytest.approx(expected_probability)
        total += probability
        assert selected is not None
        assert selected.labels == state.labels[:position] + state.labels[position + 1:]
        np.testing.assert_allclose(selected.to_numpy(), dense / np.sqrt(expected_probability), atol=1e-14)
    assert total == 1
    x_norms = state.x_measurement_norms(state.labels[position])
    z_norms = state.z_measurement_norms(state.labels[position])
    assert sum(x_norms) == 2 * state.norm_squared()
    assert sum(z_norms) == state.norm_squared()


def test_missing_partner_cancellation_and_deterministic_outcomes():
    plus = SparseState(("q",), {"0": 1, "1": 1})
    minus = SparseState(("q",), {"0": 1, "1": -1})
    assert plus.project_x("q", 1) == (None, Fraction(0))
    assert minus.project_x("q", 0) == (None, Fraction(0))
    assert plus.measure_x("q", Random(1))[1:] == (0, Fraction(1))
    assert minus.measure_x("q", Random(1))[1:] == (1, Fraction(1))
    only_one = SparseState(("q", "other"), {"10": 3})
    selected, probability = only_one.project_x("q", 1)
    assert probability == Fraction(1, 2)
    assert selected.weights == {"0": -3}
    assert only_one.project_z("q", 0) == (None, Fraction(0))
    assert sample_binary(0, 7, Random(1)) == 1
    assert sample_binary(7, 0, Random(1)) == 0


def test_pauli_expectations_against_numpy():
    state = example_state()
    paulis = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
              "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}
    vector = state.to_numpy()
    for symbols in ("III", "XZI", "YYX", "YZX", "ZZZ"):
        xs = tuple(q for q, symbol in enumerate(symbols) if symbol in "XY")
        zs = tuple(q for q, symbol in enumerate(symbols) if symbol in "ZY")
        operator = np.kron(np.kron(paulis[symbols[0]], paulis[symbols[1]]), paulis[symbols[2]])
        assert float(state.expectation_pauli(xs, zs)) == pytest.approx(np.vdot(vector, operator @ vector).real)


def test_scipy_export_json_roundtrip_and_common_phase():
    state = example_state()
    column = state.to_scipy_column()
    assert sparse.issparse(column) and column.format == "csc"
    assert column.nnz == len(state.weights)
    assert (column.conjugate().T @ column)[0, 0] == pytest.approx(1)
    payload = state.canonical_payload()
    loaded = SparseState.from_payload(payload)
    assert loaded.canonical_payload() == payload
    assert state.global_sign(-1).canonical_payload() == payload
    scaled = SparseState(state.labels, {key: -3 * value for key, value in state.weights.items()})
    assert scaled.canonical_payload() == payload
    with pytest.raises(ValueError):
        state.to_numpy(max_qubits=2)
    with pytest.raises(ValueError):
        SparseState.from_payload({**payload, "norm_squared": 123})
    with pytest.raises(ValueError):
        state.fredkin("a", "a", "b")
