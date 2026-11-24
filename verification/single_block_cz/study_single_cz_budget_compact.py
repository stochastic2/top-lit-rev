"""Measure joint lookup use with the budgeted compact13 block-flag arm."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from run_single_cz_compact_block_z_pilot import CompactBlockZPilot
import single_cz_direct_outer_pilot as direct
from study_single_cz_vote_budget import BudgetPilot, noisy


class CompactBudgetPilot(BudgetPilot, CompactBlockZPilot):
    """Compact resource preparation and budgeted block-flag votes."""


def trial(seed):
    decisions = []
    joint = direct.joint_decision

    def traced(graph, record):
        row = joint(graph, record)
        decisions.append({"record": record, "correction": row.get("correction")})
        return row

    with patch.object(direct, "joint_decision", traced), patch.object(
        noisy, "controller", lambda backend, *_: CompactBudgetPilot(backend, **noisy.OPTIONS)
    ):
        row = noisy.trial((None, seed, seed, noisy.RATES, False))
    return row | {"ambiguous_data_joint_lookups": decisions}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--shots", type=int, default=64)
    parser.add_argument("--seed", type=int, default=81000)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    with args.output.open("x") as stream, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(trial, range(args.seed, args.seed + args.shots)):
            stream.write(json.dumps(row) + "\n")
            stream.flush()
