"""Flag-conditioned tables, physical faults, history invalidation and CLI."""
from pathlib import Path
from copy import deepcopy
import json
import subprocess
import sys

import pytest
import c4_helix_single_block_cz as m
from single_cz_flag_recovery import decision, recovery_table
from single_cz_runtime import QuantumBackend, NoiseModel
from single_cz_controller import SimulationController
from single_cz_diagnostics import diagnose
from simulate_single_block_cz_depolarizing import simulate, clean_costs
from verify_single_block_cz_run import verify_controller, verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)


def assert_target(result, backend):
    assert result["accepted"], result.get("reason")
    assert diagnose(*backend.state.sparse_output(backend.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    manifest={k:result[k] for k in ("profile","history_policy","route","verification_extraction",
                                  "flag_recovery","max_flag_recoveries","direct_cz_extraction")}
    manifest.update(graph={"name":result["graph"]},graph_verification="three_zero_Z_edge_scans")
    verify_controller(result["record"],manifest,True)


@pytest.mark.parametrize("axis",("X","Z"))
@pytest.mark.parametrize("support",(m.SUPPORTS[0],m.SUPPORTS[5]))
def test_independent_clifford_and_class_certificate(axis,support):
    from check_single_cz_flag_recovery import check_shape
    result=check_shape(axis,support)
    assert result["accepted_syndrome_decisions"]>0
    assert result["ambiguous_syndrome_decisions"]>0


def test_zero_syndrome_can_be_logically_ambiguous():
    assert decision("X",m.SUPPORTS[5],24,[0]*18)=={"classes":2,"correction":None}
    assert decision("X",m.SUPPORTS[0],1,[0]*18)=={"classes":1,"correction":(0,0)}
    with pytest.raises(ValueError):recovery_table("W",m.SUPPORTS[0],1)
    with pytest.raises(ValueError):recovery_table("X",m.X0,1)
    with pytest.raises(ValueError):recovery_table("X",m.SUPPORTS[0],0)


@pytest.mark.parametrize("route,graph",(("gauging","compact13"),("gauging","current20"),("direct_cat","compact13")))
def test_controller_hook_is_recovered_with_matched_cat_option(route,graph):
    prefix="gauged/0/code" if route=="gauging" else "terminal/0"
    fault={"context":prefix+"/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}
    options=dict(seed=2,model=ZERO,source_extraction="decoded_flags",route=route,graph=graph,
                 direct_cz_extraction="cat" if route=="direct_cat" else "auto",injections=[fault])
    strict,_=simulate(**options)
    assert not strict["accepted"] and strict["reason"].startswith("verification_flag:")
    result,b=simulate(**options,flag_recovery="data")
    assert len(b.injected_events)==1 and result["successful_flag_recoveries"]==1
    assert_target(result,b)
    if route=="gauging" and graph=="compact13":
        tampered=deepcopy(result["record"])
        repair=next(row for row in tampered if "flag_data_recovery" in row)
        repair["correction"][0]^=1
        manifest={k:result[k] for k in ("profile","history_policy","route","verification_extraction",
                                      "flag_recovery","max_flag_recoveries","direct_cz_extraction")}
        manifest.update(graph={"name":graph},graph_verification="three_zero_Z_edge_scans")
        with pytest.raises(AssertionError):verify_controller(tampered,manifest,True)


def test_second_fault_during_fallback_is_in_the_same_global_budget():
    faults=[{"context":"gauged/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}},
            {"context":"flag_recovery/0/0/Z/0","operation":"CX","targets":["s","D0"],"paulis":{"D0":"Y"}}]
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",injections=faults)
    assert len(b.injected_events)==2
    assert_target(result,b)


def test_two_separate_flagged_episodes_and_configurable_bound():
    faults=[{"context":"gauged/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}},
            {"context":"gauged/1/code/Z/5","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True}]
    options=dict(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",injections=faults)
    result,b=simulate(**options,max_flag_recoveries=8)
    assert len(b.injected_events)==2 and result["successful_flag_recoveries"]==2
    assert_target(result,b)
    result,b=simulate(**options,max_flag_recoveries=1)
    assert not result["accepted"] and result["reason"]=="flag_recovery_limit"


def test_one_remaining_fault_gadget_is_not_used_as_a_two_fault_gadget():
    from check_optimized_extraction import signatures
    from single_cz_flagged import single_fault_pauli_program
    sigs,_=signatures(single_fault_pauli_program("X",8),range(8),255,1)
    def cost(x,z):return min((x | z).bit_count(),((x ^ 255) | z).bit_count())
    assert all(f or cost(x,z)<=1 for x,z,f in sigs)
    assert any(f==g and cost(x ^ a,z ^ b)>2 for x,z,f in sigs for a,b,g in sigs)


def test_terminal_flag_restarts_whole_row_and_invalidates_old_history():
    fault={"context":"terminal/1/Z/5","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True}
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",injections=[fault])
    assert len(b.injected_events)==1
    assert_target(result,b)
    reset=next(r for r in result["record"] if r.get("history_reset")=="terminal_recovery")
    assert len(reset["discarded_records"])==1 and reset["old_epoch"]==0 and reset["new_epoch"]==1
    history=next(r for r in result["record"] if r.get("history")=="terminal_recovery")
    assert len(history["records"])==3


def test_flags_during_fallback_and_nonpauli_checks_still_reject():
    first={"context":"gauged/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}
    second={"context":"flag_recovery/0/0/Z/0","operation":"MZ","targets":["f0"],"timing":"report","flip_report":True}
    result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",injections=[first,second])
    assert not result["accepted"] and result["reason"].startswith("verification_flag:flag_recovery/")
    assert len(b.injected_events)==2
    for context,target in (("gauged/0/root_Gauss","D0"),("gauged/0/star/1","A0")):
        fault={"context":context,"operation":"CX","targets":["s",target],"paulis":{"s":"X"}}
        result,b=simulate(seed=2,model=ZERO,source_extraction="decoded_flags",flag_recovery="data",injections=[fault])
        assert not result["accepted"] and result["reason"].startswith("verification_flag:")


def test_coherent_two_participant_fault_preserves_magic_on_accepted_paths():
    class CoherentFault(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="gauged/0/code/X/5" and targets==("s","D7"):
                # One arbitrary two-qubit location action. Do not sample this
                # H_s T_D7 error as a mixture of Paulis.
                self.state.gate("H","s")
                self.state.gate("T","D7")
                self.used=True
    recovered=0
    for seed in range(6):
        b=CoherentFault(seed=seed,model=ZERO)
        c=SimulationController(b,source_extraction="decoded_flags",flag_recovery="data")
        result=c.run()
        assert b.used
        if result["accepted"]:
            assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
            recovered+=c.data_epoch>0
    assert recovered


def test_clean_schedule_unchanged_and_cli_saves_policy(tmp_path):
    for mode in ("reject","data"):
        costs=clean_costs(source_extraction="decoded_flags",flag_recovery=mode)
        assert costs["compact13/recovery"]["gates"]["CX"]==2809
    directory=tmp_path/"saved"
    command=[sys.executable,str(Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")),
             "--shots","1","--seed","2","--two-qubit-infidelity","0","--readout-flip-probability","0",
             "--flag-recovery","data","--source-extraction","decoded_flags","--output-dir",str(directory)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    assert json.loads((directory/"manifest.json").read_text())["flag_recovery"]=="data"
    assert verify_run(directory)["accepted_outputs_recomputed"]==1
    # The new policy cannot silently be requested with cat verification.
    command[command.index("--output-dir")+1]=str(tmp_path/"invalid")
    command += ["--verification-extraction","cats"]
    assert subprocess.run(command,capture_output=True,text=True).returncode!=0
