# Fault tolerance of the full C4-Helix gauging procedure

## Introduction

This note develops the fault-tolerance proof for the procedure specified
in [full_procedure.md](full_procedure.md) and drawn in
[full_circuit.md](full_circuit.md). It concerns one gauging/ungauging
cycle, with three rounds of verification while gauged, followed by
original-code verification, recovery, and logical readout.

Each data block B and C is a \([[20,2,6]]\) C4-Helix code. The ideal
procedure prepares the encoded inputs
\(|\overline{00}\rangle_B|\overline{+0}\rangle_C\), selects the
positive outcome of the whole-block SWAP, and then selects logical
\(B_0=0\). Its retained output is

\[
|\overline{M0}\rangle_C,
\qquad
|M\rangle=\frac{2|0\rangle+|1\rangle}{\sqrt5}.
\]

An overbar denotes an encoded state. The second logical qubit of C is
a spectator in zero.

### Statement to be proved

**Every accepted attempt containing at most two faulty circuit locations
has the intended decoded logical output \(|M\rangle\otimes|0\rangle\)
in C.** Physical errors may remain, provided they belong to a correctable
error space and do not change this logical output.

A *location* is one preparation, gate, physical measurement, or
single-qubit waiting interval in the scheduled circuit. A faulty location
may undergo an arbitrary error on its participating qubits; a measurement
report may also be wrong. Classical processing is assumed reliable.
The two-fault allowance applies to the **entire attempt**, including
input preparation, measurement helpers, gauge readout, recovery, and
final logical readout. No stage receives a new allowance of two faults.

The procedure is postselected: some reported outcomes cause rejection.
The claim concerns attempts that pass all acceptance tests. Correctness
of the decoded output does not assume an additional fault-free physical
recovery after the procedure ends.

### Structure of the proof

The argument has four parts.

1. **Bound how faults spread.** Establish the error bound supplied by
   verified source preparation, verified measurement cats, and the
   assignment of each enrichment controller to one inner four-qubit
   group. The local data errors caused by two faults remain confined to
   at most two matched pairs of inner C4 blocks, with the same two labels
   across B and C. This permits up to four actual inner C4 blocks and
   more than two erroneous physical qubits, so distance-six recovery alone is not
   yet sufficient. Errors in the gauge register and possible changes of
   the SWAP outcome must be tracked separately; they are not excluded
   by this spatial bound.

2. **Protect the intended SWAP projection.** Among the three complete
   gauged verification rounds, at least one contains no faulty location.
   Prove that its paired, cycle, and Gauss checks enforce the positive
   logical SWAP projection, even on an input corrupted by earlier faults
   or wrong reports. Some errors within the affected inner groups may
   remain. The other rounds must preserve the resulting error bound
   under the same total fault budget.

3. **Remove the larger errors after ungauging.** First prove that decoding
   the full gauge readout gives the required partial-SWAP correction.
   Then use a clean round among the three original-code verification
   rounds. The essential code property is that an operator confined to
   at most two inner groups cannot induce a nontrivial logical action
   while passing the original stabilizers. Consequently a clean positive
   projection rejects the detectable error components and retains the
   intended logical state. This filtering step avoids having to correct
   an arbitrary unknown error on two whole groups.

4. **Protect the remainder of the circuit.** After the last clean
   original-code filtering round, each further fault can affect at most
   one physical data qubit. Prove that repeated syndrome recovery and
   decoded B readout handle these remaining errors, including faults in
   the recovery and readout themselves. Distance six supplies the
   required correction of up to two physical-qubit errors. The accepted
   final readout then leaves the intended logical magic state in C.

A *clean round* means that its entire circuit interval is fault-free,
including helper preparation and waiting locations. It need not receive
an error-free input. The decoder never needs to identify which round
was clean: acceptance requires all the prescribed positive reports,
and the proof uses the existence of a clean round among them.

Repetition therefore supplies a fault-free verification interval, but
does not by itself prove fault tolerance. The substantive task is to
show what each such interval does to the errors it receives, and how
the remaining errors stay within the bound required by the next part
of the argument.

## 1. Bound how faults spread

### 1.1. The two-group lemma

Each *inner group* is one original \([[4,2,2]]\) C4 block, containing
four physical qubits. There are five such groups inside each
twenty-qubit C4-Helix block: a contains qubits 0–3, b contains 4–7,
c contains 8–11, d contains 12–15, and e contains 16–19.

The first ingredient is a property of the code itself. It explains why
confining errors to two inner groups will be sufficient for the later
filtering argument; the circuit error-spreading bound is a separate step.

**Lemma (two-group detectability).** Consider one C4-Helix data block,
initially in a valid encoded state. A Pauli error supported on at most
two inner groups either anticommutes with a stabilizer check, and is
therefore detected, or acts on every encoded state as the identity up
to a global phase. In particular, it cannot pass every original-code
check while changing the encoded information.

More generally, for an arbitrary error operator supported on those two
groups, the component retained by projecting onto all positive
original-code check outcomes is a scalar times the original encoded
state. After normalization, an accepted state is unchanged.

The proof below derives this statement from the published code
properties; it is not quoted as a named lemma from the literature.
The ingredients are given in Section 2.1, Corollary 2.4, and Table 1 of
[Berthusen and Durso-Sabina, *Simple logical quantum computation with
concatenated symplectic double codes*](https://quantum-journal.org/papers/q-2026-08-19-2195/pdf/).
The physical stabilizers for the present implementation are listed in
[Appendix A of the experimental manuscript](../arXiv-2609.03194v1/appendix.tex).

**Proof.** First consider Pauli errors: products of \(I,X,Y,Z\).
The extension to arbitrary errors is given at the end.

The three code properties needed are:

1. Every inner group has the checks \(XXXX\) and \(ZZZZ\).
2. The full code has generators consisting entirely of X operators or
   entirely of Z operators. This is what *CSS* means here.
3. The distance is six. By definition, a Pauli operator that passes
   every check but changes the encoded information must act on at
   least six physical qubits.

A valid encoded state \(|\psi\rangle\) satisfies
\(S|\psi\rangle=|\psi\rangle\) for every stabilizer \(S\).
Consequently, multiplying an error by a stabilizer does not change its
action on encoded states:

\[
(ES)|\psi\rangle=E|\psi\rangle.
\]

This is a mathematical replacement of the error, not a correction gate
that needs to be executed.

**1. Start with an error made only of X operators.**

Assume that it passes every check and occupies at most two inner groups.

Within either group, consider its \(ZZZZ\) check. Every X contributes
one anticommutation with Z. Thus passing that check requires an **even
number of X operators** in that group.

There are only three possibilities:

| Number of X operators in the group | Replacement |
|---|---|
| 0 | Leave it unchanged |
| 2 | Leave it unchanged |
| 4 | Multiply by that group's \(XXXX\) stabilizer, removing all four |

The last replacement uses simply

\[
(XXXX)(XXXX)=IIII.
\]

After doing this in both affected groups, the resulting error \(E'\)
has **at most two X operators per group**, hence

\[
\operatorname{weight}(E')\le 2+2=4.
\]

Here the weight is the number of physical qubits on which the operator
is not the identity. Moreover:

- \(E'\) acts exactly like the original error on encoded states.
- \(E'\) still passes every check, because it differs from the original
  error only by stabilizers, which commute with every check.

But a nontrivial logical operator needs weight at least six. Therefore
**this undetected error of weight at most four cannot change the encoded
information**. Neither can the original error.

This proves the claim for X-only errors. If an X-only error fails a
check instead, it is detected: anticommutation changes that check's
eigenvalue from +1 to −1.

**2. The same argument works for Z-only errors.**

Exchange X and Z throughout:

- Passing each inner \(XXXX\) check requires an even number of Z
  operators.
- Multiply by the inner \(ZZZZ\) stabilizer whenever all four
  positions carry Z.
- The equivalent error has weight at most four.
- Distance six excludes a nontrivial logical action.

**3. Now allow any mixture of X, Y, and Z.**

Using \(Y=iXZ\), write any Pauli error as

\[
E=\omega E_XE_Z,
\]

where \(E_X\) contains only X operators, \(E_Z\) contains only Z
operators, and \(\omega\) is an overall phase. Both parts remain
supported within the same two inner groups.

The important point is that **if \(E\) passes every check, each part
passes every check separately**:

- For a Z-type check, \(E_Z\) commutes automatically, so the
  commutation sign comes entirely from \(E_X\).
- For an X-type check, the sign comes entirely from \(E_Z\).
- Each part automatically commutes with checks of its own type.

Parts 1 and 2 therefore apply separately to \(E_X\) and \(E_Z\).
Each acts trivially on the encoded information. Their product does too,
up to phase.

**4. Extend the argument to arbitrary quantum errors.**

An arbitrary operator on those two groups can be expanded as a linear
combination of Pauli products supported on the same groups.

When all stabilizers are measured and only positive outcomes are retained:

- Any Pauli term that anticommutes with a check is projected out.
- Every surviving Pauli term acts as a scalar times the identity on
  the encoded state, by the proof above.

Their sum therefore also acts as a scalar times the identity. After
normalization, the accepted encoded state is unchanged; if the scalar
vanishes, that branch is rejected. This proves the lemma.

The crucial observation is that **the inner stabilizers allow the X
and Z parts to be reduced separately to weight at most four**. This
is what makes distance six sufficient, even though the original
two-group error could involve eight physical qubits.

### 1.2. What is counted: inner C4 blocks and matched pairs

In the preceding lemma, an *inner group* means one four-qubit C4 block
inside a single twenty-qubit copy. In the circuit argument, it is useful
to count corresponding blocks in B and C together.

**Definition.** A *matched pair of inner C4 blocks* consists of one inner
block in B and the block with the same label in C. For example, matched
pair a contains the eight physical qubits

\[
B_0,B_1,B_2,B_3,\qquad C_0,C_1,C_2,C_3.
\]

Two affected matched pairs therefore allow up to four actual inner C4
blocks. For example:

| Copy | Affected inner C4 blocks |
|---|---|
| B | a and c |
| C | a and c |

The bound uses the **same two labels across both copies**. Allowing a,b
in B and c,d in C would involve four matched-pair labels and would be a
different, weaker bound.

The aim is to show that **each fault can add local data damage in at
most one new matched pair**, while subsequent operations preserve this
counting. Two faults then account for at most two matched pairs.

This is a bound on local physical damage. Faulty measurements may also
select the wrong logical SWAP projection. That possibility must be
retained explicitly; the second part of the proof will address it.

### 1.3. The measurement gadget: local damage and measurement action

Every check uses a fresh verified cat. Each leaf interacts with exactly
one target port:

- One physical qubit for a Pauli factor.
- One pair \((B_q,C_q)\) for a SWAP factor in a Gauss check.

A faulty leaf-target interaction can therefore damage only that port,
which belongs to at most one matched pair. The remaining issue is that
raw cat preparation can spread a fault over many leaves.

**What cat verification guarantees.** Among three complete adjacent-ZZ
verification scans, at least one is clean under the global two-fault
budget. In an accepted attempt, that clean scan projects the cat into

\[
\operatorname{span}\{|00\cdots0\rangle,\ |11\cdots1\rangle\}.
\]

For a pure state, the result can be

\[
c_0|00\cdots0\rangle+c_1|11\cdots1\rangle.
\]

The tests establish agreement between the computational-basis bits.
They do not establish equal amplitudes or the correct relative phase.
For example, both states

\[
\frac{|00\cdots0\rangle+|11\cdots1\rangle}{\sqrt2},
\qquad
\frac{|00\cdots0\rangle-|11\cdots1\rangle}{\sqrt2}
\]

pass every adjacent-ZZ check. The cat can also be entangled with an
unobserved environment; the same two-dimensional leaf-space constraint
applies.

This guarantee holds **at the end of the clean scan**. Faults afterward
can introduce additional leaf bit errors. No leaf-to-leaf gates remain
after raw preparation, and the parity helper is always a CNOT target.
Its bit errors therefore cannot propagate back into several leaves.
A subsequent faulty verification interaction can flip at most its one
participating leaf. Helper phase errors can spread phases to leaves,
but do not create additional leaf bit flips. The helper is reset before
each adjacent-pair test.

Consequently, each subsequent fault can introduce an incorrect target
operation at only one port. The uniform all-zero/all-one uncertainty is
a separate issue: it can change the measurement action even without
local target damage.

**Deriving the measurement action.** Let \(Q\) denote the observable
being measured. For example, take the actual inner check

\[
Q=X_{B_0}X_{B_1}X_{B_2}X_{B_3}.
\]

Suppose the four-leaf cat is
\(c_0|0000\rangle+c_1|1111\rangle\), and the data initially have
state \(|\phi\rangle\). The controlled gates act as follows:

- In branch 0000, none of the four X gates is applied: the data receive I.
- In branch 1111, all four are applied: the data receive Q.

After coupling, the joint state is

\[
c_0|0000\rangle|\phi\rangle
+c_1|1111\rangle Q|\phi\rangle.
\]

Measure all leaves in X. If the product of the actual measurement signs
is \(r=\pm1\), the unnormalized data state is proportional to

\[
c_0|\phi\rangle+r c_1Q|\phi\rangle
=(c_0I+r c_1Q)|\phi\rangle.
\]

This is the origin of \(aI+bQ\): a and b are coefficients determined
by the cat and the measurement branch. The ideal positive measurement
has a factor proportional to \(I+Q\). A wrong report can label a
different physical branch as positive; it does not make that branch
the intended positive projector.

Now include a coupling fault that damages a target. Let **D denote the
additional local target-error operator**. For example, \(D=Z_{B_2}\)
would give

\[
Z_{B_2}(aI+bQ)|\phi\rangle.
\]

Thus the general form of a term in the conditional gadget operation is

\[
D(aI+bQ).
\]

The two factors have distinct roles:

- D contains physical target damage. Each fault contributes at most one
  target port, or one separately counted idling target, to its support.
- \(aI+bQ\) contains the possibly incorrect measurement action,
  including cat-phase faults and wrong reports.

This expression describes a conditional operation arising from
measurement, which need not be unitary. It is not an extra gate to
execute. General faults require a **sum of such terms**, with different
local operators D; one fixed D need not describe the whole noisy gadget.

### 1.4. Verified preparation supplies the starting error bound

The known B input, C input, and graph resource are each specified by a
complete stabilizer family with a **unique common positive state**.
Each source undergoes three complete positive verification rounds.
At least one round for each source is clean, since there are at most
two faulty locations in the entire attempt.

That clean round projects onto the intended source state, or rejects.
Errors that spread widely during raw preparation cannot survive this
projection as an incorrect source state.

Afterward, verified measurement gadgets leave at most one erroneous
source qubit per later fault. To see why the nonlocal measured checks
do not invalidate this statement, let \(|\sigma\rangle\) be the intended
source, Q one of its Pauli checks, and F an existing local error. Since
\(Q|\sigma\rangle=|\sigma\rangle\),

\[
(aI+bQ)F|\sigma\rangle
=(aF+bQFQ)|\sigma\rangle.
\]

Conjugating F by a Pauli product Q does not enlarge its support. The
remaining factor D from a faulty gadget adds only its locally damaged
targets. Thus later checks preserve the local-error bound rather than
spreading a source error across their full support.

The residual source errors are accounted for as follows:

- A data-qubit error belongs to one inner C4 block and hence one matched pair.
- A graph-vertex error can affect only its assigned matched pair during
  the subsequent enrichment.
- A gauge-qubit bit error changes only that gauge bit.

Waiting errors are included in the same global fault budget. In
particular, graph verification is essential: a raw graph-preparation
fault could otherwise spread into many gauge bits before enrichment.

### 1.5. Enrichment confines propagation to a matched pair

Let \(J_v\) be the four physical labels of inner block v, and define

\[
T_v=\prod_{q\in J_v}\operatorname{SWAP}(B_q,C_q),
\qquad U=T_aT_bT_cT_dT_e.
\]

The operator U is the whole-block SWAP. Vertex a controls only the four
physical SWAPs on pairs

\[
(B_0,C_0),\ (B_1,C_1),\ (B_2,C_2),\ (B_3,C_3).
\]

A fault on a can therefore affect several data pairs, but all belong
to matched pair a. A faulty Fredkin can damage its vertex and data
targets, including subsequent propagation from that vertex, but again
only within that same matched pair. The same argument applies to the
other four vertices.

An existing data error can move between B and C under a SWAP, while its
matched-pair label stays unchanged. Controlled SWAPs may also correlate
the error with the controller branch, but their data targets remain
inside that matched pair.

Thus enrichment can enlarge physical support **within** a matched pair
without introducing a new matched-pair label, except when a new fault
occurs in that label. Vertex phase faults and wrong X reports are
retained in the branch coefficients; they need not cause local data
damage in order to corrupt the logical projection.

### 1.6. Gauged verification preserves the matched-pair counting

For a Pauli check, moving an existing Pauli error through the
measurement can change a check sign without enlarging the error's
support. Faulty gadgets add only their locally damaged ports. This
applies to paired code checks and, after ungauging, to original-code
checks. The paired checks are products of corresponding B/C checks;
their matched factors \(P_{B_q}P_{C_q}\), for \(P=X,Z\), commute with
the physical SWAPs.

Cycle checks involve only gauge Z operators. They can change branch
amplitudes or reject a branch, without moving damage between data
matched pairs.

Gauss checks require an additional distinction between an intended
frame change and a gauge error. Write

\[
G_v=\Big(\prod_{q\in E_v}X_{A_q}\Big)T_v,
\]

where \(E_v\) is the set of incident gauge edges. For a, this set is

\[
E_a=\{0,3,6,7,10,11,12,15\}.
\]

**A Gauss operation changes the gauge word and data frame together.**
Label a frame by five bits t. Its gauge word and data operation are

\[
(\delta t)_q=t_u\oplus t_v
\quad\text{for an edge }q:u\text{--}v,
\qquad
V_t=\prod_vT_v^{t_v}.
\]

After the temporary vertices have been measured, t remains a label for
these components; it is not a surviving vertex register.

For example, on a component with all gauge bits zero, \(G_a\) flips
precisely the eight bits in \(E_a\) and applies \(T_a\) to the data.
The new gauge word is the valid cut corresponding to \(t_a=1\) and
all other t bits zero. It records the same partial SWAP just applied
to the data. These eight flips are **not eight independent errors**.
For a general frame, \(G_v\) toggles \(t_v\), changing the edge word
and the data operation consistently.

**Existing damage can remain, but does not acquire a new matched-pair
label.** As an explicit example, let \(|\Phi\rangle\) be an ideal
gauged state with \(G_a|\Phi\rangle=|\Phi\rangle\), and introduce
\(X_{B_0}\). A SWAP exchanges which copy carries X, so

\[
G_aX_{B_0}=X_{C_0}G_a.
\]

The positive Gauss measurement alone then gives the unnormalized state

\[
\frac{I+G_a}{2}X_{B_0}|\Phi\rangle
=\frac{X_{B_0}+X_{C_0}}{2}|\Phi\rangle.
\]

The error has not disappeared. It has become a superposition of an
error on \(B_0\) and an error on \(C_0\). Both belong to matched
pair a; no damage has appeared in b,c,d,e. This example isolates the
Gauss measurement, rather than asserting acceptance of the complete
verification sequence.

The same support argument holds for a general local error: conjugation
by \(T_v\) exchanges B and C only inside matched pair v. A Gauss
measurement is a sum of the identity branch and the \(G_v\) branch.
The frame changes in the latter are consistent, while existing local
data damage retains its matched-pair labels. Faulty measurement ports
add at most one new label per fault.

### 1.7. Full-word gauge decoding protects the correction choice

Reading the gauge register does not itself repair quantum data. Its
purpose is to identify the classical frame needed for the ordinary
SWAP correction.

In each term of the error expansion, the reported twenty-bit word has
the form

\[
m=\delta t\oplus e,
\qquad |e|\le2.
\]

Here \(|e|\) counts the positions that differ from the underlying valid
cut word. Residual gauge bit errors and faulty gauge-readout reports
each contribute at most one position per fault. The consistent Gauss
frame changes described above change \(\delta t\), rather than adding
eight positions to e. Gauge phase errors change branch amplitudes,
not computational-basis bit values. All contributions share the same
global two-fault budget.

The doubled-K5 graph makes different valid cut words well separated.
A cut separating k vertices from the others contains

\[
2k(5-k)
\]

edges. Its smallest nonzero value is eight. Since the difference of
two cut words is itself a cut word, distinct valid words differ in
at least eight positions.

The decoder selects a valid word within distance two of m. The underlying
\(\delta t\) is such a word. There cannot be a second candidate: two
words each within distance two of m would differ on at most four
positions, contradicting their minimum separation of eight.

Thus **the decoder recovers the correct cut word**. If several coherent
error terms produce the same reported m, they must agree on that
underlying cut word, so the feedforward is consistent across those terms.

**Example and limitation.** Suppose the true gauge word is all zeros,
but the report for \(A_7\) is wrong:

\[
m_7=1,\qquad m_q=0\quad(q\ne7).
\]

The decoder recognizes a word one bit away from the zero cut. It returns
the zero frame, so no data SWAP is applied. This prevents the readout
fault from selecting an incorrect group-wide correction.

If the data already contain \(X_{B_2}\), that error remains. A faulty
physical SWAP correction can also damage its data pair. Successful
classical decoding prevents an erroneous choice of frame correction;
it does not guarantee an error-free data state or the correct logical
SWAP projection.

### 1.8. Undoing the controlled SWAPs without spreading existing errors

We now show why the decoded correction preserves the matched-pair error
bound. First track the ideal states, then insert the local errors.
Write \(|\psi\rangle\) for the intended encoded B/C input.

**Resource preparation.** The five vertex qubits V start in
\(|+\rangle^{\otimes5}\), so all 32 bit patterns
\(t=(t_a,t_b,t_c,t_d,t_e)\) are present with equal amplitudes.
The resource CNOTs prepare the following twenty-bit string on the
ancilla register A:

\[
p(t)_q=t_u\oplus t_v
\quad\text{for an edge }q\text{ joining vertices u and v}.
\]

Let \(\bar t\) mean t with all five bits flipped. Both endpoint bits
are reversed, so \(p(\bar t)=p(t)\). Because the graph is connected,
these are the only two vertex patterns giving this ancilla string.
Choose t with \(t_a=0\). The resource state contains the pair of terms

\[
\bigl(|t\rangle_V+|\bar t\rangle_V\bigr)
|p(t)\rangle_A|\psi\rangle.
\]

Only this pair is displayed; its common normalization factor is omitted.

**Controlled SWAPs.** Recall that \(T_v\) swaps the four corresponding
data pairs in inner blocks v of B and C. Define

\[
V_t=\prod_vT_v^{t_v},\qquad U=\prod_vT_v.
\]

There is one controlled-SWAP circuit. On vertex component t it applies
\(V_t\); on \(\bar t\) it applies \(V_{\bar t}=V_tU\).
The displayed pair becomes

\[
|t\rangle_V|p(t)\rangle_A V_t|\psi\rangle
+|\bar t\rangle_V|p(t)\rangle_A V_tU|\psi\rangle.
\]

**Vertex readout and ancilla readout.** For example, if all five vertex-X
outcomes are +1, then
\(\langle+|^{\otimes5}|t\rangle
=\langle+|^{\otimes5}|\bar t\rangle=1/\sqrt{32}\).
The contribution with ancilla string \(p(t)\) is therefore proportional to

\[
|p(t)\rangle_A V_t(I+U)|\psi\rangle.
\]

Other accepted vertex outcomes use the prescribed ancilla-Z sign
corrections. The ideal intervening gauged checks leave the ideal state
unchanged. Later, measuring A in Z and decoding its twenty reports
identifies \(p(t)\), as shown in Section 1.7. The decoder chooses the
root-zero t and applies the ordinary SWAPs \(V_t\). Since \(V_t^2=I\),

\[
V_t\bigl[V_t(I+U)|\psi\rangle\bigr]=(I+U)|\psi\rangle.
\]

**Include the errors and check their support.** For a fixed set of
reported outcomes, expand the faults into operator terms. By the
preceding support bounds, the two contributions in one such term,
after the ancilla readout but before correction, have the form

\[
cE_tV_t|\psi\rangle+dE_{\bar t}V_tU|\psi\rangle.
\]

Here \(E_t,E_{\bar t}\) are local data-error operators; each occupies
at most f matched pairs if f faults have occurred so far. The numbers
c,d include the measurement amplitudes and phase errors. They need not
be equal in a faulty attempt. Different observed records are treated
separately; the expansion is within a fixed record.

Applying the decoded correction gives exactly

\[
\begin{aligned}
V_t\bigl[cE_tV_t|\psi\rangle+dE_{\bar t}V_tU|\psi\rangle\bigr]
&=cE'_t|\psi\rangle+dE'_{\bar t}U|\psi\rangle,\\
E'_t&=V_tE_tV_t,\\
E'_{\bar t}&=V_tE_{\bar t}V_t.
\end{aligned}
\]

Each SWAP in \(V_t\) exchanges \(B_q\) with \(C_q\), which have the
same inner-block label. For example,

\[
\operatorname{SWAP}(B_0,C_0)X_{B_0}
\operatorname{SWAP}(B_0,C_0)=X_{C_0}.
\]

The error can move between the two copies, but stays inside matched
pair a. The same reasoning applies to every factor of a general error.
Thus \(E'_t\) and \(E'_{\bar t}\) have no new matched-pair labels.
A fault in a correction SWAP can add only the matched pair containing
its two targets. With g such additional faults, the bound is therefore
\(f+g\le2\), not two new faults at the correction stage.

Collecting the terms yields the form used below,
\(\sum_\nu E_\nu(\alpha_\nu I+\beta_\nu U)|\psi\rangle\),
where \(\nu\) labels expansion terms and each \(E_\nu\) acts on at
most two matched pairs. Distinct local errors are kept as separate
terms, with one coefficient zero if necessary. If an environment is
retained, the argument applies to each component in an environment basis.
This proves the support bound through the correction; controlling the
remaining coefficients to obtain the positive SWAP projection belongs
to the next part of the proof.

### 1.9. Conclusion of the spatial argument

The gadget, preparation, propagation, and decoding arguments together
give the following bound: **each fault can add local data damage in at
most one new matched pair**. Fault-free propagation and frame removal
preserve the existing matched-pair labels. Therefore, with at most two
faults in the whole attempt, the conditional state after ungauging lies
in the span

\[
\operatorname{span}\left\{
E_\nu(\alpha_\nu I+\beta_\nu U)|\psi\rangle:
E_\nu\text{ acts on at most two matched pairs}
\right\}.
\]

This permits up to four actual inner C4 blocks, at most two in either
copy and with the same two allowed labels across B and C. The bound
applies **term by term**; a coherent superposition need not have one
fixed damaged-pair set shared by all its terms.

The expressions \(D(aI+bQ)\) and
\(E_\nu(\alpha_\nu I+\beta_\nu U)\) separate local damage from
coherent alternatives in a conditional measurement operation. In the
first expression the alternatives are I and the measured check Q;
in the second they are I and the whole-block SWAP U.

The spatial bound does not yet establish the intended logical state:
\(\alpha=\beta\) gives the positive SWAP projection, whereas
\(\alpha=-\beta\) gives the negative projection. The next part of the
proof must establish the correct positive projection despite faulty
measurement actions. Only after that step can the two-group lemma be
used to filter the remaining local damage around the intended state.

## 2. Protect the intended SWAP measurement

The aim is to remove the negative SWAP contribution without assuming
that earlier measurements reported their true outcomes. Local errors
on at most two matched pairs are still allowed.

### 2.1. Positive and negative SWAP components

The whole-block SWAP U exchanges B and C and satisfies \(U^2=I\).
For the intended encoded input \(|\psi\rangle\), define

\[
|\psi_+\rangle=\Pi_+|\psi\rangle,
\qquad
|\psi_-\rangle=\Pi_-|\psi\rangle,
\qquad
\Pi_\pm=\frac{I\pm U}{2}.
\]

These components are generally unnormalized. They satisfy

\[
U|\psi_+\rangle=|\psi_+\rangle,
\qquad
U|\psi_-\rangle=-|\psi_-\rangle.
\]

A *negative SWAP component* is a state with the second property: the
eigenvalue of U is −1. U itself remains the SWAP operator, not the number −1.
For example, swapping two ordinary qubits gives

\[
U\frac{|01\rangle-|10\rangle}{\sqrt2}
=-\frac{|01\rangle-|10\rangle}{\sqrt2}.
\]

During the gauged checks, the ancilla register A is still present.
Using the explicit ancilla strings \(p(t)\) and data SWAPs \(V_t\)
from Section 1.8, write the two reference states as

\[
|\Phi_\pm\rangle
=\frac14\sum_{t:t_a=0}|p(t)\rangle_A V_t|\psi_\pm\rangle.
\]

Each sum has sixteen terms. These are the same correlated ancilla/data
states as in Section 1.8, with the input replaced by \(|\psi_\pm\rangle\).
They are reference states for the error expansion; the negative one is
not an additional accepted preparation. Since U acts only on the data
and commutes with every \(V_t\),

\[
U|\Phi_\pm\rangle=\pm|\Phi_\pm\rangle.
\]

The task is to show that a clean accepted round removes all terms coming
from \(|\Phi_-\rangle\), even when local errors are present.

### 2.2. What passing the paired checks says about an error

A paired check measures \(N_j=S^j_BS^j_C\), where \(S^j\) is one of
the eighteen independent original-code stabilizers. The superscript j
here labels a check, including its X or Z type. Both reference states
\(|\Phi_\pm\rangle\) pass every paired check: the original input does,
and each matched factor \(P_{B_q}P_{C_q}\), with \(P=X,Z\), commutes
with the enrichment SWAPs.

Consider one Pauli term of a data error, written

\[
E=P_B R_C.
\]

The symbols have the following meanings:

- P is a Pauli pattern on twenty positions, applied to B as \(P_B\).
- R is a potentially different Pauli pattern, applied to C as \(R_C\).
- \(P_C\) means the **same pattern as P**, applied to C instead of B.
  For example, \(P_B=X_{B_0}\) means \(P_C=X_{C_0}\).

An error term that anticommutes with a paired check is rejected by its
clean positive measurement. If E commutes with every paired check,
P and R must have the same commutation sign with every original
stabilizer \(S^j\): both commute, or both anticommute. Their relative
Pauli pattern \(P^\dagger R\) consequently commutes with every \(S^j\).

In \(P^\dagger R\), both patterns are written on the same list of
twenty positions; this is not the forty-qubit operator
\(P_B^\dagger R_C\). The dagger denotes the Hermitian adjoint, which
is the inverse because P is unitary. For the usual Hermitian choice
of Pauli phase, \(P^\dagger=P\).

P and R together occupy at most two matched-pair labels. Thus
\(P^\dagger R\) occupies at most two inner C4 blocks of one copy.
The two-group lemma gives

\[
P^\dagger R=S
\]

up to an overall phase, where S is a stabilizer. Overall phases are
omitted in the following operator rewritings. Multiplying on the left
by P gives

\[
P(P^\dagger R)=PS
\quad\Longrightarrow\quad R=PS.
\]

Therefore \(R_C=P_CS_C\), and the original error can be rewritten as

\[
E=P_BR_C=P_B(P_CS_C)=(P_BP_C)S_C.
\]

**Nothing has been changed on B.** Only \(R_C\) has been rewritten;
this is an operator identity, not a correction gate being applied.

### 2.3. A worked example: one X in B and three in C

Use throughout this section the error

\[
E=X_{B_0}X_{C_1}X_{C_2}X_{C_3}.
\]

It occupies only matched pair a. Its one-copy patterns and relative
stabilizer are

\[
P=X_0,\qquad R=X_1X_2X_3,\qquad
S=P^\dagger R=X_0X_1X_2X_3.
\]

The stabilizer S is the inner XXXX check. Explicitly,

\[
\begin{aligned}
E
&=\underbrace{X_{B_0}X_{C_0}}_{P_BP_C}
\underbrace{X_{C_0}X_{C_1}X_{C_2}X_{C_3}}_{S_C}\\
&=X_{B_0}X_{C_1}X_{C_2}X_{C_3},
\end{aligned}
\]

because the two \(X_{C_0}\) factors cancel.

**The error passes the paired checks.** For the inner Z check, the
paired observable is

\[
N_a^Z=(Z_{B_0}Z_{B_1}Z_{B_2}Z_{B_3})
       (Z_{C_0}Z_{C_1}Z_{C_2}Z_{C_3}).
\]

E anticommutes once on B and three times on C. The total sign is
\((-1)^{1+3}=+1\), so E commutes with this paired check, although it
flips both individual inner-Z checks. It also commutes with every
paired X check, since all factors are X. The remaining paired Z checks
commute with E because \(P^\dagger R=S\) is a stabilizer. For example,
the upper Z check on \(R_5\) overlaps P at position 0 and R at
position 3: one minus sign in each copy again cancels in their product.

This example shows why passing paired checks need not mean that the
original checks of B and C are individually positive. What is fixed
is their product.

### 2.4. A surviving error cannot change the SWAP eigenvalue

First complete the argument for a general surviving error
\(E=(P_BP_C)S_C\). Let \(|\chi\rangle\) pass all paired checks.
Since S is a product of original stabilizers, \(S_BS_C\) is a
product of their paired checks. Hence

\[
S_BS_C|\chi\rangle=|\chi\rangle,
\qquad S_B|\chi\rangle=S_C|\chi\rangle.
\]

U leaves \(P_BP_C\) unchanged and exchanges \(S_C\) with \(S_B\).
Also, \(U|\chi\rangle\) still passes all paired checks. Therefore

\[
\begin{aligned}
UE|\chi\rangle
&=(P_BP_C)S_B U|\chi\rangle\\
&=(P_BP_C)S_C U|\chi\rangle
=EU|\chi\rangle.
\end{aligned}
\]

Thus, if \(U|\chi\rangle=\pm|\chi\rangle\), then
\(UE|\chi\rangle=\pm E|\chi\rangle\): E preserves that sign.

**For the worked example, this equality can be checked directly.**
Swapping B and C exchanges E with

\[
UEU=X_{C_0}X_{B_1}X_{B_2}X_{B_3}.
\]

Define the paired inner-X check

\[
N_a^X=(X_{B_0}X_{B_1}X_{B_2}X_{B_3})
       (X_{C_0}X_{C_1}X_{C_2}X_{C_3}).
\]

Multiplying E by this check cancels four factors and gives exactly

\[
EN_a^X=X_{B_1}X_{B_2}X_{B_3}X_{C_0}=UEU.
\]

On a state passing \(N_a^X\), E and its exchanged version therefore
act identically. In particular,

\[
UE|\Phi_\pm\rangle
=EN_a^X U|\Phi_\pm\rangle
=\pm E|\Phi_\pm\rangle.
\]

The example can leave physical errors in both copies, but cannot turn
the −1 SWAP contribution into a +1 contribution.

### 2.5. The Gauss measurements reject the negative contribution

Multiplying the five commuting Gauss checks cancels every gauge-X
factor, because each edge belongs to two stars:

\[
G_aG_bG_cG_dG_e=T_aT_bT_cT_dT_e=U.
\]

Their joint positive projector therefore contains the positive SWAP
projector. More explicitly,

\[
P_G:=\prod_{v=a}^e\frac{I+G_v}{2}
=\left[\prod_{v=b}^e\frac{I+G_v}{2}\right]\Pi_+.
\]

The paired, cycle, and Gauss observables commute, so the factors can
be grouped this way when analyzing a clean round without changing
the physical schedule.

An error E surviving the paired checks preserves the U sign, as proved
above. Therefore

\[
\begin{aligned}
\Pi_+ E|\Phi_-\rangle
&=\frac12(E|\Phi_-\rangle+UE|\Phi_-\rangle)=0,\\
\Pi_+ E|\Phi_+\rangle
&=\frac12(E|\Phi_+\rangle+UE|\Phi_+\rangle)
=E|\Phi_+\rangle.
\end{aligned}
\]

The negative contribution is removed. Other positive-check constraints
may reject additional components, but cannot restore the negative one.
Gauge-only errors do not change this argument: they commute with U,
which acts on B and C, and with the paired data checks.

**In the example, the distinction is especially explicit.** Conjugating
E by \(G_a\) swaps its B/C factors just as U does:

\[
G_aEG_a=EN_a^X.
\]

The reference states obey
\(G_a|\Phi_\pm\rangle=\pm|\Phi_\pm\rangle\). This follows by
toggling the root bit in the sum in Section 2.1: rewriting the result
with root zero complements the other bits and adds U to the data.
For b,c,d,e, toggling a nonroot bit only permutes that sum, so
\(G_v|\Phi_\pm\rangle=|\Phi_\pm\rangle\).
Consequently,

\[
G_aE|\Phi_\pm\rangle=\pm E|\Phi_\pm\rangle.
\]

In a clean round, \(E|\Phi_-\rangle\) gives a negative \(G_a\)
outcome and is rejected. The positive component \(E|\Phi_+\rangle\)
passes: E commutes with the other four Gauss checks and all cycle
checks. Its physical error remains, but its SWAP sign is correct.

### 2.6. One clean round fixes the reference; later faults stay local

Each complete gauged round includes its helper preparation, checks,
and waiting locations. With at most two faulty locations total, one
of the three rounds is clean. An accepted attempt must pass that
round's actual positive projections, not merely faulty reports from
the other rounds.

After the negative contribution has been removed, the remaining
projectors leave errors around the same positive reference
\(|\Phi_+\rangle\). Each measured check Q satisfies
\(Q|\Phi_+\rangle=|\Phi_+\rangle\). For any existing error E,

\[
\frac{I+Q}{2}E|\Phi_+\rangle
=\frac12(E+QEQ)|\Phi_+\rangle.
\]

Conjugation by a paired or cycle check does not enlarge the data
support; conjugation by a Gauss check exchanges B and C only within
matched pairs. Thus these projectors preserve the matched-pair bound.

The same calculation covers subsequent faulty check measurements.
Using the gadget form from Section 1.3,

\[
D(aI+bQ)E|\Phi_+\rangle
=D(aE+bQEQ)|\Phi_+\rangle.
\]

The coefficients a,b may be wrong, but the reference on the right
remains \(|\Phi_+\rangle\). D adds only its charged local ports.
No new fault budget begins after the clean round. The decoder from
Section 1.7 and the correction from Section 1.8 then leave, after
ungauging, a sum of terms

\[
E_\nu\Pi_+|\psi\rangle,
\qquad E_\nu\text{ supported on at most two matched pairs}.
\]

This proves the second step: the underlying projection is positive,
while the local physical damage remains for the next filtering stage.

### 2.7. What remains of the example after ungauging

For the worked error, each partial SWAP correction either leaves E
unchanged or exchanges it with \(EN_a^X\). These operators act
identically on the corrected original-code reference
\(|\psi_+\rangle=\Pi_+|\psi\rangle\), since
\(N_a^X|\psi_+\rangle=|\psi_+\rangle\). Ignoring new faults, the
surviving data state is therefore proportional to

\[
X_{B_0}X_{C_1}X_{C_2}X_{C_3}|\psi_+\rangle
=X_{B_0}X_{C_0}|\psi_+\rangle.
\]

The equality uses the original C inner-X stabilizer. There is still
an X error in each copy. Each flips that copy's inner-Z check, so a
clean original-code positive filtering round rejects this component.
The paired check did not reject it because the two negative signs
multiplied to +1; the later individual checks do reject it. This
illustrates the different jobs of the gauged verification in step two
and the original-code filtering in step three.

## 3. Remove the larger errors after ungauging

After ungauging, measure the **original stabilizers separately on B
and C**, in three complete rounds, requiring every reported outcome
to be +1. This stage rejects damaging errors rather than trying to
determine which correction to apply.

### 3.1. State entering this stage

Write

\[
|\psi_+\rangle=\frac{I+U}{2}|\psi\rangle
\]

for the desired data state before the final B readout. It is generally
unnormalized. Both B and C are in their original code spaces, so every
original stabilizer S satisfies

\[
S|\psi_+\rangle=|\psi_+\rangle.
\]

Point two leaves a sum of terms

\[
\sum_\nu c_\nu E_\nu|\psi_+\rangle,
\]

where each error \(E_\nu\) occupies at most two matched pairs: at most
two inner C4 blocks in each copy. The \(c_\nu\) are coefficients for
a fixed measurement record. As before, expand a general error into
Pauli terms; the argument below treats each term and then adds the
surviving contributions.

### 3.2. Apply the original checks to the worked example

Recall

\[
E=X_{B_0}X_{C_1}X_{C_2}X_{C_3}.
\]

Consider the two original inner-Z checks:

\[
S_B=Z_{B_0}Z_{B_1}Z_{B_2}Z_{B_3},
\qquad
S_C=Z_{C_0}Z_{C_1}Z_{C_2}Z_{C_3}.
\]

E anticommutes with \(S_B\) once and with \(S_C\) three times.
Therefore,

\[
S_BE|\psi_+\rangle=-E|\psi_+\rangle,
\qquad
S_CE|\psi_+\rangle=-E|\psi_+\rangle.
\]

**Both individual checks give −1, so a clean positive filtering round
rejects this component.** Previously, the paired check measured
\(S_BS_C\): the two minus signs multiplied to +1. Measuring the
individual checks now reveals what their product did not.

### 3.3. Why this works for every allowed error

For each Pauli term \(E_\nu\), there are two possibilities.

**If it anticommutes with an original stabilizer S**, positive
postselection removes it:

\[
\frac{I+S}{2}E_\nu|\psi_+\rangle
=\frac{E_\nu|\psi_+\rangle-E_\nu|\psi_+\rangle}{2}
=0.
\]

**If it commutes with every original stabilizer**, we must still
determine whether it changes the encoded information. Commutation
alone puts no bound on physical weight. For example, on one copy,
both of the following commute with every check:

- \(X_0X_1X_2X_3\): weight four, an inner stabilizer, which leaves
  every encoded state unchanged.
- \(X_2X_3X_8X_{11}X_{12}X_{15}=\overline X_0\): weight six, a
  logical X, which can change the encoded information.

Thus passing every check does not by itself imply a harmless error.

**Why distance six alone is insufficient here.** Distance six gives
two different guarantees:

- Every Pauli of weight at most five either changes a check outcome
  or acts trivially on the encoded information.
- Every unknown physical error of weight at most two can be corrected.

The first statement concerns detection of damaging errors; the second
concerns identifying a correction reliably. A stabilizer error needs
no correction because its action on an encoded state is already the
identity.

Our bound at this stage is two inner C4 blocks per copy, containing up
to eight physical qubits. Such an error can have weight six, seven,
or eight. A small fault earlier in the circuit can propagate into an
error on several physical qubits, so two faults cannot yet be treated
as ordinary weight-at-most-two errors.

**The two-group lemma supplies the missing restriction.** Restating
Section 1.1 for one copy:

> A Pauli confined to at most two inner C4 blocks either changes an
> original-code check outcome or acts as the identity, up to phase,
> on every encoded state.

The reason is concrete: passing the inner ZZZZ checks requires an
even number of X factors in each inner block. Multiplying by XXXX
removes any group of four X factors, leaving at most two per block,
hence at most four in total. The Z-only part is reduced in the same
way using ZZZZ. Because the code is CSS, an undetected mixed Pauli
has undetected X-only and Z-only parts separately. Distance six then
excludes a nontrivial logical action for either reduced part.

Apply this lemma separately to B and C. A joint Pauli \(E_\nu\)
is a product of a Pauli on B and a Pauli on C. Commuting with every
original B/C check means that each factor commutes with all checks
of its own copy. Each factor occupies at most two inner C4 blocks,
so each acts trivially on that copy's code space. Therefore, also
for the entangled encoded state \(|\psi_+\rangle\),

\[
E_\nu|\psi_+\rangle=\eta_\nu|\psi_+\rangle,
\]

where \(\eta_\nu\) is an overall phase.

For the Pauli terms used here, these harmless operators are
**proportional to products of stabilizer generators**, including
the identity. A Pauli that acts as a scalar times the identity on
every encoded state has the form

\[
E_\nu=e^{i\theta}S_1S_2\cdots S_k,
\]

where the \(S_j\) are original B/C stabilizer generators. For example,
\(X_{B_0}X_{B_1}X_{B_2}X_{B_3}\) passes all checks because it is
itself a stabilizer and leaves \(|\psi_+\rangle\) unchanged.

A general harmless quantum operator need not be proportional to one
Pauli stabilizer product. If S is a stabilizer, for instance,

\[
e^{i\theta S}=\cos\theta\,I+i\sin\theta\,S,
\qquad
e^{i\theta S}|\psi_+\rangle=e^{i\theta}|\psi_+\rangle.
\]

It is harmless on the code, although generally a linear combination
of stabilizer operators. This is why the proof treats Pauli terms
first and then adds their surviving contributions.

**Action of a complete clean positive round.** Detected terms disappear;
harmless terms contribute only their scalar factors. Consequently,

\[
\sum_\nu c_\nu E_\nu|\psi_+\rangle
\quad\longmapsto\quad c\,|\psi_+\rangle.
\]

If \(c=0\), the branch is rejected. Otherwise normalization gives
exactly the intended state. This argument also applies component by
component if the errors are correlated with an unobserved environment.

### 3.4. Why repeat the filter, and why recovery is still needed

With three complete rounds and at most two faulty locations in the
entire attempt, at least one round is clean.

Choose the **last clean round** as a reference point in the proof;
the decoder does not need to identify it. At its end, an accepted
branch has the intended state.

Faults afterward can still introduce errors. But all enrichment and
correction SWAPs have finished. The remaining Pauli-check gadgets use
one cat leaf per physical data qubit, so each later fault contributes
at most one erroneous data qubit.

Faulty check amplitudes also preserve existing support. For an original
stabilizer S and an existing error F,

\[
(aI+bS)F|\psi_+\rangle
=(aF+bSFS)|\psi_+\rangle.
\]

Because S is a product of single-qubit Paulis, \(SFS\) does not occupy
additional qubits. Any additional local target damage from a faulty
gadget is charged to its faulty locations, as in Section 1.3.

**The result of point three:** inherited errors affecting whole inner
C4 blocks have been filtered out. At the end of filtering, only
errors caused after the last clean round can remain—at most two
physical-qubit errors. Point four must protect their recovery and
the final readout within the remaining global fault budget.

## 4. Protect recovery and final readout

The filter would suffice if everything afterward were perfect. This
last step is needed because waiting, recovery gates, and readout can
also fail. All these faults remain part of the same two-fault budget.

### 4.1. An error that the preceding filter cannot catch

Suppose filtering has finished successfully, leaving
\(|\psi_+\rangle\). While \(C_0\) waits for recovery, it suffers
an X error:

\[
|\psi_+\rangle\longrightarrow X_{C_0}|\psi_+\rangle.
\]

All previous filtering outcomes remain positive: those measurements
happened **before this error**. A new measurement of the C inner-Z
check would give

\[
(Z_{C_0}Z_{C_1}Z_{C_2}Z_{C_3})X_{C_0}|\psi_+\rangle
=-X_{C_0}|\psi_+\rangle.
\]

Recovery measures the original checks again to detect such residual
errors. The useful result of point three is that these are now
**small errors**: after the last clean filtering round, each further
fault can damage at most one physical data qubit.

### 4.2. Recovery must tolerate wrong measurement reports

Measure all 36 original B/C checks repeatedly, with fresh verified
cats. Their reported bits form the *syndrome*: zero means a reported
+1 outcome and one means a reported −1 outcome. Retain either sign
and apply no corrections between rounds. Failed cat verification
still rejects the attempt.

Stop at the first three consecutive identical joint syndrome records,
allowing at most nine rounds. Reject if there is no such triple by
round nine.

Why this rule works:

- At most two rounds can contain faults. A round includes its helper
  preparation and all waiting locations; boundary idles belong to the
  following interval.
- An identical triple therefore contains at least one clean round.
- Its common record is consequently a genuine syndrome at the time
  of that clean round.

Nine rounds suffice to contain three consecutive clean rounds: two
faulty rounds can separate the clean rounds into at most three runs.
If every clean run had length at most two, there would be at most
\(3\times2+2=8\) rounds altogether. Consecutive clean rounds have the
same true syndrome because no intervening operation introduces an
error. Thus the recovery stopping rule is reached by round nine in
an unrejected attempt under the fault bound.

The clean round inside the stopping triple is a reference point for
the proof, not a round the decoder must identify. Faults later in
that triple are handled as subsequent local errors below.

### 4.3. Why the selected correction is logically correct

Work on either copy and let E be its Pauli error at the clean reference
round inside the stopping triple. E has weight at most two. Choose a
minimum-weight Pauli correction R of weight at most two giving the
same eighteen syndrome bits for that copy. Use the prescribed fixed
lookup; reject if no candidate exists.

The two operators have the same commutation signs with every
stabilizer, so RE commutes with every stabilizer. Also,

\[
\operatorname{weight}(RE)
\le\operatorname{weight}(R)+\operatorname{weight}(E)
\le4.
\]

Distance six excludes a nontrivial logical action. Therefore, with
E and R acting on the copy under consideration,

\[
RE|\psi_+\rangle=e^{i\theta}|\psi_+\rangle.
\]

Applying this argument to both B and C proves that the chosen
corrections remove the errors present at that reference time without
changing the intended encoded state. The argument applies to each
Pauli term of a general error, including coherent superpositions.

Faults **after** the reference round may still occur. But Pauli
correction gates do not spread an error to other qubits: conjugating
an error by a Pauli only changes its Pauli coefficients, not its
support. A faulty single-qubit correction adds damage only on its
own qubit. The recovery measurements have the same bounded-support
property established in Section 3.4.

Consequently, after correction, the remaining errors are attributable
to faults after the reference round. Their physical support is bounded
by that remaining fault count, rather than by the number of gates
used in the selected correction. There is no new allowance of two
faults during recovery.

### 4.4. Protect the complete B readout and retain C

Measure all twenty B qubits in Z. Even after successful recovery:

- A B measurement can report the wrong bit.
- A residual X or Y error on B can flip a readout bit.
- C can suffer a waiting error during B readout.

Therefore, decode the **complete twenty-bit B report**, using its
nine independent Z-check parities and a bit-flip correction of weight
at most two. Reject if no such correction exists. The bound includes
both preceding B bit errors and wrong readout reports under the same
remaining fault budget; it does not allow two of each. A Z-only error
on measured B contributes a phase to an individual Z-readout branch,
without changing the retained C state for that branch.

The decoded logical parity is well-defined. Two candidate bit-flip
corrections of weight at most two with the same Z-check syndrome
differ by an X-type Pauli of weight at most four. This difference
commutes with the Z checks and, automatically, with the X checks.
Distance six makes it a stabilizer up to phase, so it cannot change
the logical-Z parity. This also compares the chosen correction with
the true bit-flip pattern, whose weight is within the same bound.

Let \(n'\) be the corrected classical report. Evaluate

\[
\ell=n'_0\oplus n'_3\oplus n'_6\oplus n'_7\oplus n'_{18}\oplus n'_{19},
\]

which is the logical \(\overline Z^B_0\) measurement bit. Keep
\(\ell=0\). The raw parity on these six uncorrected reports is not
the protected logical readout. Correction of the report is classical;
no further quantum correction is applied to the measured B qubits.

Selecting decoded logical \(B_0=0\) from the intended reference
\(|\psi_+\rangle\) leaves the encoded magic state in C. Residual
C errors, including its waiting errors during B readout, belong to
its weight-at-most-two correctable error space.

### 4.5. Final guarantee

Every accepted attempt with at most two faulty locations in the
entire scheduled procedure has decoded C output

\[
|M\rangle\otimes|0\rangle,
\qquad |M\rangle=\frac{2|0\rangle+|1\rangle}{\sqrt5}.
\]

The guarantee is a correct logical output, not a physically flawless
output. Filtering, recovery, and readout share the same global fault
budget. Mathematical decoding defines the output criterion; it is
not an additional fault-free physical recovery appended to the circuit.
