"""Minimal exceptional-recovery witness and direct-copy handoff bounds."""
import argparse
from itertools import combinations
import json
from pathlib import Path

from check_single_cz_short_gauss_witnesses import report, shot
from study_single_cz_vote_budget import BudgetPilot, NoSharedVPilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    flip = report("direct/vote/0/Z/0", "f0")
    runs = {cls.__name__: {"zero": shot(2, [], cls), "one": shot(2, [flip], cls)}
            for cls in (BudgetPilot, NoSharedVPilot)}
    assert all(r["zero"]["accepted"] for r in runs.values())
    assert runs["BudgetPilot"]["one"]["accepted"] and runs["BudgetPilot"]["one"]["coordinates_CX"] > 0
    assert runs["NoSharedVPilot"]["one"]["reason"] == "exception_requires_shared_V"
    # Model: unchanged physical Z readout and ancillary XORs of the tree
    # bits. A parity incidence costs one direct edge-to-helper CX.
    words = [sum(((x >> bit) & 1) * (7 << (3 * bit)) for bit in range(4)) for x in range(16)]
    distance = min((a ^ b).bit_count() for a, b in combinations(words, 2))
    assert distance == 3
    handoff = {"scope": "one arbitrary reported-bit flip; ideal independent parity-copy operations",
               "lower_bound_CX": 8, "achieved_distance": distance,
               "one_copy_ambiguous_received_edge_pair": [0, 1],
               "explanation": "Either true bit gives this received pair with one report flip. For each of four edges, adjacent input words must differ in at least three recorded bits, including its destructive readout. Each edge must enter at least two extra checks."}
    args.output.write_text(json.dumps({"handoff": handoff, "exceptional_flag": runs}, indent=2) + "\n")


if __name__ == "__main__":
    main()
