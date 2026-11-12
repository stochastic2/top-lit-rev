# C4-Helix gauging and ungauging with less rejection

**Output scope:** the body of this note specifies the retained Z-output
procedure and its 5/8 ideal acceptance. The sparse simulators now default
to the [Y-output extension](magic_y_preparation.md), which keeps both final
Y outcomes in a Clifford frame and has 3/4 ideal acceptance. Use
`--magic-output z` for this note's original target and counts.

**Compact terminal option.** `--terminal-extraction compact_flagged`
uses six-gate inner and eighteen-gate upper Pauli-check gadgets, with
flag-conditioned repair and protected recovery when a flag fires. It
reduces a clean complete B/C round from 1,068 to 408 two-qubit gates.
The [concrete schedule](compact_terminal_extraction.md) and
[proof](compact_terminal_extraction_proof.md) preserve the accepted-output
two-fault guarantee. The default remains `protected` for comparison.

**Adaptive-history edition.** The new `--history-policy adaptive`
uses the complete syndrome history to certify a reference record in at
most five rounds. It also applies to cat repair after the two-initial-zero
shortcut. The former consecutive-triple rule is retained as
`--history-policy triple`, which remains the simulator default while the
high-noise acceptance/fidelity tradeoff is evaluated. Select `adaptive`
explicitly to execute the procedure below. Clean circuit costs are unchanged.

At two-qubit infidelity 8 × 10⁻⁴, the first 50-attempt comparison accepted
17 outputs with adaptive history versus 7 with consecutive triples.
Sixteen adaptive outputs decoded exactly; one had fidelity 4/5. The
[implementation guide](../src/ADAPTIVE_HISTORY.md) gives the complete
comparison and explains why the default has not been switched automatically.

**Cost-optimized edition.** The default implementation now uses the
block structure of the code and paper-style source flags. Comparing
accepted runs with twelve ungauging SWAPs, the executed two-qubit
count falls from **17,577 to 8,052**, a **54.2% reduction**; the 80 Fredkins
are counted separately and unchanged. Peak live qubits fall from 77 to 75.
The former implementation remains available as `--extraction verified_cat`.
The new default is `--extraction optimized`. These cost figures concern
the noiseless schedule. A separate [depolarizing-noise runner](../src/DEPOLARIZING_SIMULATION.md)
now uses the same physical gadgets, with explicit channel assumptions.

This is a replacement procedure for the current five-vertex circuit in
[integrated V2](full_procedure_integrated_v2.md), starting from
[the rejection-reduction note](../src/note_reduce_postselection.md).
It retains the twenty enrichment Fredkins, the current twenty-edge graph,
vertex-X readout, gauged checks, gauge-Z readout, and correcting SWAPs.
The changes concern how measurement gadgets are prepared and how their
reports are used for recovery. The accompanying
[proof](full_procedure_reduced_rejection_proof.md) treats these changes
under the same **two faults in the entire attempt** assumption.

The main improvements are concrete:

1. Use two initial all-zero cat scans on the inexpensive path; retain
   adaptive whole-record repair when a nonzero scan is seen.
2. Use compact flagged extraction for the known B/C sources, rebuilding
   only that source if a flag fires. Group other cat controls within a
   matched C4 block where the proof permits correlated physical errors.
   Prepare known states by accepting either syndrome and correcting it.
3. While gauged, repair gauge-bit errors and even Gauss-sign patterns.
   Repeat a suspicious report instead of immediately discarding data.
   Certify the SWAP sign there instead of rejecting an odd vertex report early.
4. After ungauging, use the **joint B/C syndrome** to recover every
   unambiguous error class in the proven two-matched-block error model.
5. If a nonzero paired syndrome prevented certification, recover the
   data this way and run a fresh gauging/ungauging cycle on those data.

These rules remove specific unnecessary rejections. They do **not** establish
a globally optimal noisy yield. A genuinely nonzero paired syndrome
cannot simply be flipped to zero while gauged. This version instead
tries recovery after ungauging and repeats the gauging only when that
recovery is unambiguous. Section 12 explains the remaining limitations.

**Convention about the fraction.** In the starting note, \(5/8\) is the
ideal **acceptance** probability; the ideal rejection is \(3/8\).
Both ideal logical selections are unchanged here:

\[
\Pr(U=+1)=\frac34,\qquad
\Pr(\overline Z^B_0=+1\mid U=+1)=\frac56.
\]

No direct whole-block SWAP measurement replaces gauging and ungauging.
Appendix B gives a smaller graph as a separate option within the same
gauging construction; the main procedure uses the existing graph.

## 1. Registers, state, and what counts as a fault

B and C each have twenty physical qubits and encode two logical qubits
in the \([[20,2,6]]\) code. Their inner four-qubit blocks are

| Block label | Physical positions in either copy |
|---|---|
| a | 0,1,2,3 |
| b | 4,5,6,7 |
| c | 8,9,10,11 |
| d | 12,13,14,15 |
| e | 16,17,18,19 |

A **matched block label** includes the block of that label in both B
and C. Two such labels can contain sixteen data qubits in total.
Twenty gauge qubits \(A_q\) and five vertices a,b,c,d,e implement the
current graph. Cat leaves and one parity helper are temporary.

For the supports in Appendix A, write

\[
S^P_{D,s}=\prod_{q\in R_s}P_{D_q},\quad
T_v=\prod_{q\in J_v}\operatorname{SWAP}(B_q,C_q),\quad
U=\prod_vT_v.
\]

The intended input and unnormalized post-SWAP state are

\[
|\psi\rangle=|\overline{00}\rangle_B|\overline{+0}\rangle_C,
\qquad |\psi_+\rangle=\frac{I+U}{2}|\psi\rangle.
\]

Decoded logical B zero then leaves
\(|\overline{M0}\rangle_C\), with
\(|M\rangle=(2|0\rangle+|1\rangle)/\sqrt5\).

One faulty location is a preparation, gate, physical meter, or
single-qubit waiting interval. Gate errors can be arbitrary on the gate's
participants; reports can be wrong. Classical calculations are reliable.
The schedule is serial, with **every live qubit's waiting intervals counted**.
An X meter is H followed by a physical Z meter, with separate locations.
A Fredkin is an atomic three-qubit location, or is decomposed using those
same three physical qubits and every resulting location is counted.

There is no fresh fault allowance when a gadget repeats or a stage changes.
Correctness means the accepted C output has the correct decoded logical
state. At most two correctable physical errors can remain at the end.

## 2. Certify a reliable whole record from its history

The following rule is used at several levels, always on the **entire
specified record**.

```text
Measure a complete record, accepting either sign of every component.
Do not apply a correction between these rounds.
Mark every boundary where two consecutive complete records differ.
List every set of at most two bad rounds that touches every marked boundary.
For each observed whole record s, collect all rounds reporting s.
If no compatible bad-round set contains all those occurrences, s is certified.
Stop at the first prefix with a certified record, preferring the most recent one.
Use that whole record for correction. At most five rounds are needed.
```

For example, \(0,s,0,0,0\), with nonzero s, stops at round four and
uses zero: zero has already occurred in three rounds, which cannot all be
faulty under the two-fault bound. Consecutive occurrences are unnecessary.
The record could be a cat's adjacent-ZZ vector, twenty known-source
stabilizers, all 39 gauged checks, or the 36 original B/C checks.
The optimized cat has one special early exit: its **first two** complete
ZZ scans can both be zero. Section 3.1 explains why that is sufficient
under the two-fault budget. The source, graph, gauged, and terminal data
records use this adaptive certificate; the cat shortcut is the only
two-round exit.

Why does the certificate work? If two neighboring rounds are both clean,
their reports agree, because the complete observables commute and no
correction occurs between rounds. Every changed boundary therefore touches
a bad round. The actual bad-round set is among those enumerated. If none
can contain all occurrences of s, at least one occurrence of s is clean.
The controller learns the syndrome, without learning which occurrence
was clean. Later faults remain charged to the global budget.

For a concrete case, let A, B, C denote distinct complete vectors and
observe `A, B, B, C, C`. The early A-to-B change requires a fault in
round 1 or 2. At most one fault remains, so rounds 4 and 5 cannot both
be bad. C is certified at round five, although no triple agrees.
The [proof's Section 2](full_procedure_reduced_rejection_proof.md#2-a-certified-record-supplies-a-clean-reference-round)
establishes the five-round bound for every possible record history.

Nested rounds are literal physical operations. For example, a source
round includes the repair of every cat it uses, and all data idles while
those cats are repaired. This is essential to the counting argument.

The decision uses neither sampled fault locations nor bitwise majority.
The exact record, marked boundaries, compatible bad-round sets, and its
certificate are saved. The previous three-consecutive-equal, nine-round
rule remains reproducible with `--history-policy triple`.
At nonzero noise with more than two actual faults, a certificate is still
a statement conditional on the two-fault bound. Decoded output fidelity
must be evaluated separately; this is not a guarantee for arbitrary
numbers of stochastic faults.

## 3. The new cat gadget: correct its measured bit pattern

### 3.1. Physical circuit before the data coupling

To measure \(Q=\prod_j Q_j\), first choose the allowed port grouping
in Section 3.5. A Pauli port has one target; a SWAP port has the pair
\((B_q,C_q)\). Give each group one cat leaf. A leaf may control several
ports only inside its permitted matched block. For m leaves, prepare
the raw cat using

```text
reset all leaves to zero
H on leaf 0
CNOT(leaf 0 -> leaf 1), ..., CNOT(leaf m-2 -> leaf m-1)
```

Measure every adjacent parity \(Z_{\ell_j}Z_{\ell_{j+1}}\) in a complete
scan. For each parity use a newly reset helper w:

```text
reset w to zero
CNOT(leaf j -> w)
CNOT(leaf j+1 -> w)
measure w in Z
```

If the **first two complete scans both report all zero**, proceed with
no cat-bit correction. Otherwise retain both signs and use Section 2's
adaptive reference certificate, within five total scans including
the initial scans. This is repair, not rejection on the first negative.
Let the common vector be \(d=(d_0,\ldots,d_{m-2})\).
Calculate a bit pattern r by

\[
r_0=0,\qquad r_{j+1}=r_j\oplus d_j.
\]

Apply one physical X to every leaf with \(r_j=1\). These are independent
single-qubit gates; no new leaf-to-leaf gates are allowed after raw
preparation. If \(d=0\), apply nothing.

Why can two zero scans suffice? A dangerous error from raw cat preparation
already needs at least one fault. If raw preparation was faulty, one of
two scans must then be clean; an accepted clean zero scan removes that
correlated bit pattern. If raw preparation was clean, the cat was uniform
already, and each of at most two scan faults can flip only its participating
leaf. This argument **does not** authorize two arbitrary equal nonzero
records for repair. A noisy nonzero record could otherwise select an
incorrect correction on many leaves.

### 3.2. A four-leaf example

A preparation fault can give

\[
\frac{|0111\rangle+|1000\rangle}{\sqrt2}.
\]

Its adjacent-ZZ vector is \(d=(1,0,0)\). The old gadget rejects it.
Here three matching scans select \(r=0111\). Apply
\(X_{\ell_1}X_{\ell_2}X_{\ell_3}\), obtaining

\[
\frac{|0000\rangle+|1111\rangle}{\sqrt2}.
\]

This correction is allowed before the cat touches the retained data.
It does not rely on decoding an unknown logical data state.

### 3.3. Couple and read the repaired cat

Use CNOT from a leaf for an X port, CZ for a Z port, and Fredkin for
a SWAP port. Complete **all** controlled factors before measuring any
leaf in X. The XOR of all leaf-X reports is the report for Q.

For an ideal positive cat and leaf-report parity y, the operation is
proportional to

\[
\Pi_y(Q)=\frac{I+(-1)^yQ}{2}.
\]

**What has been corrected?** A clean adjacent-ZZ scan with record d
projects the cat onto
\(\operatorname{span}\{|r\rangle,|\bar r\rangle\}\).
The X correction maps this to
\(\operatorname{span}\{|0^m\rangle,|1^m\rangle\}\).
Each later verification or correction fault can add a bit error to only
one leaf. Its possible spread is limited to that leaf's allowed group.

**What remains uncertain?** The relative phase and amplitudes can still
be wrong. In particular a minus cat passes all adjacent-ZZ checks and
can reverse the check report. A faulty gadget is therefore treated as
a sum of terms

\[
D(aI+bQ),
\]

where D damages at most one permitted group per relevant fault, and a,b
need not specify the reported projector. Repetition of the *data*
record protects against this uncertainty. Cat repair does not make a
single data-check report trustworthy.

For \(m=1\), omit adjacent-ZZ scanning; there is no correlated bit pattern
to remove. The possible phase/report error is treated in the same way.

### 3.4. Simpler implementation option: local retries

Keeping the old three-positive-scan cat and rebuilding only a failed,
unused cat is also safe. Under at most two faults, at most two builds
can fail, so a cap of three builds suffices. All waiting faults count.
Do not restart **only the cat** after it has coupled to data. Section 3.6's
local rebuild instead discards the entire still-known source and is allowed
before that source participates in enrichment.

The protected-cat branch uses repair because it also handles a persistent
but known cat bit pattern without throwing the cat away. Neither choice
has a proven lower hardware cost without gate and idle error rates.

### 3.5. Group controls by the damage the next decoder can tolerate

Before terminal recovery, the proof tolerates arbitrary errors within
two matched inner blocks. It does not require one physical error per
fault. Exploit that distinction explicitly:

| Stage/check | Control assignment in the optimized procedure |
|---|---|
| Known B/C sources | Compact decoded block cat with flags; Section 3.6 |
| Graph-resource checks | One leaf per physical vertex/gauge target |
| Paired N checks | One leaf per matched C4 label, controlling all B/C factors there |
| Cycle checks | One leaf per gauge qubit |
| Gauss checks | One leaf for each gauge-X port, plus one leaf controlling all four SWAPs in its matched data block |
| Terminal original-code checks | One leaf per physical data qubit |

For example, a paired inner check has eight Pauli ports but all belong
to matched label a. One control leaf can measure that product using
eight couplings. A paired upper check has sixteen ports in four matched
labels: four leaves suffice, rather than sixteen. A Gauss cat uses nine
leaves rather than twelve on the current graph.

Gauge targets remain separate because full cut decoding tolerates only
two bad gauge bits. Terminal data targets remain separate because faults
after the terminal recovery reference must leave at most two **physical**
errors for final B readout and the decoded-output guarantee.

This is a stage-specific grouping rule, not permission to fan one
ancilla through arbitrary data blocks.

### 3.6. Paper-style flagged extraction for the known B/C sources

For a weight-eight original source check, its support has two positions
in each of four inner blocks. Use one syndrome leaf s and three flag
leaves f1,f2,f3, assigning one leaf to each block. The physical circuit is:

```text
prepare s in plus, f1/f2/f3 in zero
CNOT(s -> f1), CNOT(s -> f2), CNOT(s -> f3)
each leaf controls the first target in its block
each leaf controls the second target in its block
CNOT(s -> f3), CNOT(s -> f2), CNOT(s -> f1)
measure f1/f2/f3 in Z, and s in X
```

Use CNOT target couplings for an X check and CZ for a Z check. There
are **8 target couplings + 6 flag CNOTs = 14 two-qubit gates**. This is
the decoded-cat pattern of the [paper's weight-eight extraction circuit](../arXiv-2609.03194v1/figures/new_se_circuit.png),
with target order chosen so a leaf's two data targets lie in the same
inner block. For R5 the blocks are a:(0,3), b:(6,7), c:(10,11), d:(12,15);
visit 0,6,10,12, then 3,7,11,15.

With ideal gates, uncomputing the fanout returns every flag to zero for
**any data input**. The syndrome leaf measures the full joint Pauli;
the circuit does not measure each block separately.

The source's inner weight-four check uses one leaf and four target
couplings. Both inner checks therefore cost eight couplings in total.
This has the paper's eight-gate count, but uses two sequential block-local
measurements, not its simultaneous data-refresh/teleportation circuit.
The six-body known logical checks use three block leaves, two flags,
and ten two-qubit gates. All six source circuit shapes are covered by
the finite locality certificate linked in Appendix C.

If any source flag reports one, finish reading that helper and rebuild
**only that known B or C source**, before enrichment. Restart its full
known-state history. Keep the other source, with all its waiting locations
counted. Allow three local builds; two faults can cause at most two
flagged failures. This turns a flag into a local resource retry rather
than factory rejection within the two-fault bound.

A zero-flag source gadget with k faults, k<=2, has an operator expansion
whose data damage, modulo the measured check, occupies at most k inner
blocks. The certificate enumerates Pauli faults at preparations, gates,
meters, and idles, including pairs that hide one another's flags. The
companion proof explains the extension to arbitrary local errors.

We use this compact flagged gadget on known sources. We do **not** pass
its possible two-block residual errors directly to the final physical
weight-two readout decoder. That distinction is why terminal extraction
keeps its individually controlled data ports.

## 4. Prepare B and C by syndrome correction

One can use the existing unitary encoder, or start from physical zeros.
Then measure these complete known-state families, using Section 3.6's
compact source gadgets (or repaired cats in the retained baseline):

\[
\begin{aligned}
\mathcal F_B&=(S^X_{B,0:8},S^Z_{B,0:8},\overline Z^B_0,\overline Z^B_1),\\
\mathcal F_C&=(S^X_{C,0:8},S^Z_{C,0:8},\overline X^C_0,\overline Z^C_1).
\end{aligned}
\]

Do B first, then C; obtain a reliable twenty-bit record for each.
Unlike the old source filter, **do not require zero**.

For commuting independent generators \(g_1,\ldots,g_n\), find a Pauli R
with

\[
Rg_j=(-1)^{s_j}g_jR.
\]

Apply its single-qubit factors in physical-label order. This sends the
recorded eigenspace to the all-positive eigenspace. Here \(n=20\), so
each complete eigenspace is one dimensional: the positive space is
exactly the desired known source. Corrections may have large weight;
they are **not** constrained to the ordinary weight-two decoder.

For implementation, write each Pauli as \(X^xZ^z\). If generator j has
binary X and Z supports \(a_j,b_j\), solve

\[
b_j\cdot x+a_j\cdot z=s_j\pmod2
\]

by binary Gaussian elimination. Fix free variables to zero for a
deterministic rule. Execute one X, Y, or Z per nonidentity physical
factor; Y is one gate, not an X gate followed by a Z gate.

**Concrete distinction.** In a known-state preparation, correcting a
logical-check sign is legitimate: we deliberately want a specified
logical state. Later, when B and C contain the magic-producing
superposition, those source logical checks must not be measured again.

This removes the illustrative \(2^{-19}\) source-selection penalty.
That penalty was already absent in the current noiseless unitary encoder;
the new feature is correction instead of positive-only verification
under faults. B waiting during C and graph preparation is included.

## 5. Prepare and correct the current graph resource

The twenty edges in Appendix A have endpoints \(u_q,v_q\). Prepare

\[
|\Gamma\rangle=\frac1{\sqrt{32}}\sum_{t\in\{0,1\}^5}
|t\rangle_V|p(t)\rangle_A,
\qquad p(t)_q=t_{u_q}\oplus t_{v_q},
\]

using H on every vertex and the forty endpoint-to-edge CNOTs, in the
same order as integrated V2.

Measure the complete 25-generator family

\[
K_v=X_v\prod_{q\ni v}X_{A_q},\qquad
K_q=Z_{u_q}Z_{A_q}Z_{v_q}
\]

in the order \(K_a,\ldots,K_e,K_0,\ldots,K_{19}\).
Keep either sign, obtain Section 2's certified complete record, and solve
the same Pauli sign-correction equations as for B and C, now on 25 qubits.
Apply that correction before enrichment.

**Example.** A raw \(X_a\) partway through the graph encoder can create
several incorrect edge bits. Ordinary radius-two gauge decoding is not
yet applicable. The 25-generator correction is allowed to remove that
whole syndrome because the resource is a **known unique stabilizer
state**. Late faults after its clean reference round remain local;
there are no further vertex-to-edge preparation CNOTs.

One may instead rebuild a failed graph resource before using it, but
the retained B/C waiting locations still count. The signed-state
correction above avoids making resource failure an automatic factory
failure.

## 6. Gauge with the original enrichment and vertex readout

Vertex v controls four Fredkins, one for every \(q\in J_v\), exactly as
in V2. Complete all twenty. This gives ideally

\[
\frac1{\sqrt{32}}\sum_t|t\rangle_V|p(t)\rangle_A V_t|\psi\rangle,
\qquad V_t=\prod_v T_v^{t_v}.
\]

Measure all five vertices in X, recording b. **Keep either reported
parity for now**, and apply

\[
F_b=Z_{A_7}^{b_b}Z_{A_{11}}^{b_c}Z_{A_3}^{b_d}Z_{A_0}^{b_e}.
\]

These gates remove the known nonroot measurement signs. Under faults
they may be wrong; the following gauged checks protect the logical
selection. For parity \(r=\bigoplus_v b_v\), the ideal corrected state
is proportional to

\[
|\Phi_{(-1)^r}\rangle
=\sum_{t:t_a=0}|p(t)\rangle_A V_t\frac{I+(-1)^rU}{2}|\psi\rangle.
\]

The positive-SWAP selection is **postponed**, not removed: Section 7
requires a certified even Gauss product. With no faults, an odd vertex
parity produces an odd Gauss product and is rejected there. The ideal
success remains \(3/4\) for this selection and \(5/8\) overall.

This rescues a false odd vertex report. For example, flip only the root
a report when the actual state is positive. The nonroot feedforward
gates are unchanged, so the gauged state remains positive; its repeated
Gauss record certifies this and the attempt can continue. The old
immediate parity rejection would discard it. No reported odd sign is
arbitrarily forced positive.

## 7. While gauged: collect the full syndrome and repair the gauge part

### 7.1. The same 39 checks, with different report handling

One full round measures, in order,

\[
\begin{aligned}
N_s^P&=S^P_{B,s}S^P_{C,s} &&(18\text{ paired checks}),\\
L_\eta&=\prod_{q\in\eta}Z_{A_q} &&(16\text{ cycle checks}),\\
G_v&=\left(\prod_{q\ni v}X_{A_q}\right)T_v &&(5\text{ Gauss checks}).
\end{aligned}
\]

These 39 observables commute. Use one repaired, appropriately grouped
cat per check. A Gauss cat has eight individually controlled gauge-X
ports and one leaf controlling its four data-SWAP ports: nine leaves
on the current graph. Retain both signs of every check, without correcting between
rounds. Obtain a reliable common record \((n,l,g)\) using Section 2.

The interpretation is:

| Part of the common record | Action |
|---|---|
| \(n\ne0\) | Mark this cycle uncertified; try the ungauge/recover/re-gauge fallback in Section 9.7 |
| l has no weight-at-most-two edge-X explanation | Reject as inconsistent with the bound |
| \(n=0\) and \(g_a\oplus\cdots\oplus g_e=1\) | Reject: the certified SWAP sector is negative |
| Otherwise | Correct the gauge X and Z patterns below, then continue |

A cycle with \(n=0\) and even g is **certified**. For an uncertified
cycle, do the cycle-X repair, omit Gauss-sign repair, and continue to
ungauging; do not infer its logical SWAP sign from g. A lone negative
report no longer immediately rejects. For example,
\((0,0,0), (0,0,g), (0,0,0), (0,0,0)\) uses zero at round four:
three whole zero records have occurred. The controller never labels
the middle round as faulty.

### 7.2. Correct cycle signs by an edge-X lookup

For a binary edge mask e, define

\[
c(e)_\eta=\bigoplus_{q\in\eta}e_q.
\]

Enumerate the 211 masks of weight zero, one, or two. Choose the unique
one with \(c(e)=l\), and apply \(X_{A_q}\) for its set bits.
The cycle constraints define the graph's cut code, whose distance is
eight. Two weight-at-most-two masks cannot have the same cycle syndrome.

**Example.** An \(X_{A_7}\) flips the cycle signs for
\((7,15),(7,8,11),(7,14,3),(7,4,0)\). The lookup selects edge 7 and
corrects it. The old positive-only cycle filter discards this event.

Edge-X corrections commute with every Gauss and paired check. A faulty
correction gate can add one residual edge-bit error, counted in the
remaining fault budget.

### 7.3. Correct even Gauss signs with the root tree

If the five Gauss bits have even parity, apply

\[
Z_{A_7}^{g_b}Z_{A_{11}}^{g_c}Z_{A_3}^{g_d}Z_{A_0}^{g_e}.
\]

A Z on an edge reverses the Gauss signs at its two endpoints. Thus
the nonroot signs are cleared, and even parity clears the root sign too.
These corrections commute with all cycle and paired checks.

**Example.** A \(Z_{A_7}\) gives negative Gauss signs at a and b.
This is an even pattern. Another \(Z_{A_7}\) repairs it. By contrast,
five signs with odd parity cannot be cleared by edge-Z gates:

\[
\prod_vG_v=U.
\]

The paired-zero condition is part of this rule. It is what makes
the inferred SWAP sector safe in the presence of bounded data damage.
Neither an isolated Gauss measurement nor an arbitrary sign change
is a substitute for that condition.

## 8. Ungauge using the full twenty-bit edge report

Measure all twenty A qubits in Z. For report m, find the unique cut
\(p(\widehat t)\) within Hamming distance two, using \(\widehat t_a=0\).
Reject if it does not exist. Apply the ordinary SWAPs

\[
V_{\widehat t}=\prod_{v:\widehat t_v=1}T_v
\]

as individual physical SWAP gates in increasing q. This is the original
ungauging circuit. Full decoding remains necessary even after the
gauge repair: faults after its reference round or during readout can
leave wrong edge bits.

On an ideal component,
\(V_{\widehat t}V_{\widehat t}|\psi_+\rangle=|\psi_+\rangle\).
An erroneous \(X_{B_4}\) can move to \(X_{C_4}\), but remains in
matched label b. A faulty correcting SWAP also affects just its own
matched label.

After a certified cycle, the state is a sum of terms

\[
E_\nu|\psi_+\rangle,
\]

each supported on **at most two matched labels**. This permits
correlated errors of weight greater than two; the next decoder is
designed for precisely that situation.

After an uncertified cycle, the same support bound holds but both
reference states \(|\psi_+\rangle\) and
\(|\psi_-\rangle=(I-U)|\psi\rangle/2\) may occur. Such data must use
the fallback in Section 9.7, never proceed directly to final extraction.

## 9. Replace the positive original-code filter by joint recovery

### 9.1. Obtain the syndrome without rejecting its signs

Measure the original 36 checks in the same order as V2:

\[
\mathcal O=(S^X_{B,0:8},S^Z_{B,0:8},S^X_{C,0:8},S^Z_{C,0:8}).
\]

Use protected cats with one leaf per physical data qubit and the
two-initial-zero-scan shortcut. Keep either check sign and use Section 2's
certified complete record, without intermediate corrections. Call its
eighteen-bit records \(s_B,s_C\).

Alternatively, the compact terminal option executes the
[flagged gadgets](compact_terminal_extraction.md) for these same checks.
Zero flags continue compact acquisition. A nonzero flag receives its
certified preliminary repair, and the same retained B/C data undergo a
fresh protected acquisition before this joint lookup is used. An
unfinished compact history is saved but is not used as the final syndrome.

The new lookup is **not** the ordinary minimum-weight-two decoder.
It explicitly includes all errors on two whole matched blocks, and
rejects only when the available syndrome information leaves a logical
ambiguity in that error model.

### 9.2. The exact lookup, described as an executable recipe

Let \(\mathcal S\) be the stabilizer group of one original code. Two
Paulis are equivalent if they differ by an element of \(\mathcal S\),
ignoring their overall phase. They then act identically on every
encoded state, including states entangled with the other copy.

For every two-label set \(F\subset\{a,b,c,d,e\}\):

1. Enumerate every Pauli E supported on the eight positions in F.
2. Compute its eighteen-bit original-code syndrome.
3. Store a representative \(E_F(s)\) for every syndrome reached.

For a **fixed** F, all representatives of the same syndrome are
equivalent. This follows from the two-block lemma: their product is
an undetected error still supported in F. Thus each \(E_F(s)\) is
well defined up to stabilizers. Choose a minimum-weight representative,
with a fixed binary-mask tie-break, to reduce correction gates.

At runtime:

```text
candidates = empty
for each of the ten two-label sets F:
    if E_F(s_B) and E_F(s_C) both exist:
        add (E_F(s_B), E_F(s_C))

if candidates is empty: reject
if two candidates differ by a nontrivial logical Pauli on B or C: reject
otherwise choose one candidate and apply its inverse, one physical Pauli at a time
```

Paulis are their own inverses up to phase. Both syndromes must be
explained using the **same** F. Errors on fewer than two labels are
included because their support is contained in some two-label set.

This is the largest acceptance set for a decoder using only this
joint syndrome, the common-two-label error bound, and a requirement
to preserve arbitrary logical states in the original product code.
It is not a claim of optimality over full circuit histories, extra
flags, or the particular known spectator logical qubits.

### 9.3. Example: a nonzero syndrome that can be corrected

Suppose a late error, after the relevant gauged checks, is
\(X_{B_0}\). It flips B's Z-check bits s=0 and s=5.
Across **all** possible two-label sets, every error producing that
syndrome is equivalent to \(X_{B_0}\). With \(s_C=0\), the joint lookup
therefore applies \(X_{B_0}\), recovering \(|\psi_+\rangle\).
The old terminal positive filter rejects this same nonzero syndrome.

This example concerns a late error. If the same error is already present
during a clean gauged paired-check round, Section 7 marks that cycle
uncertified and invokes the recovery/re-gauging fallback below.

### 9.4. Example: why some two-block syndromes must remain ambiguous

On B, compare

\[
E_1=X_2X_3,\qquad E_2=X_8X_{11}X_{12}X_{15}.
\]

Both satisfy the two-block bound. They have the same original syndrome,
but

\[
E_1E_2=X_2X_3X_8X_{11}X_{12}X_{15}=\overline X_0.
\]

Correcting \(E_2\) as though it were \(E_1\) introduces a logical X.
With no further information and zero C syndrome, the joint decoder
rejects. A minimum-weight guess would be unsafe.

### 9.5. Example: C can resolve B's ambiguity

Now take the actual errors to be

\[
E_B=X_2X_3,\qquad E_C=X_0X_4.
\]

C's two negative inner-Z parities locate labels a and b. Since there
are at most two matched labels altogether, the common set must be
\(F=\{a,b\}\). Within that fixed set, B's syndrome has a unique
correction class. The joint decoder accepts and repairs both copies,
although B's syndrome alone has four possible logical classes.

With the specified tie-break, one correction is \(X_{B_0}X_{B_1}\)
and \(X_{C_0}X_{C_4}\). On B the correction times the actual error is
\(X_0X_1X_2X_3\), an inner stabilizer; on C it is I. Thus both copies
are restored even though the B correction is not the error's literal inverse.

This is useful location information obtained from the existing checks;
no new flag qubits are needed for this example.

### 9.6. What happens to faults during this recovery?

The common record equals a true syndrome in a clean reference round.
At that reference point the two-label lookup applies to all inherited
errors. Its selected correction removes those errors up to stabilizers.
Every later fault in a Pauli-check gadget, correction gate, or data idle
adds at most one physical data error. Single-qubit Pauli corrections
do not spread them. Consequently the final residual errors are ordinary
weight-at-most-two errors on each copy.

This one recovery replaces V2's three positive original-code rounds
**and** its mandatory subsequent small-error recovery. If desired,
one can add the old repeated weight-two recovery afterward to clean
physical residual errors; it is not needed for the decoded-output
claim, and its gates and waiting errors must still count.

### 9.7. Recover and re-gauge after a nonzero paired syndrome

This fallback avoids having to implement an unproved one-copy recovery
inside the gauged code.

```text
If the gauged stopping record had n != 0:
    ungauge normally, using the root-a cut representative
    obtain the repeated original B/C syndrome
    apply the joint correction if its class is unambiguous; otherwise reject
    prepare and correct a fresh graph resource
    run the same enrichment, vertex readout, gauged checks, and ungauging again
    do not reset B or C, and do not measure their source logical checks
```

Allow at most **three total gauging/ungauging cycles**, including the
first. On every cycle postpone the vertex-parity decision to the
repeated gauged record, as in Section 6.
Only a cycle certified by paired zero and even Gauss parity can proceed,
after terminal recovery, to final B extraction.

Why can this help? Suppose \(X_{B_0}\) occurs on a positive gauged state.
It gives a nonzero paired syndrome. A positive a-Gauss measurement can
leave \((X_{B_0}+X_{C_0})|\Phi_+\rangle/2\), and a negative one can
leave the corresponding difference. After ungauging, the original
syndrome distinguishes the B-error and C-error components. Either
component is corrected to \(|\psi_+\rangle\), up to a scalar. Re-gauging
then certifies that sector with fresh verified resources, retaining
those data instead of discarding them at the first paired check.

More precisely, before certification the restored logical data lie in

\[
\mathcal K=\operatorname{span}\{|\psi\rangle,U|\psi\rangle\}
=\operatorname{span}\{|\psi_+\rangle,|\psi_-\rangle\}.
\]

The joint recovery is valid on **every** original-code logical state,
so it restores a state in this span without assuming the positive sector.
A later certified positive projection maps that span to the desired
one-dimensional \(|\psi_+\rangle\) subspace. It may instead reject;
the fallback does not promise to turn a genuine negative resource positive.

Every uncertified cycle has a true nonzero paired syndrome in a clean
round, requiring a fault since the preceding recovery reference.
Two faults can cause at most two such fallbacks. The third cycle cannot
need another fallback under the bound. New graph preparation, extra
Fredkins, and all B/C waiting errors remain in the same global budget.

## 10. Read B and retain the quantum C output

Measure all twenty B qubits in Z. For report word n, compute the
nine Z-check parities. Choose a weight-at-most-two binary mask e with
the same parities and set \(n'=n\oplus e\). Reject if no such mask exists.
Use the fixed minimum-weight, then lexicographic, tie-break of V2.

Keep only

\[
n'_0\oplus n'_3\oplus n'_6\oplus n'_7\oplus n'_{18}\oplus n'_{19}=0.
\]

The logical first-pair state before this selection is

\[
\frac{2|00\rangle+|01\rangle+|10\rangle}{\sqrt6}.
\]

The retained state in C is therefore \(|\overline{M0}\rangle\), up to
correctable physical errors. Physical errors or bad reports on B occupy
at most two positions under the remaining global budget. C's waiting
errors during B readout are included in that same budget.

## 11. Full schedule and what has improved

| Stage | Main procedure | Remaining rejection |
|---|---|---|
| Protected check's cat | Two initially zero scans, otherwise adaptive whole-record repair within five scans; use allowed control groups | No agreement-limit rejection |
| B and C sources | Compact source flags; local source rebuild on a flag; adaptive known-state syndrome and Pauli correction | Three flagged local builds |
| Graph source | Adaptive certificate for its 25 generators | No agreement-limit rejection |
| Enrichment and vertex readout | Original twenty Fredkins; retain vertex reports and postpone the SWAP-sign decision | No early vertex-parity rejection |
| Gauged verification | Adaptive 39-bit record; repair cycle and even Gauss syndromes; mark nonzero paired syndrome for fallback | Certified odd Gauss parity, inconsistent cycle lookup, or fallback limit |
| Ungauging | Decode all twenty reports, then physical SWAPs | No cut within distance two |
| Original-code recovery | Adaptive 36-bit record; joint two-label lookup; re-gauge uncertified cycles | Absent or logically ambiguous candidate class |
| B extraction | Full classical decoding, then original logical selection | No readout correction, or decoded logical B one |

The adaptive stopping rule always produces a record within five rounds;
its clean-reference guarantee is conditional on at most two faults.
Radius-two gauge lookups cannot fail under that fault model and the
stated input bounds, but can fail outside it. Data ambiguity and the logical selection rules remain substantive
rejection mechanisms. A nonzero paired syndrome causes an attempted
recovery and another gauging cycle, whose success is not guaranteed.

With no faults and the unitary source encoder, all these repeated
records on an accepted branch are zero and stop after three rounds.
The negative-SWAP branch instead has a stable negative root Gauss sign.
No new ideal probability
penalty is introduced. There are still 420 check gadgets in that clean
schedule: 120 source, 75 graph, 117 gauged, and 108 terminal. V2 uses
528, including its separate 108-gadget recovery. Both counts exclude
the internal cat-parity tests. The optimized schedule has 540 complete
cat-verification scans, instead of 1,260, and 168 source-flag readouts.
The complete data-syndrome histories still have three rounds.

The measured and independently counted two-qubit costs are:

| Contribution | Previous `verified_cat` | New default `optimized` |
|---|---:|---:|
| B/C known-state checking | 4,728 | 1,032 |
| Graph-resource checking | 1,995 | 1,515 |
| Three gauged rounds | 6,465 | 2,148 |
| Terminal joint recovery | 4,236 | 3,204 |
| Input encoder + graph preparation | 141 | 141 |
| **Total before selected ungauging SWAPs** | **17,565** | **8,040** |

Add the same 0--16 ordinary SWAPs to either column for the same decoded
cut. With twelve SWAPs, this is 17,577 versus 8,052. The 80 atomic
Fredkins are separate from both columns. These are full physical
gadget counts, not estimates from logical operations.

One twenty-check source pass falls from 788 gates to 172: ten inner
checks at four gates each, eight upper checks at fourteen each, and
two logical checks at ten each. This is where the paper's compact
extraction gives the strongest direct saving.

Postponing the vertex-parity decision also means that a noiseless
negative-SWAP branch now runs gauged verification before being discarded.
This trades more work on those branches for recovery of false odd
reports; retaining the early cut is an optional cost/yield tradeoff.

With serial helper reuse, the optimized peak is **75 physical qubits**.
It occurs during graph verification: 40 data + 20 gauge + 5 vertices
plus 9 cat leaves and one parity helper. The former sixteen-leaf paired
checks no longer set the peak. The baseline still uses 77.
The clean main schedule still contains 80 Fredkins:
20 enrichment and 60 in three gauged rounds. A history requiring extra
gauged rounds can use up to \(20+9(5\cdot4)=200\) Fredkins. Variable
waiting time and correction gates must be included in any practical
cost comparison. The fallback permits up to three cycles; 600 Fredkins
is a loose bound obtained by multiplying their individual caps. The
clean 420-gadget count concerns the single-cycle noiseless schedule.

The finite audit finds 27,136 reachable **single-copy** syndromes for
the two-block error class. Of these, 23,281 have one stabilizer coset,
3,675 have four, and 180 have ten. The joint decoder can accept some
cases from the latter groups, as Section 9.5 illustrates. These counts
are not probabilities and do not predict noisy yield.

## 12. Further rejection reduction: precise opportunities and limits

**Direct recovery inside the gauged code remains an opportunity.** The
fallback already salvages unambiguously recoverable paired-syndrome
events through an extra gauging/ungauging cycle. Avoiding that extra
cycle needs more work: the paired syndrome alone does not identify which
copy is damaged, and a one-copy correction can interact with partial
SWAPs and the logical sector. A direct gadget must prove sector preservation
and correctability of its output; “distance six corrects it” is insufficient.

**Located-block recovery is valid if the location record is reliable.**
For a known set F of at most two inner blocks on each copy, every Pauli
on F with a given original syndrome is equivalent. That is erasure
recovery, and the table \(E_F(s)\) already implements it. But a two-fault
protocol must include false flags, missed flags, faults in flag gadgets,
and faults outside the flagged set. A flag is information to constrain
the candidate set; it is not permission to assume all other blocks clean.

General Pauli flag constructions can reduce ancilla usage, but substituting
one for a Shor cat needs a code- and circuit-specific correction table.
The ordinary Pauli-check results of
[Chao and Reichardt](https://arxiv.org/abs/1912.09549) and
[Chamberland and Beverland](https://arxiv.org/abs/1708.02246) do not by
themselves certify a flagged Fredkin or Gauss gadget. Section 3.6 uses
a specifically certified source circuit; the other stages use protected
cats with explicit matched-block or physical-qubit spread bounds.

**The remaining terminal cost is deliberate.** The original paper's
152-gate complete extraction uses a circuit-wide decoder and its flagged
syndrome history. Replacing our terminal extraction by that circuit
requires a new decoder proof for late correlated errors. The present
terminal pass is 534 gates, repeated three times on each copy. We have
reduced its cat-verification cost while preserving the final physical
weight-two argument, rather than assuming that the source's flagged
locality guarantee is sufficient at the output boundary.

**Use the entire history to make a stronger candidate set.** The lookup
in Section 9 deliberately forgets when an error occurred. A full-history
decoder could retain candidate fault paths, corrections, flags, and
their minimum required fault count, then use only compatible residual
errors. It may accept a syndrome rejected by the broad two-label table.
The safe test is that every surviving same-record error pair acts
identically on the protected logical state after the chosen recovery.
Choosing only the most likely candidate weakens the present guarantee.

**Shorter stopping rules save waiting errors.** Section 2 now uses an
explicit complete-history certificate, with a proof in the companion note.
The adaptive
Shor-style schemes of
[Tansuwannont, Pato, and Brown](https://arxiv.org/abs/2208.05601)
use syndrome differences to reduce measurement rounds. Their stopping
conditions require their corresponding input-error and gadget conditions.
Our argument instead derives the needed clean-reference property directly
for the commuting families here, including the non-Pauli gauged checks.
It does not import a Pauli-code recovery theorem for the two-whole-block
input class. A noise-aware decoder exploiting individual bit changes and
gate correlations remains a possible further improvement.

**Track frames where the hardware benefits.** Pauli corrections in
known-state preparation and after ungauging can often be tracked instead
of executed. Through an enrichment Fredkin, an X on a controller acquires
data SWAPs, so a frame implementation must propagate the full operation,
not just flip later Pauli signs. This note specifies physical corrections
so that every new location and propagation rule is explicit.

**Optimize expected cost, not only acceptance.** A useful objective is
\(\mathbb E[\text{gates or elapsed time per attempt}]/
\Pr(\text{accepted and logically correct})\).
No numerical improvement in this quantity is asserted without a noise
model. Extra rounds can rescue false reports while adding waiting errors.

## Appendix A. Complete physical data for the main procedure

For either P=X or P=Z, the nine independent check supports are

\[
\begin{aligned}
R_0&=(0,1,2,3),&R_1&=(4,5,6,7),\\
R_2&=(8,9,10,11),&R_3&=(12,13,14,15),\\
R_4&=(16,17,18,19),\\
R_5&=(0,3,6,7,10,11,12,15),\\
R_6&=(4,7,8,9,14,15,16,19),\\
R_7&=(1,2,8,11,12,13,18,19),\\
R_8&=(2,3,5,6,13,14,16,17).
\end{aligned}
\]

Logical supports are

\[
\overline X_0=X_{2,3,8,11,12,15},\quad
\overline Z_0=Z_{0,3,6,7,18,19},\quad
\overline Z_1=Z_{2,3,8,11,12,15}.
\]

In gauge-edge order q=0 through 19 the endpoints are

```text
ae, ce, cd, ad, be, de, ad, ab, bc, be,
ae, ac, ac, cd, bd, ab, bd, de, ce, bc.
```

The cycle supports, in measurement order, are

```text
(7,15), (11,12), (3,6), (0,10), (8,19),
(14,16), (4,9), (2,13), (1,18), (5,17),
(7,8,11), (7,14,3), (7,4,0),
(11,2,3), (11,1,0), (3,5,0).
```

X checks precede Z checks; indices increase within each family.
Gauss vertices are a,b,c,d,e. Original-code order is B-X, B-Z, C-X,
C-Z. In all corrections visit physical labels in order. For the
terminal lookup, minimize total physical correction weight, then the
binary masks \((x_B,z_B,x_C,z_C)\); Appendix C implements that rule.

## Appendix B. Optional smaller graph, still gauging and ungauging

This appendix changes only the graph resource and its gauge checks.
The forty data qubits, five four-qubit controllers, enrichment,
logical selections, and terminal recovery remain the same.

For this particular paired/cycle/Gauss protocol, the necessary graph
properties are connectivity and a cut-code distance of at least five,
which uniquely corrects two edge-bit errors. The twenty-edge doubled
\(K_5\) has distance eight, more than this two-fault proof requires.

Take simple \(K_5\) and add three parallel edges forming an edge cover:
ab, cd, ae. Use these thirteen edges:

```text
q:  0  1  2  3  4  5  6  7  8  9 10 11 12
   ab ac ad ae bc bd be cd ce de ab cd ae
```

The degrees are \((6,5,5,5,5)\), and every nontrivial cut has at least
five edges. The graph therefore uses **13 gauge qubits + 5 vertices =
18 resource qubits**, instead of 25, and still corrects two edge-bit
errors. The optimized peak is **66 physical qubits** (70 with the
retained baseline extraction).

Use root tree edges \((0,1,2,3)\) for b,c,d,e. A convenient independent
cycle basis is

```text
(0,1,4), (0,2,5), (0,3,6),
(1,2,7), (1,3,8), (2,3,9),
(0,10), (1,2,11), (3,12).
```

Replace the graph preparation by 26 endpoint-to-edge CNOTs. Its complete
known-state family has 18 generators. Gauged rounds now have
18 paired + 9 cycle + 5 Gauss = 32 checks. A Gauss cat has nine or ten
physical ports, depending on the vertex degree, but uses six or seven
leaves after grouping its four SWAP ports. The paired-check cats use
at most four leaves. Graph verification uses at most seven leaves
plus its parity helper while the five vertices remain live.

Use the same algorithms, substituting thirteen-bit cuts, the new cycle
basis, and the new root tree. In particular, gauge readout still needs
radius-two decoding; all gauge bits are decoded before data SWAPs.
The ideal state identity using t and its complement, and
\(\prod_vG_v=U\), are unchanged. The proof's required graph distance
is now five. The clean total is 378 check gadgets, using the same
three-round schedules: 120 source + 54 graph + 96 gauged + 108 terminal.
The optimized two-qubit cost before selected SWAPs is 7,120, compared
with 16,357 for baseline extraction on this same smaller graph.

Thirteen edges is minimal **for a five-vertex loopless multigraph with
one qubit per edge and distance at least five**: every vertex must have
degree at least five, requiring at least \(\lceil25/2\rceil=13\) edges.
This is a restricted graph optimality statement. The existing graph has
more margin against errors beyond the two-fault guarantee; the smaller
one is not automatically better under a specified hardware noise model.

## Appendix C. Reproducible certificates and implementation status

Run from the repository root:

```sh
python3 src/check_reduced_rejection.py
```

The [audit script](../src/check_reduced_rejection.py) checks the code
supports against the local manuscript, distance and stabilizer ranks,
all 65,536 Paulis on each of the ten fixed two-block sets, the exact
syndrome-class counts, the joint recovery example, cat bit-pattern
repair through sixteen leaves, gauge-bit lookup uniqueness, all sixteen
even Gauss patterns, and both graphs' cut distances. It also checks
the complete source sign-correction equations.

Its [JSON certificate](../output/c4-helix-reduced-rejection-certificates.json)
records the results. These are algebraic checks supporting the separate
proof. They are **not** an enumeration of all physical fault pairs or
a simulation of the modified adaptive circuit. The existing
`simulate_c4_helix_gadgets.py` still implements integrated V2; it has
not been silently changed to this proposal.

The [optimized-gadget audit](../src/check_optimized_extraction.py) and
[its certificate](../output/c4-helix-optimized-extraction-certificates.json)
add all six source circuit shapes and two-zero-scan cats of sizes 2--16.
They propagate arbitrary participating-qubit Pauli faults and single-qubit
idles, and check every accepted pair of merged fault signatures. Simulator
tests compare the actual physical event programs to the audited programs.
This is a gadget-local certificate, not enumeration of factory fault pairs.

The new, separate [noiseless sparse simulator](../src/simulate_c4_helix_reduced.py)
now executes this procedure with all physical correction gadgets. Its
[validation guide](../src/REDUCED_REJECTION_SIMULATION.md) describes the
saved examples, tests, and read-only run verifier. The separate
[depolarizing implementation](../src/DEPOLARIZING_SIMULATION.md) adds sampled
X/Y/Z gate errors and exact accepted-state logical diagnostics. Its first
50-attempt pilot establishes feasibility; it does not establish an
optimized-versus-baseline improvement in noisy yield.
