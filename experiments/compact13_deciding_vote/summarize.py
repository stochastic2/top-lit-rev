from pathlib import Path
import json
from collections import Counter
from statistics import fmean
import numpy as np

here=Path(__file__).resolve().parent
def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]
paired=read(here/"shots.jsonl")
rows={key:[r[key] for r in paired] for key in ("LeanResourceCat","DeferredCompact")}
rows["RecoveringCompact"]=read(here/"recovery_shots.jsonl")
rows["HookCompact"]=read(here.parent/"compact13_cat_comparison/shots.jsonl")
idx=np.random.default_rng(51).integers(500,size=(10000,500))
out={}
for name,group in rows.items():
    assert [r["seed"] for r in group]==list(range(2610000,2610500))
    assert all(r["status"]=="completed" for r in group)
    acc=np.array([int(r["accepted"]) for r in group])
    good=np.array([int(r.get("diagnostics",{}).get("decoded_target_within_tolerance",False)) for r in group])
    cx=np.array([r["metrics"]["gate_counts"]["CX"] for r in group])
    t=sum(sum(r["metrics"]["gate_counts"].get(k,0) for k in ("T","TDG")) for r in group)
    costs=cx[idx].sum(axis=1)/good[idx].sum(axis=1)
    if name=="LeanResourceCat":
        ref_acc,ref_costs=acc,costs
    out[name]=dict(accepted=int(acc.sum()),target_matches=int(good.sum()),
        accepted_fidelity=fmean(r["diagnostics"]["decoded_target_fidelity"] for r in group if r["accepted"]),
        peak=max(r["metrics"]["peak_live_qubits"] for r in group),cx_per_match=cx.sum()/good.sum(),
        t_per_match=t/good.sum(),delta_acceptance_95=np.quantile((acc-ref_acc)[idx].mean(axis=1),[.025,.975]).tolist(),
        cx_ratio_95=np.quantile(costs/ref_costs,[.025,.975]).tolist(),reasons=Counter(r["reason"] for r in group if not r["accepted"]),
        misses=[(r["seed"],r["metrics"]["sampled_noise_events"],r["diagnostics"]["decoded_target_fidelity"])
                for r in group if r["accepted"] and not r["diagnostics"]["decoded_target_within_tolerance"]])
(here/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
for k,r in out.items(): print(k,{x:y for x,y in r.items() if x!="reasons"})
