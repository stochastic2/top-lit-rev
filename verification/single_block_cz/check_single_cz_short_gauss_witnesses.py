"""Targeted physical trajectories through the optimized Gauss schedule."""

import argparse
import json
from pathlib import Path

import run_single_cz_direct_outer_pilot as noisy
from single_cz_tree_z_recovery_pilot import TreeZRecoveryPilot


class RepeatedTreeReadout(TreeZRecoveryPilot):
    """Measure two additional Z copies before using majority feedback."""

    def mz(self, q):
        if self.b.context == "edge_readout" and q.startswith("A") and int(q[1:]) in self.graph_choice.tree:
            bits = []
            for _ in range(2):
                self.prep("w")
                self.gate("CX", q, "w")
                bits.append(super().mz("w"))
            return int((sum(bits) + super().mz(q)) >= 2)
        return super().mz(q)


def shot(seed, injections, cls=TreeZRecoveryPilot):
    coordinate_gates = []

    def trace(event):
        if event.get("kind") == "physical" and event["context"] == "coordinates/V" and event["operation"] == "CX":
            coordinate_gates.append(event["event"])

    backend = noisy.QuantumBackend(seed=seed, noise_seed=noisy.noise_seed(seed),
                                   model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES, "0")), injections=injections, trace=trace)
    pilot = cls(backend, **noisy.OPTIONS)
    run = pilot.run()
    assert len(backend.injected_events) == len(injections)
    votes = [event for event in run["record"] if set(event).intersection({"direct_vote", "vertex_reports",
                                                                        "root_parity_frame_after_Z_recovery"})]
    result = {"accepted": run["accepted"], "reason": run.get("reason"), "votes": votes,
              "faults": backend.injected_events,
              "gauged_Z_reference": [entry for entry in run["record"] if "gauged_Z_reference" in entry],
              "coordinates_CX": len(coordinate_gates),
              "graph_verifier_reports": [r["reported_parity"] for r in run["record"]
                                         if r.get("check") == "graph/tree_hook_check"],
              "terminal_screen_outcome": pilot.terminal_screen_outcome, "cx": backend.gate_counts["CX"]}
    if run["accepted"]:
        diagnostic = noisy.diagnose(*backend.state.sparse_output(backend.data_labels))
        assert diagnostic["decoded_target_within_tolerance"]
        result["decoded_fidelity"] = diagnostic["decoded_target_fidelity"]
        result["raw_fidelity"] = diagnostic["raw_physical_target_fidelity"]
    return result


def idle_at_vote_start(q, pauli):
    return {"timing": "idle", "context": "direct/vote/0/Z/0", "operation": "PREP", "targets": ["s"],
            "paulis": {q: pauli}}


def report(context, q):
    return {"timing": "report", "context": context, "operation": "MZ", "targets": [q], "flip_report": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {
        "clean_positive": shot(2, []),
        "odd_Z_sign_is_corrected_in_the_vote": shot(2, [idle_at_vote_start("D0", "Z")]),
        "wrong_tree_bit_is_rejected_at_terminal": shot(2, [report("edge_readout", "A1")]),
        "repeated_tree_readout_recovers_wrong_report": shot(2, [report("edge_readout", "A1")], RepeatedTreeReadout),
        "gauged_Z_recovery_preserves_pending_Z_phase_error": shot(2, [idle_at_vote_start("D8", "X"), idle_at_vote_start("D5", "Z")]),
        "negative_sector_two_wrong_votes": shot(0, [report("vertex_readout", "a0"), report("direct/vote/0/root_Gauss", "s")]),
        "dangerous_raw_resource_hook_rejects_that_resource": shot(2, [{"context": "graph/tree_raw", "operation": "CX",
                                                                      "targets": ["a0", "A1"], "paulis": {"a0": "X"}}]),
    }
    assert results["clean_positive"]["accepted"]
    parity = results["odd_Z_sign_is_corrected_in_the_vote"]
    assert parity["accepted"] and parity["votes"][1]["root"] == parity["votes"][1]["inner_x_parity_frame"] == 1
    handoff = results["wrong_tree_bit_is_rejected_at_terminal"]
    assert not handoff["accepted"] and handoff["reason"] == "data_ambiguity"
    repeated = results["repeated_tree_readout_recovers_wrong_report"]
    assert repeated["accepted"] and repeated["terminal_screen_outcome"] == "zero_accept"
    assert repeated["cx"] == results["clean_positive"]["cx"] + 8
    recovery = results["gauged_Z_recovery_preserves_pending_Z_phase_error"]
    assert recovery["accepted"] and len(recovery["gauged_Z_reference"]) == 1
    assert recovery["coordinates_CX"] == 0
    assert any(row.get("root_parity_frame_after_Z_recovery") == 1 for row in recovery["votes"])
    assert not results["negative_sector_two_wrong_votes"]["accepted"]
    assert results["dangerous_raw_resource_hook_rejects_that_resource"]["graph_verifier_reports"][:2] == [1, 0]
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(f"Verified {len(results)} targeted physical trajectories and saved {args.output}")


if __name__ == "__main__":
    main()
