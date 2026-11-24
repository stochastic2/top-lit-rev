"""Compact terminal Pauli checks with certified zero-flag physical spread.

Four-data checks bracket the dangerous two middle couplings with one flag.
Eight-data checks add two post-coupling cat parities before decoding flags.
Nonzero flags receive a certified block-locality repair and switch to
protected terminal recovery. Unknown B/C data are never reinitialized.
"""

from collections import Counter

from c4_helix_reduced_decoders import ReducedRejection


TERMINAL_EXTRACTIONS = ("protected", "compact_flagged")


class TerminalFlagRecovery(Exception):
    """Keep the repaired data and restart acquisition with protected cats."""

    def __init__(self, details):
        super().__init__("Compact terminal flag requests protected recovery")
        self.details = details


def flag_repair_pattern(weight, flags):
    """Audit-certified repair in virtual data order; upper flag bit 0 is first.

    All reachable nonzero flags admit the identity repair except word 13.
    Word 19 cannot arise from <=2 faults in this gadget and is rejected.
    The resulting bound is in matched blocks, requiring protected cleanup.
    """
    expected = 1 if weight == 4 else 5 if weight == 8 else -1
    if len(flags) != expected or any(type(b) not in (int, bool) or b not in (0, 1) for b in flags):
        raise ValueError("Invalid compact terminal flag vector")
    word = sum(int(b) << j for j, b in enumerate(flags))
    if weight == 8 and word == 19:
        raise ReducedRejection("terminal_flag_unsupported", "Flag vector requires more than two gadget faults",
                               {"flags": tuple(flags), "weight": weight})
    return (2, 3, 4, 5) if weight == 8 and word == 13 else ()


def compact_terminal_program(weight, axis):
    if axis not in ("X", "Z"):
        raise ValueError("Compact terminal checks are Pauli X or Z")
    gate = "CX" if axis == "X" else "CZ"
    if weight == 4:
        a, f = 4, 5
        return [("PREP", (a,)), ("PREP", (f,)), ("H", (a,)),
                (gate, (a, 0)), ("CX", (a, f)),
                (gate, (a, 1)), (gate, (a, 2)), ("CX", (a, f)), (gate, (a, 3)),
                ("MZ", (f,)), ("H", (a,)), ("MZ", (a,))]
    if weight != 8:
        raise ValueError("Compact terminal checks have weight four or eight")
    ops = [("PREP", (8+j,)) for j in range(4)]+[("H", (8,))]
    ops += [("CX", (8, 8+j)) for j in range(1, 4)]
    ops += [(gate, (8+j, 2*j+i)) for i in range(2) for j in range(4)]
    # Connecting three leaves rules out every two-versus-two cat pattern.
    # The fourth leaf is still tested by its decoded flag below.
    for left, right in ((8, 9), (9, 10)):
        ops += [("PREP", (12,)), ("CX", (left, 12)), ("CX", (right, 12)), ("MZ", (12,))]
    ops += [("CX", (8, 8+j)) for j in reversed(range(1, 4))]
    ops += [("MZ", (8+j,)) for j in range(1, 4)]
    return ops+[("H", (8,)), ("MZ", (8,))]


def terminal_targets(ports):
    ports = tuple((axis, tuple(labels)) for axis, labels in ports)
    if len(ports) not in (4, 8) or len({a for a, _ in ports}) != 1:
        raise ValueError("Compact terminal ports require one axis and four or eight targets")
    if any(len(qs) != 1 or not qs[0].startswith(("B_", "C_")) for _, qs in ports):
        raise ValueError("Compact terminal checks require original B/C data coordinates")
    labels = tuple(qs[0] for _, qs in ports)
    if len(set(labels)) != len(labels) or len({q.split("_")[0] for q in labels}) != 1:
        raise ValueError("Compact terminal targets must be distinct and on one copy")
    groups = {}
    for q in labels:
        groups.setdefault(int(q.split("_")[1])//4, []).append(q)
    sizes = sorted(map(len, groups.values()))
    if sizes != ([4] if len(ports) == 4 else [2]*4):
        raise ValueError("Compact terminal target layout is outside the certified shapes")
    return ports[0][0], tuple(q for group in groups.values() for q in group)


def compact_terminal_cost(ports):
    axis, labels = terminal_targets(ports)
    ops = compact_terminal_program(len(labels), axis)
    return {"gates": Counter(op for op, _ in ops), "leaves": 2 if len(labels) == 4 else 4,
            "cat_scans": 0, "flags": (1 if len(labels) == 4 else 5),
            "meters": sum(op == "MZ" for op, _ in ops)}


def measure_compact_terminal(runtime, location, ports):
    axis, labels = terminal_targets(ports)
    if not set(labels) <= runtime.live:
        raise ValueError("Compact terminal check targets absent data")
    n = len(labels)
    mapping = dict(enumerate(labels))
    mapping.update({n+j: f"L_{j}" for j in range(2 if n == 4 else 4)})
    if n == 8:
        mapping[12] = "w"
    reports = []
    for index, (op, qs) in enumerate(compact_terminal_program(n, axis)):
        targets = tuple(mapping[q] for q in qs)
        prefix = f"{location}/compact/{index}/{op}"
        if op == "PREP":
            runtime.prepare(prefix, targets[0])
        elif op == "MZ":
            reports.append(runtime.measure_z(prefix, targets[0]))
        else:
            runtime.gate(prefix, op, *targets)
    flags, report = tuple(reports[:-1]), reports[-1]
    runtime.cats_prepared += 1
    runtime.check_gadgets_completed += 1
    runtime.flagged_terminal_checks += 1
    runtime.terminal_flag_bits_measured += len(flags)
    record = {"location": location, "flags": flags, "reported_syndrome": report, "weight": n, "axis": axis,
              "action": "pending_recovery" if any(flags) else "continue", "repair_targets": []}
    runtime.terminal_flag_records.append(record)
    runtime.decision("terminal_flag_record", **record)
    runtime.log_check(location, (report,), report)
    if any(flags):
        try:
            positions = flag_repair_pattern(n, flags)
        except ReducedRejection:
            record["action"] = "reject_unsupported"
            raise
        record.update(action="protected_fallback", repair_targets=[labels[j] for j in positions])
        for j in positions:
            runtime.gate(f"{location}/flag_repair/{j}", axis, labels[j])
        runtime.decision("terminal_flag_repair", location, **{k: v for k, v in record.items() if k != "location"})
        raise TerminalFlagRecovery(dict(record))
    return report
