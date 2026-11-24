"""Prune the known-source scan only when fixed-location common support survives."""
import argparse
import json
from pathlib import Path

from check_single_cz_fast_source import CHECKS, audit, envelope
from check_single_cz_source_coherent import certify, support_tables
from study_single_cz_source_windows import source_meter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    tables = support_tables()
    selected = list(range(20))
    history = []
    for j in sorted(selected, key=lambda i: -len(source_meter(CHECKS[i][0], CHECKS[i][2]))):
        trial = [i for i in selected if i != j]
        outcome = certify(trial, *tables)
        passed = outcome["all_have_common_support"]
        history.append({"try_remove":j, "passed":passed})
        if passed:
            selected = trial
    common = certify(selected, *tables)
    independent = audit(selected, *envelope())
    assert common["all_have_common_support"] and not independent["bad_one"] and not independent["bad_two"]
    args.output.write_text(json.dumps({"selected":selected, "eliminations":history, "common_support":common,
                                      "forward_propagation":independent}, indent=2) + "\n")


if __name__ == "__main__":
    main()
