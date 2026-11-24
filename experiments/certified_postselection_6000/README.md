# Postselection on certified C4-Helix factories

The circuits are CertifiedCompact (the 630-CX schedule), BareInnerTree and LeanResourceCat. The fixed primary cohort contains 6,000 common seeds per circuit. Noise rates and endpoints are in [the plan](plan.json).

The primary policy stops on a nonzero syndrome that triggers terminal-screen fallback or a full recovery reference during a vote. In particular, it allows a terminal flag by itself to proceed through the original verified flag recovery. The secondary strict policy additionally stops on a terminal flag or any ordinary vote recovery. Both policies retain all other checks of the underlying certified circuit.

[The controller mixin](run.py) can execute a real early stop by setting its class attribute `hard_stop` to `"moderate"` or `"strict"`. The matched experiment records the first veto for each policy and continues the baseline circuit. Up to that veto, gates, readouts, corrections and T cost are identical for the two executions. Rejected disposal uses no T gates. An accepted trajectory therefore incurs its actual gate cost and obtains its original decoded state. [Independent hard-stop replays](validation.json) check early disposal, T totals, and retained fidelities. Restricting acceptance in this way inherits the original two-location accepted-output theorem.

Two cat failures in the exploratory prefix motivated an additional early stop before a 121st T/T† gate, in combination with the primary veto. [Its separate plan](budget_plan.json) uses only the final 4,000 seeds for evaluation. The cost cap is a directly observable indicator of extra voting or recovery work. [The physical budget guard](budget.py) and [hard-stop replays](budget_validation.json) verify the implementation.

The denominator of mean decoded fidelity is the number of accepted shots. T cost sums spending over every attempted factory, including runs that stop early, and divides by accepted target matches at tolerance 1e-10. These policies inspect only gate counts and controller reports. Injected-fault locations, simulated fidelity and ideal decoding enter only the evaluation.

For each arm and policy, the summary gives a conservative individual one-sided 95% lower confidence bound on mean conditional fidelity. The bound uses the exact binomial upper limit on conditional mismatch probability, allows any missed output to have zero fidelity, and accounts for the numerical matching tolerance. It assumes independent attempts within each circuit. The primary one-sided Fisher test compares mismatch proportions in retained and discarded baseline accepts; its three-arm Holm adjustment is included separately. The budget rule and the strict policy are secondary. Physical benchmarks refer to the [same-state preparation calculation](../tree4_cat_fairness_review/comparison_500/direct_physical.json).

[Primary outcomes](summary.json) · [Held-out budget outcomes](budget_summary.json) · [Paired trajectory ledger](shots.jsonl)
