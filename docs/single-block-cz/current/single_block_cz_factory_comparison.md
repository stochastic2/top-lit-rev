# One-block CZ magic factories and their measured tradeoffs

The C4-Helix code supports two fault-tolerant implementations of the same logical CZ projection. A gauging circuit reads local Gauss observables and ungauges with measurement-dependent corrections. A direct circuit uses a verified cat to control the twenty physical factors of logical CZ. Both start from encoded |++⟩ and prepare the positive projection, `(|00⟩ + |01⟩ + |10⟩)/√3` in the encoded basis, with ideal probability 3/4. The comparison concerns complete factories, including their syndrome extraction, recovery, and release rules. [Original C4-Helix proposal](../../../arXiv-2609.03194v1/appendix.tex) · [Physical convention and target](full_procedure_single_block_cz.md)

## Fault-tolerant constructions

| Construction | Logical measurement and output verification | Clean CX | Clean T/T† | Peak live qubits |
|---|---|---:|---:|---:|
| Tree4 | Five vertices and four persistent edges. Local Gauss votes, edge readout and feedback, then the ordered data screen. | 576 | 120 | 30 |
| Certified compact13 | Same four tree edges plus nine chords. The recovery veto rejects cycle-only data corrections when the full data syndrome is ambiguous. | 630 | 120 | 38 |
| 20-leaf cat | One leaf per data site. The ordered data screen can precede every possible deciding vote. | 540 | 120 | 41 |
| Five-leaf cat | One leaf per four-site inner block. The ordered data screen follows the deciding vote. | 551 | 120 | 26 |
| Hybrid cat | Five leaves on ordinary votes and 20 leaves on every possible deciding vote, with the ordered screen before that vote. | 494 | 120 | 41 |

The peak includes the twenty data qubits and live helpers. The CX and T/T† counts are for the successful fault-free path. Each construction has a two-location accepted-output guarantee for arbitrary participant-local circuit faults with reliable classical control and a shared budget across retries, measurements, and one-qubit idles. The proofs bound the residual physical errors at release, so an ideal distance-six decoder recovers the target from every accepted branch within that budget. [Tree4 and 20-leaf proof](../../../experiments/tree4_cat_fairness/PROOF.md) · [Compact13 proof](../../../experiments/compact13_certified_recovery/PROOF.md) · [Five-leaf and hybrid proof](../../../experiments/tree4_cat_fairness_review/BLOCK_CAT_PROOF.md) · [Clean traces](../../../experiments/tree4_cat_fairness_review/README.md)

The difference between five and twenty leaves is fault propagation. A five-leaf control can spread a single fault through several later ports in its own inner block. The post-vote screen can convert that block-level error bound to a physical-site bound. In the 20-leaf meter, each leaf has one data port and the verifier bounds preparation errors by physical sites. That stronger bound lets the hybrid reuse the pre-vote screen on its deciding measurement. Moving tree4's screen ahead of the ungauging handoff exposed a different failure route. Two faulty edge reports produced an accepted state with decoded fidelity 1/2 in the relocation test. [Five-leaf argument](../../../experiments/tree4_cat_fairness_review/BLOCK_CAT_PROOF.md) · [Tree handoff counterexample](../../../experiments/tree4_cat_fairness/forced_checks.json)

## Matched operating points

The table uses the same 5,000 seeds for every row (3,300,000–3,304,999). All rows use the same screened source, noise rates, and final ideal diagnostic decoder. Two-qubit average infidelity and readout-flip probability are both 0.001, one-qubit and T/T† average infidelity are 0.0001, and preparation and idle fault rates are zero. The selective rule rejects a terminal syndrome that triggers fallback or a full recovery reference during a vote, while keeping simpler recovery paths. The cap also stops before the 121st physical T or T† gate. The five-leaf and hybrid rows use the shared seed slice of the 6,000-seed study. Their early-stop costs come from saved branch records and were checked against physical hard-stop replays in that study. [Replication](../../../experiments/tree4_postselection_replication_5000/summary.json) · [Five-leaf ledger](../../../experiments/five_leaf_postselection_6000/shots.jsonl) · [Hard-stop validation](../../../experiments/five_leaf_postselection_6000/validation.json)

| Circuit and policy | Acceptance | Correct / accepted | Mean decoded fidelity | One-sided 95% fidelity lower bound | T/T† per correct output |
|---|---:|---:|---:|---:|---:|
| Tree4, selective | 47.70% | 2,385 / 2,385 | 100% observed | 99.8745% | 249.6 |
| Certified compact13, selective | 46.62% | 2,331 / 2,331 | 100% observed | 99.8716% | 258.4 |
| 20-leaf cat, selective | 53.42% | 2,669 / 2,671 | 99.9251% | 99.7645% | 217.8 |
| 20-leaf cat, selective and capped | 46.42% | 2,321 / 2,321 | 100% observed | 99.8710% | 239.2 |
| Five-leaf cat, selective | 48.86% | 2,442 / 2,443 | 99.9591% | 99.8060% | 241.4 |
| Five-leaf cat, selective and capped | 45.76% | 2,288 / 2,288 | 100% observed | 99.8692% | 249.4 |
| Hybrid cat, selective | 53.44% | 2,672 / 2,672 | 100% observed | 99.8879% | 209.3 |

Acceptance counts every released output. A correct output has decoded fidelity within \(10^{-10}\) of one. T/T† cost sums work on all attempts, including rejections, and divides by correct outputs. Each fidelity bound is individual and conservative. It uses an exact binomial upper bound on the conditional miss probability and assigns every miss zero fidelity. The two direct physical preparations have fidelity **99.8656%** with native rotations and **99.7539%** with a heralded Clifford+T circuit in the stated model. These are state-preparation benchmarks for the same target under their gate and noise assumptions. Zero observed misses support a bound, with statistical uncertainty in the true miss rate. [Physical baseline circuits and calculations](../../../experiments/tree4_cat_fairness_review/comparison_500/direct_physical.py)

At these operating points the selectively filtered hybrid combines the highest observed correct-output yield with the lowest T cost, at 41 live qubits. The capped all-five-leaf cat uses 26 live qubits with a T cost close to tree4's. Tree4 is the four-edge gauging example and outperforms this compact13 configuration in observed yield and T cost using eight fewer live qubits. The quoted bounds compare each fixed row with the physical benchmarks. A fidelity ranking among the zero-miss rows remains unresolved.

## What the comparison establishes

The final ideal decoder is shared across arms. The controller's online recovery still differs because graph and cat circuits collect different records. Recovery and selective rejection change both which states reach the decoder and how much work the factory spends. The data quantify their effect on complete implementations. They leave the separate contribution of architecture and decoder to the performance gap undetermined.

The paired 512-seed holdout gives a concrete example. The baseline cat used 447 more CX per correct output than repaired tree4 at the point estimate. After both sides were optimized, the short 20-leaf cat used about 52 fewer CX per correct output than bare-inner tree4. The interval at that later operating point spans either ordering. The prespecified one-sided tests supported cat noninferiority in correct-output yield and T cost, with CX noninferiority unresolved. That supports a statement of competitive performance in the specified simulation. A formal claim of practical equivalence would require two-sided margins for the named metrics. [Holdout and paired intervals](../../../experiments/tree4_cat_fairness/README.md)

The strongest research comparison is between two realizations of the same projection. Graph gauging gives a low-width tree example with a protected local measurement and an explicit ungauging handoff. Cats give the choice of a 26-qubit block-local schedule or a higher-yield hybrid at a larger footprint. The exact circuit, recovery rule, and noise model belong in the claim. The measurements here price gates and live qubits. Hardware time and throughput depend also on connectivity, parallel scheduling, readout latency, and idle noise.

The existing small-resource examples suffice for this comparison. The smallest evaluated complete direct factory here uses five cat leaves, and the small evaluated gauging graph is tree4. A separate three-leaf cat appears in an edge check of the earlier two-block SWAP circuit. A complete three-leaf one-block CZ factory is an open extension in this study. With three controls over five inner blocks, a straightforward grouping reuses at least one control across blocks, so its propagation bound would require a new analysis. [Earlier edge-check circuit](../../two-block-swap/history/full_circuit.md) · [Experiment handoff](../../../experiments/README.md)
