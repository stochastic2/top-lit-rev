"""Editable SVG/PNG from the actual one-remaining-fault fallback program."""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from single_cz_flagged import single_fault_pauli_program
import c4_helix_single_block_cz as m

out=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"svg.fonttype":"none"})
ops=single_fault_pauli_program("X",8)
labels=[f"D{q}" for q in m.SUPPORTS[5]]+["s: syndrome","f: flag"]
fig,ax=plt.subplots(figsize=(16,8))
ax.set_xlim(-4,len(ops)+2)
ax.set_ylim(12,-2)
ax.axis("off")
ax.text(-3.8,-1.45,"Conditional fallback: eight-port X stabilizer",fontsize=17,weight="bold")
ax.text(-3.8,-.8,"Only after a nonzero data flag: at most one of the global two faults can remain. 10 CNOTs.",fontsize=11)
for j,label in enumerate(labels):
    ax.plot([-.7,len(ops)+1],[j,j],color="#65758a",lw=.85)
    ax.text(-1,j,label,ha="right",va="center")
measured={}
for col,(op,qs) in enumerate(ops):
    if op=="CX":
        c,t=qs
        ax.plot([col,col],[c,t],color="#193d65",lw=1.1)
        ax.add_patch(Circle((col,c),.07,color="#193d65",zorder=5))
        ax.add_patch(Circle((col,t),.19,facecolor="white",edgecolor="#193d65",lw=1.1,zorder=6))
        ax.plot([col-.13,col+.13],[t,t],color="#193d65",zorder=7)
        ax.plot([col,col],[t-.13,t+.13],color="#193d65",zorder=7)
    else:
        q=qs[0]
        text={"PREP":"|0>","MZ":"MZ"}.get(op,op)
        ax.add_patch(Rectangle((col-.34,q-.27),.68,.54,facecolor="#fff0d4" if op=="MZ" else "#eaf2fc",edgecolor="#193d65",zorder=8))
        ax.text(col,q,text,ha="center",va="center",fontsize=10,zorder=9)
        if op=="MZ":
            measured[q]=col
            ax.add_patch(Rectangle((col+.36,q-.08),len(ops)+.64-col,.16,color="white",zorder=5))
            for delta in (-.035,.035):ax.plot([col+.36,len(ops)+1],[q+delta,q+delta],color="#65758a",lw=.8,zorder=6)
            ax.text(col,q+.48,"b" if q==8 else "r",color="#9c4a13",ha="center")
ax.add_patch(Rectangle((1,10.2),13.7,1.45,facecolor="#fff8ea",edgecolor="#9c4a13"))
ax.text(7.85,10.65,"r = 1: reject.  r = 0: continue the complete 18-check record.",ha="center",color="#763b13")
ax.text(7.85,11.2,"Two equal records → unique flag/syndrome class → physical Pauli correction → restart history.",ha="center",fontsize=10,color="#763b13")
ax.annotate("",xy=(14,10.2),xytext=(measured[9]+.45,9),arrowprops={"arrowstyle":"->","linestyle":"--","color":"#9c4a13"})
fig.tight_layout()
for ext in ("svg","png"):
    fig.savefig(out/f"11-flag-dependent-fallback.{ext}",dpi=150,bbox_inches="tight",facecolor="white")
plt.close(fig)
print(out/"11-flag-dependent-fallback.png")
