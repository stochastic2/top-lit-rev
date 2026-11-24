"""Bind the factory traces to independent exact Clifford and W-port checks."""
from hashlib import sha256
import json
from unittest.mock import patch

from candidates import ARMS, LeanResourceCat, settings
from cat_envelope import FULL, ghz_prefix, signatures, syndrome_certificate
from trace_audit import HERE, RepairedTree, ScreenCat, phase_counts, trace
from check_optimized_extraction import signatures as pauli_signatures
from check_single_block_cz_cyclotomic import audit as w_port
from check_single_cz_block_z import certificate as outer_z
from check_single_cz_compact_checks import local_certificate
from check_single_cz_short_gauss_vote import compact_screen, sector_certificate, terminal
from single_cz_flagged import dual_single_fault_pauli_program
from single_cz_recovery import m
from study_single_cz_bare_inner import inner_program


def certify_cat(cls):
    program = ghz_prefix(cls, settings(cls))
    report_mask = (1 << sum(op == "MZ" for op, _ in program)) - 1
    labels = {f"L{q}": q for q in range(20)} | {"w": 20}
    numeric = [(op, tuple(labels[q] for q in roles)) for op, roles in program]
    exact, count = pauli_signatures(numeric, (), FULL, report_mask)
    independent, _ = signatures(program)
    assert {(x, report) for x, _, report in exact} | {(0, 0)} == set(independent)
    result = syndrome_certificate(program)
    assert result["locations"] == count
    for faults, bounds in result["bounds"].items():
        assert bounds["max_sites"] == faults
    return result


def terminal_trace(clean):
    labels = {f"D{q}": q for q in range(20)} | {"s": 20} | {f"f{j}": 21+j for j in range(4)}
    return [(op, tuple(labels[q] for q in roles)) for context, (op, roles) in clean["gates"]
            if context.startswith("compact/terminal_screen/")]


def main():
    traces = {}
    for cls, cx in zip(ARMS, (616, 684, 656, 576, 540, 576, 576, 540), strict=True):
        clean, _ = trace(cls, settings(cls))
        assert clean["accepted"] and clean["counts"]["CX"] == cx
        assert clean["counts"]["T"] + clean["counts"]["TDG"] == 120
        if cls is not ScreenCat:
            assert [gate for gate in terminal_trace(clean) if gate[0] != "BOUNDARY"] == compact_screen()[0][:-1]
        source = [gate for context, gate in clean["gates"] if context.startswith("source/")]
        if cls is RepairedTree:
            source_reference = source
        else:
            assert source == source_reference
        traces[cls.__name__] = {"counts": clean["counts"], "peak_live": clean["peak_live"],
                                "phases": phase_counts(clean["contexts"]), "contexts": clean["contexts"]}
    bare_inner = {}
    conditional = {}
    for axis in "XZ":
        for block, support in enumerate(m.SUPPORTS[:5]):
            labels = {f"D{q}": q for q in range(20)} | {"s": 20}
            program = [(op, tuple(labels[q] for q in roles))
                       for op, roles in inner_program(axis, [f"D{q}" for q in support])]
            sig, count = pauli_signatures(program, range(20), FULL, 1)
            assert all(sum(bool((x | z) & (15 << (4*v))) for v in range(5)) <= 1 for x, z, _ in sig)
            bare_inner[f"{axis}{block}"] = {"locations": count, "signatures": len(sig)}
        for n in (4, 8):
            mask = (1 << n) - 1
            program = dual_single_fault_pauli_program(axis, n)
            size = sum(op == "MZ" for op, _ in program) - 1
            sig, count = pauli_signatures(program, range(n), mask, (1 << size) - 1)
            for x, z, flags in sig:
                alt = (x ^ mask, z) if axis == "X" else (x, z ^ mask)
                if not flags:
                    assert min((x | z).bit_count(), (alt[0] | alt[1]).bit_count()) <= 1
            conditional[f"{axis}{n}"] = {"locations": count, "signatures": len(sig)}
    with patch.object(terminal, "screen_program", compact_screen):
        compact = terminal.audit()
    # The baseline's ordinary check order cannot be used for a generic terminal
    # screen with an arbitrary upstream one-block error. It has a tighter input
    # envelope after its first full round, proved separately.
    normal = tuple((axis, j) for axis in "ZX" for j in range(9))
    with patch.object(terminal, "screen_program", lambda order=None: compact_screen(normal)):
        try:
            terminal.audit()
        except AssertionError as error:
            bad_ordinary_terminal = error.args[0]
        else:
            raise AssertionError("Expected ordinary-order terminal support failure")
    original = HERE.parent / "tree4_flag_repair"
    certificate = json.loads((original / "composition.json").read_text())
    for filename, digest in certificate["source_sha256"].items():
        assert sha256((HERE.parents[1] / filename).read_bytes()).hexdigest() == digest, filename
    result = dict(traces=traces, cat_prefixes={cls.__name__: certify_cat(cls) for cls in (ScreenCat, LeanResourceCat)},
                  sector=sector_certificate(), signed_ports={s: w_port(s) for s in (-1, 1)},
                  bare_inner=bare_inner, block_z=[outer_z(s) for s in m.SUPPORTS[5:]],
                  conditional=conditional, compact_meters=[local_certificate(a,n) for a in "XZ" for n in (4,8)],
                  compact_terminal=compact, ordinary_order_terminal_counterexample=bad_ordinary_terminal,
                  inherited_tree_source_hashes_verified=len(certificate["source_sha256"]))
    (HERE / "local_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Verified candidate traces, both cat resources, signed W ports, CSS sector and terminal screen.")


if __name__ == "__main__":
    main()
