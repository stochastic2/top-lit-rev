"""Scientific graph/circuit drawings for Synthesis.md; no workflow boxes.

The manuscript table supplies the code and graph incidence. Colors label
the five inner C4 groups; gauge qubits and cat leaves have their own colors.
Run with the workspace Python that provides matplotlib.
"""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/c4-helix-matplotlib')
from pathlib import Path
from itertools import combinations
import json
import math
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
import c4_helix_intrinsic_decoder as decoder

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'notes/figures/c4-helix/synthesis'
OUT.mkdir(parents=True, exist_ok=True)
raw = (ROOT / 'arXiv-2609.03194v1/appendix.tex').read_text()
table = raw.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
rows = []
for line in table.splitlines():
    syms = re.findall(r'\$(X|Z|\\cdot)\$', line)
    if len(syms) == 20:
        rows.append([q for q, s in enumerate(syms) if s != r'\cdot'])
R = rows[:10]
V = 'abcde'
EDGES = {q: tuple(v for v, s in zip(V, R[5:]) if q in s) for q in range(20)}
PAIRS = {pair: [q for q in EDGES if EDGES[q] == pair] for pair in combinations(V, 2)}
COL = dict(zip(V, ['#367AAF', '#D47D28', '#378957', '#8863AF', '#CA5D85']))
INK, GRAY, LIGHT, GAUGE, CAT, RED = '#203044', '#657487', '#D8E0E6', '#148E9E', '#A47B1C', '#BC3F4C'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13,
                     'svg.fonttype': 'none', 'savefig.facecolor': 'white'})
FIGURES = []


def canvas(w, h, title, subtitle=''):
    fig, ax = plt.subplots(figsize=(w, h), facecolor='white')
    ax.set(xlim=(0, w), ylim=(0, h))
    ax.axis('off')
    fig.subplots_adjust(left=.025, right=.975, top=.98, bottom=.025)
    ax.text(.2, h-.30, title, color=INK, fontsize=20, weight='bold', va='top')
    if subtitle:
        ax.text(.2, h-.86, subtitle, color=GRAY, fontsize=12, va='top')
    return fig, ax


def save(fig, name):
    for ext in ('png', 'svg'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=190)
    FIGURES.append(name)
    plt.close(fig)


def node(ax, x, y, text, color, r=.24, square=False, fill=True, size=14):
    patch = (Rectangle((x-r, y-r), 2*r, 2*r, facecolor=color if fill else 'white',
                       edgecolor=color, lw=1.8, zorder=5) if square else
             Circle((x, y), r, facecolor=color if fill else 'white', edgecolor=color, lw=1.8, zorder=5))
    ax.add_patch(patch)
    ax.text(x, y, text, ha='center', va='center', color='white' if fill else color,
            fontsize=size, zorder=6)


def wire(ax, x0, x1, y, color=INK, lw=1.35):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, zorder=1)


def gate(ax, x, y, text, color=INK, width=.48, height=.38, size=12):
    ax.add_patch(FancyBboxPatch((x-width/2, y-height/2), width, height,
                              boxstyle='round,pad=.025', facecolor='white',
                              edgecolor=color, lw=1.5, zorder=5))
    ax.text(x, y, text, ha='center', va='center', fontsize=size, color=color, zorder=6)


def ctrl(ax, x, y0, y1, kind='X', color=INK):
    ax.plot([x, x], [y0, y1], color=color, lw=1.6, zorder=2)
    ax.add_patch(Circle((x, y0), .055, color=color, zorder=4))
    if kind == 'X':
        ax.add_patch(Circle((x, y1), .105, fc='white', ec=color, lw=1.6, zorder=4))
        ax.plot([x-.105, x+.105], [y1, y1], color=color, lw=1.4, zorder=5)
        ax.plot([x, x], [y1-.105, y1+.105], color=color, lw=1.4, zorder=5)
    else:
        ax.add_patch(Circle((x, y1), .06, color=color, zorder=4))


def swap(ax, x, y0, y1, control=None, color=INK):
    ax.plot([x, x], [min(y0, y1), max(y0, y1) if control is None else control], color=color, lw=1.6, zorder=2)
    if control is not None:
        ax.add_patch(Circle((x, control), .055, color=color, zorder=4))
    for y in (y0, y1):
        ax.plot([x-.09, x+.09], [y-.09, y+.09], color=color, lw=1.8, zorder=4)
        ax.plot([x-.09, x+.09], [y+.09, y-.09], color=color, lw=1.8, zorder=4)


def port(ax, x, y, leaf, target, kind='X', target_color=GAUGE, second=None, width=4.1):
    """A small wire fragment. All displayed leaves share the stated cat input."""
    labels = [leaf, target] + ([] if second is None else [second])
    yy = [y, y-.38] + ([] if second is None else [y-.76])
    for i, (label, yi) in enumerate(zip(labels, yy)):
        ax.text(x, yi, label, va='center', color=CAT if i == 0 else target_color, fontsize=12)
        wire(ax, x+1.0, x+width-.1, yi, CAT if i == 0 else target_color)
    if second is None:
        ctrl(ax, x+2.15, yy[0], yy[1], kind)
    else:
        swap(ax, x+2.15, yy[1], yy[2], yy[0])
    gate(ax, x+width-.46, y, r'$M_X$', CAT, width=.55, size=11)


def positions(cx, cy, radius):
    return {v: (cx+radius*math.cos(math.pi/2-2*math.pi*i/5),
                cy+radius*math.sin(math.pi/2-2*math.pi*i/5)) for i, v in enumerate(V)}


def bundled_graph(ax, pos, bits=None, labels=True):
    for pair, qs in PAIRS.items():
        u, v = pair
        x, y = pos[u]; xx, yy = pos[v]
        selected = bits is None or bits[u] != bits[v]
        ax.plot([x, xx], [y, yy], color=GAUGE if selected else LIGHT,
                lw=2.0 if selected else 1.2, zorder=1)
        if labels:
            t = .31 if 'e' not in pair else .66
            lx, ly = x*(1-t)+xx*t, y*(1-t)+yy*t
            ax.text(lx, ly, ', '.join(map(str, qs)), ha='center', va='center', fontsize=11,
                    color=GAUGE if selected else GRAY, zorder=4,
                    bbox=dict(fc='white', ec=LIGHT, boxstyle='round,pad=.17'))
    for v, (x, y) in pos.items():
        node(ax, x, y, v if bits is None else f'{v}\n{bits[v]}', COL[v],
             r=.29 if bits is None else .34, size=16 if bits is None else 13)


# 1. The code registers: a label q is not a vertex, nor an encoded qubit.
fig, ax = canvas(12, 5.3, 'Two data blocks, five inner groups in each',
                 'Color always follows the inner group. Circles are B data; squares are C data.')
for i, v in enumerate(V):
    cx = 1.35+2.17*i
    ax.text(cx, 3.8, f'group {v}', ha='center', fontsize=14, weight='bold', color=COL[v])
    for j in range(4):
        q = 4*i+j; x = cx-.72+.48*j
        node(ax, x, 2.95, str(q), COL[v], r=.18, size=10)
        node(ax, x, 1.85, str(q), COL[v], r=.18, size=10, square=True, fill=False)
    wire(ax, cx-.9, cx+.9, 3.45, COL[v], 2.4)
ax.text(.12, 2.95, 'B', va='center', weight='bold', fontsize=17, color=INK)
ax.text(.12, 1.85, 'C', va='center', weight='bold', fontsize=17, color=INK)
ax.text(.25, .80, r'Example: $S^X_{B,0}=X_{B_0}X_{B_1}X_{B_2}X_{B_3}$; the corresponding Z check uses the same four sites.', fontsize=12, color=INK)
ax.text(.25, .30, 'Each entire row is a [[20, 2, 6]] code. Its two logical qubits are not individual colored groups.', fontsize=12, color=GRAY)
save(fig, '01-data-registers')

# 2. Graph extraction from the upper check incidence.
fig, ax = canvas(12, 5.6, 'Each physical label occurs in two upper-check supports',
                 'Those two rows become the endpoints of edge q. R9 is redundant as a code check but useful for the graph.')
x0, dx = 2.1, .45
for q in range(20):
    ax.text(x0+dx*q, 3.95, str(q), ha='center', fontsize=11, color=COL[V[q//4]])
for i, v in enumerate(V):
    y = 3.35-.53*i
    ax.text(.3, y, f'{v} : R{i+5}', va='center', color=COL[v], fontsize=14, weight='bold')
    wire(ax, x0-.25, x0+19*dx+.25, y, LIGHT, .8)
    for q in R[5+i]:
        ax.add_patch(Circle((x0+dx*q, y), .065, color=GAUGE))
for g in range(5):
    ax.add_patch(Rectangle((x0+4*g*dx-.22, 1.0), 4*dx, 3.15,
                           facecolor=COL[V[g]]+'0B', edgecolor='none', zorder=0))
ax.add_patch(Rectangle((x0+dx-.15, 1.1), .30, 2.65, fc='none', ec=RED, lw=1.5))
ax.text(.25, .35, 'Highlighted example: q = 1 appears in R7 (row c) and R9 (row e), so A1 lies on c—e.', color=GRAY, fontsize=12)
save(fig, '02-incidence')

# 3. A legible complete graph with a literal edge dictionary.
fig, ax = canvas(12, 7.2, 'The gauging graph: two edges between every vertex pair',
                 'Each numbered line bundles TWO edges. Each edge has its own gauge qubit Aq; crossings are not vertices.')
bundled_graph(ax, positions(3.3, 3.35, 2.05))
ax.text(6.8, 5.55, 'Endpoints', color=INK, weight='bold', fontsize=13)
ax.text(8.8, 5.55, 'Gauge qubits', color=GAUGE, weight='bold', fontsize=13)
for i, (p, qs) in enumerate(PAIRS.items()):
    y = 5.05-.39*i
    ax.text(7.0, y, ' — '.join(p), fontsize=13, color=INK)
    ax.text(8.8, y, rf'$A_{{{qs[0]}}},\ A_{{{qs[1]}}}$', fontsize=13, color=GAUGE)
ax.text(.3, .45, 'The vertex colors also label the data groups, but edge endpoints do not set the SWAP controller.', fontsize=12, color=GRAY)
save(fig, '03-graph')

# 4. Actual cat preparation and the non-propagating parity-verifier circuit.
fig, ax = canvas(13, 5.7, 'The reusable measurement helper: prepare and verify a cat',
                 'Left: a four-leaf example. Right: one adjacent ZZ test; scan all adjacent pairs three times.')
for j in range(4):
    y = 3.8-.65*j
    ax.text(.2, y, rf'$\ell_{j}:|0\rangle$', color=CAT, va='center', fontsize=13)
    wire(ax, 1.35, 6.0, y, CAT)
gate(ax, 1.85, 3.8, 'H', CAT)
for j in range(3):
    ctrl(ax, 2.8+1.0*j, 3.8-.65*j, 3.8-.65*(j+1))
ax.text(1.3, .8, r'One shared state: $(|0000\rangle+|1111\rangle)/\sqrt{2}$', fontsize=13, color=INK)
for y, label, color in [(3.7, r'$\ell_j$', CAT), (2.8, r'$\ell_{j+1}$', CAT), (1.9, r'$w:|0\rangle$', GRAY)]:
    ax.text(7.0, y, label, va='center', fontsize=13, color=color)
    wire(ax, 8.25, 12.35, y, color)
ctrl(ax, 9.0, 3.7, 1.9)
ctrl(ax, 10.2, 2.8, 1.9)
gate(ax, 11.7, 1.9, r'$M_Z$', GRAY, width=.6)
ax.text(7, .8, 'Keep only reported +1; reset w for the next pair.', fontsize=12, color=INK)
ax.text(.25, .25, 'ZZ tests align the cat bits. They do not certify its logical phase; the full protocol also repeats complete sweeps.', fontsize=11.5, color=GRAY)
save(fig, '04-cat-preparation')

# 5. Original code X and Z check circuits: four leaf ports, not a reused control.
fig, ax = canvas(12, 6.3, 'Read an original code check with one leaf per target',
                 'Each panel uses its own verified four-leaf cat. Couple all leaves before multiplying their X reports.')
for k, typ in enumerate('XZ'):
    x = .35+6*k
    ax.text(x, 4.72, rf'$S^{typ}_{{B,0}}={typ}_{{B_0}}{typ}_{{B_1}}{typ}_{{B_2}}{typ}_{{B_3}}$', fontsize=16, color=COL['a'])
    for q in range(4):
        port(ax, x, 4.0-.89*q, rf'$\ell_{q}$', rf'$B_{q}$', typ, COL['a'], width=5.1)
ax.text(.25, .32, 'The product of four reported leaf-X signs is ONE check result. Larger Pauli checks use the same rule.', fontsize=12, color=GRAY)
save(fig, '05-code-checks')

# 6. The cluster preparation fragment and its basis-state parity.
fig, ax = canvas(12, 5.9, 'Prepare the resource on edge 1: c — A1 — e',
                 'These are resource CNOTs. The data qubits B1 and C1 are not involved yet.')
for y, label, color in [(4.0, r'$c:|+\rangle$', COL['c']), (2.9, r'$A_1:|0\rangle$', GAUGE), (1.8, r'$e:|+\rangle$', COL['e'])]:
    ax.text(.3, y, label, va='center', fontsize=16, color=color)
    wire(ax, 2.1, 6.6, y, color)
ctrl(ax, 3.1, 4.0, 2.9)
ctrl(ax, 5.0, 1.8, 2.9)
node(ax, 8.0, 3.0, 'c', COL['c'])
node(ax, 10.8, 3.0, 'e', COL['e'])
ax.plot([8, 10.8], [3, 3], color=GAUGE, lw=2, zorder=1)
node(ax, 9.4, 3.0, r'$A_1$', GAUGE, r=.32, square=True, size=13)
ax.text(7.3, 4.15, r'$K_1=Z_cZ_{A_1}Z_e$', fontsize=17, color=INK)
ax.text(7.3, 1.9, r'$z_1=t_c\oplus t_e$', fontsize=17, color=GAUGE)
ax.text(.25, .65, r'Initialize all five vertices in $|+\rangle$ and all twenty edges independently in $|0\rangle$; apply two CNOTs per edge.', fontsize=12, color=GRAY)
ax.text(.25, .20, 'The full resource has 25 qubits and 25 independent Pauli stabilizers. Verify them before touching B or C.', fontsize=12, color=GRAY)
save(fig, '06-resource')

# 7. The four original Fredkins at one temporary vertex, with explicit data labels.
fig, ax = canvas(12, 8.4, 'Gauging: the temporary vertex a controls four data-pair SWAPs',
                 'a is already entangled with its gauge neighbors. Gauge wires are omitted from this fragment.')
wire(ax, 1.65, 11.1, 6.8, COL['a'])
ax.text(.3, 6.8, 'a', fontsize=17, color=COL['a'], va='center')
for q in range(4):
    by, cy = 5.85-1.2*q, 5.4-1.2*q
    for y, label in [(by, rf'$B_{q}$'), (cy, rf'$C_{q}$')]:
        ax.text(.3, y, label, color=COL['a'], fontsize=14, va='center')
        wire(ax, 1.65, 11.1, y, COL['a'])
    swap(ax, 3.0+1.85*q, by, cy, 6.8)
gate(ax, 10.45, 6.8, r'$M_X$', COL['a'], width=.65)
ax.text(.25, .90, 'Repeat for b on pairs 4–7; c on 8–11; d on 12–15; e on 16–19. Total: twenty Fredkins.', fontsize=12, color=INK)
ax.text(.25, .35, 'Example: pair B1,C1 is controlled by a, although its gauge label A1 belongs to edge c—e.', fontsize=12, color=GRAY)
save(fig, '07-enrichment')

# 8. Initial vertex signs, then the quantum Z frame update, not ungauging.
fig, ax = canvas(12, 6.4, 'Use the vertex-X reports to put the ideal Gauss signs at +1',
                 'Example: xb = xd = −1; xa = xc = xe = +1. Their product is +1, so retain this branch.')
for offset, after in [(0, False), (6, True)]:
    pos = positions(3+offset, 2.9, 1.65)
    for v, edge in [('b', 7), ('c', 11), ('d', 3), ('e', 0)]:
        p, q = pos['a'], pos[v]
        selected = v in 'bd'
        ax.plot([p[0], q[0]], [p[1], q[1]], color=RED if selected else LIGHT, lw=2, zorder=1)
        if selected and not after:
            xx, yy = .45*p[0]+.55*q[0], .45*p[1]+.55*q[1]
            ax.text(xx, yy, rf'$Z_{{A_{edge}}}$', fontsize=13, color=RED,
                    bbox=dict(fc='white', ec='none', pad=2), zorder=4)
    for v, (x, y) in pos.items():
        sign = '+' if after or v not in 'bd' else '−'
        node(ax, x, y, f'{v}\n{sign}', COL[v], r=.32, size=13)
    ax.text(3+offset, .65, 'Reported vertex signs' if not after else 'Gauss signs after these Z gates',
            ha='center', fontsize=12, color=INK)
ax.text(.3, .18, 'The vertices have been measured and released. The right-hand nodes label Gauss checks, not surviving vertex qubits.', fontsize=11.5, color=GRAY)
save(fig, '08-vertex-frame')

# 9. A paired check must have one shared cat across both data blocks.
fig, ax = canvas(12, 6.8, r'While gauged, measure the PRODUCT $N_0^Z$, with one eight-leaf cat',
                 'All eight gold wires belong to ONE cat. Couple both panels, then read all eight leaves in X.')
for block_i, block in enumerate('BC'):
    x = .35+6*block_i
    ax.text(x, 5.1, f'Data block {block}', fontsize=15, color=COL['a'], weight='bold')
    for q in range(4):
        leaf_index = q+4*block_i
        port(ax, x, 4.35-1.0*q, rf'$\ell_{leaf_index}$', rf'${block}_{q}$', 'Z', COL['a'], width=5.1)
ax.text(.25, .55, r'$N^Z_0=Z_{B_0}Z_{B_1}Z_{B_2}Z_{B_3}\,Z_{C_0}Z_{C_1}Z_{C_2}Z_{C_3}$', fontsize=15, color=INK)
ax.text(.25, .16, 'One reported parity is obtained. Measuring the two block checks separately would be a different measurement.', fontsize=12, color=GRAY)
save(fig, '09-paired-check')

# 10. Cycle checks as graph operators, with exact leaf ports.
fig, ax = canvas(12, 7.3, 'Cycle checks: multiply Z only on the selected gauge edges',
                 'These are two different checks, with a fresh cat for each. The graph vertices are not measured here.')
node(ax, 1.1, 4.9, 'a', COL['a']); node(ax, 4.9, 4.9, 'b', COL['b'])
for ymid, q in [(5.6, 7), (4.2, 15)]:
    pp = MPath([(1.35, 4.9), (3, ymid+(.3 if q == 7 else -.3)), (4.65, 4.9)], [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3])
    ax.add_patch(PathPatch(pp, fc='none', ec=GAUGE, lw=2))
    node(ax, 3, (4.9+ymid+(.3 if q == 7 else -.3))/2, rf'$A_{{{q}}}$', GAUGE, r=.29, square=True, size=12)
ax.text(.35, 3.85, r'$L_{(7,15)}=Z_{A_7}Z_{A_{15}}$', fontsize=15, color=INK)
tri = {'a': (8.9, 5.7), 'b': (7.0, 4.4), 'c': (10.8, 4.4)}
for p, q, edge in [('a', 'b', 7), ('a', 'c', 11), ('b', 'c', 8)]:
    x, y = tri[p]; xx, yy = tri[q]
    ax.plot([x, xx], [y, yy], color=GAUGE, lw=2, zorder=1)
    node(ax, (x+xx)/2, (y+yy)/2, rf'$A_{{{edge}}}$', GAUGE, r=.28, square=True, size=12)
for v, (x, y) in tri.items(): node(ax, x, y, v, COL[v])
ax.text(6.35, 3.85, r'$L_{(7,8,11)}=Z_{A_7}Z_{A_8}Z_{A_{11}}$', fontsize=15, color=INK)
for column, qs in [(0, [7, 15]), (1, [7, 8, 11])]:
    for i, q in enumerate(qs):
        port(ax, .4+6*column, 3.1-.85*i, rf'$\ell_{i}$', rf'$A_{{{q}}}$', 'Z', GAUGE, width=5.0)
ax.text(.25, .25, 'Use ten parallel-edge checks and six independent triangle checks: sixteen cycle constraints in total.', fontsize=12, color=GRAY)
save(fig, '10-cycle-checks')

# 11. An entire Gauss check, every actual helper and target explicitly labelled.
fig, ax = canvas(14, 8.1, r'A complete local Gauss measurement: $G_a$',
                 'All twelve leaves below form ONE verified cat. Each leaf has exactly one controlled target factor.')
for col_i in range(2):
    x = .25+4.55*col_i
    ax.text(x, 6.5, 'Four gauge-X factors', fontsize=13, color=GAUGE, weight='bold')
    for row_i in range(4):
        j = col_i*4+row_i; q = R[5][j]
        port(ax, x, 5.82-1.25*row_i, rf'$\ell_{j}$', rf'$A_{{{q}}}$', 'X', GAUGE, width=4.1)
x = 9.4
ax.text(x, 6.5, 'Four data-pair SWAPs', fontsize=13, color=COL['a'], weight='bold')
for q in range(4):
    port(ax, x, 5.82-1.25*q, rf'$\ell_{{{8+q}}}$', rf'$B_{q}$', 'X', COL['a'], second=rf'$C_{q}$', width=4.1)
ax.text(.25, .85, r'$G_a=(X_{A_0}X_{A_3}X_{A_6}X_{A_7}X_{A_{10}}X_{A_{11}}X_{A_{12}}X_{A_{15}})\,\mathrm{SWAP}_{0}\mathrm{SWAP}_{1}\mathrm{SWAP}_{2}\mathrm{SWAP}_{3}$', fontsize=14, color=INK)
ax.text(.25, .30, 'Multiply all twelve leaf-X reports. The old vertex a is absent; it only labels this check and its data group.', fontsize=12, color=GRAY)
save(fig, '11-gauss-check')

# 12. Decode a noisy gauge word, then ordinary data SWAPs in whole groups.
example_t = {'a': 0, 'b': 1, 'c': 0, 'd': 1, 'e': 0}
word = [example_t[u] ^ example_t[v] for u, v in EDGES.values()]
measured = word.copy(); measured[7] ^= 1
decoded = decoder.decode_gauge_z(measured)
assert decoded['corrected_cut_bits'] == tuple(word)
assert decoded['swap_pair_labels'] == tuple(list(range(4, 8))+list(range(12, 16)))
fig, ax = canvas(12, 7.1, 'Ungauging: decode the whole gauge word, then undo its partial SWAPs',
                 'Example decoded offset: (ta,tb,tc,td,te) = (0,1,0,1,0). Teal connections have gauge bit 1.')
bundled_graph(ax, positions(3.15, 3.3, 1.95), example_t)
for i, (v, qs) in enumerate([('b', range(4, 8)), ('d', range(12, 16))]):
    top = 4.8-2.3*i
    ax.text(6.45, top+.55, rf'Apply $T_{v}$ to group {v}', fontsize=14, color=COL[v], weight='bold')
    ax.text(6.35, top, 'B', color=COL[v], va='center', fontsize=14)
    ax.text(6.35, top-1.0, 'C', color=COL[v], va='center', fontsize=14)
    for j, q in enumerate(qs):
        x = 7.25+.95*j
        node(ax, x, top, str(q), COL[v], r=.18, size=10)
        node(ax, x, top-1, str(q), COL[v], r=.18, square=True, fill=False, size=10)
        ax.plot([x, x], [top-.19, top-.81], color=COL[v], lw=1.6, zorder=1)
        swap(ax, x, top-.30, top-.70, color=COL[v])
ax.text(.3, .55, 'A single wrong report m7 = 0 is corrected to w7 = 1 using all twenty bits, before extracting tb.', fontsize=12, color=RED)
ax.text(.3, .16, 'Only data groups b and d are exchanged in this example; a, c and e are untouched. No controlled SWAP is needed.', fontsize=12, color=GRAY)
save(fig, '12-ungauging')

# 13. Logical amplitudes and the non-stabilizer location of the output state.
fig = plt.figure(figsize=(12, 4.8), facecolor='white')
axes = fig.subplots(1, 3, gridspec_kw={'width_ratios': [1.15, 1, 1.05]})
fig.subplots_adjust(left=.065, right=.97, bottom=.18, top=.75, wspace=.5)
fig.suptitle('The retained resource is an encoded non-stabilizer state', fontsize=19, color=INK, weight='bold', y=.96)
ax = axes[0]
ax.bar(range(3), [2/math.sqrt(6), 1/math.sqrt(6), 1/math.sqrt(6)], color='#455B70', width=.55)
ax.set_xticks(range(3), [r'$|00\rangle$', r'$|01\rangle$', r'$|10\rangle$'])
ax.set_ylim(0, 1.0); ax.set_ylabel('Real amplitude'); ax.set_title(r'After positive SWAP projection: $|M_2\rangle$', fontsize=11.5, color=INK)
for i, text in enumerate([r'$2/\sqrt{6}$', r'$1/\sqrt{6}$', r'$1/\sqrt{6}$']):
    ax.text(i, [2/math.sqrt(6), 1/math.sqrt(6), 1/math.sqrt(6)][i]+.04, text, ha='center', fontsize=12)
ax = axes[1]
ax.bar([0, 1], [2/math.sqrt(5), 1/math.sqrt(5)], color='#455B70', width=.55)
ax.set_xticks([0, 1], [r'$|0\rangle$', r'$|1\rangle$']); ax.set_ylim(0, 1.05)
ax.set_title(r'Keep decoded $Z_{B_0}^{L}=+1$', fontsize=12, color=INK)
for i, text in enumerate([r'$2/\sqrt{5}$', r'$1/\sqrt{5}$']):
    ax.text(i, [2/math.sqrt(5), 1/math.sqrt(5)][i]+.04, text, ha='center', fontsize=12)
ax = axes[2]
angles = [2*math.pi*i/200 for i in range(201)]
ax.plot([math.cos(t) for t in angles], [math.sin(t) for t in angles], color=LIGHT, lw=2)
ax.axhline(0, color=LIGHT); ax.axvline(0, color=LIGHT)
for x, z, label in [(1, 0, '+X'), (-1, 0, '−X'), (0, 1, '+Z'), (0, -1, '−Z')]:
    ax.plot(x, z, 'o', color=GRAY, ms=5)
    ax.text(1.20*x, 1.18*z, label, ha='center', va='center', fontsize=11, color=GRAY)
ax.annotate('', xy=(.8, .6), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='#455B70', lw=2.5))
ax.plot(.8, .6, 'o', color='#455B70', ms=8)
ax.text(.85, .75, 'M', fontsize=13, color='#455B70')
ax.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), aspect='equal'); ax.axis('off')
ax.set_title('Logical Bloch X–Z plane\n(x,y,z) = (4/5, 0, 3/5)', fontsize=11.5, color=INK)
for ax in axes[:2]:
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=11)
save(fig, '13-magic-output')

manifest = {'figure_names': FIGURES, 'group_colors': COL, 'gauge_color': GAUGE,
            'cat_color': CAT, 'source_supports': R, 'graph_edges': {str(q): p for q, p in EDGES.items()},
            'ungauging_example': {'t': example_t, 'true_word': word, 'reported_word': measured,
                                   'corrected_word': decoded['corrected_cut_bits'],
                                   'swap_pairs': decoded['swap_pair_labels']},
            'scope': 'Scientific explanatory figures; circuit fragments specify connectivity, serial scheduling is in Synthesis.md'}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(f'Saved {len(FIGURES)} PNG/SVG figure pairs to {OUT}')
