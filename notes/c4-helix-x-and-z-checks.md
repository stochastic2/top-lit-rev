# Understanding the X and Z checks of C4-Helix

**Source:** [Appendix A of arXiv:2609.03194v1](../arXiv-2609.03194v1/appendix.tex),
“Details of the [[20,2,6]] C4-Helix code,” and Table I.
**Background:** the stabilizer and binary-support notation in
[Non-Abelian anyons from gauging, v2](non-abelian-anyons-from-gauging-v2.md).

This note focuses on the code's defining constraints. We begin by reading
the first matrix in Appendix A. The paper constructs C4-Helix in three
stages: a five-qubit code, a ten-qubit code, then the twenty-qubit code.
The first matrix describes the **five-qubit starting code**.

## 1. What is a symplectic parity-check matrix?

**Definition — check.** A Pauli check is a Hermitian Pauli product
\(S_i\) whose +1 eigenspace is required by the code. For mutually
commuting checks, the code space is

\[
\mathcal C=\{\,|\psi\rangle:S_i|\psi\rangle=|\psi\rangle
\text{ for every }i\,\}.
\]

For example, the check \(Z_0Z_1\) requires even computational parity
on two qubits: its +1 eigenspace is spanned by |00> and |11>.
This is the same notion of check as in the companion note.

**Definition — binary symplectic support matrix.** For a list of m Pauli
operators on n qubits, this is an \(m\times2n\) binary matrix
\(H=(H_X\mid H_Z)\). Row i contains the X-selection bits followed by
the Z-selection bits for operator i. Operator phases are specified separately.

**Definition — symplectic parity-check matrix.** This is a binary
symplectic support matrix whose rows describe a chosen generating list
of the code's commuting Pauli checks. Thus “parity-check” identifies
**which operators are being recorded**: the constraints defining the code.
It is the same binary representation you already understand.

For example, the checks \(S_1=X_0X_1\), \(S_2=Z_0Z_1\) have matrix

\[
H=\begin{pmatrix}
1&1&\vline&0&0\\
0&0&\vline&1&1
\end{pmatrix}.
\]

Together they select the state \((|00\rangle+|11\rangle)/\sqrt2\).
The matrix specifies the two operators; their prescribed +1 eigenvalues
give the constraints on the state.

**Definition — generating list.** A list of checks generates all their
products. Requiring +1 for the listed checks automatically requires +1
for their products. The list may include redundant checks: adding a
check already equal to a product of others adds no new constraint.

### Why “parity-check” and “symplectic”?

The word *parity* comes from counting anticommutations modulo two.
Let a check have row \((\mathbf x_i\mid\mathbf z_i)\), and let a Pauli
error E have support vector \((\mathbf e_X\mid\mathbf e_Z)\). Then

\[
S_iE=(-1)^{s_i}ES_i,\qquad
s_i=\mathbf x_i\cdot\mathbf e_Z+
\mathbf z_i\cdot\mathbf e_X\pmod2.
\]

Here each dot product is the sum of pairwise bit products, modulo two.
The first counts X factors of the check overlapping Z factors of the
error; the second counts Z factors of the check overlapping X factors of
the error. This paired overlap rule is the **symplectic pairing**.

If the initial state has \(S_i=+1\), the errored state has eigenvalue
\((-1)^{s_i}\). For the two-check example, \(E=Z_0\) gives
\((s_1,s_2)=(1,0)\): the XX check changes sign, and the ZZ check does not.
This list of sign-change bits is the **syndrome**.

Thus H is both a compact list of the code's constraints and the data from
which we compute these parity tests. The signs of the chosen checks are
still needed in addition to H; the checks used below all have positive signs.

## 2. Reading the first matrix in Appendix A

The paper writes

\[
H_{[[5,1,3]]}=
\left(\begin{array}{ccccc|ccccc}
1&0&0&1&0&0&1&1&0&0\\
0&1&0&0&1&0&0&1&1&0\\
1&0&1&0&0&0&0&0&1&1\\
0&1&0&1&0&1&0&0&0&1
\end{array}\right).
\]

**Definition — \([[n,k,d]]\).** This labels a code with n physical
qubits, k encoded qubits, and distance d. The distance is the smallest
number of qubits supporting a Pauli operator that preserves the code
space but acts nontrivially on its encoded information.

Here there are five physical qubits, labelled 0 through 4, and four rows
specifying four checks. Both halves refer to those same five qubits.
Reading the rows gives

\[
\begin{aligned}
S_1&=X_0Z_1Z_2X_3,\\
S_2&=X_1Z_2Z_3X_4,\\
S_3&=X_0X_2Z_3Z_4,\\
S_4&=Z_0X_1X_3Z_4.
\end{aligned}
\]

What you should infer from this matrix is precisely the code-space
condition \(S_i|\psi\rangle=|\psi\rangle\) for these four operators.
They commute: for example, S_1 and S_2 have two anticommuting overlaps,
at qubits 1 and 3. The four constraints are independent, leaving a
\(2^{5-4}=2\)-dimensional code space, or one encoded qubit.

### What do the paper's \(H_X\) and \(H_Z\) mean here?

In the next sentence of Appendix A, the paper names the two halves
\(H=(H_X\mid H_Z)\). Here \(H_X\) records the X factors of **all four
mixed checks**, and \(H_Z\) records their Z factors. For example,
their first rows select \(X_0X_3\) and \(Z_1Z_2\). The actual first
check is their product \(X_0X_3Z_1Z_2\); neither factor is separately
imposed as a check.

**Definition — CSS code.** A Pauli stabilizer code is CSS if it admits
a generating list consisting of pure X checks and pure Z checks. This
five-qubit starting code is non-CSS: the displayed checks mix X and Z.

In the companion's CSS notation, \(H_X\) instead lists pure X checks,
and \(H_Z\) lists pure Z-check supports in columns. Therefore the symbols
\(H_X,H_Z\) in this first Appendix A matrix do not yet have the same
meaning as the companion's two incidence matrices. In particular,
\(H_XH_Z=0\) from the companion is not the commutation test for this
mixed-check matrix.

For the paper's mixed-check convention, the commutation test is

\[
H_XH_Z^{\mathsf T}+H_ZH_X^{\mathsf T}=0
\qquad\text{over }\mathbb F_2,
\]

where \(\mathsf T\) denotes transpose. Its entry (i,j) is the symplectic
pairing of check rows i and j, so zero means those checks commute.

## 3. Doubling: each mixed check gives one X check and one Z check

Write the five-qubit support matrix as \(H=(P\mid Q)\), using P and Q
for the paper's two halves to keep them distinct from CSS check matrices.
The ten-qubit code has pure X-check support rows \((P\ Q)\) and pure
Z-check support rows \((Q\ P)\).

For example, the original first check \(X_0Z_1Z_2X_3\) has support row
\((10010\mid01100)\). It supplies two new checks on qubits 0 through 9:

\[
T^X_1=X_0X_3X_6X_7,\qquad
T^Z_1=Z_1Z_2Z_5Z_8.
\]

For the X check, both halves now select X's, on two different groups of
five qubits. For the Z check, the halves are exchanged and both select Z's.
Repeating this for the four original rows gives four independent checks
of each type. Thus ten physical qubits have eight independent constraints
and encode two qubits.

A mixed Pauli check is measured as one joint observable. For example,
measuring \(X_0Z_1Z_2X_3\) returns its product eigenvalue; it does not
require separately measuring each factor and revealing their individual
values. “X check” and “Z check” likewise refer to joint products.

## 4. Encoding the ten-qubit code into five C4 blocks

**Definition — encoded or logical qubit.** A two-dimensional degree of
freedom inside a code space is an encoded qubit. Its logical X and Z are
operators preserving that code space and acting there as the usual X and Z.
A code space of dimension four can carry two such qubits.

### The C4 code carries two qubits in four physical qubits

The inner \([[4,2,2]]\) code, called C4, has checks

\[
s_X=X_0X_1X_2X_3,\qquad s_Z=Z_0Z_1Z_2Z_3.
\]

Two independent constraints on four qubits leave dimension
\(2^{4-2}=4\), so this block carries two encoded qubits. In the paper's
choice of encoded operators,

\[
\begin{array}{c|cc}
&\text{encoded qubit 0}&\text{encoded qubit 1}\\\hline
\text{logical X}&X_0X_3&X_2X_3\\
\text{logical Z}&Z_2Z_3&Z_0Z_3
\end{array}.
\]

These four operators commute with both checks. Within each column X
and Z anticommute; between columns they commute. Hence they describe
two independent qubits within the constrained space.

### Which ten-qubit labels go into which block?

Group the ten intermediate qubits into pairs

\[
(0,5),\ (1,6),\ (2,7),\ (3,8),\ (4,9).
\]

Each pair becomes the two encoded qubits of one C4 block. Thus pair
\((j,j+5)\) is represented by four final physical qubits
\(4j,4j+1,4j+2,4j+3\), with j the first encoded qubit and j+5 the second.
The resulting substitution is

\[
\begin{aligned}
X_j&\longmapsto X_{4j}X_{4j+3},&
Z_j&\longmapsto Z_{4j+2}Z_{4j+3},\\
X_{j+5}&\longmapsto X_{4j+2}X_{4j+3},&
Z_{j+5}&\longmapsto Z_{4j}Z_{4j+3},
\end{aligned}
\qquad j=0,\ldots,4.
\]

The left-hand indices refer to the ten-qubit code. The right-hand indices
refer to the final twenty physical qubits. This step is **concatenation**:
the ten-qubit code is the outer code, and C4 is the inner code used to
represent its qubits. We need five blocks of four qubits, giving twenty
physical qubits in total.

### What happens to an outer check?

Replace every Pauli factor by its corresponding inner logical operator.
For the first X check from section 3,

\[
\begin{aligned}
T^X_1=X_0X_3X_6X_7
&\longmapsto
(X_0X_3)(X_{12}X_{15})(X_6X_7)(X_{10}X_{11})\\
&=X_0X_3X_6X_7X_{10}X_{11}X_{12}X_{15}.
\end{aligned}
\]

Similarly,

\[
T^Z_1=Z_1Z_2Z_5Z_8
\longmapsto Z_0Z_3Z_6Z_7Z_{10}Z_{11}Z_{12}Z_{15}.
\]

The resulting X and Z checks have the same support. Each acts on eight
final qubits. They impose the outer constraints on the encoded qubits
inside the C4 blocks.

The final code therefore has two kinds of constraint:

- **Inner checks:** one four-qubit X check and one four-qubit Z check
  per C4 block, giving ten independent checks.
- **Outer checks:** the four X checks and four Z checks of the ten-qubit
  code, rewritten using the substitution above, giving eight more.

Together they give eighteen independent constraints on twenty qubits,
leaving the same two encoded qubits as the outer code. The manuscript
establishes distance six, hence the final label \([[20,2,6]]\).

## 5. The final check representatives in Table I

For reference, the final checks themselves can already be read directly
from the right panel of Table I. The paper multiplies some substituted
outer checks by inner checks to make their measurement more convenient.
This changes their supports but leaves the joint +1 code space unchanged.

**Definition — check support set.**
For a subset R of physical-qubit labels, let

\[
X_R=\prod_{q\in R}X_q,\qquad Z_R=\prod_{q\in R}Z_q.
\]

Each row of the following table supplies **two** C4-Helix checks, X_R and
Z_R, both required to have eigenvalue +1. Physical labels now run from
0 through 19.

| Row | Support R |
|---|---|
| 0 | 0,1,2,3 |
| 1 | 4,5,6,7 |
| 2 | 8,9,10,11 |
| 3 | 12,13,14,15 |
| 4 | 16,17,18,19 |
| 5 | 0,3,6,7,10,11,12,15 |
| 6 | 4,7,8,9,14,15,16,19 |
| 7 | 1,2,8,11,12,13,18,19 |
| 8 | 2,3,5,6,13,14,16,17 |
| 9 | 0,1,4,5,9,10,17,18 |

For example, row 5 means
\(X_0X_3X_6X_7X_{10}X_{11}X_{12}X_{15}\) and
\(Z_0Z_3Z_6Z_7Z_{10}Z_{11}Z_{12}Z_{15}\).

Rows 0–4 are the checks inside the five four-qubit blocks. Rows 5–9
are inherited from the ten-qubit code. The product of the five latter
X checks is identity, and likewise for the Z checks. Hence only nine
checks of each type are independent: eighteen total constraints on
twenty qubits leave two encoded qubits.
