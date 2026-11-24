# Noisy direct gauging and shortened local Gauss votes

The unchanged noisy backend now runs both the full direct dressed record and a shortened local-Gauss schedule. The latter uses the deformation to move work out of routine verification. Its clean path has no coordinate changes, uses the original vertex readout as the first vote, and reserves outer X checks for recovery and the original-code handoff. The compact13 version keeps the six incident edges of the root. A four-edge experiment keeps the same four-data root construction with the four incident tree edges.

## Why a clean vote can defer the outer X checks

Work in diagnostic coordinates for the argument. Expand a charged error on a fixed set of up to two inner blocks in Pauli terms \(X^x Z^z\). A clean round of the nine bare \(Z_R\) checks selects the terms with zero data-Z syndrome. On any two inner blocks the kernel of these nine checks contains exactly the empty X pattern, the two individual full-block X patterns, and their product. The full-block Xs are stabilizers, so \(X^x Z^z\) is equivalent on the encoded input to \(Z^z\) up to phase. This works on an arbitrary encoded input, including a reference-entangled one. The finite check enumerates all 2,560 X masks and 10,240 compatible X/Z pairs across the ten block pairs. Every proper subset of the nine original Z checks loses this kernel property for some pair.

Each \(W_q\) anticommutes with \(Z_q\), so \(UZ^zU=(-1)^{|z|}Z^z\). The product of the five inner X generators is all twenty data Xs. The XOR of the five measured inner-X bits therefore gives \(|z| \bmod 2\). On the actual positive Z sector these five instruments can use the bare inner X circuit. The signed logical vote bit is the root report XOR the four nonroot Gauss reports XOR the inner-X parity. The Gauss product is \(U\), and the last XOR accounts for the residual Z term. A negative inner-X parity can remain in the state until terminal correction. An apparent nonzero data-Z record triggers recovery before a vote. Flags likewise trigger recovery or rejection. A faulty report can still cause a dirty vote, so the clean-vote argument needs a global history to become an accepted-output theorem.

At entry, the five vertex X reports supply one vote from the original gauging measurement. Two further positive corrected votes are needed, with at most four local-Gauss attempts. The new pilots use the same decoded flagged source as the saved baselines. The shortened root circuit uses the compact eight-port flag pattern on its four data sites and four tree edges. For compact13 the two root chords come after all flag windows. Each W port is its original signed pair of T rotations around a CX, with faults on their individual physical gates. The exact opaque-port check gives a one-port bound for zero flags and a two-port bound for equal flag words modulo the full measured product. The chord tail is arbitrary graph support in this bound. The terminal screen uses the original order with compact Pauli meters. Its independent Clifford audit covers 8,159 locations, two-screen signatures and the incoming one- and two-block envelopes. It verifies the compact screen's residual guarantee conditional on that input envelope.

The most economical votes replace the four outer Z meters with one phase flag each. The eight data ports occur as four consecutive inner-block pairs. The flag is prepared in X, couples into the Z syndrome target after ports two and six, then is read in X. It ideally uncomputes for arbitrary input, and the bare data-Z parity remains the meter's signed projector. The check needs a bound in inner blocks, so treating every two-site hook as two charged faults would overprotect it. The exact audit covers all four supports. For each meter it checks 153 locations, 49 signatures and 686 distinct equal-flag pairs. Zero flags leave at most one block per fault modulo the measured stabilizer. The noisy pilots reject nonzero reports from this new flag. This saves six CX and three flag preparations and readouts per meter, or 48 CX across the two clean votes.

## Tree-bit handoff and resource check

For an arbitrary edge word \(w\), write the gauged state as a sum of \(|w\rangle U(w_{\rm tree})|\phi_w\rangle\), where \(U(w_{\rm tree})\) is the product of \(U_v\) on the blocks selected by the tree bits. A physical edge readout with actual word \(w\) and reported tree bits \(b\) gives \(U(w_{\rm tree}\oplus b)|\phi_w\rangle\) after feedback. A wrong tree report adds its own block. Chord reports have no effect. This equality applies in every cycle sector. The terminal screen deals with the charged data block errors, so the pilot avoids a final cycle measurement and cut decoder. This differs from replacing a distance-five cut decoder by a distance-one cut decoder. The finite check tests 114,768 actual-word and single-report-flip cases across tree4 and compact13. On compact13 the chords still supply cycle information in triggered joint recovery.

On tree4 there is a separate resource optimization. Order the root-to-edge CXs by tree edge. A single root X hook leaves a prefix of defects in the four resource parities \(Z_{a0}Z_{A_e}Z_{a_v}\). After enrichment, a defect mask \(\delta\) supplies one \(U_v\) per bit, modulo the global \(U\) branch. Its block cost is \(\min(|\delta|,5-|\delta|)\), since complementing all five vertex labels multiplies by \(U\). A single fault is dangerous only for the prefixes of length two or three. Both intersect the check on \(a_0,A_1,a_2\), so just that parity is measured. Two faults have block cost at most two for any mask. The exact resource check covers 179 physical locations and 118 one-fault signatures, with every zero report having block cost at most one. It independently sees the dangerous \(X_{a0}\) fault immediately after \(\mathrm{CX}(a_0,A_1)\) and a positive detector bit. This optimization is specific to the ordered four-edge resource. It does not transfer to a general compact13 entangler.

## Recovery paths in the pilots

- **Full direct compact13.** The outer dressed circuit from the first experiment runs in each clean vote. Nonzero sectors and flagged meters trigger entirely gauged diagnostics. The outer-flag lookup combines the exact isolated class union with the stated outside envelope and uses data, cycles and stars. For ambiguous unflagged data syndromes the pilot tries graph-assisted lookup. Root flags reject. Some diagnostics exceed the sparse simulator's configured capacity.
- **Short Gauss compact13.** Routine votes have the five inner X checks and the nine data-Z checks. A flagged check or nonzero Z report can trigger a shared V pair around conditional recovery. The clean path and every routine vote remain gauged. One version retains the original cycle/cut handoff, and one uses the reported tree bits. The latter still uses cycles for flagged or exceptional joint recovery.
- **Short Gauss tree4.** The same votes use the four-edge graph and tree-bit handoff. Two resource scans can be replaced by the single targeted hook check. The last variant also handles a routine nonzero Z report with two matching measurements of just the nine Z checks in gauged coordinates. Its lookup corrects a unique X class while keeping the residual Z sector pending. It then measures the five inner Xs and uses their parity in the root vote. A measured flag or ambiguous X class can still trigger a shared V pair around the full conditional fallback.

The gauged Z-only path uses the X component of the existing two-block Pauli decoder. With the X class identified, physical feedback implements \(V X^{x_{\rm corr}} V\) and leaves any pending Z error for the parity frame and terminal screen. A nonroot X correction uses a data X, an edge S/S† and an edge–data CZ. The routine history costs 70 CX per nine-Z acquisition with the one-remaining-fault dual flags, plus 30 CX to read the five inner Xs. The typical two-acquisition path therefore uses 170 CX before correction gates and the ordinary Gauss checks. The prior exceptional path also measured the X record, cycles and graph stars and paid both coordinate passes.

## Noise model and scope

The experiments use the existing exact cyclotomic trajectory backend and the existing decoded-target diagnostic on accepted data. Controllers see only reported results. The matched pilot uses average infidelities \(r_2=10^{-3}\) and \(r_1=r_T=10^{-4}\), readout flips \(10^{-3}\), and zero preparation and idle rates. A supplemental run uses idle infidelity \(10^{-6}\) per serialized waiting location, for both the tuned cat and the final tree schedule. The backend has no fault-count cap. Attempts with capacity or timeout failures are unresolved. Counts include preparation retries and recovery. Shared Born seeds do not imply paired physical fault trajectories in circuits of different shape.

The finite certificates cover the clean-vote algebra, root port support, compact terminal instrument and raw tree resource. The injected trajectories exercise the sign correction, Z-only recovery, tree-readout error and a negative sector with two wrong votes. A full certification still has to justify the one-block-per-fault accounting through noisy histories and feedback, including flags that cancel, faults after a certified occurrence, and composition with the terminal input envelope. A selected reference can occur before its last matching report. The experiments report decoded fidelity independently of that proof.

The injected tree-readout flip exposes a yield cost of using a single report. A flipped \(A_1\) report supplies a full \(U_2\) byproduct, and the unlocated terminal decoder rejects the sampled syndrome as ambiguous. Two additional nondestructive Z copies per tree edge give majority feedback and recover the injected report flip. That experiment adds eight CX and has only been tested on the forced witness. Also in the forced tests, a pending odd Z error reverses the uncorrected root vote and is handled by inner parity, \(X_{D8}\) and \(Z_{D5}\) are jointly handled without a V pass, and a negative entry branch rejects after two wrong votes.

## Matched 200-attempt results

| Arm | Clean CX | Clean T/T† | Accepted | Decoded target matches | Unresolved | Completed CX per decoded match |
|---|---:|---:|---:|---:|---:|---:|
| Round trip, compact13 | 1,889 | 256 | 94 | 94 | 0 | 5,459.2 |
| Full direct dressed, compact13 | 1,985 | 448 | 54 | 54 | 15 | 8,943.1 |
| Short compact13, cycle/cut handoff | 1,310 | 120 | 113 | 113 | 0 | 3,270.9 |
| Short compact13, tree-bit handoff | 1,235 | 120 | 115 | 115 | 0 | 3,065.2 |
| Short compact13, block-level outer Z flags | 1,187 | 120 | 109 | 109 | 0 | 2,997.6 |
| Short tree4, two resource scans | 1,127 | 120 | 119 | 119 | 0 | 2,712.7 |
| Short tree4, targeted resource check | 1,106 | 120 | 116 | 116 | 0 | 2,860.2 |
| Short tree4, gauged Z-only routine recovery | 1,106 | 120 | 117 | 117 | 0 | 2,866.0 |
| Short tree4, block-level outer Z flags | 1,058 | 120 | 118 | 118 | 0 | 2,654.3 |
| Tuned five-parity cat | 1,126 | 120 | 125 | 124 | 0 | 2,917.1 |

The full direct arm's completed cost excludes the work in the 15 capacity-limited attempts. It had 58 rejections from a flag during diagnostics and accepted 20 outputs after a successful direct recovery. The block-flag compact13 arm reduced CX per decoded match by 45% against the round trip while retaining the full graph. The tree4 block-flag arm used 9% fewer CX per decoded match than the tuned cat in these trials, and used about 217 versus 180 T/T† per decoded match. Its clean-path peak was 30 live qubits, versus 41 for the cat and 39 for the compact13 pilot. The sample yield and resource totals show different tradeoffs. The one cat mismatch sampled seven faults and decoded to the negative logical sector. The tree4 block-flag arm had 75 accepted attempts with at most two sampled faults, all matching. The stochastic results do not certify arbitrary two-location faults.

With idle infidelity \(10^{-6}\) the tree4 block-flag pilot returned 36 decoded target matches from 64 attempts at 2,828.3 CX and 222.9 T/T† per match. The tuned cat returned 34 from 64 at 3,490.9 CX and 201.2 T/T† per match. All accepted outputs in those two samples matched. See the [machine-readable comparison and per-arm summary paths](../../../output/single-cz-noisy-gauged-comparison.json).

The deformation helps here through the voting rule and handoff. Trying to extract the full dressed record in every round spends more gates and rejects more often. Reading a small set of bare checks with local Gauss uses fewer routine gates, and the graph can still help a conditional compact13 decoder distinguish data cones. The four-edge run trades away those cycle observations and tests a different graph, while the compact13 run keeps all nine. The two designs are useful for different constraints. The short compact13 arm is the direct replacement to pursue if graph support must stay fixed. The tree4 block-flag arm is the lower-CX option if the goal is a smaller measured factory.

## Reproduction

Run from the repository root and use a fresh output directory for each noisy run.

~~~sh
py=/Users/kevinhemery/pytket-venv/bin/python
"$py" -B verification/single_block_cz/check_single_cz_short_gauss_vote.py --output output/single-cz-short-gauss-vote.json
"$py" -B verification/single_block_cz/check_single_cz_tree_resource.py --output output/single-cz-tree-resource-certificate.json
"$py" -B verification/single_block_cz/check_single_cz_short_gauss_witnesses.py --output output/single-cz-short-gauss-witnesses.json
"$py" -B verification/single_block_cz/check_single_cz_block_z.py --output output/single-cz-block-z-certificate.json
"$py" -B verification/single_block_cz/run_single_cz_direct_outer_pilot.py --arms full --recover-outer --output-dir output/direct-full-repro
"$py" -B verification/single_block_cz/run_single_cz_short_gauss_pilot.py --output-dir output/direct-short-repro
"$py" -B verification/single_block_cz/run_single_cz_tree_handoff_pilot.py --output-dir output/direct-handoff-repro
"$py" -B verification/single_block_cz/run_single_cz_tree_resource_pilot.py --output-dir output/direct-resource-repro
"$py" -B verification/single_block_cz/run_single_cz_tree_z_recovery_pilot.py --output-dir output/direct-Z-repro
"$py" -B verification/single_block_cz/run_single_cz_tree_z_recovery_pilot.py --shots 64 --idle-infidelity 1e-6 --output-dir output/direct-Z-idle-repro
"$py" -B verification/single_block_cz/run_single_cz_block_z_pilot.py --output-dir output/direct-block-Z-repro
"$py" -B verification/single_block_cz/run_single_cz_block_z_pilot.py --shots 64 --idle-infidelity 1e-6 --output-dir output/direct-block-Z-idle-repro
"$py" -B verification/single_block_cz/run_single_cz_compact_block_z_pilot.py --output-dir output/direct-compact-block-Z-repro
"$py" -B tmp/cz_review_noisy.py --arms cat-five-parity --shots 200 --seed 1000 --output-dir output/cat-matched-repro
"$py" -B tmp/cz_review_noisy.py --arms cat-five-parity --shots 64 --seed 1000 --idle-infidelity 1e-6 --output-dir output/cat-idle-repro
~~~

The [short-vote and compact-meter certificate](../../../output/single-cz-short-gauss-vote.json), [resource and handoff certificate](../../../output/single-cz-tree-resource-certificate.json), [block-Z flag certificate](../../../output/single-cz-block-z-certificate.json) and [injected trajectories](../../../output/single-cz-short-gauss-witnesses.json) are stored separately from the noisy attempts.
