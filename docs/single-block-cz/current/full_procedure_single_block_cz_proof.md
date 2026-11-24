# Accepted-output proof for the single-block C4-Helix CZ factory

The optional `--root-recovery joint` local-Gauss schedule has a separate
[graph-assisted recovery proof](single_block_cz_graph_assisted_root_recovery_proof.md).
It derives the conditional commuting diagnostic history, correlated
graph/data fault envelopes and complete affine-class acceptance rule.
The proof retains coherent W-hook spans and composes with the original
terminal tail under the same global two-fault budget. It also certifies
`--conditional-checks dual_flags` for the shared one-remaining-fault
data recovery, including the genuine-cat baseline. The saved finite
certificate covers the generated error families, not all factory fault pairs.

The optional persistent-frame schedule has a separate
[composition proof](single_block_cz_persistent_coordinates_proof.md).
It transports the root to U times the graph root star and keeps all later
data faults in physical-site cones, allowing the intrinsic tail and tree4.
The old cut-distance and terminal-recovery lemmas below are not asserted
for that changed schedule. The theorem's global two-fault budget is retained.

The optional `--data-checks compact_flags` schedule composes via the
[compact-check replacement proof](single_block_cz_compact_checks_proof.md):
the same signed Pauli projectors, a one-physical-site-per-zero-flag-fault
bound, and independently certified extraction-specific flag recovery.
It retains the global two-fault contract and all outer checks; it does
not change the existing ordered terminal-screen circuit.

This proof applies to the **specific conservative physical schedule** in
[the integrated procedure](full_procedure_single_block_cz.md) and
[`c4_helix_single_block_cz.py`](../src/c4_helix_single_block_cz.py).
It does not extend the old SWAP theorem by analogy. In particular there is
no second data block, paired B/C check, or joint B/C decoder here.

The result is analytical, using the finite certificates stated below.
There is no claim of full-circuit fault-pair enumeration. The default
gadget deliberately uses three cat-verification scans and three complete
rounds; the old adaptive history and two-initial-zero shortcuts are not used.

## The theorem and physical model

Let at most two locations fail in the **entire executed attempt**, including
all unused-resource retries, source corrections, graph phase corrections,
conditional ungauging corrections, helper preparation, destructive
measurement, wrong reports, and single-qubit idles. A gate location acts
on exactly the participants of one gate from

\[
\{|0\rangle\text{ preparation},H,S,S^\dagger,X,Y,Z,T,T^\dagger,
  \mathrm{CX},M_Z,\mathrm{IDLE}\}.
\]

A faulty location is an arbitrary linear operator/channel on its
participants, possibly correlated with an environment. A faulty meter
may implement an arbitrary quantum instrument on its one qubit and
return either bit. Classical calculation and scheduling are reliable.
Leakage which later corrupts additional gates consumes those additional
faulty locations; uncounted persistent leakage is outside this model.

Every controlled W is the three individual locations T/CX/T†. CZ ports
are H/CX/H, also individual locations. There are no atomic controlled-W,
Fredkin, Toffoli, CCZ, or multi-data gates. All physical gates are serial;
every other live qubit has a separate idle during each operation.
There is one further idle on each live qubit at each stage boundary,
including after the final round and before handoff. There are no
unmodelled waits between operations. A round includes its own helper
preparations, failed local-cat retries, and idles. Boundaries belong to
the interval immediately following the preceding round for purposes of
the late-error bound. They cannot be excluded from the global fault count.

**Theorem.** Every accepted output is supported on

\[
\mathcal E_2|\overline{CZ_{\rm magic}}\rangle,
\qquad
|CZ_{\rm magic}\rangle=(|00\rangle+|01\rangle+|10\rangle)/\sqrt3,
\]

where \(\mathcal E_2\) is the linear span of all physical Pauli errors
of weight at most two on the twenty output data qubits. The standard
distance-six error-correcting recovery maps this entire subspace to the
stated logical pure state, tensored with an error/environment state.
The guarantee concerns decoded output; no noiseless physical recovery
operation is assumed to have been performed by the factory.

There need not be positive acceptance for every adversarial fault.
There is positive acceptance 3/4 without faults. No lower bound on noisy
yield, matched-fidelity stochastic cost, or general scalability follows.

## A. Signed logical action and exact measurement

Let H be the nine binary supports in the integrated note; C=span(H).
The exact computational logical basis is

\[
|\overline{l_0l_1}\rangle=2^{-9/2}
 \sum_{c\in C}|c+l_0 X_0+l_1 X_1\rangle.
\]

The independent code checks have rank eighteen, with X/Z commutation
matrix zero and canonical logical pairing. C has 512 words; its dual
has 2048 words and is span(H,X0,X1). Minimum nonstabilizer weight in the
dual is six, proving CSS distance six, including mixed X/Z errors:
any nontrivial mixed logical has at least one nonstabilizer component.
The independent encoder audit propagates the signed computational
amplitudes through every H and CNOT and obtains exactly +1 on all 2048
dual words, zero elsewhere. Thus its normalized state is |++>.

For epsilon=(-1,+1,+1,-1) on every inner block,

\[
W_\epsilon=e^{-i\epsilon\pi/4}XS^\epsilon
=\frac{X-\epsilon Y}{\sqrt2}
=T^{-\epsilon}XT^\epsilon.
\]

The matrices are Hermitian involutions. The scalar phases cancel in
each native four-site epsilon pattern, so U0=X_all F exactly on the
full Hilbert space. X_all is the product of the five inner X checks.
On the four logical sectors F has phases (+,-,+,+), hence F=CZbar Zbar1.
For D=Xbar0, U=D U0 D has logical phases (+,+,+,-), including the
positive phase on logical 00. Set s_q=epsilon_q(-1)^[q in X0]. Then
U=product W_s_q, with no missing branch phase.

The identity

\[
C(W_s)=(I\otimes T^{-s})\,\mathrm{CX}\,(I\otimes T^s)
\]

is exact, so the physical execution order is T^s, CX, T^-s.
This is not a Clifford-only enrichment circuit. Exact matrices and
Pauli expansions are checked over Q(zeta8), retaining coefficients and
phases; two-term coherent errors occur already for a single T fault.

For N vertices the prepared graph state is

\[
|R\rangle=2^{-N/2}\sum_t |t\rangle|dt\rangle.
\]

Enrichment gives the same sum with U_t|psi> on data. An X-basis vertex
word b contributes 2^-N/2 (-1)^(b.t). An edge Z word z has zero ideal
probability unless z=d eta. A connected graph has precisely two
compatible t, eta and eta+1, so the uncorrected Kraus operator is

\[
K_{b,z}=2^{-N}(-1)^{b\cdot\eta} U_\eta(I+xU),
\qquad x=(-1)^{\sum_v b_v}.
\]

After U_eta† it is 2^(1-N) x_eta P_x, with
P_x=(I+xU)/2. For N=5, each of the 256 full records in sector x has
probability ||P_x psi||²/256. All 512 records sum to probability one;
invalid edge words have zero probability. For |++>, each positive
record has probability 3/1024, each negative one 1/1024.

Applying Z on root edge (a,v) for every nonroot b_v=1 changes only the
record-global sign for each later edge readout. It makes nonroot Gauss
eigenvalues +; root Gauss eigenvalue is x. It does not change P_x.
Specifically the frame contributes x_eta again, cancelling the bare
Kraus sign above. With the physical S/X implementation of U_eta in G,
the chosen accepted graph-record Kraus is kappa P_+/16, where
kappa=(-1)^(eta_c+eta_d), apart from the explicitly positive
normalization factors for individual helper-meter records. Thus both
the unfixed graph identity and the chosen framed schedule have tracked
global phases, while defining the same measured observable.
Discarding a reported odd b rejects immediately, but its parity is not
trusted as the final sector certificate.

## B. Gauged checks, algebra, and distance

This section describes the fully cycle-fixed reference code. The opt-in
[bare-star schedule](single_block_cz_bare_graph_stars.md) temporarily leaves
cycle sectors unfixed and proves accepted-output correctness by a separate
operator-span and terminal chord-recovery argument. Its enlarged intermediate
space is not assigned this reference code's distance claim.

Write J_v for inner block v, Xstar_v=product of incident edge Xs, and

\[
V=\prod_{v=b,c,d,e} C_{A_{av}}(U_v),\qquad V^2=I.
\]

It uses sixteen CNOTs and thirty-two T/T† gates. On every edge basis
word V applies U_eta with eta_a=0 and eta_v=z_av. It is a diagnostic
change of coordinates, not the final destructive ungauging operation.
Both V passes in each gauged round are charged to the schedule.

The globally commuting family of **31 independent** constraints is

\[
Z_s=S_s^Z,\quad Q_s=V S_s^X V,\quad
B_f=Z_{\partial f},\quad G_v=U_vXstar_v=V Xstar_v V\ (v\ne a).
\]

Under V these are the eighteen code stabilizers plus nine independent
cycle checks and four independent X stars. The last thirteen specify
the unique graph state

\[
|C_G\rangle=\tfrac14\sum_{\eta:\eta_a=0}|d\eta\rangle.
\]

Their common space on 33 qubits therefore has dimension four.
The root constraint satisfies

\[
V G_a V=U Xstar_a,
\qquad Xstar_a=\prod_{v\ne a}Xstar_v,
\qquad \prod_vG_v=U.
\]

In the graph-positive sector G_a is just U in these coordinates. Its
positive constraint leaves dimension three; its negative constraint
leaves dimension one. These are not Pauli stabilizer dimensions.

All Z_s, cycles, Q_s and nonroot G_v commute **globally**, by common
conjugation by V. Root G_a commutes globally with Z_s, cycles and all
other Gauss checks. Its group commutator with Q_s is Z_s; it commutes
with Q_s only when Z_s=+1. Equivalently U X_R U=X_R Z_R, with positive
sign for every listed R. A root check on an uncorrected Z syndrome
cannot be treated as commuting syndrome extraction.

For explicit dressing signs, put m_sv=|R_s intersect J_v| and

\[
c_{sv}=k_{sv}Z_{R_s\cap J_v},\qquad
k_{sv}=(-1)^{m_{sv}/2}\prod_{q\in R_s\cap J_v}s_q.
\]

All m_sv are even, all k_sv are real, and product_v c_sv=Z_s.
Then Q_s=X_Rs product_(v!=a) C_(A_av)(c_sv).
The integrated note lists every support and minus sign. No phase is
discarded from a controlled operator. Using the same four root paths
makes Q_s commute exactly even outside the cycle-positive sector.

**Graph conditions.** Degrees (6,5,5,5,5), cycle rank nine, complete
cycle filling H1=0, maximum basis-cycle length three, every pair of
vertices adjacent, and h_Z2=min |dt|/min(|t|,5-|t|)=3 satisfy the graph
desiderata. Grouping four disjoint one-qubit involutions into an inner
block is a valid coarse graining. The general literature's d/nu bound
alone is too weak to establish the desired circuit claim; we do not
use it for that claim.

In fact the positive gauged code has **physical distance exactly six**.
For a Pauli E of weight at most five, let f be its edge X/Y support.
If f is not a cut, some cycle anticommutes with E, so its compression
to the gauged code is zero. If f=0, conjugation by V does not enlarge
data support: expand the edge-controlled single-site conjugations;
all resulting data terms have weight at most five. Code distance six
makes each compression scalar. If f is a nonzero cut of weight at
most five, the finite cut list says it is the five-edge star of one
nonroot vertex. All five supported sites must then be edges. V E V
has data U_v on that one inner block, with arbitrary graph factors.
The two-block detection lemma below again makes its compression scalar.
This proves the lower bound. Physical Zbar0 has weight six, commutes
with V and U, and acts nontrivially on the three-dimensional positive
sector, proving the upper bound. The argument also covers arbitrary
operators supported on these sites by linearity.

**Two-block detection lemma.** If E has support in any fixed set of
at most two inner blocks, Pi E Pi=c_E Pi for the original code
projector Pi. For each of the ten pairs, enumerating all 4^8 Paulis
gives exactly sixteen zero-syndrome operators, all stabilizers; the
rest have zero compression. These sixteen are the products of the
four inner X/Z checks. Pauli expansion proves the arbitrary-operator
version, including coefficients correlated with a graph/environment.
This is detection of two blocks and correction of their known erasure.
It is **not** correction of two unknown blocks.

## C–E. Primitive gadgets and spatial fault bounds

### C1. Three-scan cat with local retry

Prepare m zeros, H on L0, then CX(L_j,L_(j+1)) for j=0..m-2.
For three complete scans, and in increasing j, prepare fresh w=0,
CX(L_j,w), CX(L_(j+1),w), MZ(w). Every reported flag must be zero.
If any is nonzero, finish/dispose this unused cat, consume one of the
two shared retry tokens, and repeat; a third failure rejects. No data
coupling has occurred yet. A retry retains the unknown data and adds
its actual idles to the same global fault budget.

At least one of the three scans is entirely fault free. If this attempt
is used, that scan's actual parities were all zero; it projects the cat
onto span{|0^m>,|1^m>}. Its phase may still be wrong or entangled with
an environment. After that scan no fanout remains. A later parity-gate
fault can add an X to at most one leaf; a verifier Z can propagate to
several leaves but changes only cat phase. Thus the used cat's bit
pattern is, modulo a simultaneous X on every leaf, supported on at most
k leaves for k actual later faults. Its coherent logical phase remains
arbitrary. No assumption of a stochastic Pauli mixture is involved.

The independent Clifford-only cat audit includes all Pauli faults on
each preparation, gate, meter and live-cat idle, then every pair of
merged signatures with zero combined flags. It confirms precisely this
bit bound for all nine cat sizes used by either factory. XOR is used
only in this Clifford preparation audit, never across T gates.

### C2. One leaf per physical port

For a product Q of disjoint one-qubit Hermitian Clifford involutions,
use a verified cat and one distinct leaf per physical target. X ports
use CX, Z ports H/CX/H, and W ports T^s/CX/T^-s. Measure every leaf
with H then MZ and report their XOR. In a clean gadget the data
projector is (I+(-1)^r Q)/2. Individual leaf results are retained in
the classical record; their product is the measured Q sign.

For a fixed full m-bit leaf word of parity r, its exact clean Kraus
operator is 2^((1-m)/2) Pi_r(Q), and its probability is
2^(1-m)||Pi_r(Q) psi||². The 2^(m-1) words of each parity sum to the
Born probability. The exact mixed-port audit checks every leaf word
on every input basis state for two three-port examples, including all
three physical verification scans and W-containing couplings.

For a faulty used cat or coupling, each conditional operation is a
linear combination of

\[
E\,(aI+bQ),
\]

or equivalently E times Q-eigenprojectors, allowing either eigenvalue
regardless of the reported bit. New data/graph support can be charged
to at most one physical target per coupling fault or surviving leaf
bit fault. A phase error changes a,b or the report; it does not spread
to additional data. This follows by expanding the cat's two coherent
branches and factoring the single-target gates, not by propagating
Paulis through a non-Clifford circuit as if it were Clifford.

An incoming target error can propagate to a leaf, but that leaf never
touches another target. Cat readout is transversal, with no inverse
fanout. Thus existing physical data support never spreads to other
data in these gadgets. The three-gate port audit retains the exact
cyclotomic coefficients for all 27 single basis faults and 234 pairs
of distinct local locations, for each sign, including control idles.
Its scope is that small port, not the full product-check gadget.

### C3. Known source and graph verification

The encoder may spread a raw fault arbitrarily across the twenty known
source qubits. Acquisition measures all twenty source generators and
applies the specified linear Pauli correction; this correction may
also have broad support if a report was wrong. Three all-zero complete
source-verification rounds follow. At a clean round their common
projector has rank one, exactly |++><++|. It removes all earlier
source error or rejects the attempt. Subsequent used-cat gadgets
contribute at most one physical source error per remaining fault.

**Graph verification uses only direct Z parities, without check cats.**
For every edge e=(u,v), prepare w in |0>, execute
CX(a_u,w), CX(A_e,w), CX(a_v,w), and measure w in Z. Scan all edges
in increasing order. Require three complete all-zero scans; stop at the
first nonzero scan, discard only the unused graph, and spend one shared
retry token. Every scan boundary and every idle of the retained data is
part of the global fault budget. No K_v measurement or graph correction
is performed in this preparation stage.

The E operators L_e=Z_(a_u) Z_(A_e) Z_(a_v) are independent, since each
contains its own edge bit. Their common positive projector Q_C has rank
2^5, with image

\[
\mathcal C=\operatorname{span}\{|t\rangle_a|dt\rangle_A:t\in\mathbb F_2^5\}.
\]

It does **not** project to the unique |R>. Among three accepted scans,
at least one whole scan is fault free under the global two-fault bound.
Fix the last such scan. Its actual all-zero outcomes put the graph in C,
with arbitrary amplitudes and environment correlations:

\[
|\chi\rangle=\sum_t |t,dt\rangle|c_t\rangle_{\rm env}.
\]

This removes any earlier broad *bit* error as an obstacle to the
normal form; it does not remove phase errors or make their amplitudes
uniform. The 32 vertex-Z characters acting on |R> are a complete
orthogonal basis of C, as checked by integer Walsh inner products.

**Why arbitrary graph phases are sufficient.** On each basis word,
V uses the four root-tree bits (dt)_(a,v)=t_a XOR t_v. Since all U_v
are commuting exact involutions,

\[
V\Omega\bigl(|t,dt\rangle|\psi\rangle\bigr)
=|t,dt\rangle U_a^{t_a}
 \prod_{v\ne a}U_v^{t_v\oplus(dt)_{a,v}}|\psi\rangle
=|t,dt\rangle U^{t_a}|\psi\rangle.
\]

Thus arbitrary coefficients |c_t> produce only I/U logical branches.
Vertex readout, including any conditioned report record, acts on the
graph coefficients. It cannot create another logical branch. The
initial inclusion in N_b used in F therefore holds with this rank-32
reference, rather than requiring the stronger rank-one |R> reference.
Subsequent combined code/cycle/Gauss rounds still certify the positive
magic line. Ideal probabilities in A remain unchanged: with no faults,
the preparation supplies the original uniform |R> exactly.

**Errors after the clean reference.** Every verification CNOT points
from a resource qubit into the meter. X on the meter does not propagate
to another resource; Z on it can spread Z to the remaining controls.
Expanding an arbitrary faulty location in its local Pauli basis shows
at most one new resource X/Y site per fault, multiplied by an arbitrary
resource Z operator. Prep/readout/report faults and boundary idles obey
the same bound. Resetting the meter prevents carryover to the next check.
The finite meter audit includes all participant Paulis, idles, and a
Pauli action together with a report flip at the same readout location.
It explicitly permits three-resource Z spread from one meter fault.

The arbitrary Z operator commutes with both Omega and V and remains a
graph/environment coefficient. Each resource bit-error site propagates
to at most one inner data block: a vertex controls its own block, a
root-tree edge controls its associated block, and another edge controls
none. Hence the b-fault normal form N_b and the later cut-readout bound
are preserved. The claim is not that the graph has only b arbitrary
single-site errors: its phase errors can have broad support.

Data idles during graph work add one physical data site per fault.
Failed graph preparations retry only this **known unused** resource;
each failure requires a fault in that attempt, so two shared tokens
suffice under the same global two-fault bound. Nothing resets an unknown
magic block. The independent certificates are generated by
`src/check_single_cz_graph_parity.py`; general arbitrary-fault composition
uses the analytical operator-span argument, not Pauli Monte Carlo.

### D. Enrichment and vertex measurement

After graph preparation there are no more vertex-to-edge resource
CNOTs. Vertex v controls only its four data sites. An arbitrary control
fault can affect the whole J_v, including a coherent sum of partial-W
operations, but cannot touch any other inner block. A data T or CNOT
fault has the same one-block bound. A vertex phase or wrong report
may change the apparent P_+ branch to P_-; no spatial argument alone
certifies the measured sector. We explicitly keep both branches in
the invariant until the clean gauged round.

### E. Coordinate passes, cycles, stars, and root Gauss

V has four distinct root-edge controls, each used only on its own
four-site block. Conjugating any local faulty location by the remaining
V gates can affect at most that one block and that root edge.
An error on a data target cannot generate an edge X: the ideal gates
are block diagonal in their edge control. It can generate edge Z and
coherent controlled Paulis; these are retained as graph coefficients.
Thus a data error cannot travel through an edge into another block.

Code and graph checks between the two V passes are the one-port cats
above. A single fault on a root-edge port maps, in V coordinates, to
that edge's one block; a nonroot-edge port adds no block. The root
Gauss check is measured **after** the second V, using ten leaves:
four separate W data ports on J_a and six separate edge-X ports.
In coordinates its ideal operator is U Xstar_a. A faulty edge port
maps to at most its one associated nonroot block; a faulty data port
stays in a. Its arbitrary cat phase supplies I or U times a graph
operator, not a new unbounded data fault.

Graph-star reports r_v are repaired by Z_(A_av)^r_v. These operations
commute with V and touch no data. A wrong report therefore changes
only graph phase. An arbitrary fault of the Z correction can also
flip that edge, and is charged to its one edge/one associated data
block in coordinates. No uncharged block is introduced. No X
correction is applied to a nonzero cycle or
data syndrome. Such a record rejects rather than risking an unknown
two-block logical ambiguity.

Consequently each actual fault after the known-source references adds
at most one inner block to the data support in the coordinate frame.
This remains a statement about operator spans and permits arbitrary
graph factors. Two faults may affect eight physical data qubits;
they are not silently identified with two physical-qubit errors.

## F. Conditional histories without a false commuting-projector assumption

A precise invariant behind the following expansion is

\[
\mathcal N_b=\operatorname{span}\{P_B U^r|\overline{++}\rangle
 \otimes|\gamma\rangle:\ r=0,1,\ |B|\le b\},\qquad b\le2,
\]

where P_B is any data Pauli supported in those inner blocks, and
|gamma> is an arbitrary graph/environment vector. Once we use the V
coordinate picture, ideal code projectors, graph operations, and
I/U combinations preserve N_b. Code projectors only select the
syndrome of P_B; U conjugates P_B without changing its support and
toggles r. The local gadget lemmas map a history with b faults to
N_b, increasing b only when an actual new faulty location occurs.
This remains true for non-Pauli faults because their complete
phase-sensitive operator expansions stay in this linear span.

For b<=2, the two-block detection lemma gives
Pi N_b contained in span{|++>,U|++>} tensor H_graph,env. The positive
U projector maps this last data span to its one-dimensional line
P_+|++>. This is the concrete finite-size substitute for importing
the old SWAP commuting-history theorem.

Fix the entire reported record and actual faulty locations. An arbitrary
quantum instrument has a Pauli-operator expansion on each local
participant set. Coefficients may be operators on an environment. For
T-containing gadgets expand the conditional operator, keeping all
complex coefficients. The spatial lemmas give, term by term, data
Paulis on a union B of at most one new inner block per actual fault.

In V coordinates every intervening ideal data operation is a code
stabilizer projector or I/U, with arbitrary graph operations. This
also holds for a faulty cat's logical-phase choice. The ideal initial
gauging map has only I and U branches after the coordinate change.
Physical U is a product of single-qubit Cliffords and normalizes the
entire original stabilizer group, with the signed action in A/B.
Therefore commute U powers through Pauli errors, and commute Pauli
errors through stabilizer projectors while updating their signs.
All remaining stabilizer projectors act on the known initial codespace.
They are either zero or scalar there. Each term at a complete code
projection thus has the form

\[
\Pi E_B (\alpha I+\beta U)|\overline{++}\rangle,
\qquad |B|\le2.
\]

The two-block detection lemma reduces this to a scalar combination of
|++> and U|++>. This reduction is valid with graph/environment-valued
coefficients. It is not an XOR composition of a Clifford audit.

Of the three complete gauged rounds, at least one has no faulty
location. In that round the bare Z checks first enforce Z=+1, then
the X checks enforce the code. Cycles enforce the cut sector; nonroot
stars and their actual Z repairs set all four star signs to +.
Root G_a is measured last with reported +, so its data action is P_+.
Since Pi commutes with U, the data at the end of that clean round are
exactly |CZ_magic>, factored from the graph/environment, or the
trajectory has zero amplitude and cannot be accepted.

This is the only clean-history fact needed. It does not assert that
root Gauss and X-decorated checks commute on arbitrary syndrome
sectors, or that three equal reported records identify a hidden clean
record. On faulty rounds the operator-span invariant handles their
actual ordered algebra. After this reference, all ideal stabilizer/U
operations stabilize the target, so subsequent faulty rounds leave
only block-supported errors acting on that target.

## G. Edge readout, decoding, and physical byproducts

After the graph's clean cut-subspace reference, each fault adds at most one
non-cut edge bit. All ideal edge-X operations in a check or Gauss
projector are whole stars, hence cuts. V is diagonal in edge Z;
cycles and graph phase repairs do not change computational bits.
Thus each operator term at edge readout has a cut word plus at most
two bit flips, counting wrong final reports in the same bound.

The 13-bit cut code has distance five. Every record within radius two
of a cut has exactly one such cut. All 8192 records are explicitly
classified; 1472 accept, 6720 reject. This includes every cut plus
every zero/one/two-report-flip pattern. No single tree report is used
without the full cut decoder.

For a fixed record the decoded root-zero eta identifies the underlying
cut in every compatible low-fault operator term. Contracting with the
edge basis and applying U_eta removes the ideal byproduct. An edge-X
component on a root edge changes V only by U_v on that same block;
this is the block already charged to that edge fault, not a second
unaccounted block. Nonroot-edge flips introduce no additional data
block. Both coherent branches and wrong reports obey the bound.

Implement U_eta using S^s then X on each chosen site. This is
e^(i*pi*sum_selected(s)/4) times the normalized U_eta, a known global
phase of the **fixed classical record**. It is never discarded inside
a controlled gate. On whole selected blocks the phase is
(-1)^(eta_c+eta_d). Its inverse is the same sign. Faults on these
individual single-qubit corrections add one physical error each.

Therefore the terminal stage begins with errors on at most two inner
blocks multiplying the intended positive magic resource. No global
negative branch can survive a clean gauged certificate and then
become an undetectable logical branch through only these block errors.

## H. Terminal recovery and late faults

The following is the original full terminal reference. The opt-in
[ordered terminal replacement](single_block_cz_terminal_screen.md) proves
that one outer-then-inner screen suffices on its all-zero path, using the
upstream block envelope and an exhaustive terminal fault certificate.
Its nonzero paths retain certified recovery; this is not a deletion of
two records from the ordering below.

There are exactly three complete terminal rounds, each measuring the
eighteen original code stabilizers with one leaf per physical site.
All reported syndrome bits must be zero. **Neither source logical X
is measured again**, and there is no terminal magic-reset operation.
No global direct-cat U measurement is needed on the gauging route.

At least one terminal round is clean. At its complete projector Pi,
the inherited error has support in at most two inner blocks, including
any earlier terminal faults and all preceding correction gates. The
detection lemma removes it or rejects it; the surviving data state is
exactly the positive magic state. At no point was an unknown-two-block
correction chosen from an ambiguous syndrome.

After the **last clean terminal round**, no V pass, graph interaction,
or shared controller remains. All used cats have the physical one-port
bound. All ideal measured stabilizers stabilize the target. Commuting
their projectors past residual Paulis changes signs, not support.
Every subsequent faulty location, including the final boundary idles,
adds at most one physical data position. Hence the accepted output
lies in E_2|CZ_magic>. Error-correcting recovery exists for this whole
span, not merely for each sampled Pauli separately. This proves the
stated decoded guarantee without assuming faults stop at the final
clean report.

## I. Negative sector and rejection

With no faults P_-|++>=|11>/2. It is a stabilizer branch, rejected by
the odd vertex parity. If a faulty report falsely declares that parity
positive, a clean gauged round still enforces the actual positive
sector. The preceding code projection and two-block lemma restrict the
logical state to span{|++>,U|++>}; its positive component is uniquely
the desired three-term resource. A genuinely pure negative component
has zero accepted amplitude. Once a clean positive reference exists,
later allowed errors are removed by the terminal code projection or
are correctable residual errors. Repeating a measurement is never
used to change a genuine negative eigenvalue into positive.

There is an explicit reason to reject nonzero data syndromes instead
of automatically correcting them: X_(2,3) and X_(8,11,12,15) have the
same syndrome. They occupy one and two inner blocks respectively;
their difference is Xbar0. Any purported decoder correcting both
unknown alternatives necessarily makes a logical mistake. The
conservative zero-syndrome rule has a complete certificate: the only
two-block zero-syndrome class is the stabilizer class.

## J. Composition, baseline, and scope of validation

Compose C3, D/E, F, G and H with the same two-fault budget. The first
references remove broad known-resource encoder faults; the spatial
invariant limits subsequent damage to two inner blocks; a clean
gauged round certifies the logical resource; complete cut decoding
restores its original-code frame; a clean terminal round removes
the inherited block errors; all later faults leave a correctable
physical residual. This establishes the theorem.

The direct-cat comparator uses the identical source, gate alphabet,
three-scan cats, retry rules and terminal all-zero code tests. It has
three rounds of eighteen code checks followed by a twenty-port U cat;
the first clean complete round both produces and certifies P_+|++>.
Source residuals and all comparator faults are physical-site local,
so the same normal-form/reference argument proves the same theorem,
with no graph or block-controller lemma required. It is our explicit
reconstruction, not a published cost measurement.

The saved checks establish: ranks and signed source amplitudes;
all 2048 native/canonical phase strings; 655360 two-block Paulis;
the complete physical-radius-two correction table up to stabilizers;
all graph cuts, cycle rank, expansion and 8192 decoding decisions;
the rank-32 graph cut subspace, 1024 Walsh inner products on each graph,
all 96 local Pauli/report meter cases (32 merged signatures and 1024
signature pairs), and emitted direct-parity graph schedules;
all 512 ideal records and 65536 physical monomial/byproduct tests;
all local Clifford cat signature pairs with accepted flags;
and exact cyclotomic controlled-W identities/port expansions.

The general arbitrary-fault composition is the analytical argument
above. It is not claimed as an executable whole-factory fault-pair
certificate, nor as a noisy simulator. No conjectural central lemma,
unverified adaptive stopping rule, or Pauli-noise-only extrapolation
is needed by this conservative version. T noise, memory noise and
faults on every correction are part of the theorem's location model;
their stochastic rates are exposed in the separate simulator. Finite
noise pilots do not establish the theorem or a graph-yield advantage.
