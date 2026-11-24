"""Density-matrix baselines for the three-term physical resource (wire 0 first)."""
import itertools
import json
from functools import reduce
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RATES = {k: float(v) for k, v in json.loads((HERE / "summary.json").read_text())["noise"].items()}
assert RATES["idle_infidelity"] == RATES["preparation_flip_probability"] == 0
I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1])
H = (X + Z) / np.sqrt(2)
T = np.diag([1, np.exp(1j * np.pi / 4)])
TARGET = np.array([1, 1, 1, 0]) / np.sqrt(3)


def ry(angle):
    c, s = np.cos(angle / 2), np.sin(angle / 2)
    return np.array([[c, -s], [s, c]])


def embed(n, local):
    return reduce(np.kron, [local.get(q, I) for q in range(n)])


def simulate(n, gates, scale):
    rho = np.diag([1+0j] + [0.] * (2**n - 1))
    for name, qubits, single in gates:
        if name == "CX":
            c, t = qubits
            unitary = embed(n, {c: np.diag([1, 0])}) + embed(n, {c: np.diag([0, 1]), t: X})
            r = RATES["two_qubit_infidelity"]
        else:
            unitary = embed(n, {qubits[0]: single})
            r = RATES["t_infidelity" if name in ("T", "TDG") else "one_qubit_infidelity"]
        rho = unitary @ rho @ unitary.conj().T
        d = 2**len(qubits)
        p = scale * r * (d+1)/d
        mixed = (1-p)*rho
        for word in list(itertools.product((I, X, Y, Z), repeat=len(qubits)))[1:]:
            error = embed(n, dict(zip(qubits, word)))
            mixed += p/(d*d-1) * (error @ rho @ error.conj().T)
        rho = mixed
    assert np.isclose(rho.trace(), 1)
    if n == 3:
        flip = scale * RATES["readout_flip_probability"]
        rho = (1-flip)*rho[::2, ::2] + flip*rho[1::2, 1::2]
    accept = rho.trace().real
    return dict(acceptance=accept, fidelity=float((TARGET @ rho @ TARGET).real / accept))


def gate(name, q, u):
    return name, (q,), u


def cx(c, t):
    return "CX", (c, t), None


# Diagonalize the real symmetric 2x2 target amplitude matrix.
eigenvalues, _ = np.linalg.eigh([[1, 1], [1, 0]])
schmidt = 2*np.arctan(eigenvalues[0]/eigenvalues[1])
basis = np.arctan2(2, 1)
direct = [gate("RY", 0, ry(schmidt)), cx(0, 1),
          gate("RY", 0, ry(basis)), gate("RY", 1, ry(basis))]

# Relative-phase Toffoli into a clean flag. The accepted three amplitudes
# have equal phase; the phase of the discarded |11> component is immaterial.
herald = [gate("H", q, H) for q in range(3)] + [
    gate("T", 2, T), cx(1, 2), gate("TDG", 2, T.conj()), cx(0, 2),
    gate("T", 2, T), cx(1, 2), gate("TDG", 2, T.conj()), gate("H", 2, H)]

if __name__ == "__main__":
    result = {}
    for name, n, gates, ideal_yield in [("native_Ry", 2, direct, 1), ("clifford_T_heralded", 3, herald, .75)]:
        ideal = simulate(n, gates, 0)
        assert abs(ideal["fidelity"]-1) < 1e-12
        assert abs(ideal["acceptance"]-ideal_yield) < 1e-12
        result[name] = dict(noiseless=ideal, noisy=simulate(n, gates, 1))
    report = json.dumps(result, indent=2)
    (HERE / "direct_physical.json").write_text(report+"\n")
    print(report)
