# Section II.A in detail: anyon permutation, defects, and gauging

**Target text:** Section II.A, "Non-Abelian Anyons from Gauging," of
[arXiv-2602.12228v1](../arXiv-2602.12228v1/main.tex).  
**Level:** advanced undergraduate quantum mechanics, with prior exposure to the
toric code and stabilizer codes.

## What this subsection is trying to establish

Section II.A is not yet the lattice construction. Its purpose is to explain
*why* gauging a particular symmetry of two toric codes produces non-Abelian
topological order. The key chain of ideas is

\[
\begin{aligned}
\text{controlled-Z symmetry}
&\ \Longrightarrow\ \text{permutation of anyon types}\\
&\ \Longrightarrow\ \text{symmetry defect}
\ \Longrightarrow\ \text{dynamical gauge flux with non-Abelian braiding}.
\end{aligned}
\]

The result is a model with \(\mathcal D(D_4)\) topological order. Here
\(\mathcal D(G)\) denotes the quantum double of a finite group \(G\), and the
paper uses \(D_4\) for the eight-element dihedral group. The derivation of the
actual gauged stabilizers is postponed to Section II.B. This note explains the
physics and algebra that motivate that derivation.

## Starting point: two decoupled toric codes

Put one qubit on each edge of a square lattice. For one toric code, introduce

\[
A_v=\prod_{e\ni v} X_e,
\qquad
B_p=\prod_{e\in\partial p} Z_e.
\]

\(A_v\) is the vertex (or star) stabilizer and \(B_p\) is the plaquette
stabilizer. The Hamiltonian can be written

\[
H_{\mathrm{TC}}=-\sum_v A_v-\sum_p B_p.
\]

The ground space is the simultaneous \(+1\) eigenspace of every \(A_v\) and
\(B_p\). In this note, copy \(B\) and copy \(C\) have independent Pauli
operators:

\[
X_e^{B},Z_e^{B},
\qquad
X_e^{C},Z_e^{C}.
\]

Their decoupled Hamiltonian is \(H_{\mathrm{TC}}^{B}+H_{\mathrm{TC}}^{C}\).
The superscripts are labels of the two codes, not powers.

### Excitations and string operators

An \(e\) anyon is a vertex where \(A_v=-1\). If \(\gamma\) is a path on the
direct lattice, then

\[
W_e^B(\gamma)=\prod_{e\in\gamma} Z_e^B
\]

commutes with all \(B_p^B\) and anticommutes only with the two star
stabilizers at the endpoints of \(\gamma\). Acting on a ground state, it
therefore creates a pair of \(e_B\) anyons at those endpoints.

Likewise, if \(\gamma^\star\) is a path on the dual lattice, then

\[
W_m^B(\gamma^\star)=\prod_{e\perp\gamma^\star} X_e^B
\]

creates a pair of \(m_B\) anyons at the two endpoint plaquettes. The same
statements hold for code \(C\).

We use the usual \(\mathbb Z_2\) fusion rules:

\[
e_B^2=m_B^2=e_C^2=m_C^2=1.
\]

For example, \(m_Be_C\) is a composite excitation carrying an \(m\) flux of
code \(B\) and an \(e\) charge of code \(C\). Before gauging, every excitation
of the two-copy theory has a unique fusion outcome: this is an Abelian anyon
theory.

### Logical operators and the bar

On a torus, a closed string that cannot be shrunk to a point is not a product
of stabilizers. It acts nontrivially within the ground-state subspace and is a
logical operator. A bar distinguishes such an encoded operation from a
single-qubit Pauli:

\[
\bar X_B,\ \bar Z_B,\ \bar X_C,\ \bar Z_C.
\]

For instance, \(\bar X_B\) is a noncontractible \(X^B\)-string (with the
precise direct/dual choice depending on convention). It acts as Pauli \(X\) on
one encoded qubit of code \(B\). The bar does **not** mean complex
conjugation. It means "logical operator."

## The controlled-Z symmetry

The two codes are placed with a small relative displacement. The circuit
\(U_{\mathsf{CZ}}\) in the paper is a product of physical controlled-Z gates:
each horizontal edge qubit of one copy is coupled to a nearby vertical edge
qubit of the other copy, and conversely. The geometry is chosen so that the
extra \(Z\) factors produced by these gates form plaquette stabilizers of the
other code.

Everything follows from the one-pair identities

\[
\mathsf{CZ}_{12}\,(X_1)\,\mathsf{CZ}_{12}=X_1Z_2,
\qquad
\mathsf{CZ}_{12}\,(X_2)\,\mathsf{CZ}_{12}=Z_1X_2,
\]

\[
\mathsf{CZ}_{12}\,(Z_1)\,\mathsf{CZ}_{12}=Z_1,
\qquad
\mathsf{CZ}_{12}\,(Z_2)\,\mathsf{CZ}_{12}=Z_2.
\]

There is no dagger on the right in these equations because
\(\mathsf{CZ}^{\dagger}=\mathsf{CZ}=\mathsf{CZ}^{-1}\).

### Why it preserves the ground space

Consider a \(B\)-code star operator. Conjugating each of its \(X^B\) factors
by the nearby controlled-Z gates produces a pattern of \(Z^C\) factors. For
the pairing shown in the paper, that pattern is precisely a neighboring
\(C\)-code plaquette operator. Schematically,

\[
U_{\mathsf{CZ}} A_v^B U_{\mathsf{CZ}}^\dagger
=A_v^B B_{p(v)}^C.
\]

Similarly, a \(C\)-code star is sent to itself times a \(B\)-code plaquette.
Plaquette stabilizers themselves are unchanged because controlled-Z commutes
with every \(Z\).

Thus \(U_{\mathsf{CZ}}\) does *not* leave each term of the microscopic
Hamiltonian fixed. Nevertheless, if \(\lvert\psi\rangle\) is a ground state,
then \(A_v^B\lvert\psi\rangle=B_p^C\lvert\psi\rangle=\lvert\psi\rangle\), so

\[
\bigl(A_v^B B_{p(v)}^C\bigr)\lvert\psi\rangle
=\lvert\psi\rangle.
\]

All transformed stabilizers still have eigenvalue \(+1\). Therefore
\(U_{\mathsf{CZ}}\) maps the ground-state subspace to itself. This is what the
paper means by an **emergent symmetry of the ground-state subspace**.

### Its logical action

The same local conjugation rule applied along noncontractible strings gives

\[
\begin{aligned}
U_{\mathsf{CZ}}\bar X_B U_{\mathsf{CZ}}^\dagger
  &=\bar X_B\bar Z_C, &
U_{\mathsf{CZ}}\bar Z_B U_{\mathsf{CZ}}^\dagger
  &=\bar Z_B,\\
U_{\mathsf{CZ}}\bar X_C U_{\mathsf{CZ}}^\dagger
  &=\bar Z_B\bar X_C, &
U_{\mathsf{CZ}}\bar Z_C U_{\mathsf{CZ}}^\dagger
  &=\bar Z_C .
\end{aligned}
\]

These are exactly the Heisenberg-picture conjugation rules of a controlled-Z
gate acting on the two encoded qubits. Since every physical
\(\mathsf{CZ}\) squares to identity,

\[
U_{\mathsf{CZ}}^2=1.
\]

The symmetry group is consequently \(\mathbb Z_2\).

## From the logical gate to an anyon permutation

The logical equation already suggests the local anyon action. More directly,
take an \(m_B\) string. It is made from \(X^B\) operators. Under conjugation
by \(U_{\mathsf{CZ}}\), every \(X^B\) in the string acquires a nearby
\(Z^C\). Symbolically,

\[
U_{\mathsf{CZ}}W_m^B(\gamma^\star)U_{\mathsf{CZ}}^\dagger
=W_m^B(\gamma^\star)\,W_e^C(\gamma).
\]

The exact path \(\gamma\) is set by the shifted edge pairing, but its endpoints
are at the same physical locations as the endpoints of the \(m_B\) string.
Thus each endpoint now carries both an \(m_B\) and an \(e_C\) excitation:

\[
g(m_B)=m_Be_C.
\]

Repeating the argument with \(B\) and \(C\) exchanged gives

\[
g(m_C)=m_Ce_B,
\qquad
g(e_B)=e_B,
\qquad
g(e_C)=e_C.
\]

The map \(g\) is an **anyon automorphism**. It is not merely a phase
assignment: it changes the superselection label of an excitation.

It is useful to write the complete action once. Every two-copy toric-code
anyon can be labeled as

\[
x=e_B^a m_B^b e_C^c m_C^d,
\qquad a,b,c,d\in\{0,1\}.
\]

All exponents are understood modulo two. The symmetry acts as

\[
g(x)=e_B^{a+d}m_B^b e_C^{c+b}m_C^d.
\]

This formula makes two facts transparent:

1. \(g\) respects fusion. Since fusion adds the four exponents modulo two,
   \(g(xy)=g(x)g(y)\).
2. \(g^2=1\). Applying the map twice adds \(2b\) and \(2d\), both zero modulo
   two.

For example, the two-element orbit of \(m_B\) is

\[
\mathcal O_{m_B}=\{m_B,\ m_Be_C\}.
\]

## A symmetry patch is a defect line

Until now, \(U_{\mathsf{CZ}}\) was applied everywhere. A **symmetry patch**
means applying the same circuit only in a finite region \(R\). Denote this
partial operation by \(U_{\mathsf{CZ}}(R)\).

Inside \(R\), an anyon label is related to the outside label by \(g\). Thus an
\(m_B\) anyon crossing the boundary has the following description:

\[
m_B\quad\xrightarrow{\text{cross }\partial R}\quad m_Be_C.
\]

The boundary \(\partial R\) is therefore not an ordinary boundary between two
materials. It is a line across which anyon labels are *twisted* by the
permutation \(g\). Such a line is called an **extrinsic symmetry defect** or
**branch cut**.

"Extrinsic" matters. At this stage we chose \(R\) by hand and applied an
external operation. The defect line is not yet a fluctuating degree of freedom
of the Hamiltonian. This distinction is exactly what gauging changes.

## What gauging does

Gauging a global \(\mathbb Z_2\) symmetry means two related things:

1. Add new gauge degrees of freedom, called the \(A\) sublattice in the paper.
2. Replace the global symmetry by a local redundancy, so that a symmetry
   transformation can be applied independently in different regions.

After gauging, the choice of region \(R\) is no longer externally specified.
The information formerly carried by the imposed branch cut \(\partial R\) is
carried by a configuration of the \(A\) gauge field. In the language of the
paper, a closed \(A\)-gauge-field loop realizes the boundary of a
controlled-Z symmetry patch.

Consequently, crossing the gauge-field loop has the same effect as crossing
the old defect line:

\[
\text{A-gauge loop}:
\qquad
m_B\longmapsto m_Be_C,
\qquad
m_C\longmapsto m_Ce_B.
\]

The loop may be opened into a string. Its endpoints are now genuine
point-like excitations of the gauged theory; the paper calls such a gauge-flux
excitation \(m_A\). The string is the dynamical descendant of the old
extrinsic defect line.

Section II.B will show how the \(A\) qubits, a cluster state, a
symmetry-enrichment circuit, and projection implement this statement in a
commuting-projector lattice model. Section II.A only needs the physical
consequence: an \(A\) flux is an endpoint of a line that performs \(g\).

## Why the resulting braiding is non-Abelian

Take an \(m_B\) anyon around an \(m_A\) flux once. Topologically, its path
crosses the \(m_A\) defect string once. Therefore

\[
m_B
\quad\xrightarrow{\text{braid once around }m_A}\quad
m_Be_C.
\]

For comparison, in an Abelian anyon theory a full braid of two fixed anyon
types changes a state only by a complex number:

\[
\lvert\psi\rangle\longmapsto e^{i\theta}\lvert\psi\rangle.
\]

Here the braid changes the anyon label. It acts nontrivially on the orbit
\(\mathcal O_{m_B}\), rather than multiplying one fixed label by a scalar.
After gauging, a label such as \(m_B\) is not separately gauge invariant:
local gauge transformations can exchange the two labels in its orbit. The
gauged excitation must therefore retain an internal two-component space
associated with that orbit.

This is the physical mechanism behind non-Abelian statistics. More
precisely, a non-Abelian anyon theory has fusion spaces of dimension larger
than one and braiding acts by noncommuting matrices on those spaces. The
type-changing braid above is the observable sign that this structure has
appeared. The complete \(\mathcal D(D_4)\) theory obtained after the lattice
construction supplies the corresponding fusion and braiding data.

## The torus diagnostic mentioned in the paper

The final paragraph of Section II.A refers to two pairs of nontrivially
braiding anyons wound around the two independent cycles of a torus. The
important point is not a failure of charge conservation. Rather, the two
windings cannot be treated as two independent Abelian processes: their
ordering and fusion channel affect the final state.

When the second pair is fused, a nontrivial excitation can remain at the
fusion point. The figure single_anyon.pdf is a diagnostic of the
non-Abelian fusion space and of the nontrivial topology of the torus. The
paper will later look for an analogous diagnostic in qLDPC codes, where no
ordinary geometric torus is available.

## Where \(D_4\) enters

Each input toric code is a \(\mathbb Z_2\) gauge theory, so the pair has
Abelian gauge structure \(\mathbb Z_2\times\mathbb Z_2\). Gauging the extra
\(\mathbb Z_2\) symmetry whose action is \(g\) does not give three independent
commuting \(\mathbb Z_2\) factors. The new symmetry acts nontrivially on the
old topological data.

At the group level, this is captured by

\[
D_4\cong
(\mathbb Z_2\times\mathbb Z_2)\rtimes\mathbb Z_2.
\]

The symbol \(\rtimes\) means semidirect product: the final
\(\mathbb Z_2\) acts nontrivially on the first factor. The classification of
gauged anyon-permuting symmetries identifies the resulting topological order
as \(\mathcal D(D_4)\). Section II.A invokes this known correspondence; the
next subsection constructs a specific lattice realization.

## Check your understanding

1. Using \(\mathsf{CZ}X_1\mathsf{CZ}=X_1Z_2\), explain why an \(X^B\)-string
   can acquire a \(Z^C\)-string.
2. Use the four-exponent formula for \(g\) to verify explicitly that
   \(g^2(x)=x\).
3. Explain the difference between a symmetry defect before gauging and a gauge
   flux after gauging.
4. Why is a label-changing braid stronger than the Abelian statement
   "braiding gives a phase"?

## Worked solutions

### 1. Conjugating an \(X^B\)-string

Let \(\Gamma\) be the set of \(B\)-code edges in an \(m_B\) string:

\[
W_m^B(\Gamma)=\prod_{e\in\Gamma}X_e^B.
\]

For the circuit in the paper, each relevant \(B\) edge \(e\) is paired with a
nearby \(C\) edge, which we call \(\phi(e)\). On that pair,

\[
\mathsf{CZ}_{e,\phi(e)}\,X_e^B\,\mathsf{CZ}_{e,\phi(e)}
=X_e^B Z_{\phi(e)}^C.
\]

All controlled-Z gates commute with one another because they are diagonal in
the computational basis. Pauli operators on distinct qubits also commute.
We can consequently conjugate the whole string one factor at a time:

\[
\begin{aligned}
U_{\mathsf{CZ}}W_m^B(\Gamma)U_{\mathsf{CZ}}^\dagger
&= \prod_{e\in\Gamma}
   \left(X_e^B Z_{\phi(e)}^C\right)\\
&= \left(\prod_{e\in\Gamma}X_e^B\right)
   \left(\prod_{e\in\Gamma}Z_{\phi(e)}^C\right)\\
&=W_m^B(\Gamma)\,W_e^C\bigl(\phi(\Gamma)\bigr).
\end{aligned}
\]

The first factor is the original \(m_B\) string. The second is a \(Z^C\)
string on the partner path \(\phi(\Gamma)\). A \(Z^C\) string anticommutes
with the \(C\)-code star stabilizers at its endpoints, so it creates an
\(e_C\) anyon at each of those endpoints. The shifted geometry chosen in the
paper ensures that these endpoints coincide with the endpoints of the
\(m_B\) string. Thus each endpoint changes from \(m_B\) to \(m_Be_C\).

The essential point is local: controlled-Z turns every \(X\) in the original
string into \(XZ\). The global anyon transmutation follows because the extra
\(Z\) factors join into a second string.

### 2. Verifying \(g^2=1\)

Write a general anyon as

\[
x=e_B^a m_B^b e_C^c m_C^d,
\qquad a,b,c,d\in\mathbb Z_2.
\]

The note derived

\[
g(x)=e_B^{a+d}m_B^b e_C^{c+b}m_C^d.
\]

It is helpful to regard this as an update rule for the four exponents:

\[
(a,b,c,d)\xrightarrow{g}(a+d,\ b,\ c+b,\ d).
\]

Apply the same rule again:

\[
\begin{aligned}
(a+d,\ b,\ c+b,\ d)
&\xrightarrow{g}
\bigl((a+d)+d,\ b,\ (c+b)+b,\ d\bigr)\\
&=(a+2d,\ b,\ c+2b,\ d)\\
&=(a,b,c,d).
\end{aligned}
\]

The last equality holds because the exponents lie in \(\mathbb Z_2\), where
\(2b=2d=0\). Hence \(g^2(x)=x\) for every anyon \(x\). This agrees with the
operator statement \(U_{\mathsf{CZ}}^2=1\).

### 3. Extrinsic defect versus dynamical gauge flux

Before gauging, choose a region \(R\) and actively apply
\(U_{\mathsf{CZ}}(R)\). Its boundary \(\partial R\) is a symmetry defect:
crossing it changes an anyon label by \(g\). It is called **extrinsic** because
the Hamiltonian did not create it. We introduced it from outside by choosing
\(R\) and applying a circuit. We can also move or remove it by changing that
externally imposed circuit.

After gauging, the choice of whether the symmetry is applied locally is stored
in new \(A\)-sublattice gauge variables. A branch cut is then a configuration
of the gauge field, rather than an externally prescribed boundary. Its
endpoint is a gauge-invariant, point-like excitation of the gauged
Hamiltonian: the gauge flux \(m_A\).

There is an important subtlety. The *path* of the defect string is not itself
an observable after gauging; local gauge transformations can deform it. Its
endpoint is observable, for example by braiding an \(m_B\) anyon around it.
Thus the same label-changing line has two different statuses:

- before gauging: an externally imposed defect, not an intrinsic excitation;
- after gauging: a dynamical gauge string whose endpoint is an intrinsic
  quasiparticle.

### 4. Why label-changing braiding is stronger than a phase

For Abelian anyons, the state space for a fixed set of anyon labels and a
fixed fusion channel is one dimensional. A full braid must therefore act as

\[
\lvert\psi\rangle\longmapsto e^{i\theta}\lvert\psi\rangle.
\]

The output has the same anyon labels as the input; only its phase changes.

In the present example, one circuit around \(m_A\) sends

\[
m_B\longmapsto m_Be_C.
\]

The two labels span an orbit. If we use the basis
\(\{\lvert m_B\rangle,\lvert m_Be_C\rangle\}\), then the label part of this
braid is represented, up to possible phase conventions, by

\[
P=
\begin{pmatrix}
0&1\\
1&0
\end{pmatrix}.
\]

\(P\) is not a scalar multiple of the identity: it mixes two components.
Consequently a single Abelian phase cannot describe this braid. After
gauging, the two components must be regarded as internal states of one
gauge-invariant excitation.

The swap matrix by itself does not prove every mathematical property of a
non-Abelian anyon theory; it squares to the identity and hence commutes with
itself. The full conclusion comes from the fusion and braiding data of the
gauged \(\mathcal D(D_4)\) theory, where suitable braids act by
noncommuting matrices on multidimensional fusion spaces. The label-changing
process is the physically transparent signal of why such a non-Abelian
description is needed.

# Section II.B in detail: gauging on the lattice

Section II.A explained what gauging is meant to achieve.  Section II.B is
the constructive part: it gives a local circuit and measurements whose
remaining degrees of freedom realize that gauging.  The construction has
three ingredients:

1. an auxiliary cluster state, built from new qubits (a) and (A);
2. a controlled-controlled-\(Z\) circuit that couples this cluster state to
   the two toric codes; and
3. \(X\)-measurements of all the \(a\) qubits.

The notation is deliberately suggestive: lower-case \(a\) denotes qubits
which will be measured away, while upper-case \(A\) denotes the gauge qubits
which remain.  The original two toric codes continue to be called \(B\) and
\(C\).

## The auxiliary lattice and its cluster state

Put an \(a\) qubit at every vertex of the square lattice and an \(A\) qubit
at the midpoint of every edge.  This vertex--edge lattice is often called a
Lieb lattice.  An \(A\) edge \(e\) has two endpoint vertices; write them as
\(v\) and \(w\).

Initially put every new qubit in \(\lvert+\rangle\).  The stabilizer of an
individual \(\lvert+\rangle\) is \(X=+1\).  Apply a controlled-\(Z\) gate
between every incident \(a\)--\(A\) pair, and then apply a Hadamard to every
\(A\) qubit.  The resulting state is a slightly rotated form of the usual
two-dimensional cluster state.  Its stabilizers are

\[
K_v^a=X_v^a\prod_{e\ni v}X_e^A,
\qquad
K_e^A=Z_v^a Z_e^A Z_w^a.
\tag{1}
\]

Here and below, \(\prod_{e\ni v}\) means the product over the four square
lattice edges touching vertex \(v\).

### Deriving Eq. (1), rather than memorising it

Two elementary conjugation rules are enough:

\[
\operatorname{CZ}_{ij}X_i\operatorname{CZ}_{ij}=X_iZ_j,
\qquad
H X H=Z,\quad H Z H=X.
\tag{2}
\]

Before the final Hadamards, the stabilizer which began as \(X_v^a\) has
passed through one controlled-\(Z\) for each neighbouring edge.  It is
therefore

\[
X_v^a\prod_{e\ni v}Z_e^A.
\]

The Hadamards on the \(A\) qubits exchange their \(Z\)'s for \(X\)'s.  This
gives the first operator in Eq. (1).  Similarly, the \(X_e^A\) stabilizer
acquires a \(Z^a\) at each endpoint under the two controlled-\(Z\) gates:

\[
X_e^A Z_v^aZ_w^a.
\]

The final Hadamard changes its \(X_e^A\) into \(Z_e^A\), giving the second
operator in Eq. (1).  This short calculation is useful: all later
stabilizer bookkeeping is just this same idea applied to a larger circuit.

## Why this cluster state is the correct resource for gauging

The cluster state has two symmetries.  The first is an ordinary, or
``0-form'', global symmetry,

\[
G_a=\prod_v X_v^a.
\tag{3}
\]

The second is a loop, or ``1-form'', symmetry.  For every closed collection
of \(A\) edges \(\gamma\), it is

\[
G_A(\gamma)=\prod_{e\in\gamma}Z_e^A.
\tag{4}
\]

For example, \(G_a\) commutes with \(K_e^A\) because that stabilizer has two
\(Z^a\) factors, each of which anticommutes with its corresponding \(X^a\).
The two minus signs cancel.  A closed \(A\) loop meets each vertex in zero
or two edges, so the same even-number-of-minus-signs argument shows that
\(G_A(\gamma)\) commutes with every \(K_v^a\).

The key identity is obtained by multiplying the vertex stabilizers in any
connected region \(R\):

\[
\prod_{v\in R}K_v^a
=
\left(\prod_{v\in R}X_v^a\right)
\left(\prod_{e\in\partial R}X_e^A\right).
\tag{5}
\]

Every \(A\)-edge strictly inside \(R\) occurs in two vertex stabilizers and
therefore contributes \((X_e^A)^2=1\).  Exactly the edges crossing the
boundary occur once, which proves Eq. (5).

What is true is the state-dependent identity

\[
G_a(R)\,X_A(\partial R)\lvert\mathrm{cluster}\rangle
=
\lvert\mathrm{cluster}\rangle.
\]

This follows because the left-hand operator is precisely the product of the
vertex stabilizers in \(R\):

\[
\prod_{v\in R}K_v^a
=
G_a(R)X_A(\partial R).
\]

Since \(X_A(\partial R)^2=1\), we may rearrange this to obtain

\[
G_a(R)\lvert\mathrm{cluster}\rangle
=
X_A(\partial R)\lvert\mathrm{cluster}\rangle.
\]

Equation (5) is the elementary lattice form of the SPT ``patch-to-boundary''
principle.  Acting with the \(a\)-symmetry only inside \(R\) is inseparable,
on this state, from an operator living on the boundary of \(R\).  Notice that
the boundary operator is \(X^A\), whereas the 1-form symmetry is a loop of
\(Z^A\).  They anticommute when they cross once.  That is the seed from which
a gauge field and its flux--charge relation will emerge.

## The general gauging move

Let \(U\) be a global symmetry of a matter state \(\lvert\psi\rangle\), so

\[
U\lvert\psi\rangle=\lvert\psi\rangle.
\tag{6}
\]

The role of the additional circuit \(\Omega\) is to *attach* that matter
symmetry to the cluster-state symmetry.  The required algebraic condition is

\[
\Omega G_a\Omega^\dagger=G_aU.
\tag{7}
\]

This equation deserves a literal reading.  Before \(\Omega\), a global flip
of the disposable \(a\) qubits is \(G_a\).  Afterwards, exactly the same
operation is accompanied by the matter transformation \(U\).  Combining
Eq. (7) with the patch identity (5) says that a partial \(U\) action is tied
to an \(A\)-edge boundary.  That is precisely the relation we wanted from
the discussion of symmetry-defect lines in Section II.A.

Write the symmetry operation applied only inside a region \(R\) as

\[
G_a(R)=\prod_{v\in R}X_v^a.
\]

Equation (5) says that, for the auxiliary cluster state,

\[
G_a(R)
\quad\text{has exactly the same action as}\quad
X_A(\partial R)=\prod_{e\in\partial R}X_e^A.
\]

Why? Every \(A\)-edge inside \(R\) is touched twice and cancels; only the
edges on the boundary remain. So an \(a\)-symmetry *patch* leaves an
\(A\)-edge operator on its boundary.

Now add the CCZ coupling circuit \(\Omega\). Equation (7),

\[
\Omega G_a\Omega^\dagger=G_aU,
\]

means: after coupling to the matter, performing the \(a\)-symmetry also
performs the matter symmetry \(U\).

Because \(\Omega\) is local, the same statement works region by region:

\[
\Omega G_a(R)\Omega^\dagger
=
G_a(R)\,U(R),
\]

where \(U(R)\) is the controlled-\(Z\) circuit applied only in region \(R\).

Putting this into the patch identity gives, schematically,

\[
G_a(R)\,U(R)
\quad\longleftrightarrow\quad
X_A(\partial R).
\]

Finally, measuring all \(a\) qubits in the \(X=+1\) state makes
\(G_a(R)=1\). Therefore, in the remaining \(A,B,C\) system,

\[
U(R)
\quad\longleftrightarrow\quad
X_A(\partial R).
\]

This is the quoted sentence’s content: applying the matter symmetry only in
\(R\) is inseparable from creating an \(A\)-field string on the boundary of
\(R\).

That matches Section II.A because a partial \(U\) operation has a
symmetry-defect line on its boundary: crossing that line changes an anyon’s
type. After gauging, that boundary is no longer an externally chosen defect;
it is represented by physical \(A\)-gauge degrees of freedom.

Finally measure every \(a\) qubit in the \(X\) basis and retain the
\(+1\) outcomes for the moment.  In this postselected description,

\[
X_v^a=+1\quad\hbox{for every }v.
\tag{8}
\]

The \(a\) variables disappear, but the \(A\) variables retain the record of
where the formerly global operation was applied.  Thus local changes of that
record are gauge transformations, and the unmeasured \(A\) qubits are the
gauge field.  Section II.C of the paper explains how non-\(+1\) measurement
outcomes are corrected by feedforward; for the derivation here, Eq. (8) is
the cleanest starting point.

A useful sanity check is the familiar special case \(U=X\) on a collection
of matter qubits.  Choosing \(\Omega\) to be a product of CNOT gates from
matter to the neighbouring \(a\) qubits satisfies Eq. (7).  Measuring the
\(a\)'s then produces the usual toric-code gauging construction.  The paper
uses the same architecture for a less elementary symmetry: logical
controlled-\(Z\) on the two toric codes.

## Attaching the controlled-\(Z\) symmetry with CCZ gates

For the present problem \(U=U_{\mathrm{CZ}}\), the finite-depth circuit that
implements the anyon relabelling described in Section II.A.  The appropriate
three-qubit gate is

\[
\operatorname{CCZ}_{abc}\lvert x_a x_b x_c\rangle
=(-1)^{x_ax_bx_c}\lvert x_a x_b x_c\rangle.
\tag{9}
\]

It is diagonal, and it has the following especially important conjugation
identities:

\[
\begin{aligned}
\operatorname{CCZ}_{abc}X_a\operatorname{CCZ}_{abc}
 &=X_a\operatorname{CZ}_{bc},\\
\operatorname{CCZ}_{abc}X_b\operatorname{CCZ}_{abc}
 &=X_b\operatorname{CZ}_{ac}.
\end{aligned}
\tag{10}
\]

The first follows directly by comparing the phase before and after flipping
\(x_a\): their ratio is \((-1)^{x_bx_c}\), which is exactly the phase of a
\(\operatorname{CZ}_{bc}\).  The second identity is the same statement with
the labels exchanged.  Every \(Z\) operator is unchanged because CCZ is
diagonal.

The paper chooses a local pattern of CCZ gates.  Each gate has one \(a\)
vertex as its control and targets one nearby \(B\) edge and one nearby \(C\)
edge.  Denote the set of \(B\)--\(C\) pairs coupled to vertex \(v\) by
\(\mathcal P(v)\), and write

\[
\Omega_{aBC}=
\prod_v\prod_{(b,c)\in\mathcal P(v)}
\operatorname{CCZ}_{vbc}.
\tag{11}
\]

The diagrams in the paper specify \(\mathcal P(v)\).  What matters for the
derivation is that, across all vertices, each controlled-\(Z\) gate in
\(U_{\mathrm{CZ}}\) occurs exactly once.  Equation (10) then gives

\[
\Omega_{aBC}X_v^a\Omega_{aBC}^\dagger
=X_v^a\prod_{(b,c)\in\mathcal P(v)}\operatorname{CZ}_{bc}.
\tag{12}
\]

Multiplying Eq. (12) over all vertices yields the promised symmetry
enrichment condition,

\[
\Omega_{aBC}G_a\Omega_{aBC}^\dagger
=G_aU_{\mathrm{CZ}}.
\tag{13}
\]

This is the central derivation of Section II.B.  A CCZ gate is not chosen by
analogy: it is chosen because conjugating its \(X\) on the \(a\) leg literally
creates the desired CZ on the \(B,C\) legs.

## What survives the \(X^a\) measurements

We can now track the stabilizers.  This is a good place to distinguish two
simple rules.

- A stabilizer with no \(a\)-support commutes with the measurement and is
  retained immediately.
- A stabilizer containing \(X_v^a\) also commutes with the \(X_v^a\)
  measurement; after projection its \(X_v^a\) can be replaced by \(+1\).

An operator containing a lone \(Z_v^a\) anticommutes with that measurement,
so it cannot be retained by itself.  We must multiply such relations
together, or rewrite them using other stabilizers, until their \(a\)
dependence cancels.

### Diagonal plaquette relations

We first make the notation completely explicit. A **plaquette** \(p\) is one
elementary square. Its boundary, written \(\partial p\), is the closed loop
made from its four sides. Hence \(e\in\partial p\) means that \(e\) is one of
the four lattice edges lying along the perimeter of \(p\), and
\(\prod_{e\in\partial p}\) means to multiply one operator for each of those
four edges.

For corners \(v_1,v_2,v_3,v_4\), name the four sides
\(\partial p=\{e_{12},e_{23},e_{34},e_{41}\}\). Then the compact notation
expands to

\[
\prod_{e\in\partial p}Z_e^B
=Z_{e_{12}}^B Z_{e_{23}}^B Z_{e_{34}}^B Z_{e_{41}}^B.
\tag{14a}
\]

The superscript specifies the layer: the same geometrical square has a
\(B\)-plaquette operator, a \(C\)-plaquette operator, and, after gauging, an
\(A\)-plaquette operator.

We also need a precise meaning of “survives the measurements.” Let
\(\lvert\Psi\rangle\) be the state immediately before measuring the \(a\)
qubits. Conditioning on a \(+1\) result for every \(X_v^a\) applies

\[
P_+=\prod_v\frac{1+X_v^a}{2}.
\tag{14b}
\]

Thus the unnormalised post-measurement state is \(P_+\lvert\Psi\rangle\).
If a pre-measurement stabilizer \(S\) obeys
\(S\lvert\Psi\rangle=\lvert\Psi\rangle\) and commutes with \(P_+\), then

\[
S P_+\lvert\Psi\rangle
=P_+S\lvert\Psi\rangle
=P_+\lvert\Psi\rangle.
\tag{14c}
\]

So \(S\) remains a \(+1\) constraint on the projected state. This, rather
than simply being “left over,” is what we mean by *survives*.

CCZ is diagonal in the computational basis and therefore commutes with every
\(Z\) operator. The enrichment circuit \(\Omega_{aBC}\) leaves the old
\(B\)- and \(C\)-plaquette stabilizers unchanged. They act only on \(B\) or
\(C\) qubits, while \(P_+\) acts only on \(a\) qubits, so they commute with
\(P_+\). Equation (14c) therefore proves that the projected state obeys

\[
B_p^B=\prod_{e\in\partial p}Z_e^B,
\qquad
B_p^C=\prod_{e\in\partial p}Z_e^C.
\tag{14}
\]

The \(A\)-layer relation needs one more step. The pre-measurement cluster
stabilizer on an \(A\) edge \(e=(v,w)\) is

\[
K_e^A=Z_v^aZ_e^AZ_w^a.
\tag{14d}
\]

It too is unchanged by \(\Omega_{aBC}\), because CCZ is diagonal. But
\(K_e^A\) does **not** survive by itself: it contains \(Z_v^a\) and
\(Z_w^a\), which anticommute with the \(X^a\) measurements at their
respective vertices. Equivalently, it does not commute with \(P_+\).

Now multiply these edge relations around the closed boundary of a single
plaquette. With the labels introduced above,

\[
\begin{aligned}
\prod_{e\in\partial p}K_e^A
&=(Z_{v_1}^aZ_{e_{12}}^AZ_{v_2}^a)
  (Z_{v_2}^aZ_{e_{23}}^AZ_{v_3}^a)
  (Z_{v_3}^aZ_{e_{34}}^AZ_{v_4}^a)
  (Z_{v_4}^aZ_{e_{41}}^AZ_{v_1}^a)\\
&=(Z_{v_1}^a)^2(Z_{v_2}^a)^2
  (Z_{v_3}^a)^2(Z_{v_4}^a)^2\,
  Z_{e_{12}}^AZ_{e_{23}}^AZ_{e_{34}}^AZ_{e_{41}}^A\\
&=\prod_{e\in\partial p}Z_e^A.
\end{aligned}
\tag{14e}
\]

Every corner lies on exactly two sides of the square. Hence every \(Z_v^a\)
appears twice and cancels because \((Z_v^a)^2=1\). The final operator has no
\(a\)-support, hence it commutes with \(P_+\). The criterion in Eq. (14c)
therefore proves that the projected state satisfies

\[
B_p^A=\prod_{e\in\partial p}Z_e^A.
\tag{15}
\]

This is the magnetic-flux, or plaquette, constraint for the newly created
\(A\) gauge field. The contrast is essential: an open edge relation
\(K_e^A\) is incompatible with the \(X^a\) measurement, but the closed
product of four such relations is compatible because all dependence on the
discarded \(a\) qubits cancels exactly.

### The dressed \(A\)-star constraint

The enriched version of the first cluster stabilizer in Eq. (1) is immediate
from Eq. (12):

\[
\widetilde K_v^a
=X_v^a\left(\prod_{e\ni v}X_e^A\right)
\left(\prod_{(b,c)\in\mathcal P(v)}\operatorname{CZ}_{bc}\right).
\tag{16}
\]

It commutes with the measurement, so applying Eq. (8) gives the surviving
constraint

\[
\widetilde A_v^A
=\left(\prod_{e\ni v}X_e^A\right)
\left(\prod_{(b,c)\in\mathcal P(v)}\operatorname{CZ}_{bc}\right).
\tag{17}
\]

Without the second factor, this is the usual toric-code star: it flips the
four gauge bits adjacent to \(v\).  The product of CZ gates dresses that flip
by a local transformation of the \(B,C\) matter.  This is the microscopic
form of the slogan that an \(A\)-gauge transformation carries the old
controlled-\(Z\) symmetry along with it.

### Why the \(B\)- and \(C\)-star constraints take more work

This is the only genuinely delicate measurement update in the construction,
so we now do it completely for one representative \(B\)-star.  Every other
\(B\)-star is a translate or rotation of this calculation.  The \(C\)-star
calculation is the same with \(B\) and \(C\) interchanged.

Let \(A_v^B\) be the ordinary \(B\)-code star centered at \(v\).  Near it,
label the four \(C\)-edge qubits on the relevant neighbouring \(C\)
plaquette by \(c_1,c_2,c_3,c_4\), in cyclic order.  The CCZ incidence pattern
in the paper has three nearby disposable vertex qubits:

\[
\begin{array}{c|c}
\text{vertex ancilla} & \text{controlled-Z factors attached after CCZ conjugation}\\
\hline
a_{12} & \operatorname{CZ}_{a_{12},c_1}\operatorname{CZ}_{a_{12},c_2}\\
a_3 & \operatorname{CZ}_{a_3,c_3}\\
a_4 & \operatorname{CZ}_{a_4,c_4}.
\end{array}
\tag{18}
\]

The subscripts are labels, not powers.  They describe the local pattern:
\(a_{12}\) is attached to the two \(C\) edges \(c_1,c_2\), while \(a_3\) and
\(a_4\) are attached to \(c_3\) and \(c_4\), respectively.  Let \(A_3\) and
\(A_4\) be the two \(A\)-edge qubits connecting \(a_{12}\) to \(a_3\) and to
\(a_4\).  This is exactly the part of the incidence diagram used in the
paper's rewrite.

For any qubit \(q\), define its computational-basis occupation number by

\[
n_q=\frac{1-Z_q}{2}.
\tag{19}
\]

It is \(0\) on a \(Z_q=+1\) state and \(1\) on a \(Z_q=-1\) state.  Therefore

\[
\operatorname{CZ}_{r,s}=Z_r^{\,n_s}.
\tag{20}
\]

The enriched \(B\)-star is consequently

\[
\begin{aligned}
S_v^B
&=A_v^B
\operatorname{CZ}_{a_{12},c_1}
\operatorname{CZ}_{a_{12},c_2}
\operatorname{CZ}_{a_3,c_3}
\operatorname{CZ}_{a_4,c_4}\\
&=A_v^B
Z_{a_{12}}^{\,n_{c_1}+n_{c_2}}
Z_{a_3}^{\,n_{c_3}}
Z_{a_4}^{\,n_{c_4}}.
\end{aligned}
\tag{21}
\]

The first line is the post-CCZ stabilizer; the second line is only the
identity (20) applied four times.  At this stage the operator cannot be
kept after an \(X^a\) measurement: it contains \(Z\)'s on the measured
qubits \(a_{12},a_3,a_4\).

The cluster state supplies the way to remove them.  Its edge stabilizers on
\(A_3\) and \(A_4\) say

\[
Z_{a_{12}}^a Z_{A_3}^A Z_{a_3}^a=1,
\qquad
Z_{a_{12}}^a Z_{A_4}^A Z_{a_4}^a=1.
\tag{22}
\]

Equivalently,

\[
Z_{a_3}^a=Z_{a_{12}}^aZ_{A_3}^A,
\qquad
Z_{a_4}^a=Z_{a_{12}}^aZ_{A_4}^A.
\tag{23}
\]

Substitute Eq. (23) into Eq. (21).  The two endpoint \(a\)-variables are
moved onto the two \(A\) edges, and all remaining \(a\)-dependence collects
at the single vertex \(a_{12}\):

\[
S_v^B
=A_v^B
\left(Z_{a_{12}}^a\right)^{n_{c_1}+n_{c_2}+n_{c_3}+n_{c_4}}
\left(Z_{A_3}^A\right)^{n_{c_3}}
\left(Z_{A_4}^A\right)^{n_{c_4}}.
\tag{24}
\]

The first factor in Eq. (24) looks troublesome, but it is actually the
existing \(C\)-plaquette constraint in disguise.  Write
\(n_{a_{12}}=(1-Z_{a_{12}}^a)/2\).  On a computational-basis state,

\[
\begin{aligned}
\left(Z_{a_{12}}^a\right)^{\sum_{i=1}^4n_{c_i}}
&=(-1)^{n_{a_{12}}\sum_{i=1}^4n_{c_i}}\\
&=\prod_{i=1}^4\left(Z_{c_i}^C\right)^{n_{a_{12}}}\\
&=\left(\prod_{i=1}^4Z_{c_i}^C\right)^{n_{a_{12}}}
=\left(B_p^C\right)^{n_{a_{12}}}=1.
\end{aligned}
\tag{25}
\]

The penultimate equality uses the fact that \(c_1,\ldots,c_4\) form the
boundary of that \(C\) plaquette \(p\).  The final equality is legitimate on
the code state because \(B_p^C=+1\), and Section 2.5.1 proved that this
plaquette stabilizer is still valid after the \(a\)-measurements.

Removing the identity factor in Eq. (25) leaves an operator with no
\(a\)-support:

\[
\begin{aligned}
\widetilde A_v^B
&=A_v^B
\left(Z_{A_3}^A\right)^{n_{c_3}}
\left(Z_{A_4}^A\right)^{n_{c_4}}\\
&=A_v^B\,
\operatorname{CZ}_{A_3,c_3}
\operatorname{CZ}_{A_4,c_4}.
\end{aligned}
\tag{26}
\]

Equation (26) is the explicit final dressed \(B\)-star represented by the
paper's diagram.  It commutes with every \(X^a\) measurement because it
contains no \(a\) qubit at all.  The old \(B\)-star is therefore not
discarded; it is converted into a gauge-invariant local constraint whose
two control qubits are now physical \(A\)-gauge-field edges.

For a different \(B\)-star, the names \(A_3,A_4,c_3,c_4\) change according to
translation or rotation.  A notation that covers every location is

\[
\widetilde A_v^B
=A_v^B\prod_{(A_e,c)\in\mathcal Q_B(v)}
\operatorname{CZ}_{A_e,c},
\tag{27}
\]

where \(\mathcal Q_B(v)\) is the local pair of \(A\)- and \(C\)-edge qubits
read from the translated incidence pattern.  In the representative above,
\(\mathcal Q_B(v)=\{(A_3,c_3),(A_4,c_4)\}\).

Repeating the same four steps for a \(C\)-star gives

\[
\widetilde A_w^C
=A_w^C\prod_{(A_e,b)\in\mathcal Q_C(w)}
\operatorname{CZ}_{A_e,b}.
\tag{28}
\]

Here the opposite-code edges \(b\) belong to the \(B\) layer, and the
residual \(a\)-factor is removed by the neighbouring \(B\)-plaquette
constraint \(B_p^B=+1\).  Thus the two derivations are exact layer-swapped
copies of each other.

## The final stabilizer structure and what is unusual about it

After the projection, the state is characterized locally by three diagonal
plaquette families,

\[
B_p^A,\qquad B_p^B,\qquad B_p^C,
\tag{22}
\]

and three dressed star families,

\[
\widetilde A_v^A,\qquad
\widetilde A_v^B,\qquad
\widetilde A_v^C.
\tag{23}
\]

The tildes matter.  These are no longer Pauli stabilizers in the elementary
toric-code sense, because they contain controlled-\(Z\) factors.  In
particular, two bare-looking \(X\)-type constraints need not commute as
literal operators.  Instead, as the paper notes, interchanging two of them
can produce a product \(Q\) of the diagonal plaquette constraints:

\[
S_iS_j=S_jS_iQ.
\tag{24}
\]

On a physical ground state, every such \(Q\) has eigenvalue \(+1\), so the
two orders act identically there.  This is why the construction is
consistent even though its local terms are not simply a mutually commuting
Pauli stabilizer group.  Put differently, the diagonal flux constraints
carry exactly the bookkeeping needed to make the dressed gauge constraints
compatible.

The output is the lattice realization of the gauged phase discussed in
Section II.A: the \(A\) field supplies dynamical symmetry-defect strings,
and its flux endpoints enact the controlled-\(Z\)-induced relabelling of
\(B,C\) anyons.  The construction is therefore a preparation of the
\(\mathcal D(D_4)\) topological order, not merely three independent toric
codes.

## The construction in one line per stage

\[
\begin{array}{rcl}
\text{cluster resource} && \text{encodes ``symmetry patch = }A\text{ boundary''},\\
\Omega_{aBC} && \text{changes that symmetry into }G_aU_{\mathrm{CZ}},\\
X^a\text{ measurement} && \text{removes }a\text{ and leaves }A\text{ as the gauge field}.
\end{array}
\]

The first stage supplies the geometry, the second supplies the desired anyon
automorphism, and the third turns the formerly imposed symmetry patch into a
dynamical gauge configuration.  That is the entire logical skeleton of
Section II.B.  We now replace its ideal postselection by the actual,
random-outcome measurement procedure of Section II.C.

## Section II.C: preparation by measurement and feedforward

### What has to be fixed

Up to now we pretended that every measurement of \(X_v^a\) gave the outcome
\(+1\).  That is useful for deriving the code, but it is not a preparation
protocol: quantum measurements do not allow us to choose their outcomes.
Section II.C makes the construction deterministic:

1. Measure all disposable \(a\) qubits in the \(X\) basis.
2. Treat the pattern of negative outcomes as a syndrome.
3. Apply a Pauli correction on the unmeasured \(A\) qubits.

The correction removes *only Abelian electric charges* of the new \(A\)
gauge field.  It does not have to undo, or even identify, any non-Abelian
excitation.  This is why ordinary decoder-style feedforward is enough.

### Keep the measurement record instead of postselecting it

Write the outcome at \(a\)-vertex \(v\) as a bit \(s_v\in\{0,1\}\):

\[
X_v^a=(-1)^{s_v}.
\tag{32}
\]

Thus \(s_v=0\) denotes the old \(+1\) branch, whereas \(s_v=1\) denotes a
\(-1\) outcome.  The projector onto the complete outcome record
\(s=\{s_v\}\) is

\[
P_s=\prod_v\frac{1+(-1)^{s_v}X_v^a}{2}.
\tag{33}
\]

If \(\lvert\Psi\rangle\) is the state immediately before these
measurements, write the normalised branch state as
\(\lvert\psi_s\rangle\propto P_s\lvert\Psi\rangle\).  The outcome bits are
classical information; the \(a\) qubits do not remain part of the code.

### A negative outcome is exactly an \(e_A\) excitation

Before measuring, Eq. (16) gave the enriched vertex stabilizer

\[
\widetilde K_v^a=X_v^a\widetilde A_v^A,
\qquad
\widetilde K_v^a\lvert\Psi\rangle=\lvert\Psi\rangle.
\tag{34}
\]

Here \(\widetilde A_v^A\) is the dressed \(A\)-star from Eq. (17).  It acts
only on retained qubits, so it commutes with \(P_s\).  Use this and Eq. (34):

\[
\begin{aligned}
\widetilde A_v^A P_s\lvert\Psi\rangle
 &=X_v^a\widetilde K_v^aP_s\lvert\Psi\rangle\\
 &=X_v^aP_s\lvert\Psi\rangle\\
 &=(-1)^{s_v}P_s\lvert\Psi\rangle.
\end{aligned}
\tag{35}
\]

After normalisation,

\[
\widetilde A_v^A\lvert\psi_s\rangle
=(-1)^{s_v}\lvert\psi_s\rangle.
\tag{36}
\]

This is the complete syndrome calculation.  In a toric code, an electric
anyon \(e\) at a vertex is defined by a \(-1\) eigenvalue of the star
constraint at that vertex.  Equation (36) is the identical definition for
the new, dressed gauge field: every \(s_v=1\) marks an \(e_A\) charge at
\(v\).  No \(A\)-plaquette, \(B\)-plaquette, or \(C\)-plaquette eigenvalue is
flipped.  In particular, the random measurements do not create an
\(m_A\) flux, the excitation responsible for the type-changing braiding in
Section II.A.

Although \(\widetilde A_v^A\) contains CZ gates on \(B,C\), its eigenvalue is
still a single \(\mathbb Z_2\) sign.  The charge \(e_A\) is therefore
Abelian, exactly as stated in the paper.

### The correction string, derived operator by operator

Choose a collection \(\gamma\) of \(A\)-edges.  Its boundary
\(\partial\gamma\) is the set of vertices incident on an odd number of
chosen edges:

\[
(\partial\gamma)_v=
\sum_{e\ni v}\gamma_e\pmod 2,
\qquad \gamma_e\in\{0,1\}.
\tag{37}
\]

If \(\gamma\) is a path, every interior vertex touches two chosen edges and
drops out modulo two; only its endpoints lie in \(\partial\gamma\).  Apply
the Pauli string

\[
R_\gamma=\prod_{e:\,\gamma_e=1}Z_e^A.
\tag{38}
\]

Each \(Z_e^A\) anticommutes with the \(X_e^A\) in the dressed star at the
endpoints of \(e\), and commutes with all CZ dressing factors because they
are diagonal.  Hence

\[
\widetilde A_v^A R_\gamma
=(-1)^{(\partial\gamma)_v}R_\gamma\widetilde A_v^A.
\tag{39}
\]

Read Eq. (39) literally: \(R_\gamma\) flips the star eigenvalue precisely at
the vertices in \(\partial\gamma\), and nowhere else.  It commutes with the
plaquette constraints because they are products of \(Z\)'s (or do not act on
\(A\)).  It also commutes with the dressed \(B\)- and \(C\)-stars: their
\(A\)-dependent parts are diagonal CZ gates, while their \(X\)'s act on
\(B\) or \(C\), not on \(A\).

Let a classical decoder choose \(\gamma\) so that

\[
\partial\gamma=s.
\tag{40}
\]

In words: pair the vertices with negative measurement outcomes and draw an
\(A\)-edge path for each pair.  Then

\[
\begin{aligned}
\widetilde A_v^A R_\gamma\lvert\psi_s\rangle
&=(-1)^{(\partial\gamma)_v}R_\gamma
  \widetilde A_v^A\lvert\psi_s\rangle\\
&=(-1)^{s_v}(-1)^{s_v}R_\gamma\lvert\psi_s\rangle\\
&=R_\gamma\lvert\psi_s\rangle.
\end{aligned}
\tag{41}
\]

Thus \(R_\gamma\lvert\psi_s\rangle\) has the desired \(+1\) \(A\)-star
eigenvalue at every vertex.  Since the other final constraints were
unaffected, it is the desired \(\mathcal D(D_4)\) ground state in the chosen
global sector.

### Why the charges can be paired

On a closed lattice, local \(e_A\) charges cannot occur singly: the allowed
syndrome has even total parity in the sector prepared here, so its vertices
can be partitioned into pairs.  This is why Eq. (40) has a solution made
from open paths.  It is the familiar toric-code fact that a \(Z\) string has
two endpoints, never one.

For a finite lattice with boundaries, a path may instead end at a boundary
that condenses \(e_A\).  On a torus, two pairing choices can differ by a
closed noncontractible \(Z_A\) loop.  This is a logical operator, so a
decoder must use a convention (or track a logical frame) to prepare a
specified ground-state sector.

The paper calls this a finite-depth adaptive circuit.  Once a correction is
chosen, every factor in Eq. (38) is a single-qubit \(Z\) gate, so all of them
can be applied simultaneously in one quantum layer, irrespective of path
length.  Finding a good pairing from a noisy syndrome is the separate
classical decoding problem.

### The deterministic adaptive circuit

Section II.C is therefore the following procedure:

\[
\begin{array}{rcl}
\text{prepare cluster state and the two toric-code states}
&\longrightarrow& \Omega_{aBC}\\
&\longrightarrow& \text{measure all }X_v^a\text{ and record }s\\
&\longrightarrow& \text{classically choose }\gamma\text{ with }\partial\gamma=s\\
&\longrightarrow& R_\gamma=\prod_{e\in\gamma}Z_e^A.
\end{array}
\tag{42}
\]

The first two stages are fixed finite-depth circuits, and all \(X^a\)
measurements are parallel.  The final operation depends on the recorded
outcomes: that dependence is the *feedforward*.  It replaces the
unphysical instruction “keep only the all-\(+1\) branch” with a procedure
that succeeds for every allowed record.

This completes Section II.C.  Its role is narrow but crucial: Section II.B
constructs the desired phase in an ideal measurement branch; Section II.C
shows that branch randomness only creates correctable Abelian \(e_A\)
excitations, so the preparation is deterministic.

## What exactly is the \(\mathcal D(D_4)\) quantum double?

This section fills in the name that has appeared throughout the discussion.
The short answer is that \(\mathcal D(D_4)\) is a particular non-Abelian
topological order: it is the quantum-double gauge theory whose finite gauge
group is the eight-element symmetry group of a square.  It has 22 anyon
types on the plane and consequently 22 ground states on a torus.

There are two closely related uses of the phrase *quantum double*, which are
worth separating.

- Kitaev's **quantum-double lattice model** is a solvable gauge-theory
  Hamiltonian built from a finite group \(G\).
- \(\mathcal D(G)\), also called the Drinfeld double of \(G\), denotes the
  topological order — equivalently, the complete fusion and braiding data —
  of that model.

Thus the statement “the construction gives \(\mathcal D(D_4)\)” does *not*
mean that every displayed local term has to look like the textbook
group-element Hamiltonian.  It means that, at long distances, the
superselection sectors and their fusion and braiding are those of the
\(D_4\) quantum double.

### First reminder: the ordinary finite-group quantum double

For a finite group \(G\), put a \(G\)-valued degree of freedom
\(\lvert h_e\rangle\), \(h_e\in G\), on each oriented lattice edge.  Reversing
the orientation replaces \(h_e\) by \(h_e^{-1}\).  The standard
quantum-double Hamiltonian has two kinds of local constraints:

\[
H_{D(G)}=-\sum_v A_v-\sum_p B_p.
\tag{43}
\]

The plaquette term \(B_p\) checks **flatness**.  If the oriented boundary
edges of \(p\) carry \(h_1,\ldots,h_n\), it keeps precisely the states with

\[
h_1h_2\cdots h_n=1_G.
\tag{44}
\]

The vertex term \(A_v\) imposes **gauge invariance**.  More precisely,
\(A_v\) is the average over all local gauge transformations:

\[
A_v=\frac{1}{|G|}\sum_{g\in G}A_v^g.
\tag{45}
\]

Here \(A_v^g\) multiplies every edge variable leaving \(v\) by \(g\), and
every edge variable entering \(v\) by \(g^{-1}\).  The two requirements,
flatness and gauge invariance, are the group-valued analogues of the
plaquette and star constraints of the toric code.

For \(G=\mathbb Z_2=\{1,-1\}\), Eq. (44) becomes the usual \(Z\)-plaquette
constraint and Eq. (45) becomes the usual \(X\)-star constraint.  Thus

\[
\text{toric code}=\mathcal D(\mathbb Z_2).
\tag{46}
\]

This is the reason it was natural to describe the two \(B,C\) toric codes
as an Abelian \(\mathbb Z_2\times\mathbb Z_2\) starting point.

### Flux and charge labels in \(\mathcal D(G)\)

An anyon in \(\mathcal D(G)\) carries two related pieces of information:

\[
\boxed{\quad \text{anyon type} =([h],\pi).\quad}
\tag{47}
\]

The first label \([h]\) is the **conjugacy class** of a group element \(h\):

\[
[h]=\{ghg^{-1}:g\in G\}.
\tag{48}
\]

It is the gauge-invariant version of magnetic flux.  A local gauge
transformation changes a particular representative \(h\) by conjugation, so
only its whole conjugacy class is observable.

The second label \(\pi\) is an irreducible representation of the
**centralizer**

\[
C_h=\{g\in G:gh=hg\}.
\tag{49}
\]

This is the allowed electric charge attached to that flux.  A particle with
no flux has \(h=1\), hence \(C_1=G\), so its pure electric charges are the
ordinary irreducible representations of \(G\).

The quantum dimension is

\[
d_{([h],\pi)}=|[h]|\,\dim\pi.
\tag{50}
\]

This one formula shows where non-Abelian particles come from.  A dimension
larger than one can arise because a flux has several gauge-related
representatives (\(|[h]|>1\)), because it carries a multidimensional charge
representation (\(\dim\pi>1\)), or both.

For an Abelian group all conjugacy classes have one element, every
centralizer is the whole group, and every irreducible representation is
one-dimensional.  Equation (50) then gives \(d=1\) for every anyon.  This
recovers the fact that all toric-code anyons are Abelian.

### The group \(D_4\)

The convention in both papers is

\[
D_4=\langle r,s\mid r^4=s^2=1,\ srs=r^{-1}\rangle.
\tag{51}
\]

Geometrically, \(r\) is a quarter-turn of a square and \(s\) is a reflection.
The elements are

\[
\{1,r,r^2,r^3,s,rs,r^2s,r^3s\}.
\tag{52}
\]

The notation varies in the literature: some authors call this eight-element
group \(D_8\), because it has eight elements.  This note follows the
notation of the two local papers: \(D_4\) means the symmetry group of the
four-sided square, hence \(|D_4|=8\).

The relevant conjugacy classes and centralizers are:

\[
\begin{array}{c|c|c|c|c}
\text{flux class }[h] & |[h]| & C_h
&\text{number of irreps of }C_h
&\text{anyon dimensions in this row}\\
\hline
\{1\} &1&D_4&5&1,1,1,1,2\\
\{r^2\}&1&D_4&5&1,1,1,1,2\\
\{r,r^3\}&2&\mathbb Z_4&4&2,2,2,2\\
\{s,r^2s\}&2&\mathbb Z_2^2&4&2,2,2,2\\
\{rs,r^3s\}&2&\mathbb Z_2^2&4&2,2,2,2
\end{array}
\tag{53}
\]

There are \(5+5+4+4+4=22\) rows-with-charge-labels, so
\(\mathcal D(D_4)\) has **22 anyon types**.  As a check, their dimensions
satisfy

\[
\sum_a d_a^2=|D_4|^2=8^2=64.
\tag{54}
\]

The total quantum dimension is therefore \(\mathcal D_{\rm total}=8\).  On a
torus, the ground-state degeneracy of a quantum double equals the number of
anyon types, explaining the number 22 that appears in the paper and in the
trapped-ion experiment.

The two-dimensional entries in Eq. (53) are already enough to establish
non-Abelian order.  For example, the pure charge associated with the unique
two-dimensional irrep of \(D_4\) has \(d=2\), even though its flux is
trivial.  The word “flux” should therefore not be used as a synonym for
“non-Abelian anyon”: \(\mathcal D(D_4)\) contains non-Abelian charges,
non-Abelian fluxes, and flux-charge composites.

### How the Section II.A--II.C derivation reaches this phase

The derivation in this note does not begin by putting eight-level \(D_4\)
variables on edges.  Instead it starts from qubits and proceeds through

\[
\underbrace{\mathcal D(\mathbb Z_2)\times\mathcal D(\mathbb Z_2)}
_{\text{two Abelian toric codes}}
\quad\xrightarrow[\text{anyon-permuting }\,\mathbb Z_2]{\text{gauge}}
\quad
\mathcal D(D_4).
\tag{55}
\]

There are three concrete stages behind this arrow.

1. **The starting Abelian order.**  \(B\) and \(C\) each contribute a
   \(\mathbb Z_2\) gauge sector.  Before gauging, every excitation has
   dimension one.

2. **A nontrivial action on the anyons.**  The controlled-\(Z\) circuit
   fixes \(e_B,e_C\) but acts as

   \[
   m_B\mapsto m_Be_C,\qquad m_C\mapsto m_Ce_B.
   \tag{56}
   \]

   This is not merely a phase symmetry.  It changes the superselection label.
   Its defect line is therefore a type-changing line.

3. **Gauging the symmetry.**  The \(A\) qubits make that defect line
   dynamical.  An \(A\)-flux endpoint is now a genuine excitation, and
   transporting an old \(B,C\) excitation around it enacts Eq. (56).
   Because \(m_B\) and \(m_Be_C\) belong to one gauge orbit, the resulting
   gauge-invariant object carries a two-component internal space.  This is
   the physical counterpart of a dimension-two entry in Eq. (53).

The semidirect-product identity

\[
D_4\cong(\mathbb Z_2\times\mathbb Z_2)\rtimes\mathbb Z_2
\tag{57}
\]

is a compact group-theory mnemonic for the outcome: the added
\(\mathbb Z_2\) does not remain an independent commuting factor.  A useful
explicit realization takes two commuting involutions \(x,y\) and an
involution \(t\) which swaps them,

\[
x^2=y^2=t^2=1,\qquad xy=yx,\qquad txt=y,\quad tyt=x.
\tag{58}
\]

Then \(xt\) has order four because \((xt)^2=xy\), so the group is
non-Abelian and isomorphic to \(D_4\).

Equation (57) should not be read too literally as a statement about an
individual \(B\)- or \(C\)-edge variable: Eq. (56) is an automorphism of the
*anyon theory* and mixes a magnetic label with an electric label.  The
precise conclusion of the lattice derivation is that, after gauging, the
resulting topological order has the \(\mathcal D(D_4)\) anyon data.  The
semidirect product is the group-theoretic presentation that records the
nontrivial extension, not a replacement for the stabilizer calculation in
Section II.B.

Section II.B provides the microscopic constraints that realize this arrow:
the diagonal plaquettes are the flatness-type constraints, while the dressed
stars are the gauge-invariance-type constraints.  Their CZ decorations are
the local memory of Eq. (56).  Section II.C then makes the preparation
deterministic: a \(-1\) \(X^a\) result gives only an Abelian \(e_A\) charge,
and a \(Z_A\) string removes it.  In particular, the feedforward corrects
preparation byproducts; it does not remove the intended non-Abelian
\(A\)-flux sectors.

### Relationship to arXiv:2305.03766

The local paper [arXiv-2305.03766v2](../arXiv-2305.03766v2/main.tex),
*Non-Abelian Topological Order and Anyons on a Trapped-Ion Processor*, is an
experimental realization of the same \(\mathcal D(D_4)\) topological order.
It prepared a 27-qubit kagome-lattice state on Quantinuum's H2 trapped-ion
processor and used braiding and torus-sector tests to probe its non-Abelian
properties.  The connection is direct at the level of the phase, but the
two works use different microscopic presentations:

\[
\begin{array}{c|c|c}
&\text{this note / arXiv:2602.12228}&\text{arXiv:2305.03766}\\
\hline
\text{starting point}
&\text{two toric codes plus an }A\text{ gauge field}
&\text{a type-III }\mathbb Z_2^3\text{ SPT construction}\\
\text{geometrical lattice}
&\text{three square-lattice sublattices}
&\text{kagome lattice}\\
\text{nontrivial local factor}
&\text{CCZ enrichment, then CZ-dressed stars}
&\text{CZ-dressed 12-body stars}\\
\text{measurement byproduct}
&e_A\text{ charges corrected by }Z_A\text{ strings}
&\text{Abelian star excitations corrected by }Z\text{ strings}\\
\text{long-distance order}
&\mathcal D(D_4)
&\mathcal D(D_4)
\end{array}
\tag{59}
\]

The apparently different “gauge group” language is not a contradiction.
The experimental paper writes its kagome Hamiltonian as a **type-III twisted
quantum double**

\[
\mathcal D^\alpha(\mathbb Z_2^3),\qquad
\alpha(a,b,c)=(-1)^{\rho_a\gamma_b\beta_c},
\tag{60}
\]

where \(a=R^{\rho_a}G^{\gamma_a}B^{\beta_a}\).  Without the CZ factors in
its star operators, its three colours would be three decoupled toric codes,
namely an untwisted \(\mathbb Z_2^3\) gauge theory.  The type-III twist makes
the fluxes carry projective, sometimes two-dimensional, internal
representations.  Thus an Abelian-looking input group can nevertheless
produce non-Abelian anyons.

Crucially, the experimental paper gives an explicit anyon table identifying
its \(\mathcal D^\alpha(\mathbb Z_2^3)\) anyons with the
\(\mathcal D(D_4)\) labels of Eq. (47).  This is a **braided equivalence**:
the two descriptions have the same anyon types, quantum dimensions, fusion
rules, and braiding data.  It is not a claim that
\(\mathbb Z_2^3\cong D_4\); those groups are plainly different, since the
former is Abelian and the latter is not.

For instance, the experiment uses three dimension-two non-Abelian bosons
\(m_R,m_G,m_B\).  One of its characteristic fusion rules is

\[
m_B\times m_B
=1+e_R+e_G+e_Re_G.
\tag{61}
\]

The four possible outcomes on the right have total dimension four, matching
\(d_{m_B}^2=2^2\).  Braiding \(m_G\) around \(m_B\) changes their fusion
channel; after the pairs are fused, it can leave Abelian \(e_R\) charges.
This is the same qualitative phenomenon that motivated the “single anyon
on a torus” discussion in Section II.A.

Finally, the measurement-and-feedback logic of arXiv:2305.03766 is almost
the same as Section II.C.  There, \(-1\) outcomes of measured SPT ancillas
signal **Abelian** star excitations, which are paired by conditional
\(Z\)-strings.  Here, Eq. (36) showed that \(-1\) outcomes signal Abelian
\(e_A\) charges, again paired by \(Z_A\)-strings.  Both protocols exploit
the same crucial separation: random measurement outcomes create only
correctable Abelian byproducts, whereas the desired non-Abelian topological
order remains in the unmeasured system.

### What to retain

1. \(\mathcal D(D_4)\) is the non-Abelian quantum double of the eight-element
   dihedral group; it has 22 anyons and torus ground states.
2. Anyons of \(\mathcal D(G)\) are labelled by a flux conjugacy class and a
   charge representation of its centralizer.
3. Dimension-two anyons are the sharp algebraic signature of the
   non-Abelian internal spaces anticipated by the defect-gauging argument.
4. The present derivation and arXiv:2305.03766 realize the same phase by
   different local circuits and lattices.
5. The experimental paper's twisted
   \(\mathcal D^\alpha(\mathbb Z_2^3)\) description is braided-equivalent to
   \(\mathcal D(D_4)\), not an assertion that the two underlying groups are
   isomorphic.

## Section III: from 2D gauging to non-Abelian qLDPC codes

The paper now leaves the square lattice.  This is a real change of setting,
not just a change of notation.  Sections II.A--II.C started with two toric
codes, where vertices, edges, plaquettes, strings, and anyon motion were
visible in ordinary two-dimensional space.  A general qLDPC code still has
local *checks* in the coding-theory sense, but it normally has no embedding
in a fixed-dimensional Euclidean lattice.  One cannot assume that it has
literal plaquettes, geometric paths, or mobile point particles.

The question guiding the rest of the paper is therefore:

\[
\boxed{\quad
\text{Can the measurement-based gauging idea survive after ordinary spatial
geometry is removed?}
\quad}
\tag{62}
\]

The authors' answer is yes, provided that “geometry” is replaced by the
algebraic incidence structure of the code and by a carefully chosen ancillary
gauge system.  This opening section announces the two ways they do so.

### What a qLDPC code supplies, and what it does not

For the purposes of this paper, an Abelian CSS qLDPC code supplies:

- physical qubits;
- a sparse family of \(X\)-type checks and a sparse family of \(Z\)-type
  checks;
- commutation between every \(X\)-check and every \(Z\)-check;
- logical operators and, sometimes, transversal logical Clifford gates.

“Low density” means that each check acts on only \(O(1)\) qubits and each
qubit occurs in only \(O(1)\) checks as the code grows.  This is the
coding-theory analogue of locality.  It does **not** mean that the qubits
must lie near one another in a plane or in three-dimensional space.

The 2D toric-code picture had a convenient dictionary:

\[
\begin{array}{c|c}
\text{square-lattice toric code}&\text{general CSS qLDPC code}\\
\hline
\text{edge}&\text{physical qubit}\\
\text{vertex/star}&X\text{-check}\\
\text{plaquette}&Z\text{-check}\\
\text{which qubits touch a vertex or plaquette}
&\text{the check--qubit incidence pattern}\\
\text{boundary of a region}&\text{a relation among checks / an incidence map}
\end{array}
\tag{63}
\]

The final row is the subtle one.  On a square lattice, “the boundary of a
boundary is zero” is visibly why stars and plaquettes commute and why
closed strings have no endpoints.  In a qLDPC code, the same statements are
encoded algebraically.  The next subsection of the paper introduces chain
complexes precisely to record this incidence data without drawing a lattice.

For now, it is enough to keep this distinction in mind:

\[
\text{qLDPC locality} \neq \text{ordinary spatial locality}.
\tag{64}
\]

That distinction is the source of both the difficulty and the novelty of the
paper.  The authors cannot simply copy the red \(A\)-sublattice of the
square-lattice construction.  They must decide what the new gauge degrees
of freedom should be connected to.

### The input is an emergent logical symmetry, not necessarily a Hamiltonian symmetry

The 2D prototype gauged a controlled-\(Z\) circuit \(U_{\mathrm{CZ}}\).
As stressed earlier, this circuit need not leave each microscopic
Hamiltonian term unchanged.  Rather, it maps stabilizers to products of
stabilizers and hence preserves the code subspace.  Such a circuit is an
**emergent symmetry of the encoded information**.

Exactly the same is true here.  Start with two copies, called \(B\) and
\(C\), of an Abelian CSS qLDPC code.  The desired input is a transversal
Clifford gate \(U\) between them:

\[
U=\bigotimes_j U_j,
\tag{65}
\]

where each \(U_j\) has bounded support, often on the corresponding qubits of
the two copies.  “Transversal” is important operationally: even though the
logical action of \(U\) can be global, the physical circuit has constant
depth and preserves the LDPC character of the construction.

The paper distinguishes these gates from the code's usual logical Pauli
operators.  Logical \(X\)- and \(Z\)-operators are often described
algebraically as cycles and cocycles.  They are important symmetries, but
they are **not** the symmetries being gauged here.  The construction instead
gauges a finite-depth transversal *Clifford* operation which acts on the
encoded degrees of freedom, such as:

\[
\mathsf{CZ},\qquad \mathsf{SWAP},\qquad
\text{or, in a different qudit example, charge conjugation.}
\tag{66}
\]

This is the central generalization of Section II:

\[
\boxed{\quad
\text{gauge an encoded transversal gate, rather than a geometrically
onsite microscopic symmetry.}
\quad}
\tag{67}
\]

The distinction matters because it is what makes the proposal relevant to
qLDPC codes.  A good qLDPC code may have no useful Euclidean geometry at all,
yet it can possess a sparse physical implementation of a meaningful logical
Clifford gate.

### The same three-stage mechanism survives

Although the geometry changes, the logical skeleton from Section II remains
unchanged:

\[
\begin{array}{rcl}
\text{ancilla resource state}
&\longrightarrow&
\text{a system with an ancilla symmetry},\\
\text{symmetry enrichment }\Omega
&\longrightarrow&
\Omega G_a\Omega^\dagger=G_aU,\\
X^a\text{ measurement}
&\longrightarrow&
\text{a gauged non-Abelian qLDPC code}.
\end{array}
\tag{68}
\]

Here \(G_a\) denotes a symmetry of the ancilla resource state, and \(U\) is
the transversal gate of the \(B,C\) code pair that we intend to gauge.  The
second line is the same symmetry-enrichment equation encountered in
Eq. (13), now written without assuming a square lattice.

The new ancillary qubits play the role previously held by the \(a\)-vertex
and \(A\)-edge qubits:

- the measured \(a\)-type qubits carry the ancilla symmetry;
- the unmeasured \(A\)-type qubits retain the gauge information after
  measurement;
- \(\Omega\) ties local changes of that ancilla symmetry record to the
  logical gate \(U\) on the code.

The decisive design problem is therefore not “how do we draw the old square
lattice again?”  It is:

\[
\boxed{\quad
\text{Which ancillary incidence structure has the right symmetry to gauge
the chosen }U\text{?}
\quad}
\tag{69}
\]

This is why the paper calls the ancillary degrees of freedom an **ancilla
chain complex** later on.  In the most general language, it is an algebraic
object describing which ancilla checks touch which ancilla qubits.  In a
special case it is literally a graph; in another it can mirror the
chain-complex structure of the input code.

### Why there are two constructions

In two dimensions, the obvious ancillary lattice is a copy of the original
toric-code lattice.  In the qLDPC setting, that choice is sometimes natural
but not always possible or useful.  The authors identify two regimes:

**Homological gauging** requires the input code to have a
Poincare-duality-like algebraic structure.  The ancilla complex is then a
copy of, or close analogue of, the input code's complex.  The payoff is that
the construction can exploit a structured family of transversal gates,
naturally including CZ gates, and can make some of them addressable.  The
price is that a generic qLDPC code need not have the necessary duality.

**Graph gauging** makes no Poincare-duality assumption.  The ancillas instead
form a separately chosen graph.  Its single global symmetry is matched to
one selected transversal gate; transversal SWAP is always available between
two identical code copies.  The payoff is broad applicability.  The price is
that the graph must be tailored to the chosen gate, and it does not
automatically provide the structured family of gates available in the
homological case.

Poincare duality will be defined carefully later.  At this stage, its role
can be stated without technical machinery: it is the extra algebraic
structure that lets the authors identify stabilizer redundancies with a
family of compatible transversal logical gates.  That match allows the
ancilla system to inherit the code's structure and gauge more than one
related symmetry.

Graph gauging makes the opposite choice.  It sacrifices that structured
family in exchange for generality.  A connected graph has one global
\(\mathbb Z_2\) ancilla symmetry, so it is suited to gauging one selected
global \(\mathbb Z_2\) transversal gate.  The paper later shows that this is
enough to gauge transversal SWAP for two copies of essentially any suitable
input code.

The two methods are not competing answers to the same constrained problem.
They answer two different needs:

\[
\begin{array}{c}
\text{Use homological gauging when the code has the needed duality and you
want to exploit it.}\\[3pt]
\text{Use graph gauging when broad applicability to a chosen gate is the
priority.}
\end{array}
\tag{71}
\]

### What “non-Abelian qLDPC code” means here

The phrase should be read with care.  For the toric code, the non-Abelian
claim could be visualized directly through particles moving in a plane and
braiding.  For a generic qLDPC code, there may be no ambient plane in which
to define a conventional braid.  The paper does not claim that every such
code literally realizes a 2D gas of mobile \(D_4\) anyons.

Instead, it constructs codes with non-Pauli, controlled-Clifford dressed
constraints whose ground-state and logical-operator algebra has a
non-Abelian character inherited from gauging \(U\).  Later, in Section IV,
the authors provide an operational diagnostic: suitable logical operations
can create a state with a single violated gauge-charge constraint in a
subsystem-symmetry sector.  This is the qLDPC analogue of the “single anyon
on a torus” phenomenon from Section II.A.

So the logical order of the paper is:

\[
\begin{array}{rcl}
\text{Section III} && \text{construct the gauged qLDPC codes},\\
\text{Section IV} && \text{show their non-Abelian-like physical signatures},\\
\text{Section V} && \text{use gauging and ungauging as logical-gate measurement.}
\end{array}
\tag{72}
\]

The present introduction promises the construction; it does not yet prove
all those later physical claims.

### Road map for the next subsections

The remaining parts of Section III can initially be read with the following
questions in mind:

1. **Toy model:** How can the same stack of toric codes admit two different
   ancilla choices, and what symmetry does each choice gauge?
2. **Chain-complex dictionary:** How are qubits and checks encoded without a
   Euclidean lattice?
3. **General gauging rule:** What condition must \(\Omega\) and the ancilla
   complex satisfy so that an ancilla symmetry becomes \(G_aU\)?
4. **Two constructions:** What additional structure permits homological
   gauging, and how does graph gauging avoid needing it?

For a first pass, the most important result of this introduction is not a
formula.  It is the design principle:

\[
\boxed{\quad
\text{the choice of ancillary gauge structure must match the transversal
logical symmetry one wants to gauge.}
\quad}
\tag{73}
\]

Everything that follows is an increasingly explicit realization of that
principle.

## Section III.A: toy model — the ancilla chooses which symmetry is gauged

The paper's first example is deliberately familiar: take \(N\) independent
two-dimensional toric-code layers, and take two identical stacks of them.
Call the stacks \(B\) and \(C\).  Thus each layer \(\ell=1,\ldots,N\)
contains a pair

\[
\bigl(\text{toric code }B_\ell\bigr)
\quad\text{and}\quad
\bigl(\text{toric code }C_\ell\bigr).
\tag{74}
\]

Nothing initially couples distinct layers.  The full Hamiltonian is simply

\[
H_{\mathrm{in}}
=\sum_{\ell=1}^{N}
\left(H_{\mathrm{TC}}^{B_\ell}+H_{\mathrm{TC}}^{C_\ell}\right).
\tag{75}
\]

This is not yet a non-Abelian model; it is just \(2N\) independent Abelian
toric codes.  The advantage of this example is that we already know how to
gauge a controlled-\(Z\) symmetry for one pair of layers.  We can now ask
the new question in its simplest form:

\[
\text{Should we gauge each layer's symmetry separately, or only one
symmetry acting on the entire stack?}
\tag{76}
\]

The authors show that both choices are legitimate, but they require
different ancillary gauge structures and lead to different physics.

### The symmetry content of the input stack

For each layer, let

\[
U_\ell=U_{\mathrm{CZ}}^{(\ell)}
\tag{77}
\]

denote the controlled-\(Z\) circuit between \(B_\ell\) and \(C_\ell\).  It is
the direct layer-by-layer analogue of the circuit in Section II: within that
layer it permutes the appropriate anyon labels and is an emergent symmetry
of the encoded subspace.

Because the layers are decoupled, the \(N\) operations \(U_\ell\) commute:

\[
[U_\ell,U_{\ell'}]=0\qquad(\ell\ne\ell').
\tag{78}
\]

Each has order two, \(U_\ell^2=1\).  Consequently the stack has a whole
family of possible \(\mathbb Z_2\) symmetries:

\[
\left\{\,\prod_{\ell=1}^{N}U_\ell^{\,q_\ell}
\ \middle|\ q_\ell\in\{0,1\}\right\}
\cong\mathbb Z_2^N.
\tag{79}
\]

Two choices within this family will matter:

\[
\begin{aligned}
\text{layer-resolved generators:}\qquad
&U_1,U_2,\ldots,U_N,\\
\text{one stack-wide product:}\qquad
&U_{\rm all}=\prod_{\ell=1}^{N}U_\ell.
\end{aligned}
\tag{80}
\]

The first list allows us to change the topological sector of one selected
layer without touching the others.  The second operation instead changes
every layer simultaneously.  They are not interchangeable pieces of
information, even though \(U_{\rm all}\) is the product of the first list.

This distinction is the whole toy model in one sentence:

\[
\boxed{
\begin{gathered}
\text{independent ancilla symmetry generators}\\
\Longleftrightarrow\\
\text{independent input symmetries that can be gauged}
\end{gathered}}
\tag{81}
\]

### Choice 1: one ancillary cluster layer per toric-code layer

First give every physical toric-code layer its own copy of the two-dimensional
ancilla resource used in Section II.  In each ancillary layer there are
\(a\)-qubits at vertices and \(A\)-qubits on edges; together they form a
Lieb-lattice cluster state.  The picture is therefore

\[
\begin{array}{ccccc}
(B_1,C_1)&\longleftrightarrow&\text{ancilla layer }1
&\longleftrightarrow&U_1,\\
(B_2,C_2)&\longleftrightarrow&\text{ancilla layer }2
&\longleftrightarrow&U_2,\\
\vdots&&\vdots&&\vdots\\
(B_N,C_N)&\longleftrightarrow&\text{ancilla layer }N
&\longleftrightarrow&U_N.
\end{array}
\tag{82}
\]

For a connected two-dimensional cluster layer, the relevant 0-form symmetry
is the simultaneous \(X\) flip of all its \(a\)-vertex qubits.  Write it as

\[
G_\ell^a=\prod_{v\text{ in ancilla layer }\ell}X_{v,\ell}^a.
\tag{83}
\]

Because the ancillary layers are disconnected from one another, these are
\(N\) independent symmetries:

\[
\mathcal G_{\rm anc}^{\rm layer}
=\langle G_1^a,\ldots,G_N^a\rangle
\cong\mathbb Z_2^N.
\tag{84}
\]

This independence is physical.  Applying \(G_3^a\), for example, changes
only the \(a\)-qubits in layer 3.  It does not have to be accompanied by an
operation in layers 1, 2, 4, and so on.

The enrichment circuit is chosen independently in every layer:

\[
\Omega_{\rm layer}=\prod_{\ell=1}^N\Omega_\ell,
\qquad
\Omega_\ell G_\ell^a\Omega_\ell^\dagger
=G_\ell^aU_\ell.
\tag{85}
\]

Equation (85) is just the Section II relation
\(\Omega G_a\Omega^\dagger=G_aU_{\mathrm{CZ}}\), repeated \(N\) times.
After measuring all \(a\)-qubits, the \(A\)-qubits in each layer become that
layer's gauge field.  Thus the procedure gauges every \(U_\ell\)
independently.

For this decoupled toy input, the output is correspondingly a stack of
independently gauged two-dimensional systems: each layer has the same local
\(\mathcal D(D_4)\)-type construction discussed in Section II.  The
important word is *independently*.  A defect or gauge transformation can be
specified separately in each layer, because the ancilla resource had one
symmetry per layer.

The paper calls this the prototype of **homological gauging** because the
ancilla inherits the same layer-by-layer structure as the input code.  In
the later qLDPC generalization, “same structure” becomes “the ancilla and
input are described by closely related chain complexes.”

### Choice 2: one connected three-dimensional ancillary graph

Now keep exactly the same \(B,C\) stack, but choose a completely different
ancilla resource: a connected three-dimensional cubic cluster state spanning
all layers.  The \(a\)-qubits live at cubic-lattice vertices and the
\(A\)-qubits live on cubic-lattice edges.  The crucial structural difference
is that the ancillas are now connected *between* layers.

A connected cluster resource of this kind has one relevant global 0-form
symmetry,

\[
G_{\rm 3D}^a=\prod_{v\text{ in the full 3D ancilla}}X_v^a.
\tag{86}
\]

There is no independent factor analogous to \(G_\ell^a\) for an individual
horizontal slice.  Flipping only one slice is not a symmetry of this
three-dimensional cluster state, because the vertical ancilla-edge
constraints link that slice to neighbouring slices.

Hence the symmetry matching condition can tie this sole ancilla symmetry
only to one input operation:

\[
\Omega_{\rm 3D}G_{\rm 3D}^a\Omega_{\rm 3D}^\dagger
=G_{\rm 3D}^aU_{\rm all}
=G_{\rm 3D}^a\prod_{\ell=1}^{N}U_\ell.
\tag{87}
\]

The procedure now gauges the single stack-wide controlled-\(Z\), not the
\(N\) layer-resolved controlled-\(Z\) gates.  Measuring the \(a\)-qubits
leaves a three-dimensional \(A\) gauge system, because the unmeasured
\(A\)-qubits occupy the edges of the connected cubic ancillary lattice.

It is tempting to say that Eq. (87) is merely a simultaneous version of
Eq. (85), but that would miss the point.  The two outputs differ because
their gauge fields have different connectivity:

\[
\begin{array}{c|c|c}
&\text{layer-resolved choice}&\text{connected-3D choice}\\
\hline
\text{ancilla 0-form symmetry}&\mathbb Z_2^N&\mathbb Z_2\\
\text{gauged input operation}&U_1,\ldots,U_N\text{ separately}&U_{\rm all}\text{ only}\\
\text{unmeasured }A\text{ field}&N\text{ independent 2D gauge fields}
&\text{one connected 3D gauge field}\\
\text{resulting interpretation}&\text{stack of 2D non-Abelian layers}
&\text{hybrid 3D/2D non-Abelian system}
\end{array}
\tag{88}
\]

The source paper summarizes the second output by saying that its
three-dimensional gauge field has non-Abelian mutual statistics with
two-dimensional gauge fields of restricted mobility.  The toy subsection
does not derive those statistics, and neither do we need to derive them yet.
The safe conclusion at this point is simply that this is **not** a stack of
independent \(\mathcal D(D_4)\) layers: the connected ancillary field
correlates what happens in different layers.

### Why the second choice is more general

The layer-resolved construction required a strong property of the input:
each individual layer had to possess its own useful emergent controlled-\(Z\)
symmetry \(U_\ell\).  In the toy model this is automatic because the input
was deliberately chosen as \(N\) decoupled toric-code pairs.

A more general qLDPC code may have no meaningful decomposition into layers,
and it may not admit a family of separately addressable transversal gates.
It can nevertheless have one transversal gate \(U\) on the entire code.  A
connected ancillary graph with one matching global symmetry is then enough
to gauge that \(U\).

This is the conceptual trade:

\[
\begin{array}{rcl}
\text{more independent input symmetries}
&\Longleftrightarrow&
\text{more independent ancilla symmetry generators},\\
\text{one available global input symmetry}
&\Longleftrightarrow&
\text{one connected ancillary graph is sufficient}.
\end{array}
\tag{89}
\]

It is not that the graph method is an approximation to the homological
method.  It is a different design choice: it gives up layer-by-layer
addressability in order to work when the input code supplies only one
global symmetry.

### The lesson for the qLDPC construction

The toy model is a controlled experiment.  The matter code is held fixed;
only the ancilla architecture changes.  That change alters

\[
\text{ancilla symmetry}
\ \longrightarrow\
\text{which logical gate is gauged}
\ \longrightarrow\
\text{connectivity and character of the emergent gauge field}.
\tag{90}
\]

This is exactly the chain of reasoning that will survive in the general
qLDPC setting.  The rest of Section III replaces the visible layer geometry
by chain complexes and graphs, but the selection rule remains Eq. (81).

### Check your understanding

1. Why is \(\prod_{\ell}U_\ell\) not equivalent, for gauging purposes, to
   having the \(N\) generators \(U_\ell\) available separately?
2. In Eq. (85), what would go wrong if one tried to enrich
   \(G_1^a\) with \(U_1U_2\) while leaving \(G_2^a\) untouched?
3. Why does connecting ancillary layers by vertical edges reduce the number
   of independent 0-form symmetries?
4. Which feature makes graph gauging suitable for a code that has one
   transversal gate but no layer decomposition?

## Interlude: binary linear algebra over \(\mathbb F_2\)

The next subsection replaces the visible edges, vertices, and plaquettes of
the toric code by matrices.  The required mathematics is ordinary linear
algebra, with one change: all numbers belong to the two-element field

\[
\mathbb F_2=\{0,1\}.
\tag{B1}
\]

Its addition and multiplication are performed modulo two:

\[
\begin{array}{c|cc}
 +&0&1\\ \hline
 0&0&1\\
 1&1&0
\end{array}
\qquad
\begin{array}{c|cc}
 \cdot&0&1\\ \hline
 0&0&0\\
 1&0&1
\end{array}.
\tag{B2}
\]

Thus \(1+1=0\).  Subtraction is exactly the same operation as addition,
because \(-1=1\) in \(\mathbb F_2\).  The word *field* means that the usual
rules of linear algebra still apply: addition and multiplication distribute,
and every nonzero number has an inverse (here, the inverse of \(1\) is
\(1\)).

### Vectors are subsets, and addition is XOR

The vector space \(\mathbb F_2^n\) consists of binary strings
\(v=(v_1,\ldots,v_n)\).  Choose labels \(e_1,\ldots,e_n\) for some objects
(for example, qubits).  The vector

\[
v=\sum_{i=1}^n v_i e_i
\tag{B3}
\]

can be read as the subset of labels for which \(v_i=1\).  Adding two vectors
is bitwise XOR, so it takes the **symmetric difference** of their subsets:
an element included twice disappears.  For instance,

\[
(1,0,1,1)+(0,1,1,0)=(1,1,0,1).
\tag{B4}
\]

This cancellation is the algebraic form of the Pauli facts \(X_i^2=Z_i^2=I\).
If a binary vector records the support of a product of \(Z\)'s, then adding
support vectors records multiplication of those Pauli products, with repeated
factors cancelling.

### Linear maps are binary matrices

A linear map \(M:\mathbb F_2^n\to\mathbb F_2^m\) is an \(m\times n\)
matrix with entries 0 or 1.  It acts by the usual matrix multiplication, but
every sum is reduced modulo two.  In particular,

\[
(Mv)_a=\sum_{i=1}^n M_{ai}v_i\pmod 2.
\tag{B5}
\]

The entry \(M_{ai}=1\) says that input label \(i\) is incident on, or is
selected by, output label \(a\).  Hence such a matrix is often called an
**incidence matrix**.  The value \((Mv)_a=1\) means that output \(a\) sees an
odd number of selected input labels; value 0 means that it sees an even
number.

Three familiar linear-algebra notions will recur:

- The **image** \(\operatorname{im}M\) is the set of outputs \(Mv\) that can
  be produced.
- The **kernel** \(\ker M=\{v:Mv=0\}\) is the set of input patterns invisible
  to the map.
- The **rank** is \(\dim\operatorname{im}M\).  Rank--nullity still holds:
  \(\dim\ker M+\operatorname{rank}M=n\).

As over the real numbers, these quantities can be found by Gaussian
elimination.  The only nontrivial row operation is “add one row to another,”
which is again XOR; there is no distinction between adding and subtracting a
row.

### The mod-two dot product and transpose

For \(u,v\in\mathbb F_2^n\), define

\[
u\mathbin{\cdot}v=\sum_{i=1}^n u_i v_i\pmod2.
\tag{B6}
\]

It equals 1 precisely when the two corresponding subsets overlap in an odd
number of labels.  We call \(u\) and \(v\) **orthogonal** when
\(u\mathbin{\cdot}v=0\), i.e. when their overlap is even.  This is the CSS
commutation test: the \(X\)-product with support \(u\) and the \(Z\)-product
with support \(v\) commute exactly when \(u\mathbin{\cdot}v=0\).

The transpose \(M^{\mathsf T}:\mathbb F_2^m\to\mathbb F_2^n\) reverses the
direction of an incidence matrix and obeys

\[
u\mathbin{\cdot}(Mv)=(M^{\mathsf T}u)\mathbin{\cdot}v.
\tag{B7}
\]

This identity lets us translate freely between “which checks contain this
qubit?” and “which qubits are selected by this collection of checks?”

### The one equation to watch for

If two maps can be composed,

\[
\mathbb F_2^r\xrightarrow{\;N\;}\mathbb F_2^n
\xrightarrow{\;M\;}\mathbb F_2^m,
\tag{B8}
\]

then \(MN=0\) means: every column of \(N\), after being tested by every row
of \(M\), has even overlap.  Equivalently, \(\operatorname{im}N\subseteq
\ker M\).  In the next section this becomes
\(\partial_1\partial_2=0\).  It is simultaneously the abstract statement
“a boundary has no boundary” and the concrete CSS statement that every
\(X\)-check and \(Z\)-check overlap an even number of times.

Nothing deeper than this binary bookkeeping is being assumed.  The new names
(*chains*, *cochains*, *boundary maps*) organize these same vectors and
matrices so that the toric-code construction can be stated without relying on
a lattice picture.

## Section III.B: generalizing gauging to a qLDPC code

The toy model made the central design choice visible by drawing layers:
independent ancilla layers gave independent symmetries, whereas one connected
ancilla gave one global symmetry.  A general qLDPC code need not come with
layers, surfaces, or any other useful picture.  This subsection replaces the
picture with an algebraic description that works for any CSS code.

The paper's strategy is:

\[
\boxed{
\begin{gathered}
\text{encode the incidence pattern of qubits and checks in a chain complex;}\\
\text{use that description to specify both the input code and the ancillary
gauge system;}\\
\text{then impose the same symmetry-matching condition as in the toy model.}
\end{gathered}}
\tag{91}
\]

This is not a new physical mechanism.  The measurement-based gauging
mechanism remains Eq. (68).  What changes is the language used to answer the
question “which qubits and checks are connected to which?”

### From labelled qubits to a CSS chain complex

We now make the word “sum” fully precise.  Let \(Q\), \(C_X\), and \(C_Z\)
be finite sets labelling, respectively, the physical qubits, the \(X\)-check
generators, and the \(Z\)-check generators.  For a finite set \(S\), write
\(\mathbb F_2[S]\) for the free \(\mathbb F_2\)-vector space on \(S\): it has
one **canonical basis vector** \([s]\) for every \(s\in S\).  Thus the
three spaces in this paper are, precisely,

\[
D_2=\mathbb F_2[C_Z],\qquad
D_1=\mathbb F_2[Q],\qquad
D_0=\mathbb F_2[C_X].
\tag{92}
\]

For example, an element \(b\in D_1\) is a formal binary sum

\[
b=\sum_{q\in Q} b_q\,[q],\qquad b_q\in\mathbb F_2.
\tag{93}
\]

It is not a sum of physical qubits: it is a vector whose coefficient \(b_q\)
records whether the label \(q\) is selected.  In particular,
\(\sum_{q\in S}[q]\) means the vector with coefficient one on the
subset \(S\subseteq Q\) and zero elsewhere.  This is exactly the XOR/symmetric-
difference addition introduced in the interlude.

Choose two binary incidence matrices \(H_Z\) and \(H_X\), or equivalently
two linear maps,

\[
0\longrightarrow D_2
\xrightarrow{\ \partial_2\ }D_1
\xrightarrow{\ \partial_1\ }D_0
\longrightarrow0,
\qquad
\begin{aligned}
\partial_2[z]&=\sum_{q\in Q}(H_Z)_{qz}\,[q],\\
\partial_1[q]&=\sum_{x\in C_X}(H_X)_{xq}\,[x].
\end{aligned}
\tag{94}
\]

Here \([z]\) and \([x]\) are canonical basis vectors labelled by
\(z\in C_Z\) and \(x\in C_X\).  Therefore \((H_Z)_{qz}=1\) means that qubit
\(q\) belongs to \(Z\)-check \(z\), while \((H_X)_{xq}=1\) means that qubit
\(q\) belongs to \(X\)-check \(x\).  The arrows in Eq. (94) are simply the
two incidence matrices written as linear maps.

The notation becomes physical through two support-to-Pauli maps.  As in the
paper, we write \(D^1=\operatorname{Hom}_{\mathbb F_2}(D_1,\mathbb F_2)\)
for the cochain space.  Here \(\operatorname{Hom}_{\mathbb F_2}(V,W)\) is
the vector space of \(\mathbb F_2\)-linear maps from \(V\) to \(W\); this
will be unpacked carefully below.  Let \(\mathbf q\in D^1\) be the coordinate
function defined by \(\mathbf q([q'])=\delta_{q,q'}\).  Then, for
\(b=\sum_qb_q[q]\in D_1\) and
\(\mathbf a=\sum_q a_q\mathbf q\in D^1\), define

\[
\mathsf Z(b):=\prod_{q\in Q}Z_q^{b_q},
\qquad
\mathsf X(\mathbf a):=\prod_{q\in Q}X_q^{a_q}.
\tag{95}
\]

The exponents are bits: exponent 0 means the identity and exponent 1 means
the indicated Pauli.  Consequently vector addition in \(D_1\) corresponds
to multiplication of \(Z\)-Pauli products, and cochain addition in \(D^1\)
corresponds to multiplication of \(X\)-Pauli products.

### Why restrict to CSS qLDPC codes?

Using the paper's coboundary notation \(d_0:D^0\to D^1\), defined carefully
below, the actual check operators are
therefore

\[
S^Z_z=\mathsf Z(\partial_2[z]),
\qquad
S^X_x=\mathsf X(d_0\mathbf x),
\tag{96}
\]

and a CSS stabilizer Hamiltonian is

\[
H_{\rm CSS}=-\sum_{x\in C_X}S^X_x-\sum_{z\in C_Z}S^Z_z.
\tag{97}
\]

The paper writes the natural pairing of a cochain with a chain as evaluation:
\(\mathbf a(b)=\sum_q a_qb_q\pmod2\).  The Pauli commutation rule is
exactly

\[
\mathsf X(\mathbf a)\mathsf Z(b)
=(-1)^{\mathbf a(b)}
\mathsf Z(b)\mathsf X(\mathbf a).
\tag{98}
\]

Thus \(S_x^X\) and \(S_z^Z\) commute precisely when
\((d_0\mathbf x)(\partial_2[z])=0\).  By the
transpose identity from Eq. (B7), this pairing is the \((x,z)\) entry of
the product \(H_XH_Z\), equivalently the coefficient of \([x]\) in
\(\partial_1\partial_2[z]\).  All CSS checks commute if and only if

\[
\partial_1\partial_2=0
\qquad\text{(equivalently, \(H_XH_Z=0\) over \(\mathbb F_2\)).}
\tag{99}
\]

Read Eq. (99) from right to left.  For one \(Z\)-check \(z\),
\(\partial_2[z]\) is its binary support vector.  Applying
\(\partial_1\) then counts, modulo two, how many qubits of that support
belong to each \(X\)-check.  The zero vector says that all those numbers are
even.

The toric code is the standard geometric realization:

\[
\begin{array}{c|c|c}
&\text{basis label}&\text{support vector and operator}\\
\hline
C_X&v\text{ (vertex)}&d_0\mathbf v=\sum_{e\ni v}\mathbf e,
\quad S_v^X=\prod_{e\ni v}X_e\\
C_Z&p\text{ (plaquette)}&\partial_2[p]=\sum_{e\in\partial p}[e],
\quad S_p^Z=\prod_{e\in\partial p}Z_e
\end{array}
\tag{100}
\]

The equality \(\partial_1\partial_2=0\) says that a vertex and a square
plaquette share zero or two edges.  For a general CSS qLDPC code there may be
no geometric vertex or plaquette, but the same matrix equation remains the
complete commutation condition.

### A tiny non-geometrical example

Let \(Q=\{e_1,\ldots,e_5\}\), \(C_Z=\{\beta\}\), and
\(C_X=\{\alpha_1,\alpha_2,\alpha_3\}\).  Bracketed symbols below are the
canonical basis vectors introduced above, whereas unbracketed symbols are
labels.
Choose the \(Z\)-check support vector to be

\[
\partial_2[\beta]
=[e_1]+[e_2]+[e_4]+[e_5].
\tag{101}
\]

The corresponding physical stabilizer is not the vector on the left; it is
the Pauli operator obtained from it using Eq. (95):

\[
S^Z_\beta=\mathsf Z(\partial_2[\beta])
=Z_{e_1}Z_{e_2}Z_{e_4}Z_{e_5}.
\tag{102}
\]

Assume the other incidence map has the values

\[
\begin{aligned}
\partial_1[e_1]&=[\alpha_1]+[\alpha_2], &
\partial_1[e_2]&=[\alpha_2]+[\alpha_3],\\
\partial_1[e_4]&=[\alpha_1]+[\alpha_3], &
\partial_1[e_5]&=0.
\end{aligned}
\tag{103}
\]

Linearity over \(\mathbb F_2\) now gives

\[
\begin{aligned}
\partial_1\partial_2[\beta]
&=([\alpha_1]+[\alpha_2])
+([\alpha_2]+[\alpha_3])
+([\alpha_1]+[\alpha_3])+0\\
&=2[\alpha_1]+2[\alpha_2]+2[\alpha_3]=0
\qquad\text{in }D_0\text{ over }\mathbb F_2.
\end{aligned}
\tag{104}
\]

This says that every \(X\)-check overlaps the support of \(S^Z_\beta\) an
even number of times.  For example, \(\alpha_1\) sees \(e_1,e_4\), and
\(\alpha_2\) sees \(e_1,e_2\).  Let \(\boldsymbol{\alpha}_i\in D^0\)
denote the indicator cochain for the label \(\alpha_i\), as defined
generally below.  Consequently the physical \(X\)-check operators
\(S^X_{\alpha_i}=\mathsf X(d_0\boldsymbol{\alpha}_i)\) commute with
\(S^Z_\beta\).  The example has no drawing, but it has all the algebraic
information the construction needs.

### The dual language: why “cochains” will appear

The paper denotes the cochain spaces by upper indices:

\[
D^0,\qquad D^1,\qquad D^2,
\tag{105}
\]

called **cochains**, and defines them by

\[
D^n=\operatorname{Hom}_{\mathbb F_2}(D_n,\mathbb F_2).
\tag{106}
\]

Read \(\operatorname{Hom}\) as “the set of homomorphisms,” which in this
vector-space setting means **linear maps**.  Thus \(\mathbf a\in D^n\) is a
function \(\mathbf a:D_n\to\mathbb F_2\) satisfying

\[
\mathbf a(u+v)=\mathbf a(u)+\mathbf a(v),
\qquad
\mathbf a(cu)=c\,\mathbf a(u)
\quad (u,v\in D_n,\ c\in\mathbb F_2).
\tag{107}
\]

Such functions form a vector space, with addition defined pointwise.  For
example, \((\mathbf a+\mathbf b)(u)=\mathbf a(u)+\mathbf b(u)\).  The paper
uses boldface for cochains: for every qubit label \(q\), the 1-cochain
\(\mathbf q\in D^1\) is the indicator function
\(\mathbf q([q'])=\delta_{q,q'}\).  Hence
\(\mathbf a=\sum_q a_q\mathbf q\) is a row-vector way to select qubits,
whereas \(b=\sum_qb_q[q]\) is the corresponding column-vector chain.

In precisely the paper's notation, the associated cochain complex is

\[
0\longleftarrow D^2
\xleftarrow{\ d_1\ }D^1
\xleftarrow{\ d_0\ }D^0
\longleftarrow0,
\qquad
d_n=\partial_{n+1}^{\mathsf T}.
\tag{108}
\]

The superscript on \(D^n\) reminds us that this is a cochain space, not the
chain space \(D_n\).  The left-pointing arrows make the reversal of direction
visible.  In the bases introduced above, the co-boundary maps act as

\[
d_0\mathbf x=\sum_{q\in Q}(H_X)_{xq}\mathbf q,
\qquad
d_1\mathbf q=\sum_{z\in C_Z}(H_Z)_{qz}\mathbf z,
\tag{109}
\]

where \(\mathbf x\in D^0\) and \(\mathbf z\in D^2\) are the analogous
indicator cochains for check labels.  Thus \(d_0\) turns the cochain for one
\(X\)-check label into the cochain selecting precisely the qubits in that
check.  While \(\partial_1\) asks “which \(X\)-checks touch this qubit?”,
\(d_0\) asks “which qubits are selected by this collection of \(X\)-checks?”
Likewise, \(d_1:D^1\to D^2\) takes a 1-cochain selecting qubits and returns
a 2-cochain on \(Z\)-check labels.  For a \(Z\)-check \(z\),

\[
(d_1\mathbf a)([z])=\mathbf a(\partial_2[z]).
\tag{109a}
\]

It equals 1 precisely when the selected qubits have **odd overlap** with the
support of \(z\).  Thus \(d_1\) asks “which \(Z\)-checks have odd overlap
with this selected collection of qubits?”  The shorter phrase “which
\(Z\)-checks use these qubits?” is only an intuition: a \(Z\)-check
containing two selected qubits gives 0 because all counting is modulo two.
In the toric code, applying \(d_0\) to one vertex cochain selects its
incident edges—the support of the star operator.

Accordingly, the paper represents:

\[
\begin{array}{c|c}
\text{chain language}&\text{Pauli operator}\\
\hline
b=\sum_{e\in Q} b_e[e]\in D_1&\mathsf Z(b)=\prod_{e\in Q}(Z_e)^{b_e}\\
\mathbf a=\sum_{e\in Q}a_e\mathbf e\in D^1&
\mathsf X(\mathbf a)=\prod_{e\in Q}(X_e)^{a_e}
\end{array}
\tag{110}
\]

and Eq. (99) becomes \(d_1d_0=0\) after transposition.  In the paper's
function notation this is immediate: for \(\mathbf x\in D^0\) and
\(p\in D_2\), \((d_1d_0\mathbf x)(p)=\mathbf x(\partial_1\partial_2p)=0\).

#### Cocycles, coboundaries, and the quotient \(H^1\)

The word **cocycle** has a precise and very practical meaning here.  A
1-cochain \(\mathbf a\in D^1\) is a **1-cocycle** exactly when

\[
d_1\mathbf a=0.
\tag{110g}
\]

Equivalently, it belongs to the kernel of \(d_1\),

\[
\ker d_1:=\{\mathbf a\in D^1\mid d_1\mathbf a=0\}.
\tag{110h}
\]

This is not just a name inherited from topology.  By Eq. (109a), each
coefficient of \(d_1\mathbf a\) records the parity of the overlap between
the support of \(\mathbf a\) and one \(Z\)-check.  Therefore

\[
\mathbf a\in\ker d_1
\quad\Longleftrightarrow\quad
X_{\mathbf a}\text{ commutes with every (Z)-check.}
\tag{110i}
\]

So a 1-cocycle is precisely a candidate \(X\)-type logical operator: it has
zero \(Z\)-syndrome.  It need not look like a loop.  “Cycle” in this word
means only that the co-boundary map gives zero.

There is one further distinction.  A **1-coboundary** is a 1-cochain of the
form \(d_0\mathbf x\) for some \(\mathbf x\in D^0\).  The set of all of them
is the image of \(d_0\):

\[
\operatorname{im}d_0:=\{d_0\mathbf x\mid\mathbf x\in D^0\}\subseteq D^1.
\tag{110j}
\]

Physically, \(\mathbf x\) selects a collection of \(X\)-check labels, and
\(X_{d_0\mathbf x}\) is the product of exactly those \(X\)-check stabilizers.
It consequently acts as the identity on every code state.  The identity
\(d_1d_0=0\) says that every coboundary is automatically a cocycle:

\[
\operatorname{im}d_0\subseteq\ker d_1.
\tag{110k}
\]

This inclusion is what makes the quotient well-defined.  The slash in

\[
H^1(D_\bullet):=\ker d_1/\operatorname{im}d_0
\tag{110l}
\]

does **not** mean ordinary numerical division.  Here is the precise
definition.  Abbreviate

\[
V:=\ker d_1,
\qquad
W:=\operatorname{im}d_0.
\tag{110l-a}
\]

We have already proved \(W\subseteq V\).  For every cocycle
\(\mathbf a\in V\), its **coset** modulo \(W\) is the set

\[
\mathbf a+W
:=\{\mathbf a+\mathbf w\mid\mathbf w\in W\}.
\tag{110l-b}
\]

In words: begin with \(\mathbf a\), add every possible coboundary, and put
all resulting cocycles into one set.  The quotient vector space is the set
of all these cosets:

\[
V/W
:=\{\mathbf a+W\mid\mathbf a\in V\}.
\tag{110l-c}
\]

Thus an element of \(H^1=V/W\) is not a single cochain.  It is one entire
coset, i.e. a whole collection of cochains.  Two cocycles represent the
same quotient element precisely when their cosets are equal.  Equivalently,
they differ by an element of \(W\).  In the present notation,

\[
\mathbf a\sim\mathbf a'
\quad\Longleftrightarrow\quad
\mathbf a'=\mathbf a+d_0\mathbf x
\quad\text{for some }\mathbf x\in D^0.
\tag{110m}
\]

The notation \([\mathbf a]\) denotes the coset
\(\mathbf a+W=\mathbf a+\operatorname{im}d_0\), not an arbitrarily chosen
representative \(\mathbf a\).  All cochains in this coset give Pauli
operators that differ only by an \(X\)-stabilizer, and so have exactly the
same action on the encoded subspace.  A nonzero class in \(H^1\) is therefore
an independent logical \(X\) operator.

Mathematically, \(H^1(D_\bullet)\) is a **quotient vector space over
\(\mathbb F_2\)**.  It is not a subset of \(\ker d_1\): its elements are
the cosets \([\mathbf a]=\mathbf a+W\).  Since every vector space is an
abelian group under addition, \(H^1\) is also an abelian group.  Its zero
element is the coset

\[
[0]=W=\operatorname{im}d_0,
\tag{110l-c-i}
\]

which contains *all* \(X\)-stabilizer products, not only the empty
operator.  The corresponding statement for the chain quotient
\(H_1=\ker\partial_1/\operatorname{im}\partial_2\) is identical: it is a
vector space over \(\mathbb F_2\), hence an abelian group, whose elements
are cosets of \(Z\)-cycles modulo \(Z\)-stabilizer boundaries.

Addition in the quotient is defined on cosets by

\[
[\mathbf a]+[\mathbf b]:=[\mathbf a+\mathbf b].
\tag{110l-d}
\]

This does not depend on which representatives are chosen.  Indeed, replacing
\(\mathbf a\) by \(\mathbf a+\mathbf w\) and \(\mathbf b\) by
\(\mathbf b+\mathbf w'\), with \(\mathbf w,\mathbf w'\in W\), changes the
sum by \(\mathbf w+\mathbf w'\in W\), which remains in the same coset.
In short:

\[
\begin{array}{c|c|c}
\text{object}&\text{algebraic condition}&\text{physical meaning}\\
\hline
\text{1-cocycle }\mathbf a&d_1\mathbf a=0&
X_{\mathbf a}\text{ commutes with every (Z)-check}\\
\text{1-coboundary }d_0\mathbf x&\mathbf x\in D^0&
X_{d_0\mathbf x}\text{ is a product of (X)-stabilizers}\\
\text{class }[\mathbf a]\in H^1&\mathbf a\in\ker d_1\text{ modulo }\operatorname{im}d_0&
\text{a logical (X) action}
\end{array}
\tag{110n}
\]

The later gauging construction also uses **0-cocycles**.  These are not
1-cocycles placed at vertices; they are elements \(\boldsymbol\mu\in D^0\)
with

\[
d_0\boldsymbol\mu=0,
\qquad
\ker d_0=\{\boldsymbol\mu\in D^0\mid d_0\boldsymbol\mu=0\}.
\tag{110o}
\]

Because this level-\((2+1)\) complex begins at \(D^0\), there is no
preceding co-boundary map whose image must be quotiented out at degree zero.
Thus \(H^0=\ker d_0\) here.  A 0-cocycle is a binary choice of
\(X\)-check labels for which every qubit is selected an even number of
times.  Equivalently, the corresponding product of \(X\)-check stabilizers
is the identity.  In Section III.C these 0-cocycles become the ancilla
subsystem symmetries and the relations among its final \(X\)-checks.

The notation is more general than the lattice picture, but its job is still
only to track which qubits a Pauli product acts on.

### A tiny non-geometrical example: cochains

Return to the five-qubit example above.  Its single \(Z\)-check has support

\[
\partial_2[\beta]=[e_1]+[e_2]+[e_4]+[e_5].
\tag{110a}
\]

To make one cochain calculation fully definite, complete the previously
unspecified incidence data by taking \(\partial_1[e_3]=0\).  This choice does
not change the earlier calculation: \(e_3\) does not occur in the support of
\(\partial_2[\beta]\).  Let \(\boldsymbol{\alpha}_2\in D^0\) be the
indicator cochain of the \(X\)-check label \(\alpha_2\).  The displayed
incidences in Eq. (103) say that this check contains \(e_1\) and \(e_2\),
and no other qubit.  Therefore its co-boundary is

\[
d_0\boldsymbol{\alpha}_2
=\mathbf e_1+\mathbf e_2
=:\mathbf a\in D^1.
\tag{110b}
\]

The right-hand side is a 1-cochain, not a chain.  It is the function whose
value is one on \([e_1]\) and \([e_2]\), and zero on \([e_3]\), \([e_4]\), and
\([e_5]\).  Its associated physical Pauli operator is consequently

\[
X_{\mathbf a}=X_{e_1}X_{e_2}.
\tag{110c}
\]

Now test whether \(\mathbf a\) is a cocycle.  There is only one \(Z\)-check
label, so it is enough to evaluate \(d_1\mathbf a\) on \([\beta]\):

\[
\begin{aligned}
(d_1\mathbf a)([\beta])
&=\mathbf a(\partial_2[\beta])\\
&=\mathbf a\bigl([e_1]+[e_2]+[e_4]+[e_5]\bigr)\\
&=1+1+0+0=0\qquad\text{in }\mathbb F_2.
\end{aligned}
\tag{110d}
\]

Since \(D^2\) has just the one basis label \(\beta\), this proves
\(d_1\mathbf a=0\).  Equivalently, the \(X\)-operator in Eq. (110c) overlaps
the \(Z\)-stabilizer \(S^Z_\beta=Z_{e_1}Z_{e_2}Z_{e_4}Z_{e_5}\) twice, and
therefore commutes with it.

This cocycle is not a new logical \(X\) operator, because Eq. (110b) shows
that it is a co-boundary: \(\mathbf a\in\operatorname{im}d_0\).  The operator
\(X_{\mathbf a}=X_{e_1}X_{e_2}\) is exactly the \(X\)-stabilizer associated
with \(\alpha_2\).  This is the concrete reason for the quotient

\[
H^1(D_\bullet)=\frac{\ker d_1}{\operatorname{im}d_0}:
\tag{110e}
\]

\(\ker d_1\) first selects all \(X\)-operators that commute with every
\(Z\)-check, and then quotienting by \(\operatorname{im}d_0\) removes the
ones that are already \(X\)-stabilizers.  A cocycle not in
\(\operatorname{im}d_0\) would represent a logical \(X\) operator.

For contrast, consider the cochain
\(\mathbf a'=\mathbf e_1+\mathbf e_3\).  It gives

\[
(d_1\mathbf a')([\beta])=1+0=1,
\tag{110f}
\]

so it is not a cocycle.  Correspondingly, \(X_{e_1}X_{e_3}\) has odd overlap
with \(S^Z_\beta\) and anticommutes with it.  The two examples show the full
logic of the cochain complex: \(d_1\) computes an \(X\)-operator's
mod-two commutation syndrome against the \(Z\)-checks, while
\(\operatorname{im}d_0\) identifies the zero-syndrome operators that are
already stabilizers.

### What this formalism must accomplish for gauging

The authors now use the same kind of chain-complex data twice:

\[
\begin{array}{rcl}
D_\bullet&:&\text{the chain complex of the input \(B,C\) qLDPC codes},\\
A_\bullet&:&\text{the chain complex of the ancillary \(a,A\) gauge system}.
\end{array}
\tag{111}
\]

This notation does **not** say that \(A_\bullet=D_\bullet\).  The toy model
already taught us why that equality can either hold or fail:

- for homological gauging, the ancilla tends to mirror the input structure,
  so \(A_\bullet\) is chosen to be a copy or close relative of
  \(D_\bullet\);
- for graph gauging, \(A_\bullet\) is instead the chain complex of a chosen
  graph and can be very different from \(D_\bullet\).

The rest of this subsection will formulate two questions in this language:

\[
\begin{array}{ll}
\textbf{Question 1:}&
\text{Which transversal logical symmetry }U\text{ of the two input codes is
to be gauged?}\\[3pt]
\textbf{Question 2:}&
\text{Which ancillary complex }A_\bullet\text{ has enough appropriate
symmetry to gauge that }U?
\end{array}
\tag{112}
\]

These are exactly the qLDPC versions of the questions answered by the toy
model.  The chain-complex formalism does not choose the answer automatically;
it gives a precise way to test whether a proposed ancilla structure and
symmetry-enrichment circuit match.

### What to retain before the next subsection

1. A CSS qLDPC code is sparse check--qubit incidence data satisfying an
   even-overlap rule.
2. The chain complex \(D_2\to D_1\to D_0\) packages \(Z\)-checks, qubits,
   and \(X\)-checks, respectively.
3. \(\partial_1\partial_2=0\) is the algebraic version of “a boundary has no
   boundary”; physically, it proves \(X\)- and \(Z\)-checks commute.
4. \(d_1\) maps the support of an \(X\)-operator to its mod-two syndrome
   against the \(Z\)-checks.  A 1-cocycle is an element of \(\ker d_1\), so
   its \(X\)-operator has zero such syndrome.
5. \(\operatorname{im}d_0\) consists of \(X\)-stabilizer products.  Hence
   \(H^1=\ker d_1/\operatorname{im}d_0\) labels zero-syndrome \(X\)-actions
   modulo stabilizers: the logical \(X\) operators.
6. Gauging requires both an input complex \(D_\bullet\) and an ancilla
   complex \(A_\bullet\).  Their relation determines whether the
   homological or graph construction is appropriate.

## Section III.C: symmetries and gauging in qLDPC codes

We can now state the problem without referring to a square lattice.  Take two
identical CSS qLDPC codes, called \(B\) and \(C\), with common chain complex

\[
0\longrightarrow D_2\xrightarrow{\ \partial_2\ }D_1
\xrightarrow{\ \partial_1\ }D_0\longrightarrow0.
\tag{113}
\]

The purpose of this subsection is not to invent a new measurement protocol.
The protocol is still the one encountered in Section II: prepare an ancilla
cluster state, entangle it with the two input codes in a symmetry-respecting
way, and measure the temporary ancillas in the \(X\) basis.  What changes is
the bookkeeping.  The paper asks two questions:

\[
\boxed{\begin{minipage}{0.82\linewidth}
\begin{enumerate}
\item Which transversal Clifford symmetry of the pair \(B,C\) should be
gauged?
\item Which ancilla chain complex has the right subsystem symmetries to
gauge that symmetry?
\end{enumerate}
\end{minipage}}
\tag{114}
\]

The answers are linked: choosing the symmetry constrains the possible
ancilla, and choosing the ancilla determines how many independently
addressable symmetries can be gauged.

### First distinction: logical-string symmetries are not the target

Every CSS code described by Eq. (113) has two familiar kinds of logical
Pauli operator.  In the paper's chain notation, their labels are

\[
H_1(D_\bullet)=\frac{\ker\partial_1}{\operatorname{im}\partial_2},
\qquad
H^1(D_\bullet)=\frac{\ker d_1}{\operatorname{im}d_0}.
\tag{115}
\]

Here is a direct reading of the first quotient.  A 1-chain
\(\eta\in D_1\) satisfying \(\partial_1\eta=0\) is a **cycle**.  Its
operator \(Z_\eta\) commutes with all \(X\)-checks.  But if
\(\eta=\partial_2p\) for some \(p\in D_2\), then \(Z_\eta\) is a product
of \(Z\)-stabilizers and acts trivially on the encoded space.  The quotient
therefore identifies cycles which differ by a stabilizer boundary.  Its
**nonzero** classes label nontrivial logical \(Z\) operators.  The second
quotient says the dual thing: a 1-cocycle
\(\boldsymbol\gamma\in\ker d_1\), modulo the co-boundaries
\(\operatorname{im}d_0\), labels a logical \(X\) operator
\(X_{\boldsymbol\gamma}\).

#### Where do the stabilizer boundaries go?

They are not absent from \(H_1(D_\bullet)\).  Instead, all of them become
the *same* element of the quotient: its zero class.  Indeed, the chain
condition \(\partial_1\partial_2=0\) implies

\[
\operatorname{im}\partial_2\subseteq\ker\partial_1.
\tag{115a}
\]

Thus a boundary \(b=\partial_2p\) is certainly an allowed cycle in the
numerator.  But its class in the quotient is

\[
[b]
=b+\operatorname{im}\partial_2
=\partial_2p+\operatorname{im}\partial_2
=\operatorname{im}\partial_2
=[0].
\tag{115b}
\]

The notation \([b]\) means the coset containing \(b\), not the original
chain by itself.  Equation (115b) says that a \(Z\)-stabilizer product and
the empty operator represent the same *logical* action: both act as the
identity on every encoded state.  Consequently, it would be incorrect to
say that quotienting simply throws stabilizers away.  It groups every
stabilizer boundary into the identity logical operation.

For a minimal abstract example, suppose

\[
\ker\partial_1=\{0,b,\ell,\ell+b\},
\qquad
\operatorname{im}\partial_2=\{0,b\}.
\tag{115c}
\]

Here \(b\) is a stabilizer boundary and \(\ell\) is a cycle which is not a
boundary.  There are only two quotient classes:

\[
H_1(D_\bullet)
=\underbrace{\{0,b\}}_{[0]\text{: identity logical action}}
\ \cup\ 
\underbrace{\{\ell,\ell+b\}}_{[\ell]\text{: one nontrivial logical }Z}.
\tag{115d}
\]

Multiplying \(Z_\ell\) by the stabilizer \(Z_b\) changes its representative
to \(Z_{\ell+b}\), but cannot change what it does to the encoded qubits.
The quotient records exactly this physical equivalence.  In summary,

\[
\begin{array}{c|l}
\ker\partial_1&\text{all \(Z\)-strings with no \(X\)-syndrome}\\
\operatorname{im}\partial_2&\text{the syndrome-free \(Z\)-strings that are stabilizers}\\
H_1(D_\bullet)&\text{logical \(Z\) actions modulo \(Z\)-stabilizers.}
\end{array}
\tag{115e}
\]

So the zero class contains all the stabilizers; the nonzero classes are the
genuinely distinct logical \(Z\) operators.  For the toric code, a
contractible closed loop belongs to the zero class, while a loop winding
around the torus represents a nonzero class.

For a toric code these are the usual noncontractible loop operators.  The
paper calls them 1-cycle and 1-cocycle symmetries, generalizing the toric
code's 1-form symmetries.  In a qLDPC code they need not look like geometric
loops or surfaces; \(\eta\) and \(\boldsymbol\gamma\) are simply sparse or
non-sparse binary vectors satisfying the displayed kernel conditions.

These logical Pauli symmetries are **not** what this construction gauges.
The target is a transversal Clifford gate \(U\) acting on the two copies
\(B,C\).  “Transversal” here means that it factors into gates of bounded
size acting on corresponding or otherwise locally prescribed physical
qubits.  It can act on every qubit, or only on a specified subsystem.  The
important condition is that it preserves the code space: under conjugation,
it maps each stabilizer to a product of stabilizers.  It need not fix each
Hamiltonian term individually.  Thus it is an **emergent symmetry** of the
encoded subspace—the same sense in which the controlled-\(Z\) in Section
II.A was an emergent symmetry.

This distinction matters.  A logical Pauli \(Z_\eta\) is an operator *inside*
one code's protected logical algebra.  A transversal Clifford \(U\) is a
physical circuit that *acts on* that logical algebra, for example by
permuting its logical Pauli operators.  It is the latter action that the
gauging construction promotes to a dynamical gauge action.

### The ancilla is another chain complex

Replace the square-lattice ancilla by an arbitrary level-\((2+1)\) chain
complex

\[
0\longrightarrow A_2\xrightarrow{\ \partial^a_2\ }A_1
\xrightarrow{\ \partial^a_1\ }A_0\longrightarrow0.
\tag{116}
\]

Let \(V_A\) label a basis of \(A_0\) and \(E_A\) a basis of \(A_1\).  The
construction places one temporary ancilla qubit \(a_v\) at each
\(v\in V_A\), and one surviving gauge-field qubit \(A_e\) at each
\(e\in E_A\).  The labels “vertex” and “edge” are only mnemonic: for a
general qLDPC complex, they mean a 0-chain and a 1-chain basis label, not a
location in ordinary space.

For a vertex label \(v\), let \(\mathbf v\in A^0\) be its indicator
cochain.  For an edge label \(e\), let \([e]\in A_1\) be its chain basis
vector.  The ancilla cluster state is the simultaneous \(+1\) eigenspace of
the following two kinds of stabilizer:

\[
K^a_v=X_{a_v}\,X^A_{d^a_0\mathbf v},
\qquad
K^A_e=Z_{A_e}\,Z^a_{\partial^a_1[e]}.
\tag{117}
\]

This compact expression has a concrete meaning.  If
\(d^a_0\mathbf v=\sum_e c_e\mathbf e\), then
\(X^A_{d^a_0\mathbf v}=\prod_e(X_{A_e})^{c_e}\): it acts on all
gauge-field qubits incident on \(v\).  If
\(\partial^a_1[e]=\sum_v r_v[v]\), then
\(Z^a_{\partial^a_1[e]}=\prod_v(Z_{a_v})^{r_v}\): it acts on all temporary
ancillas incident on \(e\).  These are exactly the ordinary graph-cluster
stabilizers, expressed through the incidence maps of \(A_\bullet\).

#### Reading Eq. (117) one edge at a time

It is worth slowing down here, because the superscripts and the maps in
Eq. (117) encode three different ideas at once.  The superscript \(a\)
means “temporary vertex-ancilla qubit,” whereas the superscript \(A\) means
“surviving gauge-field qubit.”  Thus \(X_{a_v}\) flips the qubit placed at
the vertex label \(v\), while \(X_{A_e}\) flips the qubit placed at the
edge label \(e\).  The subscript \(d^a_0\mathbf v\) does *not* name one
qubit.  It names a binary 1-cochain, and \(X^A\) turns that binary list into
a product of \(X\)'s on the selected \(A\) qubits.

For an ordinary graph, suppose that the edges incident on \(v\) are
\(e_1,\ldots,e_r\).  Then the coboundary of the indicator cochain of \(v\)
is

\[
d^a_0\mathbf v=\mathbf e_1+\cdots+\mathbf e_r
\quad\text{in }A^1,
\]

where addition is in \(\mathbb F_2\).  Consequently Eq. (117)'s first
operator is nothing more mysterious than

\[
K^a_v=X_{a_v}X_{A_{e_1}}\cdots X_{A_{e_r}}
=X_{a_v}\prod_{e\ni v}X_{A_e}.
\]

It is one stabilizer for vertex \(v\): it flips that vertex ancilla and
every gauge-field qubit on an edge touching it.

Now take one edge \(e\) with endpoints \(u\) and \(w\).  Its boundary is

\[
\partial^a_1[e]=[u]+[w]\quad\text{in }A_0.
\]

The second operator of Eq. (117) therefore reads

\[
K^A_e=Z_{A_e}Z_{a_u}Z_{a_w}.
\]

It is one stabilizer for edge \(e\): it compares the \(Z\)-parity of the
gauge-field qubit on the edge with the \(Z\)-parity of the two temporary
ancillas at its endpoints.  In particular, for the one-edge graph

```text
u  --- e ---  w
```

the complete set of cluster stabilizers is

\[
K^a_u=X_{a_u}X_{A_e},\qquad
K^a_w=X_{a_w}X_{A_e},\qquad
K^A_e=Z_{A_e}Z_{a_u}Z_{a_w}.
\]

This tiny example is also a useful check that Eq. (117) is consistent.
For example, \(K^a_u\) and \(K^A_e\) overlap on two qubits: on \(a_u\),
where they contain \(X\) and \(Z\), and on \(A_e\), where they again
contain \(X\) and \(Z\).  Each overlap supplies a minus sign on swapping
the operators, and the two signs cancel.  Hence the stabilizers commute.

They commute.  For an incident pair \((v,e)\), \(K^a_v\) and \(K^A_e\)
have one \(X/Z\) overlap on \(a_v\) and a second one on \(A_e\); the two
minus signs cancel.  For a nonincident pair they have no overlap.  No spatial
lattice is needed for this argument—only the common incidence coefficient
\((\partial^a_1)_{ve}\).

### The two ancilla symmetries, and why cocycles matter

The cluster state has two relevant families of symmetries.

First, if \(\eta\in\ker\partial^a_1\subseteq A_1\) is an ancilla 1-cycle,
then

\[
G_A(\eta)=Z^A_\eta
\tag{118}
\]

is a symmetry.  Indeed, its possible sign when commuting past
\(K^a_v\) is the mod-two overlap
\((d^a_0\mathbf v)(\eta)=\mathbf v(\partial^a_1\eta)=0\).  These are the
ancilla's 1-cycle symmetries and become the familiar magnetic-type structure
of the gauge field.

Second, if \(\boldsymbol\mu\in\ker d^a_0\subseteq A^0\) is a 0-cocycle,
then

\[
G_a(\boldsymbol\mu)=X^a_{\boldsymbol\mu}
=\prod_{v\in V_A}(X_{a_v})^{\boldsymbol\mu([v])}
\tag{119}
\]

is a symmetry acting only on the temporary \(a\) qubits.  To see it, commute
this operator through \(K^A_e\).  The sign is
\(\boldsymbol\mu(\partial^a_1[e])=(d^a_0\boldsymbol\mu)([e])=0\).  It
clearly commutes with all \(K^a_v\), which are \(X\)-type on the \(a\)
qubits.  These are called **0-cocycle subsystem symmetries** because a
nonzero \(\boldsymbol\mu\) can select only part of the set of \(a\) qubits.

Why is the kernel condition more than a formal label?  After measuring every
\(a_v\) in the \(X\) basis and correcting to the \(+1\) branch, the first
family of cluster stabilizers becomes the \(X\)-check family
\(X^A_{d^a_0\mathbf v}\) on the remaining \(A\) qubits.  Multiplying these
checks according to a cocycle gives

\[
\prod_{v\in V_A}\bigl(X^A_{d^a_0\mathbf v}\bigr)^{\boldsymbol\mu([v])}
=X^A_{d^a_0\boldsymbol\mu}=I
\qquad(\boldsymbol\mu\in\ker d^a_0).
\tag{120}
\]

Thus \(\boldsymbol\mu\) labels a relation, or redundancy, among the
remaining \(X\)-checks.  On a single connected square lattice, the familiar
example is the product of all star checks, which is the identity.  In the
layer-resolved toy model, each independent layer supplied one such relation.
This is exactly why the number and shape of 0-cocycles determine how many
symmetry actions the ancilla can keep track of.

### Symmetry enrichment: attaching an input-code gate to each cocycle

Let \(\Omega_{a,BC}\) denote the finite-depth circuit that entangles the
ancilla with the two input codes.  The central condition of the subsection
is

\[
\Omega_{a,BC}\,X^a_{\boldsymbol\mu}\,
\Omega_{a,BC}^{\dagger}
=X^a_{\boldsymbol\mu}\,U_{\boldsymbol\mu}
\qquad\text{for every }\boldsymbol\mu\in\ker d^a_0.
\tag{121}
\]

The left side asks what happens to an exact ancilla symmetry under the
entangling circuit.  The right side says that it remains a symmetry, but is
now **decorated** by a transversal Clifford operation \(U_{\boldsymbol\mu}\)
on the \(B,C\) codes.  This is the abstract qLDPC version of the partial
controlled-\(Z\) patch in Section II: a transformation in the ancilla/gauge
sector is tied to a type-changing symmetry action in the matter sector.

Equation (121) must hold for every cocycle, not merely for one chosen
generator.  It is allowed that several cocycles produce the same gate, or
that some produce \(U_{\boldsymbol\mu}=I\).  At least one must produce a
nontrivial encoded action, otherwise the gauging is physically trivial.  The
linearity of the left side also forces compatible gates to compose
consistently: because
\(X^a_{\boldsymbol\mu+\boldsymbol\nu}=X^a_{\boldsymbol\mu}
X^a_{\boldsymbol\nu}\), the encoded actions must satisfy the corresponding
product rule on the code space (up to stabilizers, which act trivially
there).

Once Eq. (121) is satisfied, the temporary \(a\) qubits are projected into
\(|+\rangle\) states.  As in Section II.C, actual \(X\)-measurements can give
\(-1\) outcomes; a classically chosen Pauli correction returns the desired
stabilizer sector.  The paper later proves this deterministic feedforward
step in the general setting.  What remains after removing the \(a\) qubits
is a gauge-field code on \(A\), coupled to the input-code symmetry that has
been gauged.

### What to retain before the two constructions

1. The qLDPC construction gauges transversal Clifford **emergent
   symmetries**, not the logical Pauli operators labelled by \(H_1\) and
   \(H^1\).
2. The ancilla complex \(A_\bullet\) supplies temporary vertex qubits \(a\),
   surviving gauge-field qubits \(A\), and a cluster state specified entirely
   by \(\partial^a_1\) and \(d^a_0\).
3. Every ancilla 0-cocycle \(\boldsymbol\mu\in\ker d^a_0\) is both an
   \(X\)-symmetry of the temporary ancillas and a relation among the final
   \(A\)-sublattice \(X\)-checks.
4. Symmetry enrichment attaches a transversal gate
   \(U_{\boldsymbol\mu}\) to each such cocycle through Eq. (121).
5. The next subsection compares two ways to choose \(A_\bullet\): a
   homological choice that mirrors \(D_\bullet\), and a graph choice that
   needs only the symmetry required for one global gate.

## Section III.D: two approaches to gauging qLDPC codes

This short subsection is a decision point, not yet the full construction of
either resulting code.  Section III.C established the common requirement:
every ancilla 0-cocycle \(\boldsymbol\mu\in\ker d^a_0\) must be decorated by
an input-code transversal gate through

\[
\Omega_{a,BC}X^a_{\boldsymbol\mu}\Omega_{a,BC}^{\dagger}
=X^a_{\boldsymbol\mu}U_{\boldsymbol\mu}.
\tag{122}
\]

The choice of ancilla complex \(A_\bullet\) determines the available
0-cocycles, hence the set of gates that Eq. (122) must encode.  The paper
develops two natural choices.  They are not competing approximations; they
are designed for different symmetry resources supplied by the input code.

\[
\begin{array}{c|c|c}
&\text{homological gauging}&\text{graph gauging}\\
\hline
\text{ancilla complex}&A_\bullet\simeq D_\bullet&
A_\bullet\text{ is a connected graph complex}\\
\text{0-cocycle symmetries}&\text{a structured family}&
\text{one global generator}\\
\text{what is gauged}&\text{a compatible collection of gates}&
\text{one transversal gate}\\
\text{extra input structure}&\text{local Poincare duality}&
\text{none beyond the chosen gate}\\
\text{canonical example later}&\text{addressable transversal \(\mathsf{CZ}\)'s}&
\text{transversal \(\mathsf{SWAP}\)}
\end{array}
\tag{123}
\]

The word “structured” in the second row is deliberately cautious: the
relevant number is not simply the number of physical ancilla qubits, but the
dimension and support structure of \(\ker d^a_0\).  These cocycles label the
independent relations among final ancilla \(X\)-checks, and therefore the
independent symmetry sectors that can be enriched.

### Homological gauging: preserve the input's higher-dimensional structure

The homological route applies when the input complex \(D_\bullet\) has a
suitable algebraic version of **Poincare duality**.  The paper requires a
*local isomorphism* between

\[
H^2(D_\bullet)
\quad\text{and}\quad
H_0(D_\bullet).
\tag{124}
\]

At this stage, the most useful reading is operational.  An isomorphism says
that these two spaces carry the same independent information; *local* says
that the identification can be implemented using bounded-support incidence
data, rather than by a dense matrix reaching across the whole code.  It is
much stronger than the bare numerical statement
\(\dim H^2=\dim H_0\).  The later construction uses this local dictionary
to turn the check-redundancy data of one type into the local support data
needed to define transversal controlled gates.

For intuition, a two-dimensional toric-code lattice has a dual lattice:
vertices of one lattice correspond locally to plaquettes of the other.
Poincare duality abstracts precisely the part of this picture that survives
without drawing a surface.  A generic qLDPC code need not possess such a
local primal--dual dictionary, even though its chain complex still obeys
\(\partial_1\partial_2=0\).

When the dictionary does exist, the authors choose an ancilla that mirrors
the input complex,

\[
A_\bullet\simeq D_\bullet.
\tag{125}
\]

This does not mean that the ancilla qubits are the input qubits.  It means
that their check--qubit incidence pattern is an isomorphic copy of the one
used by \(B\) and \(C\).  Consequently its 0-cocycles have the same
structured family of relations that the duality can connect to collections
of transversal gates on \(B,C\).  Eq. (122) can then enrich different
\(\boldsymbol\mu\)'s by different, compatible gates.  This is the sense in
which the resulting symmetries are **addressable**: one is not limited to
gauging only the product of all available gates at once.

The later Poincare-duality section makes this statement concrete using
transversal controlled-\(Z\) gates.  For now, retain the logical order:

\[
\text{local duality of \(D_\bullet\)}
\ \Longrightarrow\ 
\text{structured 0-cocycles of \(A_\bullet\simeq D_\bullet\)}
\ \Longrightarrow\ 
\text{a compatible family of enrichable gates.}
\tag{126}
\]

### Graph gauging: retain only one global symmetry

Suppose instead that the input code offers one useful transversal gate, but
does not come with a local Poincare-duality structure or a decomposition
into independently addressable pieces.  The authors then choose
\(A_\bullet\) to be the chain complex of a **connected graph**:

\[
0\longrightarrow A_1\xrightarrow{\ \partial^a_1\ }A_0
\longrightarrow0.
\tag{127}
\]

There is no \(A_2\) in an ordinary graph.  Put a temporary \(a\) qubit on
each graph vertex and a surviving \(A\) gauge qubit on each graph edge, as
before.  Over \(\mathbb F_2\), a connected graph has one independent
0-cocycle, represented by the uniform vertex cochain

\[
\boldsymbol\mu_{\rm all}=\sum_{v\in V_A}\mathbf v,
\qquad
d^a_0\boldsymbol\mu_{\rm all}=0.
\tag{128}
\]

The second equation is easy to verify.  Each edge has two endpoints.  When
\(d^a_0\) tests the cochain on that edge, it adds one contribution from each
endpoint, obtaining \(1+1=0\) in \(\mathbb F_2\).  Conversely, on a
connected graph the condition \(d^a_0\boldsymbol\mu=0\) forces neighbouring
vertices to have equal values; connectivity then forces every vertex to have
the same value.  Thus the kernel is spanned by
\(\boldsymbol\mu_{\rm all}\).

The enrichment condition now contains only one nontrivial instruction:

\[
\Omega_{a,BC}X^a_{\boldsymbol\mu_{\rm all}}
\Omega_{a,BC}^{\dagger}
=X^a_{\boldsymbol\mu_{\rm all}}U.
\tag{129}
\]

This construction can gauge that one gate \(U\), but it cannot separately
gauge a family \(U_1,U_2,\ldots\): the necessary independent 0-cocycle
symmetries are absent.  This is exactly the distinction already visible in
the stacked-toric-code toy model, now expressed without layers.

There is an important universal example.  Any two identical quantum codes
have a physical transversal swap:

\[
U_{\mathsf{SWAP}}=\prod_{q\in Q}\mathsf{SWAP}(B_q,C_q).
\tag{130}
\]

It exchanges every physical qubit of copy \(B\) with its counterpart in
copy \(C\), so it maps each \(B\) stabilizer to the corresponding \(C\)
stabilizer and vice versa.  It is therefore an emergent symmetry of the two-
copy code space.  Graph gauging is available whenever this one global gate
can be matched by a suitable symmetry-enrichment circuit; it requires no
Poincare duality of \(D_\bullet\).

“Choose a graph” does not mean choose one arbitrarily.  Its incidence matrix
must still let a finite-depth \(\Omega_{a,BC}\) satisfy Eq. (129), and it must
retain bounded-weight checks if the final code is to remain qLDPC.  Hence the
appropriate graph depends on the input complex and on the gate being gauged.

### The practical decision rule

Before reading the two detailed constructions, use the following rule.

1. If the input code has a local Poincare-duality structure and the goal is
   to gauge a structured, addressable family of transversal gates, follow
   **homological gauging**.
2. If the goal is to gauge one global transversal gate—especially the
   inevitable swap between two identical copies—and no usable local duality
   is available, follow **graph gauging**.

Both routes use the same physical mechanism: an ancilla cluster state,
symmetry enrichment, \(X\)-measurement of temporary ancillas, and
feedforward.  They differ only in the symmetry algebra deliberately built
into the ancilla.

## Section III.E: non-Abelian codes from gauging with graph states

The graph-state construction is the paper's general-purpose route when the
input qLDPC code has a useful **single global** transversal symmetry but does
not have the local Poincare-duality structure required by homological
gauging.  Its central idea is simple:

\[
\boxed{\text{replace the input's missing geometric duality by a deliberately
chosen connected ancilla graph.}}
\tag{131}
\]

The graph is not meant to represent the geometry of the qLDPC code.  It is
an auxiliary device whose one global 0-cocycle symmetry supplies exactly one
symmetry generator to gauge.  The input code contributes the transversal
gate; the graph contributes the gauge-field degrees of freedom and the
symmetry that is tied to that gate.

### What this section does, and does not, assume

We again begin with two identical CSS qLDPC codes \(B\) and \(C\), whose
common check--qubit incidence data are described by \(D_\bullet\).  Suppose
there is a transversal operation \(U\) on the pair that has \(\mathbb Z_2\)
character: applying it twice acts trivially on the code space.  The canonical
case is

\[
U_{\mathsf{SWAP}}=\prod_{q\in Q}\mathsf{SWAP}(B_q,C_q).
\tag{132}
\]

No Poincare duality, cup product, or layer decomposition of \(D_\bullet\) is
assumed.  This is why the graph route is more broadly applicable than the
homological one.  But “more general” does not mean automatic: we must still
choose a graph and an entangling circuit that meet three precise conditions.

The distinction from the earlier homological route is useful to keep in
view:

\[
\begin{gathered}
\text{homological route: input local primal--dual structure and a gate family}
\\[-1pt]
\text{\hspace{25mm}\(\Longleftrightarrow\) ancilla: a matching copy of that structure;}\\[3pt]
\text{graph route: input one uniform transversal \(\mathbb Z_2\) gate}
\\[-1pt]
\text{\hspace{25mm}\(\Longleftrightarrow\) ancilla: one global symmetry of a chosen graph.}
\end{gathered}
\tag{133}
\]

### The graph ancilla, written without a picture

Choose a finite connected graph \(G=(V,E)\).  Its chain complex is just

\[
0\longrightarrow A_1=\mathbb F_2[E]
\xrightarrow{\ \partial^a_1\ }
A_0=\mathbb F_2[V]
\longrightarrow0.
\tag{134}
\]

For an edge \(e=\langle v,w\rangle\), the boundary map is

\[
\partial^a_1[e]=[v]+[w].
\tag{135}
\]

The ancilla has two kinds of qubit:

- a temporary qubit \(a_v\) at every graph vertex \(v\in V\);
- a gauge-field qubit \(A_e\) at every graph edge \(e\in E\).

The notation is the same as before, but now it has an ordinary graph
interpretation.  Let \(\mathbf v\in A^0\) be the indicator cochain at
vertex \(v\).  Since \(d^a_0=(\partial^a_1)^{\mathsf T}\),
\(d^a_0\mathbf v\) selects exactly the graph edges incident on \(v\).
The graph cluster state is stabilized by

\[
K^a_v=X_{a_v}\prod_{e\ni v}X_{A_e},
\qquad
K^A_{\langle v,w\rangle}=Z_{A_{\langle v,w\rangle}}Z_{a_v}Z_{a_w}.
\tag{136}
\]

This is Eq. (117) specialized to an ordinary graph.  The first stabilizer
ties a vertex qubit to the incident gauge-field qubits.  The second ties an
edge gauge qubit to the two endpoint vertex qubits.  For an endpoint--edge
pair, the two stabilizers have two anticommuting overlaps, one on the vertex
qubit and one on the edge qubit, so they commute overall.

### Why connectedness produces exactly one symmetry to gauge

The temporary vertex qubits have a global \(X\)-symmetry

\[
X^a_{\boldsymbol\mu_{\rm all}}
=\prod_{v\in V}X_{a_v},
\qquad
\boldsymbol\mu_{\rm all}=\sum_{v\in V}\mathbf v.
\tag{137}
\]

It is a 0-cocycle because each edge sees both of its endpoints:

\[
\bigl(d^a_0\boldsymbol\mu_{\rm all}\bigr)([\langle v,w\rangle])
=1+1=0\qquad\text{in }\mathbb F_2.
\tag{138}
\]

Conversely, let \(\boldsymbol\mu\in\ker d^a_0\).  Equation (138), with
\(1\)'s replaced by the values of \(\boldsymbol\mu\), says that the values
of \(\boldsymbol\mu\) at the endpoints of every edge are equal.  If the
graph is connected, that equality propagates along paths, so all vertices
have the same value.  Therefore

\[
H^0(A_\bullet)=\ker d^a_0
=\operatorname{span}_{\mathbb F_2}\{\boldsymbol\mu_{\rm all}\}
\cong\mathbb Z_2.
\tag{139}
\]

This proof explains the role of connectedness more deeply than the slogan
“one connected graph gives one symmetry.”  A graph with \(r\) connected
components has \(r\) independent uniform cocycles, one per component.  The
authors deliberately take \(r=1\), because the graph construction is
intended to gauge one global gate rather than an independently addressable
family.

### Symmetry enrichment becomes a group-commutator test

The graph's sole nontrivial cocycle must be linked to the desired input-code
gate.  In the notation of Section III.C, the condition is

\[
\Omega_{a,BC}X^a_{\boldsymbol\mu_{\rm all}}
\Omega_{a,BC}^{\dagger}
=X^a_{\boldsymbol\mu_{\rm all}}U.
\tag{140}
\]

Because \((X^a_{\boldsymbol\mu_{\rm all}})^2=I\), multiply Eq. (140) on the
left by \(X^a_{\boldsymbol\mu_{\rm all}}\) to obtain the equivalent form
used in the paper:

\[
X^a_{\boldsymbol\mu_{\rm all}}\,
\Omega_{a,BC}\,
X^a_{\boldsymbol\mu_{\rm all}}\,
\Omega_{a,BC}^{\dagger}=U.
\tag{141}
\]

The left-hand side is a group commutator: it measures the failure of
\(\Omega_{a,BC}\) to commute with the global ancilla symmetry.  The required
failure is not an error.  It is exactly the desired physical statement:
flipping every temporary ancilla vertex performs the transversal gate \(U\)
on the two matter codes.  After the \(a\) qubits are measured and removed,
this relation is what makes \(U\) a gauged, rather than externally imposed,
symmetry.

### The three graph requirements

The paper's requirements can now be stated sharply.

\[
\begin{array}{c|p{0.67\linewidth}}
\text{requirement}&\text{reason}\\
\hline
\text{connected graph}&
\(\ker d^a_0\cong\mathbb Z_2\), so the ancilla supplies exactly the one
global symmetry intended for gauging.\\
\text{enrichment circuit \(\Omega\)}&
It must satisfy Eq. (140), or equivalently Eq. (141), so the global cocycle
symmetry implements the chosen transversal gate \(U\).\\
\text{LDPC preservation}&
Every final stabilizer must have bounded weight, and every qubit must occur
in only a bounded number of final stabilizers.  This constrains both graph
degrees and the locality/sparsity of \(\Omega\).
\end{array}
\tag{142}
\]

The final row is essential.  A connected graph always supplies the desired
one-dimensional symmetry, but a dense graph can give a high-weight vertex
stabilizer \(K^a_v\), and a nonlocal enrichment circuit can spread one
input check across too many ancilla qubits.  Either failure would destroy the
LDPC property, even though the abstract symmetry condition was correct.

The next subsection gives the promised worked example: gauge
\(U_{\mathsf{SWAP}}\).  It will introduce a sparse assignment from input
code data to graph vertices, construct \(\Omega_{a,BC}\) explicitly, and
derive the resulting non-Abelian stabilizers.

## Section III.E.1: example - gauging the transversal \(\mathsf{SWAP}\) gate

We now work through the paper's first graph-state example.  Its target
symmetry is the transversal interchange of the two input copies:

\[
U_{\mathsf{SWAP}}
=\prod_{e\in Q}\mathsf{SWAP}_{B_e,C_e}.
\tag{143}
\]

Here \(Q\) is the set of input qubits.  Each \(e\in Q\) labels one qubit
in copy \(B\) and its counterpart in copy \(C\).  The two-qubit operator
\(\mathsf{SWAP}_{B_e,C_e}\) exchanges their states:

\[
\mathsf{SWAP}_{B_e,C_e}
\bigl(|b\rangle_{B_e}|c\rangle_{C_e}\bigr)
=|c\rangle_{B_e}|b\rangle_{C_e}.
\tag{144}
\]

The product in Eq. (143) is unambiguous because its factors act on disjoint
pairs.  The word *transversal* means precisely this: the gate is a product
of identical, pairwise local gates, one per input-qubit label.  If the two
copies use the same CSS code, this gate exchanges the entire two code blocks
without spreading a single physical error into many qubits within either
block.

The aim is not merely to implement Eq. (143).  It is to make it the global
\(\mathbb Z_2\) symmetry which is subsequently gauged by the graph-state
ancilla.  The result is the qLDPC analogue of the layer-exchange gauging
that led to non-Abelian excitations in Section II.

### Reading the enrichment circuit in practice

The formula for \(\Omega\) looks more formidable than the operation it
describes.  Start by keeping three label sets apart:

- \(Q\) labels the input qubits.  For each \(e\in Q\), there is one
  qubit \(B_e\) and one qubit \(C_e\), which are the two qubits to be
  swapped.
- \(V\) labels vertices of the new auxiliary graph.  For each \(v\in V\),
  there is a temporary ancilla qubit \(a_v\).  This qubit is used as a
  control and is measured away later.
- \(E\) labels edges of that graph.  For each graph edge \(f\in E\), there
  is a surviving gauge qubit \(A_f\).  These edge qubits are not the
  controls in the SWAP circuit; they become important after the
  measurement.

The paper sometimes uses \(e\) for both an input-code edge/qubit and a
graph edge.  In this note, \(e\) always means an input-qubit label in this
example, and \(f\) means a graph-edge label.

Now choose, for each input qubit \(e\), which temporary ancilla should
control its swap.  Call that vertex \(v_e\).  This choice is what the paper
calls \(\phi\):

\[
\phi(e)=v_e.
\]

Read this sentence literally:

> The temporary qubit \(a_{v_e}\) controls the swap of \(B_e\) and \(C_e\).

The occupation number

\[
n^a_{v_e}=\frac{I-Z^a_{v_e}}2
\]

has value \(0\) when \(a_{v_e}\) is \(|0\rangle\), and value \(1\) when
it is \(|1\rangle\).  Therefore the enrichment circuit is simply

\[
\Omega_{a,BC}
=\prod_{e\in Q}
\left(\mathsf{SWAP}_{B_e,C_e}\right)^{n^a_{v_e}}.
\]

In words: for every input-qubit pair \((B_e,C_e)\), do a controlled SWAP,
with \(a_{v_e}\) as its control.  This is the whole practical definition
of symmetry enrichment in this example.

So where does the paper's integral
\(\int_{\phi(\mathbf e)}\boldsymbol v\) come from?  It is only a compact
way to write the preceding choice while keeping the product over *all*
vertices \(v\in V\).  Its value is

\[
\int_{\phi(\mathbf e)}\boldsymbol v
=\begin{cases}
1,&v=v_e,\\
0,&v\ne v_e.
\end{cases}
\]

Thus, in the paper's double product, every vertex gives the identity except
the one chosen by \(\phi(e)\).  The integral is not a spatial integral.  It
is a binary yes/no test: ``is this particular vertex \(v\) the chosen
controller for input qubit \(e\)?''  Substituting the two possible answers
into the paper's expression immediately recovers the simple controlled-SWAP
circuit above.

The paper allows a more general choice in which \(\phi(e)\) names several
vertices.  Then several temporary qubits control the same SWAP.  Its
condition that \(\int_{\phi(\mathbf e)}\boldsymbol\mu=1\) says that their
number must be odd.  The authors then choose the simplest case: exactly one
controller \(v_e\) for every \(e\).

One piece of notation is implicit in the paper.  It says that \(\phi\) maps
into \(D_0\), even though the controls live at vertices of the distinct
ancilla graph.  To read the formula, identify the relevant basis labels of
\(D_0\) with the graph vertices \(V\), or equivalently supply a map from
those labels to \(V\).  The paper does not display that identification, so
we will always state it in words as ``\(\phi(e)\) chooses the controlling
ancilla vertex.''  Likewise, its use of both \(D^1\) and \(D_1\) is a way
of saying that the same qubit-label assignment is used whether \(e\) is
encountered in an \(X\)-check or a \(Z\)-check.

### A warning about labels: \(e\), \(\mathbf e\), and \(\phi\)

This example uses the chain-complex notation introduced above, but it is
easy to lose track of what is a qubit and what is a binary vector.  The
following dictionary is useful.

\[
\begin{array}{c|l}
\text{paper notation}&\text{meaning in this example}\\
\hline
e\in Q&\text{one physical input-qubit label (equivalently, a basis 1-cell)}\\
\lbrack e\rbrack\in D_1&\text{the corresponding basis vector, regarded as a chain}\\
\mathbf e\in D^1&\text{the coordinate cochain which reads whether }\lbrack e\rbrack\text{ is present}\\
v\in V&\text{one vertex of the temporary-ancilla graph}\\
\boldsymbol v\in D^0&\text{the associated coordinate 0-cochain}\\
\phi&\text{the sparse rule which assigns the qubit }e\text{ to an ancilla vertex.}
\end{array}
\tag{149}
\]

The paper writes

\[
\phi:D^1\oplus D_1\longrightarrow D_0.
\tag{150}
\]

At first sight this may look strange: why can \(\phi\) accept both a
cochain and a chain?  The construction encounters an input-qubit label in
two complementary ways.  An \(X\)-type CSS check is naturally described by
a 1-*cochain* \(\mathbf e\), while a \(Z\)-type check is naturally
described by a 1-*chain* \([e]\).  Once bases have been chosen, both carry
the same finite list of qubit labels.  Equation (150) records that the same
sparse incidence rule is used in both appearances.  Operationally, you may
remember just the basis-level statement

\[
e\longmapsto\phi(e)=v_e\in V:
\qquad\text{``qubit \(e\) is controlled by temporary ancilla \(a_{v_e}\).''}
\tag{151}
\]

As explained in the preceding practical guide, the paper tacitly identifies
the output \(D_0\) of \(\phi\) with labels of ancilla-graph vertices.  More
formally, one must choose a labelled copy of the basis of \(D_0\) as \(V\),
or supply a map into \(A_0\).  This is why a symbol such as \(\phi(e)\) may
be used both as a 0-cell label and as a graph vertex.  It is a label, not an
additional quantum degree of freedom.

The map is required to be sparse and local.  Sparsity says that its binary
matrix has only \(O(1)\) nonzero entries in each relevant row and column.
The stronger geometric condition mentioned by the paper is

\[
\phi(\mathbf e)\in\partial[e].
\tag{152}
\]

When the input code has a geometric cellulation, this says that the vertex
chosen for qubit \(e\) is one of the endpoints of that edge.  For a general
qLDPC complex, it should be read as an incidence condition: \(\phi(e)\)
must be a 0-cell participating in the boundary data of \(e\).  This is not
needed to define the symmetry, but it is the natural condition for keeping
the later stabilizers local in the code's incidence graph.

### The enrichment circuit is a collection of controlled swaps

For a temporary ancilla vertex \(v\), define its computational-basis
occupation operator by

\[
n^a_v:=\frac{I-Z^a_v}{2}.
\tag{153}
\]

It has eigenvalue \(0\) on \(|0\rangle_a\) and \(1\) on \(|1\rangle_a\).
Thus \(W^{n^a_v}\), for an involution \(W^2=I\), means ``apply \(W\) if
the \(a_v\) qubit is \(|1\rangle\), and otherwise do nothing.''  This
compact exponent notation is used throughout the paper.

The paper's enrichment circuit is

\[
\Omega_{a,BC}
=\prod_{v,e}
\left(\mathsf{SWAP}_{B_e,C_e}\right)^
 {\,n^a_v\int_{\phi(\mathbf e)}\boldsymbol v}.
\tag{154}
\]

The integral is not a continuum integral.  It is the \(\mathbb F_2\)
pairing between a 0-chain and a 0-cochain:

\[
\int_{\phi(\mathbf e)}\boldsymbol v
=\boldsymbol v\bigl(\phi(\mathbf e)\bigr)
=\begin{cases}
1,&v=\phi(e),\\
0,&v\ne\phi(e).
\end{cases}
\tag{155}
\]

Consequently, only one term in the product over \(v\) is active for a
given qubit \(e\).  With the basis-level assignment \(v_e=\phi(e)\),
Eq. (154) is simply

\[
\boxed{\quad
\Omega_{a,BC}
=\prod_{e\in Q}
\left(\mathsf{SWAP}_{B_e,C_e}\right)^{n^a_{v_e}}.
\quad}
\tag{156}
\]

It is a product of Fredkin gates: temporary qubit \(a_{v_e}\) controls a
swap of the two matter qubits \(B_e,C_e\).  Controlled swaps for different
\(e\)'s commute, even when they share their control, because their target
pairs are disjoint.  This makes the circuit particularly transparent.

### Why this circuit enriches the global cocycle symmetry

The unique nontrivial graph cocycle is the operation
\(X^a_{\boldsymbol\mu_{\rm all}}=\prod_{v\in V}X^a_v\).  Conjugating the
occupation projector by its control flip gives

\[
X^a_v n^a_v X^a_v=I-n^a_v.
\tag{157}
\]

Use this in one controlled-swap factor.  Since \(\mathsf{SWAP}^2=I\),

\[
X^a_{v_e}
\left(\mathsf{SWAP}_{B_e,C_e}\right)^{n^a_{v_e}}
X^a_{v_e}
\left(\mathsf{SWAP}_{B_e,C_e}\right)^{n^a_{v_e}}
=\mathsf{SWAP}_{B_e,C_e}.
\tag{158}
\]

Multiplying this result over all \(e\) gives exactly the required
commutator condition from Eq. (141):

\[
X^a_{\boldsymbol\mu_{\rm all}}\,
\Omega_{a,BC}\,
X^a_{\boldsymbol\mu_{\rm all}}\,
\Omega_{a,BC}^{\dagger}
=\prod_e\mathsf{SWAP}_{B_e,C_e}
=U_{\mathsf{SWAP}}.
\tag{159}
\]

This is the central calculation of the example.  Globally flipping every
temporary ancilla reverses every control bit.  Each controlled swap is then
applied exactly once in the commutator, so the global ancilla symmetry acts
on the matter as layer exchange.  If a qubit were assigned to an even number
of controlling vertices, its swaps would cancel pairwise; this is the
paper's condition that \(\int_{\phi(\mathbf e)}\boldsymbol\mu=1\) for
each \(e\).  Choosing one vertex \(\phi(e)\) per qubit is the simplest way
to satisfy it.

### Conjugating the input stabilizers before measurement

It is helpful to pause at the intermediate, premeasurement stabilizers.
For one input qubit, controlled swap changes a Pauli on the \(B\) copy as

\[
\begin{aligned}
\Omega X^B_e\Omega^\dagger
 &=X^B_e\left(X^B_eX^C_e\right)^{n^a_{\phi(e)}},\\
\Omega Z^B_e\Omega^\dagger
 &=Z^B_e\left(Z^B_eZ^C_e\right)^{n^a_{\phi(e)}}.
\end{aligned}
\tag{160}
\]

Check the two possible control values.  If \(n^a_{\phi(e)}=0\), the right
side is the original \(B\) Pauli.  If it is one, the extra product turns
\(X^B_e\) into \(X^C_e\), or \(Z^B_e\) into \(Z^C_e\), exactly as a swap
should.  The corresponding formulas for a \(C\) Pauli have the same
correction factor.

Therefore an \(X\)-check labelled by the 0-cochain \(\boldsymbol v\)
becomes

\[
\widetilde S^X_{B,\boldsymbol v}
=X^B_{d_0\boldsymbol v}
 \prod_{\mathbf e\in d_0\boldsymbol v}
 \left(X^B_{\mathbf e}X^C_{\mathbf e}\right)^{n^a_{\phi(\mathbf e)}},
\tag{161}
\]

This equation is simply the original \(B\)-check with the one-qubit rule
in Eq. (160) applied to every qubit in that check.  To read it, start with
the 0-cochain \(\boldsymbol v\in D^0\).  Its coboundary

\[
d_0\boldsymbol v\in D^1
\]

is a binary list of input qubits: its value on the basis chain \([e]\) is
either zero or one.  The shorthand

\[
X^B_{d_0\boldsymbol v}
=\prod_{e\in Q}\left(X^B_e\right)^{(d_0\boldsymbol v)([e])}
\]

therefore means ``put \(X^B_e\) on precisely those qubits for which
\((d_0\boldsymbol v)([e])=1\).''  In the displayed formula,
\(\mathbf e\in d_0\boldsymbol v\) is only a compact shorthand for the
same condition.  A cochain is not literally a set: the product is over the
*support* of the binary cochain \(d_0\boldsymbol v\).

For a small graph-like example, suppose \(\boldsymbol v\) selects a vertex
whose check contains three input qubits \(e_1,e_2,e_3\).  Then

\[
d_0\boldsymbol v=\mathbf e_1+\mathbf e_2+\mathbf e_3,
\qquad
X^B_{d_0\boldsymbol v}=X^B_{e_1}X^B_{e_2}X^B_{e_3}.
\]

Equation (161) says that this becomes

\[
\begin{aligned}
\widetilde S^X_{B,\boldsymbol v}
={}&X^B_{e_1}X^B_{e_2}X^B_{e_3}\\
&\times
\left(X^B_{e_1}X^C_{e_1}\right)^{n^a_{\phi(e_1)}}
\left(X^B_{e_2}X^C_{e_2}\right)^{n^a_{\phi(e_2)}}
\left(X^B_{e_3}X^C_{e_3}\right)^{n^a_{\phi(e_3)}}.
\end{aligned}
\]

For any one qubit \(e_i\), the corresponding temporary-control value
decides what happens.  If \(n^a_{\phi(e_i)}=0\), its extra factor is the
identity and the check still contains \(X^B_{e_i}\).  If
\(n^a_{\phi(e_i)}=1\), then

\[
X^B_{e_i}\left(X^B_{e_i}X^C_{e_i}\right)=X^C_{e_i}.
\]

That local part of the stabilizer has been swapped from copy \(B\) to copy
\(C\).  The compact formula in Eq. (161) says this independently for every
qubit in the original check.  A general \(\boldsymbol v\) can label a
product of check generators rather than one independent generator; if
\(d_0\boldsymbol v=0\), it labels the identity.  This is why the paper uses
all 0-cochains rather than choosing an independent check basis at this
stage.

The corresponding \(C\)-check has exactly the same correction factors,
with \(B\) and \(C\) exchanged.  Similarly, a \(Z\)-check labelled by a
2-chain \([p]\) becomes

\[
\widetilde S^Z_{B,[p]}
=Z^B_{\partial_2[p]}
 \prod_{e\in\partial_2[p]}
 \left(Z^B_eZ^C_e\right)^{n^a_{\phi(e)}}.
\tag{162}
\]

The temporary-vertex graph stabilizer has an equally important change.  A
control flip \(X^a_v\) toggles every controlled swap assigned to \(v\), so

\[
\widetilde K^a_v
=X^a_v X^A_{d^a_0\boldsymbol v}
 \mathsf{SWAP}_{\phi^T(v)},
\qquad
\mathsf{SWAP}_{\phi^T(v)}
:=\prod_{e:\,\phi(e)=v}\mathsf{SWAP}_{B_e,C_e}.
\tag{163}
\]

Equation (163) is the original vertex stabilizer of the graph cluster state,
now conjugated by the enrichment circuit.  Before enrichment it was only

\[
K^a_v=X^a_v X^A_{d^a_0\boldsymbol v}.
\]

Here \(d^a_0\) is the coboundary map of the *ancilla graph*, not the
coboundary map of the input code.  If the graph vertex \(v\) is incident
on edges \(f_1,f_2,f_3\), then

\[
X^A_{d^a_0\boldsymbol v}=X^A_{f_1}X^A_{f_2}X^A_{f_3}.
\]

Thus the original cluster constraint says: flip the temporary qubit
\(a_v\), and simultaneously flip every surviving gauge-field qubit on a
graph edge incident on \(v\).

The final factor in Eq. (163) records which matter-qubit swaps were
controlled by \(a_v\):

\[
\mathsf{SWAP}_{\phi^{\mathsf T}(v)}
=\prod_{e:\,\phi(e)=v}\mathsf{SWAP}_{B_e,C_e}.
\]

The superscript \(\mathsf T\) is the paper's matrix-transpose notation.  In
the chosen bases, \(\phi^{\mathsf T}(v)\) means the list of all input-qubit
labels \(e\) whose assigned controlling vertex is \(v\).  For example, if

\[
\phi(e_1)=v,\qquad\phi(e_3)=v,
\]

then

\[
\mathsf{SWAP}_{\phi^{\mathsf T}(v)}
=\mathsf{SWAP}_{B_{e_1},C_{e_1}}
 \mathsf{SWAP}_{B_{e_3},C_{e_3}}.
\]

If, in addition, \(v\) has the two incident graph edges \(f_1,f_2\), the
full stabilizer is

\[
\widetilde K^a_v
=X^a_v X^A_{f_1}X^A_{f_2}
 \mathsf{SWAP}_{B_{e_1},C_{e_1}}
 \mathsf{SWAP}_{B_{e_3},C_{e_3}}.
\]

Why does this new SWAP factor appear?  The enrichment circuit attached
controlled swaps to \(a_v\).  Conjugating \(X^a_v\) through them flips
their control bit.  For every input pair controlled by \(a_v\), this leaves
one ordinary swap:

\[
\Omega_{a,BC}X^a_v\Omega_{a,BC}^{\dagger}
=X^a_v\prod_{e:\,\phi(e)=v}\mathsf{SWAP}_{B_e,C_e}.
\]

The \(X^A_{d^a_0\boldsymbol v}\) factor is unaffected, which gives
Eq. (163).  Physically, the equation says that a local ancilla/gauge
transformation at vertex \(v\) is tied to swapping the two matter-code
layers on precisely the qubits assigned to \(v\).

Finally, the graph-edge stabilizers \(Z^A_f Z^a_{\partial f}\) are unchanged
because \(\Omega_{a,BC}\) is diagonal in every control \(Z^a_v\).

### Measuring the temporary qubits: how strings of \(Z^A\) appear

**Vertex stabilizers.**  First consider only the graph-cluster vertex
stabilizer \(\widetilde K^a_v\) in Eq. (163).  Its \(X\)-measurement has a
particularly direct effect: it removes \(X^a_v\) and leaves a constraint on
the surviving \(A,B,C\) qubits.

The protocol now measures every \(a_v\) in the \(X\) basis and, after the
standard Pauli-frame correction, takes the outcomes to be \(+1\).  Thus the
factor \(X^a_v\) can be removed from Eq. (163), leaving the gauged vertex
constraint

\[
G^A_v=X^A_{d^a_0\boldsymbol v}\,
\mathsf{SWAP}_{\phi^T(v)}.
\tag{164}
\]

Thus \(G^A_v\) is precisely what the graph cluster state's vertex
stabilizer becomes after symmetry enrichment and the \(X\)-measurement
(with postselection or Pauli-frame correction) removes the temporary qubit
\(a_v\).

It is called a constraint because physical code states must satisfy

\[
G^A_v|\Psi_{\rm gauged}\rangle
=|\Psi_{\rm gauged}\rangle.
\]

And it is called gauged because it is now a local relation involving only
surviving degrees of freedom:

- an \(X\) transformation on gauge-field edges adjacent to \(v\);
- the associated swaps of \(B,C\) matter qubits.

Without enrichment, the surviving relation would have been only

\[
X^A_{d^a_0\boldsymbol v}=1,
\]

which is an ordinary pure-\(\mathbb Z_2\) gauge-type vertex constraint.
Enrichment dresses it by layer exchange.

A useful global check is to multiply all these local constraints.  Every
\(A\)-edge appears at both of its endpoints, so its two \(X^A\)'s cancel.
If every input qubit is assigned to exactly one vertex, the SWAP factors
multiply to the global transversal swap:

\[
\prod_{v\in V}G^A_v
=U_{\mathsf{SWAP}}.
\]

This is the essential gauging idea: the former global \(B\leftrightarrow C\)
symmetry has been distributed across local vertex constraints of the
enlarged \(A,B,C\) system.

**\(B\)- and \(C\)-code stabilizers.**  We now return to a different
family of stabilizers: the dressed input-code checks in Eqs. (161) and
(162).  Their measurement problem is not solved merely by setting an
\(X^a_v\) factor to \(+1\), because they contain \(Z^a\)-dependent
occupation projectors.  They must first be rewritten using the graph-edge
stabilizers.

There is one remaining issue.  Equations (161) and (162) still contain
operators on measured \(a\) qubits.  More precisely, the problematic
operators are the occupation projectors in their exponents,

\[
n^a_{\phi(e)}=\frac{I-Z^a_{\phi(e)}}2.
\]

For example, the factor

\[
\left(X^B_eX^C_e\right)^{n^a_{\phi(e)}}
\]

is a controlled operator: it acts as \(I\) or as \(X^B_eX^C_e\), depending
on the \(Z\)-basis value of the temporary qubit \(a_{\phi(e)}\).  Thus the
\(n^a\)'s are not harmless numerical exponents; before measurement they
are genuine operators acting on the temporary ancilla and the matter system.
The same point applies to the \(n^a_{\phi(e)}\)'s in Eq. (162).

We measure every \(a\) qubit in the \(X\) basis, whereas \(n^a\) is made
from \(Z^a\).  They do not commute:

\[
\left[X^a_v,n^a_v\right]\ne0.
\]

Consequently, after projecting a qubit onto \(|+\rangle\), one cannot
replace \(n^a_v\) by either \(0\) or \(1\), nor can one leave it in a
stabilizer of the surviving system.  In contrast, a \(Z\)-basis measurement
would supply a definite value for \(n^a_v\), but that is not the measurement
used by the gauging protocol.

The paper therefore first changes to an equivalent set of stabilizer
generators in which the unwanted temporary-ancilla dependence occurs in
pairs such as \(Z^a_uZ^a_w\).  The graph cluster-state stabilizers then
replace each such pair by a string of \(Z^A\)'s on the surviving edge
qubits.  Only after this rewriting is it safe to measure and discard the
\(a\) qubits.  Here ``equivalent'' means *equal on the prepared stabilizer
subspace*, after multiplication by already satisfied input and cluster
stabilizers; it does not mean that the displayed operators are unconstrained
identities on the whole Hilbert space.  This distinction is important.

The key cluster-state relation on any graph path \(\gamma_{u,w}\) from
vertices \(u\) to \(w\) is

\[
\prod_{f\in\gamma_{u,w}}
\bigl(Z^A_f Z^a_{\partial f}\bigr)
=Z^A_{\gamma_{u,w}}Z^a_uZ^a_w\doteq I.
\tag{165}
\]

Read Eq. (165) directly as a product of stabilizers.  Every factor
\(Z^A_fZ^a_{\partial f}\) in the product is a graph-edge stabilizer, so it
acts as \(+1\) on the premeasurement cluster state.  Their product must
therefore also act as \(+1\) on that state.

Now take a simple path from \(u\) to \(w\).  Every temporary vertex in the
interior of the path belongs to exactly two successive graph edges.  Its
\(Z^a\) operator consequently occurs twice in the product and cancels:

\[
\left(Z^a_{\text{interior vertex}}\right)^2=I.
\]

The two endpoint vertices \(u,w\) occur only once, so their \(Z^a\)'s do
*not* cancel.  Each edge of the path also occurs once, leaving one \(Z^A\)
on each surviving edge qubit.  Thus it is the combined operator

\[
Z^A_{\gamma_{u,w}}Z^a_uZ^a_w
\]

that is equivalent to the identity on the premeasurement stabilizer
subspace.  Hence,

\[
Z^a_uZ^a_w\doteq Z^A_{\gamma_{u,w}}.
\tag{166}
\]

The symbol \(\doteq\) means equality on that stabilized subspace, not an
operator identity on every state.  Equation (166) is the precise reason
that a pair of unwanted temporary-ancilla \(Z\)'s can be replaced by a
string of \(Z\)'s on the surviving \(A\) edge qubits.  The notation
\(\langle u,w\rangle\) in the paper denotes a chosen such path; it need
not be a single graph edge.

After this generator rewriting, the paper gives the surviving matter
checks in the following form.  For an \(X\)-check \(\boldsymbol v\), choose
the graph path \(\langle\phi(\mathbf e),v\rangle\) for every qubit in its
support:

\[
\begin{aligned}
S^{X,\mathrm{gauged}}_{B,\boldsymbol v}
 &=X^B_{d_0\boldsymbol v}
 \prod_{\mathbf e\in d_0\boldsymbol v}
 \left(Z^A_{\langle\phi(\mathbf e),v\rangle}\right)^
 {m^B_{\mathbf e}+m^C_{\mathbf e}},\\
S^{X,\mathrm{gauged}}_{C,\boldsymbol v}
 &=X^C_{d_0\boldsymbol v}
 \prod_{\mathbf e\in d_0\boldsymbol v}
 \left(Z^A_{\langle\phi(\mathbf e),v\rangle}\right)^
 {m^B_{\mathbf e}+m^C_{\mathbf e}},
\end{aligned}
\tag{167}
\]

Here \(m^B_{\mathbf e}=(I-X^B_{\mathbf e})/2\), and similarly for \(C\).
The sum in each exponent is modulo two.

**Deriving Eq. (167), including the origin of the path.**  Temporarily use
the simpler symbol \(s\) for one input \(X\)-check.  If

\[
E_s:=\operatorname{supp}(s),
\]

then its checks in the two copies are

\[
S^X_{B,s}=\prod_{e\in E_s}X^B_e,
\qquad
S^X_{C,s}=\prod_{e\in E_s}X^C_e.
\]

In the paper's notation, \(s\) is the basis label \(v\), its coordinate
cochain is \(\boldsymbol v\), and \(E_s=\operatorname{supp}(d_0\boldsymbol
v)\).  The paper also uses the same label \(s\) for a vertex of the
ancilla graph.  This identification is implicit in the paper; formally one
could instead introduce a map sending each check label to a chosen graph
vertex.

For each input qubit \(e\), the map \(\phi\) chooses one ancilla vertex
\(\phi(e)\) whose temporary qubit controls the SWAP of \(B_e\) and \(C_e\).
This controller need not equal \(s\).  Indeed, one physical qubit can belong
to several \(X\)-checks, whereas the simplifying assumption in the paper
assigns it only one controller \(\phi(e)\).  If \(e\) belongs to two checks
\(s\) and \(t\), one cannot in general have both \(\phi(e)=s\) and
\(\phi(e)=t\).

Let

\[
P_e:=X^B_eX^C_e.
\]

Equation (161) says that after symmetry enrichment the dressed \(B\)-check
is

\[
\widetilde S^X_{B,s}
=S^X_{B,s}\prod_{e\in E_s}P_e^{n^a_{\phi(e)}}.
\tag{167a}
\]

Only the controller occupations \(n^a_{\phi(e)}\) occur here; no operator
on \(a_s\) has appeared yet.  We now introduce one in a way that does not
change the enriched state.

First define

\[
Q_s:=S^X_{B,s}S^X_{C,s}=\prod_{e\in E_s}P_e.
\tag{167b}
\]

The two original checks give \(Q_s=+1\) before enrichment.  More
importantly, this remains true afterwards.  A SWAP on \(B_e,C_e\) leaves
\(P_e=X^B_eX^C_e\) invariant, so every controlled-SWAP in the enrichment
circuit commutes with \(Q_s\).  If
\(\lvert\Psi_{\mathrm{enr}}\rangle=\Omega\lvert\Psi_0\rangle\), then

\[
Q_s\lvert\Psi_{\mathrm{enr}}\rangle
=\Omega Q_s\lvert\Psi_0\rangle
=\lvert\Psi_{\mathrm{enr}}\rangle.
\tag{167c}
\]

Since \(n^a_s\) acts on an ancilla and commutes with \(Q_s\), the controlled
operator

\[
Q_s^{n^a_s}=(I-n^a_s)+n^a_sQ_s
\]

also acts as the identity on the enriched state.  We may therefore multiply
Eq. (167a) by it.  Using Eq. (167b), this gives the equivalent representative

\[
\widetilde S^X_{B,s}
\doteq
S^X_{B,s}\prod_{e\in E_s}
P_e^{n^a_{\phi(e)}+n^a_s}.
\tag{167d}
\]

This multiplication is the precise step that introduces the previously
absent operator on \(a_s\).

For each \(e\), the following is an operator identity:

\[
P_e^{n^a_{\phi(e)}+n^a_s}
=\left(Z^a_{\phi(e)}Z^a_s\right)^{m^B_e+m^C_e},
\qquad
m^B_e=\frac{I-X^B_e}{2},
\tag{167e}
\]

with the exponent understood modulo two.  To verify it, work in a joint
\(X^B_e,X^C_e\) eigenstate.  If their eigenvalues agree, then \(P_e=+1\)
and both sides are the identity.  If they disagree, then \(P_e=-1\), and
the left side is
\((-1)^{n^a_{\phi(e)}+n^a_s}=Z^a_{\phi(e)}Z^a_s\), exactly the right side.

We now have two temporary-ancilla \(Z\)'s.  The second one is essential:
a finite graph path has two endpoints, so the cluster-state path relation
cannot replace a single \(Z^a_{\phi(e)}\) by a finite \(A\)-string.  For
each \(e\in E_s\), choose a path in the ancilla graph

\[
\gamma_{e,s}:\ \phi(e)\longrightarrow s.
\]

The paper denotes it by \(\langle\phi(e),s\rangle\).  Equation (166) gives

\[
Z^a_{\phi(e)}Z^a_s
\doteq Z^A_{\gamma_{e,s}}
:=\prod_{f\in\gamma_{e,s}}Z^A_f.
\tag{167f}
\]

Substituting Eq. (167f) into Eq. (167d) removes every measured \(a\) qubit
and yields Eq. (167).  Thus the path for the term associated with \(e\) is
specifically the ancilla-graph path from the SWAP controller \(\phi(e)\)
to the vertex carrying the label of the whole check \(s\).  If
\(\phi(e)=s\), this is the empty path and its \(Z^A\) product is the
identity.

The \(Z\)-type checks have the parallel form

\[
\begin{aligned}
S^{Z,\mathrm{gauged}}_{B,[p]}
 &=Z^B_{\partial_2[p]}
 \prod_{e\in\partial_2[p]}
 \left(Z^A_{\langle\phi(e),v(p)\rangle}\right)^{n^B_e+n^C_e},\\
S^{Z,\mathrm{gauged}}_{C,[p]}
 &=Z^C_{\partial_2[p]}
 \prod_{e\in\partial_2[p]}
 \left(Z^A_{\langle\phi(e),v(p)\rangle}\right)^{n^B_e+n^C_e},
\end{aligned}
\tag{168}
\]

where \(n^B_e=(I-Z^B_e)/2\), and likewise for \(C\).  Let us unpack the
choice of \(v(p)\) without using geometrical language.  A basis element
\([p]\in D_2\) labels one \(Z\)-check, and

\[
\partial_2[p]=\sum_{e\text{ acted on by }p}[e]
\]

lists the physical qubits on which that check acts.  For each such qubit,
\(\partial_1[e]\in D_0\) lists the \(X\)-check labels that also act on
\(e\).  The paper's ``closure'' of \(p\) is therefore the set

\[
\operatorname{cl}(p)
:=
\bigcup_{e\in\operatorname{supp}(\partial_2[p])}
\operatorname{supp}(\partial_1[e]).
\tag{168a}
\]

In words,

\[
\boxed{
\operatorname{cl}(p)
=
\{\text{\(X\)-check labels touching at least one qubit of the
\(Z\)-check \(p\)}\}.
}
\tag{168b}
\]

To choose \(v(p)\), pick one physical qubit \(e\) on which the \(Z\)-check
\(p\) acts, then pick an \(X\)-check \(v\) that also acts on that qubit.
Call the selected \(X\)-check label \(v(p)\).  Because the ancilla-graph
vertices are indexed by \(X\)-check labels, \(v(p)\) also names an ancilla
vertex.  In the Tanner-incidence structure, this is simply the two-step
choice

\[
p\ \text{(a \(Z\)-check)}
\longrightarrow e\ \text{(a data qubit)}
\longrightarrow v(p)\ \text{(an \(X\)-check/ancilla vertex)}.
\tag{168c}
\]

One must not replace the union in Eq. (168a) by
\(\operatorname{supp}(\partial_1\partial_2[p])\).  The chain-complex
identity \(\partial_1\partial_2=0\) makes that support empty: the incident
\(X\)-check labels cancel modulo two after all qubits of the \(Z\)-check
are summed.  The closure instead collects the supports of the individual
\(\partial_1[e]\)'s *before* those cancellations.  Geometrically, for a
square toric-code plaquette, \(\partial_2[p]\) gives its four boundary
edges, \(\operatorname{cl}(p)\) gives its four corner vertices, and
\(v(p)\) is one chosen corner.  No literal face or corner is required in a
general qLDPC code.

The notation in Eqs. (167)--(168) deserves one last reading.  For example,
if \(m^B_e+m^C_e=0\), the associated path contributes nothing.  If it is
one, multiply \(Z^A\) over every graph edge on the chosen path from
\(\phi(e)\) to \(v\) for an \(X\)-check, or to \(v(p)\) for a \(Z\)-check.
These are finite products of *controlled-Pauli*
factors; as whole operators they need not be bare Pauli products.  In a
fixed matter eigenvalue sector each factor reduces to either \(I\) or an
ordinary \(Z^A\) string.  Together with Eq. (164), they are the stabilizers
of the gauged model written in the paper's occupation-number convention.

### Where the qLDPC difficulty has moved

The symmetry calculation was easy; code locality is the nontrivial part.
Equations (167) and (168) contain graph paths.  A long path makes one
stabilizer high weight, while too many selected paths through one graph edge
make that qubit participate in too many checks.  Either outcome violates
the qLDPC conditions.

The paper therefore proposes designing the graph so that the needed pairs
are near each other: include short connections between \(\phi(e)\) and
\(v\) whenever \(e\in d_0\boldsymbol v\), and between \(\phi(e)\) and
\(v(p)\) whenever \(e\in\partial_2[p]\).  A bounded-degree implementation
of those connections is the remaining graph-design problem.  It must also
retain the single connected component required by Eq. (139).  This is a
good point at which to separate the two achievements of the example:

1. Eqs. (154)--(159) prove that the graph ancilla gauges transversal
   \(\mathsf{SWAP}\).
2. Eqs. (164)--(168) show what the resulting constraints are and expose the
   precise locality conditions a qLDPC graph must satisfy.

The construction is consequently a template, not yet a universal qLDPC
theorem.  It tells us exactly which sparse incidence data and short graph
paths would turn the elegant gauging idea into a family of good
non-Abelian codes.

## Section IV.A: non-Abelian fractons from gauging transversal \(\mathsf{CZ}\) gates

The SWAP example established the graph-gauging mechanism in its most
universal form.  This example is more directly connected to quantum
computation: it gauges a transversal \(\mathsf{CZ}\), the logical Clifford
operator whose measurement will later prepare a magic state.  It is also the
paper's first fully spatial qLDPC example.

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
\tag{165}
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
\tag{166}
\]

The middle line is the surprise.  A horizontal \(xy\) *plaquette* carries a
qubit, whereas a vertical \(z\) *edge* carries a qubit.  There are no qubits
on horizontal edges.  This is why the ALP stabilizers do not look like the
usual cubic-lattice toric-code stabilizers.

The following deliberately flattens the geometry into two readable 2D
schematics.  Blue squares stand for horizontal-plaquette qubits and orange
circles for vertical-edge qubits; they are not physical projections of every
part of the 3D lattice.

\begin{center}
\begin{tikzpicture}[scale=0.9, every node/.style={font=\small}]
  \node[font=\bfseries] at (1.8,3.45) {(a) Cube \(Z\) check};
  \draw[gray,thick] (0.2,0.6)--(2.2,0.6)--(2.2,2.5)--(0.2,2.5)--cycle;
  \draw[gray,thick] (0.9,1.25)--(2.9,1.25)--(2.9,3.15)--(0.9,3.15)--cycle;
  \foreach \x/\y/\X/\Y in {0.2/0.6/0.9/1.25,2.2/0.6/2.9/1.25,2.2/2.5/2.9/3.15,0.2/2.5/0.9/3.15}
    \draw[gray,thick] (\x,\y)--(\X,\Y);
  \filldraw[fill=blue!60] (1.2,1.55) rectangle +(0.28,0.28);
  \filldraw[fill=blue!60] (1.9,2.25) rectangle +(0.28,0.28);
  \foreach \x/\y in {0.55/0.93,2.55/0.93,2.55/2.83,0.55/2.83}
    \filldraw[fill=orange!85] (\x,\y) circle (0.11);
  \node[align=center,text width=3.6cm,font=\footnotesize] at (1.55,-0.12) {Six qubits: two \(xy\)-face qubits and four vertical-edge qubits.};

  \begin{scope}[xshift=5.0cm]
    \node[font=\bfseries] at (1.8,3.45) {(b) Vertex \(X\) check};
    \draw[gray!55] (0,0.65) grid[step=1.1] (3.3,2.85);
    \foreach \x/\y in {0.55/1.2,2.75/1.2,0.55/2.3,2.75/2.3}
      \filldraw[fill=blue!60] (\x,\y) rectangle +(0.30,0.30);
    \filldraw[fill=green!55] (1.65,1.75) circle (0.15) node[white] {\(v\)};
    \filldraw[fill=orange!85] (1.65,0.82) circle (0.11);
    \filldraw[fill=orange!85] (1.65,2.68) circle (0.11);
    \node[align=center,text width=3.6cm,font=\footnotesize] at (1.65,-0.12) {Six qubits: four adjacent \(xy\)-plaquette qubits and two vertical-edge qubits.};
  \end{scope}
\end{tikzpicture}
\end{center}

In the paper's compact notation, the two stabilizer families are therefore

\[
A_v=X_{d_0\boldsymbol v},\qquad B_c=Z_{\partial_2[c]}.
\tag{167}
\]

The chain-complex condition \(\partial_1\partial_2=0\), or dually
\(d_1d_0=0\), guarantees that each \(A_v\) and \(B_c\) overlap on an even
number of qubits and hence commute.  This is the only fact needed for the
gauging construction; one does not need the detailed fracton mobility theory
yet.  The name “lineon-planeon” signals that some excitations in this model
have restricted motion, but the present section uses the model principally
as a concrete CSS qLDPC code.

For an \(L_x\times L_y\times L_z\) periodic lattice, the paper reports
\(2(L_x+L_y-1)\) logical qubits and distance scaling as
\(\min(L_x,L_y,L_z)\).  This is a useful reminder that it is a subsystem-like
3D code rather than a conventional topological code with a constant number
of logical qubits.

### The transversal \(\mathsf{CZ}\) symmetry between two copies

Make two identical ALP blocks, named \(B\) and \(C\).  The paper specifies a
periodic, local pairing \(\mathcal P\) of a \(B\)-qubit with a \(C\)-qubit in
each cubic unit cell.  Its drawing uses black line segments between the
paired qubits.  Write the resulting gate without committing to one
misleading 2D projection as

\[
U_{\mathsf{CZ}}=
\prod_{(e,e')\in\mathcal P}\mathsf{CZ}_{B_e,C_{e'}}.
\tag{168}
\]

“Transversal” means that each physical qubit occurs in only a bounded,
fixed number of these elementary gates (in this pattern, one).  The paired
qubits need not be drawn directly on top of one another: the pairing is a
local matching determined by the cubic unit cell.  This is a point at which
the paper's 3D perspective matters more than an attempted planar picture.

The elementary conjugation rules are

\[
\mathsf{CZ}_{B,C}X_B\mathsf{CZ}_{B,C}=X_BZ_C,
\qquad
\mathsf{CZ}_{B,C}X_C\mathsf{CZ}_{B,C}=Z_BX_C,
\tag{169}
\]

while both \(Z_B\) and \(Z_C\) are unchanged.  The chosen pairing makes the
extra \(Z\) factors fit the ALP check structure.  This sentence hides an
important qualification: a *single physical* \(X_e\), \(Z_e\), or
\(\mathsf{CZ}_{B_e,C_{e'}}\) is generally **not** a symmetry of the code.
For example, a lone \(Z_e\) anticommutes with the \(X\)-checks incident on
that qubit and creates syndrome defects.  Equation (169) is only a local
operator identity; it does not say that its individual factors preserve
check eigenvalues.

The simple lattice-level picture is this.  Pick **one whole** \(B\)-block
\(X\)-check \(A_v^B\), not one physical \(X_e\).  Every \(\mathsf{CZ}\)
touching that six-qubit check contributes a \(Z\) on a qubit of the
\(C\) block.  When all those contributions are multiplied, the special
pairing drawn in the paper makes them close up into one or a few complete
\(C\)-block \(Z\)-checks.  Symbolically,

\[
\begin{aligned}
U_{\mathsf{CZ}}A_v^BU_{\mathsf{CZ}}^\dagger
 &=A_v^B\prod_{c\in R_C(v)}B_c^C,\\
U_{\mathsf{CZ}}A_v^CU_{\mathsf{CZ}}^\dagger
 &=\left(\prod_{c\in R_B(v)}B_c^B\right)A_v^C.
\end{aligned}
\tag{170}
\]

Here \(R_C(v)\) and \(R_B(v)\) are small, local sets of cubes determined
by the \(\mathsf{CZ}\)-line pattern.  The important point is not their exact
shape yet; it is that the added \(Z\)'s form **complete stabilizers**, not
an open string with endpoints.  This is the cancellation you had in mind:
when the gates are applied throughout the lattice, intermediate \(Z\)'s
cancel modulo two and only closed \(Z\)-check products remain.

Thus it is fair to say, informally, “an \(X\)-check on one copy acquires
\(Z\)-checks on the other copy.”  It is not quite right to say “all the
\(X\)-stabilizers and all the \(Z\)-stabilizers are added.”  The statement is
local and check-by-check: a particular \(A_v^B\) acquires a particular
nearby product \(\prod_{c\in R_C(v)}B_c^C\).  On the codespace every factor
in Eq. (170) has eigenvalue \(+1\), so the check value remains \(+1\).
The generator is merely replaced by another generator of the same stabilizer
group.

The \(Z\)-checks themselves do not acquire anything, because
\(\mathsf{CZ}\) is diagonal:

\[
U_{\mathsf{CZ}}B^B_cU_{\mathsf{CZ}}^\dagger=B^B_c,
\qquad
U_{\mathsf{CZ}}B^C_cU_{\mathsf{CZ}}^\dagger=B^C_c.
\tag{171}
\]

So the correct conclusion is not “single \(X\)'s and \(Z\)'s commute with
the stabilizers.”  They generally do not.  Rather, the *whole* transversal
\(\mathsf{CZ}\) maps every stabilizer to a product of stabilizers, and so
preserves the codespace while acting as a logical Clifford operation.  If
you later want the compact binary test for whether a proposed pairing has
this property, it is exactly the condition that its added \(Z\) support be
in \(\operatorname{im}\partial_2\) for every \(X\)-check support in
\(\operatorname{im}d_0\).

### The cubic ancilla graph and the controlled-\(\mathsf{CZ}\) enrichment

The graph method now supplies a third set of qubits.  Put temporary qubits
\(a_v\) on every cubic-lattice vertex and gauge-field qubits \(A_f\) on every
cubic-lattice edge \(f=\langle v,w\rangle\).  After making the graph cluster
state (the paper applies a Hadamard to the \(A\) sublattice), its convenient
stabilizer generators are

\[
K^a_v=X^a_v\prod_{f\ni v}X^A_f,
\qquad
K^A_f=Z^A_fZ^a_vZ^a_w.
\tag{172}
\]

Because the cubic graph is connected, the temporary vertices possess exactly
one global \(X\) symmetry,

\[
X^a_{\rm all}=\prod_vX^a_v.
\tag{173}
\]

The enrichment must tie this single symmetry to Eq. (168).  It uses
\(\mathsf{CCZ}\), the three-qubit controlled-controlled-Z gate.  Its action
is diagonal in the computational basis:

\[
\mathsf{CCZ}_{a,B,C}|r,b,c\rangle
=(-1)^{rbc}|r,b,c\rangle.
\tag{174}
\]

Thus when the temporary control is \(|0\rangle_a\), it does nothing; when
the control is \(|1\rangle_a\), it applies \(\mathsf{CZ}\) to the selected
\(B,C\) pair.  The essential local motif is

\begin{center}
\begin{tikzpicture}[every node/.style={font=\small}, scale=1.0]
  \node[font=\bfseries] at (2.6,3.15) {A 2D schematic of the local 3D enrichment rule};
  \filldraw[fill=purple!60] (2.6,2.35) circle (0.24) node[white] {\(a_v\)};
  \filldraw[fill=blue!60] (1.15,0.75) circle (0.24) node[white] {\(B_e\)};
  \filldraw[fill=orange!85] (4.05,0.75) circle (0.24) node[white] {\(C_{e'}\)};
  \draw[green!55!black,very thick] (2.48,2.14)--(1.30,0.96);
  \draw[green!55!black,very thick] (2.72,2.14)--(3.90,0.96);
  \node[draw=green!55!black,fill=green!10,rounded corners,inner sep=5pt] at (2.6,1.57)
    {\(\mathsf{CCZ}_{a_v,B_e,C_{e'}}\)};
  \node[align=center] at (2.6,0.0) {The actual cubic construction assigns a bounded nearby collection of \\
  \(B\)-\(C\) pairs to each vertex \(v\); the schematic shows one such pair.};
\end{tikzpicture}
\end{center}

The paper denotes this local assignment by \(\phi^{\mathsf T}(v)\).  In this
example \(\phi^{\mathsf T}(v)\) is a set of **pairs** \((e,e')\), not merely
a set of single qubits as in the SWAP example.  In a basis-independent form,
the enrichment circuit is

\[
\Omega=
\prod_v\ \prod_{(e,e')\in\phi^{\mathsf T}(v)}
\mathsf{CCZ}_{a_v,B_e,C_{e'}}.
\tag{175}
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
\tag{176}
\]

It follows just by checking \(a=0,1\): flipping the control interchanges
the “apply \(\mathsf{CZ}\)” and “do nothing” branches.  Multiply Eq. (176)
over all temporary vertices and their assigned pairs.  The odd-assignment
condition then gives

\[
X^a_{\rm all}\Omega X^a_{\rm all}\Omega^\dagger
=U_{\mathsf{CZ}}.
\tag{177}
\]

This is the same group-commutator test as Eq. (155), with controlled swaps
replaced by controlled \(\mathsf{CZ}\) gates.  It is the one equation that
shows the cubic ancilla is gauging the desired logical symmetry rather than
merely adding extra qubits.

### What survives measurement, and why the final formulas look difficult

Measure every temporary \(a_v\) qubit in the \(X\) basis.  For the moment,
pretend every outcome is \(+1\); the next paper subsection explains how a
decoder and feedforward correct the actual random signs.  From Eq. (172),
the temporary-vertex stabilizer becomes the surviving gauge constraint

\[
\widetilde K^A_v=
\left(\prod_{f\ni v}X^A_f\right)
\left(\prod_{(e,e')\in\phi^{\mathsf T}(v)}
\mathsf{CZ}_{B_e,C_{e'}}\right).
\tag{178}
\]

Read this slowly.  The first factor is an ordinary \(X\)-type gauge
transformation on the six edges incident to a cubic vertex.  The second
factor simultaneously performs the local piece of the original
\(B\)-\(C\) symmetry.  This is the concrete form of the slogan “a gauge
transformation carries the old symmetry.”

The matter checks become dressed as well.  The useful one-qubit identity is

\[
\mathsf{CCZ}_{a,B,C}X_B\mathsf{CCZ}_{a,B,C}
=X_B\mathsf{CZ}_{a,C},
\tag{179}
\]

and the analogous equation holds with \(B\) and \(C\) exchanged.  Therefore
each \(X\)-type ALP check picks up controlled-Z factors involving temporary
ancillas.  Before measurement, those factors can be traded, using products
of the edge relations \(K^A_f\), for operators on paths of surviving
\(A\)-edge qubits - precisely the path-replacement mechanism explained in
Eqs. (161)--(162).  The \(Z\)-type checks are simpler at the first step
because \(\mathsf{CCZ}\) is diagonal, but the complete final commuting
projectors still include the corresponding gauge dressing.

This explains why the paper presents the final stabilizers mainly as 3D
figures rather than as a short one-line formula.  Three distinct incidence
structures must be superimposed: the six-qubit ALP checks, the cubic ancilla
graph, and the local \(B\)-\(C\) pair assignment.  The final operators are
local, but “local” now means local in that combined three-layer incidence
structure, not local in a single planar projection.

There is a second subtlety.  The raw dressed generators can commute only
**up to** the gauged \(U_{\mathsf{CZ}}\) symmetry.  To define a Hamiltonian
with mutually commuting projectors, the paper symmetrizes them with respect
to that \(\mathbb Z_2\) action.  This is not a failure of the construction;
it is the non-Abelian feature in algebraic form.  A bare matter-check label
can be changed by the gauge transformation, so the gauge-invariant term must
include both members of its symmetry orbit.

### Why this example deserves priority for the magic-state goal

The SWAP example taught the general graph procedure.  This ALP example adds
the specific ingredient needed later for computation:

\[
\text{temporary control}\quad+\quad\mathsf{CCZ}
\quad\Longrightarrow\quad
\text{gauged transversal logical }\mathsf{CZ}.
\tag{180}
\]

The later ungauging protocol reverses the ancilla construction and measures
the gauge qubits.  Equation (177) then reappears as a projector onto an
eigenvalue of the logical \(\mathsf{CZ}\) acting on the original \(B,C\)
blocks.  On appropriate logical input states, that Clifford measurement
prepares a non-stabilizer state.  Thus the CCZ gates used here are not being
claimed as directly applied logical non-Clifford gates; rather, they are the
local measurement gadget from which a non-Clifford *resource state* emerges
after gauging and ungauging.

For the next reading step, retain the following four statements:

1. The ALP code has qubits on \(xy\) plaquettes and \(z\) edges, giving
   six-qubit cube and vertex checks.
2. Two copies possess a local transversal \(\mathsf{CZ}\) matching.
3. A cubic graph cluster state plus local \(\mathsf{CCZ}\) enrichment
   satisfies the global commutator identity (177).
4. Measuring the temporary ancillas turns this into a non-Abelian gauge
constraint (178); ungauging later converts the same construction into a
   logical \(\mathsf{CZ}\) measurement.

## Section III.E: measurement preparation of non-Abelian qLDPC codes

Up to now, the gauging discussion has used an idealized instruction:
“project every temporary ancilla \(a_v\) onto \(|+\rangle\).”  A physical
\(X\)-basis measurement cannot promise that outcome.  It returns a random
number

\[
x_v\in\{+1,-1\},
\qquad
X^a_v\longmapsto x_v.
\tag{181}
\]

This section explains why that randomness does not turn gauging into a
postselected protocol.  Assuming that the Abelian code on the ancilla
complex has a decoder, the random signs can be removed deterministically by
a Pauli correction on the surviving \(A\) qubits.  The word *deterministic*
means that every possible measurement record is accepted and corrected; it
does not mean that individual measurement outcomes cease to be random.

### First ignore the matter codes: measuring a graph cluster state

It is useful to strip the problem to its simplest form.  Before the
measurement, the temporary-vertex graph-cluster stabilizer is

\[
K^a_v=X^a_vX^A_{d^a_0\boldsymbol v}.
\tag{182}
\]

For an ordinary graph, \(X^A_{d^a_0\boldsymbol v}\) is the product of \(X\)
on all \(A\)-edge qubits incident to vertex \(v\).  Since \(K^a_v=+1\) on
the cluster state, measuring \(X^a_v=x_v\) leaves the surviving \(A\) qubits
with the signed check

\[
x_vX^A_{d^a_0\boldsymbol v}=+1.
\tag{183}
\]

The usual \(Z\)-type ancilla checks, labelled schematically by
\(Z^A_{\partial_2[p]}\), are unaffected.  Thus the only difference between
the desired Abelian ancilla code and the actually prepared one is the list
of signs \(\{x_v\}\) in Eq. (183).

Turn these signs into a binary syndrome vector,

\[
s=\sum_v s_v[v]\in A_0,
\qquad
s_v=\begin{cases}
0,&x_v=+1,\\
1,&x_v=-1.
\end{cases}
\tag{184}
\]

**Why are there an even number of \(-1\) outcomes in the clean target
sector?**  Multiply every premeasurement vertex stabilizer in Eq. (182).
Each \(A\)-edge occurs at the two ends of that edge, so its two factors
cancel:

\[
\prod_vK^a_v
=\left(\prod_vX^a_v\right)
 \left(\prod_{f\in A_1}(X^A_f)^2\right)
=\prod_vX^a_v
=X^a_{\rm all}.
\tag{185}
\]

All the \(K^a_v\)'s have eigenvalue \(+1\), hence the cluster state has
\(X^a_{\rm all}=+1\).  The individual \(X^a_v\) measurements commute, so
their outcomes must obey

\[
\prod_vx_v=+1.
\tag{186}
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
\tag{187}
\]

The decoder is the classical algorithm that finds a suitably likely such
chain \(r\) from the syndrome.  It is not necessary for this discussion to
know how that algorithm works internally.

The corresponding quantum correction is the Pauli product

\[
Z^A_r:=\prod_{f\in A_1}(Z^A_f)^{r(f)}.
\tag{188}
\]

Why does it fix the signs?  A factor \(Z^A_f\) anticommutes with an
\(X\)-check precisely when edge \(f\) occurs in that check.  Therefore

\[
Z^A_rX^A_{d^a_0\boldsymbol v}Z^A_r
=(-1)^{\boldsymbol v(\partial^a_1r)}X^A_{d^a_0\boldsymbol v}
=(-1)^{s_v}X^A_{d^a_0\boldsymbol v}.
\tag{189}
\]

Because \(x_v=(-1)^{s_v}\), conjugating Eq. (183) by \(Z^A_r\) changes it
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
\tag{190}
\]

The decoder can therefore choose the shortest possible correction chain,
\(r=[f]\).  Its quantum correction contains just **one** single-qubit
Pauli:

\[
Z^A_r=Z^A_f.
\tag{191}
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
\tag{192}
\]

Edge \(f\) occurs once in each of the two vertex checks.  Hence

\[
Z^A_fX^A_{d^a_0\boldsymbol v}Z^A_f
=-X^A_{d^a_0\boldsymbol v},
\qquad
Z^A_fX^A_{d^a_0\boldsymbol w}Z^A_f
=-X^A_{d^a_0\boldsymbol w}.
\tag{193}
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
\tag{194}
\]

The factor \(\mathcal U_v\) is the local piece of the old transversal
symmetry.  In the SWAP example it is a product of
\(\mathsf{SWAP}_{B_e,C_e}\)'s; in the ALP \(\mathsf{CZ}\) example it is a
product of \(\mathsf{CZ}_{B_e,C_{e'}}\)'s.  Crucially, the random outcome
\(x_v\) occurs in exactly the same place as it did in Eq. (183): it merely
multiplies the \(X^A\) factor by a sign.

The correction \(Z^A_r\) has two equally important properties:

1. By Eq. (189), it flips precisely the unwanted signs in
   \(\mathcal G_v[x_v]\).
2. It commutes with \(\mathcal U_v\), because \(Z^A_r\) acts on the
   surviving gauge qubits whereas \(\mathcal U_v\) acts on \(B,C\).  It also
   commutes with the other \(Z\)-type and matter constraints.

Hence the same correction selected by the *Abelian* ancilla decoder turns

\[
\mathcal G_v[x_v]\quad\longmapsto\quad
\mathcal G_v[+1]
\tag{195}
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
\tag{196}
\]

After this correction, we may use the same clean \(+1\)-outcome gauged
state in subsequent reasoning.  In particular, the next section can safely
ungauge it and interpret the overall protocol as a logical Clifford
measurement rather than as a postselected experiment.

## Section IV: logical Clifford measurement from gauging and ungauging

We now reach the computational claim of the paper.  Gauging was introduced
as a way to make a transversal symmetry local and dynamical.  **Ungauging**
reverses that enlargement: undo the ancilla cluster entangler and measure
away the surviving \(A\) gauge qubits.  The surprising result is that the
combined operation is a measurement of the logical symmetry that was
gauged.

The paper writes the derivation for a transversal \(\mathsf{CZ}\) in the
homological construction, where there can be several cocycle symmetries.
The conclusion is broader.  In the connected-graph construction there is
only one nontrivial cocycle, so the same derivation reduces to a measurement
of its one chosen transversal Clifford gate.

### The claim in one line

Let \(U_{\boldsymbol\mu}\) be the transversal logical Clifford symmetry
associated with an ancilla 0-cocycle
\(\boldsymbol\mu\in\ker d^a_0\).  Gauging and then ungauging applies the
projector

\[
P_{x_{\boldsymbol\mu}}
=\frac{I+x_{\boldsymbol\mu}U_{\boldsymbol\mu}}{2}
\tag{191}
\]

to the two input code blocks.  Here
\(x_{\boldsymbol\mu}=\pm1\) is obtained from the temporary-ancilla
measurement outcomes.  Equation (191) is precisely the projective
measurement of the Hermitian involution \(U_{\boldsymbol\mu}\): it selects
its \(+1\) or \(-1\) eigenspace.

For the connected graph used in the SWAP and ALP examples,
\(\ker d^a_0\) has just the uniform cocycle \(\boldsymbol\mu_{\rm all}\).
The formula is then simply

\[
\frac{I+x\,U}{2}.
\tag{192}
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
\tag{193}
\]

The gauging protocol applies the enrichment circuit \(\Omega\), measures
every temporary qubit \(a_v\) in the \(X\) basis, and leaves the \(A\)
qubits in place.  The ungauging protocol does the reverse ancilla operation:
apply \(C_A^\dagger\), then measure every \(A\) qubit in the \(Z\) basis.
The full conceptual circuit is

\begin{center}
\begin{tikzpicture}[node distance=0.50cm and 0.43cm, every node/.style={font=\scriptsize}, >=Latex]
  \node[draw,rounded corners,fill=blue!10,align=center,minimum width=1.65cm,minimum height=.72cm] (in)
    {input code state\\\(|\Psi\rangle_{BC}\)};
  \node[draw,rounded corners,fill=purple!10,align=center,right=of in,minimum width=1.65cm,minimum height=.72cm] (cl)
    {prepare cluster\\\(C_A\)};
  \node[draw,rounded corners,fill=green!10,align=center,right=of cl,minimum width=1.65cm,minimum height=.72cm] (en)
    {enrich\\\(\Omega\)};
  \node[draw,rounded corners,fill=orange!12,align=center,right=of en,minimum width=1.65cm,minimum height=.72cm] (ma)
    {measure \(X_a\)\\and record \(x_v\)};
  \node[draw,rounded corners,fill=purple!10,align=center,right=of ma,minimum width=1.65cm,minimum height=.72cm] (un)
    {ungauge\\\(C_A^\dagger\), measure \(Z_A\)};
  \node[draw,rounded corners,fill=red!10,align=center,right=of un,minimum width=1.65cm,minimum height=.72cm] (out)
    {input blocks left in\\\(P_x|\Psi\rangle_{BC}\)};
  \draw[->,thick] (in)--(cl); \draw[->,thick] (cl)--(en); \draw[->,thick] (en)--(ma);
  \draw[->,thick] (ma)--(un); \draw[->,thick] (un)--(out);
\end{tikzpicture}
\end{center}

We now unpack only the two algebraic moves which make this work.

### Reset: chains and cochains on the ancilla graph

Before using the calculation, it is worth resetting the notation on the
smallest ordinary graph.  Temporarily ignore the word “dual.”  Imagine the
ancilla graph

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

Only after this concrete picture is solid do we restore the formal statement

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

### Step 1: the \(X_a\) measurements create a sum over ancilla cochains

For a record \(x_v=\pm1\), the one-qubit measurement projector is

\[
\Pi_v(x_v)=\frac{I+x_vX^a_v}{2}.
\tag{194}
\]

The cluster relation lets us move this projector through the preparation
circuit.  In the notation used throughout the note,

\[
\Pi_{\boldsymbol x}\,\Omega C_A
\bigl(|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a\bigr)
\ \doteq\ 
C_A\prod_v\frac{I+x_vX^a_vX^A_{d^a_0\boldsymbol v}}{2}
\Omega\bigl(|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a\bigr).
\tag{195}
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
\doteq
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

The sign \(\doteq\) suppresses normalization and already-known Pauli-frame
byproducts.  The crucial feature is the factor
\(X^a_vX^A_{d^a_0\boldsymbol v}\): measuring an \(a\) qubit is tied to an
\(X\) operation on the adjacent \(A\)-gauge qubits.

Expanding the product in Eq. (195) means choosing either the \(I\) term or
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
\tag{196}
\]

There is one important typography point. The definition is

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

The equation itself is just the familiar expansion of a product of
binomials. Define

\[
K_v:=X^a_vX^A_{d^a_0\mathbf v}.
\]

Then Eq. (196) says

\[
\prod_v(I+x_vK_v)
=
\sum_{\boldsymbol\phi\in A^0}
x_{\boldsymbol\phi}\,
X^a_{\boldsymbol\phi}X^A_{d^a_0\boldsymbol\phi}.
\]

Here

\[
X^a_{\boldsymbol\phi}:=\prod_v(X^a_v)^{\boldsymbol\phi(v)}.
\]

So \(\boldsymbol\phi\) tells us, vertex by vertex, which term we selected
while expanding each factor:

\[
\begin{array}{c|c}
\boldsymbol\phi(v)&\text{term selected from }I+x_vK_v\\
\hline
0&I\\
1&x_vK_v.
\end{array}
\]

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

The missing factors of \(1/2\) are intentional: Eq. (196) expands the
numerators of the measurement projectors. The full projector has an overall
factor \(2^{-|V_A|}\), which is irrelevant once the state is normalized.

This is not a new physical superposition of measurement records.  It is an
algebraic expansion of the fixed-record projector.  It is useful because the
co-boundary \(d^a_0\boldsymbol\phi\) will be tested by the later \(Z_A\)
measurements.

### Step 2: measuring \(Z_A\) keeps only cocycles

Ungauging first applies \(C_A^\dagger\), which turns the \(A\) subsystem
back into qubits initially prepared in \(|0\rangle_A\).  Let the subsequent
\(Z_A\) measurement record be a binary 1-cochain \(\boldsymbol z\):
\(z(f)=1\) means the outcome on edge \(f\) is \(-1\).

Here the cleanest way to read the notation is: choose the natural bases of
vertices and edges, then represent each cochain by its list of values on
those basis objects.  Thus \(\boldsymbol\phi\in A^0\) is formally a linear
function on vertex chains, but we draw it as vertex bits; likewise,
\(\boldsymbol z\in A^1\) is formally a linear function on edge chains, but
we draw it as edge bits.  The important point is that \(\boldsymbol z\) and
\(d^a_0\boldsymbol\phi\) belong to the same space, \(A^1\).  Equation (197)
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
\tag{197}
\]

The subscript \(0\) says only: choose one cochain whose coboundary matches
the actual record.  It need not be unique.  This is an outcome constraint,
not a postselection condition: the actual record automatically has this form
because it came from the state in Eq. (196).

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
\tag{198}
\]

Thus every surviving label has the form

\[
\boldsymbol\phi=\boldsymbol\phi_0+\boldsymbol\mu,
\qquad
\boldsymbol\mu\in\ker d^a_0.
\tag{199}
\]

This is the mathematical heart of ungauging.  The final \(Z_A\) measurement
eliminates all non-symmetry components of the temporary-ancilla expansion;
only the 0-cocycles, i.e. the ancilla symmetries, remain.

The offset \(\boldsymbol\phi_0\) is an ordinary measurement byproduct.
Applying or tracking \(X^a_{\boldsymbol\phi_0}\) removes it.  After this
feedforward, the part that acts nontrivially on the input blocks is

\[
\sum_{\boldsymbol\mu\in\ker d^a_0}
x_{\boldsymbol\mu}X^a_{\boldsymbol\mu}\,\Omega.
\tag{200}
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
\tag{201}
\]

The remaining \(a\) qubits are in \(|+\rangle_a\), so
\(X^a_{\boldsymbol\mu}\) acts as \(+1\) and can be discarded.  Choose a
basis \(\{\boldsymbol\mu_i\}\) of the cocycle space.  The output on the
input codes is, up to normalization,

\[
|\Psi\rangle_{BC}
\longmapsto
\prod_i\frac{I+x_{\boldsymbol\mu_i}U_{\boldsymbol\mu_i}}{2}
|\Psi\rangle_{BC}.
\tag{202}
\]

#### What \(\boldsymbol\mu\in\ker d^a_0\) means here

The expression does not mean “the kernel of \(\boldsymbol\mu\).”  Rather,
\(\boldsymbol\mu\) is one 0-cochain belonging to the kernel of the
coboundary map:

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
\(\boldsymbol\mu_{\rm all}\).  Thus, after normalization, this is simply

\[
\frac{I+x_{\rm all}U_{\rm all}}{2},
\qquad
x_{\rm all}=x_{\boldsymbol\mu_{\rm all}}=\prod_vx_v.
\]

Although every temporary qubit was measured separately, only this global
parity of their outcomes remains after ungauging.  It is exactly the outcome
of measuring the logical symmetry \(U_{\rm all}\).

This is Eq. (191), now derived.  In the homological construction, each
independent cocycle can measure a related, potentially addressable logical
\(\mathsf{CZ}\).  In the connected-graph construction, there is one cocycle
and Eq. (202) is one logical-gate measurement.

### Final summary: the full symbolic procedure

Now that Steps 1--3 have each been derived, we can summarize the complete
physical protocol in one equation.  The labels “Step 1” and “Step 2” below
refer to parts of the derivation, not to extra physical operations.

Let

\[
|\Phi_0\rangle=|\Psi\rangle_{BC}|0\rangle_A|+\rangle_a,
\qquad
P^A_{\boldsymbol z}
=\prod_{e\in E_A}\frac{I+(-1)^{z(e)}Z_{A_e}}{2},
\]

where \(P^A_{\boldsymbol z}\) is the projector for the final, observed
\(Z_A\)-measurement record.  Choose one \(\boldsymbol\phi_0\) satisfying
\(d^a_0\boldsymbol\phi_0=\boldsymbol z\).  Then

\[
\begin{aligned}
|\Phi_0\rangle
&\xrightarrow{\;C_A,\;\Omega,\;\Pi_{\boldsymbol x}\;}
\Pi_{\boldsymbol x}\Omega C_A|\Phi_0\rangle
\\[2pt]
&\doteq
C_A\,2^{-|V_A|}
\sum_{\boldsymbol\phi\in A^0}
x_{\boldsymbol\phi}\,
X^a_{\boldsymbol\phi}X^A_{d^a_0\boldsymbol\phi}\,
\Omega|\Phi_0\rangle
&&\text{(Step 1)}
\\[2pt]
&\xrightarrow{\;C_A^\dagger,\;P^A_{\boldsymbol z}\;}
\sum_{\boldsymbol\phi:\,d^a_0\boldsymbol\phi=\boldsymbol z}
x_{\boldsymbol\phi}\,X^a_{\boldsymbol\phi}\,
\Omega|\Phi_0\rangle
&&\text{(Step 2)}
\\[2pt]
&=
x_{\boldsymbol\phi_0}X^a_{\boldsymbol\phi_0}
\sum_{\boldsymbol\mu\in\ker d^a_0}
x_{\boldsymbol\mu}X^a_{\boldsymbol\mu}\,
\Omega|\Phi_0\rangle
\\[2pt]
&\xrightarrow{\;\text{correct/track }\boldsymbol\phi_0,\;\Omega^\dagger\;}
\left[
\prod_i\frac{I+x_{\boldsymbol\mu_i}U_{\boldsymbol\mu_i}}{2}
\right]|\Psi\rangle_{BC}
\otimes|+\rangle_a.
\end{aligned}
\]

In the last line, \(\{\boldsymbol\mu_i\}\) is a basis of
\(\ker d^a_0\).  The \(A\) qubits have been measured and discarded; the
temporary \(a\) qubits can also be discarded because they are again in
\(|+\rangle_a\).  The only nontrivial action left is the product of logical
projectors on the original \(B,C\) code blocks.

The five lines have a simple interpretation:

1. Prepare the cluster ancilla, enrich it, then measure the temporary
   \(a\)-qubits: this is physical **gauging**.
2. **Step 1** rewrites that fixed record as a sum over vertex cochains
   \(\boldsymbol\phi\).  Each term leaves the edge pattern
   \(d^a_0\boldsymbol\phi\) on the surviving \(A\) qubits.
3. Undo \(C_A\) and measure the \(A\) qubits: this begins **ungauging**.
4. **Step 2** retains only terms with
   \(d^a_0\boldsymbol\phi=\boldsymbol z\), namely
   \(\boldsymbol\phi=\boldsymbol\phi_0+\boldsymbol\mu\) with
   \(\boldsymbol\mu\) a cocycle.
5. **Step 3** removes the correctable local piece
   \(\boldsymbol\phi_0\) and turns each surviving cocycle into the logical
   projector \((I+x_{\boldsymbol\mu_i}U_{\boldsymbol\mu_i})/2\).

Thus gauging creates a local ancilla record of the symmetry, while ungauging
filters away all local information and leaves only the global symmetry
eigenvalue on the original code blocks.

### The magic-state example

Take the connected-graph case and choose the input logical state
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
\tag{203}
\]

The \(|\overline{11}\rangle\) component is absent because it is the unique
computational-basis component with \(\mathsf{CZ}\) eigenvalue \(-1\).  The
state in Eq. (203) is non-stabilizer: a stabilizer state has a
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

### The essential takeaway

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
  Clifford Measurement from Gauging and Ungauging” (from about line 421).
- Context for gauging and \(\mathcal D(D_4)\):
  [arXiv-2209.06202v2/main.tex](../arXiv-2209.06202v2/main.tex), especially
  its discussion of Abelian Kramers-Wannier gauging and \(D_4\) quantum
  doubles.
- Experimental and twisted-\(\mathbb Z_2^3\) presentation:
  [arXiv-2305.03766v2/main.tex](../arXiv-2305.03766v2/main.tex), especially
  “The model,” “Ground State Preparation,” and its table equating
  \(\mathcal D(D_4)\) with \(\mathcal D^\alpha(\mathbb Z_2^3)\).
