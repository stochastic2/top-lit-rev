# Proof for the C4-Helix procedure with reduced rejection

This body proves the retained Z-output profile. The default logical-Y
profile, both-outcome selection and tracked Clifford correction are
covered by [the Y-output extension proof](magic_y_preparation_proof.md).

This note proves the accepted-output claim for
[the new integrated procedure](full_procedure_reduced_rejection.md).
It retains the current gauging and ungauging circuit and changes the
cat, source, gauged-syndrome, and terminal-recovery rules. It also allows
the specified recover-and-re-gauge fallback for uncertified cycles.
The original proof's two-block and paired-check ideas remain essential;
accepting arbitrary negative syndromes without new recovery arguments
would not be justified.

The default optimized extraction uses compact flagged B/C-source gadgets,
grouped controls before ungauging, and a two-initial-zero-scan cat shortcut.
The new adaptive history policy replaces consecutive triples with
the certified clean-reference rule proved in Section 2. The former
triple policy is still covered as a special case.
The previous `verified_cat` profile remains covered as a special case.
Sections 3.4--3.6 give the new locality arguments; the final data controls
remain individual so that the physical weight-two output guarantee survives.

The proof below is analytical. The accompanying
[finite audit](../src/check_reduced_rejection.py) verifies its code and
graph ingredients, rather than enumerating every physical fault pair.
The [adaptive-history audit](../src/check_adaptive_history.py) separately
checks all 52 five-round equality patterns and 197 compatible bad-round
placements at the selector's first stopping prefixes. These finite checks
supplement the analytical reference lemma below.

## 1. Claim and global assumptions

**Theorem.** Execute the main procedure using at most two faulty
locations in the entire serial schedule, including every cat-repair
scan, extra syndrome round, correction gate, and live-qubit idle.
Every accepted output has decoded C state

\[
|M\rangle\otimes|0\rangle,
\qquad |M\rangle=\frac{2|0\rangle+|1\rangle}{\sqrt5}.
\]

The physical output may have a correctable residual error. No additional
fault-free physical recovery is appended to the circuit.

Classical processing is reliable. A faulty quantum operation has
arbitrary action on its participants, a meter may give a wrong report,
and each idle location belongs to one physical qubit. Fredkins are
three-qubit operations or decompositions on the same participants.
Helpers are reset between uses and follow their specified physical gadgets.
Protected cats are repaired before coupling; known-source flags are read
after coupling and may trigger rebuilding that unused source.

Write \(J_a=\{0,1,2,3\},\ldots,J_e=\{16,17,18,19\}\).
A matched-label set F specifies positions in **both** B and C. A term
supported in two matched labels need not have small physical weight.

The proof uses operator expansions and linearity; it does not assume
that arbitrary errors are stochastic Pauli faults. Coefficients in
such expansions may be operators on an environment. Classical records
are fixed when discussing a conditional branch.

## 2. A certified record supplies a clean reference round

### 2.1. Report-only certificate

A round includes its helpers and all live-qubit idles. Boundary idles
belong to the following interval. Let complete reports be
\(s_1,\ldots,s_m\). Mark edge \((i,i+1)\) exactly when
\(s_i\ne s_{i+1}\), and let \(\mathcal B\) contain **every** subset
of at most two round indices touching every marked edge.

Two adjacent clean rounds give the same report. Indeed, the first
ideal round projects onto the joint eigenspace of the complete commuting
family and the second preserves it. There are no intervening corrections.
Thus every marked edge has a bad endpoint, and the actual bad-round set
belongs to \(\mathcal B\) under the global two-fault assumption.

For a reported vector s, define \(I_s=\{i:s_i=s\}\). Certify s iff
\(\mathcal B\ne\varnothing\) and no \(B\in\mathcal B\) contains
all of \(I_s\). Consequently at least one occurrence of s is a clean
round. This is the needed reference syndrome. The controller does not
identify that clean occurrence and never consults actual fault locations.
The certificate also need not assert that the final round is clean.

Stop at the first prefix with a certificate, preferring the usable vector
whose latest occurrence is most recent. This tie rule changes no guarantee.
For `A,B,B,C,C`, with distinct whole vectors, forcing rounds 4 and 5
both bad also requires a third bad round at the A-to-B boundary. Hence C
is usable. Three occurrences of the same whole vector, consecutive or
otherwise, are another sufficient case.

### 2.2. Five rounds suffice for every history

There are four possible marked edges after five rounds. Choosing rounds
2 and 4 touches all four, so \(\mathcal B\) is always nonempty; the
certificate never relies on an impossible fault assignment.

If any constant run has length at least three, its vector is usable.
Otherwise write the lengths of the consecutive constant runs. All parts
are 1 or 2 and sum to 5, giving exactly these eight cases. Indices below
are one based.

| Run lengths | Equal pair | Marked edge disjoint from that pair |
|---|---|---|
| 2,2,1 | 1,2 | 4–5 |
| 2,1,2 | 4,5 | 2–3 |
| 1,2,2 | 4,5 | 1–2 |
| 2,1,1,1 | 1,2 | 3–4 |
| 1,2,1,1 | 2,3 | 4–5 |
| 1,1,2,1 | 3,4 | 1–2 |
| 1,1,1,2 | 4,5 | 1–2 |
| 1,1,1,1,1 | No pair | See below |

In each paired case, declaring both pair members bad requires a third
bad round to cover the disjoint marked edge. That pair's vector is usable,
including when its vector has additional nonconsecutive occurrences.
In the final case all four edges are marked. Their only cover with at
most two vertices is \(\{2,4\}\), so round 5 is clean in every compatible
assignment and its vector is usable. Therefore every five-round history
has a certificate. Clean histories still stop after three rounds.

The implementation independently checks all 52 equality patterns of five
whole records, and all compatible placements of at most two bad rounds,
in [the adaptive tests](../src/test_c4_helix_adaptive.py). This finite check
tests the selector; the argument above establishes the general lemma.

### 2.3. Applicability to this complete circuit

The argument uses commuting observables and the ideal projective action
of a clean complete round. It does not require Pauli observables or a
particular code distance. It therefore applies to known sources, the
commuting gauged family including Gauss involutions, original-code
recovery, and the adjacent-ZZ scans in cat repair. The two-initial-zero
cat shortcut retains its separate Section 3.4 proof.

A clean *outer* round has clean nested cat circuits. A fault inside one
such interval spoils that outer interval, but is still charged only once
in the global budget. Earlier stopping adds no gates or enlarged control
groups. All subsequent arguments require an actual reference syndrome
at some clean occurrence, rather than three consecutive copies. They
already charge errors after that reference to the remaining fault budget,
so they continue to apply if the usable reference predates the last round.

For the retained `triple` policy, one of three identical consecutive
rounds is clean. Two bad rounds cannot prevent nine rounds from containing
three consecutive clean rounds: without them there could be at most
\(2+3\cdot2=8\) rounds. This recovers the former nine-round argument.

With unrestricted stochastic noise, more than two bad rounds may occur.
The selector still stops by five, but its reference guarantee is then
conditional and can fail. Numerical acceptance must therefore be reported
together with decoded output fidelity; removing agreement-limit rejection
alone is not evidence of improved logical yield.

## 3. Cat repair preserves the required spread bound

### 3.1. What the clean scan projects onto

For adjacent-ZZ signs \(d_j\), define \(r_0=0\) and
\(r_{j+1}=r_j\oplus d_j\). Their joint eigenspace is exactly

\[
\mathcal H_d=\operatorname{span}\{|r\rangle,|\bar r\rangle\}.
\]

Indeed each basis string z with these adjacent parities is determined
by its first bit; the two choices are r and its complement.
A clean occurrence of the certified scan vector therefore projects an
arbitrary raw cat state, even one entangled with an environment, into
\(\mathcal H_d\). The raw CNOT-chain preparation may have spread an
early fault to many leaves; this projection does not assume otherwise.

### 3.2. Later faults do not recreate an unbounded bit pattern

After raw preparation there are no leaf-to-leaf gates. In each parity
test, both leaves are controls and the reset helper is the target.
A faulty leaf-helper gate directly touches one leaf. An X on the
helper does not propagate back to the leaves. A helper Z can produce
leaf phases, but cannot flip a second leaf's computational bit.
Consequently each post-reference fault adds at most one leaf-bit
error. Independent X correction gates have the same property.

Apply \(X^r\). Up to the post-reference local leaf defects, the cat is
now in

\[
\operatorname{span}\{|0^m\rangle,|1^m\rangle\}.
\]

The phase and amplitudes of these two components need not be correct.
Keeping that uncertainty is necessary: adjacent-ZZ checks do not
distinguish positive and negative cats.

### 3.3. Effective instrument after coupling

Each leaf controls only its assigned disjoint factor or group \(Q_j\).
A leaf-bit defect therefore adds only that target factor. A faulty
coupling can damage its own targets and the remaining ports of that
same control group; separate data idles each
damage only their idling qubit. Expanding errors on the leaves,
couplings, and meters gives a sum of terms

\[
D(aI+bQ),\qquad Q=\prod_jQ_j. \tag{1}
\]

For a fault-free gadget this is the exact reported projector up to
normalization. For a faulty gadget a,b include the unknown cat phase,
amplitudes, and report errors. D contains at most one assigned target group per
fault not removed by cat repair, plus individually faulty target idles.
For a grouped SWAP factor, D may occupy its matched four-qubit block
in both copies. The assignment below controls where that is allowed.

Equation (1) is the same bounded-spread instrument needed by the
original proof, now obtained by correcting a cat coset rather than
requiring the positive coset. A phase fault that changes the effective
projector is not being treated as a harmless data Pauli; it remains
in a,b and is handled by later complete-record repetition.

### 3.4. Why two initially zero scans suffice

Suppose the first two complete adjacent-ZZ scans both report zero.
Partition the global fault budget by whether raw cat preparation contained
a fault.

- If raw preparation was fault-free, the cat started uniform. Each fault
  during the scans can flip only its one participating leaf. There are
  therefore at most k bad leaf bits from k such faults, with arbitrary
  relative phase still allowed.
- If raw preparation contained a fault, at most one fault remains for
  the two scans and their idles. At least one scan is clean. Its reported
  zero is a genuine uniform-subspace projection. Every later fault adds
  at most its one leaf-bit defect. Earlier nonuniform patterns have been
  projected out; an entirely uniform raw error merely changes a,b.

If both faults occurred in raw preparation, both scans are clean, so
the same conclusion holds. Accepted two-zero-scan cats thus satisfy the
bounded-spread instrument (1). This argument conditions on two **zero**
records. It does not permit estimating a nonzero repair vector from only
two matching records. The latter branch retains Section 2's full rule.

The finite audit independently propagates all local Pauli faults, meter
report errors, and idles through two scans for m=2,...,16. It checks every
accepted pair of merged signatures, modulo the uniform all-leaf flip.
The simulator's executed event lists are checked against those exact
audited programs.

### 3.5. Grouped controls preserve the matched-label bound

During paired checks, every control group lies in one matched inner block.
During a Gauss check, each gauge-X port has its own leaf; the four SWAP
ports share a leaf but all lie in the Gauss vertex's matched data block.
Existing data damage can acquire phases or move between B and C through
those SWAPs, but it cannot reach another label through that control.

Consequently each bad leaf or faulty port can add at most one matched
label. Gauge bit errors are still at most one physical gauge position
per faulty gauge port; a full ideal Gauss star is a valid cut change.
For graph-resource and terminal checks, every physical target retains
its own leaf. In particular, after a clean terminal reference, each
remaining gadget fault adds at most one physical data qubit, as required
by Sections 9.4 and 10.

### 3.6. Compact flagged source extraction and local rebuilds

The optimized known-input circuit uses a star cat of m=1,3,4 leaves.
Each leaf's targets lie in one inner block. After the target couplings,
the fanout is uncomputed; the m-1 other leaves are read in Z as flags,
and the first leaf is read in X as the Pauli syndrome. For ideal gates,
the flags are zero for arbitrary data, and the data instrument is the
reported Pauli projector. For m=4 and two targets per leaf the cost is
six fanout/uncompute CNOTs plus eight target couplings.

All operations in this source gadget are Clifford. Propagate a Pauli
term from any faulty preparation, one- or two-qubit gate, meter, or idle
to the end. It gives a data Pauli E, helper Paulis, and classical flag
flips. A zero reported flag record retains only terms whose propagated
flag flips cancel. The remaining syndrome uncertainty changes a,b.
Multiplication of E by the measured Pauli Q can be absorbed by exchanging
a,b in (1), so E can be reduced modulo Q when bounding its support.

The [finite locality audit](../src/check_optimized_extraction.py) proves
the following for all six implemented source shapes (axis X/Z, with
block sizes 1x4, 3x2, 4x2):

1. One fault and zero flags leave a representative E supported in at
   most one inner block.
2. Two faults and zero flags leave a representative in at most two
   inner blocks, including cases where the two faults hide their flags.

The enumeration includes every nonidentity Pauli on a gate's participants
and every single-qubit waiting location in the gadget. Flags' wrong
reports are equivalent to X before their Z meters. Errors on waiting
data outside the measured support cannot propagate through this gadget
and add only their own one label. The audit groups identical signatures
and checks all pairs, even an overestimate allowing both faults at one
location. Tests compare the real simulator's primitive programs to the
audited programs, not only their gate counts.

Expanding arbitrary local faults in Pauli operators and projecting onto
the reported flags extends these termwise bounds to coherent errors and
environmental coefficients. For a zero-flag gadget containing k faults,
k<=2, at most k source-block labels are therefore added. Different
gadgets' contributions sum within the same global two-fault budget.

If a flag fires, rebuild only that still-known source, restarting its
entire source history. The source has not touched the other copy or
the gauge circuit. A failed build needs a fault because ideal flags
are zero for any data. At most two builds can fail, so a cap of three
local builds per source suffices. Discard/reset operations, re-encoding,
and the retained other copy's idles remain counted. A later clean source
reference projects the new build onto its unique source eigenspace.

## 4. Deterministic recovery of known sources

### 4.1. Complete stabilizer signs can always be corrected

Let \(g_1,\ldots,g_n\) be independent commuting Pauli generators on
n qubits. Their symplectic vectors have rank n. The linear map sending
a correction Pauli to its commutation signs with these generators has
rank n and is onto all n-bit sign vectors. Thus for every record s
there exists a Pauli \(R(s)\) such that

\[
R(s)g_j=(-1)^{s_j}g_jR(s).
\]

The joint eigenspace for s has dimension one. Its normalized state
\(|\sigma_s\rangle\) satisfies

\[
R(s)|\sigma_s\rangle=e^{i\theta_s}|\sigma_0\rangle. \tag{2}
\]

The B and C source families each contain twenty independent generators;
the graph family contains 25. Their positive states are the intended
known sources. No assumption about the raw encoder's fault propagation
is needed before a clean reference round.

### 4.2. The correction itself need not be fault-free

At a clean reference round, a complete measurement projects the source
onto \(|\sigma_s\rangle\). Subsequent Pauli-check gadgets have the
form (1). For an existing Pauli term F and one measured generator g,

\[
(aI+bg)F|\sigma_s\rangle
=\bigl(aF+(-1)^{s_g}b\,gFg\bigr)|\sigma_s\rangle. \tag{3}
\]

Conjugating by a Pauli does not enlarge F's support. For optimized B/C
source gadgets, Section 3.6 bounds additional damage by the number of
faults in **inner-block labels**; for the protected graph gadgets it is
bounded in physical targets. Thus just before the source correction,
the state is a sum of \(F_\nu|\sigma_s\rangle\). B/C need only the
matched-label bound at this stage; their individual-qubit bound is not
used until after terminal recovery.

Since R is also a Pauli, applying it changes F only by a phase:

\[
R F_\nu|\sigma_s\rangle
=\pm F_\nu R|\sigma_s\rangle
\propto F_\nu|\sigma_0\rangle. \tag{4}
\]

Execute R as independent single-qubit factors. A faulty correction
gate or later idle adds one more physical error; no such gate couples
different positions. Equations (2)--(4) prove the source guarantee
even if R has high weight.

For the graph source, this argument occurs after all raw
vertex-to-edge CNOTs. A residual vertex error later reaches only its
assigned matched data label during enrichment. A residual edge-bit
error affects only that edge. Waiting errors on already prepared
data have the ordinary single-qubit support bound.

## 5. Code lemmas: detection, erasures, and paired checks

### 5.1. Two-block detectability

For one original \([[20,2,6]]\) copy, a Pauli supported on at most two
inner blocks that commutes with all original checks is a stabilizer
up to phase.

For an X-only Pauli, passing each inner ZZZZ check means an even
number of X factors per occupied block. Multiplying by inner XXXX
removes four factors when present, leaving at most two per block.
The equivalent X Pauli has weight at most four; distance six excludes
a nontrivial logical operator. The Z-only case is identical with X
and Z exchanged. For a mixed Pauli, its X and Z components separately
pass the opposite-type checks because the code is CSS. Apply the
preceding reasoning to each component. This proves the claim.

The finite audit independently checks the stabilizer supports, rank,
distance of the pure X/Z normalizer classes, and the fixed-two-block
syndrome equivalences. The physical supports come from the local
experimental manuscript's [Appendix A](../arXiv-2609.03194v1/appendix.tex).

### 5.2. A known two-block set is correctable

Fix a two-block set F. If E and F' are two Pauli errors supported
there and have the same syndrome, then \(E^\dagger F'\) commutes with
all checks and is still supported in that set. By Section 5.1 it is
a stabilizer. Therefore **every syndrome in a fixed two-block set
specifies one correction class**.

Equivalently, for the code projector P and arbitrary operators E,F'
on that fixed set,

\[
P E^\dagger F' P=c_{E,F'}P.
\]

This is the error-correction condition for an erasure in that known
set. It does not imply correction of two *unknown* blocks: the union
of two possible sets can contain four blocks and a logical operator.

### 5.3. Paired-zero errors preserve the SWAP sector

Let \(P_N\) project onto all \(N_s^P=S_{B,s}^PS_{C,s}^P=+1\).
Write a bounded data Pauli as \(E=P_B R_C\), where P and R have
support in the same at-most-two-label set.

If E anticommutes with a paired check, \(P_NEP_N=0\). Otherwise P
and R have the same original-code syndrome. Their relative Pauli
\(P^\dagger R\) is a stabilizer S by Section 5.1. Hence, up to phase,

\[
E=(P_BP_C)S_C.
\]

On the paired-positive sector, \(S_BS_C=+1\), so S on B and C act
identically. The matched Pauli \(P_BP_C\) is unchanged by U. It follows
that

\[
UE|\chi\rangle=EU|\chi\rangle
\quad\text{for paired-positive }|\chi\rangle. \tag{5}
\]

Gauge operators commute with U. Thus the same conclusion applies
with arbitrary gauge Paulis multiplying E. This is why positive paired
syndromes remain essential when certifying the logical SWAP sector.

## 6. Spatial bounds through enrichment and gauged measurements

After source correction the ideal states have residual local errors
charged to actual later faults. During enrichment, vertex v controls
only the four data SWAPs in \(J_v\). An X on that controller can
propagate through several remaining Fredkins, but every data target
belongs to matched label v. A faulty Fredkin also touches only that
label. Existing data errors can change copies without changing labels.

In every later protected check gadget, Section 3 supplies one permitted
control group per fault. Each data group lies in one matched label;
gauge targets stay individual. Conjugation by a Gauss generator exchanges B and C only
inside one matched label. Thus it never expands the affected label
set. Pauli-check conjugation changes only signs.

Consequently, prior to terminal recovery, each operator term has data
support in at most two matched labels. The two labels are common to
the two copies, although different terms may use different sets.

Gauge bit errors require a separate bound. After the graph's clean
source reference round, no raw vertex-to-edge preparation CNOTs remain.
Each subsequent fault adds at most one non-cut gauge-bit flip. Whole
Gauss star flips change one valid cut to another and are not independent
bit errors. Before gauge correction every term therefore has an edge
word of the form

\[
p(t)\oplus e,\qquad |e|\le2. \tag{6}
\]

Arbitrary gauge phases are allowed. They do not change (6).

## 7. A certified gauged stage fixes the positive reference sector

### 7.1. Expansion before the clean reference round

Let \(|\Phi_\pm\rangle\) denote the ideal gauged states with U sign
\(\pm1\), in the root-a convention:

\[
|\Phi_\pm\rangle
\propto\sum_{t:t_a=0}|p(t)\rangle V_t(I\pm U)|\psi\rangle.
\]

Both have all paired and cycle checks positive. Their nonroot Gauss
signs are positive and their root Gauss sign is \(\pm1\).
The noisy vertex readout, its sign corrections, and earlier noisy
gauged rounds yield a sum of bounded-error terms multiplying these
two reference states. Equation (1), and conjugation by the measured
observables, preserve this expansion even when earlier check reports
were negative and retained.

### 7.2. A certified record with zero paired bits and even Gauss parity

Choose a clean occurrence of the certified record. That record is
\((0,l,g)\), with even parity of g on an accepted branch. Because
the checks commute, reason in their scheduled order: paired, cycle,
then Gauss.

The paired-positive projector removes every Pauli error term with
nonzero paired syndrome. Every remaining bounded term satisfies (5).
For the actual Gauss projectors in this clean round,

\[
\prod_vG_v=U
\]

implies that the joint g eigenspace has U eigenvalue
\((-1)^{\sum_v g_v}=+1\). Hence it annihilates the negative reference:

\[
P_{G,g}E|\Phi_-\rangle=0. \tag{7}
\]

No assumption that l is zero or that every Gauss bit is zero enters
(7). It is their **even product**, together with paired zero, that
certifies the positive reference contribution.

After that reference round all remaining terms multiply
\(|\Phi_+\rangle\). Later faulty checks do not create a new independent
negative reference: each measured Q stabilizes \(|\Phi_+\rangle\), and

\[
D(aI+bQ)F|\Phi_+\rangle
=D(aF+bQFQ)|\Phi_+\rangle. \tag{8}
\]

Conjugation in (8) preserves the matched-label bound. Gauge corrections
below commute with U and cannot undo the positive reference conclusion.

### 7.3. Cycle-syndrome correction is unambiguous

The 16 cycle checks have the cut code as their kernel. For the current
graph a cut separating k vertices has weight \(2k(5-k)\), so its
minimum nonzero weight is eight. If two masks \(e,e'\), each of weight
at most two, had the same cycle syndrome, their difference would be a
cut of weight at most four, impossible unless \(e=e'\).

At the clean reference round, (6) therefore determines the same mask
e for every coherent component compatible with l. The physical
\(X^e\) correction removes that mask. Later faults can add only their
own local edge-bit defects. This correction commutes with all paired
and Gauss checks and does not damage data.

### 7.4. Even Gauss signs admit an edge-Z correction

A Z on edge uv flips exactly the u and v Gauss bits, leaving their
total parity invariant. Using root-a edges ab,ac,ad,ae, choose

\[
z_{ab}=g_b,\quad z_{ac}=g_c,\quad
z_{ad}=g_d,\quad z_{ae}=g_e.
\]

Each nonroot sign is cleared. The induced root flip is
\(g_b\oplus g_c\oplus g_d\oplus g_e=g_a\), using even parity.
The cycle and paired syndromes are unchanged. In a clean implementation
these X and Z corrections send the reference eigenspace to all-positive
gauged checks. With faults, they introduce only individually charged
edge errors and arbitrary phases, without increasing data support.

Odd parity cannot be corrected this way because edge-Z operations
commute with U. Rejecting an odd certified Gauss product protects the
logical selection instead of concealing it.

## 8. Gauge readout and correcting SWAPs preserve the bound

After removing the reference cycle mask, remaining gauge-bit faults
and corrupt reports give

\[
m=p(t)\oplus e_{\rm late},\qquad |e_{\rm late}|\le2.
\]

The cleanly applied correction itself adds no error to this count;
its faulty gates are counted among the late faults. Gauge-Z phases
do not affect computational-basis words. Radius-two decoding therefore
returns the unique true cut. For a fixed report, all compatible
coherent components share that decoded cut.

For one expanded component, gauge readout gives data proportional to

\[
E_D V_t|\psi_+\rangle.
\]

Any gauge-Z contribution is now a scalar coefficient. The correcting
SWAPs give

\[
V_tE_DV_t|\psi_+\rangle. \tag{9}
\]

Conjugation only exchanges B and C at matching physical positions,
so (9) has the same affected matched labels. A faulty ordinary SWAP
adds its own one label. The global total is still at most two.

Thus terminal recovery after a certified cycle receives a sum of
\(E_\nu|\psi_+\rangle\), with every \(E_\nu\) in the common-two-label
class. No claim of physical weight two is made at this point.

For a cycle whose clean stopping record has nonzero paired syndrome,
Section 7's positive-sector conclusion is not used. The expansion
before it still holds, now retaining both bounded-error reference
terms \(E_\nu|\psi_\pm\rangle\) after ungauging. Gauge decoding and
the root-fixed SWAP correction remain valid for either reference sign.
Such a cycle is sent to the fallback after joint recovery.

## 9. Joint terminal recovery corrects every accepted class

### 9.1. A true joint syndrome exists in the common record

The original 36 checks commute. A clean occurrence of the
certified record measures their true joint syndrome \((s_B,s_C)\).
For each term at that reference time, both data errors have support
in some common set F of at most two labels. A preceding fault during
terminal extraction can add a single physical position, but its
label is charged to that same global two-fault bound.

Therefore every actual error term compatible with the record appears
in the table-generated candidate set

\[
\mathcal C(s_B,s_C)=
\bigcup_{|F|=2}
\{(E_B,E_C):\operatorname{supp}E_B,\operatorname{supp}E_C\subseteq J_F,
\ \operatorname{syn}E_D=s_D\}. \tag{10}
\]

For each fixed F, Section 5.2 reduces (10) to at most one stabilizer
class on each copy. The reference decoder therefore needs at most
ten representative pairs at runtime.

### 9.2. Why one candidate class is sufficient

Acceptance requires that every candidate pair in (10) has the same
class modulo \(\mathcal S_B\times\mathcal S_C\). Select one pair
R of inverse representatives. For every actual error term E with
the common syndrome,

\[
RE=e^{i\theta_E}S_{B,E}S_{C,E}.
\]

Both copies of \(|\psi_+\rangle\) are in their original code spaces,
even though their logical qubits are entangled. Hence

\[
RE|\psi_+\rangle=e^{i\theta_E}|\psi_+\rangle. \tag{11}
\]

Linearity proves this for arbitrary coherent sums of candidate errors
and for environmental coefficients. If the sum vanishes the branch
has zero probability; otherwise normalization restores the desired
logical state. Harmless stabilizer degeneracy does not cause rejection.

### 9.3. Why the class test is maximal under its stated information

If two same-record candidates E,F' differ by a nontrivial logical
Pauli, then

\[
P E^\dagger F' P
\]

is not a scalar multiple of the original product-code projector P.
The error-correction condition fails. No recovery based only on that
record can preserve **all** logical states for that candidate set.
This proves maximality for the stated broad error model and information,
not for the narrower physical circuit histories or known target state.

For the explicit ambiguity in the integrated note,
\(X_2X_3\) and \(X_8X_{11}X_{12}X_{15}\) differ by
\(\overline X_0\). The certificate checks their equal syndrome and
different classes. It also verifies that adding C error \(X_0X_4\)
restricts the common set to a,b and makes the joint record recoverable.

### 9.4. Later noisy extraction and correction leave only small errors

After the clean reference round, every check is an original-code
Pauli. The same calculation as (3), now on a fixed nonzero syndrome,
shows that subsequent extraction cannot enlarge an inherited term's
support except at a newly faulty target or idle. Factor those late
defects as L. Pauli correction R commutes or anticommutes with each
Pauli term L, so

\[
RLE|\psi_+\rangle
=\pm LRE|\psi_+\rangle
\propto L|\psi_+\rangle. \tag{12}
\]

Each additional correction-gate fault is also local, because corrections
are independent one-qubit Paulis. Thus the final residual L has at
most one erroneous data qubit per fault after the terminal reference
round, and at most two per copy. This counts all later idles as well.

Equation (12) is why a high-weight but certified correction is safe:
its weight does not propagate existing Pauli errors, whereas an
uncertified high-weight correction could change logical information.

### 9.4a. Compact terminal extraction and a flagged protected pass

The optional `compact_flagged` terminal profile is covered by the
[compact-terminal proof](compact_terminal_extraction_proof.md), with
primitive circuits and flag-conditioned repairs checked in
[the local certificate](../output/c4-helix-compact-terminal-certificates.json).
For k≤2 local faults, every zero-flag gadget leaves an error of physical
weight at most k modulo its measured original-code stabilizer. Thus the
late-error argument above applies to a compact stage with no flags.

For a nonzero flag, a certified preliminary Pauli repair restores the
weaker bound of at most k matched blocks. The controller retains the data
and restarts acquisition with the original protected gadgets. That is
exactly their input invariant under the global two-fault budget. Their
clean reference and joint correction then restore the same final
physical-weight and decoded-C guarantees as before. No unsupported source
locality bound is assumed for the final output. Subsequent re-gauging is
still governed by the existing logical-span argument below.

### 9.5. The fallback preserves the logical span and terminates

Let

\[
\mathcal K=\operatorname{span}\{|\psi\rangle,U|\psi\rangle\}.
\]

Before any positive-sector certification, a cycle with logical input
in this span has bounded-error terms multiplying its positive and
negative U projections. All raw sources other than the retained data
are known states. The enrichment identities and every gauged check
preserve that form, as in Sections 6 and 7.1. After ungauging, a term
therefore has the form \(E|\chi\rangle\) with \(|\chi\rangle\in\mathcal K\).
Different terms may have different \(|\chi\rangle\) and environmental
coefficients; this does not require a pure logical input.

The class condition (11) holds on the **whole original product code**,
not just on \(|\psi_+\rangle\). Consequently a successful joint
recovery maps these terms to a state in \(\mathcal K\), with only
the local late defects described in (12). Fresh graph preparation
does not measure or reset the retained logical data. Its faults and
their waiting errors add the same individually charged defects.
This proves the input invariant needed for the next gauging cycle.

If a later cycle is certified, Section 7 removes the negative
reference contribution. Within \(\mathcal K\), the positive U
eigenspace has dimension one, spanned by \(|\psi_+\rangle\).
Thus its accepted terminal recovery produces the desired state,
independently of coefficients left by earlier uncertified cycles.
A purely negative logical input may simply fail the next selection;
no conversion of the intrinsic negative branch is claimed.

For the cycle bound, each SWAP-uncertified stopping record has a
clean round with **true nonzero paired syndrome**. The first such
event needs a fault before that round. After its joint recovery,
all inherited damage is removed at its clean terminal reference,
up to individually charged later faults. With no new fault after
that reference, a fresh graph and a new cycle on an input in
\(\mathcal K\) have paired syndrome zero throughout. A second
uncertified cycle therefore needs a distinct fault between the
previous terminal reference and its own gauged reference. The same
argument would require a third distinct fault for a third fallback.
These time intervals are disjoint. Under two faults there are at
most two fallbacks, so a cap of three total cycles suffices.

This argument does not promise that all such cycles have a recoverable
terminal class or pass the certified Gauss logical selection. Those
conditions remain explicit. It proves accepted-output correctness
and the bound on how many fallbacks the model can require.

## 10. Final B readout and C waiting errors

Only single-qubit operations and B's destructive Z meters remain.
On B, an X or Y component of a residual physical error is a bit flip
in the reported computational word; a Z component contributes only a
branch phase. Additional wrong reports or faulty pre-measurement
operations affect their own positions. These effects occupy at most
two positions under the remaining global budget.

Two weight-at-most-two masks with equal original Z-check syndrome
differ by an X Pauli of weight at most four commuting with every
original check. Distance six makes that difference a stabilizer.
It cannot change the decoded logical-Z parity. Therefore the classical
readout decoder makes the correct logical B selection.

On the two first logical qubits, the normalized positive-SWAP state is

\[
\frac{2|00\rangle+|01\rangle+|10\rangle}{\sqrt6}.
\]

Selecting B zero gives C state
\((2|0\rangle+|1\rangle)/\sqrt5\). Both spectator logical qubits
remain zero. Residual errors on C, including C idles while B is read,
occupy at most two physical qubits and are correctable by distance six.
Thus C has the claimed decoded state. This proves the theorem.

## 11. What has and has not been guaranteed about rejection

The theorem permits the following events to be repaired rather than
discarded: nonuniform raw-cat bit patterns, arbitrary complete
known-source syndromes, up to two gauge-bit errors, even Gauss-sign
patterns, isolated bad check reports, and unambiguous joint terminal
error classes.

It does not promise that every two-fault history accepts. A nonzero
paired syndrome now invokes joint recovery and re-gauging; that
recovery can still be ambiguous or the later selection can reject.
The certified negative SWAP sector, terminal logical ambiguities,
and final logical B selection can also
reject. Arbitrary faults can affect branch
probabilities, so the ideal acceptance fraction is not a noisy-yield
bound. No independence model or stochastic error rate was specified.

Both vertex parities are retained provisionally. For ideal parity r,
the same nonroot feedforward leaves Gauss product \((-1)^r\), so
the certified positive-product test rejects exactly the ideal negative
SWAP branch. A false odd report on an actually positive state can
instead be repaired or confirmed by the later record. This does not
force negative resources into the positive sector.

The ideal source preparation is deterministic after syndrome correction.
In the noiseless unitary-source case the three repeated records at
each stage are zero, and the two unchanged logical selections give
\((3/4)(5/6)=5/8\). This addresses the user's requested distinction
between intrinsic magic-preparation selection and avoidable rejection
from the error-correction machinery.

## 12. Proof of the smaller-graph appendix option

Replace the twenty-edge doubled \(K_5\) by simple \(K_5\) with parallel
ab, cd, ae edges added, for thirteen edges in total. The graph is
connected, so its incidence map has rank four and exactly sixteen
distinct cuts. Its 18 resource generators (five vertex-X and thirteen
edge-Z) are independent commuting Paulis and specify its known
resource state uniquely.

For any graph of this form, enrichment and vertex readout give

\[
\sum_t(-1)^{b\cdot t}|p(t)\rangle V_t|\psi\rangle.
\]

Connectivity ensures \(p(t)=p(t')\) precisely when t and t' differ
by the all-ones vector. Pairing t with its complement therefore gives
the same positive/negative U projection as before. Root-tree Z
feedforward removes the same ideal signs. No identification of a
gauge-edge index with a data-qubit index is required: data enrichment
still uses the fixed four-position sets \(J_v\).

The 18 paired, nine cycle, and five Gauss checks commute. Every edge
is incident on two vertices, so \(\prod_vG_v=U\). The entire paired
and Gauss-sector proof is unchanged. Each Gauss port still touches
one edge qubit or one matched data pair.

Every singleton cut has weight five or six. For a two-vertex cut,
the simple \(K_5\) contribution alone has weight six, and added edges
cannot decrease it. Every larger cut is the complement of a singleton
or pair. Thus the minimum nonzero cut weight is exactly five. Two
weight-at-most-two error masks cannot share a cycle syndrome or lie
within distance two of distinct cuts, because their difference has
weight at most four. Sections 7--10 consequently apply with thirteen
gauge positions and the new root tree/cycle basis.

All thirteen-edge graph claims, including the same fallback, are
therefore covered by the accepted-output proof with a smaller graph
distance margin. They do
not require a direct whole-block SWAP measurement or abandoning
gauging and ungauging. The finite audit checks both graphs separately.

## 13. Scope of the finite verification

The [saved certificate](../output/c4-helix-reduced-rejection-certificates.json)
and [script](../src/check_reduced_rejection.py) establish finite algebraic
facts used above: known-state generator independence and sign solvability,
fixed-set erasure correction, syndrome-class counts and examples,
cat bit-pattern repair, gauge syndrome uniqueness, Gauss root-tree
correction, the repetition bound, and the graph cut distances.

The [optimized gadget certificate](../output/c4-helix-optimized-extraction-certificates.json)
adds the compact zero-flag source bounds and two-initial-zero-scan cats.
It establishes the finite locality claims used in Sections 3.4--3.6;
it is not an enumeration of all fault pairs in the full factory.

They do not implement the new quantum schedule, simulate coherent
two-fault gate errors, certify a hardware Fredkin decomposition, or
predict an acceptance rate at nonzero noise. The composition argument
is Sections 2--10 above. The existing V2 simulator remains a simulator
of its original positive-only schedule.

A separate [noiseless implementation and validation guide](../src/REDUCED_REJECTION_SIMULATION.md)
is now available for this procedure. Its physical-gadget tests and exact
saved-state checks supplement the algebraic audit; they do not constitute
an exhaustive noisy fault-pair enumeration or a realistic-noise study.

The subsequent [depolarizing-noise implementation](../src/DEPOLARIZING_SIMULATION.md)
samples unrestricted physical X/Y/Z faults on the same circuit and reports
acceptance separately from ideal-decoded output fidelity. Its finite
pilot and numerical tests supplement this argument; they are not an
exhaustive proof of the factory's two-fault behavior.
