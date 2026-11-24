"""Finite audit of five-round adaptive clean-reference certificates.

All equality patterns of whole records, and every compatible placement of
up to two bad rounds, are included. No quantum trajectory is simulated.
"""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from c4_helix_reduced_decoders import AdaptiveRecord


def equality_patterns(n, prefix=()):
    if not n:
        yield prefix
    else:
        for value in range(max(prefix, default=-1)+2):
            yield from equality_patterns(n-1, prefix+(value,))


def audit():
    rows = []
    placements = 0
    for pattern in equality_patterns(5):
        history = AdaptiveRecord(3, "audit")
        for value in pattern:
            if history.add(tuple((value >> j) & 1 for j in range(3))) is not None:
                break
        if history.common is None:
            raise ArithmeticError("No five-round certificate")
        checked = 0
        for bad in product((False, True), repeat=len(history.records)):
            if sum(bad) > 2 or any(history.records[i] != history.records[i+1] and not (bad[i] or bad[i+1])
                                   for i in range(len(history.records)-1)):
                continue
            if not any(report == history.common and not bad[i] for i, report in enumerate(history.records)):
                raise ArithmeticError("Selected vector has no clean occurrence")
            checked += 1
        if not checked:
            raise ArithmeticError("Certificate used an impossible premise")
        placements += checked
        rows.append({"five_round_equality_pattern": pattern, "rounds_used": len(history.records),
                     "certificate": history.certificate, "compatible_placements_checked": checked})
    return {"verified": True, "fault_budget": 2, "whole_record_equality_patterns": len(rows),
            "compatible_bad_round_placements_checked": placements,
            "stopping_rounds": dict(Counter(str(r["rounds_used"]) for r in rows)),
            "scope": "Report-only reference lemma; not a full circuit fault-pair enumeration", "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))


if __name__ == "__main__":
    main()
