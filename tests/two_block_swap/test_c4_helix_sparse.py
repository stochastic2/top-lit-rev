"""Physical branch checks for the V2 sparse simulation, including a full attempt.

The original-order nineteen-qubit statevector below is an independent NumPy
reference. It keeps all gauge sectors and measures the vertices before A.
The sparse method measures A first and must reproduce every joint branch.
"""

from collections import Counter
from fractions import Fraction
from itertools import product
import json
from random import Random

import numpy as np
import pytest

from simulate_c4_helix_sparse import (
    CircuitSpecification, ShotResult, SparseC4HelixSimulator,
    output_diagnostics, write_result,
)
from sparse_wavefunction import SparseState


def repetition_specification():
    return CircuitSpecification(
        data_qubits=5, edges=((0, 1), (0, 2), (0, 3), (0, 4)),
        controllers=(0, 1, 2, 3, 4), tree_edges=(0, 1, 2, 3),
        b_source_generators=(), c_source_generators=((0, 1, 2, 3, 4),),
        b_logical_z0=(0,),
    )


def apply_dense_gate(vector, matrix, coordinates, n_qubits):
    """Independent tensor-axis gate application on a dense NumPy vector."""
    axes = list(coordinates) + [q for q in range(n_qubits) if q not in coordinates]
    tensor = vector.reshape((2,) * n_qubits).transpose(axes)
    transformed = matrix @ tensor.reshape(2 ** len(coordinates), -1)
    return transformed.reshape((2,) * n_qubits).transpose(np.argsort(axes)).ravel()


@pytest.fixture(scope="module")
def dense_original_order():
    """V(5), A(4), B(5), C(5), with gauge readout still in physical order."""
    n = 19
    state = np.zeros(2 ** n, dtype=np.complex128)
    state[0] = 1
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    cx = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    fredkin = np.eye(8)[[0, 1, 2, 3, 4, 6, 5, 7]]
    # B=00000; C=(00000+11111)/sqrt(2), the same input as the existing
    # nineteen-qubit Guppy/Selene probe in test_c4_helix_noiseless.py.
    state = apply_dense_gate(state, h, (14,), n)
    for q in range(1, 5):
        state = apply_dense_gate(state, cx, (14, 14 + q), n)
    for v in range(5):
        state = apply_dense_gate(state, h, (v,), n)
    for q, (u, v) in enumerate(repetition_specification().edges):
        state = apply_dense_gate(state, cx, (u, 5 + q), n)
        state = apply_dense_gate(state, cx, (v, 5 + q), n)
    for q in range(5):
        state = apply_dense_gate(state, fredkin, (q, 9 + q, 14 + q), n)
    for v in range(5):
        state = apply_dense_gate(state, h, (v,), n)
    return state.reshape(32, 16, 1024)


def test_every_joint_branch_matches_original_order_dense_simulation(dense_original_order):
    simulator = SparseC4HelixSimulator(repetition_specification())
    seen_phase_correction = False
    for gauge_word, preimages in simulator.gauge_table.items():
        enriched = simulator.enrich(simulator.conditioned_input(preimages))
        for vertex_bits in product((0, 1), repeat=5):
            conditional = enriched
            probability = Fraction(1, 16)  # Computed gauge-table size.
            for label, bit in zip(simulator.specification.vertex_labels, vertex_bits):
                conditional, p = conditional.project_x(label, bit)
                probability *= p
                assert conditional is not None
            vertex_index = int("".join(map(str, vertex_bits)), 2)
            dense = dense_original_order[vertex_index, int(gauge_word, 2)].copy()
            dense_probability = float(np.vdot(dense, dense).real)
            assert float(probability) == pytest.approx(dense_probability, abs=1e-14)
            expected_vertex_probability = Fraction(3 if sum(vertex_bits) % 2 == 0 else 1, 64)
            assert probability * 16 == expected_vertex_probability
            np.testing.assert_allclose(conditional.to_numpy(), dense / np.sqrt(dense_probability), atol=1e-13)

            if sum(vertex_bits) % 2 == 0:
                exponent = sum(vertex_bits[v] * int(gauge_word[q])
                               for v, q in enumerate(simulator.specification.tree_edges, 1))
                corrected_phase = simulator.apply_vertex_feedforward(conditional, vertex_bits, gauge_word)
                dense *= (-1) ** exponent
                np.testing.assert_allclose(corrected_phase.to_numpy(), dense / np.sqrt(dense_probability), atol=1e-13)
                seen_phase_correction |= exponent % 2 == 1
                corrected, offsets = simulator.correct_swaps(corrected_phase, gauge_word)
                swap = np.eye(4)[[0, 2, 1, 3]]
                for q, offset in enumerate(offsets):
                    if offset:
                        dense = apply_dense_gate(dense, swap, (q, 5 + q), 10)
                np.testing.assert_allclose(corrected.to_numpy(), dense / np.sqrt(dense_probability), atol=1e-13)

                # In either ordering, inspect all 32 physical B words and the
                # complete conditional C amplitudes, not only logical parity.
                for b_index in range(32):
                    word = format(b_index, "05b")
                    selected = corrected
                    conditional_probability = Fraction(1)
                    for label, bit in zip(simulator.b_labels, word):
                        selected, p = selected.project_z(label, int(bit))
                        conditional_probability *= p
                        if selected is None:
                            break
                    c_vector = dense.reshape(32, 32)[b_index] / np.sqrt(dense_probability)
                    p_dense = float(np.vdot(c_vector, c_vector).real)
                    assert float(conditional_probability) == pytest.approx(p_dense, abs=1e-13)
                    if selected is not None:
                        np.testing.assert_allclose(selected.to_numpy(), c_vector / np.sqrt(p_dense), atol=1e-13)
    assert seen_phase_correction


class PrescribedOutcomes:
    """Choose a gauge word and physical bits through the sampler's integer interface.

    This is a test RNG, not an alternative state-preparation implementation.
    After the five vertex draws it chooses zero (or one) whenever a B
    measurement is nondeterministic. Deterministic measurements need no draw.
    """

    def __init__(self, gauge_index, vertex_bits, b_bit=0):
        self.gauge_index = gauge_index
        self.vertex_bits = iter(vertex_bits)
        self.b_bit = b_bit
        self.first = True

    def randrange(self, stop):
        if self.first:
            self.first = False
            assert 0 <= self.gauge_index < stop
            return self.gauge_index
        bit = next(self.vertex_bits, self.b_bit)
        return stop - 1 if bit else 0


def test_rejections_hide_unperformed_measurements_and_seeded_stream():
    simulator = SparseC4HelixSimulator(repetition_specification())
    odd = simulator.simulate_attempt(PrescribedOutcomes(0, (1, 0, 0, 0, 0)))
    assert not odd.accepted and not odd.swap_plus
    assert odd.vertex_probability_given_gauge == Fraction(1, 64)
    assert odd.gauge_z is odd.swap_offsets is odd.b_z is odd.c_state is None
    failed_b = simulator.simulate_attempt(PrescribedOutcomes(0, (0, 0, 0, 0, 0), b_bit=1))
    assert failed_b.swap_plus and not failed_b.accepted and failed_b.b_logical_z0 == 1
    assert failed_b.b_probability_given_vertex_gauge == Fraction(1, 6)
    assert failed_b.c_state is None
    signatures = lambda seed: [(r.vertex_x, r.gauge_z, r.b_z, r.accepted)
                               for r in simulator.iter_attempts(12, seed)]
    assert signatures(33) == signatures(33)
    with pytest.raises(ValueError):
        list(simulator.iter_attempts(-1))


def test_full_65_qubit_accepted_trajectory_and_exact_saved_output(tmp_path):
    simulator = SparseC4HelixSimulator()
    assert len(simulator.b_source.weights) == 512
    assert len(simulator.c_source.weights) == 1024
    assert set(simulator.b_source.weights.values()) == set(simulator.c_source.weights.values()) == {1}
    assert len(simulator.gauge_table) == 16
    assert all(len(pair) == 2 and all(a != b for a, b in zip(*pair))
               for pair in simulator.gauge_table.values())
    # t=01000 and b=01010 give theta=1: the physical gauge-Z feedforward
    # must actually change the sign, and nonzero partial SWAPs are required.
    desired_vertices = "01000"
    gauge_word = next(word for word, pair in simulator.gauge_table.items() if desired_vertices in pair)
    gauge_index = tuple(simulator.gauge_table).index(gauge_word)
    observed = {}

    def inspect(stage, state):
        if stage in ("conditioned_input", "enriched", "before_vertex_feedforward",
                     "after_vertex_feedforward", "after_swap_correction"):
            observed[stage] = (len(state.weights), Counter(state.weights.values()), state.norm_squared())
        if stage == "after_swap_correction":
            marginal_norms = Counter()
            for key, weight in state.weights.items():
                marginal_norms[key[:20]] += weight * weight
                b_word, c_word = key[:20], key[20:]
                if b_word in simulator.b_source.weights:
                    assert c_word in simulator.c_source.weights
                    assert weight == (2 if c_word in simulator.b_source.weights else 1)
                else:
                    assert b_word in simulator.c_source.weights and c_word in simulator.b_source.weights
                    assert weight == 1
            assert len(marginal_norms) == 1024
            assert Counter(marginal_norms.values()) == {2560: 512, 512: 512}
            assert all(value == (2560 if word in simulator.b_source.weights else 512)
                       for word, value in marginal_norms.items())

    result = simulator.simulate_attempt(PrescribedOutcomes(gauge_index, (0, 1, 0, 1, 0)), observer=inspect)
    assert result.accepted and result.swap_plus and result.b_z == "0" * 20
    assert result.gauge_z == gauge_word and any(result.swap_offsets)
    assert result.vertex_probability_given_gauge == Fraction(3, 64)
    assert result.b_probability_given_vertex_gauge == Fraction(5, 3072)
    assert observed["conditioned_input"] == (1048576, {1: 1048576}, 1048576)
    assert observed["enriched"] == observed["conditioned_input"]
    assert observed["before_vertex_feedforward"][1] == {-2: 262144, -1: 524288}
    expected_corrected = (786432, {2: 262144, 1: 524288}, 1572864)
    assert observed["after_vertex_feedforward"] == expected_corrected
    assert observed["after_swap_correction"] == expected_corrected
    assert result.metrics.peak_state_entries == 1048576

    diagnostics = output_diagnostics(result.c_state)
    assert diagnostics == {"entries": 1024, "norm_squared": 2560,
                           "weight_counts": {2: 512, 1: 512}, "in_original_code_space": True,
                           "logical_X0": "4/5", "logical_Z0": "3/5",
                           "logical_Y0": "0", "logical_Z1": "1"}
    reference = SparseState(simulator.c_labels, {
        word: 2 if word in simulator.b_source.weights else 1
        for word in simulator.c_source.weights
    })
    actual_column = result.c_state.to_scipy_column()
    reference_column = reference.to_scipy_column()
    assert abs((reference_column.conjugate().T @ actual_column)[0, 0]) ** 2 == pytest.approx(1)

    record = write_result(result, tmp_path)
    saved = SparseState.from_payload(json.loads((tmp_path / record["c_state_reference"]).read_text()))
    assert saved.weights == reference.weights
    negative = ShotResult(1, accepted=True, c_state=result.c_state.global_sign(-1))
    second = write_result(negative, tmp_path)
    assert second["c_state_reference"] == record["c_state_reference"]
    assert len(list((tmp_path / "states").glob("*.json"))) == 1


def test_disconnected_or_inconsistent_geometry_is_rejected():
    with pytest.raises(ValueError):
        SparseC4HelixSimulator(CircuitSpecification(tree_edges=(1, 11, 3, 0)))
