"""Paired prefix experiment on the shortened tree4 voting controller."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import run_single_cz_direct_outer_pilot as noisy
from run_single_block_cz_controller import Reject
from single_cz_block_z_pilot import BlockZPilot


class BudgetPilot(BlockZPilot):
    def check_budget(self, slots):
        passes = next(row["passes"] for row in reversed(self.record) if "passes" in row)
        if passes + slots < 3:
            raise Reject("insufficient_direct_votes")

    def bare_check(self, prefix, axis, check):
        # First operation of an ordinary vote. Recovery prefixes have extra fields.
        fields = prefix.split("/")
        if fields[:2] == ["direct", "vote"] and len(fields) == 3 and axis == "Z" and check == 0:
            self.check_budget(4 - int(fields[2]))
        return super().bare_check(prefix, axis, check)

    def direct_recover(self, prefix, flag=None):
        # Only the OUTER flag handler abandons this vote. Nested flags during
        # syndrome recovery return to a still-eligible root measurement.
        if flag is not None and prefix.split("/")[3:] == ["flag_recovery"]:
            self.check_budget(3 - int(prefix.split("/")[2]))
        return super().direct_recover(prefix, flag)


class NoSharedVPilot(BudgetPilot):
    def direct_reference(self, prefix, flagged):
        raise Reject("exception_requires_shared_V")


def trial(seed):
    result = {}
    for cls in (BlockZPilot, BudgetPilot, NoSharedVPilot):
        with patch.object(noisy, "controller", lambda backend, *_: cls(backend, **noisy.OPTIONS)):
            row = noisy.trial((None, seed, seed, noisy.RATES, False))
        assert row["execution_status"] == "completed"
        result[cls.__name__] = row
    base, budget, simple = result.values()
    assert base["accepted"] == budget["accepted"]
    assert not simple["accepted"] or budget["accepted"]
    for left, right in ((base, budget), (budget, simple)):
        if right["accepted"]:
            assert left["diagnostics"] == right["diagnostics"]
            assert left["metrics"]["gate_counts"] == right["metrics"]["gate_counts"]
        for op, n in right["metrics"]["gate_counts"].items():
            assert n <= left["metrics"]["gate_counts"].get(op, 0)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=81000)
    parser.add_argument("--shots", type=int, default=64)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    for entry in (0, 1):
        for votes in product((0, 1, None), repeat=4):  # None denotes a flagged slot
            for r in range(5):
                passes = entry + votes[:r].count(1)
                if passes + 4 - r < 3:
                    assert entry + votes.count(1) < 3
    with args.output.open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for result in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(result) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
