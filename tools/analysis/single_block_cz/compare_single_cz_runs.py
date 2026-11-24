"""Verify and aggregate a small single-block CZ run collection; no resampling."""
from pathlib import Path
import argparse
import json
from verify_single_block_cz_run import verify_run
from simulate_single_block_cz_depolarizing import write_json


def compare(root):
    root=Path(root).resolve()
    runs={}
    for manifest_path in sorted(root.glob("*/manifest.json")):
        directory=manifest_path.parent
        verified=verify_run(directory)
        manifest=json.loads(manifest_path.read_text())
        summary=json.loads((directory/"summary.json").read_text())
        records=[json.loads(line) for line in (directory/"shots.jsonl").read_text().splitlines()]
        key="direct_cat/"+manifest["profile"] if manifest["route"]=="direct_cat" else manifest["graph"]["name"]+"/"+manifest["profile"]
        costs=json.loads((directory/"clean-costs.json").read_text())[key]
        edge_distances=[]
        for shot in records:
            if shot.get("accepted"):
                decisions=json.loads((Path(shot["detail_directory"])/"controller.json").read_text())
                edge=next((r for r in decisions if "edge_reports" in r),None)
                if edge:edge_distances.append(edge["decoded"]["report_error"].bit_count())
        runs[directory.name]={"verified":verified,"manifest_reference":str(manifest_path),
                              "graph":manifest["graph"]["name"],"profile":manifest["profile"],"route":manifest["route"],
                              "graph_allocated":manifest.get("graph_allocated",manifest["route"]=="gauging"),
                              "verification_extraction":manifest.get("verification_extraction","cats"),
                              "direct_cz_extraction":manifest.get("direct_cz_extraction","auto"),
                              "flag_recovery":manifest.get("flag_recovery","reject"),
                              "graph_stars":manifest.get("graph_stars","flags"),
                              "data_checks":manifest.get("data_checks","rolling_flags"),
                              "gauss_frame":manifest.get("gauss_frame","round_trip"),
                              "conditional_checks":manifest.get("conditional_checks","legacy"),
                              "root_recovery":manifest.get("root_recovery","reject"),
                              "terminal_policy":manifest.get("terminal_policy"),
                              "max_flag_recoveries":manifest.get("max_flag_recoveries"),
                              "successful_flag_recoveries":summary.get("successful_flag_recoveries",0),
                              "source_extraction":manifest["source_extraction"],
                              "rates":manifest["noise"]["rates"],"attempts":summary["attempts"],
                              "accepted":summary["accepted"],"unresolved":summary["unresolved"],
                              "assessed_accepted":summary["accepted_assessed"],
                              "target_matches_within_tolerance":summary["accepted_within_target_tolerance"],
                              "mean_decoded_fidelity_of_assessed":summary["mean_decoded_fidelity"],
                              "acceptance_Wilson95":summary["acceptance_Wilson95"],
                              "sample_CX_per_accepted":(summary["cost_per_accepted_completed"] or {}).get("CX"),
                              "accepted_edge_distance_from_decoded_cut":edge_distances,
                              "clean_CX":costs["gates"]["CX"],"clean_T_TDG":costs["T_or_TDG"],"peak_live":costs["peak_live"]}
    return {"scope":"implementation pilot; not a statistically powered or matched-fidelity graph ranking",
            "all_saved_runs_verified":all(row["verified"]["verified"] for row in runs.values()),
            "graph_yield_advantage_established":False,"matched_noisy_fidelity_cost_established":False,"runs":runs}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=compare(args.root)
    write_json(args.output or args.root/"comparison.json",result)
    print(json.dumps({name:{k:row[k] for k in ("attempts","accepted","unresolved","clean_CX","peak_live",
                                               "target_matches_within_tolerance")} for name,row in result["runs"].items()},indent=2))
