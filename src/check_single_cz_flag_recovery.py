"""Independent finite certificate for flag-dependent Pauli-data recovery.

Exhausts the stated one-block/exact-gadget two-fault envelope, NOT all
location pairs of the factory. Independent Clifford propagation comes from
check_optimized_extraction; independent class labels use logical commutation
bits, with explicit stabilizer-group membership for accepted corrections.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json

import c4_helix_single_block_cz as m
from check_optimized_extraction import signatures
from single_cz_flagged import flagged_program, flag_count, single_fault_pauli_program
from single_cz_compact_checks import data_program, data_flag_count
from single_cz_flag_recovery import local_signatures, recovery_table
from single_cz_recovery import STABILIZERS


def independent_syndrome(x, z):
    return sum((sum((x >> q) & 1 for q in r) % 2) << j for j, r in enumerate(m.SUPPORTS)) | sum(
        (sum((z >> q) & 1 for q in r) % 2) << (j + 9) for j, r in enumerate(m.SUPPORTS))


def logical_label(x, z):
    # Within a fixed syndrome, these four bits distinguish ALL Pauli classes.
    return tuple(sum((word >> q) & 1 for q in r) % 2
                 for word, r in ((x, m.X1), (x, m.X0), (z, m.X0), (z, m.X1)))


def independent_cases(axis, support, extraction="rolling_flags"):
    n=len(support)
    sigs,_=signatures(data_program(axis,n,extraction),range(n),(1 << n)-1,
                      (1 << data_flag_count(axis,n,extraction))-1)
    sigs.add((0,0,0))
    assert sigs == set(local_signatures(axis,n,extraction)), "Independent propagation disagrees"
    def lift(w):
        return sum(1 << q for j,q in enumerate(support) if w & (1 << j))
    full=[(lift(x),lift(z),f) for x,z,f in sorted(sigs)]
    for x,z,f in full:
        if f:
            for block in range(5):
                for a,b in product(range(16),repeat=2):
                    yield f,x ^ (a << (block*4)),z ^ (b << (block*4))
    for x,z,f in full:
        for a,b,g in full:
            if f ^ g:
                yield f ^ g,x ^ a,z ^ b


def check_shape(axis,support,extraction="rolling_flags"):
    expected=defaultdict(lambda:defaultdict(set))
    witnesses={}
    case_count=0
    # Materialize independent candidate sets once. No production candidate
    # generator, syndrome routine, or RREF class reducer is used here.
    for f,x,z in independent_cases(axis,support,extraction):
        s=independent_syndrome(x,z)
        label=logical_label(x,z)
        expected[f][s].add(label)
        witnesses.setdefault((f,s,label),(x,z))
        case_count+=1
    accepted=ambiguous=0
    accepted_corrections={}
    digest=sha256()
    for f,rows in sorted(expected.items()):
        table=recovery_table(axis,tuple(support),f,extraction)
        assert set(table)==set(rows)
        decisions=[]
        accepted_corrections[f]={}
        for s,labels in sorted(rows.items()):
            row=table[s]
            assert row["classes"]==len(labels)
            c=row["correction"]
            assert (c is not None)==(len(labels)==1)
            if c is not None:
                assert independent_syndrome(*c)==s
                for label in labels:
                    x,z=witnesses[f,s,label]
                    assert x ^ c[0] in STABILIZERS and z ^ c[1] in STABILIZERS
                accepted+=1
                accepted_corrections[f][s]=c
            else:
                ambiguous+=1
                reps=[witnesses[f,s,label] for label in labels]
                assert any((a ^ reps[0][0]) not in STABILIZERS or (b ^ reps[0][1]) not in STABILIZERS
                           for a,b in reps[1:])
            decisions.append([s,len(labels),c])
        digest.update(json.dumps([f,decisions],separators=(",",":")).encode())
    accepted_terms=0
    for f,x,z in independent_cases(axis,support,extraction):
        c=accepted_corrections[f].get(independent_syndrome(x,z))
        if c is not None:
            assert (x ^ c[0]) in STABILIZERS and (z ^ c[1]) in STABILIZERS
            accepted_terms+=1
    witness=None
    if 24 in expected and len(expected[24].get(0,()))>1:
        witness={"flag_word":24,"syndrome":0,
                 "errors":[list(witnesses[24,0,label]) for label in sorted(expected[24][0])],
                 "decision":"reject distinct logical classes"}
    return {"axis":axis,"support":list(support),"candidate_terms_with_duplicates":case_count,
            "flag_words":len(expected),"accepted_syndrome_decisions":accepted,
            "ambiguous_syndrome_decisions":ambiguous,"all_decisions_sha256":digest.hexdigest(),
            "accepted_physical_candidate_checks":accepted_terms,
            "ambiguity_example":witness}


def audit():
    shapes=[check_shape(axis,support) for axis in "XZ" for support in m.SUPPORTS]
    fallback=[]
    for axis,n in product("XZ",(4,8)):
        ops=single_fault_pauli_program(axis,n)
        sigs,locations=signatures(ops,range(n),(1 << n)-1,1)
        full=(1 << n)-1
        for x,z,f in sigs:
            costs=((x | z).bit_count(),((x ^ full if axis=="X" else x) |
                                       (z ^ full if axis=="Z" else z)).bit_count())
            assert f or min(costs)<=1
        fallback.append({"axis":axis,"ports":n,"remaining_fault_budget":1,
                         "locations_including_idles":locations,"Pauli_signatures":len(sigs),
                         "CX":sum(op=="CX" for op,qs in ops),"reported_flags":1,
                         "zero_flag_support_modulo_measured_stabilizer":1})
    directory=Path(__file__).resolve().parent
    return {"verified":True,"scope":"All actual 18 Pauli-data checks and every flag/syndrome in the stated envelope",
            "global_fault_budget":2,"external_fault_envelope":"arbitrary one-inner-block Pauli algebra",
            "full_factory_location_pair_enumeration":False,"T_gates_Pauli_propagated":False,
            "shapes":shapes,"one_remaining_fault_fallbacks":fallback,
            "source_sha256":{name:sha256((directory/name).read_bytes()).hexdigest()
            for name in ("single_cz_flag_recovery.py","single_cz_flagged.py",
                         "check_single_cz_flag_recovery.py","check_optimized_extraction.py")}}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
