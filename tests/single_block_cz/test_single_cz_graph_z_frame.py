"""Persistent graph-Z frames: physical equivalence and report provenance."""
from copy import deepcopy
from pathlib import Path
import json,subprocess,sys
import numpy as np
import pytest
from simulate_single_block_cz_depolarizing import simulate
from single_cz_runtime import NoiseModel
from single_cz_diagnostics import diagnose
from verify_single_block_cz_run import verify_controller
from verify_single_block_cz_run import verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)

def options(graph="tree4",**extra):
    result=dict(seed=2,model=ZERO,graph=graph,source_extraction="decoded_flags",
                flag_recovery="data",graph_stars="bare",terminal_policy="intrinsic",
                data_checks="compact_flags",gauss_frame="persistent")
    result.update(extra)
    return result

def audit(r):
    keys=("profile","history_policy","route","verification_extraction","flag_recovery",
          "max_flag_recoveries","direct_cz_extraction","graph_stars","terminal_policy",
          "data_checks","gauss_frame","graph_z_corrections")
    manifest={k:r[k] for k in keys};manifest["graph"]={"name":r["graph"]}
    verify_controller(r["record"],manifest,r["accepted"])
    return manifest

@pytest.mark.parametrize("graph",["tree4","compact13","current20"])
def test_physical_and_virtual_corrections_same_output_and_cx(graph):
    runs={mode:simulate(**options(graph),graph_z_corrections=mode) for mode in ("physical","frame")}
    for r,b in runs.values():
        assert r["accepted"];audit(r)
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)
    a,ba=runs["physical"];b,bb=runs["frame"]
    assert ba.state.sparse_output(ba.data_labels)[0].tolist()==bb.state.sparse_output(bb.data_labels)[0].tolist()
    va=ba.state.sparse_output(ba.data_labels)[1];vb=bb.state.sparse_output(bb.data_labels)[1]
    assert abs(np.vdot(va,vb))==pytest.approx(1)
    updates=[r for r in b["record"] if "graph_z_frame_update" in r]
    assert updates and all(r["reason"].startswith("vertex/") for r in updates)
    assert a["metrics"]["gate_counts"]["CX"]==b["metrics"]["gate_counts"]["CX"]
    assert a["metrics"]["gate_counts"].get("Z",0)-b["metrics"]["gate_counts"].get("Z",0)==len(updates)

@pytest.mark.parametrize("fault",[
    {"context":"persistent/0/star/1","operation":"MZ","targets":["s"],"timing":"report","flip_report":True},
    {"context":"persistent/0/star/1","operation":"CX","targets":["s","A0"],"paulis":{"A0":"Z"}},
    {"context":"persistent/2/transported_Gauss","operation":"MZ","targets":["s"],"timing":"report","flip_report":True},
])
def test_one_fault_report_or_graph_phase_is_not_hidden(fault):
    r,b=simulate(**options(),graph_z_corrections="frame",injections=[fault])
    assert len(b.injected_events)==1
    audit(r)
    if r["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)

def test_frame_and_sign_tampering_rejected():
    r,b=simulate(**options(),graph_z_corrections="frame");manifest=audit(r)
    for key in ("graph_z_frame_mask","graph_z_frame_flip","raw_reported_parity"):
        rows=deepcopy(r["record"])
        row=next(row for row in rows if row.get("check","").endswith("/transported_Gauss"))
        row[key]^=1
        with pytest.raises(AssertionError):verify_controller(rows,manifest,True)
    rows=deepcopy(r["record"])
    rows.pop(next(i for i,row in enumerate(rows) if "graph_z_frame_update" in row))
    with pytest.raises(AssertionError):verify_controller(rows,manifest,True)

@pytest.mark.parametrize("graph",["tree4","compact13"])
def test_two_faults_share_one_global_budget(graph):
    faults=[{"context":"persistent/0/star/1","operation":"MZ","targets":["s"],"timing":"report","flip_report":True},
            {"context":"persistent/1/transported_Gauss","operation":"MZ","targets":["s"],"timing":"report","flip_report":True}]
    r,b=simulate(**options(graph),graph_z_corrections="frame",injections=faults)
    assert len(b.injected_events)==2;audit(r)
    if r["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)

def test_negative_sector_and_unsupported_schedule():
    for mode in ("physical","frame"):
        r,b=simulate(**options(seed=0),graph_z_corrections=mode)
        assert not r["accepted"];audit(r)
    with pytest.raises(ValueError,match="persistent"):
        simulate(graph_z_corrections="frame",model=ZERO)

def test_default_is_resolved_in_api_and_old_manifests_remain_physical():
    r,b=simulate(**options())
    assert r["graph_z_corrections"]=="frame"
    assert any("graph_z_frame_update" in row for row in r["record"])
    audit(r)
    # Other schedules retain their physical default, including old manifests.
    r,b=simulate(seed=2,model=ZERO)
    assert r["graph_z_corrections"]=="physical"
    manifest=audit(r);manifest.pop("graph_z_corrections")
    verify_controller(r["record"],manifest,r["accepted"])

@pytest.mark.parametrize("override",[None,"physical"])
def test_cli_default_override_and_saved_metadata(tmp_path,override):
    folder=tmp_path/"run"
    command=[sys.executable,str(Path(sys.modules[simulate.__module__].__file__)),
             "--shots","1","--seed","2","--graph","tree4","--gauss-frame","persistent",
             "--source-extraction","decoded_flags","--flag-recovery","data","--graph-stars","bare",
             "--terminal-policy","intrinsic","--data-checks","compact_flags",
             "--two-qubit-infidelity","0","--readout-flip-probability","0","--output-dir",str(folder)]
    if override:command += ["--graph-z-corrections",override]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    mode=override or "frame"
    assert json.loads((folder/"manifest.json").read_text())["graph_z_corrections"]==mode
    assert json.loads((folder/"shots.jsonl").read_text())["graph_z_corrections"]==mode
    assert verify_run(folder)["accepted_outputs_recomputed"]==1
