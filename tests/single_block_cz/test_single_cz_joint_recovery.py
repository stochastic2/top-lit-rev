"""Global-budget quantum regressions for conditional joint code/cycle recovery."""
from copy import deepcopy
from collections import Counter
from pathlib import Path
import json,subprocess,sys
import pytest
from simulate_single_block_cz_depolarizing import simulate,clean_costs
from single_cz_runtime import NoiseModel,QuantumBackend
from single_cz_controller import SimulationController
from single_cz_diagnostics import diagnose
from single_cz_joint_recovery import decision_word
from single_cz_recovery import COMPACT13,data_table
from verify_single_block_cz_run import verify_controller,verify_run

ZERO=NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)
WITNESS={'context':'coordinates/V','operation':'CX','targets':['A0','D5'],'paulis':{'A0':'X'}}

def options(**extra):
    o=dict(seed=2,model=ZERO,source_extraction='decoded_flags',flag_recovery='data',graph_stars='bare',
           terminal_policy='screen',data_checks='compact_flags',conditional_checks='dual_flags',root_recovery='joint',joint_recovery='fallback')
    o.update(extra);return o

def assert_target(r,b):
    assert r['accepted'],r.get('reason')
    assert diagnose(*b.state.sparse_output(b.data_labels))['decoded_target_fidelity']==pytest.approx(1)
    keys=('profile','history_policy','route','verification_extraction','flag_recovery','max_flag_recoveries',
          'direct_cz_extraction','graph_stars','terminal_policy','terminal_screen_version','data_checks',
          'gauss_frame','graph_z_corrections','root_recovery','conditional_checks','joint_recovery')
    manifest={k:r[k] for k in keys};manifest['graph']={'name':r['graph']}
    verify_controller(r['record'],manifest,True)
    verify_controller(json.loads(json.dumps(r['record'])),manifest,True)
    return manifest

@pytest.mark.parametrize('graph,edge,diagnostic_cx,diagnostic_mz',[
    ('compact13',0,330,90),('current20',7,356,104)])
def test_one_coordinate_fault_is_recovered_where_old_decoder_rejects(graph,edge,diagnostic_cx,diagnostic_mz):
    witness=deepcopy(WITNESS);witness['targets']=[f'A{edge}','D5'];witness['paulis']={f'A{edge}':'X'}
    old,b=simulate(**options(joint_recovery='off',graph=graph),injections=[witness])
    assert not old['accepted'] and old['reason']=='data_ambiguity'
    events=[]
    r,b=simulate(**options(graph=graph),injections=[witness],trace=events.append);assert_target(r,b)
    assert len(b.injected_events)==1 and r['successful_joint_recoveries']==1
    row=next(row for row in r['record'] if 'joint_graph_data_history' in row)
    assert len(row['records'])==2
    assert r['successful_flag_recoveries']==0
    diagnostic=Counter(e['operation'] for e in events if e['kind']=='physical' and '/joint/' in e['context']
                       and not e['context'].endswith('/correction'))
    assert diagnostic==dict(CX=diagnostic_cx,H=72,PREP=diagnostic_mz,MZ=diagnostic_mz)

def test_two_coordinate_control_faults_share_the_same_global_budget():
    other={'context':'coordinates/V','operation':'CX','targets':['A1','D9'],'paulis':{'A1':'X'}}
    r,b=simulate(**options(),injections=[WITNESS,other]);assert_target(r,b)
    assert len(b.injected_events)==2

def test_one_arbitrary_local_coherent_fault_retains_complex_amplitudes():
    class Coherent(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=='coordinates/V' and name=='CX' and targets==('A0','D5'):
                self.state.gate('X','A0');self.state.gate('T','A0');self.used=True
    b=Coherent(seed=2,model=ZERO);opts=options();opts.pop('model');opts.pop('seed')
    c=SimulationController(b,**opts);r=c.run()
    assert b.used and r['accepted'],r.get('reason')
    assert c.successful_joint_recoveries==1
    assert diagnose(*b.state.sparse_output(b.data_labels))['decoded_target_fidelity']==pytest.approx(1)

@pytest.mark.parametrize('second',[
    {'context':'gauged/0/data_recovery/joint/0/cycle/0','operation':'MZ','targets':['w'],'timing':'report','flip_report':True},
    {'context':'gauged/0/data_recovery/joint/1/cycle/8','operation':'MZ','targets':['w'],'timing':'idle','paulis':{'D19':'Y'}},
])
def test_wrong_report_or_late_data_fault_is_not_a_fresh_budget(second):
    r,b=simulate(**options(),injections=[WITNESS,second]);assert_target(r,b)
    assert len(b.injected_events)==2

def test_new_flag_rejects_and_negative_branch_is_not_repaired_positive():
    flag={'context':'gauged/0/data_recovery/joint/0/code/Z/0','operation':'MZ','targets':['f0'],'timing':'report','flip_report':True}
    r,b=simulate(**options(),injections=[WITNESS,flag])
    assert not r['accepted'] and r['reason'].startswith('verification_flag:') and len(b.injected_events)==2
    r,b=simulate(**options(seed=0),injections=[WITNESS])
    assert not r['accepted']

def test_tampered_trigger_history_cycle_and_correction_are_rejected():
    r,b=simulate(**options(),injections=[WITNESS]);manifest=assert_target(r,b)
    for kind in ('trigger','history','cycle','correction'):
        rows=deepcopy(r['record'])
        if kind=='trigger':next(x for x in rows if 'joint_recovery_begin' in x)['certified_nonzero_data']=[0]*18
        elif kind=='history':next(x for x in rows if 'joint_graph_data_history' in x)['records'][0][18]^=1
        elif kind=='cycle':next(x for x in rows if x.get('decoder')=='joint_graph_data')['joint_syndrome'][18]^=1
        else:next(x for x in rows if x.get('decoder')=='joint_graph_data')['correction'][0]^=1
        with pytest.raises(AssertionError):verify_controller(rows,manifest,True)

def test_clean_path_is_identical_and_cycle_zero_does_not_weaken_rejection():
    old,b=simulate(**options(joint_recovery='off'));r,c=simulate(**options());assert_target(r,c)
    assert old['accepted'] and old['metrics']['gate_counts']==r['metrics']['gate_counts']
    assert r['joint_recovery_episodes']==0
    s=320
    assert data_table()[s]['correction'] is None
    assert decision_word(COMPACT13,s,0)['correction'] is None
    assert decision_word(COMPACT13,s,71)['correction'] is not None
    with pytest.raises(ValueError,match='round-trip'):
        simulate(joint_recovery='fallback',gauss_frame='persistent',model=ZERO)

def test_cli_records_mode_snapshot_and_rejects_incompatible_route(tmp_path):
    folder=tmp_path/'joint'
    cmd=[sys.executable,str(Path(sys.modules[simulate.__module__].__file__)),
         '--shots','1','--seed','2','--source-extraction','decoded_flags','--data-checks','compact_flags',
         '--graph-stars','bare','--terminal-policy','screen','--joint-recovery','fallback',
         '--two-qubit-infidelity','0','--readout-flip-probability','0','--output-dir',str(folder)]
    subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=50)
    manifest=json.loads((folder/'manifest.json').read_text())
    assert manifest['joint_recovery']=='fallback' and 'single_cz_joint_recovery.py' in manifest['source_sha256']
    assert verify_run(folder)['accepted_outputs_recomputed']==1
