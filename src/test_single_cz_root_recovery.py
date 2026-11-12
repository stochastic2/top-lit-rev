"""Graph-assisted root recovery, direct control, shared dual fallbacks."""
from pathlib import Path
from copy import deepcopy
from itertools import product
import json,subprocess,sys
import pytest

import c4_helix_single_block_cz as m
from single_cz_controller import SimulationController
from single_cz_runtime import QuantumBackend,NoiseModel
from single_cz_diagnostics import diagnose
from single_cz_recovery import COMPACT13
from single_cz_root_recovery import AffineSpan,decision
from check_single_cz_root_recovery import verify_space,phase_certificate,dual_certificate
from simulate_single_block_cz_depolarizing import simulate
from verify_single_block_cz_run import verify_controller,verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)
WITNESS={"context":"gauged/0/root_Gauss","operation":"CX","targets":["s","A0"],"paulis":{"s":"X","A0":"X"}}


def options(**extra):
    opts=dict(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",
              terminal_policy="screen",data_checks="compact_flags",conditional_checks="dual_flags",root_recovery="joint")
    opts.update(extra);return opts


def assert_target(r,b):
    assert r["accepted"],r.get("reason")
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    keys=("profile","history_policy","route","verification_extraction","flag_recovery","max_flag_recoveries",
          "direct_cz_extraction","graph_stars","terminal_policy","terminal_screen_version","data_checks",
          "gauss_frame","conditional_checks","root_recovery")
    manifest={k:r[k] for k in keys};manifest.update(graph={"name":r["graph"]},graph_verification="three_zero_Z_edge_scans")
    verify_controller(r["record"],manifest,True)
    return manifest


def test_graph_information_changes_a_physical_recovery_decision():
    outcomes={}
    for mode in ("reject","data","joint"):
        r,b=simulate(**options(root_recovery=mode),injections=[WITNESS])
        assert len(b.injected_events)==1;outcomes[mode]=r
        if r["accepted"]:assert_target(r,b)
    assert outcomes["reject"]["reason"].startswith("verification_flag:")
    assert outcomes["data"]["reason"]=="root_data_ambiguous"
    r=outcomes["joint"]
    assert r["accepted"] and r["successful_root_recoveries"]==1
    entry=next(row for row in r["record"] if "root_data_recovery" in row)
    assert entry["flag_word"]==48 and entry["syndrome"]==[0]*31
    assert entry["decision"]["correction"]==(0,0)
    rounds=[row for row in r["record"] if "passing_gauged_round" in row]
    assert rounds[0]["passing"] is False and rounds[-1]["passes"]==3


def test_affine_report_solver_including_a_logical_kernel():
    logical=sum(1 << q for q in m.X0)
    for generators in ((1,1 << 20,16,16 << 20),(1,1 << 20,logical)):
        space=AffineSpan.create(3,generators)
        rank,images,reports=verify_space(space)
        assert images==1 << rank and reports>0
    assert phase_certificate()["Pauli_XOR_through_T"] is False
    assert all(row["H"]==2 for row in dual_certificate())


@pytest.mark.parametrize("second",[
    {"context":"coordinates/V","operation":"CX","targets":["A1","D8"],"paulis":{"A1":"X"},"occurrence":2},
    {"context":"root_recovery/0/0/cycle/0","operation":"MZ","targets":["w"],"timing":"report","flip_report":True},
    {"context":"root_recovery/0/0/cycle/0","operation":"MZ","targets":["w"],"timing":"idle","paulis":{"D8":"Y"}},
    {"context":"root_recovery/0/0/star/1","operation":"CX","targets":["s","A0"],"paulis":{"s":"X"}},
])
def test_second_fault_is_in_the_same_global_budget(second):
    r,b=simulate(**options(),injections=[WITNESS,second])
    assert len(b.injected_events)==2
    if r["accepted"]:assert_target(r,b)
    else:assert r["reason"].startswith(("root_data_","verification_flag:","insufficient_positive_","data_"))


def test_wrong_cycle_report_requires_a_fresh_matching_pair():
    second={"context":"root_recovery/0/0/cycle/0","operation":"MZ","targets":["w"],"timing":"report","flip_report":True}
    r,b=simulate(**options(),injections=[WITNESS,second]);assert_target(r,b)
    history=next(row for row in r["record"] if "root_recovery_history" in row)
    assert len(history["records"])==3


def test_a_second_flag_in_conditional_recovery_rejects():
    second={"context":"root_recovery/0/0/code/Z/0","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True}
    r,b=simulate(**options(),injections=[WITNESS,second])
    assert len(b.injected_events)==2 and not r["accepted"]
    assert r["reason"].startswith("verification_flag:root_recovery/")


def test_two_flagged_roots_leave_three_good_rounds_and_share_the_cap():
    faults=[{"context":f"gauged/{j}/root_Gauss","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True} for j in range(2)]
    r,b=simulate(**options(),injections=faults)
    assert len(b.injected_events)==2 and r["successful_root_recoveries"]==2;assert_target(r,b)
    assert len([row for row in r["record"] if "passing_gauged_round" in row])==5
    r,b=simulate(**options(max_flag_recoveries=1),injections=faults)
    assert not r["accepted"] and r["reason"]=="flag_recovery_limit"


def test_negative_branch_is_not_repaired_into_magic():
    fault={"context":"gauged/0/root_Gauss","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True}
    r,b=simulate(**options(seed=0),injections=[fault])
    assert len(b.injected_events)==1 and not r["accepted"]
    assert r["reason"]=="insufficient_positive_gauged_rounds"


def test_late_terminal_fault_after_a_recovered_root_is_correctable():
    second={"context":"terminal_screen/0/X/4","operation":"MZ","targets":["s"],"timing":"idle","paulis":{"D19":"Y"}}
    r,b=simulate(**options(),injections=[WITNESS,second])
    assert len(b.injected_events)==2;assert_target(r,b)
    assert diagnose(*b.state.sparse_output(b.data_labels))["raw_physical_target_fidelity"]<1e-10


def test_coherent_graph_phase_and_controller_fault_retains_complex_amplitudes():
    class Coherent(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="gauged/0/root_Gauss" and targets==("s","A0"):
                self.state.gate("X","s");self.state.gate("X","A0");self.state.gate("T","A0");self.used=True
    b=Coherent(seed=2,model=ZERO);opts=options();opts.pop("model");opts.pop("seed")
    r=SimulationController(b,**opts).run()
    assert b.used and r["accepted"],r.get("reason")
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)


def test_shared_dual_conditional_gadget_saves_208_H_on_cat_flag_repair():
    fault={"context":"terminal/0/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}
    rows={}
    for variant in ("legacy","dual_flags"):
        r,b=simulate(**options(route="direct_cat",direct_cz_extraction="cat",graph_stars="flags",terminal_policy="certified",
                              root_recovery="reject",conditional_checks=variant),injections=[fault])
        assert_target(r,b);rows[variant]=r
    assert rows["legacy"]["metrics"]["gate_counts"]["H"]-rows["dual_flags"]["metrics"]["gate_counts"]["H"]==208
    assert rows["legacy"]["metrics"]["gate_counts"]["CX"]==rows["dual_flags"]["metrics"]["gate_counts"]["CX"]


def test_direct_global_flagged_control_has_the_same_conservative_recovery():
    fault={"context":"terminal/0/U","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True}
    r,b=simulate(**options(seed=0,route="direct_cat",graph_stars="flags",terminal_policy="certified",root_recovery="data"),injections=[fault])
    assert len(b.injected_events)==1 and r["successful_root_recoveries"]==1;assert_target(r,b)


def test_recovery_certificates_reject_tampered_cycles_or_retained_root_vote():
    r,b=simulate(**options(),injections=[WITNESS]);manifest=assert_target(r,b)
    for kind in ("cycle","vote"):
        rows=deepcopy(r["record"])
        if kind=="cycle":next(s for s in rows if "root_data_recovery" in s)["syndrome"][18]^=1
        else:next(s for s in rows if "root_flag_recovery" in s and "passing_gauged_round" in s)["passing"]=True
        with pytest.raises(AssertionError):verify_controller(rows,manifest,True)


def test_cli_saves_modes_and_rejects_incompatible_global_cat_option(tmp_path):
    folder=tmp_path/"joint"
    command=[sys.executable,str(Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")),
             "--shots","1","--seed","2","--two-qubit-infidelity","0","--readout-flip-probability","0",
             "--source-extraction","decoded_flags","--flag-recovery","data","--graph-stars","bare",
             "--terminal-policy","screen","--data-checks","compact_flags","--conditional-checks","dual_flags",
             "--root-recovery","joint","--output-dir",str(folder)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    manifest=json.loads((folder/"manifest.json").read_text())
    assert manifest["root_recovery"]=="joint" and manifest["conditional_checks"]=="dual_flags"
    assert "single_cz_root_recovery.py" in manifest["source_sha256"]
    assert verify_run(folder)["accepted_outputs_recomputed"]==1
    command[command.index("--output-dir")+1]=str(tmp_path/"invalid")
    command[command.index("--graph-stars")+1]="flags"
    command[command.index("--terminal-policy")+1]="certified"
    command += ["--route","direct_cat","--direct-cz-extraction","cat"]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode!=0 and "Root recovery requires" in result.stderr
