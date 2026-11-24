"""Four-edge resource preparation with one targeted raw-hook check."""

from single_cz_tree_handoff_pilot import TreeHandoffPilot


def tree_resource_program(edges):
    assert tuple(edges) == ((0, 1), (0, 2), (0, 3), (0, 4))
    raw = []
    for v in range(5):
        raw.extend([("PREP", (f"a{v}",)), ("H", (f"a{v}",))])
    for e, (u, v) in enumerate(edges):
        role = f"A{e}"
        raw.extend([("PREP", (role,)), ("CX", (f"a{u}", role)), ("CX", (f"a{v}", role))])
    # A root X hook makes a prefix of parity defects. Prefixes of length
    # two or three both meet this check and cost two blocks modulo U.
    scan = [("PREP", ("s",)), *(("CX", (q, "s")) for q in ("a0", "A1", "a2")), ("MZ", ("s",))]
    return raw, scan


class TreeResourcePilot(TreeHandoffPilot):
    def __init__(self, backend, **options):
        super().__init__(backend, tree_only=True, **options)

    def graph(self):
        raw, scan = tree_resource_program(self.graph_choice.edges)
        roles = [sites[0] for op, sites in raw if op == "PREP"]
        while True:
            self.context("graph/tree_raw")
            for op, sites in raw:
                if op == "PREP":
                    self.prep(*sites)
                else:
                    self.gate(op, *sites)
            self.b.boundary()
            bit = self.direct_meter("graph/tree_hook_check", scan)
            self.b.boundary()
            if not bit:
                return
            self.dispose(roles)
            self.retry("known_unused_tree_hook_check")
