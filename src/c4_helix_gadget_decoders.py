"""Classical decoders for integrated V2 Sections 12, 15, and 16.

Only reported bits are used. No decoder receives the fault list or the true
measurement outcomes. Physical supports are imported from the Guppy circuit.
"""

from functools import lru_cache
from itertools import combinations, product

from c4_helix_noiseless import CHECK_SUPPORTS, EDGES, LOGICAL_Z0
from c4_helix_fault_runtime import RejectAttempt


def _bits(values, length):
    bits = tuple(int(value) for value in values)
    if len(bits) != length or any(bit not in (0, 1) for bit in bits):
        raise ValueError(f"Expected {length} binary reports")
    return bits


def decode_gauge(reports):
    """Unique graph cut within Hamming distance <=2; root bit t_a=0."""
    reports = _bits(reports, 20)
    candidates = []
    for nonroot in product((0, 1), repeat=4):
        offset = (0,) + nonroot
        cut = tuple((offset[u] + offset[v]) % 2 for u, v in EDGES)
        if sum(a != b for a, b in zip(reports, cut)) <= 2:
            candidates.append((cut, offset))
    if len(candidates) != 1:
        raise RejectAttempt("Gauge readout has no unique distance-two cut")
    cut, offset = candidates[0]
    return {"corrected_bits": cut, "offsets": offset}


def syndrome(paulis):
    """E's X-check signs followed by Z-check signs, each in s=0,...,8 order."""
    if len(paulis) != 20 or any(p not in "IXYZ" for p in paulis):
        raise ValueError("Expected a twenty-qubit Pauli")
    return tuple(sum(paulis[q] in "ZY" for q in support) % 2 for support in CHECK_SUPPORTS) + tuple(
        sum(paulis[q] in "XY" for q in support) % 2 for support in CHECK_SUPPORTS)


@lru_cache(maxsize=1)
def recovery_table():
    """Fixed minimum-weight representative: weight, position list, then X/Y/Z."""
    table = {}
    for weight in (0, 1, 2):
        for positions in combinations(range(20), weight):
            for axes in product("XYZ", repeat=weight):
                pauli = ["I"] * 20
                for q, axis in zip(positions, axes):
                    pauli[q] = axis
                table.setdefault(syndrome(pauli), "".join(pauli))
    return table


def recovery_from_history(records):
    """First identical triple in <=9 joint 36-bit rounds; otherwise wait/reject."""
    if not records or len(records) > 9:
        raise ValueError("Recovery needs between one and nine records")
    records = tuple(_bits(record, 36) for record in records)
    for end in range(2, len(records)):
        if records[end] == records[end - 1] == records[end - 2]:
            common = records[end]
            table = recovery_table()
            if common[:18] not in table or common[18:] not in table:
                raise RejectAttempt("No weight-at-most-two recovery matches the stopping record")
            return {"rounds_used": end + 1, "B": table[common[:18]], "C": table[common[18:]]}
    if len(records) == 9:
        raise RejectAttempt("Recovery did not reach three identical records by round nine")
    return None


@lru_cache(maxsize=1)
def _readout_table():
    table = {}
    for weight in (0, 1, 2):
        for positions in combinations(range(20), weight):
            check_bits = tuple(sum(q in positions for q in support) % 2 for support in CHECK_SUPPORTS)
            table.setdefault(check_bits, positions)
    return table


def decode_b_readout(reports):
    """Correct up to two bit reports before evaluating logical Z0.

    Ties are broken by minimum weight and lexicographic flipped-position list.
    """
    reports = _bits(reports, 20)
    check_bits = tuple(sum(reports[q] for q in support) % 2 for support in CHECK_SUPPORTS)
    table = _readout_table()
    if check_bits not in table:
        raise RejectAttempt("B readout has no weight-at-most-two correction")
    flips = table[check_bits]
    corrected = tuple((bit + (q in flips)) % 2 for q, bit in enumerate(reports))
    logical_bit = sum(corrected[q] for q in LOGICAL_Z0) % 2
    return {"corrected_bits": corrected, "flipped_positions": flips,
            "logical_bit": logical_bit, "keep": logical_bit == 0}
