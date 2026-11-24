# Review of the tree4–cat comparison and a five-leaf probe

The 512-seed fairness holdout is internally reproducible: all 58 frozen dependency hashes and the compressed ledger digest match. Recounting all 4,096 attempts gives the published acceptance, match, CX and T/T† numerators. The design compares complete factories with a common source, noise, and decoder. In its prespecified unfiltered comparison the optimized cat meets one-sided noninferiority criteria for yield and T cost; the CX ratio interval extends to 1.0533 against a 1.05 margin. This establishes competitive performance in this model. A two-sided equivalence claim would require separate margins and evidence. Neither hardware time nor idle exposure at realistic rates has been priced.

## New schedule probe

Early cat votes can use a leaf per four-site block when a later screen will remove surviving block errors. Each five-leaf resource uses four chain CX and measures Z on leaves 1 and 3 jointly using two CX. It rejects any nonzero report before the data ports. The quantum state can be conditioned on this report; that attempt is discarded. Each of the five leaves then controls four signed W ports within its own block, and all leaf X reports are combined.

For the ideal cat the two possible control words apply I and U. A leaf-bit disagreement inserts the corresponding block product of W operators. A complement of the bit word exchanges I and U; an arbitrary phase changes their coefficients. A port fault can propagate along the remaining ports of the same leaf. This motivates a block bound, whereas a site bound is required for a finishing vote following the ordered screen. In the first variant all potential deciding votes retain the twenty-leaf meter; in the second all votes use five leaves and the ordered screen follows the third positive. The fast parity verifier was checked by Clifford propagation at all 58 raw preparation and scan locations including leaf/helper waits, with every zero-flag pair and complement included. This local check and a positive noiseless decoded replay are recorded in [probe.json](probe.json). The [two-location composition proof and targeted fault replays](BLOCK_CAT_PROOF.md) extend the accepted-output guarantee to both five-leaf schedules.

| Unfiltered arm, seeds 2510000–2510127 | Clean CX | Matched / 128 | CX/match | T/T† per match | Peak live |
|---|---:|---:|---:|---:|---:|
| Bare-inner tree control | 576 | 72 | 1,383.3 | 214.3 | 30 |
| Four-parity twenty-leaf cat control | 540 | 77 | 1,396.8 | 204.2 | 41 |
| Five-leaf ordinary votes, twenty-leaf deciding votes | 494 | 79 | 1,127.3 | 188.9 | 41 |
| Five-leaf votes throughout, ordered post-screen | 551 | 79 | 1,258.8 | 192.4 | 26 |

All 512 pilot attempts resolved and all accepts matched. The table is exploratory. Compare the candidates against the controls on these same fresh seeds. The noninferiority analysis in the original holdout applies only to its frozen arms. The change in measured footprint suggests that a 30-versus-41 comparison is specific to the previously tested constructions.

[Probe implementation](block_cat_probe.py) · [Pilot arm totals](pilot_summary.json) · [Per-seed diagnostics](pilot.jsonl)

Reproduce with the repository's simulator environment and an empty pilot output path (the pilot refuses to overwrite its ledger):

~~~sh
/Users/kevinhemery/pytket-venv/bin/python -B experiments/tree4_cat_fairness_review/block_cat_probe.py
/Users/kevinhemery/pytket-venv/bin/python -B experiments/tree4_cat_fairness_review/pilot.py
~~~
