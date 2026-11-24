"""Render actual compact eight-port X/Z circuits and flag-dependent feedback."""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from single_cz_compact_checks import compact_pauli_program

out=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","svg.fonttype":"none","font.size":10})
fig,axes=plt.subplots(2,1,figsize=(20,13))
support=(0,3,6,7,10,11,12,15)
for ax,axis in zip(axes,"XZ"):
    ops=compact_pauli_program(axis,8)
    ax.set_xlim(-2.3,len(ops)+.8);ax.set_ylim(14.4,-2.4);ax.axis("off")
    ax.text(-2.1,-1.8,f"R5 {axis} check: 16 CNOTs; four flags; {'2' if axis=='X' else '8'} H gates",fontsize=16,weight="bold")
    labels=[f"D{q}" for q in support]+["s"]+[f"f{j}" for j in range(4)]
    for q,label in enumerate(labels):
        ax.plot([-.4,len(ops)+.3],[q,q],color="#8a99aa",lw=.7)
        ax.text(-.7,q,label,ha="right",va="center",weight="bold" if q>=8 else "normal")
    for x,(op,qs) in enumerate(ops):
        if op=="CX":
            c,t=qs;ax.plot([x,x],[c,t],color="#244466",lw=1)
            ax.add_patch(Circle((x,c),.07,color="#244466",zorder=4))
            ax.add_patch(Circle((x,t),.18,facecolor="white",edgecolor="#244466",zorder=5))
            ax.plot([x-.12,x+.12],[t,t],color="#244466",zorder=6)
            ax.plot([x,x],[t-.12,t+.12],color="#244466",zorder=6)
        else:
            q=qs[0]
            ax.add_patch(Rectangle((x-.35,q-.3),.7,.6,facecolor="#fff1d8" if op=="MZ" else "#e7effa",edgecolor="#244466",zorder=7))
            ax.text(x,q,{"PREP":"|0>","MZ":"MZ"}.get(op,op),ha="center",va="center",fontsize=9,zorder=8)
            if op=="MZ":
                ax.add_patch(Rectangle((x+.36,q-.12),len(ops)-x,.24,color="white",zorder=3))
                for d in (-.035,.035):ax.plot([x+.36,len(ops)+.3],[q+d,q+d],color="#8a99aa",lw=.8,zorder=4)
                ax.text(len(ops)+.4,q,"b" if q==8 else f"f{q-9}",va="center",fontsize=9)
    ax.text(-2.1,13.4,"Reported flags zero: use code parity b.  Any nonzero flag: pause, acquire two equal fallback records, repair a unique class or reject.",fontsize=11,color="#8f521d")
fig.tight_layout(h_pad=2)
for ext in ("png","svg"):fig.savefig(out/f"14-compact-pauli-checks.{ext}",dpi=150,bbox_inches="tight",facecolor="white")
plt.close(fig)
print(out/"14-compact-pauli-checks.png")
