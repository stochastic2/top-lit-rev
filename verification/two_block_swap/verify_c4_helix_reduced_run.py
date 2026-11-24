"""Read-only validation of a completed noiseless reduced-rejection run.

Checks reported histories, decoder decisions, saved exact amplitudes, and
summary consistency. Does not rerun the quantum circuit, certify a physical
event trace, or perform a noisy-yield analysis.
"""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from c4_helix_gadget_decoders import decode_b_readout
from c4_helix_history_validation import verify_history, verify_terminal_flags, verify_y_output_frame
from c4_helix_magic_y import MAGIC_OUTPUTS, ideal_success_probability
from c4_helix_compact_terminal import TERMINAL_EXTRACTIONS
from c4_helix_reduced_decoders import (
    GRAPHS, KnownStateDecoder, ReducedRejection, StableRecord, decode_gauged,
    decode_gauge_word, decode_joint,
)
from simulate_c4_helix_gadgets import VERTICES, source_family
from simulate_c4_helix_reduced import exact_magic_target, graph_family, gauged_family, clean_resource_plan
from sparse_wavefunction import SparseState


def require(value, message):
    if not value:
        raise ValueError(message)


def json_value(value):
    return json.loads(json.dumps(value))


def stable(section, length, name, policy="triple"):
    common = verify_history(section, length, name, policy, require_complete=True)
    require(common is not None, f"{name}: missing stopping triple")
    require(section["rounds_used"] == len(section["records"]) == 3, f"{name}: expected three noiseless rounds")
    require(list(common) == section["stopping_record"], f"{name}: stopping bits do not match history")
    return common


def verify_run(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    summary = json.loads((directory / "summary.json").read_text())
    require(manifest["noise_model"] == summary["noise_model"] == "none", "This verifier handles only noiseless runs")
    require(manifest["procedure"] == "reduced_rejection", "Wrong procedure")
    require(summary["completed"] is True, "The run did not complete")
    graph = GRAPHS[manifest["graph"]["name"]]
    extraction = manifest.get("extraction", "verified_cat")
    policy = manifest.get("history_policy", "triple")
    terminal = manifest.get("terminal_extraction", "protected")
    magic = manifest.get("magic_output", "z")
    require(magic in MAGIC_OUTPUTS and summary.get("magic_output", "z") == magic, "Magic output profile mismatch")
    require(terminal in TERMINAL_EXTRACTIONS, "Unknown terminal extraction")
    require(summary.get("terminal_extraction", "protected") == terminal, "Summary terminal extraction mismatch")
    if terminal == "compact_flagged":
        require(manifest.get("terminal_flag_policy") == summary.get("terminal_flag_policy") == "repair_then_protected",
                "Unsupported compact terminal flag-recovery policy")
    require(summary.get("history_policy", "triple") == policy, "Summary history policy mismatch")
    require(extraction in ("optimized", "verified_cat"), "Unknown extraction profile")
    require(summary.get("extraction", "verified_cat") == extraction, "Summary extraction mismatch")
    graph.validate()
    require(manifest["graph"] == json_value({"name": graph.name, "edges": graph.edges,
                                             "cycles": graph.cycles, "tree_edges": graph.tree_edges}),
            "Manifest graph differs from the supported physical graph")
    require(summary["graph"] == graph.name, "Summary graph mismatch")
    require(manifest["ideal_success_probability"] == summary["ideal_success_probability"] == ideal_success_probability(magic),
            "Wrong ideal success probability")
    require(manifest["noise_study_enabled"] is False, "A noise study is not a noiseless validation run")
    accepted = attempts = 0
    rejections, counts, verified_states = Counter(), Counter(), set()
    with (directory / "shots.jsonl").open() as stream:
        for line in stream:
            record = json.loads(line)
            index = attempts
            attempts += 1
            require(record["shot_index"] == index and record["seed"] == manifest["seed"] + index,
                    "Shot order or per-attempt seed mismatch")
            require(record["noise_model"] == "none" and record["graph"] == graph.name, "Shot configuration mismatch")
            require(record["source_preparation"] == manifest["source_preparation"], "Source mode mismatch")
            require(record.get("extraction", "verified_cat") == extraction, "Shot extraction mismatch")
            require(record.get("history_policy", "triple") == policy, "Shot history policy mismatch")
            require(record.get("terminal_extraction", "protected") == terminal, "Shot terminal extraction mismatch")
            require(record.get("magic_output", "z") == magic, "Shot magic profile mismatch")
            verify_terminal_flags(record, terminal)
            for copy in "BC":
                section = record["sources"][copy]
                common = stable(section, 20, f"source/{copy}", policy)
                decoder = KnownStateDecoder(tuple(f"{copy}_{q}" for q in range(20)), source_family(copy))
                require(section["correction"] == list(decoder.decode(common)), "Wrong known-source correction")
                if extraction == "optimized":
                    require(len(section["attempts"]) == 1 and section["attempts"][0]["outcome"] == "prepared",
                            "A noiseless optimized source must not require a flag retry")
                if record["source_preparation"] == "encoded":
                    require(not any(common), "A noiseless encoded source must have zero complete syndrome")
            require(len(record["cycles"]) == 1, "An unmodified noiseless input must use one cycle")
            cycle = record["cycles"][0]
            require(cycle["index"] == 0, "Wrong cycle index")
            graph_signs = stable(cycle["graph_source"], 5 + len(graph.edges), "graph", policy)
            require(not any(graph_signs), "The noiseless graph must have positive source signs")
            graph_labels = VERTICES + tuple(f"A_{q}" for q in range(len(graph.edges)))
            require(cycle["graph_source"]["correction"] == list(
                KnownStateDecoder(graph_labels, graph_family(graph)).decode(graph_signs)),
                "Wrong graph-source correction")
            common = stable(cycle["gauged"], len(gauged_family(graph)), "gauged", policy)
            r = sum(cycle["vertex_x"]) % 2
            require(cycle["vertex_reported_parity"] == r, "Vertex parity mismatch")
            require(common == (0,) * (len(common) - 5) + (r, 0, 0, 0, 0),
                    "Noiseless gauged signs do not match vertex outcome")
            require(Fraction(cycle["vertex_word_probability"]) == Fraction(1 if r else 3, 64),
                    "Vertex word has wrong exact Born probability")
            try:
                decoded = decode_gauged(common, graph)
            except ReducedRejection as rejection:
                require(rejection.code == record["rejection_code"] == "negative_swap", "Wrong SWAP rejection")
                require(cycle["gauged"]["decoding"] == json_value(rejection.details),
                        "Wrong negative-SWAP decoder decision")
                require(not record["accepted"], "Negative SWAP was accepted")
                require(cycle["gauge_z"] is None and record["b_z"] is None and not cycle["terminal"],
                        "Negative SWAP exposes unperformed later stages")
            else:
                require(cycle["gauged"]["decoding"] == json_value(decoded), "Wrong gauged decoding")
                require(cycle["gauge_decoding"] == json_value(decode_gauge_word(cycle["gauge_z"], graph)),
                        "Wrong gauge readout decoding")
                require(cycle["gauge_z"] == cycle["gauge_decoding"]["corrected_bits"],
                        "Noiseless gauge word requires an unexpected bit correction")
                signs = stable(cycle["terminal"], 37 if magic == "y" else 36, "terminal", policy)
                require(not any(signs[:36]), "Noiseless terminal code syndrome must be zero")
                require(cycle["terminal"]["decoding"] == json_value(decode_joint(signs[:36])), "Wrong joint recovery")
                require(cycle["next_action"] == "extract", "Noiseless positive cycle did not extract")
                if magic == "y":
                    require(record["accepted"] is True and record["rejection_code"] is None, "Ideal Y readout rejected an outcome")
                    verify_y_output_frame(record)
                else:
                    b = decode_b_readout(record["b_z"])
                    require(record["b_decoding"] == json_value(b), "Wrong B readout decoding")
                    require(record["accepted"] is b["keep"], "Acceptance differs from decoded B selection")
                    require(record["rejection_code"] == (None if b["keep"] else "logical_B_one"), "Wrong B rejection")
            metrics = record["metrics"]
            require(metrics["physical_events"] == sum(metrics["gate_counts"].values()), "Physical event count mismatch")
            require(metrics["gate_counts"]["FREDKIN"] == 80, "Wrong full-gadget Fredkin count")
            plan = clean_resource_plan(graph, extraction, record["source_preparation"], include_terminal=not r,
                                       terminal_extraction=terminal, magic_output=magic)
            require(metrics["peak_live_qubits"] == plan["peak_live_qubits"], "Wrong helper/register peak")
            checks = plan["check_gadgets"]
            require(metrics["check_gadgets_completed"] == metrics["cats_prepared"] == checks,
                    "Wrong number of executed check gadgets")
            require(metrics["cat_scans_completed"] == plan["cat_scans"], "Wrong number of noiseless cat scans")
            if extraction == "optimized":
                require(metrics["flag_bits_measured"] == plan["flag_bits"], "Wrong source-flag bit count")
                require(metrics["flagged_source_checks"] == 120, "Wrong source-flag gadget count")
            if terminal == "compact_flagged":
                require(metrics["terminal_flag_bits_measured"] == plan["terminal_flag_bits"], "Terminal flag count mismatch")
                require(metrics["flagged_terminal_checks"] == (0 if r else 108), "Terminal check count mismatch")
            for gate in ("CX", "CZ", "FREDKIN"):
                require(metrics["gate_counts"].get(gate, 0) == plan["gate_counts"][gate],
                        f"Wrong executed {gate} count for the extraction profile")
            swaps = 0 if r else 4*sum(cycle["gauge_decoding"]["offsets"])
            require(metrics["gate_counts"].get("SWAP", 0) == swaps, "Wrong ungauging SWAP count")
            require(metrics["implicit_single_qubit_idles"] == sum(metrics["idle_locations_by_register"].values())
                    == sum(metrics["idle_locations_by_operation"].values()), "Idle accounting mismatch")
            counts.update(metrics["gate_counts"])
            if record["accepted"]:
                accepted += 1
                reference = record["c_state_reference"]
                y_bit = record["b_y"]["logical_bit"] if magic == "y" else None
                target = exact_magic_target(magic, y_bit).canonical_payload()
                path = (directory / reference).resolve()
                require(path.is_relative_to(directory / "states"), "State reference is outside this run's states folder")
                if reference not in verified_states:
                    payload = json.loads(path.read_text())
                    state = SparseState.from_payload(payload)
                    require(state.canonical_payload() == target, "Saved C amplitudes differ from the exact magic target")
                    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
                    require(path.stem == sha256(serialized.encode()).hexdigest(), "State content hash mismatch")
                    verified_states.add(reference)
                require(record["exact_magic_target_match"] is True, "Saved target diagnostic is false")
                d = record["physical_C_diagnostics"]
                require(d["in_original_code_space"] and d["entries"] == 1024, "C code diagnostic mismatch")
                expected = (["2/3", "1/3" if y_bit == 0 else "-1/3", "2/3", "1"] if magic == "y" else
                            ["4/5", "0", "3/5", "1"])
                require([d[k] for k in ("logical_X0", "logical_Y0", "logical_Z0", "logical_Z1")]
                        == expected, "C logical diagnostic mismatch")
            else:
                rejections[record["rejection_code"]] += 1
                require(record["c_state_reference"] is None, "Rejected attempt exposes a C output")
    require(attempts == summary["attempts"] == manifest["attempts_requested"], "Attempt count mismatch")
    require(accepted == summary["accepted"] == summary["accepted_states_exactly_validated"], "Acceptance count mismatch")
    require(summary["rejected"] == attempts - accepted, "Rejection count mismatch")
    require(summary["rejection_counts"] == dict(rejections), "Rejection breakdown mismatch")
    require(summary["gate_counts"] == dict(counts), "Aggregate gate counts mismatch")
    require(Fraction(summary["observed_noiseless_acceptance_fraction"]) == Fraction(accepted, attempts),
            "Observed noiseless acceptance fraction mismatch")
    return {"verified": True, "noise_model": "none", "attempts": attempts, "accepted": accepted,
            "distinct_C_states_checked": len(verified_states), "graph": graph.name, "extraction": extraction,
            "scope": "Saved reports/decisions/amplitudes; not a replay of the physical event trace"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_run(args.run_directory), indent=2))
    except (ValueError, KeyError, OSError, TypeError, ZeroDivisionError) as error:
        parser.exit(1, f"Verification failed: {error}\n")


if __name__ == "__main__":
    main()
