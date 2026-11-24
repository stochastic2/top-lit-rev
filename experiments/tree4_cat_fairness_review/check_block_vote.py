"""Check the compiled block partition, prefix bound, and handoff to the final meter."""
import json
from itertools import combinations_with_replacement

from block_cat_probe import BlockCat, PostBlockCat, LeanResourceCat, trace, settings, signatures
from single_cz_recovery import m


def check():
    reference, _ = trace(LeanResourceCat, settings(LeanResourceCat))
    def meter(trace_row, slot):
        return [(op,tuple(q)) for ctx,(op,q) in trace_row["gates"] if ctx == f"terminal/{slot}/U"]
    result = {}
    for cls in (BlockCat,PostBlockCat):
        t,_ = trace(cls,settings(cls))
        assert t["accepted"]
        leaves = [f"L{i}" for i in range(5)]
        prefix = [("PREP",(l,)) for l in leaves] + [("H",(leaves[0],))]
        prefix += [("CX",(a,b)) for a,b in zip(leaves,leaves[1:])]
        prefix += [("PREP",("w",)),("CX",("L1","w")),("CX",("L3","w")),("MZ",("w",))]
        expected = list(prefix)
        for i,s in enumerate(m.SIGNS):
            q = f"D{i}"
            expected += [("T" if s==1 else "TDG",(q,)),("CX",(leaves[i//4],q)),("TDG" if s==1 else "T",(q,))]
        expected += [(op,(l,)) for l in leaves for op in ("H","MZ")]
        expected.append(("BOUNDARY", ()))
        block_slots = (0,1) if cls is BlockCat else (0,1,2)
        assert all(meter(t,r)==expected for r in block_slots)
        if cls is BlockCat:
            assert meter(t,2) == meter(reference,2)
        labels=leaves+["w"]
        ops=[(op,tuple(labels.index(w) for w in wires)) for op,wires in prefix]
        sig,loc=signatures(ops,(),31,1)
        sig.add((0,0,0))
        wt=lambda x:min(x.bit_count(),5-x.bit_count())
        one=max(wt(x) for x,z,f in sig if not f)
        two=max(wt(x^y) for (x,z,f),(y,v,g) in combinations_with_replacement(sig,2) if f==g)
        assert (one,two)==(1,2)
        result[cls.__name__]=dict(checked_clean_block_slots=block_slots,prefix_locations=loc,
                                  max_leaf_disagreements_mod_complement=[one,two],
                                  twenty_leaf_deciding_meter=cls is BlockCat)
    return result

if __name__=="__main__":
    print(json.dumps(check(),indent=2))
