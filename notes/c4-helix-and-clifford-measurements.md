# The C4-Helix code and logical Clifford measurement

**Primary source:** *Experimental validation of a compact fault-tolerant
architecture for trapped ions*, [arXiv:2609.03194v1](https://arxiv.org/abs/2609.03194v1),
especially [Appendix A](../arXiv-2609.03194v1/appendix.tex), Table I,
the logical-gate figure `fig:actions`, and “Non-Clifford gates.” The
[main text](../arXiv-2609.03194v1/main.tex) explains the experimental architecture.

**Companion:** [Non-Abelian anyons from gauging logical gates, v2](non-abelian-anyons-from-gauging-v2.md),
especially “From labelled qubits to a CSS chain complex,” the graph-gauging
construction, and “Section VI.A: logical Clifford measurement from gauging
and ungauging.” Its source is arXiv:2602.12228v1, a different manuscript.

**Scope of this first note.** We derive the code's checks, logical operators,
and relevant logical symmetries in the companion's language. We then give
an explicit ideal graph-gauging construction measuring CZ between the two
logical qubits **inside one C4-Helix block**. The involutory physical
representative and five-vertex measurement gadget below are derivations in
this note, rather than circuits claimed to have been experimentally tested
in the manuscript. Their ideal algebra has been checked exactly; their
circuit-level fault tolerance remains to be established.

## What system are we trying to measure?

The C4-Helix code has parameters \([[20,2,6]]\): twenty data qubits carry
two logical qubits, and the smallest undetectable Pauli error with a
nontrivial logical action has weight six. There are eighteen independent
commuting constraints. Their simultaneous +1 eigenspace has dimension
\(2^{20-18}=4\), the dimension of two qubits.

The construction proceeds through

\[
[[5,1,3]]\quad\longrightarrow\quad [[10,2,3]]
\quad\longrightarrow\quad [[20,2,6]].
\]

The first arrow is **symplectic doubling**. It turns a non-CSS Pauli code
into a CSS code: its generators can be chosen to contain only X's or only
Z's. The second arrow encodes pairs of the ten intermediate qubits into
five \([[4,2,2]]\) blocks. Each such block carries two intermediate
qubits in four physical qubits. Consequently we need twenty, rather than
forty, final data qubits.

The ten-qubit intermediate code can be drawn on a twisted torus. That
geometry explains the Helix terminology, but the gauging construction
needs its binary checks and logical action. We will obtain those directly.
The final twenty-qubit device is an input CSS code for gauging; it is not
already a non-Abelian code.

## From the five-qubit Pauli code to the ten-qubit CSS code

### A symplectic support vector has two halves

Start with five qubits labelled \(0,1,2,3,4\), and the Pauli product

\[
G=X_0Z_1Z_2X_3.
\]

This applies X on qubits 0 and 3, Z on qubits 1 and 2, and identity on
qubit 4. Written with one symbol per qubit, it is \(G=XZZXI\): the
last I records the identity on qubit 4. We want to record these instructions
using bits, just as we recorded supports in the companion note.

Recall the companion's notation

\[
\mathsf X(\mathbf a)=\prod_qX_q^{a_q},\qquad
\mathsf Z(b)=\prod_qZ_q^{b_q}.
\]

A bit equal to one selects a qubit; a bit equal to zero leaves it out.
Use one list to select the X's and another to select the Z's. For G these
lists are

\[
\mathbf x=(1,0,0,1,0),\qquad
\mathbf z=(0,1,1,0,0).
\]

Here we use bold symbols for both lists because we are introducing the
usual paired Pauli notation. The Z list performs the same job as the plain
support vector b in \(\mathsf Z(b)\) in the companion.

| Qubit q | X-selection bit \(x_q\) | Z-selection bit \(z_q\) | Operator |
|---|---|---|---|
| 0 | 1 | 0 | X |
| 1 | 0 | 1 | Z |
| 2 | 0 | 1 | Z |
| 3 | 1 | 0 | X |
| 4 | 0 | 0 | I |

Thus \(G=\mathsf X(\mathbf x)\mathsf Z(\mathbf z)\). **The two lists
describe the same five qubits.** No additional qubits have been introduced.

“Two halves” means joining these lists into one row:

\[
(\mathbf x\mid\mathbf z)
=(1,0,0,1,0\mid0,1,1,0,0).
\]

The vertical bar is a separator: the X-selection list is on its left,
and the Z-selection list is on its right. For n qubits, each list has n
bits, so their combined row has 2n bits. The notation
\((\mathbf x\mid\mathbf z)\in\mathbb F_2^{2n}\) says precisely that
this is a list of 2n bits, with addition performed modulo two.

This combined list is called a **symplectic support vector**. Its support
bits record which Pauli factors to use. The word *symplectic* refers to
the commutation rule described below; it is not needed to read the row.

There is one qualification: the bits do not record an operator's overall
phase. For example, G and -G have the same support vector. Also, if both
selection bits at one site are one, their product is \(XZ=-iY\).
Thus the pair \((x_q,z_q)=(1,1)\) records a Y up to a phase. The complete
dictionary for one site is

\[
\begin{array}{c|c}
(x_q,z_q)&\text{Pauli factor, up to phase}\\\hline
(0,0)&I\\
(1,0)&X\\
(0,1)&Z\\
(1,1)&Y
\end{array}.
\]

To reconstruct an exact Pauli operator, supply its phase as well as these
bits. The four generators we introduce next have positive signs and no
sites with both selection bits equal to one.

### A matrix records several Pauli products, one per row

For one Pauli product we need one combined row. For several stabilizer
generators, we stack their rows into a matrix. Appendix A starts from

\[
\begin{aligned}
G_1&=XZZXI,\\
G_2&=IXZZX,\\
G_3&=XIXZZ,\\
G_4&=ZXIXZ.
\end{aligned}
\]

The **support** of a Pauli product is the set of qubits on which it acts
with something other than identity. For example,
\(\operatorname{supp}(X_0Z_1Z_2X_3)=\{0,1,2,3\}\).

A **binary symplectic support matrix** is a table whose rows are the paired
support vectors of a chosen list of Pauli operators. For m operators on n
qubits, it has m rows and 2n columns. Writing it as \(H=(P\mid Q)\),
its entries are defined by

\[
P_{iq}=x_q^{(i)},\qquad Q_{iq}=z_q^{(i)},
\qquad
G_i=\omega_i\prod_{q=0}^{n-1}X_q^{P_{iq}}Z_q^{Q_{iq}},
\]

where \(\omega_i\in\{1,-1,i,-i\}\) supplies the phase omitted from
the matrix. Thus H records both which qubits each operator acts on and
which Pauli factors it uses. Qubit q belongs to the support of row i
exactly when \((P_{iq},Q_{iq})\ne(0,0)\). Hereafter we abbreviate this
name to **support matrix**. When its rows describe stabilizer generators,
it is also called a **symplectic parity-check matrix**.

For the four generators above, the support matrix is

\[
H=(P\mid Q)=
\left(
\begin{array}{ccccc|ccccc}
1&0&0&1&0&0&1&1&0&0\\
0&1&0&0&1&0&0&1&1&0\\
1&0&1&0&0&0&0&0&1&1\\
0&1&0&1&0&1&0&0&0&1
\end{array}
\right).
\]

Read it one row at a time. Row 1 describes \(G_1\), row 2 describes
\(G_2\), and so on. Within a row, the left five bits select X's and
the right five bits select Z's on those same five qubits.

The name P denotes the whole left-hand table of X-selection bits, and
Q denotes the whole right-hand table of Z-selection bits. Separately,
they are

\[
P=\begin{pmatrix}
1&0&0&1&0\\
0&1&0&0&1\\
1&0&1&0&0\\
0&1&0&1&0
\end{pmatrix},\qquad
Q=\begin{pmatrix}
0&1&1&0&0\\
0&0&1&1&0\\
0&0&0&1&1\\
1&0&0&0&1
\end{pmatrix}.
\]

Each has four rows, one for each generator, and five columns, one for each
qubit. They are tables of bits specifying Pauli products. They are not
themselves quantum gates acting on the state. Similarly, H here names a
support matrix; it does not denote a Hadamard gate.

The essential reading rule is: **one row describes one Pauli product;
its two halves select X's and Z's on the same qubits.**

### The commutation rule in this notation

Two Pauli products with support vectors \((\mathbf x\mid\mathbf z)\)
and \((\mathbf x'\mid\mathbf z')\) commute when

\[
\mathbf x\cdot\mathbf z'+\mathbf z\cdot\mathbf x'=0
\qquad\text{over }\mathbb F_2.
\]

This extends the companion note's X-versus-Z overlap rule to mixed Pauli
operators. For the four generators above, the condition can be written as
\(PQ^{\mathsf T}+QP^{\mathsf T}=0\). Their product gives the redundant
fifth generator \(ZZXIX\).

### Doubling changes a mixed row into two pure rows

Label the doubled qubits \(0,\ldots,9\). Its X-check row matrix and
Z-check row matrix are

\[
M_X=(P\ Q),\qquad M_Z=(Q\ P).
\]

They commute because

\[
M_XM_Z^{\mathsf T}=PQ^{\mathsf T}+QP^{\mathsf T}=0.
\]

Each has rank four, so \(k=10-4-4=2\). For example, the first
five-qubit row becomes the two checks

\[
X_0X_3X_6X_7,\qquad Z_1Z_2Z_5Z_8.
\]

The fifth redundant row supplies an additional check of each type. The
five X-check supports XOR to zero, as do the five Z-check supports. This
resembles the product-of-all-stars and product-of-all-plaquettes relations
in the toric-code discussion of the companion note.

Exchanging \(i\leftrightarrow i+5\), for \(i=0,\ldots,4\), exchanges
the two support matrices. This is the **ZX-duality** \(\tau\). It is a
permutation of the physical support labels, rather than an assertion that
\(M_X=M_Z\) in the original ordering.

## The inner C4 code: four qubits carrying two intermediate qubits

### Constraints and logical operators

On one four-qubit block, using local indices \(0,1,2,3\), impose

\[
s_X=X_0X_1X_2X_3,\qquad s_Z=Z_0Z_1Z_2Z_3.
\]

These commute through four overlaps. Their joint +1 eigenspace has
dimension four. In the manuscript's convention its logical Paulis are

\[
\begin{array}{c|cc}
&\text{logical 0}&\text{logical 1}\\\hline
X&X_0X_3&X_2X_3\\
Z&Z_2Z_3&Z_0Z_3
\end{array}.
\]

Within each column, X and Z overlap once and anticommute. Across columns,
the overlaps have even parity, so different logical qubits commute.
Every listed operator commutes with both constraints.

An explicit logical computational basis is

\[
|\ell_0\ell_1\rangle_{C_4}
=\frac{|\ell_1,\ell_0+\ell_1,\ell_0,0\rangle
+|\ell_1+1,\ell_0+\ell_1+1,\ell_0+1,1\rangle}{\sqrt2},
\]

where additions are modulo two. Both bit strings have even parity, so
\(s_Z=+1\). Their equal superposition has \(s_X=+1\). The parities
of bits 2,3 and 0,3 give \(\ell_0\) and \(\ell_1\), respectively.

This little code detects every single-qubit Pauli error, but cannot
correct an arbitrary such error on its own. Its distance is two. The
outer checks supply the additional information needed in C4-Helix.

### Concatenation is a substitution of Pauli representatives

For \(j=0,\ldots,4\), place intermediate qubits \(j,j+5\) in one
inner block \(B_j=\{4j,4j+1,4j+2,4j+3\}\). Here B_j is an inner-block
label, not the companion's name B for an entire matter-code copy.
Make the replacements

\[
\begin{aligned}
X_j&\mapsto X_{4j}X_{4j+3},&
Z_j&\mapsto Z_{4j+2}Z_{4j+3},\\
X_{j+5}&\mapsto X_{4j+2}X_{4j+3},&
Z_{j+5}&\mapsto Z_{4j}Z_{4j+3}.
\end{aligned}
\]

An outer weight-four check therefore lifts to weight eight. For example,

\[
X_0X_3X_6X_7\ \mapsto\
X_0X_3X_{12}X_{15}X_6X_7X_{10}X_{11}.
\]

All lifted checks commute with the ten inner checks, because the
substituted operators are inner logical operators. Their mutual
commutation follows from the outer code. We have ten inner independent
checks and eight outer independent checks, giving eighteen in total.

Multiplying a lifted check by an inner check changes its physical support
without changing the code space. Table I uses this freedom to improve
syndrome extraction. It is that table's representatives, not an
unmodified concatenation, that we use below.

## The exact twenty-qubit checks in the companion's chain language

For a subset R of qubit labels, write \(X_R=\prod_{q\in R}X_q\) and
\(Z_R=\prod_{q\in R}Z_q\). Table I gives the same ten support sets
for both kinds of check:

| Row | Support R | Weight |
|---|---|---|
| 0 | 0,1,2,3 | 4 |
| 1 | 4,5,6,7 | 4 |
| 2 | 8,9,10,11 | 4 |
| 3 | 12,13,14,15 | 4 |
| 4 | 16,17,18,19 | 4 |
| 5 | 0,3,6,7,10,11,12,15 | 8 |
| 6 | 4,7,8,9,14,15,16,19 | 8 |
| 7 | 1,2,8,11,12,13,18,19 | 8 |
| 8 | 2,3,5,6,13,14,16,17 | 8 |
| 9 | 0,1,4,5,9,10,17,18 | 8 |

Let M be the \(10\times20\) binary matrix with these supports as rows.
Then \(MM^{\mathsf T}=0\) and \(\operatorname{rank}M=9\).
Rows 5 through 9 XOR to zero; this is the sole row relation. Thus each
Pauli type has five independent inner checks and four independent outer
checks. Keeping all twenty checks introduces two redundant measurements;
keeping eighteen independent checks defines the same code.

The manuscript says its code is self-dual, \(H_X=H_Z\), using a
convention in which both check matrices have checks in rows. The companion
note instead puts Z-check supports in **columns**. In its convention,

\[
D_2=\mathbb F_2^{10},\quad D_1=\mathbb F_2^{20},\quad
D_0=\mathbb F_2^{10},\qquad
\partial_2=M^{\mathsf T},\quad\partial_1=M.
\]

Consequently

\[
\partial_1\partial_2=MM^{\mathsf T}=0,\qquad
d_0=M^{\mathsf T},\quad d_1=M.
\]

The two logical-support quotients are

\[
H_1=\ker M/\operatorname{im}M^{\mathsf T},\qquad
H^1=\ker M/\operatorname{im}M^{\mathsf T}.
\]

Each has dimension \(20-9-9=2\). These equal expressions say that the
sets of allowed X- and Z-support vectors coincide. They do not fix the
canonical pairing between the chosen logical X's and Z's.

The check relation also gives

\[
H^0=\ker M^{\mathsf T}
=\operatorname{span}\{(0,0,0,0,0,1,1,1,1,1)\}.
\]

It is the uniform pattern on the five **outer** check labels, not on all
ten check labels. This is precisely the distinction between checks and
relations among checks emphasized in the companion. Having such a relation
does not by itself supply a homological enrichment circuit; one still has
to attach the intended logical gate to it. The graph construction below
chooses its own ancilla complex instead.

### Logical operators and the crossed self-duality

Define the two six-qubit sets

\[
R_a=\{2,3,8,11,12,15\},\qquad
R_b=\{0,3,6,7,18,19\}.
\]

Table I chooses

\[
\overline X_0=X_{R_a},\quad\overline X_1=X_{R_b},\qquad
\overline Z_0=Z_{R_b},\quad\overline Z_1=Z_{R_a}.
\]

Both supports belong to \(\ker M\) but not to
\(\operatorname{im}M^{\mathsf T}\). Their intersection is just {3}.
Thus \(\overline X_i\) anticommutes with \(\overline Z_i\), while
\(\overline X_0\) commutes with \(\overline Z_1\) through six
overlaps, and similarly for the other cross pair.

In particular, transversal physical Hadamard exchanges
\(\overline X_0\leftrightarrow\overline Z_1\) and
\(\overline X_1\leftrightarrow\overline Z_0\). Its logical action is
\(\overline H_0\overline H_1\overline{\mathsf{SWAP}}_{0,1}\).
This is why “self-dual” does not mean two separately addressed logical
Hadamards in this choice of logical basis.

### Why the distance is six

It is tempting simply to multiply outer distance three by inner distance
two. Because each inner block contains two outer qubits, that argument
needs an extra check: could an outer logical operator act on fewer than
three paired blocks?

Any final normalizer Pauli first has to commute with all inner checks.
Modulo inner stabilizers, it therefore defines a Pauli on the ten outer
qubits. If that outer Pauli is an outer stabilizer, the original Pauli is a
final stabilizer. If it is logically nontrivial, direct enumeration of the
outer code shows that it touches at least three distinct pairs
\(\{j,j+5\}\). A nontrivial inner logical Pauli costs at least two
physical qubits in each occupied block. Hence the final weight is at
least six; the displayed logical operators attain six.

There is also a short exact CSS audit: \(\ker M\) has 2048 elements,
the stabilizer-support space has 512, and the minimum weight in their
difference is six. This establishes both X and Z distances. For a CSS code,
a nontrivial mixed logical Pauli has a nontrivial X or Z component, whose
support is contained in its total support, so it cannot have lower weight.

## Which Clifford symmetry should we measure?

### Inside one block versus between two complete blocks

The manuscript's native intra-block gates include logical SWAP,
\(\overline H_0\overline H_1\overline{\mathsf{SWAP}}\),
a CNOT/SWAP combination, and logical CZ, up to residual Paulis.
They are automorphisms implemented through single-qubit gates and physical
permutations. An additional flagged phase-gate circuit supplies
\(\overline S_0\overline S_1\), completing Clifford control.

For the companion's projector \((I+xU)/2\), choose a Hermitian
involution. CZ, SWAP, and Hadamard are candidates; an S gate does not have
order two. Also, a circuit with the correct binary symplectic action may
have the wrong signed logical operator for the measurement.

There are two particularly direct CZ-related targets:

1. **One complete block:** measure \(\overline{\mathsf{CZ}}_{0,1}\)
   on its two internal logical qubits. This is the target derived below.
2. **Two complete blocks B,C:** apply matched physical CZ's,
   \(U_{BC}=\prod_{q=0}^{19}\mathsf{CZ}_{B_q,C_q}\).
   Self-duality makes this a code-preserving involution.

For the second target, conjugation gives

\[
\overline X_0^B\mapsto\overline X_0^B\overline Z_1^C,
\qquad
\overline X_1^B\mapsto\overline X_1^B\overline Z_0^C,
\]

and the corresponding transformations with B,C exchanged. The signed
logical action, fixed with +1 phase on logical |0000>, is

\[
U_{BC}\big|_{\mathrm{code}}
=\overline{\mathsf{CZ}}_{B_0,C_1}
\overline{\mathsf{CZ}}_{B_1,C_0}.
\]

So the simplest two-copy implementation measures a **product of two
crossed logical CZ's**, rather than one addressed logical CZ. A connected
ancilla graph gives one outcome for this product. It does not give two
separate CZ outcomes. This route fits the companion's CCZ enrichment
directly, but consumes forty data qubits and measures a different observable.

### The native one-block phase pattern has a residual Pauli

On inner block j define

\[
F_j=S_{4j}^{\dagger}S_{4j+1}S_{4j+2}S_{4j+3}^{\dagger},
\qquad F=\prod_{j=0}^4F_j.
\]

This is the five-inner-block phase pattern associated with the logical CZ
in `fig:actions` and the controlled-phase pattern in `fig:cz_to_tof`.
We specify all five blocks explicitly and check its action against Table I.
The last row of the supplied `figures/table.png` prints an upper product
index of 3 for this phase pattern, which would include only four inner
blocks. We use the five-block version here, independently verified against
the code table, rather than treating that printed range as a complete
twenty-qubit circuit.
The appendix explicitly warns that the native logical CZ actually has
the action

\[
F\big|_{\mathrm{code}}
=\overline{\mathsf{CZ}}_{0,1}\overline Z_1.
\]

For a computational bit string b satisfying \(Mb=0\), define
\(\ell_0=b\cdot R_b\) and \(\ell_1=b\cdot R_a\). Exact evaluation
of the phase gives

\[
F|b\rangle=(-1)^{\ell_0\ell_1+\ell_1}|b\rangle.
\]

The phase is constant on each coset of the X-stabilizer-support space,
so it acts this way on the encoded computational basis as well.
The four logical phases are (+1,-1,+1,+1), ordered as 00,01,10,11.
To obtain standard CZ phases (+1,+1,+1,-1), use
\(\overline Z_1 F\) **as the measured observable**.

Applying \(\overline Z_1\) to the state after measuring F would not
change which eigenspace was selected. The Pauli must be included in the
controlled measurement circuit, or the observable must be changed by a
suitable conjugation before measurement.

### Why controlled S's need a little more work than controlled CZ's

Physically,

\[
F_j^2=Z_{4j}Z_{4j+1}Z_{4j+2}Z_{4j+3}=s_{Z,j}.
\]

Thus \(F_j^2=I\) on the inner code space, but not on the full
four-qubit Hilbert space. A controlled order-four gate does not satisfy
the simple enrichment identity
\(\Omega^{\dagger}X_a\Omega=X_aF_j\) as an unrestricted operator
identity: its two off-diagonal control blocks contain \(F_j\) and
\(F_j^{\dagger}\), which differ outside the inner code space.

One could work with explicitly constrained inner sectors. Instead, we
can replace F_j by an exactly involutory Clifford with the same action
on the inner +1 sector. This keeps the companion's Z2 derivation intact.

## An order-two physical representative for the desired intra-block CZ

Let \(p_j\) be the computational parity of the four bits in block j.
Apply an S-dagger phase to this parity:

\[
Q_j=\frac{I+s_{Z,j}}2-i\frac{I-s_{Z,j}}2.
\]

This is a unitary Clifford: it is a Clifford rotation about the Pauli
\(s_{Z,j}\). On every valid inner codeword, \(Q_j=I\). Hence replacing
F_j by \(V_j=F_jQ_j\) leaves its encoded action unchanged.

For local bits \(b_0,b_1,b_2,b_3\), F_j contributes
\(i^{-b_0+b_1+b_2-b_3}\), while Q_j contributes \(i^{-p_j}\).
The mod-four identity

\[
p_j\equiv\sum_r b_r-2\sum_{r<s}b_rb_s\pmod4
\]

therefore gives

\[
\boxed{
V_j=Z_{4j}Z_{4j+3}
\prod_{0\le r<s\le3}\mathsf{CZ}_{4j+r,4j+s}.
}
\]

This is six CZ's on the six unordered pairs in one four-qubit block,
and two Z's. Every factor is diagonal and squares to identity, so
\(V_j^{\dagger}=V_j\) and \(V_j^2=I\) on the entire Hilbert space.
It agrees with F_j on the inner code space. The parity phase is needed
only for this derivation; the displayed Z/CZ circuit implements V_j directly.

Now include the required logical \(\overline Z_1=Z_{R_a}\).
The combined single-qubit Z support is

\[
R=\left(\bigcup_{j=0}^4\{4j,4j+3\}\right)\mathbin\triangle R_a
=\{0,2,4,7,16,19\},
\]

where \(\triangle\) denotes symmetric difference. Define

\[
\boxed{
U=Z_R\prod_{j=0}^4\prod_{0\le r<s\le3}
\mathsf{CZ}_{4j+r,4j+s}.
}
\]

This is an exact physical Clifford involution, and

\[
U\big|_{\mathrm{code}}=\overline{\mathsf{CZ}}_{0,1}.
\]

Its global phase is fixed by the displayed circuit: U has eigenvalue +1
on logical |00>. That phase matters because a minus sign exchanges the
labels of the two measured outcomes.

Factor U into five commuting involutions with disjoint data supports:

\[
w_j=Z_{R\cap B_j}\prod_{0\le r<s\le3}
\mathsf{CZ}_{4j+r,4j+s},\qquad U=\prod_{j=0}^4w_j.
\]

Each factor preserves its inner C4 code space. A single w_j need not
preserve the upper-level code space; the full product does. This is
analogous to the companion's partial physical CZ products outside the
ancilla cocycle kernel.

## A five-vertex graph that measures this U

### Ancilla complex and enrichment

Choose a path with vertices \(v_0,\ldots,v_4\) and edges
\(e_j=\langle v_j,v_{j+1}\rangle\), \(j=0,\ldots,3\). Put one
temporary qubit \(a_j\) on each vertex and one gauge qubit \(A_j\)
on each edge. There are nine ancillary qubits.

The ancilla coboundary is

\[
d^a_0\phi=(\phi_0+\phi_1,\phi_1+\phi_2,
\phi_2+\phi_3,\phi_3+\phi_4).
\]

Its kernel is \(\{00000,11111\}\): connectedness gives one global
symmetry. This ancilla is not the twenty-qubit code's check complex.

Initialize \(|+\rangle_a^{\otimes5}|0\rangle_A^{\otimes4}\).
The cluster entangler is the eight-CNOT circuit

\[
C_A=\prod_{j=0}^3
\mathsf{CNOT}_{a_j\to A_j}
\mathsf{CNOT}_{a_{j+1}\to A_j}.
\]

Enrich it with

\[
\Omega=\prod_{j=0}^4\operatorname{ctrl}_{a_j}(w_j).
\]

Each controlled CZ factor is a CCZ. Each controlled Z factor is a CZ
between a_j and its data target. Thus one application of enrichment uses
**thirty CCZ's and six CZ's**, grouped into five disjoint four-data-qubit
neighborhoods. This circuit has non-Clifford physical gates, just as the
CCZ enrichment in the companion does.

Because the w_j's are involutions,

\[
\Omega^{\dagger}X^a_j\Omega=X^a_jw_j,
\qquad
\Omega^{\dagger}X^a_{11111}\Omega=X^a_{11111}U.
\]

This proves the required symmetry-enrichment identity on the full Hilbert
space, and U has the desired code-preserving action. Moreover,
\([\Omega,C_A]=0\): both circuits leave all computational control bits
unchanged and act on different targets. These are the two identities used
in the companion's gauging/ungauging derivation.

### All steps, including the offset correction

Let \(|\Psi\rangle\) be any state of one C4-Helix block.

1. Prepare the nine ancillas, apply C_A, then apply \(\Omega\).
2. Measure all five a_j's in X; retain signs \(x_j\in\{+1,-1\}\).
3. Apply \(C_A^{\dagger}\). Measure the four A_j's in Z, and write
   their signs as \((-1)^{z_j}\), with \(z_j\in\mathbb F_2\).
4. Choose the vertex vector \(\eta\) with \(\eta_0=0\) and
   \(\eta_{j+1}=\eta_j+z_j\). It satisfies \(d^a_0\eta=z\).
   Apply \(X^a_\eta\).
5. Apply \(\Omega^{\dagger}\). The temporary qubits return to
   \(|+\rangle^{\otimes5}\); the gauge qubits remain in \(|z\rangle\).
   Both registers can now be discarded.

The a_j measurements must leave the qubits available for the later gates.
For destructive readout, reprepare the recorded X eigenstates before
step 3. The X correction is required for the chosen offset irrespective
of the sign \(x_\eta=\prod_jx_j^{\eta_j}\); that sign is only a global
phase. A software correction requires propagating its effect through the
inverse enrichment.

### Why the result is precisely a logical projector

Write \(\Pi_x=\prod_j(I+x_jX^a_j)/2\). Expanding these projectors
and pulling them through C_A, exactly as in the companion, gives

\[
C_A^{\dagger}\Pi_x\Omega C_A
\bigl(|\Psi\rangle|0\rangle_A|+\rangle_a\bigr)
=2^{-5}\sum_{\phi\in\mathbb F_2^5}
x_\phi X^a_\phi\Omega
\bigl(|\Psi\rangle|d^a_0\phi\rangle_A|+\rangle_a\bigr).
\]

The observed edge string z retains only \(d^a_0\phi=z\). On this
path, the solutions are \(\eta\) and \(\eta+11111\). Applying
\(X^a_\eta\) cancels their common offset. Applying
\(\Omega^{\dagger}\) then attaches I or U to the two remaining
ancilla symmetry patterns. Since \(X^a_{11111}|+\rangle_a=|+\rangle_a\),
the unnormalized final state is

\[
2^{-5}x_\eta(I+xU)|\Psi\rangle\otimes|z\rangle_A\otimes|+\rangle_a
=\frac{x_\eta}{16}P_x|\Psi\rangle\otimes|z\rangle_A\otimes|+\rangle_a,
\]

where

\[
\boxed{
x=\prod_{j=0}^4x_j,\qquad
P_x=\frac{I+x\overline{\mathsf{CZ}}_{0,1}}2
\quad\text{on the input code space}.
}
\]

There are sixteen vertex-sign strings of each parity and sixteen edge
strings. Each fixed full record with parity x has probability
\(\|P_x\Psi\|^2/256\); summing them gives the usual Born probability
\(\|P_x\Psi\|^2\). The edge correction removes a physical byproduct,
while the parity x records the logical measurement. There is no ideal
postselection on the edge string: all sixteen strings are in
\(\operatorname{im}d^a_0\).

### The magic state agrees with both manuscripts

Start from the encoded state \(|\overline{++}\rangle\). CZ has
eigenvalue +1 on 00,01,10 and -1 on 11. Therefore

\[
P_+|\overline{++}\rangle
=\frac{|\overline{00}\rangle+|\overline{01}\rangle
+|\overline{10}\rangle}{2},
\qquad
P_-|\overline{++}\rangle=\frac{|\overline{11}\rangle}{2}.
\]

With probability 3/4 the normalized output is the manuscript's magic
state \(|\overline{CZ}\rangle\), with three amplitudes of magnitude
\(1/\sqrt3\). With probability 1/4 the output is the non-magic
\(|\overline{11}\rangle\). The latter branch can be recycled by
logical X's followed by transversal physical H, whose logical SWAP has
no effect on |++>.

Here “CZ state” means this three-term resource state. Applying a CZ
unitary to |++> gives a four-term stabilizer graph state instead.
Measuring CZ is the non-Clifford operation, despite CZ itself being a
Clifford unitary.

## What the source's fault-tolerant architecture contributes

The manuscript measures inner weight-four checks using paired syndrome
ancillas that also flag one another's dangerous errors. Alternating
circuits exchange all four data qubits with fresh ancillas over two rounds
to mitigate leakage. Upper weight-eight checks use a syndrome ancilla and
three flags. A full eighteen-check extraction uses 32 ancillas and has
depth ten in the stated schedule.

The important distinction is between **code distance** and **circuit-level
distance**. An ordinary transversal single-qubit gate does not spread a
single data error to several data qubits. Controlled enrichment couples
ancillas to several data qubits, and our new Z/CZ representative contains
intra-block two-qubit gates. Neither its order-two identity nor the static
distance-six calculation proves that its noisy measurement circuit is
fault tolerant.

The source establishes circuit-level distance six for its flagged global
phase gate followed by syndrome extraction. In its non-Clifford appendix,
it describes logical CZ measurement using a twenty-qubit cat state and
mentions flags or modified Shor extraction as possible alternatives. The
main experiments validate memory, Clifford control, and a heterogeneous
chain-map interface; they do not implement the graph-gauging circuit
derived here.

For a practical version of this construction, the next concrete tasks are:

1. Choose decompositions of the CCZ/CZ enrichment and its inverse, including
   suitable flags or verified ancillary resources. Check how a fault on a
   temporary qubit spreads through its six CCZ gates.
2. Specify where to measure the inner and upper checks. Intermediate
   code deformation matters: measuring original upper checks while only a
   partial symmetry has acted can destroy the intended coherent branch.
3. Construct detectors for the entire adaptive measurement circuit,
   preserving the logical measurement parity while correcting actual
   errors. Unlike a redundant code syndrome, that parity is information
   about the input state and must not simply be forced to +1.
4. Verify the circuit's minimum failing-fault order, including ancilla
   preparation, readout, correlated propagation, and residual phases.
5. Compare the full resources against the manuscript's cat-state CZ
   measurement. Our ideal circuit uses twenty data plus nine ancilla qubits,
   but that count excludes verification, flags, and QEC ancillas.

Random initial stabilizer signs also require attention. The ideal derivation
assumes the +1 code space. The native F has order two there because each
inner \(s_{Z,j}=+1\). Our involutory U exists on every physical sector,
but its identification with the chosen logical CZ was proved for the
standard +1 sector. The source's sign tracking, or an explicit recovery
to that sector, must be included before claiming the same observable in a
random-syndrome preparation.

Finally, a C4-Helix code and a rotated surface code can be coupled by a
chain-map CNOT in the source's architecture. Those chain maps are maps
**between input CSS code complexes**. The map \(d^a_0\) above instead
records differences of vertex bits in the **measurement ancilla**. They
serve different jobs, although both are binary maps.

## Reproducible checks and current status

[check-c4-helix.py](check-c4-helix.py) reads the twenty-qubit check and
logical-support table directly from the manuscript TeX. Run it with
`python3 notes/check-c4-helix.py` from the repository root. It uses only
Python's standard library and checks:

- CSS commutation, rank nine for each check type, the two redundant-check
  relations, and the canonical logical commutation pairing;
- minimum logical distance six, and the outer code's three-paired-block
  lower bound used in the concatenation argument;
- the native \(\mathsf{CZ}\overline Z_1\) phase and corrected physical
  involution on all 2048 computational strings satisfying the Z checks;
- the two-term kernel sum for every one of the 512 ancillary measurement
  records, on all four logical computational sectors.

The code translation and the ideal logical CZ projector are explicit and
verified. A flagged, decoded measurement circuit with demonstrated
circuit-level distance is the remaining engineering and fault-tolerance
problem; the native gate's fault-tolerance result cannot be transferred to
our enrichment circuit without that analysis.
