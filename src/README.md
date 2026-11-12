# Noiseless C4-Helix magic preparation in Guppy

**New output default:** the reduced sparse simulators now use logical-Y
extraction, retaining both outcomes with an explicit output Clifford frame.
See [Y-output simulation](MAGIC_Y_SIMULATION.md): ideal success is 3/4.
Use `--magic-output z` for the previous target and every earlier comparison
below. The original Guppy and bare sparse implementations are unchanged.

For the new procedure with repaired cats, active syndrome correction,
joint B/C recovery, and adaptive re-gauging, see
[Reduced-rejection noiseless simulation](REDUCED_REJECTION_SIMULATION.md)
and `simulate_c4_helix_reduced.py`. It executes all physical gadgets and
has no realistic-noise model enabled.

For sampled X/Y/Z depolarization on that same physical circuit, see
[Depolarizing-noise simulation](DEPOLARIZING_SIMULATION.md) and
`simulate_c4_helix_depolarizing.py`. The default is two-qubit average
infidelity 10⁻⁴, with separate optional rates for other operations.

[Adaptive syndrome histories](ADAPTIVE_HISTORY.md) documents the new
`--history-policy adaptive` option. It certifies a complete record within
five rounds and preserves the two-fault argument. The default remains
`triple` while its high-noise acceptance/fidelity tradeoff is evaluated.

The [compact terminal gadgets](../notes/compact_terminal_extraction.md)
are available as `--terminal-extraction compact_flagged`. A clean B/C
round uses 408 two-qubit gates rather than 1,068; flags invoke a certified
repair and protected recovery on the retained data.

For the separate implementation with all verified cats, gauged checks,
filtering, recovery, and named Pauli-fault locations, see
[Full gadget simulation](GADGET_SIMULATION.md) and
`simulate_c4_helix_gadgets.py`. The noiseless implementations below are
unchanged.

`c4_helix_noiseless.py` implements the noiseless specialization of
[`full_procedure_integrated_v2.md`](../notes/full_procedure_integrated_v2.md).
It was checked with Python 3.12, Guppy 1.1.1 and Selene 0.3.2 in
`$HOME/pytket-venv/`. Guppy provides the quantum operations, mid-circuit
measurements, and classical control flow; Python only builds fixed circuit
geometry and input preparation schedules at compile time. See the
[official Guppy documentation](https://guppylang.org/).

The physical procedure uses 65 qubits: twenty B, twenty C, twenty gauge A,
and five vertices. Its stages are:

1. Prepare B in encoded `|00>` and C in encoded `|+0>` using only H/CNOT
   circuits. The B source is the uniform superposition of the binary span
   of the nine independent X-check supports. The C source adds logical X0
   as a tenth independent generator. Row reduction constructs the circuits;
   the check operators are never measured.
2. Prepare the five-vertex/twenty-edge graph resource, using forty CNOTs
   in V2's edge order.
3. Apply twenty Fredkins, with vertex `q // 4` controlling physical pair
   `(B_q,C_q)`. These are V2's contiguous inner blocks, rather than the
   different controller assignment in older saved graph audits.
4. Measure the vertices in X. Reject odd parity. For an even report b,
   apply the physical feedforward `Z(A7)^b_b Z(A11)^b_c Z(A3)^b_d Z(A0)^b_e`.
5. Measure all twenty A qubits in Z. Choose `t_a=0` and recover
   `(t_b,t_c,t_d,t_e)=(m7,m11,m3,m0)`. Apply four ordinary data SWAPs for
   each nonzero vertex offset. This spanning-tree decoding is exact on
   noiseless reports; no error-correcting decoder is run.
6. Measure all twenty B qubits in Z. Keep logical Z0 parity zero on
   positions `0,3,6,7,18,19`. Return the twenty live C qubits.

There are no cat states, verification gadgets, stabilizer measurements,
syndrome rounds, recovery operations, or checks on the measured gauge
cycles. The vertex and B postselections are intrinsic to magic preparation.
There are at most 45 physical measurements in a successful attempt;
rejected odd-vertex attempts stop earlier.

`prepare_magic()` is the reusable Guppy function. Its return type is
`Option[array[qubit, 20]]`: `some(C)` means success and `nothing()` means
postselection failed. On success C is encoded `|M0>`, with
`|M> = (2|0> + |1>)/sqrt(5)`. C is neither decoded nor measured, and the
caller takes ownership of it. Ideal success per attempt is `5/8`.

Inside a Guppy caller:

```python
attempt = prepare_magic()
if attempt.is_some():
    c = attempt.unwrap()
    # Continue the quantum computation using c; eventually consume it.
else:
    attempt.unwrap_nothing()
    # This attempt was rejected; there is no quantum output.
```

Classical outputs are tagged `vertex_x`, `swap_plus`, `gauge_z`,
`swap_offsets`, `b_z`, `b_logical_z0`, and `accepted`. Later-stage tags are
absent if the attempt exits earlier. Array indices follow physical labels;
vertex arrays are in a,b,c,d,e order. A true measurement bit denotes the
negative eigenvalue. `swap_plus` and `accepted` are success flags.

From the repository root, compile the full physical program:

```sh
"$HOME/pytket-venv/bin/python" src/c4_helix_noiseless.py
"$HOME/pytket-venv/bin/python" src/c4_helix_noiseless.py --output /tmp/c4-helix.hugr
```

The standalone `compile_entrypoint()` consumes successful C outputs with
`discard_array`; it is a compilation/demo sink. Call `prepare_magic()` from
your own Guppy function to retain and use the resource. To compile its
reusable function definition, use `prepare_magic.compile_function()`.

Run validation:

```sh
"$HOME/pytket-venv/bin/python" -m pytest -q src/test_c4_helix_noiseless.py
```

The tests compile the full 65-qubit procedure, check the physical encoded
input amplitudes and every accepted physical B report, and verify all 512
vertex/gauge branches algebraically, including the gauge-Z phase correction.
They also execute the actual Guppy gauging function on a smaller 19-qubit
repetition-code/tree instance with the ideal Selene statevector simulator,
testing feedforward, postselection probabilities, and X/Y/Z magic-state
readout statistics. A separate execution checks all eight Fredkin inputs.
These Guppy tests are not full 65-qubit statevector simulations. The sparse
simulator below provides exact compressed execution of the full procedure.
Selene's Zig build step needs access to its compiler cache.

## Exact full-circuit sparse simulation

`simulate_c4_helix_sparse.py` implements the
[V2 sparse-wavefunction plan](../notes/c4-helix-exact-simulation-plan-v2.md).
It uses the unchanged Guppy file's supports, graph, controller assignment,
source H/CNOT schedules, and readout parity. It simulates the physical data
amplitudes and samples the required measurements, retaining C on success.

Run from the repository root with the existing environment:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_sparse.py \
    --shots 3 --seed 0 --output-dir output/my-c4-helix-run
```

`--shots` counts attempts, including rejections. Use a new output directory
for each run: the CLI refuses to overwrite an existing `shots.jsonl`.
`--quiet` hides stage progress. The CLI streams each result immediately;
it does not retain all attempts' wavefunctions.

Files written:

- `shots.jsonl`: physical measurement records and exact conditional
  probabilities, one attempt per line.
- `states/<hash>.json`: a successful C state's coordinate labels, integer
  weights, and squared normalization. Equal output states share a file.
- `summary.json`: accepted count, seed, timings, source sizes, and process
  peak memory. The peak is the process-lifetime RSS, including imports and
  sources; the largest individual state is separately reported per attempt.

### State representation and physical equations

`SparseState` stores a dictionary of explicit binary strings and nonzero
Python integer weights:

\[
|\Psi_w\rangle=\frac{\sum_x w(x)|x\rangle}{\sqrt{N(w)}},
\qquad N(w)=\sum_x w(x)^2.
\]

Coordinate names specify the ordering of the characters. Source Hadamards
omit a common factor `1/sqrt(2)`, which this normalization absorbs. Gates
return new states; treat their `weights` dictionaries as read-only.

The input in integrated-procedure V2 Section 5 is

\[
|\psi\rangle=|\overline{00}\rangle_B|\overline{+0}\rangle_C,
\qquad |\overline{+0}\rangle=(I+\overline X_0)|\overline{00}\rangle/\sqrt2.
\]

The B/C sources have 512/1024 entries. After the graph preparation and
Fredkins (Sections 6--7), the physical state would be

\[
\frac1{\sqrt{32}}\sum_t |t\rangle_V|p(t)\rangle_A V_t|\psi\rangle,
\quad p(t)_q=t_{u_q}+t_{v_q}\pmod2,
\quad V_t=\prod_v T_v^{t_v}.
\]

Here `t` has five bits, `u_q,v_q` are edge q's endpoints, and `T_v` swaps
the four matched data pairs of vertex v's block. The simulator samples
the gauge word m first, using the exact commuting-projector reordering
proved in the V2 plan. It keeps **both** preimages t and its complement:

\[
|\Omega_m\rangle=
\frac{|t\rangle V_t|\psi\rangle+|\bar t\rangle V_{\bar t}|\psi\rangle}{\sqrt2}.
\]

This needs at most 1,048,576 entries per state. The sampled m is internal
until the physical attempt reaches gauge readout. It is not exposed in
the public records of an odd-vertex rejection.

For a vertex-X result b, the sparse backend groups weights by the remaining
key y, adds their amplitudes, and samples using

\[
u_b(y)=w(0,y)+(-1)^b w(1,y),\qquad
\Pr(b)=\frac{\sum_y u_b(y)^2}{2N(w)}.
\]

It computes both norms first and constructs only the selected output.
Zero amplitudes are removed after exact cancellation. This implements
the H/Z readout in Section 8 without expanding a large post-H state.

For an even five-bit vertex report, apply the actual feedforward

\[
F_b=Z_{A_7}^{b_b}Z_{A_{11}}^{b_c}Z_{A_3}^{b_d}Z_{A_0}^{b_e},
\qquad
F_b|m\rangle=(-1)^{b_bm_7+b_cm_{11}+b_dm_3+b_em_0}|m\rangle.
\]

The sign is explicitly applied to the weights. The gauge word then selects
the Section 13 SWAP corrections through
`t_hat=(0,m7,m11,m3,m0)`. The expected corrected state is

\[
|\Psi_+\rangle=(|\psi\rangle+U|\psi\rangle)/\sqrt3,
\qquad U=T_aT_bT_cT_dT_e.
\]

The simulator obtains this by its gates and sampled measurements. It never
initializes this expected output directly. At colliding keys the weights
add, giving 262,144 weights of two and 524,288 weights of one.

For physical B-Z readout (Section 16), sample each s using

\[
\Pr(n_q=s)=\frac{\sum_{x:x[B_q]=s} w(x)^2}{N(w)}.
\]

Retain the selected strings, remove the measured coordinate, and accept
only logical parity zero on positions `0,3,6,7,18,19`. The retained C state
has 1024 entries, squared normalization 2560, and represents

\[
|\overline{M0}\rangle=
\frac{2|\overline{00}\rangle+|\overline{10}\rangle}{\sqrt5}.
\]

No code checks, recovery circuits, or C measurements are inserted. The
reported stabilizer and logical expectations are read-only diagnostics of
the retained amplitudes. For accepted C they must give all eighteen code
checks +1 and logical expectations `X0=4/5`, `Z0=3/5`, `Y0=0`, `Z1=1`.

### Python API, NumPy/SciPy exports, and tests

With `src` on Python's import path:

```python
from pathlib import Path
from simulate_c4_helix_sparse import SparseC4HelixSimulator
from sparse_wavefunction import SparseState
import json

simulator = SparseC4HelixSimulator()
for result in simulator.iter_attempts(number_of_attempts=3, seed=0):
    if result.accepted:
        c = result.c_state                 # Exact, unmeasured quantum output.
        column = c.to_scipy_column()       # Normalized floating-point CSC vector.
        print(c.norm_squared(), column.nnz)
    # Save/use this result before requesting the next one.

saved = SparseState.from_payload(json.loads(Path("path/to/state.json").read_text()))
```

The core uses string dictionaries and exact Python integers/Fractions, as
specified by V2. NumPy and SciPy provide explicit normalized-vector exports
and independent matrix-based validation. `to_scipy_column()` stores only
nonzero amplitudes; `to_numpy(max_qubits=20)` is an explicitly bounded dense
export. The first coordinate is the most significant bit in either export.

```sh
"$HOME/pytket-venv/bin/python" -m pytest -q \
    src/test_sparse_wavefunction.py src/test_c4_helix_sparse.py
```

These tests check both measurement branches, destructive interference,
Fredkin's coherent action and its decomposition, all 512 joint vertex/gauge
branches against an independent original-order nineteen-qubit NumPy statevector,
physical B branches, rejection records, and a successful full 65-qubit
trajectory with nontrivial feedforward. They check exact source/support
counts, all physical B-word probabilities in the corrected state, saved
output roundtrips, SciPy overlap with the encoded magic target, and code
and logical observables. The existing Guppy/Selene tests remain in
`test_c4_helix_noiseless.py`.

This explicit method is exponential in the nineteen source-generator
choices, not polynomial in arbitrary data size. The V2 early measurement
bounds each state's support by about one million entries; out-of-place
updates temporarily keep both old and new dictionaries. Actual memory and
timings are reported by the CLI instead of inferred from the support bound.

### Measured full-circuit validation

The saved [three-attempt run](../output/c4-helix-sparse-demo/summary.json)
used seed 0 in `pytket-venv`: 44.63 seconds total and 485,113,856 bytes
(about 463 MiB) of process peak RSS. Two attempts retained the same exact
C state; the other failed the final B logical selection. Each retained
state passed all code and logical checks. These are measurements on this
machine, not runtime or memory guarantees for another environment.

The [shot records](../output/c4-helix-sparse-demo/shots.jsonl) include the
actual vertex, gauge, and B words, exact branch probabilities, and a
reference to the saved C amplitudes. A separate seed-7 attempt exercised
odd-vertex rejection before physical gauge/B readout.

## Verify an existing saved run

`verify_c4_helix_run.py` checks completed full-circuit runs without rerunning
the simulator or modifying any saved files. From the repository root:

```sh
"$HOME/pytket-venv/bin/python" -B src/verify_c4_helix_run.py \
    src/output/my-c4-helix-run
```

The argument is the **run directory** containing `summary.json`,
`shots.jsonl`, and its referenced `states/` files. It can be an absolute
path; it is not required to be under `output/`. For example, the run above
was started from `src`, so its files are under `src/output/`.

The command checks:

- Summary counts against the actual shot records and the expected source sizes.
- Vertex parity, gauge-word validity, correcting SWAP offsets, B logical
  selection, and recorded exact branch probabilities for every shot.
- That rejected attempts expose no unperformed later measurements or C output.
- Every distinct referenced state's content hash, coordinate labels, integer
  weights, and squared normalization.
- The actual saved amplitudes against the independently constructed target
  `2 sum_{h in H}|h> + sum_{h in H}|h+xi>`, up to common scale/sign. Here H
  is generated directly from the nine X-check supports and xi is logical X0;
  the verifier does not rerun the simulator's source-preparation routines.
- Recomputed code checks and logical expectations against the target, and
  recomputed diagnostics against every accepted shot's saved diagnostic.

Only one 1024-amplitude C file needs checking when many shots reference
the same state. Unreferenced state files are not inspected. A run with no
accepted shots explicitly reports that no output state could be verified.

The acceptance statistics are reported separately: exact two-sided binomial
tests against `5/8` overall, `3/4` for vertex selection, and `5/6` for B
selection conditioned on passing the vertices. A low p-value prints a
sampling notice; it is not a deterministic state/file error. `--alpha`
sets the notice threshold and the confidence-interval level (default 0.05).
These are three individual tests, not one multiple-testing-adjusted test.

For a machine-readable report, print JSON to the terminal:

```sh
"$HOME/pytket-venv/bin/python" -B src/verify_c4_helix_run.py \
    src/output/my-c4-helix-run --json
```

Exit code **0** means the exact saved-file/state checks passed; **1** means
an inconsistency or unreadable input was found. Argument syntax errors use
argparse's exit code **2**. Statistical notices alone leave the exit code 0.
The verifier does not check historical timing/RAM measurements or replay
the random seed. It verifies saved outputs, not a fresh execution trace.

Fast verifier regression tests, including deliberately corrupted fixtures:

```sh
"$HOME/pytket-venv/bin/python" -m pytest -q src/test_verify_c4_helix_run.py
```
