"""Editable circuits for fused coordinates and the transported Gauss tail."""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from single_cz_persistent import transported_gauss_program

out=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","svg.fonttype":"none","font.size":11})
fig,axes=plt.subplots(3,1,figsize=(19,14),gridspec_kw={"height_ratios":[1.6,2.5,5]})

ax=axes[0];ax.set_xlim(0,20);ax.set_ylim(3,0);ax.axis("off")
ax.text(.1,.25,"Persistent gauging coordinates: one fused entry, three combined positive certificates",fontsize=16,weight="bold")
boxes=[(.1,2.7,"Verified graph\n5 vertices + 4 edges"),(3.1,3.3,"Fused enrichment / V\n36 CX + 40 T/Tdg"),
       (6.7,7.7,"Repeat up to 5 times; stop at 3 positives\n18 code checks -> 4 X stars + sign repair -> transported root"),
       (14.8,4.8,"MZ graph edges; discard reports\nRetain encoded CZ magic")]
for x,w,label in boxes:
    ax.add_patch(Rectangle((x,.7),w,1.2,facecolor="#e8f0fa",edgecolor="#294c70"))
    ax.text(x+w/2,1.3,label,ha="center",va="center",fontsize=10)
for a,b in ((2.8,3.1),(6.4,6.7),(14.4,14.8)):
    ax.annotate("",xy=(b,1.3),xytext=(a,1.3),arrowprops={"arrowstyle":"->","color":"#294c70"})
ax.text(.1,2.55,"Tree edges: ab, ac, ad, ae.  No cut decoding or second data byproduct.  One global two-fault budget.",fontsize=11)

def wires(ax,labels,xmax):
    for y,label in enumerate(labels):
        ax.plot([-.5,xmax],[y,y],color="#7b8da0",lw=.85)
        ax.text(-.8,y,label,ha="right",va="center")
def gate(ax,x,y,label):
    ax.add_patch(Rectangle((x-.32,y-.25),.64,.5,facecolor="#fff1d7" if label=="MZ" else "#e7effa",edgecolor="#294c70",zorder=5))
    ax.text(x,y,label,ha="center",va="center",fontsize=10,zorder=6)
def cx(ax,x,c,t):
    ax.plot([x,x],[c,t],color="#294c70",lw=1.1)
    ax.add_patch(Circle((x,c),.06,color="#294c70",zorder=5))
    ax.add_patch(Circle((x,t),.16,facecolor="white",edgecolor="#294c70",zorder=5))
    ax.plot([x-.11,x+.11],[t,t],color="#294c70",zorder=6)
    ax.plot([x,x],[t-.11,t+.11],color="#294c70",zorder=6)

ax=axes[1];ax.set_xlim(-3.4,13);ax.set_ylim(4,-1.2);ax.axis("off")
ax.text(-3.2,-.75,"Expanded fused port D19 (sign -1): two controls, two physical T rotations",fontsize=14,weight="bold")
wires(ax,["a_e (vertex)","A3 (edge ae)","D19"],12)
gate(ax,1,2,"Tdg");cx(ax,2.5,0,2);cx(ax,4,1,2);gate(ax,5.5,2,"T")
gate(ax,7,0,"H");gate(ax,8.5,0,"MZ");ax.text(8.5,-.4,"reported x_e",ha="center",fontsize=9)
gate(ax,10.5,1,"Z")
ax.annotate("",xy=(10.5,.72),xytext=(8.9,.05),arrowprops={"arrowstyle":"->","linestyle":"--","color":"#a15c1a"})
ax.text(10.5,1.6,"if x_e = 1",ha="center",fontsize=9,color="#a15c1a")
ax.text(-3.2,3.2,"Apply the corresponding signed ports to D16..D18 before reading a_e. Root-block ports have only their vertex control.",fontsize=10)

ops=transported_gauss_program(4)
start=next(i for i,(op,qs) in enumerate(ops) if qs==(19,) and op in ("T","TDG"))
tail=ops[start:]
labels={19:0,24:1,44:2,45:3,20:4,21:5,22:6,23:7}
ax=axes[2];ax.set_xlim(-3.4,len(tail)+1);ax.set_ylim(9,-1.5);ax.axis("off")
ax.text(-3.2,-1,"Transported root tail: all graph interactions follow the final data port",fontsize=14,weight="bold")
wires(ax,["D19","s (already live)","f1 (active)","f2 (active)","A0 = ab","A1 = ac","A2 = ad","A3 = ae"],len(tail)+.5)
for x,(op,qs) in enumerate(tail):
    if op=="CX":cx(ax,x,labels[qs[0]],labels[qs[1]])
    else:
        q=labels[qs[0]];gate(ax,x,q,{"TDG":"Tdg"}.get(op,op))
        if op=="MZ":
            ax.add_patch(Rectangle((x+.34,q-.08),len(tail)+.2-x,.16,color="white",zorder=3))
            for d in (-.03,.03):ax.plot([x+.34,len(tail)+.5],[q+d,q+d],color="#7b8da0",lw=.8,zorder=4)
            ax.text(len(tail)+.6,q,"b" if q==1 else "flag",va="center",fontsize=10)
ax.text(-3.2,8.3,"Earlier data ports use the existing rolling two-fault flags. Any root flag rejects; count b = 0 only after code restoration and star repairs.",fontsize=10)
fig.tight_layout(h_pad=2)
for ext in ("png","svg"):fig.savefig(out/f"15-persistent-coordinates.{ext}",dpi=150,bbox_inches="tight",facecolor="white")
plt.close(fig)
print(out/"15-persistent-coordinates.png")
