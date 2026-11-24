# C4-Helix tree4 and direct-cat fairness audit

The clean 68-CX advantage of the repaired baseline tree comes from the logical measurement circuits. They save 80 CX while the tree spends 12 more CX on data checks and output certification. Direct cats can use the shortened sign rule. A cat with the ordered screen reused in its deciding round and a four-parity resource check costs 540 CX on the same clean trace. Applying bare inner meters to tree4 brings it to 576 CX. All these clean traces use 120 T/T†.

[Two-location proof](PROOF.md) · [Exact baseline traces](baseline_traces.json) · [Local certificates](local_checks.json) · [Forced trajectories](forced_checks.json)

## What the exact baselines execute

Both exact baselines come from the final diagnostic and share the same encoder and twelve-check source circuit, gate for gate. The all-zero source costs 125 CX. The report record below sets measurements to zero to reproduce the saved clean accounting. Actual positive noiseless quantum shots can have different individual vertex, edge and leaf reports. The requested conditional frame and byproduct gates do not alter the clean CX or T/T† totals.

| Clean work | Repaired tree4 | Matched five-parity cat |
|---|---:|---:|
| Raw data encoder and source screen | 125 | 125 |
| Logical measurement resource preparation and verification | 11 | 123 |
| Logical measurement ports, including their flags | 92 | 60 |
| Routine data checks | 200 | 376 |
| Ordered terminal data screen | 188 | 0 |
| Edge readout and classically selected physical byproducts | 0 | 0 |
| **Total CX** | **616** | **684** |
| **Total T/T†** | **120** | **120** |
| Peak live qubits | 30 | 41 |

- **Repaired tree4.** Prepare the five vertices and four edges with eight CX, use the three-CX targeted resource check, apply twenty controlled-W ports, then XOR the five destructive vertex reports for the entry vote. The four edges remain live across all confirmation slots. Each ordinary clean confirmation reads nine Z checks and five inner X checks for 100 CX. The four leaf Gauss meters use five CX apiece. The root uses eight data/edge ports and eight flag couplings, for another 16 CX. The five Gauss reports and inner-X parity give the signed vote. Entry plus two positives reaches three. A nonzero ordinary Z row triggers a cheap in-frame Z-only history, with fresh full-code/graph recovery in V coordinates on ambiguous Z lookup. Inner flags can abandon a slot and invoke flagged recovery, subject to the repaired veto. A nested inner flag in Z-only recovery can return to the root of that slot. Outer one-flag Z and compact-root flags reject. There are at most four confirmation slots after entry. The vote-budget guard stops an impossible prefix and can skip a recovery of an abandoned slot. The four edges are read in Z once, classically selected local S/S† and X byproducts are applied, and the order-sensitive compact screen checks the output. A nonzero screen uses either a fresh complete code history or flag-conditioned recovery and a fresh screen.
- **Matched cat.** The first vote measures U directly after the screened source. The inherited `SourceAsFirstVote` returns a zero row without executing another code scan. Each later vote first reads the nine Z and nine X checks in that order. A nonzero syndrome uses the complete commuting reference procedure. Data flags trigger conditioned recovery, then the partial pre-correction row is discarded and the complete row is repeated. Each vote prepares its own GHZ20 with nineteen chain CXs, measures five Z parities costing 22 CX, applies twenty controlled-W ports, and XORs the twenty destructive X measurements. A nonzero resource parity starts the adjacent-ZZ fallback and leaf repair, within that vote. No leaf is retained or coupled back after readout. Three positives in at most five slots accept immediately. The code already stops as soon as three positives become unreachable. The exact baseline has no post-U screen or data handoff.
- With no noise and a negative entry, both baselines make two further negative votes and stop at three failed slots. The alternate immediate-negative policies save that work but discard attempts with a false-negative first report that could otherwise accumulate three positives. Forced single-report witnesses establish the lost recovery opportunity on both sides. Source rebuilds, graph retries, cat repair, conditional data checks and cleanup are included in attempt accounting. [Baseline trace operations and reports](baseline_traces.json) · [Stopping and entry-filter controls](forced_checks.json)

The persistent tree uses 112 fewer resource CX than the baseline cat, offset by 32 more data/edge meter and flag CX across the three logical results. This is an implementation-level accounting of the persistent-readout architecture. An abstract edge-lifetime intervention would require a different circuit. The information deferral saves 176 CX in the two routine tree records relative to the two full cat records, and the tree pays 188 CX at the output. The 80-CX logical-circuit difference and 12-CX data/screen difference account for all 68 CX.

## Controlled changes

| Controller | Change from preceding comparison | Logical-result CX | Routine checks CX | Screen CX | Full clean CX |
|---|---|---:|---:|---:|---:|
| ScreenCat | Exact matched-source control | 183 | 376 | 0 | 684 |
| ShortPostCat | Short votes and post-U compact screen | 183 | 160 | 188 | 656 |
| ShortPreCat | Use the screen as the data check for the deciding vote | 183 | 80 | 188 | 576 |
| LeanResourceCat | Ten-CX four-parity verifier replaces 22-CX five-parity verifier | 147 | 80 | 188 | 540 |
| RepairedTree | Exact repaired control | 103 | 200 | 188 | 616 |
| BareInnerTree | Bare meters on the ten routine inner checks per confirmation | 103 | 160 | 188 | 576 |

The shared source adds 125 CX to every row. To split the first cat comparison further, omitting four 16-CX outer-X meters in each confirmation saves 128 CX. Adding the 188-CX screen costs 60 CX net with ordinary compact routine meters. The one-flag outer-Z meters save another 48 CX over two rounds and the bare inner meters save 40 CX. All 18 checks still execute at terminal verification, and a triggered full-code recovery still measures all 18.

Every clean shortened vote uses nine original Z reports and the XOR of five inner X reports. On the two-block envelope, nine positive Z checks make the X part a product of stabilizers. The remaining Z part flips the physical U sign exactly when the inner-X XOR is odd. An honest positive therefore uses the raw sign XOR that parity. The direct-cat Z-only recovery can use ordinary physical X correction, and full recovery can use the same two-block table in original data coordinates. The altered controllers reject on a routine outer-Z flag. They retain recovery for unambiguous nonzero Z records and for screen flags. Rejection versus trying a new decoder for the altered outer-Z flag pattern is outside the measured ablations. [Shortened-vote kernel and extraction checks](local_checks.json) · [Global history and terminal proof](PROOF.md)

Both cat verifiers have a physical one-site-per-fault support bound, including cancelling report signatures from two faults and arbitrary phase. This is stronger than the block bound needed for the sign calculation. It allows the final screen to take the place of the deciding round's data checks. The deciding measurement only consumes the verified cat and adds site-local tails. Four parity supports exploit equal-syndrome raw-chain hooks that differ by at most two leaf bits. One forced pair of 15- and 13-leaf suffix faults cancels in the check word and leaves only L5 and L6 as the disagreement. Each fault alone triggers the recovery path. [Correlated preparation witness](correlated_cat_witness.json)

The bare-inner change transfers safely to the tree. Relocating its screen ahead of handoff fails. In proper data coordinates with a physical V/V pair around the moved screen, a single fault on the second-pass CX(A0,D6) can leave half of the output weight outside all radius-two syndrome sectors. The fixed fallback still decodes that one case. Two flipped handoff reports, A0 and A1, instead produce decoded fidelity 0.5 on an accepted output. All four single-report-flip controls have unit decoded fidelity on the same seed. The pre-handoff relocation and the unframed shortened cat are experimental counterexamples and are excluded from the holdout. The eight holdout controllers have complete two-location accepted-output proofs in the stated model. [Single-location support witness](single_fault_tree_transfer.json) · [Two-report and unframed witnesses](forced_checks.json)

## Holdout design

The manifest freezes both baselines, both five-parity shortened variants, the four-parity cat, the bare-inner tree and symmetric filtered versions of the two optimized controllers. The final holdout uses 512 shared-seed groups, seeds 2250000–2250511, disjoint from the original diagnostics, the forced replays, and the aborted launch. The two-qubit infidelity and readout flip probability are 0.001. The single-qubit and T/T† infidelities are 0.0001. Preparation and serialized idle infidelities are zero. Fault counts are unrestricted. The decoder is fixed to ideal syndrome projection followed by the radius-two physical table and the fixed GF2 fallback. A decoded match uses tolerance 1e-10.

Work from every attempt contributes to the CX and T/T† numerators, including rejection, resource repair, rebuild, and any partial unresolved work. Decoded matches per attempt divides by all 512 starts. Accepted raw and decoded fidelity are mean overlaps conditional on acceptance. Wilson intervals are per-arm 95% intervals. Paired uncertainty comes from 10,000 seed-group bootstrap resamples with predeclared randomness. Shared seeds pair simulation draws for uncertainty and do not identify the same physical fault after circuits diverge. Comparisons are descriptive per contrast. For the lean cat relative to the bare-inner tree, the predefined noninferiority margins are 5% extra CX per decoded match, 5% extra T/T† per decoded match, or a loss of 2 percentage points in decoded matches per attempt. Each endpoint is interpreted separately.

The first launch was aborted after five serialized groups when the simulator tried to regroup the same helper twice in the shortened cat's ambiguous-Z full fallback. Restricting the representation-only helper hook to the routine Z contexts fixed the fault. The physical circuits, candidate definitions, noise, sample size and analysis were retained, and the run was frozen again with fresh nonoverlapping seeds before examining performance. The partial ledger and fixed-seed replay are kept. [Frozen plan](holdout_plan.json) · [Final manifest](holdout_2250000/manifest.json) · [Aborted launch record](holdout_2240000/launch_error.json)

## Reproduction

From the repository root, use the existing simulator environment. The evidence files written by the first three commands can be regenerated in a copy of this experiment directory. The freeze command creates a new result directory and refuses to overwrite an existing one.

~~~sh
py=/Users/kevinhemery/pytket-venv/bin/python
audit=experiments/tree4_cat_fairness
"$py" -B "$audit/trace_audit.py"
"$py" -B "$audit/local_checks.py"
"$py" -B "$audit/forced_checks.py"
"$py" -B "$audit/holdout.py" freeze
"$py" -B "$audit/holdout.py" run
"$py" -B "$audit/summarize_holdout.py"
~~~

## Holdout results

| Proven arm | Accepted / 512, 95% Wilson | Rejected | Matches / attempt | Raw fidelity | Decoded fidelity | CX / match | T/T† / match | Peak live |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Repaired tree4 | 296, 53.5%–62.0% | 216 | 296/512 (57.8%) | 0.993243 | 1.000000 | 1,372.6 | 210.4 | 30 |
| Matched five-parity cat | 324, 59.0%–67.3% | 188 | 323/512 (63.1%) | 0.981481 | 0.996914 | 1,820.0 | 189.8 | 41 |
| Short cat, post-U screen | 316, 57.4%–65.8% | 196 | 316/512 (61.7%) | 0.996835 | 1.000000 | 1,475.5 | 203.2 | 41 |
| Short cat, pre-U screen | 323, 58.8%–67.2% | 189 | 323/512 (63.1%) | 0.965944 | 1.000000 | 1,306.9 | 195.3 | 41 |
| Four-parity short cat | 327, 59.6%–67.9% | 185 | 327/512 (63.9%) | 0.975535 | 1.000000 | 1,250.0 | 190.3 | 41 |
| Bare-inner tree4 | 303, 54.9%–63.4% | 209 | 302/512 (59.0%) | 0.977264 | 0.997066 | 1,302.1 | 201.6 | 30 |
| Bare-inner tree4, entry filter | 299, 54.1%–62.6% | 213 | 299/512 (58.4%) | 0.983278 | 1.000000 | 1,182.1 | 165.7 | 30 |
| Four-parity short cat, entry filter | 310, 56.2%–64.7% | 202 | 310/512 (60.5%) | 0.974194 | 1.000000 | 1,125.6 | 159.0 | 41 |

All 4,096 attempts resolved. The baseline cat had one accepted mismatch at seed 2250460, with four sampled faults and decoded fidelity 0. The bare-inner tree had one at seed 2250292, with three sampled faults and decoded fidelity 1/9. Every accepted attempt with at most two sampled faults matched and had unit weight in the radius-two lookup. The holdout contains 39 adjacent-ZZ fallback episodes for the four-parity short cat and 64 for the otherwise identical five-parity short cat. The source had 25 retry tokens per cat arm. Each tree arm used those 25 source tokens plus three graph tokens. [Shot ledger](holdout_2250000/shots.jsonl.gz) · [Mismatch records](holdout_2250000/accepted_mismatches.json) · [Numerators, retry and rejection summaries](holdout_2250000/summary.json)

### Paired differences

Each entry is right minus left, with its 95% paired interval in brackets.

| Left → right | Decoded matches per attempt, pp | CX per decoded match | T/T† per decoded match |
|---|---:|---:|---:|
| Repaired tree4 → Matched five-parity cat | +5.3 [-0.4, +10.9] | +447.4 [+291.8, +616.3] | -20.5 [-39.5, -2.3] |
| Repaired tree4 → Four-parity short cat | +6.1 [+0.4, +11.7] | -122.5 [-248.5, +1.0] | -20.0 [-38.8, -1.8] |
| Matched five-parity cat → Short cat, post-U screen | -1.4 [-4.3, +1.6] | -344.5 [-473.9, -222.4] | +13.3 [+4.6, +22.2] |
| Short cat, post-U screen → Short cat, pre-U screen | +1.4 [-0.8, +3.7] | -168.6 [-247.7, -94.4] | -7.9 [-14.6, -1.8] |
| Short cat, pre-U screen → Four-parity short cat | +0.8 [-1.6, +3.1] | -56.8 [-129.6, +13.8] | -5.0 [-11.5, +1.3] |
| Repaired tree4 → Bare-inner tree4 | +1.2 [-2.0, +4.5] | -70.5 [-168.1, +25.3] | -8.8 [-19.6, +1.5] |
| Bare-inner tree4 → Four-parity short cat | +4.9 [-1.0, +10.5] | -52.0 [-168.4, +65.4] | -11.3 [-29.0, +6.1] |
| Bare-inner tree4 → Bare-inner tree4, entry filter | -0.6 [-1.4, +0.0] | -120.0 [-149.2, -94.3] | -35.9 [-43.9, -29.1] |
| Four-parity short cat → Four-parity short cat, entry filter | -3.3 [-4.9, -1.8] | -124.4 [-162.2, -91.2] | -31.4 [-38.5, -25.1] |
| Bare-inner tree4, entry filter → Four-parity short cat, entry filter | +2.1 [-3.5, +7.8] | -56.5 [-155.2, +43.1] | -6.7 [-16.3, +2.7] |


For the predefined comparison of the unfiltered four-parity cat against bare-inner tree4, the CX ratio is 0.960 [0.877, 1.053]. Its upper bound exceeds the 1.05 margin, so CX noninferiority is unresolved under the chosen rule. The T/T† ratio is 0.944 [0.864, 1.032] and meets the 1.05 margin. Decoded yield differs by +4.88 percentage points [−0.98, +10.55], meeting the −2-point margin. For both resource costs, the paired interval includes equal consumption. The apparent baseline tree advantage of 447 CX per decoded match shrinks to a 52-CX point advantage for the shortened cat after optimizing both circuits, with paired uncertainty spanning either ordering. [Paired estimates and criteria](holdout_2250000/summary.json)

Early rejection stopped 146 tree attempts and 152 cat attempts at entry. It cut CX and T/T† per match in both cases. It lost three decoded tree matches and seventeen decoded cat matches among the 512 starts, and also removed the bare-inner tree's one accepted mismatch. These are policy effects on the same candidate within each architecture. [Paired policy estimates](holdout_2250000/summary.json)

## Best proven designs for the measured resource budgets

The entry-filtered versions had the lowest measured CX and T/T† cost per decoded match within each architecture. The full rows above retain the unfiltered versions for factories that value salvaging a negative entry.

| Best proven circuit by gate-cost point estimate | Clean CX | Clean T/T† | Accepted and matched / 512 | Acceptance, 95% Wilson | Mean raw / decoded fidelity | CX per decoded match | T/T† per decoded match | Peak live qubits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Bare-inner tree4, entry filter** | 576 | 120 | 299 | 58.4% [54.1%, 62.6%] | 0.983278 / 1.000000 | 1,182.1 | 165.7 | **30** |
| **Four-parity short cat, entry filter** | **540** | 120 | 310 | 60.5% [56.2%, 64.7%] | 0.974194 / 1.000000 | **1,125.6** | **159.0** | 41 |

The optimized tree still spends 44 fewer clean CX on its three logical measurements. It prepares and verifies the graph once for 11 CX and uses 92 CX on W, edge and flag ports. The optimized cat uses 87 CX to prepare and verify three resources, and 60 CX for their W ports. The tree spends an extra 80 CX on one shortened data pass because its final ordered screen must follow handoff. The cat can make its 188-CX screen do double duty as the data checks for the deciding vote. The balance is 36 clean CX in favor of the cat. The tree needs 11 fewer live qubits because it holds four edges between votes and never allocates twenty cat leaves. [Clean gate and qubit traces](local_checks.json)

- **CX-limited.** Use the filtered four-parity cat if 41 live qubits fit and the lower point cost is the deciding metric. The paired filtered cat minus tree difference is −56.5 CX per match [−155.2, +43.1], so the holdout leaves uncertainty about the ordering.
- **T-limited.** The filtered cat has the lowest point cost, 159.0 T/T† per match, and the filtered tree is close at 165.7. If salvaging negative entries matters, the four-parity cat meets the prespecified 5% T-cost margin against the unfiltered bare-inner tree.
- **Qubit-limited.** Use the 30-qubit bare-inner tree. Turn on the entry filter when the observed savings in both gate budgets are worth the lost recovery opportunities.

These are gate and space budgets for the specified noise model. The clean filtered trees and cats use 141 and 167 destructive measurements, respectively, plus 161 and 187 preparations including the initial data. The matched simulator uses serialized wait locations at zero idle noise. Hardware throughput requires calibrated preparation/reset and measurement latency, a parallel schedule and idle noise for that schedule.
