"""Fast verifier tests on saved files; no quantum trajectories are rerun."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import pytest

from c4_helix_noiseless import LOGICAL_X0
from simulate_c4_helix_sparse import output_diagnostics
from sparse_wavefunction import SparseState
from verify_c4_helix_run import expected_codewords, main, verify_run


def save_state(directory, payload):
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    reference = f"states/{sha256(serialized.encode()).hexdigest()}.json"
    destination = directory / reference
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(serialized + "\n")
    return reference


def save_records(directory, records):
    (directory / "shots.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records))


def json_diagnostics(state):
    return json.loads(json.dumps(output_diagnostics(state)))


@pytest.fixture
def saved_run(tmp_path):
    h_words, k_words = expected_codewords()
    state = SparseState(tuple(f"C_{q}" for q in range(20)),
                        {word: 2 if word in h_words else 1 for word in k_words})
    reference = save_state(tmp_path, state.canonical_payload())
    accepted = {"shot_index": 0, "accepted": True, "swap_plus": True,
                "vertex_x": [0] * 5, "gauge_z": "0" * 20, "swap_offsets": [0] * 5,
                "b_z": "0" * 20, "b_logical_z0": 0,
                "vertex_probability_given_gauge": "3/64",
                "b_probability_given_vertex_gauge": "5/3072",
                "c_state_reference": reference, "c_diagnostics": json_diagnostics(state)}
    odd = {**deepcopy(accepted), "shot_index": 1, "accepted": False, "swap_plus": False,
           "vertex_x": [1, 0, 0, 0, 0], "vertex_probability_given_gauge": "1/64"}
    for field in ("gauge_z", "swap_offsets", "b_z", "b_logical_z0",
                  "c_state_reference", "c_diagnostics", "b_probability_given_vertex_gauge"):
        odd[field] = None
    xi = "".join("1" if q in LOGICAL_X0 else "0" for q in range(20))
    failed_b = {**deepcopy(accepted), "shot_index": 2, "accepted": False,
                "b_z": xi, "b_logical_z0": 1, "b_probability_given_vertex_gauge": "1/3072",
                "c_state_reference": None, "c_diagnostics": None}
    records = [accepted, odd, failed_b, {**deepcopy(accepted), "shot_index": 3}]
    save_records(tmp_path, records)
    summary = {"attempts": 4, "accepted": 2, "b_source_entries": 512,
               "c_source_entries": 1024, "gauge_words": 16, "ideal_success_probability": "5/8"}
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    return tmp_path, records


def test_valid_run_and_cli_are_read_only(saved_run):
    directory, _ = saved_run
    before = {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    report = verify_run(directory)
    assert report["valid"] and report["errors"] == []
    assert report["counts"] == {"attempts": 4, "accepted": 2, "vertex_pass": 3,
                                "vertex_rejected": 1, "B_rejected": 1}
    assert len(report["verified_states"]) == 1
    assert report["statistics"]["overall_acceptance"]["expected_probability"] == "5/8"
    script = Path(__file__).with_name("verify_c4_helix_run.py")
    process = subprocess.run([sys.executable, "-B", str(script), str(directory), "--json"],
                             capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout)["valid"]
    after = {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    assert before == after


@pytest.mark.parametrize("change, message", [
    (lambda records: records[0]["c_diagnostics"].update(logical_X0="0"), "diagnostics disagree"),
    (lambda records: records[0].update(swap_offsets=[1, 0, 0, 0, 0]), "SWAP offsets"),
    (lambda records: records[0].update(b_logical_z0=1), "B logical parity"),
    (lambda records: records[0].update(vertex_probability_given_gauge="1/64"), "vertex-branch"),
    (lambda records: records[1].update(gauge_z="0" * 20), "not performed"),
    (lambda records: records[3].update(shot_index=0), "out of order"),
])
def test_inconsistent_shot_record_fails(saved_run, change, message):
    directory, records = saved_run
    change(records)
    save_records(directory, records)
    report = verify_run(directory)
    assert not report["valid"]
    assert any(message in error for error in report["errors"])
    assert main([str(directory), "--json"]) == 1


def test_summary_and_missing_file_fail(saved_run):
    directory, records = saved_run
    summary = json.loads((directory / "summary.json").read_text())
    summary["accepted"] = 999
    (directory / "summary.json").write_text(json.dumps(summary))
    report = verify_run(directory)
    assert not report["valid"] and any("summary.json: accepted" in error for error in report["errors"])
    (directory / records[0]["c_state_reference"]).unlink()
    report = verify_run(directory)
    assert not report["valid"] and any("No such file" in error for error in report["errors"])


def test_wrong_amplitudes_fail_even_if_hash_and_diagnostics_are_updated(saved_run):
    directory, records = saved_run
    payload = json.loads((directory / records[0]["c_state_reference"]).read_text())
    payload["weights"][next(iter(payload["weights"]))] *= -1
    # Norm unchanged: update both the hash and diagnostics, so the independent
    # mathematical target (not just metadata consistency) must catch the error.
    reference = save_state(directory, payload)
    diagnostics = json_diagnostics(SparseState.from_payload(payload))
    for record in records:
        if record["accepted"]:
            record["c_state_reference"] = reference
            record["c_diagnostics"] = diagnostics
    save_records(directory, records)
    report = verify_run(directory)
    assert not report["valid"]
    assert any("amplitudes do not equal" in error for error in report["errors"])


def test_hash_and_normalization_are_checked(saved_run):
    directory, records = saved_run
    path = directory / records[0]["c_state_reference"]
    payload = json.loads(path.read_text())
    payload["norm_squared"] += 1
    path.write_text(json.dumps(payload))
    assert any("content hash" in error for error in verify_run(directory)["errors"])
    reference = save_state(directory, payload)
    for record in records:
        if record["accepted"]:
            record["c_state_reference"] = reference
    save_records(directory, records)
    assert any("normalization" in error for error in verify_run(directory)["errors"])


def test_zero_accepted_states_and_statistics_are_reported_separately(saved_run):
    directory, records = saved_run
    odd = records[1]
    records = [{**deepcopy(odd), "shot_index": index} for index in range(30)]
    save_records(directory, records)
    summary = json.loads((directory / "summary.json").read_text())
    summary.update(attempts=30, accepted=0)
    (directory / "summary.json").write_text(json.dumps(summary))
    report = verify_run(directory)
    assert report["valid"] and report["verified_states"] == {}
    assert report["statistics"]["overall_acceptance"]["below_alpha"]
    assert report["statistics"]["B_selection_given_vertex_pass"] is None
    assert main([str(directory)]) == 0


def test_unreadable_input_and_reference_escape_fail(saved_run, capsys):
    directory, records = saved_run
    records[0]["c_state_reference"] = "../outside.json"
    save_records(directory, records)
    assert any("inside the run directory" in error for error in verify_run(directory)["errors"])
    (directory / "shots.jsonl").write_text("not JSON\n")
    assert not verify_run(directory)["valid"]
    assert main([str(directory / "missing")]) == 1
    assert "FAIL" in capsys.readouterr().out
