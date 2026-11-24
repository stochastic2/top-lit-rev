# Exact simulation of the noiseless 65-qubit C4-Helix circuit

This note specifies a proposed classical simulator for
[`src/c4_helix_noiseless.py`](../src/c4_helix_noiseless.py), implementing the
noiseless specialization of the
[V2 integrated procedure](full_procedure_integrated_v2.md).
It is a simulation plan, not an implementation or a runtime benchmark.

The simulator will follow the physical preparations, Fredkins, measurements,
and feedforward gates. It will sample the physical measurement records and
return a compressed description of the unmeasured C state.

**No physical stabilizer measurement is added.** “Stabilizer” describes a
classical representation of a quantum state. The only physical measurements
in a successful attempt are the five vertex-X measurements, twenty gauge-Z
measurements, and twenty B-Z measurements already present in the circuit.

The concrete representation proposed below is simpler than a general
stabilizer tableau: for this particular circuit, each component is a uniform
superposition over a binary affine subspace. We store its generators, not
its individual basis strings. Interference is retained by keeping a signed
coherent sum of these components.

## 1. Registers, bits, and operators

The registers are:

| Register | Physical qubits | Measurement |
|---|---|---|
| V | a, b, c, d, e | X after enrichment |
| A | A_0,...,A_19 | Z after vertex feedforward |
| B | B_0,...,B_19 | Z after ungauging |
| C | C_0,...,C_19 | Retained quantum output |

There are 65 physical qubits in total. A classical computational-basis
label for BC is a vector

\[
x=(x_B,x_C)\in\mathbb F_2^{40},
\qquad
x_B,x_C\in\mathbb F_2^{20}.
\]

Here \(\mathbb F_2=\{0,1\}\); addition and dot products of binary vectors are
evaluated modulo two. Coordinates are in physical-label order, so \(x_B[q]\)
is the value of B_q. The twenty-bit vector \(e_q\) has a one only at q.

Let \(v\in\{a,b,c,d,e\}\), with numerical indices 0,...,4, and define

\[
J_v=\{4v,4v+1,4v+2,4v+3\},\qquad
T_v=\prod_{q\in J_v}\mathrm{SWAP}(B_q,C_q).
\]

For a five-bit vector \(t=(t_a,t_b,t_c,t_d,t_e)\), set

\[
V_t=\prod_v T_v^{t_v},\qquad U=\prod_vT_v.
\]

We use \(P_t\) for the permutation of forty binary coordinates induced by
\(V_t\), so \(V_t|x\rangle=|P_tx\rangle\). A SWAP exchanges two coordinates;
it introduces no sign.

The symbol \(t\) labels coherent components. It is **never sampled as a
hidden vertex-Z measurement**. Actual measured records will be called
\(b\) for vertex X, \(m\) for gauge Z, and \(n\) for B Z.

## 2. Construct the physical encoded inputs

For a support R_s, define the binary vector
\(r_s=\sum_{q\in R_s}e_q\). Use these nine independent supports:

\[
\begin{aligned}
R_0&=\{0,1,2,3\},&R_1&=\{4,5,6,7\},\\
R_2&=\{8,9,10,11\},&R_3&=\{12,13,14,15\},\\
R_4&=\{16,17,18,19\},\\
R_5&=\{0,3,6,7,10,11,12,15\},\\
R_6&=\{4,7,8,9,14,15,16,19\},\\
R_7&=\{1,2,8,11,12,13,18,19\},\\
R_8&=\{2,3,5,6,13,14,16,17\}.
\end{aligned}
\]

Define the binary subspaces and logical-X vector

\[
H=\operatorname{span}_{\mathbb F_2}\{r_0,\ldots,r_8\},\qquad
\xi=e_2+e_3+e_8+e_{11}+e_{12}+e_{15},\qquad
K=\operatorname{span}_{\mathbb F_2}(H,\xi).
\]

Their dimensions are \(\dim H=9\), \(\dim K=10\), and \(\xi\notin H\).
The physical input states are

\[
|\overline{00}\rangle=2^{-9/2}\sum_{h\in H}|h\rangle,
\qquad
|\overline{+0}\rangle=2^{-10/2}\sum_{k\in K}|k\rangle.
\]

Therefore define

\[
L_0=H\times K\subseteq\mathbb F_2^{40},\qquad
d=\dim L_0=19,
\qquad
|\psi\rangle=2^{-d/2}\sum_{x\in L_0}|x\rangle.
\]

**What the simulator stores:** nineteen independent forty-bit generators:
\((r_s,0)\), \((0,r_s)\), and \((0,\xi)\). It does not store the
\(2^{19}\) strings in L_0.

To check the actual source circuits, start with an empty generator list.
Each source H gate, applied to a fresh zero pivot, adds that coordinate's
unit vector. For every source CNOT c->q, replace coordinate q of every
generator by its value plus coordinate c. This follows the actual H/CNOT
schedule and must produce the spaces above. This H rule is used only for
these fresh-zero source pivots, not as a general rule for arbitrary H gates.

## 3. The data structure used after measurements

A binary affine subspace has the form

\[
\mathcal A=o+\operatorname{span}\{g_1,\ldots,g_r\},
\]

where o is an offset vector and the g_i are independent binary generators.
It contains \(2^r\) strings. Define an **unnormalized** ket

\[
|\mathcal A\rangle:=\sum_{x\in\mathcal A}|x\rangle,
\qquad
\langle\mathcal A|\mathcal A\rangle=2^r.
\]

Its normalized version is a stabilizer state. We deliberately store the
unnormalized version to keep the sampling arithmetic integral.

Explicitly, for a binary vector y let X(y) and Z(y) mean the products of
physical X and Z operators at its nonzero positions. Then

\[
X(g_i)|\mathcal A\rangle=|\mathcal A\rangle,\qquad
Z(z)|\mathcal A\rangle=(-1)^{z\cdot o}|\mathcal A\rangle
\quad\text{if }z\cdot g_i=0\text{ for every }i.
\]

These identities explain the stabilizer description; no such operator
is measured during the simulation unless the physical circuit calls for it.

Each coherent component will contain:

1. A signed integer coefficient \(w_j\).
2. The computational-basis label \(v_j\) of unmeasured vertices.
3. The computational-basis label \(\gamma_j\) of unmeasured gauge qubits.
4. A data affine space \(\mathcal A_j\), represented by offset and generators.

These describe

\[
|\eta\rangle=\sum_{j=1}^{\chi}
w_j|v_j\rangle|\gamma_j\rangle|\mathcal A_j\rangle,
\qquad
|\Psi\rangle=\frac{|\eta\rangle}{\sqrt{\mathcal N}},
\qquad
\mathcal N=\langle\eta|\eta\rangle.
\]

A common nonzero scalar multiplying all components can be omitted. Empty
vertex or gauge registers have a single empty label. B coordinates can
remain in the data vectors after measurement, fixed to their recorded
values, until they are removed when returning C.

The components are added **coherently**. We never pick one component with
probability proportional to its individual norm.

## 4. Compute norms using binary linear equations

Two unnormalized affine kets have overlap

\[
\boxed{\langle\mathcal A_i|\mathcal A_j\rangle
=|\mathcal A_i\cap\mathcal A_j|.}
\]

For example, the spaces \(\{00,11\}\) and \(\{00,10\}\) have overlap one:
only the basis string 00 appears in both sums.

For general spaces
\(\mathcal A=o+\operatorname{rowspan}(G)\) and
\(\mathcal B=o'+\operatorname{rowspan}(G')\), with dimensions r and r',
solve the binary linear system

\[
G^T\lambda+(G')^T\mu=o+o'.
\]

If it is inconsistent, the intersection is empty. Otherwise, with
\(R=\operatorname{rank}\begin{bmatrix}G\\G'\end{bmatrix}\),

\[
|\mathcal A\cap\mathcal B|=2^{r+r'-R}.
\]

This needs Gaussian elimination on small binary matrices, not enumeration
of either space. Consequently,

\[
\boxed{
\mathcal N=
\sum_{i,j=1}^{\chi}w_iw_j
\mathbf1[v_i=v_j]\mathbf1[\gamma_i=\gamma_j]
|\mathcal A_i\cap\mathcal A_j|.
}
\]

The symbol \(\mathbf1[\cdot]\) is one when its condition is true, otherwise
zero. The terms with i different from j are interference terms. A sum of
the separate component norms would omit them and give wrong probabilities.

All terms in this expression are integers. Destructive interference can
make \(\mathcal N=0\); such a candidate measurement outcome is impossible.

## 5. Prepare the graph resource without sampling its vertices

For edge q, let its endpoints be \((u_q,v_q)\). The exact edge list is:

| q | Endpoints | q | Endpoints |
|---|---|---|---|
| 0 | a,e | 10 | a,e |
| 1 | c,e | 11 | a,c |
| 2 | c,d | 12 | a,c |
| 3 | a,d | 13 | c,d |
| 4 | b,e | 14 | b,d |
| 5 | d,e | 15 | a,b |
| 6 | a,d | 16 | b,d |
| 7 | a,b | 17 | d,e |
| 8 | b,c | 18 | c,e |
| 9 | b,e | 19 | b,c |

Define

\[
p(t)_q=t_{u_q}+t_{v_q}\pmod2.
\]

The physical graph preparation applies H to each vertex and then the two
endpoint-to-A_q CNOTs for each q. Its state, including the data, is

\[
|\Psi_{\mathrm{graph}}\rangle
=\frac{1}{\sqrt{32}}\sum_t|t\rangle|p(t)\rangle|\psi\rangle.
\]

**Concrete construction of the stored records:**

1. Start with one record: all vertex and gauge labels zero, data space L_0.
2. For each vertex H, replace each record by its two coherent copies with
   that vertex bit 0 and 1. The common factor \(1/\sqrt2\) can be omitted.
3. For each CNOT vertex v -> A_q, add the record's bit t_v to its gauge bit q.

There are 32 records at the end, all with coefficient +1. Their labels are
\((t,p(t))\), and every data space is still L_0. Their unnormalized norm is
\(32\,2^{19}=2^{24}\).

No random choice has been made: all 32 records are retained.

## 6. Apply every physical enrichment Fredkin

At physical label q, the control is vertex \(\lfloor q/4\rfloor\).
In each record its computational-basis value is known:

- If that bit is 0, leave the data generators and offset unchanged.
- If it is 1, exchange the B_q and C_q coordinates in every data generator
  and in the offset.

This is exactly the action of the Fredkin on that component. It does not
replace a coherent control by a sampled classical bit: the coherent sum
still contains both values of that control.

After the twenty gates, the record labelled t has data space

\[
L_t=P_tL_0,
\]

and the normalized physical state is

\[
\boxed{
|\Psi_{\mathrm{enriched}}\rangle
=2^{-(5+d)/2}\sum_t|t\rangle|p(t)\rangle|L_t\rangle,
\qquad d=19.
}
\]

Every L_t is obtained by coordinate permutations. The record count is
still 32, and each space still has nineteen independent generators.

The three-gate Fredkin in the Guppy source can also be followed directly.
After its first CNOT, its Toffoli has a fixed vertex-control bit in each
record, so it becomes either identity or a CNOT. The last CNOT is then
applied normally. This permits checking the decomposition gate by gate.

## 7. Sample the five actual vertex-X measurements

The source applies H to a vertex and measures it in Z. Equivalently, use
the X-basis bra

\[
\langle b_X|z\rangle=2^{-1/2}(-1)^{bz},
\qquad b,z\in\{0,1\}.
\]

Here b=0 means X eigenvalue +1; b=1 means eigenvalue -1.
For the next measured vertex, construct a candidate list for each b:

1. In record j, read that vertex bit z_j.
2. Replace \(w_j\) by \((-1)^{bz_j}w_j\).
3. Remove the measured vertex from its label.
4. Compute the candidate norm \(\mathcal N_b\) with Section 4.

The common bra factor \(1/\sqrt2\) was omitted in forming the candidate.
Therefore the correct conditional probability is

\[
\boxed{\Pr(b\mid\text{previous reports})
=\frac{\mathcal N_b}{2\mathcal N}.}
\]

As a consistency check, \(\mathcal N_0+\mathcal N_1=2\mathcal N\).
Sample using these probabilities, keep only the selected candidate list,
and use its norm \(\mathcal N_b\) as the new representation's normalizer.
Repeat in a,b,c,d,e order.

Removing a vertex label can allow formerly orthogonal records to overlap.
This is why the candidate norm must include the cross terms. There is no
independent measurement sample for each component.

After all five reports b, the physical unnormalized conditional state is

\[
|\chi_b\rangle
=\frac1{32}\sum_t(-1)^{b\cdot t}|p(t)\rangle V_t|\psi\rangle.
\]

The recorded parity is
\(r=b_a+b_b+b_c+b_d+b_e\pmod2\). If r=1, record `swap_plus=False`, reject
the attempt, and stop. Sampling includes these rejected outcomes.

### Exact probability check for this stage

The full SWAP sends L_0=H x K to K x H. Their intersection is H x H:

\[
\dim(L_0\cap P_{11111}L_0)=18,
\qquad
\langle\psi|U|\psi\rangle=\frac{2^{18}}{2^{19}}=\frac12.
\]

The connected graph gives the same gauge word only for t and its complement.
Taking the norm of the displayed conditional state therefore gives

\[
\boxed{
\Pr(b)=\frac{1+(-1)^r/2}{32}
=\begin{cases}3/64,&r=0,\\1/64,&r=1.\end{cases}
}
\]

Thus the first four vertex bits are independent fair bits. Given those
four, the fifth completes even parity with probability 3/4. This is a
check on the norm-based sampler; the sampler can compute the probabilities
without inserting these answers by hand. The total positive-SWAP
probability is 16(3/64)=3/4.

## 8. Apply the recorded vertex-to-gauge feedforward

For an accepted record b, execute the actual gates

\[
F_b=Z_{A_7}^{b_b}Z_{A_{11}}^{b_c}Z_{A_3}^{b_d}Z_{A_0}^{b_e}.
\]

A Z on gauge coordinate q acts on a component by

\[
Z_{A_q}|\gamma_j\rangle=(-1)^{\gamma_j[q]}|\gamma_j\rangle.
\]

Consequently, each gate that is selected by b multiplies the record's
integer coefficient by +1 or -1. It changes no affine space or norm.

For the current circuit the combined coefficient is

\[
(-1)^{b\cdot t}
(-1)^{b_b p(t)_7+b_c p(t)_{11}+b_d p(t)_3+b_e p(t)_0}
=(-1)^{r t_a}=1.
\]

Thus all retained coefficients become +1. For example, b=(0,1,0,1,0)
selects Z on A_7 and A_3 and removes the sign \((-1)^{t_b+t_d}\).

The simulator should apply these sign updates even though the last
identity predicts their result. This directly exercises the implemented
feedforward rule and exposes an incorrect edge index.

## 9. Sample all twenty gauge-Z measurements

For each gauge coordinate q, in increasing order, form candidate lists for
outcomes s=0,1 by retaining exactly the records with gauge value s at
physical label q. Remove that coordinate from the surviving gauge labels.
Compute their norms
\(\mathcal N_s\).

There is no omitted Hadamard factor in a Z-basis projection. Therefore

\[
\boxed{\Pr(m_q=s\mid\text{previous reports})
=\frac{\mathcal N_s}{\mathcal N},
\qquad \mathcal N_0+\mathcal N_1=\mathcal N.}
\]

Sample the bit, keep the selected list, update the normalizer, and append
the bit to m. A gauge outcome can be deterministic. The twenty bits must
not be sampled as independent fair coins.

After a complete word m has been measured, only the vertex assignments
with p(t)=m survive. The graph is connected, so any nonempty surviving
list has exactly two original labels, t and
\(\bar t=t+(1,1,1,1,1)\). Thus at most two coherent components remain.

For this noiseless circuit the sixteen possible complete gauge words
have equal conditional probability 1/16. This follows because each pair
has the same norm:

\[
\|\,|L_t\rangle+|L_{\bar t}\rangle\,\|^2
=2\,2^{19}+2\,2^{18}=3\,2^{19}.
\]

## 10. Decode the measured gauge word and execute the correcting SWAPs

Apply the same classical decoding as the Guppy circuit:

\[
\widehat t_a=0,\qquad
(\widehat t_b,\widehat t_c,\widehat t_d,\widehat t_e)
=(m_7,m_{11},m_3,m_0).
\]

For every q whose block has \(\widehat t_v=1\), exchange data coordinates
B_q and C_q in the offsets and generators of **both** components.
This is the physical feedforward SWAP correction.

As a mathematical check, the two resulting data spaces are L_0 and
\(UL_0:=P_{11111}L_0\), because

\[
P_{\widehat t}P_tL_0=L_0,\qquad
P_{\widehat t}P_{\bar t}L_0=UL_0,
\]

when t is the representative with t_a=0. Reversing their ordering makes
no difference to their coherent sum. The normalized BC state is

\[
\boxed{
|\Psi_+\rangle
=\frac{|L_0\rangle+|UL_0\rangle}{\sqrt{3\,2^{19}}}
=\frac{|\psi\rangle+U|\psi\rangle}{\sqrt3}.
}
\]

The normalizer is not \(\sqrt{2\,2^{19}}\), because the components overlap.

## 11. Sample the twenty physical B-Z measurements

At this stage we have at most two affine data spaces with coefficients.
For the next B coordinate q and candidate outcome s, restrict each space:

\[
\mathcal A_j^{(s)}=\{x\in\mathcal A_j:x_B[q]=s\}.
\]

This set is empty or affine. Keep each nonempty restricted component
with its existing coefficient; do not normalize components separately.
Compute the candidate norms and sample with

\[
\boxed{\Pr(n_q=s\mid\text{all previous reports})
=\frac{\mathcal N_s}{\mathcal N}.}
\]

### How to restrict an affine space, explicitly

Suppose \(\mathcal A=o+\operatorname{span}\{g_1,\ldots,g_r\}\), and the
coordinate being measured is k in the forty-bit data vector.

1. If every generator has g_i[k]=0, this coordinate is fixed to o[k].
   Return the space unchanged for s=o[k], or the empty space otherwise.
2. Otherwise choose one generator h with h[k]=1.
3. Set the new offset to \(o'=o+(s+o[k])h\).
4. For every other generator g_i, replace it by \(g_i+g_i[k]h\).
5. Delete h from the generator list.

All new generators have zero at coordinate k, and o'[k]=s. The surviving
space has dimension r-1. These are binary row operations only.

After all twenty bits n are sampled, compute the same logical parity as
the circuit:

\[
\ell(n)=n_0+n_3+n_6+n_7+n_{18}+n_{19}\pmod2.
\]

Reject if \(\ell(n)=1\). Otherwise return the coherent C state, deleting
the now-fixed B coordinates from its affine descriptions.

### Exact physical-word probabilities and the retained state

These formulas provide independent checks on the sequential sampler.
Let \(z_0=e_0+e_3+e_6+e_7+e_{18}+e_{19}\). Then \(z_0\cdot h=0\) for
every h in H and \(z_0\cdot\xi=1\). Hence \(\ell(n)=0\) on H and
\(\ell(n)=1\) on the coset H+xi. Given the normalized state in Section 10,

\[
\Pr(n\mid\text{positive SWAP})=
\begin{cases}
5/3072,&n\in H,\\
1/3072,&n\in H+\xi,\\
0,&n\notin K.
\end{cases}
\]

For n in H, the two C components are respectively K and H. Their sum is

\[
|K\rangle+|H\rangle
=2\sum_{h\in H}|h\rangle+\sum_{h\in H}|h+\xi\rangle.
\]

Its squared norm is \(5\,2^9\), so every accepted physical B report leaves

\[
\boxed{
|\mathrm{out}\rangle_C
=\frac{2\sum_{h\in H}|h\rangle+\sum_{h\in H}|h+\xi\rangle}
{\sqrt{5\,2^9}}
=\frac{2|\overline{00}\rangle+|\overline{10}\rangle}{\sqrt5}
=|\overline{M0}\rangle.
}
\]

Here \(|M\rangle=(2|0\rangle+|1\rangle)/\sqrt5\), and the second logical
qubit is zero.

There are 512 words in H. Thus the conditional extraction success is
\(512(5/3072)=5/6\); the total attempt success is \((3/4)(5/6)=5/8\).

## 12. Exactly where randomness is used

The following table separates coherent enumeration from measurement
sampling. A “component count” refers to a representation of one current
conditional quantum state, not to distinct sampled experimental attempts.

| Stage | Classical work | Random sample? | Components |
|---|---|---|---|
| Encoded sources | Binary generators for H x K | No | 1 |
| Five vertex H gates and graph CNOTs | Retain both values of each control | No | Up to 32 |
| Twenty Fredkins | Update data coordinates in each component | No | 32 |
| Vertex X readout | Signed candidate lists and coherent norms | Yes, five bits | At most 32 |
| Gauge-Z feedforward | Change integer coefficient signs | No | At most 32 |
| Gauge Z readout | Filter candidates and recompute norms | Yes, twenty bits | At most 2 after complete readout |
| Correcting SWAPs | Permute data coordinates | No | At most 2 |
| B Z readout | Affine restrictions and coherent norms | Yes, twenty bits | At most 2 |
| Accepted C output | Retain a compressed coherent sum | No C measurement | At most 2 |

For an exact rational probability A/B, draw an integer R uniformly from
\(\{0,\ldots,B-1\}\) and select the outcome when R<A. Such a uniform
integer can be generated with random bits and rejection. No floating-point
probability approximation is necessary.

“Exact” here means no state truncation and exact Born probabilities. A
finite set of simulated shots still has ordinary sampling fluctuations.
Exact acceptance probabilities can also be calculated algebraically, as
above, without estimating them from shot counts.

## 13. Why this is efficient for this circuit

### 13.1. There are never more than 32 coherent components

Only the five vertex H gates require introducing computational-basis
components. They produce \(2^5=32\) records. The graph CNOTs and Fredkins
update those records without splitting them. Vertex-X projection changes
signs, gauge-Z projection filters records, and B-Z projection replaces
each affine space by at most one affine space. None increases the count.

This is an explicit construction and an upper bound, not an assumption
that a numerical compression routine will find a small decomposition.
It also shows why we should exploit the five shared controls rather than
expand twenty Fredkins independently.

### 13.2. Storage is polynomial in the number of physical qubits

For N physical qubits, an affine component needs at most N independent
N-bit generators, an N-bit offset, labels, and an integer coefficient.
With chi components, this takes \(O(\chi N^2)\) binary storage, apart from
ordinary data-structure overhead. Here N=65, chi<=32, and the data-space
generators are actually only nineteen forty-bit vectors before readout.

For comparison, a dense complex128 wavefunction on 65 qubits needs
\(16\,2^{65}=2^{69}\) bytes, or 512 EiB. We never allocate it, enumerate
its amplitudes, or expand an entire density matrix in the Pauli basis.

### 13.3. Each probability is obtained by small Gaussian eliminations

An affine-intersection count costs at most \(O(N^3)\) elementary binary
operations with a straightforward implementation. One norm requires at
most \(\chi^2\) such counts, giving the conservative bound

\[
O(\chi^2N^3)
\]

per norm. Two candidate norms give each measurement probability. There
are at most M=45 physical measurements, so measurement processing has
the conservative per-attempt bound

\[
\boxed{O(M\chi^2N^3),\qquad N=65,\quad M\le45,\quad\chi\le32.}
\]

Integer counts have O(N) bits for this fixed-size component list. Their
arithmetic is polynomial as well. Sampling does not require building
the tree of all possible measurement records.

The actual overlap work is smaller: before gauge readout, unequal gauge
words make most pairs orthogonal. After complete vertex readout there
are sixteen gauge-label groups of two components, so at most 64 ordered
pairs contribute. After gauge readout there are at most four ordered
pairs. Identical spaces and cached intersections can reduce this further.

A CNOT or coordinate SWAP updates generator columns in polynomial time.
For L such gate updates, a coarse additional bound is \(O(L\chi N^2)\).
These bounds justify feasibility; they are not measured wall-clock times.

### 13.4. Rejection has constant expected overhead

One attempt succeeds with probability 5/8. Independent repetitions need
an expected \(1/(5/8)=8/5\) attempts per accepted resource. Neither the
five-vertex enumeration nor the postselection imposes an exponential
cost in the forty data-qubit count for this circuit family with five
fixed coherent controls. If the number c of independent coherent controls
grows, the analogous bound is \(\chi\le2^c\), exponential in c.

## 14. Concrete implementation and validation sequence

The following would be the order of work in a subsequent implementation.

1. **Binary linear algebra.** Implement independent row bases, affine
   intersection counts, coordinate restrictions, CNOT column updates,
   and coordinate swaps. Check these against explicit sets on a few bits.
2. **Coherent norm and measurement rules.** Implement the integer norm
   formula, the vertex-X candidate rule with its factor 2, and the Z
   filtering/restriction rule. Test interference and zero-probability
   outcomes before adding circuit-specific logic.
3. **Consume the physical schedule.** Reuse the current Guppy file's
   source schedules, edge order, contiguous block controllers, feedforward
   edges, and final logical parity support. Avoid the different controller
   assignment in older graph-audit JSON files. Verify individual gates or
   their exact semantic decomposition, rather than inserting the expected
   logical output state.
4. **One physical attempt.** Execute the stages in this note. Emit b,
   `swap_plus`, m, the decoded swap offsets, n, and `accepted`, with later
   records absent after an early rejection. Preserve the compressed C
   output on success.
5. **Small dense comparison.** Compare exact branch probabilities and
   conditional output amplitudes with a statevector simulation on the
   existing smaller nineteen-qubit test geometry. Include nonzero
   feedforward records and verify their signs before gauge readout.
6. **Full physical circuit checks.** Compute, rather than assume, the
   source ranks 9 and 10, data rank 19, global-SWAP intersection rank 18,
   all 32 vertex-word probabilities, and all sixteen possible gauge words
   for every accepted vertex word. Check the physical B-word formula and
   the retained C state for every allowed B word. Then generate shots.

These checks separate a physical-circuit simulator from a sampler that
merely hard-codes the known probabilities 3/4 and 5/6.

## 15. Role of PerOpQPrivate and limits of this proposal

The first simulator proposed here would use binary affine spaces and
coherent integer coefficients. It would not need PerOpQ's sparse Pauli
operator propagation to evolve the state.

PerOpQ can provide an independent route for selected observables later.
Its existing sparse-operator representation is different from the
affine-ket representation above. In particular, the sum of squared
coefficients is not the state norm when the corresponding component
kets overlap. A probability calculation must retain their Gram matrix,
which here is given explicitly by affine intersection counts.

For the retained output, useful exact checks include original code-space
membership and

\[
\langle\overline X_0\rangle=4/5,\quad
\langle\overline Z_0\rangle=3/5,\quad
\langle\overline Y_0\rangle=0,\quad
\langle\overline Z_1\rangle=1.
\]

Here the logical operators on C are
\(\overline X_0=X(\xi)\), \(\overline Z_0=Z(z_0)\),
\(\overline Z_1=Z(\xi)\), and
\(\overline Y_0=i\overline X_0\overline Z_0\).

These expectations can also be computed without a wavefunction. Write
the retained C representation as \(\sum_j w_j|\mathcal A_j\rangle\), with
normalizer \(\mathcal N_C\); all vectors now have twenty coordinates.
For any binary vectors s and z,

\[
\langle X(s)\rangle
=\frac1{\mathcal N_C}\sum_{i,j}w_iw_j
|\mathcal A_i\cap(\mathcal A_j+s)|,
\]

\[
\langle Z(z)\rangle
=\frac1{\mathcal N_C}\sum_{i,j}w_iw_j
\left(
|\mathcal A_i\cap\mathcal A_j\cap\{x:z\cdot x=0\}|
-|\mathcal A_i\cap\mathcal A_j\cap\{x:z\cdot x=1\}|
\right).
\]

Translation by s only changes an affine offset. The extra parity condition
is one more binary linear equation. Thus these diagnostics use the same
intersection-counting machinery. Check each X(r_s) and Z(r_s) for code
membership and use xi and z_0 for the logical expectations. The output
amplitudes are real, so the expectation of the purely imaginary logical
Y operator is zero.

These are computed properties of the compressed output, not additional
measurements inserted into the physical procedure.

The simple affine representation is justified by the actual noiseless
gates: source H/CNOT preparation, computationally controlled SWAPs,
vertex-X readout, gauge-Z phases, ordinary SWAPs, and Z readout. Additional
phase gates, arbitrary rotations, noisy channels, or another protocol
need a new representation analysis. A more general coherent stabilizer
simulator may then be appropriate; the present 32-component bound must
not be assumed for an arbitrary modified circuit.

General polynomial-time stabilizer processing and overlap calculations
are discussed by [Aaronson and Gottesman, *Improved Simulation of
Stabilizer Circuits*](https://arxiv.org/abs/quant-ph/0406196). Coherent sums
of stabilizer states are developed more generally by [Bravyi et al.,
*Simulation of quantum circuits by low-rank stabilizer
decompositions*](https://arxiv.org/abs/1808.00128). The affine-space update
rules and the five-control resource bound in this note are derived here
for the particular circuit being simulated.
