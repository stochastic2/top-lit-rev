"""Exact code/branch checks and quantum execution of the shared Guppy kernel.

Run with $HOME/pytket-venv/bin/python -m pytest -q src/test_c4_helix_noiseless.py
The physical 65-qubit program is compiled, not densely statevector simulated.
"""

from fractions import Fraction
from itertools import product

import pytest
from guppylang import guppy
from guppylang.std.builtins import array, comptime
from guppylang.std.platform import output
from guppylang.std.quantum import (
    collect_measurements, cx, discard_array, h, measure_array, qubit, sdg, x,
)

from c4_helix_noiseless import (
    CHECK_SUPPORTS, CONTROLLERS, EDGES, LOGICAL_X0, LOGICAL_Z0, LOGICAL_Z1,
    TREE_EDGES, compile_entrypoint, fredkin, make_gauging,
    preparation_schedule, prepare_magic,
)


def mask(support):
    # Compact bit strings are used only for the independent test calculations.
    return sum(1 << q for q in support)


def span(rows):
    words = {0}
    for row in rows:
        words |= {x ^ row for x in words}
    return words


def parity(word):
    return word.bit_count() % 2


def source_words(supports):
    # Execute every H/CX basis path of the actual source preparation schedule.
    pivots, gates = preparation_schedule(supports)
    words = {sum(bit << p for bit, p in zip(bits, pivots))
             for bits in product((0, 1), repeat=len(pivots))}
    for control, target in gates:
        words = {word ^ (((word >> control) & 1) << target) for word in words}
    return words


def test_unitary_sources_and_exact_encoded_output():
    b = source_words(CHECK_SUPPORTS)
    c = source_words(CHECK_SUPPORTS + (LOGICAL_X0,))
    checks = tuple(map(mask, CHECK_SUPPORTS))
    assert len(b) == 512 and len(c) == 1024
    assert b == span(checks)
    assert c == b | {word ^ mask(LOGICAL_X0) for word in b}
    for words in (b, c):
        assert all(parity(word & check) == 0 for word in words for check in checks)
        # X stabilizers: translation leaves every uniform positive source intact.
        assert all({word ^ check for word in words} == words for check in checks)
        assert all(parity(word & mask(LOGICAL_Z1)) == 0 for word in words)
    assert all(parity(word & mask(LOGICAL_Z0)) == 0 for word in b)
    assert {word ^ mask(LOGICAL_X0) for word in c} == c

    # Exact physical computational-basis amplitudes of (I+U)|B>|C>.
    # Common amplitude is 1/sqrt(512*1024). No logical-only input assumption.
    norms = {False: 0, True: 0}
    for b_word in c:
        amplitudes = {c_word: int(b_word in b) + int(c_word in b) for c_word in c}
        amplitudes = {word: value for word, value in amplitudes.items() if value}
        logical_one = bool(parity(b_word & mask(LOGICAL_Z0)))
        norms[logical_one] += sum(a * a for a in amplitudes.values())
        if not logical_one:
            # Every accepted *physical* B report leaves exactly the same encoded M0.
            assert all(value == (2 if word in b else 1)
                       for word, value in amplitudes.items())
            assert len(amplitudes) == 1024
    assert Fraction(sum(norms.values()), 4 * 512 * 1024) == Fraction(3, 4)
    assert Fraction(norms[False], sum(norms.values())) == Fraction(5, 6)
    assert Fraction(norms[False], 4 * 512 * 1024) == Fraction(5, 8)


def test_all_512_vertex_and_gauge_branches():
    """Compare physical SWAP polynomials, including gauge-Z feedforward phases."""
    def gauge_word(t):
        return sum((((t >> u) ^ (t >> v)) & 1) << q
                   for q, (u, v) in enumerate(EDGES))

    def swap_word(t):
        return sum(((t >> v) & 1) << q for q, v in enumerate(CONTROLLERS))

    for vertex_report in range(32):
        for t in range(0, 32, 2):  # t_a=0, all sixteen gauge records
            gauge = gauge_word(t)
            decoded = sum(((gauge >> q) & 1) << v
                          for v, q in enumerate(TREE_EDGES, 1))
            assert decoded == t
            assert gauge_word(t ^ 31) == gauge
            frame_phase = sum(((vertex_report >> v) & 1) * ((gauge >> q) & 1)
                              for v, q in enumerate(TREE_EDGES, 1)) % 2
            corrected = {
                swap_word(component) ^ swap_word(decoded):
                (-1) ** (parity(vertex_report & component) ^ frame_phase)
                for component in (t, t ^ 31)
            }
            # The complete data operator is I + (-1)^r U, with no relative
            # phase left over on even branches. Odd outcomes must be rejected.
            assert corrected == {0: 1, (1 << 20) - 1: (-1) ** parity(vertex_report)}
    assert CONTROLLERS == tuple(q // 4 for q in range(20))


def test_full_physical_program_compiles():
    assert compile_entrypoint.compile().to_bytes()
    assert prepare_magic.compile_function().to_bytes()


# Small quantum execution fixture: five repetition-code data qubits per copy,
# four root-tree gauge qubits, five vertices (19 live qubits). This invokes the
# exact production Guppy kernel with a smaller compile-time geometry.
small_gauging = make_gauging(5, ((0, 1), (0, 2), (0, 3), (0, 4)),
                             (0, 1, 2, 3, 4), (0, 1, 2, 3))


def small_probe(basis):
    @guppy
    def probe() -> None:
        b = array(qubit() for _ in range(5))
        c = array(qubit() for _ in range(5))
        h(c[0])
        for q in range(1, 5):
            cx(c[0], c[q])
        if small_gauging(b, c):
            b_bits = collect_measurements(measure_array(b))
            output("b_readout", b_bits)
            if not b_bits[0]:
                # Unitary repetition-code decoding, then single-qubit tomography.
                for q in range(1, 5):
                    cx(c[0], c[q])
                if comptime(basis == "Y"):
                    sdg(c[0])
                if comptime(basis != "Z"):
                    h(c[0])
                output("c_readout", collect_measurements(measure_array(c)))
            else:
                discard_array(c)
        else:
            discard_array(b)
            discard_array(c)

    return probe


@pytest.mark.parametrize("basis, expectation", [("X", 0.8), ("Y", 0.0), ("Z", 0.6)])
def test_shared_guppy_kernel_quantum_execution(basis, expectation):
    shots = (small_probe(basis).emulator(n_qubits=19)
             .with_seed(9123).with_shots(128).run()).results
    records = [shot.as_dict() for shot in shots]
    plus = [r for r in records if r["swap_plus"]]
    accepted = [r for r in plus if "c_readout" in r]
    assert abs(len(plus) / len(records) - 0.75) < 0.15
    assert abs(len(accepted) / len(records) - 0.625) < 0.15
    # Nontrivial classical feedforward paths must actually be exercised.
    assert any(any(r["vertex_x"][1:]) for r in accepted)
    assert any(any(r["swap_offsets"][1:]) for r in accepted)
    assert all(len(set(r["b_readout"])) == 1 for r in plus)
    assert all(not any(r["c_readout"][1:]) for r in accepted)
    observed = sum(1 - 2 * int(r["c_readout"][0]) for r in accepted) / len(accepted)
    assert abs(observed - expectation) < 0.3


@guppy
def fredkin_truth_table() -> None:
    # All eight computational-basis inputs in one execution.
    for value in range(8):
        from_guppy = array(qubit() for _ in range(3))
        set_basis(from_guppy, value)
        fredkin(from_guppy[0], from_guppy[1], from_guppy[2])
        output("out", collect_measurements(measure_array(from_guppy)))


@guppy
def set_basis(qs: array[qubit, 3], value: int) -> None:
    for q in range(3):
        if (value >> q) & 1 == 1:
            x(qs[q])


def test_fredkin_gate_truth_table():
    shot = fredkin_truth_table.emulator(n_qubits=3).with_seed(42).run().results[0]
    outputs = [value for tag, value in shot.entries if tag == "out"]
    for value, actual in enumerate(outputs):
        control, left, right = ((value >> q) & 1 for q in range(3))
        assert actual == [bool(control), bool(right if control else left),
                          bool(left if control else right)]
    assert len(outputs) == 8
