"""Finite SUPPORT certificates for flagged X/Z/W product measurements.

Non-Clifford ports are opaque one-site operator algebras, not Pauli XORs.
Controller-X faults append the exact local involution at each later port;
local target faults stay arbitrary operators on their port. Binary XOR is
used only for flag flips and products of commuting, disjoint involutions.
Cyclotomic coefficients and measurement conditioning are retained in the
analytical proof and the quantum simulator, not inferred from this audit.
"""
from collections import defaultdict,Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
from single_cz_flagged import flagged_program,flag_count,active_trace
from check_optimized_extraction import signatures
import c4_helix_single_block_cz as m


def opaque_signatures(ops,n):
    syndrome=n
    def tail(local,hook,x,z,report,start):
        meter_index=sum(op=="MZ" for op,qs in ops[:start])
        for op,qs in ops[start:]:
            if op=="CX":
                c,t=qs
                if t<n:
                    assert c==syndrome
                    hook^=((x>>syndrome)&1)<<t
                else:
                    x^=((x>>c)&1)<<t
                    z^=((z>>t)&1)<<c
            elif op=="H" and qs[0]>=n:
                q=qs[0]
                if ((x^z)>>q)&1:x^=1<<q;z^=1<<q
            elif op=="PREP":
                q=qs[0];x&=~(1<<q);z&=~(1<<q)
            elif op=="MZ":
                q=qs[0]
                report^=((x>>q)&1)<<meter_index
                meter_index+=1;x&=~(1<<q);z&=~(1<<q)
        return local,hook,report&((1<<flag_count_from_ops(ops))-1)
    def error(axes,qs,flip,start):
        local=x=z=0
        for p,q in zip(axes,qs):
            if q<n:
                if p:local|=1<<q
            else:
                x|=(p&1)<<q;z|=(p>>1)<<q
        # The current readout's index precedes tail propagation.
        report=flip<<sum(op=="MZ" for op,qs in ops[:start])
        return tail(local,0,x,z,report,start)
    result={(0,0,0)};live=set(range(n));locations=cases=0
    for i,(op,qs) in enumerate(ops):
        for q in live-set(qs):
            locations+=1
            for p in range(1,4):result.add(error((p,),(q,),0,i));cases+=1
        locations+=1
        for axes in product(range(4),repeat=len(qs)):
            for flip in range(2 if op=="MZ" else 1):
                result.add(error(axes,qs,flip,i if op=="MZ" else i+1));cases+=1
        if op=="PREP":live.update(qs)
        elif op=="MZ":live.difference_update(qs)
    return result,locations,cases


def flag_count_from_ops(ops):
    return sum(op=="MZ" for op,qs in ops)-1


def certificate(axes,signs=None):
    n=len(axes);full=(1<<n)-1;ops=flagged_program(axes,signs)
    sigs,locations,cases=opaque_signatures(ops,n)
    def cost(local,hook):
        return min((local|hook).bit_count(),(local|(hook^full)).bit_count())
    assert all(f or cost(local,hook)<=1 for local,hook,f in sigs)
    groups=defaultdict(list)
    for local,hook,flags in sigs:groups[flags].append((local,hook))
    pairs=0
    for group in groups.values():
        for a,b in product(group,repeat=2):
            assert cost(a[0]|b[0],a[1]^b[1])<=2,(axes,a,b)
            pairs+=1
    # Independently compare ordinary Pauli gadgets against the old explicit
    # symplectic propagator, using the actual H/CX/H decomposition for Z.
    clifford_pairs=None
    if len(set(axes))==1 and axes[0] in ("X","Z"):
        axis=axes[0]
        ordinary,_=signatures(ops,range(n),full,(1<<flag_count(axes))-1)
        def pauli_cost(x,z):
            return min((x|z).bit_count(),((x^full if axis=="X" else x)|(z^full if axis=="Z" else z)).bit_count())
        assert all(f or pauli_cost(x,z)<=1 for x,z,f in ordinary)
        groups=defaultdict(list)
        for x,z,f in ordinary:groups[f].append((x,z))
        clifford_pairs=0
        for group in groups.values():
            for a,b in product(group,repeat=2):
                assert pauli_cost(a[0]^b[0],a[1]^b[1])<=2
                clifford_pairs+=1
    return {"axes":"".join(axes),"W_signs":list(signs) if signs is not None else None,
            "locations_with_idles":locations,"local_basis_cases":cases,
            "support_signatures":len(sigs),"accepted_support_pairs":pairs,
            "independent_Pauli_pairs":clifford_pairs,"CX":sum(op=="CX" for op,qs in ops),
            "T_TDG":sum(op in ("T","TDG") for op,qs in ops),
            "flags":flag_count(axes),"accepted_support_per_fault_modulo_measured_product":1}


def audit():
    gadgets=[]
    for n in (4,5,6,8,10,12,20):
        for axis in "XZ":gadgets.append(certificate([axis]*n))
        trace=active_trace(n)
        for (a,i),(b,j) in product(trace,repeat=2):
            if a==b:assert abs(i-j)<=1 or (not a and {i,j}=={0,n})
    for n in (10,12):
        for signs in ((-1,1,-1,1)+(1,)*(n-4),(1,-1,1,-1)+(1,)*(n-4)):
            gadgets.append(certificate(["W"]*4+["X"]*(n-4),signs))
    for signs in (m.SIGNS,tuple(-s for s in m.SIGNS)):
        gadgets.append(certificate(["W"]*20,signs))
    return {"verified":True,"scope":"local zero-flag support certificates, NOT full-factory fault pairs",
            "proof":"notes/single_block_cz_flagged_verification_proof.md",
            "full_factory_fault_pair_enumeration":False,"gadgets":gadgets,
            "non_Clifford_treatment":"opaque port algebras and exact involution hooks; not a Pauli-XOR approximation"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path)
    args=p.parse_args();result=audit();directory=Path(__file__).resolve().parent
    result["source_sha256"]={name:sha256((directory/name).read_bytes()).hexdigest() for name in
                             ("single_cz_flagged.py","check_single_cz_flags.py","check_optimized_extraction.py")}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
