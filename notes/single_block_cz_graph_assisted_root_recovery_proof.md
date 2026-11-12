# Proof: graph-assisted recovery of a flagged local Gauss check

This proves the opt-in schedule in the
[integrated note](single_block_cz_graph_assisted_root_recovery.md), not an
extension by analogy with the persistent or two-block SWAP circuits.
All old schedules remain available. The gauging route keeps the physical
four-data local root G_a; no global-U quantum measurement is substituted.

## Theorem and physical model

With at most two arbitrary faulty locations in the entire specified
attempt, every accepted output decodes to encoded CZ_magic and has only
a residual in the correctable physical weight-two operator span. Quantum
locations are PREP/reset, each H/Pauli/S/T/Tdg, each CX, destructive
measurement/report and each waiting/boundary idle. Fault participants
are exactly the listed gate participants, or one waiting qubit. Classical
processing is reliable. Failed known-resource attempts, all conditional
records, physical corrections and later operations share the same budget.

This proof assumes the previously certified signed source/U/V action,
source/resource normal forms, bare-star schedule, ordinary data decoder,
flag-dependent Pauli recovery and terminal-screen/tail lemmas. Those
circuits are unchanged except for the separately certified dual-basis
one-remaining-fault Pauli gadget. The new finite premises are in
`check_single_cz_root_recovery.py`. The external-cone and composition
arguments below are analytical; there is no full-factory pair enumeration.

## 1. Why a root flag permits conditional recovery

For arbitrary input on the target ports, every ideal rolling flag
uncomputes to zero: its two CXs see the same computational controller
bit, which ideal controlled-W/X ports preserve. Thus any nonzero reported
flag proves a faulty location in that root gadget, including a possible
wrong report. Earlier target errors alone cannot generate a flag in an
otherwise ideal gadget. At most one fault remains outside that gadget,
or both global faults occurred within it.

The controller finishes all helper readouts, records their complete flag
vector, and discards the root parity as a vote. The helper is not assumed
available after destructive measurement. In gauging, apply V and acquire
the joint Pauli family: 18 data stabilizers, E-4 cycle-Z checks, four
nonroot X stars. Data/graph supports are disjoint; every cycle meets a
star evenly. The whole family commutes globally in this coordinate frame.
Graph rank is E and data rank is 18. No correction is applied between
records. Two equal consecutive complete records therefore include a clean
reference under the one-remaining-fault bound; four records suffice.
The rule is not applied to a history containing the non-Pauli root.
New conditional data flags and unstable records reject.

## 2. Root fault operator span, retaining coherent coefficients

For every elementary root location, expand arbitrary local fault action
in a Pauli basis on its participants, retaining environment coefficients
and classical readout branches. A target action remains an opaque
one-site algebra. A controller X/Y component appends the exact later
local involutions W/X. Helper Pauli propagation and flag flips are binary;
this does not make target propagation through T into Pauli XOR.

The independently checked one-location signatures have (A,h,f): directly
damaged target set A, hook support h, and reported flag vector f. Two
root faults give A1 union A2, h1 XOR h2 and f1 XOR f2, with arbitrary
complex coefficients and I/G_a branch choices. Local operators can be
moved through W without enlarging their site set. The production support
enumerator agrees exactly with the prior independent opaque propagator
for every root signature, including each physical T, CX, Tdg and idle.

Conjugate the target operator by V. Root-data local operators stay on
block a. An edge X on tree edge (a,v) acquires U_v; edge Z commutes with
V. Therefore each graph-X assignment on the locally damaged graph ports
determines both a graph X mask g and a data W-product support D. All such
assignments are included. G_a becomes Q=U Xstar_a. Multiplying a hook by
the full measured product replaces D by its complement and adds a Q
branch choice. It changes no cycle syndrome. This normalization is an
I/U logical branch, not a discarded relative controlled phase.

The exact expansion on D is

    W_D = 2^(-|D|/2) X_D product_(q in D) (I - i s_q Z_q).

Every term has fixed X support D and arbitrary Z subset of D. The
decoder conservatively permits arbitrary coefficients on these terms,
as well as arbitrary local Paulis on A. Consequently any accepted
correction works for all coherent sums, including the exact physical
coefficients. Exact cancellations are never used to justify acceptance.
The tensor-product identity is verified over Z[zeta8]; stochastic Pauli
sampling is not its proof. The full simulator retains all complex phases.

## 3. Exhaustive typed envelope for the one outside fault

Describe errors at a clean reference in V coordinates. Graph Z support
is unrestricted. The allowed graph-X cycle word is correlated with the
data cone as follows; identity action is included in every algebra.

| Outside fault source | Data algebra | Graph-X possibilities |
|---|---|---|
| Late source, enrichment, vertex operation; zero-flag Pauli data checks or physical data corrections | One inner block B | Cycle word zero |
| A tree-edge bit error or faulty coordinate control v | Block v | Zero or that tree edge |
| A non-tree edge or graph-only one-edge fault | Identity on data | One edge |
| Bare star v, including its helper and measurement | Identity on data in V coordinates | Each suffix of the incident-edge order, or a singleton |
| Any graph phase or wrong graph sign report | Identity, or the already charged block above | Arbitrary Z; no additional X |

This table is an overapproximation, not a diagnosis from the syndrome.
Each location belongs to one row:

* A clean known-source reference removes raw encoder faults; accepted
  decoded-source tails have the original one-block bound. A clean graph
  parity scan projects onto span{|t,dt>}; raw faults surviving that reference
  contribute arbitrary phases/source I/U coefficients. Later resource
  meter faults add at most one resource bit. Vertex bits produce their
  own block cone and a cut-equivalent graph representative.
* Enrichment controls couple only to their own block. Coordinate edge
  controls couple only to the block paired with that tree edge. Data
  target actions can add graph-control Z, not another edge X. An arbitrary
  paired data/graph action at such a CX is included in the full block
  algebra with that edge's cycle word.
* An accepted earlier zero-flag root has its original one-port bound
  modulo the full root product. In V coordinates this is one data site,
  or a graph edge paired with its own U_v block. I/U factors stay explicit.
* For a bare star, a controller bit fault gives an incident-edge suffix;
  a joint controller/target fault at its CX gives the suffix including that
  target. Waiting/target faults add a singleton. The audit compares this
  complete X-mask set with independent Clifford propagation. The star
  operates on graph only in V coordinates, even for a broad hook.
* Code/cycle/star diagnostics have exactly these same participant types.
  Cycle meters have one-edge bit spread with unrestricted phase support.
  A physical graph correction changes only its own edge. All waiting-data
  faults belong to a one-block algebra, independently of their context.

A previous successful flag repair has no earlier-fault residual at a
later clean reference; faults after its reference obey the same rows.
With a current root flag, only one outside fault can exist. This is why
the table must not be broadened to 'any data block AND any graph X mask'
for one fault. It must also not be narrowed to one edge for a bare-star
controller hook. Both would invalidate the inference being tested.

At the clean diagnostic reference, enumerate either one current-root
fault plus one table-row outside fault, or two current-root faults. The
program does both, including same-location pairs as a conservative
overapproximation. Pauli conjugation by U preserves each data block and
does not change graph-X cycle words. Thus moving an I/Q projector past
the outside operator introduces no omitted cone.

## 4. Complete affine recovery decision

Each resulting data-Pauli family is an affine space in 40 binary Pauli
coordinates: fixed X_D; arbitrary X/Z on damaged data sites and the
allowed outside block; arbitrary Z on D. Its graph cycle word is fixed.
Graph phase is arbitrary, so star signs do not restrict data classes.
They are retained for graph restoration. Graph-blind control mode takes
the union over all cycle words instead of filtering by the reported one.

The linear class map consists of eighteen syndrome bits and four logical
commutation bits. At fixed syndrome the four bits distinguish every data
Pauli class modulo stabilizers. Elimination retains physical witnesses
for each syndrome pivot. Its zero-syndrome logical kernel is nonzero
exactly when one family admits multiple logical classes at every covered
syndrome. The decoder rejects that ambiguity, or disagreement between
any matching families. It accepts only one common label and chooses a
physical Pauli representative C. Shortening C multiplies only stabilizers.

The certificate independently verifies generator-span equality, ranks,
logical kernels, every class and every report decision in each distinct
affine image. Accepted physical witnesses differ from the chosen one by
the explicit data stabilizer group. This covers every syndrome in each
family, not just queries sampled from a trajectory. Taking the union of
all families and requiring one common label proves the corresponding
decision for every report tuple; no family is dropped on a heuristic.

Consequently C E is a stabilizer for each surviving Pauli term. Projecting
the graph's complete stabilizer family fixes a unique graph syndrome
state and leaves only coefficients on the data/environment. A chord-X
correction fixes the cycles and tree-edge Z fixes the four star signs,
both physically within V coordinates. The corrected logical map is a
sum of **alpha I + beta U** terms with graph/environment coefficients.
It preserves the I/U span of the known source. More strongly, it preserves
every already-positive U eigenstate, including CZ_magic, and every
negative eigenstate separately. It cannot turn genuine 11 into magic.

## 5. Reference timing, late faults and composition

The selected value need only have a clean occurrence; its last equal
record might contain the remaining fault. At its clean reference the
preceding decoder applies. If the outside fault occurred later, the
identity-outside case was included, and its late residual is charged
separately. One conditional data-gadget fault adds one physical site.
One cycle fault adds one edge bit; one star hook is confined to one
star and therefore contains at most its own single tree-control edge.
Physical data/graph correction faults have their listed one-site supports.
Commuting those late errors past planned Pauli corrections does not enlarge
support. On returning through V they charge at most one data block per
remaining fault. Non-tree chord corrections themselves commute with V.

The repaired root contributes **no positive vote**. All previous votes
may be retained because the repair's logical map is diagonal I/U: if
a previous clean vote established CZ_magic, the repair preserves it.
Resume the next complete round in V coordinates, avoiding a redundant
V-return/V-entry pair. At most five combined rounds remain the bound.
With three positive unflagged complete rounds and two faults globally,
one passing round is clean. Its code restoration, star repairs and local
root measurement select the same unique positive magic line as in the
original proof. No commuting-history claim is made across those rounds.

Before a clean passing round, the new accepted repair preserves the
source I/U span plus charged late blocks. After a clean passing round,
it preserves CZ_magic plus those blocks. The original final cycle
flattening, cut decoder, physical byproduct and terminal-screen theorem
therefore apply unchanged. Later faults, including correction gates and
the final boundary, leave only the original correctable physical weight-two
span. No source-logical-X measurement or reset of unknown data occurs.

## 6. Shared dual conditional primitive and direct control

The new Z conditional program is the full Hadamard dual of the existing
X single-flag program. Data observables change from X to Z; all actual
basis rotations are on the flag helper. It measures the same signed Z
projector. The finite one-location audit, including measurement/report
combinations and idles, proves its zero-flag one-site bound. It is used
only after a reported flag has spent at least one global fault. A new
conditional flag rejects. Thus it replaces that primitive in all existing
data-flag recovery proofs, for both gauging and genuine GHZ20 cat.

For the direct global flagged-U control, omit graph variables and V;
use the same root span on twenty W ports, the same arbitrary one-block
outside algebra, and eighteen commuting data diagnostics. Affine recovery
still returns an I/U logical map. Three unflagged complete code/U votes
and the original late physical-site bound prove the same accepted-output
contract. No such used-root recovery is asserted for the genuine-cat
gadget, whose measured-leaf circuit has a different flag mechanism.

## 7. Scope and physical witness

Flag word 48, zero data syndrome and zero cycle syndrome admit only class
I in the joint compact13 decoder. The graph-blind union includes a
nontrivial logical-Z alternative at cycle word 71 and rejects. The test
injects X_s X_A0 at the actual root CX(s,A0), completes the conditional
diagnostics, and verifies the accepted decoded output. Coherent graph
phase faults, second coordinate/diagnostic faults, wrong cycle reports,
two root flags, genuine negative branches and late terminal faults have
additional quantum regressions. These support the analytical composition;
they are not described as exhaustive full-factory fault-pair tests.
