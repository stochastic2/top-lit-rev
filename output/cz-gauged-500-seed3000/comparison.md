# 500-shot gauged-CZ comparison, seed 3000

Each arm used attempt seeds 3000–3499 and the previous gate and readout rates. The simulator sampled an unbounded number of faults.

| Method | Accepted | Rejected | Unresolved | Acceptance, 95% Wilson interval | Decoded matches | Clean CX / T | Completed CX per match |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Compact13 round trip, joint off](parallel-reference/joint-off/summary.json) | 229 / 500 | 271 | 0 | 45.8% (41.5%–50.2%) | 229 | 1,889 / 256 | 5,877.7 |
| [Compact13 round trip, joint fallback](parallel-reference/joint-fallback/summary.json) | 230 / 500 | 270 | 0 | 46.0% (41.7%–50.4%) | 230 | 1,889 / 256 | 5,866.7 |
| [Compact13 shortened votes](short-handoff/compact13/summary.json) | 274 / 500 | 226 | 0 | 54.8% (50.4%–59.1%) | 272 | 1,235 / 120 | 3,470.3 |
| [Tree4 shortened votes, two resource scans](short-handoff/tree4/summary.json) | 275 / 500 | 225 | 0 | 55.0% (50.6%–59.3%) | 275 | 1,127 / 120 | 3,116.3 |
| [Tree4 shortened votes, block flags](tree4-block-flags/tree4/summary.json) | 287 / 500 | 213 | 0 | 57.4% (53.0%–61.7%) | 287 | 1,058 / 120 | 2,817.9 |
| [Cat-dual](parallel-reference/cat-dual/summary.json) | 288 / 500 | 212 | 0 | 57.6% (53.2%–61.9%) | 287 | 1,476 / 120 | 3,993.2 |
| [Tuned five-parity cat](tuned-cat/cat-five-parity/summary.json) | 321 / 500 | 179 | 0 | 64.2% (59.9%–68.3%) | 320 | 1,126 / 120 | 2,915.1 |

Wilson intervals use completed attempts. CX per match includes the cost of completed rejections.

## Same-seed comparisons

| Comparison | Left-only accepts | Right-only accepts | Acceptance difference | Adjusted p |
|---|---:|---:|---:|---:|
| Tree4 shortened votes, two resource scans vs. Compact13 round trip, joint fallback | 93 | 48 | +9.0 pp | 0.001317 |
| Tree4 shortened votes, two resource scans vs. Compact13 shortened votes | 58 | 57 | +0.2 pp | 1 |
| Tree4 shortened votes, two resource scans vs. Cat-dual | 96 | 109 | -2.6 pp | 1 |
| Tree4 shortened votes, two resource scans vs. Tuned five-parity cat | 82 | 128 | -9.2 pp | 0.01099 |
| Tree4 shortened votes, block flags vs. Tree4 shortened votes, two resource scans | 44 | 32 | +2.4 pp | 0.8269 |
| Tree4 shortened votes, block flags vs. Compact13 round trip, joint fallback | 102 | 45 | +11.4 pp | 2.351e-05 |
| Tree4 shortened votes, block flags vs. Cat-dual | 100 | 101 | -0.2 pp | 1 |
| Tree4 shortened votes, block flags vs. Tuned five-parity cat | 84 | 118 | -6.8 pp | 0.1001 |

The two-sided exact McNemar tests compare acceptance by attempt seed. A common seed does not imply an identical physical trajectory across circuits. Holm adjustment accounts for all eight comparisons, including the supplementary block-flag comparisons.

The reference arms use the unchanged simulator in persistent parallel workers. Cross-check counts against the original harness are recorded in the comparison JSON.
