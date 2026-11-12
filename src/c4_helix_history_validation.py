"""Read-only checks of complete-record histories, including unfinished stages."""

import json

from c4_helix_reduced_decoders import ReducedRejection, history_metadata, record_history


def verify_history(section, length, location, policy, require_complete=False):
    if section.get("history_policy", "triple") != policy:
        raise ValueError(f"{location}: history policy mismatch")
    history = record_history(length, location, policy)
    reports = section.get("records", [])
    common = None
    for index, report in enumerate(reports):
        try:
            common = history.add(report)
        except ReducedRejection:
            if policy != "triple" or index != len(reports)-1 or "stopping_record" in section:
                raise ValueError(f"{location}: invalid exhausted history") from None
    if "stopping_record" in section:
        if common is None or list(common) != section["stopping_record"] or section["rounds_used"] != len(reports):
            raise ValueError(f"{location}: stopping record does not match the first certified prefix")
        if policy == "adaptive":
            expected = json.loads(json.dumps(history_metadata(history)["reference_certificate"]))
            if section.get("reference_certificate") != expected:
                raise ValueError(f"{location}: clean-reference certificate mismatch")
    elif common is not None or require_complete:
        raise ValueError(f"{location}: missing stopping record")
    return common


def verify_report_histories(record, graph, policy):
    for copy, source in record.get("sources", {}).items():
        for attempt in source.get("attempts", [source]):
            if "records" in attempt:
                verify_history(attempt, 20, f"source/{copy}", policy)
        if "stopping_record" in source:
            verify_history(source, 20, f"source/{copy}", policy, require_complete=True)
    for cycle in record.get("cycles", []):
        for key, length in (("graph_source", 5+len(graph.edges)),
                            ("gauged", 18+len(graph.cycles)+5), ("terminal", 36)):
            section = cycle[key]
            if key == "terminal":
                expected_y = record.get("magic_output", "z") == "y" and cycle["gauged"].get("decoding", {}).get("certified", False)
                if "records" in section and section.get("includes_logical_y", False) != expected_y:
                    raise ValueError("Terminal logical-Y family does not match the output profile")
                length += int(expected_y)
            if "records" in section:
                verify_history(section, length, f"cycle/{cycle['index']}/{key}", policy)
            if key == "terminal" and "compact_history" in section:
                verify_history(section["compact_history"], length, f"cycle/{cycle['index']}/compact_terminal", policy)


def verify_terminal_flags(record, terminal):
    rows = record.get("terminal_flag_records", [])
    if terminal == "protected":
        if rows:
            raise ValueError("Protected extraction contains unexpected terminal flags")
        return
    from simulate_c4_helix_gadgets import original_family
    from c4_helix_compact_terminal import flag_repair_pattern, terminal_targets
    family = original_family()
    m = record["metrics"]
    if len(rows) != m["flagged_terminal_checks"] or sum(len(r["flags"]) for r in rows) != m["terminal_flag_bits_measured"]:
        raise ValueError("Terminal flag accounting mismatch")
    used = 0
    for cycle in record.get("cycles", []):
        prefix = f"cycle/{cycle['index']}/terminal/round/"
        section = cycle["terminal"]
        compact = section.get("compact_history", section)
        observed = [r for r in rows if r["location"].startswith(prefix)]
        full = len(compact.get("records", []))
        nonzero = [r for r in observed if any(r["flags"])]
        if nonzero and (len(nonzero) != 1 or nonzero[0] != observed[-1]):
            raise ValueError("Compact acquisition continued after a terminal flag")
        if bool(section.get("compact_history") is not None) != bool(nonzero and nonzero[0]["action"] == "protected_fallback"):
            raise ValueError("Terminal flag fallback history mismatch")
        if len(observed) < full*len(family):
            raise ValueError("Missing compact terminal flag records")
        for index, row in enumerate(observed):
            round_index, check = divmod(index, len(family))
            name, ports = family[check]
            if row["location"] != f"{prefix}{round_index}/{name}" or row["axis"] != ports[0][0] or row["weight"] != len(ports):
                raise ValueError("Terminal flag location/shape mismatch")
            if len(row["flags"]) != (1 if len(ports) == 4 else 5) or any(type(b) is not int or b not in (0, 1) for b in row["flags"]):
                raise ValueError("Invalid terminal flag bits")
            if row["reported_syndrome"] not in (0, 1):
                raise ValueError("Invalid compact syndrome bit")
            if any(row["flags"]):
                try:
                    positions = flag_repair_pattern(len(ports), row["flags"])
                except ReducedRejection:
                    if row["action"] != "reject_unsupported" or record.get("rejection_code") != "terminal_flag_unsupported":
                        raise ValueError("Unsupported terminal flags did not reject") from None
                else:
                    _, targets = terminal_targets(ports)
                    if row["action"] != "protected_fallback" or row["repair_targets"] != [targets[j] for j in positions]:
                        raise ValueError("Wrong terminal flag repair")
                    if section.get("extraction_used") != "protected_fallback" or section.get("flag_recovery") != row:
                        raise ValueError("Terminal flag repair did not trigger protected acquisition")
            elif row["action"] != "continue" or row["repair_targets"]:
                raise ValueError("Zero flags received an unexpected repair")
            if round_index < full:
                if row["reported_syndrome"] != compact["records"][round_index][check]:
                    raise ValueError("Terminal flag syndrome differs from complete history")
            elif (not nonzero and not (record.get("rejection_code") == "unstable_record" and
                                      compact.get("includes_logical_y", False))) or round_index != full:
                raise ValueError("Unexpected incomplete compact terminal round")
        used += len(observed)
    if used != len(rows):
        raise ValueError("Terminal flag records reference an unknown cycle")


def verify_y_output_frame(record):
    """Recompute Y outcome correction from reported syndrome and chosen Pauli."""
    if record.get("magic_output", "z") != "y" or not record.get("accepted"):
        return
    from c4_helix_magic_y import corrected_y_bit, output_frame
    from c4_helix_reduced_decoders import decode_joint
    section = record["cycles"][-1]["terminal"]
    signs = section["stopping_record"]
    if len(signs) != 37 or not section.get("includes_logical_y"):
        raise ValueError("Accepted Y output has no joint Y reference")
    decoded = decode_joint(signs[:36])
    if json.loads(json.dumps(decoded)) != section["decoding"]:
        raise ValueError("Wrong joint correction used for Y readout")
    bit = corrected_y_bit(signs[36], decoded["B"])
    expected = {"reported_word_bit": signs[36], "logical_bit": bit,
                "eigenvalue": 1 if bit == 0 else -1, "both_outcomes_kept": True,
                "source": "joint terminal clean-reference record"}
    if record.get("b_y") != expected or section.get("logical_y_decoding") != expected:
        raise ValueError("Logical Y decoding mismatch")
    if record.get("output_clifford_frame") != output_frame(bit):
        raise ValueError("Output Clifford frame mismatch")
    if record["b_decoding"] != {"basis": "Y", "logical_bit": bit, "keep": True,
                                "z_reports_used_only_for_discard": True}:
        raise ValueError("Y readout did not keep both outcomes")
