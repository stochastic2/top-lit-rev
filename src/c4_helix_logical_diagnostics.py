"""Exact, read-only ideal decoding of the final twenty-qubit C wavefunction.

This is a diagnostic, not a noiseless recovery secretly inserted into the
physical circuit. Every original syndrome is decoded: minimum-weight <=2
when available, otherwise a fixed GF(2) pure-error correction. A Walsh
transform resolves X syndromes while retaining all four logical amplitudes.
No sampled fault list or actual measurement oracle enters this calculation.
"""

from fractions import Fraction
from functools import lru_cache

from c4_helix_noiseless import CHECK_SUPPORTS, LOGICAL_X0, LOGICAL_Z0, LOGICAL_Z1
from c4_helix_gadget_decoders import recovery_table
from gaussian_integer import conjugate, abs_squared


def mask(positions):
    return sum(1 << q for q in positions)


H = tuple(map(mask, CHECK_SUPPORTS))
X0, X1, Z0, Z1 = map(mask, (LOGICAL_X0, LOGICAL_Z0, LOGICAL_Z0, LOGICAL_Z1))


def component_syndrome(v):
    return sum(((v & h).bit_count() % 2) << j for j, h in enumerate(H))


@lru_cache(maxsize=1)
def right_inverse():
    rows = [[h, 1 << j] for j, h in enumerate(H)]
    pivots = []
    for q in range(20):
        used = len(pivots)
        found = next((j for j in range(used, 9) if rows[j][0] >> q & 1), None)
        if found is None:
            continue
        rows[used], rows[found] = rows[found], rows[used]
        for j in range(9):
            if j != used and rows[j][0] >> q & 1:
                rows[j][0] ^= rows[used][0]
                rows[j][1] ^= rows[used][1]
        pivots.append(q)
        if len(pivots) == 9:
            break
    if len(pivots) != 9:
        raise ArithmeticError("Original check supports are not independent")
    return tuple((q, rows[j][1]) for j, q in enumerate(pivots))


def solve_component(s):
    return sum(((rhs & s).bit_count() % 2) << q for q, rhs in right_inverse())


@lru_cache(maxsize=1)
def stabilizer_coordinates():
    coordinates = {0: 0}
    for j, h in enumerate(H):
        coordinates.update({w ^ h: u | (1 << j) for w, u in list(coordinates.items())})
    if len(coordinates) != 512:
        raise ArithmeticError("Expected 512 original X-stabilizer words")
    return coordinates


@lru_cache(maxsize=1)
def small_corrections():
    result = {}
    for report, axes in recovery_table().items():
        s = sum(b << j for j, b in enumerate(report))
        result[s] = (mask(q for q, p in enumerate(axes) if p in "XY"),
                     mask(q for q, p in enumerate(axes) if p in "ZY"))
    return result


def walsh(values):
    """Unnormalized exact transform; values are indexed by H-generator bits."""
    step = 1
    while step < len(values):
        for start in range(0, len(values), 2*step):
            for j in range(start, start + step):
                a, b = values[j], values[j+step]
                values[j], values[j+step] = a+b, a-b
        step *= 2


def decoded_c_diagnostics(state, max_sector_details=128, magic_output="z", y_outcome=None):
    if state.labels != tuple(f"C_{q}" for q in range(20)):
        raise ValueError("Logical diagnostics require the twenty final C coordinates")
    state.validate()
    if max_sector_details < 0:
        raise ValueError("Sector detail limit must be nonnegative")
    norm = state.norm_squared()
    target = (2, 1, 0, 0)
    if magic_output == "y":
        from c4_helix_magic_y import raw_y_amplitudes
        target = raw_y_amplitudes(y_outcome)
    elif magic_output != "z":
        raise ValueError("Magic output is y or z")
    target_norm = sum(abs_squared(a) for a in target)
    coordinates = stabilizer_coordinates()
    logical_x = (0, X0, X1, X0 ^ X1)
    groups = {}
    amplitude_by_mask = {}
    for word, amplitude in state.weights.items():
        w = int(word[::-1], 2)
        amplitude_by_mask[w] = amplitude
        z_syndrome = component_syndrome(w)
        base = solve_component(z_syndrome)
        c = w ^ base
        logical = ((c & Z0).bit_count() % 2) | (((c & Z1).bit_count() % 2) << 1)
        h = c ^ logical_x[logical]
        if h not in coordinates:
            raise ArithmeticError("Physical word does not decompose into the specified CSS logical basis")
        vectors = groups.setdefault(z_syndrome, [[0]*512 for _ in range(4)])
        vectors[logical][coordinates[h]] += amplitude
    target_numerator = probability_numerator = small_probability_numerator = 0
    active = 0
    details = []
    table = small_corrections()
    for z_syndrome, vectors in sorted(groups.items()):
        base = solve_component(z_syndrome)
        for vector in vectors:
            walsh(vector)
        for x_syndrome in range(512):
            amplitudes = [v[x_syndrome] for v in vectors]
            sector_norm = sum(abs_squared(a) for a in amplitudes)
            if not sector_norm:
                continue
            active += 1
            s = x_syndrome | (z_syndrome << 9)
            if s in table:
                rx, rz = table[s]
                decoder = "minimum_weight_at_most_two"
                small_probability_numerator += sector_norm
            else:
                rx, rz = base, solve_component(x_syndrome)
                decoder = "fixed_GF2_pure_error_fallback"
            delta = base ^ rx
            logical_flip = ((delta & Z0).bit_count() % 2) | (((delta & Z1).bit_count() % 2) << 1)
            corrected = [0]*4
            for l, a in enumerate(amplitudes):
                sign = -1 if (rz & (base ^ logical_x[l])).bit_count() % 2 else 1
                corrected[l ^ logical_flip] = sign*a
            contribution = abs_squared(sum(conjugate(t)*a for t, a in zip(target, corrected)))
            target_numerator += contribution
            probability_numerator += sector_norm
            if len(details) < max_sector_details:
                details.append({"syndrome_XZ": [(s >> j) & 1 for j in range(18)],
                                "probability": str(Fraction(sector_norm, 512*norm)), "decoder": decoder,
                                "decoded_target_fidelity_in_sector": str(Fraction(contribution, target_norm*sector_norm))})
    if probability_numerator != 512*norm:
        raise ArithmeticError("Ideal syndrome probabilities do not sum to one")
    fidelity = Fraction(target_numerator, target_norm*512*norm)
    if not 0 <= fidelity <= 1:
        raise ArithmeticError("Decoded fidelity is outside the physical range")
    raw_overlap = sum(conjugate(target[0])*amplitude_by_mask.get(h, 0) + conjugate(target[1])*amplitude_by_mask.get(h ^ X0, 0)
                      for h in coordinates)
    small_probability = Fraction(small_probability_numerator, 512*norm)
    result = {"decoder": "perfect original syndrome measurement; fixed <=2 lookup, then GF2 fallback",
            "diagnostic_only": True, "decoded_target_fidelity": str(fidelity),
            "decoded_target_infidelity": str(1-fidelity), "decoded_target_is_exact": fidelity == 1,
            "raw_physical_target_fidelity": str(Fraction(abs_squared(raw_overlap), target_norm*512*norm)),
            "probability_in_weight_two_lookup": str(small_probability),
            "probability_outside_weight_two_lookup": str(1-small_probability),
            "active_syndrome_sectors": active, "syndrome_probability_sum": "1",
            "sector_details": details, "sector_details_truncated": active > len(details)}
    if magic_output == "y":
        from c4_helix_magic_y import output_frame
        result.update(magic_output="y", logical_y_outcome=y_outcome, output_clifford_frame=output_frame(y_outcome),
                      fidelity_target="corrected logical |m_Y>|0> in the recorded Clifford frame")
    return result
