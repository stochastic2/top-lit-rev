# Noiseless sparse simulation of the procedure with less rejection

**Output profile:** the runner now defaults to `--magic-output y`, with
both Y outcomes retained in an explicit Clifford frame and ideal success
3/4. See [the Y guide](MAGIC_Y_SIMULATION.md). The historical states,
counts and 5/8 examples below concern `--magic-output z`; add that option
to reproduce them.

`simulate_c4_helix_reduced.py` implements the
[new integrated procedure](../notes/full_procedure_reduced_rejection.md),
including its physical error-correction gadgets and adaptive controller.
The main configuration retains the existing five vertices, twenty gauge
edges, forty data qubits, and gauging/ungauging circuit. The earlier
simulators are unchanged.

The default `--extraction optimized` now reduces the full current-graph
two-qubit count by **54.2%**, from 17,577 to 8,052 in accepted examples
with twelve ungauging SWAPs. The 80 Fredkins remain separate. The original
three-scan circuit is retained as `--extraction verified_cat`; old saved
runs remain readable by the verifier.

**This entry point is noiseless.** A separate
[depolarizing-noise runner](DEPOLARIZING_SIMULATION.md) now samples X/Y/Z
errors at its physical operation boundaries, using the same controller
and gadgets. Its guide specifies the rates and reports the first pilot.

The new [adaptive history policy](ADAPTIVE_HISTORY.md) is available with
`--history-policy adaptive` in both runners. It certifies complete records
within five rounds, including nonzero cat repair. The default remains
`triple` because high-noise testing shows an acceptance/fidelity tradeoff.

`--terminal-extraction compact_flagged` selects the
[new terminal gadgets](../notes/compact_terminal_extraction.md), reducing
a clean B/C round from 1,068 to 408 two-qubit gates. A nonzero flag triggers
a certified preliminary repair and protected extraction on the same data.
The default `protected` retains the previous circuit and all saved runs.

## Run a validation example

From the repository root, using the existing environment:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_reduced.py \
    --shots 4 --seed 0 --output-dir output/my-reduced-validation
```

Attempt k uses seed `seed + k`. With optimized extraction, the saved
seed-0--3 example has two negative-SWAP rejections and two accepted outputs.
The retained baseline example also exercises a final B-one rejection.
Changing the physical gadget changes how many random measurement samples
are consumed, so the same seed need not give the same branch in both
profiles. These are actual Born samples; no outcome is forced or retried
until an acceptance is obtained.

For one accepted example with every physical operation recorded:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_reduced.py \
    --seed 2 --trace --output-dir output/my-reduced-trace
```

Use a **new** output directory. Existing runs are never overwritten.
The trace records every physical operation, rather than an abstract
check projector. Omit `--trace` for smaller outputs; all complete source, graph,
gauged, and terminal syndrome histories remain in the shot record.

To use the smaller graph from the note's appendix:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_reduced.py \
    --graph compact13 --seed 2 --output-dir output/my-reduced-compact13
```

The default is `--graph current20`. Both choices still perform gauging
and ungauging. Neither is a direct whole-block SWAP measurement.

## What the code physically executes

| Stage | Executed operations and decision |
|---|---|
| Protected cats | Raw H/CNOT-chain preparation; stop early on two initially zero complete ZZ scans, otherwise use the first three identical vectors within nine scans and physically X-correct |
| Cat/data coupling | Group controls only within a matched C4 block where allowed; finish every coupling before reading cat leaves; retain individual gauge and final data targets |
| B and C preparation | Actual encoders, then compact source extraction: four-gate inner checks, fourteen-gate upper checks, ten-gate known logical checks; local rebuild on a flag, and three equal complete known-state records before correction |
| Graph preparation | Actual vertex H gates and endpoint-to-edge CNOTs; repeated complete known-state checks and physical sign correction |
| Enrichment | Twenty physical Fredkins, vertex v controlling its four corresponding data pairs |
| Vertex readout | Five H gates, five Z meters, and physical gauge-Z feedforward; retain either vertex parity provisionally |
| Gauged verification | Repeated paired/cycle/Gauss family; decode cycle-X errors, correct even Gauss signs, certify the SWAP sector or mark the cycle for fallback |
| Ungauging | Measure every gauge qubit in Z, decode the entire cut word, and apply ordinary physical data SWAPs |
| Original-code recovery | Repeated complete B/C syndrome; use the shared-two-block candidate table and apply its selected physical Paulis |
| Fallback | For an uncertified but recoverable cycle, keep B/C, prepare a fresh graph, and gauge/ungauge again; at most three total cycles |
| Final extraction | Twenty physical B meters; full classical bit-word decoding before the logical selection; keep C as an unmeasured quantum state |

With the default `--history-policy triple`, the source, graph, gauged,
and terminal data agreement rule remains
**three consecutive identical complete records**, at most nine rounds.
There is no clean-round oracle or intermediate data correction. Only the
protected cat's two initially zero scans have a shorter path. A nonzero
cat history still uses the full three-equal-record repair.
With `adaptive`, these stages use the certified whole-history rule and
stop within five rounds. The two-initial-zero-scan shortcut remains.

The default protected port assignment is:

- Graph/cycle checks: one leaf per physical target.
- Paired checks: one leaf per matched data-block label (one or four leaves).
- Gauss checks: separate gauge leaves, one leaf controlling four data SWAPs.
- Terminal checks: one leaf per physical data target.

For source checks, the decoded star-cat fanout is uncomputed after coupling.
Its non-syndrome leaves are measured in Z as flags; the syndrome leaf is
measured in X. Each leaf controls targets in one inner block. A source
flag triggers measurement/reset/re-encoding of only that unused known
source, restarting its complete history; at most three builds are allowed.
All waiting operations on the other source remain counted.

| Accepted clean schedule | Current graph | Compact graph |
|---|---:|---:|
| Check gadgets | 420 | 378 |
| Complete protected-cat scans | 540 | 456 |
| Source-flag bits | 168 | 168 |
| Two-qubit gates before selected SWAPs | 8,040 | 7,120 |
| Atomic Fredkins | 80 | 80 |
| Peak live qubits | 75 | 66 |

Add 0--16 ordinary ungauging SWAPs to the two-qubit column. The retained
baseline has 17,565/16,357 two-qubit gates before those SWAPs, 1,260/1,134
cat scans, and peaks of 77/70 qubits. Internal adjacent-ZZ tests and
source flags are physical operations but not additional check gadgets.

The source weight-eight fourteen-gate circuit follows the paper's decoded
cat pattern, with reordered targets to confine each leaf to one C4 block.
The inner eight-gate pair uses two sequential block-local checks; it does
not emulate the paper's simultaneous leakage-refresh circuit. The final
recovery retains stronger physical spread protection than source extraction.
See the updated note/proof for why copying every paper gadget into that
output stage would need a different late-error decoder.

A negative ideal vertex parity now reaches all three gauged rounds and
is rejected by the **measured Gauss product**. The program does not use
the vertex parity alone as an early exit. That is how the revised
procedure leaves room to rescue a false odd report in a future noisy run.

The default `--source-mode encoded` executes the unitary source encoder.
`--source-mode projected` instead starts B and C in physical zeros and
executes the complete known-state measurements. Random negative source
signs are **corrected**, not selected away. Both modes have ideal source
success one. The projected option is useful for validating nonzero
syndrome corrections without introducing any noise model.

## Sparse wavefunction representation

The shared backend is `sparse_gadget_state.py`, also used by the previous
full-gadget simulator. It represents

\[
|\eta\rangle=\sum_{z,F}c_{z,F}|z\rangle\bigotimes_{f\in F}|f\rangle,
\qquad |f\rangle=\sum_x f(x)|x\rangle.
\]

Each data factor f is an explicit dictionary of physical bit strings and
integer amplitudes. z is an explicit quantum basis string for vertices,
gauge qubits, and helpers. Different terms are added **coherently**.
Born probabilities include all overlap cross terms, even when different
SWAP histories give different data partitions. No orthogonality shortcut,
stabilizer tableau, or classical mixture replaces this wavefunction.

The initial B/C sparse factors have 512/1,024 amplitudes. SWAPs exchange
physical coordinates between factors; their coherent controls remain
quantum. The backend does not sample those controls during gates. Actual
measurements construct both branches and sample their exact rational
norm ratios. H's common normalization factors are handled consistently
through these ratios. Y uses its real XZ action and a tracked global i
phase, while still being one physical gate location.

There is **no early gauge-Z measurement**. The gauged Gauss gadgets use
X on A, so the reordering used in the older bare noiseless simulator
would be invalid here. Measurement gadgets are not replaced by ideal
check projectors.

`--max-terms` is a checked resource bound on the coherent expansion,
default 4096. Exceeding it raises a computational error. It never truncates
small amplitudes and never counts a memory failure as a circuit rejection.

## Output files and independent verification

Each run writes:

- `manifest.json`: extraction profile, exact graph, source mode, seed rule, serial scheduling
  convention, atomic three-qubit Fredkin choice, and `noise_model: "none"`.
- `shots.jsonl`: one record per physical attempt, including every complete
  syndrome history, stopping record, correction, cycle decision, rejection
  reason, actual gauge/B reports when reached, and resource counts.
  Source records also list local builds, nonzero source flags, and the
  successful restarted history when a rebuild is needed.
- `states/<content-hash>.json`: the exact unmeasured C amplitudes on
  acceptance. Identical outputs share one file. Rejected attempts expose
  no C output.
- `summary.json`: completed-attempt counts, intrinsic rejection breakdown,
  runtime, process-lifetime peak RSS, and operation counts. It is written
  only after all requested attempts complete.
- `events.jsonl`, with `--trace`: every physical preparation, gate, and
  meter, plus cat scans, complete syndrome rounds, and decoder decisions.

Physical trace events include participant names, the named waiting-qubit
set, and the actual/reported meter bit and exact branch probability.
In this version actual and reported bits agree. Classical decoders consume
only the reported records. Trace diagnostics do not influence acceptance.

Validate a completed run without replaying it or writing anything:

```sh
"$HOME/pytket-venv/bin/python" src/verify_c4_helix_reduced_run.py \
    output/my-reduced-validation
```

The verifier checks the saved histories and correction decisions, expected
noiseless branch structure, register/gadget counts, summaries, content hashes,
and **the saved amplitudes themselves** against an independently constructed
encoded magic target. It does not merely trust the simulator's success flag.
It does not certify a full event trace or estimate a noisy rejection rate.

On success the canonical C state has 1,024 nonzero amplitudes and squared
normalization 2,560: 512 amplitudes equal to 2 in the original X-stabilizer
span, and 512 equal to 1 in its logical-X0 translate. Its logical expectations
are \(\langle\overline X_0\rangle=4/5\),
\(\langle\overline Z_0\rangle=3/5\),
\(\langle\overline Y_0\rangle=0\), and
\(\langle\overline Z_1\rangle=1\); every original code check is positive.

## Python API

With `src` on the Python path:

```python
from simulate_c4_helix_reduced import ReducedRejectionSimulator

result = ReducedRejectionSimulator(seed=2).run()
print(result["accepted"], result["rejection_reason"])
print(result["cycles"][0]["gauged"]["records"])

if result["accepted"]:
    c = result["c_state"]       # SparseState: quantum C was not measured.
    print(c.norm_squared(), len(c.weights))
    column = c.to_scipy_column()
```

For a direct comparison, use
`ReducedRejectionSimulator(seed=2, extraction="verified_cat")` for the
previous profile. Both configurations execute physical gadgets.

Create a fresh simulator for each attempt. The CLI does this and streams
results so large intermediate stores are not retained across shots.
`observer(stage, runtime)` can inspect exact state probes at stage boundaries;
these are diagnostics, not extra physical measurements.

## Validation performed

Run the new tests and the shared backend's previous gadget tests:

```sh
"$HOME/pytket-venv/bin/python" -m pytest -q \
    src/test_c4_helix_optimized.py src/test_c4_helix_reduced.py \
    src/test_c4_helix_gadgets.py
```

The new checks cover:

- A nonuniform cat **prepared as an input state**, its measured nonzero ZZ
  vector, and the actual physical X gates that repair it before coupling.
- Small physical SWAP/Pauli cat gadgets against independent dense projectors,
  including interference in both measurement branches.
- Complete known-state correction of negative signs, including full raw-zero
  B/C preparation and graph sign-equation solutions.
- Agreement history limits, gauge-X masks, even Gauss correction patterns,
  and the distinction between an uncertified cycle and a negative certified one.
- Every production two-block lookup entry against the independent brute-force
  audit enumerating all 65,536 Paulis on each of ten fixed block sets.
- Genuine logical ambiguity and the worked joint B/C location example.
- Full current/compact graph schedules, exact output states, all intrinsic
  rejection branches, and the exact conditional B-zero probability \(5/6\).
- A fixed extra X gate that prepares a recovery-test input, followed by actual
  ungauging, joint correction, fresh graph preparation, and re-gauging while
  retaining B/C. This is a deterministic circuit fixture, not a noise model.
- Explicit serial waiting-qubit accounting, state-save roundtrips and
  deduplication, and detection of corrupted amplitudes or summary counts.
- Every compact source shape against an independent quantum projector and
  the exact primitive program used by its locality certificate.
- Two-zero-scan programs, nonzero-scan repair, flagged local source rebuilds,
  and matched current/compact trajectories with identical quantum outputs.

The combined command passed all **57 tests**. Saved optimized examples:

- [Four current-graph attempts](../output/c4-helix-optimized-current20-validation/summary.json).
- [Accepted current-graph attempt with complete trace](../output/c4-helix-optimized-smoke/summary.json).
- [Compact-graph attempt](../output/c4-helix-optimized-compact13-validation/summary.json).
- [Executed gate comparison by stage](../output/c4-helix-optimized-cost-comparison.json),
  verifying identical saved C amplitudes and the same twelve-SWAP count.

The retained baseline examples remain in
[the earlier run](../output/c4-helix-reduced-noiseless-v1/summary.json).
The optimized four-attempt example took about 12.4 seconds with about
641 MiB process peak RSS on this machine. Fewer physical gates do not
imply proportional simulator speedups: coherent overlaps and sparse-factor
caches also cost time and memory. These are measured examples, not
performance guarantees or a precise acceptance-rate estimate.

The [finite audit](check_optimized_extraction.py) and
[saved certificate](../output/c4-helix-optimized-extraction-certificates.json)
verify every accepted pair of merged local Pauli signatures for all six
source shapes and two-zero-scan cats of sizes 2--16. Idles, meter/report
errors, and arbitrary two-participant Pauli gate errors are included.
This is gadget-local analysis; the full composition argument is in the
updated proof. The exact ideal success probability remains \(5/8\).

## Boundary with the separate noise runner

The controller, report-only decoders, runtime, and sparse state backend
are separate modules. The new depolarizing runtime integrates noise at
this boundary; physical operation names and complete
waiting sets are retained even when an adaptive path takes extra rounds
or a fresh gauging cycle. Gates skipped by feedforward have no executed
locations. Classical lookups and read-only state diagnostics are not
counted as quantum gates.

The current idle counts are **one waiting location per nonparticipant
per serial physical operation**, not calibrated durations. No gate times,
T1/T2 values, readout/reset error rates, decoder latency, spatial scheduling,
or Fredkin decomposition errors have been calibrated. The manifest explicitly
records the atomic Fredkin assumption so it cannot be confused with a
hardware decomposition.

The present backend is exact for these real gates and trajectory-wise
Pauli operations. General complex channels or nonuniform Kraus amplitude
updates would require an extension of its integer-amplitude representation.
That choice belongs with the later noise-model specification. A trace
alone does not supply the correct quantum timing of a channel; the noisy
runner samples at the runtime's operation/idle boundaries before
destructive meters when appropriate.

The CLI's exact-target assertion is specific to this noiseless validation.
The controller's acceptance decision itself uses only measured records.
The separate noisy runner reports acceptance and decoded logical quality
separately: an accepted block can contain correctable physical errors and
therefore fail a raw exact-target comparison. Such a mismatch must not be
silently recategorized as rejection. The two-fault proof is also not a
guarantee for an unrestricted realistic-noise trajectory.

The [depolarizing guide](DEPOLARIZING_SIMULATION.md) describes the implemented
channel, accepted-state diagnostics, resource-failure accounting, and first
50-attempt pilot. The reduced number of locations remains a cost result,
not a proof of improved noisy acceptance: grouped controls also change
error correlations. A noisy baseline-versus-optimized comparison remains
to be performed.
