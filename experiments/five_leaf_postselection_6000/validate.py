"""Compare the inferred stops to physical early rejection on representative seeds."""
import json
from study import HERE, Five, Hybrid, CappedFive, CappedHybrid, PostBlockCat, BlockCat, run_arm, noisy
from budget_analysis import add_budget

if __name__=="__main__":
    checked=[]
    seen=set()
    with (HERE/"shots.jsonl").open() as f:
        for line in f:
            for name,s in json.loads(line).items():
                cls,base,cap = (Five,PostBlockCat,CappedFive) if name=="Five" else (Hybrid,BlockCat,CappedHybrid)
                add_budget(s)
                for policy in ("moderate","strict","budget","baseline"):
                    mark=s["veto"].get(policy)
                    label="stopped" if mark else ("accepted" if s["accepted"] else "rejected")
                    key=(name,policy,label)
                    if key in seen: continue
                    seen.add(key)
                    real = base if policy=="baseline" else cap if policy=="budget" else type("Stopping"+name,(cls,),{"hard_stop":policy})
                    row=run_arm(real,s["seed"],noisy.RATES)
                    assert row["status"]=="completed"
                    assert row["accepted"]==(s["accepted"] and mark is None)
                    assert row.get("diagnostics",{}).get("decoded_target_fidelity")== (s["fidelity"] if mark is None else None)
                    counts=row["metrics"]["gate_counts"]
                    assert counts.get("T",0)+counts.get("TDG",0)==(s["t"] if mark is None else mark["T"])
                    checked.append([*key,s["seed"],row["reason"]])
            if len(checked)==22: break
    assert len(checked)==22,len(checked)
    (HERE/"validation.json").write_text(json.dumps(checked,indent=2)+"\n")
    print(len(checked),"independent early-stop and baseline replays passed")
