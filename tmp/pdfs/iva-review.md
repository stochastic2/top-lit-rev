## Section IV.A: non-Abelian fractons from gauging transversal \(\mathsf{CZ}\) gates

The SWAP example established the graph-gauging mechanism in its most
universal form.  This example is more directly connected to quantum
computation: it gauges a transversal \(\mathsf{CZ}\), the logical Clifford
operator whose measurement will later prepare a magic state.  It also lets us follow the construction on a concrete three-dimensional
lattice.

There are two things to keep distinct from the outset.  The **ALP code** is
an Abelian CSS code with fracton/subsystem structure.  The construction then
takes two copies of that code and gauges a symmetry between the copies.  The
gauged code is the non-Abelian object.  In this first pass we will follow the
graph construction through its local circuit and its resulting constraints.
The later subsections on addressable gates and cup products are deliberately
postponed: they answer how to gauge a family of \(\mathsf{CZ}\) gates, not
what the basic \(\mathsf{CZ}\)-gauging mechanism is.

### The unusual qubit placement in the ALP code

The anisotropic lineon-planeon (ALP) model lives on a periodic cubic lattice.
Its CSS chain complex is

\[
0\longrightarrow D_2\xrightarrow{\partial_2}D_1
\xrightarrow{\partial_1}D_0\longrightarrow0.
\tag{169}
\]

The word *anisotropic* is literal: the three spatial directions are not
treated alike.  The bases have the following geometric interpretation:

\[
\begin{array}{c|c|c}
\text{space}&\text{basis object}&\text{role}\\
\hline
D_2&\text{cubes }c&Z\text{-check labels}\\
D_1&\text{plaquettes in }xy\text{ planes and edges parallel to }z&\text{physical qubits}\\
D_0&\text{vertices }v&X\text{-check labels}.
\end{array}
\tag{170}
\]

The middle line is the surprise.  A horizontal \(xy\) *plaquette* carries a
qubit, whereas a vertical \(z\) *edge* carries a qubit.  There are no qubits
on horizontal edges.  This is why the ALP stabilizers do not look like the
usual cubic-lattice toric-code stabilizers.

The drawings below are reproduced directly from the paper's TikZ source,
with the geometry unchanged. The left drawing gives a cube \(Z\)-check;
the right drawing gives a vertex \(X\)-check. A letter marks a qubit on
which that Pauli acts. In particular, a letter inside a horizontal face
means a **face qubit**, not a qubit at a hidden vertex.

![ALP cube Z check (left) and vertex X check (right), reproduced from the paper.](figures/alp-paper/checks.png){width=70%}

*Source: Section IV.A, equation labelled `eq:qubit-ALP-stabilizers` in the
paper's source. Each check acts on six qubits.*

To make these perspective drawings unambiguous, label a vertex by integer
coordinates \((i,j,k)\). Write \(p_{i,j,k}\) for the horizontal square
with corners \((i,j,k),(i+1,j,k),(i,j+1,k),(i+1,j+1,k)\), and
\(\ell_{i,j,k}\) for the vertical edge from \((i,j,k)\) to
\((i,j,k+1)\). Coordinates are understood periodically. The cube
\(c_{i,j,k}\) then has the following check:

\[
B_{i,j,k}=
Z_{p_{i,j,k}}Z_{p_{i,j,k+1}}
\prod_{\alpha,\beta\in\{0,1\}}Z_{\ell_{i+\alpha,j+\beta,k}}.
\]

The two face factors sit on the bottom and top; the other four factors sit
on the upright edges. At a vertex, the check is instead

\[
A_{i,j,k}=
X_{\ell_{i,j,k-1}}X_{\ell_{i,j,k}}
\prod_{\alpha,\beta\in\{0,1\}}X_{p_{i-\alpha,j-\beta,k}}.
\]

Here the two edge factors are below and above the vertex, and the four
horizontal squares meet at that vertex. These formulas specify every qubit
in the drawings without requiring the reader to reconstruct depth from a
flat image.

The chain maps encode exactly these incidences. The map \(\partial_2\)
sends a cube to the sum of its two horizontal faces and four vertical
edges. The map \(\partial_1\) sends a face qubit to its four corner
vertices, and an edge qubit to its two endpoints. This is a **code chain
complex**: its degree records a qubit's role in the checks, not necessarily
the spatial dimension of the object carrying it. Both kinds of qubit belong
to \(D_1\), even though a square is geometrically two-dimensional.

For example, applying \(\partial_1\partial_2\) to a cube counts each of
its eight corners twice: once from a horizontal face, once from a vertical
edge. Over \(\mathbb F_2\), these contributions cancel. Equivalently, an
incident vertex check and that cube check share two qubits, so commuting
them produces \((-1)^2=+1\). This is the concrete content of the
chain-complex condition in this model.

In the paper's compact notation, the two stabilizer families are therefore

\[
A_v=X_{d_0\boldsymbol v},\qquad B_c=Z_{\partial_2[c]}.
\tag{171}
\]

The chain-complex condition \(\partial_1\partial_2=0\), or dually
\(d_1d_0=0\), guarantees that each \(A_v\) and \(B_c\) overlap on an even
number of qubits and hence commute.  This establishes that the checks define a CSS code. Gauging will additionally
require a symmetry preserving that code, which we verify below.

An excitation is a check with eigenvalue \(-1\), rather than the ground-state
value \(+1\). Restricted mobility means that transporting an isolated
excitation in some directions requires creating additional excitations.
A *lineon* can move along a line; a *planeon* can move within a plane. For a
concrete first example, \(Z_{\ell_{i,j,k}}\) anticommutes with the vertex
checks at the two ends of that edge. A product of \(Z\)'s along a vertical
segment leaves defects only at its endpoints, because the interior signs
flip twice. In contrast, \(Z_{p_{i,j,k}}\) creates four vertex defects at
that square's corners. This already shows why vertical and horizontal
operations have different effects. The broader term *fracton order*
includes systems with such restricted-mobility excitations; it does not
mean that every excitation is completely immobile.

Here each check has weight six, and each qubit occurs in a bounded number
of checks, independently of lattice size. That is the low-density condition
in qLDPC. “Subsystem” in the discussion of spatial symmetries should not be
confused with a subsystem error-correcting code with noncommuting gauge
checks: the starting ALP code is a commuting CSS stabilizer code.

For an \(L_x\times L_y\times L_z\) periodic lattice, the paper reports
\(2(L_x+L_y-1)\) logical qubits and distance scaling as
\(\min(L_x,L_y,L_z)\).  This is a useful reminder that it is a subsystem-like
3D code rather than a conventional topological code with a constant number
of logical qubits.

### The transversal \(\mathsf{CZ}\) symmetry between two copies

The next step is to identify a gate that preserves the two input code
spaces. This matters because gauging an arbitrary collection of physical
gates would not automatically produce a logical-symmetry measurement.

Make two identical ALP blocks, named \(B\) and \(C\). In the paper's
original drawing, blue dots belong to \(B\), orange dots to \(C\), and
black segments specify the \(\mathsf{CZ}\) pairs. Repeat the displayed
pattern in every cubic cell.

![Original ALP transversal CZ pairing from Section IV.A of the paper.](figures/alp-paper/cz-pairing.png){width=27%}

*Source: the paper's equation labelled `eq:cubic-CZ-sym`. Colours distinguish
code blocks, not face qubits from edge qubits.*

Writing \(\mathcal P\) for this matching gives

\[
U_{\mathsf{CZ}}=
\prod_{(e,e')\in\mathcal P}\mathsf{CZ}_{B_e,C_{e'}}.
\tag{172}
\]

In this transversal matching, each physical qubit participates in exactly
one two-qubit gate between blocks. Merely having a bounded number of gates
per qubit would describe a bounded-depth circuit, a weaker condition.  The paired
qubits need not be drawn directly on top of one another: the pairing is a
local matching determined by the cubic unit cell.  This is a point at which
the paper's 3D perspective matters more than an attempted planar picture.

The elementary conjugation rules are

\[
\mathsf{CZ}_{B,C}X_B\mathsf{CZ}_{B,C}=X_BZ_C,
\qquad
\mathsf{CZ}_{B,C}X_C\mathsf{CZ}_{B,C}=Z_BX_C,
\tag{173}
\]

while both \(Z_B\) and \(Z_C\) are unchanged.  The chosen pairing makes the
extra \(Z\) factors fit the ALP check structure. The code-preserving
property concerns the complete gate: a *single physical* \(X_e\), \(Z_e\), or
\(\mathsf{CZ}_{B_e,C_{e'}}\) is generally **not** a symmetry of the code.
For example, a lone \(Z_e\) anticommutes with the \(X\)-checks incident on
that qubit and creates syndrome defects.  Equation (173) is only a local
operator identity; it does not say that its individual factors preserve
check eigenvalues.

The coordinate convention above makes it possible to check the symmetry
explicitly. In cell \((i,j,k)\), the two pairs in the drawing are

\[
(C_{p_{i,j,k}},B_{\ell_{i+1,j+1,k}}),\qquad
(C_{\ell_{i,j,k}},B_{p_{i,j,k+1}}).
\]

Consider the entire \(B\)-vertex check at \((i,j,k)\). Its two vertical
edge qubits acquire \(C\)-block \(Z\)'s on the horizontal faces
\(p_{i-1,j-1,k-1}\) and \(p_{i-1,j-1,k}\). Its four face qubits acquire
\(Z\)'s on the four vertical edges of the same cube. The six new factors
are therefore **exactly one complete cube check**:

\[
\begin{aligned}
U_{\mathsf{CZ}}A^B_{i,j,k}U_{\mathsf{CZ}}^\dagger
 &= A^B_{i,j,k}B^C_{i-1,j-1,k-1},\\
U_{\mathsf{CZ}}A^C_{i,j,k}U_{\mathsf{CZ}}^\dagger
 &= B^B_{i,j,k}A^C_{i,j,k}.
\end{aligned}
\tag{174}
\]

For the second identity, the two \(C\)-edge qubits attach \(Z\)'s to the
bottom and top \(B\)-faces of \(c_{i,j,k}\); the four \(C\)-face qubits
attach them to its four upright \(B\)-edges. This verifies both directions
of the matching. The mechanism is the assembly of complete checks, rather
than a claim that each physical \(X\) or each elementary gate preserves
the code separately. For products of checks, repeated Pauli factors cancel
modulo two in the usual way.

On a code state, both factors on either right-hand side have eigenvalue
\(+1\). Thus the transformed check still fixes the state: the transversal
gate maps the stabilizer group to itself. It can change the encoded logical
state while keeping the physical state inside the codespace.

The \(Z\)-checks themselves do not acquire anything, because
\(\mathsf{CZ}\) is diagonal:

\[
U_{\mathsf{CZ}}B^B_cU_{\mathsf{CZ}}^\dagger=B^B_c,
\qquad
U_{\mathsf{CZ}}B^C_cU_{\mathsf{CZ}}^\dagger=B^C_c.
\tag{175}
\]

In binary language, the test for a proposed matching is that its added
\(Z\) support be
in \(\operatorname{im}\partial_2\) for every \(X\)-check support in
\(\operatorname{im}d_0\).

### The cubic ancilla graph and the controlled-\(\mathsf{CZ}\) enrichment

Having verified the matter symmetry, we now introduce the ancillary
system that will turn its global action into local gauge constraints.  Put temporary qubits
\(a_v\) on every cubic-lattice vertex and gauge-field qubits \(A_f\) on every
cubic-lattice edge \(f=\langle v,w\rangle\).  After making the graph cluster
state (the paper applies a Hadamard to the \(A\) sublattice), its convenient
stabilizer generators are

\[
K^a_v=X^a_v\prod_{f\ni v}X^A_f,
\qquad
K^A_f=Z^A_fZ^a_vZ^a_w.
\tag{176}
\]

Because the cubic graph is connected, the temporary vertices possess exactly
one global \(X\) symmetry,

\[
X^a_{\rm all}=\prod_vX^a_v.
\tag{177}
\]

The enrichment must tie this single symmetry to Eq. (172).  It uses
\(\mathsf{CCZ}\), the three-qubit controlled-controlled-Z gate.  Its action
is diagonal in the computational basis:

\[
\mathsf{CCZ}_{a,B,C}|r,b,c\rangle
=(-1)^{rbc}|r,b,c\rangle.
\tag{178}
\]

Thus when the temporary control is \(|0\rangle_a\), it does nothing;
when it is \(|1\rangle_a\), it applies \(\mathsf{CZ}\) to the selected
\(B,C\) pair. The paper's original enrichment drawing shows exactly which
two pairs are controlled by the purple vertex:

![Original ALP CCZ enrichment: two green paths connect the purple control to the two matter pairs.](figures/alp-paper/ccz-enrichment.png){width=27%}

*Source: the paper's equation labelled `eq:cubic-symm-enrich`. Each shade
of green denotes one three-qubit gate, not two successive two-qubit gates.*

At \(a_{i,j,k}\), these are the two pairs listed above: the lower
\(C\)-face with the far \(B\)-edge, and the near \(C\)-edge with the upper
\(B\)-face. There are exactly two \(\mathsf{CCZ}\)'s per control in this
pattern. This assignment is repeated at every vertex.

The paper denotes this local assignment by \(\phi^{\mathsf T}(v)\).  In this
example \(\phi^{\mathsf T}(v)\) is a set of **pairs** \((e,e')\), not merely
a set of single qubits as in the SWAP example.  In a basis-independent form,
the enrichment circuit is

\[
\Omega=
\prod_v\ \prod_{(e,e')\in\phi^{\mathsf T}(v)}
\mathsf{CCZ}_{a_v,B_e,C_{e'}}.
\tag{179}
\]

The map must be local and surjective in the paper's sense: every required
physical \(\mathsf{CZ}\) in \(U_{\mathsf{CZ}}\) is assigned to an odd number
of controls, preferably exactly one, and each control reaches only \(O(1)\)
nearby pairs.  This is the \(\mathsf{CZ}\) version of the sparse assignment
\(e\mapsto\phi(e)\) in the SWAP construction.

To see the symmetry enrichment explicitly, use the one-gate identity

\[
X_a\,\mathsf{CCZ}_{a,B,C}\,X_a\,\mathsf{CCZ}_{a,B,C}
=\mathsf{CZ}_{B,C}.
\tag{180}
\]

It follows just by checking \(a=0,1\): flipping the control interchanges
the “apply \(\mathsf{CZ}\)” and “do nothing” branches.  Multiply Eq. (180)
over all temporary vertices and their assigned pairs.  The odd-assignment
condition then gives

\[
X^a_{\rm all}\Omega X^a_{\rm all}\Omega^\dagger
=U_{\mathsf{CZ}}.
\tag{181}
\]

This is the same group-commutator test used for graph-gauged SWAP, with controlled swaps
replaced by controlled \(\mathsf{CZ}\) gates.  It is the one equation that
shows the cubic ancilla is gauging the desired logical symmetry rather than
merely adding extra qubits.

### Gauge constraints, matter checks and commuting projectors

Measure every temporary \(a_v\) qubit in the \(X\) basis.  For the moment,
consider the all-\(+1\) branch; the next subsection of this note explains how a
decoder and feedforward correct the actual random signs.  From Eq. (176),
the temporary-vertex stabilizer becomes the surviving gauge constraint

\[
\widetilde K^A_v=
\left(\prod_{f\ni v}X^A_f\right)
\left(\prod_{(e,e')\in\phi^{\mathsf T}(v)}
\mathsf{CZ}_{B_e,C_{e'}}\right).
\tag{182}
\]

The first factor is an ordinary \(X\)-type gauge
transformation on the six edges incident to a cubic vertex.  The second
factor simultaneously performs the local piece of the original
\(B\)-\(C\) symmetry.  This is the concrete form of the slogan “a gauge
transformation carries the old symmetry.”

The matter checks become dressed as well.  The useful one-qubit identity is

\[
\mathsf{CCZ}_{a,B,C}X_B\mathsf{CCZ}_{a,B,C}
=X_B\mathsf{CZ}_{a,C},
\tag{183}
\]

and the analogous equation holds with \(B\) and \(C\) exchanged.  Therefore
each \(X\)-type ALP check picks up controlled-Z factors involving temporary
ancillas.  Before measurement, those factors can be traded, using products
of the edge relations \(K^A_f\), for operators on paths of surviving
\(A\)-edge qubits - the path-replacement mechanism developed in the graph-gauged SWAP example.  The original ALP \(Z\)-checks themselves remain unchanged, since
\(\mathsf{CCZ}\) is diagonal and they act only on matter qubits. Products
of \(K^A_f\) around a closed ancilla loop also survive: every temporary
\(Z^a_v\) occurs twice, leaving only the loop product of \(Z^A_f\).
On the cubic lattice the elementary examples are the four-edge plaquette
flux checks. The complicated dressing belongs to the matter \(X\)-checks
and the combined gauge constraints; it should not obscure these simple
unchanged \(Z\)-type operators.

This explains why the paper presents the final stabilizers mainly as 3D
figures rather than as a short one-line formula.  Three distinct incidence
structures must be superimposed: the six-qubit ALP checks, the cubic ancilla
graph, and the local \(B\)-\(C\) pair assignment.  The final operators are
local, but “local” now means local in that combined three-layer incidence
structure, not local in a single planar projection.

There is a second subtlety.  The raw dressed generators can commute only
**up to** the gauged \(U_{\mathsf{CZ}}\) symmetry.  To define a Hamiltonian
with mutually commuting projectors, the paper symmetrizes them with respect
to that \(\mathbb Z_2\) action.  Commutation on the constrained codespace is weaker than commutation as
operators on the entire Hilbert space; a commuting-projector Hamiltonian
requires the latter.  A bare matter-check label
can be changed by the gauge transformation, so the gauge-invariant term must
include both members of its symmetry orbit.

For a concrete illustration of an orbit, the transversal symmetry above
sends \(A_v^B\) to \(A_v^B B_c^C\) and back again, while fixing
\(B_c^C\). Here an *orbit* simply means the set of operators obtained by
repeatedly applying the symmetry. The simultaneous positive-eigenvalue
projector

\[
Q=\frac{I+A_v^B}{2}\frac{I+B_c^C}{2}
\]

is invariant under this exchange: replacing \(A_v^B\) by
\(A_v^B B_c^C\) leaves \(Q\) unchanged, because
\(B_c^C(I+B_c^C)=I+B_c^C\). The condition \(B_c^C=+1\) makes the two
representatives of the vertex check equivalent. This elementary example
explains why imposing the relevant constraints can turn a symmetry orbit
into one well-defined projector. For the gauged operators one must also
include the gauge constraints; the paper's appendix on graph-gauged ALP fractons carries out the
local dressing calculation. Simply averaging two arbitrary operators is
not, by itself, a proof that the result is a projector or that different
terms commute.

### From the ALP construction to logical measurement

The SWAP example taught the general graph procedure.  This ALP example adds
the specific ingredient needed later for computation:

\[
\text{temporary control}\quad+\quad\mathsf{CCZ}
\quad\Longrightarrow\quad
\text{gauged transversal logical }\mathsf{CZ}.
\tag{184}
\]

The later ungauging protocol reverses the ancilla construction and measures
the gauge qubits.  Equation (181) then reappears as a projector onto an
eigenvalue of the logical \(\mathsf{CZ}\) acting on the original \(B,C\)
blocks.  On appropriate logical input states, that Clifford measurement
prepares a non-stabilizer state.  Thus the CCZ gates used here are not being
claimed as directly applied logical non-Clifford gates; rather, they are the
local measurement gadget from which a non-Clifford *resource state* emerges
after gauging and ungauging.

The construction therefore connects four ingredients:

1. The ALP code has qubits on \(xy\) plaquettes and \(z\) edges, giving
   six-qubit cube and vertex checks.
2. Two copies possess a local transversal \(\mathsf{CZ}\) matching.
3. A cubic graph cluster state plus local \(\mathsf{CCZ}\) enrichment
   satisfies the global commutator identity (181).
4. Measuring the temporary ancillas turns this into a non-Abelian gauge
constraint (182); ungauging later converts the same construction into a
   logical \(\mathsf{CZ}\) measurement.

## Returning to Section III.E: measurement preparation of non-Abelian qLDPC codes

Before using the ALP construction for computation, we return to the
measurement-preparation argument of Section III.E. It supplies the missing
operational step in the example: handling random measurement signs.
The gauging discussion has used an idealized instruction:
“project every temporary ancilla \(a_v\) onto \(|+\rangle\).”  A physical
\(X\)-basis measurement cannot promise that outcome.  It returns a random
number

\[
x_v\in\{+1,-1\},
\qquad
X^a_v\longmapsto x_v.
\tag{185}
\]

This section explains why that randomness does not turn gauging into a
postselected protocol.  For preparation from the symmetry-invariant input sector, and assuming
that the Abelian code on the ancilla complex has a decoder, the random
local signs can be removed deterministically by a Pauli correction on the
surviving \(A\) qubits.  The word *deterministic*
means that every possible measurement record is accepted and corrected; it
does not mean that individual measurement outcomes cease to be random.

### First ignore the matter codes: measuring a graph cluster state

It is useful to strip the problem to its simplest form.  Before the
measurement, the temporary-vertex graph-cluster stabilizer is

\[
K^a_v=X^a_vX^A_{d^a_0\boldsymbol v}.
\tag{186}
\]

For an ordinary graph, \(X^A_{d^a_0\boldsymbol v}\) is the product of \(X\)
on all \(A\)-edge qubits incident to vertex \(v\).  Since \(K^a_v=+1\) on
the cluster state, measuring \(X^a_v=x_v\) leaves the surviving \(A\) qubits
with the signed check

\[
x_vX^A_{d^a_0\boldsymbol v}=+1.
\tag{187}
\]

The usual \(Z\)-type ancilla checks, labelled schematically by
\(Z^A_{\partial_2[p]}\), are unaffected.  Thus the only difference between
the desired Abelian ancilla code and the actually prepared one is the list
of signs \(\{x_v\}\) in Eq. (187).

Turn these signs into a binary syndrome vector,

\[
s=\sum_v s_v[v]\in A_0,
\qquad
s_v=\begin{cases}
0,&x_v=+1,\\
1,&x_v=-1.
\end{cases}
\tag{188}
\]

**Why are there an even number of \(-1\) outcomes in the clean target
sector?**  Multiply every premeasurement vertex stabilizer in Eq. (186).
Each \(A\)-edge occurs at the two ends of that edge, so its two factors
cancel:

\[
\prod_vK^a_v
=\left(\prod_vX^a_v\right)
 \left(\prod_{f\in A_1}(X^A_f)^2\right)
=\prod_vX^a_v
=X^a_{\rm all}.
\tag{189}
\]

All the \(K^a_v\)'s have eigenvalue \(+1\), hence the cluster state has
\(X^a_{\rm all}=+1\).  The individual \(X^a_v\) measurements commute, so
their outcomes must obey

\[
\prod_vx_v=+1.
\tag{190}
\]

A product of signs is \(+1\) precisely when an even number of its factors
are negative.  For three temporary qubits, for example, \((+,+,+)\) and
\((+,-,-)\) are allowed, whereas \((-,+,+)\) is not.  After symmetry
enrichment the corresponding global relation is
\(X^a_{\rm all}U=+1\).  In the clean target-preparation sector, the input
matter state has \(U=+1\), so the same even-parity conclusion follows.  An
odd parity would instead record the opposite global symmetry sector, not an
ordinary local syndrome that an \(A\)-edge correction can erase.

This is exactly the familiar CSS situation: a \(-1\) outcome says that the
corresponding \(X\)-check has the wrong sign.  On a 2D surface-code graph,
one would draw the \(-1\) vertices and connect them pairwise by a path of
edges.  In a general qLDPC complex there may be no literal picture, but the
same binary linear-algebra question remains: find a 1-chain

\[
r\in A_1
\quad\text{such that}\quad
\partial^a_1 r=s.
\tag{191}
\]

For ideal measurements, finding any such chain suffices to correct these
signs. In error correction with physical noise, a decoder uses a noise
model to seek a likely error representative; choosing the logical class
then also matters.  It is not necessary for this discussion to
know how that algorithm works internally.

The corresponding quantum correction is the Pauli product

\[
Z^A_r:=\prod_{f\in A_1}(Z^A_f)^{r(f)}.
\tag{192}
\]

Why does it fix the signs?  A factor \(Z^A_f\) anticommutes with an
\(X\)-check precisely when edge \(f\) occurs in that check.  Therefore

\[
Z^A_rX^A_{d^a_0\boldsymbol v}Z^A_r
=(-1)^{\boldsymbol v(\partial^a_1r)}X^A_{d^a_0\boldsymbol v}
=(-1)^{s_v}X^A_{d^a_0\boldsymbol v}.
\tag{193}
\]

Because \(x_v=(-1)^{s_v}\), conjugating Eq. (187) by \(Z^A_r\) changes it
to the desired \(+X^A_{d^a_0\boldsymbol v}=+1\) check.  The correction
commutes with all \(Z\)-type ancilla checks, since it consists only of
\(Z\)'s.  This is the full deterministic-preparation argument for the
Abelian ancilla code.

**Worked nearest-neighbour example: two \(-1\) outcomes.**

Take two neighbouring vertices \(v\) and \(w\) of the cubic ancilla graph,
joined by one surviving \(A\)-edge \(f=\langle v,w\rangle\).  Suppose that
the two temporary measurements give \(x_v=x_w=-1\), while every other
temporary measurement gives \(+1\).  This is the smallest nontrivial
syndrome compatible with a closed, periodic graph:

\[
s=[v]+[w]=\partial^a_1[f].
\tag{194}
\]

The decoder can therefore choose the shortest possible correction chain,
\(r=[f]\).  Its quantum correction contains just **one** single-qubit
Pauli:

\[
Z^A_r=Z^A_f.
\tag{195}
\]

\begin{center}
\begin{tikzpicture}[every node/.style={font=\small}, >=Latex]
  \node[draw,circle,fill=purple!10,minimum size=0.9cm] (v) at (0,0) {\(v\)};
  \node[draw,circle,fill=purple!10,minimum size=0.9cm] (w) at (5.0,0) {\(w\)};
  \draw[very thick,red!70!black] (v)--node[above,black] {\(f\)}(w);
  \node[above=0.55cm of v] {\(x_v=-1\)};
  \node[above=0.55cm of w] {\(x_w=-1\)};
  \node[below=0.55cm of v] {wrong sign at \(v\)};
  \node[below=0.55cm of w] {wrong sign at \(w\)};
  \node[below=1.35cm of $(v)!0.5!(w)$,align=center] {apply \(Z^A_f\): the one selected edge has\\exactly the two defective vertices as endpoints};
\end{tikzpicture}
\end{center}

The two signed checks before correction are

\[
-X^A_{d^a_0\boldsymbol v}=+1,
\qquad
-X^A_{d^a_0\boldsymbol w}=+1.
\tag{196}
\]

Edge \(f\) occurs once in each of the two vertex checks.  Hence

\[
Z^A_fX^A_{d^a_0\boldsymbol v}Z^A_f
=-X^A_{d^a_0\boldsymbol v},
\qquad
Z^A_fX^A_{d^a_0\boldsymbol w}Z^A_f
=-X^A_{d^a_0\boldsymbol w}.
\tag{197}
\]

The correction flips both minus signs to plus signs at once.  At every other
vertex \(u\), the edge \(f\) does not occur in \(d^a_0\boldsymbol u\), so
the \(u\)-check is unchanged.  In the gauged code, exactly the same
calculation applies to
\(-X^A_{d^a_0\boldsymbol v}\mathcal U_v\) and
\(-X^A_{d^a_0\boldsymbol w}\mathcal U_w\), because \(Z^A_f\) commutes with
the matter dressing \(\mathcal U\).  This is the most concrete example of
the general rule \(\partial^a_1r=s\).

\begin{center}
\begin{tikzpicture}[node distance=0.75cm and 0.75cm, every node/.style={font=\small}, >=Latex]
  \node[draw,rounded corners,fill=purple!10,align=center,minimum width=2.25cm,minimum height=0.85cm] (m)
    {measure all \(X^a_v\)\\record \(x_v=\pm1\)};
  \node[draw,rounded corners,fill=orange!12,align=center,right=of m,minimum width=2.25cm,minimum height=0.85cm] (s)
    {syndrome \(s_v=(1-x_v)/2\)};
  \node[draw,rounded corners,fill=blue!10,align=center,right=of s,minimum width=2.25cm,minimum height=0.85cm] (d)
    {classical decoder finds\\\(r\) with \(\partial_1^ar=s\)};
  \node[draw,rounded corners,fill=green!10,align=center,right=of d,minimum width=2.25cm,minimum height=0.85cm] (c)
    {apply or track \(Z_r^A\)\\all \(X\)-check signs become \(+1\)};
  \draw[->,thick] (m)--(s); \draw[->,thick] (s)--(d); \draw[->,thick] (d)--(c);
\end{tikzpicture}
\end{center}

### Why exactly the same decoder works after gauging

Now restore the matter blocks \(B,C\) and the enrichment circuit.  After
the \(X_a\) measurements, the gauged vertex constraint has the general
form

\[
\mathcal G_v[x_v]
=x_vX^A_{d^a_0\boldsymbol v}\,\mathcal U_v.
\tag{198}
\]

The factor \(\mathcal U_v\) is the local piece of the old transversal
symmetry.  In the SWAP example it is a product of
\(\mathsf{SWAP}_{B_e,C_e}\)'s; in the ALP \(\mathsf{CZ}\) example it is a
product of \(\mathsf{CZ}_{B_e,C_{e'}}\)'s.  Crucially, the random outcome
\(x_v\) occurs in exactly the same place as it did in Eq. (187): it merely
multiplies the \(X^A\) factor by a sign.

The correction \(Z^A_r\) has two equally important properties:

1. By Eq. (193), it flips precisely the unwanted signs in
   \(\mathcal G_v[x_v]\).
2. It commutes with \(\mathcal U_v\), because \(Z^A_r\) acts on the
   surviving gauge qubits whereas \(\mathcal U_v\) acts on \(B,C\).  It also
   commutes with the other \(Z\)-type and matter constraints.

Hence the same correction selected by the *Abelian* ancilla decoder turns

\[
\mathcal G_v[x_v]\quad\longmapsto\quad
\mathcal G_v[+1]
\tag{199}
\]

without changing the non-Abelian matter dressing.  This is the central
observation of the paper's subsection.  Measurement randomness creates only
an Abelian syndrome, even though the final code has non-Abelian structure.

### What “feedforward” means here

The decoder may be a nonlocal classical computation: it reads the full list
of outcomes before deciding on \(r\).  But once \(r\) is known, every factor
of \(Z^A_r\) is a one-qubit Pauli.  They can all be performed in one quantum
layer.  Often one does not physically apply them at all.  One instead stores
the binary vector \(r\) as a **Pauli frame** and flips the interpretation of
later measurements accordingly.

This is why the paper calls the preparation a finite-depth *adaptive*
circuit: the quantum circuit has bounded depth, while a classical decoder
and a classically chosen Pauli frame connect the measurement step to later
operations.  This is a deterministic state-preparation statement assuming
an appropriate decoder exists.  It is not yet a complete proof of fault
tolerance against noisy gates and noisy measurements; the paper identifies
that stronger question as future work.

### What to retain for the computation section

The ideal \(|+\rangle_a\) projection used in a formal gauging derivation is
therefore operationally replaced by

\[
\text{measure }X^a_v
\quad\longrightarrow\quad
\text{decode the sign syndrome}
\quad\longrightarrow\quad
\text{update by }Z^A_r.
\tag{200}
\]

This prepares the desired \(+1\) constraints in the invariant input
sector. The next section asks a different question: what happens for an
**arbitrary logical input**, possibly a superposition of symmetry sectors?
Then the global products of outcomes contain information about that input
and must be retained.

Indeed, an edge correction changes a sign syndrome by \(\partial^a_1r\).
For any cocycle \(\boldsymbol\mu\), its effect on the corresponding
outcome parity is zero because
\(\boldsymbol\mu(\partial^a_1r)=(d^a_0\boldsymbol\mu)(r)=0\).
Thus local feedforward cannot erase a logical symmetry outcome. This is
why deterministic preparation and logical measurement are compatible,
but are not the same protocol on the same class of inputs.

## Section VI.A: logical Clifford measurement from gauging and ungauging

We now reach the computational claim of the paper.  Gauging was introduced
as a way to make a transversal symmetry local and dynamical.  **Ungauging**
reverses that enlargement: undo the ancilla cluster entangler and measure
away the surviving \(A\) gauge qubits.  The surprising result is that the
combined operation is a measurement of the logical symmetry that was
gauged.

The paper writes the derivation for a transversal \(\mathsf{CZ}\) in the
homological construction, where there can be several cocycle symmetries.
The conclusion is broader.  In the connected-graph construction there is
only one independent cocycle, so the same derivation reduces to a measurement
of its chosen involutory symmetry, such as SWAP or the CZ considered here.

### The claim in one line

Let \(U_{\boldsymbol\mu}\) be the transversal logical Clifford symmetry
with \(U_{\boldsymbol\mu}^\dagger=U_{\boldsymbol\mu}\) and
\(U_{\boldsymbol\mu}^2=I\), associated with an ancilla 0-cocycle
\(\boldsymbol\mu\in\ker d^a_0\).  Gauging and then ungauging applies the
projector

\[
P_{x_{\boldsymbol\mu}}
=\frac{I+x_{\boldsymbol\mu}U_{\boldsymbol\mu}}{2}
\tag{201}
\]

to the two input code blocks.  Here
\(x_{\boldsymbol\mu}=\pm1\) is obtained from the temporary-ancilla
measurement outcomes.  Equation (201) is precisely the projective
measurement of the Hermitian involution \(U_{\boldsymbol\mu}\): it selects
its \(+1\) or \(-1\) eigenspace.

For the connected graph used in the SWAP and ALP examples,
\(\ker d^a_0\) is one-dimensional: it contains zero and the uniform
nonzero cocycle \(\boldsymbol\mu_{\rm all}\).
The formula is then simply

\[
\frac{I+x\,U}{2}.
\tag{202}
\]

The rest of this section derives this statement.  The logical information
never has to be decoded into individual physical qubits; all operations are
performed on the qLDPC blocks and the ancillary qubits.

### Ingredients and notation

Let \(|\Psi\rangle_{BC}\) be an arbitrary state in the two input code
spaces.  Let \(C_A\) be the Clifford circuit which prepares the ancilla
cluster state from

\[
|0\rangle_A^{\otimes}\,|+\rangle_a^{\otimes}.
\tag{203}
\]

In the Hadamard convention used here, \(C_A\) is a product of CNOT gates
from temporary controls \(a_v\) to the adjacent \(A\) qubits. The complete
measurement procedure is:

1. Apply \(C_A\), then the enrichment circuit \(\Omega\).
2. Measure each \(a_v\) in the \(X\) basis and record \(x_v\).
3. Apply \(C_A^\dagger\), then measure each \(A_e\) in the \(Z\) basis,
   recording its bit \(z(e)\).
4. Solve \(d^a_0\boldsymbol\phi_0=\boldsymbol z\), and apply
   \(X^a_{\boldsymbol\phi_0}\).
5. Apply \(\Omega^\dagger\). The ancillary registers now factor from
   the matter state and can be discarded.

The measured \(a\) qubits must remain available for the later gates.
An ideal nondestructive \(X\) measurement leaves them in the recorded
\(X\)-eigenstates. With destructive readout, reprepare those same
\(|x_v\rangle_X\) states before step 3. Discarding them without this
replacement would not implement the displayed protocol.

The correction in step 4 removes the offset \(\boldsymbol\phi_0\), not
the logical measurement outcome. It is required independently of whether
\(x_{\boldsymbol\phi_0}\) is positive or negative: that scalar is only a
global phase. A software frame can replace the physical correction only if
its propagation through the subsequent enrichment inverse is accounted for.

We next recall the ancillary chain complex, then derive why these operations
produce a projector on the original encoded state.

### Chains and cochains on the ancillary register

The calculation uses two different maps on the ancillary register. A
boundary locates the endpoints of a correction string; a coboundary tells
us which gauge qubits are flipped by a choice of temporary controls.
Keeping these roles separate is easiest on a three-vertex graph:

```text
v1 ----- e12 ----- v2 ----- e23 ----- v3
 a1                 a2                 a3

         A12                 A23
```

Each vertex \(v\) carries a temporary qubit \(a_v\), and each edge \(e\)
carries a surviving gauge qubit \(A_e\).  This is the same vertex-and-edge
picture used in ordinary lattice gauging.  The qLDPC construction permits
the graph to be an abstract incidence structure rather than a planar drawing,
but the following bookkeeping is identical.

The symbols \(A_0\) and \(A_1\) mean, respectively, the binary vector
spaces of collections of vertices and collections of edges:

\[
\begin{array}{c|c|c}
\text{mathematical object}&\text{plain-English meaning}&\text{physical qubits}\\
\hline
A_0&\text{collections of vertices}&a_v\text{ live at vertices}\\
A_1&\text{collections of edges}&A_e\text{ live on edges}.
\end{array}
\]

Because the coefficients are in \(\mathbb F_2\), a collection means “mark
some objects,” and marking an object twice cancels: \(1+1=0\pmod2\).  For
example,

\[
r=e_{12}+e_{23}\in A_1
\]

means “mark both edges,” while

\[
s=v_1+v_3\in A_0
\]

means “mark vertices \(v_1\) and \(v_3\).”  These are **chains**.

The boundary map turns a marked set of edges into the marked endpoints left
over:

\[
\partial^a_1(e_{12})=v_1+v_2,
\qquad
\partial^a_1(e_{23})=v_2+v_3,
\]

and therefore

\[
\partial^a_1(e_{12}+e_{23})
=(v_1+v_2)+(v_2+v_3)=v_1+v_3.
\]

The interior vertex \(v_2\) cancels because the two selected edges meet
there.  This is the familiar fact that a path has endpoints but its interior
has no boundary.  In measurement decoding, the equation

\[
\partial^a_1r=s
\]

means: choose an edge string \(r\) whose endpoints are exactly the vertices
with unwanted measurement signs \(s\).

Now introduce a 0-cochain \(\boldsymbol\phi\in A^0\).  For intuition, draw
it as another assignment of bits to vertices:

```text
vertex:       v1   v2   v3
phi(v):        1    0    1
```

The coboundary \(d^a_0\boldsymbol\phi\) assigns bits to edges.  On an edge,
it asks whether the endpoint bits differ:

\[
(d^a_0\boldsymbol\phi)(e_{12})
=\boldsymbol\phi(v_1)+\boldsymbol\phi(v_2)=1+0=1,
\]

\[
(d^a_0\boldsymbol\phi)(e_{23})
=\boldsymbol\phi(v_2)+\boldsymbol\phi(v_3)=0+1=1.
\]

Thus \(d^a_0\boldsymbol\phi\) marks the edges crossing from a vertex with
bit \(0\) to one with bit \(1\):

```text
vertex bits phi:       1 ---- 0 ---- 1
edge bits d phi:           1       1
```

The distinction between the two maps is therefore

\[
\partial^a_1:
\underbrace{\text{marked edges}}_{\text{chain}}
\longrightarrow
\underbrace{\text{their endpoints}}_{\text{chain}},
\]

\[
d^a_0:
\underbrace{\text{vertex-bit assignment}}_{\text{cochain}}
\longrightarrow
\underbrace{\text{edge-bit assignment}}_{\text{cochain}}.
\]

In the measurement-and-ungauging calculation, \(\boldsymbol\phi\) is used
only to choose a term in an expansion.  Its coboundary specifies the
surviving edge qubits on which to apply \(X\):

\[
X^A_{d^a_0\boldsymbol\phi}
=\prod_{e:\,(d^a_0\boldsymbol\phi)(e)=1}X_{A_e}.
\]

For the displayed example, this gives

\[
X^A_{d^a_0\boldsymbol\phi}=X_{A_{12}}X_{A_{23}},
\qquad
X^A_{d^a_0\boldsymbol\phi}|0\rangle_A
=|1\rangle_{A_{12}}|1\rangle_{A_{23}}.
\]

Thus a subsequent \(Z_A\) measurement records two minus signs.  Its
edge-outcome pattern is written as the 1-cochain
\(\boldsymbol z=d^a_0\boldsymbol\phi\).

The precise definitions underlying these bit assignments are

\[
A^0=\operatorname{Hom}(A_0,\mathbb F_2),
\qquad
A^1=\operatorname{Hom}(A_1,\mathbb F_2).
\]

Formally, cochains are linear functions.  But because there is a preferred
basis of vertices and edges, such a function is completely specified by one
bit per vertex or edge.  That is why a cochain can be drawn just like a
marked collection.  For a first reading, retain the following rule:

```text
chain:    “Which vertices or edges have I selected?”
cochain:  “What bit do I assign to each vertex or edge?”
```

They look alike in coordinates, but they participate in different maps:

\[
\partial:\text{chains}\longrightarrow\text{chains},
\qquad
d:\text{cochains}\longrightarrow\text{cochains}.
\]


For this three-vertex example, the two maps are the matrices

\[
\partial^a_1=
\begin{pmatrix}1&0\\1&1\\0&1\end{pmatrix},\qquad
d^a_0=(\partial^a_1)^{\mathsf T}=
\begin{pmatrix}1&1&0\\0&1&1\end{pmatrix}.
\]

Multiplying the first by the edge-chain column \((1,1)^{\mathsf T}\)
gives the endpoint column \((1,0,1)^{\mathsf T}\). Multiplying the second
by the vertex-cochain column \((1,0,1)^{\mathsf T}\) gives the edge bits
\((1,1)^{\mathsf T}\). All matrix arithmetic is modulo two.
The transpose relation follows from the definition

\[
(d^a_0\boldsymbol\phi)(r)=\boldsymbol\phi(\partial^a_1r).
\]

The left side evaluates an edge cochain on an edge chain; the right side
evaluates the vertex cochain on that chain's boundary. For a single edge,
this equation says to add the two endpoint bits. For a path, all interior
bits cancel.

In homological gauging, \(A_0,A_1\) still label temporary and surviving
qubits, but the incidence matrix need not be that of an ordinary graph.
An \(A\) qubit can then couple to a different set of temporary controls.
The matrix equations, dual-space definitions and calculation below still
apply; the statement “add the two endpoint bits” is specific to a graph.
Consequently \(\ker d^a_0\) can describe subsystem symmetries rather than
just a uniform bit assignment.

### Step 1: expand the fixed \(X_a\)-measurement record

For a record \(x_v=\pm1\), the one-qubit measurement projector is

\[
\Pi_v(x_v)=\frac{I+x_vX^a_v}{2}.
\tag{204}
\]

The cluster relation lets us move this projector through the preparation
circuit.  In the notation used throughout the note,

\[
\Pi_{\boldsymbol x}\,\Omega C_A
\bigl(|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a\bigr)
\ =\ 
C_A\prod_v\frac{I+x_vX^a_vX^A_{d^a_0\boldsymbol v}}{2}
\Omega\bigl(|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a\bigr).
\tag{205}
\]

This equation says: “instead of viewing the \(X_a\) measurements as acting
after cluster preparation, we can pull their projectors through the
cluster-preparation circuit.” In that new viewpoint, each measured temporary
qubit is accompanied by \(X\)'s on all adjacent surviving \(A\)-qubits.

Write the initial state as

\[
|\Phi_0\rangle=|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a .
\]

For a particular set of recorded measurement outcomes
\(\boldsymbol x=\{x_v\}\), with \(x_v=\pm1\),

\[
\Pi_{\boldsymbol x}
=\prod_v\Pi_v(x_v),
\qquad
\Pi_v(x_v)=\frac{I+x_vX^a_v}{2}.
\]

This is just the projector onto the stated outcomes: if \(x_v=+1\), it
projects \(a_v\) onto \(|+\rangle\); if \(x_v=-1\), onto \(|-\rangle\).

The cluster-preparation circuit \(C_A\) is a product of CNOTs from a
temporary vertex qubit \(a_v\) to each neighbouring gauge-field qubit
\(A_e\). Its basic conjugation rule is

\[
C_A^\dagger X^a_v C_A
=
X^a_v X^A_{d^a_0\mathbf v}.
\]

Here \(d^a_0\mathbf v\) is the binary list of edges incident on \(v\). Thus,
if \(v\) has neighbouring edges \(e_1,\ldots,e_r\),

\[
X^A_{d^a_0\mathbf v}
=
X_{A_{e_1}}\cdots X_{A_{e_r}}.
\]

For example, for a degree-three vertex,

\[
C_A^\dagger X^a_v C_A
=
X_{a_v}X_{A_{e_1}}X_{A_{e_2}}X_{A_{e_3}}.
\]

Now insert \(I=C_A C_A^\dagger\) around each measurement projector:

\[
\Pi_v(x_v)C_A
=
C_A\bigl(C_A^\dagger\Pi_v(x_v)C_A\bigr)
=
C_A\frac{I+x_vX^a_vX^A_{d^a_0\mathbf v}}{2}.
\]

Doing this for every vertex gives the displayed equation:

\[
\Pi_{\boldsymbol x}\Omega C_A|\Phi_0\rangle
=
C_A
\prod_v
\frac{I+x_vX^a_vX^A_{d^a_0\mathbf v}}{2}
\Omega|\Phi_0\rangle.
\]

The enrichment circuit \(\Omega\) commutes with \(C_A\): both are
controlled by the \(a\)-qubits, but they act on different targets
(\(\Omega\) on \(B,C\), \(C_A\) on \(A\)). That is why their order can be
exchanged here.

So the important content is not a new operation. It is a change of
description:

\[
\boxed{\text{measuring }X_{a_v}\text{ after cluster preparation}}
\quad\longleftrightarrow\quad
\boxed{\text{measuring the cluster stabilizer }
X_{a_v}X^A_{d^a_0\mathbf v}\text{ before it}.}
\]

These are exact identities for unnormalized post-measurement states;
the factors of \(1/2\) have been retained. The crucial feature is the factor
\(X^a_vX^A_{d^a_0\boldsymbol v}\): measuring an \(a\) qubit is tied to an
\(X\) operation on the adjacent \(A\)-gauge qubits.

Expanding the product in Eq. (205) means choosing either the \(I\) term or
the \(X^a_vX^A_{d^a_0\boldsymbol v}\) term at every vertex.  A choice is a
binary 0-cochain \(\boldsymbol\phi\in A^0\).  Concretely, this means that
\(\boldsymbol\phi\) is a binary label assigned to every temporary-ancilla
vertex:

\[
\boldsymbol\phi:V_A\longrightarrow\mathbb F_2=\{0,1\}.
\]

If there are \(N\) temporary \(a\)-qubits, \(\boldsymbol\phi\) is simply an
\(N\)-bit string.  In this equation it is not a new quantum state, a
measurement outcome, or a physical excitation.  It is an accounting device
for one term in the algebraic expansion.  At each vertex \(v\), it records
which of the two terms was selected:

\[
\begin{array}{c|c}
\boldsymbol\phi(v)&\text{selected term}\\
\hline
0&I\\
1&x_vX^a_vX^A_{d^a_0\boldsymbol v}.
\end{array}
\]

For example, for three vertices,
\(\boldsymbol\phi=(1,0,1)\) means: select the non-identity term at
vertices \(1\) and \(3\), and select \(I\) at vertex \(2\).  The
corresponding contribution is \(x_1x_3K_1K_3\), where
\(K_v=X^a_vX^A_{d^a_0\boldsymbol v}\).  Therefore

\[
\prod_v\left(I+x_vX^a_vX^A_{d^a_0\boldsymbol v}\right)
=\sum_{\boldsymbol\phi\in A^0}
x_{\boldsymbol\phi}\,X^a_{\boldsymbol\phi}X^A_{d^a_0\boldsymbol\phi},
\qquad
x_{\boldsymbol\phi}:=\prod_vx_v^{\boldsymbol\phi(v)}.
\tag{206}
\]

The subscript on \(x_{\boldsymbol\phi}\) denotes a product of signs,
whereas the entries of \(\boldsymbol\phi\) are exponents:

\[
x_{\boldsymbol\phi}:=\prod_vx_v^{\boldsymbol\phi(v)},
\]

not \(\prod_vx_{\boldsymbol\phi(v)}\). The exponent is essential. Since
\(\boldsymbol\phi(v)\) is either \(0\) or \(1\),

\[
x_v^{\boldsymbol\phi(v)}
=
\begin{cases}
1,&\boldsymbol\phi(v)=0,\\
x_v,&\boldsymbol\phi(v)=1.
\end{cases}
\]

Thus \(x_{\boldsymbol\phi}\) is simply the product of the recorded signs
\(x_v\) over those vertices selected by \(\boldsymbol\phi\).

This is the ordinary binomial expansion, with
\(K_v=X^a_vX^A_{d^a_0\mathbf v}\) and
\(X^a_{\boldsymbol\phi}=\prod_v(X^a_v)^{\boldsymbol\phi(v)}\).
The two-vertex case displays every term explicitly.

For two vertices \(v_1,v_2\), the left-hand side is

\[
(I+x_1K_1)(I+x_2K_2)
=
I+x_1K_1+x_2K_2+x_1x_2K_1K_2.
\]

The four terms correspond exactly to the four binary cochains:

\[
\begin{array}{c|c|c}
\boldsymbol\phi=(\boldsymbol\phi(v_1),\boldsymbol\phi(v_2))
&x_{\boldsymbol\phi}&\text{Pauli operator}\\
\hline
(0,0)&1&I\\
(1,0)&x_1&K_1\\
(0,1)&x_2&K_2\\
(1,1)&x_1x_2&K_1K_2.
\end{array}
\]

Finally, the compact form of the Pauli operator follows because \(d^a_0\)
is linear over \(\mathbb F_2\):

\[
d^a_0\boldsymbol\phi
=
\sum_v\boldsymbol\phi(v)\,d^a_0\mathbf v.
\]

Therefore, selecting \(K_v\) at every vertex with
\(\boldsymbol\phi(v)=1\) gives

\[
\prod_{v:\boldsymbol\phi(v)=1}K_v
=
\left[\prod_v(X^a_v)^{\boldsymbol\phi(v)}\right]
\left[\prod_v\left(X^A_{d^a_0\mathbf v}\right)^{\boldsymbol\phi(v)}\right]
=
X^a_{\boldsymbol\phi}X^A_{d^a_0\boldsymbol\phi}.
\]

The missing factors of \(1/2\) are intentional: Eq. (206) expands the
numerators of the measurement projectors. The full projector has an overall
factor \(2^{-|V_A|}\), which is irrelevant once the state is normalized.

This is not a new physical superposition of measurement records.  It is an
algebraic expansion of the fixed-record projector.  It is useful because the
co-boundary \(d^a_0\boldsymbol\phi\) will be tested by the later \(Z_A\)
measurements.

### Step 2: the \(Z_A\) record fixes a coset of cocycles

Ungauging first applies \(C_A^\dagger\), removing the leftmost cluster
entangler in Step 1. The \(A\) register is not yet reset to zero: each
summand contains \(X^A_{d^a_0\boldsymbol\phi}|0\rangle_A
=|d^a_0\boldsymbol\phi\rangle_A\).  Let the subsequent
\(Z_A\) measurement record be a binary 1-cochain \(\boldsymbol z\):
\(z(f)=1\) means the outcome on edge \(f\) is \(-1\).

Here the cleanest way to read the notation is: choose the natural bases of
vertices and edges, then represent each cochain by its list of values on
those basis objects.  Thus \(\boldsymbol\phi\in A^0\) is formally a linear
function on vertex chains, but we draw it as vertex bits; likewise,
\(\boldsymbol z\in A^1\) is formally a linear function on edge chains, but
we draw it as edge bits.  The important point is that \(\boldsymbol z\) and
\(d^a_0\boldsymbol\phi\) belong to the same space, \(A^1\).  Equation (207)
is an equality of two edge cochains, meaning

\[
z(e)=(d^a_0\boldsymbol\phi_0)(e)
\qquad\text{for every edge }e.
\]

Take the concrete vertex assignment

```text
vertex:       v1   v2   v3
phi(v):        1    0    1
```

Its coboundary is

\[
(d^a_0\boldsymbol\phi)(e_{12})=1+0=1,
\qquad
(d^a_0\boldsymbol\phi)(e_{23})=0+1=1.
\]

Thus its edge values are

```text
edge:             e12  e23
(d phi)(e):         1    1
```

The operator \(X^A_{d^a_0\boldsymbol\phi}\) applies \(X\) precisely on
those edge qubits with assigned bit \(1\).  Therefore

\[
X^A_{d^a_0\boldsymbol\phi}|0\rangle_A
=X_{A_{12}}X_{A_{23}}
\bigl(|0\rangle_{A_{12}}|0\rangle_{A_{23}}\bigr)
=|1\rangle_{A_{12}}|1\rangle_{A_{23}}.
\]

The later \(Z_A\) measurement reads this computational-basis string.  With
the convention \(z(e)=0\) for a \(+1\) \(Z_{A_e}\) outcome and \(z(e)=1\)
for a \(-1\) outcome, the displayed state has only one possible record:

```text
edge:       e12  e23
z(e):         1    1
```

Hence \(\boldsymbol z=d^a_0\boldsymbol\phi\).  If instead the measurement
reported \(\boldsymbol z=(0,1)\), its overlap with this branch would vanish:

\[
\langle 0,1|1,1\rangle=0.
\]

This is the meaning of “its overlap with the observed record is nonzero only
if” there is some 0-cochain \(\boldsymbol\phi_0\) with

\[
\boldsymbol z=d^a_0\boldsymbol\phi_0
\tag{207}
\]

The subscript \(0\) says only: choose one cochain whose coboundary matches
the actual record.  It need not be unique.  This is an outcome constraint,
not a postselection condition: the actual record automatically has this form
because it came from the state in Eq. (206).

Indeed, if \(\boldsymbol\mu\in\ker d^a_0\), then

\[
d^a_0(\boldsymbol\phi_0+\boldsymbol\mu)
=d^a_0\boldsymbol\phi_0
=\boldsymbol z.
\]

These alternative \(\boldsymbol\phi\)'s are precisely the branches that
remain after the \(Z_A\) measurement, and they differ by ancilla symmetries.

Now compare any other surviving summand \(\boldsymbol\phi\) with
\(\boldsymbol\phi_0\).  It must obey

\[
d^a_0\boldsymbol\phi=d^a_0\boldsymbol\phi_0
\quad\Longleftrightarrow\quad
d^a_0(\boldsymbol\phi+\boldsymbol\phi_0)=0.
\tag{208}
\]

Thus every surviving label has the form

\[
\boldsymbol\phi=\boldsymbol\phi_0+\boldsymbol\mu,
\qquad
\boldsymbol\mu\in\ker d^a_0.
\tag{209}
\]

The surviving set is the **coset**
\(\boldsymbol\phi_0+\ker d^a_0\): the set obtained by adding
\(\boldsymbol\phi_0\) to every vector in the kernel. Unless the observed
edge string is zero, the surviving \(\boldsymbol\phi\)'s are not themselves
cocycles. Their differences are. Subtracting the known offset (the same as
adding it over \(\mathbb F_2\)) leaves only the symmetry labels.

On the three-vertex line, take \(\boldsymbol z=(1,1)\). The equations are
\(\phi_1+\phi_2=1\) and \(\phi_2+\phi_3=1\), with exactly two solutions:
\((1,0,1)\) and \((0,1,0)\). Their difference is \((1,1,1)\), which has
zero coboundary. Neither solution has zero coboundary. This small example
is why the coset, rather than just the kernel, appears before feedforward.

The binary string \(\boldsymbol z\) is a **coboundary**, belonging to
\(\operatorname{im}d^a_0\). On a graph with loops, not every edge string
has this property: around any loop the endpoint differences sum to zero.
These restrictions hold automatically for ideal outcomes in this protocol;
no experiment is rejected to enforce them.

The offset \(\boldsymbol\phi_0\) is an ordinary measurement byproduct.
Applying \(X^a_{\boldsymbol\phi_0}\) before undoing enrichment removes it.  After this
feedforward, the part that acts nontrivially on the input blocks is

\[
\sum_{\boldsymbol\mu\in\ker d^a_0}
x_{\boldsymbol\mu}X^a_{\boldsymbol\mu}\,\Omega.
\tag{210}
\]

Notice the contrast with the previous measurement-preparation section.
Local byproducts such as \(\boldsymbol\phi_0\) are correctable.  The signs
\(x_{\boldsymbol\mu}\) attached to genuine cocycles are not local syndrome
data to erase: they are the logical measurement outcomes we want to retain.

### Step 3: remove the ancilla and reveal the logical projector

Undo the enrichment circuit and use its defining symmetry-enrichment
identity,

\[
\Omega^\dagger X^a_{\boldsymbol\mu}\Omega
=X^a_{\boldsymbol\mu}U_{\boldsymbol\mu}.
\tag{211}
\]

After conjugating through \(\Omega\), the remaining ancilla operators
act on the original \(|+\rangle_a\) factors. Hence each
\(X^a_{\boldsymbol\mu}\) acts as \(+1\), and the resulting state
factors into an ancilla product state and a matter state.  Choose a
basis \(\{\boldsymbol\mu_i\}\) of the cocycle space.  The output on the
input codes is, up to normalization,

\[
|\Psi\rangle_{BC}
\longmapsto
\prod_i\frac{I+x_{\boldsymbol\mu_i}U_{\boldsymbol\mu_i}}{2}
|\Psi\rangle_{BC}.
\tag{212}
\]

#### What \(\boldsymbol\mu\in\ker d^a_0\) means here

The kernel belongs to the map \(d^a_0\): it is the vector space of
inputs that this map sends to zero. Saying that \(\boldsymbol\mu\)
belongs to it means

\[
\boldsymbol\mu\in\ker d^a_0
\qquad\Longleftrightarrow\qquad
d^a_0\boldsymbol\mu=0.
\]

For an ordinary ancilla graph, on an edge \(e=\langle v,w\rangle\), this
condition says

\[
(d^a_0\boldsymbol\mu)(e)
=\boldsymbol\mu(v)+\boldsymbol\mu(w)=0\pmod2.
\]

Thus neighbouring vertices must have equal \(\boldsymbol\mu\)-bits.  On a
connected graph, \(\boldsymbol\mu\) must be constant everywhere, leaving
just two possibilities:

```text
mu = 0:       0 ---- 0 ---- 0 ---- ...
mu = mu_all:  1 ---- 1 ---- 1 ---- ...
```

For the three-vertex line used above,

\[
d^a_0(m_1,m_2,m_3)=(m_1+m_2,\;m_2+m_3),
\]

so \(d^a_0\boldsymbol\mu=0\) requires
\(m_1=m_2=m_3\).  Hence

\[
\ker d^a_0=\{(0,0,0),(1,1,1)\}.
\]

Why do precisely these cochains survive Step 2?  Suppose one vertex cochain
\(\boldsymbol\phi_0\) explains the final edge record:

\[
\boldsymbol z=d^a_0\boldsymbol\phi_0.
\]

For any \(\boldsymbol\mu\in\ker d^a_0\),

\[
d^a_0(\boldsymbol\phi_0+\boldsymbol\mu)
=d^a_0\boldsymbol\phi_0+d^a_0\boldsymbol\mu
=\boldsymbol z.
\]

Therefore \(\boldsymbol\phi_0\) and
\(\boldsymbol\phi_0+\boldsymbol\mu\) create exactly the same bit pattern
on every surviving \(A\)-edge qubit.  The final \(Z_A\) measurements cannot
distinguish them.  In a connected graph, adding
\(\boldsymbol\mu_{\rm all}\) simply flips every vertex bit; each edge still
has the same endpoint *difference*.  The kernel is therefore the residual
global ambiguity left after the edge measurements have removed all local
information.

Step 3 translates that ambiguity into a logical operation.  The enrichment
circuit was chosen so that every such ancilla symmetry obeys

\[
\Omega^\dagger X^a_{\boldsymbol\mu}\Omega
=X^a_{\boldsymbol\mu}U_{\boldsymbol\mu}.
\]

Moving \(X^a_{\boldsymbol\mu}\) backward through enrichment produces the
same ancilla operator times the logical Clifford symmetry
\(U_{\boldsymbol\mu}\) on the \(B,C\) code blocks.  The \(a\) qubits are in
\(|+\rangle_a\), so \(X^a_{\boldsymbol\mu}\) acts as \(+1\) and disappears.
What remains is

\[
\sum_{\boldsymbol\mu\in\ker d^a_0}
x_{\boldsymbol\mu}U_{\boldsymbol\mu}.
\]

For a connected graph, the kernel has only \(0\) and
\(\boldsymbol\mu_{\rm all}\). Dividing this operator sum by two gives
the projector

\[
\frac{I+x_{\rm all}U_{\rm all}}{2},
\qquad
x_{\rm all}=x_{\boldsymbol\mu_{\rm all}}=\prod_vx_v.
\]

Although every temporary qubit was measured separately, only this global
parity of their outcomes remains after ungauging.  It is exactly the outcome
of measuring the logical symmetry \(U_{\rm all}\).

This is Eq. (201), now derived.  In the homological construction, each
independent cocycle can measure a related, potentially addressable logical
\(\mathsf{CZ}\).  In the connected-graph construction, there is one independent cocycle
and Eq. (212) is one logical-gate measurement.


#### Why a sum over cocycles becomes a product of projectors

Let \(k=\dim\ker d^a_0\). Choosing a basis means that every cocycle has
one unique expression \(\boldsymbol\mu=\sum_{i=1}^k t_i\boldsymbol\mu_i\)
with bits \(t_i\). In this CZ construction the symmetry operators are
commuting involutions and obey
\(U_{\mu+\nu}=U_\mu U_\nu\); the outcome signs obey the same multiplication
rule, since \(x_v^2=1\). Therefore

\[
\sum_{\boldsymbol\mu\in\ker d^a_0}x_{\boldsymbol\mu}U_{\boldsymbol\mu}
=\prod_{i=1}^k(I+x_{\boldsymbol\mu_i}U_{\boldsymbol\mu_i}).
\]

For two basis cocycles this reads

\[
I+x_{\mu_1}U_{\mu_1}+x_{\mu_2}U_{\mu_2}
+x_{\mu_1}x_{\mu_2}U_{\mu_1}U_{\mu_2}
=(I+x_{\mu_1}U_{\mu_1})(I+x_{\mu_2}U_{\mu_2}).
\]

It is the same binomial expansion as Step 1, now restricted to the
undistinguished symmetry labels. Each factor divided by two is a projector:

\[
\left(\frac{I+xU}{2}\right)^2
=\frac{I+2xU+U^2}{4}=\frac{I+xU}{2},
\qquad
U\frac{I+xU}{2}=x\frac{I+xU}{2}.
\]

The first identity says repeating the projection has no further effect;
the second says its surviving states have eigenvalue \(x\). Opposite-sign
projectors are orthogonal, and their sum is \(I\). The simultaneous
projector is their product because these symmetries commute. Independent
cocycles need not give independent logical gates: a symmetry acting as
identity on the codespace has a fixed positive outcome.

For a normalized input, the probability of a logical record is
\(\|P_{\boldsymbol x}|\Psi\rangle\|^2\), and the conditional output is
\(P_{\boldsymbol x}|\Psi\rangle/\|P_{\boldsymbol x}|\Psi\rangle\|\).
The projector's factor of two and the state's normalization are different
things. A general Clifford gate need not satisfy \(U^2=I\); the binary
projector formula here applies to the involutions in this construction.

### The complete protocol with the ancillary registers retained

The following calculation keeps the normalization factors and the measured
\(A\) register, so that every equality has the same input and output
spaces. Set \(N=\dim A^0\), \(k=\dim\ker d^a_0\), and define

\[
|\Phi_0\rangle=|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a,\qquad
P^A_{\boldsymbol z}=\prod_e\frac{I+(-1)^{z(e)}Z_{A_e}}2.
\]

For the fixed records \(\boldsymbol x,\boldsymbol z\), the unnormalized
state after undoing the cluster entangler and measuring \(A\) is

\[
\begin{aligned}
P^A_{\boldsymbol z}C_A^\dagger\Pi_{\boldsymbol x}\Omega C_A|\Phi_0\rangle
&=2^{-N}\sum_{\phi:\,d^a_0\phi=\boldsymbol z}
x_\phi X^a_\phi\Omega
\bigl(|\Psi\rangle_{BC}|\boldsymbol z\rangle_A|+\rangle_a\bigr)\\
&=2^{-N}x_{\phi_0}X^a_{\phi_0}
\sum_{\mu\in\ker d^a_0}x_\mu X^a_\mu\Omega
\bigl(|\Psi\rangle_{BC}|\boldsymbol z\rangle_A|+\rangle_a\bigr).
\end{aligned}
\]

The first line is Step 1's expansion followed by Step 2's selection rule.
The second substitutes \(\phi=\phi_0+\mu\). Applying the correction
\(X^a_{\phi_0}\) and then \(\Omega^\dagger\) gives exactly

\[
2^{k-N}x_{\phi_0}
\left[\prod_{i=1}^k\frac{I+x_{\mu_i}U_{\mu_i}}2\right]
|\Psi\rangle_{BC}\otimes|\boldsymbol z\rangle_A\otimes|+\rangle_a.
\]

The factor \(x_{\phi_0}\) is a global sign. The scalar \(2^{k-N}\)
contributes to the probability of the *full* ancillary record; it does not
change the normalized conditional matter state. The \(A\) qubits are left
in the measured string \(|\boldsymbol z\rangle\), not automatically
\(|0\rangle\); they can be discarded or reset by \(X^A_{\boldsymbol z}\).
The \(a\) qubits have returned to \(|+\rangle\) and can also be discarded.

The physical roles of the three steps are now explicit. The temporary
measurements introduce the sum over cochains. The gauge-qubit measurements
identify their coboundaries, leaving a coset of the kernel. Correcting its
offset and undoing enrichment converts the remaining symmetry sum into
logical projectors. In a connected graph, the only logical measurement bit
left is \(x_{\rm all}=\prod_vx_v\).

### The magic-state example

Suppose the measured symmetry acts as one logical
\(\overline{\mathsf{CZ}}\) on a chosen pair of encoded qubits. This is a
simple logical example of the preceding result, not an assertion that the
whole-block ALP gate acts on only one pair: each ALP block encodes many
qubits. If a logical gate acts on several pairs, one must analyze that full
action, use an addressable construction, or fix suitable spectator logical
qubits so the action reduces to the stated pair.

For that pair, choose the input logical state
\(|\overline{+}\rangle_B|\overline{+}\rangle_C\).  A \(+1\) logical
\(\mathsf{CZ}\) outcome gives

\[
\begin{aligned}
\frac{I+\overline{\mathsf{CZ}}}{2}
|\overline{+}\rangle_B|\overline{+}\rangle_C
&\propto
|\overline{00}\rangle+
|\overline{01}\rangle+
|\overline{10}\rangle,\\
|\overline{M}_{\mathsf{CZ}}\rangle
&:=\frac{
|\overline{00}\rangle+
|\overline{01}\rangle+
|\overline{10}\rangle}{\sqrt3}.
\end{aligned}
\tag{213}
\]

The \(|\overline{11}\rangle\) component is absent because it is the unique
computational-basis component with \(\mathsf{CZ}\) eigenvalue \(-1\).  The
state in Eq. (213) is non-stabilizer: a stabilizer state has a
computational-basis support of size a power of two when its nonzero
amplitudes have equal magnitude, whereas this state has three equal nonzero
amplitudes.  It is therefore a magic-state resource.

For this particular input, the \(+1\) outcome occurs with probability
\(3/4\); the \(-1\) outcome gives \(|\overline{11}\rangle\).  Thus this
simple demonstration is heralded rather than a deterministic magic-state
factory: retain a \(+1\) trial or repeat the preparation.  The paper's
central achievement is that the required logical \(\mathsf{CZ}\) measurement
has been compiled into gauging, local measurements, decoding, and
feedforward on qLDPC code blocks.

Applying a Clifford **unitary** to a stabilizer state would leave a
stabilizer state. Measuring its eigenspaces is a different operation:
\((I+\mathsf{CZ})/2\) deletes one of the four amplitudes rather than merely
changing its sign. This is not a Pauli measurement. The physical enrichment
uses non-Clifford \(\mathsf{CCZ}\) gates, so the protocol does not obtain
magic from Clifford gates and Pauli measurements alone. It converts that
physical resource into an encoded non-stabilizer state.

### From gauging to an encoded resource state

The construction is not using a transversal \(\mathsf{CCZ}\) as a direct
logical non-Clifford gate.  It uses local controlled-symmetry enrichment,
then removes the ancillary gauge system, to perform a **logical Clifford
measurement**.  On a suitable logical input, that measurement supplies the
non-Clifford resource needed for universal computation.

## Sources and scope

- Target text: [arXiv-2602.12228v1/main.tex](../arXiv-2602.12228v1/main.tex),
  Sections II.A--III.C, “Two Approaches to Gauging qLDPC Codes,” and the
  introduction, “Graph requirements,” and “Example: Gauging transversal
  \(\mathsf{SWAP}\) gate” of “Non-Abelian Codes from Gauging with Graph
  States,” plus the opening graph-gauged ALP fracton example and
  “Measurement Preparation of Non-Abelian qLDPC Codes,” and “Logical
  Clifford Measurement from Gauging and Ungauging” (Section VI.A).
- ALP illustrations: the original TikZ diagrams from source labels
  `eq:qubit-ALP-stabilizers`, `eq:cubic-CZ-sym`, and
  `eq:cubic-symm-enrich`, rendered with their original geometry and colours.
  Reproducible extracts are in [figures/alp-paper](figures/alp-paper/).
- Context for gauging and \(\mathcal D(D_4)\):
  [arXiv-2209.06202v2/main.tex](../arXiv-2209.06202v2/main.tex), especially
  its discussion of Abelian Kramers-Wannier gauging and \(D_4\) quantum
  doubles.
- Experimental and twisted-\(\mathbb Z_2^3\) presentation:
  [arXiv-2305.03766v2/main.tex](../arXiv-2305.03766v2/main.tex), especially
  “The model,” “Ground State Preparation,” and its table equating
  \(\mathcal D(D_4)\) with \(\mathcal D^\alpha(\mathbb Z_2^3)\).
