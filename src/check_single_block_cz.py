"""Exact finite certificates for the one-block CZ construction (standard library).

Not an enumeration of faults in the full factory. The analytical composition
proof covers arbitrary local faults. This checks its finite code, graph,
cat-bit-spread, and signed monomial premises, independently of a state simulator.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from hashlib import sha256
import argparse
import ast
import json
import re

import c4_helix_single_block_cz as schedule
from check_single_cz_graph_parity import audit as graph_parity_audit

ROOT = Path(__file__).resolve().parents[1]


def span(rows):
    result = {0}
    for row in rows:
        result |= {v ^ row for v in tuple(result)}
    return result


def basis(rows):
    result = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in result:
                row ^= result[p]
            else:
                result[p] = row
                break
    return result


def source_table():
    """Read authoritative TeX table, rather than trusting schedule constants."""
    tex = (ROOT / "arXiv-2609.03194v1/appendix.tex").read_text()
    section = tex.split(r"\begin{minipage}{0.6\textwidth}")[1].split(r"\end{minipage}")[0]
    rows = []
    for line in section.splitlines():
        fields = line.split("&")
        if len(fields) >= 21 and fields[0].strip().startswith("$"):
            letters = [re.sub(r"[^XYZ]", "", s) for s in fields[:20]]
            rows.append((sum(("X" in s or "Y" in s) << q for q, s in enumerate(letters)),
                         sum(("Z" in s or "Y" in s) << q for q, s in enumerate(letters))))
    assert len(rows) == 24, len(rows)
    assert [r[0] for r in rows[:9]] == list(map(schedule.mask, schedule.SUPPORTS))
    assert [r[1] for r in rows[10:19]] == list(map(schedule.mask, schedule.SUPPORTS))
    assert rows[20:] == [(schedule.mask(schedule.X0), 0), (schedule.mask(schedule.X1), 0),
                        (0, schedule.mask(schedule.Z0)), (0, schedule.mask(schedule.Z1))]
    return rows


def code_certificate():
    rows = source_table()
    current = ast.parse((ROOT / "src/c4_helix_noiseless.py").read_text())
    current_values = {node.targets[0].id: ast.literal_eval(node.value) for node in current.body
                      if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                      and node.targets[0].id in ("CHECK_SUPPORTS", "LOGICAL_X0", "LOGICAL_Z0")}
    assert current_values == {"CHECK_SUPPORTS": schedule.SUPPORTS,
                              "LOGICAL_X0": schedule.X0, "LOGICAL_Z0": schedule.Z0}
    h = [x for x, z in rows[:9]]
    stabilizers = span(h)
    assert len(stabilizers) == 512
    assert rows[9][0] in stabilizers and rows[19][1] in stabilizers
    assert [x for x, z in rows[:10]] == [z for x, z in rows[10:20]]
    assert all((a & b).bit_count() % 2 == 0 for a in h for b in h)
    logicals = [schedule.mask(r) for r in (schedule.X0, schedule.X1, schedule.Z0, schedule.Z1)]
    assert [[(x & z).bit_count() % 2 for z in logicals[2:]] for x in logicals[:2]] == [[1, 0], [0, 1]]
    dual = span(h + logicals[:2])
    assert len(dual) == 2048
    distance = min(w.bit_count() for w in dual - stabilizers)
    assert distance == 6
    def syn(x, z):
        return sum(((x & row).bit_count() % 2) << j for j, row in enumerate(h)) | sum(
            ((z & row).bit_count() % 2) << (9+j) for j, row in enumerate(h))
    def is_stabilizer(x, z):
        return x in stabilizers and z in stabilizers
    block_rows = []
    for blocks in combinations(range(5), 2):
        positions = [q for b in blocks for q in range(4*b, 4*b+4)]
        words = [sum(((w >> j) & 1) << q for j, q in enumerate(positions)) for w in range(256)]
        normalizers = [(x, z) for x, z in product(words, repeat=2) if syn(x, z) == 0]
        assert len(normalizers) == 16
        assert all(is_stabilizer(x, z) for x, z in normalizers)
        block_rows.append({"blocks": blocks, "Paulis_tested": 65536,
                           "normalizers": len(normalizers), "nontrivial_logicals": 0})
    # All radius-two physical errors; equal syndrome must mean stabilizer-equivalence.
    table = {}
    tests = 0
    for weight in range(3):
        for sites in combinations(range(20), weight):
            for axes in product(range(1, 4), repeat=weight):
                x = sum((a & 1) << q for q, a in zip(sites, axes))
                z = sum((a >> 1) << q for q, a in zip(sites, axes))
                s = syn(x, z)
                if s in table:
                    a, b = table[s]
                    assert is_stabilizer(a ^ x, b ^ z)
                else:
                    table[s] = x, z
                tests += 1
    # A real ambiguity of unknown-two-block recovery, deliberately NOT accepted.
    e = schedule.mask((2, 3))
    f = schedule.mask((8, 11, 12, 15))
    assert syn(e, 0) == syn(f, 0) and not is_stabilizer(e ^ f, 0)
    # Signed encoder state: independent direct simulation of H and CX on basis amplitudes.
    pivots, gates = schedule.rref_encoder()
    amplitudes = {0: 1}
    for q in pivots:
        updated = defaultdict(int)
        for b, a in amplitudes.items():
            low = b & ~(1 << q)
            updated[low] += a
            updated[low | (1 << q)] += a * (-1 if b >> q & 1 else 1)
        amplitudes = dict(updated)
    for c, t in gates:
        amplitudes = {b ^ (((b >> c) & 1) << t): a for b, a in amplitudes.items()}
    assert amplitudes == {b: 1 for b in dual}
    for j in range(20):
        bits = [int(j == k) for k in range(20)]
        x, z = schedule.source_correction(bits)
        assert [((x & b).bit_count() + (z & a).bit_count()) % 2
                for a, b in schedule.source_generators()] == bits
    # Native and corrected phases over ALL computational Z-check strings.
    eps = (-1, 1, 1, -1)*5
    native, canonical = Counter(), Counter()
    for b in dual:
        l0, l1 = ((b & z).bit_count() % 2 for z in logicals[2:])
        exp = sum(e*((b >> q) & 1) for q, e in enumerate(eps)) % 4
        assert exp == (2*(l0*l1 ^ l1)) % 4
        shifted = b ^ logicals[0]
        assert sum(e*((shifted >> q) & 1) for q, e in enumerate(eps)) % 4 == 2*l0*l1
        expw = sum(s*(2*((b >> q) & 1)-1) for q, s in enumerate(schedule.SIGNS)) % 8
        assert expw == 4*l0*l1
        assert b ^ ((1 << 20)-1) in dual
        native[str((l0, l1, exp))] += 1
        canonical[str((l0, l1, expw))] += 1
    # Commutator signs on every local block of every X check.
    decorations = []
    for r in schedule.SUPPORTS:
        local = []
        for v in range(5):
            support = tuple(q for q in r if q//4 == v)
            assert len(support) % 2 == 0
            k = (-1)**(len(support)//2)
            for q in support:
                k *= schedule.SIGNS[q]
            local.append({"vertex": v, "support": support, "sign": k,
                          "path": [] if v == 0 else [v-1]})
            # Independent local computational action of U_v X_R U_v X_R.
            for b in range(16):
                word, phase = b, 0
                rlocal = sum(1 << (q % 4) for q in support)
                for kind in ("X_R", "U_v", "X_R", "U_v"):
                    if kind == "X_R":
                        word ^= rlocal
                    else:
                        phase += sum(schedule.SIGNS[4*v+j]*(2*((word >> j) & 1)-1)
                                     for j in range(4))
                        word ^= 15
                assert word == b
                assert phase % 8 == (4*(int(k == -1) + (b & rlocal).bit_count())) % 8
        assert product_sign(row["sign"] for row in local) == 1
        decorations.append(local)
    return {"authoritative_TeX_and_current_implementation_match": True,
            "CSS_rank_each": 9, "source_rank": 20, "code_distance": distance,
            "encoder_H": len(pivots), "encoder_CX": len(gates), "signed_source_terms": len(amplitudes),
            "source_right_inverse_basis_tests": 20, "two_block_detection": block_rows,
            "radius_two_errors": tests, "radius_two_syndromes": len(table),
            "radius_two_ambiguous_classes": 0,
            "radius_two_recovery_table": {str(s): [x, z] for s, (x, z) in sorted(table.items())},
            "unsafe_unknown_two_block_example": {"E_X": [2, 3], "F_X": [8, 11, 12, 15],
                                                  "same_syndrome": syn(e, 0), "difference": "logical_X0"},
            "native_phase_counts": dict(native), "canonical_phase_counts": dict(canonical),
            "X_decorations": decorations}, dual


def product_sign(values):
    result = 1
    for value in values:
        result *= value
    return result


def graph_certificate():
    cuts = {schedule.cut(t) for t in range(32)}
    cm = list(map(schedule.mask, schedule.CYCLES))
    assert len(cuts) == 16 and len(basis(cm)) == 9
    assert all((c & cyc).bit_count() % 2 == 0 for c in cuts for cyc in cm)
    assert min(c.bit_count() for c in cuts if c) == 5
    h = min(Fraction(schedule.cut(t).bit_count(), min(t.bit_count(), 5-t.bit_count())) for t in range(1, 31))
    assert h >= 1
    decisions = Counter()
    decision_table = []
    for word in range(1 << 13):
        result = schedule.decode_edges(word)
        candidates = [c for c in cuts if (c ^ word).bit_count() <= 2]
        assert len(candidates) <= 1
        assert (result is not None) == bool(candidates)
        if result:
            assert result["corrected"] == candidates[0]
            decisions["accept"] += 1
            decision_table.append(result["eta"])
        else:
            decisions["reject"] += 1
            decision_table.append(-1)
    weight_five = [t for t in range(0, 32, 2) if schedule.cut(t).bit_count() == 5]
    assert all(t.bit_count() == 1 for t in weight_five)
    return {"vertices": 5, "edges": 13, "degrees": [sum(v in e for e in schedule.EDGES) for v in range(5)],
            "cut_distance": 5, "cycle_rank": 9, "H1_dimension": 0,
            "generalized_Cheeger_Z2": str(h), "maximum_cycle_length": max(map(len, schedule.CYCLES)),
            "all_8192_readout_decisions": dict(decisions),
            "readout_decision_table": decision_table,
            "weight_five_root_zero_cuts": weight_five,
            "gauged_distance": 6,
            "distance_scope": "Analytical cut classification + code distance/block detection; not 4**33 brute force"}


def ideal_certificate(dual):
    # Check physical monomial multiplication U_eta U_t, including phases.
    def action(t, b):
        support = [q for q in range(20) if t >> (q//4) & 1]
        return b ^ schedule.mask(support), sum(schedule.SIGNS[q]*(2*((b >> q) & 1)-1) for q in support) % 8
    tests = 0
    for eta in range(0, 32, 2):
        for b in dual:
            for t in (eta, eta ^ 31):
                out, p = action(t, b)
                out, p2 = action(eta, out)
                expected, phase = action(t ^ eta, b)
                assert (out, (p+p2) % 8) == (expected, phase)
                tests += 1
    records = []
    total = Fraction(0)
    for xb in range(32):
        sign = (-1)**xb.bit_count()
        branch_prob = Fraction(3 if sign == 1 else 1, 4)
        for eta in range(0, 32, 2):
            z = schedule.cut(eta)
            ts = [t for t in range(32) if schedule.cut(t) == z]
            assert ts == sorted((eta, eta ^ 31))
            amplitudes = {t: Fraction((-1)**((xb & t).bit_count()), 32) for t in ts}
            xeta = (-1)**((xb & eta).bit_count())
            # Test all four logical sectors and all x vectors, not only ++.
            for l0, l1 in product(range(2), repeat=2):
                eigen = (-1)**(l0*l1)
                exact = amplitudes[eta] + amplitudes[eta ^ 31]*eigen
                expected = Fraction(xeta, 16) * Fraction(1+sign*eigen, 2)
                assert exact == expected
            probability = branch_prob / 256
            total += probability
            records.append({"vertex_word": xb, "edge_word": z, "eta": eta,
                            "sector": sign, "bare_corrected_global_sign": xeta,
                            "vertex_frame_global_sign": xeta,
                            "physical_byproduct_global_sign": (-1)**(((eta >> 2) & 1)+((eta >> 3) & 1)),
                            "chosen_physical_record_global_sign": (-1)**(((eta >> 2) & 1)+((eta >> 3) & 1)),
                            "chosen_ideal_controller_keeps": sign == 1,
                            "probability_on_plus_plus": str(probability)})
    assert total == 1
    return {"full_records": len(records), "physical_monomial_phase_tests": tests,
            "positive_probability": "3/4", "negative_probability": "1/4",
            "Kraus": "2**(1-N) * x_eta * P_x", "records": records}


def cat_program(m):
    # Intentionally independent list construction, with prep/reset/live tracking.
    ops = [("P", (q,)) for q in range(m)] + [("H", (0,))]
    ops += [("CX", (q, q+1)) for q in range(m-1)]
    for _ in range(3):
        for q in range(m-1):
            ops += [("P", (m,)), ("CX", (q, m)), ("CX", (q+1, m)), ("M", (m,))]
    return ops


def cat_signatures(m):
    ops = cat_program(m)
    full = (1 << m)-1
    meter_prefix = []
    n = 0
    for op, qs in ops:
        meter_prefix.append(n)
        n += op == "M"
    def propagate(x, z, start):
        reports = 0
        for i in range(start, len(ops)):
            op, qs = ops[i]
            q = qs[0]
            if op == "H":
                if ((x ^ z) >> q) & 1:
                    x ^= 1 << q
                    z ^= 1 << q
            elif op == "CX":
                c, t = qs
                x ^= ((x >> c) & 1) << t
                z ^= ((z >> t) & 1) << c
            elif op == "P":
                x &= ~(1 << q)
                z &= ~(1 << q)
            elif op == "M":
                reports |= ((x >> q) & 1) << meter_prefix[i]
                x &= ~(1 << q)
                z &= ~(1 << q)
        return x & full, reports
    cases, live = {(0, 0)}, set()
    locations = 0
    for i, (op, qs) in enumerate(ops):
        for q in live - set(qs):
            locations += 1
            for x, z in ((1, 0), (0, 1), (1, 1)):
                cases.add(propagate(x << q, z << q, i))
        locations += 1
        for axes in product(range(4), repeat=len(qs)):
            if not any(axes):
                continue
            x = sum((p & 1) << q for p, q in zip(axes, qs))
            z = sum((p >> 1) << q for p, q in zip(axes, qs))
            cases.add(propagate(x, z, i if op == "M" else i+1))
        if op == "P":
            live.update(qs)
        elif op == "M":
            live.difference_update(qs)
    assert all(flags or min(x.bit_count(), m-x.bit_count()) <= 1 for x, flags in cases)
    groups = defaultdict(list)
    for x, flags in cases:
        groups[flags].append(x)
    pairs = 0
    for group in groups.values():
        for a, b in product(group, repeat=2):
            x = a ^ b
            assert min(x.bit_count(), m-x.bit_count()) <= 2
            pairs += 1
    return {"leaves": m, "physical_and_cat_idle_locations": locations,
            "merged_X_and_flag_signatures": len(cases), "zero_flag_ordered_pairs": pairs,
            "single_fault_bit_cost_at_most": 1, "two_fault_bit_cost_at_most": 2,
            "scope": "Only Clifford cat preparation/three scans; arbitrary cat phase retained analytically"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/single-block-cz")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    code, dual = code_certificate()
    graph = graph_certificate()
    (args.output_dir / "physical-recovery-table.json").write_text(
        json.dumps(code.pop("radius_two_recovery_table"), indent=2)+"\n")
    (args.output_dir / "edge-decisions.json").write_text(
        json.dumps(graph.pop("readout_decision_table"))+"\n")
    ideal = ideal_certificate(dual)
    (args.output_dir / "ideal-records.json").write_text(json.dumps(ideal.pop("records"), indent=2)+"\n")
    cats = [cat_signatures(m) for m in (2, 3, 4, 5, 6, 7, 8, 10, 20)]
    resources = schedule.accounting()
    payload = {"verified": True, "arithmetic": "integers and Fraction; no floating tolerance",
               "code": code, "graph": graph, "ideal": ideal, "cat_preparation": cats,
               "graph_parity_verification": graph_parity_audit(),
               "full_factory_fault_pair_enumeration": False,
               "proof": "notes/full_procedure_single_block_cz_proof.md",
               "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in (
                   Path(__file__), ROOT / "src/c4_helix_single_block_cz.py",
                   ROOT / "src/check_single_cz_graph_parity.py", ROOT / "src/run_single_block_cz_controller.py",
                   ROOT / "src/single_cz_controller.py", ROOT / "src/single_cz_recovery.py",
                   ROOT / "src/single_cz_flagged.py",
                   ROOT / "arXiv-2609.03194v1/appendix.tex")}}
    (args.output_dir / "certificates.json").write_text(json.dumps(payload, indent=2)+"\n")
    (args.output_dir / "resources.json").write_text(json.dumps(resources, indent=2)+"\n")
    print(json.dumps({"verified": True, "code_distance": code["code_distance"],
                      "two_block_Paulis": sum(r["Paulis_tested"] for r in code["two_block_detection"]),
                      "graph": graph, "ideal": ideal, "cat_shapes": len(cats)}, indent=2))


if __name__ == "__main__":
    main()
