"""Apply the identical twelve-check source to compact13 and count cycle-assisted rescues."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_screened_source import ScreenTree, noisy
from run_single_cz_compact_block_z_pilot import CompactBlockZPilot
import single_cz_direct_outer_pilot as direct


class ScreenCompact(ScreenTree, CompactBlockZPilot):
    pass


def trial(seed):
    decisions = []
    joint = direct.joint_decision

    def lookup(graph, record):
        decision = joint(graph, record)
        decisions.append({"record":record, "correction":decision.get("correction")})
        return decision

    with patch.object(direct,"joint_decision",lookup), patch.object(
        noisy,"controller",lambda b,*_: ScreenCompact(b, **noisy.OPTIONS)
    ):
        row = noisy.trial((None, seed, seed, noisy.RATES, False))
    return row | {"joint_lookups":decisions}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=96000)
    parser.add_argument("--shots", type=int, default=240)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(row) + "\n")
            out.flush()
