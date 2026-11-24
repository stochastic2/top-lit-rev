"""Readable static diagrams for the intrinsic gauged-verification note."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/c4-helix-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

OUT = Path(__file__).resolve().parent / 'figures/c4-helix/intrinsic-gauged-verification'
OUT.mkdir(parents=True, exist_ok=True)
INK, BLUE, GREEN, ORANGE, GRAY = '#203044', '#277da8', '#258375', '#b86b27', '#657487'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'savefig.facecolor': 'white', 'figure.facecolor': 'white'})


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    fig.subplots_adjust(left=.02, right=.98, top=.98, bottom=.02)
    return fig, ax


def box(ax, x, y, w, h, text, color=BLUE, size=12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08,rounding_size=0.10',
                              facecolor=color+'12', edgecolor=color, linewidth=1.6))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', color=INK, fontsize=size, linespacing=1.5)


def arrow(ax, a, b, color=GRAY, lw=1.7):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=14,
                               linewidth=lw, color=color))


def save(fig, name):
    for ext in ['png', 'svg']:
        fig.savefig(OUT / f'{name}.{ext}', dpi=180)
    plt.close(fig)


fig, ax = canvas(13, 6.6)
ax.text(.3, 6.1, 'One root for every dressed check', fontsize=21, weight='bold', color=INK)
ax.text(.3, 5.55, 'The doubled-K5 graph is retained. Only the four highlighted edges enter the dressings.', color=GRAY)
ax.add_patch(Circle((1.6, 2.8), .40, color=INK))
ax.text(1.6, 2.8, 'a', ha='center', va='center', color='white', fontsize=23)
ax.text(1.6, 1.95, 'common root', ha='center', color=INK)
ax.text(1.6, 1.35, 'root group\n0, 1, 2, 3', ha='center', color=GRAY)
for y, v, edge, group, labels in [(4.65, 'b', 7, 1, '4–7'), (3.45, 'c', 11, 2, '8–11'),
                                  (2.25, 'd', 3, 3, '12–15'), (1.05, 'e', 0, 4, '16–19')]:
    ax.plot([2.05, 3.75], [2.8, y], color=BLUE, lw=2.1)
    ax.add_patch(Circle((4.0, y), .23, color=INK))
    ax.text(4.0, y, v, ha='center', va='center', color='white', fontsize=14)
    box(ax, 4.65, y-.35, 1.25, .7, f'$A_{{{edge}}}$', BLUE, 16)
    arrow(ax, (6.05, y), (7.0, y), ORANGE)
    box(ax, 7.15, y-.38, 4.65, .76, f'Errors spread only within group {v}\nB and C physical labels {labels}', GREEN, 11)
ax.text(.35, .25, 'All other gauge edges still carry qubits and cycle checks; they do not control a dressed-check factor.', color=GRAY, fontsize=11)
save(fig, '01-common-root')

fig, ax = canvas(14.5, 6.3)
ax.text(.3, 5.85, 'One complete gauging / ungauging cycle', fontsize=22, weight='bold', color=INK)
stages = [(.3, 2.0, 'Verified\ninputs + graph', BLUE), (2.7, 1.9, 'Enrich; measure\nvertices; fix signs', BLUE),
          (5.0, 2.1, '3 complete\ngauged sweeps', GREEN), (7.5, 1.85, 'Gauge Z readout\n+ decoded SWAPs', BLUE),
          (9.75, 1.95, '3 complete\noriginal-code sweeps', GREEN), (12.1, 2.0, 'Recovery +\nlogical extraction', BLUE)]
for x, width, text, color in stages:
    box(ax, x, 3.45, width, 1.10, text, color, 10.5)
for (x, w, *_), (next_x, *_) in zip(stages, stages[1:]):
    arrow(ax, (x+w+.12, 4), (next_x-.12, 4))
box(ax, 3.75, 1.50, 5.0, 1.05, 'A clean gauged sweep fixes the SWAP-sector label.\nLocal group errors can remain until the terminal sweeps.', GREEN, 11)
arrow(ax, (6.05, 3.3), (6.05, 2.7), GREEN)
box(ax, 9.2, 1.50, 4.7, 1.05, 'A clean original-code sweep removes group errors.\nLater faults add only local physical errors.', GREEN, 11)
arrow(ax, (10.75, 3.3), (10.75, 2.7), GREEN)
ax.text(.35, .65, 'At most two faults TOTAL, including helpers, wrong reports, idles, recovery and readout.',
        fontsize=13, color=INK, weight='bold')
ax.text(.35, .2, 'Three disjoint sweeps guarantee one complete fault-free sweep. Rejection ends the attempt.', color=GRAY, fontsize=12)
save(fig, '02-schedule')

fig, ax = canvas(13, 6.3)
ax.text(.3, 5.85, 'Measuring one dressed-check factor', fontsize=21, weight='bold', color=INK)
ax.text(.3, 5.3, 'For q in group v ≠ a, use its one assigned gauge edge eᵥ.', color=GRAY)
ys = [4.25, 3.35, 2.45, 1.55]
labels = [r'cat leaf $\ell_q$', r'gauge $A_{e_v}$', r'data $B_q$', r'data $C_q$']
for y, label in zip(ys, labels):
    ax.text(.35, y, label, va='center', color=INK)
    ax.plot([2.35, 10.75], [y, y], color=GRAY, lw=1.3)
for gate_x in [4, 8]:
    ax.plot([gate_x, gate_x], [ys[1], ys[3]], color=BLUE, lw=1.7)
    ax.add_patch(Circle((gate_x, ys[1]), .065, color=BLUE))
    for y in ys[2:]:
        ax.plot([gate_x-.09, gate_x+.09], [y-.09, y+.09], color=BLUE, lw=2)
        ax.plot([gate_x-.09, gate_x+.09], [y+.09, y-.09], color=BLUE, lw=2)
    ax.text(gate_x, .98, 'Fredkin', ha='center', color=BLUE)
ax.plot([6, 6], [ys[0], ys[2]], color=ORANGE, lw=1.7)
ax.add_patch(Circle((6, ys[0]), .065, color=ORANGE))
box(ax, 5.79, ys[2]-.22, .42, .44, 'P', ORANGE, 14)
ax.text(6, .98, 'controlled P', ha='center', color=ORANGE)
ax.text(10.95, ys[0], 'measure X', va='center', color=INK, fontsize=11)
ax.text(.35, .35, 'P = X or Z. Multiply the cat-leaf X reports to obtain the full dressed-check outcome.', color=GRAY, fontsize=11)
save(fig, '03-dressed-factor')

fig, ax = canvas(13, 6.9)
ax.text(.3, 6.45, '77 physical qubits suffice with serial reset and reuse', fontsize=20, weight='bold', color=INK)
ax.text(.3, 5.93, 'Bars show occupied registers at each stage; unused hardware is reset or idle.', fontsize=12, color=GRAY)
allocations = [
    ('Known input checks', [40, 0, 0, 8, 1]),
    ('Graph-resource checks', [40, 20, 5, 9, 1]),
    ('Largest paired check', [40, 20, 0, 16, 1]),
    ('Local Gauss check', [40, 20, 0, 12, 1]),
    ('Terminal checks / recovery', [40, 0, 0, 8, 1]),
    ('Retained output', [20, 0, 0, 0, 0]),
]
colors = [BLUE, GREEN, '#8970b0', ORANGE, '#c45151']
names = ['data B/C', 'gauge edges', 'initial vertices', 'cat leaves', 'parity helper']
start, scale = 3.5, .108
for i, (label, values) in enumerate(allocations):
    y = 5.08 - .70*i
    ax.text(.3, y+.20, label, va='center', fontsize=11, color=INK)
    x = start
    for value, color in zip(values, colors):
        if value:
            ax.add_patch(plt.Rectangle((x, y), value*scale, .40, facecolor=color, edgecolor='white'))
            if value >= 5:
                ax.text(x+value*scale/2, y+.20, str(value), color='white', ha='center', va='center', fontsize=10)
            x += value*scale
    ax.text(x+.12, y+.20, str(sum(values)), va='center', fontsize=11, color=INK, weight='bold')
for i, (name, color) in enumerate(zip(names, colors)):
    x = .4 + i*2.45
    ax.add_patch(plt.Rectangle((x, .55), .20, .20, facecolor=color))
    ax.text(x+.28, .65, name, va='center', fontsize=10, color=INK)
ax.text(.35, .15, 'The five measured vertices return to the helper pool; the three sweeps reuse the same physical qubits.', fontsize=11, color=GRAY)
save(fig, '04-qubit-allocation')
print(OUT)
