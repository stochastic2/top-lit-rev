"""Persistent gauging: global-budget physical regressions and report audits."""
from copy import deepcopy
from pathlib import Path
import json,subprocess,sys
import pytest

from single_cz_persistent import PERSISTENT_GRAPHS,TREE4
from single_cz_controller import SimulationController
from single_cz_runtime import NoiseModel,QuantumBackend
from single_cz_diagnostics import diagnose
from simulate_single_block_cz_depolarizing import simulate,clean_costs
from verify_single_block_cz_run import verify_controller,verify_run
from check_single_cz_persistent import root_certificate,ideal_records,naive_root_counterexample,fused_certificate

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)


def options(graph="tree4",**extra):
    return dict(seed=2,model=ZERO,graph=graph,source_extraction="decoded_flags",flag_recovery="data",
                graph_stars="bare",terminal_policy="intrinsic",data_checks="compact_flags",gauss_frame="persistent",**extra)


def assert_target(r,b):
    assert r["accepted"],r.get("reason")
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    manifest={k:r[k] for k in ("profile","history_policy","route","verification_extraction","flag_recovery",
            "max_flag_recoveries","direct_cz_extraction","graph_stars","terminal_policy","data_checks","gauss_frame")}
    manifest.update(graph={"name":r["graph"]},graph_verification="three_zero_Z_edge_scans")
    verify_controller(r["record"],manifest,True)
    return manifest


@pytest.mark.parametrize("graph",tuple(PERSISTENT_GRAPHS))
def test_local_opaque_cones_all_ideal_records_and_clean_factory(graph):
    assert root_certificate(PERSISTENT_GRAPHS[graph])["zero_flag_data_support_per_fault"]==1
    assert fused_certificate(PERSISTENT_GRAPHS[graph])["gates"]["T"]==20
    assert ideal_records(PERSISTENT_GRAPHS[graph])["positive_probability"]=="3/4"
    r,b=simulate(**options(graph));assert_target(r,b)
    assert len([s for s in r["record"] if s.get("persistent_coordinates_entered")])==1
    assert not any("edge_reports" in s or "final_cycle_flattening" in s or "terminal_screen_begin" in s for s in r["record"])


def test_old_root_in_new_frame_cannot_certify_negative_branch():
    assert naive_root_counterexample()["positive_probability_on_genuine_negative_logical_11"]=="3/4"


@pytest.mark.parametrize("graph",("tree4","compact13"))
def test_two_false_root_reports_cannot_retain_genuine_negative(graph):
    faults=[{"context":f"persistent/{j}/transported_Gauss","operation":"MZ","targets":["s"],
             "timing":"report","flip_report":True} for j in range(2)]
    opts=options(graph);opts["seed"]=0
    r,b=simulate(**opts,injections=faults)
    assert len(b.injected_events)==2 and not r["accepted"]
    assert r["reason"]=="insufficient_positive_persistent_rounds"


@pytest.mark.parametrize("graph",("tree4","compact13"))
def test_two_late_data_faults_without_terminal_screen_are_correctable(graph):
    faults=[{"context":"persistent/2/transported_Gauss","operation":"CX","targets":["s","A0"],
             "timing":"idle","paulis":{q:p}} for q,p in (("D0","X"),("D19","Y"))]
    r,b=simulate(**options(graph),injections=faults)
    assert len(b.injected_events)==2;assert_target(r,b)
    assert diagnose(*b.state.sparse_output(b.data_labels))["raw_physical_target_fidelity"]<1e-10


def test_wrong_graph_disposal_reports_do_not_invoke_any_byproduct():
    faults=[{"context":"persistent/discard_graph","operation":"MZ","targets":[f"A{j}"],
             "timing":"report","flip_report":True} for j in (0,1)]
    r,b=simulate(**options(),injections=faults)
    assert len(b.injected_events)==2;assert_target(r,b)


def test_broad_graph_star_hooks_are_not_charged_as_data_faults():
    faults=[{"context":"persistent/0/star/1","operation":"CX","targets":["s","A0"],"paulis":{"s":"X"}},
            {"context":"persistent/1/star/2","operation":"CX","targets":["s","A1"],"paulis":{"s":"X"}}]
    r,b=simulate(**options("compact13"),injections=faults)
    assert len(b.injected_events)==2;assert_target(r,b)


def test_initial_coordinate_controller_and_compact_hook_share_two_faults():
    faults=[{"context":"persistent/fused_initial","operation":"CX","targets":["A0","D4"],"paulis":{"A0":"X"}},
            {"context":"persistent/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}]
    r,b=simulate(**options(),injections=faults)
    assert len(b.injected_events)==2
    if r["accepted"]:assert_target(r,b)
    else:assert r["reason"].startswith(("flag_data_","data_","insufficient_positive_","verification_flag:"))


def test_data_hook_flag_recovery_and_faulty_fallback():
    faults=[{"context":"persistent/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}},
            {"context":"flag_recovery/0/0/Z/0","operation":"CX","targets":["s","D0"],"paulis":{"D0":"Y"}}]
    r,b=simulate(**options(),injections=faults)
    assert len(b.injected_events)==2 and r["successful_flag_recoveries"]==1;assert_target(r,b)


def test_root_flag_rejects_and_is_not_sent_to_pauli_data_decoder():
    fault={"context":"persistent/0/transported_Gauss","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}
    r,b=simulate(**options(),injections=[fault])
    assert len(b.injected_events)==1 and not r["accepted"]
    assert r["reason"]=="verification_flag:persistent/0/transported_Gauss"


def test_coherent_joint_meter_graph_fault_after_data_ports():
    class Coherent(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="persistent/0/transported_Gauss" and targets==("s","A0"):
                self.state.gate("H","s");self.state.gate("T","A0");self.used=True
    b=Coherent(seed=2,model=ZERO)
    c=SimulationController(b,graph=TREE4,source_extraction="decoded_flags",flag_recovery="data",
        graph_stars="bare",terminal_policy="intrinsic",data_checks="compact_flags",gauss_frame="persistent")
    r=c.run();assert b.used
    assert r["accepted"],r.get("reason")
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)


def test_output_certificate_cannot_drop_positive_rounds_or_add_a_byproduct():
    r,b=simulate(**options());manifest=assert_target(r,b)
    for kind in ("round","byproduct"):
        rows=deepcopy(r["record"])
        if kind=="round":rows.remove(next(s for s in rows if "passing_persistent_round" in s))
        else:next(s for s in rows if s.get("persistent_graph_discard"))["data_byproduct"]="apply U_eta again"
        with pytest.raises(AssertionError):verify_controller(rows,manifest,True)


def test_tree_costs_and_old_modes_remain_available():
    costs=clean_costs("decoded_flags","flags","cat","data","bare","intrinsic","compact_flags","persistent")
    assert [(costs[n+"/recovery"]["gates"]["CX"],costs[n+"/recovery"]["T_or_TDG"],costs[n+"/recovery"]["peak_live"])
            for n in ("compact13","current20","tree4")]==[(1574,160,39),(1693,160,46),(1421,160,30)]
    old=clean_costs("decoded_flags","flags","cat","data","bare","screen","compact_flags")
    assert old["compact13/recovery"]["gates"]["CX"]==1889 and old["direct_cat/recovery"]["gates"]["CX"]==1476


def test_cli_tree_graph_snapshot_and_report_verification(tmp_path):
    folder=tmp_path/"tree"
    command=[sys.executable,str(Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")),
             "--shots","1","--seed","2","--two-qubit-infidelity","0","--readout-flip-probability","0",
             "--source-extraction","decoded_flags","--flag-recovery","data","--graph-stars","bare",
             "--terminal-policy","intrinsic","--data-checks","compact_flags","--gauss-frame","persistent",
             "--graph","tree4","--output-dir",str(folder)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    manifest=json.loads((folder/"manifest.json").read_text())
    assert manifest["cut_distance"]==1 and manifest["edge_decode_radius"] is None
    assert manifest["cycle_policy"]=="unfixed_and_discarded" and manifest["terminal_policy"]=="intrinsic_persistent_tail"
    assert "single_cz_persistent.py" in manifest["source_sha256"]
    assert verify_run(folder)["accepted_outputs_recomputed"]==1
    command[command.index("--output-dir")+1]=str(tmp_path/"invalid")
    command[command.index("--gauss-frame")+1]="round_trip"
    bad=subprocess.run(command,capture_output=True,text=True)
    assert bad.returncode!=0 and "require --gauss-frame persistent" in bad.stderr
