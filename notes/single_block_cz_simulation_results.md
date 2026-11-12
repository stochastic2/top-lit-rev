# One-block CZ simulation: implementation and initial graph comparison

## Current default: flagged verification throughout

The default recovery mode now replaces all separately prepared verification
cats with a syndrome ancilla and flags. Three resource Z scans remain,
and cycle Z checks use direct meters. Uniform four-port Pauli checks cost
six CX; other m-port checks cost 3m+2 CX with at most three live flags.
Small flags are temporarily entangled; the claim is absence of a large
cat resource/verification stage, not absence of GHZ-type correlations.

| Default flagged schedule | CX | T/T† | PREP | MZ | Fixed 1q Clifford | Peak live |
|---|---:|---:|---:|---:|---:|---:|
| compact13 gauging | **3217** | 256 | 1172 | 1152 | 1323 | **39** |
| current20 gauging | **3459** | 256 | 1263 | 1243 | 1323 | **46** |
| Direct flagged CZ comparator | 1965 | 120 | 734 | 714 | 869 | 24 |

These lists include the default uniform flagged source (975 CX including
encoding). With the earlier `--source-extraction decoded_flags` option,
the totals are 2809, 3051 and 1557 CX respectively; that option retains
small source fanout correlations with decoded flags and no cat verification.
The historical CLI name `--route direct_cat` uses a twenty-port flagged
measurement when flag extraction is selected. T gates remain individual
physical locations in both routes.

Compact13 stage costs changed as follows:

| Stage | Previous cat extraction | Default flags |
|---|---:|---:|
| Source including encoding | 567 | 975 |
| Graph preparation/verification | 143 | 143 |
| Enrichment | 20 | 20 |
| Coordinate passes | 96 | 96 |
| Three gauged code records | 1602 | 804 |
| Cycle checks | 315 | 75 |
| Nonroot stars | 300 | 204 |
| Root Gauss checks | 165 | 96 |
| Terminal recovery | 1602 | 804 |
| **Total CX** | **4810** | **3217** |

The net savings are 33.1% on compact13 and 34.3% on current20 relative
to the immediately preceding parity-verified graph/cat-extraction mode.
Default fixed serial idle counts are 193403 and 233207; ideal mean
feedback adds eighteen Cliffords and 368 idles. Peak graph preparation
uses one helper; every later flagged check uses at most four.

The [new proof](single_block_cz_flagged_verification_proof.md) transfers
the same global two-arbitrary-fault accepted-output guarantee using an
exact local-port support lemma, rather than a Pauli-XOR model of W ports.
All twenty actual gadget configurations have finite single/pair support
certificates. Independent Clifford propagation and dense complex mixed-W
Kraus/fault tests provide separate checks. Nonzero flags after source
preparation reject; no unknown magic block is reset or sent to a cat fallback.

### Small pilot: lower gate count did not boost observed acceptance

Sixteen attempts per graph were run at r2=q=1e-3, other channels explicitly
zero. Both graphs accepted **2/16**, with all four outputs matching the
decoded target within 1e-10. There were no unresolved computations.
Acceptance was 12.5%, Wilson95 [0.035,0.360], versus 3/8 in the earlier
cat-extraction pilot. Schedules consume different random draws, so these
are not paired-noise trajectories. The samples cannot establish a yield
or output-fidelity ranking, and they do not demonstrate an acceptance boost.

Most rejections are now flag rejections: the conservative first version
discards a flagged magic-data attempt rather than attempting an uncertified
repair. Less gate noise alone does not guarantee more outputs. A future
flag-and-syndrome recovery table would need its own accepted-ambiguity
certificate before such flags could be retained safely. No such repair
is silently assumed here.

The [saved runs and manifests](../output/single-cz-flags-pilot/README.md)
and [verified comparison](../output/single-cz-flags-pilot/comparison.json)
retain all attempts, actual outcomes, reports, decisions, errors and complex
outputs. Sample CX per nominal accepted output is 21127.5 / 23137; these
are not matched-fidelity resource estimates. Earlier accepted failures
and all previous source snapshots remain preserved below.

## Previous implementation: direct graph Z parities with cat extraction

The graph verifier has been replaced in both profiles by three complete
all-zero scans of Z_(a_u)Z_(A_e)Z_(a_v). Each check uses one fresh helper,
three resource-to-helper CNOTs and Z readout. Nonzero scans rebuild only
the unused graph with the shared retry budget. There are no graph-check
cats, preparation-stage K_v checks or graph sign corrections. The
[revised C3 proof](full_procedure_single_block_cz_proof.md#c3-known-source-and-graph-verification)
shows that a rank-32 cut-subspace reference with arbitrary phases suffices.

| Current recovery schedule | Graph stage CX | Total clean CX | T/T† | Peak live qubits |
|---|---:|---:|---:|---:|
| compact13 | 143 | **4,810** | 256 | **44** |
| current20 | 220 | **5,268** | 256 | **53** |
| Same direct-cat comparator | — | 2,514 | 120 | 41 |

Relative to the previous graph verifier, this saves 873 CX (15.4%) on
compact13 and 1335 CX (20.2%) on current20, and two peak qubits on each.
The conservative schedules now cost 8724 and 9302 CX. These are counts
from executed elementary gate lists with zero feedback, not noisy means.

Current compact13 recovery also uses 2288 preparations, 2268 measurements,
2166 fixed one-qubit Cliffords, and 369464 serial idle locations. Ideal
mean feedback adds eighteen Cliffords and 368 idles. Current20 uses
2517 preparations, 2497 measurements, 2346 fixed Cliffords and 465818 idles.
Physical slots allocated with reuse equal the peak counts; preparation
counts include every subsequent reset.

The new independent [graph certificate](../output/single-cz-graph-parity-certificates.json)
checks both constraint ranks, all 1024 Walsh inner products per graph,
all 32 coordinate patterns, 96 local Pauli/report meter cases and their
1024 merged-signature pairs, and independently reconstructs both emitted
graph programs. It explicitly allows broad phase errors. Factory
composition remains analytical; no complete factory fault-pair enumeration
is claimed. Tests include a coherent T error on the helper at one CNOT
location, graph retries, and two late bit faults after the last clean scan.

### New small noise pilot

Eight attempts per graph were run with r2=q=1e-3, other channels explicitly
zero, starting Born seed zero and the separate hashed noise seeds. Every
attempt completed; none were unresolved. All saved output diagnostics and
report/control certificates were independently rechecked from disk.

| Direct-parity graph run | Accepted / attempted | Target matches / accepted | Sample CX / nominal acceptance |
|---|---:|---:|---:|
| compact13 recovery | 3 / 8 | **2 / 3** | 26,154.3 |
| current20 recovery | 3 / 8 | **3 / 3** | 21,470 |

Compact13 shot 7 accepted but decoded to **|11>**, with CZ-magic fidelity
zero. It contained **23 sampled noise events**; its graph-parity scans
were all zero, and three of four complete gauged rounds passed. The two
other compact13 acceptances and all three current20 acceptances matched
the target within 1e-10. There was no observed accepted violation with at
most two faulty locations. The failing shot is retained with its actual
measurements, reports, recovery decisions, sampled errors and complex ket;
it is not removed from the acceptance or fidelity statistics.

Consequently the sample mean decoded fidelities are 2/3 and 1. This is
**not** a matched-fidelity cost comparison, and eight attempts cannot
establish a graph advantage or a population error rate. The 95% Wilson
acceptance interval is [0.137,0.694] for both. Different schedules consume
different Born/noise draws even with the same starting seed; this is not
a paired-noise before/after comparison. In particular, a shorter clean
circuit does not imply that unverified graph phases improve noisy output
quality. The global two-fault theorem and unrestricted stochastic
performance are different claims.

The [saved comparison](../output/single-cz-parity-pilot/comparison.json)
and [run index](../output/single-cz-parity-pilot/README.md) contain the current
results and source snapshots. Reverify without new sampling:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/compare_single_cz_runs.py \
  output/single-cz-parity-pilot
```

The sections below preserve the **historical full-stabilizer/cat-verifier**
pilot and its costs. Its saved runtime sources remain immutable; those
numbers are not current counts and must not be pooled with new runs.

## Historical implementation and initial pilot

The [runner and commands](../src/SINGLE_BLOCK_CZ_SIMULATION.md) implement
both compact13 and current20, with Z-basis edge readout and the encoded
two-logical-qubit CZ-magic target. The original conservative controller and
two-block SWAP simulator are preserved. The
[recovery proof extension](single_block_cz_simulation_recovery_proof.md)
states the global two-fault guarantee for the optimized controller.

## Implemented yield changes

The recovery profile retains nonzero **certified** source and graph
syndromes, repairs cat bits, uses decoded source flags, defers vertex
parity, and corrects unambiguous single-block data/cycle syndromes. It
does not use the old joint B/C decoder. It certifies three passing combined
gauged rounds within five, then performs certified terminal Pauli recovery.
Source logical X checks are never repeated after magic preparation.

The actual finite certificates include expanded H/CX/H source-Z gadgets,
the two-zero cat shortcut, every fixed-two-block Pauli against the recovery
decision, commuting-history hypotheses, passing-round fault placements,
and both complete correctable cut neighborhoods. They are saved in
[`single-cz-simulation-certificates.json`](../output/single-cz-simulation-certificates.json).

The simulator keeps complex phases and exact integer arithmetic in
Z[zeta8]. It executes and noises each individual T/CX/T† location. Exact
coherent CSS-basis compression improves runtime without projecting onto
any syndrome or applying an ideal correction. Only the final saved
wavefunction and read-only density-matrix diagnostics use complex128.

An independent counterexample test ruled out a tempting shortcut:
separate positive physical-CZ certification can accept a state that
ordinary recovery decodes to the negative logical branch after one fault.
The combined-round certificate in this implementation avoids that error.

## Historical clean elementary schedules: cat-verified graph

| Profile and graph | CX | T/T† | Peak live qubits |
|---|---:|---:|---:|
| Conservative compact13 | 9,909 | 256 | 46 |
| Recovery compact13 | **5,683** | 256 | 46 |
| Conservative current20 | 11,117 | 256 | 55 |
| Recovery current20 | **6,603** | 256 | 55 |
| Equally optimized direct cat | 2,514 | 120 | 41 |

Recovery compact13 uses 2771 preparations, 2751 physical measurements,
and 2664 one-qubit Cliffords before ideal record-dependent feedback
(mean eighteen more Cliffords). These are clean-attempt counts, not
noisy averages or cost per accepted output.

## Historical small validated noise pilot

The graph/profile pilot uses average CX infidelity r2=10^-3, uniform
nonidentity Pauli probability 5r2/4, and independent readout-report flips
q=10^-3. Clifford, T/T†, memory and preparation noise are explicitly zero
in this comparison. Born seeds start at zero with separate hashed noise
seeds. Different schedules consume different draws; this is not a paired
noise experiment.

| Graph/profile | Accepted / attempted | Accepted trajectories matching target within 10^-10 | Sample CX / accepted |
|---|---:|---:|---:|
| compact13 conservative | 0 / 4 | — | — |
| current20 conservative | 0 / 4 | — | — |
| compact13 recovery | 3 / 8 | 3 / 3 | 29,624 |
| current20 recovery | 3 / 8 | 3 / 3 | 31,322 |

All twenty-four attempts completed; none were reclassified computational
failures. All conservative attempts stopped in source preparation, so
those rows do not supply graph-level performance information. Recovery
acceptances contained ten to twenty-two sampled noise events; the simulator
did not impose a two-fault cap. Their observed decoded fidelity was one
within the numerical tolerance. That observation on three outputs per
graph does not establish the population logical-error rate or fidelity one.

The 95% Wilson acceptance interval for each 3/8 recovery result is
approximately [0.137,0.694]. For 0/4 it is [0,0.490]. These intervals are
wide. The pilot demonstrates working noisy recovery and exposes rejection
bottlenecks; it does not establish a statistically significant yield
advantage or a matched-fidelity cost advantage.

Validated records, physical measurement outcomes, noise events, complex
outputs, code hashes and source snapshots are under
[`single-cz-validated-pilot`](../output/single-cz-validated-pilot/).
The read-only [comparison JSON](../output/single-cz-validated-pilot/comparison.json)
also includes a separate multichannel implementation check and a tiny
direct-cat execution check; neither is pooled into the graph table.

Rebuild its verification/aggregation without resampling:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/compare_single_cz_runs.py \
  output/single-cz-validated-pilot
```

Earlier exploratory outputs under `single-cz-implementation-smoke` and
`single-cz-implementation-pilot` predate the final recovery policy. Their
manifests retain the differing code hashes. They are not pooled with this
validated comparison.

## What the twenty-edge graph provides

Current20 is a valid double-K5 choice for this one-block construction:
all degrees are eight, its cycle rank is sixteen, its cut distance is
eight, and its positive gauged-code distance is six. Its radius-three
decoder covers 1351 edge-error patterns and 21616 cut-neighborhood
words. Compact13 has cut distance five, cycle rank nine and the same
gauged distance six; it covers 92 patterns and 1472 cut-neighborhood
words at radius two.

Thus current20 can retain a three-edge-readout-flip record that compact13
cannot uniquely recover. This extra redundancy cost 920 clean recovery
CNOTs and nine peak qubits in the historical schedule; the current extra
cost is 458 CX and nine peak qubits. It does not extend the circuit theorem to
three arbitrary faults. In the pilot all six accepted edge records were
already at distance zero from their decoded cuts, so the additional
radius was not exercised at final readout in those accepted shots.

Compact13 remains the default because of its smaller clean circuit.
Current20 remains a supported comparison with stronger classical edge
redundancy. The present data do not show that it improves noisy yield;
ranking the graphs needs a larger comparison at matched decoded fidelity,
with T and memory noise included if making a hardware-level conclusion.
# Flag-dependent recovery pilot, 10 November 2026

The opt-in `--flag-recovery data` implementation now uses a flag/syndrome
unique-class decoder for Pauli data checks. Its conditional fallback has
one flag per check, a 140-CX complete record, and two matching records.
The bounded episode limit defaults to eight; the proof still assumes
two faults globally. Clean-path counts and peaks are unchanged.

The final matched 40-shot pilot at r2=q=0.001, with all other channels
zero, accepted 2→7 gauging outputs and 5→16 genuine-cat outputs when
switching from strict rejection to recovery. All accepted saved states
matched the decoded target within tolerance; no attempt was unresolved.
Executed CX per accepted output changed from 37245.5→21563.0 for gauging
and 14631.8→7376.3 for the cat route. These are small-sample observations,
not a matched population-fidelity guarantee. The cat route benefits too
and remains cheaper in this pilot.

See [the procedure/proof and commands](single_block_cz_flag_dependent_recovery.md)
and `output/single-cz-flag-recovery-bounded8-pilot-20261110/comparison.md`.
This pilot is separate from earlier versions and is not pooled with them.

# Bare graph stars, 10 November 2026

The opt-in `--graph-stars bare` schedule now removes nonroot-star flags
and defers certified cycle correction to before edge readout. Corrections
are restricted to non-tree edges, so they commute with V and do not act
on data. The global two-fault theorem is extended in
[the dedicated note](single_block_cz_bare_graph_stars.md).

With decoded source, clean compact13 falls from 2809 to 2665 CX; current20
falls from 3051 to 2835 CX. T counts and peak qubits are unchanged.
The separate 40-shot matched pilot accepted 7 previous-star gauging,
8 bare-star gauging and 16 genuine-cat outputs; all decoded outputs
matched the target. This sample is too small to establish a yield or
population-fidelity advantage. The clean gate savings are exact.
See `output/single-cz-bare-star-pilot-20261110/comparison.md` and
`src/benchmark_single_cz_graph_stars.py` for a larger comparison.

