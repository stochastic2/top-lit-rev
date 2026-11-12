"""Classical decoding routines for the postselected single-cycle factory.

All bits are 0 for reported +1 and 1 for reported -1 (or Z outcome |1>).
These functions consume reports, never an oracle telling whether a round
was fault-free. They make no quantum operations. See the companion note
for the physical schedule and global two-fault assumptions.
"""
from itertools import combinations, product
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
_source = (ROOT / 'arXiv-2609.03194v1/appendix.tex').read_text()
_table = _source.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
_rows = []
for _line in _table.splitlines():
    _symbols = re.findall(r'\$(X|Z|\\cdot)\$', _line)
    if len(_symbols) == 20:
        _rows.append(sum(1 << q for q, s in enumerate(_symbols) if s != r'\cdot'))
H = tuple(_rows[:9])
LOGICAL_Z0 = _rows[22]
VERTICES = 'abcde'
EDGE_ENDPOINTS = {q: tuple(i for i, s in enumerate(_rows[5:10]) if s >> q & 1)
                  for q in range(20)}


class RejectAttempt(ValueError):
    """The reported history does not meet the acceptance rule."""


def _bits(values, length=None):
    out = tuple(values)
    if (length is not None and len(out) != length) or any(b not in (0, 1) for b in out):
        raise ValueError('Expected a binary report of the prescribed length')
    return out


def _word(values):
    return sum(b << q for q, b in enumerate(values))


def require_positive(values):
    """Apply to all cat-verification bits and all positive-check reports."""
    if any(_bits(values)):
        raise RejectAttempt('A required positive verification report was negative')


def require_three_gauged_sweeps(sweeps, include_dressed=False):
    """Each sweep has 34 central and 5 Gauss bits.

    The optional full-check variant appends 9 dressed-X and 9 dressed-Z.

    The caller must additionally pass every helper's raw cat-verification
    reports to require_positive before using that helper.
    """
    sweeps = tuple(sweeps)
    if len(sweeps) != 3:
        raise ValueError('The scheduled protocol requires three complete gauged sweeps')
    for sweep in sweeps:
        require_positive(_bits(sweep, 57 if include_dressed else 39))


def require_three_original_sweeps(sweeps):
    sweeps = tuple(sweeps)
    if len(sweeps) != 3:
        raise ValueError('Three terminal original-code sweeps are required')
    for sweep in sweeps:
        require_positive(_bits(sweep, 36))


def vertex_frame(reported_x_bits):
    """Initial vertex-X sign bits -> gauge-Z sign-fixing gate labels."""
    bits = _bits(reported_x_bits, 5)
    if sum(bits) % 2:
        raise RejectAttempt('Initial reported whole-block SWAP parity is negative')
    tree = {1: 7, 2: 11, 3: 3, 4: 0}
    return tuple(tree[v] for v in range(1, 5) if bits[v])


def _cut(t):
    return sum((((t >> u) ^ (t >> v)) & 1) << q for q, (u, v) in EDGE_ENDPOINTS.items())


_CUTS = {_cut(t): t for t in range(32) if not t & 1}


def decode_gauge_z(reported_bits):
    """Return the corrected cut and physical SWAP labels, or reject."""
    m = _word(_bits(reported_bits, 20))
    candidates = [w for w in _CUTS if (m ^ w).bit_count() <= 2]
    if len(candidates) != 1:
        raise RejectAttempt('Gauge word has no unique cut within distance two')
    w = candidates[0]
    t = _CUTS[w]
    return {
        'corrected_cut_bits': tuple(w >> q & 1 for q in range(20)),
        'vertex_offset_bits': tuple(t >> v & 1 for v in range(5)),
        'swap_pair_labels': tuple(q for q in range(20) if t >> (q // 4) & 1),
    }


def syndrome(x, z):
    """One block: X-check bits first, then Z-check bits, s=0..8."""
    return tuple((z & h).bit_count() % 2 for h in H) + tuple((x & h).bit_count() % 2 for h in H)


def _small_paulis():
    yield 0, 0
    for weight in (1, 2):
        for positions in combinations(range(20), weight):
            for labels in product(((1, 0), (0, 1), (1, 1)), repeat=weight):
                yield (sum(a << q for q, (a, b) in zip(positions, labels)),
                       sum(b << q for q, (a, b) in zip(positions, labels)))


_RECOVERY = {}
for _x, _z in sorted(_small_paulis(), key=lambda e: ((e[0] | e[1]).bit_count(), e[0], e[1])):
    _RECOVERY.setdefault(syndrome(_x, _z), (_x, _z))


def recovery_from_reports(rounds):
    """Decode the first equal triple in at most nine 36-bit joint rounds.

    Return None when more reports are needed. The caller applies each
    returned Pauli only after stopping, using single-qubit corrections.
    """
    rounds = tuple(_bits(r, 36) for r in rounds)
    if len(rounds) > 9:
        raise ValueError('At most nine recovery rounds are scheduled')
    for i in range(2, len(rounds)):
        if rounds[i] == rounds[i-1] == rounds[i-2]:
            s = rounds[i]
            if s[:18] not in _RECOVERY or s[18:] not in _RECOVERY:
                raise RejectAttempt('No weight-at-most-two Pauli matches the stopping syndrome')
            return {'rounds_used': i+1, 'B_XZ_masks': _RECOVERY[s[:18]],
                    'C_XZ_masks': _RECOVERY[s[18:]]}
    if len(rounds) == 9:
        raise RejectAttempt('No equal syndrome triple by the recovery limit')
    return None


_READOUT = {}
for _weight in range(3):
    for _qs in combinations(range(20), _weight):
        _e = sum(1 << q for q in _qs)
        _s = tuple((_e & h).bit_count() % 2 for h in H)
        _READOUT.setdefault(_s, _e)


def decode_B_readout(reported_bits):
    """Return decoded logical-Z0 bit and keep flag; spectators are unused."""
    m = _word(_bits(reported_bits, 20))
    s = tuple((m & h).bit_count() % 2 for h in H)
    if s not in _READOUT:
        raise RejectAttempt('B readout has no weight-at-most-two correction')
    corrected = m ^ _READOUT[s]
    logical_bit = (corrected & LOGICAL_Z0).bit_count() % 2
    return {'logical_Z0_bit': logical_bit, 'keep': logical_bit == 0}
