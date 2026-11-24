"""Finite checks for the deferred projector proof using emitted gates."""
from itertools import combinations_with_replacement, combinations, product
from unittest.mock import patch
import json
from run import DeferredCompact, HookCompact, HERE, trace, settings, noisy
from compare import run_arm
from check_optimized_extraction import signatures
from check_single_cz_tree_resource import defect, blocks, handoff_certificate
from check_single_cz_short_gauss_vote import compact_screen, terminal
from single_cz_recovery import m, syndrome, remainder

t,_ = trace(DeferredCompact, settings(DeferredCompact))
parent,_ = trace(HookCompact, settings(HookCompact))
assert t["accepted"]
prefix = [(ctx,op) for ctx,op in t["gates"] if not ctx.startswith("direct/vote/1/")]
assert prefix == [(ctx,op) for ctx,op in parent["gates"] if not ctx.startswith("direct/vote/1/")]
def gauss_ops(trace):
    return [g for c,g in trace["gates"] if c.startswith("direct/vote/1/")]
assert gauss_ops(t) == [g for c,g in parent["gates"] if c.startswith("direct/vote/1/") and
                        c.split("/")[3] in ("G","root_Gauss")]

def integer_ops(gates, labels):
    return [(op,tuple(labels.index(q) for q in qs)) for op,qs in gates]

graph = [op for c,op in t["gates"] if c.startswith("graph/")]
labels = [f"a{i}" for i in range(5)]+[f"A{i}" for i in range(13)]+["s"]
sig,ng = signatures(integer_ops(graph,labels),(),(1<<18)-1,1)
rs = {(defect(x),f) for x,z,f in sig} | {(0,0)}
assert all(f or blocks(x)<=1 for x,f in rs)
assert all(f!=g or blocks(x^y)<=2 for (x,f),(y,g) in combinations_with_replacement(rs,2))

root = [op for c,op in t["gates"] if c=="direct/vote/1/root_Gauss" and op[0]!="BOUNDARY"]
for q in range(4):
    wire = f"D{q}"
    on_wire=[op for op,qs in root if wire in qs]
    assert on_wire == (["T","CX","TDG"] if m.SIGNS[q]==1 else ["TDG","CX","T"])
ports = [f"D{i}" for i in range(4)]+[f"A{e}" for e,uv in enumerate(m.EDGES) if 0 in uv]
labels = ports+["s"]+[f"f{i}" for i in range(4)]
ops = integer_ops([g for g in root if g[0] not in ("T","TDG")],labels)
sig,nr = signatures(ops,range(len(ports)),255,15)
sig.add((0,0,0))
def weight(x,z):
    return min((x|z).bit_count(),((x^255)|z).bit_count())
assert all(f or weight(x,z)<=1 for x,z,f in sig)
assert all(f!=g or weight(x^y,z^w)<=2 for (x,z,f),(y,w,g) in combinations_with_replacement(sig,2))

masks=0
for v,w in combinations(range(5),2):
    for a,b in product(range(16),repeat=2):
        x=(a<<(4*v))|(b<<(4*w))
        if syndrome(x,0)==0:
            assert not remainder(x)
        masks+=1
for support in m.SUPPORTS:
    assert len(support)%4==0 and sum(m.SIGNS[q]<0 for q in support)%2==0
with patch.object(terminal,"screen_program",compact_screen):
    screen=terminal.audit()
assert screen["verified"]
out=dict(resource_locations=ng,root_clifford_locations=nr,two_block_component_masks=masks,
         handoff=handoff_certificate(),terminal=screen,clean_counts=t["counts"])
rates = dict.fromkeys(noisy.RATES,"0")
def flip(ctx,q):
    return dict(context=ctx,timing="report",operation="MZ",targets=[q],flip_report=True)
cases={"clean":[], "one_edge":[flip("edge_readout","A0")],
       "two_edges":[flip("edge_readout","A0"),flip("edge_readout","A1")],
       "hidden_chord":[dict(context="graph/chords",operation="CX",targets=["a1","A4"],paulis={"a1":"X","A4":"Z"})],
       "deciding_negative_retry":[flip("direct/vote/1/root_Gauss","s")]}
out["injections"]={}
for name,faults in cases.items():
    row=run_arm(DeferredCompact,2,rates,faults)
    assert len(row["injected_events"])==len(faults)
    assert row["status"]=="completed"
    if row["accepted"]:
        assert row["diagnostics"]["decoded_target_within_tolerance"]
    out["injections"][name]=dict(accepted=row["accepted"],reason=row["reason"],events=row["injected_events"],
        fidelity=row.get("diagnostics",{}).get("decoded_target_fidelity"),
        votes=[r for r in row["record"] if "direct_vote" in r])
(HERE/"checks.json").write_text(json.dumps(out,indent=2)+"\n")
