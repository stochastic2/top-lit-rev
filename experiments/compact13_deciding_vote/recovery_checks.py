"""Exercise the recovery decisions on the post-handoff screen."""
import json
from recovery import RecoveringCompact
from run import HERE, noisy
from compare import run_arm

def idle(q, edge):
    return dict(context="edge_readout",timing="idle",operation="MZ",targets=[edge],paulis={q:"Z"})
one = idle("D0","A0")
two = idle("D4","A1")
flag = dict(context="compact/terminal_screen/0/Z/5",timing="report",operation="MZ",targets=["f0"],flip_report=True)
results = {}
for name, faults, accept in [("clean",[],True),("odd_Z",[one],False),
                             ("even_Z",[one,two],True),("flag",[flag],True)]:
    row = run_arm(RecoveringCompact,2,dict.fromkeys(noisy.RATES,"0"),faults)
    assert len(row["injected_events"])==len(faults)
    results[name] = dict(accepted=row["accepted"],reason=row["reason"],screen=row["terminal_screen_outcome"],
        fidelity=row.get("diagnostics",{}).get("decoded_target_fidelity"),events=row["injected_events"])
    print(name, results[name]["accepted"], results[name]["reason"], results[name]["screen"])
    assert row["accepted"] == accept
    if accept:
        assert row["diagnostics"]["decoded_target_within_tolerance"]
(HERE/"recovery_checks.json").write_text(json.dumps(results,indent=2)+"\n")
