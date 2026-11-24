r"""Read-only verification of a completed full C4-Helix sparse simulation.

Usage from the repository root::

    $HOME/pytket-venv/bin/python -B src/verify_c4_helix_run.py \
        src/output/my-c4-helix-run

Check summary.json, every shots.jsonl record, and every referenced C state.
No trajectories are rerun and no files are written. File/state inconsistencies
produce exit code 1. Statistical fluctuations are reported separately and do
not make a mathematically correct saved state fail verification.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from scipy.stats import binomtest

from c4_helix_noiseless import CHECK_SUPPORTS, EDGES, LOGICAL_X0, LOGICAL_Z0, TREE_EDGES
from simulate_c4_helix_sparse import output_diagnostics
from sparse_wavefunction import SparseState


def toggle_positions(word: str, positions: tuple[int, ...]) -> str:
    characters = list(word)
    for q in positions:
        characters[q] = "1" if characters[q] == "0" else "0"
    return "".join(characters)


def expected_codewords() -> tuple[set[str], set[str]]:
    """Construct the target independently of the simulator's H/CNOT schedules.

    H = span{r_0,...,r_8}; K = H union (H+xi), xi=logical-X0 support.
    |00_L> = sum_{h in H}|h>/sqrt(512).
    |M0_L> = [2 sum_{h in H}|h> + sum_{h in H}|h+xi>]/sqrt(2560).
    """
    h_words = {"0" * 20}
    for support in CHECK_SUPPORTS:
        h_words |= {toggle_positions(word, support) for word in h_words}
    k_words = h_words | {toggle_positions(word, LOGICAL_X0) for word in h_words}
    if len(h_words) != 512 or len(k_words) != 1024:
        raise ValueError("Physical supports do not generate the expected codeword counts")
    return h_words, k_words


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_state(run_directory: Path, reference: str, expected_weights: dict[str, int]) -> dict:
    """Reload and check actual amplitudes, content hash, and exact observables.

    Compare canonical integer weights with the explicit encoded magic target;
    this also permits a physically irrelevant common real scale or sign.
    Recompute diagnostics from the saved amplitudes rather than trusting JSON.
    """
    require(isinstance(reference, str), "C state reference must be a string")
    relative = Path(reference)
    path = (run_directory / relative).resolve()
    require(not relative.is_absolute() and path.is_relative_to(run_directory),
            "C state reference must remain inside the run directory")
    payload = json.loads(path.read_text())
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    require(path.stem == sha256(serialized.encode()).hexdigest(), "C state content hash mismatch")
    state = SparseState.from_payload(payload)
    require(state.labels == tuple(f"C_{q}" for q in range(20)), "Unexpected C coordinate labels")
    require(state.canonical_payload()["weights"] == expected_weights,
            "Saved amplitudes do not equal the encoded magic state |M0_L>")
    diagnostics = output_diagnostics(state)
    require(diagnostics["in_original_code_space"], "Saved C state fails an original code check")
    expected_logical = {"logical_X0": "4/5", "logical_Z0": "3/5",
                        "logical_Y0": "0", "logical_Z1": "1"}
    require(all(diagnostics[key] == value for key, value in expected_logical.items()),
            "Saved C state has incorrect logical expectations")
    # JSON object keys are strings; the recomputation uses integer weights.
    diagnostics["weight_counts"] = {str(weight): count
                                    for weight, count in diagnostics["weight_counts"].items()}
    return diagnostics


def rate_test(successes: int, attempts: int, expected: Fraction, alpha: float) -> dict | None:
    """Exact two-sided binomial test, with a Wilson interval for the observed rate."""
    if attempts == 0 or not 0 <= successes <= attempts:
        return None
    result = binomtest(successes, attempts, float(expected))
    interval = result.proportion_ci(confidence_level=1 - alpha, method="wilson")
    return {"successes": successes, "attempts": attempts,
            "observed_rate": successes / attempts, "expected_probability": str(expected),
            "two_sided_p_value": float(result.pvalue),
            "rate_confidence_interval": [float(interval.low), float(interval.high)],
            "below_alpha": bool(result.pvalue < alpha)}


def verify_run(run_directory: Path, alpha: float = 0.05) -> dict:
    """Audit a completed full-circuit run without simulating it or changing it.

    Returns a JSON-ready report. ``valid`` concerns exact file/state checks;
    ``statistics`` describes finite-shot evidence, separately. Each distinct
    referenced C file is loaded and checked once, even if many shots share it.
    """
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    directory = Path(run_directory).resolve()
    summary = json.loads((directory / "summary.json").read_text())
    require(isinstance(summary, dict), "summary.json must contain an object")
    h_words, k_words = expected_codewords()
    target = {word: 2 if word in h_words else 1 for word in k_words}
    gauge_words = set()
    for number in range(32):
        vertices = format(number, "05b")
        gauge_words.add("".join(str((int(vertices[u]) + int(vertices[v])) % 2)
                                for u, v in EDGES))
    errors = []
    states: dict[str, dict] = {}
    attempts = accepted = positive = 0
    later_fields = ("gauge_z", "swap_offsets", "b_z", "b_logical_z0",
                    "c_state_reference", "c_diagnostics", "b_probability_given_vertex_gauge")
    with (directory / "shots.jsonl").open() as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            index = attempts
            attempts += 1
            try:
                record = json.loads(line)
                require(isinstance(record, dict), "Shot record must be an object")
                require(type(record["accepted"]) is bool and type(record["swap_plus"]) is bool,
                        "accepted and swap_plus must be booleans")
                accepted += record["accepted"]
                positive += record["swap_plus"]
                require(type(record["shot_index"]) is int and record["shot_index"] == index,
                        "Shot index is duplicated, missing, or out of order")
                bits = record["vertex_x"]
                require(isinstance(bits, list) and len(bits) == 5
                        and all(type(bit) is int and bit in (0, 1) for bit in bits),
                        "Expected five binary vertex-X outcomes")
                even = sum(bits) % 2 == 0
                require(record["swap_plus"] == even, "Vertex parity disagrees with swap_plus")
                require(Fraction(record["vertex_probability_given_gauge"]) == Fraction(3 if even else 1, 64),
                        "Incorrect recorded vertex-branch probability")
                if not even:
                    require(not record["accepted"], "Odd vertex outcome was accepted")
                    require(all(record[field] is None for field in later_fields),
                            "An odd rejection exposes measurements/output that were not performed")
                    continue
                gauge = record["gauge_z"]
                require(isinstance(gauge, str) and gauge in gauge_words, "Invalid gauge-Z word")
                require(record["swap_offsets"] == [0] + [int(gauge[q]) for q in TREE_EDGES],
                        "SWAP offsets disagree with the measured gauge word")
                word = record["b_z"]
                require(isinstance(word, str) and word in k_words, "B-Z word lies outside the code support")
                logical = sum(int(word[q]) for q in LOGICAL_Z0) % 2
                require(record["b_logical_z0"] == logical and record["accepted"] == (logical == 0),
                        "B logical parity or acceptance flag is incorrect")
                require(Fraction(record["b_probability_given_vertex_gauge"])
                        == Fraction(5 if logical == 0 else 1, 3072),
                        "Incorrect recorded B-word probability")
                if record["accepted"]:
                    reference = record["c_state_reference"]
                    require(isinstance(reference, str), "Accepted shot has no C state reference")
                    if reference not in states:
                        states[reference] = verify_state(directory, reference, target)
                    require(record["c_diagnostics"] == states[reference],
                            "Stored diagnostics disagree with the saved amplitudes")
                else:
                    require(record["c_state_reference"] is None and record["c_diagnostics"] is None,
                            "Rejected B outcome has a saved C resource")
            except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
                errors.append(f"shots.jsonl line {line_number}: {exc}")

    expected_summary = {"attempts": attempts, "accepted": accepted,
                        "b_source_entries": 512, "c_source_entries": 1024,
                        "gauge_words": 16, "ideal_success_probability": "5/8"}
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(f"summary.json: {key} is {summary.get(key)!r}; expected {value!r}")
    if attempts == 0:
        errors.append("No shot records were found")
    return {"run_directory": str(directory), "valid": not errors, "errors": errors,
            "counts": {"attempts": attempts, "accepted": accepted, "vertex_pass": positive,
                       "vertex_rejected": attempts - positive, "B_rejected": positive - accepted},
            "verified_states": states, "alpha": alpha,
            "statistics": {"overall_acceptance": rate_test(accepted, attempts, Fraction(5, 8), alpha),
                           "vertex_selection": rate_test(positive, attempts, Fraction(3, 4), alpha),
                           "B_selection_given_vertex_pass": rate_test(accepted, positive, Fraction(5, 6), alpha)}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_directory", type=Path, help="Directory containing summary.json, shots.jsonl, and states/")
    parser.add_argument("--json", action="store_true", help="Print the complete report as JSON to stdout")
    parser.add_argument("--alpha", type=float, default=0.05, help="Statistical notice threshold (default: 0.05)")
    args = parser.parse_args(argv)
    try:
        report = verify_run(args.run_directory, args.alpha)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        if args.json:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        counts = report["counts"]
        print(f"{'PASS' if report['valid'] else 'FAIL'}: saved files and exact quantum-state checks")
        print(f"Run: {report['run_directory']}")
        print(f"Attempts: {counts['attempts']}; accepted: {counts['accepted']}; "
              f"vertex rejections: {counts['vertex_rejected']}; B rejections: {counts['B_rejected']}")
        print(f"Distinct accepted C states verified: {len(report['verified_states'])}")
        for reference, diagnostics in report["verified_states"].items():
            print(f"  {reference}: exact encoded |M0_L>; {diagnostics['entries']} amplitudes; "
                  f"N={diagnostics['norm_squared']}")
            print("  All 18 code checks +1; X0=4/5, Z0=3/5, Y0=0, Z1=1")
        if not report["verified_states"]:
            print("No accepted C state was available to verify.")
        for name, test in report["statistics"].items():
            if test is not None:
                print(f"{name}: {test['successes']}/{test['attempts']} = {test['observed_rate']:.2%}; "
                      f"expected {test['expected_probability']}; two-sided binomial p={test['two_sided_p_value']:.4g}")
                if test["below_alpha"]:
                    print(f"  Sampling notice: p < {args.alpha:g}; investigate with more independent attempts. "
                          "This is separate from exact state verification.")
        for error in report["errors"][:10]:
            print(f"  ERROR: {error}")
        if len(report["errors"]) > 10:
            print(f"  ... and {len(report['errors']) - 10} more errors; use --json for the complete list.")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
