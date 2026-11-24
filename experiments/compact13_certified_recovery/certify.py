"""Keep the complete compact13 recovery, vetoing only a cycle-only choice of data class."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "compact13_cat_comparison"))
from compare import HookCompact, settings, noisy, run_arm, trace
from run_single_block_cz_controller import Reject
from single_cz_recovery import data_table
from single_cz_joint_recovery import decision


class CertifiedCompact(HookCompact):
    def direct_reference(self, prefix, flagged):
        row = super().direct_reference(prefix, flagged)
        if not flagged:
            syndrome = sum(bit << j for j, bit in enumerate(row[:18]))
            if data_table().get(syndrome, {}).get("correction") is None:
                stop = 18 + len(self.graph_choice.cycles)
                narrowed = decision(self.graph_choice, row[:stop])["correction"]
                self.record.append({"cycle_only_lookup": True, "proposed": narrowed})
                if narrowed is not None:
                    raise Reject("uncertified_cycle_only_data_correction")
        return row


def trial(seed):
    row = run_arm(CertifiedCompact, seed, noisy.RATES)
    kept = {k:row[k] for k in ("seed","accepted","status","reason","diagnostics","metrics") if k in row}
    kept["cycle_only"] = [r for r in row["record"] if "cycle_only_lookup" in r]
    kept["full_references"] = [r["direct_reference"] for r in row["record"] if "direct_reference" in r]
    return kept


if __name__ == "__main__":
    original,_ = trace(HookCompact, settings(HookCompact))
    updated,_ = trace(CertifiedCompact, settings(CertifiedCompact))
    assert updated["gates"] == original["gates"] and updated["accepted"]
    with (HERE/"shots.jsonl").open("x") as ledger, ProcessPoolExecutor(8) as pool:
        for row in pool.map(trial,range(2610000,2610500)):
            ledger.write(json.dumps(row)+"\n")
            ledger.flush()
