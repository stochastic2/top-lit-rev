"""Fresh paired transfer of the fixed postselection policies to both five-leaf schedules."""
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent/"certified_postselection_6000"), str(HERE.parent/"tree4_cat_fairness_review")]
from run import Monitor, run_arm, noisy
from block_cat_probe import PostBlockCat, BlockCat
from budget import Budget

class Five(Monitor, PostBlockCat): pass
class Hybrid(Monitor, BlockCat): pass
class CappedFive(Budget, Five): pass
class CappedHybrid(Budget, Hybrid): pass

ARMS = (Five, Hybrid)
SEEDS = range(3300000,3306000)

def trial(seed):
    group = {}
    for cls in ARMS:
        row = run_arm(cls,seed,noisy.RATES)
        assert row["status"]=="completed", (seed,cls.__name__,row.get("detail"))
        d = row.get("diagnostics",{})
        gates = row["metrics"]["gate_counts"]
        group[cls.__name__] = dict(seed=seed,accepted=row["accepted"],reason=row["reason"],
            matched=d.get("decoded_target_within_tolerance",False),fidelity=d.get("decoded_target_fidelity"),
            t=gates.get("T",0)+gates.get("TDG",0),faults=row["metrics"]["sampled_noise_events"],
            veto=next((r["postselection"] for r in row["record"] if "postselection" in r),{}))
    return group


if __name__=="__main__":
    with (HERE/"plan.json").open("x") as f:
        json.dump(dict(seeds_inclusive=[SEEDS.start,SEEDS.stop-1],arms=[c.__name__ for c in ARMS],rates=noisy.RATES,
            primary="selective versus baseline, Holm across the two schedules",
            secondary=["strict: also reject any terminal flag or ordinary vote recovery",
                       "budget: selective plus stop before T or Tdg number 121"],
            selective="reject terminal syndrome fallback or a full short-cat vote recovery"),f,indent=2)
    with (HERE/"shots.jsonl").open("x") as out, ProcessPoolExecutor(9) as pool:
        for n,group in enumerate(pool.map(trial,SEEDS),1):
            out.write(json.dumps(group)+"\n")
            out.flush()
            if n%1000==0: print(n,flush=True)
