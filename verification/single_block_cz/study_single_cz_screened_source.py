"""Test the twelve-check encoder-specific source screen on held-out seeds."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
from unittest.mock import patch

from study_single_cz_fast_source import FastTree, FastCat
from study_single_cz_shared_source import FilterWindowTree, WindowCat
from study_single_cz_source_windows import BudgetPilot, SourceWindowPilot, cat, noisy, source_meter, KnownSourceFlag, DressedFlag
from check_single_cz_source_coherent import certify, support_tables
from check_single_cz_fast_source import CHECKS, audit, envelope
from check_single_cz_short_gauss_witnesses import shot, report

SELECTED = (0,1,2,3,4,10,11,15,16,17,18,19)


class PartialSourceScan:
    def acquire(self, name, measure, initial=None):
        if name != "known_source":
            return super().acquire(name, measure, initial)
        assert initial is None
        for i in SELECTED:
            axis,j,support = CHECKS[i]
            prefix = f"source/certify/screen/{axis}/{j}"
            try:
                bit = self.direct_meter(prefix, source_meter(axis,support))
            except DressedFlag as flag:
                raise KnownSourceFlag(prefix) from flag
            if bit:
                self.record.append({"nonzero_source_screen": i})
                return super().acquire(name, measure)
        # The zero vector selects identity feedback. Omitted checks have no
        # physical readout; the certificate is specific to the raw encoder.
        self.record.append({"encoder_screen_pass": True, "source_feedback": "identity"})
        return [0] * 20


class ScreenTree(PartialSourceScan, SourceWindowPilot):
    pass


class FilterScreenTree(PartialSourceScan, FilterWindowTree):
    pass


class ScreenCat(PartialSourceScan, WindowCat):
    pass


def trial(seed):
    result = {}
    for cls in (BudgetPilot,FastTree,ScreenTree,FilterScreenTree):
        with patch.object(noisy, "controller", lambda b,*_: cls(b, **noisy.OPTIONS)):
            result[cls.__name__] = noisy.trial((None, seed, seed, noisy.RATES, False))
    for cls in (cat.FiveParityCat,ScreenCat):
        b = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed), model=noisy.NoiseModel(**noisy.RATES))
        run = cls(b, **cat.MATCHED, **cat.DIRECT).run()
        row = {"seed": seed, "execution_status": "completed", "accepted": run["accepted"],
               "reason": run.get("reason"), "metrics": b.metrics()}
        if row["accepted"]:
            row["diagnostics"] = noisy.diagnose(*b.state.sparse_output(b.data_labels))
            if not row["diagnostics"]["decoded_target_within_tolerance"]:
                row.update(noise_events=b.noise_events, controller_record=run["record"])
        result[cls.__name__] = row
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=96000)
    parser.add_argument("--shots", type=int, default=240)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    cert = certify(SELECTED, *support_tables())
    independent = audit(SELECTED, *envelope())
    assert cert["all_have_common_support"] and not independent["bad_one"] and not independent["bad_two"]
    clean = {}
    for cls in (BudgetPilot,FastTree,ScreenTree,FilterScreenTree,cat.FiveParityCat,ScreenCat):
        b = noisy.RecordBackend()
        options = (cat.MATCHED | cat.DIRECT) if issubclass(cls, cat.FiveParityCat) else noisy.OPTIONS
        assert cls(b, **options).run()["accepted"]
        clean[cls.__name__] = Counter(op for op,_ in b.ops)
    w = {"clean": shot(2, [], ScreenTree), "nonzero": shot(2,[report("source/certify/screen/Z/0","s")],ScreenTree)}
    assert w["nonzero"]["accepted"] and w["nonzero"]["cx"] > w["clean"]["cx"]
    (args.folder / "certificate.json").write_text(json.dumps({"selected": SELECTED, "common": cert, "forward": independent,
                                                              "clean_gates": clean, "witnesses":w}, indent=2) + "\n")
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for group in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(group) + "\n")
            out.flush()
