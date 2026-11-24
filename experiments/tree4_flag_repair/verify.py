"""Cross-check the repaired decision against an independent exhaustive envelope."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

from controller import RepairedTree, ScreenTree, noisy, vetoes
from check_single_cz_gauged_flag_composition import shot, GuardedTree
from check_single_cz_short_gauss_vote import signatures
from single_cz_flag_recovery import recovery_table
from single_cz_compact_checks import compact_pauli_program
from single_cz_recovery import m, H, data_table

OUT = Path(__file__).resolve().parent


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def independent_audit():
    # Syndrome and logical labels by raw commutation, independent of remainder().
    def label(x,z):
        bits = [((x & h).bit_count() % 2) for h in H] + [((z & h).bit_count() % 2) for h in H]
        logical = tuple((w & m.mask(s)).bit_count() % 2 for w,s in
                        ((x,m.Z0),(x,m.Z1),(z,m.X0),(z,m.X1)))
        return sum(bit << i for i,bit in enumerate(bits)), logical

    results = {}
    for axis in "XZ":
        ops = compact_pauli_program(axis,4)
        sig,_ = signatures(ops,range(4),15,1)
        local = [(x,z) for x,z,f in sig if f]
        for v,support in enumerate(m.SUPPORTS[:5]):
            tab = recovery_table(axis,support,1,"compact_flags")
            banned = vetoes(axis,support,1,"compact_flags")
            errors = {(x << (4*v),z << (4*v)) for x,z in product(range(16),repeat=2)}
            for x,z in local:
                for conj in range(2 if v else 1):
                    for b in range(5):
                        errors.update(((x << (4*v)) ^ (i << (4*b)), ((z ^ (conj*x)) << (4*v)) ^ (j << (4*b)))
                                      for i,j in product(range(16),repeat=2))
            unsafe = set()
            for x,z in errors:
                s,l = label(x,z)
                c = tab.get(s,{}).get("correction")
                if c and label(*c)[1] != l:
                    unsafe.add(s)
            assert unsafe == banned
            unique = {s for s,r in tab.items() if r["correction"] is not None}
            broad = {s for s in unique if data_table()[s]["correction"] is None}
            assert banned <= broad
            results[f"{axis}/{v}"] = dict(physical_data_terms=len(errors),old_unique=len(unique),
                                          broad_vetoes=len(broad),new_vetoes=sorted(banned))
    return results


def trial(seed):
    out = {}
    for cls in (ScreenTree,RepairedTree,GuardedTree):
        with patch.object(noisy,"controller",lambda b,*_: cls(b,**noisy.OPTIONS)):
            out[cls.__name__] = noisy.trial((None,seed,seed,noisy.RATES,False))
    old,new,broad = out.values()
    assert all(r["execution_status"]=="completed" for r in out.values())
    if new["reason"] != "gauged_flag_frame_collision":
        assert old["accepted"] == new["accepted"] and old.get("diagnostics")==new.get("diagnostics")
        assert old["metrics"]["gate_counts"] == new["metrics"]["gate_counts"]
    assert not broad["accepted"] or new["accepted"]
    return out


def nested_regression():
    faults = [
        {"timing":"idle","context":"direct/vote/0/Z/0","operation":"PREP","targets":["s"],"paulis":{"D8":"X"}},
        {"timing":"report","context":"direct/vote/0/syndrome_recovery/inner_after_X_correction/X/1",
         "operation":"MZ","targets":["f0"],"flip_report":True},
    ]
    b = noisy.QuantumBackend(seed=2, model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES,"0")), injections=faults)
    run = RepairedTree(b,**noisy.OPTIONS).run()
    assert len(b.injected_events) == 2 and any("inner_flag" in r.get("direct_reference","") for r in run["record"])
    diag = noisy.diagnose(*b.state.sparse_output(b.data_labels)) if run["accepted"] else None
    assert diag is None or diag["decoded_target_within_tolerance"]
    return {"accepted":run["accepted"],"reason":run.get("reason"),"faults":b.injected_events,"diagnostic":diag}


if __name__ == "__main__":
    dump("nested.json",nested_regression())
    dump("decoder.json",independent_audit())
    runs = {cls.__name__:[shot(cls,subset) for subset in ((),(0,),(1,),(0,1))]
            for cls in (ScreenTree,RepairedTree)}
    assert runs["RepairedTree"][-1]["reason"] == "gauged_flag_frame_collision"
    assert abs(runs["ScreenTree"][-1]["diagnostic"]["decoded_target_fidelity"]-1/9)<1e-12
    dump("replay.json",runs)
    clean = {}
    for cls in (ScreenTree,RepairedTree):
        b=noisy.RecordBackend()
        assert cls(b,**noisy.OPTIONS).run()["accepted"]
        clean[cls.__name__]=b.ops
    assert clean["ScreenTree"]==clean["RepairedTree"]
    dump("clean.json",Counter(op for op,_ in clean["RepairedTree"]))
    with ProcessPoolExecutor(6) as pool, (OUT/"shots.jsonl").open("w") as stream:
        for rows in pool.map(trial,range(102000,102128)):
            stream.write(json.dumps(rows)+"\n")
