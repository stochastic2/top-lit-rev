# Single-block CZ depolarizing simulation

Entry point: [`simulate_single_block_cz_depolarizing.py`](simulate_single_block_cz_depolarizing.py).
It implements the [one-block gauging procedure](../notes/full_procedure_single_block_cz.md),
with a retained conservative profile and a recovery profile using flagged extraction by default.
The original two-block SWAP simulators are unchanged.

Optional graph-assisted root recovery: `--root-recovery joint
--conditional-checks dual_flags` on the compact round-trip gauging schedule.
This retains the four-data local Gauss meter and uses graph cycles to
resolve some flagged-root data ambiguities. Clean compact13 costs remain
1889 CX / 256 T/Tdg / 39 peak qubits. See the
[integrated circuit, proof and seven-arm benchmark command](../notes/single_block_cz_graph_assisted_root_recovery.md).
`benchmark_single_cz_root_recovery.py` compares reject/blind/joint graph
decoders, old/new genuine-cat conditional gadgets, and direct flagged-U
reject/recover controls. Defaults remain unchanged.

Optional persistent coordinates: `--gauss-frame persistent --graph-stars bare
--terminal-policy intrinsic --graph tree4 --data-checks compact_flags`.
With decoded source this uses **1421 CX, 160 T/Tdg and 30 peak qubits**.
It replaces repeated coordinate changes with a transported root-Gauss
measurement and coherent initial ungauging; disposal edge reports control
no second data correction. See the
[integrated schedule and proof](../notes/single_block_cz_persistent_coordinates.md).
`benchmark_single_cz_persistent.py` compares old gauging, persistent compact13,
persistent tree4, GHZ20 cat and the direct flagged-CZ alternative. Tree4
is allowed only with this intrinsic persistent tail; its cut distance is one.

Optional `--data-checks compact_flags` reduces each ordinary post-source
code record from 268 to **188 CX**, 140 to **60 Clifford gates**, and 100
to **60 preparations/MZ**. The source, ordered terminal screen and W
gadgets retain their separate schedules. See the
[circuits, proof and certificate commands](../notes/single_block_cz_compact_checks.md).
`benchmark_single_cz_compact_checks.py` compares old/new checks for both
gauging and genuine-cat factories at matched noise settings. Defaults
remain unchanged.

The default output is the encoded **two-logical-qubit CZ magic resource**.
The default graph is compact13 and its gauge edges are read destructively
in Z. The old SWAP simulator's optional final Y/Z single-qubit output is
not substituted for this resource.

## Run and verify

From `/Users/kevinhemery/quanti/top-order-lit-rev`:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/simulate_single_block_cz_depolarizing.py \
  --shots 8 --graph compact13 --profile recovery \
  --two-qubit-infidelity 1e-3 --readout-flip-probability 1e-3 \
  --output-dir output/my-one-block-cz

/Users/kevinhemery/pytket-venv/bin/python -B src/verify_single_block_cz_run.py \
  output/my-one-block-cz
```

Choose a new output directory; existing runs are never overwritten.
Set `--graph current20` for the existing twenty-edge geometry, or
`--profile conservative` for the original postselection schedule.
`--route direct_cat` supplies the fair normalized-W direct measurement
baseline. The route name is historical: with default flag extraction, this
route uses a twenty-port flagged measurement, not a twenty-leaf cat.
For a genuine cat-state benchmark with matched source and data checks,
use the separate [cat baseline runner and commands](SINGLE_BLOCK_CZ_CAT_BASELINE.md).
Use `--cost-only` to generate elementary clean schedules and
resource counts without quantum sampling.

Recovery defaults to `--verification-extraction flags` and
`--source-extraction rolling_flags`. There is no separately prepared
verification-cat resource. A syndrome ancilla and up to three live flags
are temporarily entangled, then decoded/read and reused. Select
`--verification-extraction cats` to reproduce the previous protection;
its default source is the earlier `decoded_flags` option.

Runtime needs Python and NumPy; it does not require Guppy, Stim or SciPy.
The existing `/Users/kevinhemery/pytket-venv/bin/python` environment supplies
NumPy and pytest. Tests and finite certificates run with:

```sh
/Users/kevinhemery/pytket-venv/bin/python -m pytest -q src/test_single_cz_simulation.py
/Users/kevinhemery/pytket-venv/bin/python -B src/check_single_cz_recovery.py
/Users/kevinhemery/pytket-venv/bin/python -B src/check_single_cz_flags.py \
  --output output/single-cz-flag-certificates.json
/Users/kevinhemery/pytket-venv/bin/python -B src/check_single_cz_graph_parity.py \
  --output output/single-cz-graph-parity-certificates.json
```

## Actual noise and physical gates

Every controlled W remains the actual T^s, CX, T^-s decomposition. No atomic
controlled-W, Fredkin or CCZ location replaces it. Noise is sampled after
each executed physical gate, including corrections and failed/retried
preparations; reports flip only after the actual quantum measurement.
Noise draws and Born draws have separate seeded streams. No trajectory
is capped or filtered by its number of faults.

| Parameter | Meaning/default |
|---|---|
| `--two-qubit-infidelity` | Average CX infidelity, default 1e-3; nonidentity Pauli probability 5r2/4 |
| `--readout-flip-probability` | Independent report flips, default 1e-3 |
| `--one-qubit-infidelity` | Average Clifford/Pauli-gate infidelity, default 0 |
| `--t-infidelity` | Average T/T† infidelity, default inherits the one-qubit rate |
| `--idle-infidelity` | Average single-qubit infidelity per serial waiting interval, default 0 |
| `--preparation-flip-probability` | X after zero preparation, default 0 |

One-qubit depolarization has total nonidentity probability 3r1/2, with X/Y/Z
uniform. Two-qubit errors are uniform over all fifteen nonidentity Pauli
products, including both single-participant and correlated errors. Idles
occur on every live nonparticipant before each serial operation and on
every live qubit at explicit boundaries, including final handoff.
These are counted operation intervals, not calibrated physical durations.

For a multichannel check, for example:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/simulate_single_block_cz_depolarizing.py \
  --shots 2 --two-qubit-infidelity 1e-4 --readout-flip-probability 1e-4 \
  --one-qubit-infidelity 1e-5 --t-infidelity 1e-3 \
  --idle-infidelity 1e-6 --preparation-flip-probability 1e-4 \
  --output-dir output/my-one-block-multichannel
```

Zero T or memory rates are explicit experimental assumptions, not claims
that these channels are physically harmless. The manifest records every rate.

## Recovery choices and their guarantees

The [recovery composition](../notes/single_block_cz_simulation_recovery_proof.md)
and [flagged-gadget proof](../notes/single_block_cz_flagged_verification_proof.md) keep the global two-fault accepted-output guarantee while changing:

1. **Known source flags.** Measure all twenty source constraints using the
   same flagged primitive. Only this known unused source can be rebuilt
   on a flag; an unknown magic block is never re-encoded. The optional
   `--source-extraction decoded_flags` retains the earlier small grouped
   source gadget; it uses transient fanout correlations, with no cat verification.
2. **Flagged product measurements.** Four-port uniform Pauli checks cost
   six CX with one flag. Other m-port checks cost 3m+2 CX and use a
   syndrome ancilla plus at most three simultaneous flags. Two flags are
   active at each target port; the next opens before the oldest closes.
   After source preparation, any reported flag rejects the attempt. There
   is no cat fallback. Nonzero syndromes with zero flags still use recovery.
   The retained `cats` option uses the old two-zero-scan/cat-repair gadget.
3. **Known-source recovery and direct graph parity verification.** Correct
   a certified source syndrome. For the graph, measure only
   L_e=Z_(a_u)Z_(A_e)Z_(a_v), using PREP0(w), three resource-to-w CNOTs,
   and MZ(w). Three complete zero scans accept; a nonzero scan rebuilds
   only the unused graph. Known resources share two bounded retry tokens.
   There are no graph-verification cats, K_v checks, or graph sign corrections.
   Graph phases are allowed: V Omega |t,dt>|psi> = |t,dt> U^(t_a)|psi>.
   The later combined Gauss rounds certify the positive logical sector.
4. **Single-block data recovery.** On a nonzero code record, acquire a
   commuting whole-code reference in V coordinates. Correct only if all
   compatible errors on two unknown inner blocks have one stabilizer class.
   All 655360 two-block Paulis are audited. Ambiguities still reject.
5. **Cycle correction.** Certify the commuting cycle vector before applying
   edge-X corrections. Radius is two for compact13, three for current20.
6. **Deferred parity and passing rounds.** A reported negative vertex parity
   no longer immediately discards data. Three positive combined gauged rounds
   within five certify magic. A recovered nonzero syndrome can pass, provided
   its correction is certified and the root report is positive. This never
   repairs a genuine negative logical CZ eigenvalue into positive.
7. **Terminal recovery.** Certify eighteen original code checks and apply the
   same unambiguous one-block decoder. Neither source logical X is measured
   again. Late correction and final idle errors remain in the correctable
   physical weight-two span under the global two-fault assumption.

Default `--history-policy triple` uses three consecutive identical **whole**
records within nine. `--history-policy adaptive` uses the five-record
combinatorial clean-reference certificate. Both are restricted to globally
commuting subfamilies. The combined dressed data/root-Gauss measurements
use the separate passing-round argument; they are not assumed to commute
on erroneous Z sectors. Under unrestricted noise, compare decoded fidelity
as well as yield when choosing history policy.

There is a real rejected optimization: measuring code and physical CZ in
separate certified stages can falsely accept a negative decoded state after
one intervening data fault. The new independent test constructs this
counterexample. The implemented combined-round rule avoids that assumption.

## Graph and clean-cost comparison

`--terminal-policy screen` is an opt-in replacement for the gauging route's
extra certified terminal history. One all-zero outer-Z/outer-X/inner-Z/inner-X
record suffices under the proved block-to-physical-error lemma. Nonzero
syndromes use the same full recovery as the comparator. A data flag uses
the existing flag-conditioned repair and then a fresh verification screen;
failed verification invokes full recovery. No extra CZ measurement is used.
With decoded source and bare stars the clean counts are 2129/2299 CX for
compact13/current20, with 256 T/T† and unchanged 39/46 peak qubits.
See [the version-3 procedure and proof](../notes/single_block_cz_terminal_screen.md)
and `benchmark_single_cz_terminal_screen.py`. Default terminal policy remains
`certified`. The comparison reports successful-attempt lengths separately
from total CNOT spending per accepted output.

`--graph-stars bare` is now an opt-in alternative for the gauging/recovery
route with ordinary flag extraction. It measures nonroot X stars with one
bare meter, omits per-round cycles, then certifies and repairs the complete
cycle vector using non-tree edges before destructive edge readout. It
composes with `--flag-recovery data`; root flags retain rejection.
With decoded source it costs 2665/2835 CX for compact13/current20, with
unchanged 256 T/T† and 39/46 peak qubits. Add 408 CX for rolling source.
The tables below retain the previous `--graph-stars flags` reference.
See [the schedule/proof](../notes/single_block_cz_bare_graph_stars.md) and
`benchmark_single_cz_graph_stars.py` for the matched three-arm comparison.

Optional `--flag-recovery data` recovers unambiguous flags on the eighteen
Pauli data stabilizers. The strict default is `--flag-recovery reject`.
After a flag, conditional one-remaining-fault checks cost 140 CX per whole
record; two identical records certify a reference. Ambiguous table rows,
new fallback flags and Gauss/star flags still reject. Corrections restart
the interrupted row and any enclosing syndrome history. The bounded
`--max-flag-recoveries` default is eight; this does not change the theorem's
two-fault **global** budget. All noise remains uncapped.
See [the procedure and proof extension](../notes/single_block_cz_flag_dependent_recovery.md)
and `benchmark_single_cz_flag_recovery.py` for a four-arm comparison using
the same extension on the actual-cat baseline. Clean-path counts below
are unchanged; executed-cost reports include every fallback and rejection.

Both graphs implement the same signed logical observable and ideal 3/4
projector. All counts are generated from actual elementary schedules.

| Quantity | compact13 | current20 |
|---|---:|---:|
| Edges + vertices | 13+5 | 20+5 |
| Degrees | 6,5,5,5,5 | 8,8,8,8,8 |
| Independent cycles | 9 | 16 |
| Classical cut distance | 5 | 8 |
| Recovery-profile edge/cycle radius | 2 | 3 |
| Correctable edge-X patterns | 92 | 1351 |
| Correctable cut-neighborhood words | 1472 | 21616 |
| Positive gauged-code distance | 6 | 6 |
| Graph preparation + three parity scans, CX | 143 | 220 |
| Default flagged recovery peak qubits | 39 | 46 |
| Conservative / cat-recovery peak qubits | 44 | 53 |
| Conservative clean CX | 8724 | 9302 |
| Default flagged recovery clean CX | **3217** | **3459** |
| Previous cat-recovery clean CX | 4810 | 5268 |
| Recovery clean T/T† | 256 | 256 |

The extra redundancy in current20 can recover an additional independent
edge report flip. It costs 242 more default flagged CNOTs and seven
more peak qubits. This does not establish a three-circuit-fault theorem,
or prove which graph wins at matched noisy output fidelity.

At zero-feedback clean acceptance, flagged compact13 uses 1172 preparations,
1152 measurements and 1323 one-qubit Cliffords; ideal mean feedback adds
18 Cliffords and 368 serial idles. Current20 uses 1263 preparations,
1243 measurements and the same 1323 fixed Cliffords. T/T† remain 256.
The peak is graph preparation with its one parity helper: 20+18+1=39,
or 20+25+1=46. Other checks need at most four helpers, independently of arity.

The new source uses 308 CX per complete twenty-check round; the earlier
known-source `decoded_flags` option uses 172 and remains certified. With
that option and otherwise flagged extraction, compact13 costs 2809 CX,
current20 3051 CX, and the direct comparator 1557 CX. The uniform default
avoids the earlier source fanout circuit; these alternate counts are not
noisy-yield measurements or an optimality claim.

For comparison, the immediately preceding parity-verified graph with cat
extraction used 4810/5268 CX and 44/53 peak qubits. Replacing those checks
with default flags saves 1593/1809 CX, or 33.1%/34.3%. It removes repeated
cat verification scans but introduces strict rejection on flags. The new
pilot did not show an acceptance boost; see the [results](../notes/single_block_cz_simulation_results.md).

The equally configured **direct flagged CZ measurement** uses 1965 CX,
120 T/T†, 869 one-qubit Cliffords, 734 preparations, 714 measurements and
24 peak qubits. Both routes share the physical alphabet, source, noise
parameters and global two-fault accepted-output guarantee. This reconstructed
baseline is not a published circuit budget from the C4-Helix paper.

## State representation and fidelity diagnostics

One term is an exact cyclotomic coefficient times an explicit helper-basis
word and a sparse data ket. The helper words form a **coherent sum**;
different data factors interfere in Born probabilities. Every T gate acts
on eighth-root phases. Arbitrary sampled Pauli faults are inserted at the
individual physical locations. No Pauli XOR approximation is made across
the T/CX/T† sequence.

Coefficients, overlaps and Born norms use integer arithmetic in Z[zeta8].
Rational Born draws use exact integer Bernoulli sampling; irrational draws
compare lazy random-bit intervals to exact a+b sqrt(2) signs. After complete
code extraction, an optional exact Walsh change into the full CSS basis
reduces redundant coherent terms. It retains all syndromes and logical
amplitudes, adds no quantum gates, and supplies no state information to the
controller. The tests check this identity independently.

Only the saved output and read-only logical-density diagnostics use
complex128. Exact cyclotomic normalization precedes that conversion. Perfect
syndrome decoding uses a fixed physical-radius-two table, then a fixed GF2
fallback for every other sector. Its target is (1,1,1,0)/sqrt3. It is not an
ideal physical recovery inserted into the noisy circuit. Raw physical overlap,
decoded fidelity, syndrome mass and the complex logical density matrix are
reported separately.

The backend supports the factory's port ordering and Pauli trajectories,
not unrestricted interleaved Clifford+T circuits. An H on a nonflat factor
outside that invariant raises a backend error instead of approximating it.
`--max-terms`, `--max-factors`, `--max-operations`, and `--attempt-timeout`
bound computation. Exceeding them is **unresolved**, never physical rejection.

## Saved data and interpretation

Each attempt is isolated in its own process. The run contains:

- `manifest.json`: exact graph, source extraction, history/terminal policy,
  explicit graph-verifier policy, noise rates, seeds, capacities, code hashes
  and Python/NumPy versions.
- `source_snapshot/`: the runtime sources used to reproduce the run.
- `clean-costs.json`: counts from actual elementary gate lists.
- `shots.jsonl` and `summary.json`: every attempt, unresolved bounds, rejection
  reasons, accepted fidelity statistics and executed cost per accepted output.
- `attempts/.../controller.json`: reported histories, flags, corrections,
  passing-round decisions, vertex and edge records.
- `measurements.json`: actual and reported outcomes, separately.
- `noise.json`: every sampled event, with participants and Pauli axes.
- `output.npz`: normalized complex sparse output for each diagnosed acceptance.
- `events.jsonl` if `--trace`: elementary operations, exact Born norms and noise.

Attempt k uses Born seed `seed+k`; noise uses `noise_seed+k` or a documented
SHA256-derived seed. Different graphs/profiles consume different draws,
so matching seeds do not constitute a paired-noise experiment.

The verifier recomputes controller certificates, correction decisions,
readout-flip accounting and output diagnostics from files. It reports source
drift and missing diagnostics. It is not a full elementary-gate replay tool.
The summary keeps unresolved computations and unavailable accepted diagnostics
out of unjustified rejection/fidelity estimates, and records any observed
accepted violation with at most two sampled/injected fault locations.

Cost per accepted output includes rejected completed attempts. It is explicitly
not labeled a matched-fidelity comparison. Small implementation pilots can
establish execution and expose rejection bottlenecks; they cannot establish
a graph's statistically significant yield or fidelity advantage.
