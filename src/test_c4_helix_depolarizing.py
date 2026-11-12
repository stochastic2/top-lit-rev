"""Channel, sparse trajectory, and read-only logical-decoder validation."""

from fractions import Fraction
from itertools import product
import json
from random import Random

import numpy as np
import pytest

from c4_helix_depolarizing import (
    DepolarizingModel, DepolarizingRuntime, coin, nonidentity_pauli, nonidentity_probability,
)
from c4_helix_logical_diagnostics import (
    X0, X1, Z0, decoded_c_diagnostics, solve_component, stabilizer_coordinates,
    small_corrections,
)
from simulate_c4_helix_depolarizing import DepolarizingSimulator, isolated_attempt, summarize
from simulate_c4_helix_reduced import ReducedRejectionSimulator, exact_magic_target, save_result
from sparse_wavefunction import SparseState
from verify_c4_helix_depolarizing_run import verify_run


ZERO = DepolarizingModel(two_qubit_infidelity=0)
PAULI = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
         "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}


class Selection:
    def __init__(self, index):
        self.index = index

    def randrange(self, stop):
        assert 0 <= self.index < stop
        return self.index


def matrix(axes):
    result = np.ones((1, 1))
    for p in axes:
        result = np.kron(result, PAULI[p])
    return result


def pauli_state(state, x=0, z=0):
    weights = {}
    for word, value in state.weights.items():
        w = int(word[::-1], 2)
        value *= (-1)**((w & z).bit_count() % 2)
        weights[f"{w ^ x:020b}"[::-1]] = value
    return SparseState(state.labels, weights)


def test_infidelity_calibration_and_rate_validation():
    assert nonidentity_probability("1e-4", 2) == Fraction(1, 8000)
    assert nonidentity_probability("1e-4", 1) == Fraction(3, 20000)
    assert nonidentity_probability("1e-4", 3) == Fraction(9, 80000)
    for bad in ("nan", "inf", "-1", "1.1", True):
        with pytest.raises(ValueError):
            DepolarizingModel(two_qubit_infidelity=bad)
    with pytest.raises(ValueError, match="maximum"):
        DepolarizingModel(two_qubit_infidelity="0.81")
    rng = Random(1)
    before = rng.getstate()
    assert not coin(rng, Fraction(0)) and coin(rng, Fraction(1))
    assert rng.getstate() == before


@pytest.mark.parametrize("n", (1, 2, 3))
def test_uniform_pauli_ensemble_is_the_calibrated_depolarizing_channel(n):
    axes = [nonidentity_pauli(Selection(j), n) for j in range(4**n - 1)]
    assert len(set(axes)) == 4**n - 1
    assert set(axes) == set(product("IXYZ", repeat=n)) - {("I",)*n}
    rng = np.random.default_rng(7)
    v = rng.normal(size=2**n) + 1j*rng.normal(size=2**n)
    v /= np.linalg.norm(v)
    rho = np.outer(v, v.conj())
    r = Fraction(1, 10)
    p = nonidentity_probability(r, n)
    output = float(1-p)*rho
    for word in axes:
        op = matrix(word)
        output += float(p / len(axes)) * (op @ rho @ op.conj().T)
    d = 2**n
    lam = float(p * Fraction(d*d, d*d-1))
    np.testing.assert_allclose(output, (1-lam)*rho + lam*np.eye(d)/d, atol=1e-12)
    assert Fraction(d*(1-p)+1, d+1) == 1-r


@pytest.mark.parametrize("choice", range(15))
def test_all_two_qubit_noise_updates_match_dense_post_gate_action(choice):
    events = []
    model = DepolarizingModel(two_qubit_infidelity=Fraction(4, 5))  # p=1
    rt = DepolarizingRuntime(Random(0), Selection(choice), model, events.append)
    labels = ("q_0", "q_1")
    rt.reserve_data(labels)
    for q in labels:
        rt.prepare("prep/" + q, q)
    rt.gate("H", "H", labels[0])
    before = rt.state.to_sparse().to_numpy()
    cx = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    rt.gate("CX", "CX", *labels)
    axes = nonidentity_pauli(Selection(choice), 2)
    expected = matrix(axes) @ cx @ before
    actual = rt.state.to_sparse().to_numpy()
    assert abs(np.vdot(expected, actual)) == pytest.approx(1)
    assert len(rt.noise_events) == 1
    assert rt.events == 4 and rt.gate_counts["CX"] == 1
    assert rt.noise_events[0]["timing"] == "after"
    assert rt.state.global_i_power == axes.count("Y") % 4
    physical = [e for e in events if e.get("kind") == "physical"]
    assert physical[-1]["noise_event_indices"] == [0]


def test_preparation_readout_and_idle_timing_do_not_relabel_quantum_rejection():
    # Preparation flip precedes the actual quantum meter; report flip is later.
    events = []
    model = DepolarizingModel(two_qubit_infidelity=0, preparation_flip_probability=1,
                              readout_flip_probability=1)
    rt = DepolarizingRuntime(Random(0), Random(1), model, events.append)
    rt.prepare("prep", "q_0")
    assert rt.measure_z("read", "q_0") == 0
    event = [e for e in events if e.get("operation") == "MZ" and e.get("kind") == "physical"][-1]
    assert event["actual"] == 1 and event["reported"] == 0
    assert rt.live == set() and rt.state.to_sparse().weights == {"": 1}
    # Zero-rate preparation, then turn on idle depolarization for one interval.
    rt = DepolarizingRuntime(Random(0), Selection(0), ZERO)
    rt.prepare("prep0", "q_0")
    rt.prepare("prep1", "q_1")
    rt.model = DepolarizingModel(two_qubit_infidelity=0, idle_infidelity=Fraction(2, 3))
    rt.gate("H1", "H", "q_1")
    assert rt.noise_events[0]["channel"] == "idle_depolarizing"
    assert rt.noise_events[0]["targets"] == ["q_0"]
    assert rt.noise_events[0]["timing"] == "idle"
    assert all(word[0] == "1" for word in rt.state.to_sparse().weights)


def test_atomic_fredkin_can_receive_a_three_qubit_pauli_without_a_fault_cap():
    rt = DepolarizingRuntime(Random(0), Selection(0),
                            DepolarizingModel(two_qubit_infidelity=0, three_qubit_infidelity=Fraction(8, 9)))
    rt.reserve_data(("B_0", "C_0"))
    for q in ("B_0", "C_0", "V_a"):
        rt.prepare("prep/" + q, q)
    for j in range(4):
        rt.gate(f"F/{j}", "FREDKIN", "V_a", "B_0", "C_0")
    assert len(rt.noise_events) == 4
    assert all(e["channel"] == "gate_3q_depolarizing" for e in rt.noise_events)
    assert rt.gate_counts["FREDKIN"] == 4


@pytest.mark.parametrize("x,z,expected", ((0, 0, "1"), (1, 0, "1"), (0, 1, "1"), (1, 1, "1"),
                                        (1 | (1 << 7), (1 << 7), "1"),
                                        (X0, 0, "16/25"), (0, Z0, "9/25"), (X1, 0, "0")))
def test_read_only_logical_decoder_distinguishes_physical_from_logical_errors(x, z, expected):
    state = pauli_state(exact_magic_target(), x, z)
    before = state.canonical_payload()
    d = decoded_c_diagnostics(state)
    assert d["decoded_target_fidelity"] == expected
    assert d["syndrome_probability_sum"] == "1"
    assert state.canonical_payload() == before


def test_walsh_logical_decoder_matches_direct_overlap_on_all_syndromes_of_a_random_sector():
    rng = Random(71)
    h = stabilizer_coordinates()
    zsyn = 7
    base = solve_component(zsyn)
    logical = (0, X0, X1, X0 ^ X1)
    amplitudes = {base ^ w ^ l: rng.randrange(-3, 4) for w in h for l in logical}
    amplitudes = {w: a for w, a in amplitudes.items() if a}
    state = SparseState(tuple(f"C_{q}" for q in range(20)),
                        {f"{w:020b}"[::-1]: a for w, a in amplitudes.items()})
    result = decoded_c_diagnostics(state)
    # Independent direct <target|R_s|state> calculation, with no Walsh transform.
    target = {w: 2 for w in h} | {w ^ X0: 1 for w in h}
    total = 0
    for xsyn in range(512):
        s = xsyn | (zsyn << 9)
        x, z = small_corrections().get(s, (base, solve_component(xsyn)))
        overlap = sum(t * (-1)**(((w ^ x) & z).bit_count() % 2) * amplitudes.get(w ^ x, 0)
                      for w, t in target.items())
        total += overlap*overlap
    assert Fraction(result["decoded_target_fidelity"]) == Fraction(total, 2560*state.norm_squared())
    assert result["active_syndrome_sectors"] == 512


def test_zero_noise_runner_reproduces_the_existing_physical_circuit_exactly(tmp_path):
    reference = ReducedRejectionSimulator(magic_output="z", seed=2).run()
    noisy = DepolarizingSimulator(magic_output="z", seed=2, noise_seed=900, model=ZERO).run()
    assert noisy["accepted"] == reference["accepted"]
    assert noisy["c_state"].canonical_payload() == reference["c_state"].canonical_payload()
    assert noisy["cycles"] == reference["cycles"] and noisy["sources"] == reference["sources"]
    assert noisy["metrics"]["gate_counts"] == reference["metrics"]["gate_counts"]
    assert noisy["noise"]["sampled_events"] == 0
    assert noisy["decoded_C_diagnostics"]["decoded_target_fidelity"] == "1"
    manifest = {"noise_model": ZERO.manifest(), "attempts_requested": 1, "seed": 2,
                "noise_seed_base": 900, "graph": {"name": "current20"}, "extraction": "optimized",
                "history_policy": noisy["history_policy"]}
    record = save_result(noisy, tmp_path, 0)
    record.update(execution_status="completed", diagnostic_status="completed")
    summary = dict(summarize([record]), completed=True, noise_model=ZERO.manifest(),
                   history_policy=noisy["history_policy"])
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "shots.jsonl").write_text(json.dumps(record) + "\n")
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    assert verify_run(tmp_path)["verified"]
    record["noise"]["channel_opportunities"]["gate_2q"] += 1
    (tmp_path / "shots.jsonl").write_text(json.dumps(record) + "\n")
    with pytest.raises(ValueError, match="opportunities"):
        verify_run(tmp_path)
    record["noise"]["channel_opportunities"]["gate_2q"] -= 1
    record["decoded_C_diagnostics"]["decoded_target_fidelity"] = "0"
    (tmp_path / "shots.jsonl").write_text(json.dumps(record) + "\n")
    with pytest.raises(ValueError, match="diagnostic mismatch"):
        verify_run(tmp_path)


def test_computational_timeouts_are_not_counted_as_rejection(tmp_path):
    request = {"directory": str(tmp_path), "attempt_dir": str(tmp_path), "shot_index": 0,
               "seed": 0, "noise_seed": 0, "model_rates": ZERO.manifest()["rates"],
               "graph": "current20", "source_mode": "encoded", "extraction": "optimized",
               "max_terms": 4096, "trace": False}
    record = isolated_attempt(request, 0.001)
    assert record["execution_status"] == "resource_failure" and record["failure_kind"] == "timeout"
    assert record["accepted"] is None and record["rejection_code"] is None
    summary = summarize([record])
    assert summary["rejected"] == 0 and summary["unresolved_attempts"] == 1
    assert summary["rejection_fraction_bounds_over_all_requested"] == ["0", "1"]


def test_summary_keeps_unresolved_attempts_and_unavailable_diagnostics_explicit():
    def complete(accepted, fidelity="1", diagnostic=True):
        r = {"shot_index": 0, "execution_status": "completed", "accepted": accepted,
             "rejection_code": None if accepted else "negative_swap",
             "noise": {"sampled_events": 3, "event_counts_by_channel": {}, "pauli_factor_counts": {}},
             "metrics": {"process_peak_rss_bytes": 1, "peak_coherent_terms": 2, "fallback_overlaps": 0},
             "diagnostic_status": "completed" if diagnostic else "timeout"}
        if accepted and diagnostic:
            r["decoded_C_diagnostics"] = {"decoded_target_fidelity": fidelity}
        return r
    unresolved = {"execution_status": "resource_failure", "failure_kind": "timeout"}
    result = summarize([complete(False), complete(False), complete(True), unresolved])
    assert result["observed_rejection_fraction_among_completed"] == "2/3"
    assert result["rejection_fraction_bounds_over_all_requested"] == ["1/2", "3/4"]
    assert result["completed_subset_may_be_selection_biased"]
    result = summarize([complete(True), complete(True, diagnostic=False)])
    assert result["accepted_diagnostics_completed"] == 1 and result["accepted_diagnostics_unavailable"] == 1
    assert result["decoded_fidelity_bounds_among_known_accepted"] == ["1/2", "1"]
