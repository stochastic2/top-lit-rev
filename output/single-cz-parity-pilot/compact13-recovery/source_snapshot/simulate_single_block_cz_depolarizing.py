"""Physical one-block CZ gauging with independently sampled depolarizing noise.

Default: compact13, two-logical-qubit CZ magic, recovery profile, Z edge
readout; r2=q=1e-3. T/Clifford/memory/preparation noise are exposed separately.
Existing SWAP simulators are unchanged. Computational failures are unresolved,
never counted as physical rejection. Each attempt uses an isolated process.
"""
from collections import Counter
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from time import monotonic,perf_counter
import argparse
import json
import math
import multiprocessing as mp
import resource
import sys
import traceback
import numpy as np

import c4_helix_single_block_cz as m
from run_single_block_cz_controller import RecordBackend
from single_cz_controller import SimulationController
from single_cz_runtime import QuantumBackend,NoiseModel
from single_cz_recovery import GRAPHS
from single_cz_diagnostics import diagnose


def write_json(path,value):
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,indent=2)+"\n")
    temporary.replace(path)


def noise_seed(seed):
    return int.from_bytes(sha256(f"single-block-CZ-noise:{seed}".encode()).digest()[:8],"big")


def clean_costs(source_extraction=None):
    def stage(ctx):
        if ctx.startswith("source/"):return "source/"+("checks" if "/certify/" in ctx else ctx.split("/")[1])
        if ctx.startswith("graph/"):return "graph/"+ctx.split("/")[1]
        if ctx.startswith("gauged/"):return "gauged/"+ctx.split("/")[2]
        if ctx.startswith("terminal/") or ctx.startswith("terminal_recovery"):
            return "terminal/U" if "/U" in ctx else "terminal/code"
        return ctx
    result = {}
    for graph in GRAPHS.values():
        for profile in ("conservative","recovery"):
            b = RecordBackend()
            extraction = source_extraction if profile == "recovery" else "verified_cat"
            outcome = SimulationController(b,graph=graph,profile=profile,source_extraction=extraction).run()
            assert outcome["accepted"]
            p = m.Program()
            p.ops = [m.Op(stage(ctx),name,qs) for ctx,(name,qs) in zip(b.contexts,b.ops)]
            result[graph.name+"/"+profile] = m.count_program(p)
    for profile in ("conservative","recovery"):
        b = RecordBackend()
        extraction = source_extraction if profile == "recovery" else "verified_cat"
        assert SimulationController(b,route="direct_cat",profile=profile,source_extraction=extraction).run()["accepted"]
        p = m.Program()
        p.ops = [m.Op(stage(ctx),name,qs) for ctx,(name,qs) in zip(b.contexts,b.ops)]
        result["direct_cat/"+profile] = m.count_program(p)
    return result


def simulate(seed=0,noise_seed_value=None,model=None,graph="compact13",profile="recovery",
             history_policy="triple",route="gauging",source_extraction=None,trace=None,progress=None,**limits):
    rt = QuantumBackend(seed=seed,noise_seed=noise_seed(seed) if noise_seed_value is None else noise_seed_value,
                        model=model,trace=trace,progress=progress,**limits)
    controller = SimulationController(rt,route=route,graph=GRAPHS[graph],profile=profile,
                                      history_policy=history_policy,source_extraction=source_extraction)
    result = controller.run()
    result.update(seed=seed,noise_seed=noise_seed(seed) if noise_seed_value is None else noise_seed_value,
                  graph=graph,profile=profile,history_policy=history_policy,route=route,
                  source_extraction=controller.source_extraction,metrics=rt.metrics())
    return result,rt


def _worker(connection,request):
    directory = Path(request["attempt_dir"])
    rt,trace_stream = None,None
    try:
        if request["trace"]:
            trace_stream = (directory/"events.jsonl").open("x")
        def trace(event):
            trace_stream.write(json.dumps(event)+"\n")
        def progress(b):
            write_json(directory/"progress.json",{"context":b.context,"metrics":b.metrics()})
        result,rt = simulate(seed=request["seed"],noise_seed_value=request["noise_seed"],
                             model=NoiseModel(**request["rates"]),graph=request["graph"],profile=request["profile"],
                             history_policy=request["history_policy"],route=request["route"],
                             source_extraction=request["source_extraction"],
                             trace=trace if trace_stream else None,progress=progress,**request["limits"])
        write_json(directory/"controller.json",result.pop("record"))
        write_json(directory/"measurements.json",rt.measurements)
        write_json(directory/"noise.json",{"sampled":rt.noise_events,"injected":rt.injected_events})
        result.update(execution_status="completed",diagnostic_status="pending" if result["accepted"] else "not_applicable",
                      shot_index=request["index"],detail_directory=str(directory),
                      output_reference=None)
        write_json(directory/"circuit_result.json",result)
        connection.send({"kind":"circuit_complete","result":result})
        if result["accepted"]:
            try:
                indices,values = rt.state.sparse_output(rt.data_labels)
                output = directory/"output.npz"
                np.savez_compressed(output,indices=indices,amplitudes=values)
                result["output_reference"] = str(output)
                result["output_sha256"] = sha256(output.read_bytes()).hexdigest()
                result["diagnostics"] = diagnose(indices,values)
                result["diagnostic_status"] = "completed"
            except Exception as exc:
                result.update(diagnostic_status="error",diagnostic_error=f"{type(exc).__name__}: {exc}",
                              diagnostic_traceback=traceback.format_exc())
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result["peak_rss_bytes"] = rss if sys.platform == "darwin" else rss*1024
        write_json(directory/"result.json",result)
        connection.send({"kind":"complete","result":result})
    except Exception as exc:
        result = {"execution_status":"resource_failure","accepted":None,"diagnostic_status":"unavailable",
                  "failure_kind":"capacity" if isinstance(exc,MemoryError) else "backend_error",
                  "error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()}
        if rt:
            result["last_metrics"] = rt.metrics()
        write_json(directory/"failure.json",result)
        connection.send({"kind":"failure","result":result})
    finally:
        if trace_stream:
            trace_stream.close()
        connection.close()


def isolated(request,timeout):
    context = mp.get_context("spawn")
    receiver,sender = context.Pipe(duplex=False)
    worker = context.Process(target=_worker,args=(sender,request))
    start = monotonic()
    worker.start()
    sender.close()
    circuit,final = None,None
    timed_out = False
    try:
        while monotonic()-start < timeout:
            if receiver.poll(.1):
                try:
                    message = receiver.recv()
                except EOFError:
                    break
                if message["kind"] == "circuit_complete":
                    circuit = message["result"]
                else:
                    final = message["result"]
                    break
            elif not worker.is_alive():
                break
        timed_out = final is None and monotonic()-start >= timeout
        if worker.is_alive() and final is None:
            worker.terminate()
        worker.join(3)
        if worker.is_alive():
            worker.kill()
            worker.join(3)
        directory = Path(request["attempt_dir"])
        if final is None and circuit is None and (directory/"circuit_result.json").exists():
            circuit = json.loads((directory/"circuit_result.json").read_text())
        if final is None and circuit:
            final = circuit
            final["diagnostic_status"] = "timeout" if timed_out else "worker_exit"
        if final is None:
            final = {"execution_status":"resource_failure","accepted":None,"diagnostic_status":"unavailable",
                     "failure_kind":"timeout" if timed_out else "worker_exit"}
            if (directory/"progress.json").exists():
                final["last_progress"] = json.loads((directory/"progress.json").read_text())
        final.update(shot_index=request["index"],seed=request["seed"],noise_seed=request["noise_seed"],
                     graph=request["graph"],profile=request["profile"],history_policy=request["history_policy"],
                     route=request["route"],wall_seconds=monotonic()-start,detail_directory=str(directory))
        return final
    finally:
        receiver.close()
        if worker.is_alive():
            worker.terminate()
            worker.join(3)


def wilson(k,n):
    if not n:
        return None
    z = 1.959963984540054
    denominator = 1+z*z/n
    center = (k/n+z*z/(2*n))/denominator
    half = z*math.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/denominator
    return [max(0,center-half),min(1,center+half)]


def summarize(records):
    done = [r for r in records if r["execution_status"] == "completed"]
    accepted = [r for r in done if r["accepted"]]
    assessed = [r for r in accepted if r.get("diagnostic_status") == "completed"]
    fid = [r["diagnostics"]["decoded_target_fidelity"] for r in assessed]
    gates = Counter()
    for r in done:
        gates.update(r["metrics"]["gate_counts"])
    violations = [r["shot_index"] for r in assessed
                  if r["metrics"]["sampled_noise_events"]+r["metrics"]["injected_fault_events"] <= 2
                  and not r["diagnostics"]["decoded_target_within_tolerance"]]
    return {"attempts":len(records),"completed":len(done),"unresolved":len(records)-len(done),
            "accepted":len(accepted),"rejected":len(done)-len(accepted),
            "acceptance_among_completed":len(accepted)/len(done) if done else None,
            "acceptance_Wilson95":wilson(len(accepted),len(done)),
            "acceptance_bounds_all_attempts":[len(accepted)/len(records),(len(accepted)+len(records)-len(done))/len(records)] if records else None,
            "rejection_counts":dict(Counter(r.get("reason") for r in done if not r["accepted"])),
            "failure_counts":dict(Counter(r.get("failure_kind") for r in records if r["execution_status"] != "completed")),
            "accepted_assessed":len(assessed),"accepted_diagnostics_missing":len(accepted)-len(assessed),
            "mean_decoded_fidelity":sum(fid)/len(fid) if fid else None,
            "mean_is_assessed_accepted_subset_only":True,
            "decoded_fidelity_bounds_all_known_accepted":[sum(fid)/len(accepted),
                (sum(fid)+len(accepted)-len(fid))/len(accepted)] if accepted else None,
            "minimum_decoded_fidelity":min(fid) if fid else None,
            "accepted_within_target_tolerance":sum(r["diagnostics"]["decoded_target_within_tolerance"] for r in assessed),
            "total_executed_gates_completed":dict(gates),
            "cost_per_accepted_completed":{k:v/len(accepted) for k,v in gates.items()} if accepted else None,
            "cost_is_matched_fidelity":False,"unresolved_can_bias_completed_subset":len(done) != len(records),
            "two_fault_prediction_violation_shots":violations,
            "ideal_success_probability":.75,"target":"encoded_two_logical_qubit_CZ_magic"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shots",type=int,default=8)
    parser.add_argument("--seed",type=int,default=0)
    parser.add_argument("--noise-seed",type=int)
    parser.add_argument("--graph",choices=tuple(GRAPHS),default="compact13")
    parser.add_argument("--profile",choices=("conservative","recovery"),default="recovery")
    parser.add_argument("--history-policy",choices=("triple","adaptive"),default="triple")
    parser.add_argument("--source-extraction",choices=("decoded_flags","verified_cat"))
    parser.add_argument("--route",choices=("gauging","direct_cat"),default="gauging")
    parser.add_argument("--two-qubit-infidelity",default="1e-3")
    parser.add_argument("--one-qubit-infidelity",default="0")
    parser.add_argument("--t-infidelity",default=None)
    parser.add_argument("--idle-infidelity",default="0")
    parser.add_argument("--preparation-flip-probability",default="0")
    parser.add_argument("--readout-flip-probability",default="1e-3")
    parser.add_argument("--attempt-timeout",type=float,default=60)
    parser.add_argument("--max-terms",type=int,default=4096)
    parser.add_argument("--max-factors",type=int,default=4096)
    parser.add_argument("--max-operations",type=int,default=200000)
    parser.add_argument("--trace",action="store_true")
    parser.add_argument("--cost-only",action="store_true")
    parser.add_argument("--output-dir",type=Path,default=Path("output/single-block-cz-noisy"))
    args = parser.parse_args()
    if args.profile == "conservative" and args.source_extraction == "decoded_flags":
        parser.error("The conservative profile retains verified-cat source extraction")
    if args.shots < 1 or min(args.max_terms,args.max_factors,args.max_operations) < 1 or not math.isfinite(args.attempt_timeout) or args.attempt_timeout <= 0:
        parser.error("Positive shots, capacities and finite timeout required")
    try:
        model = NoiseModel(**{k:getattr(args,k) for k in NoiseModel.__dataclass_fields__})
    except ValueError as exc:
        parser.error(str(exc))
    if args.output_dir.exists():
        parser.error("Choose a new output directory; saved runs are never overwritten")
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True)
    costs = clean_costs(args.source_extraction)
    write_json(directory/"clean-costs.json",costs)
    if args.cost_only:
        print(json.dumps(costs,indent=2))
        return
    graph = GRAPHS[args.graph]
    source_files = [Path(__file__)]+[Path(__file__).with_name(name) for name in
                    ("single_cz_state.py","single_cz_runtime.py","single_cz_controller.py",
                     "single_cz_recovery.py","single_cz_diagnostics.py","run_single_block_cz_controller.py",
                     "c4_helix_single_block_cz.py")]
    manifest = {"schema_version":1,"target":"encoded_two_logical_qubit_CZ_magic","edge_readout_basis":"Z",
                "graph_verification":"three_zero_Z_edge_scans",
                "noise":model.manifest(),"graph":asdict(graph),"cut_distance":graph.distance,
                "edge_decode_radius":2 if args.profile == "conservative" else graph.radius,
                "profile":args.profile,"history_policy":args.history_policy,"route":args.route,
                "terminal_policy":"certified_commuting_recovery" if args.profile=="recovery" and args.route=="gauging" else "passing_rounds",
                "source_extraction":args.source_extraction or ("decoded_flags" if args.profile == "recovery" else "verified_cat"),
                "shots_requested":args.shots,"seed":args.seed,"noise_seed_base":args.noise_seed,
                "noise_seed_rule":"noise_seed_base+k or SHA256(single-block-CZ-noise:born_seed)[:8] big-endian",
                "source_sha256":{p.name:sha256(p.read_bytes()).hexdigest() for p in source_files},
                "backend":"exact cyclotomic coherent sums of sparse phase-flat unitary data factors",
                "diagnostics":"complex128 output and perfect syndrome recovery; never used by controller",
                "limits":{"max_terms":args.max_terms,"max_factors":args.max_factors,"max_operations":args.max_operations},
                "attempt_timeout_seconds":args.attempt_timeout,"trace":args.trace}
    snapshot = directory/"source_snapshot"
    snapshot.mkdir()
    for path in source_files:
        (snapshot/path.name).write_bytes(path.read_bytes())
    manifest["python_version"] = sys.version
    manifest["numpy_version"] = np.__version__
    write_json(directory/"manifest.json",manifest)
    records = []
    with (directory/"shots.jsonl").open("x") as stream:
        for k in range(args.shots):
            attempt = directory/"attempts"/f"{k:06d}"
            attempt.mkdir(parents=True)
            seed = args.seed+k
            request = {"index":k,"seed":seed,"noise_seed":noise_seed(seed) if args.noise_seed is None else args.noise_seed+k,
                       "rates":model.manifest()["rates"],"attempt_dir":str(attempt),"graph":args.graph,
                       "profile":args.profile,"history_policy":args.history_policy,"route":args.route,
                       "source_extraction":manifest["source_extraction"],
                       "trace":args.trace,"limits":manifest["limits"]}
            record = isolated(request,args.attempt_timeout)
            records.append(record)
            stream.write(json.dumps(record)+"\n")
            stream.flush()
            write_json(directory/"summary.json",{**summarize(records),"finished":len(records)==args.shots})
            outcome = "accepted" if record.get("accepted") else record.get("reason",record.get("failure_kind"))
            print(f"attempt {k}: {outcome}; {record['wall_seconds']:.2f}s",flush=True)
    print(json.dumps(summarize(records),indent=2))


if __name__ == "__main__":
    main()
