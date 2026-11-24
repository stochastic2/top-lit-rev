# A 616-CX clean tree4 factory

The previous tree4 factory spent 1,058 CX on a clean attempt. Replacing the known-source verification accounts for all 442 CX saved here. Source preparation happens before enrichment, while the desired twenty-qubit state is known and a failed preparation can still be rebuilt. The same change reduces the tuned cat from 1,126 to 684 clean CX. All four circuits spend 120 clean T/T†.

## The operator schedule

1. **Entry.** Run the existing raw source encoder. Measure five inner Z generators, then the seven selected X generators below. On twelve zero parities with clear flags, use identity feedback and proceed. A nonzero parity immediately starts the complete twenty-generator reference procedure from its first measurement. A source-meter flag rebuilds the unused source under the existing shared retry limit. Prepare the checked tree, enrich the vertices, and use their X readout as the first vote.
2. **Routine vote.** Use the previous block-flag tree4 controller. All nine data Z checks establish the sector, all five inner X reports correct the sign, and the five Gauss reports supply the local measurements whose product gives the vote. The root touches four data qubits and four incident edges. Stop after three positive votes or when that count is unreachable.
3. **Exceptional recovery.** A routine nonzero Z record triggers gauged X-class recovery. The shared V pair is still available for an ambiguous class or eligible flag. In the optional entry filter, a negative vertex vote rejects the attempt before any confirmation gates. This saves T gates at the price of some recoverable positive states.
4. **Handoff.** Read each tree edge once in Z. Apply its four-site leaf byproduct and run the compact terminal screen with the original-code checks. Acceptance and decoded target match are recorded separately.

The twelve source checks, in execution order, are Z0–Z4, X1, X2, X6, X7, X8, and the two logical X generators of the known source. Indices are zero-based. This list screens *the output of the specified encoder*. The twenty-zero vector returned to the source feedback routine selects identity correction. Only twelve operators were measured. During the later vote the data can be magic-bearing and the nine Z checks are still required by the clean-sector argument.

## Where the gates went

| Clean tree4 schedule | CX | T/T† | Readouts |
|---|---:|---:|---:|
| Previous block flags with early stop | 1,058 | 120 | 288 |
| Replace source meters and keep three full scans | 950 | 120 | 234 |
| Accept after one complete all-zero source scan | 678 | 120 | 174 |
| Accept after the twelve selected zero checks | 616 | 120 | 161 |

A source meter on one block uses a bare four-port parity instrument. An outer or logical source meter visits the data in consecutive pairs from each block, with one flag opening after the first pair and closing before the last pair. On the X meters the syndrome helper controls the flag. On the Z meters the flag in the X basis controls the syndrome helper. Both ideal flag couplings cancel and the syndrome reports the signed generator. A flag triggers a source rebuild before enrichment. This replaces multi-leaf decoded-cat source checks and avoids the pair of data Hadamards formerly used at each source Z port. The per-meter forward audit covers all twenty actual supports and both Pauli axes. [Source meter audit](../../../output/cz-source-windows-93000/audit.json)

## What the source certificate proves

For the first, all-zero branch, the audited circuit begins at the raw data preparations and ends at the source output boundary. The known source has twenty independent positive stabilizers on twenty qubits. Pulling them back through the actual encoder gives positive input Z stabilizers. Thus the twenty-bit symplectic syndrome is a complete label for a Pauli modulo the **known-source** stabilizer, including both logical Xs. Two residual Paulis with the same syndrome act identically on this source up to phase.

- **Forward calculation.** Propagate a nonidentity Pauli on each gate's participating wires and the single-wire idle faults through encoding, flag readout and syndrome readout. Store the physical record flips and the output Pauli syndrome. A fault pair can pass the zero screen only when its two record-flip words agree. For each surviving output, test equality of its syndrome to a Pauli supported on at most as many inner blocks as faults. The twelve-check circuit has 3,965 physical or idle locations, 1,051 physical signatures and 6,197 equal-record syndrome pairs in this calculation.
- **Fixed-location calculation.** Independently pull the syndrome and report maps backwards. For a fixed fault location keep the entire set of Pauli components, including identity. For a fixed pair, intersect the allowed supports over **all** component pairs whose reported words cancel. All 45,451 pairs of the 301 distinct location classes have a common support of at most two blocks. Each single location has a common support of at most one block. This common-support result permits a coherent fault on the participating wires: conditioned on a zero record, all surviving terms for those fixed locations act on the same permitted blocks, up to their action on the known stabilizer state. The calculation includes report flips and preparation errors in the circuit fault model.
- **Execution check.** The 206-operation source prefix on the twelve-check tree and cat agrees operation-for-operation with the certificate. The complete twenty-check alternative also passes both audits, with a 310-operation source prefix. Greedy removal found the twelve measured checks. Global minimum measurement count is open. [Forward and fixed-location results](../../../output/cz-screened-source-96000/certificate.json) · [Gate trace and ideal source signs](../../../output/cz-screened-source-96000/trace.json) · [Deletion history](../../../output/cz-fast-source-95000/subset.json)

A nonzero prefix can contain a damaging encoder fault. In the saved one-fault example, a Y on D13 immediately after raw CX(D4,D13) propagates to a source Pauli with no representative on any two blocks. The screen triggers the full source reference and the completed factory decodes to fidelity 1. A nonzero branch reuses the full commuting history policy. The per-meter flag audit gives the same post-reference block bound as the previous decoded source, modulo each measured source generator. [Single raw fault](../../../output/cz-screened-source-96000/raw-hook.json) · [Known-source reference argument](../components/single_block_cz_simulation_recovery_proof.md)

As a boundary test, I enumerated raw CX Pauli faults whose output needs two blocks and flips just one selected source parity. For each of the ten distinct resulting source syndromes, I injected one representative fault and flipped the corresponding meter report. All twenty trajectories on Born seeds 0 and 2 passed the source screen and then rejected safely. Eighteen reached an ambiguous gauged recovery and two reached terminal data ambiguity. [Hidden two-location trajectories](../../../output/cz-screened-source-96000/hidden-hooks.json)

The source result assumes this encoder, order and ideal classical control. A different encoder needs a new audit. It supplies the input envelope at enrichment. The complete factory still needs the two-location composition through noisy votes, the choice of recovery reference, feedback, and the terminal input. The existing vote, tree-resource, block-flag, terminal and forced-trajectory checks reproduced their saved outputs byte for byte. Every noisy run here used the ordinary unbounded-fault sampler.

## Alternatives tested

Removing the flags on the ten ordinary inner meters saves another 40 clean CX on the previous tree. Every physical meter then touches just one block. On seeds 92000–92199, however, the original tree returned 105 decoded matches from 106 accepts, and bare-inner returned 96 matches from 97 accepts. Their costs were 2,834 and 2,889 CX per match respectively. The smaller meter did not pay for itself in this cohort. Retain the routine flags in the source-screen variants.

A concrete failure on bare-inner seed 92082 originally contained four sampled faults. Replaying all subsets through size three isolated a three-location mismatch at decoded fidelity 1/9. The faults were X on the syndrome and Z on D11 after inner X CX(s,D11), X on both wires after leaf Gauss CX(s,A0), and Z on D19 with X on the syndrome during terminal recovery CX(D19,s). The residual data and edge errors change the state reaching terminal decoding, and the last fault also changes the recovery parity. The other sampled fault in source preparation was dispensable. On original-tree seed 92019, all three sampled faults were needed to reproduce its mismatch on that Born seed. These are fixed-trajectory subset minima. [Bare-inner replay](../../../output/cz-bare-inner-92000/minimal-92082.json) · [Parent replay](../../../output/cz-bare-inner-92000/minimal-92019.json)

The entry filter is a resource choice. A forced single root-vertex report flip on an otherwise positive entry produces a match under the ordinary controller and an immediate rejection with the filter. Outputs accepted by the filter run the identical positive-entry trajectory. The simulator cross-checks those shared accepted trajectories by seed. [Entry-filter witness](../../../output/cz-entry-filter-92000/witness.json)

## Measured factory performance

On fresh seeds 96000–96239, the twelve-check tree used 46.3% fewer CX per decoded match than the previous tree and 32.1% fewer than the tuned cat given exactly the same source. A paired seed bootstrap puts the respective 95% savings intervals at 38.9–53.2% and 21.4–41.5%. The tree also saved eleven peak live qubits against either cat.

| 240 attempts per circuit | Accepted | Rejected | Decoded matches | CX/match | T/T† per match | Peak live |
|---|---:|---:|---:|---:|---:|---:|
| Previous tree4 with early stop | 135 | 105 | 135 | 2,517.1 | 204.0 | 30 |
| Tree4, complete twenty-check source scan | 162 | 78 | 161 | 1,504.1 | 187.5 | 30 |
| **Tree4, twelve-check source screen** | **155** | **85** | **155** | **1,351.2** | **186.2** | **30** |
| Twelve-check tree4, reject negative entry | 149 | 91 | 149 | 1,261.9 | 163.8 | 30 |
| Compact13, twelve-check source screen | 149 | 91 | 149 | 1,638.3 | 199.9 | 39 |
| Tuned five-parity cat, previous source | 133 | 107 | 133 | 3,078.8 | 203.0 | 41 |
| Tuned five-parity cat, twelve-check source screen | 144 | 96 | 144 | 1,988.5 | 200.3 | 41 |

The full-scan tree's one mismatch on seed 96153 had nine sampled faults. Of all 130 subsets through size three, exactly one three-fault subset reproduced an accepted output with fidelity zero. All three faults occur on CX gates in different nonroot Gauss votes: Z on the syndrome helper with Y on D16, Y on the helper with Z on D4, and Y on the helper after its CX to A0. After a negative entry and negative first confirmation, the next three corrected reports count as positive. The terminal syndrome screen accepts the wrong logical sector. This subset requires no source fault. [Minimized three-vote failure](../../../output/cz-screened-source-96000/minimal-96153.json)

The twelve-check tree produced 20 more matches than its parent. Of discordant seeds, 45 matched only on the twelve-check tree and 25 only on the parent. The two-sided exact paired test gives p = 0.0225 before adjustment and 0.135 after Holm adjustment across the six reported match comparisons. The data support a CX efficiency gain. A repeatable yield advantage remains unestablished.

The full twenty-check scan is a useful simpler alternative. On an independent 400-attempt cohort (95000–95399), it produced 238 matches, with 162 rejections, at 1,507.8 CX and 207.5 T/T† per match. The original tree produced 230 matches at 2,575.1 CX and 198.5 T/T† per match. The full-scan cat produced 251 matches at 1,959.5 CX and 188.7 T/T† per match. Every accept in that cohort matched. On seeds 93000–93399, changing only the source meters while retaining the three full scans reduced tree CX per match from 2,582.0 to 2,250.5 (227 and 232 matches). The largest observed improvement came from shortening verification of the known input.

**Recommendation.** Pursue the twelve-check tree with ordinary entry voting. Its selected source checks and local root fit in 30 live qubits, and the remaining graph redundancy bought little in this sample. Compact13 reached an ambiguous-data joint lookup once, on 96173, and its cycle record did not resolve it. Enable the negative-entry filter if T supply limits throughput. It spent 12.1% fewer T/T† per match while sacrificing six matches on this cohort. Retain the full twenty-check version as the simpler implementation when the encoder or its ordering may change.

All attempts in all four cohorts resolved. The comparisons use two-qubit infidelity and readout flip probability of 0.001, one-qubit and T/T† infidelities of 0.0001, and zero idle and preparation rates. Costs sum the gates in every completed attempt, including rejections and preparation retries, and divide by decoded matches. Peak live is the observed maximum. Common seed numbers pair the statistical comparison, while gate-list differences can change sampled faults and Born outcomes. The comparison JSON contains all cohort tables, six paired match tests, unadjusted 95% bootstrap intervals for the final resource comparisons, mismatch seeds and joint-lookup details. [Numerical results](../../../output/cz-screened-source-96000/comparison.json) · [Tree and cat shots](../../../output/cz-screened-source-96000/shots.jsonl) · [Compact13 shots](../../../output/cz-screened-compact-96000/shots.jsonl)

## Reproduction

The following commands use the existing noisy backend and run from the repository root. Use an empty output root. The final summary expects the directory names shown. The default seeds, attempt counts and physical rates are the ones used for the tables.

~~~sh
py=/Users/kevinhemery/pytket-venv/bin/python
v=verification/single_block_cz
out=output/source-screen-reproduction
mkdir "$out"
"$py" -B "$v/study_single_cz_bare_inner.py" --folder "$out/cz-bare-inner-92000"
"$py" -B "$v/study_single_cz_entry_filter.py" --folder "$out/cz-entry-filter-92000"
"$py" -B tmp/cz_review_noisy.py --arms cat-five-parity --shots 200 --seed 92000 --output-dir "$out/cz-bare-inner-cat-92000"
"$py" -B "$v/study_single_cz_source_windows.py" --folder "$out/cz-source-windows-93000"
"$py" -B "$v/study_single_cz_shared_source.py" --folder "$out/cz-common-source-93000"
"$py" -B "$v/study_single_cz_fast_source.py" --folder "$out/cz-fast-source-95000"
"$py" -B "$v/search_single_cz_source_subset.py" --output "$out/cz-fast-source-95000/subset.json"
"$py" -B "$v/study_single_cz_screened_source.py" --folder "$out/cz-screened-source-96000"
"$py" -B "$v/study_single_cz_screened_compact.py" --folder "$out/cz-screened-compact-96000"
"$py" -B "$v/check_single_cz_source_trace.py" --output "$out/cz-screened-source-96000/trace.json"
"$py" -B "$v/check_single_cz_raw_source_hook.py" --output "$out/cz-screened-source-96000/raw-hook.json"
"$py" -B "$v/check_single_cz_hidden_source_hooks.py" --output "$out/cz-screened-source-96000/hidden-hooks.json"
"$py" -B "$v/reduce_single_cz_factory_mismatch.py" BudgetPilot 92019 --output "$out/cz-bare-inner-92000/minimal-92019.json"
"$py" -B "$v/reduce_single_cz_factory_mismatch.py" BareInnerPilot 92082 --output "$out/cz-bare-inner-92000/minimal-92082.json"
"$py" -B "$v/reduce_single_cz_factory_mismatch.py" FastTree 96153 --output "$out/cz-screened-source-96000/minimal-96153.json"
"$py" -B "$v/summarize_single_cz_screened_factory.py" --root "$out"
~~~
