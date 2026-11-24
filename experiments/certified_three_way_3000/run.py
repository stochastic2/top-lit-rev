"""Fixed-size paired replication of the three certified, unfiltered factories."""
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"compact13_certified_recovery"))
from certify import CertifiedCompact, run_arm, noisy, settings
from candidates import BareInnerTree, LeanResourceCat

ARMS = (CertifiedCompact, BareInnerTree, LeanResourceCat)
SEEDS = range(3100000,3103000)


def trial(seed):
    arms = {}
    for cls in ARMS:
        raw = run_arm(cls,seed,noisy.RATES)
        row = {k:raw[k] for k in ("seed","status","accepted","reason","detail","metrics","diagnostics") if k in raw}
        if raw["accepted"] and not raw["diagnostics"]["decoded_target_within_tolerance"]:
            row.update(noise_events=raw["noise_events"], record=raw["record"])
        arms[cls.__name__] = row
    return arms


if __name__ == "__main__":
    files = {Path(module.__file__).resolve() for module in list(sys.modules.values()) if getattr(module,"__file__",None)}
    hashes = {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files if p.is_relative_to(ROOT) and p.suffix==".py"}
    manifest = dict(seed_range=[SEEDS.start,SEEDS.stop-1], attempts_per_arm=len(SEEDS), rates=noisy.RATES,
        options={c.__name__:settings(c) for c in ARMS}, source_sha256=hashes,
        endpoints=["accepted decoded mean target fidelity","acceptance per attempt","total T and TDG divided by accepted target matches"],
        uncertainty="paired seed bootstrap for acceptance and T cost; exact paired permutation for conditional fidelity, Holm across three pairs")
    with (HERE/"manifest.json").open("x") as out:
        json.dump(manifest,out,indent=2)
    with (HERE/"shots.jsonl").open("x") as out, ProcessPoolExecutor(9) as pool:
        for n,group in enumerate(pool.map(trial,SEEDS),1):
            out.write(json.dumps(group)+"\n")
            out.flush()
            if n%500==0:
                print(n,"paired seeds completed",flush=True)
