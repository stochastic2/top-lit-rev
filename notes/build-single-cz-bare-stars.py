"""Render actual bare star and terminal parity primitives to editable SVG/PNG."""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from single_cz_graph_stars import bare_star_program

out=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"svg.fonttype":"none"})
fig,axes=plt.subplots(2,1,figsize=(15,10),gridspec_kw={"height_ratios":[1.1,1]})


def draw(ax,labels,ops,title,subtitle):
    ax.set_xlim(-2.4,12.5)
    ax.set_ylim(len(labels)+1.8,-1.8)
    ax.axis("off")
    ax.text(-2.25,-1.35,title,fontsize=15,weight="bold")
    ax.text(-2.25,-.72,subtitle,fontsize=10)
    for q,label in enumerate(labels):
        ax.plot([-.4,11.8],[q,q],color="#64748b",lw=.9)
        ax.text(-.65,q,label,ha="right",va="center")
    def box(x,q,text,color="#e9f1fc"):
        ax.add_patch(Rectangle((x-.34,q-.27),.68,.54,facecolor=color,edgecolor="#244466",zorder=8))
        ax.text(x,q,text,ha="center",va="center",fontsize=10,zorder=9)
    measured={}
    for col,(op,qs) in enumerate(ops):
        if op=="CX":
            c,t=qs
            ax.plot([col,col],[c,t],color="#244466",lw=1)
            ax.add_patch(Circle((col,c),.07,color="#244466",zorder=5))
            ax.add_patch(Circle((col,t),.18,facecolor="white",edgecolor="#244466",zorder=6))
            ax.plot([col-.12,col+.12],[t,t],color="#244466",zorder=7)
            ax.plot([col,col],[t-.12,t+.12],color="#244466",zorder=7)
        else:
            q=qs[0]
            box(col,q,{"PREP":"|0>","MZ":"MZ"}.get(op,op),"#fff0d5" if op=="MZ" else "#e9f1fc")
            if op=="MZ":
                measured[q]=col
                ax.add_patch(Rectangle((col+.36,q-.07),11.44-col,.14,color="white",zorder=5))
                for d in (-.035,.035):ax.plot([col+.36,11.8],[q+d,q+d],color="#64748b",lw=.8,zorder=6)
    return box,measured


box,measured=draw(axes[0],["A0","A4","A5","A6","A10","s"],bare_star_program(5),
                   "Compact13 bare star b: five CNOTs; no flags",
                   "Between the existing V passes. Twenty data wires are spectators. Complete all helper readouts.")
box(10,0,"Z^b","#fff0d5")
axes[0].text(8,5.5,"reported b",ha="center",color="#995014")
axes[0].annotate("",xy=(10,.33),xytext=(8.4,5),arrowprops={"arrowstyle":"->","linestyle":"--","color":"#995014"})
axes[0].text(5.4,6.6,"Controller hooks may affect several edges. Cycle sectors are repaired at the end.",ha="center",fontsize=10)

cycle_ops=[("PREP",(3,)),("CX",(0,3)),("CX",(1,3)),("CX",(2,3)),("MZ",(3,))]
box,measured=draw(axes[1],["A0","A1","A4","w"],cycle_ops,
                   "Terminal cycle (0,1,4): three CNOTs per parity measurement",
                   "Acquire the entire nine-cycle vector. Require three identical complete records (bounded at nine).")
axes[1].add_patch(Rectangle((5.4,3.8),5.2,.8,facecolor="#fff7e7",edgecolor="#995014"))
axes[1].text(8,4.2,"History certificate → s0",ha="center",color="#995014")
axes[1].annotate("",xy=(5.5,4.05),xytext=(4.4,3),arrowprops={"arrowstyle":"->","linestyle":"--","color":"#995014"})
box(10,2,"X^s0","#fff0d5")
axes[1].annotate("",xy=(10,2.35),xytext=(10,3.8),arrowprops={"arrowstyle":"->","linestyle":"--","color":"#995014"})
axes[1].text(5.5,5.25,"Only certified parities drive non-tree X corrections. Edge Z readout follows afterwards.",ha="center",fontsize=10)
fig.tight_layout(h_pad=2)
for ext in ("svg","png"):
    fig.savefig(out/f"12-bare-star-and-final-cycles.{ext}",dpi=150,bbox_inches="tight",facecolor="white")
plt.close(fig)
print(out/"12-bare-star-and-final-cycles.png")
