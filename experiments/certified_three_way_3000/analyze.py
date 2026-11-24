"""Validate the paired ledger, estimate the predeclared endpoints, and quantify uncertainty."""
from collections import Counter
from itertools import combinations
from hashlib import sha256
import json

import numpy as np
from scipy.stats import binom, binomtest
from run import ARMS, SEEDS, HERE


def interval(x):
    return np.quantile(x,[.025,.975]).tolist()


def exact_swap(left, right):
    """Swap complete outcomes within seed under the joint arm-exchangeability null.

    Exact up to rounding infidelities to 12 decimal places. Group identical rare
    outcome types and analytically average over ordinary accept/reject discordances.
    """
    types = Counter()
    fixed_n = ordinary = 0
    fixed_loss = 0.
    for (a,_,_,l),(b,_,_,r) in zip(left,right):
        x,y = sorted(((int(a),round(l,12)), (int(b),round(r,12))))
        if x == y:
            fixed_n += x[0]
            fixed_loss += x[1]
        elif x[1] == y[1] == 0:
            ordinary += 1
        else:
            types[x,y] += 1
    na,_,_,la = left.sum(axis=0)
    nb,_,_,lb = right.sum(axis=0)
    threshold = abs(la/na-lb/nb)
    k = np.arange(ordinary+1)
    weight = binom.pmf(k,ordinary,.5)
    states = [(fixed_n,fixed_loss,1.)]
    for (x,y),count in types.items():
        states = [(n+j*x[0]+(count-j)*y[0], loss+j*x[1]+(count-j)*y[1], p*pj)
                  for n,loss,p in states for j,pj in enumerate(binom.pmf(np.arange(count+1),count,.5))]
    pvalue = 0.
    for n,loss,p in states:
        size = n+k
        delta = loss/size - (la+lb-loss)/(na+nb-size)
        pvalue += p * weight[np.abs(delta)>=threshold-1e-13].sum()
    return min(1.,pvalue)


def main():
    names = [cls.__name__ for cls in ARMS]
    data = {n:[] for n in names}
    misses = {n:[] for n in names}
    with (HERE/"shots.jsonl").open() as ledger:
        for seed,line in zip(SEEDS,ledger,strict=True):
            group = json.loads(line)
            assert set(group)==set(names)
            for name,row in group.items():
                assert row["seed"]==seed and row["status"]=="completed", (seed,name,row.get("detail"))
                a = row["accepted"]
                g = row["metrics"]["gate_counts"]
                d = row.get("diagnostics",{})
                assert bool(d)==a
                good = bool(d.get("decoded_target_within_tolerance"))
                loss = (1-d["decoded_target_fidelity"]) if a else 0.
                if a:
                    assert abs(loss)<=1.000000001 and good==(abs(loss)<=1e-10)
                    if not good:
                        misses[name].append([seed,1-loss,row["metrics"]["sampled_noise_events"]])
                data[name].append([int(a),int(good),g.get("T",0)+g.get("TDG",0),loss])
    data = {k:np.array(v) for k,v in data.items()}
    rng = np.random.default_rng(41219)
    bootstrap = {n:[] for n in names}
    for _ in range(100):
        idx = rng.integers(len(SEEDS),size=(100,len(SEEDS)))
        for n in names:
            a,m,t,l = data[n][idx].sum(axis=1).T
            bootstrap[n].append(np.column_stack((a/len(SEEDS),t/m,1-l/a)))
    bootstrap = {n:np.concatenate(v) for n,v in bootstrap.items()}
    out = dict(arms={},pairs={},ledger_sha256=sha256((HERE/"shots.jsonl").read_bytes()).hexdigest())
    for n in names:
        a,m,t,l = data[n].sum(axis=0)
        ci = binomtest(int(a-m),int(a)).proportion_ci(confidence_level=.95)
        out["arms"][n] = dict(attempts=len(SEEDS),accepted=int(a),matched=int(m),acceptance=a/len(SEEDS),
                              decoded_fidelity=1-l/a,total_T_TDG=int(t),T_per_match=t/m,
                              miss_rate_exact_95=[ci.low,ci.high],mismatches=misses[n])
    for n,v in combinations(names,2):
        diff = bootstrap[n]-bootstrap[v]
        out["pairs"][n+" minus "+v] = dict(acceptance_difference_95=interval(diff[:,0]),
                 t_per_match_difference_95=interval(diff[:,1]),decoded_fidelity_difference_95=interval(diff[:,2]),
                 p_exact_swap=exact_swap(data[n],data[v]))
    pairs = sorted(out["pairs"].values(),key=lambda v:v["p_exact_swap"])
    adjusted = 0.
    for i,p in enumerate(pairs):
        adjusted = max(adjusted,min(1.,(len(pairs)-i)*p["p_exact_swap"]))
        p["p_holm"] = adjusted
    (HERE/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
