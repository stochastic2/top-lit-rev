"""Editable circuit-figure source. Requires matplotlib; no TeX installation.

MPLCONFIGDIR=/private/tmp/c4-cz-mpl /Users/kevinhemery/pytket-venv/bin/python \
    -B notes/build-single-block-cz.py
All files are additive SVG + PNG assets. Wire time runs left to right.
"""
import os
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import c4_helix_single_block_cz as model

OUT = Path(__file__).resolve().parent / "figures/c4-helix/single-block-cz"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none"})


class Circuit:
    def __init__(self, labels, columns, title, subtitle="", width=None):
        self.labels, self.n, self.columns = labels, len(labels), columns
        self.fig, self.ax = plt.subplots(figsize=(width or max(8, columns*.34+3), .44*len(labels)+1.8))
        self.ax.set_xlim(-3.4, columns+1)
        self.ax.set_ylim(len(labels)-.3, -2.6)
        self.ax.axis("off")
        for q, label in enumerate(labels):
            self.ax.plot([-.5, columns+.5], [q, q], color="#536171", lw=.8, zorder=0)
            self.ax.text(-.8, q, label, ha="right", va="center", fontsize=10)
        self.ax.text(-3.2, -1.9, title, weight="bold", fontsize=14)
        self.ax.text(-3.2, -1.1, subtitle, fontsize=10, color="#445267")

    def gate(self, x, q, label, color="#e9f0fa", width=.8):
        if label in ("MZ", "|0>"):
            # Double wire: classical report after destructive readout.
            # A fresh preparation starts a quantum segment on reused w.
            start = x+width/2
            self.ax.add_patch(Rectangle((start, q-.08), self.columns+.5-start, .16,
                                       facecolor="white", edgecolor="none", zorder=1))
            for delta in ((-.035, .035) if label == "MZ" else (0,)):
                self.ax.plot([start, self.columns+.5], [q+delta, q+delta],
                             color="#536171", lw=.65, zorder=1)
        self.ax.add_patch(Rectangle((x-width/2, q-.3), width, .6,
                                   facecolor=color, edgecolor="#304761", lw=1, zorder=4))
        self.ax.text(x, q, label, ha="center", va="center", fontsize=9, zorder=5)

    def cx(self, x, c, t):
        self.ax.plot([x, x], [c, t], color="#26394e", lw=1, zorder=2)
        self.ax.add_patch(Circle((x, c), .075, facecolor="#26394e", zorder=5))
        self.ax.add_patch(Circle((x, t), .19, facecolor="white", edgecolor="#26394e", zorder=5))
        self.ax.plot([x-.12, x+.12], [t, t], color="#26394e", zorder=6)
        self.ax.plot([x, x], [t-.12, t+.12], color="#26394e", zorder=6)

    def feedback(self, x1, q1, x2, q2, label=""):
        self.ax.annotate("", xy=(x2, q2-.34), xytext=(x1+.4, q1),
                         arrowprops={"arrowstyle": "->", "linestyle": "--", "color": "#b2501c", "lw": 1})
        if label:
            self.ax.text((x1+x2)/2, (q1+q2)/2-.2, label, fontsize=9, color="#a24317")

    def save(self, name):
        self.fig.tight_layout(pad=1)
        for ext in ("svg", "png"):
            self.fig.savefig(OUT / f"{name}.{ext}", dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(self.fig)


# Complete unitary CSS source; split time into two panels to keep gate spacing.
pivots, gates = model.rref_encoder()
for part, pairs in enumerate((gates[:26], gates[26:]), 1):
    c = Circuit([f"D{q}  |0>" if part == 1 else f"D{q}" for q in range(20)],
                len(pairs)+4, f"Encoded |++>: unitary CSS encoder, panel {part}/2",
                "All 20 data wires shown. Continue directly from panel 1 to panel 2.", width=18)
    if part == 1:
        for q in pivots:
            c.gate(0, q, "H")
    for x, (a, b) in enumerate(pairs, 2):
        c.cx(x, a, b)
    c.save(f"01-source-{part}")

c = Circuit(["a_v (control)"] + [f"D{q}" for q in range(4, 8)], 14,
            "Enrichment on inner block b", "Each controlled W' is THREE physical locations: T^s, CX, T^-s.")
for k, q in enumerate(range(4, 8)):
    s = model.SIGNS[q]
    c.gate(3*k, k+1, "T" if s == 1 else "T†")
    c.cx(3*k+1, 0, k+1)
    c.gate(3*k+2, k+1, "T†" if s == 1 else "T")
c.gate(13, 0, "H")
c.gate(14, 0, "MZ", "#fff0dc")
c.ax.text(14.5, 0, "x_b", va="center", color="#a24317")
c.save("02-enrichment")

c = Circuit([f"a_{v} |+>" for v in "abcde"] + [f"A{e} |0>" for e in range(13)], 27,
            "Graph resource: compact13", "Endpoint CNOTs in edge order; then THREE zero scans of L_e only, using the one-helper circuit in 03b.", width=18)
for e, (u, v) in enumerate(model.EDGES):
    c.cx(2*e, u, 5+e)
    c.cx(2*e+1, v, 5+e)
c.save("03-graph-resource")

c = Circuit(["a_u (vertex)", "A_e (edge)", "a_v (vertex)", "w (fresh helper)"], 10,
            "Graph verification: direct Z(a_u) Z(A_e) Z(a_v) parity",
            "All CNOTs point INTO w. No cat and no preparation-stage X checks.", width=12)
c.gate(0, 3, "|0>", "#e7f5ea")
for x,q in enumerate(range(3),2):
    c.cx(x,q,3)
c.gate(6,3,"MZ","#fff0dc")
c.ax.text(6,3.55,"ell_e = reported bit",ha="center",color="#a24317",fontsize=9)
c.gate(9,3,"retry?","#fff0dc",width=1.4)
c.feedback(6,3,9,3,"ell_e")
c.ax.text(3.7,4.2,"Scan all 13 edges, three times. First nonzero scan: rebuild ONLY the unused graph.",
          ha="center",fontsize=9)
c.ax.set_ylim(4.6,-2.6)
c.save("03b-graph-parity")

# One full ZZ scan shown; repeated thrice before any coupling to unknown data.
c = Circuit(["L0 |0>", "L1 |0>", "L2 |0>", "L3 |0>", "w (fresh each parity)"], 17,
            "Four-leaf cat and its verification flags", "Repeat the bracketed ZZ scan THREE times. Any nonzero flag: discard this unused cat and retry.")
c.gate(0, 0, "H")
for j in range(3):
    c.cx(j+1, j, j+1)
for j in range(3):
    x = 5+4*j
    c.gate(x, 4, "|0>", "#e7f5ea")
    c.cx(x+1, j, 4)
    c.cx(x+2, j+1, 4)
    c.gate(x+3, 4, "MZ", "#fff0dc")
    c.ax.text(x+3, 4.55, f"f{j}", ha="center", fontsize=9, color="#a24317")
c.ax.plot([4.5, 16.5], [-.65, -.65], color="#b2501c")
c.ax.text(10.5, -.85, "one scan × 3", ha="center", color="#a24317")
c.save("04-cat-verification")

c = Circuit(["A0 (edge ab)"] + [f"D{q}" for q in range(4, 8)], 26,
            "Coordinates for measuring the dressed checks: block b slice",
            "The complete V uses the same pattern on b,c,d,e. The middle checks use verified cats (Figure 4).", width=17)
for offset in (0, 15):
    for k, q in enumerate(range(4, 8)):
        s = model.SIGNS[q]
        c.gate(offset+3*k, k+1, "T" if s == 1 else "T†")
        c.cx(offset+3*k+1, 0, k+1)
        c.gate(offset+3*k+2, k+1, "T†" if s == 1 else "T")
for q in range(5):
    c.gate(13, q, "checks", "#e7f5ea", width=1.6)
c.ax.text(13, 5, "bare code Z then X; cycle Z; four graph X stars; phase repairs", ha="center", fontsize=9)
c.save("05-coordinate-checks")

root_edges = [e for e, ends in enumerate(model.EDGES) if 0 in ends]
ports = [f"D{q}" for q in range(4)] + [f"A{e}" for e in root_edges]
c = Circuit(ports + [f"L{j}" for j in range(10)], 27,
            "Root Gauss measurement G_a: ten separate cat ports",
            "Prepare and verify GHZ10 with Figure 4 first. Each leaf couples to ONE physical target. Accept parity 0.", width=18)
for j in range(10):
    x = 3*j+1 if j < 4 else 13+(j-4)
    if j < 4:
        s = model.SIGNS[j]
        c.gate(x, j, "T" if s == 1 else "T†")
        c.cx(x+1, 10+j, j)
        c.gate(x+2, j, "T†" if s == 1 else "T")
    else:
        c.cx(x, 10+j, j)
    c.gate(21, 10+j, "H")
    c.gate(23, 10+j, "MZ", "#fff0dc")
c.ax.text(25, 14.5, "XOR all\n10 reports\n= g_a", ha="center", va="center", color="#a24317")
c.save("06-root-gauss")

c = Circuit([f"A{e}" for e in range(13)] + ["D4", "D5", "D6", "D7"], 13,
            "Ungauging: a corrected edge record selects U_eta",
            "All 13 edges are measured in Z. Example: decoded eta_b=1; eta_c=eta_d=eta_e=0.", width=13)
for e in range(13):
    c.gate(0, e, "MZ", "#fff0dc")
c.gate(3, 6, "decode all 13", "#fff0dc", width=3)
for j, q in enumerate(range(4, 8)):
    c.gate(7, 13+j, "S" if model.SIGNS[q] == 1 else "S†")
    c.gate(10, 13+j, "X")
c.feedback(4.5, 6, 7, 13, "eta_b")
c.ax.text(6, 17.2, "Apply S/X iff eta_b=1. No measured vertex is reused.", ha="center", fontsize=9)
c.save("07-ungauging-feedback")

c = Circuit(["L0", "L1", "L2", "L3", "D0", "D1", "D2", "D3"], 9,
            "A terminal ZZZZ check: four independent physical ports",
            "Verified GHZ4 is supplied by Figure 4. Repeat the COMPLETE eighteen-check record three times.")
for j in range(4):
    c.gate(0, 4+j, "H")
    c.cx(j+1, j, 4+j)
    c.gate(5, 4+j, "H")
    c.gate(7, j, "H")
    c.gate(8, j, "MZ", "#fff0dc")
c.ax.text(9, 1.5, "XOR\nreports", ha="left", color="#a24317")
c.save("08-terminal-check")
print(f"Wrote SVG and PNG circuits to {OUT}")
