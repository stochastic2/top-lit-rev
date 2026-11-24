"""Inject representative two-location raw-encoder hooks hidden from the twelve-check screen."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json
from pathlib import Path

from check_single_cz_fast_source import code, envelope, syndrome, CHECKS
from check_optimized_extraction import propagate
from study_single_cz_screened_source import ScreenTree, SELECTED, noisy


def cases():
    _, cx = code.rref_encoder()
    one, two = envelope()
    found = {}
    for i, (c,t) in enumerate(cx):
        for a,b in product(range(4),repeat=2):
            x = (a & 1) << c | (b & 1) << t
            z = (a >> 1) << c | (b >> 1) << t
            x,z,_ = propagate(x,z,[("CX",g) for g in cx],i+1)
            s = syndrome(x,z)
            visible = [j for j in SELECTED if (s >> j) & 1]
            if s in one or len(visible) != 1:
                continue
            assert s in two
            axis,j,_ = CHECKS[visible[0]]
            inject = [{"context":"source/raw", "operation":"CX", "targets":[f"D{c}",f"D{t}"],
                       "paulis":{f"D{c}":"IXZY"[a], f"D{t}":"IXZY"[b]}, "occurrence":cx[:i].count((c,t))},
                      {"context":f"source/certify/screen/{axis}/{j}", "operation":"MZ","targets":["s"],
                       "timing":"report","flip_report":True}]
            found.setdefault(s, inject)
    return found


def trial(item):
    seed,s,inject = item
    b = noisy.QuantumBackend(seed=seed, model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES,"0")), injections=inject)
    pilot = ScreenTree(b, **noisy.OPTIONS)
    run = pilot.run()
    assert len(b.injected_events) == 2 and any(r.get("encoder_screen_pass") for r in run["record"])
    row = {"seed":seed,"syndrome":s,"accepted":run["accepted"],"reason":run.get("reason")}
    if run["accepted"]:
        d = noisy.diagnose(*b.state.sparse_output(b.data_labels))
        row.update(fidelity=d["decoded_target_fidelity"],match=d["decoded_target_within_tolerance"])
        if not row["match"]:
            row["record"] = run["record"]
    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    found = cases()
    with ProcessPoolExecutor(args.workers) as pool:
        results = list(pool.map(trial, ((seed,s,inject) for s,inject in found.items() for seed in (0,2))))
    args.output.write_text(json.dumps({"representatives":found, "outcomes":results}, indent=2) + "\n")
