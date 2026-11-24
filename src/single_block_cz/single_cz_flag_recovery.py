"""Flag-conditioned Pauli-data recovery, with a GLOBAL two-fault envelope.

Only X/Z code-stabilizer gadgets enter this table. No Pauli propagation is
performed through T gates. One fault outside the flagged gadget is allowed
an arbitrary Pauli on any ONE inner block (the existing coordinate-frame
normal form); two faults inside the gadget are also included. Reported flag
bits, never actual outcomes or injected/noise events, select the table.
"""
from collections import defaultdict
from functools import lru_cache
from itertools import product

import c4_helix_single_block_cz as m
from single_cz_compact_checks import data_program, data_flag_count
from single_cz_recovery import syndrome, remainder


def _tail(ops, start, x, z, reports=0):
    meter = sum(op == "MZ" for op, _ in ops[:start])
    for op, qs in ops[start:]:
        if op == "H":
            bit = 1 << qs[0]
            if (x ^ z) & bit:
                x ^= bit
                z ^= bit
        elif op == "CX":
            a, b = qs
            x ^= ((x >> a) & 1) << b
            z ^= ((z >> b) & 1) << a
        elif op == "PREP":
            x &= ~(1 << qs[0])
            z &= ~(1 << qs[0])
        elif op == "MZ":
            reports ^= ((x >> qs[0]) & 1) << meter
            meter += 1
            x &= ~(1 << qs[0])
            z &= ~(1 << qs[0])
        else:
            raise ValueError("Recovery table only propagates Clifford X/Z checks")
    return x, z, reports


@lru_cache(maxsize=None)
def local_signatures(axis, n, extraction="rolling_flags"):
    """All one-location Pauli/report signatures, including waiting idles.

Quantum measurement action and wrong report may occur at the SAME faulty
location. Global Pauli phases do not affect stabilizer-class decisions;
the proof keeps their arbitrary complex coefficients on conditioned paths.
"""
    if axis not in ("X", "Z") or n not in (4, 8):
        raise ValueError("Only actual four/eight-port Pauli code checks")
    ops = data_program(axis,n,extraction)
    keep, flags = (1 << n) - 1, (1 << data_flag_count(axis,n,extraction)) - 1
    result = {(0, 0, 0)}
    live = set(range(n))
    for i, (op, qs) in enumerate(ops):
        for q in sorted(live - set(qs)):
            for p in (1, 2, 3):
                x, z, r = _tail(ops, i, (p & 1) << q, (p >> 1) << q)
                result.add((x & keep, z & keep, r & flags))
        for axes in product(range(4), repeat=len(qs)):
            x = sum((p & 1) << q for p, q in zip(axes, qs))
            z = sum((p >> 1) << q for p, q in zip(axes, qs))
            for flip in range(2 if op == "MZ" else 1):
                r = flip << sum(name == "MZ" for name, _ in ops[:i])
                a, b, r = _tail(ops, i if op == "MZ" else i + 1, x, z, r)
                result.add((a & keep, b & keep, r & flags))
        if op == "PREP":
            live.update(qs)
        elif op == "MZ":
            live.difference_update(qs)
    return tuple(sorted(result))


def embed(word, support):
    return sum(((word >> j) & 1) << q for j, q in enumerate(support))


@lru_cache(maxsize=None)
def signature_groups(axis, support, extraction="rolling_flags"):
    if tuple(support) not in m.SUPPORTS:
        raise ValueError("No source-logical or arbitrary product recovery")
    groups = defaultdict(set)
    for x, z, f in local_signatures(axis, len(support),extraction):
        groups[f].add((embed(x, support), embed(z, support)))
    return {f: tuple(sorted(rows)) for f, rows in groups.items()}


def candidates(axis, support, flags, extraction="rolling_flags"):
    """Overcomplete physical error envelope AT a clean recovery reference.

Case A: one flagged-gadget fault, plus zero/one other fault anywhere. The
other fault's full one-inner-block algebra also includes late unflagged
recovery faults. Case B: both faults in this gadget, with XOR of their
reported flags equal to the observed vector. Same-location pairs are
overincluded, never used to justify a more permissive decision.
"""
    groups = signature_groups(axis, tuple(support),extraction)
    if not flags or flags >= 1 << data_flag_count(axis,len(support),extraction):
        raise ValueError("Nonzero, in-range flag word required")
    for x, z in groups.get(flags, ()):
        for block in range(5):
            for a, b in product(range(16), repeat=2):
                yield x ^ (a << (4 * block)), z ^ (b << (4 * block))
    for f, left in groups.items():
        for x, z in left:
            for a, b in groups.get(f ^ flags, ()):
                yield x ^ a, z ^ b


@lru_cache(maxsize=256)
def recovery_table(axis, support, flags, extraction="rolling_flags"):
    classes, best = defaultdict(set), {}
    for x, z in candidates(axis, tuple(support), flags,extraction):
        s = syndrome(x, z)
        classes[s].add((remainder(x), remainder(z)))
        if s not in best or ((x | z).bit_count(), x, z) < (
                (best[s][0] | best[s][1]).bit_count(), *best[s]):
            best[s] = x, z
    return {s: {"classes": len(cs), "correction": best[s] if len(cs) == 1 else None}
            for s, cs in classes.items()}


def decision(axis, support, flags, bits, extraction="rolling_flags"):
    if len(bits) != 18 or any(b not in (0, 1) for b in bits):
        raise ValueError("Expected eighteen reported code-check bits")
    row = recovery_table(axis, tuple(support), flags,extraction).get(sum(b << j for j, b in enumerate(bits)))
    return row if row is not None else {"classes": 0, "correction": None}
