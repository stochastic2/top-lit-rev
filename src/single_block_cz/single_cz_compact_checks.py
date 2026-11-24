"""Compact two-fault flagged Pauli checks; no T gates or data basis changes.

Eight-port X check: after data port j, couple s to f[j % 4]. Each flag
therefore brackets four consecutive ports. Four-port checks retain the
certified single flag bracketing the middle two ports. Z checks use the
Hadamard dual on ALL wires: data controls and plus-prepared flag controls
couple into a zero-prepared syndrome target, with X readout of the flags.
"""
from single_cz_flagged import flagged_program, flag_count


def compact_pauli_program(axis, n):
    if axis not in ("X", "Z") or n not in (4, 8):
        raise ValueError("Only actual four/eight-port Pauli data checks")
    s = n
    ops = [("PREP", (s,))]
    if axis == "X":
        ops.append(("H", (s,)))

    def couple(q):
        return ("CX", (s, q) if axis == "X" else (q, s))

    for j in range(n):
        ops.append(couple(j))
        if n == 8:
            f=n + 1 + j % 4
            if j<4:
                ops.append(("PREP", (f,)))
                if axis=="Z":ops.append(("H", (f,)))
            ops.append(couple(f))
            if j>=4:
                if axis=="Z":ops.append(("H", (f,)))
                ops.append(("MZ", (f,)))
        elif j in (0, 2):
            if j==0:
                ops.append(("PREP", (n+1,)))
                if axis=="Z":ops.append(("H", (n+1,)))
            ops.append(couple(n + 1))
            if j==2:
                if axis=="Z":ops.append(("H", (n+1,)))
                ops.append(("MZ", (n+1,)))
    if axis == "X":
        ops.append(("H", (s,)))
    return ops + [("MZ", (s,))]


def data_program(axis, n, extraction="rolling_flags"):
    if extraction == "compact_flags":
        return compact_pauli_program(axis, n)
    if extraction == "rolling_flags":
        return flagged_program((axis,) * n)
    raise ValueError("Unknown Pauli-data extraction: " + str(extraction))


def data_flag_count(axis, n, extraction="rolling_flags"):
    if extraction == "compact_flags":
        return 1 if n == 4 else 4
    if extraction == "rolling_flags":
        return flag_count((axis,) * n)
    raise ValueError(extraction)
