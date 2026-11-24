# Sparse depolarizing-noise simulation

The runner now defaults to `--magic-output y`; see
[Y-output simulation](MAGIC_Y_SIMULATION.md) for the 3/4 ideal-success
procedure and tracked Clifford correction. All historical Z-target runs
and comparisons below are reproduced with `--magic-output z`.

`simulate_c4_helix_depolarizing.py` executes the optimized gauging/ungauging
procedure with its actual error-correction gadgets and adaptive decisions.
It reuses the noiseless controller and sparse wavefunction backend. The
new runtime samples physical Pauli noise while the circuit runs; the
controller sees only its measured reports.

The default is **average two-qubit gate infidelity 10⁻⁴**. One-qubit gates,
atomic Fredkins, preparation, readout, and idles are ideal unless their
separate parameters are set. This is a specified gate-noise experiment,
not a calibrated hardware model.

The new [adaptive history option](ADAPTIVE_HISTORY.md) can improve
high-noise acceptance using at most five complete rounds. Select
`--history-policy adaptive` explicitly. The default remains `triple`;
compare decoded fidelity as well as acceptance when changing the policy.

The new [compact terminal option](../notes/compact_terminal_extraction.md)
is selected with `--terminal-extraction compact_flagged`. It uses guarded
flag gadgets and switches to protected recovery when a flag fires. The
default is `protected`; the manifest records both extraction choices.

## Run

From the repository root, with the existing Python environment:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_depolarizing.py \
    --shots 50 --seed 0 --two-qubit-infidelity 1e-4 \
    --output-dir output/my-depolarizing-pilot

"$HOME/pytket-venv/bin/python" src/verify_c4_helix_depolarizing_run.py \
    output/my-depolarizing-pilot
```

Choose a new output directory. Attempt k uses Born seed `seed + k` and
a separate noise seed obtained by hashing that Born seed. `--noise-seed N`
instead sets noise seed `N + k`. Every attempt is retained, including
rejections. No fault-count cutoff is applied.

The default graph is `current20`, extraction is `optimized`, and source
preparation is `encoded`. `--graph compact13`, `--extraction verified_cat`,
and `--source-mode projected` are also available. Changing the circuit or
noise parameters changes the random draws, so matching seeds across
different configurations need not produce matching branches.

## What “infidelity 10⁻⁴” means

Immediately after each executed CX, CZ, or ordinary two-qubit SWAP, apply

\[
\mathcal E(\rho)=(1-p_2)\rho+
\frac{p_2}{15}\sum_{P\in\{I,X,Y,Z\}^{\otimes2}\setminus\{II\}}P\rho P.
\]

For average gate infidelity r₂, **p₂ = 5r₂/4**. Thus r₂ = 10⁻⁴ means a
nonidentity Pauli pair occurs with probability **1/8000**, not 1/10000.
The fifteen pairs IX, IY, IZ, XI, XX, …, ZZ are equally likely. For
example, YX means Y on the first gate participant and X on the second.
Both single-participant errors and correlated errors are included.

More generally, for an n-qubit gate the nonidentity probability is
\(p_n=(2^n+1)r_n/2^n\), uniformly over \(4^n-1\) Pauli words. These are
independent channel draws at different physical locations. A sampled
Pauli update is an error, not another recursively noisy gate.

An accepted clean current-graph schedule has about 8,050 two-qubit gates,
so its sum of two-qubit error probabilities is about 1.01. Rejected
attempts can stop earlier, while retries can add locations. Noise is
sampled on the operations actually executed, including extra cat scans,
source rebuilds, physical corrections, and fresh gauging cycles.

Additional parameters, all zero by default:

| Parameter | Channel and timing |
|---|---|
| `--one-qubit-infidelity` | Depolarization after H/X/Y/Z |
| `--three-qubit-infidelity` | Depolarization after each atomic Fredkin, uniformly over 63 nonidentity Pauli triples |
| `--idle-infidelity` | Single-qubit depolarization on every waiting live qubit before each serial physical operation |
| `--preparation-flip-probability` | X immediately after physical zero preparation |
| `--readout-flip-probability` | Classical report flip after the actual destructive Z meter |

For example, adding `--three-qubit-infidelity 1e-4` turns on noise on
the 80 Fredkins of a clean schedule. A Fredkin remains an atomic gate;
its rate does not specify a decomposition into noisy two-qubit gates.
Preparation/readout parameters are direct flip probabilities, unlike the
gate parameters, which are average infidelities.

An idle interval is one serial operation, **not a calibrated duration**.
Gate times, parallel scheduling, T₁/T₂, leakage, and coherent calibration
errors are not modeled. Pauli depolarization includes X, Y, and Z; it is
not restricted to dephasing.

## Why the sparse method still works

One Monte Carlo trajectory is a pure quantum wavefunction with a sampled
sequence of Pauli errors. X permutes sparse bit strings, Z changes their
signs, and Y combines both with a tracked global i phase. No density
matrix is constructed. Measurements retain their actual Born probabilities,
and coherent Fredkin branches remain coherent until physically measured.
Averaging trajectories reproduces the specified stochastic channel.

Errors can nevertheless make different sparse factors less compatible,
or force longer adaptive histories. Runtime is not guaranteed by the
number of qubits alone. The runner therefore uses one fresh worker per
attempt, defaults to a 60-second attempt timeout, and checks a 4096-term
coherent expansion bound. Neither limit truncates the wavefunction.

A computational failure is recorded as **unresolved**, with
`accepted: null`; it is never counted as a circuit rejection. The summary
gives both the rejection fraction among completed circuits and bounds
over all requested attempts. If any attempts are unresolved, completed
attempts alone can be a biased sample. If the circuit decision is already
saved but the final diagnostic times out, that physical decision is kept
and only the diagnostic is marked unavailable.

## Acceptance and logical quality are separate

The physical controller uses the same measured-record rules as the
noiseless procedure. It never inspects the sampled error list or the
unmeasured final C state to decide acceptance.

Each accepted C wavefunction is saved exactly. Two read-only diagnostics
then answer different questions:

1. `exact_magic_target_match`: does the physical state already equal the
   encoded target? A remaining correctable X error can make this false.
2. `decoded_C_diagnostics`: after ideal original-code syndrome measurement
   and a fixed recovery, how close is the decoded two-logical-qubit state
   to \(|M\rangle\otimes|0\rangle\), with
   \(|M\rangle=(2|0\rangle+|1\rangle)/\sqrt5\)?

The diagnostic decoder uses the existing minimum-weight-at-most-two
lookup where defined. Every other syndrome uses a fixed GF(2) pure-error
correction; no syndrome is discarded. All syndrome probabilities and
logical amplitudes are summed exactly using integer Walsh transforms.
The diagnostic is **not an extra perfect recovery in the physical
circuit**, and it does not change acceptance or the saved wavefunction.

For a concrete example, a physical single-qubit X/Y/Z error gives decoded
target fidelity 1. A logical X₀ gives fidelity 16/25, and logical Z₀ gives
9/25. Thus the mean accepted decoded infidelity is a useful logical-quality
measure; it is not automatically a probability of a binary logical fault.
The summary also flags accepted trajectories with at most two sampled
events and decoded fidelity below one for investigation of the two-fault
prediction. A pilot with no such examples does not prove that prediction.

## Saved files and verification

- `manifest.json`: exact rational rates, channel convention, graph,
  extraction, source mode, seed rules, atomic-Fredkin assumption, and limits.
- `shots.jsonl`: all attempts, physical decisions and syndrome histories,
  sampled noise events, operation counts, resources, and available diagnostics.
- `states/<hash>.json`: canonical exact accepted C wavefunctions; duplicates
  share a file. Rejected/unresolved attempts expose no output state.
- `attempts/000000/`: stage progress, persisted physical circuit decision,
  and final result or failure details. With `--trace`, also `events.jsonl`
  containing physical operations, actual/reported meter bits, and noise timing.
- `summary.json`: updated after every attempt, with final `completed: true`.
  Counts during an unfinished run cover the attempts recorded so far;
  the manifest retains the total requested.

The verifier recomputes operation/noise accounting, seed rules, state
hashes, decoded C diagnostics, and aggregate statistics. It accepts
imperfect accepted outputs as valid simulation results. It does not
replay the quantum circuit or certify the random generator.

Under noise, a `negative_swap` code describes the measured rejection
decision. It does not identify whether its cause was the intrinsic
noiseless selection or a physical error. The noiseless rejection reference
remains 3/8; these counts do not isolate noise-induced rejection.

## Validation and first pilot

```sh
"$HOME/pytket-venv/bin/python" -m pytest -q \
    src/test_c4_helix_depolarizing.py src/test_c4_helix_optimized.py \
    src/test_c4_helix_reduced.py src/test_c4_helix_gadgets.py
```

Tests cover every two-qubit Pauli pair against dense evolution, the full
one-/two-/three-qubit depolarizing channel and infidelity calibration,
preparation/readout/idle timing, Y phases, unrestricted fault counts,
logical versus physical errors, exact syndrome-sector decoding, zero-noise
agreement with the previous simulator, timeouts, and corrupted saved results.
The combined command passed **90 tests**.

The [saved 50-attempt pilot](../output/c4-helix-depolarizing-pilot-50/summary.json)
used seeds 0–49 and the default model. All 50 circuits and all accepted
diagnostics completed:

| Result | Observed value |
|---|---:|
| Accepted / rejected | 27 / 23 |
| Rejection breakdown | 17 negative-SWAP, 5 B-one, 1 unstable-record |
| Observed rejection fraction | 46% |
| Wilson 95% interval | 33.0–59.6% |
| Accepted decoded target fidelity | 1 for all 27 |
| Sampled two-qubit Pauli events | 69 total; 0–5 per attempt |
| X / Y / Z factors | 36 / 38 / 42 |
| Total wall time | 241 seconds |
| Largest worker peak RSS | 1.11 GiB |
| Largest coherent expansion | 1,024 terms |
| Computational failures | 0 |

All 27 accepted states also physically matched the target in this sample.
The pilot establishes practical feasibility on this machine. Fifty attempts
do not resolve a small change from the noiseless rejection rate, establish
a logical error rate, or compare the optimized and baseline noisy yields.
Those require larger runs with explicitly chosen channel parameters.
