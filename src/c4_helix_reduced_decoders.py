"""Report-only decoders for full_procedure_reduced_rejection.md.

No quantum state, actual measurement outcome, or fault oracle enters these
decoders. In particular the joint lookup covers two whole matched blocks,
not merely two physical qubits. This module contains no noise model.
"""

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product

from c4_helix_noiseless import CHECK_SUPPORTS, EDGES, TREE_EDGES
from c4_helix_fault_runtime import RejectAttempt
from simulate_c4_helix_gadgets import CYCLE_SUPPORTS


class ReducedRejection(RejectAttempt):
    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def bits(values, length):
    values = tuple(values)
    if len(values) != length or any(type(b) not in (int, bool) or b not in (0, 1) for b in values):
        raise ValueError(f"Expected {length} binary reported bits")
    return tuple(int(b) for b in values)


def mask(positions):
    return sum(1 << q for q in positions)


def word(values):
    return sum(b << q for q, b in enumerate(values))


def binary_basis(rows):
    result = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in result:
                row ^= result[pivot]
            else:
                result[pivot] = row
                break
    return tuple(sorted(result.items(), reverse=True))


H = tuple(map(mask, CHECK_SUPPORTS))
STABILIZERS = binary_basis(H)


def remainder(v):
    for pivot, row in STABILIZERS:
        if v >> pivot & 1:
            v ^= row
    return v


@lru_cache(maxsize=None)
def component_syndrome(v):
    return word((v & h).bit_count() % 2 for h in H)


def pauli_syndrome(error):
    x, z = error
    return component_syndrome(z) | (component_syndrome(x) << 9)


def pauli_coset(error):
    return tuple(remainder(v) for v in error)


def pauli_axes(error, n):
    x, z = error
    return tuple("IXZY"[((x >> q) & 1) | (((z >> q) & 1) << 1)] for q in range(n))


@dataclass(frozen=True)
class GaugeGraph:
    name: str
    edges: tuple
    cycles: tuple
    tree_edges: tuple

    def cut(self, offsets):
        return tuple(offsets[u] ^ offsets[v] for u, v in self.edges)

    def validate(self):
        if any(not (0 <= u < v < 5) for u, v in self.edges):
            raise ValueError("Gauge edges must join distinct vertices a through e")
        if len(self.tree_edges) != 4 or any(
                not 0 <= q < len(self.edges) or self.edges[q] != (0, v)
                for v, q in enumerate(self.tree_edges, 1)):
            raise ValueError("The root tree must use ab, ac, ad, ae, in that order")
        if any(not cycle or len(set(cycle)) != len(cycle)
               or any(not 0 <= q < len(self.edges) for q in cycle) for cycle in self.cycles):
            raise ValueError("Invalid cycle support")
        cycle_masks = tuple(map(mask, self.cycles))
        if len(self.cycles) != len(self.edges) - 4 or len(binary_basis(cycle_masks)) != len(self.cycles):
            raise ValueError("An independent, complete cycle basis is required")
        cuts = {word(self.cut((0,) + t)) for t in product((0, 1), repeat=4)}
        if len(cuts) != 16 or min(c.bit_count() for c in cuts if c) < 5:
            raise ValueError("Cut distance must allow unique correction of two edge errors")
        if any((c & h).bit_count() % 2 for c in cuts for h in cycle_masks):
            raise ValueError("A cycle constraint fails on a valid cut")


CURRENT_GRAPH = GaugeGraph("current20", EDGES, CYCLE_SUPPORTS, TREE_EDGES)
COMPACT_GRAPH = GaugeGraph(
    "compact13", tuple(combinations(range(5), 2)) + ((0, 1), (2, 3), (0, 4)),
    ((0, 1, 4), (0, 2, 5), (0, 3, 6), (1, 2, 7), (1, 3, 8), (2, 3, 9),
     (0, 10), (1, 2, 11), (3, 12)), (0, 1, 2, 3))
GRAPHS = {g.name: g for g in (CURRENT_GRAPH, COMPACT_GRAPH)}


class StableRecord:
    """First identical triple, at most nine COMPLETE records, no corrections."""

    max_rounds = 9
    policy = "triple"

    def __init__(self, length, location):
        self.length, self.location = length, location
        self.records = []
        self.common = None

    def add(self, report):
        if self.common is not None or len(self.records) >= 9:
            raise ValueError("This complete-record measurement has already stopped")
        report = bits(report, self.length)
        self.records.append(report)
        if len(self.records) >= 3 and self.records[-3:] == [report] * 3:
            self.common = report
            return report
        if len(self.records) == 9:
            raise ReducedRejection("unstable_record", f"No identical triple by round nine at {self.location}",
                                   {"location": self.location, "records": self.records})
        return None


HISTORY_POLICIES = ("adaptive", "triple")


def clean_reference_certificate(records):
    """Certify a whole record using only reported changes and a two-fault bound.

    Changed adjacent records require a bad round at one of their endpoints.
    Enumerate ALL compatible bad-round sets of size <=2. A record is usable
    iff none of those sets contains all its occurrences. Prefer the most
    recent usable record. No actual faults, syndrome bits individually, or
    assumed clean round are consulted. Intended for prefixes of length <=5.
    """
    records = tuple(tuple(r) for r in records)
    if not 1 <= len(records) <= 5:
        raise ValueError("Adaptive reference certificates require one to five complete records")
    edges = tuple(i for i in range(len(records)-1) if records[i] != records[i+1])
    covers = [frozenset(c) for w in range(3) for c in combinations(range(len(records)), w)
              if all(i in c or i+1 in c for i in edges)]
    if not covers:
        return None
    for candidate in dict.fromkeys(reversed(records)):
        occurrences = frozenset(i for i, report in enumerate(records) if report == candidate)
        if any(occurrences <= bad for bad in covers):
            continue
        # This minimum also makes the certificate readable: declaring every
        # occurrence bad would require at least three faulty rounds.
        minimum = next(w for w in range(len(occurrences), len(records)+1)
                       if any(occurrences <= set(c) and all(i in c or i+1 in c for i in edges)
                              for c in combinations(range(len(records)), w)))
        return {"fault_budget": 2, "round_index_convention": "zero_based",
                "change_edges": [[i, i+1] for i in edges],
                "compatible_bad_round_sets": [sorted(c) for c in covers],
                "selected_occurrences": sorted(occurrences),
                "selected_record_index": max(occurrences),
                "min_faulty_rounds_if_all_occurrences_bad": minimum}
    return None


class AdaptiveRecord:
    """First certified whole record; at most five rounds, no corrections."""

    max_rounds = 5
    policy = "adaptive"

    def __init__(self, length, location):
        self.length, self.location = length, location
        self.records = []
        self.common = None
        self.certificate = None

    def add(self, report):
        if self.common is not None or len(self.records) >= self.max_rounds:
            raise ValueError("This complete-record measurement has already stopped")
        self.records.append(bits(report, self.length))
        self.certificate = clean_reference_certificate(self.records)
        if self.certificate is not None:
            self.common = self.records[self.certificate["selected_record_index"]]
            return self.common
        if len(self.records) == self.max_rounds:
            raise ArithmeticError("The five-round clean-reference lemma failed")
        return None


def record_history(length, location, policy):
    if policy not in HISTORY_POLICIES:
        raise ValueError("History policy is adaptive or triple")
    return (AdaptiveRecord if policy == "adaptive" else StableRecord)(length, location)


def history_metadata(history):
    result = {"history_policy": history.policy}
    if history.policy == "adaptive" and history.certificate is not None:
        result["reference_certificate"] = history.certificate
    return result


def cat_repair_pattern(report):
    report = bits(report, len(report))
    r = [0]
    for d in report:
        r.append(r[-1] ^ d)
    return tuple(r)


class KnownStateDecoder:
    """GF(2) sign corrections for n independent commuting checks on n qubits."""

    def __init__(self, labels, family):
        self.labels = tuple(labels)
        if len(set(self.labels)) != len(self.labels) or len(family) != len(self.labels):
            raise ValueError("Known-state checks must specify one complete n-qubit stabilizer state")
        generators = []
        for _, ports in family:
            x = z = 0
            for axis, targets in ports:
                if axis not in ("X", "Z") or len(targets) != 1:
                    raise ValueError("Known-state extraction uses only single-qubit X or Z ports")
                q = self.labels.index(targets[0])
                if axis == "X":
                    x ^= 1 << q
                else:
                    z ^= 1 << q
            generators.append((x, z))
        self.generators = tuple(generators)
        if any(((x & zz).bit_count() + (z & xx).bit_count()) % 2
               for (x, z), (xx, zz) in combinations(generators, 2)):
            raise ValueError("Known-state checks do not commute")
        n = len(labels)
        # Row-reduce once, carrying every RHS simultaneously as an n-bit row.
        rows = [[z | (x << n), 1 << j] for j, (x, z) in enumerate(generators)]
        pivots = []
        for col in range(2*n):
            used = len(pivots)
            found = next((j for j in range(used, n) if rows[j][0] >> col & 1), None)
            if found is None:
                continue
            rows[used], rows[found] = rows[found], rows[used]
            for j in range(n):
                if j != used and rows[j][0] >> col & 1:
                    rows[j][0] ^= rows[used][0]
                    rows[j][1] ^= rows[used][1]
            pivots.append(col)
            if len(pivots) == n:
                break
        if len(pivots) != n:
            raise ValueError("Known-state checks are not independent")
        self.solutions = tuple((col, rows[j][1]) for j, col in enumerate(pivots))

    def decode(self, report):
        report = word(bits(report, len(self.labels)))
        solution = sum(((rhs & report).bit_count() % 2) << col for col, rhs in self.solutions)
        n = len(self.labels)
        return pauli_axes((solution & ((1 << n) - 1), solution >> n), n)


@lru_cache(maxsize=None)
def cycle_lookup(graph):
    table = {}
    cycle_masks = tuple(map(mask, graph.cycles))
    for weight in range(3):
        for positions in combinations(range(len(graph.edges)), weight):
            e = mask(positions)
            s = tuple((e & c).bit_count() % 2 for c in cycle_masks)
            if s in table:
                raise ValueError("Graph has ambiguous weight-two cycle decoding")
            table[s] = positions
    return table


def decode_gauged(report, graph):
    report = bits(report, 18 + len(graph.cycles) + 5)
    paired, cycles, gauss = report[:18], report[18:-5], report[-5:]
    if cycles not in cycle_lookup(graph):
        raise ReducedRejection("cycle_syndrome", "No edge-X mask of weight at most two matches the cycle syndrome")
    certified = not any(paired)
    details = {"paired": paired, "cycles": cycles, "gauss": gauss,
               "certified": certified, "cycle_x_edges": cycle_lookup(graph)[cycles],
               "gauss_z_edges": (), "action": "regauge"}
    if certified:
        if sum(gauss) % 2:
            details["action"] = "reject_negative_swap"
            raise ReducedRejection("negative_swap", "The repeated gauged record certifies the negative SWAP sector", details)
        details["gauss_z_edges"] = tuple(q for v, q in enumerate(graph.tree_edges, 1) if gauss[v])
        details["action"] = "extract"
    return details


def decode_gauge_word(report, graph):
    report = bits(report, len(graph.edges))
    candidates = []
    for t in product((0, 1), repeat=4):
        offsets = (0,) + t
        cut = graph.cut(offsets)
        if sum(a != b for a, b in zip(report, cut)) <= 2:
            candidates.append({"corrected_bits": cut, "offsets": offsets})
    if len(candidates) != 1:
        raise ReducedRejection("gauge_readout", "No unique graph cut within distance two of the edge report")
    return candidates[0]


@lru_cache(maxsize=1)
def two_block_tables():
    # Quotient only the known inner XXXX and ZZZZ stabilizers, retaining a
    # minimum-weight physical representative of each of the 64 local cosets.
    local = {}
    for x, z in product(range(16), repeat=2):
        key = (x ^ (15 if x & 8 else 0), z ^ (15 if z & 8 else 0))
        if key not in local or ((x | z).bit_count(), x, z) < (
                (local[key][0] | local[key][1]).bit_count(), *local[key]):
            local[key] = (x, z)
    tables = {}
    for a, b in combinations(range(5), 2):
        table = {}
        for (xa, za), (xb, zb) in product(local.values(), repeat=2):
            e = (xa << (4*a) | xb << (4*b), za << (4*a) | zb << (4*b))
            s = pauli_syndrome(e)
            if s in table:
                raise ArithmeticError("Fixed two-block set does not have unique correction classes")
            table[s] = e
        tables[(a, b)] = table
    return tables


def decode_joint(report):
    report = bits(report, 36)
    s_b, s_c = word(report[:18]), word(report[18:])
    candidates = [(blocks, (table[s_b], table[s_c])) for blocks, table in two_block_tables().items()
                  if s_b in table and s_c in table]
    classes = {(pauli_coset(b), pauli_coset(c)) for _, (b, c) in candidates}
    details = {"compatible_blocks": [list(blocks) for blocks, _ in candidates],
               "candidate_logical_classes": len(classes)}
    if len(classes) != 1:
        raise ReducedRejection("terminal_ambiguity" if classes else "terminal_absent",
                               "Joint B/C syndrome has no unique stabilizer-equivalent correction class", details)
    _, pair = min(candidates, key=lambda item: (
        sum((x | z).bit_count() for x, z in item[1]), item[1]))
    return {**details, "B": pauli_axes(pair[0], 20), "C": pauli_axes(pair[1], 20)}
