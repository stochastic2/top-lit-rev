"""Exploratory clean circuits and local five-leaf verifier audit."""
import json
from pathlib import Path
import sys
from itertools import combinations_with_replacement
from functools import reduce
from operator import xor

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tree4_cat_fairness"))
from candidates import LeanResourceCat, settings
from trace_audit import trace, noisy
from run_single_block_cz_controller import Reject
from check_optimized_extraction import signatures

class BlockCat(LeanResourceCat):
    def check(self, name, ports):
        if not name.endswith("/U"):
            return super().check(name, ports)
        passes = sum(bool(row.get("passing")) for row in self.record if "passing_terminal_round" in row)
        if self.screen_before_deciding_vote and passes == 2:
            return super().check(name, ports)
        assert ports == [("W", f"D{i}") for i in range(20)]
        self.context(name)
        leaves = [f"L{i}" for i in range(5)]
        for leaf in leaves:
            self.prep(leaf)
        self.gate("H", leaves[0])
        for a,b in zip(leaves,leaves[1:]):
            self.gate("CX",a,b)
        self.prep("w")
        for i in (1,3):
            self.gate("CX", leaves[i],"w")
        if self.mz("w"):
            raise Reject("five_leaf_resource_flag")
        for q in range(20):
            self.cw(leaves[q//4],q)
        bits=[]
        for leaf in leaves:
            self.gate("H",leaf)
            bits.append(self.mz(leaf))
        return reduce(xor,bits)

class PostBlockCat(BlockCat):
    screen_before_deciding_vote = False

if __name__ == "__main__":
    results={}
    for cls in (BlockCat,PostBlockCat):
        clean,_=trace(cls,settings(cls))
        assert clean["accepted"]
        gates=[(op,qs) for name,(op,qs) in clean["gates"] if name=="terminal/0/U"]
        labels=[f"L{i}" for i in range(5)]+["w"]
        pre=gates[:next(i for i,(op,_) in enumerate(gates) if op in ("T","TDG"))]
        ops=[(op,tuple(labels.index(q) for q in qs)) for op,qs in pre]
        sig,loc=signatures(ops,(),31,1)
        sig.add((0,0,0))
        def weight(x):
            return min(x.bit_count(),5-x.bit_count())
        assert all(f or weight(x)<=1 for x,z,f in sig)
        assert all(f!=g or weight(x^y)<=2 for (x,z,f),(y,t,g) in combinations_with_replacement(sig,2))
        b=noisy.QuantumBackend(seed=2,model=noisy.NoiseModel(**dict.fromkeys(noisy.RATES,"0")))
        run=cls(b,**settings(cls)).run()
        assert run["accepted"]
        fidelity=noisy.diagnose(*b.state.sparse_output(b.data_labels))["decoded_target_fidelity"]
        assert abs(fidelity-1)<1e-10
        results[cls.__name__]=dict(counts=clean["counts"],peak=clean["peak_live"],raw_prefix_locations=loc,
                                   noiseless_seed_2_fidelity=fidelity)
    (HERE/"probe.json").write_text(json.dumps(results,indent=2)+"\n")
    print(results)
