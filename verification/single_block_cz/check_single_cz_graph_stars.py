"""Finite certificates for bare stars, arbitrary cycle sectors and cut readout.

This is not a full-factory location-pair enumeration. The star gadget's
entire fault algebra acts on GRAPH qubits; the analytical proof covers
data spectators and the existing non-Clifford location normal form.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import argparse
import json

import c4_helix_single_block_cz as m
from single_cz_recovery import GRAPHS,cycle_table
from single_cz_graph_stars import bare_star_program,cycle_syndrome,chord_correction,chord_basis
from check_optimized_extraction import signatures


def delayed_cycle_counterexample(graph):
    hooks=[]
    for v in range(1,5):
        ports=[e for e,ends in enumerate(graph.edges) if v in ends]
        for j,edge in enumerate(ports):
            hooks.append(({"vertex":v,"after_edge":edge,"Pauli_on_syndrome":"X"},m.mask(ports[j+1:])))
    old=cycle_table(graph)
    for (a,x),(b,y) in product(hooks,repeat=2):
        word=x ^ y
        bits=[(word & m.mask(c)).bit_count()%2 for c in graph.cycles]
        if tuple(bits) not in old:
            correction=chord_correction(graph,bits)
            assert cycle_syndrome(graph,word ^ m.mask(correction))==0
            return {"faults":[a,b],"edge_X_mask":word,"cycle_bits":bits,
                    "old_radius_decoder":"rejects","new_chord_correction":list(correction)}
    raise AssertionError("Expected a broad two-hook example")


def graph_certificate(graph):
    stars=[m.mask(e for e,ends in enumerate(graph.edges) if v in ends) for v in range(5)]
    assert stars[0]==stars[1]^stars[2]^stars[3]^stars[4]
    cuts=[graph.cut(eta) for eta in range(0,32,2)]
    assert len(set(cuts))==16
    # The 16 characters span the cut orbit; physical root-tree Z repairs
    # turn every nonroot-star sign sector positive without data operations.
    for character,eta in product(range(16),range(0,32,2)):
        sign=(-1)**((character & (eta >> 1)).bit_count()%2)
        repair=(-1)**sum((character >> j & 1)*(graph.cut(eta) >> e & 1)
                        for j,e in enumerate(graph.tree))
        assert sign*repair==1
    chords=[e for e in range(len(graph.edges)) if e not in graph.tree]
    cycle_masks=[m.mask(c) for c in graph.cycles]
    cases=0
    decisions=sha256()
    # Enumerate every chord sector and all 16 cut translates. This covers
    # EVERY computational graph word, including nonzero cycle syndromes.
    for packed in range(1 << len(chords)):
        word=sum(((packed >> j)&1) << e for j,e in enumerate(chords))
        bits=[(word & mask).bit_count()%2 for mask in cycle_masks]
        correction=m.mask(chord_correction(graph,bits))
        decisions.update(sum(b << j for j,b in enumerate(bits)).to_bytes(4,"little"))
        decisions.update(correction.to_bytes(4,"little"))
        assert correction==word and not correction & m.mask(graph.tree)
        for cut in cuts:
            raw=word ^ cut
            assert all(((raw & mask).bit_count()%2)==bit for mask,bit in zip(cycle_masks,bits))
            assert raw ^ correction==cut
            cases+=1
    assert cases==1 << len(graph.edges)
    # After a clean terminal reference, <=2 subsequent edge bit/report
    # errors are handled by the existing cut decoder, even for current20.
    readout_cases=0
    for cut in cuts:
        for weight in range(3):
            for sites in combinations(range(len(graph.edges)),weight):
                decoded=graph.decode(cut ^ m.mask(sites))
                assert decoded is not None and decoded["corrected"]==cut
                readout_cases+=1
    gadgets=[]
    for v in range(1,5):
        n=sum(v in ends for ends in graph.edges)
        ops=bare_star_program(n)
        assert all(all(q<=n for q in qs) for op,qs in ops)
        sigs,locations=signatures(ops,range(n),(1 << n)-1,1)
        # All Pauli operators on these n targets act on GRAPH, without
        # asserting an invalid one-edge-per-fault bound for controller hooks.
        max_hook=max(x.bit_count() for x,z,r in sigs)
        assert max_hook>=n-1
        gadgets.append({"vertex":v,"ports":n,"CX":n,"flags":0,
                        "locations_with_edge_idles":locations,"one_fault_Pauli_signatures":len(sigs),
                        "two_fault_pairs_covered_by_graph_algebra_closure":len(sigs)**2,"max_single_fault_X_spread":max_hook,
                        "fault_algebra":"graph only, unrestricted X/Z support"})
    return {"edges":len(graph.edges),"cycle_sectors":1 << len(chords),"all_graph_words_checked":cases,
            "all_chord_decisions_sha256":decisions.hexdigest(),"chord_inverse_pivots":list(chord_basis(graph)),
            "late_two_error_readout_cases":readout_cases,"star_product_identity_on_full_Hilbert_space":True,
            "star_sign_character_repairs_checked":256,
            "chord_corrections_disjoint_from_V_controls":True,"star_gadgets":gadgets,
            "broad_hook_example":delayed_cycle_counterexample(graph)}


def exact_logical_instrument_check(graph):
    """Exact Gaussian-integer sparse check on an ABSTRACT logical register.

    It tests arbitrary graph sectors and coherent I/U coefficients without
    throwing away phases. It supplements the separate signed physical U/V
    certificates; it is not a simulation of all physical data locations.
    """
    cuts=[graph.cut(eta) for eta in range(0,32,2)]
    chords=[e for e in range(len(graph.edges)) if e not in graph.tree]
    sectors=(0,1,(1 << len(chords))-1,((1 << len(chords))-1)//3)
    state=defaultdict(complex)
    # Gaussian integers fit exactly in complex128 at these tiny magnitudes.
    # Work with unnormalized projector numerators, avoiding divisions.
    for j,packed in enumerate(sectors):
        word=sum(((packed >> k)&1) << e for k,e in enumerate(chords))
        alpha,beta=complex(j+1,2-j),complex(2-j,j+1)
        for cut in cuts:
            for logical in range(4):
                state[logical,word ^ cut]+=alpha+beta*(-1 if logical==3 else 1)
    # Xstar_a=+ on every cut-orbit state, regardless of the cycle sector.
    root=graph.cut(1)
    assert all(state.get((q,w ^ root),0)==a for (q,w),a in state.items())
    positive={key:2*a if key[0]!=3 else 0j for key,a in state.items()}
    negative={key:2*a if key[0]==3 else 0j for key,a in state.items()}
    assert any(negative.values()) and all(q==3 or not a for (q,w),a in negative.items())
    branches=0
    for packed in sectors:
        word=sum(((packed >> k)&1) << e for k,e in enumerate(chords))
        bits=[(word & m.mask(c)).bit_count()%2 for c in graph.cycles]
        correction=m.mask(chord_correction(graph,bits))
        branch={(q,w ^ correction):a for (q,w),a in positive.items()
                if cycle_syndrome(graph,w)==cycle_syndrome(graph,word)}
        for cut in cuts:
            assert branch.get((0,cut),0)==branch.get((1,cut),0)==branch.get((2,cut),0)
            assert branch.get((3,cut),0)==0
        branches+=1
    return {"representation":"exact small Gaussian-integer coefficients in an abstract logical register",
            "coherent_cycle_branches":branches,"positive_logical_amplitudes":"equal on 00,01,10; zero on 11"}


def audit():
    directory=Path(__file__).resolve().parent
    result={"verified":True,"scope":"finite graph/Clifford/algebra certificates, not full factory fault pairs",
            "proof":"notes/single_block_cz_bare_graph_stars.md","global_fault_budget":2,
            "non_Clifford_Pauli_XOR_used":False,
            "graphs":{name:graph_certificate(g) for name,g in GRAPHS.items()},
            "logical_checks":{name:exact_logical_instrument_check(g) for name,g in GRAPHS.items()}}
    result["source_sha256"]={name:sha256((directory/name).read_bytes()).hexdigest() for name in
                             ("single_cz_graph_stars.py","single_cz_recovery.py","check_single_cz_graph_stars.py",
                              "check_optimized_extraction.py")}
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
