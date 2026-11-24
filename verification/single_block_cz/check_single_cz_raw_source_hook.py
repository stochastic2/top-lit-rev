"""Find a single raw-encoder fault that needs the partial source screen."""
import argparse
import json
from pathlib import Path

from check_single_cz_fast_source import code, envelope, syndrome
from study_single_cz_screened_source import ScreenTree, noisy
from check_single_cz_short_gauss_witnesses import shot
from check_optimized_extraction import propagate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    one, two = envelope()
    _, cx = code.rref_encoder()
    gates = [("CX", qs) for qs in cx]
    candidates = []
    for i, (c,t) in enumerate(cx):
        for p in ("X","Z","Y"):
            for q in (c,t):
                x,z,_ = propagate((p != "Z") << q, (p != "X") << q, gates,i+1)
                s = syndrome(x,z)
                if s not in one:
                    candidates.append((s in two,i,c,t,q,p,x,z,s))
    # Prefer a hook outside the two-block envelope, then the earliest gate.
    in_two,i,c,t,q,p,x,z,s = min(candidates)
    injection = {"context":"source/raw","operation":"CX","targets":[f"D{c}",f"D{t}"],"paulis":{f"D{q}":p},
                 "occurrence":cx[:i].count((c,t))}
    trajectory = shot(2,[injection],ScreenTree)
    backend = noisy.QuantumBackend(seed=2, model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES, "0")), injections=[injection])
    pilot = ScreenTree(backend, **noisy.OPTIONS)
    pilot.source()
    triggered = [r["nonzero_source_screen"] for r in pilot.record if "nonzero_source_screen" in r]
    history = [r for r in pilot.record if r.get("history") == "known_source"]
    assert len(triggered) == len(history) == 1 and trajectory["accepted"]
    args.output.write_text(json.dumps({"raw_encoder_gate_index":i, "single_fault":injection, "raw_x":x, "raw_z":z,
                                      "source_syndrome":s, "in_one_block_envelope":False, "in_two_block_envelope":in_two,
                                      "first_nonzero_source_check":triggered[0], "full_source_reference":history[0], "screen_trajectory":trajectory}, indent=2) + "\n")


if __name__ == "__main__":
    main()
