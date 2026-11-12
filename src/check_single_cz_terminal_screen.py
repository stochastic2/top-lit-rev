"""Exhaustive finite certificate for the ordered terminal screen.

All partitions of the GLOBAL two-fault budget are covered: two upstream
one-inner-block algebras; one upstream block plus one screen location;
two screen locations. Screen locations include every gate, preparation,
measurement/report action, waiting-data/helper idle and final boundary.
The upstream block envelope is analytical, not a full-factory enumeration.
"""
from collections import defaultdict
from functools import lru_cache
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import argparse
import json

import c4_helix_single_block_cz as m
from check_optimized_extraction import signatures,propagate
from single_cz_terminal_screen import screen_program,screen_checks

H=tuple(m.mask(s) for s in m.SUPPORTS)
STABILIZERS={0}
for h in H:STABILIZERS|={x ^ h for x in tuple(STABILIZERS)}


def syndrome(x,z):
    return sum(((w & h).bit_count()%2) << (j+offset) for w,offset in ((x,0),(z,9)) for j,h in enumerate(H))


@lru_cache(maxsize=1)
def correctable_representatives():
    table={}
    for weight in range(3):
        for sites in combinations(range(20),weight):
            for axes in product(range(1,4),repeat=weight):
                x=sum((p&1) << q for p,q in zip(axes,sites))
                z=sum((p>>1) << q for p,q in zip(axes,sites))
                s=syndrome(x,z)
                if s in table:
                    a,b=table[s]
                    assert (x ^ a) in STABILIZERS and (z ^ b) in STABILIZERS
                else:table[s]=(x,z)
    return table


def correctable(x,z):
    c=correctable_representatives().get(syndrome(x,z))
    return c is not None and (x ^ c[0]) in STABILIZERS and (z ^ c[1]) in STABILIZERS


def incoming(readouts):
    groups=defaultdict(list)
    for block in range(5):
        for a,b in product(range(16),repeat=2):
            x,z=a << (4*block),b << (4*block)
            r=sum((((x if axis=="Z" else z) & H[j]).bit_count()%2) << pos for axis,j,pos in readouts)
            groups[r].append((x,z))
    return groups


def collect(order=None):
    ops,readouts=screen_program(order)
    size=sum(op=="MZ" for op,qs in ops)
    sigs,locations=signatures(ops,range(20),(1 << 20)-1,(1 << size)-1)
    sigs.add((0,0,0))
    return ops,readouts,sigs,locations


def audit():
    ops,readouts,sigs,locations=collect()
    assert set((a,j) for a,j,p in readouts)==set((a,j) for a in "ZX" for j in range(9))
    groups=incoming(readouts)
    # Independently check the input-syndrome wiring against full Clifford
    # propagation. No production recovery table or RREF reducer is used.
    for r,errors in groups.items():
        for x,z in errors:
            a,b,report=propagate(x,z,ops,0)
            assert (a,b,report)==(x,z,r)
    checked_external=0
    digest=sha256()
    for x,z,r in sorted(sigs):
        for a,b in groups.get(r,()):
            assert correctable(x ^ a,z ^ b),("upstream+screen",x,z,r,a,b)
            checked_external+=1
            digest.update(json.dumps([x,z,r,a,b],separators=(",",":")).encode())
    same_reports=defaultdict(list)
    for x,z,r in sigs:same_reports[r].append((x,z))
    checked_pairs=0
    for r,errors in sorted(same_reports.items()):
        for (x,z),(a,b) in product(sorted(errors),repeat=2):
            assert correctable(x ^ a,z ^ b),("two screen faults",x,z,r,a,b)
            checked_pairs+=1
            digest.update(json.dumps([r,x,z,a,b],separators=(",",":")).encode())
    raw_upstream=zero_upstream=0
    local={v:[(x << (4*v),z << (4*v),syndrome(x << (4*v),z << (4*v)))
              for x,z in product(range(16),repeat=2)] for v in range(5)}
    for v,w in combinations(range(5),2):
        for (x,z,s),(a,b,t) in product(local[v],local[w]):
            raw_upstream+=1
            if s==t:
                assert (x ^ a) in STABILIZERS and (z ^ b) in STABILIZERS
                zero_upstream+=1
    # Rank 3 of each outer restriction is the special C4-Helix fact used
    # by the analytical one-upstream/one-screen case split.
    outer_kernels=[]
    for v in range(5):
        rows=[(h >> (4*v)) & 15 for h in H[5:]]
        kernel=[x for x in range(16) if all((x & row).bit_count()%2==0 for row in rows)]
        assert kernel==[0,15]
        outer_kernels.append({"block":v,"outer_rows":rows,"kernel":kernel})
    directory=Path(__file__).resolve().parent
    result={"verified":True,"global_fault_budget":2,
            "scope":"all terminal-screen location signatures/pairs plus arbitrary upstream one/two-block Pauli envelopes",
            "full_factory_location_pairs_enumerated":False,"T_gates_Pauli_propagated":False,
            "screen_order":[list(c) for c in screen_checks()],"CX":sum(op=="CX" for op,qs in ops),
            "physical_measurements":sum(op=="MZ" for op,qs in ops),
            "locations_including_idles_and_boundary":locations,"one_location_signatures":len(sigs),
            "accepted_upstream_plus_screen_cases":checked_external,"accepted_two_screen_signature_pairs":checked_pairs,
            "raw_two_upstream_block_cases":raw_upstream,"accepted_two_upstream_cases":zero_upstream,
            "accepted_decisions_sha256":digest.hexdigest(),"outer_local_kernels":outer_kernels,
            "correctability_test":"explicit weight<=2 Pauli representatives and independent stabilizer-span membership"}
    result["source_sha256"]={name:sha256((directory/name).read_bytes()).hexdigest() for name in
                             ("single_cz_terminal_screen.py","single_cz_flagged.py","check_single_cz_terminal_screen.py",
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
