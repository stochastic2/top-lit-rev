"""Run the tree-bit pilot with one targeted graph-preparation check."""

from hashlib import sha256
from pathlib import Path
import sys
from unittest.mock import patch

import run_single_cz_tree_handoff_pilot as harness
from single_cz_tree_resource_pilot import TreeResourcePilot


def controller(backend, arm=None, recover_outer=False, *, graph):
    assert graph == "tree4"
    return TreeResourcePilot(backend, **harness.base.OPTIONS)


def main():
    write_json = harness.base.write_json

    def write_with_resource_policy(path, item):
        if path.name == "manifest.json":
            item["tree_resource_policy"] = "one Z parity on a0,A1,a2"
            for value in (__file__, TreeResourcePilot.graph.__code__.co_filename):
                source = Path(value)
                item["source_sha256"][str(source.relative_to(harness.base.ROOT))] = sha256(source.read_bytes()).hexdigest()
        write_json(path, item)

    sys.argv.extend(("--graphs", "tree4"))
    with patch.object(harness.base, "write_json", write_with_resource_policy):
        harness.main()


if __name__ in {"__main__", "__mp_main__"}:
    harness.controller = controller
if __name__ == "__main__":
    main()
