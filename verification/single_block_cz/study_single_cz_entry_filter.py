"""Price immediate rejection on negative entry in the bare-inner tree."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_bare_inner import BareInnerPilot
from study_single_cz_vote_budget import noisy
from check_single_cz_short_gauss_witnesses import shot, report
from run_single_block_cz_controller import Reject


class EntryFilterPilot(BareInnerPilot):
    def context(self, name):
        if name == "vertex_frame":
            entry = self.record[-1]
            assert entry["entry_vote"]
            if entry["passes"] == 0:
                raise Reject("negative_entry")
        super().context(name)


def trial(seed):
    with patch.object(noisy, "controller", lambda backend, *_: EntryFilterPilot(backend, **noisy.OPTIONS)):
        return noisy.trial((None, seed, seed, noisy.RATES, False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=92000)
    parser.add_argument("--shots", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    flip = [report("vertex_readout", "a0")]
    w = {cls.__name__: shot(2, flip, cls) for cls in (BareInnerPilot, EntryFilterPilot)}
    assert w["BareInnerPilot"]["accepted"] and w["EntryFilterPilot"]["reason"] == "negative_entry"
    (args.folder / "witness.json").write_text(json.dumps(w, indent=2) + "\n")
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(row) + "\n")
            out.flush()
