"""Audit-only variations of the final diagnostic's two exact baselines."""
from trace_audit import RepairedTree, ScreenCat, noisy, options
from run_single_block_cz_controller import Reject
from single_cz_block_z_pilot import block_z_program
from single_cz_direct_outer_pilot import DressedFlag
from single_cz_recovery import data_table, m
from study_single_cz_bare_inner import inner_program


class BareInnerTree(RepairedTree):
    def check(self, name, ports):
        path = name.split("/")
        if len(path) == 5 and path[:2] == ["direct", "vote"] and path[2].isdigit() and path[3] in "ZX" and int(path[4]) < 5:
            return self.direct_meter(name, inner_program(path[3], [q for _, q in ports]))
        return super().check(name, ports)

    def prep(self, q):
        super().prep(q)
        path = self.b.context.split("/")
        if (q == "s" and len(path) == 5 and path[:2] == ["direct", "vote"] and path[2].isdigit()
                and path[3] == "Z" and int(path[4]) < 5 and hasattr(self.b, "absorb_parity_helper")):
            self.b.absorb_parity_helper(q)


class FilteredTree(BareInnerTree):
    def context(self, name):
        if name == "vertex_frame" and self.record[-1]["passes"] == 0:
            raise Reject("negative_entry")
        super().context(name)


class ShortPostCat(ScreenCat):
    """Source for entry, short rounds thereafter, ordered post-vote verification."""
    screen_before_deciding_vote = False
    reject_negative_entry = False

    def check(self, name, ports):
        if name.startswith("terminal_screen/"):
            name = "compact/" + name
        return super().check(name, ports)

    def prep(self, q):
        super().prep(q)
        fields = self.b.context.split("/")
        # Only the bare/one-flag routine meters need this regrouping here.
        # The shared compact/conditional flag path handles its own helper.
        if (q == "s" and 4 <= len(fields) <= 5 and fields[0] == "short_cat" and fields[2] == "Z"
                and hasattr(self.b, "absorb_parity_helper")):
            self.b.absorb_parity_helper(q)

    def inner(self, prefix, axis, j):
        sites = [f"D{q}" for q in m.SUPPORTS[j]]
        return self.direct_meter(f"{prefix}/{axis}/{j}", inner_program(axis, sites))

    def vote_z(self, prefix, j):
        if j < 5:
            return self.inner(prefix, "Z", j)
        try:
            return self.direct_meter(f"{prefix}/Z/{j}/block_Z", block_z_program(m.SUPPORTS[j]))
        except DressedFlag as flag:
            raise Reject("one_flag_outer_Z") from flag

    def short_sign(self, prefix):
        z = [self.vote_z(prefix, j) for j in range(9)]
        if any(z):
            if not self.recover_z(prefix + "/Z_recovery"):
                return 0  # the full-code fallback corrected the pending X frame
        inner = [self.inner(prefix, "X", j) for j in range(5)]
        return sum(inner) % 2

    def recover_z(self, prefix):
        def acquire_z(j):
            return self.family(f"{prefix}/Z_history/{j}", [
                [("Z", f"D{q}") for q in support] for support in m.SUPPORTS
            ])

        rows = []
        self._flag_fallback = True
        try:
            for j in range(4):
                rows.append(acquire_z(j))
                if len(rows) > 1 and rows[-1] == rows[-2]:
                    break
            else:
                raise Reject("unstable_cat_Z_reference")
        finally:
            self._flag_fallback = False
        s = sum(bit << j for j, bit in enumerate(rows[-1]))
        correction = data_table().get(s, {}).get("correction")
        self.record.append({"cat_Z_reference": prefix, "records": rows, "correction": correction})
        if correction is None:
            self.data_recover(prefix + "/full", None)
            return False
        x, z = correction
        assert z == 0
        self.context(prefix + "/X_correction")
        self.pauli_correction(x, 0, [f"D{q}" for q in range(20)])
        self.data_epoch += 1
        return True

    def run(self):
        try:
            self.source()
            passed = 0
            for r in range(5):
                if r == 0:
                    sign, mode = 0, "source"
                elif self.screen_before_deciding_vote and passed == 2:
                    self.terminal_screen()
                    sign, mode = 0, "pre_U_screen"
                else:
                    sign, mode = self.short_sign(f"short_cat/{r}"), "short"
                if hasattr(self.b, "compress_data"):
                    self.b.compress_data()
                bit = self.check(f"terminal/{r}/U", [("W", f"D{q}") for q in range(20)])
                positive = bit == sign
                passed += positive
                self.record.append({"passing_terminal_round": r, "passing": positive, "passes": passed,
                                    "vote_mode": mode, "raw_U": bit, "inner_x_parity_frame": sign})
                self.b.boundary()
                if r == 0 and self.reject_negative_entry and not positive:
                    raise Reject("negative_entry")
                if passed == 3:
                    break
                if passed + 4 - r < 3:
                    raise Reject("insufficient_terminal_rounds")
            assert passed == 3
            if not self.screen_before_deciding_vote:
                self.terminal_screen()
                self.b.boundary()
        except Reject as exc:
            self.context("rejected_disposal")
            self.dispose(sorted(self.live))
            return {"accepted": False, "reason": str(exc), "retries": self.retries, "record": self.record}
        assert self.live == {f"D{q}" for q in range(20)}
        return {"accepted": True, "retries": self.retries, "record": self.record,
                "output_roles": [f"D{q}" for q in range(20)]}


class ShortPreCat(ShortPostCat):
    """Use the screen as the data check for every potential deciding vote."""
    screen_before_deciding_vote = True


class LeanResourceCat(ShortPreCat):
    """Partition the ten checked leaf incidences over four parity meters."""
    fast_parities = ((0, 7, 12, 16), (1, 14), (4, 19), (10, 18))

    def cat(self, size, name):
        assert size == 20
        leaves = [f"L{q}" for q in range(size)]
        for leaf in leaves:
            self.prep(leaf)
        self.gate("H", leaves[0])
        for control, target in zip(leaves, leaves[1:]):
            self.gate("CX", control, target)

        def scan(checks):
            bits = []
            for support in checks:
                self.prep("w")
                for q in support:
                    self.gate("CX", leaves[q], "w")
                bits.append(self.mz("w"))
            return bits

        fast = scan(self.fast_parities)
        self.record.append({"cat": name, "four_parity_reports": fast})
        if any(fast):
            chain = [(q, q + 1) for q in range(size - 1)]
            rows = []
            for _ in range(4):
                rows.append(scan(chain))
                if len(rows) > 1 and rows[-1] == rows[-2]:
                    break
            else:
                raise Reject("unstable_four_parity_cat_fallback")
            self.record.append({"cat_fallback": name, "records": rows})
            bit = 0
            for q, parity in enumerate(rows[-1], 1):
                bit ^= parity
                if bit:
                    self.gate("X", leaves[q])
        return leaves


class FilteredCat(LeanResourceCat):
    reject_negative_entry = True


ARMS = (RepairedTree, ScreenCat, ShortPostCat, ShortPreCat, LeanResourceCat,
        BareInnerTree, FilteredTree, FilteredCat)


def settings(cls):
    return options(ScreenCat) if issubclass(cls, ScreenCat) else options(RepairedTree)
