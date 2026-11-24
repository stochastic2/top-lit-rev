"""Graph-Z frames, genuine GHZ20, or conditional joint graph/data recovery.

Adds the explicit module paths needed by the reorganized flat-import code.
Saved source snapshots/results are never modified or overwritten.
"""
from pathlib import Path
import argparse,json,os,subprocess,sys
from concurrent.futures import ThreadPoolExecutor,as_completed

ROOT=Path(__file__).resolve().parents[2]
MODULES=[ROOT/p for p in ("src/single_block_cz","src/shared","src/two_block_swap",
                        "verification/single_block_cz","verification/shared","verification/two_block_swap")]
sys.path[:0]=[str(p) for p in MODULES]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shots",type=int,default=200)
    p.add_argument("--seed",type=int,default=1000)
    p.add_argument("--workers",type=int,choices=(1,2),default=2)
    p.add_argument("--graph",choices=("compact13","current20","tree4"),default="compact13")
    p.add_argument("--comparison",choices=("frames","cat","joint-data"),default="frames",
                   help="frames: physical vs virtual Z; cat: persistent virtual Z vs GHZ20; joint-data: round-trip joint off/fallback vs GHZ20")
    p.add_argument("--max-flag-recoveries",type=int,default=8)
    p.add_argument("--output-dir",type=Path,required=True)
    for name,default in (("two-qubit-infidelity","1e-3"),("readout-flip-probability","1e-3"),
                         ("one-qubit-infidelity","1e-4"),("t-infidelity","1e-4"),
                         ("idle-infidelity","0"),("preparation-flip-probability","0")):
        p.add_argument("--"+name,default=default)
    a=p.parse_args()
    if a.shots<1:p.error("Positive shot count required")
    if not 1<=a.max_flag_recoveries<=32:p.error("Flag-recovery cap must be between 1 and 32")
    if a.comparison=="joint-data" and a.graph=="tree4":p.error("Joint recovery requires compact13 or current20")
    a.output_dir=a.output_dir.resolve()
    a.output_dir.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ)
    env["PYTHONPATH"]=os.pathsep.join([*(str(x) for x in MODULES),env.get("PYTHONPATH","")])
    results={}
    from verify_single_block_cz_run import verify_run
    def run(mode):
        folder=a.output_dir/mode
        cat=mode=="cat-dual"
        joint=a.comparison=="joint-data" and not cat
        entry="simulate_single_block_cz_cat_depolarizing.py" if cat else "simulate_single_block_cz_depolarizing.py"
        command=[sys.executable,str(MODULES[0]/entry),
                 "--shots",str(a.shots),"--seed",str(a.seed),
                 "--graph",a.graph,"--source-extraction","decoded_flags","--flag-recovery","data",
                 "--max-flag-recoveries",str(a.max_flag_recoveries),
                 "--data-checks","compact_flags","--gauss-frame","round_trip" if cat or joint else "persistent",
                 "--graph-stars","flags" if cat else "bare",
                 "--terminal-policy","certified" if cat else "screen" if joint else "intrinsic",
                 "--graph-z-corrections","physical" if cat or joint else mode,
                 "--conditional-checks","dual_flags" if a.comparison!="frames" else "legacy",
                 "--output-dir",str(folder)]
        if joint:
            command += ["--root-recovery","joint","--joint-recovery","fallback" if mode=="joint-fallback" else "off"]
        for key in ("two_qubit_infidelity","readout_flip_probability","one_qubit_infidelity","t_infidelity",
                    "idle_infidelity","preparation_flip_probability"):
            command += ["--"+key.replace("_","-"),getattr(a,key)]
        (a.output_dir/(mode+"-command.json")).write_text(json.dumps(command,indent=2)+"\n")
        with (a.output_dir/(mode+".log")).open("x") as log:
            subprocess.run(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        return mode,{"summary":json.loads((folder/"summary.json").read_text()),"verification":verify_run(folder)}
    modes=(("joint-off","joint-fallback","cat-dual") if a.comparison=="joint-data" else
           ("frame","cat-dual") if a.comparison=="cat" else ("physical","frame"))
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for future in as_completed([pool.submit(run,mode) for mode in modes]):
            mode,result=future.result();results[mode]=result
            print(mode,result["summary"]["accepted"],"/",a.shots,flush=True)
    (a.output_dir/"comparison.json").write_text(json.dumps(results,indent=2)+"\n")
    paired=None
    if a.comparison=="joint-data":
        def shots(mode):
            return {r['shot_index']:r for line in (a.output_dir/mode/'shots.jsonl').read_text().splitlines()
                    if line for r in [json.loads(line)]}
        old,new=shots('joint-off'),shots('joint-fallback')
        complete=[i for i in old.keys() & new.keys()
                  if old[i]['execution_status']==new[i]['execution_status']=='completed']
        gained=[i for i in complete if not old[i]['accepted'] and new[i]['accepted']]
        lost=[i for i in complete if old[i]['accepted'] and not new[i]['accepted']]
        paired=dict(completed_pairs=len(complete),gained_acceptances=gained,lost_acceptances=lost,
                    strict_acceptances_preserved=sum(old[i]['accepted'] and new[i]['accepted'] for i in complete),
                    gained_baseline_reasons={str(i):old[i].get('reason') for i in gained})
        (a.output_dir/'pairing.json').write_text(json.dumps(paired,indent=2)+'\n')
    title="Conditional joint graph/data recovery" if a.comparison=="joint-data" else "Persistent software graph-Z comparison"
    lines=["# "+title,"",
           "| Method | Accepted / attempts | Decoded target matches / assessed | Clean CX | Total CX / accepted output |",
           "|---|---:|---:|---:|---:|"]
    for mode in modes:
        s=results[mode]["summary"]
        key="direct_cat/recovery" if mode=="cat-dual" else a.graph+"/recovery"
        clean=json.loads((a.output_dir/mode/"clean-costs.json").read_text())[key]["gates"]["CX"]
        cost=(s["cost_per_accepted_completed"] or {}).get("CX")
        cost=f"{cost:,.1f}" if cost is not None else "n/a"
        lines.append(f"| {mode} | {s['accepted']} / {s['attempts']} | {s['accepted_within_target_tolerance']} / {s['accepted_assessed']} | {clean} | {cost} |")
    lines += ["","Total CX/output includes rejected attempts. No matched population fidelity or yield advantage is established by a finite sample.",
              "The cat arm uses a genuine GHZ20 resource. Cat and joint-data comparison modes use dual conditional checks in every arm.",
              "Equal seeds do not imply identical fault trajectories. See each manifest for all rates and the selected schedule."]
    if a.comparison=="joint-data":
        lines += ["","Joint fallback runs only after a protected nonzero data syndrome has an ambiguous data-only correction. Clean circuits are identical."]
        lines += [f"Completed same-seed pairs: {paired['completed_pairs']}; gained acceptances: {len(paired['gained_acceptances'])}; lost acceptances: {len(paired['lost_acceptances'])}.",
                  "See pairing.json for shot indices. Unresolved attempts are excluded from these paired counts."]
    (a.output_dir/"comparison.md").write_text("\n".join(lines)+"\n")
    print("Saved",a.output_dir/"comparison.json")
    print("Table",a.output_dir/"comparison.md")
    print("Different schedules change noise trajectories; equal seeds do not imply paired faults.")

if __name__=="__main__":main()
