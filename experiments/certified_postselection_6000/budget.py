"""Physical stop for the supplementary prospective T-budget policy."""
from run import Cat, Compact, Tree, Reject

class Budget:
    hard_stop = "moderate"

    def gate(self,op,*targets):
        if op in ("T","TDG"):
            counts = self.b.gate_counts
            if counts["T"] + counts["TDG"] >= 120:
                raise Reject("postselection_T_budget")
        return super().gate(op,*targets)


class BudgetCat(Budget,Cat): pass
class BudgetCompact(Budget,Compact): pass
class BudgetTree(Budget,Tree): pass
