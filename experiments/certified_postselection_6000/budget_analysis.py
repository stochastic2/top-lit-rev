"""Evaluate the prespecified supplementary policy only on its untouched suffix."""
import json
from copy import deepcopy
from run import HERE, ARMS, run_arm, noisy, SEEDS
from budget import BudgetCat, BudgetCompact, BudgetTree
from analyze import evaluate

def add_budget(s):
    mark = s["veto"].get("moderate")
    t = mark["T"] if mark else s["t"]
    if t>120:
        s["veto"]["budget"] = {"event":"T_budget","T":120}
    elif mark:
        s["veto"]["budget"] = mark
    return s


def validate():
    tests=[]
    chosen={3200166,3201247,3200681,3200000,3200001,3200002}
    for line in (HERE/"shots.jsonl").open():
        rows=json.loads(line)
        seed=rows["Cat"]["seed"]
        if seed>max(chosen):break
        if seed not in chosen:continue
        for name,cls in [("Cat",BudgetCat),("Compact",BudgetCompact),("Tree",BudgetTree)]:
            s=add_budget(rows[name])
            mark=s["veto"].get("budget")
            r=run_arm(cls,seed,noisy.RATES)
            assert r["status"]=="completed" and r["accepted"]==(s["accepted"] and not mark)
            counts=r["metrics"]["gate_counts"]
            assert counts.get("T",0)+counts.get("TDG",0)==(mark["T"] if mark else s["t"])
            assert r.get("diagnostics",{}).get("decoded_target_fidelity")== (None if mark else s["fidelity"])
            tests.append([seed,name,r["accepted"],r["reason"]])
    assert len(tests)==3*len(chosen)
    (HERE/"budget_validation.json").write_text(json.dumps(tests,indent=2)+"\n")


def summarize():
    with (HERE/"budget_plan.json").open() as f: plan=json.load(f)
    lo,hi=plan["held_out_suffix"]
    groups={c.__name__:[] for c in ARMS}
    with (HERE/"shots.jsonl").open() as f:
        for seed,line in zip(SEEDS,f,strict=True):
            if not lo<=seed<=hi: continue
            for n,s in json.loads(line).items():
                assert s["seed"]==seed
                groups[n].append(add_budget(s))
    assert all(len(v)==hi-lo+1 for v in groups.values())
    result={n:{k:evaluate(rows,k) for k in ("baseline","moderate","budget")} for n,rows in groups.items()}
    (HERE/"budget_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    for n,v in result.items():
        for p,r in v.items():
            print(n,p,r["accepted"],len(r["misses"]),r["mean_decoded_fidelity"],r["T_per_match"],r["fidelity_conservative_lower_95"])


if __name__=="__main__":
    import sys
    validate() if sys.argv[1:]==["validate"] else summarize()
