"""Test block-ordered single-flag meters for the known source on fresh attempts."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations_with_replacement
import json
from pathlib import Path
import sys
from unittest.mock import patch

from study_single_cz_bare_inner import inner_program, signatures, code
from study_single_cz_vote_budget import BudgetPilot, noisy
from single_cz_direct_outer_pilot import DressedFlag
from single_cz_controller import KnownSourceFlag

sys.path.insert(0, str(noisy.ROOT / "tmp"))
import cz_review_noisy as cat


def source_meter(axis, support):
    sites = [f"D{q}" for q in support]
    ops = inner_program(axis, sites)
    if len(sites) == 4:
        assert len({q // 4 for q in support}) == 1
        return ops
    assert len(sites) in (6, 8)
    assert all(support[i] // 4 == support[i + 1] // 4 for i in range(0, len(sites), 2))
    flag_cx = ("CX", ("s", "f0") if axis == "X" else ("f0", "s"))
    flag_basis = [("H", ("f0",))] if axis == "Z" else []
    data_start = 2 if axis == "X" else 1
    close = data_start + len(sites) - 2
    ops[close:close] = [flag_cx, *flag_basis, ("MZ", ("f0",))]
    ops[data_start + 2:data_start + 2] = [("PREP", ("f0",)), *flag_basis, flag_cx]
    return ops


def generators():
    for axis, supports in (("Z", code.SUPPORTS), ("X", (*code.SUPPORTS, code.X0, code.X1))):
        for j, support in enumerate(supports):
            yield axis, j, support


class SourceWindowPilot(BudgetPilot):
    def prep(self, q):
        super().prep(q)
        if q == "s" and self.b.context.startswith("source/certify/") and "/Z/" in self.b.context:
            if hasattr(self.b, "absorb_parity_helper"):
                self.b.absorb_parity_helper(q)

    def source_code(self, name):
        reports = []
        for axis, j, support in generators():
            prefix = f"{name}/{axis}/{j}"
            try:
                reports.append(self.direct_meter(prefix, source_meter(axis, support)))
            except DressedFlag as flag:
                raise KnownSourceFlag(prefix) from flag
        return reports


def certificate():
    checks = {}
    for axis, j, support in generators():
        gates = source_meter(axis, support)
        labels = [f"D{q}" for q in support] + ["s", "f0"]
        gates = [(op, tuple(labels.index(q) for q in qs)) for op, qs in gates] + [("BOUNDARY", ())]
        full = (1 << len(support)) - 1
        flag_mask = int(len(support) > 4)
        cases, n = signatures(gates, range(len(support)), full, flag_mask)
        cases.add((0, 0, 0))

        def blocks(x, z):
            return min(len({q // 4 for i,q in enumerate(support) if (a | b) >> i & 1})
                       for a,b in ((x,z),(x ^ full,z) if axis == "X" else (x,z ^ full)))

        assert all(f or blocks(x,z) <= 1 for x,z,f in cases)
        pairs = 0
        for (x,z,f),(a,b,g) in combinations_with_replacement(cases, 2):
            if f == g:
                assert blocks(x ^ a,z ^ b) <= 2
                pairs += 1
        checks[f"{axis}/{j}"] = {"locations": n, "signatures": len(cases), "flag_cancelling_pairs": pairs}
    clean = {}
    for cls in (BudgetPilot, SourceWindowPilot):
        rec = noisy.RecordBackend()
        assert cls(rec, **noisy.OPTIONS).run()["accepted"]
        clean[cls.__name__] = Counter(op for op,_ in rec.ops)
    return {"checks": checks, "clean_gates": clean}


def trial(seed):
    rows = {}
    cat_cls, cat_options = cat.ARMS["cat-five-parity"]
    for name, make in (("parent", lambda b: BudgetPilot(b, **noisy.OPTIONS)),
                       ("source_window", lambda b: SourceWindowPilot(b, **noisy.OPTIONS))):
        with patch.object(noisy, "controller", lambda b,*_: make(b)):
            rows[name] = noisy.trial((None, seed, seed, noisy.RATES, False))
    backend = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed), model=noisy.NoiseModel(**noisy.RATES))
    run = cat_cls(backend, **cat.MATCHED, **cat_options).run()
    row = {"seed": seed, "execution_status": "completed", "accepted": run["accepted"],
           "reason": run.get("reason"), "metrics": backend.metrics()}
    if row["accepted"]:
        row["diagnostics"] = noisy.diagnose(*backend.state.sparse_output(backend.data_labels))
    rows["tuned_cat"] = row
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--shots", type=int, default=400)
    parser.add_argument("--seed", type=int, default=93000)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    args.folder.mkdir(exist_ok=False)
    (args.folder / "audit.json").write_text(json.dumps(certificate(), indent=2) + "\n")
    with (args.folder / "shots.jsonl").open("x") as out, ProcessPoolExecutor(args.workers) as pool:
        for group in pool.map(trial, range(args.seed, args.seed + args.shots)):
            out.write(json.dumps(group) + "\n")
            out.flush()
