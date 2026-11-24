# Adaptive whole-record syndrome histories

The historical experiments below use `--magic-output z`. The simulator
now defaults to the [Y-output profile](MAGIC_Y_SIMULATION.md); add the Z
option when reproducing these old targets and comparisons.

The new `--history-policy adaptive` replaces three consecutive identical
records with a certificate using the whole history. It applies to source
and graph preparation, gauged verification, terminal recovery, and cat
repair. It retains the graph, physical gadgets, gauging/ungauging, correction
lookups, and ideal 5/8 success.

**The simulator default remains `triple`.** The adaptive policy preserves
the analytical two-fault guarantee, but the high-noise experiment also
found an imperfect accepted output. Choose the policy explicitly when
comparing acceptance and logical quality.

## Run it

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_depolarizing.py \
    --shots 50 --seed 0 --two-qubit-infidelity 8e-4 \
    --history-policy adaptive --output-dir output/my-adaptive-8e-4

"$HOME/pytket-venv/bin/python" src/verify_c4_helix_depolarizing_run.py \
    output/my-adaptive-8e-4
```

Use a new output directory. For the previous rule, pass
`--history-policy triple`. The option also works in
`simulate_c4_helix_reduced.py` and both simulator Python constructors.
The policy is saved in manifests, shot records, and summaries. Older
manifests without a policy field mean `triple` and remain verifiable.

## A concrete example

Let A, B, C denote different **complete** syndrome vectors:

```text
round:  1  2  3  4  5
record: A  B  B  C  C
```

The previous rule continues because no triple agrees. The adaptive rule
stops at five and uses C. Assume at most two faulty locations in the full
circuit. Two adjacent clean rounds must agree, so the A-to-B change requires
a fault in round 1 or 2. At most one fault remains. Both C rounds cannot
be bad, and therefore one C is a true reference syndrome. The controller
does not know which C was clean.

Similarly, `0,s,0,0`, for nonzero s, stops at four: zero occurs three times,
which cannot all be bad rounds. Clean identical records still stop after
three rounds, so the clean resource count is unchanged.

## The exact decision

After each complete round, without intermediate correction:

1. Mark every boundary where consecutive whole records differ.
2. List all sets of at most two bad rounds touching every marked boundary.
3. For each observed record, collect all its occurrence indices.
4. Certify it if no compatible bad-round set contains all its occurrences.
5. Stop at the first certified prefix, preferring the usable vector whose
   latest occurrence is most recent.

The list of compatible sets is nonempty for prefixes of at most five
rounds. Every five-round history has a certificate, proved in
[Section 2 of the updated proof](../notes/full_procedure_reduced_rejection_proof.md#2-a-certified-record-supplies-a-clean-reference-round).
The saved `reference_certificate` lists changed boundaries, compatible
bad-round sets, selected occurrences, the selected record index, and the
minimum bad-round count needed to declare every occurrence bad. Indices
are zero based; that minimum is at least three.

Only measured reports enter this decision. It does not consult actual
meter bits, sampled faults, or the wavefunction, or assemble different
syndrome bits from different times.

The ideal complete families commute, including the non-Pauli Gauss
involutions. A clean round has the required projective action and two
adjacent clean rounds agree. This establishes the certificate directly
for this circuit. The remaining proof uses a genuine reference syndrome
and charges later errors to the remaining global fault budget. It does
not require three consecutive copies or a clean final round.

## Cat repair and saved histories

The two-initial-zero-scan shortcut remains. Otherwise retain those scans
in adaptive history, stop by scan five, and apply the selected physical
X repair before coupling. Source flags still rebuild only the unused
known source.

Outer sections save full `records`, `rounds_used`, `stopping_record`, policy,
and certificate. Cat scans and certificates appear in the optional physical
trace. Verifiers replay the report-only selector, enforce the first stopping
prefix, and check the certificate. The noisy verifier also checks unfinished
outer histories when a physical stage rejected.

With unrestricted noise, the rule still stops within five rounds. Removing
`unstable_record` rejection does not alone establish improved logical yield:
with more than two faults, the certificate's clean-reference premise can
fail. Existing lookups and selections may reject, or an imperfect logical
state may be accepted. These outcomes are reported separately.

## Validation

```sh
"$HOME/pytket-venv/bin/python" src/check_adaptive_history.py \
    --output output/my-adaptive-history-audit.json

"$HOME/pytket-venv/bin/python" -m pytest -q \
    src/test_c4_helix_adaptive.py src/test_c4_helix_depolarizing.py \
    src/test_c4_helix_optimized.py src/test_c4_helix_reduced.py \
    src/test_c4_helix_gadgets.py
```

The [saved audit](../output/c4-helix-adaptive-history-certificates.json)
checks all 52 equality patterns and 197 compatible bad-round placements
at their first stopping prefixes. Every selected vector has a clean
occurrence for every compatible placement. Tests also cover physical
five-round acquisition and correction, five-scan cat repair, the two-zero
shortcut, corrupted certificates, and exact noiseless circuit agreement.
The combined validation command passed all **101 tests**. Both the new
noiseless and noisy saved runs passed their read-only verifiers, as did
the retained baseline runs.

The [new noiseless validation](../output/c4-helix-adaptive-noiseless-validation/summary.json)
retains two acceptances and two negative-SWAP rejections for seeds 0–3,
with identical gate totals and exact output states.

Adaptive Shor-style repetition is also studied by
[Tansuwannont, Pato and Brown](https://quantum-journal.org/papers/q-2023-08-08-1075/).
Their results motivate using syndrome changes. Our clean-reference proof
is derived for this circuit's commuting families and does not assume
their Pauli-code recovery theorem applies to the gauged circuit.

## First comparison at two-qubit infidelity 8 × 10⁻⁴

The [adaptive 50-attempt run](../output/c4-helix-adaptive-8e-4-50/summary.json)
uses the same graph, extraction, source preparation, rates, seed range
0–49, and seed rules as
[the saved triple-policy run](output/my-depolarizing-pilot6/summary.json).
Only two-qubit gates are noisy in both runs. The
[saved comparison](../output/c4-helix-adaptive-8e-4-comparison.json)
checks those manifest fields and sums the actual executed CX/CZ/SWAP counts.

| Observed result | Consecutive triple | Adaptive |
|---|---:|---:|
| Accepted / attempted | 7 / 50 | 17 / 50 |
| Rejection fraction | 86% | 66% |
| Rejection Wilson 95% interval | 73.8–93.0% | 52.2–77.6% |
| Agreement-limit rejections | 32 | 0 |
| Accepted decoded fidelity exactly 1 | 7 | 16 |
| Imperfect accepted outputs | 0 | 1 |
| Mean accepted decoded fidelity | 1 | 84/85 ≈ 98.82% |
| Two-qubit gates across all attempts | 629,152 | 749,703 |
| Two-qubit gates per accepted output | 89,879 | 44,100 |
| Two-qubit gates per decoded-exact output | 89,879 | 46,856 |
| Unresolved computations | 0 | 0 |

The imperfect adaptive output is shot 12, with 26 sampled noise events
and decoded fidelity 4/5. It is **kept as an accepted imperfect output**;
the diagnostic is not a filter. Fourteen adaptive outputs already matched
the physical target exactly, two more decoded exactly after ideal recovery,
and the remaining one was imperfect. No assessed accepted trajectory with
at most two sampled faults violated the predicted fidelity-one property.

The adaptive rejection breakdown is 11 terminal ambiguities, 7 absent
terminal candidates, 9 negative-SWAP decisions, 2 source retry limits,
2 cycle-syndrome failures, and 2 B-one decisions. These identify the next
decoder bottlenecks after removing the agreement limit.

Total gate count rose because more attempts reached later stages or fresh
gauging cycles. In this sample the two-qubit cost per decoded-exact output
fell by about 48%. The adaptive run took 545 seconds, peaked at 2.98 GiB
worker RSS and 2,048 coherent terms, and had no resource failures. Timing
is not a controlled speed comparison: other validation jobs ran concurrently.

These are actual new quantum trajectories, rather than a retrospective
change of acceptance flags. Different stopping decisions change later
measurement and noise draws, so equal seeds do not pair identical physical
fault histories. Fifty attempts establish an observed improvement and a
quality tradeoff, not a precise yield or rare logical-error estimate.
