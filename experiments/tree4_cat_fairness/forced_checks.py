"""Forced physical trajectories for the global-history proof and its exclusions."""
import json

from candidates import BareInnerTree, FilteredCat, FilteredTree, LeanResourceCat, ShortPostCat, settings
from cat_envelope import ghz_prefix, syndrome_certificate
from holdout import run_arm
from trace_audit import HERE, RepairedTree, ScreenCat, noisy, trace
from final_diagnostic import ScreenTree
from check_single_cz_gauged_flag_composition import shot as old_tree_shot
from single_cz_controller import SimulationController


CLEAN_RATES = dict.fromkeys(noisy.RATES, "0")


class UnframedCat(ShortPostCat):
    def short_sign(self, prefix):
        super().short_sign(prefix)
        return 0


class ScreenBeforeTreeHandoff(BareInnerTree):
    """Experimental relocation through V, with the post-handoff screen deleted."""

    def flatten_final_cycles(self):
        SimulationController.coordinates(self)
        super().terminal_screen()
        SimulationController.coordinates(self)

    def terminal_screen(self):
        pass


def report(name, q):
    return dict(timing="report", context=name, operation="MZ", targets=[q], flip_report=True)


def idle(q, pauli):
    return dict(timing="idle", context="short_cat/1/Z/0", operation="PREP", targets=["s"], paulis={q: pauli})


def forced(cls, seed, faults=()):
    row = run_arm(cls, seed, CLEAN_RATES, faults)
    assert row["status"] == "completed", (cls.__name__, row.get("detail"))
    assert len(row["injected_events"]) == len(faults), (cls.__name__, seed, row["injected_events"], faults)
    return row


def check_match(row):
    assert row["accepted"], row["reason"]
    assert row["diagnostics"]["decoded_target_within_tolerance"]
    assert abs(row["diagnostics"]["probability_in_weight_two_lookup"] - 1) < 1e-10


def votes(row):
    return [r for r in row["record"] if "vote_mode" in r]


def main():
    results = {}
    for cls in (ScreenTree, RepairedTree):
        results[cls.__name__ + "_tree_regression"] = [old_tree_shot(cls, pair) for pair in ((), (0,), (1,), (0, 1))]
    original, repaired = (results[cls.__name__ + "_tree_regression"][-1] for cls in (ScreenTree, RepairedTree))
    assert original["accepted"] and abs(original["diagnostic"]["decoded_target_fidelity"] - 1/9) < 1e-12
    assert repaired["reason"] == "gauged_flag_frame_collision"

    clean = forced(LeanResourceCat, 2)
    check_match(clean)
    results["lean_clean"] = clean
    sign = forced(LeanResourceCat, 2, [idle("D5", "Z")])
    assert votes(sign)[1]["raw_U"] == votes(sign)[1]["inner_x_parity_frame"] == 1
    check_match(sign)
    results["odd_Z_corrected_sign"] = sign
    recovery = forced(LeanResourceCat, 2, [idle("D8", "X"), idle("D5", "Z")])
    assert any(r.get("correction") == (1 << 8, 0) for r in recovery["record"] if "cat_Z_reference" in r)
    assert votes(recovery)[1]["raw_U"] == votes(recovery)[1]["inner_x_parity_frame"] == 1
    check_match(recovery)
    results["Z_recovery_keeps_odd_X_parity"] = recovery

    audit = syndrome_certificate(ghz_prefix(LeanResourceCat, settings(LeanResourceCat)))
    witnesses = audit["bounds"][2]["largest"]["faults"]
    broad = [dict(w, context="terminal/2/U") for w in witnesses]
    masking = forced(LeanResourceCat, 2, broad)
    row = next(r for r in masking["record"] if r.get("cat") == "terminal/2/U")
    assert row["four_parity_reports"] == [0]*4
    check_match(masking)
    assert masking["diagnostics"]["raw_physical_target_fidelity"] < .99
    results["two_broad_cat_hooks_cancel_to_two_sites"] = masking
    fallback = [
        dict(context="terminal/2/U", operation="CX", targets=["L7", "L8"], paulis={"L8": "X"}),
        dict(context="terminal/2/U", operation="CX", targets=["L19", "w"], occurrence=2, paulis={"L19": "X"}),
    ]
    history = forced(LeanResourceCat, 2, fallback)
    records = next(r["records"] for r in history["record"] if r.get("cat_fallback") == "terminal/2/U")
    assert len(records) == 2 and records[0] == records[1]
    check_match(history)
    results["late_leaf_fault_after_clean_cat_reference"] = history

    late = forced(LeanResourceCat, 2, [
        report("compact/terminal_screen/0/Z/5", "f0"),
        dict(context="terminal/2/U", operation="T", targets=["D0"], paulis={"D0": "Z"}),
    ])
    assert late["terminal_screen_outcome"] == "flag_verified"
    check_match(late)
    results["screen_flag_recovery_then_physical_T_fault"] = late

    negative_seed = next(s for s in range(30) if not votes(forced(ShortPostCat, s))[0]["passing"])
    negative = forced(ShortPostCat, negative_seed, [report("terminal/0/U", "L0"), report("terminal/1/U", "L0")])
    assert [r["passing"] for r in votes(negative)][:2] == [True, True] and not negative["accepted"]
    results["true_negative_with_two_wrong_positive_votes"] = negative
    bad_sign = forced(UnframedCat, negative_seed, [idle("D5", "Z")])
    assert bad_sign["accepted"] and bad_sign["diagnostics"]["decoded_target_fidelity"] < 1e-10
    good_sign = forced(ShortPostCat, negative_seed, [idle("D5", "Z")])
    assert not good_sign["accepted"]
    results["omitting_sign_frame_one_fault_counterexample"] = {"unframed": bad_sign, "framed": good_sign}

    for unfiltered, filtered, name, qubit in (
        (BareInnerTree, FilteredTree, "vertex_readout", "a0"),
        (LeanResourceCat, FilteredCat, "terminal/0/U", "L0"),
    ):
        inj = [report(name, qubit)]
        uncut, cut = forced(unfiltered, 2, inj), forced(filtered, 2, inj)
        check_match(uncut)
        assert cut["reason"] == "negative_entry"
        results[filtered.__name__ + "_false_negative_entry"] = {"unfiltered": uncut, "filtered": cut}

    transfer = [report("edge_readout", q) for q in ("A0", "A1")]
    clean_transfer = forced(ScreenBeforeTreeHandoff, 2)
    check_match(clean_transfer)
    singles = [forced(ScreenBeforeTreeHandoff, 2, [report("edge_readout", f"A{e}")]) for e in range(4)]
    for row in singles:
        check_match(row)
    bad = forced(ScreenBeforeTreeHandoff, 2, transfer)
    assert bad["accepted"] and abs(bad["diagnostics"]["decoded_target_fidelity"] - .5) < 1e-10
    good = forced(BareInnerTree, 2, transfer)
    assert not good["accepted"] or good["diagnostics"]["decoded_target_within_tolerance"]
    results["tree_screen_relocation_counterexample"] = {"clean": clean_transfer,
        "single_report_flips": singles, "two_report_flips": bad, "post_handoff_control": good}

    context_reports = {("terminal/0/U", "L0"): 1, ("terminal/1/U", "L0"): 1,
                       ("terminal/2/U", "L0"): 1}
    baseline_stop, _ = trace(ScreenCat, backend=noisy.RecordBackend(context_reports=context_reports))
    assert baseline_stop["reason"] == "insufficient_terminal_rounds"
    assert sum("passing_terminal_round" in r for r in baseline_stop["record"]) == 3
    results["baseline_cat_stops_after_three_failed_votes"] = {k: baseline_stop[k] for k in ("reason", "record", "counts")}
    (HERE / "forced_checks.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Saved {len(results)} forced checks")


if __name__ == "__main__":
    main()
