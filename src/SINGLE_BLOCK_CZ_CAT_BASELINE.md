# Matched twenty-qubit-cat CZ baseline

Entry point: [simulate_single_block_cz_cat_depolarizing.py](simulate_single_block_cz_cat_depolarizing.py).
It prepares the same encoded **two-logical-qubit CZ magic resource** as
the gauging runner, using the same canonical physical product of W'_q.

Shared conditional-gadget improvement: `--conditional-checks dual_flags`
saves 104 H in each complete one-remaining-fault data record, hence 208 H
for a minimum two-record data-flag repair. CX counts and peak qubits are
unchanged. This option is applied equally to gauging and this genuine-cat
factory. The [graph-assisted recovery benchmark](../notes/single_block_cz_graph_assisted_root_recovery.md)
includes cat legacy/dual arms to isolate its effect. This GHZ20 circuit
retains `--root-recovery reject`; the direct flagged-U control has its own
distinct root-recovery mechanism.

The [persistent-coordinate comparison](../notes/single_block_cz_persistent_coordinates.md)
keeps this genuine GHZ20 factory as one control arm. It also includes a
distinct **direct global flagged-U** control (`--route direct_cat
--direct-cz-extraction auto --verification-extraction flags` on the shared
entry point), with **1317 CX, 120 T/Tdg, 25 peak qubits** for compact data
checks and decoded source. That control does not prepare a cat. Including
it makes the new transported-Gauss meter comparison explicit.

The optional `--data-checks compact_flags` uses the same new Pauli-check
optimization as gauging. Its clean decoded-source cost is **1476 CX,
686 one-qubit Cliffords, 120 T/Tdg**, peak 41. The GHZ20 preparation and
logical-U measurement are unchanged. See the
[compact-check construction and matched benchmark](../notes/single_block_cz_compact_checks.md).

The separate file defines a small controller subclass. It reuses the exact
complex/cyclotomic backend, noise sampler, source encoder, source checks,
Pauli recovery, histories, process isolation, output diagnostics and saved
run format. It overrides only the logical-CZ measurement. No graph is
prepared or allocated. Changing `--graph` has no physical effect on this
baseline; it remains a reference field for the shared file format.

Unlike the historical `--route direct_cat` name alone, this entry point
**always uses an actual GHZ20 cat for CZ**, including when all other
checks use the current `flags` extraction. The shared runner also exposes
this choice as `--route direct_cat --direct-cz-extraction cat`.

## Physical schedule and guarantee

After matched source preparation, each complete direct-measurement round:

1. Measures the eighteen original code checks with the selected extraction.
   A nonzero syndrome uses the same certified one-block recovery table;
   ambiguous classes reject. Neither source logical X is remeasured.
2. Prepares twenty zero leaves, H on L0, then the nineteen chain CNOTs.
3. Uses the existing cat-bit verification/repair rule: two initially zero
   adjacent-ZZ scans stop; otherwise certify a commuting parity history
   under the selected triple/adaptive policy and physically repair leaves.
   Every verification meter and correction is a noisy physical operation.
4. Leaf Lq controls exactly one physical W'_q through T^epsilon, CX,
   T^-epsilon. This is twenty CX and forty physical T/T† gates, with
   individual noise locations and the canonical residual-Pauli correction
   already included in the signs. No atomic controlled-W or Fredkin is used.
5. Applies H and MZ to each leaf. The XOR of the **reported** twenty bits
   is the measured CZ sign. Actual outcomes and wrong reports are saved
   separately; the leaves are consumed and are not reused without PREP0.

Three passing complete code/CZ rounds within five accept; otherwise reject.
A genuine negative branch is never converted into the positive resource.
The ideal positive-branch probability is 3/4. Cat phase faults can alter
the I/U measurement branch, so one positive report alone is insufficient.

The global at-most-two-arbitrary-local-fault accepted-output theorem uses
the cat preparation/one-target-port lemmas from the
[conservative proof](../notes/full_procedure_single_block_cz_proof.md), the
[recovery composition](../notes/single_block_cz_simulation_recovery_proof.md),
and the [flagged Pauli-check lemma](../notes/single_block_cz_flagged_verification_proof.md).
Both routes have a clean complete certification round under that single
global budget. Later errors stay in the correctable physical weight-two
span. There is no fresh budget for cat preparation, retries or recovery.
This is an analytical composition, not a full-factory fault-pair enumeration.

## Matching a benchmark

From `/Users/kevinhemery/quanti/top-order-lit-rev`, run the cat baseline:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/simulate_single_block_cz_cat_depolarizing.py \
  --shots 100 --seed 100 \
  --profile recovery --history-policy triple \
  --verification-extraction flags --source-extraction rolling_flags \
  --two-qubit-infidelity 1e-3 --readout-flip-probability 1e-3 \
  --output-dir output/cz-comparison/cat
```

Run the current graph protocol with identical common settings:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/simulate_single_block_cz_depolarizing.py \
  --shots 100 --seed 100 --graph compact13 \
  --profile recovery --history-policy triple \
  --verification-extraction flags --source-extraction rolling_flags \
  --two-qubit-infidelity 1e-3 --readout-flip-probability 1e-3 \
  --output-dir output/cz-comparison/gauging
```

Use new output directories. Both expose identical Clifford, T/T†, idle,
preparation and report-noise parameters. The commands above leave Clifford,
T, preparation and memory noise explicitly at their shared zero defaults.
Add those channels identically when varying them. Average CX infidelity
r2 corresponds to nonidentity probability 5r2/4 on each physical CX.
Different circuits consume different random draws: the same seeds do not
make a paired-noise experiment. No trajectory is limited to two faults.

For the cheaper `decoded_flags` source, select that option on **both**
runners. Keep the same history policy, source, capacities, noise rates and
serial-idle convention. The differing measurement and certification
schedules are part of the two protocols and are counted in full.

The manifests identify `direct_cz_extraction="cat"`, the actual entry
point, all rates, limits, hashes and immutable runtime snapshots.
`graph_allocated=false` prevents mistaking the reference graph field for
allocated graph qubits. Root-cat decisions are labeled `verified_cat_CZ`.

Verify and aggregate without generating additional trajectories:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/compare_single_cz_runs.py \
  output/cz-comparison
```

Acceptance, decoded fidelity, unresolved attempts, rejection reasons and
executed costs are available in each summary and the comparison JSON.
Timeout/capacity failures are unresolved, never physical rejection.
Cost per accepted output is not labeled matched-fidelity unless such a
comparison has actually been established. No ranking is inferred by the tool.

## Reproducible clean counts and short checks

| Matched recovery source/checks | Graph compact13 | Actual cat baseline |
|---|---:|---:|
| CX | 3217 | **2124** |
| T/T† | 256 | **120** |
| PREP | 1172 | **842** |
| MZ | 1152 | **822** |
| Fixed one-qubit Cliffords | 1323 | **926** |
| Peak physical qubits | 39 | **41** |

Each cat-CZ measurement costs 115 CX on the clean path: 19 cat-chain,
76 ZZ verification, and 20 W ports. Three such measurements cost 345 CX.
The matched source costs 975 CX and three flagged code rounds cost 804,
giving 2124. With `decoded_flags` sources the cat total is 1716 CX and
the compact13 graph total 2809. These are per clean accepted attempt,
not noisy means, latency estimates or costs at matched noisy fidelity.

The previous fully flagged direct measurement remains available through
the shared runner with `--route direct_cat` and no forced cat extraction;
its clean count is 1965 CX. It is a separate comparator, not the GHZ20
baseline implemented by this file.

Generate only gate counts with the new runner's `--cost-only` option.
Short regression tests (no benchmark campaign) run with:

```sh
/Users/kevinhemery/pytket-venv/bin/python -m pytest -q \
  src/test_single_cz_cat_simulation.py src/test_single_cz_simulation.py
```

They check matched source/data gate lists, actual GHZ20 ports and readouts,
no graph allocation, exact elementary counts, noiseless decoded outputs,
cat-bit repair of a broad hook, wrong leaf reports, late two-site errors,
saved-record verification and execution from the saved runtime snapshot.
## Flag-dependent data recovery

`benchmark_single_cz_terminal_screen.py` compares the new ordered terminal
screen with the previous gauging history and this unchanged actual-cat
baseline. Generic syndrome recovery is matched across arms. The cat route
has no extra gauging-to-code terminal history to replace and does not
accept `--terminal-policy screen`.

The genuine-cat runner also accepts `--flag-recovery data` with ordinary
flag verification. It uses exactly the same Pauli-data recovery as the
gauging runner; its CZ measurement remains a genuine twenty-qubit cat.
Strict rejection remains `--flag-recovery reject`. Use
`benchmark_single_cz_flag_recovery.py` for a matched four-arm comparison.
See [the new procedure and proof](../notes/single_block_cz_flag_dependent_recovery.md).

