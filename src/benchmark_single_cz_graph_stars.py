"""Matched old-stars / bare-stars / genuine-cat comparison, no hidden sweep.

All arms retain flag-dependent DATA recovery. The user controls shot count.
Schedules differ, so shared seeds do not imply paired-fault trajectories or
monotone acceptance. Report circuit length separately from amortized cost.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import argparse
import json
import statistics
import subprocess
import sys

from simulate_single_block_cz_depolarizing import write_json
from verify_single_block_cz_run import verify_run

ARMS=(("gauging-flags","gauging","flags","certified"),("gauging-bare","gauging","bare","certified"),
      ("cat-data","cat","flags","certified"))


def analyze(directory,arms=ARMS,title="Bare graph-star comparison"):
    directory=Path(directory).resolve()
    result={"arms":{},"matched_population_fidelity_claim":False,
            "paired_fault_trajectories":False,"clean_counts_are_not_amortized_costs":True}
    first=None
    for arm,route,stars,terminal,*data_option in arms:
        folder=directory/arm
        manifest=json.loads((folder/"manifest.json").read_text())
        summary=json.loads((folder/"summary.json").read_text())
        shots=[json.loads(s) for s in (folder/"shots.jsonl").read_text().splitlines()]
        verified=verify_run(folder)
        assert manifest["graph_stars"]==stars and manifest["flag_recovery"]=="data"
        if data_option:assert manifest.get("data_checks","rolling_flags")==data_option[0]
        if len(data_option)>1:assert manifest.get("gauss_frame","round_trip")==data_option[1]
        if len(data_option)>2 and data_option[2]:assert manifest["graph"]["name"]==data_option[2]
        if len(data_option)>3:assert manifest.get("conditional_checks","legacy")==data_option[3]
        if len(data_option)>4:assert manifest.get("root_recovery","reject")==data_option[4]
        assert manifest["direct_cz_extraction"]==("cat" if route=="cat" else "auto")
        assert manifest["terminal_policy"]==("intrinsic_persistent_tail" if terminal=="intrinsic" else "screen" if terminal=="screen" else
                                               "passing_rounds" if route in ("cat","direct_flags") else "certified_commuting_recovery")
        if first is None:first=manifest
        for key in ("noise","graph","profile","source_extraction","history_policy","verification_extraction",
                    "max_flag_recoveries","shots_requested","seed","noise_seed_base","limits"):
            if key=="graph" and any(len(a)>6 and a[6] for a in arms):continue
            assert manifest[key]==first[key],"Unmatched setting: "+key
        assert all(manifest["source_sha256"][name]==digest for name,digest in first["source_sha256"].items())
        cx=[s["metrics"]["gate_counts"]["CX"] for s in shots if s.get("accepted")]
        raw=[s["diagnostics"]["raw_physical_target_fidelity"] for s in shots if s.get("accepted") and
             s.get("diagnostic_status")=="completed"]
        key="direct_cat/recovery" if route in ("cat","direct_flags") else manifest["graph"]["name"]+"/recovery"
        clean=json.loads((folder/"clean-costs.json").read_text())[key]
        result["arms"][arm]={"summary":summary,"verified":verified,"clean_CX":clean["gates"]["CX"],
                             "data_checks":manifest.get("data_checks","rolling_flags"),
                             "gauss_frame":manifest.get("gauss_frame","round_trip"),"graph":manifest["graph"]["name"],
                             "conditional_checks":manifest.get("conditional_checks","legacy"),"root_recovery":manifest.get("root_recovery","reject"),
                             "mean_raw_physical_fidelity":statistics.mean(raw) if raw else None,
                             "clean_T_TDG":clean["T_or_TDG"],"peak_live":clean["peak_live"],
                             "successful_attempt_CX":{"mean":statistics.mean(cx),"median":statistics.median(cx),
                                                      "min":min(cx),"max":max(cx)} if cx else None}
    write_json(directory/"comparison.json",result)
    lines=["# "+title,"",
           "All arms use matched source selection and flag-dependent data recovery. Cat-labelled CZ uses genuine GHZ20; direct-flags is a separate global flagged-U comparator when present.","",
           "| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for arm,*_ in arms:
        row=result["arms"][arm]
        s=row["summary"]
        def fmt(value):return "—" if value is None else f"{value:,.1f}"
        mean=row["successful_attempt_CX"]["mean"] if row["successful_attempt_CX"] else None
        cost=(s["cost_per_accepted_completed"] or {}).get("CX")
        lines.append(f"| {arm} | {s['accepted']} / {s['attempts']} | {s['accepted_within_target_tolerance']} / {s['accepted_assessed']} | "
                     f"{row['clean_CX']} | {fmt(mean)} | {fmt(cost)} | {row['mean_raw_physical_fidelity'] if row['mean_raw_physical_fidelity'] is not None else '—'} |")
    lines += ["","Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. "
              "Total CX/output includes all discarded attempts and fallbacks.","",
              "Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.","",
              "Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.","",
              "Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.",""]
    (directory/"comparison.md").write_text("\n".join(lines))
    return result


def main(arms=ARMS,description=None,title="Bare graph-star comparison"):
    p=argparse.ArgumentParser(description=description or __doc__)
    p.add_argument("--shots",type=int,default=40)
    p.add_argument("--seed",type=int,default=1000)
    p.add_argument("--workers",type=int,default=1)
    p.add_argument("--graph",choices=("compact13","current20"),default="compact13")
    p.add_argument("--source-extraction",choices=("decoded_flags","rolling_flags"),default="decoded_flags")
    p.add_argument("--history-policy",choices=("triple","adaptive"),default="triple")
    p.add_argument("--max-flag-recoveries",type=int,default=8)
    p.add_argument("--data-checks",choices=("rolling_flags","compact_flags"),default="rolling_flags")
    for name,default in (("two-qubit-infidelity","1e-3"),("readout-flip-probability","1e-3"),
                         ("one-qubit-infidelity","0"),("t-infidelity",None),("idle-infidelity","0"),
                         ("preparation-flip-probability","0")):
        p.add_argument("--"+name,default=default)
    p.add_argument("--attempt-timeout",type=float,default=60)
    p.add_argument("--max-terms",type=int,default=4096)
    p.add_argument("--max-factors",type=int,default=4096)
    p.add_argument("--max-operations",type=int,default=200000)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--analyze-only",action="store_true")
    args=p.parse_args()
    if args.analyze_only:
        analyze(args.output_dir,arms,title)
        print((args.output_dir/"comparison.md").resolve())
        return
    if args.shots<1 or not 1<=args.workers<=3 or not 1<=args.max_flag_recoveries<=32:
        p.error("Positive shots, one to three workers and one to 32 recoveries required")
    if args.output_dir.exists():p.error("Choose a fresh output directory")
    args.output_dir.mkdir(parents=True)
    root=Path(__file__).resolve().parent
    def run(arm,route,stars,terminal,data_checks=None,gauss_frame="round_trip",graph_choice=None,conditional_checks="legacy",root_recovery="reject"):
        entry="simulate_single_block_cz_cat_depolarizing.py" if route=="cat" else "simulate_single_block_cz_depolarizing.py"
        command=[sys.executable,str(root/entry),"--profile","recovery","--verification-extraction","flags",
                 "--flag-recovery","data","--graph-stars",stars,"--terminal-policy",terminal,
                 "--data-checks",data_checks or args.data_checks,
                 "--gauss-frame",gauss_frame,"--graph",graph_choice or args.graph,
                 "--conditional-checks",conditional_checks,"--root-recovery",root_recovery,
                 "--output-dir",str((args.output_dir/arm).resolve())]
        if route=="direct_flags":command += ["--route","direct_cat"]
        for name in ("shots","seed","source_extraction","history_policy","max_flag_recoveries",
                     "two_qubit_infidelity","readout_flip_probability","one_qubit_infidelity","t_infidelity",
                     "idle_infidelity","preparation_flip_probability","attempt_timeout","max_terms","max_factors","max_operations"):
            value=getattr(args,name)
            if value is not None:command += ["--"+name.replace("_","-"),str(value)]
        write_json(args.output_dir/(arm+"-command.json"),command)
        with (args.output_dir/(arm+".log")).open("x") as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        summary=json.loads((args.output_dir/arm/"summary.json").read_text())
        return f"{arm}: {summary['accepted']}/{summary['attempts']} accepted; {summary['unresolved']} unresolved"
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(run,*arm) for arm in arms]):print(future.result(),flush=True)
    analyze(args.output_dir,arms,title)
    print((args.output_dir/"comparison.md").resolve())


if __name__=="__main__":main()
