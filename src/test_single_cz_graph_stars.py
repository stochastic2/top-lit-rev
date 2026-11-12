"""Bare-star physical faults, delayed-cycle repair, CLI and regression checks."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys

import pytest
from single_cz_runtime import NoiseModel,QuantumBackend
from single_cz_controller import SimulationController
from single_cz_recovery import GRAPHS
from single_cz_graph_stars import chord_correction,cycle_syndrome
from single_cz_diagnostics import diagnose
from simulate_single_block_cz_depolarizing import simulate,clean_costs
from verify_single_block_cz_run import verify_controller,verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)


def manifest_for(result):
    manifest={k:result[k] for k in ("profile","history_policy","route","verification_extraction",
                                  "flag_recovery","max_flag_recoveries","direct_cz_extraction","graph_stars")}
    manifest.update(graph={"name":result["graph"]},graph_verification="three_zero_Z_edge_scans")
    return manifest


def assert_magic(result,backend):
    assert result["accepted"],result.get("reason")
    assert diagnose(*backend.state.sparse_output(backend.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    verify_controller(result["record"],manifest_for(result),True)


@pytest.mark.parametrize("graph",("compact13","current20"))
@pytest.mark.parametrize("history",("triple","adaptive"))
def test_noiseless_bare_factory_and_unchanged_T_and_peak(graph,history):
    result,b=simulate(seed=2,model=ZERO,graph=graph,history_policy=history,
                      source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare")
    assert_magic(result,b)
    assert all(row.get("extraction")=="bare_graph_X_star" for row in result["record"] if "/star/" in row.get("check",""))
    assert not any(row.get("check","").startswith("gauged/") and "/cycle/" in row.get("check","") for row in result["record"])
    costs=clean_costs(source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare")
    expected=(2665,39) if graph=="compact13" else (2835,46)
    assert (costs[graph+"/recovery"]["gates"]["CX"],costs[graph+"/recovery"]["peak_live"])==expected
    assert costs[graph+"/recovery"]["T_or_TDG"]==256


@pytest.mark.parametrize("name",("compact13","current20"))
def test_two_broad_controller_hooks_are_repaired_without_radius_assumption(name):
    from check_single_cz_graph_stars import delayed_cycle_counterexample
    example=delayed_cycle_counterexample(GRAPHS[name])
    faults=[{"context":f"gauged/0/star/{f['vertex']}","operation":"CX","targets":["s",f"A{f['after_edge']}"],
             "paulis":{"s":"X"}} for f in example["faults"]]
    result,b=simulate(seed=2,model=ZERO,graph=name,source_extraction="decoded_flags",flag_recovery="data",
                      graph_stars="bare",injections=faults)
    assert len(b.injected_events)==2
    assert_magic(result,b)
    repair=next(r for r in result["record"] if "final_cycle_flattening" in r)
    assert repair["syndrome"]==example["cycle_bits"]
    assert repair["X_edges"]==example["new_chord_correction"]
    assert not set(repair["X_edges"]) & set(GRAPHS[name].tree)
    tampered=deepcopy(result["record"])
    next(r for r in tampered if "final_cycle_flattening" in r)["X_edges"].append(GRAPHS[name].tree[0])
    with pytest.raises(AssertionError):verify_controller(tampered,manifest_for(result),True)


def test_late_edge_bit_error_and_wrong_edge_report_share_global_budget():
    faults=[{"context":"final_cycles/2/cycle/8","operation":"MZ","targets":["w"],"timing":"idle","paulis":{"A0":"X"}},
            {"context":"edge_readout","operation":"MZ","targets":["A1"],"timing":"report","flip_report":True}]
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",injections=faults)
    assert len(b.injected_events)==2
    assert_magic(result,b)
    edge=next(r for r in result["record"] if "edge_reports" in r)
    assert edge["decoded"]["report_error"].bit_count()==2


def test_terminal_cycle_meter_phase_spread_does_not_change_magic():
    faults=[{"context":"final_cycles/2/cycle/0","operation":"CX","targets":["A0","w"],"paulis":{"w":"Z"}}]
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",injections=faults)
    assert len(b.injected_events)==1
    assert_magic(result,b)


def test_bare_star_hook_and_a_faulty_chord_correction():
    faults=[{"context":"gauged/0/star/1","operation":"CX","targets":["s","A0"],"paulis":{"s":"X"}},
            {"context":"final_cycles/correction","operation":"X","targets":["A4"],"paulis":{"A4":"Y"}}]
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",injections=faults)
    assert len(b.injected_events)==2
    assert_magic(result,b)


def test_graph_hook_and_data_flag_recovery_compose():
    faults=[{"context":"gauged/0/star/1","operation":"CX","targets":["s","A0"],"paulis":{"s":"X"}},
            {"context":"gauged/1/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}]
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",injections=faults)
    assert len(b.injected_events)==2 and result["successful_flag_recoveries"]==1
    assert_magic(result,b)


def test_two_false_root_reports_cannot_certify_genuine_negative_branch():
    faults=[{"context":f"gauged/{r}/root_Gauss","operation":"MZ","targets":["s"],
             "timing":"report","flip_report":True} for r in range(2)]
    result,b=simulate(seed=0,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",injections=faults)
    assert len(b.injected_events)==2 and not result["accepted"]
    assert result["reason"]=="insufficient_positive_gauged_rounds"


def test_two_faults_after_final_clean_data_record_remain_correctable():
    faults=[{"context":"terminal/2/X/8","operation":"MZ","targets":["s"],"timing":"idle","paulis":{q:p}}
            for q,p in (("D0","X"),("D7","Y"))]
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",injections=faults)
    assert len(b.injected_events)==2
    assert_magic(result,b)
    assert diagnose(*b.state.sparse_output(b.data_labels))["raw_physical_target_fidelity"]<1e-10


def test_coherent_graph_meter_fault_is_not_sampled_as_Paulis():
    class CoherentFault(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="gauged/0/star/1" and targets==("s","A5"):
                self.state.gate("H","s")
                self.state.gate("T","A5")
                self.used=True
    b=CoherentFault(seed=2,model=ZERO)
    c=SimulationController(b,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare")
    result=c.run()
    assert b.used and result["accepted"],result.get("reason")
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)


def test_chord_inverse_is_total_and_does_not_touch_tree():
    from check_single_cz_graph_stars import exact_logical_instrument_check
    for g in GRAPHS.values():
        for word in (0,(1 << len(g.edges))-1,1 << g.tree[0],0b1010101010101):
            bits=[(cycle_syndrome(g,word) >> j)&1 for j in range(len(g.cycles))]
            correction=chord_correction(g,bits)
            mask=sum(1 << e for e in correction)
            assert not set(correction) & set(g.tree) and cycle_syndrome(g,word ^ mask)==0
        assert exact_logical_instrument_check(g)["coherent_cycle_branches"]==4
    with pytest.raises(ValueError):chord_correction(GRAPHS["compact13"],[0])


def test_cli_saves_bare_schedule_and_verifies(tmp_path):
    folder=tmp_path/"bare"
    command=[sys.executable,str(Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")),
             "--shots","1","--seed","2","--two-qubit-infidelity","0","--readout-flip-probability","0",
             "--source-extraction","decoded_flags","--flag-recovery","data","--graph-stars","bare",
             "--output-dir",str(folder)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    manifest=json.loads((folder/"manifest.json").read_text())
    assert manifest["cycle_policy"]=="terminal_chord_flattening"
    assert verify_run(folder)["accepted_outputs_recomputed"]==1
    command[command.index("--output-dir")+1]=str(tmp_path/"invalid")
    command += ["--route","direct_cat"]
    assert subprocess.run(command,capture_output=True,text=True).returncode!=0
