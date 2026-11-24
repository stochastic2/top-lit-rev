"""Additive physical schedule for the conservative one-block CZ factory.

No Guppy/legacy simulator imports. All controlled W gates are three locations.
This module generates gate lists and accounting, not noisy quantum trajectories.
See notes/full_procedure_single_block_cz.md for the report-driven controller.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
SUPPORTS = (
    (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11),
    (12, 13, 14, 15), (16, 17, 18, 19),
    (0, 3, 6, 7, 10, 11, 12, 15),
    (4, 7, 8, 9, 14, 15, 16, 19),
    (1, 2, 8, 11, 12, 13, 18, 19),
    (2, 3, 5, 6, 13, 14, 16, 17),
)
X0 = (2, 3, 8, 11, 12, 15)
X1 = (0, 3, 6, 7, 18, 19)
Z0, Z1 = X1, X0
SIGNS = tuple((-1, 1, 1, -1)[q % 4] * (-1 if q in X0 else 1)
              for q in range(20))
EDGES = tuple(combinations(range(5), 2)) + ((0, 1), (2, 3), (0, 4))
CYCLES = ((0, 1, 4), (0, 2, 5), (0, 3, 6),
          (1, 2, 7), (1, 3, 8), (2, 3, 9),
          (0, 10), (1, 2, 11), (3, 12))
TREE = (0, 1, 2, 3)


def mask(support):
    return sum(1 << q for q in support)


def cut(t):
    return sum((((t >> u) ^ (t >> v)) & 1) << e for e, (u, v) in enumerate(EDGES))


def decode_edges(word):
    """Unique radius-two cut; root a=0. All other records reject."""
    candidates = [(eta, cut(eta)) for eta in range(0, 32, 2)
                  if (word ^ cut(eta)).bit_count() <= 2]
    if len(candidates) != 1:
        return None
    eta, corrected = candidates[0]
    return {"eta": eta, "corrected": corrected, "report_error": word ^ corrected}


def rref_encoder():
    rows = [mask(r) for r in SUPPORTS + (X0, X1)]
    pivots = []
    for q in range(20):
        k = len(pivots)
        selected = next((i for i in range(k, len(rows)) if rows[i] >> q & 1), None)
        if selected is None:
            continue
        rows[k], rows[selected] = rows[selected], rows[k]
        for i in range(len(rows)):
            if i != k and rows[i] >> q & 1:
                rows[i] ^= rows[k]
        pivots.append(q)
    assert len(pivots) == 11
    return pivots, [(p, q) for p, row in zip(pivots, rows)
                    for q in range(20) if q != p and row >> q & 1]


def source_generators():
    return tuple((0, mask(r)) for r in SUPPORTS) + tuple(
        (mask(r), 0) for r in SUPPORTS + (X0, X1))


def source_correction(bits):
    """Linear right inverse of the 20-check syndrome; physical Pauli masks.

    Only for the known source before enrichment. Never called on magic data.
    """
    if len(bits) != 20 or any(b not in (0, 1) for b in bits):
        raise ValueError("Twenty binary source reports required")
    rows = [(z | (x << 20), int(b)) for (x, z), b in zip(source_generators(), bits)]
    pivots = []
    for col in range(40):
        i = len(pivots)
        found = next((j for j in range(i, 20) if rows[j][0] >> col & 1), None)
        if found is None:
            continue
        rows[i], rows[found] = rows[found], rows[i]
        for j in range(20):
            if j != i and rows[j][0] >> col & 1:
                rows[j] = (rows[j][0] ^ rows[i][0], rows[j][1] ^ rows[i][1])
        pivots.append(col)
        if len(pivots) == 20:
            break
    assert len(pivots) == 20
    result = sum(b << p for p, (_, b) in zip(pivots, rows))
    return result & ((1 << 20) - 1), result >> 20


@dataclass(frozen=True)
class Op:
    stage: str
    name: str
    qubits: tuple[str, ...]


class Program:
    def __init__(self):
        self.ops = []
        self.stage = ""

    def op(self, name, *qubits):
        self.ops.append(Op(self.stage, name, tuple(qubits)))

    def boundary(self):
        # Expanded as one IDLE location for every currently live qubit.
        self.op("BOUNDARY")

    def cw(self, control, q):
        sign = SIGNS[q]
        self.op("T" if sign == 1 else "TDG", f"D{q}")
        self.op("CX", control, f"D{q}")
        self.op("TDG" if sign == 1 else "T", f"D{q}")

    def coordinates(self):
        for v in range(1, 5):
            for q in range(4*v, 4*v+4):
                self.cw(f"A{v-1}", q)

    def cat_prepare(self, size):
        leaves = [f"L{j}" for j in range(size)]
        for leaf in leaves:
            self.op("PREP", leaf)
        self.op("H", leaves[0])
        for j in range(size - 1):
            self.op("CX", leaves[j], leaves[j+1])
        for scan in range(3):
            for j in range(size - 1):
                self.op("PREP", "w")
                self.op("CX", leaves[j], "w")
                self.op("CX", leaves[j+1], "w")
                self.op("MZ", "w")
        return leaves

    def check(self, axis, targets):
        self.check_ports([(axis, target) for target in targets])

    def check_ports(self, ports):
        targets = [target for axis, target in ports]
        leaves = self.cat_prepare(len(targets))
        for leaf, (axis, target) in zip(leaves, ports):
            if axis == "W":
                self.cw(leaf, int(target[1:]))
            else:
                if axis == "Z":
                    self.op("H", target)
                self.op("CX", leaf, target)
                if axis == "Z":
                    self.op("H", target)
        for leaf in leaves:
            self.op("H", leaf)
            self.op("MZ", leaf)

    def code_checks(self, source=False):
        for axis in "ZX":
            for r in SUPPORTS:
                self.check(axis, [f"D{q}" for q in r])
        if source:
            for r in (X0, X1):
                self.check("X", [f"D{q}" for q in r])


def build(route="gauging", eta=0, vertex_word=0, source_bits=None, gauss_bits=None):
    """One complete path with successful cats/resources and given feedback.

    Verification/terminal reports must be zero to accept, except four graph
    stars per gauged round (gauss_bits). No ideal projectors hide gates here.
    Failed unused-cat/source retries are specified in the note and bounded in
    accounting(), rather than included in this clean successful path.
    """
    if route not in ("gauging", "direct_cat"):
        raise ValueError(route)
    if eta & 1 or not 0 <= eta < 32 or not 0 <= vertex_word < 32:
        raise ValueError("Use root-zero eta and five vertex bits")
    if vertex_word.bit_count() % 2:
        raise ValueError("This builder emits accepted paths only")
    p = Program()
    p.stage = "source_raw"
    for q in range(20):
        p.op("PREP", f"D{q}")
    pivots, cx = rref_encoder()
    for q in pivots:
        p.op("H", f"D{q}")
    for c, t in cx:
        p.op("CX", f"D{c}", f"D{t}")
    p.boundary()
    p.stage = "source_acquire"
    p.code_checks(source=True)
    x, z = source_correction(source_bits or [0]*20)
    for q in range(20):
        word = ((x >> q) & 1) | (((z >> q) & 1) << 1)
        if word:
            p.op({1: "X", 2: "Z", 3: "Y"}[word], f"D{q}")
    p.boundary()
    for r in range(3):
        p.stage = f"source_verify_{r}"
        p.code_checks(source=True)
        p.boundary()
    if route == "gauging":
        p.stage = "graph_raw"
        for v in range(5):
            p.op("PREP", f"a{v}")
            p.op("H", f"a{v}")
        for e in range(13):
            p.op("PREP", f"A{e}")
        for e, (u, v) in enumerate(EDGES):
            p.op("CX", f"a{u}", f"A{e}")
            p.op("CX", f"a{v}", f"A{e}")
        p.boundary()
        for r in range(3):
            p.stage = f"graph_verify_{r}"
            for e, (u, v) in enumerate(EDGES):
                p.op("PREP", "w")
                for target in (f"a{u}", f"A{e}", f"a{v}"):
                    p.op("CX", target, "w")
                p.op("MZ", "w")
            p.boundary()
        p.stage = "enrich_and_vertex"
        for q in range(20):
            p.cw(f"a{q//4}", q)
        for v in range(5):
            p.op("H", f"a{v}")
            p.op("MZ", f"a{v}")
        for v in range(1, 5):
            if vertex_word >> v & 1:
                p.op("Z", f"A{v-1}")
        p.boundary()
        for r in range(3):
            p.stage = f"gauged_verify_{r}"
            p.coordinates()
            p.code_checks()
            for cycle in CYCLES:
                p.check("Z", [f"A{e}" for e in cycle])
            for v in range(1, 5):
                p.check("X", [f"A{e}" for e, ends in enumerate(EDGES) if v in ends])
                if gauss_bits and gauss_bits[r][v-1]:
                    p.op("Z", f"A{v-1}")
            p.coordinates()
            # Root Gauss check in the actual gauged frame, with one leaf per
            # data/edge port. Under V this is U times the a-star. It is NOT a
            # separate global direct-cat CZ measurement on twenty data qubits.
            p.check_ports([("W", f"D{q}") for q in range(4)] +
                          [("X", f"A{e}") for e, ends in enumerate(EDGES) if 0 in ends])
            p.boundary()
        p.stage = "edge_readout_and_byproduct"
        for e in range(13):
            p.op("MZ", f"A{e}")
        for v in range(1, 5):
            if eta >> v & 1:
                for q in range(4*v, 4*v+4):
                    # Equals W'_q up to e^(+i s_q pi/4). The product is a
                    # known record-global phase, never a controlled phase.
                    p.op("S" if SIGNS[q] == 1 else "SDG", f"D{q}")
                    p.op("X", f"D{q}")
        p.boundary()
    for r in range(3):
        p.stage = f"terminal_{r}"
        p.code_checks()
        if route == "direct_cat":
            p.check("W", [f"D{q}" for q in range(20)])
        p.boundary()
    return p


def count_program(program, expect_output=True):
    live = set()
    counts, stages = Counter(), defaultdict(Counter)
    free, allocation, next_slot = [], {}, 0
    peak = resets = 0
    for op in program.ops:
        if op.name == "BOUNDARY":
            counts["IDLE"] += len(live)
            stages[op.stage]["IDLE"] += len(live)
            continue
        qs = set(op.qubits)
        if op.name == "PREP":
            assert not qs & live
            if free:
                slot = min(free)
                free.remove(slot)
                resets += 1
            else:
                slot, next_slot = next_slot, next_slot + 1
            allocation[op.qubits[0]] = slot
            live |= qs
        else:
            assert qs <= live, (op, live)
        counts["IDLE"] += len(live - qs)
        stages[op.stage]["IDLE"] += len(live - qs)
        counts[op.name] += 1
        stages[op.stage][op.name] += 1
        peak = max(peak, len(live))
        if op.name == "MZ":
            live -= qs
            free.append(allocation.pop(op.qubits[0]))
    assert live == ({f"D{q}" for q in range(20)} if expect_output else set())
    return {"gates": dict(counts), "stages": {k: dict(v) for k, v in stages.items()},
            "peak_live": peak, "allocated_physical_slots": next_slot,
            "reinitializations_after_first_use": resets,
            "T_or_TDG": counts["T"] + counts["TDG"],
            "one_qubit_Clifford": sum(counts[g] for g in ("H", "S", "SDG", "X", "Y", "Z")),
            "atomic_multiqubit_gates": 0}


def accounting():
    result = {route: count_program(build(route)) for route in ("gauging", "direct_cat")}
    result["clean_feedback"] = {
        "gauging": {"vertex_Z_min_mean_max": [0, 2, 4],
                    "byproduct_Clifford_min_mean_max": [0, 16, 32],
                    "source_correction": 0, "graph_phase_repairs": 0},
        "fault_path_additions": {"source_correction_gates_per_source_attempt_at_most": 20,
                                 "gauged_graph_phase_Z_at_most": 12,
                                 "shared_local_retry_tokens": 2,
                                 "attempts_per_local_resource_at_most": 3},
    }
    # Uniform, deliberately loose bounded-path operation ceiling: at most two
    # retries, each bounded by a full source attempt plus disposal. Extra idle
    # ceiling follows from 44 (or 41) live qubits per elementary operation.
    for route in ("gauging", "direct_cat"):
        counts = result[route]["gates"]
        source = Counter()
        for stage, costs in result[route]["stages"].items():
            if stage.startswith("source"):
                source.update(costs)
        bound = Counter(counts)
        for _ in range(2):
            bound.update({k: v for k, v in source.items() if k != "IDLE"})
            bound["MZ"] += 20  # discard a failed known data source
        # Each axis separately bounded by 60; their sum is a deliberately
        # loose envelope, not a claim that 180 corrections can be executed.
        for axis in ("X", "Y", "Z"):
            bound[axis] += 60
        if route == "gauging":
            bound["Z"] += 16  # four vertex-frame and twelve phase repairs
            bound["S"] += 16  # each sign bounded separately (loose envelope)
            bound["SDG"] += 16
            bound["X"] += 16
        events = sum(v for k, v in bound.items() if k != "IDLE")
        bound["IDLE"] = result[route]["peak_live"] * (events + 32)
        result[route]["bounded_path_upper_envelope"] = dict(bound)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/single-block-cz/resources.json")
    parser.add_argument("--schedule", type=Path)
    parser.add_argument("--route", choices=("gauging", "direct_cat"), default="gauging")
    parser.add_argument("--eta", type=int, default=0)
    parser.add_argument("--vertex-word", type=int, default=0)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(accounting(), indent=2) + "\n")
    if args.schedule:
        args.schedule.parent.mkdir(parents=True, exist_ok=True)
        args.schedule.write_text(json.dumps([asdict(o) for o in build(
            args.route, args.eta, args.vertex_word).ops], indent=2) + "\n")
    print(json.dumps({k: {j: v for j, v in row.items() if j not in ("stages", "bounded_path_upper_envelope")}
                      for k, row in accounting().items()}, indent=2))


if __name__ == "__main__":
    main()
