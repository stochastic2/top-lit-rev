"""Tree4 with a coordinate-aware veto on exceptional inner-meter recovery."""
from functools import lru_cache
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "verification/single_block_cz"))
from study_single_cz_screened_source import ScreenTree, noisy
from single_cz_controller import DataCheckFlag
from run_single_block_cz_controller import Reject
from single_cz_flag_recovery import recovery_table, signature_groups
from single_cz_recovery import remainder, syndrome


@lru_cache(None)
def vetoes(axis, support, flags, extraction):
    old = recovery_table(axis, support, flags, extraction)
    assert len(support) == 4 and len({q // 4 for q in support}) == 1
    if support[0] < 4:
        return frozenset()
    # At most one outside fault when one flag-producing fault is in this
    # meter. Include the edge-one conjugate of its physical tail.
    bad = set()
    for x, z in signature_groups(axis, support, extraction)[flags]:
        for v in range(5):
            for a, b in product(range(16), repeat=2):
                u = x ^ (a << (4*v))
                t = z ^ x ^ (b << (4*v))
                s = syndrome(u, t)
                c = old.get(s, {}).get("correction")
                if c is not None and (remainder(c[0] ^ u) or remainder(c[1] ^ t)):
                    bad.add(s)
    return frozenset(bad)


class RepairedTree(ScreenTree):
    active_gauged_flag = None

    def bare_check(self, prefix, axis, check):
        # Both a routine flag and a nested flag after gauged X correction
        # originate here. The nested handler dispatches directly to a parent.
        try:
            return super().bare_check(prefix, axis, check)
        except DataCheckFlag as exc:
            self.active_gauged_flag = exc.record
            raise

    def direct_reference(self, prefix, flagged):
        row = super().direct_reference(prefix, flagged)
        if flagged:
            f = self.active_gauged_flag
            assert f is not None
            support = tuple(int(q[1:]) for q in f["targets"])
            flags = sum(bit << j for j, bit in enumerate(f["flags"]))
            s = sum(bit << j for j, bit in enumerate(row[:18]))
            if s in vetoes(f["axes"][0], support, flags, f["extraction"]):
                raise Reject("gauged_flag_frame_collision")
        return row
