"""Logical Y readout and an explicit output Clifford frame for |m_Y>."""

from c4_helix_noiseless import CHECK_SUPPORTS, LOGICAL_X0
from gaussian_integer import gaussian
from sparse_wavefunction import GaussianSparseState


MAGIC_OUTPUTS = ("y", "z")
Y0_X_MASK, Y0_Z_MASK = 1333, 867
Y0_WORD_SIGN = 1  # This nine-body Hermitian word equals -logical Y0 on the code.


def logical_y_ports():
    return tuple(("Y" if (Y0_X_MASK & Y0_Z_MASK) >> q & 1 else
                  "X" if Y0_X_MASK >> q & 1 else "Z", (f"B_{q}",))
                 for q in range(20) if (Y0_X_MASK | Y0_Z_MASK) >> q & 1)


def corrected_y_bit(reported_bit, b_correction):
    anti = sum(((p in "XY") and bool(Y0_Z_MASK >> q & 1)) +
               ((p in "ZY") and bool(Y0_X_MASK >> q & 1))
               for q, p in enumerate(b_correction)) % 2
    return reported_bit ^ Y0_WORD_SIGN ^ anti


def output_frame(y_bit):
    if y_bit not in (0, 1):
        raise ValueError("Logical Y outcome is a bit")
    return {"kind": "logical_Clifford", "register": "C", "logical_qubit": 0,
            "apply_order": ["SDG", "H"] if y_bit == 0 else ["H", "SDG", "H"],
            "implemented_as": "tracked_output_frame", "physical_correction_gates": 0,
            "corrected_target": "((1-i)|0>+|1>)/sqrt(3)",
            "spectator_logical_qubit": 1, "spectator_target": "0"}


def raw_y_amplitudes(y_bit):
    if y_bit not in (0, 1):
        raise ValueError("Logical Y outcome is a bit")
    return (gaussian(2, -1 if y_bit == 0 else 1), 1, 0, 0)


def exact_raw_y_target(y_bit):
    words = {0}
    for support in CHECK_SUPPORTS:
        h = sum(1 << q for q in support)
        words |= {w ^ h for w in tuple(words)}
    x0 = sum(1 << q for q in LOGICAL_X0)
    a, b, _, _ = raw_y_amplitudes(y_bit)
    weights = {f"{w:020b}"[::-1]: a for w in words}
    weights.update({f"{w ^ x0:020b}"[::-1]: b for w in words})
    return GaussianSparseState(tuple(f"C_{q}" for q in range(20)), weights)


def ideal_success_probability(magic_output):
    return "3/4" if magic_output == "y" else "5/8"
