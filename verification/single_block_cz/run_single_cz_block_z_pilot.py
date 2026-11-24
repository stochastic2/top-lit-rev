"""Noisy short-vote tree pilot with one flag per outer Z check."""

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import run_single_cz_tree_z_recovery_pilot as recovery
from single_cz_block_z_pilot import BlockZPilot


def controller(backend, arm=None, recover_outer=False, *, graph):
    assert graph == "tree4"
    return BlockZPilot(backend, **recovery.resource.harness.base.OPTIONS)


def main():
    base = recovery.resource.harness.base
    write_json = base.write_json

    def write_with_check_policy(path, item):
        if path.name == "manifest.json":
            item["outer_Z_flags"] = "one phase flag between ports 2 and 6; reject nonzero"
            for value in (__file__, BlockZPilot.bare_check.__code__.co_filename):
                source = Path(value)
                item["source_sha256"][str(source.relative_to(base.ROOT))] = sha256(source.read_bytes()).hexdigest()
        write_json(path, item)

    with patch.object(base, "write_json", write_with_check_policy):
        recovery.main()


if __name__ in {"__main__", "__mp_main__"}:
    recovery.resource.harness.controller = controller
if __name__ == "__main__":
    main()
