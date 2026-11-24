"""Read-only verification of saved noisy-run accounting and exact C diagnostics.

This checks saved artifacts, not the random sampling or a replay of the
physical circuit. Imperfect accepted states are valid simulation results.
"""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from c4_helix_depolarizing import DepolarizingModel, nonidentity_probability
from c4_helix_logical_diagnostics import decoded_c_diagnostics
from c4_helix_history_validation import verify_report_histories, verify_terminal_flags, verify_y_output_frame
from c4_helix_magic_y import MAGIC_OUTPUTS
from c4_helix_compact_terminal import TERMINAL_EXTRACTIONS
from c4_helix_reduced_decoders import GRAPHS, HISTORY_POLICIES
from simulate_c4_helix_depolarizing import default_noise_seed, summarize
from simulate_c4_helix_reduced import exact_magic_target
from sparse_wavefunction import SparseState


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_noise(record, model):
    noise, metrics = record["noise"], record["metrics"]
    gates = Counter(metrics["gate_counts"])
    opportunities = Counter(noise["channel_opportunities"])
    expected = Counter({"preparation": gates["PREP"], "readout": gates["MZ"],
                        "gate_1q": sum(gates[p] for p in ("H", "X", "Y", "Z", "S", "SDG")),
                        "gate_2q": sum(gates[p] for p in ("CX", "CZ", "SWAP")),
                        "gate_3q": gates["FREDKIN"], "idle": metrics["implicit_single_qubit_idles"]})
    require(opportunities == expected, "Noise opportunities differ from physical operation counts")
    require(sum(gates.values()) == metrics["physical_events"], "Physical event total mismatch")
    rates = {f"gate_{n}q_depolarizing": model.gate_probability(n) for n in (1, 2, 3)}
    rates.update(idle_depolarizing=nonidentity_probability(model.idle_infidelity, 1),
                 preparation_flip=model.preparation_flip_probability,
                 readout_flip=model.readout_flip_probability)
    counts, axes = Counter(), Counter()
    previous = -1
    for index, event in enumerate(noise["events"]):
        channel = event["channel"]
        require(channel in rates and rates[channel] > 0, "Event on an unknown or zero-rate channel")
        require(event["id"] == index, "Nonconsecutive noise event IDs")
        physical = event["physical_event_index"]
        require(previous <= physical < metrics["physical_events"], "Noise event order/range mismatch")
        previous = physical
        targets, paulis = event["targets"], event["paulis"]
        require(len(set(targets)) == len(targets) and set(paulis) <= set(targets), "Invalid noise targets")
        require(all(p in ("X", "Y", "Z") for p in paulis.values()), "Invalid noise Pauli")
        if channel.startswith("gate_"):
            n = int(channel[5])
            operations = {1: ("H", "X", "Y", "Z", "S", "SDG"), 2: ("CX", "CZ", "SWAP"), 3: ("FREDKIN",)}
            require(len(targets) == n and paulis and event["operation"] in operations[n]
                    and event["timing"] == "after", "Invalid gate-noise event")
        elif channel == "idle_depolarizing":
            require(len(targets) == 1 and paulis and event["timing"] == "idle", "Invalid idle event")
        elif channel == "preparation_flip":
            require(len(targets) == 1 and paulis == {targets[0]: "X"}
                    and event["operation"] == "PREP" and event["timing"] == "after", "Invalid preparation event")
        else:
            require(len(targets) == 1 and not paulis and event["operation"] == "MZ"
                    and event["timing"] == "report", "Invalid readout event")
        require(event["flip_report"] == (channel == "readout_flip"), "Report-flip marker mismatch")
        counts[channel] += 1
        axes.update(paulis.values())
    require(noise["sampled_events"] == len(noise["events"]), "Sampled event total mismatch")
    require(dict(counts) == noise["event_counts_by_channel"], "Channel event counts mismatch")
    require(dict(axes) == noise["pauli_factor_counts"], "Pauli factor counts mismatch")
    hazard = sum((expected[f"gate_{n}q"] * model.gate_probability(n) for n in (1, 2, 3)), Fraction(0))
    hazard += expected["idle"] * rates["idle_depolarizing"]
    hazard += expected["preparation"] * rates["preparation_flip"] + expected["readout"] * rates["readout_flip"]
    require(str(hazard) == noise["sum_of_executed_channel_probabilities"], "Channel probability sum mismatch")


def verify_run(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    summary = json.loads((directory / "summary.json").read_text())
    model = DepolarizingModel(**manifest["noise_model"]["rates"])
    policy = manifest.get("history_policy", "triple")
    terminal = manifest.get("terminal_extraction", "protected")
    magic = manifest.get("magic_output", "z")
    require(magic in MAGIC_OUTPUTS and summary.get("magic_output", "z") == magic, "Magic output profile mismatch")
    require(terminal in TERMINAL_EXTRACTIONS, "Unknown terminal extraction")
    require(summary.get("terminal_extraction", "protected") == terminal, "Summary terminal extraction mismatch")
    if terminal == "compact_flagged":
        require(manifest.get("terminal_flag_policy") == summary.get("terminal_flag_policy") == "repair_then_protected",
                "Unsupported compact terminal flag-recovery policy")
    require(policy in HISTORY_POLICIES, "Unknown history policy")
    require(summary.get("history_policy", "triple") == policy, "Summary history policy mismatch")
    require(model.manifest() == manifest["noise_model"], "Noise manifest mismatch")
    require(summary["completed"] is True, "Run is still in progress")
    records = [json.loads(line) for line in (directory / "shots.jsonl").read_text().splitlines()]
    require(len(records) == manifest["attempts_requested"], "Requested attempt count mismatch")
    states = {}
    for index, record in enumerate(records):
        require(record["shot_index"] == index and record["seed"] == manifest["seed"] + index, "Attempt seed/index mismatch")
        base = manifest["noise_seed_base"]
        noise_seed = default_noise_seed(record["seed"]) if base is None else base + index
        require(record["noise_seed"] == noise_seed, "Noise seed mismatch")
        require(record["noise_model"] == "pauli_depolarizing", "Shot noise model mismatch")
        require(record.get("magic_output", "z") == magic, "Shot magic profile mismatch")
        require(record.get("history_policy", "triple") == policy, "Shot history policy mismatch")
        require(record.get("terminal_extraction", "protected") == terminal, "Shot terminal extraction mismatch")
        if terminal == "compact_flagged" and record["execution_status"] == "completed":
            require(record.get("terminal_flag_policy") == "repair_then_protected", "Shot terminal flag policy mismatch")
        require(record["graph"] == manifest["graph"]["name"] and record["extraction"] == manifest["extraction"],
                "Shot circuit configuration mismatch")
        if record["execution_status"] != "completed":
            require(record["execution_status"] == "resource_failure" and record["accepted"] is None
                    and record["rejection_code"] is None and record["c_state_reference"] is None,
                    "Computational failure was treated as a physical decision")
            continue
        require(type(record["accepted"]) is bool, "Completed attempt has no physical decision")
        verify_report_histories(record, GRAPHS[manifest["graph"]["name"]], policy)
        verify_terminal_flags(record, terminal)
        verify_y_output_frame(record)
        verify_noise(record, model)
        if not record["accepted"]:
            require(record["c_state_reference"] is None and record["rejection_code"], "Invalid rejected output")
            continue
        require(record["rejection_code"] is None, "Accepted attempt has a rejection code")
        reference = record["c_state_reference"]
        y_bit = record["b_y"]["logical_bit"] if magic == "y" else None
        target = exact_magic_target(magic, y_bit).canonical_payload()
        path = (directory / reference).resolve()
        require(path.is_relative_to(directory / "states"), "State reference escapes the run's states folder")
        state_key = (reference, y_bit)
        if state_key not in states:
            payload = json.loads(path.read_text())
            serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            require(path.stem == sha256(serialized.encode()).hexdigest(), "State content hash mismatch")
            state = SparseState.from_payload(payload)
            require(payload == state.canonical_payload(), "Saved state is not canonical")
            states[state_key] = (payload == target, decoded_c_diagnostics(state, magic_output=magic, y_outcome=y_bit))
        exact, diagnostic = states[state_key]
        require(record["exact_magic_target_match"] == exact, "Raw target comparison mismatch")
        if record["diagnostic_status"] == "completed":
            require(record["decoded_C_diagnostics"] == diagnostic, "Decoded C diagnostic mismatch")
    for key, value in summarize(records).items():
        require(summary[key] == value, f"Aggregate summary mismatch: {key}")
    require(summary["noise_model"] == manifest["noise_model"], "Summary noise model mismatch")
    return {"verified": True, "attempts": len(records), "accepted": summary["accepted"],
            "unresolved_attempts": summary["unresolved_attempts"], "distinct_C_states_checked": len(states),
            "scope": "Saved accounting, hashes, amplitudes and logical diagnostics; no physical-circuit replay"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_run(args.run_directory), indent=2))
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, f"Verification failed: {error}\n")


if __name__ == "__main__":
    main()
