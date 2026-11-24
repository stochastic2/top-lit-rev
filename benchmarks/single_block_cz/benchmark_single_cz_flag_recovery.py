"""Short reproducible four-arm comparison; the user controls shot count.

Compare strict rejection and flag-dependent data recovery for gauging and
the genuine GHZ20-CZ baseline. Both use the same physical noise, source,
ordinary flag gadgets and seeds. Costs include rejected attempts/fallbacks.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import json
import subprocess
import sys

from simulate_single_block_cz_depolarizing import write_json
from verify_single_block_cz_run import verify_run

ARMS=(("gauging-reject","gauging","reject"),("gauging-data","gauging","data"),
      ("cat-reject","cat","reject"),("cat-data","cat","data"))


def analyze(directory):
    directory=Path(directory).resolve()
    summaries={}
    manifests={}
    shots={}
    verified={}
    for arm,route,policy in ARMS:
        folder=directory/arm
        manifests[arm]=json.loads((folder/"manifest.json").read_text())
        summaries[arm]=json.loads((folder/"summary.json").read_text())
        shots[arm]=[json.loads(s) for s in (folder/"shots.jsonl").read_text().splitlines()]
        assert manifests[arm]["flag_recovery"]==policy
        assert manifests[arm]["direct_cz_extraction"]==("cat" if route=="cat" else "auto")
        verified[arm]=verify_run(folder)
    first=manifests[ARMS[0][0]]
    for manifest in manifests.values():
        for key in ("noise","graph","profile","source_extraction","history_policy",
                    "verification_extraction","max_flag_recoveries","shots_requested","seed","noise_seed_base","limits"):
            if key=="max_flag_recoveries":
                assert manifest.get(key,2)==first.get(key,2), "Unmatched comparison setting: "+key
            else:
                assert manifest[key]==first[key], "Unmatched comparison setting: "+key
        assert manifest["source_sha256"]==first["source_sha256"] or all(
            manifest["source_sha256"][name]==digest for name,digest in first["source_sha256"].items())
    paired={}
    for route in ("gauging","cat"):
        old={r["seed"]:r for r in shots[route+"-reject"] if r["execution_status"]=="completed"}
        new={r["seed"]:r for r in shots[route+"-data"] if r["execution_status"]=="completed"}
        common=sorted(old.keys() & new.keys())
        gains=losses=preserved=0
        for seed in common:
            a,b=old[seed],new[seed]
            gains+=not a["accepted"] and b["accepted"]
            losses+=a["accepted"] and not b["accepted"]
            if a["accepted"]:
                assert b["accepted"], "Strictly accepted seed lost under recovery"
                assert a["metrics"]["gate_counts"]==b["metrics"]["gate_counts"]
                assert a["diagnostics"]==b["diagnostics"]
                preserved+=1
        paired[route]={"completed_pairs":len(common),"gained_acceptances":gains,
                       "lost_acceptances":losses,"strict_acceptances_preserved":preserved}
    report={"summaries":summaries,"paired":paired,"saved_run_verification":verified,
            "matched_fidelity_claim":False,"scope":"Pilot; new accepted outputs can include >2 faults"}
    write_json(directory/"comparison.json",report)
    lines=["# Flag-dependent recovery comparison", "",
           "Same source, physical noise, graph, capacities, and seeds. Cat arms use a genuine GHZ20 CZ measurement.","",
           "| Arm | Accepted / attempts | Target matches / assessed | Mean decoded F | CX / accepted | Recovered episodes |", 
           "|---|---:|---:|---:|---:|---:|"]
    def number(v):return "—" if v is None else f"{v:.4f}"
    for arm,_,_ in ARMS:
        s=summaries[arm]
        cx=s["cost_per_accepted_completed"].get("CX") if s["cost_per_accepted_completed"] else None
        lines.append(f"| {arm} | {s['accepted']} / {s['attempts']} | {s['accepted_within_target_tolerance']} / {s['accepted_assessed']} | "
                     f"{number(s['mean_decoded_fidelity'])} | {number(cx)} | {s['successful_flag_recoveries']} |")
    lines += ["", "Executed CX counts include rejected attempts and all fallback operations. Missing computational results remain unresolved.", "",
              "Paired-seed changes: `"+json.dumps(paired,sort_keys=True)+"`.", "",
              "This sample does not establish equal population fidelity. Inspect fidelity and cost together, and increase shots before drawing performance conclusions.", ""]
    (directory/"comparison.md").write_text("\n".join(lines))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shots",type=int,default=40)
    p.add_argument("--seed",type=int,default=1000)
    p.add_argument("--workers",type=int,default=1)
    p.add_argument("--graph",choices=("compact13","current20"),default="compact13")
    p.add_argument("--source-extraction",choices=("decoded_flags","rolling_flags"),default="decoded_flags")
    p.add_argument("--history-policy",choices=("triple","adaptive"),default="triple")
    p.add_argument("--max-flag-recoveries",type=int,default=8)
    for option,default in (("two-qubit-infidelity","1e-3"),("one-qubit-infidelity","0"),
                           ("t-infidelity",None),("idle-infidelity","0"),
                           ("preparation-flip-probability","0"),("readout-flip-probability","1e-3")):
        p.add_argument("--"+option,default=default)
    p.add_argument("--attempt-timeout",type=float,default=60)
    p.add_argument("--max-terms",type=int,default=4096)
    p.add_argument("--max-factors",type=int,default=4096)
    p.add_argument("--max-operations",type=int,default=200000)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--analyze-only",action="store_true")
    args=p.parse_args()
    if args.analyze_only:
        print(json.dumps(analyze(args.output_dir)["paired"],indent=2))
        return
    if args.shots<1 or not 1<=args.workers<=4:
        p.error("Positive shots and one to four worker processes required")
    if args.output_dir.exists():p.error("Choose a new output directory")
    args.output_dir.mkdir(parents=True)
    root=Path(__file__).resolve().parent
    def run(arm,route,policy):
        script="simulate_single_block_cz_cat_depolarizing.py" if route=="cat" else "simulate_single_block_cz_depolarizing.py"
        command=[sys.executable,str(root/script),"--shots",str(args.shots),"--seed",str(args.seed),
                 "--profile","recovery","--verification-extraction","flags","--flag-recovery",policy,
                 "--output-dir",str((args.output_dir/arm).resolve())]
        for key in ("graph","source_extraction","history_policy","max_flag_recoveries","two_qubit_infidelity","one_qubit_infidelity",
                    "t_infidelity","idle_infidelity","preparation_flip_probability","readout_flip_probability",
                    "attempt_timeout","max_terms","max_factors","max_operations"):
            if getattr(args,key) is not None:
                command += ["--"+key.replace("_","-"),str(getattr(args,key))]
        write_json(args.output_dir/(arm+"-command.json"),command)
        with (args.output_dir/(arm+".log")).open("x") as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        summary=json.loads((args.output_dir/arm/"summary.json").read_text())
        return arm,summary["accepted"],summary["attempts"]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(run,*arm) for arm in ARMS]
        for future in as_completed(futures):
            arm,k,n=future.result()
            print(f"{arm}: {k}/{n} accepted",flush=True)
    report=analyze(args.output_dir)
    print(json.dumps(report["paired"],indent=2))
    print(str((args.output_dir/"comparison.md").resolve()))


if __name__=="__main__":main()
