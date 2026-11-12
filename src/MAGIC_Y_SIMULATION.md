# Logical-Y magic output and Clifford frames

Both reduced simulators now default to `--magic-output y`. The existing
gauging/ungauging prepares a positive SWAP sector, then both logical-Y
outcomes on B are retained. A tracked Clifford frame represents the output
as `((1-i)|0>+|1>)/sqrt(3)` on C's first logical qubit. C's second logical
qubit stays zero. Ideal success is **3/4**. Use `--magic-output z` to
reproduce the previous target `(2|0>+|1>)/sqrt(5)` and its ideal 5/8 success.

The [procedure](../notes/magic_y_preparation.md) gives the physical circuit
and [proof](../notes/magic_y_preparation_proof.md). The strict recovery
decoder and all graph/gauging options remain available.

## Run and verify

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_reduced.py \
    --shots 6 --seed 0 --magic-output y --history-policy adaptive \
    --terminal-extraction compact_flagged --output-dir output/my-magic-y

"$HOME/pytket-venv/bin/python" src/verify_c4_helix_reduced_run.py output/my-magic-y
```

The noisy runner accepts the same option:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_depolarizing.py \
    --shots 50 --seed 0 --magic-output y --history-policy adaptive \
    --terminal-extraction compact_flagged --two-qubit-infidelity 1e-3 \
    --readout-flip-probability 1e-3 --output-dir output/my-noisy-magic-y

"$HOME/pytket-venv/bin/python" src/verify_c4_helix_depolarizing_run.py output/my-noisy-magic-y
```

Always choose a new output directory. To repeat any earlier saved experiment,
include `--magic-output z` with its original settings and seed. Historical
manifests without an output-profile field are interpreted as Z, not Y.
The Python constructors likewise default to Y; specify `magic_output="z"`
for the old resource.

## Physical state versus corrected output frame

The saved C wavefunction is the **physical raw branch**, with logical
amplitudes `(2-i,1)/sqrt(6)` for decoded Y=+1, or `(2+i,1)/sqrt(6)` for
decoded Y=−1. The record includes:

- `magic_output: "y"`.
- `b_y`: selected physical-word parity and decoded logical Y bit/eigenvalue.
- `output_clifford_frame`: gates in application order, `SDG,H` or `H,SDG,H`.
- `b_decoding`: `keep: true`; final Z meters are used only to discard B.
- `decoded_C_diagnostics`: ideal-decoded target fidelity **in the recorded
  Clifford frame**, not a physical correction performed by the simulator.

The raw logical expectations are X₀=Z₀=2/3 and Y₀=±1/3. After the
Clifford frame the target Bloch vector is `(2/3,2/3,1/3)`, as required
for |m_Y⟩. A wrong reported frame changes the diagnostic fidelity; the
actual error list is never consulted to select or repair that frame.

`exact_magic_target_match` compares the raw physical amplitudes with the
ideal raw branch corresponding to the recorded frame. It does not claim
that a physical encoded Clifford was executed on C.

## Joint recovery and physical cost

On a positively certified final cycle, acquisition measures a 37-bit
commuting record: the original B/C 36 stabilizers and a weight-nine mixed
Pauli word implementing minus logical Y₀. The B correction from the
unchanged joint lookup determines whether to flip its reported parity.
This handles correctable B errors; a bare logical-Y parity alone would
not suffice. On cycles that need re-gauging, the family remains 36 bits
and Y is deferred.

Each controlled physical Y is decomposed into CZ, CX, and S on its cat
leaf. The extra check adds 52 two-qubit gates and three physical S gates
per round. Three clean rounds add 156 two-qubit gates, nine S gates and
75 meters. S gates receive the configured single-qubit depolarizing
channel. Only the final logical Clifford correction is virtual.

For current20 with compact terminal extraction, the clean count is 6,216
two-qubit gates before selected ungauging SWAPs; the 80 atomic Fredkins
and 75-qubit peak remain unchanged. Noisy acceptance is not guaranteed
to equal 75% or to improve by exactly the ideal factor, since physical
Y extraction itself can introduce faults.

## Exact complex sparse arithmetic

Relative phases use Gaussian integers a+ib in the coherent coefficients
of `SparseProductState`. Data factors remain explicit real integer sparse
dictionaries. Norms use complex conjugation and exact integer arithmetic;
measurement probabilities remain exact Fractions. No amplitude is truncated
and no dense statevector or density matrix replaces the sparse method.

Complex saved payloads have `amplitude_type: "gaussian_integer"` and
amplitudes `[real_integer, imaginary_integer]`. Gaussian gcd normalization
removes common complex factors and irrelevant global phases before hashing.
`SparseState.from_payload` loads both old real files and this new format.
Normalized NumPy/SciPy export is available for inspection.

This extension supplies S/SDG on explicit cat/basis qubits, as needed by
Y extraction. It is not a general implementation of arbitrary complex
channels or physical S gates inside a data factor. Trajectory-wise Pauli
noise is supported before and after the Y measurement.

## Validation

The [saved noiseless run](../output/c4-helix-magic-y-noiseless-validation/summary.json)
has six attempts, four accepts and two intrinsic negative-SWAP rejections.
Both Y outcomes occur, with exact physical raw states and verified frames.
The run passed the profile-aware read-only verifier. The finite sample
does not estimate the analytical 3/4 probability.

Tests independently check the two-logical-qubit Born calculation and
Clifford matrices, the physical nine-body word/sign, complex interference,
controlled-Y projectors, large exact complex scale normalization, both
complete output branches, wrong-frame corruption, physical B Pauli errors,
discard-meter flips and deferral of Y across re-gauging. Earlier tests
explicitly select Z to retain regression coverage of the previous procedure.

The combined suite passed **138 tests**. The new noiseless and noisy
outputs, and the historical Z-output artifacts checked for compatibility,
passed their read-only verifiers. Exact complex scale normalization and
the recorded Clifford gate order also have independent regression checks.

The [bounded noisy pilot](../output/c4-helix-magic-y-1e-3-readout-1e-3-20/summary.json)
uses two-qubit infidelity 10⁻³ and readout-flip probability 10⁻³, with other
noise channels ideal. It completed twenty attempts and accepted four;
all four had decoded target fidelity one in their frames. Three already
matched their raw physical target, while one had a correctable physical
error. Both Y eigenvalues occurred among the accepted outputs. There
were no resource failures. This small pilot does not establish a noisy
yield improvement, a rare logical-error rate, or 75% noisy acceptance.

With `src` on the Python path:

```python
from simulate_c4_helix_reduced import ReducedRejectionSimulator

result = ReducedRejectionSimulator(
    magic_output="y", history_policy="adaptive",
    terminal_extraction="compact_flagged",
).run()
if result["accepted"]:
    print(result["b_y"]["eigenvalue"])
    print(result["output_clifford_frame"])
    physical_c = result["c_state"]
```
