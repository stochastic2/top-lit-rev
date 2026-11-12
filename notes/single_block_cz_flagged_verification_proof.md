# One-block CZ verification with syndrome ancillas and rolling flags

The strict policy proved here remains `--flag-recovery reject`. The
[flag-dependent recovery extension](single_block_cz_flag_dependent_recovery.md)
proves the opt-in `--flag-recovery data` schedule, including conditional
one-remaining-fault gadgets, phase-safe table decisions and history resets.

This is the proof extension for the default recovery simulator:
`--verification-extraction flags --source-extraction rolling_flags`.
It replaces the separately prepared/verified cats in source, data, star,
root-Gauss and terminal checks. Edge-Z cycle checks use direct parity
meters. The [cut-subspace graph verifier](full_procedure_single_block_cz_proof.md#c3-known-source-and-graph-verification)
and the [recovery controller](single_block_cz_simulation_recovery_proof.md)
otherwise keep their ordering, decoder and history rules.

The physical alphabet remains PREP0, H/S/S†/Paulis, T/T†, CX, MZ and
explicit serial/boundary idles. Every T/CX/T† is three separate locations.
Faults may act arbitrarily on a location's participants; measurement faults
include quantum action and arbitrary wrong reports. Classical computation
is reliable. **At most two locations globally** may be faulty, including
all failed source/graph attempts, corrections and helper reinitializations.

## Exact primitive and ideal instrument

Let Q=product_j Q_j have m disjoint physical ports, with Q_j one of X,
Z or the signed single-qubit Clifford involution W'_j. Prepare syndrome
s in |+>. At port j execute CX(s,target) for X, H(target), CX, H for Z,
and T^epsilon(target), CX, T^-epsilon for W'. The sign epsilon is exactly
the canonical physical pattern, including D conjugation; no controlled
phase is discarded. An ideal X readout of s measures Q, with instrument

    K_b = (I + (-1)^b Q)/2.

This measures a product observable; it does not apply Q deterministically.

For the rolling gadget, prepare f0,f1 in zero and apply CX(s,f0), CX(s,f1).
For j=0,...,m-1:

1. Execute the physical target port j.
2. If j<m-1, prepare f_(j+2) in zero, apply CX(s,f_(j+2)), then
   CX(s,f_j), and read f_j in Z.

After the last port, close and Z-read f_(m-1), then f_m. Finally apply
H(s), MZ(s). Readouts preceding the last one are flags, in increasing
logical index. There are m+1 flags, **at most three live flags**, and
one syndrome qubit. Physical flag slot j mod 3 is reused only after its
previous destructive measurement and a fresh preparation.

The active flags during port j are {j,j+1}. Between ports, the next flag
opens before the oldest closes. Ideal controlled ports never change s's
computational bit, so all flags uncompute to zero without disturbing the
data; the ideal instrument above is exact. Small flags are temporarily
entangled with s (GHZ-type correlations can occur). The claim is absence
of a separate many-leaf cat preparation/verification resource, not absence
of ancilla entanglement.

For a uniform four-port Pauli check, use the cheaper special case:
PREP0(s), PREP0(f), H(s), port0, CX(s,f), port1, port2, CX(s,f), port3,
MZ(f), H(s), MZ(s). It costs six CX. The generic rolling circuit costs
m target CX plus 2(m+1) flag CX = 3m+2 CX; Z basis changes and T gates
are counted separately. Both variants are explicit in
`src/single_cz_flagged.py`.

## Accepted local spread with one or two faults

The bound is conditional on **reported flags all zero**. A fault can still
change the reported syndrome or the I/Q branch; correctness is not inferred
from a single noisy syndrome bit.

Track a controller X/Y component on s. It appends the exact involution Q_j
to each later port it crosses. Z/I components change the conditional branch
coefficients but do not append a hook. Flag X/Y components flip their own
Z readout; flag Z components may change s's phase. A physical fault on a
target port supplies an arbitrary local operator on that port, including
coherent sums from the T decomposition. Moving an operator through Q_j
preserves that port's support. It need not remain a single Pauli.

Consequently a Pauli-basis term at each helper/gate/readout fault has:

- A set A of directly damaged target ports.
- A hook mask h, denoting product_(j in h) Q_j.
- A flag-flip vector f.
- Unrestricted complex branch coefficients and an I/Q choice.

For two terms, A combines by union, hooks by symmetric difference (the
disjoint Q_j commute and square exactly to I), and flag flips by XOR.
This is **not Pauli-XOR propagation through T**. Local port operators
are opaque algebras and every coefficient is retained in the simulator.

The active-flag sets along the syndrome worldline are distinct except
across one target port; the empty set occurs at the two ends. Opening or
closing a flag has two endpoint signatures, since a fault can flip both
s and that flag at the same CX. The finite support audit includes both,
every target T/CX/T† and Z-basis H, every waiting-qubit idle, preparation,
and a quantum Pauli together with a report flip at a faulty readout.

For every one-fault signature with f=0, and every pair whose flags cancel,
the audit certifies

    min(|A union h|, |A union (h XOR all_ports)|) <= k,
    k = 1 or 2 respectively.

Thus the residual operator, **modulo Q**, acts on at most k target ports.
Multiplication by Q changes P_+/-Q only by its eigenvalue. Commuting Q
past a local target error conjugates only that target. These reductions
retain the arbitrary complex coefficients and apply to every conditioned
measurement branch. Pauli expansion on each actual faulty location and
linearity extend the support result to arbitrary local quantum actions.

`check_single_cz_flags.py` audits every actual arity (4,5,6,8,10,12,20),
both Pauli axes, mixed four-W root checks and twenty-W direct checks.
All single signatures and all matching-flag signature pairs are checked;
pairs at one location are overincluded. The Clifford subcases also use an
independent symplectic propagator. Dense complex tests independently check
a mixed-W ideal Kraus operator and every local Pauli at its T/CX/T† and
flag-CX gates against the predicted one-port operator span. These dense
tests are numerical spot checks; the local support certificate and the
analytical reduction supply the proof, not Monte Carlo.

## Direct edge-Z cycle meters

For a graph cycle, prepare w in zero, apply CX(A_e,w) in the specified
cycle order, and Z-read w. No flags are needed here. A meter Z may spread
Z over several graph edges; these commute with V and remain allowed graph
phases. Each faulty gate or idle adds at most one resource bit-error site,
which controls at most one data inner block. A wrong report is handled by
the unchanged certified commuting cycle history. This shortcut is **not**
used for data Z stabilizers or X stars.

## Global accepted-output theorem and controller decisions

With at most two faulty locations in the entire flagged schedule, every
accepted output decodes to |CZ_magic>, with residual error in the span
of physical Paulis of weight at most two.

The composition is the existing recovery proof with the following local
replacements:

1. A used flagged gadget has zero reports on all flags; otherwise the
   controller does not accept that data path. Its local spread is at most
   one target port per fault, modulo the measured product, by the lemma.
2. In V coordinates, each port is one physical data site or one edge
   controlling one inner block. Root Q becomes U Xstar_a; its I/Q choices
   preserve the same I/U logical span. The block-supported invariant and
   the separate three-passing-complete-round certificate therefore hold.
3. A clean Pauli acquisition is an ordinary commuting QND syndrome
   acquisition. The triple/adaptive history hypotheses are unchanged;
   the noncommuting dressed/root family is still certified only through
   complete passing rounds.
4. At a clean terminal reference, the unique-class decoder removes inherited
   block errors. Later flagged Pauli gadgets have at most one physical
   data site per faulty location, modulo a code stabilizer. Individual
   correction gates and final boundary idles preserve the weight-two span.

A nonzero source flag rebuilds **only the known unused source**, using the
same two shared source/graph retry tokens. The circuit finishes all helper
readouts before retrying. A nonzero flag after enrichment rejects the whole
attempt; it never resets an unknown magic block and never falls back to a
cat gadget. A nonzero syndrome with zero flags still uses certified recovery.
Source logical X operators are absent after source preparation.

The direct-measurement comparator uses exactly the same flagged source and
code gadgets and a twenty-port flagged U measurement, with three passing
combined code/U rounds. Its historical CLI route name remains `direct_cat`,
but with flag extraction it prepares no twenty-leaf cat.

This theorem does not promise acceptance under two faults, nor high yield
under unrestricted stochastic noise. Strict flag rejection can trade yield
against lower gate count; it must be benchmarked. No full-factory location
pair enumeration or matched-fidelity performance claim is made.
