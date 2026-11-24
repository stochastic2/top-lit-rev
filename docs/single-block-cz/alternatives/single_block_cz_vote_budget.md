# Three positive votes in five opportunities

Use the block-flag tree4 circuit with the same local root meter and the same terminal screen. Stop once three affirmative votes are impossible. This change shortens failed attempts and gives a simple specification for the classical controller. The clean positive attempt still uses 1,058 CX and 120 T/T†. Keep the exceptional shared \(V\) recovery available when a vote can still affect acceptance.

## The protocol in four stages

1. **Entry.** Prepare the certified source and the four-edge star. Check the targeted resource parity on \(a_0,A_1,a_2\) before coupling the resource to the data. Enrich each vertex with controlled \(W\) on its four data sites. Measuring the five vertices in X projects the branch. The XOR of their reports supplies the first vote, with even parity voting yes. Each reported negative leaf also calls for a Z frame correction on its edge. The source and resource checks protect the input. Neither contributes a vote.
2. **Routine vote.** Measure all nine data Z checks. A zero record with clear flags licenses use of the five bare inner X checks on the clean-sector argument below. Measure those five checks and all five local Gauss operators. The root touches four data sites and four incident edges. In a common Gauss eigensector the product of the five eigenvalues gives the sign of \(U\). Accordingly, XOR the root report, the four leaf Gauss reports and the five inner X reports. Zero votes yes. The Z checks establish the sector, and the inner X and Gauss instruments physically project their observables. A negative inner X or leaf Gauss report changes the sign assigned to the root. It alone calls for neither rejection nor physical byproduct correction. Flags are evidence about meter faults and control the recovery branch.
3. **Exceptional recovery.** After an ordinary nonzero Z record, stay gauged. Seek two consecutive matching nine-Z records in up to four acquisitions. Apply the gauged X correction for a unique class and remeasure the five inner Xs before completing the current Gauss vote. An ambiguous class or an eligible data-meter flag can require the shared \(V\) reference, with full code checks, cycles where available, and graph stars. Unstable or undecodable records reject. The routine outer-Z flag and compact root flag reject directly. A flag caught by the outer vote handler consumes the opportunity even if recovery succeeds. A nested flag handled inside syndrome recovery can return to that same vote. Keep this distinction when counting opportunities.
4. **Handoff.** After the third yes, measure the edges in Z. Every reported tree bit of one applies the corresponding four-site \(U_v\) to its leaf block. This is physical feedback. A wrong bit leaves precisely the extra block byproduct for that edge relative to ideal feedback on the same actual word. The terminal screen measures the original code checks, including outer X, and corrects or rejects according to its history. A decoded target match is assessed independently *after* controller acceptance.

### Why the vote works

In diagnostic coordinates, fix the at-most-two-block support and expand an incoming error in \(X^x Z^z\) terms. Projection onto nine positive data Z checks leaves only X masks that are products of full-block inner X stabilizers. Each surviving term acts on the encoded input as a Z error up to phase. Since each local \(W_q\) anticommutes with \(Z_q\), the logical sign changes by \((-1)^{|z|}\). The product of the five inner X checks covers all twenty sites, so their measured parity selects precisely this sign. All surviving terms for a given five-bit record have the same parity, including on a reference-entangled input. The measurements used in this argument presume an actual clean round. Report errors must be accounted for across the whole history.

Deleting any one of the nine current Z checks admits a nonstabilizer X term in that kernel. For example, \(X_4 X_7\) evades the other eight when check 5 (zero-based) is omitted. Deleting the inner X report of block \(v\) misses the sign of a single \(Z_{4v}\). The saved exhaustive search gives minimum-weight X examples separately for all nine omissions. These are obstructions to deleting existing checks under this proof. An instrument that measures a different generating set or a protected product requires its own analysis. [Omission witnesses](../../../output/cz-tree-vote-budget/omissions.json)

### Why the early stop is exact

Let \(p\) count reported yes votes and \(s\) count the opportunities still eligible to vote. Reject the attempt if \(p+s<3\). At the start of ordinary slot \(r=0,1,2,3\), \(s=4-r\). When its outer flag handler fires, \(s=3-r\) before spending gates on recovery. Even if all remaining reports say yes, the old schedule must reject that prefix. For example, after a negative entry and two negative routine votes, two opportunities remain and no amount of recovery can produce a third yes. The runner also exhausts the 162 combinations of the entry bit and four positive, negative or flagged slots.

Every accepting trajectory executes the same gates, measurements and feedback as before. This statement about the controller holds for arbitrary faulty quantum locations and noisy reported bits under the model of trusted classical control. It transfers any accepted-output guarantee the parent circuit has. Establishing that guarantee still requires a global two-location proof. A stopped rejection can acquire a different reason code because the old suffix sometimes hit another flag.

### Two alternatives

**Reject when a shared V is needed.** This removes the exceptional coordinate-change circuit from gauging. It leaves ordinary gauged X-class recovery available. A minimal yield counterexample has one faulty report and no physical data error. On Born seed 2, flip only the flag readout at `direct/vote/0/Z/0` on `f0`. With recovery, the shot spends 32 coordinate CX (1,384 total) and decodes with fidelity 1. Reject-on-exception exits at 604 CX. Both clean controls accept at 1,058 CX. [Injected trajectories](../../../output/cz-tree-vote-budget/witness.json)

**Protect the tree reports.** A single extra copy on an edge cannot decide whether a disagreement came from the original or the copy. In a fixed scheme that keeps all four destructive readouts and supplements them with direct edge-to-helper XOR checks, the eight-CX majority construction is optimal for guaranteed correction of one arbitrary report flip using only that record. Two input edge words differing only in edge \(e\) must have output records at Hamming distance at least three. Its own readout supplies one difference, so edge \(e\) must enter at least two other checks, each at a cost of one CX. Sum over four edges. Triple readout attains the bound and recovers the injected A1 report flip on the block-flag controller. The bound assumes ideal parity-copy gates. Adaptive measurements, terminal syndrome side information and two faulty physical locations are outside it. [Distance check and witness](../../../output/cz-tree-vote-budget/witness.json)

## Proof still needed

Establish a single invariant through entry, voting, recovery, feedback and terminal input. It must track the logical sign, the data blocks charged to faults, and the faulty reports still compatible with the observed history. Include canceling flags, a fresh fault after the selected matching reference, and faults in the gauged X correction or the tree-controlled byproduct. At the terminal boundary show that each history with zero, one or two faults lands in the corresponding certified input envelope with the correct logical sign. The repeated local audits establish the two-block kernel, the opaque root-port bound, the tree-resource and block-flag bounds, and the terminal guarantee conditional on its input. The global invariant is open. [Vote and terminal audit](../../../output/cz-tree-vote-budget/short_gauss_vote.json) · [Tree resource audit](../../../output/cz-tree-vote-budget/tree_resource.json) · [Outer Z audit](../../../output/cz-tree-vote-budget/block_z.json)

## Factory comparison

The 500-shot replay uses the original attempt seeds 3000–3499. Only the early-stop tree4 row was rerun for this table. All 287 accepted trajectories reproduced their original decoded diagnostics and gate counts exactly. Early rejection saved 31,135 CX and 8,008 T/T† across 110 attempts. The ratios include all completed rejections and preparation retries. Peak means the largest live-qubit count observed over the entire cohort.

| Schedule | Accepted | Rejected | Decoded matches | CX/match | T/T† per match | Peak live |
|---|---:|---:|---:|---:|---:|---:|
| Compact13 round trip, joint fallback | 230 | 270 | 230 | 5,866.7 | 508.0 | 39 |
| Compact13 shortened | 274 | 226 | 272 | 3,470.3 | 281.4 | 39 |
| Tree4 block flags | 287 | 213 | 287 | 2,817.9 | 237.1 | 30 |
| Tree4 block flags, early stop | 287 | 213 | 287 | 2,709.4 | 209.2 | 30 |
| Tuned five-parity cat | 321 | 179 | 320 | 2,915.1 | 181.8 | 41 |

The cat supplied 33 additional decoded matches per 500 attempts in this cohort. Tree4 with early stopping used 7.1% fewer CX per match and eleven fewer live qubits, with 15.1% more T/T† per match. Because the two tree4 acceptance vectors are identical, the original Holm-adjusted acceptance comparison with the cat still gives p = 0.1001. These resource counts measure gates and space. Wall-clock throughput also depends on reset, measurement and scheduling costs.

A separate pilot used fresh seeds 81000–81063 for every arm. Both cohorts used two-qubit infidelity and readout flip probability of 0.001, one-qubit and T/T† infidelities of 0.0001, and zero idle and preparation rates. Every attempt resolved. Each circuit used the same per-seed initialization convention. Changing the gates can change subsequent noise draws and measurement outcomes.

| Schedule, 64 fresh attempts each | Accepted | Rejected | Decoded matches | CX/match | T/T† per match | Peak live |
|---|---:|---:|---:|---:|---:|---:|
| Tree4 block flags | 42 | 22 | 42 | 2,460.2 | 185.5 | 30 |
| Tree4 with early stop | 42 | 22 | 42 | 2,410.3 | 172.6 | 30 |
| Early stop and reject if shared V is needed | 40 | 24 | 40 | 2,422.2 | 167.0 | 30 |
| Early stop and triple tree readout | 42 | 22 | 42 | 2,432.7 | 172.6 | 30 |
| Compact13 block flags with early stop | 36 | 28 | 36 | 3,046.0 | 214.0 | 39 |
| Tuned five-parity cat | 43 | 21 | 43 | 2,875.9 | 176.7 | 41 |

Six tree attempts reached a shared-V exception. Two yielded matches after recovery (81003 and 81019). Triple readout gained an acceptance on 81002 and lost one on 81050, for zero net gain. These seed differences alone do not identify a flipped edge as their cause. Keep single tree-bit feedback as the default at the tested noise rates.

The controlled round-trip comparison isolates one benefit from compact13 redundancy. In 500 attempts the joint fallback triggered four times. Seed 3197 became the sole additional match relative to the same graph with fallback disabled. In the fresh shortened compact13 arm, the full reference reached ambiguous-data joint lookup once, on 81012. Its cycle record was all zero and the class remained ambiguous. These results establish a real recovery use for the chords, with too few rescues here to justify the measured cost. The fresh between-graph comparison also includes the graph-specific resource preparation and root circuits, so its yield difference cannot be attributed entirely to cycle decoding. [Counts and seed lists](../../../output/cz-tree-vote-budget/comparison.json) · [Compact lookup records](../../../output/cz-tree-vote-budget/compact.jsonl)

## Reproduction

From the repository root, set an unused output directory. The physical experiments use the existing exact trajectory backend. The three-arm runner checks gate-count monotonicity and equality of accepted diagnostics against its parent on each seed.

~~~sh
py=/Users/kevinhemery/pytket-venv/bin/python
v=verification/single_block_cz
out=output/cz-tree-vote-budget-repro
mkdir "$out"
"$py" -B "$v/study_single_cz_vote_budget.py" --output "$out/paired.jsonl"
"$py" -B "$v/study_single_cz_majority_budget.py" --output "$out/majority.jsonl"
"$py" -B "$v/study_single_cz_budget_compact.py" --output "$out/compact.jsonl"
"$py" -B tmp/cz_review_noisy.py --arms cat-five-parity --seed 81000 --shots 64 --output-dir "$out/fresh-cat"
"$py" -B "$v/replay_single_cz_vote_budget.py" --reference output/cz-gauged-500-seed3000/tree4-block-flags/tree4/shots.jsonl --output "$out/replay.jsonl"
"$py" -B "$v/check_single_cz_vote_budget_witness.py" --output "$out/witness.json"
"$py" -B "$v/check_single_cz_vote_omissions.py" --output "$out/omissions.json"
for check in short_gauss_vote tree_resource block_z short_gauss_witnesses; do
  "$py" -B "$v/check_single_cz_${check}.py" --output "$out/${check}.json"
done
"$py" -B "$v/summarize_single_cz_vote_budget.py" --results "$out"
~~~
