"""Executable report-driven controller; supply a physical/simulator backend.

This is NOT a new noisy simulator. Backend.measure_z returns the REPORTED bit.
The backend owns actual quantum evolution, true outcomes, noise and serial
single-qubit idles. All gate participant sets and retry branches are explicit.
Run --control-flow-check for deterministic record/control checks only.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import json

import c4_helix_single_block_cz as m


class Reject(Exception):
    pass


class Controller:
    def __init__(self, backend, route="gauging"):
        if route not in ("gauging", "direct_cat"):
            raise ValueError(route)
        self.b, self.route = backend, route
        self.live = set()
        self.retries = 0
        self.record = []

    def prep(self, q):
        assert q not in self.live
        self.b.prepare(q)
        self.live.add(q)

    def gate(self, gate, *qs):
        assert set(qs) <= self.live
        self.b.gate(gate, *qs)

    def mz(self, q):
        assert q in self.live
        bit = self.b.measure_z(q)
        assert bit in (0, 1)
        self.live.remove(q)
        return int(bit)

    def dispose(self, qs):
        for q in qs:
            if q in self.live:
                self.mz(q)

    def retry(self, reason):
        if self.retries == 2:
            raise Reject("shared_retry_limit:"+reason)
        self.retries += 1
        self.record.append({"retry": reason, "tokens_used": self.retries})

    def cw(self, control, q):
        sign = m.SIGNS[q]
        self.gate("T" if sign == 1 else "TDG", f"D{q}")
        self.gate("CX", control, f"D{q}")
        self.gate("TDG" if sign == 1 else "T", f"D{q}")

    def coordinates(self):
        for v in range(1, 5):
            for q in range(4*v, 4*v+4):
                self.cw(f"A{v-1}", q)

    def cat(self, size, name):
        leaves = [f"L{j}" for j in range(size)]
        while True:
            for leaf in leaves:
                self.prep(leaf)
            self.gate("H", leaves[0])
            for j in range(size-1):
                self.gate("CX", leaves[j], leaves[j+1])
            flags = []
            for scan in range(3):
                row = []
                for j in range(size-1):
                    self.prep("w")
                    self.gate("CX", leaves[j], "w")
                    self.gate("CX", leaves[j+1], "w")
                    row.append(self.mz("w"))
                flags.append(row)
            self.record.append({"cat": name, "flags": flags})
            if not any(any(row) for row in flags):
                return leaves
            self.dispose(leaves)  # never coupled this cat to the data
            self.retry("unused_cat:"+name)

    def check(self, name, ports):
        self.b.context = name
        assert len({q for axis, q in ports}) == len(ports)
        leaves = self.cat(len(ports), name)
        for leaf, (axis, target) in zip(leaves, ports):
            if axis == "W":
                self.cw(leaf, int(target[1:]))
            else:
                if axis == "Z":
                    self.gate("H", target)
                self.gate("CX", leaf, target)
                if axis == "Z":
                    self.gate("H", target)
        bits = []
        for leaf in leaves:
            self.gate("H", leaf)
            bits.append(self.mz(leaf))
        bit = sum(bits) % 2
        self.record.append({"check": name, "leaf_reports": bits, "reported_parity": bit})
        return bit

    def family(self, prefix, family):
        return [self.check(f"{prefix}/{j}", ports) for j, ports in enumerate(family)]

    def code(self, prefix, source=False, require_zero=False):
        reports = []
        for axis in "ZX":
            bits = self.family(prefix+"/"+axis,
                               [[(axis, f"D{q}") for q in r] for r in m.SUPPORTS])
            reports += bits
            if require_zero and any(bits):
                raise Reject(prefix+"/nonzero_"+axis)
        if source:
            reports += self.family(prefix+"/logical_X",
                                   [[("X", f"D{q}") for q in r] for r in (m.X0, m.X1)])
        return reports

    def source(self):
        while True:
            for q in range(20):
                self.prep(f"D{q}")
            pivots, gates = m.rref_encoder()
            for q in pivots:
                self.gate("H", f"D{q}")
            for c, t in gates:
                self.gate("CX", f"D{c}", f"D{t}")
            self.b.boundary()
            bits = self.code("source/acquire", source=True)
            x, z = m.source_correction(bits)
            for q in range(20):
                p = ((x >> q) & 1) | (((z >> q) & 1) << 1)
                if p:
                    self.gate({1: "X", 2: "Z", 3: "Y"}[p], f"D{q}")
            self.b.boundary()
            failed = False
            for r in range(3):
                failed = any(self.code(f"source/verify/{r}", source=True))
                self.b.boundary()
                if failed:
                    break
            if not failed:
                return
            self.dispose([f"D{q}" for q in range(20)])
            self.retry("known_data_source")

    def graph(self):
        self.prepare_parity_verified_graph(m.EDGES)

    def prepare_parity_verified_graph(self, edges):
        """Verify only Z_u Z_e Z_v, using resource-to-meter CNOTs.

        Three complete all-zero scans supply a clean cut-subspace reference
        under the GLOBAL two-fault bound. Graph phases remain unrestricted;
        later combined Gauss rounds certify the logical sector. A nonzero
        scan rebuilds only this unused resource, sharing the retry budget.
        """
        roles = [f"a{v}" for v in range(5)]+[f"A{e}" for e in range(len(edges))]
        attempt = 0
        while True:
            self.b.context = f"graph/raw/{attempt}"
            for v in range(5):
                self.prep(f"a{v}")
                self.gate("H", f"a{v}")
            for e in range(len(edges)):
                self.prep(f"A{e}")
            for e, (u, v) in enumerate(edges):
                self.gate("CX", f"a{u}", f"A{e}")
                self.gate("CX", f"a{v}", f"A{e}")
            self.b.boundary()
            failed = False
            records = []
            for r in range(3):
                row = []
                for e, (u, v) in enumerate(edges):
                    self.b.context = f"graph/parity/{attempt}/{r}/{e}"
                    self.prep("w")
                    for target in (f"a{u}", f"A{e}", f"a{v}"):
                        self.gate("CX", target, "w")
                    row.append(self.mz("w"))
                records.append(row)
                failed = any(row)
                self.b.boundary()
                if failed:
                    break
            self.record.append({"graph_parity_verification":attempt,
                                "policy":"three_zero_Z_edge_scans", "records":records,
                                "accepted":not failed})
            if not failed:
                return
            self.b.context = f"graph/dispose/{attempt}"
            self.dispose(roles)
            self.retry("known_unused_graph_parity")
            attempt += 1

    def gauging(self):
        self.graph()
        for q in range(20):
            self.cw(f"a{q//4}", q)
        b = []
        for v in range(5):
            self.gate("H", f"a{v}")
            b.append(self.mz(f"a{v}"))
        self.record.append({"vertex_reports": b})
        if sum(b) % 2:
            raise Reject("reported_negative_vertex_parity")
        for v in range(1, 5):
            if b[v]:
                self.gate("Z", f"A{v-1}")
        self.b.boundary()
        for r in range(3):
            self.coordinates()
            self.code(f"gauged/{r}/code", require_zero=True)
            cycles = self.family(f"gauged/{r}/cycle", [[("Z", f"A{e}") for e in c] for c in m.CYCLES])
            if any(cycles):
                raise Reject("nonzero_cycle")
            for v in range(1, 5):
                bit = self.check(f"gauged/{r}/star/{v}",
                                 [("X", f"A{e}") for e, ends in enumerate(m.EDGES) if v in ends])
                if bit:
                    self.gate("Z", f"A{v-1}")
            self.coordinates()
            root = self.check(f"gauged/{r}/root_Gauss", [("W", f"D{q}") for q in range(4)] +
                              [("X", f"A{e}") for e, ends in enumerate(m.EDGES) if 0 in ends])
            if root:
                raise Reject("negative_root_Gauss")
            self.b.boundary()
        word = sum(self.mz(f"A{e}") << e for e in range(13))
        decoded = m.decode_edges(word)
        self.record.append({"edge_reports": word, "decoded": decoded})
        if decoded is None:
            raise Reject("edge_cut_ambiguity_or_outside_radius")
        for v in range(1, 5):
            if decoded["eta"] >> v & 1:
                for q in range(4*v, 4*v+4):
                    self.gate("S" if m.SIGNS[q] == 1 else "SDG", f"D{q}")
                    self.gate("X", f"D{q}")
        self.b.boundary()

    def run(self):
        try:
            self.source()
            if self.route == "gauging":
                self.gauging()
            for r in range(3):
                self.code(f"terminal/{r}", require_zero=True)
                if self.route == "direct_cat":
                    if self.check(f"terminal/{r}/U", [("W", f"D{q}") for q in range(20)]):
                        raise Reject("direct_cat_negative_U")
                self.b.boundary()
        except Reject as exc:
            self.dispose(sorted(self.live))
            return {"accepted": False, "reason": str(exc), "retries": self.retries, "record": self.record}
        assert self.live == {f"D{q}" for q in range(20)}
        return {"accepted": True, "retries": self.retries, "record": self.record,
                "output_roles": sorted(self.live)}


class RecordBackend:
    """Deterministic controller check only; no amplitudes or quantum proof here."""
    def __init__(self, reports=None, overrides=None, context_reports=None):
        self.ops, self.reports, self.live = [], reports or {}, set()
        self.contexts = []
        self.overrides = overrides or {}
        self.context_reports, self.context = context_reports or {}, "initial"
        self.measure_count = Counter()

    def prepare(self, q):
        self.contexts.append(self.context)
        self.ops.append(("PREP", (q,)))
        self.live.add(q)

    def gate(self, name, *qs):
        self.contexts.append(self.context)
        self.ops.append((name, qs))

    def measure_z(self, q):
        self.contexts.append(self.context)
        self.ops.append(("MZ", (q,)))
        self.live.remove(q)
        n = self.measure_count[q]
        self.measure_count[q] += 1
        return self.context_reports.get((self.context,q),
                                       self.overrides.get((q, n), self.reports.get(q, 0)))

    def boundary(self):
        self.contexts.append(self.context)
        self.ops.append(("BOUNDARY", ()))


def control_flow_check():
    results = []
    for route in ("gauging", "direct_cat"):
        backend = RecordBackend()
        result = Controller(backend, route).run()
        assert result["accepted"]
        expected = [(op.name, op.qubits) for op in m.build(route).ops]
        assert backend.ops == expected
        results.append({"route": route, "zero_record_gate_list_matches_builder": True,
                        "physical_operations_and_boundaries": len(expected)})
    backend = RecordBackend(overrides={("w", 0): 1})
    result = Controller(backend).run()
    assert result["accepted"] and result["retries"] == 1
    # A genuine-negative report takes the early exit and removes every role.
    backend = RecordBackend(reports={"a0": 1})
    result = Controller(backend).run()
    assert not result["accepted"] and not backend.live
    # Two edge report flips, corrected to the all-zero cut, do not select W.
    backend = RecordBackend(reports={"A0": 1, "A4": 1})
    result = Controller(backend).run()
    assert result["accepted"]
    assert next(r["decoded"] for r in result["record"] if "decoded" in r)["eta"] == 0
    # Known-source X(D0) syndrome and its explicitly chosen correction.
    backend = RecordBackend(overrides={("L0", 0): 1, ("L0", 5): 1})
    result = Controller(backend).run()
    bits = [1, 0, 0, 0, 0, 1, 0, 0, 0]+[0]*11
    assert result["accepted"]
    assert backend.ops == [(op.name, op.qubits) for op in m.build(source_bits=bits).ops]
    # Nonzero vertex frame and nonzero decoded byproduct on the same path.
    reports = {"a1": 1, "a2": 1}
    reports.update({f"A{e}": 1 for e in range(13) if m.cut(2) >> e & 1})
    backend = RecordBackend(reports=reports)
    result = Controller(backend).run()
    assert result["accepted"]
    assert backend.ops == [(op.name, op.qubits) for op in m.build(eta=2, vertex_word=6).ops]
    # Exact graph-phase evolution for the two-report-fault history in the note.
    phase, b_history, root_history = 0, [], []
    for r in range(3):
        for v in range(1, 5):
            reported = ((phase >> v) & 1) ^ int(r == 0 and v == 1)
            if v == 1:
                b_history.append(reported)
            if reported:
                phase ^= 1 | (1 << v)  # Z(A_av) flips exactly G_a and G_v
        root_history.append((phase & 1) ^ int(r == 0))
        assert root_history[-1] == 0 and phase.bit_count() % 2 == 0
    assert phase == 0 and b_history == [1, 1, 0]
    backend = RecordBackend(context_reports={("gauged/0/star/1","L0"):1,
                                            ("gauged/1/star/1","L0"):1})
    result = Controller(backend).run()
    assert result["accepted"] and backend.ops.count(("Z", ("A0",))) == 2
    actual_history = [r["reported_parity"] for r in result["record"]
                      if r.get("check", "").endswith("/star/1")]
    assert actual_history == b_history
    return {"scope": "classical record/control flow only; not a quantum simulation",
            "results": results, "unused_cat_flag_retry": True, "negative_report_rejection": True,
            "two_edge_report_flips": True, "nonzero_known_source_correction": True,
            "nonzero_vertex_and_edge_feedback_matches_builder": True,
            "two_report_fault_graph_phase_history": {"b_star_reports": b_history,
                                                     "root_reports": root_history}}


def ideal_cost():
    result = {}
    for route in ("gauging", "direct_cat"):
        # An odd vertex word, or a negative first direct U measurement.
        backend = (RecordBackend(reports={"a0": 1}) if route == "gauging" else
                   RecordBackend(overrides={("L0", 98): 1}))
        outcome = Controller(backend, route).run()
        assert not outcome["accepted"]
        p = m.Program()
        p.ops = [m.Op("negative_prefix_and_disposal", name, qs) for name, qs in backend.ops]
        negative = m.count_program(p, expect_output=False)
        positive = m.count_program(m.build(route))
        pc = dict(positive["gates"])
        if route == "gauging":
            # Uniform even vertex words and uniform root-zero cuts.
            pc["Z"] = 2
            pc["S_or_SDG"] = 8
            pc["X"] = 8
            pc["IDLE"] += 2*32 + 16*19
        nc = negative["gates"]
        expected = {g: str(Fraction(pc.get(g, 0)) + Fraction(nc.get(g, 0), 3))
                    for g in sorted(set(pc) | set(nc))}
        result[route] = {"negative_attempt_including_disposal": negative,
                         "expected_per_ideal_accepted_output": expected}
    return {"scope": "Exact zero-noise repeat-until-success accounting, not noisy matched-fidelity data",
            "ideal_probability": "3/4", "formula": "C_positive_mean + C_negative/3", "routes": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-flow-check", action="store_true", required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] /
                        "output/single-block-cz/controller.json")
    args = parser.parse_args()
    result = control_flow_check()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    (args.output.parent / "ideal-cost.json").write_text(json.dumps(ideal_cost(), indent=2)+"\n")
    print(json.dumps(result, indent=2))
