"""Record the clean baseline programs before changing any comparison arm."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tree4_flag_repair"))
from final_diagnostic import RepairedTree, ScreenCat, noisy, options


def trace(cls, settings=None, backend=None):
    b = backend or noisy.RecordBackend()
    controller = cls(b, **(options(cls) if settings is None else settings))
    run = controller.run()
    live = set()
    peak = 0
    groups = defaultdict(Counter)
    for context, (gate, targets) in zip(b.contexts, b.ops, strict=True):
        groups[context][gate] += 1
        if gate == "PREP":
            live.add(targets[0])
        elif gate == "MZ":
            live.remove(targets[0])
        peak = max(peak, len(live))
    return dict(accepted=run["accepted"], reason=run.get("reason"), record=run["record"],
                counts=Counter(g for g, _ in b.ops), peak_live=peak, contexts=dict(groups),
                gates=list(zip(b.contexts,b.ops))), b


def phase_counts(contexts):
    groups = defaultdict(Counter)
    for name, counts in contexts.items():
        if name.startswith("source"):
            phase = "source"
        elif name.startswith("graph/"):
            phase = "tree_resource"
        elif name in ("enrichment", "vertex_readout", "vertex_frame"):
            phase = "tree_entry_ports"
        elif "/G/" in name or name.endswith("/root_Gauss"):
            phase = "tree_confirmation_ports"
        elif name.endswith("/U"):
            phase = "cat_vote_resource_and_ports"
        elif name.startswith("compact/terminal_screen/"):
            phase = "terminal_screen"
        elif name in ("edge_readout", "byproduct"):
            phase = "tree_handoff"
        else:
            phase = "routine_data"
        groups[phase].update(counts)
    return dict(groups)


if __name__ == "__main__":
    result = {}
    for cls, cx in ((RepairedTree, 616), (ScreenCat, 684)):
        clean, _ = trace(cls)
        assert clean["accepted"]
        assert clean["counts"]["CX"] == cx
        assert clean["counts"]["T"] + clean["counts"]["TDG"] == 120
        clean["phases"] = phase_counts(clean["contexts"])
        assert clean["phases"]["source"]["CX"] == 125
        result[cls.__name__] = clean
        print(cls.__name__, {phase: counts["CX"] for phase, counts in clean["phases"].items()})
    (HERE / "baseline_traces.json").write_text(json.dumps(result, indent=2) + "\n")
