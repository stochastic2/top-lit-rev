"""Run the full noiseless C4-Helix procedure with explicit sparse amplitudes.

Read notes/c4-helix-exact-simulation-plan-v2.md for the representation and
the proof permitting early gauge-Z sampling. Physical equations below refer
to notes/full_procedure_integrated_v2.md, Sections 5--8, 12--13, and 16.

Example, from the repository root::

    $HOME/pytket-venv/bin/python src/simulate_c4_helix_sparse.py \
        --shots 1 --seed 0 --output-dir output/c4-helix-sparse-example

The CLI streams one JSON record per attempt and saves successful unmeasured
C states as exact integer weights. It adds no stabilizer measurements.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random
import resource
import sys
from time import perf_counter
from typing import Callable, Iterator

from c4_helix_noiseless import (
    CHECK_SUPPORTS, CONTROLLERS, EDGES, LOGICAL_X0, LOGICAL_Z0, LOGICAL_Z1,
    TREE_EDGES, preparation_schedule,
)
from sparse_wavefunction import SparseState


@dataclass(frozen=True)
class CircuitSpecification:
    """Physical geometry and source generators; defaults are the full V2 circuit.

    Source supports specify products of Xs whose uniform span is prepared
    by the actual H/CNOT source schedules. Smaller specifications allow an
    independent dense comparison without changing the simulation algorithm.
    """

    data_qubits: int = 20
    edges: tuple[tuple[int, int], ...] = EDGES
    controllers: tuple[int, ...] = CONTROLLERS
    tree_edges: tuple[int, ...] = TREE_EDGES
    b_source_generators: tuple[tuple[int, ...], ...] = CHECK_SUPPORTS
    c_source_generators: tuple[tuple[int, ...], ...] = CHECK_SUPPORTS + (LOGICAL_X0,)
    b_logical_z0: tuple[int, ...] = LOGICAL_Z0

    @property
    def vertex_count(self) -> int:
        return len(self.tree_edges) + 1

    @property
    def vertex_labels(self) -> tuple[str, ...]:
        return tuple(f"V_{chr(ord('a') + v)}" for v in range(self.vertex_count))

    def validate(self) -> None:
        if self.data_qubits < 1 or len(self.controllers) != self.data_qubits:
            raise ValueError("Each data pair needs exactly one controller")
        if not self.edges or self.vertex_count < 2:
            raise ValueError("A connected gauge graph with at least two vertices is required")
        if any(v < 0 or v >= self.vertex_count for v in self.controllers):
            raise ValueError("Controller vertex is outside the graph")
        for u, v in self.edges:
            if not (0 <= u < v < self.vertex_count):
                raise ValueError("Edges must have distinct, alphabetically ordered endpoints")
        for v, q in enumerate(self.tree_edges, 1):
            if q < 0 or q >= len(self.edges) or self.edges[q] != (0, v):
                raise ValueError("Tree edges must connect root a to the other vertices in order")
        for support in self.b_source_generators + self.c_source_generators + (self.b_logical_z0,):
            if len(set(support)) != len(support) or any(q < 0 or q >= self.data_qubits for q in support):
                raise ValueError("Invalid physical source/readout support")


def prepare_source(supports: tuple[tuple[int, ...], ...],
                   labels: tuple[str, ...], state_type=SparseState) -> SparseState:
    """Integrated V2 Section 5: prepare known inputs without checking syndromes.

    |00_L> = 2^(-9/2) sum_{u in {0,1}^9} prod_s (S_s^X)^u_s |0^20>,
    |+0_L> = (I + Xbar_0)|00_L>/sqrt(2).

    We execute preparation_schedule's H and CNOT gates; we do not initialize
    a precomputed set of valid codewords or measure any source stabilizer.
    """
    hadamards, cnots = preparation_schedule(supports, len(labels))
    state = state_type.zeros(labels)
    for q in hadamards:
        state = state.hadamard(labels[q])
    for control, target in cnots:
        state = state.cnot(labels[control], labels[target])
    return state


def build_gauge_preimages(edges: tuple[tuple[int, int], ...],
                         vertex_count: int = 5) -> dict[str, tuple[str, str]]:
    """Section 6: |Gamma> = 2^(-5/2) sum_t |t>|p(t)>; p(t)_q=t_u+t_v.

    Follow the two graph CNOTs for each edge, on the 32 small vertex labels.
    Verify two complementary preimages per gauge word before early sampling.
    """
    table: dict[str, list[str]] = {}
    for vertex_bits in product((0, 1), repeat=vertex_count):
        gauge_bits = [0] * len(edges)
        for q, (u, v) in enumerate(edges):
            gauge_bits[q] = (gauge_bits[q] + vertex_bits[u]) % 2
            gauge_bits[q] = (gauge_bits[q] + vertex_bits[v]) % 2
        gauge_word = "".join(map(str, gauge_bits))
        table.setdefault(gauge_word, []).append("".join(map(str, vertex_bits)))
    if len(table) != 2 ** (vertex_count - 1):
        raise ValueError("The graph must be connected")
    for preimages in table.values():
        if len(preimages) != 2 or any(a == b for a, b in zip(*preimages)):
            raise ValueError("Every gauge outcome needs two complementary vertex strings")
    return {word: (values[0], values[1]) for word, values in table.items()}


def sample_gauge(table: dict[str, tuple[str, str]], rng: Random) -> tuple[str, tuple[str, str]]:
    """Pr(m)=2/32=1/16 for the checked graph. Keep both coherent preimages."""
    words = tuple(table)
    word = words[rng.randrange(len(words))]
    return word, table[word]


def process_peak_rss_bytes() -> int:
    """Process-lifetime peak RSS, including imports and cached sources, not a delta."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


@dataclass
class AttemptMetrics:
    elapsed_seconds: float = 0.0
    peak_state_entries: int = 0
    process_peak_rss_bytes: int = 0


@dataclass
class ShotResult:
    """One physical attempt; later fields stay None if the circuit stops early.

    Conditional probabilities explicitly refer to the internally sampled m.
    An odd-vertex rejection does not expose m as a physical gauge readout.
    ``c_state`` remains quantum data; no C measurement is performed.
    """

    shot_index: int
    accepted: bool = False
    vertex_x: tuple[int, ...] = ()
    swap_plus: bool = False
    gauge_z: str | None = None
    swap_offsets: tuple[int, ...] | None = None
    b_z: str | None = None
    b_logical_z0: int | None = None
    c_state: SparseState | None = field(default=None, repr=False)
    vertex_probability_given_gauge: Fraction = Fraction(1)
    b_probability_given_vertex_gauge: Fraction | None = None
    metrics: AttemptMetrics = field(default_factory=AttemptMetrics)


StageObserver = Callable[[str, SparseState], None]


class SparseC4HelixSimulator:
    """Cache only the small source states and gauge table; execute attempts serially.

    The early gauge measurement is an exact reordering: Q_m commutes with
    enrichment and vertex operations, and with diagonal gauge feedforward.
    See simulation plan V2 Section 3. No state with all 32 gauge sectors is
    allocated. The largest individual state has at most 2*512*1024 entries.
    """

    def __init__(self, specification: CircuitSpecification | None = None, *, backend="python"):
        if backend not in ("python", "rust"):
            raise ValueError("backend must be 'python' or 'rust'")
        self.backend = backend
        self.state_type = SparseState
        self._program_type = None
        if backend == "rust":
            from peropq.sparse_wavefunction import ExactSparseState, CompiledProgram
            self.state_type = ExactSparseState
            self._program_type = CompiledProgram
        self.specification = specification or CircuitSpecification()
        self.specification.validate()
        n = self.specification.data_qubits
        self.b_labels = tuple(f"B_{q}" for q in range(n))
        self.c_labels = tuple(f"C_{q}" for q in range(n))
        self.b_source = prepare_source(self.specification.b_source_generators, self.b_labels, self.state_type)
        self.c_source = prepare_source(self.specification.c_source_generators, self.c_labels, self.state_type)
        self.gauge_table = build_gauge_preimages(self.specification.edges,
                                                self.specification.vertex_count)

    def conditioned_input(self, preimages: tuple[str, str]) -> SparseState:
        """Construct (|t>+|t_bar>)/sqrt(2) tensor |psi>, with fixed m metadata.

        Construct the two vertex prefixes directly, avoiding a second large
        BC tensor-product dictionary. The weights keep both coherent terms.
        """
        if self.backend == "rust":
            vertices = self.state_type(self.specification.vertex_labels, {word: 1 for word in preimages})
            return vertices.tensor(self.b_source).tensor(self.c_source)
        weights = {}
        for vertices in preimages:
            for b_word, b_weight in self.b_source.weights.items():
                prefix = vertices + b_word
                for c_word, c_weight in self.c_source.weights.items():
                    weights[prefix + c_word] = b_weight * c_weight
        labels = self.specification.vertex_labels + self.b_labels + self.c_labels
        return SparseState(labels, weights)

    def enrich(self, state: SparseState) -> SparseState:
        """Section 7: sum_t |t>|p(t)> V_t|psi>/sqrt(32), conditioned on m.

        Execute all twenty Fredkins in physical-label order. Controllers
        come from CONTROLLERS, independently of the endpoints of edge q.
        """
        if self.backend == "rust":
            program = self._program_type(state.labels)
            for q, v in enumerate(self.specification.controllers):
                program.fredkin(self.specification.vertex_labels[v], self.b_labels[q], self.c_labels[q])
            return state.apply(program)
        for q, v in enumerate(self.specification.controllers):
            state = state.fredkin(self.specification.vertex_labels[v],
                                 self.b_labels[q], self.c_labels[q])
        return state

    def apply_vertex_feedforward(self, state: SparseState, vertex_x: tuple[int, ...],
                                 gauge_word: str) -> SparseState:
        """Section 8.4: F_b=Z_A7^b_b Z_A11^b_c Z_A3^b_d Z_A0^b_e.

        For fixed gauge word m, F_b|m> = (-1)^theta |m>,
        theta=b_b*m7+b_c*m11+b_d*m3+b_e*m0 (mod 2).
        Apply this sign explicitly even though it is global on this trajectory.
        """
        exponent = sum(vertex_x[v] * int(gauge_word[q])
                       for v, q in enumerate(self.specification.tree_edges, 1))
        return state.global_sign((-1) ** (exponent % 2))

    def correct_swaps(self, state: SparseState, gauge_word: str) -> tuple[SparseState, tuple[int, ...]]:
        """Sections 12--13: t_hat=(0,m7,m11,m3,m0); apply V_t_hat.

        V_t_hat[V_t Pi_+|psi>] = Pi_+|psi>, Pi_+=(I+U)/2.
        The corrected state's expected normalized form is
        (|psi>+U|psi>)/sqrt(3); it is never directly initialized here.
        """
        offsets = (0,) + tuple(int(gauge_word[q]) for q in self.specification.tree_edges)
        if self.backend == "rust":
            program = self._program_type(state.labels)
            for q, v in enumerate(self.specification.controllers):
                if offsets[v]:
                    program.swap(self.b_labels[q], self.c_labels[q])
            return state.apply(program), offsets
        for q, v in enumerate(self.specification.controllers):
            if offsets[v]:
                state = state.swap(self.b_labels[q], self.c_labels[q])
        return state, offsets

    def simulate_attempt(self, rng: Random, shot_index: int = 0,
                         observer: StageObserver | None = None) -> ShotResult:
        """One exact trajectory; Pr(vertex b|m)=3/64 even, 1/64 odd in the full circuit.

        Vertex and B probabilities are calculated from the current amplitudes,
        not inserted from the expected logical-state formulas. The observer
        may inspect a stage but should not retain its large intermediate state.
        """
        started = perf_counter()
        result = ShotResult(shot_index)

        def observe(stage: str, state: SparseState) -> None:
            size = state.support_size if self.backend == "rust" else len(state.weights)
            result.metrics.peak_state_entries = max(result.metrics.peak_state_entries, size)
            if observer is not None:
                observer(stage, state)

        def finish() -> ShotResult:
            result.metrics.elapsed_seconds = perf_counter() - started
            result.metrics.process_peak_rss_bytes = process_peak_rss_bytes()
            return result

        # Reordered internal sample. It becomes a public measurement only if
        # the physical circuit reaches gauge readout after vertex selection.
        internal_m, preimages = sample_gauge(self.gauge_table, rng)
        state = self.conditioned_input(preimages)
        observe("conditioned_input", state)
        state = self.enrich(state)
        observe("enriched", state)

        vertex_bits = []
        for label in self.specification.vertex_labels:
            state, bit, probability = state.measure_x(label, rng)
            vertex_bits.append(bit)
            result.vertex_probability_given_gauge *= probability
            observe(f"measured_{label}_in_X", state)
        result.vertex_x = tuple(vertex_bits)
        result.swap_plus = sum(vertex_bits) % 2 == 0
        if not result.swap_plus:
            # No physical gauge/B record is produced on this rejection path.
            return finish()

        observe("before_vertex_feedforward", state)
        state = self.apply_vertex_feedforward(state, result.vertex_x, internal_m)
        observe("after_vertex_feedforward", state)
        result.gauge_z = internal_m
        state, result.swap_offsets = self.correct_swaps(state, internal_m)
        observe("after_swap_correction", state)

        # Section 16: h_s recovery is absent in the noiseless implementation.
        # Sample actual physical B reports, then evaluate the logical parity.
        b_bits = []
        result.b_probability_given_vertex_gauge = Fraction(1)
        for label in self.b_labels:
            state, bit, probability = state.measure_z(label, rng)
            b_bits.append(bit)
            result.b_probability_given_vertex_gauge *= probability
        result.b_z = "".join(map(str, b_bits))
        result.b_logical_z0 = sum(b_bits[q] for q in self.specification.b_logical_z0) % 2
        result.accepted = result.b_logical_z0 == 0
        if result.accepted:
            result.c_state = state
            observe("accepted_C", state)
        return finish()

    def iter_attempts(self, number_of_attempts: int, seed: int | None = None,
                      observer: StageObserver | None = None) -> Iterator[ShotResult]:
        """Yield one result at a time. Intermediate wavefunctions are not cached."""
        if number_of_attempts < 0:
            raise ValueError("Number of attempts must be nonnegative")
        rng = Random(seed)
        for index in range(number_of_attempts):
            yield self.simulate_attempt(rng, index, observer)


def output_diagnostics(state: SparseState) -> dict:
    """Exact code/logical checks of the retained C state; no added measurements.

    Section 16 predicts |M0_L>, |M>=(2|0>+|1>)/sqrt(5), hence
    <Xbar_0>=4/5, <Zbar_0>=3/5, <Ybar_0>=0, <Zbar_1>=1.
    """
    if state.labels != tuple(f"C_{q}" for q in range(20)):
        raise ValueError("Full C4-Helix diagnostics require the twenty C coordinates")
    checks = [state.expectation_pauli(x_support=s) for s in CHECK_SUPPORTS]
    checks += [state.expectation_pauli(z_support=s) for s in CHECK_SUPPORTS]
    # In this code the physical Xbar_0 and Zbar_0 supports overlap once;
    # i Xbar_0 Zbar_0 is exactly the corresponding Hermitian Pauli string.
    return {"entries": len(state.weights), "norm_squared": state.norm_squared(),
            "weight_counts": dict(Counter(w if type(w) is int else str(w) for w in state.weights.values())),
            "in_original_code_space": all(value == 1 for value in checks),
            "logical_X0": str(state.expectation_pauli(x_support=LOGICAL_X0)),
            "logical_Z0": str(state.expectation_pauli(z_support=LOGICAL_Z0)),
            "logical_Y0": str(state.expectation_pauli(LOGICAL_X0, LOGICAL_Z0)),
            "logical_Z1": str(state.expectation_pauli(z_support=LOGICAL_Z1))}


def write_result(result: ShotResult, output_directory: Path) -> dict:
    """Save exact C data if present and return a JSON-ready physical shot record.

    Identical states up to a common real scale/sign share one content-named
    file. No intermediate states are serialized. The caller writes the record
    immediately to its JSONL stream.
    """
    reference = None
    diagnostics = None
    if result.c_state is not None:
        payload = result.c_state.canonical_payload()
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = sha256(serialized.encode()).hexdigest()
        reference = f"states/{digest}.json"
        destination = output_directory / reference
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            destination.write_text(serialized + "\n")
        diagnostics = output_diagnostics(result.c_state)
    return {"shot_index": result.shot_index, "accepted": result.accepted,
            "vertex_x": result.vertex_x, "swap_plus": result.swap_plus,
            "gauge_z": result.gauge_z, "swap_offsets": result.swap_offsets,
            "b_z": result.b_z, "b_logical_z0": result.b_logical_z0,
            "vertex_probability_given_gauge": str(result.vertex_probability_given_gauge),
            "b_probability_given_vertex_gauge":
                (str(result.b_probability_given_vertex_gauge)
                 if result.b_probability_given_vertex_gauge is not None else None),
            "c_state_reference": reference, "c_diagnostics": diagnostics,
            "metrics": vars(result.metrics)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots", type=int, default=1, help="Number of attempts, including rejected attempts")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--backend", choices=("python", "rust"), default="python")
    parser.add_argument("--output-dir", type=Path, default=Path("output/c4-helix-sparse"))
    parser.add_argument("--quiet", action="store_true", help="Suppress stage progress on stderr")
    args = parser.parse_args()
    if args.shots < 1:
        parser.error("--shots must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "shots.jsonl"
    if records_path.exists():
        parser.error(f"{records_path} already exists; choose another --output-dir")

    def progress(stage: str, state: SparseState) -> None:
        if not args.quiet:
            size = state.support_size if args.backend == "rust" else len(state.weights)
            print(f"{stage}: {size:,} basis entries", file=sys.stderr, flush=True)

    simulator = SparseC4HelixSimulator(backend=args.backend)
    accepted = 0
    start = perf_counter()
    with records_path.open("x") as stream:
        for result in simulator.iter_attempts(args.shots, args.seed, progress):
            record = write_result(result, args.output_dir)
            stream.write(json.dumps(record) + "\n")
            stream.flush()
            accepted += result.accepted
            del record, result
    summary = {"attempts": args.shots, "accepted": accepted, "seed": args.seed,
               "elapsed_seconds": perf_counter() - start,
               "process_peak_rss_bytes": process_peak_rss_bytes(),
               "b_source_entries": len(simulator.b_source.weights),
               "c_source_entries": len(simulator.c_source.weights),
               "gauge_words": len(simulator.gauge_table), "ideal_success_probability": "5/8"}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Shot records: {records_path}")


if __name__ == "__main__":
    main()
