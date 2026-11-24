"""Check clean traces and exercise faults on chords and the handoff."""
import json
from compare import BareCompact, HookCompact, LeanResourceCat, HERE, shot, trace, settings, noisy
from holdout import run_arm
from trace_audit import phase_counts

audit = {}
for cls in (BareCompact, HookCompact, LeanResourceCat):
    clean, _ = trace(cls, settings(cls))
    assert clean["accepted"]
    audit[cls.__name__] = dict(clean_counts=clean["counts"], peak=clean["peak_live"],
                                phases=phase_counts(clean["contexts"]))
clean_rates = dict.fromkeys(noisy.RATES,"0")
chord = dict(context="graph/chords", operation="CX", targets=["a1","A4"], paulis={"a1":"X","A4":"Z"})
root = dict(context="graph/tree_raw",operation="CX",targets=["a0","A1"],paulis={"a0":"X"})
report = dict(context="edge_readout",timing="report",operation="MZ",targets=["A0"],flip_report=True)
audit["witnesses"] = {}
for name, faults in [("clean", []), ("chord", [chord]), ("root", [root]), ("edge_report", [report]),
                     ("chord_and_edge", [chord, report])]:
    row = run_arm(HookCompact, 2, clean_rates, faults)
    audit["witnesses"][name] = {k:row.get(k) for k in ("accepted","reason","injected_events","diagnostics","retries")}
    assert len(row["injected_events"]) == len(faults), name
(HERE/"audit.json").write_text(json.dumps(audit, indent=2)+"\n")
