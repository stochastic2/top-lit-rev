"""Transfer the screened source, bare inner meters and tree hook scan to compact13."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tree4_cat_fairness"))
from candidates import BareInnerTree, LeanResourceCat, settings
from holdout import run_arm
from trace_audit import trace, noisy
from run_single_cz_compact_block_z_pilot import CompactBlockZPilot
from single_cz_tree_resource_pilot import tree_resource_program


class BareCompact(BareInnerTree, CompactBlockZPilot):
    """Keep compact13's full graph preparation and recovery."""


class HookCompact(BareCompact):
    """Prepare all 13 edges, checking the tree hook immediately after the four tree edges."""
    def graph(self):
        graph = self.graph_choice
        assert graph.name == "compact13" and graph.tree == (0, 1, 2, 3)
        raw, scan = tree_resource_program(graph.edges[:4])
        roles = [targets[0] for op, targets in raw if op == "PREP"]
        while True:
            self.context("graph/tree_raw")
            for op, targets in raw:
                if op == "PREP":
                    self.prep(*targets)
                else:
                    self.gate(op, *targets)
            self.b.boundary()
            bit = self.direct_meter("graph/tree_hook_check", scan)
            self.b.boundary()
            if not bit:
                break
            self.dispose(roles)
            self.retry("known_unused_tree_hook_check")
        self.context("graph/chords")
        for e, (u, v) in enumerate(graph.edges[4:], 4):
            edge = f"A{e}"
            self.prep(edge)
            self.gate("CX", f"a{u}", edge)
            self.gate("CX", f"a{v}", edge)


def shot(cls, seed, rates):
    row = run_arm(cls, seed, rates)
    keep = ["seed", "status", "accepted", "reason", "metrics", "diagnostics"]
    if row.get("accepted") and not row["diagnostics"]["decoded_target_within_tolerance"]:
        keep += ["record", "noise_events"]
    return {key:row[key] for key in keep if key in row}


def trial(seed):
    return shot(HookCompact, seed, noisy.RATES)


def control_trial(seed):
    return shot(BareCompact, seed, noisy.RATES)


if __name__ == "__main__":
    for cls in (BareCompact, HookCompact, LeanResourceCat):
        t,_ = trace(cls, settings(cls))
        assert t["accepted"]
        print(cls.__name__, t["counts"], t["peak_live"], flush=True)
    clean = shot(HookCompact, 2, dict.fromkeys(noisy.RATES, "0"))
    assert clean["accepted"] and clean["diagnostics"]["decoded_target_within_tolerance"]
    control = sys.argv[1:] == ["--full-scans"]
    ledger = "full_scan_shots.jsonl" if control else "shots.jsonl"
    with (HERE / ledger).open("x") as out, ProcessPoolExecutor(4 if control else 6) as pool:
        for row in pool.map(control_trial if control else trial, range(2610000, 2610500)):
            out.write(json.dumps(row) + "\n")
            out.flush()
