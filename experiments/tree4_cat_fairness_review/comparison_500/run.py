"""Run the four unfiltered pilot arms on a disjoint, fixed set of 500 seeds."""
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parent))
from pilot import trial
from block_cat_probe import noisy

SEEDS = range(2610000, 2610500)

if __name__ == "__main__":
    with (OUT / "shots.jsonl").open("x") as ledger, ProcessPoolExecutor(8) as pool:
        print("Noise rates", noisy.RATES, flush=True)
        for index, group in enumerate(pool.map(trial, SEEDS), 1):
            ledger.write(json.dumps(group) + "\n")
            ledger.flush()
            if index % 100 == 0:
                print(index, "seed groups complete", flush=True)
