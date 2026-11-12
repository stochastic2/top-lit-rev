"""Plot the checked SWAP-gauging graph and an unambiguous edge table."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

root = Path(__file__).resolve().parent.parent
graph = json.loads((root / 'output/c4-helix-swap-graph.json').read_text())
edges = [tuple(edge) for edge in graph['edges']]
assert len(edges) == 20 and len(graph['vertices']) == 10
assert sum((f'c{i+5}', f'c{j}') in edges for i in range(5) for j in range(5)) == 20
out = root / 'notes/figures/c4-helix'
out.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans', 'svg.fonttype':'none'})
fig = plt.figure(figsize=(14, 8), facecolor='white')
ax = fig.add_axes([0.05,0.17,0.55,0.65])
mat = fig.add_axes([0.66,0.22,0.30,0.55])
blue, orange, muted = '#2369A8', '#C76C26', '#526273'
palette = ['#3E759B','#9B6DA8','#3D8B79','#B9823E','#AF6679']
pos = {f'c{j}':(0,4-j) for j in range(5)}
pos.update({f'c{i}':(3.8,9-i) for i in range(5,10)})
for u,v in edges:
    x1,y1=pos[u]; x2,y2=pos[v]
    ax.plot([x1,x2],[y1,y2],color=palette[int(u[1:])-5],lw=2.2,alpha=0.70,zorder=1)
for name,(x,y) in pos.items():
    j=int(name[1:]); color=blue if j<5 else orange
    ax.add_patch(Circle((x,y),0.205,facecolor='white',edgecolor='white',lw=7,zorder=3))
    ax.add_patch(Circle((x,y),0.205,facecolor=color,edgecolor=color,lw=1,zorder=4))
    ax.text(x,y,rf'$c_{{{j}}}$',ha='center',va='center',color='white',fontsize=17,zorder=5)
    if j<5:
        ax.text(x-0.35,y, f'SWAP labels\n{4*j}–{4*j+3}',ha='right',va='center',fontsize=11,color=muted)
ax.text(0,4.64,'SWAP controllers',ha='center',fontsize=14,color=blue,fontweight='bold')
ax.text(3.8,4.64,'Upper-check anchors',ha='center',fontsize=14,color=orange,fontweight='bold')
ax.set_xlim(-1.42,4.5); ax.set_ylim(-0.48,4.94); ax.axis('off')

for i in range(5):
    for j in range(5):
        present=(f'c{i+5}',f'c{j}') in edges
        mat.add_patch(Rectangle((j,4-i),0.91,0.91,facecolor='#EDF3F8' if present else '#F3F4F5',edgecolor='white',lw=2))
        if present:
            mat.text(j+0.455,4-i+0.455,rf'$A_{{{i+5},{j}}}$',ha='center',va='center',fontsize=14,color=blue)
        else:
            mat.text(j+0.455,4-i+0.455,'—',ha='center',va='center',fontsize=17,color='#B0B7BE')
for j in range(5):
    mat.text(j+0.455,5.13,rf'$c_{{{j}}}$',ha='center',fontsize=14,color=blue)
for i in range(5):
    mat.text(-0.20,4-i+0.455,rf'$c_{{{i+5}}}$',ha='right',va='center',fontsize=14,color=orange)
mat.text(2.42,5.77,'Edge / gauge-qubit labels',ha='center',fontsize=14,fontweight='bold',color=muted)
mat.text(2.42,-0.55,r'$A_{i,j}$ sits on the edge joining $c_i$ and $c_j$.',ha='center',fontsize=11,color=muted)
mat.set_xlim(-0.6,5); mat.set_ylim(-0.95,6.02); mat.axis('off')

fig.text(0.05,0.935,'C4-Helix: graph for transversal SWAP gauging',fontsize=22,fontweight='bold',color='#1D3145')
fig.text(0.05,0.885,'10 vertices  ·  20 edges  ·  degree 4 at every vertex',fontsize=14,color=muted)
fig.text(0.05,0.09,'Only labelled circles are vertices; crossings of lines are not connections.',fontsize=12,color=muted)
fig.text(0.05,0.055,'Each vertex carries a temporary ancilla. Each edge carries one gauge qubit. Layout is schematic.',fontsize=12,color=muted)
for ext in ('png','svg'):
    fig.savefig(out / f'swap-gauging-graph.{ext}',dpi=200,facecolor='white')
plt.close(fig)
print(out / 'swap-gauging-graph.png')
print(out / 'swap-gauging-graph.svg')
