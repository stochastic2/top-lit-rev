"""Draw source-check and source-preparation diagrams for the tutorial."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "notes/figures/understandable-inter-cz"


def save(fig, name):
    for suffix in ("png", "svg"):
        fig.savefig(OUTPUT / f"{name}.{suffix}", dpi=150, facecolor="white")
    plt.close(fig)


def source_check():
    fig, ax = plt.subplots(figsize=(16, 8.2))
    colors = ["#226488", "#8955a4", "#a96a17", "#2b7c57"]
    labels = [r"$L_0$", r"$L_1$", r"$L_2$", r"$L_3$",
              *[f"$D_{{{q}}}$" for q in (0, 3, 6, 7, 10, 11, 12, 15)]]
    for y, label in enumerate(labels):
        ax.plot([-0.8, 16.4], [y, y], lw=1, color="#a8afb8", zorder=0)
        ax.text(-1.05, y, label, ha="right", va="center", fontsize=14)
        if y < 4:
            ax.text(-0.65, y - 0.15, r"$|0\rangle$", fontsize=12, va="bottom")
    ax.add_patch(Rectangle((-0.15, -0.24), 0.5, 0.48, facecolor="white", edgecolor=colors[0], zorder=4))
    ax.text(0.1, 0, "H", ha="center", va="center", fontsize=12, zorder=5)
    gates = [(0, 1), (0, 2), (0, 3),
             (0, 4), (1, 6), (2, 8), (3, 10),
             (0, 5), (1, 7), (2, 9), (3, 11),
             (0, 3), (0, 2), (0, 1)]
    for x, (control, target) in enumerate(gates, 1):
        color = colors[control] if target >= 4 else "#425368"
        ax.plot([x, x], [control, target], color=color, lw=1.5, zorder=2)
        ax.plot(x, control, "o", ms=5, color=color, zorder=4)
        ax.add_patch(Circle((x, target), 0.13, facecolor="white", edgecolor=color, lw=1.5, zorder=4))
        ax.plot([x - 0.09, x + 0.09], [target, target], color=color, lw=1.3, zorder=5)
        ax.plot([x, x], [target - 0.09, target + 0.09], color=color, lw=1.3, zorder=5)
        ax.text(x, -0.5, str(x), ha="center", fontsize=10, color="#425368")
    for y in range(4):
        x = 15.45 if y == 0 else 14.65
        ax.add_patch(Rectangle((x, y - 0.23), 0.85, 0.46, facecolor="white", edgecolor="#425368", zorder=6))
        ax.text(x + 0.425, y, "$M_X$" if y == 0 else "$M_Z$", ha="center", va="center", fontsize=12, zorder=7)
    for x in (3.5, 7.5, 11.5):
        ax.axvline(x, ymin=0.03, ymax=0.92, ls=":", lw=1, color="#c2c7ce", zorder=-1)
    for x, title in ((1.7, "Prepare helper cat"), (5.5, "First data pass"), (9.5, "Second data pass"), (13.1, "Undo fanout")):
        ax.text(x, -1.2, title, ha="center", fontsize=12, color="#334155")
    ax.text(15.5, -1.2, "Readout", ha="center", fontsize=12, color="#334155")
    ax.text(-2.05, 1.5, "4 helpers", rotation=90, ha="center", va="center", fontsize=12)
    ax.text(-2.05, 7.5, "8 data targets (of 20)", rotation=90, ha="center", va="center", fontsize=12)
    ax.text(7.0, 11.95, "L0 gives the check result. L1, L2, L3 give flags. No data qubit is measured.", ha="center", fontsize=12, color="#334155")
    ax.set_xlim(-2.7, 16.9)
    ax.set_ylim(12.45, -1.8)
    ax.set_axis_off()
    fig.suptitle("Source-check circuit: X0 X3 X6 X7 X10 X11 X12 X15", fontsize=17, y=0.98)
    fig.subplots_adjust(left=0.02, right=0.995, top=0.94, bottom=0.02)
    save(fig, "decoded-source-check")


def source_timeline():
    fig, ax = plt.subplots(figsize=(16, 4.7))
    boxes = [(0.8, 2.0, "Raw encoder\n11 H + 51 CX"),
             (3.2, 1.35, "Record 1\n20 checks"),
             (4.95, 1.35, "Record 2\n20 checks"),
             (6.7, 1.35, "Record 3\n20 checks"),
             (8.6, 1.55, "Apply source\nPauli correction"),
             (10.65, 2.15, "18 code checks\nand data recovery"),
             (13.3, 1.95, "Cat-based\nU measurement")]
    ax.plot([0.1, 15.6], [1, 1], color="#778595", lw=2, zorder=0)
    ax.plot([0.1, 15.6], [1.05, 1.05], color="#778595", lw=1, zorder=0)
    ax.text(0.05, 0.52, r"$|0\rangle^{\otimes20}$", fontsize=13, va="bottom")
    for x, width, label in boxes:
        color = "#e6f1f6" if x < 10 else "#f3ede2"
        ax.add_patch(Rectangle((x, 0.55), width, 0.95, facecolor=color, edgecolor="#425368", lw=1.3, zorder=2))
        ax.text(x + width / 2, 1.025, label, ha="center", va="center", fontsize=11, zorder=3)
    ax.plot([3.2, 8.05], [2.05, 2.05], color="#226488", lw=1.4)
    for x in (3.875, 5.625, 7.375):
        ax.add_patch(FancyArrowPatch((x, 1.5), (x, 2.05), arrowstyle="->", mutation_scale=10, color="#226488"))
    ax.text(5.6, 2.48, "Accept the common record only after three consecutive equal records.\nNo data correction between records; fresh helpers for every check.", ha="center", va="center", fontsize=11, color="#226488")
    ax.add_patch(FancyArrowPatch((8.05, 2.05), (9.375, 1.5), connectionstyle="angle,angleA=0,angleB=90,rad=8", arrowstyle="->", mutation_scale=12, color="#226488", ls="--"))
    ax.text(12.9, 2.4, "First complete data/CZ round", ha="center", fontsize=12, color="#806124")
    ax.text(7.8, 3.45, "Shown: first 3 source records agree. Otherwise continue, up to 9 records.\nA source flag or unstable history rebuilds this unused source, within the shared retry limit.", ha="center", fontsize=11, color="#425368")
    ax.set_xlim(-0.2, 16)
    ax.set_ylim(4, -0.1)
    ax.set_axis_off()
    fig.suptitle("Source correction occurs after certification and before the first logical-U measurement", fontsize=16, y=0.98)
    fig.subplots_adjust(left=0.02, right=0.995, top=0.89, bottom=0.02)
    save(fig, "source-preparation-timeline")


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_check()
    source_timeline()
