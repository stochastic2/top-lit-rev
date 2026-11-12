"""Symbolic finite certificate for the complete conservative root decoder.

Every reachable one/two-root-fault flag, every generated affine family and
its entire syndrome image are certified algebraically. This is not full
factory fault-pair enumeration. External cone completeness is analytical.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse,json

import c4_helix_single_block_cz as m
from single_cz_recovery import GRAPHS,STABILIZERS,rank
from single_cz_root_recovery import root_signatures,external_cases,family_specs,recovery_spaces,decision,_classword
from single_cz_flagged import flagged_program,dual_single_fault_pauli_program
from single_cz_graph_stars import bare_star_program
from check_single_cz_flags import opaque_signatures
from check_optimized_extraction import signatures
from check_single_cz_flag_recovery import independent_syndrome,logical_label
from single_cz_state import C8,SQRT2


def independent_word(p):
    x,z=p & ((1 << 20)-1),p >> 20
    return independent_syndrome(x,z) | (sum(b << j for j,b in enumerate(logical_label(x,z))) << 18)


def in_span(word,basis):
    pivots={}
    for value in basis:
        while value:
            k=value.bit_length()-1
            if k in pivots:value^=pivots[k]
            else:pivots[k]=value;break
    for k,row in sorted(pivots.items(),reverse=True):
        if word >> k&1:word^=row
    return word==0


def verify_space(space):
    original=[independent_word(g) for g in space.generators]
    rows=[]
    for syndrome,label,witness in space.rows:
        assert independent_word(witness)==syndrome | (label << 18)
        assert in_span(witness,space.generators)
        rows.append(syndrome | (label << 18))
    for label,witness in space.kernels:
        assert label and independent_word(witness)==label << 18
        assert in_span(witness,space.generators)
        rows.append(label << 18)
    assert rank(original)==rank(rows)
    assert all(in_span(word,rows) for word in original)
    # These identities certify ALL assignments, not only sampled syndromes.
    assert len(space.rows)==rank(word & ((1 << 18)-1) for word in original)
    assert bool(space.kernels)==(rank(original)>len(space.rows))
    base=independent_word(space.base)
    for witness in (0,)+space.generators:
        p=space.base ^ witness;s=independent_word(p)&((1 << 18)-1)
        result=space.solve(s)
        assert result is not None and result["ambiguous"]==bool(space.kernels)
        actual=independent_word(result["pauli"])
        assert actual & ((1 << 18)-1)==s and actual >> 18==result["logical"]
        assert in_span(result["pauli"] ^ space.base,space.generators)
        if not result["ambiguous"]:
            a,b=p & ((1 << 20)-1),p >> 20
            c,d=result["pauli"] & ((1 << 20)-1),result["pauli"] >> 20
            assert a ^ c in STABILIZERS and b ^ d in STABILIZERS
    # Enumerate the WHOLE independent affine image, including every report
    # ambiguity decision. Stabilizer-equivalent physical vectors are quotiented
    # by the independently computed 18-syndrome/4-logical label map.
    pivots={}
    for generator in space.generators:
        word=independent_word(generator);physical=generator
        while word:
            k=word.bit_length()-1
            if k in pivots:
                a,b=pivots[k];word^=a;physical^=b
            else:pivots[k]=(word,physical);break
    image=[(base,space.base)]
    for word,physical in pivots.values():image += [(a ^ word,b ^ physical) for a,b in tuple(image)]
    expected=defaultdict(int)
    for word,physical in image:expected[word & ((1 << 18)-1)] |= 1 << (word >> 18)
    for s,labels in expected.items():
        result=space.solve(s)
        assert result is not None and result["ambiguous"]==bool(labels & (labels-1))
        assert labels >> result["logical"]&1
    for word,p in image:
        s=word & ((1 << 18)-1);result=space.solve(s)
        if not result["ambiguous"]:
            delta=p ^ result["pauli"]
            assert delta & ((1 << 20)-1) in STABILIZERS and delta >> 20 in STABILIZERS
    return rank(original),len(image),len(expected)


def verify_graph(graph):
    nd=4 if graph else 20
    edges=[e for e,ends in enumerate(graph.edges) if 0 in ends] if graph else []
    ops=flagged_program(("W",)*nd+("X",)*len(edges),m.SIGNS[:nd]+(1,)*len(edges))
    independent,locations,cases=opaque_signatures(ops,nd+len(edges))
    actual=root_signatures(graph)
    assert set(actual)==independent
    star_checks=[]
    if graph:
        for v in range(1,5):
            es=[e for e,ends in enumerate(graph.edges) if v in ends];n=len(es)
            rows,_=signatures(bare_star_program(n),range(n),(1 << n)-1,1)
            reachable={sum(((x >> j)&1) << e for j,e in enumerate(es)) for x,z,f in rows}
            expected={m.mask(es[j:]) for j in range(n+1)} | {1 << e for e in es}
            assert reachable==expected
            star_checks.append({"vertex":v,"one_fault_X_masks":len(reachable),"matches_independent_Clifford_propagation":True})
    flag_words=sorted({a[2] ^ b[2] for a,b in product(actual,repeat=2)}-{0})
    seen=set();spaces=families=ambiguous=0;max_rank=0;image_cases=report_cases=0;digest=sha256()
    for f in flag_words:
        specs=family_specs(graph,f);families+=len(specs)
        table=recovery_spaces(graph,f,True)
        for c,rows in sorted(table.items()):
            for space in rows:
                spaces+=1;ambiguous+=bool(space.kernels)
                if space.key not in seen:
                    dimension,images,reports=verify_space(space)
                    max_rank=max(max_rank,dimension);image_cases+=images;report_cases+=reports
                    seen.add(space.key)
                digest.update(json.dumps([f,c,space.key],separators=(",",":")).encode())
    return {"one_root_support_signatures":len(actual),"root_locations_with_idles":locations,
            "root_basis_cases":cases,"reachable_nonzero_one_two_fault_flags":len(flag_words),
            "external_typed_cases":len(external_cases(graph)),"root_external_affine_specs":families,
            "cycle_indexed_affine_spaces":spaces,"spaces_with_proved_logical_ambiguity_kernel":ambiguous,
            "distinct_affine_images_certified":len(seen),"maximum_affine_image_rank":max_rank,
            "every_affine_image_class_checked":image_cases,"every_affine_report_decision_checked":report_cases,
            "all_affine_syndrome_images_covered_symbolically":True,"root_signature_match_independent":True,
            "bare_star_masks":star_checks,"all_families_sha256":digest.hexdigest()}


def phase_certificate():
    # sqrt(2) W_s|b> = (X - sY)|b>, exactly in Z[zeta8].
    for sign,b in product((-1,1),range(2)):
        left=C8.phase(sign*(2*b-1))*SQRT2
        right=C8(1)+C8.phase(6 if sign==1 else 2)*(-1 if b else 1)
        assert left==right
    return {"exact_local_W_Pauli_expansions":4,"field":"Z[zeta8]",
            "extension":"tensor products; all Pauli terms retained as independent allowed coefficients (conservative)",
            "Pauli_XOR_through_T":False}


def dual_certificate():
    rows=[]
    for axis,n in product("XZ",(4,8)):
        ops=dual_single_fault_pauli_program(axis,n);full=(1 << n)-1
        sigs,locations=signatures(ops,range(n),full,1)
        for x,z,f in sigs:
            assert f or min((x | z).bit_count(),((x ^ full if axis=="X" else x)|(z ^ full if axis=="Z" else z)).bit_count())<=1
        rows.append({"axis":axis,"ports":n,"one_fault_signatures":len(sigs),"locations_with_idles":locations,
                     "CX":sum(op=="CX" for op,qs in ops),"H":sum(op=="H" for op,qs in ops)})
    return rows


def audit():
    graphs={name:verify_graph(g) for name,g in GRAPHS.items()}
    graphs["direct_flagged_U"]=verify_graph(None)
    graph=GRAPHS["compact13"]
    joint=decision(graph,48,[0]*18,[0]*9,True);blind=decision(graph,48,[0]*18,[0]*9,False)
    assert joint["correction"]==(0,0) and blind["status"]=="ambiguous"
    root=Path(__file__).resolve().parent
    names=("single_cz_root_recovery.py","single_cz_controller.py","single_cz_flagged.py",
           "check_single_cz_root_recovery.py","check_single_cz_flags.py","check_optimized_extraction.py")
    return {"verified":True,"global_fault_budget":2,"graphs":graphs,"W_phases":phase_certificate(),
            "conditional_one_remaining_fault_programs":dual_certificate(),
            "graph_information_witness":{"flag_word":48,"data_syndrome":0,"cycle_syndrome":0,"joint":joint,"graph_blind":blind},
            "external_cone_completeness":"analytical stage-by-stage; NOT a full-factory location-pair enumeration",
            "full_factory_fault_pairs_enumerated":False,
            "source_sha256":{n:sha256((root/n).read_bytes()).hexdigest() for n in names}}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path)
    args=p.parse_args();result=audit()
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
