"""Use the reported tree bits to undo the local gauging byproduct."""

from single_cz_persistent import TREE4, validate_persistent_graph
from single_cz_recovery import COMPACT13, Graph
from single_cz_short_gauss_pilot import ShortGaussPilot


class TreeBitHandoffGraph(Graph):
    def validate(self):
        if self.name == "tree4":
            validate_persistent_graph(self)
        else:
            super().validate()

    def decode(self, word, radius=None):
        if not 0 <= word < 1 << len(self.edges):
            raise ValueError("Invalid edge word")
        # ``radius`` is part of the parent controller's cut-decoder interface.
        # This handoff interprets each tree report as its own local control.
        eta = sum(((word >> e) & 1) << v for v, e in enumerate(self.tree, 1))
        return {"eta": eta, "policy": "reported_tree_bits"}


class TreeHandoffPilot(ShortGaussPilot):
    def __init__(self, backend, *, tree_only=False, **options):
        super().__init__(backend, **options)
        graph = TREE4 if tree_only else COMPACT13
        self.graph_choice = TreeBitHandoffGraph(graph.name, graph.edges, graph.cycles, graph.tree)
        self.graph_choice.validate()

    def flatten_final_cycles(self):
        self.record.append({"final_handoff": "reported_tree_bits_and_compact_terminal_screen"})
