"""Physical and locality checks for lower-cost noiseless extraction.

Fixed nonuniform helper/input fixtures and finite Pauli propagation are
validation, not a realistic-noise model or noisy acceptance-rate study.
"""

from random import Random

import numpy as np
import pytest

from c4_helix_reduced_decoders import CURRENT_GRAPH, COMPACT_GRAPH
from c4_helix_reduced_gadgets import (
    NoiselessRuntime, measure_flagged_source, prepare_repaired_cat, repair_cat,
)
from check_optimized_extraction import source_program, verified_cat_program, audit
from simulate_c4_helix_reduced import ReducedRejectionSimulator, clean_resource_plan


class AllZeroRandom:
    def randrange(self, stop):
        return 0


class AllOneRandom:
    def randrange(self, stop):
        return stop - 1


@pytest.mark.parametrize("m,k", ((1, 4), (3, 2), (4, 2)))
@pytest.mark.parametrize("axis", "XZ")
def test_real_flag_circuit_matches_certified_program_and_ideal_projector(m, k, axis):
    for seed in (0, 1, 2):
        events = []
        rt = NoiselessRuntime(Random(seed), events.append)
        labels = tuple(f"B_{4*j+i}" for j in range(m) for i in range(k))
        rt.reserve_data(labels)
        for j, label in enumerate(labels):
            rt.prepare(f"fixture/prepare/{j}", label)
        rt.gate("fixture/H", "H", labels[0])
        before = rt.state.to_sparse().to_numpy()
        ports = tuple((axis, (label,)) for label in labels)
        report = measure_flagged_source(rt, "check", ports)
        n = len(labels)
        if axis == "X":
            transformed = before[np.arange(2**n) ^ (2**n - 1)]
        else:
            transformed = before * np.array([(-1)**v.bit_count() for v in range(2**n)])
        expected = before + (-1)**report * transformed
        expected /= np.linalg.norm(expected)
        assert abs(np.vdot(rt.state.to_sparse().to_numpy(), expected)) == pytest.approx(1)
        coordinate = {label: j for j, label in enumerate(labels)}
        coordinate.update({f"L_{j}": n+j for j in range(m)})
        physical = [e for e in events if e.get("kind") == "physical" and e["location"].startswith("check/")]
        executed = [(e["operation"], tuple(coordinate[q] for q in e["targets"])) for e in physical]
        assert executed == source_program(m, k, axis)
        assert sum(e["operation"] in ("CX", "CZ") for e in physical) == 2*(m-1) + n
        assert rt.flag_bits_measured == m - 1
        flags = next(e["flags"] for e in events if e.get("kind") == "source_flag_record")
        assert not any(flags)
        assert rt.live == set(labels)


@pytest.mark.parametrize("m", (2, 4, 9, 16))
def test_two_zero_scan_program_is_executed_exactly_as_certified(m):
    events = []
    rt = NoiselessRuntime(Random(0), events.append)
    leaves = prepare_repaired_cat(rt, "cat", m, zero_scans=2)
    coordinate = {q: j for j, q in enumerate(leaves)} | {"w": m}
    executed = [(e["operation"], tuple(coordinate[q] for q in e["targets"])) for e in events
                if e.get("kind") == "physical"]
    assert executed == verified_cat_program(m)
    assert rt.cat_scans == 2
    assert rt.live == set(leaves)


def test_nonzero_cat_still_uses_full_repair_history():
    rt = NoiselessRuntime(Random(0))
    leaves = tuple(f"L_{j}" for j in range(4))
    for j, label in enumerate(leaves):
        rt.prepare(f"fixture/prep/{j}", label)
    rt.gate("fixture/H", "H", leaves[0])
    for j in range(3):
        rt.gate(f"fixture/CX/{j}", "CX", leaves[j], leaves[j+1])
    for j in (1, 2, 3):
        rt.gate(f"fixture/bit/{j}", "X", leaves[j])
    result = repair_cat(rt, "cat", leaves, zero_scans=2)
    assert result["scan_records"] == [(1, 0, 0)]*3
    assert result["stopping_rule"] == "three_equal_records"
    assert result["x_pattern"] == (0, 1, 1, 1)


def test_all_locality_certificates_include_gates_meters_preparation_and_idles():
    result = audit()
    assert len(result["source_shapes"]) == 6
    assert len(result["two_initial_zero_scans"]) == 15
    assert all(c["zero_flag_two_fault_block_bound"] == 2 for c in result["source_shapes"])
    assert all(c["accepted_two_fault_leaf_bound"] == 2 for c in result["two_initial_zero_scans"])


@pytest.fixture(scope="module", params=(CURRENT_GRAPH, COMPACT_GRAPH), ids=lambda g: g.name)
def matched_runs(request):
    graph = request.param
    results = {}
    for profile in ("verified_cat", "optimized"):
        results[profile] = ReducedRejectionSimulator(magic_output="z", graph=graph, extraction=profile, rng=AllZeroRandom()).run()
    return graph, results


def test_matched_complete_trajectories_preserve_state_and_reduce_executed_cost(matched_runs):
    graph, runs = matched_runs
    baseline, optimized = runs["verified_cat"], runs["optimized"]
    for profile, result in runs.items():
        assert result["accepted"] and result["exact_magic_target_match"]
        plan = clean_resource_plan(graph, profile, magic_output="z")
        metrics = result["metrics"]
        assert metrics["gate_counts"].get("SWAP", 0) == 0
        assert sum(metrics["gate_counts"].get(g, 0) for g in ("CX", "CZ")) == plan["two_qubit_gates_before_ungauging_swaps"]
        assert metrics["peak_live_qubits"] == plan["peak_live_qubits"]
        assert metrics["cat_scans_completed"] == plan["cat_scans"]
        assert metrics["flag_bits_measured"] == plan["flag_bits"]
        assert metrics["gate_counts"]["FREDKIN"] == 80
    assert optimized["c_state"].canonical_payload() == baseline["c_state"].canonical_payload()
    old = sum(baseline["metrics"]["gate_counts"].get(g, 0) for g in ("CX", "CZ"))
    new = sum(optimized["metrics"]["gate_counts"].get(g, 0) for g in ("CX", "CZ"))
    assert new < old/2
    assert (old, new) == ((17565, 8040) if graph == CURRENT_GRAPH else (16357, 7120))


def test_optimized_negative_swap_is_still_certified_by_repeated_gauss_measurements():
    result = ReducedRejectionSimulator(magic_output="z", rng=AllOneRandom()).run()
    assert not result["accepted"] and result["rejection_code"] == "negative_swap"
    cycle = result["cycles"][0]
    assert cycle["vertex_reported_parity"] == 1
    assert cycle["gauged"]["records"] == [cycle["gauged"]["stopping_record"]]*3
    assert cycle["gauged"]["stopping_record"][-5:] == (1, 0, 0, 0, 0)
    assert cycle["gauge_z"] is None and result["c_state"] is None


def test_source_flag_rebuilds_only_the_unused_known_source():
    class PreparedCatFixture(NoiselessRuntime):
        changed = False

        def gate(self, location, operation, *targets):
            super().gate(location, operation, *targets)
            if location == "source/B/round/0/X/5/flag_cat/fanout/1" and not self.changed:
                self.changed = True
                super().gate("fixture/prepare_nonuniform_cat", "X", "L_1")

    simulator = ReducedRejectionSimulator(magic_output="z", rng=AllZeroRandom())
    simulator.runtime = PreparedCatFixture(AllZeroRandom())
    result = simulator.run()
    assert result["accepted"] and result["exact_magic_target_match"]
    assert [a["outcome"] for a in result["sources"]["B"]["attempts"]] == ["flag_retry", "prepared"]
    assert len(result["sources"]["C"]["attempts"]) == 1
    assert len(result["cycles"]) == 1


def test_optimized_recovery_regauging_keeps_its_original_quantum_output():
    class PreparedDataFixture(ReducedRejectionSimulator):
        def enrich_and_frame(self, cycle):
            super().enrich_and_frame(cycle)
            if cycle["index"] == 0:
                self.runtime.gate("fixture/prepare_X_B0", "X", "B_0")

    result = PreparedDataFixture(rng=AllZeroRandom()).run()
    assert result["accepted"] and result["exact_magic_target_match"]
    assert len(result["cycles"]) == 2
    assert result["cycles"][0]["next_action"] == "regauge"
    assert result["cycles"][1]["next_action"] == "extract"
    assert result["metrics"]["gate_counts"]["FREDKIN"] == 160
