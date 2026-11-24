"""Minimum-weight obstructions to deleting original checks in the clean-vote proof."""
from itertools import combinations, product
import argparse
import json
from pathlib import Path

import check_single_cz_short_gauss_vote as vote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    supports = tuple(map(vote.m.mask, vote.m.SUPPORTS))
    witnesses = {}
    for a, b in combinations(range(5), 2):
        for left, right in product(range(16), repeat=2):
            x = (left << (4 * a)) | (right << (4 * b))
            syndrome = sum(((x & check).bit_count() % 2) << j for j, check in enumerate(supports))
            if syndrome.bit_count() != 1:
                continue
            j = syndrome.bit_length() - 1
            sites = [q for q in range(20) if x >> q & 1]
            assert x not in vote.terminal.STABILIZERS
            if j not in witnesses or (len(sites), sites) < (len(witnesses[j]), witnesses[j]):
                witnesses[j] = sites
    assert set(witnesses) == set(range(9))
    inner = {}
    for j in range(5):
        z = 1 << (4 * j)
        reports = [((z & check).bit_count() % 2) for check in supports[:5]]
        assert sum(reports) == reports[j] == 1
        inner[j] = {"Z_on_site": 4 * j, "inner_X_reports": reports}
    args.output.write_text(json.dumps({"omitted_Z_index_to_minimum_X_sites": witnesses,
                                      "omitted_inner_X_index_to_wrong_sign_example": inner,
                                      "scope": "deletion among the original reports on a two-block envelope"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
