"""Y extraction, complex interference, output frames, and reported-bit recovery."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import json
from random import Random

import numpy as np
import pytest

from c4_helix_depolarizing import DepolarizingModel
from c4_helix_logical_diagnostics import decoded_c_diagnostics
from c4_helix_fault_runtime import PauliFault
from c4_helix_magic_y import (
    Y0_X_MASK, Y0_Z_MASK, logical_y_ports, raw_y_amplitudes, output_frame,
    exact_raw_y_target, corrected_y_bit,
)
from c4_helix_noiseless import LOGICAL_X0, LOGICAL_Z0
from c4_helix_reduced_decoders import CURRENT_GRAPH, mask, remainder
from c4_helix_reduced_gadgets import NoiselessRuntime, measure_grouped_protected_cat
from gaussian_integer import gaussian, phase, abs_squared
from simulate_c4_helix_depolarizing import DepolarizingSimulator, summarize
from simulate_c4_helix_reduced import ReducedRejectionSimulator, clean_resource_plan, save_result
from sparse_wavefunction import SparseState, GaussianSparseState
from verify_c4_helix_depolarizing_run import verify_run


ZERO = DepolarizingModel(two_qubit_infidelity=0)
HADAMARD = np.array([[1, 1], [1, -1]])/np.sqrt(2)
SDG = np.diag([1, -1j])


@pytest.mark.parametrize("bit", (0, 1))
def test_dense_logical_derivation_keeps_both_outcomes_at_total_probability_three_quarters(bit):
    initial = np.array([1, 1, 0, 0], dtype=complex)/np.sqrt(2)
    swap = np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
    positive = (np.eye(4)+swap)@initial/2
    assert np.vdot(positive, positive).real == pytest.approx(3/4)
    positive /= np.linalg.norm(positive)
    eigenvector = np.array([1, (1 if bit == 0 else -1)*1j])/np.sqrt(2)
    branch = np.kron(eigenvector.conj().reshape(1,2), np.eye(2))@positive
    assert np.vdot(branch, branch).real == pytest.approx(1/2)
    branch /= np.linalg.norm(branch)
    frame = HADAMARD@SDG if bit == 0 else HADAMARD@SDG@HADAMARD
    recorded = np.eye(2, dtype=complex)
    for gate in output_frame(bit)["apply_order"]:
        recorded = {"H":HADAMARD, "SDG":SDG}[gate]@recorded
    np.testing.assert_allclose(recorded, frame, atol=1e-12)
    target = np.array([1-1j, 1])/np.sqrt(3)
    assert abs(np.vdot(target, frame@branch)) == pytest.approx(1)
    assert output_frame(bit)["physical_correction_gates"] == 0


def test_nine_body_word_is_minus_logical_y_and_has_the_expected_code_action():
    x0, z0 = mask(LOGICAL_X0), mask(LOGICAL_Z0)
    assert remainder(Y0_X_MASK ^ x0) == 0 and remainder(Y0_Z_MASK ^ z0) == 0
    assert (Y0_X_MASK & Y0_Z_MASK).bit_count() == 3
    assert len(logical_y_ports()) == 9
    state = exact_raw_y_target(0)
    assert state.expectation_pauli(LOGICAL_X0, LOGICAL_Z0) == Fraction(1, 3)
    assert state.expectation_pauli([q for q in range(20) if Y0_X_MASK >> q & 1],
                                  [q for q in range(20) if Y0_Z_MASK >> q & 1]) == Fraction(-1, 3)


def test_gaussian_canonicalization_removes_large_common_complex_scales_exactly():
    original = GaussianSparseState(("q",), {"0": gaussian(2, -1), "1": 1})
    for scale in (gaussian(3, 2), gaussian(0, 1), gaussian(1, -1), gaussian(2**180+7, -(2**190+3))):
        state = GaussianSparseState(original.labels, {k: scale*v for k, v in original.weights.items()})
        assert state.canonical_payload() == original.canonical_payload()
        assert state.norm_squared() == abs_squared(scale)*6
    loaded = SparseState.from_payload(json.loads(json.dumps(original.canonical_payload())))
    assert loaded.canonical_payload() == original.canonical_payload()
    assert GaussianSparseState(("q",), {"0":gaussian(0,1), "1":gaussian(0,2)}).canonical_payload() == \
        SparseState(("q",), {"0":1, "1":2}).canonical_payload()
    for outcome in (0, 1):
        conditional, p = original.project_x("q", outcome)
        vector = original.to_numpy()
        branch = np.array([1, (-1)**outcome])@vector/np.sqrt(2)
        assert float(p) == pytest.approx(abs(branch)**2)
        assert conditional.norm_squared() > 0


def test_complex_product_coefficients_preserve_interference_and_pauli_expectations():
    rt = NoiselessRuntime(Random(0))
    rt.prepare("prep", "a")
    rt.gate("H", "H", "a")
    rt.gate("S", "S", "a")
    assert rt.state.expectation_pauli({"a": "Y"}) == 1
    rt.gate("H2", "H", "a")
    actual = rt.state.to_sparse().to_numpy()
    expected = HADAMARD@np.diag([1, 1j])@np.array([1, 1])/np.sqrt(2)
    assert abs(np.vdot(expected, actual)) == pytest.approx(1)
    assert rt.state.inner_product(rt.state) == rt.state.norm_squared()


@pytest.mark.parametrize("x,z,expected", ((1,0,"1"), (0,1,"1"), (1,1,"1"),
    (mask(LOGICAL_X0),0,"4/9"), (mask(LOGICAL_X0),mask(LOGICAL_Z0),"1/9")))
def test_complex_ideal_decoder_distinguishes_correctable_and_logical_errors(x, z, expected):
    target = exact_raw_y_target(0)
    amplitudes = {}
    for word, weight in target.weights.items():
        w = int(word[::-1], 2)
        amplitudes[f"{w ^ x:020b}"[::-1]] = (-1)**((w & z).bit_count() % 2)*weight
    state = GaussianSparseState(target.labels, amplitudes)
    diagnostic = decoded_c_diagnostics(state, magic_output="y", y_outcome=0)
    assert diagnostic["decoded_target_fidelity"] == expected


@pytest.mark.parametrize("seed", (0, 1))
def test_physical_controlled_y_decomposition_matches_dense_projector(seed):
    rt = NoiselessRuntime(Random(seed))
    rt.reserve_data(("B_0",))
    rt.prepare("prep", "B_0")
    bit = measure_grouped_protected_cat(rt, "Y", (("Y", ("B_0",)),))
    y = np.array([[0, -1j], [1j, 0]])
    expected = (np.eye(2)+(-1)**bit*y)@np.array([1, 0])/np.sqrt(2)
    assert abs(np.vdot(expected, rt.state.to_sparse().to_numpy())) == pytest.approx(1)
    assert {op:rt.gate_counts[op] for op in ("CX", "CZ", "S")} == {"CX":1,"CZ":1,"S":1}


@pytest.fixture(scope="module", params=(0, 2))
def y_result(request):
    result = DepolarizingSimulator(seed=request.param, model=ZERO, history_policy="adaptive",
                                  terminal_extraction="compact_flagged").run()
    assert result["magic_output"] == "y" and result["accepted"]
    return result


def test_complete_y_outputs_have_exact_raw_states_and_corrected_frames(y_result):
    r = y_result
    bit = r["b_y"]["logical_bit"]
    assert bit == (0 if r["seed"] == 0 else 1)
    assert r["output_clifford_frame"] == output_frame(bit)
    assert r["c_state"].canonical_payload() == exact_raw_y_target(bit).canonical_payload()
    assert r["exact_magic_target_match"] and r["decoded_C_diagnostics"]["decoded_target_fidelity"] == "1"
    assert r["b_decoding"]["keep"] and r["b_decoding"]["z_reports_used_only_for_discard"]
    t = r["cycles"][-1]["terminal"]
    assert len(t["stopping_record"]) == 37 and t["rounds_used"] == 3
    assert bit == corrected_y_bit(t["stopping_record"][-1], t["decoding"]["B"])
    p = clean_resource_plan(CURRENT_GRAPH, "optimized", terminal_extraction="compact_flagged")
    old = clean_resource_plan(CURRENT_GRAPH, "optimized", terminal_extraction="compact_flagged", magic_output="z")
    assert p["two_qubit_gates_before_ungauging_swaps"] - old["two_qubit_gates_before_ungauging_swaps"] == 156
    assert r["metrics"]["gate_counts"]["S"] == 9 and r["metrics"]["gate_counts"]["FREDKIN"] == 80


def test_saved_complex_output_verifies_and_rejects_a_wrong_clifford_frame(tmp_path, y_result):
    r = y_result
    record = save_result(r, tmp_path, 0)
    record = deepcopy(record)
    record.update(execution_status="completed", diagnostic_status="completed")
    manifest = {"noise_model":ZERO.manifest(), "attempts_requested":1, "seed":r["seed"],
                "noise_seed_base":None, "graph":{"name":"current20"}, "extraction":"optimized",
                "history_policy":"adaptive", "terminal_extraction":"compact_flagged",
                "terminal_flag_policy":"repair_then_protected", "magic_output":"y"}
    summary = dict(summarize([record]), completed=True, noise_model=ZERO.manifest(),
                   history_policy="adaptive", terminal_extraction="compact_flagged",
                   terminal_flag_policy="repair_then_protected", magic_output="y")
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    (tmp_path/"summary.json").write_text(json.dumps(summary))
    (tmp_path/"shots.jsonl").write_text(json.dumps(record)+"\n")
    assert verify_run(tmp_path)["verified"]
    record["output_clifford_frame"]["apply_order"] = ["H"]
    (tmp_path/"shots.jsonl").write_text(json.dumps(record)+"\n")
    with pytest.raises(ValueError, match="frame"):
        verify_run(tmp_path)


@pytest.mark.parametrize("axis", "XYZ")
def test_joint_syndrome_corrects_b_errors_before_interpreting_y(axis):
    class PreparedError(ReducedRejectionSimulator):
        def recover_original(self, cycle):
            self.runtime.gate("fixture/B_error", axis, "B_0")
            super().recover_original(cycle)
    result = PreparedError(seed=2, history_policy="adaptive", terminal_extraction="compact_flagged").run()
    assert result["accepted"] and result["exact_magic_target_match"]


def test_z_meter_reports_when_discarding_b_cannot_reject_a_y_output():
    sim = ReducedRejectionSimulator(seed=2, history_policy="adaptive", terminal_extraction="compact_flagged")
    sim.runtime.faults = tuple(PauliFault(f"B/readout/{q}", when="report", flip_report=True) for q in range(20))
    result = sim.run()
    assert result["accepted"] and result["exact_magic_target_match"]
    assert sim.runtime.applied == set(range(20))


def test_y_is_deferred_until_a_positive_cycle_so_regauging_preserves_its_input():
    class ZeroRandom:
        def randrange(self, stop):
            return 0
    class PreparedError(ReducedRejectionSimulator):
        def enrich_and_frame(self, cycle):
            super().enrich_and_frame(cycle)
            if cycle["index"] == 0:
                self.runtime.gate("fixture/error", "X", "B_0")
    result = PreparedError(rng=ZeroRandom(), history_policy="adaptive", terminal_extraction="compact_flagged").run()
    assert result["accepted"] and result["exact_magic_target_match"]
    assert len(result["cycles"]) == 2
    first, last = result["cycles"]
    assert first["next_action"] == "regauge" and not first["terminal"]["includes_logical_y"]
    assert len(first["terminal"]["stopping_record"]) == 36
    assert last["terminal"]["includes_logical_y"] and len(last["terminal"]["stopping_record"]) == 37
