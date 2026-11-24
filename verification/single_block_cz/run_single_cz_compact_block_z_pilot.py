"""Keep compact13 chords for recovery while using block-level vote flags."""

from hashlib import sha256
from pathlib import Path
import sys
from unittest.mock import patch

import run_single_cz_tree_handoff_pilot as harness
from single_cz_block_z_pilot import BlockZPilot
from single_cz_recovery import COMPACT13
from single_cz_short_gauss_pilot import ShortGaussPilot
from single_cz_tree_handoff_pilot import TreeBitHandoffGraph


class CompactBlockZPilot(BlockZPilot):
    def __init__(self, backend, **options):
        super().__init__(backend, **options)
        graph = COMPACT13
        self.graph_choice = TreeBitHandoffGraph(graph.name, graph.edges, graph.cycles, graph.tree)
        self.graph_choice.validate()

    def graph(self):
        ShortGaussPilot.graph(self)


def controller(backend, arm=None, recover_outer=False, *, graph):
    assert graph == "compact13"
    return CompactBlockZPilot(backend, **harness.base.OPTIONS)


def main():
    write_json = harness.base.write_json

    def write_with_check_policy(path, item):
        if path.name == "manifest.json":
            item["outer_Z_flags"] = "one phase flag between ports 2 and 6; reject nonzero"
            item["routine_recovery"] = "gauged Z-only reference, with graph-assisted full fallback"
            for value in (__file__, BlockZPilot.bare_check.__code__.co_filename):
                source = Path(value)
                item["source_sha256"][str(source.relative_to(harness.base.ROOT))] = sha256(source.read_bytes()).hexdigest()
        write_json(path, item)

    sys.argv.extend(("--graphs", "compact13"))
    with patch.object(harness.base, "write_json", write_with_check_policy):
        harness.main()


if __name__ in {"__main__", "__mp_main__"}:
    harness.controller = controller
if __name__ == "__main__":
    main()
