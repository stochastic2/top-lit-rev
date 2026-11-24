"""Verify paired counterfactual counts against controllers that really reject and dispose."""
import json
from run import HERE, Compact, Tree, Cat, CertifiedCompact, BareInnerTree, LeanResourceCat, POLICIES, trial, noisy, run_arm

# Includes previously failing seeds plus fresh ordinary paths.
seeds=(3100063,3101089,3101011,3102010,3102270,3200001)
rows = []
for seed in seeds:
    shadow=trial(seed)
    for monitor,baseline in ((Compact,CertifiedCompact),(Tree,BareInnerTree),(Cat,LeanResourceCat)):
        s=shadow[monitor.__name__]
        for policy,cls in [("baseline",baseline)]+[(k,type("Stopping"+monitor.__name__,(monitor,),{"hard_stop":k})) for k in POLICIES]:
            r=run_arm(cls,seed,noisy.RATES)
            assert r["status"]=="completed"
            mark=s["veto"].get(policy)
            assert r["accepted"] == (s["accepted"] and mark is None)
            assert (r.get("diagnostics",{}).get("decoded_target_fidelity") ==
                    (s["fidelity"] if mark is None else None))
            g=r["metrics"]["gate_counts"]
            assert g.get("T",0)+g.get("TDG",0)==(mark["T"] if mark else s["t"])
            if mark:
                assert r["reason"]=="postselection_"+mark["event"]
            rows.append([seed,monitor.__name__,policy,r["accepted"],r.get("reason")])
(HERE/"validation.json").write_text(json.dumps(rows,indent=2)+"\n")
print(len(rows),"replays matched")
