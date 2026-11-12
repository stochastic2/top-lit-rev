"""Exploratory, CONDITIONAL located-block recovery certificate.

Assumption: all compatible data errors lie in B_b union B_c, where b is
certified and c is unknown. This script does NOT establish that any noisy
graph/flag record certifies b, and does NOT change a factory or decoder.
Pauli classes are checked independently by syndromes/logical commutation
and explicit stabilizer-group membership, not the production RREF reducer.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import argparse,json

import c4_helix_single_block_cz as m
from check_single_cz_flag_recovery import independent_syndrome,logical_label


def audit():
    h=[sum(1 << q for q in r) for r in m.SUPPORTS]
    stabilizers={0}
    for row in h:stabilizers|={s ^ row for s in tuple(stabilizers)}
    assert len(stabilizers)==512
    full=defaultdict(set)
    known=[defaultdict(dict) for _ in range(5)]
    cases=[]
    pair_checks=[]
    # Masks 0..7 are a complete set modulo each inner XXXX/ZZZZ pair.
    for a,b in combinations(range(5),2):
        pair={};count=0
        for xa,za,xb,zb in product(range(8),repeat=4):
            x=(xa << (4*a)) | (xb << (4*b));z=(za << (4*a)) | (zb << (4*b))
            syndrome=independent_syndrome(x,z);label=logical_label(x,z)
            if syndrome in pair:
                u,v=pair[syndrome]
                assert x ^ u in stabilizers and z ^ v in stabilizers
            else:pair[syndrome]=(x,z)
            full[syndrome].add(label)
            for k in (a,b):known[k][syndrome].setdefault(label,(x,z))
            cases.append((a,b,x,z,syndrome));count+=1
        pair_checks.append({"known_pair":[a,b],"reduced_Paulis":count,"syndromes":len(pair),
                            "unique_class_per_syndrome":True})
    ambiguous={s for s,labels in full.items() if len(labels)>1}
    assert len(ambiguous)==3855
    rows=[];digest=sha256()
    for block,table in enumerate(known):
        newly_unique=sorted(s for s in ambiguous if len(table.get(s,{}))==1)
        remaining=sum(len(labels)>1 for labels in table.values())
        assert (len(newly_unique),remaining)==(2895,960)
        checked=0
        for a,b,x,z,syndrome in cases:
            if block not in (a,b) or len(table[syndrome])!=1:continue
            u,v=next(iter(table[syndrome].values()))
            assert x ^ u in stabilizers and z ^ v in stabilizers
            checked+=1
        digest.update(json.dumps([block,newly_unique],separators=(",",":")).encode())
        rows.append({"certified_fault_block":block,"newly_unique_formerly_ambiguous_syndromes":len(newly_unique),
                     "remaining_ambiguous_syndromes":remaining,"accepted_candidate_checks":checked})
    x=sum(1 << q for q in (2,3));y=sum(1 << q for q in (8,11,12,15))
    s=independent_syndrome(x,0)
    assert s==independent_syndrome(y,0) and logical_label(x,0)!=logical_label(y,0)
    assert len(known[0][s])==1
    root=Path(__file__).resolve().parent
    return {"conditional_algebra_verified":True,"new_factory_implemented":False,
            "graph_or_flag_location_inference_proved":False,
            "hypothesis":"data error support in certified block b plus at most one other unknown inner block",
            "reduced_two_block_representatives":len(cases),"fixed_pair_checks":pair_checks,
            "full_unknown_pair_ambiguous_syndromes":len(ambiguous),"located_block_results":rows,
            "newly_unique_syndromes_sha256":digest.hexdigest(),
            "example":{"X_first":[2,3],"X_second":[8,11,12,15],"same_syndrome":s,
                       "difference":"logical X0","certified_block_0_restricted_classes":1},
            "acceptance_or_yield_prediction":False,
            "source_sha256":{n:sha256((root/n).read_bytes()).hexdigest() for n in
                             ("check_single_cz_located_block.py","check_single_cz_flag_recovery.py","c4_helix_single_block_cz.py")}}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path)
    args=p.parse_args();result=audit()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
