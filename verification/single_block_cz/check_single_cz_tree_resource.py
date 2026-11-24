"""Exact raw graph-hook certificate and tree-bit handoff convention."""

from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src/single_block_cz"), str(ROOT / "verification/shared")]

from check_optimized_extraction import propagate, signatures
from single_cz_persistent import TREE4
from single_cz_recovery import COMPACT13
from single_cz_tree_handoff_pilot import TreeBitHandoffGraph
from single_cz_tree_resource_pilot import tree_resource_program


def defect(x):
    return sum((((x >> (5 + e)) ^ (x >> (e + 1)) ^ x) & 1) << e for e in range(4))


def blocks(syndrome):
    weight = syndrome.bit_count()
    return min(weight, 5 - weight)  # complement the five-vertex label modulo U


def resource_certificate():
    raw, scan = tree_resource_program(TREE4.edges)
    labels = [f"a{j}" for j in range(5)] + [f"A{j}" for j in range(4)] + ["s"]
    ops = [(op, tuple(labels.index(q) for q in qs)) for op, qs in raw + [("BOUNDARY", ())] + scan + [("BOUNDARY", ())]]
    signatures_all, locations = signatures(ops, (), (1 << 9) - 1, 1)
    summaries = Counter()
    for x, _, flags in signatures_all:
        summaries[f"flag_{flags}_cost_{blocks(defect(x))}"] += 1
        if not flags:
            assert blocks(defect(x)) <= 1, (x, flags)
    pairs = 0
    for (x, _, a), (y, _, b) in combinations_with_replacement(signatures_all, 2):
        if a == b:
            assert blocks(defect(x ^ y)) <= 2
            pairs += 1
    ins = ops.index(("CX", (0, 6)))
    x, _, flag = propagate(1, 0, ops, ins + 1)
    assert blocks(defect(x)) == 2 and flag == 1
    return {"locations": locations, "one_fault_signatures": len(signatures_all),
            "signature_distribution": dict(summaries), "accepted_signature_pairs": pairs,
            "detected_example": {"operation": "CX(a0,A1)", "fault": "X_a0 after CX", "defect": defect(x), "check_report": flag}}


def handoff_certificate():
    tested = 0
    for graph in (TREE4, COMPACT13):
        decoder = TreeBitHandoffGraph(graph.name, graph.edges, graph.cycles, graph.tree)
        for word in range(1 << len(graph.edges)):
            actual = sum((word >> e & 1) << v for v, e in enumerate(graph.tree, 1))
            for flip in (0, *(1 << e for e in range(len(graph.edges)))):
                mismatch = actual ^ decoder.decode(word ^ flip)["eta"]
                expected = sum((flip >> e & 1) << v for v, e in enumerate(graph.tree, 1))
                assert mismatch == expected and mismatch.bit_count() <= 1
                tested += 1
    return {"edge_word_and_report_flip_cases": tested, "conditional_byproduct": "one U_v per wrong tree report; chord reports inert"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"resource": resource_certificate(), "handoff": handoff_certificate(),
              "sources": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in
                          map(Path, (__file__, tree_resource_program.__code__.co_filename,
                                     TreeBitHandoffGraph.decode.__code__.co_filename,
                                     signatures.__code__.co_filename))}}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
