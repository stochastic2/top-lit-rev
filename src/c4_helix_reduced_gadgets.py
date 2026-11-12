"""Protected cats and compact known-source flags on an exact sparse wavefunction.

The runtime boundary preserves named operations and implicit serial idles
for a later, separately validated noise implementation. There is no noise
sampler and no gate is replaced by a stabilizer projector.
"""

from collections import Counter
from fractions import Fraction

from c4_helix_fault_runtime import PhysicalRuntime
from c4_helix_reduced_decoders import HISTORY_POLICIES, record_history, history_metadata, cat_repair_pattern


class SourceFlag(Exception):
    """An unused known source must be rebuilt locally, before enrichment."""

    def __init__(self, location, flags, syndrome):
        super().__init__(f"Known-source flag at {location}")
        self.details = {"location": location, "flags": tuple(flags), "syndrome": syndrome}


class NoiselessRuntime(PhysicalRuntime):
    def __init__(self, rng, trace=None, max_terms=4096, history_policy="triple"):
        if max_terms < 1:
            raise ValueError("max_terms must be positive")
        super().__init__(rng, faults=(), trace=trace, max_terms=max_terms)
        if history_policy not in HISTORY_POLICIES:
            raise ValueError("History policy is adaptive or triple")
        self.history_policy = history_policy
        self.idle_locations = 0
        self.idle_locations_by_register = Counter()
        self.idle_locations_by_operation = Counter()
        self.cat_scans = 0
        self.cats_prepared = 0
        self.check_gadgets_completed = 0
        self.flagged_source_checks = 0
        self.flag_bits_measured = 0
        self.grouped_protected_checks = 0
        self.flagged_terminal_checks = 0
        self.terminal_flag_bits_measured = 0
        self.terminal_flag_records = []
        self.vertex_word_probabilities = {}

    def _event(self, location, operation, targets, fault_indices, **details):
        # PREP has already made its participant live; MZ has removed its
        # participant. In either case live - participants is exactly the
        # waiting set during this serial physical operation.
        idle = self.live.difference(targets)
        self.idle_locations += len(idle)
        self.idle_locations_by_operation[operation] += len(idle)
        self.idle_locations_by_register.update(label.split("_")[0] for label in idle)
        if operation == "MZ" and "/vertex/" in location:
            prefix = location.split("/vertex/")[0]
            self.vertex_word_probabilities[prefix] = self.vertex_word_probabilities.get(
                prefix, Fraction(1)) * Fraction(details["probability"])
        if self.trace is not None:
            details.update(kind="physical", idle_qubits=sorted(idle))
        super()._event(location, operation, targets, fault_indices, **details)

    def decision(self, kind, location, **details):
        if self.trace is not None:
            self.trace({"kind": kind, "location": location, "after_event": self.events - 1,
                        **details})


def repair_cat(runtime, location, leaves, zero_scans=3):
    """Measure/repeat the full adjacent-ZZ vector, then physically correct it.

    Exposed separately so small noiseless state-preparation experiments can
    validate arbitrary cat cosets. No clean-scan oracle is used.
    """
    leaves = tuple(leaves)
    if zero_scans not in (2, 3):
        raise ValueError("The certified zero-scan count is two or three")
    if not leaves or len(set(leaves)) != len(leaves) or not set(leaves) <= runtime.live:
        raise ValueError("Cat leaves must be nonempty, distinct, and live")
    history = record_history(len(leaves) - 1, location, getattr(runtime, "history_policy", "triple"))
    common = ()
    if len(leaves) > 1:
        for scan in range(history.max_rounds):
            reports = []
            for j in range(len(leaves) - 1):
                prefix = f"{location}/verify/{scan}/{j}"
                runtime.prepare(prefix + "/prepare", "w")
                runtime.gate(prefix + "/left", "CX", leaves[j], "w")
                runtime.gate(prefix + "/right", "CX", leaves[j + 1], "w")
                reports.append(runtime.measure_z(prefix + "/measure", "w"))
            runtime.cat_scans += 1
            runtime.decision("cat_scan", location, scan=scan, reported_bits=reports)
            common = history.add(reports)
            # Two initially zero scans suffice under the global two-fault
            # budget: a raw-chain fault already consumes one of the faults.
            # A nonzero prefix uses the selected complete-history policy.
            if zero_scans == 2 and len(history.records) == 2 and not any(
                    b for record in history.records for b in record):
                common = tuple(reports)
                break
            if common is not None:
                break
    pattern = cat_repair_pattern(common)
    for j, bit in enumerate(pattern):
        if bit:
            runtime.gate(f"{location}/cat/correction/{j}", "X", leaves[j])
    result = {"scan_records": history.records, "scans_used": len(history.records),
              "stopping_record": common, "x_pattern": pattern,
              "stopping_rule": ("two_initial_zero_scans" if len(history.records) == 2 else
                                "adaptive_clean_reference" if history.policy == "adaptive" else "three_equal_records"),
              **history_metadata(history)}
    runtime.decision("cat_repair", location, **result)
    return result


def prepare_repaired_cat(runtime, location, size, zero_scans=3):
    if size < 1:
        raise ValueError("A check requires at least one cat leaf")
    leaves = tuple(f"L_{j}" for j in range(size))
    for j, label in enumerate(leaves):
        runtime.prepare(f"{location}/cat/prepare/{j}", label)
    runtime.gate(location + "/cat/H", "H", leaves[0])
    for j in range(size - 1):
        runtime.gate(f"{location}/cat/chain/{j}", "CX", leaves[j], leaves[j + 1])
    runtime.cats_prepared += 1
    repair_cat(runtime, location, leaves, zero_scans)
    return leaves


def couple_and_read_cat(runtime, location, leaves, ports, leaf_indices=None):
    """Use the explicit allowed port-to-leaf map, then read all leaves in X."""
    leaf_indices = tuple(range(len(ports))) if leaf_indices is None else tuple(leaf_indices)
    if len(leaf_indices) != len(ports) or any(not 0 <= j < len(leaves) for j in leaf_indices):
        raise ValueError("Every port needs a valid controlling leaf")
    for j, ((operator, targets), leaf) in enumerate(zip(ports, leaf_indices)):
        if operator == "Y":
            # CY = S(control) CX(control,target) CZ(control,target), with
            # the rightmost operation first. These are physical locations.
            runtime.gate(f"{location}/couple/{j}/CZ", "CZ", leaves[leaf], *targets)
            runtime.gate(f"{location}/couple/{j}/CX", "CX", leaves[leaf], *targets)
            runtime.gate(f"{location}/couple/{j}/S", "S", leaves[leaf])
            continue
        gate = {"X": "CX", "Z": "CZ", "SWAP": "FREDKIN"}[operator]
        runtime.gate(f"{location}/couple/{j}", gate, leaves[leaf], *targets)
    reports = tuple(runtime.measure_x(f"{location}/readout/{j}", leaf)
                    for j, leaf in enumerate(leaves))
    parity = sum(reports) % 2
    runtime.log_check(location, reports, parity)
    runtime.check_gadgets_completed += 1
    return parity


def measure_repaired_cat(runtime, location, ports):
    """Section 3 of the new note, with either measured sign retained."""
    ports = tuple((axis, tuple(targets)) for axis, targets in ports)
    targets = [q for _, labels in ports for q in labels]
    if not ports or len(set(targets)) != len(targets):
        raise ValueError("Check ports must be nonempty and disjoint")
    if any(axis not in ("X", "Y", "Z", "SWAP") or len(labels) != (2 if axis == "SWAP" else 1)
           for axis, labels in ports):
        raise ValueError("A port is one X/Z target or one SWAP pair")
    if not set(targets) <= runtime.live:
        raise ValueError("A check targets absent qubits")
    leaves = prepare_repaired_cat(runtime, location, len(ports))
    return couple_and_read_cat(runtime, location, leaves, ports)


def matched_block_groups(ports):
    """Group B/C targets only within the same matched C4 label.

    Gauge and vertex targets remain individual, preserving the gauge-bit
    bound. A Gauss leaf may control its four SWAP ports in one matched block.
    """
    keys = []
    for _, targets in ports:
        data_blocks = {int(q.split("_")[1]) // 4 for q in targets if q.startswith(("B_", "C_"))}
        if len(data_blocks) == 1 and all(q.startswith(("B_", "C_")) for q in targets):
            keys.append(("data_block", next(iter(data_blocks))))
        else:
            keys.append(("individual", len(keys)))
    unique = list(dict.fromkeys(keys))
    return tuple(unique.index(key) for key in keys)


def protected_layout(ports, grouped):
    leaves = matched_block_groups(ports) if grouped else tuple(range(len(ports)))
    return leaves, max(leaves) + 1


def measure_grouped_protected_cat(runtime, location, ports, grouped=False):
    """Optimized protected extraction, with a proved two-zero-scan shortcut."""
    ports = tuple((axis, tuple(targets)) for axis, targets in ports)
    targets = [q for _, labels in ports for q in labels]
    if not ports or len(set(targets)) != len(targets) or not set(targets) <= runtime.live:
        raise ValueError("Protected ports must be disjoint, nonempty, and live")
    indices, size = protected_layout(ports, grouped)
    if size < len(ports):
        runtime.grouped_protected_checks += 1
    runtime.decision("protected_port_layout", location, leaf_for_port=indices,
                     leaves=size, zero_scan_target=2)
    leaves = prepare_repaired_cat(runtime, location, size, zero_scans=2)
    return couple_and_read_cat(runtime, location, leaves, ports, indices)


def source_flag_layout(ports):
    """At most four cat leaves, each assigned to ONE inner data block."""
    if not ports or any(axis not in ("X", "Z") or len(targets) != 1
                        or not targets[0].startswith(("B_", "C_")) for axis, targets in ports):
        raise ValueError("Flagged-source extraction is for data Pauli checks only")
    indices = matched_block_groups(ports)
    size = max(indices) + 1
    if size > 4 or len({axis for axis, _ in ports}) != 1:
        raise ValueError("The certified source shapes use one Pauli axis and at most four blocks")
    sizes = tuple(indices.count(j) for j in range(size))
    if (size, sizes) not in ((1, (4,)), (3, (2, 2, 2)), (4, (2, 2, 2, 2))):
        raise ValueError("This source shape is not covered by the finite locality certificate")
    return indices, size


def measure_flagged_source(runtime, location, ports):
    """Paper-style decoded block cat: 8 target + 6 flag CNOTs for weight 8.

    Flag failures are retried by rebuilding only this still-known source.
    This gadget is deliberately NOT used for the final recovery tail.
    """
    ports = tuple((axis, tuple(targets)) for axis, targets in ports)
    targets = [q for _, qs in ports for q in qs]
    if len(set(targets)) != len(targets) or not set(targets) <= runtime.live:
        raise ValueError("Source ports must be disjoint and live")
    indices, size = source_flag_layout(ports)
    leaves = tuple(f"L_{j}" for j in range(size))
    for j, leaf in enumerate(leaves):
        runtime.prepare(f"{location}/flag_cat/prepare/{j}", leaf)
    runtime.gate(location + "/flag_cat/H", "H", leaves[0])
    for j in range(1, size):
        runtime.gate(f"{location}/flag_cat/fanout/{j}", "CX", leaves[0], leaves[j])
    # Interleave the two positions of each block as in the paper's diagram.
    grouped_ports = [tuple(j for j, leaf in enumerate(indices) if leaf == k) for k in range(size)]
    for offset in range(max(map(len, grouped_ports))):
        for leaf, group in enumerate(grouped_ports):
            if offset < len(group):
                j = group[offset]
                axis, qs = ports[j]
                runtime.gate(f"{location}/couple/{j}", "CX" if axis == "X" else "CZ", leaves[leaf], *qs)
    for j in reversed(range(1, size)):
        runtime.gate(f"{location}/flag_cat/uncompute/{j}", "CX", leaves[0], leaves[j])
    flags = tuple(runtime.measure_z(f"{location}/flag/{j}", leaves[j]) for j in range(1, size))
    report = runtime.measure_x(location + "/syndrome", leaves[0])
    runtime.cats_prepared += 1
    runtime.check_gadgets_completed += 1
    runtime.flagged_source_checks += 1
    runtime.flag_bits_measured += len(flags)
    runtime.decision("source_flag_record", location, reported_syndrome=report, flags=flags,
                     leaf_for_port=indices, coupled_port_order=[j for i in range(max(map(len, grouped_ports)))
                     for group in grouped_ports if i < len(group) for j in (group[i],)])
    runtime.log_check(location, (report,), report)
    if any(flags):
        raise SourceFlag(location, flags, report)
    return report


def clean_check_cost(ports, stage, extraction):
    """Gate-count certificate for a clean check, independent of a state vector."""
    ports = tuple(ports)
    gates = Counter({"CX": sum(axis == "X" for axis, _ in ports),
                     "CZ": sum(axis == "Z" for axis, _ in ports),
                     "FREDKIN": sum(axis == "SWAP" for axis, _ in ports)})
    ys = sum(axis == "Y" for axis, _ in ports)
    if ys:
        gates.update(CX=ys, CZ=ys, S=ys)
    if extraction == "optimized" and stage == "source":
        _, m = source_flag_layout(ports)
        gates["CX"] += 2*(m - 1)
        scans, flags = 0, m - 1
    else:
        if extraction == "optimized":
            _, m = protected_layout(ports, stage == "gauged")
            scans = 2 if m > 1 else 0
        elif extraction == "verified_cat":
            m = len(ports)
            scans = 3 if m > 1 else 0
        else:
            raise ValueError("Unknown extraction profile")
        gates["CX"] += (m - 1)*(1 + 2*scans)
        flags = 0
    return {"gates": gates, "leaves": m, "cat_scans": scans, "flags": flags}
