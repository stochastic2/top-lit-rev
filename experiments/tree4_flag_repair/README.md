# Screened tree4 factory with coordinate-aware recovery

The final tree arm combines the twelve-check known-source screen, shortened tree4 Gauss votes, single-read handoff, and repaired flagged recovery. The benchmark imports the controller used in the [two-location proof](PROOF.md), verifies the implementation hashes against its [composition certificate](composition.json), and replays the known two-fault regression before sampling. The unchanged screened tree and the tuned five-parity cat with the identical source screen are the controls.

## Final diagnostic

Each circuit ran 500 attempts on fresh seeds 180000–180499. Every attempt resolved. The two-qubit infidelity and readout flip probability were 0.001, the one-qubit and T/T† infidelities were 0.0001, and preparation and idle rates were zero. Fault counts were uncapped. Accepted outputs were diagnosed independently of the controller.

| Circuit | Accepted | Rejected | Decoded matches | Mean raw fidelity on accepts | Mean decoded fidelity on accepts | CX/match | T/T† per match | Peak live |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Repaired tree4 | 282 (56.4%) | 218 | 282 | 0.996454 | 1.000000 | 1,439.4 | 217.6 | 30 |
| Original tree4 | 282 (56.4%) | 218 | 282 | 0.996454 | 1.000000 | 1,439.4 | 217.6 | 30 |
| Matched-source tuned cat | 305 (61.0%) | 195 | 305 | 0.983607 | 1.000000 | 1,844.9 | 195.7 | 41 |

Raw fidelity measures overlap with the encoded physical target before ideal decoding. One accepted tree output and five accepted cat outputs had zero physical overlap and decoded to the target. All remaining accepts had unit raw fidelity to numerical precision. A decoded match uses tolerance 1e-10. With zero observed decoded mismatches in 282 accepts, the one-sided 95% exact upper bound on the repaired tree's conditional mismatch probability is 1.06% for independently sampled attempts from this noise model.

The repair veto fired zero times in the random cohort. Each original/repaired pair agreed in decision, accepted-state diagnostic, and gate counts. The separately injected regression triggered the veto. The 95% Wilson acceptance intervals are 52.0–60.7% for tree4 and 56.7–65.2% for cat. The paired tree/cat comparison had 100 tree-only and 123 cat-only accepts (two-sided exact McNemar p = 0.141). Gate-cost ratios include work spent on rejected attempts.

[Summary](final_180000/summary.json) · [Shot records](final_180000/shots.jsonl) · [Noise and provenance](final_180000/manifest.json)

To repeat the run, use an unused output directory:

~~~sh
/Users/kevinhemery/pytket-venv/bin/python -B experiments/tree4_flag_repair/final_diagnostic.py --seed 180000 --shots 500 --output experiments/tree4_flag_repair/repro_180000
~~~
