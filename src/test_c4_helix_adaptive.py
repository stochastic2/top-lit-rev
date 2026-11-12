"""Exhaustive reference-lemma checks and physical acquisition regression tests."""

from copy import deepcopy
from itertools import combinations, product
import json
from random import Random

import pytest

from c4_helix_history_validation import verify_history
from c4_helix_reduced_decoders import AdaptiveRecord, clean_reference_certificate, record_history
from c4_helix_reduced_gadgets import NoiselessRuntime, repair_cat
from simulate_c4_helix_reduced import ReducedRejectionSimulator


def partitions(n, prefix=()):
    if not n:
        yield prefix
    else:
        for value in range(max(prefix, default=-1)+2):
            yield from partitions(n-1, prefix+(value,))


def test_every_five_round_equality_pattern_has_a_nonvacuous_clean_reference():
    patterns = list(partitions(5))
    assert len(patterns) == 52
    for pattern in patterns:
        h = AdaptiveRecord(3, "audit")
        for value in pattern:
            result = h.add(tuple((value >> j) & 1 for j in range(3)))
            if result is not None:
                break
        assert h.common is not None and 3 <= len(h.records) <= 5
        occurrences = {i for i, report in enumerate(h.records) if report == h.common}
        # Independent brute-force check of every actual bad-round placement.
        compatible = []
        for bad_bits in product((0, 1), repeat=len(h.records)):
            if sum(bad_bits) > 2:
                continue
            if any(h.records[i] != h.records[i+1] and not (bad_bits[i] or bad_bits[i+1])
                   for i in range(len(h.records)-1)):
                continue
            compatible.append(bad_bits)
            assert any(not bad_bits[i] for i in occurrences)
        assert compatible  # The certificate must not use an impossible premise.
        assert h.certificate["min_faulty_rounds_if_all_occurrences_bad"] >= 3
        for prefix_length in range(1, len(h.records)):
            assert clean_reference_certificate(h.records[:prefix_length]) is None


@pytest.mark.parametrize("n", (1, 2, 3, 4, 5))
def test_certificate_is_sound_for_every_prefix_and_bad_round_pattern(n):
    for pattern in partitions(n):
        records = [(v,) for v in pattern]
        certificate = clean_reference_certificate(records)
        if certificate is None:
            continue
        selected = records[certificate["selected_record_index"]]
        for w in range(3):
            for bad in combinations(range(n), w):
                if all(records[i] == records[i+1] or i in bad or i+1 in bad for i in range(n-1)):
                    assert any(r == selected and i not in bad for i, r in enumerate(records))


def test_concrete_five_round_example_and_certificate_corruption():
    h = AdaptiveRecord(2, "example")
    records = ((1, 0), (0, 0), (0, 0), (0, 1), (0, 1))
    assert [h.add(r) for r in records] == [None, None, None, None, (0, 1)]
    section = json.loads(json.dumps({"history_policy": "adaptive", "records": h.records,
                                    "rounds_used": 5, "stopping_record": h.common,
                                    "reference_certificate": h.certificate}))
    assert verify_history(section, 2, "example", "adaptive") == (0, 1)
    broken = deepcopy(section)
    broken["reference_certificate"]["selected_occurrences"] = [0]
    with pytest.raises(ValueError, match="certificate mismatch"):
        verify_history(broken, 2, "example", "adaptive")
    with pytest.raises(ValueError, match="stopped"):
        h.add((0, 1))
    with pytest.raises(ValueError, match="binary"):
        AdaptiveRecord(1, "bad").add((2,))
    with pytest.raises(ValueError, match="policy"):
        record_history(1, "bad", "majority")


def test_actual_physical_acquisition_corrects_the_selected_nonzero_reference():
    class FixtureRuntime(NoiselessRuntime):
        def gate(self, location, operation, *targets):
            if location == "fixture/round/3/left/cat/H":
                super().gate("fixture/input_flip", "X", "C_0")
            return super().gate(location, operation, *targets)

        def measure_z(self, location, label):
            result = super().measure_z(location, label)
            # One fixed corrupted report, not a clean-outcome oracle.
            return result ^ (location == "fixture/round/0/left/readout/0/measure")

    sim = ReducedRejectionSimulator(magic_output="z", history_policy="adaptive")
    sim.runtime = FixtureRuntime(Random(2), history_policy="adaptive")
    for q in ("B_0", "C_0"):
        sim.runtime.prepare("prepare/"+q, q)
    family = (("left", (("Z", ("B_0",)),)), ("right", (("Z", ("C_0",)),)))
    saved = {}
    common = sim.acquire_record("fixture", family, saved)
    assert saved["records"] == [(1, 0), (0, 0), (0, 0), (0, 1), (0, 1)]
    assert common == (0, 1) and saved["rounds_used"] == 5
    sim.apply_axes("correction", ("B_0", "C_0"), tuple("X" if b else "I" for b in common))
    assert sim.runtime.state.to_sparse().weights == {"00": 1}


def test_cat_zero_shortcut_and_nonzero_repair_remain_physical():
    for policy in ("adaptive", "triple"):
        rt = NoiselessRuntime(Random(1), history_policy=policy)
        for q in ("L_0", "L_1", "L_2"):
            rt.prepare("prepare/"+q, q)
        rt.gate("input/X", "X", "L_1")
        result = repair_cat(rt, "cat", ("L_0", "L_1", "L_2"), zero_scans=2)
        assert result["scans_used"] == 3 and result["stopping_record"] == (1, 1)
        assert rt.state.to_sparse().weights == {"000": 1}
        assert rt.gate_counts["X"] == 2


def test_cat_uses_five_scan_certificate_after_fixed_report_and_leaf_errors():
    class FixtureRuntime(NoiselessRuntime):
        def gate(self, location, operation, *targets):
            if location == "cat/verify/3/0/left":
                super().gate("fixture/leaf_flip", "X", "L_2")
            return super().gate(location, operation, *targets)

        def measure_z(self, location, label):
            return super().measure_z(location, label) ^ (location == "cat/verify/0/0/measure")

    rt = FixtureRuntime(Random(1), history_policy="adaptive")
    leaves = ("L_0", "L_1", "L_2")
    for leaf in leaves:
        rt.prepare("prepare/"+leaf, leaf)
    result = repair_cat(rt, "cat", leaves, zero_scans=2)
    assert result["scan_records"] == [(1, 0), (0, 0), (0, 0), (0, 1), (0, 1)]
    assert result["scans_used"] == 5 and result["x_pattern"] == (0, 0, 1)
    assert rt.state.to_sparse().weights == {"000": 1}
    assert rt.gate_counts["X"] == 2
    clean = NoiselessRuntime(Random(1), history_policy="adaptive")
    for leaf in leaves:
        clean.prepare("prepare/"+leaf, leaf)
    shortcut = repair_cat(clean, "cat", leaves, zero_scans=2)
    assert shortcut["scans_used"] == 2 and shortcut["stopping_rule"] == "two_initial_zero_scans"


def test_adaptive_and_triple_execute_identical_noiseless_circuits():
    a = ReducedRejectionSimulator(magic_output="z", seed=2, history_policy="adaptive").run()
    b = ReducedRejectionSimulator(magic_output="z", seed=2, history_policy="triple").run()
    assert a["accepted"] and b["accepted"]
    assert a["c_state"].canonical_payload() == b["c_state"].canonical_payload()
    assert a["metrics"]["gate_counts"] == b["metrics"]["gate_counts"]
    for copy in "BC":
        assert a["sources"][copy]["records"] == b["sources"][copy]["records"]
