"""Run the screened source with the certified tree repair and matched controls."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean

from controller import ROOT, RepairedTree, ScreenTree, noisy
from study_single_cz_screened_source import ScreenCat, cat
from check_single_cz_gauged_flag_composition import shot

ARMS = (RepairedTree, ScreenTree, ScreenCat)
HERE = Path(__file__).resolve().parent


def options(cls):
    return cat.MATCHED | cat.DIRECT if cls is ScreenCat else noisy.OPTIONS


def trial(seed):
    rows = {}
    for cls in ARMS:
        b = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed), model=noisy.NoiseModel(**noisy.RATES))
        try:
            result = cls(b, **options(cls)).run()
            row = dict(seed=seed, accepted=result["accepted"], reason=result.get("reason"), status="completed")
            if row["accepted"]:
                row["diagnostics"] = noisy.diagnose(*b.state.sparse_output(b.data_labels))
                if not row["diagnostics"]["decoded_target_within_tolerance"]:
                    row.update(record=result["record"], faults=b.noise_events)
        except (MemoryError, ArithmeticError) as exc:
            row = dict(seed=seed, status="unresolved", detail=str(exc))
        row["metrics"] = b.metrics()
        rows[cls.__name__] = row
    a,b = rows["RepairedTree"],rows["ScreenTree"]
    if a["status"] == b["status"] == "completed" and a["reason"] != "gauged_flag_frame_collision":
        assert (a["accepted"], a.get("diagnostics"), a["metrics"]["gate_counts"]) == (
            b["accepted"], b.get("diagnostics"), b["metrics"]["gate_counts"])
    return rows


def summarize(rows):
    completed = [r for r in rows if r["status"] == "completed"]
    accepted = [r for r in completed if r["accepted"]]
    bad = [r for r in accepted if not r["diagnostics"]["decoded_target_within_tolerance"]]
    matches = len(accepted) - len(bad)
    gates = Counter()
    for r in completed:
        gates.update(r["metrics"]["gate_counts"])
    return dict(attempts=len(rows), accepted=len(accepted), rejected=len(completed)-len(accepted),
                unresolved=len(rows)-len(completed), decoded_matches=matches,
                acceptance=len(accepted)/len(rows), matches_per_attempt=matches/len(rows),
                accepted_mean_raw=mean(r["diagnostics"]["raw_physical_target_fidelity"] for r in accepted) if accepted else None,
                accepted_mean_decoded=mean(r["diagnostics"]["decoded_target_fidelity"] for r in accepted) if accepted else None,
                mismatch_seeds=[r["seed"] for r in bad],
                mismatch_fault_counts=[r["metrics"]["sampled_noise_events"] for r in bad],
                veto_seeds=[r["seed"] for r in completed if r["reason"]=="gauged_flag_frame_collision"],
                cx_per_match=gates["CX"]/matches if matches else None,
                t_per_match=(gates["T"]+gates["TDG"])/matches if matches else None,
                peak_live=max((r["metrics"]["peak_live_qubits"] for r in completed),default=None))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=180000)
    p.add_argument("--shots", type=int, default=500)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    if min(args.shots,args.workers)<1:
        p.error("shots and workers must be positive")
    # Verify the exact implementation covered by the composition certificate.
    cert=json.loads((HERE/"composition.json").read_text())
    for filename,digest in cert["source_sha256"].items():
        assert sha256((ROOT/filename).read_bytes()).hexdigest()==digest, filename
    witness=shot(RepairedTree,(0,1))
    assert witness["reason"]=="gauged_flag_frame_collision"
    args.output.mkdir(parents=True,exist_ok=False)
    manifest=dict(seed=args.seed,shots=args.shots,noise=noisy.RATES,
                  options={cls.__name__:options(cls) for cls in ARMS},witness_result=witness["reason"],
                  certificate_sha256=sha256((HERE/"composition.json").read_bytes()).hexdigest(),
                  runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    groups=[]
    with ProcessPoolExecutor(args.workers) as pool, (args.output/"shots.jsonl").open("x") as stream:
        for group in pool.map(trial,range(args.seed,args.seed+args.shots)):
            groups.append(group)
            stream.write(json.dumps(group)+"\n")
            stream.flush()
    summary={cls.__name__:summarize([g[cls.__name__] for g in groups]) for cls in ARMS}
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
