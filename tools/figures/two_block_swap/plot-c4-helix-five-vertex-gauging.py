"""Human-readable figures for the five-vertex SWAP-gauging walkthrough."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/c4-helix-matplotlib')
from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'output/c4-helix-five-vertex-gauging.json').read_text())
OUT = ROOT / 'notes/figures/c4-helix/five-vertex-gauging'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
ink, purple, red, blue, orange, gray = '#233444', '#7755A4', '#AD3F58', '#2473A6', '#B86B22', '#687784'

def canvas(w, h, title, subtitle=''):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis('off')
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.025, top=0.975)
    ax.text(.2, h-.38, title, fontsize=19, color=ink, weight='bold', va='top')
    if subtitle:
        ax.text(.2, h-.91, subtitle, fontsize=12, color=gray, va='top')
    return fig, ax

def vertex(ax, x, y, label, color=purple, radius=.24):
    ax.add_patch(Circle((x,y),radius,fc=color,ec='white',lw=2,zorder=5))
    ax.text(x,y,label,ha='center',va='center',fontsize=16,color='white',zorder=6)

def gauge(ax, x, y, label, width=.65):
    ax.add_patch(FancyBboxPatch((x-width/2,y-.22),width,.44,
                 boxstyle='round,pad=0.025',fc='#FFF1F4',ec=red,lw=1.7,zorder=5))
    ax.text(x,y,label,ha='center',va='center',fontsize=14,color=red,zorder=6)

def arrow(ax, start, end, color=gray):
    ax.annotate('', xy=end, xytext=start, arrowprops={'arrowstyle':'->','lw':1.8,'color':color})

def save(fig, name):
    for ext in ('png','svg'):
        fig.savefig(OUT/f'{name}.{ext}',dpi=180,facecolor='white')
    plt.close(fig)

# 1: bundled drawing plus an exact edge table, avoiding twenty tangled labels.
fig, ax = canvas(12, 8, 'The five-vertex graph: two edges between every pair',
                 'Purple circles are vertices. A labelled line represents two separate edges, not one edge.')
pos={v:(3.25+2.20*math.cos(math.pi/2-2*math.pi*i/5),
        3.70+2.20*math.sin(math.pi/2-2*math.pi*i/5)) for i,v in enumerate('abcde')}
for pair,qs in DATA['pair_edges'].items():
    u,v=pair; x,y=pos[u]; xx,yy=pos[v]
    ax.plot([x,xx],[y,yy],color='#A3AFB9',lw=2,zorder=1)
    # Position close to the first endpoint, keeping centre crossings free.
    t=.32 if pair not in ('ae','be','ce','de') else .64
    lx,ly=x*(1-t)+xx*t,y*(1-t)+yy*t
    ax.text(lx,ly,f'{qs[0]}, {qs[1]}',ha='center',va='center',fontsize=11,color=red,
            bbox={'facecolor':'white','edgecolor':'#E3E7EB','boxstyle':'round,pad=.20'},zorder=4)
for v,(x,y) in pos.items():vertex(ax,x,y,v)
ax.text(.4,.55,'Crossings are not vertices. Numbers label gauge qubits $A_q$.',fontsize=11,color=gray)
ax.text(7.0,6.15,'Endpoints',fontsize=13,color=purple,weight='bold')
ax.text(9.0,6.15,'Gauge qubits',fontsize=13,color=red,weight='bold')
for i,(pair,qs) in enumerate(DATA['pair_edges'].items()):
    y=5.64-.43*i
    ax.text(7.2,y,f'{pair[0]} — {pair[1]}',fontsize=13,color=ink)
    ax.text(9.05,y,rf'$A_{{{qs[0]}}},\ A_{{{qs[1]}}}$',fontsize=13,color=red)
ax.text(7.0,.62,'5 vertices · 20 edges · degree 8\n16 independent cycles',fontsize=12,color=gray)
save(fig,'01-graph')

# 2: one incidence resource in the paper's CNOT convention.
fig, ax = canvas(12, 5, 'Resource preparation on one edge',
                 'Apply this same two-CNOT pattern to all twenty edges: forty CNOTs in total.')
ys=[3.2,2.2,1.2]
for y,label in zip(ys,[r'$u:\ |+\rangle$',r'$A_q:\ |0\rangle$',r'$v:\ |+\rangle$']):
    ax.text(.4,y,label,fontsize=16,va='center',color=purple if y!=2.2 else red)
    ax.plot([2.2,6.2],[y,y],color=gray,lw=1.6)
for x,y in [(3.4,3.2),(4.9,1.2)]:
    ax.plot([x,x],[y,2.2],color=ink,lw=1.7)
    ax.plot(x,y,'o',color=ink,ms=7)
    ax.add_patch(Circle((x,2.2),.13,fc='white',ec=ink,lw=1.8))
    ax.plot([x-.13,x+.13],[2.2,2.2],color=ink,lw=1.5)
    ax.plot([x,x],[2.07,2.33],color=ink,lw=1.5)
ax.text(7,3.2,r'$K_q=Z_u Z_{A_q} Z_v$',fontsize=18,color=ink)
ax.text(7,2.28,'Edge bit = endpoint-bit parity',fontsize=13,color=gray)
ax.text(7,1.62,r'$z_q=t_u\oplus t_v$',fontsize=18,color=red)
ax.text(.4,.4,r'Vertices start in $|+\rangle$. Gauge edges start independently in $|0\rangle$.',fontsize=12,color=gray)
save(fig,'02-resource')

# 3: five boxes give all twenty enrichment targets, no overlapping lines.
fig, ax = canvas(12, 6.6, 'Symmetry enrichment: four controlled SWAPs per vertex',
                 'A physical pair means Bq and Cq. Gauge qubit Aq is not a SWAP target.')
for i,v in enumerate('abcde'):
    y=4.88-.88*i
    vertex(ax,.85,y,v)
    ax.plot([.85,.85,9.64],[y+.25,y+.40,y+.40],color=purple,lw=1.8)
    for j,q in enumerate(DATA['controls'][v]):
        x=2.3+2.3*j
        ax.plot([x+.44,x+.44],[y+.40,y+.31],color=purple,lw=1.8)
        ax.add_patch(FancyBboxPatch((x-.42,y-.29),1.72,.58,boxstyle='round,pad=.04',fc='#F2F6FA',ec='#A8B8C6',lw=1.2))
        ax.text(x+.44,y,rf'SWAP($B_{{{q}}},C_{{{q}}}$)',ha='center',va='center',fontsize=12,color=ink)
ax.text(.4,.36,r'Control $|0\rangle$: do nothing. Control $|1\rangle$: exchange the two data qubits.',fontsize=12,color=gray)
save(fig,'03-enrichment')

# 4: two alternative paths with a loop; no ambiguity at crossings.
fig, ax = canvas(11, 6.5, 'Eliminating temporary vertices: multiply edge relations',
                 'Two endpoint Z operators become a string of Z operators on surviving gauge qubits.')
vertex(ax,1.3,4.5,'b'); vertex(ax,5.4,4.5,'a'); vertex(ax,9.5,4.5,'c')
ax.plot([1.3,9.5],[4.5,4.5],color=gray,lw=2,zorder=1)
gauge(ax,3.3,4.5,r'$A_7$'); gauge(ax,7.4,4.5,r'$A_{11}$')
ax.text(3.3,3.65,r'$Z_b Z_{A_7} Z_a=+1$',ha='center',fontsize=14,color=ink)
ax.text(7.4,3.65,r'$Z_a Z_{A_{11}} Z_c=+1$',ha='center',fontsize=14,color=ink)
ax.text(5.4,2.61,r'Multiply: $Z_b Z_c = Z_{A_7} Z_{A_{11}}$',ha='center',fontsize=18,color=ink)
ax.text(5.4,1.6,r'$Z_a^2=I$: the interior vertex cancels.',ha='center',fontsize=14,color=gray)
ax.text(5.4,.63,'These equalities hold on states satisfying the edge constraints.',ha='center',fontsize=12,color=gray)
save(fig,'04-path')

# 5: independent cycle types.
fig, ax = canvas(12, 6.5, 'Flux constraints: two short cycle types',
                 'Multiply edge relations around a loop: every temporary vertex cancels.')
vertex(ax,1.1,3.7,'a'); vertex(ax,4.6,3.7,'b')
for y,q in [(4.3,7),(3.1,15)]:
    ax.plot([1.1,2.8,4.6],[3.7,y,3.7],color=gray,lw=2)
    gauge(ax,2.8,y,rf'$A_{{{q}}}$')
ax.text(2.8,2.1,r'$Z_{A_7}Z_{A_{15}}=+1$',ha='center',fontsize=17,color=ink)
ax.text(2.8,1.35,'10 parallel-edge cycles',ha='center',fontsize=13,color=gray)
tri={'a':(8.4,4.7),'b':(6.5,2.9),'c':(10.3,2.9)}
for u,v,q in [('a','b',7),('b','c',8),('a','c',11)]:
    x,y=tri[u]; xx,yy=tri[v]
    ax.plot([x,xx],[y,yy],color=gray,lw=2)
    gauge(ax,(x+xx)/2,(y+yy)/2,rf'$A_{{{q}}}$')
for v,(x,y) in tri.items():vertex(ax,x,y,v)
ax.text(8.4,2.1,r'$Z_{A_7}Z_{A_8}Z_{A_{11}}=+1$',ha='center',fontsize=17,color=ink)
ax.text(8.4,1.35,'6 additional independent triangles',ha='center',fontsize=13,color=gray)
ax.text(.4,.4,'Together: 16 independent flux checks, each of weight two or three.',fontsize=12,color=gray)
save(fig,'05-flux')

# 6: the worked inner check, one distinct controller path per row.
fig, ax = canvas(12, 7, 'Dressing the inner check on physical labels 0, 1, 2, 3',
                 'Use a as the check anchor. Drawings below show separate paths, not extra copies of the graph.')
cases=[(0,'a',None),(1,'e',0),(2,'c',11),(3,'d',3)]
for i,(q,v,edge) in enumerate(cases):
    y=5.2-1.12*i
    ax.text(.35,y,rf'Data pair $B_{{{q}}},C_{{{q}}}$',fontsize=14,va='center',color=ink)
    vertex(ax,3.2,y,v)
    if edge is None:
        ax.text(5.5,y,'Controller = anchor: empty path',fontsize=13,va='center',color=gray)
        ax.text(10.1,y,r'$W=I$',fontsize=15,va='center',color=red)
    else:
        ax.plot([3.2,7.4],[y,y],color=gray,lw=2)
        gauge(ax,5.3,y,rf'$A_{{{edge}}}$'); vertex(ax,7.4,y,'a')
        ax.text(8.25,y,rf'$W_{{{edge}}}(X^B_{{{q}}}X^C_{{{q}}})$',fontsize=15,va='center',color=red)
ax.text(.35,.46,'Wf(P) applies Z to gauge qubit Af exactly when the matter-pair eigenvalue P is −1.',fontsize=12,color=gray)
save(fig,'06-dressing')

# 7: outcome corrections show paired signs rather than dense geometry.
fig, ax = canvas(11, 6, 'Correct two negative vertex outcomes with an edge path',
                 'Example: xb = xc = −1; the other three outcomes are +1.')
vertex(ax,1.5,3.6,'b'); vertex(ax,5.4,3.6,'a'); vertex(ax,9.3,3.6,'c')
ax.plot([1.5,9.3],[3.6,3.6],color=red,lw=3)
gauge(ax,3.45,3.6,r'$A_7$'); gauge(ax,7.35,3.6,r'$A_{11}$')
for x,label in [(1.5,'−1 → +1'),(5.4,'+1 → +1'),(9.3,'−1 → +1')]:
    ax.text(x,2.75,label,ha='center',fontsize=16,color=ink)
ax.text(5.4,1.78,r'Apply $Z_{A_7}Z_{A_{11}}$',ha='center',fontsize=19,color=red)
ax.text(5.4,.72,'Two flips cancel at a. The global product of outcomes is unchanged.',ha='center',fontsize=12,color=gray)
save(fig,'07-correction')
print('Saved seven PNG/SVG figure pairs to',OUT)
