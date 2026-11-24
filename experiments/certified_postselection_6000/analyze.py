"""Summarize nested acceptance sets; bound infidelity using bounded loss on target misses."""
from collections import Counter
import json
from math import fsum
from scipy.stats import binomtest, fisher_exact
from run import HERE, SEEDS, POLICIES, ARMS

def evaluate(group, policy):
    accepted=[]
    t=0
    stops=Counter()
    for s in group:
        mark=s["veto"].get(policy)
        if mark:
            stops[mark["event"]]+=1
            t+=mark["T"]
        else:
            t+=s["t"]
            if s["accepted"]:
                accepted.append(s)
    misses=[s for s in accepted if not s["matched"]]
    successes=len(accepted)-len(misses)
    loss=fsum(1-s["fidelity"] for s in accepted)/len(accepted)
    upper=binomtest(len(misses),len(accepted),alternative="less").proportion_ci(confidence_level=.95).high
    return dict(accepted=len(accepted),matched=successes,acceptance=len(accepted)/len(group),
                mean_decoded_fidelity=1-loss,T_total=t,T_per_match=t/successes,
                misses=[[s["seed"],s["fidelity"],s["faults"]] for s in misses],
                fidelity_conservative_lower_95=1-upper-1e-10,stop_reasons=dict(stops))

def main():
    groups={cls.__name__:[] for cls in ARMS}
    with (HERE/"shots.jsonl").open() as f:
        for seed,line in zip(SEEDS,f,strict=True):
            g=json.loads(line)
            assert g.keys()==groups.keys()
            for n,s in g.items():
                assert s["seed"]==seed and ("moderate" not in s["veto"] or "strict" in s["veto"])
                assert (s["fidelity"] is not None)==s["accepted"]
                if s["accepted"]:
                    assert s["matched"]==(abs(1-s["fidelity"])<=1e-10)
                groups[n].append(s)
    out={}
    for n,group in groups.items():
        ref=evaluate(group,"baseline")
        out[n]={"baseline":ref}
        for policy in POLICIES:
            result=evaluate(group,policy)
            kept_bad=len(result["misses"])
            cut_bad=len(ref["misses"])-kept_bad
            cut_good=ref["matched"]-result["matched"]
            result["retained_fraction_of_previous_accepts"]=result["accepted"]/ref["accepted"]
            result["removed_misses"]=cut_bad
            result["removed_matches"]=cut_good
            result["p_kept_lower_miss_rate"]=float(fisher_exact([[kept_bad,result["matched"]],[cut_bad,cut_good]],alternative="less").pvalue)
            out[n][policy]=result
    # Three primary within-arm contrasts; strict is secondary.
    primary=sorted([v["moderate"] for v in out.values()],key=lambda x:x["p_kept_lower_miss_rate"])
    adjusted=0
    for i,r in enumerate(primary):
        adjusted=max(adjusted,min(1,(len(primary)-i)*r["p_kept_lower_miss_rate"]))
        r["p_holm_three_primary"]=adjusted
    (HERE/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    for n,v in out.items():
        for p,r in v.items():
            print(n,p,r["accepted"],len(r["misses"]),r["mean_decoded_fidelity"],r["T_per_match"],r["fidelity_conservative_lower_95"],r.get("p_holm_three_primary"))

if __name__=="__main__":
    main()
