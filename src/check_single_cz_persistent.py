"""Persistent coordinates: local opaque root cones, graph preparation, records.

No Pauli XOR through T. Exact finite certificates cover stated local support
and graph/record algebras; full arbitrary-fault composition is analytical.
"""
from collections import defaultdict,Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product,combinations
from pathlib import Path
import argparse,json

import c4_helix_single_block_cz as m
from single_cz_persistent import PERSISTENT_GRAPHS,transported_gauss_program,validate_persistent_graph,fused_initial_program
from check_single_cz_flags import opaque_signatures
from check_single_cz_graph_parity import graph_certificate,meter_certificate
from single_cz_recovery import rank,STABILIZERS


def root_certificate(graph):
    degree=sum(0 in e for e in graph.edges)
    ops=transported_gauss_program(degree)
    sigs,locations,cases=opaque_signatures(ops,20+degree)
    data=(1 << 20)-1
    def cost(local,hook):
        return min(((local | hook)&data).bit_count(),((local | (hook ^ data))&data).bit_count())
    assert all(f or cost(l,h)<=1 for l,h,f in sigs)
    groups=defaultdict(list)
    for l,h,f in sigs:groups[f].append((l,h))
    pairs=0
    for group in groups.values():
        for a,b in product(group,repeat=2):
            assert cost(a[0] | b[0],a[1] ^ b[1])<=2
            pairs+=1
    syndrome=20+degree
    last_data=max(i for i,(op,qs) in enumerate(ops) if any(q<20 for q in qs))
    graph_cx=[i for i,(op,qs) in enumerate(ops) if op=="CX" and qs[0]==syndrome and 20<=qs[1]<syndrome]
    assert len(graph_cx)==degree and min(graph_cx)>last_data
    assert sum(op=="MZ" for op,qs in ops)==22
    return {"root_degree":degree,"gates":dict(Counter(op for op,qs in ops)),
            "locations_with_all_port_idles":locations,"local_basis_cases":cases,
            "opaque_signatures":len(sigs),"accepted_equal_flag_pairs":pairs,
            "zero_flag_data_support_per_fault":1,"graph_support":"unrestricted",
            "normalization":"modulo U times root X star; graph factors absorbed in environment",
            "graph_ports_strictly_after_data":True,"T_propagation":"opaque one-site algebras, not Pauli XOR"}


def fused_certificate(graph):
    # Independent monomial action on every computational basis input.
    tests=0
    for sign,a,e,b in product((-1,1),range(2),range(2),range(2)):
        current=b;split_phase=0
        for control in (a,e):
            split_phase+=sign*current;current^=control;split_phase-=sign*current
        fused_bit=b ^ a ^ e
        fused_phase=sign*(b-fused_bit)
        assert current==fused_bit and split_phase%8==fused_phase%8
        tests+=1
    ops=fused_initial_program(graph)
    compiled_cases=0
    for q,sign in enumerate(m.SIGNS):
        v=q//4;target=f"D{q}"
        port=[(op,qs) for op,qs in ops if target in qs]
        for a,e,b in product(range(2),repeat=3):
            bits={target:b,f"a{v}":a}
            if v:bits[f"A{graph.tree[v-1]}"]=e
            phase=0
            for op,qs in port:
                if op=="CX":bits[qs[1]]^=bits[qs[0]]
                elif op in ("T","TDG"):phase+=(1 if op=="T" else -1)*bits[qs[0]]
                else:raise AssertionError(op)
            expected=b ^ a ^ (e if v else 0)
            assert bits[target]==expected and phase%8==(sign*(b-expected))%8
            compiled_cases+=1
    # Conservative forward participant light cones, not Pauli propagation.
    cones=[]
    for i,(op,qs) in enumerate(ops):
        cone=set(qs)
        for later,targets in ops[i+1:]:
            if cone.intersection(targets):cone.update(targets)
        blocks={int(q[1:])//4 for q in cone if q.startswith("D")}
        assert len(blocks)==1
        cones.append(sorted(blocks))
    assert sum(op=="CX" for op,qs in ops)==36
    assert sum(op in ("T","TDG") for op,qs in ops)==40
    return {"two_control_matrix_basis_cases":tests,"exact_phase_modulus":8,
            "actual_compiled_port_basis_cases":compiled_cases,
            "gate_location_cones_checked":len(cones),"maximum_data_blocks_per_fused_gate_fault":1,
            "gates":dict(Counter(op for op,qs in ops)),"control_Z_strings_commute_exactly":True,
            "method":"participant light cones and exact monomial phases; not XOR through T"}


def ideal_records(graph):
    """All 32 vertex X records x 16 valid ideal edge-Z disposal records.

    Unnormalized logical ++ amplitudes are Gaussian integers. Probabilities
    have exact denominator 4096 before reducing the two-t contribution.
    """
    validate_persistent_graph(graph)
    total=positive=Fraction(0);branches=0
    for reported in range(32):
        by_word=defaultdict(lambda:[0]*4)
        for t in range(32):
            word=graph.cut(t)
            phase=(-1)**((reported&t).bit_count()%2)
            repair=(-1)**sum(((reported >> v)&1)*((word >> e)&1) for v,e in enumerate(graph.tree,1))
            # V Omega has exponent t_a on ALL blocks, hence logical U**t_a.
            assert all(((t >> v)&1)^((word >> e)&1)==(t&1) for v,e in enumerate(graph.tree,1))
            for logical in range(4):
                by_word[word][logical]+=phase*repair*(-1 if logical==3 and t&1 else 1)
        assert len(by_word)==16
        positive_parity=reported.bit_count()%2==0
        expected=[2,2,2,0] if positive_parity else [0,0,0,2]
        for word,amps in by_word.items():
            assert amps==expected
            probability=Fraction(sum(a*a for a in amps),4096)
            total+=probability
            if positive_parity:positive+=probability
            branches+=1
    assert total==1 and positive==Fraction(3,4)
    return {"vertex_records":32,"edge_words_per_record":16,"joint_branches":branches,
            "total_probability":str(total),"positive_probability":str(positive),
            "positive_data_numerator":[2,2,2,0],"negative_data_numerator":[0,0,0,2],
            "edge_dependent_data_correction":False,"status":"exact finite certificate"}


def star_algebra(graph):
    stars=[m.mask(i for i,e in enumerate(graph.edges) if v in e) for v in range(5)]
    assert stars[0]==stars[1]^stars[2]^stars[3]^stars[4]
    assert rank(stars[1:])==4
    for character,eta in product(range(16),range(0,32,2)):
        sign=(-1)**((character & (eta >> 1)).bit_count()%2)
        repair=(-1)**sum(((character >> j)&1)*((graph.cut(eta) >> e)&1) for j,e in enumerate(graph.tree))
        assert sign*repair==1
    return {"nonroot_rank":4,"all_star_sign_repairs":256,"auxiliary_graph_dimension":1 << (len(graph.edges)-4),
            "root_star_product_identity_global":True,"cut_distance":graph.distance,
            "cut_distance_used_for_recovery":False}


def passing_certificate():
    cases=0
    for n in (3,4,5):
        for reports in product((0,1),repeat=n):
            passes=0;valid=True
            for j,b in enumerate(reports):
                passes+=b==0
                if j<n-1 and (passes==3 or passes+(4-j)<3):valid=False
            if not valid or passes!=3:continue
            for f in range(3):
                for bad in combinations(range(n),f):
                    good=[i for i,b in enumerate(reports) if b==0 and i not in bad]
                    assert good
                    cases+=1
    return {"accepted_report_patterns_and_bad_round_placements":cases,
            "global_fault_budget":2,"three_positive_complete_rounds_contain_a_clean_one":True}


def transversal_phase_search():
    """Restricted exhaustive search: odd-S supports inside X-stabilizer span.

    Necessary bilinear CSS conditions; does NOT rule out other gate families.
    """
    h=[m.mask(s) for s in m.SUPPORTS];logical=[m.mask(m.X0),m.mask(m.X1)]
    candidates=[p for p in STABILIZERS if all(not (p&a&b).bit_count()%2 for a in h for b in h+logical)
                and (p&logical[0]&logical[1]).bit_count()%2]
    assert candidates==[(1 << 20)-1]
    return {"stabilizer_supports_checked":len(STABILIZERS),"allowed_odd_S_supports":[[q for q in range(20) if p >> q&1] for p in candidates],
            "scope":"necessary conditions for the same diagonal-S / Pauli-stabilizer involution family; not all logical CZ representatives"}


def naive_root_counterexample():
    expectations=[]
    for logical in range(4):
        shift=(m.mask(m.X0) if logical&1 else 0) ^ (m.mask(m.X1) if logical&2 else 0)
        phases=[sum(m.SIGNS[q]*((b ^ shift) >> q&1) for q in range(4))%4 for b in STABILIZERS]
        assert set(phases)=={0,2}
        expectation=Fraction(sum(1 if p==0 else -1 for p in phases),len(phases))
        assert expectation==Fraction(1,2)
        expectations.append(str(expectation))
    return {"naive_operator":"U_a times root X star, incorrectly retained after V",
            "encoded_computational_expectations":expectations,
            "positive_probability_on_genuine_negative_logical_11":str(Fraction(3,4)),
            "scope":"counterexample to using the old root observable in the new frame; not a full-factory trajectory"}


def audit():
    from simulate_single_block_cz_depolarizing import clean_costs
    costs=clean_costs("decoded_flags","flags","cat","data","bare","intrinsic","compact_flags","persistent")
    root=Path(__file__).resolve().parent
    names=("single_cz_persistent.py","single_cz_controller.py","single_cz_flagged.py","single_cz_graph_stars.py",
           "single_cz_compact_checks.py","single_cz_recovery.py","check_single_cz_persistent.py","check_single_cz_flags.py",
           "check_single_cz_graph_parity.py","simulate_single_block_cz_depolarizing.py")
    return {"verified":True,"persistent_version":2,"graphs":{name:{"root":root_certificate(g),"fused_initial":fused_certificate(g),"preparation":graph_certificate(g,True),
            "ideal_records":ideal_records(g),"stars":star_algebra(g),"clean_costs":costs[name+"/recovery"]}
            for name,g in PERSISTENT_GRAPHS.items()},"resource_meter":meter_certificate(),
            "passing_rounds":passing_certificate(),"restricted_phase_support_search":transversal_phase_search(),
            "naive_untransported_root_counterexample":naive_root_counterexample(),
            "full_factory_location_pairs_enumerated":False,"arbitrary_fault_composition":"analytical",
            "terminal_recovery":"not required: only physical-site cones after the last clean combined round",
            "source_sha256":{name:sha256((root/name).read_bytes()).hexdigest() for name in names}}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path)
    args=parser.parse_args();result=audit()
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
