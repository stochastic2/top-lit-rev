# C4-Helix exact simulation plan — V2: explicit sparse wavefunctions

This is a proposal for implementing an exact simulator for
[`src/c4_helix_noiseless.py`](../src/c4_helix_noiseless.py). It supersedes
the representation choice in the
[first simulation plan](c4-helix-exact-simulation-plan.md): use explicit
computational-basis strings and their weights, rather than affine spaces.
The physical procedure remains the noiseless
[V2 integrated procedure](full_procedure_integrated_v2.md).

The intended implementation will simulate one attempt at a time, write its
result, and release its intermediate state. To reduce the memory within an
attempt, it will sample the gauge-Z measurement before simulating the
Fredkins and vertex-X measurements. Section 3 proves that this reordering
preserves the required probabilities and conditional output states.

No simulator is implemented by this note. No physical stabilizer checks,
error correction, or additional physical measurements are proposed.

## 1. Symbols and physical circuit

| Symbol | Meaning |
|---|---|
| V | Five physical vertices a,b,c,d,e, in that order |
| A | Twenty gauge qubits A_0,...,A_19 |
| B, C | Twenty data qubits in each register |
| \(t\) | A five-bit computational-basis vertex string |
| \(b\) | Five actual vertex-X outcomes; bit 1 means eigenvalue -1 |
| \(m\) | Twenty gauge-Z outcomes |
| \(n\) | Twenty B-Z outcomes |
| \(\psi\) | The normalized encoded input on BC |
| \(T_v\) | SWAPs of all four corresponding B/C pairs in block v |
| \(V_t\) | Product of the T_v for which t_v=1 |
| U | SWAP of the complete B and C registers |

All binary sums and dot products in exponents are modulo two. Physical
qubit labels begin at zero. With vertex numerical indices a=0,...,e=4,

\[
J_v=\{4v,4v+1,4v+2,4v+3\},\qquad
T_v=\prod_{q\in J_v}\mathrm{SWAP}(B_q,C_q),\qquad
V_t=\prod_vT_v^{t_v},\qquad U=\prod_vT_v.
\]

The input is

\[
|\psi\rangle=|\overline{00}\rangle_B|\overline{+0}\rangle_C.
\]

For edge q with endpoints u_q,v_q, define

\[
p(t)_q=t_{u_q}+t_{v_q}\pmod2.
\]

The source file supplies the exact `EDGES`, `CONTROLLERS`, `TREE_EDGES`,
`CHECK_SUPPORTS`, `LOGICAL_X0`, and `LOGICAL_Z0` constants. Reuse these;
do not use the different controller assignment in older graph JSON files.

The physical circuit order is:

1. Prepare B, C, and the vertex/gauge graph resource.
2. Apply twenty vertex-controlled data SWAPs.
3. Measure V in X; reject odd outcome parity.
4. Apply the measurement-dependent gauge-Z gates.
5. Measure A in Z.
6. Apply the gauge-dependent ordinary data SWAPs.
7. Measure B in Z; retain C only for logical parity zero.

## 2. What “32 components” means for memory

The B input has 512 nonzero computational-basis amplitudes. The C input
has 1024. Their tensor product therefore has

\[
D=512\times1024=2^{19}=524{,}288
\]

nonzero amplitudes. There are 32 coherent vertex strings before readout.
Keeping the whole original-order wavefunction can therefore require

\[
32D=2^{24}=16{,}777{,}216
\]

entries. Running shots sequentially avoids keeping many such states at
once, but does not itself remove this per-shot peak.

The method below conditions on one gauge measurement result first. This
leaves exactly two coherent vertex strings, so its sparse state needs
at most

\[
\boxed{2D=2^{20}=1{,}048{,}576\text{ nonzero entries}.}
\]

Both strings must remain in the wavefunction. Sampling one of them would
remove the interference responsible for the magic preparation.

## 3. Why sampling the gauge word early is exact

The normalized graph resource is

\[
|\Gamma\rangle_{VA}
=\frac1{\sqrt{32}}\sum_{t\in\{0,1\}^5}|t\rangle_V|p(t)\rangle_A.
\]

Write \(\mathcal E\) for the twenty-Fredkin enrichment unitary on VBC,
and define the gauge projector

\[
Q_m=|m\rangle\langle m|_A.
\]

This projector commutes with enrichment and with every vertex operation,
because those act on VBC. For a fixed vertex outcome b, the gauge
feedforward is

\[
F_b=Z_{A_7}^{b_b}Z_{A_{11}}^{b_c}Z_{A_3}^{b_d}Z_{A_0}^{b_e}.
\]

It also commutes with Q_m: both are diagonal in the gauge computational
basis. Let \(\langle b_X|\) denote all five vertex-X measurement bras.
For a retained vertex outcome, the physical conditional BC vector is

\[
|\zeta_{b,m}\rangle
=\langle m|_A F_b\langle b_X|_V\mathcal E
\bigl(|\Gamma\rangle_{VA}|\psi\rangle_{BC}\bigr).
\]

Define the normalized early-conditioned graph state by

\[
|\Gamma_m\rangle=\frac{Q_m|\Gamma\rangle}{\sqrt{\Pr(m)}}.
\]

Commuting Q_m to the beginning gives exactly the same vector as

\[
|\zeta_{b,m}\rangle
=\sqrt{\Pr(m)}\,
\langle m|_A F_b\langle b_X|_V\mathcal E
\bigl(|\Gamma_m\rangle_{VA}|\psi\rangle_{BC}\bigr).
\]

Thus sampling m first and then sampling b from the conditional quantum
state gives the same joint probability \(\|\zeta_{b,m}\|^2\) and the same
conditional BC state as the original order.

The graph is connected. Its map t -> p(t) has sixteen images, with
exactly two preimages per image: t and its bitwise complement
\(\bar t=t+(1,1,1,1,1)\). Consequently,

\[
\Pr(m)=\frac2{32}=\frac1{16},\qquad
|\Gamma_m\rangle
=\frac{|t\rangle+|\bar t\rangle}{\sqrt2}\otimes|m\rangle.
\]

In the original circuit an odd vertex parity stops the attempt before
gauge readout. For such attempts the early sampled m is an internal
simulation variable: discard it from the public measurement record.
It must not be presented as an actually performed gauge measurement.

This reordering uses the specific noiseless circuit. Extra interactions
with A or intervening noncommuting checks require a new argument.

## 4. Store the wavefunction using strings and integer weights

Use a small state container with these fields:

```text
labels:  ordered tuple of names of the remaining quantum coordinates
weights: dictionary from a 0/1 string to a nonzero Python integer
```

For example, after early gauge sampling the coordinate order is

```text
(V_a,...,V_e, B_0,...,B_19, C_0,...,C_19).
```

A key is then a forty-five-character string. The known gauge word m is
stored once as classical metadata, rather than appended to every key.
Removing a measured vertex or B qubit removes its character from each
key and its name from `labels`.

For a dictionary w, its normalized physical state is defined to be

\[
\boxed{
|\Psi_w\rangle=\frac1{\sqrt{N(w)}}\sum_x w(x)|x\rangle,
\qquad N(w)=\sum_x w(x)^2.
}
\]

Only real integer weights are needed for this circuit. Source Hadamards
introduce common square-root factors, which this normalized definition
absorbs. Vertex-X projection adds or subtracts integer weights. The
remaining gates permute strings or change signs.

Two rules are essential:

- Whenever multiple contributions reach the same output key, **add their
  weights**. Do not overwrite a previous contribution.
- Delete a key when its accumulated weight is zero. This is exact
  cancellation, not an amplitude-truncation threshold.

Do not normalize individual entries or branches separately. Their
relative weights carry the quantum interference.

Python strings prioritize readability. Python integers keep counts and
probability arithmetic exact. NumPy is optional for small dense comparison
tests; no general stabilizer library or affine-space backend is required.

## 5. Prepare the explicit B and C wavefunctions

Reuse `preparation_schedule` from the Guppy source. Execute its H/CNOT
schedule with a simple sparse-state backend, independently on B and C.
Each source starts from the single key consisting of twenty zeros with
weight one.

For a source Hadamard on coordinate q, process each key x with weight c:

1. Let z be the old bit x[q].
2. Add c to the output key with coordinate q set to zero.
3. Add \((-1)^z c\) to the output key with coordinate q set to one.

The omitted common factor is \(1/\sqrt2\). If a is the old weight vector,
the new integer vector is \(a'=\sqrt2 H_q a\), and hence
\(a'/\sqrt{N(a')}=H_q a/\sqrt{N(a)}\). This is the correct normalized
unitary state.

For a CNOT c -> q, toggle target character q only when control character c
is one. This is a permutation of keys and changes no weight or norm.

Check the resulting explicit dictionaries:

```text
B source: 512 keys, each with weight +1
C source: 1024 keys, each with weight +1
```

Their tensor product is constructed by concatenating every B key with
every C key and multiplying the two weights. It has D=524,288 entries,
all with weight +1.

For validation, define the explicit sets

\[
\mathcal B=\{x:w_B(x)\ne0\},\qquad
\mathcal C=\{x:w_C(x)\ne0\}.
\]

If xi is the twenty-bit string supported on `LOGICAL_X0`, the sources must
satisfy \(\mathcal C=\mathcal B\cup(\mathcal B+\xi)\), a disjoint union.
Here addition toggles exactly the positions where xi has a one. This
identity is a check; execute the source gates to generate the states.

## 6. Build the small gauge-outcome table and sample m

Enumerate only the 32 five-character vertex strings. For each string t,
start a twenty-element gauge list at zero. Follow the graph CNOTs in
`EDGES` order, adding the appropriate endpoint bit modulo two to each
gauge coordinate. Record the resulting word p(t).

Collect a table of the form

```text
gauge word m -> list of vertex strings t with p(t)=m
```

Verify that it has sixteen entries and that each list contains two
complementary strings. The probability of a table entry is its list length
divided by 32. Sample one entry; for the verified graph they are uniform.

Keep both preimages. For each BC key x, create the two keys

```text
t + x       with weight +1
t_bar + x   with weight +1
```

This dictionary has 2D entries and norm N=2D. Together with the fixed gauge
word it represents

\[
\frac{|t\rangle+|\bar t\rangle}{\sqrt2}
\otimes|m\rangle_A\otimes|\psi\rangle_{BC}.
\]

The gauge table has only sixteen entries. It does not contain data
wavefunctions and does not require a 65-qubit state allocation.

## 7. Execute all twenty Fredkins

For each q=0,...,19, obtain its controller from `CONTROLLERS[q]`.
For every sparse key:

1. Read that vertex coordinate.
2. If it is zero, leave the key unchanged.
3. If it is one, exchange characters B_q and C_q.

Carry its integer weight unchanged. Build one output dictionary and
release the previous dictionary after the gate.

The state is now

\[
\boxed{
|\Omega_m\rangle
=\frac{|t\rangle V_t|\psi\rangle
       +|\bar t\rangle V_{\bar t}|\psi\rangle}{\sqrt2},
}
\]

with A fixed to m. The number of sparse entries remains 2D: distinct
vertex labels prevent collisions between the two terms at this stage.

The physical controller is the contiguous block index q//4. It is not
necessarily an endpoint of graph edge q. Test the direct Fredkin mapping
against the source's CNOT/Toffoli/CNOT decomposition on all eight inputs.

## 8. Sample each vertex-X outcome without expanding its Hadamard

Process vertices a,b,c,d,e in that order. Let y be a key for all remaining
coordinates after removing the next vertex. Denote the current integer
weights of its two extensions by

\[
a_0(y)=w(0,y),\qquad a_1(y)=w(1,y),
\]

with missing keys interpreted as weight zero. The vertex coordinate can
occur anywhere in the key; this notation puts it first only for clarity.

For candidate outcome b=0 or 1, define

\[
u_b(y)=a_0(y)+(-1)^b a_1(y),\qquad
N_b=\sum_y u_b(y)^2.
\]

The physical measurement bra contributes a common factor
\(1/\sqrt2\). Therefore

\[
\boxed{\Pr(b\mid\text{current state})=\frac{N_b}{2N(w)}.}
\]

Check \(N_0+N_1=2N(w)\). Sample b, retain the dictionary u_b after removing
zero weights, remove the vertex label, and use its norm N_b for the next
step. This normalized dictionary is the correct conditional quantum state.

### Two-pass implementation to avoid allocating both candidates

In the first pass, visit each pair of extensions exactly once and compute
N_0 and N_1. Then sample one outcome. In the second pass, build only the
selected dictionary. The mathematical steps are:

```text
N0 = N1 = 0
for each distinct pair (a0(y), a1(y)):
    N0 += (a0(y) + a1(y))**2
    N1 += (a0(y) - a1(y))**2

b = sample outcome with probabilities N0/(2*N), N1/(2*N)

for each distinct pair (a0(y), a1(y)):
    value = a0(y) + (-1)**b * a1(y)
    if value != 0:
        selected[y] = value
```

A pair iterator need not build a second large set of y keys. When visiting
an existing full key, skip it if its vertex bit is one and its zero-bit
partner exists. Otherwise visit its pair, looking up both weights in the
current dictionary. Every pair is then processed once, including pairs
with a missing zero-bit entry.

This fuses the source's final H and Z measurement into one exact X
projection. It avoids constructing an expanded post-H wavefunction.
Different vertices' H gates and measurements commute, so doing this one
vertex at a time reproduces the source's joint measurement statistics.

After all five outcomes, compute

\[
r=b_a+b_b+b_c+b_d+b_e\pmod2.
\]

For r=1, reject the attempt and stop. Record the vertex outcomes, but do
not expose the internal early gauge sample as an actual gauge readout.

For checking the sampler, the expected probabilities for every fixed m are

\[
\Pr(b\mid m)=
\begin{cases}3/64,&r=0,\\1/64,&r=1.\end{cases}
\]

Compute these probabilities from the weights during validation, rather
than using this formula to bypass vertex measurements in the simulator.

To derive the check, use
\(\langle\psi|U|\psi\rangle
=|\langle\overline{00}|\overline{+0}\rangle|^2=1/2\).
The five vertex-X bras contribute \(2^{-5/2}\), and the initial pair has
factor \(2^{-1/2}\). Thus the conditional data vector before gauge-Z
feedforward is

\[
\frac{(-1)^{b\cdot t}}8\,
V_t\bigl(I+(-1)^rU\bigr)|\psi\rangle.
\]

Its squared norm is \((2+(-1)^r)/64\), giving the displayed probabilities.

## 9. Execute gauge-Z feedforward on the fixed gauge state

The sampled m is a computational-basis state, so the original selected
Z gates have the action

\[
F_b|m\rangle=(-1)^\theta|m\rangle,\qquad
\theta=b_bm_7+b_cm_{11}+b_dm_3+b_em_0\pmod2.
\]

Multiply every current sparse weight by \((-1)^\theta\). This is a global
phase on the current trajectory, because the gauge register has already
been measured. Its explicit update records the action of the required
physical feedforward and permits phase-sensitive comparison tests.

On accepted vertex outcomes, the two original coherent terms acquired
the same vertex-measurement sign. The displayed gauge correction removes
it. The simulator should perform the actual sign calculation from b and m,
not replace it by this predicted result.

At this point expose m in the public `gauge_z` record. There is no second
gauge sample and no product of twenty independent fair coins.

## 10. Execute the ordinary SWAP feedforward

Use the source's root convention:

\[
\widehat t_a=0,\qquad
(\widehat t_b,\widehat t_c,\widehat t_d,\widehat t_e)
=(m_7,m_{11},m_3,m_0).
\]

For each q in a block whose offset is one, exchange characters B_q and C_q
in each sparse key. This is a permutation update. Store the five offsets
in the shot record.

As an independent state check, after correction the normalized BC state is

\[
|\Psi_+\rangle=\frac{|\psi\rangle+U|\psi\rangle}{\sqrt3}.
\]

The normalization follows from \(\langle\psi|U|\psi\rangle=1/2\).
The actual dictionary must be produced by the Fredkins, measurements, and
correcting SWAPs; do not directly initialize this expected final state.

For this circuit, the resulting dictionary has 786,432 distinct keys:

- 262,144 keys occur in both coherent terms and have weight 2.
- 524,288 keys occur in only one term and have weight 1.

Consequently its norm is

\[
N=262{,}144\times 2^2+524{,}288\times1^2
=1{,}572{,}864=3\,2^{19}.
\]

These counts make a useful test that amplitudes were added at colliding
keys rather than overwritten.

## 11. Sample the twenty B-Z outcomes and retain C

For B_q, partition the current keys by their value s=0 or 1 and compute

\[
N_s=\sum_{x:x[B_q]=s}w(x)^2.
\]

The exact probabilities are

\[
\boxed{\Pr(n_q=s\mid\text{previous reports})=\frac{N_s}{N(w)},
\qquad N_0+N_1=N(w).}
\]

Sample the outcome, retain that partition, remove its measured character
and coordinate label, and proceed to B_{q+1}. The retained weights require
no per-entry normalization. Append the sampled bit to n.

After all twenty measurements compute

\[
\ell(n)=n_0+n_3+n_6+n_7+n_{18}+n_{19}\pmod2.
\]

Reject if ell=1. Otherwise the remaining dictionary has twenty-character
C keys and exactly 1024 entries. Its weights are:

```text
512 keys with weight 2
512 keys with weight 1
normalization N_C = 512*4 + 512 = 2560
```

This represents

\[
|\mathrm{out}\rangle_C
=\frac{2\sum_{h\in\mathcal B}|h\rangle
       +\sum_{h\in\mathcal B}|h+\xi\rangle}{\sqrt{2560}}
=\frac{2|\overline{00}\rangle+|\overline{10}\rangle}{\sqrt5}
=|\overline{M0}\rangle,
\]

where \(|M\rangle=(2|0\rangle+|1\rangle)/\sqrt5\). The phase convention
above gives positive weights; a common overall minus sign would describe
the same physical state.

Every allowed physical B word has the following probability, conditioned
on positive vertex parity and the sampled gauge word:

\[
\Pr(n\mid r=0,m)=
\begin{cases}
5/3072,&n\in\mathcal B,\\
1/3072,&n\in\mathcal B+\xi,\\
0,&n\notin\mathcal C.
\end{cases}
\]

Thus the B selection succeeds with conditional probability 5/6. The
overall probability of returning a C state is (3/4)(5/6)=5/8.

## 12. Exact sampling and saving one shot at a time

All probabilities above are ratios of nonnegative Python integers.
For probability A/B, draw a uniform integer R from 0,...,B-1 and choose
the event when R<A. A seeded `random.Random` instance with `randrange`
can supply these draws. No floating-point normalization is needed inside
the simulator.

For X measurement, use B=2N(w) and A=N_1 to sample outcome one. For Z
measurement, use B=N(w) and A=N_1. Impossible outcomes have numerator zero
and are never selected.

The implementation should expose an iterator yielding one shot result.
A caller writes each result immediately, then releases its state before
requesting the next shot. It must not accumulate a list of intermediate
wavefunctions.

Suggested public fields are:

```text
shot_index, accepted, vertex_x, swap_plus,
gauge_z, swap_offsets, b_z, b_logical_z0,
c_state_reference
```

Later fields are absent or null if the physical attempt stops earlier.
An optional debug field can hold the internal early gauge sample, clearly
distinguished from the physical record.

For an accepted C state, a simple JSON representation can store its
ordered coordinate labels, twenty-character keys, integer weights, and
the integer normalization 2560. Its physical amplitudes are w/sqrt(2560).
Keeping weights and the normalizer preserves exactness on disk. Converting
to floating-point amplitudes should be an explicit presentation/export
operation.

No C measurement is needed. If all accepted states are found equal up to
global phase, the caller may save one reference state and point later
accepted records to it instead of duplicating identical output files.

## 13. Proposed code organization

The first implementation should favor ordinary Python and explicit names.
Keep bit packing, Numba, Rust, and affine-space routines out of the initial
sparse backend. Proposed modules are:

| Module | Responsibility |
|---|---|
| `sparse_wavefunction.py` | State container, norm, character permutations, H, direct X/Z measurement, integer sampling |
| `simulate_c4_helix_sparse.py` | Source schedules, gauge table, early conditioning, all circuit stages, one-shot iterator, CLI and output writing |
| `test_sparse_wavefunction.py` | Small exact gate, interference, probability, and normalization tests |
| `test_c4_helix_sparse.py` | Small dense comparisons and full-circuit checks |

Suggested simulator entry points are:

```text
prepare_source(schedule, labels) -> SparseState
build_gauge_preimages(edges) -> table
sample_gauge(table, rng) -> gauge_word, two_vertex_strings
simulate_attempt(rng) -> ShotResult
iter_attempts(number_of_attempts, seed) -> iterator of ShotResult
write_result(result, output_directory)
```

These are interfaces to implement later, not currently available commands.
Reuse the current source file's constants and source schedules without
changing its Guppy implementation.

The sparse backend can compute observables directly if requested. For
example, on a normalized C dictionary with squared norm N_C,

\[
\langle X(s)\rangle=\frac1{N_C}\sum_x w(x)w(x+s),\qquad
\langle Z(z)\rangle=\frac1{N_C}\sum_x(-1)^{z\cdot x}w(x)^2.
\]

Here s and z are twenty-bit support strings, and a missing w(x+s) is zero.
These formulas are dictionary lookups and sign sums, not extra physical
measurements. In particular use `LOGICAL_X0`, `LOGICAL_Z0`, and
`LOGICAL_Z1` to check the output.

## 14. Memory and cost: what is improved and what remains

The theoretical bound is at most 2D live basis entries per state, rather
than 32D. Permutation gates preserve the number of entries; a selected
direct X projection cannot increase it, and Z projection reduces it.
The source states are prepared separately before forming their tensor
product, so their source H gates do not exceed this bound either.

An out-of-place update temporarily retains old and new dictionaries.
Therefore peak allocated entries can approach 4D, even though each state
has at most 2D entries. Container overhead, temporary strings, and the
language runtime contribute additional memory. No specific RAM usage has
been benchmarked yet.

To keep memory bounded:

1. Build only one selected X-measurement output, using the two-pass method.
2. Avoid allocating a separate set of all projected keys.
3. Release an old dictionary as soon as its replacement is ready.
4. Store fixed m once, not in every basis key.
5. Run one attempt at a time and stream results.
6. Reuse the small B/C source dictionaries as read-only data if beneficial;
   do not cache every gauge-conditioned or enriched million-entry state.

Every full sparse update scans at most 2D entries. With K=45 unmeasured
coordinates initially, straightforward string editing costs O(K) per
entry. For L updates, a conservative bound is O(L D K), with ordinary
dictionary-lookup assumptions. Direct measurement uses two such passes.
The calculation remains exponential in the source dimension d=19 through
D=2^d. It does not have V1's polynomial data-size bound, but its explicit
limit of about one million entries makes it a concrete candidate for a
readable implementation.

Sampling reduces the retained gauge sectors; it does not turn the
remaining coherent BC wavefunction into one sampled basis string.
Further sampling of those strings without amplitude reconstruction would
give a different quantum process.

Expected attempts per accepted output are 8/5. More shots increase total
runtime and disk output, not the intermediate-state peak, provided shots
are processed sequentially.

## 15. Validation order before trusting a full run

1. **Gate mappings.** Check H and CNOT against dense one-/two-qubit
   matrices, and check Fredkin against all eight basis inputs and coherent
   superpositions. Confirm colliding contributions are added correctly.
2. **Measurement rules.** On small dense vectors compare both outcome
   probabilities and normalized conditional states. Include missing
   partners, exact destructive cancellation, and deterministic outcomes.
3. **Early gauge measurement.** On a small circuit, enumerate the joint
   vertex/gauge outcomes in both measurement orders and compare their
   probabilities and corrected data states up to global phase. Verify
   the actual gauge-Z phase before and after moving its measurement.
4. **Existing smaller geometry.** Reuse the nineteen-qubit repetition-code
   test from `src/test_c4_helix_noiseless.py` as a Guppy/Selene reference.
   Compare individual branches, not only noisy estimates of averages.
5. **Full sources and graph table.** Check source sizes 512 and 1024 and
   weights +1, the BC product size D, and all sixteen gauge table entries
   with exactly two complementary preimages each.
6. **Full trajectory.** Measure peak memory and elapsed time for one
   million-entry attempt before launching many shots. Check nontrivial
   vertex feedforward and nonzero data-SWAP offsets.
7. **Exact branch checks.** Derive probabilities from current weights and
   compare with 3/64 or 1/64 for each vertex word, the B-word distribution
   above, and total success 5/8. Use cached prefixes or representative
   gauge words initially if exhaustive full-state checks are expensive.
8. **Output.** Verify the 1024-key integer-weight state and original code
   constraints. Check logical expectations X_0=4/5, Z_0=3/5, Y_0=0, and
   Z_1=1. All accepted physical B reports should produce the same C state
   up to global phase.

The first implementation milestone is a tested small-state backend and
one benchmarked full trajectory. Claims about multi-shot practicality
should follow that measurement. This note proposes how to obtain the
results; it does not claim that the full sparse simulator has already run.
