"""Dense/sparse cross-checks, physical gadget faults, and decoder tests."""

from fractions import Fraction
from random import Random

import numpy as np
import pytest

from c4_helix_fault_runtime import PauliFault, PhysicalRuntime, RejectAttempt, measure_verified_cat
from c4_helix_gadget_decoders import decode_b_readout, decode_gauge, recovery_from_history, syndrome
from c4_helix_noiseless import EDGES
from sparse_gadget_state import FactorStore, SparseProductState
from sparse_wavefunction import SparseState
from simulate_c4_helix_gadgets import GadgetSimulator
from simulate_c4_helix_sparse import output_diagnostics


def little_runtime(faults=(), trace=None):
    rt = PhysicalRuntime(Random(2), faults, trace)
    for copy in "BC":
        rt.reserve_data((copy + "_0", copy + "_1"))
        for q in range(2):
            rt.prepare(f"prepare/{copy}/{q}", f"{copy}_{q}")
    return rt


def test_factor_gates_and_coherent_norm_against_flat_sparse_state():
    rt = little_runtime()
    rt.prepare("prepare/V", "V_0")
    flat = SparseState.zeros(("B_0", "B_1", "C_0", "C_1", "V_0"))
    gates = [("H", ("B_0",)), ("CX", ("B_0", "B_1")),
             ("H", ("C_0",)), ("H", ("V_0",)),
             ("CX", ("V_0", "B_0")), ("CZ", ("V_0", "C_1")),
             ("FREDKIN", ("V_0", "B_0", "C_0")), ("SWAP", ("B_1", "C_1"))]
    for i, (operation, targets) in enumerate(gates):
        rt.gate(str(i), operation, *targets)
        if operation == "CZ":
            q, t = (flat.labels.index(label) for label in targets)
            flat = SparseState(flat.labels, {key: value * (-1) ** (int(key[q]) * int(key[t]))
                                            for key, value in flat.weights.items()})
        else:
            method = {"H": "hadamard", "CX": "cnot", "SWAP": "swap", "FREDKIN": "fredkin"}[operation]
            flat = getattr(flat, method)(*targets)
        expanded = rt.state.to_sparse()
        np.testing.assert_allclose(expanded.to_numpy(), flat.to_numpy())
        assert rt.state.norm_squared() == expanded.norm_squared()
    # H before Z measurement is retained as a separate physical operation.
    rt.gate("read/H", "H", "V_0")
    before = rt.state.to_sparse()
    n0, n1 = before.z_measurement_norms("V_0")
    bit = rt.measure_z("read/measure", "V_0")
    expected, p = before.project_z("V_0", bit)
    assert p == Fraction((n0, n1)[bit], n0 + n1)
    assert rt.state.to_sparse().canonical_payload() == expected.canonical_payload()


def test_pauli_y_phase_and_fault_participant_validation():
    rt = little_runtime()
    rt.gate("Y", "Y", "B_0")
    assert rt.state.global_i_power == 1
    assert rt.state.to_sparse().weights == {"1000": 1}
    rt.gate("Y2", "Y", "B_0")
    assert rt.state.global_i_power == 2
    assert rt.state.to_sparse().weights == {"0000": -1}
    # (-1)*i^2=+1, so the two physical Y gates return exactly the input.
    bad = little_runtime((PauliFault("bad", {"C_0": "X"}),))
    with pytest.raises(ValueError, match="participants"):
        bad.gate("bad", "H", "B_0")


def test_verified_cat_positive_preserves_entangled_data_and_uses_raw_parity():
    events = []
    rt = little_runtime(trace=events.append)
    rt.gate("data/H", "H", "B_0")
    rt.gate("data/CX", "CX", "B_0", "B_1")
    initial = rt.state.to_sparse().canonical_payload()
    bit = measure_verified_cat(rt, "bell/check", (("X", ("B_0",)), ("X", ("B_1",))))
    assert bit == 0 and rt.state.to_sparse().canonical_payload() == initial
    assert len([event for event in events if event.get("operation") == "MZ" and "/verify/" in event["location"]]) == 3
    assert events[-1]["reported_parity"] == 0
    assert not any(label.startswith("L_") or label == "w" for label in rt.live)


@pytest.mark.parametrize("fault", [
    PauliFault("check/cat/chain/0", {"L_1": "X"}),
    PauliFault("check/verify/0/0/measure", when="report", flip_report=True),
])
def test_cat_verification_detects_bit_or_report_fault(fault):
    rt = little_runtime((fault,))
    with pytest.raises(RejectAttempt, match="Cat verification"):
        measure_verified_cat(rt, "check", (("Z", ("B_0",)), ("Z", ("B_1",))))
    assert rt.applied == {0}


def test_minus_cat_passes_zz_but_flips_the_measured_check_parity():
    events = []
    fault = PauliFault("check/cat/H", {"L_0": "Z"})
    rt = little_runtime((fault,), events.append)
    with pytest.raises(RejectAttempt, match="positive check"):
        measure_verified_cat(rt, "check", (("Z", ("B_0",)), ("Z", ("B_1",))))
    assert all(event["reported"] == 0 for event in events if "/verify/" in event["location"] and event.get("operation") == "MZ")
    assert events[-1]["reported_parity"] == 1


def test_controlled_swap_cat_is_a_real_projection_not_a_classical_mixture():
    rt = little_runtime()
    rt.gate("C/H", "H", "C_0")
    before = rt.state.to_sparse()
    swapped = before.swap("B_0", "C_0")
    expected_weights = dict(before.weights)
    for key, value in swapped.weights.items():
        expected_weights[key] = expected_weights.get(key, 0) + value
    expected = SparseState(before.labels, expected_weights)
    reported = measure_verified_cat(rt, "swap", (("SWAP", ("B_0", "C_0")),), require_positive=False)
    if reported == 0:
        assert rt.state.to_sparse().canonical_payload() == expected.canonical_payload()
    else:
        difference = dict(before.weights)
        for key, value in swapped.weights.items():
            difference[key] = difference.get(key, 0) - value
        difference = {key: value for key, value in difference.items() if value}
        assert rt.state.to_sparse().canonical_payload() == SparseState(before.labels, difference).canonical_payload()


def test_decoders_handle_gauge_reports_recovery_history_and_b_readout():
    offset = (0, 1, 0, 1, 0)
    cut = [(offset[u] + offset[v]) % 2 for u, v in EDGES]
    cut[7] = 1 - cut[7]
    cut[0] = 1 - cut[0]
    assert decode_gauge(cut)["offsets"] == offset
    pauli = "Y" + "I" * 19
    record = (0,) * 18 + syndrome(pauli)
    assert recovery_from_history([record, record]) is None
    decoded = recovery_from_history([record] * 3)
    assert syndrome(decoded["C"]) == syndrome(pauli)
    assert decoded["B"] == "I" * 20
    reports = [0] * 20
    reports[0] = reports[6] = 1
    decoded = decode_b_readout(reports)
    assert decoded["keep"] and decoded["logical_bit"] == 0
    assert decoded["corrected_bits"] == (0,) * 20


def assert_magic_output(result):
    assert result["accepted"]
    diagnostics = output_diagnostics(result["c_state"])
    assert diagnostics["in_original_code_space"]
    assert [diagnostics[name] for name in ("logical_X0", "logical_Y0", "logical_Z0", "logical_Z1")] == ["4/5", "0", "3/5", "1"]


@pytest.mark.parametrize("axis", ("X", "Y", "Z"))
def test_full_physical_schedule_and_late_pauli_recovery(axis):
    fault = PauliFault("filter/round/2/C/Z/8/readout/7/measure", {"C_0": axis}, when="idle")
    probes = {"C_ZZZZ": {f"C_{q}": "Z" for q in range(4)},
              "C_XXXX": {f"C_{q}": "X" for q in range(4)}}
    result = GadgetSimulator(seed=1, faults=(fault,), probes=probes).run()
    assert_magic_output(result)
    assert result["applied_fault_indices"] == [0] and not result["unreached_fault_indices"]
    assert result["metrics"]["check_gadgets_completed"] == 528
    assert result["metrics"]["gate_counts"]["FREDKIN"] == 80
    assert result["metrics"]["peak_live_qubits"] == 77
    assert result["recovery_decoding"]["rounds_used"] == 3
    assert result["recovery_decoding"]["C"] == axis + "I" * 19
    stages = {row["stage"]: row["expectations"] for row in result["probe_history"]}
    assert stages["filtered"]["C_ZZZZ"] == ("-1" if axis in "XY" else "1")
    assert stages["filtered"]["C_XXXX"] == ("-1" if axis in "YZ" else "1")
    assert stages["recovered"] == {"C_ZZZZ": "1", "C_XXXX": "1"}
    if axis == "Y":
        assert result["metrics"]["gate_counts"]["Y"] == 1  # One recovery location, not X then Z.


def test_false_vertex_report_is_rejected_by_a_real_gauss_gadget():
    # Seed zero has actual odd vertex parity. Flipping its root report
    # passes the classical parity test but cannot change the quantum U sign.
    fault = PauliFault("vertex/0/measure", when="report", flip_report=True)
    failed_checks = []

    def trace(event):
        if event.get("kind") == "check" and event["reported_parity"]:
            failed_checks.append(event["location"])

    result = GadgetSimulator(seed=0, faults=(fault,), trace=trace).run()
    assert not result["accepted"] and result["c_state"] is None
    assert sum(result["vertex_x"]) % 2 == 0
    assert failed_checks == ["gauged/round/0/gauss/a"]
    assert result["applied_fault_indices"] == [0]


def test_two_wrong_gauge_reports_are_decoded_before_swap_feedforward():
    faults = tuple(PauliFault(f"gauge/readout/{q}", when="report", flip_report=True) for q in (0, 7))
    actual = {}

    def trace(event):
        if event.get("operation") == "MZ" and event["location"].startswith("gauge/readout/"):
            actual[int(event["location"].split("/")[-1])] = event["actual"]

    result = GadgetSimulator(seed=1, faults=faults, trace=trace).run()
    assert_magic_output(result)
    assert result["gauge_decoding"]["corrected_bits"] == tuple(actual[q] for q in range(20))
    assert sum(a != b for a, b in zip(result["gauge_z"], result["gauge_decoding"]["corrected_bits"])) == 2
    assert result["applied_fault_indices"] == [0, 1]


class AllZeroRandom:
    """Replay one legal (very rare) all-zero measurement trajectory for testing."""
    def randrange(self, stop):
        return 0


def test_literal_raw_zero_sources_and_complete_projected_schedule():
    encoded = GadgetSimulator(rng=AllZeroRandom())
    encoded.prepare_inputs()
    reference_probability = encoded.runtime.measurement_probability
    reference_factors = {factor.labels: factor.weights for factor in (
        encoded.runtime.state.store.factors[fid] for _, ids in encoded.runtime.state.terms for fid in ids)}
    source_probability = []

    def inspect(stage, runtime):
        if stage == "verified_inputs":
            source_probability.append(runtime.measurement_probability)
            for _, ids in runtime.state.terms:
                for fid in ids:
                    factor = runtime.state.store.factors[fid]
                    assert factor.weights == reference_factors[factor.labels]

    result = GadgetSimulator(source_mode="projected", rng=AllZeroRandom(), observer=inspect).run()
    assert source_probability[0] / reference_probability == Fraction(1, 2 ** 19)
    assert_magic_output(result)
    assert result["metrics"]["check_gadgets_completed"] == 528


def test_readout_fault_does_not_change_the_actual_postmeasurement_state():
    events = []
    fault = PauliFault("read", when="report", flip_report=True)
    rt = little_runtime((fault,), events.append)
    assert rt.measure_z("read", "B_0") == 1
    assert events[-1]["actual"] == 0 and events[-1]["reported"] == 1
    assert rt.state.to_sparse().weights == {"000": 1}


def test_decoder_rejections_and_recovery_round_limit():
    record_zero = (0,) * 36
    record_error = (0,) * 18 + syndrome("X" + "I" * 19)
    with pytest.raises(RejectAttempt, match="round nine"):
        recovery_from_history([record_zero if i % 2 else record_error for i in range(9)])
    with pytest.raises(RejectAttempt, match="distance-two"):
        decode_gauge((1, 1, 1) + (0,) * 17)
    reports = [int(q in (0, 4, 8)) for q in range(20)]
    with pytest.raises(RejectAttempt, match="correction"):
        decode_b_readout(reports)
