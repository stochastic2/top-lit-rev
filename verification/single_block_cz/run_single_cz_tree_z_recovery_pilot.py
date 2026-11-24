"""Run the single-check tree resource with gauged Z-only routine recovery."""

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import run_single_cz_tree_resource_pilot as resource
from single_cz_tree_z_recovery_pilot import TreeZRecoveryPilot


def controller(backend, arm=None, recover_outer=False, *, graph):
    assert graph == "tree4"
    return TreeZRecoveryPilot(backend, **resource.harness.base.OPTIONS)


def main():
    base = resource.harness.base
    write_json = base.write_json

    def write_with_recovery_policy(path, item):
        if path.name == "manifest.json":
            item["routine_recovery"] = "gauged Z-only reference after a raw nonzero Z syndrome"
            for value in (__file__, TreeZRecoveryPilot.direct_recover.__code__.co_filename):
                source = Path(value)
                item["source_sha256"][str(source.relative_to(base.ROOT))] = sha256(source.read_bytes()).hexdigest()
        write_json(path, item)

    with patch.object(base, "write_json", write_with_recovery_policy):
        resource.main()


if __name__ in {"__main__", "__mp_main__"}:
    resource.harness.controller = controller
if __name__ == "__main__":
    main()
