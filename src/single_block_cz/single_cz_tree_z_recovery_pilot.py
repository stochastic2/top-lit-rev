"""Stay gauged on the ordinary nonzero data-Z recovery path."""

from run_single_block_cz_controller import Reject
from single_cz_controller import DataCheckFlag
from single_cz_direct_outer_pilot import DirectPilot
from single_cz_recovery import data_table
from single_cz_tree_resource_pilot import TreeResourcePilot


class TreeZRecoveryPilot(TreeResourcePilot):
    def __init__(self, backend, **options):
        super().__init__(backend, **options)
        self.inner_parity_after_recovery = 0

    def check(self, name, ports):
        bit = super().check(name, ports)
        if name.endswith("/root_Gauss"):
            frame = self.inner_parity_after_recovery
            self.inner_parity_after_recovery = 0
            if frame:
                self.record.append({"root_parity_frame_after_Z_recovery": frame, "raw_root_report": bit})
            return bit ^ frame
        return bit

    def direct_recover(self, prefix, flag=None):
        if flag is not None:
            return super().direct_recover(prefix, flag)
        # The preceding raw nonzero data-Z report spends a fault. Fresh Z
        # checks commute with V and do not disturb any pending X syndromes.
        assert prefix.endswith("/syndrome_recovery")
        records = []
        self._flag_fallback = True
        try:
            for r in range(4):
                row = [self.bare_check(f"{prefix}/Z_history/{r}", "Z", j) for j in range(9)]
                records.append(row)
                if len(records) >= 2 and row == records[-2]:
                    break
            else:
                raise Reject("unstable_gauged_Z_reference")
        finally:
            self._flag_fallback = False
        syndrome = sum(bit << j for j, bit in enumerate(row))
        correction = data_table().get(syndrome, {}).get("correction")
        self.record.append({"gauged_Z_reference": prefix, "records": records, "x_correction": correction})
        if correction is None:
            return super().direct_recover(prefix + "/ambiguous_Z/syndrome_recovery")
        x, z = correction
        assert z == 0
        self.direct_recoveries += 1
        self.context(prefix + "/gauged_X_correction")
        DirectPilot.gauged_pauli(self, x, 0)
        try:
            inner = [self.bare_check(prefix + "/inner_after_X_correction", "X", j) for j in range(5)]
        except DataCheckFlag as new_flag:
            return super().direct_recover(prefix + "/inner_flag", new_flag)
        self.inner_parity_after_recovery = sum(inner) % 2
        self.successful_direct_recoveries += 1
        self.data_epoch += 1
