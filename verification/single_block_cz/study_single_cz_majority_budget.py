"""Run the eight-CX majority handoff on the budgeted block-flag tree."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from check_single_cz_short_gauss_witnesses import RepeatedTreeReadout, report, shot
from study_single_cz_vote_budget import BudgetPilot, noisy


class MajorityBudgetPilot(RepeatedTreeReadout, BudgetPilot):
    """Reuse the witness readout and the block-flag budget controller."""


def trial(seed):
    with patch.object(noisy, "controller", lambda backend, *_: MajorityBudgetPilot(backend, **noisy.OPTIONS)):
        return noisy.trial((None, seed, seed, noisy.RATES, False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=81000)
    parser.add_argument("--shots", type=int, default=64)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    clean = shot(2, [], BudgetPilot)
    majority = shot(2, [], MajorityBudgetPilot)
    assert majority["accepted"] and majority["cx"] == clean["cx"] + 8
    flip = [report("edge_readout", "A1")]
    assert shot(2, flip, BudgetPilot)["reason"] == "data_ambiguity"
    assert shot(2, flip, MajorityBudgetPilot)["accepted"]
    with args.output.open("x") as stream, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(trial, range(args.seed, args.seed + args.shots)):
            stream.write(json.dumps(row) + "\n")
            stream.flush()
