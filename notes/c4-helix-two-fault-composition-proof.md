# A two-fault composition proof for verified C4-Helix gauging

> **Scope correction.** The theorem here concerns the augmented circuit
> with an independent whole-block SWAP verifier. That verifier can replace
> the graph-based state preparation, so this theorem does not by itself
> resolve the requested protection of the original construction. The
> Pauli-gadget, code-support, and recovery lemmas remain useful. The revised
> circuit and its composition argument are in
> [Protecting the original gauging by repeating complete cycles](c4-helix-repeated-gauging-fault-tolerance.md).

This note completes the analytical composition argument for a precisely
specified version of the circuit in
[the verified-gauging note](c4-helix-verified-gauging-and-ungauging.md).
The graph, block-aligned controllers, coherent frame removal, and three
verification sweeps are retained. The previously unspecified final recovery
is replaced by an explicit bounded repeated-syndrome procedure.

**Result.** For any set of at most two local circuit faults, every accepted
output has the intended logical magic state. Ancilla phase errors, incorrect
physical measurement reports, storage faults, physical recovery faults, and
destructive logical-readout faults are included in that same budget.
The output may retain a correctable physical error. This is the usual
fault-tolerance guarantee: an error at the last output location cannot be
required to disappear physically.

The crucial proof device is a space of operators containing local errors,
original code stabilizers, and I/U combinations. It is closed under the
faulty measurement gadgets. We first establish that invariant, then use a
clean sweep to obtain the desired projection, and finally prove the noisy
recovery/readout interface.

## 1. Exact scope of the theorem

The physical blocks B and C each use the \([[20,2,6]]\) C4-Helix code.
Its checks and logical representatives are those in
[Table I of the manuscript](../arXiv-2609.03194v1/appendix.tex).
Let

\[
|\psi\rangle=|\overline{00}\rangle_B|\overline{+0}\rangle_C,
\quad U=\prod_{q=0}^{19}\mathrm{SWAP}(B_q,C_q),
\quad \Pi_+=\frac{I+U}{2}.
\]

We aim to prepare \(\Pi_+|\psi\rangle\), then measure logical
\(\overline Z^B_0\) and keep its +1 result. The resulting logical state
in C is

\[
|M0\rangle_C=\frac{2|0\rangle+|1\rangle}{\sqrt5}\otimes|0\rangle.
\tag{1}
\]

**Fault model.** Preparations, one-qubit gates, CNOT/CZ gates, three-qubit
Fredkins, measurements, and single-qubit idle slots are locations.
A faulty location is an arbitrary operation on its listed qubits, possibly
coupled to an environment. A faulty measurement can also give an incorrect
reported bit. At most two locations are faulty in a complete attempt.
All other locations are ideal. Coherent faults and a shared environment
between the faulty locations are allowed.

Classical parity calculations, lookup tables, and the controller are
reliable. Measurement bits supplied to them need not be correct. An arbitrary
failure of the whole classical decoder is not declared a single physical
measurement fault; allowing that would permit a trivial wrong logical
acceptance with one fault.

Every live qubit has an idle location in a slot when it is unused. The
schedule is serial, and fresh measurement ancillas are prepared within the
measurement using them. No cat state is prepared before, or reused across,
a pass or sweep boundary. Thus a fault can spoil at most one of three
disjoint complete passes or sweeps. Boundary idle slots belong to the
following interval.

The proof also covers replacing a primitive gate by a consecutive circuit
acting on the same listed qubits. Its faulty implementation differs from
the ideal gate by an arbitrary operation on those qubits, exactly as allowed
above. A Fredkin decomposition confined to its control and two targets
therefore needs no new composition argument. Routing through other data
qubits, reused extra helpers, leakage, and faults at more than two locations
are different models.

**Output criterion.** For every accepted classical record of nonzero
probability, ideal mathematical decoding of C, followed by discarding its
syndrome subsystem, returns \(|M0\rangle\langle M0|\). This decoder defines
logical correctness; it is not an additional noiseless physical recovery
assumed after the circuit. Physical recovery is implemented and analyzed
in Section 9.

## 2. The complete schedule

### 2.1 Fixed code and graph data

Write \(S^P_{D,s}=\prod_{q\in R_s}P_{D_q}\), for D=B,C and P=X,Z.
The supports are

| s | \(R_s\) |
|---|---|
| 0 | 0, 1, 2, 3 |
| 1 | 4, 5, 6, 7 |
| 2 | 8, 9, 10, 11 |
| 3 | 12, 13, 14, 15 |
| 4 | 16, 17, 18, 19 |
| 5 | 0, 3, 6, 7, 10, 11, 12, 15 |
| 6 | 4, 7, 8, 9, 14, 15, 16, 19 |
| 7 | 1, 2, 8, 11, 12, 13, 18, 19 |
| 8 | 2, 3, 5, 6, 13, 14, 16, 17 |
| 9 | 0, 1, 4, 5, 9, 10, 17, 18 |

Indices 0 through 8 give nine independent checks of each Pauli type.
Let \(J_a=R_0,\ldots,J_e=R_4\). Vertex v controls exactly the data pairs
in \(J_v\). Set \(T_v=\prod_{q\in J_v}\mathrm{SWAP}(B_q,C_q)\).

The graph has these parallel edges:

| Endpoints | Labels | Endpoints | Labels |
|---|---|---|---|
| ab | 7, 15 | bc | 8, 19 |
| ac | 11, 12 | bd | 14, 16 |
| ad | 3, 6 | be | 4, 9 |
| ae | 0, 10 | cd | 2, 13 |
| ce | 1, 18 | de | 5, 17 |

Use tree edges \(e_b=7,e_c=11,e_d=3,e_e=0\), rooted at a.
The gauge checks, in order, are the ten parallel-edge Z parities, the six
triangle Z parities

\[
(7,8,11),\ (7,14,3),\ (7,4,0),\ (11,2,3),\ (11,1,0),\ (3,5,0),
\]

and the four X stars at b,c,d,e. Every one is required to give +1.

### 2.2 One measurement gadget, used everywhere

To measure \(V=\prod_{j=1}^n V_j\), where the involutions \(V_j\) act on
disjoint target ports:

1. Initialize fresh cat qubits in \(|0^n\rangle\), apply H to the first,
   then CNOT \(c_j\to c_{j+1}\) in increasing j.
2. Verify every adjacent \(Z_{c_j}Z_{c_{j+1}}\) parity in increasing j.
   Use a fresh w in \(|0\rangle\), CNOT \(c_j\to w\), CNOT
   \(c_{j+1}\to w\), then measure w in Z. Perform three complete scans.
   Any reported −1 rejects the whole factory attempt.
3. Apply controlled-\(V_j\) from leaf \(c_j\), once per leaf, in increasing
   target order. Then measure every leaf in X. Their reported parity is the
   reported V result.

For a Pauli check a port is one target qubit and \(V_j=X\) or Z.
For U a port is the pair \((B_q,C_q)\), and \(V_j=\mathrm{SWAP}_q\).
All measurements below use this gadget. Arbitrary reported signs are retained
in recovery rounds; the other stages demand the specified signs.

### 2.3 Preparation, gauging, verification, recovery, readout

| Stage | Operations and acceptance rule |
|---|---|
| Known inputs | Start B and C in \(|0^{20}\rangle\). For each block, verify its eighteen independent code generators and its two known logical stabilizers, in three complete passes, demanding +1 throughout. B uses \(\overline Z_0,\overline Z_1\); C uses \(\overline X_0,\overline Z_1\). |
| Cluster resource | Initialize vertices in + and gauge qubits in 0. For q=0 through 19, apply CNOT from each endpoint to \(A_q\), alphabetically ordered. Verify the five \(K_v=X_vX^A_{\mathrm{star}(v)}\), then twenty \(K_q=Z_uZ_{A_q}Z_v\), in three complete passes, demanding +1. |
| Enrichment | Apply \(\operatorname{CSWAP}(\phi(q);B_q,C_q)\) for q=0 through 19, with \(\phi(q)=v\) for \(q\in J_v\). Measure vertices in X in order a through e. Require reported \(r=\prod_vx_v=+1\). |
| Coherent ungauging | For v=b,c,d,e, apply \(\operatorname{CSWAP}(A_{e_v};B_q,C_q)\) for increasing \(q\in J_v\). Then apply \(C_x=\prod_{v=b}^e Z_{A_{e_v}}^{(1-x_v)/2}\). |
| Three verification sweeps | In each sweep: gauge checks; full B/C code scan; fresh-cat U test; full B/C code scan. Require +1 for every result. A full code scan measures B then C, X then Z, s=0 through 9. |
| Physical recovery | Discard the gauge register. Use the joint B/C repeated-syndrome recovery in Section 9. It has at most nine rounds. |
| Logical readout | Measure all twenty B qubits individually in Z, decode the whole record as in Section 10, and retain only decoded \(\overline Z^B_0=+1\). Hand out C. |

For each input pass, order its X code generators, Z code generators, then
the two logical stabilizers. Within any check, order target qubits by label.
Use single-qubit Pauli gates for the recovery correction, in increasing
physical label. These conventions remove any scheduling ambiguity.

Starting known inputs from zero and demanding all positive stabilizer signs
is deliberately simple and may require many offline attempts. No efficiency
claim depends on it. The theorem concerns each complete attempt, starting
with fresh qubits; discarded attempts do not interact with a later one.

## 3. The code fact needed by the proof

Let \(\mathcal S\) be the original B/C Pauli stabilizer group, and let
\(\mathcal P\) project onto its common +1 eigenspace.

For a set W of vertices, let \(\mathcal A_W\) be all operators supported on
the physical qubits \(B_q,C_q\) with \(q\in\bigcup_{v\in W}J_v\).
We need

\[
|W|\le2\quad\Longrightarrow\quad
\mathcal P E\mathcal P=c_E\mathcal P\quad(E\in\mathcal A_W).
\tag{2}
\]

Here is a short algebraic certificate, rather than an appeal to an exhaustive
fault search. For one code block, consider a pure-X Pauli commuting with all
Z checks and supported on one or two inner blocks. Its four-bit support on
each inner block must have even parity. Modulo the local XXXX stabilizer,
every such support is a combination of

\[
A_i=\{4i,4i+3\},\qquad B_i=\{4i+2,4i+3\}.
\]

Record its four commutation bits with the upper Z checks s=5,6,7,8.
The three nonzero possibilities on each inner block are:

| Inner block | syndrome of \(A_i\) | syndrome of \(B_i\) | syndrome of \(A_i+B_i\) |
|---|---|---|---|
| a | 0001 | 1010 | 1011 |
| b | 1000 | 0101 | 1101 |
| c | 1100 | 0010 | 1110 |
| d | 0110 | 1001 | 1111 |
| e | 0011 | 0100 | 0111 |

These are all fifteen nonzero four-bit vectors, each appearing exactly once.
Thus a nonzero syndrome from one inner block cannot cancel one from a
different inner block. An undetectable X Pauli on at most two inner blocks
must be a product of their XXXX stabilizers. Self-duality gives the same
statement for pure Z. For a general Pauli, its X and Z components satisfy
these conditions separately, so it too is a stabilizer if undetectable.

Expand any E in Pauli operators. Detectable terms are killed by
\(\mathcal P\); surviving terms are stabilizers. This proves (2), first
on each block and then on their tensor product, including entangling E.
This also proves the distance bound used below. A nonidentity Pauli on
one inner block that commutes with both XXXX and ZZZZ has weight at least
two. An undetectable Pauli of total weight at most five therefore occupies
at most two inner blocks, and the preceding argument makes it a stabilizer.
Table I supplies nontrivial weight-six logical operators, so the distance
is exactly six. In particular, a normalizer Pauli of weight at most four
must be a stabilizer.

## 4. Faulty cats and faulty measurement reports: the exact lemma

**Lemma 1.** An accepted measurement gadget with f faults, \(f\le2\), has,
for every reported result and environment branch, a Kraus operator of the
form

\[
K=\sum_\nu E_\nu\bigl(a_\nu I+b_\nu V\bigr).
\tag{3}
\]

Each \(E_\nu\) acts on at most f charged units: a target port for an
interaction fault, or a single idling qubit for a fault outside those ports.
Coefficients may be operators on an environment. A fault-free gadget with
reported y instead implements
the ideal projector \((I+yV)/2\), up to an irrelevant normalization factor.

**Proof of cat preparation.** One of the three adjacent-parity scans is
fault-free. Its accepted +1 outcomes project onto
\(\operatorname{span}\{|0^n\rangle,|1^n\rangle\}\). The cat phase and
relative amplitudes can remain arbitrary:

\[
|0^n\rangle|a\rangle_E+|1^n\rangle|b\rangle_E.
\]

After this clean scan there are no leaf-to-leaf gates. In a parity circuit
both leaves are CNOT controls, and w is always the target. An X on w cannot
spread to another leaf. A faulty CNOT can insert an X component on its one
leaf; a subsequent w-Z can spread a phase to the other leaf, but cannot
insert a bit flip there. Leaf idle faults also affect just one leaf.
Wrong parity reports do not invalidate the existence of the clean scan.

Expanding arbitrary local operations in Paulis, every accepted term at cat
use is therefore supported on at most f erroneous leaf bits, relative to
the two uniform branches. All Z components, arbitrary logical cat phase,
and environmental correlations are retained in the branch coefficients.
This argument does not assume a classical mixture of Pauli errors.

**Proof of use.** For an erroneous leaf-bit set J, the two uniform branches
apply \(V_J=\prod_{j\in J}V_j\) and \(V_JV\). Measuring the leaves, even
with a wrong reported sign or arbitrary faulty local measurement, produces
an I/V combination times an operator on the J ports.

A fault in a target interaction touches only that leaf's port. That leaf
has no later target interaction. A target idle error, propagated through its
own controlled gate, also stays on that port, although it may change the
branch coefficients. Charge such a port to that fault. A fault affecting
only a leaf measurement or a report can cost a fault without adding any
target port. Summing the local Pauli expansions proves (3), with no more
ports than faulty locations. All other data idle faults during the gadget
are charged as their own target errors. \(\square\)

This is why phase faults are not silently treated as trustworthy syndrome
measurements. For example, a faulty U gadget can implement \(aI+bU\)
instead of either ideal projector. The proof will permit arbitrary a and b.

## 5. Offline verification really supplies local residual errors

**Lemma 2.** A known stabilizer-state source verified in three full positive
passes is either rejected or leaves the correct source state with errors
on at most f source qubits, where f counts faults after one clean pass.
Subsequent storage faults add one source qubit each.

At least one pass is fault-free, including its cat preparations and data
idle slots. Its accepted results project onto a one-dimensional space, so
the source becomes exactly its intended pure state, factorized from the
environment. Its earlier preparation faults need no spread bound.

For later measurements, Lemma 1 with V a source stabilizer gives local
errors times products of source stabilizers. Pauli stabilizers normalize
the space of errors on a given set of qubits, and act as identity on the
intended source. Thus each later fault adds at most one source qubit to the
residual error support. This proves the statement for the twenty-five-qubit
cluster and both rank-twenty known input states. \(\square\)

Sources verified earlier can wait while another source is prepared. Their
idle faults are included in this bound and charged to their own source.
A fault does not get counted once for an ancilla and again for the target
error it later causes: that is one fault with one propagated support charge.

## 6. The invariant before the clean sweep

### 6.1 After enrichment and F

For any fixed set of at most two faults up to the end of F, the output can
be expanded as

\[
\sum_\nu C_\nu\otimes E_\nu U^{b_\nu}|\psi\rangle,
\qquad E_\nu\in\mathcal A_W,\quad |W|\le f_{\rm early},
\quad b_\nu\in\{0,1\}.
\tag{4}
\]

The C coefficients act only on gauge qubits, measured-register records,
and environment. The set W can be chosen for each expansion term; its size
bound is uniform. This includes incorrect vertex records and the resulting
wrong \(C_x\), since \(C_x\) acts on gauge qubits alone.

**Proof.** By Lemma 2, begin with the exact cluster and intended encoded
inputs, together with a residual source error on at most one source qubit
per surviving preparation/storage fault. Expand these residual errors in
local Paulis. Initially the cluster is

\[
2^{-5/2}\sum_{t\in\mathbb F_2^5}|t\rangle_V|\delta t\rangle_A,
\quad (\delta t)_q=t_u+t_v\text{ on edge }q:u\! -\! v,
\]

where sums of bits are modulo two.

Assign an affected data group to each relevant fault:

| Fault touching | Possible affected data group |
|---|---|
| Input data qubit q | its group \(J_{\phi(q)}\) |
| Vertex v, including a faulty enrichment Fredkin | \(J_v\) |
| Tree gauge qubit \(A_{e_v}\), including a faulty F Fredkin | \(J_v\) |
| Nontree gauge qubit; vertex readout; gauge-only correction | none, unless already charged by another row |

A vertex readout fault is after its final target interaction. Hence it
changes coefficients, not the support bound. A vertex bit fault earlier can
change all remaining SWAPs of that vertex, but all belong to its one group.
The same statement holds for a tree-control bit fault during F.

Now resolve the circuit in computational-basis control trajectories.
Outside the charged groups, enrichment applies \(T_v^{t_v}\), and F applies
\(T_v^{t_a+t_v}\) for v other than a. The combined action on every
uncharged group is \(T_v^{t_a}\), including the root group if uncharged.
All departures from this action are confined to the charged groups.
Consequently each trajectory acts on data as \(E_WU^{t_a}\).

No data gate couples different physical labels, except through a control
that is reused solely within its assigned group. Local target errors may
alter control phases, but their matrix elements still enter coefficients
of these same trajectories. Summing trajectories and taking arbitrary
measurement matrix elements proves (4), for arbitrary quantum faults.
Flatness of a faulty gauge field is not assumed in this argument. \(\square\)

### 6.2 A space closed under all preceding faulty sweeps

Define

\[
\mathfrak M_W=\operatorname{span}\{E S U^b:
E\in\mathcal A_W,\ S\in\mathcal S,\ b=0,1\},
\tag{5}
\]

allowing arbitrary gauge/environment coefficients on these data operators.
Two elementary facts give

\[
\mathfrak M_W\mathfrak M_{W'}\subseteq\mathfrak M_{W\cup W'}.
\tag{6}
\]

First, a Pauli stabilizer conjugates a local operator to another operator
on the same support. Second, U exchanges B and C, so it normalizes both
\(\mathcal S\) and each \(\mathcal A_W\). To multiply two terms, move the
first \(SU^b\) past the second local error by conjugation. Local supports
combine by union, and the remaining stabilizer/U factors stay in the same
form. This proves (6).

Fault-free code measurements have Kraus operators \((I\pm S)/2\), and
fault-free U measurements have \((I\pm U)/2\); all belong to
\(\mathfrak M_\varnothing\). By Lemma 1 a faulty code or U gadget adds at
most one inner group per fault. Gauge-check gadgets act only on coefficients;
their data idle faults add local groups in the same way.

Equation (4), followed by (6), therefore proves: **at every point before the
first clean verification sweep, the data operation belongs to a sum of
\(\mathfrak M_W\) terms with \(|W|\le f_{\rm before}\le2\)**.
This includes arbitrary ancillary phases, misleading reports, false accepted
syndromes, and partially completed earlier code scans. No earlier recorded
code syndrome is assumed correct.

### 6.3 Reduction to the requested logical component

From (2), for \(|W|\le2\),

\[
\mathcal P\mathfrak M_W\mathcal P
\subseteq\operatorname{span}\{\mathcal P,U\mathcal P\}.
\tag{7}
\]

Indeed, \(SU^b\) preserves the code, S acts as identity there, and
\(\mathcal P E\mathcal P=c_E\mathcal P\).

Thus the input to the clean sweep, **after projection onto its accepted
code component**, has exactly the form

\[
|a\rangle_{AE}|\psi\rangle+|b\rangle_{AE}U|\psi\rangle.
\tag{8}
\]

If auxiliary degrees of freedom are resolved, this is
\((\alpha I+\beta U)|\psi\rangle\). Without resolving them, the vector
coefficients in (8) are the precise statement. The raw state at the entrance
can also have nonzero-syndrome components; claiming it already equals (8)
without the code projector would be incorrect.

## 7. One complete clean sweep fixes the logical state

Each of the three sweeps includes every idle location during its fresh-cat
preparations, its gauge checks, code scans, and U test. With at most two
faults, at least one whole sweep is fault-free. Choose any such sweep.

Its gauge checks act only on the auxiliary coefficients. Its first clean
code scan, if accepted, applies \(\mathcal P\) and produces (8).
Its clean positive U test then gives

\[
\begin{aligned}
(I_{AE}\otimes\Pi_+)
\bigl(|a\rangle|\psi\rangle+|b\rangle U|\psi\rangle\bigr)
&=(|a\rangle+|b\rangle)\otimes\Pi_+|\psi\rangle.
\end{aligned}
\tag{9}
\]

If this vanishes the branch is rejected. Otherwise the data are exactly
the intended normalized \(|M_2\rangle\), independent of the environment.
The final clean code scan leaves that state unchanged. Explicitly,

\[
|M_2\rangle=\frac{2|00\rangle_L+|01\rangle_L+|10\rangle_L}{\sqrt6},
\quad U|M_2\rangle=|M_2\rangle,
\]

with both spectator logical qubits zero.

This proves the early-fault claim for every placement of up to two faults,
not just Pauli controller faults. A cat phase error may corrupt the earlier
I/U coefficients; it cannot escape the invariant. A wrong vertex record
can select the wrong actual sector; the clean positive test rejects it or
restores the desired projection if an earlier fault removed that projection.

## 8. Faults after the clean sweep have ordinary correctable support

Use physical label sets Q instead of inner-block sets W. Let
\(\mathcal A_Q\) act only on pairs \((B_q,C_q)\), \(q\in Q\), and define
\(\mathfrak N_Q=\operatorname{span}\{E S U^b:E\in\mathcal A_Q\}\).
Exactly the argument for (6) gives

\[
\mathfrak N_Q\mathfrak N_{Q'}\subseteq\mathfrak N_{Q\cup Q'}.
\tag{10}
\]

There are no more enrichment or F gates. Lemma 1 says each fault in a later
verification gadget or idle adds at most one physical label q. In a U test
it can affect both \(B_q\) and \(C_q\), which is still only one qubit per
code block. Since stabilizers and U act as identity on \(|M_2\rangle\),
after f such faults the data lie in

\[
\operatorname{span}\{E|M_2\rangle:
E\text{ acts on at most f physical qubits in each block}\}.
\tag{11}
\]

Ancilla phase faults merely allow arbitrary I/U combinations in this space;
they do not require a trusted result. Tracing out the gauge register preserves
the same error-space bound. Because f is at most two, this is an ordinary
correctable error space for the two distance-six codes.

This support statement is stronger than saying that each Pauli term would
be correctable separately. For any two such Pauli terms \(E,F\), each block
of \(E^\dagger F\) has weight at most four. Its code projection is zero or
a stabilizer scalar. Thus the entire coherent error space satisfies the
quantum error-correction conditions.

## 9. Physical recovery, with its faults included

We now specify the recovery previously left as an interface.

**One recovery round:** measure the eighteen independent generators
\(S^{X/Z}_{B,s}\), s=0 through 8, then the eighteen for C, using fresh
verified cats. Keep all signs as a joint thirty-six-bit syndrome record.
Do not apply a data correction between rounds.

**Stopping rule:** stop at the first three consecutive identical joint
syndrome records. Allow at most nine rounds. If no such triple occurs,
reject. A failed cat verification also rejects the whole attempt.

For the syndrome s in that triple, choose on each block a Pauli R(s) of
weight at most two having that syndrome, with a fixed lexicographic tie
rule. Reject if none exists. Apply these Pauli corrections locally.
This is a finite lookup table, not an assumed fault-free quantum recovery.

### 9.1 The procedure terminates within nine rounds

A bad round contains at least one fault, including faults during ancilla
preparation and data idles. There are at most two bad rounds.
Between bad rounds, successive clean rounds return the same true syndrome:
the first projects onto a syndrome subspace and later clean rounds preserve
it. If no run of three clean rounds existed, at most three clean runs of
length two could occur. Including two bad rounds would give at most eight
rounds. Nine rounds therefore contain a clean triple and force termination
earlier or at that triple.

The stopping triple itself need not be all clean. It does contain at least
one clean full round, so its common recorded syndrome s was the true joint
syndrome at the end of that round. Choose that round as the reference round.

### 9.2 Its correction is logically right even when some records are wrong

Let r bound incoming error weight per block, and let g be the number of
faults during recovery. From the single global budget,

\[
r+g\le2.
\tag{12}
\]

Before the correction, all target interactions are controlled Paulis.
Lemma 1 with V a stabilizer, and closure under Pauli stabilizers, show that
the state throughout these rounds is a sum of Pauli errors of weight at
most r plus the number of faults so far, acting on \(|M_2\rangle\).
This remains true for faulty syndrome projectors and arbitrary cat phases.

The clean reference round selects one exact syndrome s. Every surviving
Pauli E has weight at most two per block. Two such errors with the same
syndrome differ by a stabilizer: \(E^\dagger F\) is a normalizer element of
weight at most four, below distance six. Hence at that instant the data and
environment factorize as

\[
|\gamma\rangle_E\otimes E_s|M_2\rangle
\tag{13}
\]

for some representative \(E_s\) of weight at most two per block.
The table correction exists, and \(R(s)E_s\) is a stabilizer, up to phase.

Let h be the number of faults after the reference round through the end of
the physical correction. Subsequent faulty Pauli measurements introduce only
local errors and stabilizer factors. Move stabilizer factors to the right;
they act as scalars on the known syndrome representative and merely modify
environment coefficients. Immediately before correction, terms therefore
have the form \(D E_s|M_2\rangle\), with D supported on at most the faults
after that round. Applying R gives

\[
R D E_s|M_2\rangle
=(RDR^\dagger)(R E_s)|M_2\rangle
\propto (RDR^\dagger)|M_2\rangle.
\tag{14}
\]

Conjugating by a Pauli does not enlarge support. Faults in the local
correction gates add one qubit each. The actual output of recovery is thus
\(|M_2\rangle\) with an error in the span of weight-at-most-h Paulis per
block. All incoming errors and recovery faults before the reference round
have been removed logically; later faults leave bounded residual errors.

No majority vote on potentially stale syndromes was assumed. The common
record is anchored to an actual clean round, and the remaining faults are
explicitly charged to the residual output. This proves recovery correctness
including wrong reports and arbitrary phase faults.

## 10. Destructive logical readout in the same budget

After the physical recovery, measure each B qubit individually in Z, in
increasing q. Let m be the reported twenty-bit word. C only idles during
these measurements, and its idle faults are included.

Let H have rows \(R_0,\ldots,R_8\), regarded as binary support vectors.
An ideal physical-Z word w satisfies \(Hw=0\). Decode m by finding a
binary error vector e of weight at most two with \(He=Hm\), and set
\(w'=m+e\). Reject if no candidate exists. The decoded logical result is

\[
\overline z^B_0=(-1)^{\ell\cdot w'},
\qquad \ell=\{0,3,6,7,18,19\}.
\tag{15}
\]

Here a dot means the parity of the bits on that support. Retain only +1.

Let h now count faults after the recovery reference round through recovery
completion, and let b count subsequent faults in B readout or B idles.
Equation (14) and the global budget give \(h+b\le2\).
The X component of the residual B error flips at most h word positions;
each faulty physical readout can alter at most its own reported bit.
Thus an error vector of weight at most two always relates m to the true
ideal word. A general faulty one-qubit measurement has a linear expansion
in such bit-flip alternatives, with phases in the coefficients.

If two candidate corrections e and e' satisfy the parity checks, their
difference d=e+e' has weight at most four and \(Hd=0\). The Pauli X(d)
therefore commutes with every code check. Distance six makes it a stabilizer,
which commutes with \(\overline Z_0\). Hence

\[
\ell\cdot e=\ell\cdot e'.
\tag{16}
\]

The decoded logical result is unambiguous even when the physical word is
ambiguous. Phase errors on measured B affect branch amplitudes, not this
decoded logical value. The same reasoning identifies its spectator logical
Z, whose intended value is +1.

This argument also handles coherent B/C errors. For a fixed reported word,
all allowed local-error terms have the same decoded logical B value by
(16). Conditioning on decoded +1 therefore cannot mix the two logical
measurement branches. The ideal logical action is exactly
\(\langle0|_{B,0}|M_2\rangle\), with the spectator fixed at zero; it leaves
the C state in (1). Refining B's physical word and its syndrome only changes
auxiliary coefficients. Any accompanying C error remains in its correctable
error space.

Finally, B readout gates never touch C. If c further faults occur on C idle
locations after the reference round, they add at most c erroneous C qubits.
Combining these with the residual recovery faults gives a C error of weight
at most the number of faults after that reference round, which is at most
two. The accepted output satisfies the criterion in Section 1.

## 11. Putting the budget together

Choose a clean gauging-verification sweep as in Section 7. Partition all
faults into

\[
f_{\rm pre}+f_{\rm ver}+f_{\rm rec}+f_{\rm out}\le2,
\tag{17}
\]

where the terms count faults before that sweep, in later verification,
in physical recovery, and in final readout/output storage. The chosen sweep
contains none.

| Budget portion | What its faults can do on an accepted path |
|---|---|
| \(f_{\rm pre}\) | Enter the operator invariant with at most that many inner groups. The clean code projector gives (8), and the clean U test gives exactly \(|M_2\rangle\). |
| \(f_{\rm ver}\) | Leave at most that many faulty physical pairs, including coherent I/U alternatives. This supplies recovery input bound \(r\le f_{\rm ver}\). |
| \(f_{\rm rec}\) | Supply a genuine syndrome in a clean member of the stopping triple; (12) holds because \(f_{\rm ver}+f_{\rm rec}\le2\). Faults after that reference round remain local residual errors. |
| \(f_{\rm out}\) | Cause locally corrupted B measurement bits or local C storage errors. Together with residual recovery errors they total at most two, so decoded B acceptance and decoded C magic are correct. |

The proof never introduces a fresh two-fault allowance for a later stage.
For example, if two faults occurred before the clean sweep, recovery and
readout have no faults left in this analysis. If neither occurred before
it, both may occur during recovery or readout, and Sections 9–10 apply.
All mixed allocations are covered by (17).

For an arbitrary fixed fault set, expand its local operations in operator
bases and keep the environment coefficients. All terms obey the support
and closure lemmas. The clean projections and error-correction conditions
map every accepted term to the same logical target. Linearity then proves
the result for coherent combinations and general local fault channels,
without interpreting the expansion as randomly sampled Pauli errors.

**Theorem.** The complete schedule in Section 2, including its physical
recovery and destructive logical readout, is two-fault tolerant under the
location model of Section 1: every accepted nonzero-probability branch with
at most two faults has decoded C state \(|M0\rangle\langle M0|\).

## 12. What is now proved, and what is outside the theorem?

The early logical-component claim follows from a closed operator invariant,
not from assuming that faulty measurements were ideal projectors. The late
claim follows from its physical-pair version and the correctability of the
whole coherent error space. Physical recovery and final logical readout are
explicit parts of the same budget. The distinction between raw pre-sweep
state and accepted code component is essential.

The theorem concerns this fully specified, deliberately conservative
schedule. It does not prove a threshold, a favorable acceptance rate, or an
overhead advantage. Storage faults are counted, but their probability over
the long serial schedule may be substantial. An implementation that changes
target connectivity, reuses helpers, or admits leakage must check that it
still satisfies the stated location model. Those are implementation and
noise-model changes, rather than an unproved measurement-module contract
inside this theorem.

The cat and repeated-syndrome ideas are standard tools; see
[Gottesman's textbook, Chapters 12–13](https://www.cs.umd.edu/~dgottesm/QECCbook-2024.pdf).
The operator-space composition, the block-specific syndrome certificate,
and the complete budget argument above are supplied explicitly here.

A short [certificate script](check-c4-helix-two-fault-composition.py) checks
the code-specific table, the destructive-readout ambiguity condition, and
the nine-round combinatorial bound. Its
[JSON output](../output/c4-helix-two-fault-composition-certificates.json)
is a reproducibility aid; the proof does not rely on enumerating complete
circuit fault pairs.
