"""Local Gauss votes with compression and conditional coordinate recovery."""

import c4_helix_single_block_cz as m
from run_single_block_cz_controller import Reject
from single_cz_compact_checks import compact_pauli_program
from single_cz_controller import SimulationController
from single_cz_direct_outer_pilot import DirectPilot, DressedFlag


def compact_root_program(ports, tree):
    protected = [(axis, q) for axis, q in ports if q.startswith("D") or int(q[1:]) in tree]
    protected_sites = {q for _, q in protected}
    chords = [q for _, q in ports if q not in protected_sites]
    assert len(protected) == 8
    labels = [q for _, q in protected] + ["s", "f0", "f1", "f2", "f3"]
    ops = []
    for op, qs in compact_pauli_program("X", 8):
        roles = tuple(labels[q] for q in qs)
        if op == "CX" and roles[1].startswith("D"):
            sign = m.SIGNS[int(roles[1][1:])]
            first, last = ("T", "TDG") if sign == 1 else ("TDG", "T")
            ops.extend([(first, roles[1:]), (op, roles), (last, roles[1:])])
        else:
            ops.append((op, roles))
    ops[-2:-2] = [("CX", ("s", chord)) for chord in chords]
    return ops


class ShortGaussPilot(DirectPilot):
    def __init__(self, backend, **options):
        super().__init__(backend, thin=True, first_vote=True, **options)
        self.in_recovery_frame = False

    def graph(self):
        vertices = [f"a{j}" for j in range(5)]
        edges = self.graph_choice.edges
        targets = [f"A{j}" for j in range(len(edges))]
        while True:
            self.context("graph/raw")
            for vertex in vertices:
                self.prep(vertex)
                self.gate("H", vertex)
            for edge, (u, v) in zip(targets, edges):
                self.prep(edge)
                self.gate("CX", vertices[u], edge)
                self.gate("CX", vertices[v], edge)
            self.b.boundary()
            records = []
            for r in range(2):
                self.context(f"graph/parity/{r}")
                bits = []
                for edge, (u, v) in zip(targets, edges):
                    self.prep("w")
                    for q in (vertices[u], edge, vertices[v]):
                        self.gate("CX", q, "w")
                    bits.append(self.mz("w"))
                records.append(bits)
                self.b.boundary()
                if any(bits):
                    break
            self.record.append({"graph_parity_records": records, "policy": "two_zero_scans"})
            if len(records) == 2 and not any(records[-1]):
                return
            self.dispose(vertices + targets)
            self.retry("known_unused_graph_parity")

    def check(self, name, ports):
        if name.endswith("/root_Gauss"):
            try:
                return self.direct_meter(name, compact_root_program(ports, self.graph_choice.tree))
            except DressedFlag as flag:
                raise Reject("compact_root_flag") from flag
        if name.startswith("terminal_screen/"):
            return super().check("compact/" + name, ports)
        return super().check(name, ports)

    def direct_reference(self, prefix, flagged):
        # Both a flag and a nonzero unflagged Z report charge at least one
        # pre-reference location under the short vote's triggering rule.
        assert flagged or prefix.endswith("/syndrome_recovery")
        SimulationController.coordinates(self)
        self.in_recovery_frame = True
        graph = self.graph_choice
        records = []
        self._flag_fallback = True
        try:
            for r in range(4):
                name = f"{prefix}/{r}"
                row = self.code(name + "/code") + self.cycle_reports(name + "/cycle")
                row += [self.check(f"{name}/star/{v}", [("X", f"A{e}") for e, uv in enumerate(graph.edges) if v in uv])
                        for v in range(1, 5)]
                records.append(row)
                if len(records) >= 2 and row == records[-2]:
                    self.record.append({"direct_reference": prefix, "records": records, "selected": row,
                                        "conditional_V_pair": True, "minimum_spent_faults": 1})
                    return row
        finally:
            self._flag_fallback = False
        raise Reject("unstable_short_vote_reference")

    def gauged_pauli(self, x, z):
        assert self.in_recovery_frame
        labels = [f"D{q}" for q in range(20)] + [f"A{e}" for e in range(len(self.graph_choice.edges))]
        self.pauli_correction(x, z, labels)
        SimulationController.coordinates(self)
        self.in_recovery_frame = False
