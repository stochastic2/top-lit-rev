"""Exact Q(zeta_8) matrices for normalized W and its elementary fault ports.

All coefficients and phases retained. This is a three-gate controlled-W audit,
including its two control idles, not a full-factory or cat-coupling audit.
Only Python's standard library is required.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import json


class Q:
    """a0+a1*z+a2*z**2+a3*z**3, z=exp(i*pi/4), z**4=-1."""
    def __init__(self, *values):
        if len(values) == 1 and isinstance(values[0], Q):
            self.a = values[0].a
        else:
            self.a = tuple(map(F, values)) + (F(0),)*(4-len(values))

    def __add__(self, other):
        other = Q(other)
        return Q(*(a+b for a, b in zip(self.a, other.a)))
    __radd__ = __add__

    def __neg__(self):
        return Q(*(-a for a in self.a))

    def __sub__(self, other):
        return self + -Q(other)

    def __mul__(self, other):
        other = Q(other)
        out = [F(0)]*4
        for i, a in enumerate(self.a):
            for j, b in enumerate(other.a):
                out[(i+j) % 4] += a*b*(-1 if i+j >= 4 else 1)
        return Q(*out)
    __rmul__ = __mul__

    def __eq__(self, other):
        return self.a == Q(other).a

    def __bool__(self):
        return any(self.a)

    def conjugate(self):
        return Q(self.a[0], -self.a[3], -self.a[2], -self.a[1])

    def serial(self):
        return [str(a) for a in self.a]


ZERO, ONE = Q(0), Q(1)
ZETA, IMAG = Q(0, 1), Q(0, 0, 1)
INV_SQRT2 = Q(0, F(1, 2), 0, F(-1, 2))


def eye(n):
    return [[Q(int(i == j)) for j in range(n)] for i in range(n)]


def scale(a, m):
    return [[a*v for v in row] for row in m]


def add(a, b):
    return [[x+y for x, y in zip(r, s)] for r, s in zip(a, b)]


def mm(a, b):
    return [[sum((x*y for x, y in zip(row, col)), ZERO) for col in zip(*b)] for row in a]


def kron(a, b):
    return [[a[i//len(b)][j//len(b)] * b[i % len(b)][j % len(b)]
             for j in range(len(a)*len(b))] for i in range(len(a)*len(b))]


def dagger(m):
    return [[v.conjugate() for v in row] for row in zip(*m)]


def trace(m):
    return sum((m[i][i] for i in range(len(m))), ZERO)


I = eye(2)
X = [[ZERO, ONE], [ONE, ZERO]]
Y = [[ZERO, -IMAG], [IMAG, ZERO]]
Z = [[ONE, ZERO], [ZERO, -ONE]]
T = [[ONE, ZERO], [ZERO, ZETA]]
CX = [[Q(int(i == (j ^ (j >> 1)))) for j in range(4)] for i in range(4)]
PAULIS = (I, X, Y, Z)


def controlled(w):
    return [[(I[i][j] if i < 2 and j < 2 else w[i-2][j-2] if i >= 2 and j >= 2 else ZERO)
             for j in range(4)] for i in range(4)]


def expansion(m):
    out = []
    reconstructed = scale(ZERO, eye(4))
    for a, b in product(range(4), repeat=2):
        p = kron(PAULIS[a], PAULIS[b])
        coeff = F(1, 4)*trace(mm(p, m))
        if coeff:
            out.append({"control": "IXYZ"[a], "data": "IXYZ"[b], "coefficient": coeff.serial()})
            reconstructed = add(reconstructed, scale(coeff, p))
    assert reconstructed == m
    return out


def audit(sign):
    w = scale(INV_SQRT2, add(X, scale(-sign, Y)))
    t = T if sign == 1 else dagger(T)
    assert w == dagger(w) and mm(w, w) == I
    assert w == mm(mm(dagger(t), X), t)
    s = mm(t, t)
    phase = ZETA.conjugate() if sign == 1 else ZETA
    assert w == scale(phase, mm(X, s))
    assert mm(mm(X, w), X) == scale(INV_SQRT2, add(X, scale(sign, Y)))
    gates = [kron(I, t), CX, kron(I, dagger(t))]
    ideal = mm(mm(gates[2], gates[1]), gates[0])
    assert ideal == controlled(w)
    # Each entry is a distinct physical location; control idles during either T
    # are separate from the corresponding target rotation location.
    locations = [(0, "T-data", [kron(I, p) for p in PAULIS[1:]]),
                 (0, "T-control-idle", [kron(p, I) for p in PAULIS[1:]]),
                 (1, "CX", [kron(a, b) for a, b in product(PAULIS, repeat=2) if (a, b) != (I, I)]),
                 (2, "inverse-T-data", [kron(I, p) for p in PAULIS[1:]]),
                 (2, "inverse-T-control-idle", [kron(p, I) for p in PAULIS[1:]])]
    def trajectory(injections):
        result = eye(4)
        for tick, g in enumerate(gates):
            result = mm(g, result)
            for tloc, error in injections:
                if tloc == tick:
                    result = mm(error, result)
        return result
    histogram = Counter()
    examples = []
    single = pairs = 0
    for k in (1, 2):
        for locs in combinations(locations, k):
            for errors in product(*(loc[2] for loc in locs)):
                faulty = trajectory([(loc[0], e) for loc, e in zip(locs, errors)])
                out_error = mm(faulty, dagger(ideal))
                terms = expansion(out_error)
                assert mm(out_error, dagger(out_error)) == eye(4)
                histogram[len(terms)] += 1
                single += k == 1
                pairs += k == 2
                if len(terms) > 1 and len(examples) < 2:
                    examples.append({"locations": [loc[1] for loc in locs], "output_error_Pauli_sum": terms})
    return {"sign": sign, "single_Pauli_basis_faults": single, "two_distinct_location_Pauli_basis_faults": pairs,
            "coherent_term_count_histogram": dict(histogram), "coherent_examples": examples,
            "identities_exact": True}


def mixed_cat_ideal(ports):
    """Independent sparse exact simulation of a three-port measured gadget.

    Includes physical cat preparation, all six parity meters (three scans),
    elementary H/CX/T ports, and every possible leaf readout record.
    """
    m = len(ports)
    assert m == 3
    def h(state, q):
        out = {}
        for b, a in state.items():
            low = b & ~(1 << q)
            out[low] = out.get(low, ZERO) + a*INV_SQRT2
            high = low | (1 << q)
            out[high] = out.get(high, ZERO) + a*INV_SQRT2*(-1 if b >> q & 1 else 1)
        return {b: a for b, a in out.items() if a}
    def cx(state, c, t):
        return {b ^ (((b >> c) & 1) << t): a for b, a in state.items()}
    def phase(state, q, s):
        z = ZETA if s == 1 else ZETA.conjugate()
        return {b: a*(z if b >> q & 1 else ONE) for b, a in state.items()}
    tests = 0
    for b in range(8):
        state = h({b: ONE}, m)
        for j in range(m-1):
            state = cx(state, m+j, m+j+1)
        for _ in range(3):
            for j in range(m-1):
                # Verifier bit 2m starts at zero and is measured as zero.
                state = cx(cx(state, m+j, 2*m), m+j+1, 2*m)
                assert all(not (word >> (2*m) & 1) for word in state)
        for q, port in enumerate(ports):
            if port == "Z":
                state = h(cx(h(state, q), m+q, q), q)
            elif port == "X":
                state = cx(state, m+q, q)
            else:
                s = 1 if port == "W+" else -1
                state = phase(cx(phase(state, q, s), m+q, q), q, -s)
        for q in range(m):
            state = h(state, m+q)
        for record in range(8):
            actual = {word & 7: a for word, a in state.items() if word >> m == record}
            out, phase_q = b, ONE
            for q, port in enumerate(ports):
                bit = (b >> q) & 1
                if port == "Z":
                    phase_q *= -1 if bit else 1
                else:
                    out ^= 1 << q
                    if port.startswith("W"):
                        s = 1 if port == "W+" else -1
                        # W_s|bit> = zeta^(s(2bit-1)) |bit xor 1>.
                        power = s*(2*bit-1)
                        phase_q *= ZETA if power == 1 else ZETA.conjugate()
            expected = {b: Q(F(1, 4))}
            expected[out] = expected.get(out, ZERO) + F((-1)**record.bit_count(), 4)*phase_q
            expected = {word: a for word, a in expected.items() if a}
            assert actual == expected
            tests += 1
    return {"ports": ports, "input_basis_and_leaf_record_pairs": tests,
            "all_coefficients_exact": True, "Kraus": "(I+(-1)^parity Q)/4 for m=3"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] /
                        "output/single-block-cz/cyclotomic.json")
    args = parser.parse_args()
    result = {"field": "Q[zeta_8]/(zeta_8**4+1)", "floating_point_used": False,
              "scope": "W, W' and exact controlled decompositions; local port faults and coherent sums",
              "full_factory_fault_enumeration": False, "results": [audit(s) for s in (-1, 1)],
              "mixed_cat_ideal": [mixed_cat_ideal(ports) for ports in (("X", "Z", "W+"),
                                                                      ("W-", "W+", "X"))]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
