"""Verify ideal known-source signs and compare both audited sources to actual gate traces."""
import argparse
import json
from pathlib import Path

from study_single_cz_screened_source import SELECTED, ScreenTree, ScreenCat
from study_single_cz_fast_source import FastTree, FastCat
from check_single_cz_fast_source import program, GENS, code
from study_single_cz_source_windows import cat, noisy
from single_cz_hybrid_faults import row_basis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    pivots, gates = code.rref_encoder()
    assert len(row_basis((x << 20) | z for x,z in GENS)) == 20
    for x,z in GENS:
        # Each generator is pure X or pure Z, so CNOT conjugations carry no sign.
        assert not (x and z)
        for c,t in reversed(gates):
            x ^= ((x >> c) & 1) << t
            z ^= ((z >> t) & 1) << c
        assert x & ~code.mask(pivots) == 0 and z & code.mask(pivots) == 0
    matches = {}
    for cls, selected in ((FastTree,range(20)),(FastCat,range(20)),(ScreenTree, SELECTED),(ScreenCat,SELECTED)):
        rec = noisy.RecordBackend()
        opts = (cat.MATCHED | cat.DIRECT) if issubclass(cls,cat.FiveParityCat) else noisy.OPTIONS
        cls(rec, **opts).source()
        actual = [(op,tuple(20 if q=="s" else 21 if q=="f0" else int(q[1:]) for q in qs)) for op,qs in rec.ops]
        assert actual == program(selected)
        matches[cls.__name__] = len(actual)
    args.output.write_text(json.dumps({"independent_positive_source_generators":20,
                                      "exact_operation_trace_lengths": matches}, indent=2) + "\n")


if __name__ == "__main__":
    main()
