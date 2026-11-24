"""Validate the ledger, then compare fidelity, yield, and T cost for nested policies."""
import json
from scipy.stats import fisher_exact
from study import HERE, ARMS, SEEDS
from analyze import evaluate
from budget_analysis import add_budget

if __name__ == "__main__":
    groups = {c.__name__:[] for c in ARMS}
    with (HERE/"shots.jsonl").open() as f:
        for seed,line in zip(SEEDS,f,strict=True):
            group=json.loads(line)
            assert groups.keys()==group.keys()
            for name,row in group.items():
                assert row["seed"]==seed and row["accepted"]==(row["fidelity"] is not None)
                assert not row["matched"] or row["accepted"]
                if row["accepted"]:
                    assert row["matched"]==(abs(1-row["fidelity"])<=1e-10)
                groups[name].append(add_budget(row))
    result={}
    for name,group in groups.items():
        results={k:evaluate(group,k) for k in ("baseline","moderate","strict","budget")}
        for k in ("moderate","strict","budget"):
            base=results["baseline"]
            r=results[k]
            kept_bad=len(r["misses"])
            cut_bad=len(base["misses"])-kept_bad
            cut_good=base["matched"]-r["matched"]
            r["removed_misses"]=cut_bad
            r["removed_matches"]=cut_good
            r["p_kept_lower_miss_rate"]=float(fisher_exact([[kept_bad,r["matched"]],[cut_bad,cut_good]],alternative="less").pvalue)
        result[name]=results
    primary=sorted([rows["moderate"] for rows in result.values()],key=lambda r:r["p_kept_lower_miss_rate"])
    adjusted=0
    for i,r in enumerate(primary):
        adjusted=max(adjusted,min(1.,(len(primary)-i)*r["p_kept_lower_miss_rate"]))
        r["p_holm_two_primary"]=adjusted
    (HERE/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    for n,rs in result.items():
        for k,r in rs.items():
            print(n,k,r["accepted"],len(r["misses"]),r["mean_decoded_fidelity"],r["T_per_match"],r["fidelity_conservative_lower_95"],r.get("p_holm_two_primary"))
