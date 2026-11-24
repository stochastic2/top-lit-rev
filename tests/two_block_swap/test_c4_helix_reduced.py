"""Noiseless validation of physical repaired cats and the new adaptive circuit.

Deliberately prepared nonuniform cats / erroneous data below are fixed
quantum input fixtures. They exercise recovery paths; no stochastic noise
model, noise-rate sweep, or noisy-yield estimate is implemented here.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from random import Random

import numpy as np
import pytest

from c4_helix_noiseless import CHECK_SUPPORTS, LOGICAL_X0, LOGICAL_Z0
from c4_helix_reduced_decoders import (
    CURRENT_GRAPH, COMPACT_GRAPH, GRAPHS, KnownStateDecoder, ReducedRejection,
    StableRecord, cat_repair_pattern, decode_gauged, decode_gauge_word,
    decode_joint, mask, pauli_axes, pauli_coset, pauli_syndrome, two_block_tables,
)
from c4_helix_reduced_gadgets import (
    NoiselessRuntime, couple_and_read_cat, measure_repaired_cat, repair_cat,
)
from simulate_c4_helix_reduced import (
    ReducedRejectionSimulator, exact_magic_target, graph_family, gauged_family, save_result,
)
from sparse_wavefunction import SparseState


def report_from_error(error):
    s = pauli_syndrome(error)
    return tuple((s >> j) & 1 for j in range(18))


def test_production_joint_tables_equal_full_65536_pauli_enumeration_per_set():
    from check_reduced_rejection import build_tables
    reference, _ = build_tables()
    assert two_block_tables() == reference


def test_joint_recovery_uses_common_locations_and_rejects_real_logical_ambiguity():
    e1, e2 = (mask((2, 3)), 0), (mask((8, 11, 12, 15)), 0)
    assert pauli_syndrome(e1) == pauli_syndrome(e2)
    assert pauli_coset(e1) != pauli_coset(e2)
    with pytest.raises(ReducedRejection, match="unique") as caught:
        decode_joint(report_from_error(e1) + (0,) * 18)
    assert caught.value.code == "terminal_ambiguity"
    located_c = (mask((0, 4)), 0)
    decoded = decode_joint(report_from_error(e1) + report_from_error(located_c))
    assert decoded["compatible_blocks"] == [[0, 1]]
    assert decoded["B"] == pauli_axes((mask((0, 1)), 0), 20)
    assert decoded["C"] == pauli_axes(located_c, 20)
    assert decoded["candidate_logical_classes"] == 1


def test_whole_record_stopping_retains_nonzero_results_and_enforces_limit():
    history = StableRecord(2, "test")
    records = [(0, 0), (1, 0), (1, 1), (1, 1), (1, 1)]
    assert [history.add(r) for r in records] == [None, None, None, None, (1, 1)]
    with pytest.raises(ValueError, match="stopped"):
        history.add((1, 1))
    history = StableRecord(1, "test")
    with pytest.raises(ReducedRejection, match="round nine"):
        for i in range(9):
            history.add((i % 2,))
    with pytest.raises(ValueError, match="binary"):
        StableRecord(1, "test").add((0.5,))


@pytest.mark.parametrize("graph", (CURRENT_GRAPH, COMPACT_GRAPH), ids=lambda g: g.name)
def test_gauge_decoders_all_two_bit_masks_and_even_gauss_patterns(graph):
    graph.validate()
    for positions in [qs for w in range(3) for qs in combinations(range(len(graph.edges)), w)]:
        cycle = tuple(sum(q in positions for q in support) % 2 for support in graph.cycles)
        decoded = decode_gauged((0,) * 18 + cycle + (0,) * 5, graph)
        assert decoded["cycle_x_edges"] == positions
        assert decoded["certified"]
    for offsets in product((0, 1), repeat=4):
        offsets = (0,) + offsets
        for positions in [(), (0,), (0, len(graph.edges) - 1)]:
            cut = list(graph.cut(offsets))
            for q in positions:
                cut[q] ^= 1
            assert decode_gauge_word(cut, graph)["offsets"] == offsets
    for signs in product((0, 1), repeat=5):
        report = (0,) * (18 + len(graph.cycles)) + signs
        if sum(signs) % 2:
            with pytest.raises(ReducedRejection) as caught:
                decode_gauged(report, graph)
            assert caught.value.code == "negative_swap"
        else:
            result = decode_gauged(report, graph)
            z_edges = result["gauss_z_edges"]
            assert tuple(sum(q in z_edges for q, edge in enumerate(graph.edges) if v in edge) % 2
                         for v in range(5)) == signs
    # An odd Gauss product cannot certify the sector when paired data failed.
    result = decode_gauged((1,) + (0,) * (17 + len(graph.cycles)) + (1, 0, 0, 0, 0), graph)
    assert result["action"] == "regauge" and not result["gauss_z_edges"]


@pytest.mark.parametrize("graph", (CURRENT_GRAPH, COMPACT_GRAPH), ids=lambda g: g.name)
def test_known_graph_sign_corrections_solve_every_unit_syndrome(graph):
    labels = tuple(f"V_{name}" for name in "abcde") + tuple(f"A_{q}" for q in range(len(graph.edges)))
    decoder = KnownStateDecoder(labels, graph_family(graph))
    for j in range(len(labels)):
        signs = tuple(int(k == j) for k in range(len(labels)))
        axes = decoder.decode(signs)
        x = mask(q for q, p in enumerate(axes) if p in "XY")
        z = mask(q for q, p in enumerate(axes) if p in "ZY")
        assert tuple(((x & b).bit_count() + (z & a).bit_count()) % 2
                     for a, b in decoder.generators) == signs


def small_runtime(seed=0, trace=None):
    rt = NoiselessRuntime(Random(seed), trace)
    rt.reserve_data(("D_0", "D_1", "D_2", "D_3"))
    for j in range(4):
        rt.prepare(f"prepare/{j}", f"D_{j}")
    return rt


def test_nonuniform_cat_input_is_repaired_with_physical_x_gates_before_data():
    events = []
    rt = small_runtime(trace=events.append)
    leaves = tuple(f"L_{j}" for j in range(4))
    for j, leaf in enumerate(leaves):
        rt.prepare(f"fixture/cat/{j}", leaf)
    rt.gate("fixture/H", "H", leaves[0])
    for j in range(3):
        rt.gate(f"fixture/CX/{j}", "CX", leaves[j], leaves[j+1])
    for j in (1, 2, 3):
        rt.gate(f"fixture/pattern/{j}", "X", leaves[j])
    result = repair_cat(rt, "check", leaves)
    assert result["scan_records"] == [(1, 0, 0)] * 3
    assert result["x_pattern"] == (0, 1, 1, 1)
    correction_events = [e for e in events if "/cat/correction/" in e["location"]]
    assert [e["operation"] for e in correction_events] == ["X"] * 3
    ports = tuple(("Z", (f"D_{q}",)) for q in range(4))
    assert couple_and_read_cat(rt, "check", leaves, ports) == 0
    assert rt.live == {f"D_{q}" for q in range(4)}
    assert rt.state.to_sparse().canonical_payload() == SparseState.zeros(tuple(f"D_{q}" for q in range(4))).canonical_payload()
    assert cat_repair_pattern((1, 0, 0)) == (0, 1, 1, 1)


@pytest.mark.parametrize("seed", range(6))
def test_physical_repaired_swap_gadget_matches_independent_dense_projector(seed):
    rt = small_runtime(seed)
    rt.gate("data/H", "H", "D_1")
    before = rt.state.to_sparse().to_numpy()
    # Independent 16x16 SWAP(D0,D1) times Z(D2), in physical/MSB order.
    q = np.zeros((16, 16))
    for column in range(16):
        b = list(f"{column:04b}")
        sign = (-1) ** int(b[2])
        b[0], b[1] = b[1], b[0]
        q[int("".join(b), 2), column] = sign
    reported = measure_repaired_cat(rt, "check", (("SWAP", ("D_0", "D_1")), ("Z", ("D_2",))))
    expected = before + (-1)**reported * q @ before
    expected /= np.linalg.norm(expected)
    actual = rt.state.to_sparse().to_numpy()
    assert abs(np.vdot(actual, expected)) == pytest.approx(1)
    assert rt.check_gadgets_completed == 1 and rt.cat_scans == 3
    assert rt.live == {f"D_{q}" for q in range(4)}


def test_complete_small_known_state_preparation_retains_negative_syndromes():
    # A Bell-state preparation from zero, using its two complete checks.
    signs_seen = set()
    for seed in range(6):
        rt = small_runtime(seed)
        family = (("XX", (("X", ("D_0",)), ("X", ("D_1",)))),
                  ("ZZ", (("Z", ("D_0",)), ("Z", ("D_1",)))))
        history = StableRecord(2, "bell")
        for j in range(3):
            common = history.add(tuple(measure_repaired_cat(rt, f"bell/{j}/{name}", ports)
                                       for name, ports in family))
        signs_seen.add(common)
        axes = KnownStateDecoder(("D_0", "D_1"), family).decode(common)
        for j, axis in enumerate(axes):
            if axis != "I":
                rt.gate(f"correct/{j}", axis, f"D_{j}")
        state = rt.state.to_sparse()
        assert state.expectation_pauli(x_support=(0, 1)) == 1
        assert state.expectation_pauli(z_support=(0, 1)) == 1
    assert signs_seen == {(0, 0), (1, 0)}


def test_raw_zero_sources_are_actually_projected_and_corrected_without_selection():
    simulator = ReducedRejectionSimulator(magic_output="z", seed=2, source_mode="projected")
    simulator.prepare_inputs()
    assert any(any(source["stopping_record"]) for source in simulator.result["sources"].values())
    for copy, source in simulator.result["sources"].items():
        assert source["rounds_used"] == 3
        for axis in "XZ":
            for support in CHECK_SUPPORTS:
                assert simulator.runtime.state.expectation_pauli({f"{copy}_{q}": axis for q in support}) == 1
    # Full logical source checks, not just membership in the code space.
    for copy in "BC":
        from simulate_c4_helix_gadgets import source_family
        for _, ports in source_family(copy)[-2:]:
            assert simulator.runtime.state.expectation_pauli({targets[0]: axis for axis, targets in ports}) == 1


@pytest.fixture(scope="module")
def current_full_runs():
    results = []
    for seed in range(4):
        probabilities = []

        def inspect(stage, runtime):
            if stage.endswith("/terminal/recovered"):
                mean = runtime.state.expectation_pauli({f"B_{q}": "Z" for q in LOGICAL_Z0})
                probabilities.append((1 + mean) / 2)

        result = ReducedRejectionSimulator(magic_output="z", seed=seed, observer=inspect, extraction="verified_cat").run()
        result["test_pre_readout_B0_probabilities"] = [str(p) for p in probabilities]
        results.append(result)
    return results


def test_full_current_graph_runs_include_both_intrinsic_rejections_and_exact_output(current_full_runs):
    reasons = {r["rejection_code"] for r in current_full_runs}
    assert {None, "negative_swap", "logical_B_one"} <= reasons
    for result in current_full_runs:
        assert result["noise_model"] == "none"
        assert result["metrics"]["gauging_cycles_started"] == 1
        cycle = result["cycles"][0]
        assert cycle["gauged"]["rounds_used"] == 3
        assert result["metrics"]["gate_counts"]["FREDKIN"] == 80
        assert result["metrics"]["peak_live_qubits"] == 77
        if result["rejection_code"] == "negative_swap":
            assert cycle["vertex_reported_parity"] == 1
            assert cycle["vertex_word_probability"] == "1/64"
            assert cycle["gauge_z"] is None and result["b_z"] is None
            assert result["metrics"]["check_gadgets_completed"] == 312
        else:
            assert cycle["vertex_word_probability"] == "3/64"
            assert result["test_pre_readout_B0_probabilities"] == ["5/6"]
            assert result["metrics"]["check_gadgets_completed"] == 420
            assert result["metrics"]["cat_scans_completed"] == 1260
            assert cycle["terminal"]["rounds_used"] == 3
        if result["accepted"]:
            assert result["exact_magic_target_match"]
            assert result["c_state"].canonical_payload() == exact_magic_target().canonical_payload()
            d = result["physical_C_diagnostics"]
            assert d["in_original_code_space"]
            assert [d[k] for k in ("logical_X0", "logical_Y0", "logical_Z0", "logical_Z1")] == ["4/5", "0", "3/5", "1"]
        else:
            assert result["c_state"] is None


class AllZeroRandom:
    """One legal ideal trajectory; zero is selected whenever it has support."""
    def randrange(self, stop):
        return 0


def test_compact_graph_full_physical_schedule_and_exact_output():
    result = ReducedRejectionSimulator(magic_output="z", graph=COMPACT_GRAPH, rng=AllZeroRandom(), extraction="verified_cat").run()
    assert result["accepted"] and result["exact_magic_target_match"]
    assert result["metrics"]["check_gadgets_completed"] == 378
    assert result["metrics"]["gate_counts"]["FREDKIN"] == 80
    assert result["metrics"]["peak_live_qubits"] == 70
    assert len(result["cycles"][0]["gauge_z"]) == 13


def test_recover_and_regauge_executes_a_new_graph_without_resetting_data():
    class PreparedErrorFixture(ReducedRejectionSimulator):
        def enrich_and_frame(self, cycle):
            super().enrich_and_frame(cycle)
            if cycle["index"] == 0:
                # A fixed extra physical X gate prepares a recovery test input.
                # This is not an unrecorded fault or a stochastic noise model.
                self.runtime.gate("fixture/prepare_X_B0", "X", "B_0")

    result = PreparedErrorFixture(magic_output="z", rng=AllZeroRandom(), extraction="verified_cat").run()
    assert result["accepted"] and result["exact_magic_target_match"]
    assert len(result["cycles"]) == 2
    first, second = result["cycles"]
    assert first["next_action"] == "regauge"
    assert any(first["gauged"]["stopping_record"][:18])
    assert not first["gauged"]["decoding"]["certified"]
    assert first["terminal"]["decoding"]["candidate_logical_classes"] == 1
    assert second["next_action"] == "extract"
    assert second["gauged"]["decoding"]["certified"]
    assert result["metrics"]["check_gadgets_completed"] == 720
    assert result["metrics"]["gate_counts"]["FREDKIN"] == 160


def test_serial_trace_exposes_physical_idles_check_parities_and_adaptive_decisions():
    rt_events = []
    rt = small_runtime(trace=rt_events.append)
    measure_repaired_cat(rt, "check", (("Z", ("D_0",)), ("Z", ("D_1",))))
    physical = [e for e in rt_events if e.get("kind") == "physical"]
    assert [e["index"] for e in physical] == list(range(len(physical)))
    assert len({e["location"] for e in physical}) == len(physical)
    for event in physical:
        assert not set(event["targets"]) & set(event["idle_qubits"])
        assert not event["applied_fault_indices"]
        if event["operation"] == "MZ":
            assert event["actual"] == event["reported"]
            assert len(event["idle_qubits"]) == event["live_qubits"]
        else:
            assert len(event["idle_qubits"]) + len(event["targets"]) == event["live_qubits"]
    assert rt.idle_locations == sum(len(e["idle_qubits"]) for e in physical)
    assert rt.idle_locations == sum(rt.idle_locations_by_register.values())
    assert Counter(e["kind"] for e in rt_events if "kind" in e)["cat_scan"] == 3
    assert any(e.get("kind") == "cat_repair" for e in rt_events)
    assert rt_events[-1]["kind"] == "check"


def test_saved_output_roundtrip_and_deduplication(tmp_path, current_full_runs):
    original = next(r for r in current_full_runs if r["accepted"])
    first = save_result(dict(original), tmp_path, 0)
    second = save_result(dict(original), tmp_path, 1)
    assert first["c_state_reference"] == second["c_state_reference"]
    assert len(list((tmp_path / "states").glob("*.json"))) == 1
    import json
    loaded = SparseState.from_payload(json.loads((tmp_path / first["c_state_reference"]).read_text()))
    assert loaded.canonical_payload() == exact_magic_target().canonical_payload()


@pytest.fixture
def saved_noiseless_run(tmp_path, current_full_runs):
    import json
    graph = CURRENT_GRAPH
    policy = current_full_runs[0]["history_policy"]
    manifest = {"noise_model": "none", "procedure": "reduced_rejection", "noise_study_enabled": False,
                "history_policy": policy,
                "graph": {"name": graph.name, "edges": graph.edges, "cycles": graph.cycles,
                          "tree_edges": graph.tree_edges}, "source_preparation": "encoded",
                "seed": 0, "attempts_requested": len(current_full_runs), "ideal_success_probability": "5/8"}
    records = [save_result(dict(result), tmp_path, j) for j, result in enumerate(current_full_runs)]
    accepted = sum(r["accepted"] for r in records)
    counts = Counter()
    for r in records:
        counts.update(r["metrics"]["gate_counts"])
    summary = {"completed": True, "noise_model": "none", "graph": graph.name,
               "history_policy": policy,
               "attempts": len(records), "accepted": accepted, "rejected": len(records) - accepted,
               "accepted_states_exactly_validated": accepted, "ideal_success_probability": "5/8",
               "rejection_counts": dict(Counter(r["rejection_code"] for r in records if not r["accepted"])),
               "gate_counts": dict(counts),
               "observed_noiseless_acceptance_fraction": str(Fraction(accepted, len(records)))}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    (tmp_path / "shots.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    return tmp_path


def test_read_only_run_verifier_checks_reports_counts_and_actual_saved_amplitudes(saved_noiseless_run):
    from verify_c4_helix_reduced_run import verify_run
    result = verify_run(saved_noiseless_run)
    assert result["verified"] and result["attempts"] == 4
    assert result["accepted"] == 2 and result["distinct_C_states_checked"] == 1


def test_run_verifier_detects_a_corrupted_output_amplitude(saved_noiseless_run):
    import json
    from verify_c4_helix_reduced_run import verify_run
    path = next((saved_noiseless_run / "states").glob("*.json"))
    payload = json.loads(path.read_text())
    key = next(iter(payload["weights"]))
    payload["weights"][key] += 1
    payload["norm_squared"] = sum(w*w for w in payload["weights"].values())
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="amplitudes"):
        verify_run(saved_noiseless_run)


def test_run_verifier_detects_corrupted_acceptance_counts(saved_noiseless_run):
    import json
    from verify_c4_helix_reduced_run import verify_run
    path = saved_noiseless_run / "summary.json"
    summary = json.loads(path.read_text())
    summary["accepted"] += 1
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="Acceptance count"):
        verify_run(saved_noiseless_run)
