"""Short correctness checks for the matched twenty-leaf-cat baseline.

No benchmark campaign: a few exact/noiseless and injected-fault trajectories,
one small saved run, and elementary schedule comparisons.
"""
from pathlib import Path
import json
import subprocess
import sys
import pytest

from simulate_single_block_cz_cat_depolarizing import CatStateController,simulate,clean_costs
from simulate_single_block_cz_depolarizing import clean_costs as graph_costs
from single_cz_controller import SimulationController
from single_cz_runtime import NoiseModel
from single_cz_diagnostics import diagnose
from run_single_block_cz_controller import RecordBackend
from verify_single_block_cz_run import verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)


def test_matched_source_and_ordinary_checks_but_actual_twenty_leaf_cat():
    cat,graph=RecordBackend(),RecordBackend()
    a,b=CatStateController(cat),SimulationController(graph)
    a.source();b.source()
    assert cat.ops==graph.ops and a.source_extraction==b.source_extraction=="rolling_flags"
    cat,graph=RecordBackend(),RecordBackend()
    a,b=CatStateController(cat),SimulationController(graph)
    for q in range(20):a.prep(f"D{q}");b.prep(f"D{q}")
    a.code("terminal/0");b.code("terminal/0")
    assert cat.ops==graph.ops
    cat=RecordBackend();c=CatStateController(cat)
    result=c.run();assert result["accepted"]
    assert not any(q.startswith(("a","A")) for op,qs in cat.ops for q in qs)
    cats=[r for r in result["record"] if "cat" in r]
    assert len(cats)==3 and all(r["cat"].endswith("/U") for r in cats)
    assert all(r["reference"]["kind"]=="two_initial_zero_scans" for r in cats)
    measurements=[r for r in result["record"] if r.get("extraction")=="verified_cat_CZ"]
    assert len(measurements)==3 and all(len(r["leaf_reports"])==20 for r in measurements)
    assert sum(op=="CX" and qs[0].startswith("L") and qs[1].startswith("D") for op,qs in cat.ops)==60


def test_exact_clean_costs_share_the_graph_sources_and_support_decoded_option():
    cat=clean_costs();graph=graph_costs()
    c=cat["direct_cat/recovery"]
    assert (c["gates"]["CX"],c["T_or_TDG"],c["peak_live"])==(2124,120,41)
    assert cat["compact13/recovery"]==graph["compact13/recovery"]
    assert c["stages"]["source/checks"]==graph["compact13/recovery"]["stages"]["source/checks"]
    assert c["stages"]["terminal/U"]["CX"]==345
    assert clean_costs(source_extraction="decoded_flags")["direct_cat/recovery"]["gates"]["CX"]==1716
    with pytest.raises(ValueError):CatStateController(RecordBackend(),route="gauging")


@pytest.mark.parametrize("seed",(0,1,2))
def test_noiseless_cat_outputs_have_the_same_two_qubit_magic_target(seed):
    result,b=simulate(seed=seed,model=ZERO)
    assert result["route"]=="direct_cat" and result["direct_cz_extraction"]=="cat"
    assert result["metrics"]["sampled_noise_events"]==0
    assert not any("graph_parity_verification" in r for r in result["record"])
    if result["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    else:assert result["reason"]=="insufficient_terminal_rounds"


def test_false_cat_leaf_report_and_two_late_data_faults_are_charged():
    faults=[{"context":"terminal/0/U","operation":"MZ","targets":["L0"],
             "timing":"report","flip_report":True}]
    result,b=simulate(seed=0,model=ZERO,injections=faults)
    assert result["accepted"] and len(b.injected_events)==1
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)
    faults=[{"context":"terminal/2/U","operation":"BOUNDARY","timing":"idle", "paulis":{q:p}}
            for q,p in (("D2","X"),("D7","Y"))]
    result,b=simulate(seed=0,model=ZERO,injections=faults)
    assert result["accepted"] and len(b.injected_events)==2
    d=diagnose(*b.state.sparse_output(b.data_labels))
    assert d["decoded_target_fidelity"]==pytest.approx(1)
    assert d["raw_physical_target_fidelity"]<1e-10


def test_broad_cat_preparation_hook_is_repaired_before_touching_data():
    faults=[{"context":"terminal/0/U","operation":"CX","targets":["L0","L1"],
             "paulis":{"L1":"X"}}]
    result,b=simulate(seed=0,model=ZERO,injections=faults)
    assert result["accepted"] and len(b.injected_events)==1
    first=next(r for r in result["record"] if r.get("cat")=="terminal/0/U")
    assert any(any(r) for r in first["flags"]) and any(first["repair_pattern"])
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)


def test_actual_cat_baseline_cli_is_verifiable_and_its_snapshot_runs(tmp_path):
    script=Path(__file__).with_name("simulate_single_block_cz_cat_depolarizing.py")
    directory=tmp_path/"cat"
    subprocess.run([sys.executable,"-B",str(script),"--shots","1","--two-qubit-infidelity","0",
                    "--readout-flip-probability","0","--output-dir",str(directory)],
                   check=True,capture_output=True,text=True,timeout=30)
    manifest=json.loads((directory/"manifest.json").read_text())
    assert manifest["entrypoint"]==script.name and manifest["direct_cz_extraction"]=="cat"
    assert not manifest["graph_allocated"] and manifest["verification_extraction"]=="flags"
    assert manifest["source_extraction"]=="rolling_flags"
    assert script.name in manifest["source_sha256"]
    result=verify_run(directory)
    assert result["accepted_outputs_recomputed"]==1 and result["saved_source_snapshot_verified"]
    costs=tmp_path/"snapshot-cost"
    subprocess.run([sys.executable,"-B",str(directory/"source_snapshot"/script.name),
                    "--cost-only","--output-dir",str(costs)],
                   check=True,capture_output=True,text=True,timeout=15)
    assert json.loads((costs/"clean-costs.json").read_text())["direct_cat/recovery"]["gates"]["CX"]==2124
    path=directory/"attempts/000000/controller.json"
    rows=json.loads(path.read_text());row=next(r for r in rows if r.get("extraction")=="verified_cat_CZ")
    row["leaf_reports"][0]^=1;row["leaf_reports"][1]^=1
    path.write_text(json.dumps(rows))
    with pytest.raises(AssertionError):verify_run(directory)
