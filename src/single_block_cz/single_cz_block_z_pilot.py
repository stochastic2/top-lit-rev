"""Protect Z-vote extraction for inner-block support with one flag."""

import c4_helix_single_block_cz as m
from run_single_block_cz_controller import Reject
from single_cz_direct_outer_pilot import DressedFlag
from single_cz_tree_z_recovery_pilot import TreeZRecoveryPilot


def block_z_program(support):
    """Eight data sites in four consecutive inner-block pairs."""
    assert len(support) == 8
    assert all(support[j] // 4 == support[j + 1] // 4 for j in range(0, 8, 2))
    assert len({q // 4 for q in support}) == 4
    ops = [("PREP", ("s",))]
    for j, q in enumerate(support, 1):
        ops.append(("CX", (f"D{q}", "s")))
        if j == 2:
            ops.extend([("PREP", ("f0",)), ("H", ("f0",)), ("CX", ("f0", "s"))])
        elif j == 6:
            ops.extend([("CX", ("f0", "s")), ("H", ("f0",)), ("MZ", ("f0",))])
    return ops + [("MZ", ("s",))]


class BlockZPilot(TreeZRecoveryPilot):
    def prep(self, q):
        super().prep(q)
        if q == "s" and self.b.context.endswith("/block_Z") and hasattr(self.b, "absorb_parity_helper"):
            self.b.absorb_parity_helper(q)

    def bare_check(self, prefix, axis, check):
        if axis == "Z" and check >= 5 and not self._flag_fallback and prefix.startswith("direct/vote/"):
            try:
                return self.direct_meter(f"{prefix}/Z/{check}/block_Z", block_z_program(m.SUPPORTS[check]))
            except DressedFlag as flag:
                raise Reject("one_flag_outer_Z") from flag
        return super().bare_check(prefix, axis, check)
