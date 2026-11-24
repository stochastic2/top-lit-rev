"""Finite certificates for compact Pauli gadgets and their recovery tables.

Exhaustive local Clifford signatures/pairs and accepted ambiguity decisions;
NOT full-factory fault pairs. The upstream non-Clifford block envelope is
analytical. Dense ideal-instrument checks are numerical spot checks only.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import numpy as np

import c4_helix_single_block_cz as m
from check_optimized_extraction import signatures
from check_single_cz_flag_recovery import check_shape
from single_cz_compact_checks import compact_pauli_program, data_flag_count
from single_cz_recovery import physical_table, remainder, syndrome


def local_certificate(axis,n):
    ops=compact_pauli_program(axis,n)
    full=(1 << n)-1
    nf=data_flag_count(axis,n,"compact_flags")
    sigs,locations=signatures(ops,range(n),full,(1 << nf)-1)
    sigs.add((0,0,0))
    def cost(x,z):
        return min((x | z).bit_count(),((x ^ full if axis=="X" else x) |
                                       (z ^ full if axis=="Z" else z)).bit_count())
    assert all(f or cost(x,z)<=1 for x,z,f in sigs)
    groups=defaultdict(list)
    for x,z,f in sigs:groups[f].append((x,z))
    pairs=0
    for f,errors in sorted(groups.items()):
        for (x,z),(a,b) in product(errors,repeat=2):
            assert cost(x ^ a,z ^ b)<=2,(axis,n,f,x,z,a,b)
            pairs+=1
    return {"axis":axis,"ports":n,"gates":dict(Counter(op for op,qs in ops)),
            "reported_flags":nf,"peak_helpers":1+nf,"locations_including_idles":locations,
            "one_location_signatures":len(sigs),"accepted_signature_pairs":pairs,
            "single_zero_flag_support_bound":1,"two_zero_flag_support_bound":2,
            "modulo":"measured code stabilizer","same_location_pairs_overincluded":True}


def dense_instrument(axis,n):
    """Independent complex-vector spot check of EVERY ideal report branch."""
    ops=compact_pauli_program(axis,n)
    nf=data_flag_count(axis,n,"compact_flags")
    rng=np.random.default_rng(712+n)
    data=rng.normal(size=1 << n)+1j*rng.normal(size=1 << n)
    data/=np.linalg.norm(data)
    state=np.zeros(1 << (n+1+nf),dtype=complex)
    state[:1 << n]=data
    indices=np.arange(len(state))
    for op,qs in ops:
        if op in ("PREP","MZ"):continue  # all helpers start zero; readouts defer
        if op=="CX":
            c,t=qs
            permutation=indices ^ (((indices >> c)&1) << t)
            state=state[permutation]
        elif op=="H":
            mask=1 << qs[0]
            zero=indices[(indices & mask)==0];one=zero | mask
            a,b=state[zero].copy(),state[one].copy()
            state[zero]=(a+b)/np.sqrt(2);state[one]=(a-b)/np.sqrt(2)
        else:raise AssertionError(op)
    qdata=data[np.arange(1 << n) ^ ((1 << n)-1)] if axis=="X" else (
        data*np.array([(-1)**i.bit_count() for i in range(1 << n)]))
    maximum=0.
    for helper_word in range(1 << (nf+1)):
        branch=state[helper_word << n:(helper_word+1) << n]
        expected=(data+(-1)**helper_word*qdata)/2 if helper_word<2 else np.zeros_like(data)
        maximum=max(maximum,float(np.max(np.abs(branch-expected))))
    assert maximum<1e-12
    return {"axis":axis,"ports":n,"all_ideal_branches":1 << (nf+1),
            "maximum_absolute_error":maximum,"status":"numerical spot check"}


def outer_omission_witnesses():
    """Why broad two-block envelopes do not justify skipping outer checks."""
    correctable={(remainder(x),remainder(z)) for x,z in physical_table().values()}
    witnesses={}
    outer=[("Z",j,j) for j in range(5,9)]+[("X",j,j+9) for j in range(5,9)]
    for a,b in combinations(range(5),2):
        # Modulo the inner XXXX/ZZZZ stabilizers, masks 0..7 suffice.
        for xa,za,xb,zb in product(range(8),repeat=4):
            x=(xa << (4*a)) | (xb << (4*b));z=(za << (4*a)) | (zb << (4*b))
            s=syndrome(x,z)
            if not s or s & (s-1) or (remainder(x),remainder(z)) in correctable:continue
            for axis,j,bit in outer:
                if s==1 << bit:
                    witnesses.setdefault(f"{axis}{j}",{"X":[q for q in range(20) if x >> q & 1],
                                                       "Z":[q for q in range(20) if z >> q & 1],
                                                       "only_nonzero_syndrome_bit":bit})
    assert len(witnesses)==8
    return {"scope":"broad arbitrary two-inner-block envelope; not asserted actual two-location reachability",
            "each_single_outer_omission_fails_existing_zero_accept_contract":witnesses}


def audit():
    local=[local_certificate(axis,n) for axis,n in product("XZ",(4,8))]
    dense=[dense_instrument(axis,n) for axis,n in product("XZ",(4,8))]
    recovery=[check_shape(axis,support,"compact_flags") for axis in "XZ" for support in m.SUPPORTS]
    from simulate_single_block_cz_depolarizing import clean_costs
    costs=clean_costs("decoded_flags","flags","cat","data","bare","screen","compact_flags")
    root=Path(__file__).resolve().parent
    return {"verified":True,"global_fault_budget":2,"local_gadgets":local,
            "ideal_instrument_spot_checks":dense,"recovery_tables":recovery,
            "outer_check_omission_audit":outer_omission_witnesses(),
            "clean_costs":{k:costs[k] for k in ("compact13/recovery","current20/recovery","direct_cat/recovery")},
            "full_factory_location_pairs_enumerated":False,"T_gates_Pauli_propagated":False,
            "source_sha256":{name:sha256((root/name).read_bytes()).hexdigest() for name in
                             ("single_cz_compact_checks.py","single_cz_flag_recovery.py",
                              "single_cz_controller.py","single_cz_state.py","single_cz_runtime.py",
                              "check_single_cz_compact_checks.py",
                              "check_single_cz_flag_recovery.py","check_optimized_extraction.py")}}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path)
    args=p.parse_args();result=audit()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
