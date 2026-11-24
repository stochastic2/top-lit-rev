# Recovery-profile extension of the single-block CZ proof

The default recovery mode uses flagged product measurements, proved in
[the flagged extension](single_block_cz_flagged_verification_proof.md).
It has no separately prepared verification cats; small flags are temporarily
entangled with the syndrome ancilla. Nonzero post-source flags reject.
The `cats` extraction option retains the original gadgets described in
Sections 3 and 4 below. Their locality premise is replaced in default mode
by the zero-flag one-port-per-fault lemma; all global budgets, histories
and decoder decisions in the composition remain the same.

This extends the [conservative proof](full_procedure_single_block_cz_proof.md)
for `SimulationController(..., profile="recovery")`. The conservative
controller and its original files remain available. The physical gate
alphabet is unchanged: every controlled W is T/CX/T† at three independent
locations, every controlled Z is H/CX/H, and all corrections are noisy
single-qubit gates. The same **global at-most-two arbitrary faulty locations**
model includes resets, unsuccessful known-resource preparations, flags,
readout reports and serial/boundary idles. No stage receives a new allowance.

The new simulator samples independent Pauli channels without imposing this
fault-count bound. The theorem below consequently does not predict perfect
conditional fidelity on every noisy trajectory. Its full-circuit quantum
evolution retains the coherent phases of the elementary T decomposition.

## 1. Statement

For either compact13 or current20, every accepted recovery-profile gauging
output under the global two-fault model belongs to the correctable span of
weight-at-most-two physical errors on the encoded two-qubit CZ magic state.

The changes covered are:

- Decoded source flags before enrichment, with known-source rebuilds.
- Two initially zero cat scans, otherwise certified cat-syndrome repair.
- Certified source sign correction and on-demand data/cycle recovery.
- Three direct all-zero graph Z-parity scans, with local graph rebuilds.
- Deferring the reported vertex parity to combined gauged certification.
- Three passing complete gauged rounds within five, followed by one
  certified terminal code-syndrome acquisition and physical correction.

The theorem is analytical with the finite premises in
[`check_single_cz_recovery.py`](../src/check_single_cz_recovery.py).
It is not an exhaustive enumeration of all noisy factory location pairs.

## 2. Commuting reference histories: exactly where they apply

The adaptive five-record rule from the SWAP implementation requires:
two adjacent rounds without new faulty locations report the same complete
vector. This holds for each of the following separately:

| Acquisition | Measured operators | Why QND |
|---|---|---|
| Cat repair | Adjacent ZZ on the leaves | All commute; no leaf correction until certification |
| Known data source | Nine Z, nine X, two logical X checks | Twenty commuting source stabilizers |
| Data recovery in V coordinates | Eighteen bare code stabilizers | Globally commuting Paulis; no Gauss measurement inside acquisition |
| Cycle recovery | The complete graph-cycle Z vector | Globally commuting; no edge correction until certification |
| Terminal recovery | Eighteen original code stabilizers | Globally commuting; source logical X operators are absent |

An incoming error need not have a definite syndrome. A clean complete
round measures it projectively; a consecutive clean round preserves that
outcome. This establishes the hypothesis even for coherent input errors.
Cat repair operates only on unused helpers and does not change this
conclusion for a clean data-extraction round.

For adaptive history, every adjacent record change must have a faulty
round at one endpoint. Enumerate all such bad-round covers of size at
most two. Select a vector only if none of the covers contains all its
occurrences. The selected **value** therefore occurred in a clean round;
the last occurrence need not itself have been clean. The finite certificate
checks all 52 five-record equality patterns and 197 compatible placements.

The default `triple` policy uses the first three consecutive identical
whole records, with a nine-round cap. At most two faulty rounds imply
one clean occurrence of that vector. Between faulty rounds the clean
records are constant; nine rounds suffice to obtain a triple under the
two-fault assumption. At unrestricted noise the acquisition may reject
after nine rounds. This rejection is a physical control decision, not
a computational failure.

Neither rule is applied to the entire dressed data/Gauss family. The
root Gauss check commutes with dressed X checks only in the Z-positive
sector, as derived in the original proof. The simulator never invokes
the old paired B/C history or joint B/C decoder.

Graph preparation uses a separate fixed rule, independent of the selected
history policy: three complete zero scans of L_e=Z_(a_u)Z_(A_e)Z_(a_v).
Each check is PREP0(w), CX(a_u,w), CX(A_e,w), CX(a_v,w), MZ(w).
A nonzero scan rebuilds the unused graph using a shared retry token.
There are no preparation-stage K_v checks, cats or graph sign corrections.
The detailed [C3 lemma](full_procedure_single_block_cz_proof.md#c3-known-source-and-graph-verification)
replaces the previous rank-one reference with the rank-32 cut subspace.
It proves that arbitrary graph phases leave only I/U logical branches:
V Omega |t,dt>|psi> = |t,dt> U^(t_a)|psi>. Late meter faults produce at
most one resource bit-error site per fault, with arbitrary Z support.
The CNOT direction and the later combined Gauss certificate are essential.

## 3. Retained cat option: shortcut and physical repair

The raw cat and adjacent-parity circuit are identical to the old Clifford
preparation primitive. All actual preparations, CNOTs, meters and waiting
qubits remain physical locations.

If its first two complete scans report zero, the finite bit-spread audit
establishes at most k incorrect leaves, modulo simultaneous X on all leaves,
for k<=2 actual faults. A broad raw-chain hook consumes a fault; another
fault cannot hide it from both otherwise clean scans. Cases where both
scans contain faults instead have a clean raw preparation and at most
one added leaf bit per fault. Arbitrary cat phase is still allowed.

Otherwise acquire a certified commuting ZZ vector, then choose root bit
r0=0 and r_(j+1)=r_j XOR syndrome_j. Apply X on every indicated leaf.
At a clean reference this removes the cat bit syndrome, up to full-cat X.
Later parity-gadget/correction faults add at most one leaf bit per fault.
Wrong cat phase changes the conditional I/Q combination or report; it
does not justify claiming that a used cat is certainly GHZ+.

Every protected target still has its own leaf, including the four W
targets in each root Gauss gadget. The phase-sensitive one-port argument
from the original proof therefore applies unchanged. No XOR propagation
through T gates is assumed. The finite Clifford audit covers cat sizes
2,3,4,5,6,7,8,9,10,12,20, including the new current20 gadgets.

## 4. Retained decoded-source option and the default flagged source

The default `rolling_flags` source uses the same one-syndrome flag
primitive as terminal checks, for all twenty source operators. A flag
finishes all helper readouts and then rebuilds only the known source.
Its post-reference spread is physical one-site-per-fault modulo a source
stabilizer. The earlier `decoded_flags` option remains available:

Group a source Pauli check by occupied inner blocks. The allowed shapes
are one block with four targets, three blocks with two each (logical X),
or four blocks with two each (outer checks). Prepare one leaf per group,
fan out from L0, couple one target from every group before the next port
position, then undo fanout in reverse order. Read nonroot leaves in Z
as flags and L0 in X as syndrome. Z ports execute actual H/CX/H gates.

For a used zero-flag gadget, the finite audit shows at most one occupied
inner block per faulty location, modulo the measured source stabilizer.
The audit explicitly expands the H/CX/H Z ports and includes their
individual gate/idle faults. It checks all single signatures and all
zero-flag pairs for all six shapes/axes. An additional check matches
the twenty generated source gate lists to the audited virtual programs.

A nonzero source flag discards and rebuilds only this known unused data
source, before any enrichment. Its raw encoder faults are removed by a
clean rank-one source reference or the attempt rejects. A certified
source syndrome is corrected using the signed twenty-generator source
right inverse. Faults after its clean reference can leave whole-inner-block
errors, which the later gauged proof allows. The final tail does not use
these source gadgets, since there the residual bound must be physical
weight, and the magic-bearing block must not be reset.

Source flags and nonzero graph-parity scans share at most two local retry
tokens. The same global fault bound covers all attempts. A source history
cannot remain unstable with two faults and the specified cap; a nonzero
graph scan can occur, and its rebuild is explicitly charged to that same
global budget. The retained data continue to accumulate physical idles.

## 5. Single-block recovery table and late corrections

Use only the one-block syndrome: bits 0–8 are the Z checks, 9–17 the X
checks. For every possible pair of inner blocks, enumerate all Pauli
errors modulo its inner XXXX/ZZZZ stabilizers. Aggregate by syndrome
and full-code stabilizer-equivalence class across all ten pairs.

Accept a correction iff **all** compatible errors have the same class.
Choose its minimum-weight representative, breaking ties by masks.
There are 23281 unambiguous syndrome classes, 3855 ambiguous syndromes,
and additional reports outside the model. The complete independent audit
checks all 655360 fixed-two-block Paulis against every admitted decision.

This is not correction of all unknown two-block errors. For example
X(2,3) and X(8,11,12,15) have the same syndrome and differ by logical X0.
That syndrome still rejects. An arbitrary single physical Pauli error is
unambiguous; many nonzero syndromes can therefore be retained safely.

At the clean syndrome reference, each operator term has an actual error
E supported in at most two inner blocks. If the decoder accepts C, then
C E is a stabilizer on that sector for every compatible term. Subsequent
Pauli-check gadgets have certified one-site-per-fault spread (single-port
cats or the zero-flag lemma), so faults
after that reference add at most one physical site each. Commute the
ideal Pauli correction C through those late Pauli expansions; it changes
only phases, not support. Faults on the individual correction gates
also add one physical site each. Thus recovery preserves an unknown
encoded state and leaves only later, charged errors. This argument does
not reset a magic resource or measure either source logical X.

## 6. Combined gauged rounds, including repaired nonzero syndromes

Keep the original full round structure:

```text
V
bare code Z then X record
    if nonzero: certify a commuting full code record; apply its unique-class correction
cycle Z record
    if nonzero: certify a commuting cycle record; apply its decoded edge-X correction
four nonroot edge X stars, with physical root-tree Z sign repairs
V
root Gauss measurement
```

An ambiguous data/cycle recovery rejects. If recovery succeeds, a positive
root report makes this a passing round, even when the incoming code or
cycle syndrome was nonzero. In a fault-free complete round, either its
zero code projection or its certified nonzero recovery returns the data
to the original codespace in V coordinates. Cycle recovery restores
flatness; nonroot star repairs set the four signs positive. The root
then measures actual U. The original two-block detection/normal-form
argument reduces the logical input to span{|++>,U|++>}; its positive
projection is the unique desired magic line.

Require three passing complete rounds within at most five. With two
faults, three passes contain a fault-free complete round, including any
recovery subrounds and physical corrections. Its passing state is exactly
magic. Earlier failed rounds preserve the same bounded-error logical
span; subsequent faults and recoveries preserve magic up to charged
errors. This is a pigeonhole argument, not a globally commuting-history
claim. All 256 combinations of passing masks and <=2 bad-round placements
in this finite certificate satisfy the clean-pass conclusion.

The reported vertex parity is retained in the log but no longer decides
early rejection. Its sign frame still applies the nonroot Z corrections.
This saves an otherwise good attempt with a false vertex report. A genuine
negative logical branch has zero positive passing amplitude in any clean
round after code recovery, so it cannot get three false positive passes
from only two faulty locations.

**Why not separate code certification and Gauss certification?** There is
an explicit one-fault counterexample. Begin with the genuine negative
encoded |11> branch, then insert X_q after the last code reference. Since
U X_q U is +/-Y_q, measuring physical U=+ produces a nonzero superposition
of X_q|11> and +/-Y_q|11>. Both are correctable single-site errors on the
negative logical state. An ideal ordinary recovery returns |11>, despite
the positive physical U certificate. This positive branch has probability
1/2. The independent complex test constructs it and finds physical U=+
but decoded CZ-magic fidelity zero. The combined-round rule above prevents
this shortcut: a clean passing round includes code restoration and root
certification together.

## 7. Terminal recovery and the final boundary

After complete cut decoding and the physical S/X byproduct, the accepted
gauged certificate supplies magic with inherited errors on at most two
inner blocks. Acquire a single certified history of the eighteen original
Pauli code checks; accept either syndrome value. Apply the unique-class
correction from Section 5, or reject if absent/ambiguous. There is no
requirement to discard a good resource for a transient wrong report or
a correctable nonzero syndrome, nor to obtain three additional zero
records after a certified correction.

At a clean occurrence of the selected terminal value, the inherited
error is corrected on every compatible component. All later target
couplings are Pauli gadgets with certified one-site-per-fault spread and all later
corrections are individual Paulis. Their errors commute through the
chosen correction without spreading. Including the final boundary
idle, the output lies in the weight-two correctable physical span.
This proves the recovery-profile theorem with the same global budget.

The direct-cat comparator instead needs three passing combined code/U
rounds, since it has no earlier gauged magic certificate. It uses the
same source extraction, cat protection, correction class, and physical
noise parameters, and has the same two-fault accepted-output guarantee.

## 8. Twenty-edge graph and decoding radius

Current20 uses the exact edge order and root tree read from the existing
SWAP implementation. It is a double K5, with degree eight at every vertex,
sixteen independent cycle checks and cut distance eight. Compact13 has
degrees (6,5,5,5,5), nine cycles and cut distance five.

The V transformation and check algebra do not depend on the edge count;
they use the graph's four specified root-tree edges. Both graphs are
connected, fully cycle-filled, have bounded-length paths and sufficient
expansion. The positive gauged code again has physical distance six.
For current20 a weight<=5 Pauli has either no edge-X cut, in which case
the original proof applies, or a nonzero edge-X cut of weight at least
eight, which is impossible. Weight-six logical Z0 supplies the upper
bound. No new distance-scaling theorem is assumed from the SWAP code.

The recovery profile uses radius two on compact13 and radius three on
current20, for both cycle syndromes and final edge reports. The latter
certifies 1351 distinct edge-flip patterns and 21616 cut-neighborhood
records, compared with 92 and 1472. Under the two-fault theorem the true
error still has weight<=2, and cannot be confused with a weight-three
candidate: their difference would be a cut of weight<=5, below eight.
The larger radius therefore preserves the theorem, while potentially
recovering extra report faults in unrestricted noisy runs. It does not
establish a three-circuit-fault guarantee.

## 9. Simulation arithmetic and the verification boundary

Quantum evolution uses coherent integer coefficients in Z[zeta8], not
probabilities for independent Pauli branches. Intermediate T gates act
explicitly. Sparse unitary data factors keep their eighth-root phases;
their overlaps and complete Born norms include every cross term. Exact
sign tests of a+b sqrt(2) and lazy random bits sample irrational Born
probabilities without rounding them to rational or floating thresholds.

The optional internal CSS compression is a change to a **complete** basis
of syndrome/logical stabilizer kets. An exact Walsh inversion keeps every
coefficient and every syndrome. It is adopted only when it reduces the
number of coherent terms. It neither projects onto the code nor corrects
an error, and introduces no quantum/noise locations. An independent test
compares the normalized complex ket before and after this transformation.

Only final artifact conversion and read-only decoded-density diagnostics
use complex128. The output is normalized from exact cyclotomic norms at
high precision before conversion. Diagnostics are never supplied to the
physical controller. Capacity/time limits produce unresolved computations,
not inferred physical rejections. Finite gadget audits, exact trajectory
arithmetic, floating output diagnostics, and the analytical full-factory
proof are distinct claims.
