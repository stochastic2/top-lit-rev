"""Exact certificates for direct Z-parity graph-resource verification.

Scope: graph constraint/phase spans, every elementary local Pauli basis
fault of one bare parity meter (with idles and joint report errors),
the emitted clean graph programs, and global-two-fault scan references.
The arbitrary-fault factory composition remains an analytical proof.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json

from single_cz_recovery import GRAPHS,rank
from run_single_block_cz_controller import RecordBackend
from single_cz_controller import SimulationController


def meter_certificate():
    # Qubits 0..2 are arbitrary resource inputs; 3 is the fresh meter.
    # Ignore phases only for the SUPPORT certificate; the circuit is Clifford.
    ops = [("PREP",(3,))]+[("CX",(j,3)) for j in range(3)]+[("MZ",(3,))]
    def propagate(x,z,report,start):
        for name,qs in ops[start:]:
            if name == "CX":
                c,t=qs
                x ^= ((x >> c)&1) << t
                z ^= ((z >> t)&1) << c
            elif name == "MZ":
                report ^= (x >> 3)&1
                x &= 7;z &= 7
            else:
                x &= 7;z &= 7
        return x&7,z&7,report
    signatures={(0,0,0)}
    locations=0;cases=0
    live={0,1,2}
    for i,(name,qs) in enumerate(ops):
        for q in live-set(qs):
            locations+=1
            for p in range(1,4):
                signatures.add(propagate((p&1)<<q,(p>>1)<<q,0,i));cases+=1
        locations+=1
        # At readout, allow Pauli action AND arbitrary classical report flip
        # at the SAME faulty location. This includes a wrong actual outcome.
        for axes in product(range(4),repeat=len(qs)):
            for flip in range(2 if name=="MZ" else 1):
                x=sum((p&1)<<q for p,q in zip(axes,qs))
                z=sum((p>>1)<<q for p,q in zip(axes,qs))
                signatures.add(propagate(x,z,flip,i if name=="MZ" else i+1));cases+=1
        if name == "PREP":live.add(3)
        if name == "MZ":live.remove(3)
    assert all(x.bit_count()<=1 for x,z,r in signatures)
    pairs=0
    for a,b in product(signatures,repeat=2):
        assert (a[0]^b[0]).bit_count()<=2
        pairs+=1
    # Correlated phase spread really exists; we deliberately do not certify it away.
    assert any(z.bit_count()==3 for x,z,r in signatures)
    return {"locations_including_resource_idles":locations,"Pauli_and_report_cases":cases,
            "merged_signatures":len(signatures),"signature_pairs":pairs,
            "max_resource_X_support_per_fault":1,"phase_spread_can_reach_three_resources":True,
            "scope":"Clifford meter support audit; phases arbitrary in the analytical graph-span lemma"}


def graph_certificate(graph,persistent=False):
    e=len(graph.edges);n=5+e
    rows=[(1<<u)|(1<<v)|(1<<(5+j)) for j,(u,v) in enumerate(graph.edges)]
    assert rank(rows)==e
    words=[t|(graph.cut(t)<<5) for t in range(32)]
    assert len(set(words))==2**(n-rank(rows))==32
    assert all(not ((w&r).bit_count()%2) for w in words for r in rows)
    # Z on vertices generates the entire constrained subspace: Walsh characters
    # are orthogonal. Thus arbitrary amplitudes/environment coefficients are
    # retained, not merely stochastic diagonal phases.
    phase_tests=0
    for p,q in product(range(32),repeat=2):
        assert sum((-1)**(((p^q)&t).bit_count()) for t in range(32)) == (32 if p==q else 0)
        phase_tests+=1
    # U_v exponents after V Omega: t_v XOR (dt)_(a,v) = t_a, independently
    # for all four nonroot blocks; root exponent already equals t_a.
    for t in range(32):
        assert all(((t>>v)&1)^((graph.cut(t)>>edge)&1)==(t&1)
                   for v,edge in enumerate(graph.tree,1))
    b=RecordBackend();c=SimulationController(b,graph=graph,**(
        {"gauss_frame":"persistent","graph_stars":"bare","terminal_policy":"intrinsic"} if persistent else {}))
    c.graph()
    actual=b.ops
    expected=[]
    for v in range(5):expected.extend((("PREP",(f"a{v}",)),("H",(f"a{v}",))))
    expected.extend(("PREP",(f"A{j}",)) for j in range(e))
    for j,(u,v) in enumerate(graph.edges):
        expected.extend((("CX",(f"a{u}",f"A{j}")),("CX",(f"a{v}",f"A{j}"))))
    expected.append(("BOUNDARY",()))
    for scan in range(3):
        for j,(u,v) in enumerate(graph.edges):
            expected.append(("PREP",("w",)))
            expected.extend(("CX",(q,"w")) for q in (f"a{u}",f"A{j}",f"a{v}"))
            expected.append(("MZ",("w",)))
        expected.append(("BOUNDARY",()))
    assert actual==expected
    counts=Counter(op for op,qs in actual)
    assert counts["CX"]==11*e and counts["PREP"]==5+4*e and counts["MZ"]==3*e
    return {"Z_rank":e,"constrained_dimension":32,"Walsh_inner_products":phase_tests,
            "coordinate_patterns":32,"emitted_program_matches_independent_list":True,
            "clean_gates":dict(counts),"verification_helpers":1}


def audit():
    clean_patterns=[]
    for counts in product(range(3),repeat=3):
        if sum(counts)>2:continue
        clean={r for r,n in enumerate(counts) if n==0}
        assert clean
        last=max(clean)
        late=sum(counts[last+1:])
        assert late<=2 and late<=sum(counts)
        clean_patterns.append({"fault_counts_by_scan":counts,"last_clean_scan":last,
                               "max_late_bit_error_sites":late})
    return {"verified":True,"graph_policy":"three_zero_Z_edge_scans",
            "full_factory_fault_pair_enumeration":False,"meter":meter_certificate(),
            "graphs":{name:graph_certificate(g) for name,g in GRAPHS.items()},
            "scan_fault_placements":clean_patterns,
            "proof":"notes/full_procedure_single_block_cz_proof.md#c3-known-source-and-graph-verification"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit()
    source=Path(__file__).resolve().parent
    result["source_sha256"]={name:sha256((source/name).read_bytes()).hexdigest() for name in
                             ("check_single_cz_graph_parity.py","run_single_block_cz_controller.py",
                              "single_cz_controller.py","single_cz_recovery.py")}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
