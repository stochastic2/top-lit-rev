"""Reproduce the old witnesses and audit the sitewise dressed outer meters."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src/single_block_cz"), str(Path(__file__).resolve().parent)]

import check_single_cz_hybrid_faults as prior
import single_cz_direct_outer_ports as direct
import single_cz_hybrid_faults as fault
import single_cz_hybrid_study as hybrid
from single_cz_recovery import COMPACT13

ROUTE = "direct_outer_ports"


def ideal_instrument(support, program):
    data_sites = tuple(support)
    edge_sites = tuple(COMPACT13.tree[v - 1] for v, _ in hybrid.blocks(support) if v)
    labels = [f"D{q}" for q in data_sites] + [f"A{e}" for e in edge_sites] + ["s"]
    core = hybrid.monomial_core(program)
    complement = ((1 << 20) - 1) ^ sum(1 << q for q in data_sites)
    flags = {sites[0]: 0 for op, sites in program if op == "PREP" and sites[0] != "s"}
    assert program[:2] == [("PREP", ("s",)), ("H", ("s",))]
    assert program[-2:] == [("H", ("s",)), ("MZ", ("s",))]
    for flag in flags:
        uses = [(op, sites) for op, sites in program if flag in sites]
        assert uses == [("PREP", (flag,)), ("CX", ("s", flag)),
                        ("CX", ("s", flag)), ("MZ", (flag,))]
    for word in range(1 << len(labels)):
        inputs = {label: (word >> j) & 1 for j, label in enumerate(labels)}
        data = sum(inputs[f"D{q}"] << q for q in data_sites)
        edges = sum(inputs[f"A{e}"] << e for e in edge_sites)
        control = inputs["s"]
        outputs, phase = hybrid.run_core(core, inputs | flags)
        for filling in (0, complement):
            expected, signed_phase = hybrid.full_physical_oracle(support, data | filling, edges, control)
            assert phase == signed_phase
            assert all(outputs[f"D{q}"] == ((expected >> q) & 1) for q in data_sites)
        assert all(outputs[label] == inputs[label] for label in labels[len(data_sites):])
        assert all(outputs[label] == 0 for label in flags)
    return {"basis_cases": 2 << len(labels), "flag_readout": "0" * len(flags),
            "phase_mod_8_includes_s_zero_and_one": True}


def resource_counts(program):
    live = {}
    lifetimes = {}
    waiting = Counter()
    peak = 0
    for step, (op, sites) in enumerate(program):
        waiting.update(set(live).difference(sites))
        if op == "PREP":
            live[sites[0]] = step
            peak = max(peak, len(live))
        elif op == "MZ":
            lifetimes[sites[0]] = step - live.pop(sites[0]) + 1
    assert not live
    return hybrid.counts(program) | {"serialized_steps": len(program), "peak_helpers": peak,
                                     "helper_lifetimes_steps": lifetimes, "helper_idle_locations": sum(waiting.values())}


def direct_route(support, graph, route):
    assert route == ROUTE
    return direct.dressed_x_program(support, graph), 4


def zero_flag_one_fault_cones(support, events, labels, flags, graph):
    """Validate the prior outer-meter contribution to the outside envelope."""
    target_mask = (1 << 20) - 1
    measured_x = fault.m.mask(support)
    terms = 0
    for event in events:
        error = event["error"]
        flag, _, _ = fault.class_image(error, event["report"], labels, flags, graph)[0]
        if flag:
            continue
        data_x = error.x & target_mask
        edge_x = (error.x >> 20) & ((1 << len(graph.edges)) - 1)
        assert edge_x.bit_count() <= 1
        if not edge_x:
            cones = [15 << (4 * v) for v in range(5)]
        elif (edge := edge_x.bit_length() - 1) in graph.tree:
            cones = [15 << (4 * (graph.tree.index(edge) + 1))]
        else:
            cones = [0]
        base, generators = error.fourier_support(range(flags[0]))
        for z in fault.image_words(base, generators):
            data_z = z & target_mask
            assert any(((x | data_z) & ~cone) == 0 for x in (data_x, data_x ^ measured_x) for cone in cones)
            terms += 1
    return {"coherent_pauli_terms_checked": terms,
            "data_supported_in_typed_block_or_empty_modulo_measured_X": True,
            "graph_X_is_zero_or_single_edge": True}


def schedule_resources(supports, graph):
    m = fault.m
    compact = fault.compact_pauli_program
    bare_z = [gate for support in m.SUPPORTS for gate in compact("Z", len(support))]
    bare_inner = compact("X", 4) * 5
    exact_inner = [gate for support in m.SUPPORTS[:5] for gate in direct.dressed_x_program(support, graph)]
    outer = [gate for support in supports for gate in direct.dressed_x_program(support, graph)]
    reference = hybrid.reference_record_counts()
    old = hybrid.record_counts(optimized=True, outer_supports=supports)
    positive = hybrid.counts(bare_z + bare_inner + outer)
    unconditional = hybrid.counts(bare_z + exact_inner + outer)
    gauss = hybrid.counts([gate for v in range(1, 5) for gate in hybrid.bare_nonroot_gauss_program(graph, v)])
    assert (reference["CX"], reference["T_TDG"], old["CX"], old["T_TDG"]) == (220, 64, 248, 84)
    cycles_cx = sum(map(len, graph.cycles))
    assert cycles_cx == 25

    def factory(record):
        return {"CX": 1889 + 3 * (record["CX"] - reference["CX"] + gauss["CX"] - 20),
                "T_TDG": 256 + 3 * (record["T_TDG"] - reference["T_TDG"] + gauss["T_TDG"])}

    diagnostic_set = unconditional.copy()
    for op in ("CX", "T", "TDG", "T_TDG", "H", "PREP", "MZ"):
        diagnostic_set[op] = unconditional.get(op, 0) + gauss.get(op, 0)
    diagnostic_set["CX"] += cycles_cx
    for op in ("PREP", "MZ"):
        diagnostic_set[op] += len(graph.cycles)
    conflicts = len(m.SUPPORTS)
    support_weight = sum(map(len, m.SUPPORTS))
    ccz = hybrid.counts(hybrid.ccz("s", "t", "w"))
    completion = {"persistent_registers": conflicts,
                  "root_added_ports": conflicts,
                  "endpoint_factors_CX": 2 * support_weight + conflicts * ccz["CX"],
                  "endpoint_factors_T_TDG": conflicts * ccz["T_TDG"],
                  "standalone_pinning_CX": support_weight + conflicts * ccz["CX"],
                  "pinning_CX_if_sharing_unflagged_Z_readout": conflicts * ccz["CX"],
                  "pinning_T_TDG": conflicts * ccz["T_TDG"]}
    return {"data_record": {"round_trip": reference, "old_direct": old,
                            "new_on_positive_inner_Z": positive, "new_unconditional_inner": unconditional},
            "unconditional_inner_instruments": [ideal_instrument(r, direct.dressed_x_program(r, graph))
                                                for r in m.SUPPORTS[:5]],
            "nonroot_Gauss_bare_meter": gauss,
            "schematic_three_round_factory": {"round_trip": {"CX": 1889, "T_TDG": 256},
                                              "old_direct": factory(old), "new_on_positive_inner_Z": factory(positive),
                                              "new_unconditional_inner": factory(unconditional)},
            "one_gauged_commuting_diagnostic_record_excluding_root": diagnostic_set,
            "conditional_history_records_before_any_recovery": {"min": 2, "max": 4},
            "unprotected_completion_root_to_dressed_X": completion}


def report_tables(events, labels, flags, graph):
    """Check-5 report lookup for targeted regression queries and one-fault coverage."""
    nc = 19 + len(graph.cycles) + 4
    mask = (1 << nc) - 1
    clean = fault.Quadratic.pauli(len(labels), [])
    images = {fault.class_image(clean, 0, labels, flags, graph)[0]}
    for event in events:
        images.add(fault.class_image(event["error"], event["report"], labels, flags, graph)[0])

    def add(table, entries):
        for flag, origin, rows in entries:
            for word in fault.image_words(origin, rows):
                key = (flag, word & mask)
                table[key] = table.get(key, 0) | (1 << (word >> nc))

    full = {}
    add(full, images)
    one_fault_keys = set(full)
    pairs = set()
    for left, right in combinations_with_replacement(events, 2):
        for early, late in ((left, right), (right, left)) if left is not right else ((left, right),):
            if early["first"] < late["last"]:
                error = late["error"].after(early["error"])
                report = early["report"] ^ late["report"]
                pairs.add(fault.class_image(error, report, labels, flags, graph)[0])
    add(full, pairs)

    def coarse(record, data_bits):
        return (record & ((1 << data_bits) - 1)) | (record & (1 << (nc - 1)))

    reduced = []
    for data_bits in (18, 18 + len(graph.cycles)):
        projected = {}
        for (flag, record), classes in full.items():
            key = flag, coarse(record, data_bits)
            projected[key] = projected.get(key, 0) | classes
        reduced.append({key: projected[key[0], coarse(key[1], data_bits)] for key in full})
    return full, *reduced, one_fault_keys


def replay(program, labels, flags, events):
    """Propagate the specified physical faults, retaining their exact phases."""
    index = {label: i for i, label in enumerate(labels)}
    final_h = max(i for i, gate in enumerate(program) if gate == ("H", ("s",)))
    diagnostic_v = [(op, tuple(index[label] for label in sites))
                    for op, sites in fault.coordinate_program(COMPACT13)]
    error = fault.Quadratic.pauli(len(labels), [])
    report = 0
    for event in events:
        step = event["instruction"]
        op, sites = program[step]
        if event["operation"] == "IDLE":
            assert not set(event["targets"]).intersection(sites)
            start = step
        else:
            assert op == event["operation"] and list(sites) == event["targets"]
            start = step + (op != "MZ")
        assignments = []
        sign = 0
        for label, pauli in zip(event["targets"], event["paulis"]):
            if label == "s" and (step > final_h or step == final_h and start > step):
                sign += 4 * (pauli == 3)
                pauli = (pauli >> 1) | ((pauli & 1) << 1)
            assignments.append((index[label], pauli))
        inserted = fault.Quadratic.pauli(len(labels), assignments)
        inserted = fault.Quadratic(inserted.x, inserted.l, inserted.a, (inserted.phase + sign) % 8)
        suffix = [(gate, tuple(index[label] for label in qs)) for i, (gate, qs) in enumerate(program)
                  if i >= start and i != final_h and gate not in ("PREP", "MZ")]
        error = inserted.conjugate(suffix).conjugate(diagnostic_v).after(error)
        if event["flip_report"]:
            wire = index[event["targets"][0]]
            report ^= 1 << (flags.index(wire) if wire in flags else len(flags))
    return error, report


def physical_branch(error, report, labels, flags, logical_word):
    answer = prior.physical_witness(error, report, labels, flags, COMPACT13, logical_word)
    assert answer is not None
    return answer


def class_list(mask):
    return list(fault.bits(mask))


def witnesses(support, candidate_events, labels, flags):
    graph = COMPACT13
    nc = 19 + len(graph.cycles) + 4
    mask = (1 << nc) - 1
    program, _ = fault.programs(support, graph, "hybrid")
    events, _, old_labels, old_flags = fault.enumerate_faults(support, graph, "hybrid")
    old, old_data, _, _ = report_tables(events, old_labels, old_flags, graph)
    outside, outside_data, _ = prior.outside_envelope(events, old_labels, old_flags, graph)
    outcomes = []
    reg = [("D16", ("D12", "D15"), ("D12", "D15", "D16", "A3")),
           ("D17", ("D10", "D11"), ("D10", "D11", "D17", "A3"))]
    for idle, hook, expected in reg:
        step = max(i for i, gate in enumerate(program) if gate == ("CX", hook))
        history = [{"instruction": 0, "operation": "IDLE", "targets": [idle], "paulis": [2], "flip_report": False},
                   {"instruction": step, "operation": "CX", "targets": list(hook), "paulis": [2, 2], "flip_report": False}]
        error, report = replay(program, old_labels, old_flags, history)
        flag, word, rows = fault.class_image(error, report, old_labels, old_flags, graph)[0]
        assert flag == 0 and not rows and not error.x and not any(error.a)
        assert all(value in (0, 2) for value in error.l)
        assert {q for q, value in zip(old_labels, error.l) if value} == set(expected)
        outcomes.append({"faults": history, "diagnostic_Z_sites": list(expected), "record": word & mask,
                         "logical_class": word >> nc,
                         "bell": physical_branch(error, report, old_labels, old_flags, word)})
    a, b = outcomes
    collision = 1073946624
    assert a["record"] == b["record"] == collision
    assert a["logical_class"] ^ b["logical_class"] == 4
    difference = set(a["diagnostic_Z_sites"]) ^ set(b["diagnostic_Z_sites"])
    m = fault.m
    assert m.mask(int(label[1:]) for label in difference) == m.mask(m.Z0) ^ m.mask(m.SUPPORTS[4]) ^ m.mask(m.SUPPORTS[5])

    step = next(i for i, gate in enumerate(program) if gate == ("CX", ("s", "A0")))
    positive_history = [{"instruction": step, "operation": "CX", "targets": ["s", "A0"],
                         "paulis": [1, 0], "flip_report": False}]
    error, report = replay(program, old_labels, old_flags, positive_history)
    flag, origin, rows = fault.class_image(error, report, old_labels, old_flags, graph)[0]
    positive = 18612288
    word = next(word for word in fault.image_words(origin, rows) if word & mask == positive)
    assert flag == 1 and word >> nc == 2
    # Old envelope drops the star bits and places the meter after the cycle word.
    coarse_cycles = positive & ((1 << (18 + len(graph.cycles))) - 1)
    coarse_data = positive & ((1 << 18) - 1)
    joint = old[flag, positive] | outside.get((flag, coarse_cycles), 0)
    blind = old_data[flag, positive] | outside_data.get((flag, coarse_data), 0)
    assert class_list(joint) == [2] and class_list(blind) == [0, 2]
    old_positive = {"faults": positive_history, "record": positive, "flags": flag,
                    "data_only_classes_with_outside_envelope": class_list(blind),
                    "joint_classes_with_outside_envelope": class_list(joint),
                    "bell": physical_branch(error, report, old_labels, old_flags, word)}
    assert old_positive["bell"]["probability"] == "1/4"

    full, data, cycles, one_fault_keys = report_tables(candidate_events, labels, flags, graph)
    assert full.get((0, collision), 0) & ((1 << a["logical_class"]) | (1 << b["logical_class"])) == 0
    candidate_outside, _, _ = prior.outside_envelope(candidate_events, labels, flags, graph)
    rejects = []
    mask_data_cycles = (1 << (18 + len(graph.cycles))) - 1
    meter = 1 << (nc - 1)
    for (flag, record), internal in sorted(full.items()):
        if not flag:
            continue
        coarse = (record & mask_data_cycles) | ((record & meter) >> 4)
        external = candidate_outside.get((flag, coarse), 0)
        if (internal | external).bit_count() > 1:
            rejects.append({"flags": flag, "record": record, "internal_classes": class_list(internal),
                            "assumed_outside_classes": class_list(external)})
    for event in candidate_events:
        if event["noise_first"] is None:
            continue
        error, report = event["error"], event["report"]
        flag, origin, rows = fault.class_image(error, report, labels, flags, graph)[0]
        for word in fault.image_words(origin, rows):
            key = flag, word & mask
            if data[key].bit_count() < 2 or cycles[key].bit_count() != 1:
                continue
            bell = prior.physical_witness(error, report, labels, flags, graph, word)
            if bell:
                candidate_positive = {"faults": [event["noise_first"]], "flags": flag, "record": key[1],
                                      "data_only_classes": class_list(data[key]), "classes_with_cycles": class_list(cycles[key]),
                                      "bell": bell}
                return {"old_collision": outcomes, "old_cycle_witness": old_positive,
                        "candidate_classes_at_old_collision": class_list(full.get((0, collision), 0)),
                        "candidate_cycle_witness": candidate_positive,
                        "candidate_outside_envelope_rejects": rejects,
                        "zero_or_one_fault_queries_under_two_fault_lookup": {
                            "queries": len(one_fault_keys),
                            "unique_with_data": sum(data[key].bit_count() == 1 for key in one_fault_keys),
                            "unique_with_cycles": sum(cycles[key].bit_count() == 1 for key in one_fault_keys),
                            "unique_with_cycles_and_stars": sum(full[key].bit_count() == 1 for key in one_fault_keys)}}
    raise AssertionError("No reachable candidate cycle witness from one gate fault")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checks", default="5,6,7,8")
    parser.add_argument("--output", type=Path, default=ROOT / "output/single-cz-direct-outer-ports.json")
    args = parser.parse_args()
    checks = [int(s) for s in args.checks.split(",")]
    if not checks or any(s not in range(5, 9) for s in checks):
        parser.error("Expected comma-separated outer checks in 5..8")
    supports, basis = prior.choose_basis()
    graph = COMPACT13
    paths = [Path(module.__file__) for module in (sys.modules[__name__], prior, direct, fault, hybrid, fault.m)]
    paths.extend(Path(obj.__code__.co_filename) for obj in (prior.choose_basis, fault.compact_pauli_program,
                                                           type(graph).decode))
    result = {"scope": "separate outer meters, ideal post-meter diagnostics and a conditional outside envelope",
              "graph": graph.name, "basis": basis, "class_map": prior.class_map_certificate(graph), "checks": {},
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}}
    for check in checks:
        support = supports[check - 5]
        program = direct.dressed_x_program(support, graph)
        with patch.object(fault, "programs", direct_route):
            one = prior.audit(support, graph, ROUTE, 1)
            two = prior.audit(support, graph, ROUTE, 2, include_outside=True)
            candidate, _, labels, flags = fault.enumerate_faults(support, graph, ROUTE)
        result["checks"][str(check)] = {"ideal": ideal_instrument(support, program),
                                        "resources": resource_counts(program), "program": program,
                                        "zero_flag_one_fault_cones": zero_flag_one_fault_cones(support, candidate, labels, flags, graph),
                                        "one_fault": one, "two_faults": two}
        if check == 5:
            result["witnesses"] = witnesses(support, candidate, labels, flags)
    result["schedule_resources"] = schedule_resources(supports, graph)
    assert result["source_sha256"] == {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
