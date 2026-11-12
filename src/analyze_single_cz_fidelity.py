"""Recompute fidelity statistics for saved matched CZ runs; no resampling.

Binomial intervals concern the event 'decoded target mismatch at tolerance',
not an assumed Bernoulli model for every possible quantum-state infidelity.
No between-protocol independence or paired-noise significance is assumed.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from math import exp,lgamma,log,log1p
import argparse
import json
from verify_single_block_cz_run import verify_run


def binomial_cdf(k,n,p):
    if k<0:return 0.0
    if k>=n or p==0:return 1.0
    if p==1:return 0.0
    terms=[lgamma(n+1)-lgamma(j+1)-lgamma(n-j+1)+j*log(p)+(n-j)*log1p(-p)
           for j in range(k+1)]
    largest=max(terms)
    return min(1.0,exp(largest)*sum(exp(t-largest) for t in terms))


def cdf_root(k,n,target):
    lo,hi=0.0,1.0
    for _ in range(90):
        mid=(lo+hi)/2
        if binomial_cdf(k,n,mid)>target:lo=mid
        else:hi=mid
    return (lo+hi)/2


def binomial_intervals(k,n,alpha=.05):
    if not n:return None
    two=[0.0 if k==0 else cdf_root(k-1,n,1-alpha/2),
         1.0 if k==n else cdf_root(k,n,alpha/2)]
    upper=1.0 if k==n else cdf_root(k,n,alpha)
    if k==0:assert abs(upper-(1-alpha**(1/n)))<1e-12
    return {"Clopper_Pearson_two_sided_95":two,"exact_one_sided_95_upper":upper}


def rejection_group(reason):
    if "known_unused_source" in reason:return "source_retry_limit"
    if "known_unused_graph" in reason:return "graph_retry_limit"
    if reason.startswith("verification_flag:"):return "post_source_flag"
    if reason.startswith("unstable_commuting_history:"):return "unstable_history"
    if reason.startswith("insufficient_"):return "insufficient_positive_rounds"
    return reason


def analyze(root):
    root=Path(root).resolve();runs={};common=[];hashes=[]
    for path in sorted(root.glob("*/manifest.json")):
        directory=path.parent
        manifest=json.loads(path.read_text())
        verification=verify_run(directory)
        summary=json.loads((directory/"summary.json").read_text())
        records=[json.loads(s) for s in (directory/"shots.jsonl").read_text().splitlines()]
        accepted=[r for r in records if r.get("accepted")]
        assessed=[r for r in accepted if r.get("diagnostic_status")=="completed"]
        bad=[r for r in assessed if not r["diagnostics"]["decoded_target_within_tolerance"]]
        n,k=len(assessed),len(bad)
        intervals=binomial_intervals(k,n)
        costs=summary["cost_per_accepted_completed"]
        rates=manifest["noise"]["rates"]
        common.append({key:manifest.get(key) for key in
                       ("target","profile","source_extraction","history_policy","limits","seed","noise_seed_base")}
                      | {"rates":rates})
        hashes.append(manifest["source_sha256"])
        runs[directory.name]={
            "verification":verification,"manifest":str(path),"route":manifest["route"],
            "checks":manifest.get("verification_extraction","cats"),
            "attempts":summary["attempts"],"accepted":len(accepted),"unresolved":summary["unresolved"],
            "assessed":n,"missing_accepted_diagnostics":len(accepted)-n,
            "acceptance":len(accepted)/len(records),"acceptance_interval":binomial_intervals(len(accepted),len(records)),
            "mean_decoded_fidelity":summary["mean_decoded_fidelity"],
            "mean_decoded_infidelity":1-summary["mean_decoded_fidelity"] if n else None,
            "mean_raw_fidelity":sum(r["diagnostics"]["raw_physical_target_fidelity"] for r in assessed)/n if n else None,
            "target_mismatches":k,"target_mismatch_intervals":intervals,
            "fidelity_histogram":dict(Counter(str(r["diagnostics"]["decoded_target_fidelity"]) for r in assessed)),
            "correctable_physical_residual_only":sum(r["diagnostics"]["decoded_target_within_tolerance"] and
                                                     r["diagnostics"]["raw_physical_target_fidelity"]<1-1e-10 for r in assessed),
            "CX_per_accepted":costs.get("CX") if costs else None,
            "T_TDG_per_accepted":sum(costs.get(x,0) for x in ("T","TDG")) if costs else None,
            "cost_is_matched_fidelity":False,
            "rejection_groups":dict(Counter({g:sum(v for reason,v in summary["rejection_counts"].items()
                                                    if rejection_group(reason)==g)
                                               for g in {rejection_group(r) for r in summary["rejection_counts"]}})),
            "accepted_fault_count_histogram":dict(Counter(r["metrics"]["sampled_noise_events"] for r in assessed)),
            "accepted_mismatches":[{"shot":r["shot_index"],"seed":r["seed"],
                                    "faults":r["metrics"]["sampled_noise_events"],
                                    "fidelity":r["diagnostics"]["decoded_target_fidelity"],
                                    "logical_density_real":r["diagnostics"]["logical_density_real"],
                                    "logical_density_imag":r["diagnostics"]["logical_density_imag"],
                                    "details":r["detail_directory"]} for r in bad]}
        for mismatch in runs[directory.name]["accepted_mismatches"]:
            detail=Path(mismatch["details"])
            controller=json.loads((detail/"controller.json").read_text())
            meters=json.loads((detail/"measurements.json").read_text())
            mismatch["sampled_faults"]=json.loads((detail/"noise.json").read_text())["sampled"]
            mismatch["CZ_leaf_records"]=[]
            for record in controller:
                if record.get("extraction")!="verified_cat_CZ":continue
                actual=[v["actual"] for v in meters if v["context"]==record["check"] and v["label"].startswith("L")]
                mismatch["CZ_leaf_records"].append({"check":record["check"],"actual_leaf_parity":sum(actual)%2,
                                                   "reported_leaf_parity":record["reported_parity"]})
    if not runs:raise ValueError("No saved runs found")
    shared=set.intersection(*(set(h) for h in hashes))
    return {"scope":"saved matched-run fidelity analysis; no simulation campaign",
            "matched_common_settings":all(c==common[0] for c in common),"common_settings":common[0],
            "shared_runtime_hashes_match":all(len({h[name] for h in hashes})==1 for name in shared),
            "confidence_scope":"per-arm exact binomial target-mismatch bounds at saved diagnostic tolerance",
            "not_a_between_protocol_significance_test":True,
            "note":"shared seeds couple trajectories; zero observed failures do not imply perfect population fidelity",
            "runs":runs}


def markdown(result):
    lines=["# Fidelity analysis of matched CZ factory runs","",
           "All saved controller/report certificates and accepted complex-output diagnostics were rechecked.",
           "Common source, noise, history and capacity settings match: **"+str(result["matched_common_settings"])+"**.",
           "Shared runtime hashes match: **"+str(result["shared_runtime_hashes_match"])+"**.","",
           "| Run | Acceptance | Mean decoded fidelity | Mismatches / accepted | 95% upper mismatch probability | CX / accepted |",
           "|---|---:|---:|---:|---:|---:|"]
    for name,r in result["runs"].items():
        upper=r["target_mismatch_intervals"]["exact_one_sided_95_upper"]
        lines.append(f"| {name} | {r['accepted']}/{r['attempts']} | {r['mean_decoded_fidelity']:.6f} | "
                     f"{r['target_mismatches']}/{r['assessed']} | {100*upper:.2f}% | {r['CX_per_accepted']:,.1f} |")
    best=max(result["runs"],key=lambda n:result["runs"][n]["acceptance"])
    cheapest=min((n for n,r in result["runs"].items() if r["CX_per_accepted"] is not None),
                 key=lambda n:result["runs"][n]["CX_per_accepted"])
    lines += ["","Fidelity is conditional on acceptance and uses the same ideal read-only decoder for every route.",
              "The intervals bound the probability of a non-target accepted trajectory at tolerance; they are not",
              "a claim that all possible infidelities are Bernoulli. Zero failures leave substantial uncertainty.",
              "They are individual bounds, not a simultaneous four-way confidence statement.",
              "Shared seeds couple simulations, so no unqualified independent-sample significance test is reported.",
              "These bounds alone do not establish a between-protocol fidelity advantage.","",
              f"{best} has the highest observed acceptance. {cheapest} has the lowest observed CX cost per",
              "accepted output. These are different objectives, and the outputs are not certified to matched",
              "population fidelity. Fault-free diagnostics cannot be used to discard a bad accepted output",
              "in the physical factory.","","## Accepted mismatches",""]
    for name,r in result["runs"].items():
        for mismatch in r["accepted_mismatches"]:
            state="decoded |11>" if mismatch["logical_density_real"][3][3]>1-1e-10 else "non-target logical density"
            lines += [f"{name}, shot {mismatch['shot']}, seed {mismatch['seed']}: {state}, "
                      f"fidelity {mismatch['fidelity']}, {mismatch['faults']} sampled faults.", "",
                      "| CZ check | Actual leaf parity bit | Reported parity bit |", "|---|---:|---:|"]
            for record in mismatch["CZ_leaf_records"]:
                lines.append(f"| {record['check']} | {record['actual_leaf_parity']} | {record['reported_leaf_parity']} |")
            lines += ["","Actual leaf parity is a trustworthy CZ sign only if cat phase is correct.",
                      "ZZ resource checks verify bits, not the cat phase. Faults above the two-fault",
                      "budget can therefore falsely certify a genuine negative logical branch.",""]
    lines += ["## Raw physical overlap", "",
              "| Run | Mean raw overlap | Correctable residuals with decoded fidelity one |",
              "|---|---:|---:|"]
    for name,r in result["runs"].items():
        lines.append(f"| {name} | {r['mean_raw_fidelity']:.6f} | {r['correctable_physical_residual_only']} |")
    lines += ["","Low raw overlap with decoded fidelity one is a correctable physical residual, not a logical failure.",
              "A low-weight representative for a syndrome does not itself certify the logical state.","",
              "## Resource scope","",
              "CX/accepted includes every completed rejected attempt and retry. T, preparation, readout and",
              "serial idle costs remain separate metrics in the summaries. T/Clifford/memory/preparation",
              "noise were zero in these runs; the comparison does not establish a hardware-level winner."]
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("root",type=Path)
    parser.add_argument("--output-dir",type=Path)
    args=parser.parse_args();result=analyze(args.root)
    directory=args.output_dir or args.root/"fidelity-analysis"
    directory.mkdir(parents=True,exist_ok=False)
    (directory/"analysis.json").write_text(json.dumps(result,indent=2)+"\n")
    (directory/"report.md").write_text(markdown(result))
    print(json.dumps({name:{k:r[k] for k in ("accepted","mean_decoded_fidelity","target_mismatches",
                                            "target_mismatch_intervals","CX_per_accepted")}
                      for name,r in result["runs"].items()},indent=2))
