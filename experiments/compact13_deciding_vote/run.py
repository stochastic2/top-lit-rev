"""Compact13 with the deciding data check deferred to the post-handoff screen."""
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "compact13_cat_comparison"))
from compare import HookCompact, LeanResourceCat, noisy, settings, shot, trace
from run_single_block_cz_controller import Reject
from single_cz_controller import DataCheckFlag
from single_cz_direct_outer_pilot import DressedFlag


class DeferredCompact(HookCompact):
    def direct_reference(self, prefix, flagged):
        # The tree-only certificate does not cover a cycle-conditioned lookup.
        raise Reject("deferred_ambiguous_or_flagged_gauged_reference")

    def before_two_positives(self, name):
        try:
            z = [self.bare_check(name, "Z", j) for j in range(9)]
            if any(z):
                self.direct_recover(name + "/syndrome_recovery")
                return 0  # the root meter consumes the pending recovery frame
            reports = self.direct_code_record(name, z, short=True)
            return sum(reports[9:]) % 2
        except (DataCheckFlag, DressedFlag):
            raise Reject("deferred_ordinary_meter_flag")

    def gauging(self):
        self.graph()
        graph = self.graph_choice
        self.context("enrichment")
        for q in range(20):
            self.cw(f"a{q // 4}", q)
        self.context("vertex_readout")
        bits = []
        for v in range(5):
            self.gate("H", f"a{v}")
            bits.append(self.mz(f"a{v}"))
        passed = int(sum(bits) % 2 == 0)
        self.record.append(dict(vertex_reports=bits, entry_vote=True, passes=passed))
        self.context("vertex_frame")
        for bit, edge in zip(bits[1:], graph.tree):
            if bit:
                self.gate("Z", f"A{edge}")
        self.b.boundary()

        for r in range(4):
            self.check_budget(4-r)
            name = f"direct/vote/{r}"
            deferred = passed == 2
            frame = 0 if deferred else self.before_two_positives(name)
            stars = self.direct_stars(name)
            ports = [("W", f"D{q}") for q in range(4)]
            ports += [("X", f"A{e}") for e, ends in enumerate(graph.edges) if 0 in ends]
            root = self.check(name + "/root_Gauss", ports)
            passed += (sum(stars) + root + frame) % 2 == 0
            self.record.append(dict(direct_vote=r, root=root, nonroot=stars, passes=passed,
                                    data_check_deferred=deferred, inner_x_parity_frame=frame))
            self.b.boundary()
            if passed == 3:
                break
        if passed != 3:
            raise Reject("insufficient_direct_votes")

        self.flatten_final_cycles()
        self.context("edge_readout")
        word = sum(self.mz(f"A{e}") << e for e in range(len(graph.edges)))
        decoded = graph.decode(word, graph.radius)
        self.record.append(dict(edge_reports=word, decoded=decoded))
        self.context("byproduct")
        for v in range(1, 5):
            if decoded["eta"] >> v & 1:
                self.apply_block_w(v)
        self.b.boundary()

    def terminal_screen(self):
        outcome, _ = self.terminal_screen_sweep(0)
        self.terminal_screen_outcome = outcome
        if outcome != "zero_accept":
            raise Reject("deferred_terminal_" + outcome)


def trial(seed):
    return {cls.__name__: shot(cls,seed,noisy.RATES) for cls in (DeferredCompact,LeanResourceCat)}


if __name__ == "__main__":
    for cls in (DeferredCompact,LeanResourceCat):
        clean,_ = trace(cls,settings(cls))
        assert clean["accepted"]
        print(cls.__name__, clean["counts"], clean["peak_live"], flush=True)
    with (HERE/"shots.jsonl").open("x") as out, ProcessPoolExecutor(8) as pool:
        for rows in pool.map(trial,range(2610000,2610500)):
            out.write(json.dumps(rows)+"\n")
            out.flush()
