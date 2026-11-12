"""Independent dense, recovery, noise, and full-factory checks for CZ simulation."""
from itertools import combinations,product
from fractions import Fraction
from random import Random
import ast
from pathlib import Path
import json
import subprocess
import sys
import numpy as np
import pytest

import c4_helix_single_block_cz as m
from single_cz_state import C8,CoherentState,ONE
from single_cz_runtime import QuantumBackend,NoiseModel,pauli_probability
from single_cz_recovery import GRAPHS,syndrome,data_table,physical_table,remainder,clean_reference
from single_cz_controller import SimulationController
from single_cz_diagnostics import diagnose,coordinates,X0,X1
from simulate_single_block_cz_depolarizing import simulate,clean_costs,summarize,isolated
from verify_single_block_cz_run import verify_run

ZERO = NoiseModel(two_qubit_infidelity=0,readout_flip_probability=0)
MATS = {"X":np.array([[0,1],[1,0]],complex),"Y":np.array([[0,-1j],[1j,0]],complex),
        "Z":np.diag([1,-1]),"H":np.array([[1,1],[1,-1]])/np.sqrt(2),
        "S":np.diag([1,1j]),"SDG":np.diag([1,-1j]),
        "T":np.diag([1,np.exp(1j*np.pi/4)]),"TDG":np.diag([1,np.exp(-1j*np.pi/4)])}


def dense_gate(v,name,qs):
    out = np.zeros_like(v)
    if name == "CX":
        for word,a in enumerate(v):
            out[word ^ (((word >> qs[0])&1) << qs[1])] += a
    else:
        for word,a in enumerate(v):
            bit = (word >> qs[0])&1
            for new in (0,1):
                out[(word & ~(1 << qs[0])) | (new << qs[0])] += MATS[name][new,bit]*a
    return out


def dense_backend(b):
    labels = b.data_labels+tuple(b.state.basis_labels)
    out = np.zeros(1 << len(labels),complex)
    for (word,fid),c in b.state.terms.items():
        factor = b.state.store.factors[fid]
        assert factor.labels == b.data_labels
        for index,phase in zip(factor.indices,factor.phases):
            out[int(index) | (word << len(b.data_labels))] += c.complex()*np.exp(1j*np.pi*int(phase)/4)
    return out/np.linalg.norm(out)


@pytest.mark.parametrize("sign",(-1,1))
@pytest.mark.parametrize("fault_port",(0,1,2))
def test_controlled_w_all_local_pauli_faults_match_dense_complex(sign,fault_port):
    axes = list(product("IXYZ",repeat=2)) if fault_port == 1 else [(p,) for p in "IXYZ"]
    for error in axes:
        b = QuantumBackend(model=ZERO,data_labels=("D0","D1"))
        for q in ("D0","D1","c"):
            b.prepare(q)
        v = np.zeros(8,complex);v[0] = 1
        for name,qs in (("H",("D0",)),("CX",("D0","D1")),("S",("D1",)),("H",("c",))):
            b.gate(name,*qs)
            v = dense_gate(v,name,tuple(("D0","D1","c").index(q) for q in qs))
        ops = [("T" if sign == 1 else "TDG",("D0",)),("CX",("c","D0")),
               ("TDG" if sign == 1 else "T",("D0",))]
        for j,(name,qs) in enumerate(ops):
            b.gate(name,*qs)
            v = dense_gate(v,name,tuple(("D0","D1","c").index(q) for q in qs))
            if j == fault_port:
                for q,p in zip(qs,error):
                    if p != "I":
                        b.gate(p,q)
                        v = dense_gate(v,p,(("D0","D1","c").index(q),))
        np.testing.assert_allclose(dense_backend(b),v,atol=1e-12)
        # Clifford-factor invariant is restored at each completed port.
        b.gate("H","D0")
        np.testing.assert_allclose(dense_backend(b),dense_gate(v,"H",(0,)),atol=1e-12)


def test_exact_ring_phase_and_interference():
    rng = Random(7)
    for _ in range(100):
        a,b = C8(*(rng.randrange(-5,6) for j in range(4))),C8(*(rng.randrange(-5,6) for j in range(4)))
        assert (a*b).complex() == pytest.approx(a.complex()*b.complex(),abs=1e-12)
        assert a.conj().complex() == pytest.approx(a.complex().conjugate())
    b = QuantumBackend(model=ZERO,data_labels=("D0",))
    b.prepare("D0");b.gate("H","D0");b.gate("H","D0")
    assert b.measure_z("D0") == 0
    assert b.measurements[-1]["probability_one"] == 0
    a,b=1,1
    for _ in range(100):
        assert C8(a,-b,0,b).real_sign()==((a*a-2*b*b)>0)-((a*a-2*b*b)<0)
        a,b=a+2*b,a+b


def test_irrational_born_probability_uses_exact_signs():
    b=QuantumBackend(model=ZERO,data_labels=("D0",))
    b.prepare("D0");b.prepare("c")
    for name,qs in (("H",("D0",)),("H",("c",)),("T",("D0",)),
                    ("CX",("c","D0")),("TDG",("D0",)),("H",("c",))):
        b.gate(name,*qs)
    b.measure_z("c")
    assert b.measurements[-1]["probability_one"]==pytest.approx((1-1/np.sqrt(2))/2)


def test_css_compression_is_exact_coherent_basis_change_without_projection():
    labels=tuple(f"D{q}" for q in range(20))
    state=CoherentState(labels)
    fid,_=state.store.intern(labels,list(coordinates()),[0]*512)
    rotated,phase=state.store.action(fid,"S",("D0",))
    other,phase2=rotated,phase
    for q in m.SUPPORTS[0]:
        other,p=state.store.action(other,"X",(f"D{q}",))
        phase2*=p
    state.terms={(0,rotated):phase,(0,other):phase2}
    before=state.sparse_output(labels)
    state.compress_css(min_terms=0)
    assert state.css_compressions==1 and len(state.terms)==1
    after=state.sparse_output(labels)
    np.testing.assert_array_equal(before[0],after[0])
    np.testing.assert_allclose(before[1],after[1],atol=1e-12)


def test_noise_calibration_reports_and_unlimited_event_counts():
    assert pauli_probability("1e-3",2) == Fraction(1,800)
    assert pauli_probability("1e-3",1).numerator == 3
    b = QuantumBackend(model=NoiseModel(two_qubit_infidelity=0,preparation_flip_probability=1,
                                       readout_flip_probability=1),data_labels=("D0",))
    b.prepare("D0")
    assert b.measure_z("D0") == 0
    assert b.measurements[-1]["actual"] == 1 and b.measurements[-1]["reported"] == 0
    b = QuantumBackend(model=NoiseModel(two_qubit_infidelity="4/5",one_qubit_infidelity="2/3",
                                       t_infidelity="2/3",readout_flip_probability=0),data_labels=("D0","D1"))
    b.prepare("D0");b.prepare("D1")
    for name,qs in (("H",("D0",)),("CX",("D0","D1")),("T",("D1",)),("TDG",("D1",))):
        b.gate(name,*qs)
    assert len(b.noise_events) == 4
    assert b.noise_counts == {"one_qubit":1,"two_qubit":1,"T":2}
    assert all(any(p != "I" for p in e["axes"]) for e in b.noise_events)
    assert b.model.manifest()["fault_count_cap"] is None
    for bad in (True,"nan","-1","1.1"):
        with pytest.raises(ValueError):
            NoiseModel(t_infidelity=bad)


def test_graphs_are_current_and_decode_every_correctable_sphere():
    root = Path(__file__).resolve().parent
    old = ast.parse((root/"c4_helix_noiseless.py").read_text())
    values = {n.targets[0].id:ast.literal_eval(n.value) for n in old.body if isinstance(n,ast.Assign)
              and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ("EDGES","TREE_EDGES")}
    assert GRAPHS["current20"].edges == values["EDGES"]
    assert GRAPHS["current20"].tree == values["TREE_EDGES"]
    for name,distance,radius in (("compact13",5,2),("current20",8,3)):
        graph = GRAPHS[name];graph.validate()
        assert (graph.distance,graph.radius) == (distance,radius)
        for eta in range(0,32,2):
            for n in range(radius+1):
                for sites in combinations(range(len(graph.edges)),n):
                    decoded = graph.decode(graph.cut(eta) ^ m.mask(sites))
                    assert decoded["eta"] == eta


def test_single_block_decoder_all_candidate_classes():
    table = data_table()
    assert sum(r["correction"] is not None for r in table.values()) == 23281
    assert sum(r["correction"] is None for r in table.values()) == 3855
    assert table[0]["correction"] == (0,0)
    for q in range(20):
        for axis in (1,2,3):
            x,z = (axis&1) << q,(axis>>1) << q
            correction = table[syndrome(x,z)]["correction"]
            assert correction is not None
            assert remainder(x ^ correction[0]) == remainder(z ^ correction[1]) == 0
    a,b = m.mask((2,3)),m.mask((8,11,12,15))
    assert syndrome(a,0) == syndrome(b,0)
    assert table[syndrome(a,0)]["correction"] is None
    # Every admitted correction actually has the report used to select it.
    for s,row in table.items():
        if row["correction"] is not None:
            assert syndrome(*row["correction"]) == s


def target_state(logical=(1,1,1,0)):
    weights = {}
    for h in coordinates():
        for offset,a in zip((0,X0,X1,X0 ^ X1),logical):
            if a:
                weights[h ^ offset] = a
    indices = np.array(sorted(weights),np.uint32)
    values = np.array([weights[int(w)] for w in indices],complex)
    return indices,values/np.linalg.norm(values)


def test_complex_logical_decoder_corrects_representative_physical_errors():
    indices,values = target_state()
    # Independently exercise every single-site axis and mixed two-site cases.
    # Mathematical table completeness is checked separately.
    errors = [(0,0)] + [(1 << q,0) for q in range(20)] + [(0,1 << q) for q in range(20)]
    errors += [(1 << q,1 << q) for q in range(20)]
    errors += [(1 << a,1 << b) for a,b in combinations(range(0,20,2),2)]
    for x,z in errors:
        phases = np.array([(-1)**((int(w)&z).bit_count()%2) for w in indices])
        result = diagnose(indices ^ x,values*phases)
        assert result["decoded_target_fidelity"] == pytest.approx(1,abs=1e-10)
    # A genuine negative branch is not diagnosed as magic.
    assert diagnose(*target_state((0,0,0,1)))["decoded_target_fidelity"] == pytest.approx(0)
    # A coherent relative phase must remain observable, not be squared away.
    assert diagnose(*target_state((1,1,1j,0)))["decoded_target_fidelity"] == pytest.approx(5/9)


def test_positive_physical_cz_alone_cannot_certify_a_decoded_magic_state():
    indices,values = target_state((0,0,0,1))
    source = {int(w)^1:a for w,a in zip(indices,values)}  # one physical X(D0)
    def u(ket):
        return {w ^ ((1 << 20)-1):a*np.exp(1j*np.pi*sum(s*(2*((w >> q)&1)-1)
                        for q,s in enumerate(m.SIGNS))/4) for w,a in ket.items()}
    moved = u(source)
    projected = {w:(source.get(w,0)+moved.get(w,0))/2 for w in source.keys()|moved.keys()}
    norm = sum(abs(a)**2 for a in projected.values())
    assert norm == pytest.approx(.5)
    indices = np.array(sorted(projected),dtype=np.uint32)
    values = np.array([projected[int(w)] for w in indices])/np.sqrt(norm)
    again = u(dict(zip(map(int,indices),values)))
    np.testing.assert_allclose(values,[again[int(w)] for w in indices],atol=1e-12)
    assert diagnose(indices,values)["decoded_target_fidelity"] == pytest.approx(0,abs=1e-12)


@pytest.mark.parametrize("graph",("compact13","current20"))
@pytest.mark.parametrize("profile",("conservative","recovery"))
def test_full_noiseless_factory(graph,profile):
    result,b = simulate(model=ZERO,graph=graph,profile=profile,seed=0)
    assert result["metrics"]["sampled_noise_events"] == 0
    assert b.noise_rng.getstate() == Random(result["noise_seed"]).getstate()
    if result["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"] == pytest.approx(1,abs=1e-10)
    else:
        assert "negative" in result["reason"] or "positive" in result["reason"]


def test_one_false_vertex_report_is_retained_and_two_final_idle_faults_decode():
    injections = [{"context":"vertex_readout","operation":"MZ","targets":["a0"],
                   "timing":"report","flip_report":True}]
    result,b = simulate(model=ZERO,seed=2,injections=injections)
    assert result["accepted"] and len(b.injected_events) == 1
    assert sum(next(r["vertex_reports"] for r in result["record"] if "vertex_reports" in r))%2 == 1
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"] == pytest.approx(1)
    injections = [{"context":"terminal_recovery/correction","operation":"BOUNDARY","timing":"idle","paulis":{q:p}}
                  for q,p in (("D2","X"),("D7","Y"))]
    result,b = simulate(model=ZERO,seed=2,injections=injections)
    assert result["accepted"] and len(b.injected_events) == 2
    d = diagnose(*b.state.sparse_output(b.data_labels))
    assert d["decoded_target_fidelity"] == pytest.approx(1)
    assert d["raw_physical_target_fidelity"] < 1e-10


def test_controller_fault_recovery_and_known_source_flag_retry():
    fault = {"context":"enrichment","operation":"CX","targets":["a0","D0"],
             "timing":"after","paulis":{"a0":"X"}}
    result,b = simulate(model=ZERO,seed=0,injections=[fault])
    assert len(b.injected_events) == 1
    assert any("data_recovery" in row for row in result["record"])
    if result["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"] == pytest.approx(1)
    fault = {"context":"source/certify/0/Z/5","operation":"CX","targets":["s","f0"],
             "timing":"after","paulis":{"f0":"X"}}
    result,b = simulate(model=ZERO,seed=0,injections=[fault])
    assert len(b.injected_events) == 1 and result["retries"] == 1
    if result["accepted"]:
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"] == pytest.approx(1)


def test_clean_counts_and_nonzero_noise_is_reproducible():
    costs = clean_costs()
    assert [(costs[k]["gates"]["CX"],costs[k]["peak_live"]) for k in
            ("compact13/conservative","compact13/recovery","current20/conservative","current20/recovery")] == [
                (8724,44),(3217,39),(9302,53),(3459,46)]
    rows = []
    for _ in range(2):
        result,b = simulate(model=NoiseModel(two_qubit_infidelity="1e-4",readout_flip_probability=0),seed=1,noise_seed_value=100)
        rows.append((result["accepted"],result.get("reason"),result["record"],b.noise_events,b.measurements))
    assert rows[0] == rows[1]


def test_flag_extraction_local_certificates_and_no_cat_factory():
    from check_single_cz_flags import audit
    result=audit()
    assert result["verified"] and len(result["gadgets"])==20
    result,b=simulate(model=ZERO,seed=2)
    assert result["accepted"] and result["source_extraction"]=="rolling_flags"
    assert not any("cat" in row for row in result["record"])
    assert all(not row.get("flags",[]) or not any(row["flags"]) for row in result["record"]
               if row.get("extraction")=="rolling_flags")
    assert result["metrics"]["peak_live_qubits"]==39
    assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)


def test_flagged_checks_with_existing_decoded_source_option():
    costs=clean_costs(source_extraction="decoded_flags")
    assert costs["compact13/recovery"]["gates"]["CX"]==2809
    assert costs["current20/recovery"]["gates"]["CX"]==3051
    for graph in ("compact13","current20"):
        result,b=simulate(model=ZERO,seed=2,graph=graph,source_extraction="decoded_flags")
        assert result["accepted"] and not any("cat" in r for r in result["record"])
        assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)


def test_rolling_flags_detect_controller_hooks_and_a_hidden_flag_bit():
    from run_single_block_cz_controller import Reject
    def check(faults):
        b=QuantumBackend(model=ZERO,data_labels=tuple(f"D{j}" for j in range(8)),injections=faults)
        c=SimulationController(b)
        for j in range(8):c.prep(f"D{j}")
        with pytest.raises(Reject):c.check("probe",[("X",f"D{j}") for j in range(8)])
        assert len(b.injected_events)==len(faults)
        assert any(c.record[-1]["flags"])
        assert c.live=={f"D{j}" for j in range(8)}
    first={"context":"probe","operation":"CX","targets":["s","D2"],"paulis":{"s":"X"}}
    check([first])
    check([first,{"context":"probe","operation":"CX","targets":["s","D5"],"paulis":{"s":"X"}}])
    check([first,{"context":"probe","operation":"MZ","targets":["f2"],"timing":"report","flip_report":True}])


def test_flagged_terminal_two_last_readout_idles_remain_correctable():
    faults=[{"context":"terminal/2/X/8","operation":"MZ","targets":["s"],"timing":"idle",
             "paulis":{q:p}} for q,p in (("D0","X"),("D7","Y"))]
    result,b=simulate(model=ZERO,seed=2,injections=faults)
    assert result["accepted"] and len(b.injected_events)==2
    diagnostic=diagnose(*b.state.sparse_output(b.data_labels))
    assert diagnostic["decoded_target_fidelity"]==pytest.approx(1)
    assert diagnostic["raw_physical_target_fidelity"]<1e-10


def test_flagged_mixed_w_ideal_kraus_and_phase_sensitive_fault_span():
    from single_cz_flagged import flagged_program
    axes=("W","Z","W");signs=(1,1,-1);n=3;size=1<<(2*n+2)
    ops=flagged_program(axes,signs)
    w=lambda sign:MATS["TDG" if sign==1 else "T"]@MATS["X"]@MATS["T" if sign==1 else "TDG"]
    q=np.kron(w(-1),np.kron(MATS["Z"],w(1)))
    projectors=[(np.eye(8)+s*q)/2 for s in (1,-1)]
    basis=[]
    for proj in projectors:
        basis.append(proj.ravel())
        for j in range(3):
            for axis in "XYZ":
                basis.append(dense_gate(proj,axis,(j,)).ravel())
    span=np.array(basis).T
    def kraus(fault=None,outcome=0):
        a=np.zeros((size,8),complex);a[:8]=np.eye(8)
        for i,(op,qs) in enumerate(ops):
            if op not in ("PREP","MZ"):a=dense_gate(a,op,qs)
            if fault and i==fault[0]:
                for label,axis in zip(qs,fault[1]):
                    if axis!="I":a=dense_gate(a,axis,(label,))
            if op=="MZ":
                bit=outcome if qs[0]==n else 0
                a[[k for k in range(size) if ((k>>qs[0])&1)!=bit]]=0
        return a[np.arange(8)|(outcome<<n)]
    for bit in (0,1):np.testing.assert_allclose(kraus(outcome=bit),projectors[bit],atol=1e-12)
    # Every Pauli at the T/CX/Tdg locations of both W ports, plus the
    # flag-control CXs. These are dense numerical spot checks, not the proof.
    selected=[(i,op,qs) for i,(op,qs) in enumerate(ops) if op in ("T","TDG","CX")]
    for i,op,qs in selected:
        for paulis in product("IXYZ",repeat=len(qs)):
            if all(p=="I" for p in paulis):continue
            for bit in (0,1):
                k=kraus((i,paulis),bit).ravel()
                coefficients=np.linalg.lstsq(span,k,rcond=1e-11)[0]
                np.testing.assert_allclose(span@coefficients,k,atol=1e-10)


def test_capacity_failure_is_unresolved_not_rejection(tmp_path):
    request = {"attempt_dir":str(tmp_path),"index":0,"seed":0,"noise_seed":0,
               "rates":ZERO.manifest()["rates"],"graph":"compact13","profile":"recovery",
               "history_policy":"triple","route":"gauging","trace":False,"source_extraction":"decoded_flags",
               "limits":{"max_terms":1,"max_factors":4096,"max_operations":200000}}
    result = isolated(request,10)
    assert result["execution_status"] == "resource_failure" and result["accepted"] is None
    summary = summarize([result])
    assert summary["unresolved"] == 1 and summary["rejected"] == 0
    assert summary["acceptance_bounds_all_attempts"] == [0,1]


def test_saved_run_verifies_and_detects_metadata_tampering(tmp_path):
    script=Path(__file__).with_name("simulate_single_block_cz_depolarizing.py")
    directory=tmp_path/"run"
    subprocess.run([sys.executable,"-B",str(script),"--shots","1","--seed","2","--two-qubit-infidelity","0",
                    "--readout-flip-probability","0","--output-dir",str(directory)],
                   check=True,capture_output=True,text=True,timeout=30)
    result=verify_run(directory)
    assert result["accepted_outputs_recomputed"]==1 and result["source_tree_matches_saved_run"]
    manifest=json.loads((directory/"manifest.json").read_text())
    assert manifest["graph_verification"]=="three_zero_Z_edge_scans"
    path=directory/"attempts/000000/controller.json"
    original=path.read_text()
    rows=json.loads(original)
    row=next(r for r in rows if r.get("data_recovery")=="terminal_recovery")
    row["correction"]=[1,0]
    path.write_text(json.dumps(rows))
    with pytest.raises(AssertionError):verify_run(directory)
    path.write_text(original)
    rows=json.loads(original)
    row=next(r for r in rows if "graph_parity_verification" in r)
    row["records"][0][0]=1
    path.write_text(json.dumps(rows))
    with pytest.raises(AssertionError):verify_run(directory)
    path.write_text(original)
    path=directory/"attempts/000000/measurements.json"
    original=path.read_text();rows=json.loads(original);rows[0]["reported"]^=1
    path.write_text(json.dumps(rows))
    with pytest.raises(AssertionError):verify_run(directory)


def test_direct_graph_parity_certificates():
    from check_single_cz_graph_parity import audit
    result=audit()
    assert result["verified"]
    assert result["graphs"]["compact13"]["clean_gates"]["CX"]==143
    assert result["graphs"]["current20"]["clean_gates"]["CX"]==220


def test_graph_raw_hook_retries_unused_graph_and_readout_flip_retries():
    faults=[{"context":"graph/raw/0","operation":"CX","targets":["a0","A0"],
             "paulis":{"a0":"X"}},
            {"context":"graph/parity/0/1/0","operation":"MZ","targets":["w"],
             "timing":"report","flip_report":True}]
    # Test independently: the two cases have different rejection triggers.
    for fault in faults:
        result,b=simulate(model=ZERO,seed=0,injections=[fault])
        assert len(b.injected_events)==1 and result["retries"]==1
        graphs=[r for r in result["record"] if "graph_parity_verification" in r]
        assert len(graphs)==2 and not graphs[0]["accepted"] and graphs[1]["accepted"]
        assert any(graphs[0]["records"][-1])
        if result["accepted"]:
            assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)


def test_graph_last_scan_phase_spread_and_two_late_bit_faults():
    cases=[[{"context":"graph/parity/0/2/0","operation":"CX","targets":["a0","w"],
             "paulis":{"w":"Z"}}],
           [{"context":"graph/parity/0/2/12","operation":"CX","targets":[q,"w"],
             "paulis":{q:"X"}} for q in ("a0","A12")]]
    for faults in cases:
        result,b=simulate(model=ZERO,seed=0,injections=faults)
        assert len(b.injected_events)==len(faults)
        graph=next(r for r in result["record"] if "graph_parity_verification" in r)
        assert graph["accepted"] and not any(any(r) for r in graph["records"])
        if result["accepted"]:
            assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)


def test_coherent_local_graph_meter_fault_preserves_accepted_magic():
    # A T on the meter is a coherent I/Z error at ONE CX location.
    # It leaves nonuniform phases in the cut subspace, not a stochastic Pauli mixture.
    class CoherentFault(QuantumBackend):
        used=False
        def gate(self,name,*targets):
            super().gate(name,*targets)
            if not self.used and self.context=="graph/parity/0/2/0" and targets==("a0","w"):
                self.state.gate("T","w")
                self.used=True
    accepted=0
    for seed in (0,1,2):
        b=CoherentFault(seed=seed,model=ZERO)
        result=SimulationController(b).run()
        assert b.used
        graph=next(r for r in result["record"] if "graph_parity_verification" in r)
        assert graph["accepted"]
        if result["accepted"]:
            accepted+=1
            assert diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]==pytest.approx(1)
    assert accepted
