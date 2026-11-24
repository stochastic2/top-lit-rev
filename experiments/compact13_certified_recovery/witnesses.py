"""Search reachable full-reference decisions for the correlated chord fault and a data hook."""
import json
from certify import CertifiedCompact, HookCompact, run_arm, noisy, HERE
from single_cz_recovery import COMPACT13, m
from single_cz_root_recovery import cycle_word, external_cases
from single_cz_joint_recovery import families

tail = [e for e in range(5, 13) if 1 in COMPACT13.edges[e]]
cycle = cycle_word(COMPACT13,m.mask(tail))
assert cycle == 70 and (1,cycle) not in external_cases(COMPACT13)
assert (0,1) not in families(COMPACT13)[cycle]
faults = [dict(context="graph/chords",operation="CX",targets=["a1","A4"],paulis={"a1":"X"}),
          dict(context="direct/vote/0/X/0",operation="CX",targets=["s","D1"],paulis={"s":"X"})]
rates=dict.fromkeys(noisy.RATES,"0")
def replay(cls, seed, faults):
    r=run_arm(cls,seed,rates,faults)
    return {k:r.get(k) for k in ("accepted","reason","injected_events","diagnostics")} | {
        "references":[v for v in r["record"] if "direct_reference" in v or "direct_recovery" in v or "cycle_only_lookup" in v]}

if __name__ == "__main__":
    rows={}
    for seed in range(48):
        protected=replay(CertifiedCompact,seed,faults)
        if protected["reason"]=="uncertified_cycle_only_data_correction":
            assert len(protected["injected_events"]) == 2
            rows={"seed":seed,"original":replay(HookCompact,seed,faults),"certified":protected,
                  "single_controls":[replay(CertifiedCompact,seed,[f]) for f in faults]}
            break
    (HERE/"witness.json").write_text(json.dumps({"cycle":cycle,"chord_tail":tail,"replay":rows},indent=2)+"\n")
    print("found",rows.get("seed"),flush=True)
