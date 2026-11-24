# Proof: compact Pauli-check replacement

This is an additive replacement lemma for the
[one-block factory proof](full_procedure_single_block_cz_proof.md),
[flag-dependent recovery](single_block_cz_flag_dependent_recovery.md),
[bare-star extension](single_block_cz_bare_graph_stars.md) and
[ordered terminal screen](single_block_cz_terminal_screen.md).
It does not import the two-block SWAP theorem. The physical circuits and
costs are specified in the [integrated compact-check note](single_block_cz_compact_checks.md).

## 1. Physical model and scope

The global budget is at most two arbitrary faulty quantum locations in
the entire attempted factory, including preparations/resets, each H,
Pauli, S/Sdg, T/Tdg, CX, physical measurement/report location, correction,
waiting idle, resource retry and fallback. A gate location has precisely
the participants of the listed elementary gate. Classical processing is
reliable. There is no fresh budget upon a flag or stage transition.
An arbitrary local CPTP action, including an environment, is permitted
on faulty participants; reported outcomes may be wrong at a faulty
measurement. The simulation samples Pauli noise, while the theorem uses
the operator-span argument below.

Compact circuits replace ordinary post-source X/Z code checks only.
They do not replace controlled-W gadgets, graph checks, known-source
checks, the ordered screen, or conditional one-remaining-fault gadgets.

## 2. Ideal signed instrument

In the X circuit every CX has syndrome s as control. Each flag is
initialized zero and couples twice; the flag CXs commute with all data
CXs and cancel pairwise ideally. Discarding those identities leaves the
standard plus-controlled product-X parity measurement. Flag records are
zero and the syndrome-b Kraus operator is exactly
P_b=(I+(-1)^b X_support)/2, including its sign and normalization.

For Z, conjugate the entire X circuit by H on every wire. CNOTs reverse
direction. Syndrome preparation/readout become zero/Z; flags become
plus/X. The boundary H operations on the *data* conjugate X_support to
Z_support in the ideal instrument; the compiled Z circuit has no physical
data H. The resulting Kraus operator is exactly the corresponding Z P_b.
Moving a helper preparation to its first coupling or its destructive
measurement after its last coupling crosses only operations on other
wires and leaves this instrument unchanged.

Thus both replacements measure the same signed Pauli projectors as
before. Source logical X is not measured after preparation. Ideal CZ
sector probabilities and all W phases are unchanged.

## 3. Exhaustive local fault-cone certificate

`check_single_cz_compact_checks.py` calls the independent Clifford
signature propagator in `check_optimized_extraction.py` on each actual
X/Z, four/eight-port program. Each one-location basis action enumerates
all participant Paulis, destructive measurement/report combinations,
preparation errors, and waiting-data/helper idles. The identity is included.
Let a signature be (x,z,f), where f includes *reported* flag flips and
syndrome reports are deliberately unrestricted. Define

    w_S(x,z) = min(weight(x,z), weight((x,z) times S)).

The certificate checks:

* f=0 implies w_S<=1 for every one-location signature;
* f1=f2 implies w_S(E1 E2)<=2 for every signature pair.

All ordered same-location pairs are also included, a conservative
overapproximation. For eight ports there are 60 distinct signatures and
964 accepted equal-flag pairs per axis. For four ports there are 25 and
353. These are support/flag certificates, not full-factory pair counts.
An idle after the last gadget action is a single-site residual and obeys
the same bound. A spectator outside the support has no ideal propagation
into the gadget and contributes at most its own one physical site per
fault; arbitrary locations on those spectators are covered compositionally.

Modulo S is legitimate on each conditioned measurement branch: S has
fixed eigenvalue after the corresponding ideal projector. Faults that
flip that eigenvalue/report are retained in the signature expansion;
their scalar phases are not interpreted as probabilities or discarded.

All operations in these gadgets are Clifford. Expand each arbitrary
fault operator in the Pauli basis on its listed participants (and arbitrary
environment coefficients), commute each term through the actual gadget,
and condition on reported outcomes. The certificate bounds the complete
accepted operator span. It is not necessary to assume stochastic Pauli
faults or discard interference. The distance-six code corrects the span
of physical weight<=2 errors by Knill-Laflamme. No Pauli-XOR audit is
applied through any T-containing part of the factory.

## 4. Flag-dependent recovery certificate

A nonzero flag consumes at least one global fault. The existing
two-equal-complete-record rule within four conditional records therefore
still supplies a clean reference with at most one remaining fault.
Those conditional gadgets and their one-site residual bound are unchanged.

The new recovery table is indexed by extraction kind as well as axis,
support and flag word. It exhausts: (A) one exact compact-gadget fault
plus an arbitrary Pauli on any one inner block from an external fault;
(B) two exact compact-gadget faults with the observed XOR flag word.
Incoming data Paulis through a Pauli parity gadget do not spread to other
data sites or change its flag record. Thus the same external block
envelope used in the previous proof suffices. All flag/syndrome keys in
this envelope are materialized; only one stabilizer-equivalence class
admits correction. Missing and ambiguous keys reject.

The certificate constructs candidate signatures independently of the
production propagator, compares classes using four logical-commutation
bits independently of the production RREF reducer, and checks each
accepted candidate times its chosen correction against the explicit
stabilizer group. There are 88,944 accepted syndrome decisions and 608
ambiguous decisions across the eighteen new check tables. These counts
are not noise-weighted rejection probabilities. Corrections, faulty
fallbacks and epoch/history restarts retain the previous composition
argument; a changed flag alphabet never reuses the old table implicitly.

## 5. Factory composition

The preceding obligations are precisely the interfaces required by the
existing ordinary code-check histories and flag recovery: the same ideal
projector, at most one physical residual per zero-flag fault, and a complete
unique-class flag decoder with the same global budget. Substitute the
new certified local primitives into each ordinary Pauli-check occurrence.

The analytical enrichment/coordinate normal form still bounds one
upstream fault by an arbitrary one-inner-block algebra with graph and
environment coefficients. Code checks introduce no broader zero-flag
cone than before. The commuting bare-code histories still contain a
clean reference; no whole-family commutation of root/Gauss/data checks
is newly assumed. Three positive combined gauged certificates still
protect the logical sector against two false reports, and genuine negative
CZ branches cannot become certified by repetition alone. Final chord
repair, cut decoding, W byproducts and the outer-first terminal screen
are unchanged. Its full fallback uses the same certified ordinary-check
interface. Cat combined code/U histories receive the identical local
replacement, and retain their physical weight-two late-error guarantee.

Consequently, with at most two arbitrary faulty locations in the entire
chosen physical schedule, every accepted output decodes to the encoded
two-qubit CZ magic resource, with a residual in the correctable physical
weight<=2 operator span. This statement includes faults after the last
clean record and on physical correction gates under the existing proofs.
It assumes the prior source/graph/W/history/ungauging lemmas as cited;
the new finite audit does not independently enumerate those full circuits.

## 6. Limits of adaptive outer-check omission

The certificate supplies a two-inner-block witness for each omitted
outer check that passes every retained code check but is not equivalent
to weight<=2. This falsifies static omission under the current broad
envelope, even with noiseless remaining measurements. It does not falsify
all stage-specific adaptive schemes. A finer reachability certificate
for enrichment, coordinate changes and measurement faults would be a
separate proof obligation; none is claimed here.

## 7. Exact simulation regrouping

For basis helper a and factor ket F, the simulator replaces

    sum_(w,F) c_(w,F) |w> |F>

by the same sum with a's bit removed from w and appended to each factor's
computational coordinate. Coefficients and phases are unchanged. This
is a permutation of tensor labels and hence an identity on the represented
ket. CX/data actions and destructive projection use the resulting labels
exactly, returning the factor to twenty data labels on syndrome readout.
No physical instruction or noise opportunity is removed or inserted.
The regression compares exact cyclotomic amplitudes before/after the
regrouping and subsequent mixed-register gates and measurement branches.
