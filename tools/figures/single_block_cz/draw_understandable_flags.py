"""Draw the eight-data-qubit flag circuit used in Understandable_Inter_CZ.md."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "notes/figures/understandable-inter-cz"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(16, 8.8))
    colors = ["#007f8b", "#8c49ac", "#ab6500", "#287540"]
    labels = ["$s$", *[f"$q_{j}$" for j in range(1, 9)],
              *[f"$f_{j}$" for j in range(4)]]

    for y, label in enumerate(labels):
        start = 0 if y < 9 else 2 * (y - 9) + 1.2
        end = 17.6 if y < 9 else 2 * (y - 9) + 11.15
        ax.plot([start, end], [y, y], color="#a5acb4", lw=1, zorder=0)
        ax.text(-0.3, y, label, ha="right", va="center", fontsize=14)
        if y == 0 or y >= 9:
            prep = r"$|+\rangle$" if y == 0 else r"$|0\rangle$"
            ax.text(start + 0.05, y - 0.18, prep, ha="left", va="bottom",
                    fontsize=12, bbox=dict(facecolor="white", edgecolor="none", pad=0.5))

    def cx(x, target, color):
        ax.plot([x, x], [0, target], color=color, lw=1.5, zorder=2)
        ax.plot(x, 0, "o", color=color, ms=5, zorder=4)
        ax.add_patch(Circle((x, target), 0.13, facecolor="white",
                            edgecolor=color, lw=1.5, zorder=4))
        ax.plot([x - 0.09, x + 0.09], [target, target], color=color, lw=1.3, zorder=5)
        ax.plot([x, x], [target - 0.09, target + 0.09], color=color, lw=1.3, zorder=5)

    for j in range(8):
        cx(2 * j + 1, j + 1, "#294e72")
        cx(2 * j + 2, 9 + j % 4, colors[j % 4])

    for x in range(1, 17):
        ax.text(x, -0.53, str(x), ha="center", va="center", fontsize=10, color="#425064")

    for y in [0, 9, 10, 11, 12]:
        x = 16.8 if y == 0 else 10.4 + 2 * (y - 9)
        ax.add_patch(Rectangle((x, y - 0.22), 0.75, 0.44,
                               facecolor="white", edgecolor="#334155", lw=1, zorder=6))
        ax.text(x + 0.375, y, "$M_X$" if y == 0 else "$M_Z$",
                ha="center", va="center", fontsize=11, zorder=7)

    ax.plot([8.5, 8.5], [-0.19, 0.19], color="#bf3030", lw=2.3, zorder=8)
    ax.annotate("Fault position used in the first example", xy=(8.5, -0.2),
                xytext=(8.5, -1.35), ha="center", fontsize=13, color="#bf3030",
                arrowprops=dict(arrowstyle="->", color="#bf3030"))
    ax.text(-1.12, 4.5, r"arbitrary joint data state $|\psi\rangle$",
            rotation=90, ha="center", va="center", fontsize=12, color="#425064")
    ax.text(8.8, 13.15,
            "Read left to right. Filled dot: CX control. Circled +: CX target. "
            "Crossings without a gate symbol are not interactions.",
            ha="center", fontsize=11, color="#334155")
    ax.set_xlim(-1.7, 18)
    ax.set_ylim(13.65, -1.9)
    ax.set_axis_off()
    fig.suptitle("Measuring X(q1) ... X(q8) with four overlapping flags", fontsize=17, y=0.98)
    fig.subplots_adjust(left=0.025, right=0.99, top=0.94, bottom=0.02)
    for suffix in ("png", "svg"):
        fig.savefig(OUTPUT / f"eight-qubit-flagged-check.{suffix}",
                    dpi=150, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
