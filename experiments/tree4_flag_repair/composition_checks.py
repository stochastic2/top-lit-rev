"""Recompute the finite ingredients used by the composition proof."""
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

from controller import RepairedTree, ROOT, noisy
from study_single_cz_screened_source import SELECTED
from check_single_cz_fast_source import audit as source_forward, envelope, program
from check_single_cz_source_coherent import certify, support_tables
from study_single_cz_source_windows import certificate as source_meter_certificate
from check_single_cz_tree_resource import resource_certificate, handoff_certificate
from check_single_cz_block_z import certificate as outer_z
from check_single_cz_short_gauss_vote import compact_screen, sector_certificate, signatures, terminal
from check_single_cz_compact_checks import local_certificate
from single_cz_flagged import dual_single_fault_pauli_program
from single_cz_compact_checks import compact_pauli_program
from single_cz_short_gauss_pilot import compact_root_program
from single_cz_recovery import m, data_table, syndrome, STABILIZERS


def meters():
    ports = [("W",f"D{q}") for q in range(4)] + [("X",f"A{q}") for q in range(4)]
    roles = [q for _,q in ports] + ["s","f0","f1","f2","f3"]
    # Each signed local change of basis brackets exactly one syndrome CX.
    compiled = compact_root_program(ports,range(4))
    skeleton = compact_pauli_program("X",8)
    expected = []
    for op, qs in skeleton:
        wires = tuple(roles[i] for i in qs)
        if op == "CX" and wires[1].startswith("D"):
            sign = m.SIGNS[int(wires[1][1:])]
            expected += [(("T" if sign==1 else "TDG"),wires[1:]),(op,wires),
                         (("TDG" if sign==1 else "T"),wires[1:])]
        else:
            expected.append((op,wires))
    assert compiled == expected
    # Compact local certificates include zero-flag one-fault and all
    # equal-flag two-fault cases modulo the full measured port product.
    compact = [local_certificate(axis,n) for axis,n in product("XZ",(4,8))]
    conditional = []
    for axis,n in product("XZ",(4,8)):
        sig,loc = signatures(dual_single_fault_pauli_program(axis,n),range(n),(1<<n)-1,1)
        full=(1<<n)-1
        for x,z,f in sig:
            if not f:
                altered = ((x ^ full) | z) if axis=="X" else (x | (z ^ full))
                assert min((x|z).bit_count(),altered.bit_count())<=1
        conditional.append({"axis":axis,"n":n,"locations":loc,"signatures":len(sig)})
    return {"tree_root_matches_compact_X8":True,"compact":compact,"one_remaining_fault":conditional}


def x_reference():
    count = kept = 0
    for v,w in combinations(range(5),2):
        for a,b in product(range(16),repeat=2):
            x=(a << (4*v)) | (b << (4*w))
            c=data_table()[syndrome(x,0)]["correction"]
            count += 1
            if c is not None:
                assert c[1]==0 and (x ^ c[0]) in STABILIZERS
                kept += 1
    for v in range(5):
        signs = m.SIGNS[4*v:4*v+4]
        assert signs.count(-1)%2==0
        for word in range(16):
            # W_B X_B W_B versus X_B: ratio of W_B basis phases squared.
            phase = sum(s*(2*((word>>j)&1)-1) for j,s in enumerate(signs))
            assert (2*phase - 4*(word.bit_count()%2))%8==0
    return {"x_masks":count,"corrected_masks":kept,"signed_inner_conjugations":80}


def main():
    out=Path(__file__).resolve().parent
    b=noisy.RecordBackend()
    RepairedTree(b,**noisy.OPTIONS).source()
    ops=[(g,tuple(20 if q=="s" else 21 if q=="f0" else int(q[1:]) for q in qs)) for g,qs in b.ops]
    assert ops == program(SELECTED)
    src=source_forward(SELECTED,*envelope())
    assert not src["bad_one"] and not src["bad_two"]
    co=certify(SELECTED,*support_tables())
    assert co["all_have_common_support"]
    with patch.object(terminal,"screen_program",compact_screen):
        end=terminal.audit()
    assert end["verified"]
    result={"source":src,"source_fixed_locations":co,"source_meters":source_meter_certificate(),
            "graph":resource_certificate(),"handoff":handoff_certificate(),"vote":sector_certificate(),
            "meters":meters(),"X_reference":x_reference(),"outer_Z":[outer_z(s) for s in m.SUPPORTS[5:]],
            "terminal":end}
    # Pin imported repository modules and the scripts used to reproduce the proof.
    paths={Path(mod.__file__).resolve() for mod in sys.modules.copy().values() if getattr(mod,"__file__",None)}
    paths.update(out.glob("*.py"))
    result["source_sha256"]={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(paths) if p.is_relative_to(ROOT) and p.suffix==".py"}
    (out/"composition.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    main()
