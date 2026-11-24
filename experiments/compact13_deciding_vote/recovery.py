"""Restore terminal recovery when the recorded branch still certifies the sign."""
from concurrent.futures import ProcessPoolExecutor
import json
from run import DeferredCompact, HERE, noisy, shot, Reject
from single_cz_controller import SimulationController


class RecoveringCompact(DeferredCompact):
    def terminal_screen(self):
        SimulationController.terminal_screen(self)
        if self.terminal_screen_outcome == "syndrome_certified":
            selected = next(r for r in reversed(self.record)
                            if r.get("data_recovery") == "terminal_screen_recovery")
            x,z = selected["correction"]
            if x or z.bit_count() % 2:
                raise Reject("deferred_unverified_recovered_sign")


def trial(seed):
    return shot(RecoveringCompact, seed, noisy.RATES)


if __name__ == "__main__":
    with (HERE/"recovery_shots.jsonl").open("x") as out, ProcessPoolExecutor(8) as pool:
        for row in pool.map(trial, range(2610000,2610500)):
            out.write(json.dumps(row)+"\n")
            out.flush()
