"""Replay the saved negative-cat case and its three-certificate-fault witness.

Specific deterministic case study, not a stochastic campaign or exhaustive
fault audit. Imports the exact saved runtime snapshot before quantum modules.
"""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run",type=Path);parser.add_argument("--shot",type=int,default=27)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();run=args.run.resolve()
    manifest=json.loads((run/"manifest.json").read_text());snapshot=run/"source_snapshot"
    assert manifest["direct_cz_extraction"]=="cat"
    for name,h in manifest["source_sha256"].items():assert sha256((snapshot/name).read_bytes()).hexdigest()==h
    sys.path.insert(0,str(snapshot))
    import numpy as np
    from simulate_single_block_cz_cat_depolarizing import simulate
    from single_cz_runtime import NoiseModel
    from single_cz_diagnostics import diagnose
    saved=next(json.loads(s) for s in (run/"shots.jsonl").read_text().splitlines()
               if json.loads(s)["shot_index"]==args.shot)
    assert saved["accepted"] and saved["diagnostics"]["decoded_target_fidelity"]<1e-10
    detail=Path(saved["detail_directory"])
    noise=json.loads((detail/"noise.json").read_text())["sampled"]
    zero=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)
    def evaluate(faults):
        r,b=simulate(seed=saved["seed"],noise_seed_value=saved["noise_seed"],model=zero,
                     profile=manifest["profile"],history_policy=manifest["history_policy"],
                     source_extraction=manifest["source_extraction"],
                     verification_extraction=manifest["verification_extraction"],injections=faults)
        assert len(b.injected_events)==len(faults)
        output={"accepted":r["accepted"],"reason":r.get("reason"),"faults":len(faults)}
        if r["accepted"]:output["diagnostics"]=diagnose(*b.state.sparse_output(b.data_labels))
        return output,r,b
    full=[]
    for event in noise:
        if event["channel"]=="readout":
            f={"operation":"MZ","timing":"report","flip_report":True}
        elif event["channel"]=="two_qubit":
            f={"operation":"CX","timing":"after", "paulis":dict(zip(event["targets"],event["axes"]))}
        else:raise ValueError("This saved case study expects only CX and readout faults")
        full.append(f|{k:event[k] for k in ("event","context","targets")})
    original,r,b=evaluate(full)
    original_meters=json.loads((detail/"measurements.json").read_text())
    assert [(v["context"],v["label"],v["actual"],v["reported"]) for v in b.measurements]==[
        (v["context"],v["label"],v["actual"],v["reported"]) for v in original_meters]
    indices,values=b.state.sparse_output(b.data_labels)
    with np.load(saved["output_reference"]) as a:
        assert np.array_equal(indices,a["indices"])
        overlap=float(abs(np.vdot(values,a["amplitudes"]))**2)
        assert abs(overlap-1)<1e-10
    original["saved_state_overlap"]=overlap
    # This witness was identified from the recorded actual/reported signs.
    # Context/port matching replaces event indices when other faults are removed.
    witness=[{"context":"terminal/0/U","operation":"MZ","targets":["L13"],
              "timing":"report","flip_report":True},
             {"context":"terminal/1/U","operation":"MZ","targets":["L3"],
              "timing":"report","flip_report":True},
             {"context":"terminal/2/U","operation":"CX","targets":["L7","w"],
              "timing":"after","occurrence":0,"paulis":{"L7":"Z","w":"Z"}}]
    constructed,r,b=evaluate(witness)
    assert constructed["accepted"] and constructed["diagnostics"]["decoded_target_fidelity"]<1e-10
    assert constructed["diagnostics"]["logical_density_real"][3][3]>1-1e-10
    pairs=[]
    for keep in combinations(range(3),2):
        record,r,b=evaluate([witness[i] for i in keep])
        assert not record["accepted"] or record["diagnostics"]["decoded_target_within_tolerance"]
        pairs.append({"kept_fault_indices":keep,**record})
    result={"scope":"specific deterministic replay; not new Monte Carlo samples",
            "saved_run":str(run),"shot":args.shot,"seed":saved["seed"],
            "saved_runtime_snapshot_hashes_verified":True,"original_faults":full,
            "five_fault_replay":original,"three_fault_witness":witness,
            "three_fault_result":constructed,"two_fault_subsets":pairs,
            "global_two_fault_guarantee_violated":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"saved_replay_fidelity":original["diagnostics"]["decoded_target_fidelity"],
                      "saved_state_overlap":overlap,"three_fault_witness_accepted":constructed["accepted"],
                      "three_fault_witness_fidelity":constructed["diagnostics"]["decoded_target_fidelity"],
                      "two_fault_subset_outcomes":[{"kept":p["kept_fault_indices"],"accepted":p["accepted"],
                                                     "reason":p["reason"]} for p in pairs]},indent=2))


if __name__=="__main__":main()
