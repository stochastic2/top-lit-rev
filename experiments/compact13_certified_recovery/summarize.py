"""Check equality of every physical gate count, noise count and decoded result."""
from collections import Counter
import json
from pathlib import Path
from statistics import fmean

HERE = Path(__file__).resolve().parent
def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]

old = read(HERE.parent/"compact13_cat_comparison/shots.jsonl")
new = read(HERE/"shots.jsonl")
assert len(old) == len(new) == 500
changes = []
for seed,(a,b) in enumerate(zip(old,new),2610000):
    assert seed == a["seed"] == b["seed"] and a["status"] == b["status"] == "completed"
    if any(a.get(k)!=b.get(k) for k in ("accepted","reason","diagnostics")) or any(
            a["metrics"][k]!=b["metrics"][k] for k in ("gate_counts","noise_event_counts","peak_live_qubits")):
        changes.append(seed)
gates=Counter()
for row in new:
    gates.update(row["metrics"]["gate_counts"])
accepted=[r["diagnostics"] for r in new if r["accepted"]]
matches=sum(d["decoded_target_within_tolerance"] for d in accepted)
lookup=[r["seed"] for r in new if r["cycle_only"]]
out=dict(attempts=len(new),accepted=len(accepted),matches=matches,mean_decoded_fidelity=fmean(d["decoded_target_fidelity"] for d in accepted),
         cx=gates["CX"],t_and_tdg=gates["T"]+gates["TDG"],cx_per_match=gates["CX"]/matches,
         t_per_match=(gates["T"]+gates["TDG"])/matches,peak_live=max(r["metrics"]["peak_live_qubits"] for r in new),
         full_reference_seeds=[r["seed"] for r in new if r["full_references"]],cycle_only_lookup_seeds=lookup,
         new_veto_count=sum(r["reason"]=="uncertified_cycle_only_data_correction" for r in new),changed_seeds=changes)
(HERE/"summary.json").write_text(json.dumps(out,indent=2)+"\n")
print(out)
