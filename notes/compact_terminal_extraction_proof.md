# Proof for compact flagged terminal extraction

The original final Z extraction is retained in this proof. The new default
Y measurement and tracked Clifford frame are handled by
[the Y-output extension](magic_y_preparation_proof.md), which uses the
same compact-gadget locality results.

This supplements [the full procedure proof](full_procedure_reduced_rejection_proof.md)
for `--terminal-extraction compact_flagged` and the
[concrete gadget schedule](compact_terminal_extraction.md).
The same global at-most-two-fault assumption applies, including all idles,
wrong meter reports, single-qubit repairs, and protected fallback gates.

## 1. Ideal operation and data-error propagation

For a weight-four check, the two flag CNOTs cancel in the ideal circuit.
For a weight-eight check, both added adjacent-cat parities are +1 and
the reversed fanout returns the three non-root leaves to zero. The only
remaining meter is the syndrome ancilla in X. In either case, every ideal
flag is zero independently of the input data, and the data Kraus operator
for syndrome s is proportional to

\[
\Pi_s(Q)=\tfrac12(I+(-1)^sQ).
\]

An incoming Pauli on a data target propagates through a cP coupling only
to an ancilla Z component. Ancilla Z does not spread through later cP
couplings to other data. Thus an inherited data error keeps its support;
it may change the measured syndrome sign. All new data spread can be
charged to faults inside the gadget.

## 2. Exact local finite certificate

The primitive circuits are Clifford circuits with Pauli preparations and
meters. Push each injected Pauli through the remainder of the ideal
circuit. Record its final data masks (x,z) and the X flips on the flag
meters. A quantum or report fault on a meter is represented before its
destructive measurement. Each PREP, gate, meter, and each live
nonparticipating single-qubit idle is included. Pauli phases are irrelevant
for support and are not discarded by the quantum simulator.

For fixed flags f and at most two faults, the conditional data operation
can be expressed as a sum of terms EΠ_s(Q), with the selected syndrome
adjusted by the primary meter flip. Multiplying E by Q changes only a
scalar on that projected branch. Thus the relevant local physical cost is

\[
\min\{\operatorname{wt}(E),\operatorname{wt}(EQ)\}.
\]

The independent propagation routine in
[check_optimized_extraction.py](../src/check_optimized_extraction.py)
enumerates single-fault signatures. The new
[terminal audit](../src/check_compact_terminal.py) composes every pair,
including the overestimate of two errors at one location. Clifford
propagation makes composition the XOR of the propagated data masks and
flag flips. Equal signatures are merged without dropping possible errors.

The verified results for both X and Z are:

| Shape | Single signatures | Zero-flag pairs checked | Zero-flag physical cost |
|---|---:|---:|---|
| Weight four | 25 | 353 | ≤1 for one fault; ≤2 for two |
| Weight eight | 63 | 895 | ≤1 for one fault; ≤2 for two |

Faults on waiting data outside the check add one independent physical
position and are charged separately. Their combination with an internal
fault respects the same global budget.

Arbitrary local fault operators expand linearly in Pauli products.
Projecting the reported flags onto zero removes all terms with nonzero
flag signatures. Every surviving term has the stated support bound;
coefficients may act on an environment. This extends the certificate
beyond a stochastic Pauli assumption.

## 3. Certificate for the preliminary nonzero-flag repair

For each flag vector, collect every one- and two-fault data signature.
Apply the fixed repair specified in the procedure, then minimize the
number of occupied matched blocks over multiplication by Q.

For weight four, all data lie in one inner block, so the identity repair
has the required block bound. For weight eight, exactly 31 of the 32
flag vectors occur with at most two local faults. The sole absent vector
is word 19. Identity works for all reachable vectors except word 13;
word 13 is repaired by P on virtual data positions 2,3,4,5, the two
targets of each of leaves 1 and 2.

For every reachable vector, each repaired one-fault term occupies at
most one matched block and each repaired two-fault term at most two,
modulo Q. The audit checks 625 ordered signature pairs for each inner
axis and 3,969 for each upper axis, in addition to individual signatures.
It includes false flags, faults that hide flags, and data errors at the
same gate as an ancilla error. Word 19 rejection cannot occur under the
two-fault assumption.

The repair is executed as independent one-qubit Paulis. A fault on a
repair gate adds one local defect and cannot propagate an existing one.
For example, one gadget fault followed by one repair fault leaves at
most two affected matched blocks. A two-fault gadget leaves no remaining
fault budget for a faulty repair. The same reasoning includes waiting
faults during the repair.

As above, arbitrary local faults follow by Pauli expansion and linearity
for each fixed reported flag vector.

## 4. Composition without a flagged fallback

Every compact gadget on such an accepted path has zero flags. The full
commuting-record history supplies a clean reference round by the existing
triple or adaptive lemma. At that reference, inherited errors occupy at
most two common matched labels: upstream errors satisfy the old bound,
and each earlier zero-flag terminal fault adds at most one physical
position per fault.

The original joint B/C lookup therefore contains every actual candidate
term. If it accepts one stabilizer-equivalent correction class, its
chosen Pauli removes the inherited error at the reference. After the
reference, each zero-flag compact gadget adds at most one physical error
per fault, modulo a measured stabilizer. Stabilizers can be commuted
through inherited Paulis with only a sign change. This is precisely the
late-error argument in Section 9.4 of the original proof.

Independent noisy correction gates add only local errors. The residual
physical weight is at most the remaining global fault budget, hence at
most two per copy. The original final-B readout argument then applies.

## 5. Composition with a flagged fallback

All compact checks before the first flag have zero flags and the bound
above. The flagged check, followed by its certified preliminary repair,
adds at most one matched block per local fault. Every measured Q is an
original-code stabilizer. Its projector preserves each underlying logical
state in the existing span K after commuting through the Pauli errors.

Consequently, when protected acquisition begins, each term is a Pauli
error on at most two common matched labels multiplying a logical state
in K. This is the original terminal recovery's input invariant. No clean
compact reference round is needed for this fallback argument, and no
logical state has been discarded or re-prepared.

Protected acquisition starts a fresh complete classical history on the
same quantum data. It supplies a clean reference, the unchanged joint
lookup removes its inherited candidate error when unambiguous, and its
late faults have the old one-physical-position-per-fault bound. Thus an
accepted protected fallback has the same residual physical-weight and
decoded-C guarantees as the original procedure. If the cycle was not
SWAP-certified, this also preserves K for the existing re-gauging argument.

Only the first nonzero compact flag is handled in each terminal stage;
the rest of that stage uses protected gadgets. There is no infinite local
retry loop. A new gauging cycle, if required by the old controller, may
start a new compact terminal stage under the same global fault budget.

## 6. Scope

Together these arguments preserve the original accepted-output theorem
with at most two faulty locations in the entire schedule. Noiseless flags
are always zero, so the intrinsic ideal acceptance remains 5/8.

They do not guarantee fidelity one for every unrestricted noisy trajectory.
Nonzero flags may invoke an expensive protected pass, and acceptance can
still be limited by genuine joint ambiguity or other existing selections.
The finite enumeration is local to the four small gadget programs; the
full-factory conclusion uses the composition argument above.
