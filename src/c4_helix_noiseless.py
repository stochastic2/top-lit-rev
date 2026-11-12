"""Noiseless implementation of notes/full_procedure_integrated_v2.md.

All quantum operations and measurement-dependent control are Guppy. Python
only constructs fixed circuits at compile time. No stabilizer is measured.
"""

from pathlib import Path
import argparse

from guppylang import guppy
from guppylang.std.builtins import Option, array, comptime, nothing, some
from guppylang.std.platform import output
from guppylang.std.quantum import (
    collect_measurements, cx, discard_array, h, measure_array, qubit, toffoli, z,
)


# Appendix A, independent supports R_0,...,R_8, in physical-qubit labels.
CHECK_SUPPORTS = (
    (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11),
    (12, 13, 14, 15), (16, 17, 18, 19),
    (0, 3, 6, 7, 10, 11, 12, 15),
    (4, 7, 8, 9, 14, 15, 16, 19),
    (1, 2, 8, 11, 12, 13, 18, 19),
    (2, 3, 5, 6, 13, 14, 16, 17),
)
LOGICAL_X0 = (2, 3, 8, 11, 12, 15)
LOGICAL_Z0 = (0, 3, 6, 7, 18, 19)
LOGICAL_Z1 = LOGICAL_X0

# Vertices a,b,c,d,e are 0,1,2,3,4. A_q uses precisely this edge order.
EDGES = (
    (0, 4), (2, 4), (2, 3), (0, 3), (1, 4),
    (3, 4), (0, 3), (0, 1), (1, 2), (1, 4),
    (0, 4), (0, 2), (0, 2), (2, 3), (1, 3),
    (0, 1), (1, 3), (3, 4), (2, 4), (1, 2),
)
TREE_EDGES = (7, 11, 3, 0)  # a--b, a--c, a--d, a--e
CONTROLLERS = tuple(q // 4 for q in range(20))


def preparation_schedule(supports, n_qubits=20):
    """Return the H-qubit list and CNOT pairs that prepare the encoded inputs.

    Each support R_s represents S_s^X = product_{q in R_s} X_q. For B:

        |00_L> = (1/sqrt(2^9)) sum_{u in {0,1}^9}
                     (S_0^X)^u_0 ... (S_8^X)^u_8 |0>^20.

    Each binary choice u_s includes or omits one X stabilizer. The sum has
    512 distinct physical bit strings, all with the same positive amplitude.
    For C, append the support of logical X_0, giving one more binary choice:

        |+0_L> = (|00_L> + |10_L>)/sqrt(2)
               = (I + Xbar_0)|00_L>/sqrt(2)
               = (1/sqrt(2^10)) sum_{a in {0,1}, u in {0,1}^9}
                     Xbar_0^a (S_0^X)^u_0 ... (S_8^X)^u_8 |0>^20.

    To implement these sums, row reduction replaces the generators by an
    equivalent set with one exclusive pivot qubit per generator. H on each
    pivot supplies its binary choice; CNOTs copy it to that generator's other
    positions. The caller starts in physical zeros; no checks are measured.
    """
    # A row explicitly lists which qubits an X generator flips.
    # For example, support (0, 2) on three qubits becomes [1, 0, 1].
    generator_rows = [
        [1 if qubit in support else 0 for qubit in range(n_qubits)]
        for support in supports
    ]
    pivot_qubits = []

    for qubit in range(n_qubits):
        next_row = len(pivot_qubits)

        # Find an unused generator containing this qubit.
        selected_row = None
        for row_index in range(next_row, len(generator_rows)):
            if generator_rows[row_index][qubit] == 1:
                selected_row = row_index
                break
        if selected_row is None:
            continue

        generator_rows[next_row], generator_rows[selected_row] = (
            generator_rows[selected_row], generator_rows[next_row]
        )
        pivot_row = generator_rows[next_row]

        # Make this qubit exclusive to the chosen generator. Multiplying
        # X generators adds their rows modulo 2: two Xs on one qubit cancel.
        # This changes the generators but preserves the set of terms in the sum.
        for row_index, row in enumerate(generator_rows):
            if row_index != next_row and row[qubit] == 1:
                generator_rows[row_index] = [
                    (entry + pivot_entry) % 2
                    for entry, pivot_entry in zip(row, pivot_row)
                ]
        pivot_qubits.append(qubit)

    if len(pivot_qubits) != len(generator_rows):
        raise ValueError("Source generators must be independent")

    # After H, each pivot is a coherent choice of 0 or 1. Copy that choice
    # to the remaining positions of its generator using CNOTs.
    cnot_pairs = []
    for pivot, row in zip(pivot_qubits, generator_rows):
        for target, includes_qubit in enumerate(row):
            if target != pivot and includes_qubit == 1:
                cnot_pairs.append((pivot, target))

    return tuple(pivot_qubits), tuple(cnot_pairs)


def make_source(supports, n_qubits=20):
    pivot_qubits, cnot_pairs = preparation_schedule(supports, n_qubits)

    @guppy
    def prepare(data: array[qubit, comptime(n_qubits)]) -> None:
        # The caller supplies freshly allocated |0> qubits.
        for pivot in comptime(list(pivot_qubits)):
            h(data[pivot])
        for control, target in comptime(list(cnot_pairs)):
            cx(data[control], data[target])

    return prepare


# |00_L> = uniform span of the nine X checks.
# |+0_L> = uniform span of those checks and logical X_0.
prepare_b = make_source(CHECK_SUPPORTS)
prepare_c = make_source(CHECK_SUPPORTS + (LOGICAL_X0,))


@guppy
def swap(left: qubit, right: qubit) -> None:
    cx(left, right)
    cx(right, left)
    cx(left, right)


@guppy
def fredkin(control: qubit, left: qubit, right: qubit) -> None:
    # Exact controlled SWAP, on the same three qubits, with no relative phases.
    cx(right, left)
    toffoli(control, left, right)
    cx(right, left)


def make_gauging(n_data, edges, controllers, tree_edges):
    """Build V2 Sections 6--8 and 12--13, without any verification.

    The parameters are compile-time geometry, also permitting small quantum
    execution tests of precisely the same Guppy control flow. There are five
    vertices and tree_edges is in b,c,d,e order, rooted at a.
    """
    if len(controllers) != n_data or len(tree_edges) != 4:
        raise ValueError("Incorrect controller or rooted-tree shape")
    if any(v not in range(5) for v in controllers):
        raise ValueError("Controllers must be vertices a through e")
    if any(edges[q] != (0, v) for v, q in enumerate(tree_edges, 1)):
        raise ValueError("Tree edges must join a to b,c,d,e in that order")
    n_edges = len(edges)

    @guppy
    def gauging(b: array[qubit, comptime(n_data)],
                c: array[qubit, comptime(n_data)]) -> bool:
        vertices = array(qubit() for _ in range(5))
        gauge = array(qubit() for _ in range(comptime(n_edges)))
        for v in range(5):
            h(vertices[v])
        # Section 6: graph resource, increasing edge label and endpoint order.
        for q, endpoints in comptime(list(enumerate(edges))):
            u, v = endpoints
            cx(vertices[u], gauge[q])
            cx(vertices[v], gauge[q])
        # Section 7: finish every Fredkin before measuring any vertex.
        for q, v in comptime(list(enumerate(controllers))):
            fredkin(vertices[v], b[q], c[q])
        for v in range(5):
            h(vertices[v])
        vertex_bits = collect_measurements(measure_array(vertices))
        output("vertex_x", vertex_bits)
        odd = False
        for v in range(5):
            odd = odd ^ vertex_bits[v]
        output("swap_plus", not odd)
        if odd:
            discard_array(gauge)
            return False
        # Section 8.4: real classical feedforward, even without faults.
        for v, q in comptime(list(enumerate(tree_edges, 1))):
            if vertex_bits[v]:
                z(gauge[q])
        # Sections 9--11 are error checks and are deliberately absent.
        gauge_bits = collect_measurements(measure_array(gauge))
        output("gauge_z", gauge_bits)
        # Noiseless decoding: t_a=0 and t_v=m_(a,v). Read all edge bits;
        # no noisy decoder, syndrome, or cycle-check measurement is needed.
        offsets = array(False, gauge_bits[comptime(tree_edges[0])],
                        gauge_bits[comptime(tree_edges[1])],
                        gauge_bits[comptime(tree_edges[2])],
                        gauge_bits[comptime(tree_edges[3])])
        output("swap_offsets", offsets)
        for q, v in comptime(list(enumerate(controllers))):
            if offsets[v]:
                swap(b[q], c[q])
        return True

    return gauging


gauge_and_ungauge = make_gauging(20, EDGES, CONTROLLERS, TREE_EDGES)


@guppy
def prepare_magic() -> Option[array[qubit, 20]]:
    """One attempt; some(C) retains |M0_L>, nothing() means postselection failed.

    On success the caller owns twenty live encoded C qubits. No measurement
    of C is made. With deterministic sources the success probability is 5/8.
    """
    b = array(qubit() for _ in range(20))
    c = array(qubit() for _ in range(20))
    prepare_b(b)
    prepare_c(c)
    if not gauge_and_ungauge(b, c):
        discard_array(b)
        discard_array(c)
        output("accepted", False)
        return nothing()
    # Sections 14--15 (filtering and recovery) are absent.
    # Section 16: measure B and evaluate logical Z_0 from the perfect reports.
    b_bits = collect_measurements(measure_array(b))
    output("b_z", b_bits)
    logical_one = False
    for q in comptime(list(LOGICAL_Z0)):
        logical_one = logical_one ^ b_bits[q]
    output("b_logical_z0", logical_one)
    if logical_one:
        discard_array(c)
        output("accepted", False)
        return nothing()
    output("accepted", True)
    return some(c)


@guppy
def compile_entrypoint() -> None:
    """Standalone compile/demo sink. Applications should call prepare_magic()."""
    attempt = prepare_magic()
    if attempt.is_some():
        c = attempt.unwrap()
        discard_array(c)
    else:
        attempt.unwrap_nothing()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Write the compiled standalone HUGR package here")
    args = parser.parse_args()
    package = compile_entrypoint.compile()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(package.to_bytes())
        print(f"Compiled noiseless 65-qubit procedure to {args.output}")
    else:
        print("Compiled noiseless 65-qubit procedure successfully")
    print("Quantum output API: prepare_magic() -> Option[array[qubit, 20]]")


if __name__ == "__main__":
    main()
