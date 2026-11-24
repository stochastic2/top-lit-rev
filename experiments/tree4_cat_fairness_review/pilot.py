"""Fresh exploratory pilot; no entry filter on any arm."""
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import json
from block_cat_probe import HERE, BlockCat, PostBlockCat, LeanResourceCat, noisy
from candidates import BareInnerTree
from holdout import run_arm

ARMS=(BareInnerTree, LeanResourceCat, BlockCat, PostBlockCat)
def trial(seed):
    rows={}
    for cls in ARMS:
        row=run_arm(cls,seed,noisy.RATES)
        keep=("seed","status","accepted","reason","diagnostics","metrics")
        if row.get("accepted") and not row["diagnostics"]["decoded_target_within_tolerance"]:
            keep+=("noise_events","record")
        rows[cls.__name__]={key:row[key] for key in keep if key in row}
    return rows

if __name__=="__main__":
    groups=[]
    with ProcessPoolExecutor(8) as pool, (HERE/"pilot.jsonl").open("x") as f:
        for group in pool.map(trial,range(2510000,2510128)):
            f.write(json.dumps(group)+"\n"); f.flush(); groups.append(group)
    result={}
    for cls in ARMS:
        rows=[g[cls.__name__] for g in groups]
        assert all(r["status"]=="completed" for r in rows)
        n=sum(r.get("diagnostics",{}).get("decoded_target_within_tolerance",False) for r in rows)
        c=Counter()
        for r in rows:
            c.update(r["metrics"]["gate_counts"])
        result[cls.__name__]=dict(accepted=sum(r["accepted"] for r in rows),matches=n,
                                   cx_per_match=c["CX"]/n,t_per_match=(c["T"]+c["TDG"])/n,
                                   peak=max(r["metrics"]["peak_live_qubits"] for r in rows))
    (HERE/"pilot_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result)
