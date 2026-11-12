"""Whole-screen certificate, actual circuit counterexamples and recovery paths."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys

import pytest
from single_cz_controller import SimulationController
from single_cz_runtime import NoiseModel,QuantumBackend
from single_cz_diagnostics import diagnose
from simulate_single_block_cz_depolarizing import simulate,clean_costs
from verify_single_block_cz_run import verify_controller,verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)
OPTIONS=dict(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",
             graph_stars="bare",terminal_policy="screen")


def assert_magic(r,b):
    assert r["accepted"],r.get("reason")
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    manifest={k:r[k] for k in ("profile","history_policy","route","verification_extraction","flag_recovery",
                               "max_flag_recoveries","direct_cz_extraction","graph_stars","terminal_policy","terminal_screen_version")}
    manifest.update(graph={"name":r["graph"]},graph_verification="three_zero_Z_edge_scans")
    verify_controller(r["record"],manifest,True)
    return manifest


def test_all_global_budget_partitions_in_finite_certificate():
    from check_single_cz_terminal_screen import audit
    c=audit()
    assert c["verified"] and c["CX"]==268 and c["physical_measurements"]==100
    assert c["raw_two_upstream_block_cases"]==655360 and c["accepted_two_upstream_cases"]==160
    assert c["accepted_upstream_plus_screen_cases"]==2364
    assert c["accepted_two_screen_signature_pairs"]==14425


@pytest.mark.parametrize("graph",("compact13","current20"))
@pytest.mark.parametrize("stars",("flags","bare"))
def test_clean_factory_counts_and_report_verification(graph,stars):
    options={**OPTIONS,"graph":graph,"graph_stars":stars}
    r,b=simulate(**options)
    manifest=assert_magic(r,b)
    assert r["terminal_screen_outcome"]=="zero_accept"
    c=clean_costs(source_extraction="decoded_flags",flag_recovery="data",graph_stars=stars,terminal_policy="screen")
    expected={('compact13','bare'):2129,('current20','bare'):2299,
              ('compact13','flags'):2273,('current20','flags'):2515}[graph,stars]
    assert c[graph+"/recovery"]["gates"]["CX"]==expected
    assert c[graph+"/recovery"]["T_or_TDG"]==256
    tampered=deepcopy(r["record"])
    next(v for v in tampered if "terminal_screen_begin" in v)["order"].reverse()
    with pytest.raises(AssertionError):verify_controller(tampered,manifest,True)


def test_syndrome_and_false_report_use_matched_full_recovery():
    cases=[[{"context":"terminal_screen/0/Z/5","operation":"PREP","targets":["s"],"timing":"idle","paulis":{"D0":"X"}}],
           [{"context":"terminal_screen/0/Z/5","operation":"MZ","targets":["s"],"timing":"report","flip_report":True}]]
    for faults in cases:
        r,b=simulate(**OPTIONS,injections=faults)
        assert len(b.injected_events)==1
        assert_magic(r,b)
        assert r["terminal_screen_outcome"]=="syndrome_certified"
        h=next(v for v in r["record"] if v.get("history")=="terminal_screen_recovery")
        assert len(h["records"])==3
        checks=[v for v in r["record"] if v.get("check","").startswith("terminal_screen_recovery/")]
        assert checks and all(v["extraction"]=="rolling_flags" for v in checks)


def test_second_fault_during_syndrome_recovery():
    faults=[{"context":"terminal_screen/0/Z/5","operation":"MZ","targets":["s"],"timing":"report","flip_report":True},
            {"context":"terminal_screen_recovery/0/Z/0","operation":"CX","targets":["s","D0"],"paulis":{"D0":"Y"}}]
    r,b=simulate(**OPTIONS,injections=faults)
    assert len(b.injected_events)==2
    assert_magic(r,b)


def test_flag_branch_is_verified_before_output():
    f={"context":"terminal_screen/0/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}
    r,b=simulate(**OPTIONS,injections=[f])
    assert len(b.injected_events)==1 and r["terminal_screen_outcome"]=="flag_verified"
    assert_magic(r,b)
    assert [v["sweep"] for v in r["record"] if "terminal_screen_begin" in v]==[0,1]


def test_two_nonzero_reports_use_bounded_full_fallback():
    faults=[{"context":"terminal_screen/0/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}},
            {"context":"terminal_screen/1/Z/5","operation":"MZ","targets":["s"],"timing":"report","flip_report":True}]
    r,b=simulate(**OPTIONS,injections=faults)
    assert len(b.injected_events)==2 and r["terminal_screen_outcome"]=="full_fallback"
    assert_magic(r,b)


def test_final_idle_pair_still_has_correctable_physical_residual():
    faults=[{"context":"terminal_screen/0/X/4","operation":"MZ","targets":["s"],"timing":"idle","paulis":{q:p}}
            for q,p in (("D0","X"),("D7","Y"))]
    r,b=simulate(**OPTIONS,injections=faults)
    assert len(b.injected_events)==2 and r["terminal_screen_outcome"]=="zero_accept"
    assert_magic(r,b)
    assert diagnose(*b.state.sparse_output(b.data_labels))["raw_physical_target_fidelity"]<1e-10


def naive_counter_faults():
    return [{"context":"final_cycles/0/cycle/0","operation":"CX","targets":["A1","w"],"paulis":{"A1":"X"}},
            {"context":"terminal_screen/0/X/7","operation":"CX","targets":["s","D1"],"paulis":{"s":"Z","D1":"Z"}}]


def test_naive_one_record_order_fails_but_ordered_screen_rejects(monkeypatch):
    import single_cz_terminal_screen as screen
    good_order=screen.screen_checks
    monkeypatch.setattr(screen,"screen_checks",lambda:tuple((a,j) for a in "ZX" for j in range(9)))
    r,b=simulate(**{**OPTIONS,"seed":4},injections=naive_counter_faults())
    assert r["accepted"] and len(b.injected_events)==2 and r["terminal_screen_outcome"]=="zero_accept"
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1/9)
    monkeypatch.setattr(screen,"screen_checks",good_order)
    r,b=simulate(**{**OPTIONS,"seed":4},injections=naive_counter_faults())
    assert len(b.injected_events)==2 and not r["accepted"] and r["reason"]=="data_ambiguity"


def four_fault_conditional_failure():
    specs=[(3489,"gauged/2/code/Z/6",("s","D8"),("X","Y")),
           (5346,"terminal_screen/0/Z/7",("s","f0"),("Y","Z")),
           (6025,"flag_recovery/1/1/X/6",("s","D19"),("Z","Z")),
           (6344,"flag_recovery/1/2/X/4",("s","f0"),("Y","Z"))]
    return [{"event":event,"context":context,"operation":"CX","targets":list(qs),
             "paulis":dict(zip(qs,axes))} for event,context,qs,axes in specs]


def test_four_fault_pilot_failure_is_caught_by_post_recovery_screen():
    # This is OUTSIDE the two-fault theorem. It is a deterministic regression
    # for the observed fidelity failure, not evidence of four-fault FT.
    r,b=simulate(**{**OPTIONS,"seed":1034},injections=four_fault_conditional_failure())
    assert len(b.injected_events)==4
    assert not r["accepted"] and r["reason"]=="data_ambiguity"
    assert len([v for v in r["record"] if "terminal_screen_begin" in v])==2


def test_coherent_two_participant_screen_fault():
    class CoherentFault(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="terminal_screen/0/X/5" and targets==("s","D7"):
                self.state.gate("H","s")
                self.state.gate("T","D7")
                self.used=True
    b=CoherentFault(seed=2,model=ZERO)
    c=SimulationController(b,source_extraction="decoded_flags",flag_recovery="data",graph_stars="bare",terminal_policy="screen")
    r=c.run()
    assert b.used
    if r["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)


def test_screen_CLI_and_saved_run(tmp_path):
    folder=tmp_path/"screen"
    command=[sys.executable,str(Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")),
             "--shots","1","--seed","2","--two-qubit-infidelity","0","--readout-flip-probability","0",
             "--source-extraction","decoded_flags","--flag-recovery","data","--graph-stars","bare",
             "--terminal-policy","screen","--output-dir",str(folder)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    m=json.loads((folder/"manifest.json").read_text())
    assert m["terminal_policy"]=="screen" and m["terminal_screen_version"]==3
    assert verify_run(folder)["accepted_outputs_recomputed"]==1
    command[command.index("--output-dir")+1]=str(tmp_path/"bad")
    command += ["--route","direct_cat"]
    assert subprocess.run(command,capture_output=True,text=True).returncode!=0
