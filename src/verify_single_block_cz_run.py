"""Read-only saved-run verification: records, noise accounting and output states.

Recomputes diagnostic fidelities from NPZ; validates commuting-history and
passing-round certificates, corrections and reported/actual readout differences.
It does not claim to replay every gate unless a separate trajectory replay is
performed; full circuit dynamics are validated by independent dense tests.
"""
from collections import Counter,defaultdict,deque
from hashlib import sha256
from pathlib import Path
import argparse
import json
import numpy as np
import c4_helix_single_block_cz as m
from single_cz_recovery import GRAPHS,clean_reference,data_table,cycle_table,pure_error
from single_cz_persistent import PERSISTENT_GRAPHS,validate_persistent_graph
from single_cz_diagnostics import diagnose
from simulate_single_block_cz_depolarizing import summarize,write_json


def expected_ports(name,graph):
    parts=name.split("/")
    if parts[-2] in ("Z","X"):
        return [(parts[-2],f"D{q}") for q in m.SUPPORTS[int(parts[-1])]]
    if parts[-2]=="logical_X":
        return [("X",f"D{q}") for q in (m.X0,m.X1)[int(parts[-1])]]
    if parts[-1]=="U":return [("W",f"D{q}") for q in range(20)]
    if parts[-1]=="root_Gauss":
        return [("W",f"D{q}") for q in range(4)]+[("X",f"A{j}") for j,ends in enumerate(graph.edges) if 0 in ends]
    if parts[-1]=="transported_Gauss":
        return [("W",f"D{q}") for q in range(20)]+[("X",f"A{j}") for j,ends in enumerate(graph.edges) if 0 in ends]
    if parts[-2]=="star":
        return [("X",f"A{j}") for j,ends in enumerate(graph.edges) if int(parts[-1]) in ends]
    if parts[-2]=="cycle" or "cycle_recovery" in parts:
        return [("Z",f"A{j}") for j in graph.cycles[int(parts[-1])]]
    raise ValueError("Unknown flagged check: "+name)


def reference(records,policy):
    if policy == "adaptive":
        return clean_reference(records)
    if len(records)>=3 and records[-3:]==[records[-1]]*3:
        return {"selected":len(records)-1,"occurrences":list(range(len(records)-3,len(records))),
                "kind":"three_identical_complete_records"}
    return None


def verify_history(records,certificate,policy):
    assert records and len(records) <= (5 if policy == "adaptive" else 9)
    assert all(len(row)==len(records[0]) and all(b in (0,1) for b in row) for row in records)
    for k in range(1,len(records)+1):
        cert = reference(records[:k],policy)
        if cert is not None:
            assert k==len(records) and cert==certificate,"History did not stop at first certificate"
            return records[cert["selected"]]
    raise ValueError("No clean-reference certificate")


def verify_controller(rows,manifest,accepted):
    graph = PERSISTENT_GRAPHS[manifest["graph"]["name"]]
    persistent=manifest.get("gauss_frame","round_trip")=="persistent"
    if persistent:
        validate_persistent_graph(graph)
        assert manifest["route"]=="gauging" and manifest["profile"]=="recovery"
        assert manifest["terminal_policy"] in ("intrinsic","intrinsic_persistent_tail")
        assert manifest["graph_stars"]=="bare" and manifest["verification_extraction"]=="flags"
    profile,policy = manifest["profile"],manifest["history_policy"]
    checks = {row["check"]:row["reported_parity"] for row in rows if "check" in row}
    histories = 0
    graph_attempts = []
    prepared_cats={}
    flag_triggers={}
    flag_histories={}
    flag_repairs={}
    root_triggers={};root_histories={};root_repairs={};root_graph_repairs={}
    data_epoch=0
    bare_stars=manifest.get("graph_stars","flags")=="bare"
    final_cycle_history=None
    final_cycle_repairs=0
    screen_mode=manifest.get("terminal_policy")=="screen"
    screen_version=manifest.get("terminal_screen_version",1) if screen_mode else None
    screen_begin=None
    screen_result=None
    screen_history=None
    screen_begins=[]
    screen_results=[]
    screen_finish=None
    for row in rows:
        if "cat" in row:prepared_cats[row["cat"]]=row
        if row.get("extraction")=="verified_cat_CZ":
            assert manifest["route"]=="direct_cat" and manifest.get("direct_cz_extraction")=="cat"
            assert list(zip(row["axes"],row["targets"]))==[("W",f"D{q}") for q in range(20)]
            assert len(row["leaf_reports"])==20 and all(b in (0,1) for b in row["leaf_reports"])
            assert sum(row["leaf_reports"])%2==row["reported_parity"]
            assert row["check"] in prepared_cats
            prepared=prepared_cats[row["check"]]
            assert prepared["flags"] and all(len(r)==19 for r in prepared["flags"])
            if "reference" in prepared:assert len(prepared["repair_pattern"])==20
            else:assert len(prepared["flags"])==3 and not any(any(r) for r in prepared["flags"])
        if row.get("extraction") in ("rolling_flags","compact_flags","transported_Gauss","single_fault_flag","bare_graph_Z","bare_graph_X_star"):
            ports=expected_ports(row["check"],graph)
            assert list(zip(row["axes"],row["targets"]))==ports
            if row["extraction"]=="bare_graph_X_star":
                assert bare_stars and manifest["route"]=="gauging" and profile=="recovery"
                assert "/star/" in row["check"] and all(a=="X" and q.startswith("A") for a,q in ports)
                assert "flags" not in row
            elif row["extraction"]=="bare_graph_Z":
                assert all(a=="Z" and q.startswith("A") for a,q in ports)
            else:
                n=len(ports)
                conditional=row["extraction"]=="single_fault_flag"
                if conditional:
                    if row["check"].startswith("flag_recovery/"):
                        assert manifest.get("flag_recovery","reject")=="data" and flag_triggers
                    elif row["check"].startswith("root_recovery/"):
                        assert manifest.get("root_recovery","reject")!="reject" and root_triggers
                    else:
                        assert row["check"].startswith("terminal_screen_recovery/") and screen_mode
                        assert screen_version in (1,2)
                        assert screen_result is not None and screen_result["terminal_screen_result"]=="syndrome_fallback"
                    assert row["minimum_spent_faults"]==1
                    assert row.get("conditional_checks","legacy")==manifest.get("conditional_checks","legacy")
                    assert all(a==row["axes"][0] and a in ("X","Z") and q.startswith("D") for a,q in ports)
                expected=1 if conditional or (n==4 and len(set(row["axes"]))==1 and row["axes"][0] in ("X","Z")) else n+1
                if row["extraction"]=="transported_Gauss":
                    assert persistent and row["check"].endswith("/transported_Gauss")
                    assert row["axes"]==["W"]*20+["X"]*(n-20)
                    expected=21
                if row["extraction"]=="compact_flags":
                    assert manifest.get("data_checks","rolling_flags")=="compact_flags"
                    assert profile=="recovery" and manifest["verification_extraction"]=="flags"
                    assert not row["check"].startswith(("source/","terminal_screen/","flag_recovery/"))
                    assert n in (4,8) and all(a==row["axes"][0] and a in ("X","Z") and q.startswith("D") for a,q in ports)
                    expected=1 if n==4 else 4
                assert len(row["flags"])==expected and all(b in (0,1) for b in row["flags"])
                if any(row["flags"]) and "flag_recovery_episode" in row:
                    assert manifest.get("flag_recovery","reject")=="data"
                    episode=row["flag_recovery_episode"]
                    assert episode not in flag_triggers and 0<=episode<manifest.get("max_flag_recoveries",2)
                    assert all(a==row["axes"][0] and a in ("X","Z") and q.startswith("D") for a,q in ports)
                    assert not row["check"].startswith(("source/","flag_recovery/"))
                    flag_triggers[episode]=row
                elif any(row["flags"]) and "root_recovery_episode" in row:
                    assert manifest.get("root_recovery","reject")!="reject" and not persistent
                    assert row["check"].endswith("/root_Gauss") or (manifest["route"]=="direct_cat" and row["check"].endswith("/U") and manifest.get("direct_cz_extraction")!="cat")
                    episode=row["root_recovery_episode"]
                    assert episode not in root_triggers and 0<=episode<manifest.get("max_flag_recoveries",8)
                    root_triggers[episode]=row
                elif accepted and not row["check"].startswith("source/"):
                    assert not any(row["flags"])
        if "flag_recovery_history" in row:
            episode=row["flag_recovery_history"]
            assert episode in flag_triggers and episode not in flag_histories
            records=row["records"]
            assert 2<=len(records)<=4 and all(len(r)==18 and all(b in (0,1) for b in r) for r in records)
            assert all(records[j]!=records[j-1] for j in range(1,len(records)-1))
            assert records[-1]==records[-2]==row["selected_record"]
            assert row["reference"]=={"kind":"two_identical_after_nonzero_flag","minimum_spent_faults":1,
                                      "selected":len(records)-1,"occurrences":[len(records)-2,len(records)-1]}
            for r,bits in enumerate(records):
                assert bits==[checks[f"flag_recovery/{episode}/{r}/{axis}/{s}"] for axis in "ZX" for s in range(9)]
            flag_histories[episode]=row
        if "flag_data_recovery" in row:
            from single_cz_flag_recovery import decision
            episode=row["flag_data_recovery"]
            assert episode in flag_histories and episode not in flag_repairs
            trigger=flag_triggers[episode]
            assert row["trigger"]==trigger["check"]
            assert row["axis"]==trigger["axes"][0]
            assert row["support"]==[int(q[1:]) for q in trigger["targets"]]
            assert row["flag_word"]==sum(b << j for j,b in enumerate(trigger["flags"]))
            assert row["syndrome"]==flag_histories[episode]["selected_record"]
            extraction=trigger["extraction"]
            assert row.get("trigger_extraction","rolling_flags")==extraction
            result=decision(row["axis"],tuple(row["support"]),row["flag_word"],row["syndrome"],extraction)
            assert row["candidate_classes"]==result["classes"]
            assert row["correction"]==(list(result["correction"]) if result["correction"] is not None else None)
            if accepted:assert row["correction"] is not None
            flag_repairs[episode]=row
        if "root_recovery_history" in row:
            ep=row["root_recovery_history"]
            assert ep in root_triggers and ep not in root_histories
            records=row["records"];is_graph=manifest["route"]=="gauging"
            expected_size=18+len(graph.cycles)+4 if is_graph else 18
            assert 2<=len(records)<=4 and all(len(bits)==expected_size and all(b in (0,1) for b in bits) for bits in records)
            assert all(records[j]!=records[j-1] for j in range(1,len(records)-1))
            assert records[-1]==records[-2]==row["selected_record"]
            assert row["reference"]=={"kind":"two_identical_after_nonzero_root_flag","minimum_spent_faults":1,
                                      "selected":len(records)-1,"occurrences":[len(records)-2,len(records)-1]}
            assert row["trigger"]==root_triggers[ep]["check"]
            for r,bits in enumerate(records):
                prefix=f"root_recovery/{ep}/{r}"
                expected=[checks[f"{prefix}/code/{a}/{j}"] for a in "ZX" for j in range(9)]
                if is_graph:expected += [checks[f"{prefix}/cycle/{j}"] for j in range(len(graph.cycles))]+[checks[f"{prefix}/star/{v}"] for v in range(1,5)]
                assert bits==expected
            root_histories[ep]=row
        if "root_data_recovery" in row:
            from single_cz_root_recovery import decision as root_decision
            ep=row["root_data_recovery"]
            assert ep in root_histories and ep not in root_repairs
            trigger=root_triggers[ep];g=graph if manifest["route"]=="gauging" else None
            nc=len(g.cycles) if g else 0;bits=root_histories[ep]["selected_record"]
            assert row["syndrome"]==bits and row["trigger"]==trigger["check"]
            assert row["flag_word"]==sum(b << j for j,b in enumerate(trigger["flags"]))
            assert row["decoder"]==manifest["root_recovery"]
            result=root_decision(g,row["flag_word"],bits[:18],bits[18:18+nc],row["decoder"]=="joint")
            assert json.loads(json.dumps(row["decision"]))==json.loads(json.dumps(result))
            if accepted:assert result["correction"] is not None
            root_repairs[ep]=row
        if "root_graph_recovery" in row:
            from single_cz_graph_stars import chord_correction
            ep=row["root_graph_recovery"];g=graph if manifest["route"]=="gauging" else None
            assert ep in root_repairs and root_repairs[ep]["decision"]["correction"] is not None
            bits=root_histories[ep]["selected_record"];nc=len(g.cycles) if g else 0
            assert row["X_edges"]==(list(chord_correction(g,bits[18:18+nc])) if g else [])
            assert row["Z_edges"]==([e for bit,e in zip(bits[18+nc:],g.tree) if bit] if g else [])
            assert row["frame"]==("V" if g else "data") and row["faulty_root_vote_discarded"] is True
            root_graph_repairs[ep]=row
        if "data_epoch" in row:
            data_epoch+=1
            assert row["data_epoch"]==data_epoch
            if row["cause"]=="flag_data_recovery":assert flag_repairs[row["episode"]]["correction"] is not None
            else:assert row["cause"]=="root_flag_recovery" and row["episode"] in root_graph_repairs
        if "history_reset" in row:
            assert row["new_epoch"]==data_epoch and 0<=row["old_epoch"]<data_epoch
        if "terminal_screen_begin" in row:
            from single_cz_terminal_screen import screen_checks
            assert screen_mode
            if screen_version==1:assert screen_begin is None
            else:
                assert screen_version in (2,3) and row["version"]==screen_version and row["sweep"]==len(screen_begins)<2
                if screen_begins:
                    first=screen_results[0]
                    assert first["terminal_screen_result"]!="zero_accept"
                    if first["terminal_screen_result"]=="flag_recovery":
                        assert flag_repairs[first["episode"]]["correction"] is not None
                    else:
                        assert screen_version==2
                        assert screen_history is not None
                        assert any(v.get("data_recovery")=="terminal_screen_recovery" and v["correction"] is not None for v in rows)
            assert row["order"]==[list(c) for c in screen_checks()]
            screen_begin=row
            screen_begins.append(row)
            screen_result=None
        if "terminal_screen_result" in row:
            assert screen_mode and screen_begin is not None and screen_result is None
            screen_result=row
            screen_results.append(row)
            n=row["completed_checks"]
            prefix=f"terminal_screen/{row['sweep']}/" if screen_version in (2,3) else "terminal_screen/"
            if screen_version in (2,3):assert row["sweep"]==screen_begin["sweep"]
            measured=[r for r in rows if r.get("check","").startswith(prefix)]
            assert len(measured)==n and 1<=n<=18
            assert [(r["axes"][0],int(r["check"].split("/")[-1])) for r in measured]==[tuple(c) for c in screen_begin["order"][:n]]
            assert all(not any(r["flags"]) and r["reported_parity"]==0 for r in measured[:-1])
            outcome=row["terminal_screen_result"]
            if outcome=="zero_accept":
                assert n==18 and not any(measured[-1]["flags"]) and measured[-1]["reported_parity"]==0
                assert row["syndrome_reports"]==[0]*18
            elif outcome=="syndrome_fallback":
                assert row["trigger"]==measured[-1]["check"] and row["reported_parity"]==1
                assert not any(measured[-1]["flags"]) and measured[-1]["reported_parity"]==1
            else:
                assert outcome=="flag_recovery" and row["trigger"]==measured[-1]["check"] and any(measured[-1]["flags"])
                assert measured[-1]["flag_recovery_episode"]==row["episode"]
        if "terminal_screen_history" in row:
            assert screen_version in (1,2)
            assert screen_mode and screen_result["terminal_screen_result"]=="syndrome_fallback" and screen_history is None
            records=row["records"]
            assert 2<=len(records)<=4 and all(len(r)==18 and all(b in (0,1) for b in r) for r in records)
            assert all(records[j]!=records[j-1] for j in range(1,len(records)-1))
            assert records[-1]==records[-2]==row["selected_record"]
            assert row["reference"]=={"kind":"two_identical_after_nonzero_code_report","minimum_spent_faults":1,
                                      "selected":len(records)-1,"occurrences":[len(records)-2,len(records)-1]}
            for r,bits in enumerate(records):
                assert bits==[checks[f"terminal_screen_recovery/{r}/{axis}/{j}"] for axis in "ZX" for j in range(9)]
            screen_history=row
        if "terminal_screen_finish" in row:
            assert screen_mode and screen_version in (2,3) and screen_finish is None
            screen_finish=row["terminal_screen_finish"]
        if "graph_parity_verification" in row:
            records = row["records"]
            assert row["graph_parity_verification"] == len(graph_attempts)
            assert row["policy"] == "three_zero_Z_edge_scans"
            assert 1 <= len(records) <= 3
            assert all(len(r)==len(graph.edges) and all(b in (0,1) for b in r) for r in records)
            assert not any(any(r) for r in records[:-1]),"Graph did not stop at first nonzero scan"
            assert row["accepted"] == (len(records)==3 and not any(records[-1]))
            assert row["accepted"] or any(records[-1])
            assert not any(v["accepted"] for v in graph_attempts)
            graph_attempts.append(row)
        if "history" in row:
            selected = verify_history(row["records"],row["reference"],policy)
            assert selected == row["selected_record"]
            histories += 1
            if row["history"]=="final_cycles":
                assert bare_stars and final_cycle_history is None
                for r,bits in enumerate(row["records"]):
                    assert bits==[checks[f"final_cycles/{r}/cycle/{j}"] for j in range(len(graph.cycles))]
                final_cycle_history=row
        if "final_cycle_flattening" in row:
            from single_cz_graph_stars import chord_correction
            assert bare_stars and row["final_cycle_flattening"] is True and final_cycle_history is not None
            assert row["syndrome"]==final_cycle_history["selected_record"]
            assert row["X_edges"]==list(chord_correction(graph,row["syndrome"]))
            assert not set(row["X_edges"]) & set(graph.tree)
            assert row["correction_support"]=="non_tree_edges_only"
            final_cycle_repairs+=1
        if "cat" in row and "reference" in row:
            records,cert = row["flags"],row["reference"]
            if cert.get("kind") == "two_initial_zero_scans":
                assert len(records)==2 and not any(any(r) for r in records)
                selected = records[-1]
            else:
                assert not (len(records)>=2 and not any(records[0]) and not any(records[1]))
                selected = verify_history(records,cert,policy)
            pattern,bit = [0],0
            for parity in selected:
                bit ^= parity
                pattern.append(bit)
            assert pattern == row["repair_pattern"]
        if "known_source_correction" in row:
            assert list(m.source_correction(row["syndrome"])) == row["known_source_correction"]
        if "known_graph_correction" in row:
            roles=[f"a{v}" for v in range(5)]+[f"A{e}" for e in range(len(graph.edges))]
            generators=[]
            for v in range(5):
                generators.append((m.mask([v]+[5+e for e,ends in enumerate(graph.edges) if v in ends]),0))
            for e,(a,b) in enumerate(graph.edges):
                generators.append((0,m.mask((a,5+e,b))))
            assert list(pure_error(generators,row["syndrome"],len(roles)))==row["known_graph_correction"]
        if "data_recovery" in row:
            s = sum(bit << j for j,bit in enumerate(row["syndrome"]))
            expected = data_table().get(s)
            c = expected["correction"] if expected else None
            assert row["candidate_classes"] == (expected["classes"] if expected else 0)
            assert row["correction"] == (list(c) if c is not None else None)
        if "cycle_recovery" in row:
            expected = cycle_table(graph).get(tuple(row["syndrome"]))
            assert row["X_edges"] == (list(expected) if expected is not None else None)
        if "edge_reports" in row:
            if bare_stars:assert final_cycle_repairs==1
            expected = graph.decode(row["edge_reports"],2 if profile == "conservative" else None)
            assert row["decoded"] == expected
    if accepted:
        if screen_mode:
            assert screen_result is not None
            first=screen_results[0]
            outcome=first["terminal_screen_result"]
            if outcome=="syndrome_fallback":
                if screen_version==3:
                    assert any(r.get("history")=="terminal_screen_recovery" for r in rows)
                else:assert screen_history is not None
                assert any(r.get("data_recovery")=="terminal_screen_recovery" and r["correction"] is not None and
                           (screen_version==3 or r["syndrome"]==screen_history["selected_record"]) for r in rows)
            elif outcome=="flag_recovery":
                assert flag_repairs[first["episode"]]["correction"] is not None
            if screen_version in (2,3):
                assert screen_finish is not None and len(screen_begins)==len(screen_results)
                if screen_finish=="zero_accept":
                    assert len(screen_results)==1 and outcome=="zero_accept"
                elif screen_finish=="syndrome_certified":
                    assert screen_version==3 and len(screen_results)==1 and outcome=="syndrome_fallback"
                elif screen_finish in ("flag_verified","syndrome_verified"):
                    assert len(screen_results)==2 and screen_results[-1]["terminal_screen_result"]=="zero_accept"
                    assert outcome==("flag_recovery" if screen_finish=="flag_verified" else "syndrome_fallback")
                else:
                    assert screen_finish=="full_fallback" and len(screen_results)==2
                    last=screen_results[-1]
                    assert last["terminal_screen_result"]!="zero_accept"
                    if last["terminal_screen_result"]=="flag_recovery":
                        assert flag_repairs[last["episode"]]["correction"] is not None
                    assert any(r.get("history")=="terminal_screen_full" for r in rows)
                    assert any(r.get("data_recovery")=="terminal_screen_full" and r["correction"] is not None for r in rows)
            assert not any(r.get("history")=="terminal_recovery" for r in rows)
        if persistent:
            assert len([r for r in rows if r.get("persistent_coordinates_entered")])==1
            if manifest.get("persistent_version",1)>=2:
                assert next(r for r in rows if r.get("persistent_coordinates_entered"))["fused_with_enrichment"] is True
                assert next(i for i,r in enumerate(rows) if r.get("persistent_coordinates_entered"))<next(i for i,r in enumerate(rows) if "vertex_reports" in r)
            discards=[r for r in rows if r.get("persistent_graph_discard")]
            assert len(discards)==1 and discards[0]["cut_decoding"] is False
            assert discards[0]["data_byproduct"]=="already_applied_coherently_by_initial_V"
            assert len(discards[0]["untrusted_reports"])==len(graph.edges)
            assert all(b in (0,1) for b in discards[0]["untrusted_reports"])
            assert not any("edge_reports" in r or "final_cycle_flattening" in r or "terminal_screen_begin" in r for r in rows)
            assert not any(r.get("history")=="terminal_recovery" for r in rows)
            selected=[r for r in rows if "passing_persistent_round" in r]
            assert 3<=len(selected)<=5 and [r["passing_persistent_round"] for r in selected]==list(range(len(selected)))
            passes=0
            for i,r in enumerate(selected):
                prefix=f"persistent/{i}"
                zero=not any(checks[f"{prefix}/code/{a}/{j}"] for a in "ZX" for j in range(9))
                assert r["code_zero"]==zero and r["code_recovery_certified"]==(not zero)
                if not zero:
                    assert any(v.get("data_recovery")==f"{prefix}/data_recovery" and v["correction"] is not None for v in rows)
                assert all(f"{prefix}/star/{v}" in checks for v in range(1,5))
                bit=checks[f"{prefix}/transported_Gauss"]
                assert r["root_report"]==bit and r["passing"]==(bit==0)
                passes+=bit==0
                assert r["passes"]==passes and (passes<3 or i==len(selected)-1)
            assert passes==3
        if bare_stars and not persistent:
            assert final_cycle_repairs==1 and final_cycle_history is not None
            assert not any(r.get("check","").startswith("gauged/") and "/cycle/" in r.get("check","") for r in rows)
            assert all(r.get("extraction")=="bare_graph_X_star" for r in rows if "/star/" in r.get("check",""))
        assert len(flag_triggers)==len(flag_histories)==len(flag_repairs)
        assert len(root_triggers)==len(root_histories)==len(root_repairs)==len(root_graph_repairs)
        assert len(flag_triggers)+len(root_triggers)==data_epoch<=manifest.get("max_flag_recoveries",8)
        if manifest.get("verification_extraction")=="flags":
            if manifest.get("direct_cz_extraction")=="cat":
                assert all(not ("cat" in r) or (r["cat"].startswith("terminal/") and r["cat"].endswith("/U"))
                           for r in rows)
            else:assert not any("cat" in r for r in rows)
        if manifest.get("direct_cz_extraction")=="cat":
            assert manifest["route"]=="direct_cat"
            assert all(row.get("extraction")=="verified_cat_CZ" for row in rows if row.get("check","").endswith("/U"))
            assert not any("graph_parity_verification" in row for row in rows)
        if manifest.get("graph_verification") == "three_zero_Z_edge_scans" and manifest["route"] == "gauging":
            assert graph_attempts and graph_attempts[-1]["accepted"] and len(graph_attempts)<=3
        for kind in ("gauged","terminal"):
            if persistent:continue
            if kind=="terminal" and screen_mode:continue
            if kind == "gauged" and manifest["route"] == "direct_cat":
                continue
            if kind == "terminal" and any(row.get("history")=="terminal_recovery" for row in rows):
                recovery = [row for row in rows if row.get("data_recovery")=="terminal_recovery"]
                assert len(recovery)==1 and recovery[0]["correction"] is not None
                continue
            if profile == "conservative":
                for r in range(3):
                    prefix = f"gauged/{r}/code" if kind == "gauged" else f"terminal/{r}"
                    for axis in "ZX":
                        assert all(checks[f"{prefix}/{axis}/{s}"]==0 for s in range(9))
                    if kind == "gauged":
                        assert checks[f"gauged/{r}/root_Gauss"]==0
                        assert all(checks[f"gauged/{r}/cycle/{s}"]==0 for s in range(len(graph.cycles)))
                    elif manifest["route"] == "direct_cat":
                        assert checks[f"terminal/{r}/U"]==0
                continue
            selected = [row for row in rows if f"passing_{kind}_round" in row]
            assert 3<=len(selected)<=5 and [row[f"passing_{kind}_round"] for row in selected]==list(range(len(selected)))
            passes = 0
            for r,row in enumerate(selected):
                prefix = f"gauged/{r}/code" if kind == "gauged" else f"terminal/{r}"
                zero = all(checks[f"{prefix}/{axis}/{s}"]==0 for axis in "ZX" for s in range(9))
                passing = zero
                if kind == "gauged":
                    flat = True if bare_stars else all(checks[f"gauged/{r}/cycle/{s}"]==0 for s in range(len(graph.cycles)))
                    code_recovered = row.get("code_recovery_certified",False)
                    cycle_recovered = row.get("cycle_recovery_certified",False)
                    if code_recovered:
                        assert not zero and any(v.get("data_recovery")==f"gauged/{r}/data_recovery" and
                                                v["correction"] is not None for v in rows)
                    if cycle_recovered:
                        assert not flat and any(v.get("cycle_recovery")==r and v["X_edges"] is not None for v in rows)
                    passing = (zero or code_recovered) and (flat or cycle_recovered) and checks[f"gauged/{r}/root_Gauss"]==0
                    assert row["code_zero"]==zero
                    if bare_stars:
                        assert row["cycle_zero"] is None and row["cycle_policy"]=="deferred" and not cycle_recovered
                    else:assert row["cycle_zero"]==flat
                elif manifest["route"] == "direct_cat":
                    if row.get("code_recovery_certified",False):
                        assert any(v.get("data_recovery")==f"terminal/{r}/recovery" and v["correction"] is not None for v in rows)
                        passing = True
                    passing &= checks[f"terminal/{r}/U"]==0
                if "root_flag_recovery" in row:
                    ep=row["root_flag_recovery"]
                    assert ep in root_graph_repairs
                    assert root_triggers[ep]["check"]==(f"gauged/{r}/root_Gauss" if kind=="gauged" else f"terminal/{r}/U")
                    passing=False
                assert row["passing"]==passing
                passes += passing
                assert row["passes"]==passes and (passes<3 or r==len(selected)-1)
            assert passes==3
    return histories


def verify_run(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory/"manifest.json").read_text())
    rows = [json.loads(line) for line in (directory/"shots.jsonl").read_text().splitlines()]
    assert len({r["shot_index"] for r in rows})==len(rows)
    counts = Counter()
    for shot in rows:
        if shot["execution_status"] != "completed":
            assert shot["accepted"] is None
            counts["unresolved"] += 1
            continue
        assert isinstance(shot["accepted"],bool)
        detail = Path(shot["detail_directory"])
        records = json.loads((detail/"controller.json").read_text())
        counts["histories_checked"] += verify_controller(records,manifest,shot["accepted"])
        measurements = json.loads((detail/"measurements.json").read_text())
        noise = json.loads((detail/"noise.json").read_text())
        assert len(measurements)==shot["metrics"]["gate_counts"]["MZ"]
        assert len(noise["sampled"])==shot["metrics"]["sampled_noise_events"]
        assert len(noise["injected"])==shot["metrics"]["injected_fault_events"]
        assert Counter(e["channel"] for e in noise["sampled"])==shot["metrics"]["noise_event_counts"]
        flips = Counter(e["event"] for e in noise["sampled"] if e["flip_report"])
        flips.update(e["event"] for e in noise["injected"] if e.get("flip_report"))
        for event in measurements:
            assert event["reported"]==event["actual"] ^ (flips[event["event"]]%2)
        check_meters=defaultdict(deque)
        cat_readouts=defaultdict(deque)
        for event in measurements:
            if event["label"] in ("s","f0","f1","f2","f3","w"):
                check_meters[event["context"]].append(event["reported"])
            if event["label"].startswith("L"):
                cat_readouts[event["context"]].append(event["reported"])
        for row in records:
            if row.get("extraction")=="verified_cat_CZ":
                assert [cat_readouts[row["check"]].popleft() for _ in range(20)]==row["leaf_reports"]
            if row.get("extraction") not in ("rolling_flags","compact_flags","transported_Gauss","single_fault_flag","bare_graph_Z","bare_graph_X_star"):continue
            expected=row.get("flags",[])+[row["reported_parity"]]
            assert [check_meters[row["check"]].popleft() for _ in expected]==expected
        if manifest.get("graph_verification") == "three_zero_Z_edge_scans":
            graph_meters = {(e["context"],e["label"]):e["reported"] for e in measurements
                            if e["context"].startswith("graph/parity/")}
            expected_meters = {}
            for record in records:
                if "graph_parity_verification" not in record:continue
                attempt = record["graph_parity_verification"]
                for r,bits in enumerate(record["records"]):
                    for edge,bit in enumerate(bits):
                        expected_meters[(f"graph/parity/{attempt}/{r}/{edge}","w")] = bit
            assert graph_meters == expected_meters,"Graph parity decisions disagree with physical reports"
        for event in noise["sampled"]:
            if event["channel"] == "readout":
                assert not event["axes"] and len(event["targets"])==1
            else:
                assert len(event["axes"])==len(event["targets"])
                assert any(a!="I" for a in event["axes"])
                assert all(a in "IXYZ" for a in event["axes"])
        assert shot["metrics"]["gate_counts"]["PREP"]-len(measurements)==(20 if shot["accepted"] else 0)
        gates,opportunities=shot["metrics"]["gate_counts"],shot["metrics"]["channel_opportunities"]
        assert opportunities.get("two_qubit",0)==gates.get("CX",0)
        assert opportunities.get("T",0)==gates.get("T",0)+gates.get("TDG",0)
        assert opportunities.get("one_qubit",0)==sum(gates.get(g,0) for g in ("H","S","SDG","X","Y","Z"))
        assert opportunities.get("readout",0)==len(measurements)
        assert opportunities.get("preparation",0)==gates.get("PREP",0)
        assert opportunities.get("idle",0)==gates.get("IDLE",0)
        counts["completed"] += 1
        if shot["accepted"] and shot["diagnostic_status"] == "completed":
            path = Path(shot["output_reference"])
            assert sha256(path.read_bytes()).hexdigest()==shot["output_sha256"]
            with np.load(path,allow_pickle=False) as data:
                diagnostics = diagnose(data["indices"],data["amplitudes"])
            for key in ("decoded_target_fidelity","raw_physical_target_fidelity","probability_in_weight_two_lookup"):
                assert abs(diagnostics[key]-shot["diagnostics"][key])<1e-10
            counts["accepted_outputs_recomputed"] += 1
    expected = summarize(rows)
    saved = json.loads((directory/"summary.json").read_text())
    # Older snapshots may predate the diagnostic-completeness fields.
    for key,value in saved.items():
        if key != "finished":
            assert expected[key]==value,(key,expected[key],value)
    assert not expected["two_fault_prediction_violation_shots"]
    current = Path(__file__).resolve().parent
    source_match = all((current/name).exists() and sha256((current/name).read_bytes()).hexdigest()==value
                       for name,value in manifest["source_sha256"].items())
    snapshot=directory/"source_snapshot"
    snapshot_verified=None
    if snapshot.exists():
        snapshot_verified=all((snapshot/name).exists() and sha256((snapshot/name).read_bytes()).hexdigest()==value
                              for name,value in manifest["source_sha256"].items())
        assert snapshot_verified,"Saved source snapshot does not match manifest"
    return {"verified":True,**dict(counts),"source_tree_matches_saved_run":source_match,
            "saved_source_snapshot_verified":snapshot_verified,
            "scope":"saved report/control certificates, noise accounting, complex output diagnostics; not gate replay",
            "two_fault_prediction_violation_shots":expected["two_fault_prediction_violation_shots"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_run(args.directory),indent=2))
