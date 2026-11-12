"""Compact physical checks: local cones, exact regrouping and factory recovery."""
from pathlib import Path
import json
import subprocess
import sys
import pytest

from check_single_cz_compact_checks import local_certificate,dense_instrument,outer_omission_witnesses
from single_cz_state import CoherentState,ZERO
from single_cz_runtime import NoiseModel,QuantumBackend
from single_cz_controller import SimulationController
from single_cz_diagnostics import diagnose
from simulate_single_block_cz_depolarizing import simulate,clean_costs
from verify_single_block_cz_run import verify_controller,verify_run

ZERO_NOISE=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)


def options(route="gauging",graph="compact13"):
    return dict(seed=2,model=ZERO_NOISE,source_extraction="decoded_flags",route=route,graph=graph,
                flag_recovery="data",data_checks="compact_flags",
                graph_stars="bare" if route=="gauging" else "flags",
                terminal_policy="screen" if route=="gauging" else "certified",
                direct_cz_extraction="cat" if route=="direct_cat" else "auto")


def assert_target(result,backend):
    assert result["accepted"],result.get("reason")
    assert diagnose(*backend.state.sparse_output(backend.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    manifest={k:result[k] for k in ("profile","history_policy","route","verification_extraction",
                                   "flag_recovery","max_flag_recoveries","direct_cz_extraction",
                                   "graph_stars","terminal_policy","terminal_screen_version","data_checks")}
    manifest["graph"]={"name":result["graph"]}
    verify_controller(result["record"],manifest,True)


@pytest.mark.parametrize("axis",("X","Z"))
@pytest.mark.parametrize("n",(4,8))
def test_all_local_zero_flag_fault_signatures(axis,n):
    certificate=local_certificate(axis,n)
    assert certificate["gates"]["CX"]==(6 if n==4 else 16)
    assert certificate["accepted_signature_pairs"]>0
    assert dense_instrument(axis,n)["maximum_absolute_error"]<1e-12


def exact_amplitudes(state,labels):
    result={}
    for (word,fid),coefficient in state.terms.items():
        factor=state.store.factors[fid]
        for index,phase in zip(factor.indices,factor.phases):
            bits={q:(word >> j)&1 for j,q in enumerate(state.basis_labels)}
            bits.update({q:(int(index) >> j)&1 for j,q in enumerate(factor.labels)})
            key=sum(bits[q] << j for j,q in enumerate(labels))
            result[key]=result.get(key,ZERO)+coefficient.rotate(int(phase))
    return {k:v for k,v in result.items() if v}


def test_helper_tensor_regrouping_preserves_complex_entanglement_exactly():
    def prepare():
        state=CoherentState(("D0","D1"))
        state.gate("H","D0");state.gate("T","D0")
        for q in ("a","b"):state.allocate(q);state.gate("H",q)
        state.gate("CX","a","D1");state.gate("TDG","b")
        return state
    state,reference=prepare(),prepare();labels=("D0","D1","a","b")
    state.absorb_basis_label("a")
    assert exact_amplitudes(state,labels)==exact_amplitudes(reference,labels)
    for op,qs in (("CX",("D0","a")),("CX",("b","a")),("Z",("a",)),("H",("b",))):
        state.gate(op,*qs);reference.gate(op,*qs)
        assert exact_amplitudes(state,labels)==exact_amplitudes(reference,labels)
    for outcome in (0,1):
        assert state.norm(state.measurement_branch("a",outcome))==reference.norm(reference.measurement_branch("a",outcome))


@pytest.mark.parametrize("route,graph",(("gauging","compact13"),("gauging","current20"),("direct_cat","compact13")))
def test_clean_factories_and_old_ordered_screen_are_retained(route,graph):
    r,b=simulate(**options(route,graph));assert_target(r,b)
    compact=[row for row in r["record"] if row.get("extraction")=="compact_flags"]
    assert compact and all(not row["check"].startswith(("source/","terminal_screen/","flag_recovery/")) for row in compact)
    if route=="gauging":
        assert len([row for row in r["record"] if row.get("check","").startswith("terminal_screen/") and row.get("extraction")=="rolling_flags"])==18


@pytest.mark.parametrize("axis",("X","Z"))
@pytest.mark.parametrize("route",("gauging","direct_cat"))
def test_weight_four_controller_hook_uses_new_flag_table(axis,route):
    prefix="gauged/0/code" if route=="gauging" else "terminal/0"
    qs=["s","D7"] if axis=="X" else ["D7","s"]
    fault={"context":prefix+f"/{axis}/5","operation":"CX","targets":qs,
           "paulis":{"s":"X" if axis=="X" else "Z"}}
    r,b=simulate(**options(route),injections=[fault])
    assert len(b.injected_events)==1 and r["successful_flag_recoveries"]==1
    assert_target(r,b)
    repair=next(row for row in r["record"] if "flag_data_recovery" in row)
    assert repair["trigger_extraction"]=="compact_flags"


def test_hook_and_fault_in_conditional_recovery_share_global_budget():
    faults=[{"context":"gauged/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}},
            {"context":"flag_recovery/0/0/Z/0","operation":"CX","targets":["s","D0"],"paulis":{"D0":"Y"}}]
    r,b=simulate(**options(),injections=faults)
    assert len(b.injected_events)==2;assert_target(r,b)


def test_enrichment_block_fault_and_compact_hook_share_global_budget():
    faults=[{"context":"enrichment","operation":"CX","targets":["a2","D8"],"paulis":{"a2":"X"}},
            {"context":"gauged/0/code/X/5","operation":"CX","targets":["s","D7"],"paulis":{"s":"X"}}]
    r,b=simulate(**options(),injections=faults)
    assert len(b.injected_events)==2 and r["successful_flag_recoveries"]==1
    assert_target(r,b)


def test_coherent_controller_fault_is_retained_as_a_superposition():
    class CoherentFault(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="gauged/0/code/X/5" and targets==("s","D7"):
                self.state.gate("H","s");self.state.gate("T","D7");self.used=True
    backend=CoherentFault(seed=2,model=ZERO_NOISE)
    opts=options();opts.pop("seed");opts.pop("model");opts.pop("direct_cz_extraction");opts.pop("graph")
    result=SimulationController(backend,**opts).run()
    assert backend.used
    if result["accepted"]:
        assert diagnose(*backend.state.sparse_output(backend.data_labels))["decoded_target_fidelity"]==pytest.approx(1,abs=1e-10)
    else:assert result["reason"].startswith(("flag_data_","insufficient_positive_","verification_flag:"))


def test_no_static_outer_check_can_be_dropped_under_current_block_envelope():
    assert len(outer_omission_witnesses()["each_single_outer_omission_fails_existing_zero_accept_contract"])==8


def test_clean_costs_match_physical_programs():
    c=clean_costs("decoded_flags","flags","cat","data","bare","screen","compact_flags")
    assert (c["compact13/recovery"]["gates"]["CX"],c["current20/recovery"]["gates"]["CX"],c["direct_cat/recovery"]["gates"]["CX"])==(1889,2059,1476)
    assert (c["compact13/recovery"]["gates"]["H"],c["direct_cat/recovery"]["gates"]["H"])==(803,686)


def test_cli_snapshot_and_nonzero_flag_ledger_verification(tmp_path):
    folder=tmp_path/"compact"
    command=[sys.executable,str(Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")),
             "--shots","1","--seed","2","--two-qubit-infidelity","0","--readout-flip-probability","0",
             "--source-extraction","decoded_flags","--flag-recovery","data","--graph-stars","bare",
             "--terminal-policy","screen","--data-checks","compact_flags","--output-dir",str(folder)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=40)
    manifest=json.loads((folder/"manifest.json").read_text())
    assert manifest["data_checks"]=="compact_flags"
    assert "single_cz_compact_checks.py" in manifest["source_sha256"]
    assert verify_run(folder)["accepted_outputs_recomputed"]==1
    command += ["--verification-extraction","cats"]
    assert subprocess.run(command,capture_output=True,text=True).returncode!=0
