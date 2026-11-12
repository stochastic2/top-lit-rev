"""Compact terminal projectors, audited programs, late hooks, and full outputs."""

from random import Random

import numpy as np
import pytest

from c4_helix_compact_terminal import (
    compact_terminal_program, compact_terminal_cost, measure_compact_terminal,
    TerminalFlagRecovery, flag_repair_pattern,
)
from c4_helix_reduced_decoders import ReducedRejection
from c4_helix_reduced_gadgets import NoiselessRuntime
from check_compact_terminal import audit
from check_optimized_extraction import signatures, source_program, propagate
from simulate_c4_helix_reduced import ReducedRejectionSimulator, clean_resource_plan
from c4_helix_reduced_decoders import CURRENT_GRAPH, COMPACT_GRAPH
from simulate_c4_helix_depolarizing import DepolarizingSimulator
from c4_helix_depolarizing import DepolarizingModel
from c4_helix_fault_runtime import PauliFault


class AllZeroRandom:
    def randrange(self, stop):
        return 0


@pytest.mark.parametrize("weight", (4, 8))
@pytest.mark.parametrize("axis", "XZ")
def test_actual_compact_program_matches_independent_dense_projector(weight, axis):
    for seed in (0, 1, 2):
        events = []
        rt = NoiselessRuntime(Random(seed), events.append)
        labels = tuple(f"B_{j}" for j in range(4)) if weight == 4 else tuple(
            f"B_{4*j+i}" for j in range(4) for i in range(2))
        rt.reserve_data(labels)
        for q in labels:
            rt.prepare("input/"+q, q)
        rt.gate("input/H0", "H", labels[0])
        rt.gate("input/X1", "X", labels[1])
        before = rt.state.to_sparse().to_numpy()
        ports = tuple((axis, (q,)) for q in labels)
        report = measure_compact_terminal(rt, "check", ports)
        transformed = (before[np.arange(2**weight) ^ (2**weight-1)] if axis == "X" else
                       before*np.array([(-1)**v.bit_count() for v in range(2**weight)]))
        expected = before+(-1)**report*transformed
        expected /= np.linalg.norm(expected)
        assert abs(np.vdot(expected, rt.state.to_sparse().to_numpy())) == pytest.approx(1)
        coordinate = {q: j for j, q in enumerate(labels)}
        coordinate.update({f"L_{j}": weight+j for j in range(2 if weight == 4 else 4)})
        coordinate["w"] = 12
        physical = [e for e in events if e.get("kind") == "physical" and e["location"].startswith("check/")]
        executed = [(e["operation"], tuple(coordinate[q] for q in e["targets"])) for e in physical]
        assert executed == compact_terminal_program(weight, axis)
        assert rt.live == set(labels)
        assert rt.flagged_terminal_checks == 1
        assert rt.terminal_flag_bits_measured == (1 if weight == 4 else 5)
        assert not any(next(e["flags"] for e in events if e.get("kind") == "terminal_flag_record"))


def test_local_audit_has_physical_rather_than_block_weight_bounds():
    result = audit()
    assert result["verified"] and len(result["shapes"]) == 4
    assert sum(c["zero_flag_pairs_checked"] for c in result["shapes"]) == 2496
    assert all(c["accepted_single_fault_physical_weight_bound"] == 1 and
               c["accepted_two_fault_physical_weight_bound"] == 2 for c in result["shapes"])


def test_bare_source_footprint_fails_the_required_terminal_physical_bound():
    # This counterexample is why merely switching to the 304-gate source
    # footprint would not preserve the terminal proof.
    cases, _ = signatures(source_program(1, 4, "Z"), range(4), 15, 0)
    assert any(min((x | z).bit_count(), (x | (z ^ 15)).bit_count()) > 1 for x, z, _ in cases)


def test_upper_source_without_guards_can_hide_a_four_target_two_fault_hook():
    ops = source_program(4, 2, "X")
    a = propagate(1 << 8, 0, ops, 7)    # after second fanout CX
    b = propagate(1 << 8, 0, ops, 17)   # after first reverse-fanout CX
    x, z, reports = a[0]^b[0], a[1]^b[1], a[2]^b[2]
    assert reports & 7 == 0
    assert min(((x & 255) | (z & 255)).bit_count(), (((x ^ 255) & 255) | (z & 255)).bit_count()) == 4


@pytest.mark.parametrize("weight", (4, 8))
def test_report_flag_requests_protected_recovery_without_resetting_unknown_data(weight):
    class FixedReportError(NoiselessRuntime):
        def measure_z(self, location, label):
            value = super().measure_z(location, label)
            # Fixed first flag report; quantum measurement still happens.
            if label == ("L_1" if weight == 4 else "w") and not getattr(self, "flipped", False):
                self.flipped = True
                return value ^ 1
            return value
    rt = FixedReportError(Random(2))
    labels = tuple(f"B_{j}" for j in range(4)) if weight == 4 else tuple(
        f"B_{4*j+i}" for j in range(4) for i in range(2))
    for q in labels:
        rt.prepare("input/"+q, q)
    with pytest.raises(TerminalFlagRecovery) as error:
        measure_compact_terminal(rt, "check", tuple(("X", (q,)) for q in labels))
    assert error.value.details["action"] == "protected_fallback"
    assert rt.live == set(labels)
    assert rt.gate_counts["PREP"] == len(labels)+(2 if weight == 4 else 6)


def test_flag_repair_table_includes_false_reports_and_hidden_two_faults():
    result = audit()
    assert [r["reachable_flag_words"] for r in result["flag_repairs"]] == [2, 2, 31, 31]
    assert sum(r["all_single_and_two_fault_pairs_checked"] for r in result["flag_repairs"]) == 9188
    assert flag_repair_pattern(8, (1, 0, 1, 1, 0)) == (2, 3, 4, 5)
    with pytest.raises(ReducedRejection) as error:
        flag_repair_pattern(8, (1, 1, 0, 0, 1))
    assert error.value.code == "terminal_flag_unsupported"


@pytest.mark.parametrize("axis", "XZ")
def test_physical_word_13_repair_removes_a_four_target_hook(axis):
    rt = NoiselessRuntime(Random(2))
    labels = tuple(f"B_{4*j+i}" for j in range(4) for i in range(2))
    rt.reserve_data(labels)
    for q in labels:
        rt.prepare("input/"+q, q)
    rt.gate("input/H", "H", labels[0])
    before = rt.state.to_sparse().to_numpy()
    rt.faults = (PauliFault("check/compact/6/CX", {"L_0": "X"}),)
    with pytest.raises(TerminalFlagRecovery) as error:
        measure_compact_terminal(rt, "check", tuple((axis, (q,)) for q in labels))
    d = error.value.details
    assert d["flags"] == (1, 0, 1, 1, 0)
    assert d["repair_targets"] == list(labels[2:6])
    transformed = (before[np.arange(256) ^ 255] if axis == "X" else
                   before*np.array([(-1)**v.bit_count() for v in range(256)]))
    expected = before+(-1)**d["reported_syndrome"]*transformed
    expected /= np.linalg.norm(expected)
    assert abs(np.vdot(expected, rt.state.to_sparse().to_numpy())) == pytest.approx(1)
    assert rt.applied == {0} and rt.live == set(labels)


def test_full_protected_fallback_keeps_data_and_recovers_a_false_flag():
    events = []
    sim = ReducedRejectionSimulator(magic_output="z", rng=AllZeroRandom(), history_policy="adaptive",
                                    terminal_extraction="compact_flagged", trace=events.append)
    sim.runtime.faults = (PauliFault("cycle/0/terminal/round/0/B/X/0/compact/9/MZ",
                                     when="report", flip_report=True),)
    result = sim.run()
    assert result["accepted"] and result["exact_magic_target_match"]
    t = result["cycles"][0]["terminal"]
    assert t["extraction_used"] == "protected_fallback" and t["rounds_used"] == 3
    assert t["compact_history"]["records"] == []
    assert t["flag_recovery"]["repair_targets"] == []
    assert sim.runtime.applied == {0}
    assert result["metrics"]["flagged_terminal_checks"] == 1
    import json
    from c4_helix_history_validation import verify_terminal_flags, verify_report_histories
    record = json.loads(json.dumps({k: v for k, v in result.items() if k != "c_state"}))
    verify_terminal_flags(record, "compact_flagged")
    verify_report_histories(record, CURRENT_GRAPH, "adaptive")
    record["terminal_flag_records"][0]["repair_targets"] = ["B_0"]
    with pytest.raises(ValueError, match="repair"):
        verify_terminal_flags(record, "compact_flagged")
    for event in events:
        if event.get("kind") == "physical" and event["operation"] == "PREP" and any(
                q.startswith(("B_", "C_")) for q in event["targets"]):
            assert event["location"].startswith("source/")


@pytest.mark.parametrize("graph", (CURRENT_GRAPH, COMPACT_GRAPH), ids=lambda g: g.name)
def test_full_noiseless_output_and_gate_savings(graph):
    result = ReducedRejectionSimulator(magic_output="z", seed=2, rng=AllZeroRandom(), graph=graph, history_policy="adaptive",
                                      terminal_extraction="compact_flagged").run()
    assert result["accepted"] and result["exact_magic_target_match"]
    plan = clean_resource_plan(graph, "optimized", terminal_extraction="compact_flagged", magic_output="z")
    m = result["metrics"]
    assert m["gate_counts"]["CX"]+m["gate_counts"]["CZ"] == plan["two_qubit_gates_before_ungauging_swaps"]
    assert m["flagged_terminal_checks"] == 108 and m["terminal_flag_bits_measured"] == 300
    assert m["cat_scans_completed"] == plan["cat_scans"]
    assert plan["flag_bits"] == 168 and plan["terminal_flag_bits"] == 300
    assert plan["two_qubit_gates_before_ungauging_swaps"] == (6060 if graph == CURRENT_GRAPH else 5140)
    assert m["gate_counts"]["FREDKIN"] == 80


def test_zero_noise_uses_the_same_compact_program_and_controller():
    model = DepolarizingModel(two_qubit_infidelity=0)
    ideal = ReducedRejectionSimulator(magic_output="z", seed=2, terminal_extraction="compact_flagged").run()
    noisy = DepolarizingSimulator(magic_output="z", seed=2, model=model, terminal_extraction="compact_flagged").run()
    assert ideal["accepted"] and noisy["accepted"]
    assert ideal["c_state"].canonical_payload() == noisy["c_state"].canonical_payload()
    assert ideal["metrics"]["gate_counts"] == noisy["metrics"]["gate_counts"]
    assert noisy["decoded_C_diagnostics"]["decoded_target_fidelity"] == "1"
    assert noisy["noise"]["sampled_events"] == 0
