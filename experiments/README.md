# Handoff for the one-block C4-Helix CZ magic factories

Start with the [current comparison note](../docs/single-block-cz/current/single_block_cz_factory_comparison.md) for the scientific claim, a common-seed result table, and the physical break-even benchmarks. The [integrated procedure](../docs/single-block-cz/current/full_procedure_single_block_cz.md) gives the code, signed gates, and reference gauging circuit. Its historical default counts refer to older schedules.

## Implementations and proof boundaries

| Name in the experiments | Code and evidence | Use in the comparison |
|---|---|---|
| `BareInnerTree` | [Controller](tree4_cat_fairness/candidates.py) · [Optimized proof](tree4_cat_fairness/PROOF.md) · [Original tree repair](tree4_flag_repair/PROOF.md) | Small gauging example. Four edges persist across votes and are read once at ungauging. |
| `CertifiedCompact` | [Controller](compact13_certified_recovery/certify.py) · [Proof](compact13_certified_recovery/PROOF.md) · [500-seed replay](compact13_certified_recovery/summary.json) | Gauging with nine extra chords. Uses the original 630-CX vote schedule and vetoes data feedback selected solely by the narrow cycle-conditioned lookup. |
| `LeanResourceCat` | [Controller](tree4_cat_fairness/candidates.py) · [Proof](tree4_cat_fairness/PROOF.md) | Optimized 20-leaf direct cat. The four-parity verification scan checks the 20-leaf resource. “Five-parity cat” in early results describes five checks on 20 leaves. |
| `PostBlockCat` | [Controller](tree4_cat_fairness_review/block_cat_probe.py) · [Proof](tree4_cat_fairness_review/BLOCK_CAT_PROOF.md) | Five leaves throughout, one control per four-site inner block. Ordered screen after the deciding vote. Measured peak is 26 live qubits. |
| `BlockCat` | [Controller](tree4_cat_fairness_review/block_cat_probe.py) · [Proof](tree4_cat_fairness_review/BLOCK_CAT_PROOF.md) | Five leaves for ordinary votes and 20 for every possible deciding vote. Screening before that deciding vote works because the 20-leaf meter has a site-level spread bound. |
| `DeferredCompact`, `RecoveringCompact` | [Deciding-vote proof](compact13_deciding_vote/PROOF.md) · [500-seed result](compact13_deciding_vote/summary.json) | Separate 550-CX compact13 schedules. They reuse the terminal screen for the deciding vote and make different recovery decisions. |

All five main controllers have a two-location accepted-output proof, with the budget shared across the entire attempt and reliable classical control. Selective rejection and the T cap inherit the guarantee by releasing a subset of the original branches. The tree4 screen-relocation counterexample is useful when changing the circuit. The original 630-CX compact13 without the veto had a reachable gap in the cycle-conditioned support argument. The targeted replay reached the proposed correction and both variants eventually rejected. The archived 298/500 cohort agreed seed for seed after the veto. [Tree4 counterexample](tree4_cat_fairness/forced_checks.json) · [Compact13 witness](compact13_certified_recovery/witness.json)

## Evidence to cite

1. [Fairness holdout](tree4_cat_fairness/README.md) compares frozen tree and cat ablations on 512 paired seeds. Use it to show how improving the cat verifier, shortening the vote and relocating the screen closed the original gate-cost gap. The one-sided noninferiority tests have endpoint-specific margins. [Plan](tree4_cat_fairness/holdout_plan.json) · [Summary](tree4_cat_fairness/holdout_2250000/summary.json)
2. [Unfiltered three-way replication](certified_three_way_3000/summary.json) compares certified compact13, bare-inner tree4, and the optimized 20-leaf cat on 3,000 seeds each. The cat leads in acceptance and T cost in this cohort. Tree4 and cat had two accepted misses each and compact13 had seven. The adjusted comparisons leave their underlying fidelity ranking unresolved.
3. [Selective rejection](certified_postselection_6000/README.md) tests rejecting when the terminal screen would start syndrome fallback or a vote would need a full recovery reference. Simple recoveries remain available. The cap stops before physical T or T† number 121. [Primary results](certified_postselection_6000/summary.json) · [Cap evaluation](certified_postselection_6000/budget_summary.json)
4. [5,000-seed hard-stop replication](tree4_postselection_replication_5000/summary.json) covers tree4, certified compact13, and two 20-leaf cat policies. [Five-leaf and hybrid transfer](five_leaf_postselection_6000/summary.json) covers 6,000 attempts per circuit. The first 5,000 seeds are shared across the two studies. Computing the matched table on that intersection avoids comparing seed windows of different sizes. [Five-leaf policy](five_leaf_postselection_6000/plan.json) · [Hard-stop replays](five_leaf_postselection_6000/validation.json)
5. [Direct physical preparation](tree4_cat_fairness_review/comparison_500/direct_physical.py) evaluates the overlap for the same two-qubit target under the same gate error rates. Both physical references are relevant because the native-rotation circuit assumes arbitrary `Ry` at the one-qubit rate, and the heralded circuit uses Clifford+T. [Calculated fidelities](tree4_cat_fairness_review/comparison_500/direct_physical.json)

## Reading the results correctly

The factory controller uses syndrome and flag records to decide whether to recover, retry, accept, or reject. Where applicable, graph cycle records can alter the choice and graph-dependent feedback. The **final diagnostic decoder** is common. It performs ideal syndrome projection, uses a physical weight-at-most-two correction table, and falls back to a fixed GF(2) solution. It determines the reported decoded fidelity and match count after acceptance. In a gate-cost-per-match metric, changing only this evaluator can also change the denominator. [Diagnostic implementation](../src/single_block_cz/single_cz_diagnostics.py) · [Matched plan](tree4_cat_fairness/holdout_plan.json)

The current evidence supports the existence of two certified routes and practical tradeoffs at fixed operating points. Use tree4 as the main gauging example, the 20-leaf direct cat as a reference, and the five-leaf variants to show how verification placement changes the footprint and cost. Compact13 documents the effect of extra graph redundancy in this implementation. See the current note for the exact numbers and assumptions. The experiment identifies differences between these combinations of physical circuit, recovery and policy. It leaves a causal architecture-versus-decoder ranking undetermined.

For the current note, stop circuit exploration at tree4 and the five-leaf designs. A three-leaf ancilla in the earlier two-block edge check has a different role and does not supply evidence for a three-leaf CZ factory. A smaller full factory would need a separate fault-propagation bound and a reason to pay the additional proof and benchmark cost. [Three-leaf edge check](../docs/two-block-swap/history/full_circuit.md)

If a later revision needs to isolate decoder effects, hold the physical circuit and acceptance policy fixed when changing only the final diagnostic decoder. Replay the output states wherever the ledger lacks sufficient information for the new decoder. A change to **online** recovery can change the circuit path, so resimulate paired attempts and report the changes in yield, conditional fidelity, T/CX cost, and live qubits. For a formal equivalence claim, specify two-sided margins and a precision target before sampling. State the fault model for every proof and the cost model for every benchmark.

## Reproduction

Use the repository simulator environment. The original runners in the linked folders use exclusive ledger creation. Keep the existing ledgers as evidence and run fresh cohorts in a separate output directory or a copy configured with fresh seeds. The proof files and manifests give the code and settings to preserve. The two replication summarizers recompute their archived cohorts. The following read-only snippet reproduces the five-leaf and hybrid rows of the common-seed table using the existing policy analysis.

~~~sh
/Users/kevinhemery/pytket-venv/bin/python -B - <<'PY'
from pathlib import Path
import json
import sys

root = Path("experiments").resolve()
sys.path.insert(0, str(root / "certified_postselection_6000"))
from analyze import evaluate
from budget_analysis import add_budget

groups = {"Five": [], "Hybrid": []}
with (root / "five_leaf_postselection_6000" / "shots.jsonl").open() as ledger:
    for seed, line in zip(range(3300000, 3306000), ledger, strict=True):
        for name, shot in json.loads(line).items():
            assert shot["seed"] == seed
            if seed < 3305000:
                groups[name].append(add_budget(shot))
for name, policy in (("Five", "moderate"), ("Five", "budget"), ("Hybrid", "moderate")):
    assert len(groups[name]) == 5000
    print(name, policy, evaluate(groups[name], policy))
PY
~~~
