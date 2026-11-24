"""Matched early-stop policies evaluated along a single physical trajectory per arm."""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"compact13_certified_recovery"))
from certify import CertifiedCompact, noisy, run_arm
from candidates import BareInnerTree, LeanResourceCat
from run_single_block_cz_controller import Reject

SEEDS = range(3200000,3206000)
POLICIES = ("moderate","strict")


class Monitor:
    hard_stop = None

    def veto(self, event, moderate=False):
        counts = self.b.gate_counts
        mark = {"event":event,"T":counts["T"]+counts["TDG"]}
        if not hasattr(self,"marks"):
            self.marks = {}
            self.record.append({"postselection":self.marks})
        for key in POLICIES if moderate else ("strict",):
            self.marks.setdefault(key,mark)
            if key == self.hard_stop:
                raise Reject("postselection_"+event)

    def terminal_screen_sweep(self,sweep):
        outcome,flag = super().terminal_screen_sweep(sweep)
        if outcome != "zero_accept":
            self.veto("screen_"+outcome,moderate=outcome=="syndrome_fallback")
        return outcome,flag

    def direct_recover(self,prefix,flag=None):
        self.veto("ordinary_gauged_recovery")
        return super().direct_recover(prefix,flag)

    def direct_reference(self,prefix,flagged):
        self.veto("full_gauged_reference",moderate=True)
        return super().direct_reference(prefix,flagged)

    def recover_z(self,prefix):
        self.veto("ordinary_cat_Z_recovery")
        return super().recover_z(prefix)

    def data_recover(self,name,initial):
        if name.startswith("short_cat/") and name.endswith("/full"):
            self.veto("full_cat_vote_recovery",moderate=True)
        return super().data_recover(name,initial)


class Compact(Monitor,CertifiedCompact): pass
class Tree(Monitor,BareInnerTree): pass
class Cat(Monitor,LeanResourceCat): pass

ARMS = (Compact,Tree,Cat)


def trial(seed):
    group = {}
    for cls in ARMS:
        r = run_arm(cls, seed, noisy.RATES)
        assert r["status"]=="completed", (cls.__name__,seed,r.get("detail"))
        d = r.get("diagnostics",{})
        m = r["metrics"]
        gates=m["gate_counts"]
        group[cls.__name__] = dict(seed=seed,accepted=r["accepted"],reason=r["reason"],
            matched=d.get("decoded_target_within_tolerance",False),fidelity=d.get("decoded_target_fidelity"),
            t=gates.get("T",0)+gates.get("TDG",0),faults=m["sampled_noise_events"],
            veto=next((item["postselection"] for item in r["record"] if "postselection" in item),{}))
    return group


if __name__=="__main__":
    with (HERE/"plan.json").open("x") as f:
        json.dump(dict(seed_range=[SEEDS.start, SEEDS.stop-1],shots_per_arm=len(SEEDS),rates=noisy.RATES,
            primary="moderate",secondary="strict",endpoints=["mean accepted decoded fidelity","acceptance","T and Tdg per correct output"],
            primary_rule="reject syndrome fallback on any terminal screen or a full gauged/short-cat vote recovery",
            secondary_rule="also reject terminal flags and any ordinary vote recovery",
            native_rotation_reference=.9986560625271139,heralded_clifford_T_reference=.9975394866058183),f,indent=2)
    with (HERE/"shots.jsonl").open("x") as f, ProcessPoolExecutor(9) as pool:
        for n,row in enumerate(pool.map(trial,SEEDS),1):
            f.write(json.dumps(row)+"\n")
            f.flush()
            if n%1000==0: print(n,flush=True)
