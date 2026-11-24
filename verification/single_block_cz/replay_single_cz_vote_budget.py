"""Replay the prefix stop against the saved 500-shot tree4 reference."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_vote_budget import BudgetPilot, noisy


def replay(original):
    with patch.object(noisy, "controller", lambda backend, *_: BudgetPilot(backend, **noisy.OPTIONS)):
        row = noisy.trial((None, original["shot_index"], original["seed"], noisy.RATES, False))
    assert row["execution_status"] == "completed" and row["accepted"] == original["accepted"]
    if row["accepted"]:
        assert row["diagnostics"] == original["diagnostics"]
        assert row["metrics"]["gate_counts"] == original["metrics"]["gate_counts"]
    for op, n in row["metrics"]["gate_counts"].items():
        assert n <= original["metrics"]["gate_counts"].get(op, 0)
    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    with args.output.open("x") as stream, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(replay, map(json.loads, args.reference.read_text().splitlines())):
            stream.write(json.dumps(row) + "\n")
            stream.flush()
