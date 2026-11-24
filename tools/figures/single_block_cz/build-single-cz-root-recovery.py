"""Editable local-Gauss recovery flow and actual dual-basis conditional check."""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from single_cz_flagged import dual_single_fault_pauli_program

out=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","svg.fonttype":"none","font.size":11})
fig,axes=plt.subplots(3,1,figsize=(19,12),gridspec_kw={"height_ratios":[2.3,4,1.9]})
ax=axes[0];ax.set_xlim(0,20);ax.set_ylim(4.4,0);ax.axis("off")
ax.text(.1,.15,"Graph-assisted recovery retains the four-data local Gauss measurement",fontsize=16,weight="bold")
def box(x,y,w,h,label,color="#e8f0fa"):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor="#294c70"));ax.text(x+w/2,y+h/2,label,ha="center",va="center",fontsize=10)
def arrow(a,b):ax.annotate("",xy=b,xytext=a,arrowprops={"arrowstyle":"->","color":"#294c70"})
box(.1,.55,4.5,1.1,"V -> code restoration + graph stars")
box(5.1,.55,4,1.1,"V -> flagged root G_a\n4 data W ports + graph edges")
box(9.6,.55,4.5,1.1,"No flag and positive root:\ncount one complete passing round")
arrow((4.6,1.1),(5.1,1.1));arrow((9.1,1.1),(9.6,1.1))
box(5.1,2.4,6.8,1.1,"Flag -> V -> 31 commuting Pauli checks\nTwo consecutive equal records; at most four", "#fff1d7")
box(12.5,2.4,6.9,1.1,"Joint affine decoder: one class -> Pauli repair\nAmbiguous/absent -> reject; discard flagged root vote", "#e6f2df")
arrow((7.1,1.65),(7.1,2.4));arrow((11.9,2.95),(12.5,2.95))
ax.text(.1,4,"After repair, remain in V coordinates for the next code record. No global twenty-data CZ measurement is introduced.",fontsize=11)

ax=axes[1];ops=dual_single_fault_pauli_program("Z",4)
ax.set_xlim(-2.2,len(ops)+1);ax.set_ylim(7,-1.4);ax.axis("off")
ax.text(-2.1,-.9,"Expanded conditional ZZZZ check: six CX, two H; data basis is unchanged",fontsize=14,weight="bold")
for q,label in enumerate(("D0","D1","D2","D3","s","f")):
    ax.plot([-.4,len(ops)+.5],[q,q],color="#7a8c9f",lw=.8);ax.text(-.7,q,label,ha="right",va="center")
for x,(op,qs) in enumerate(ops):
    if op=="CX":
        c,t=qs;ax.plot([x,x],[c,t],color="#294c70")
        ax.add_patch(Circle((x,c),.07,color="#294c70",zorder=4))
        ax.add_patch(Circle((x,t),.18,facecolor="white",edgecolor="#294c70",zorder=5))
        ax.plot([x-.12,x+.12],[t,t],color="#294c70",zorder=6);ax.plot([x,x],[t-.12,t+.12],color="#294c70",zorder=6)
    else:
        q=qs[0];label={"PREP":"|0>","MZ":"MZ"}.get(op,op)
        ax.add_patch(Rectangle((x-.32,q-.27),.64,.54,facecolor="#fff1d7" if op=="MZ" else "#e8f0fa",edgecolor="#294c70",zorder=7))
        ax.text(x,q,label,ha="center",va="center",fontsize=10,zorder=8)
        if op=="MZ":ax.text(x,q+.5,"reported syndrome" if q==4 else "reported flag",ha="center",fontsize=9)
ax.text(-2.1,6.5,"Use only after a reported flag spends at least one GLOBAL fault. Any new conditional flag rejects; unknown data are never reset.",fontsize=10)

ax=axes[2];ax.set_xlim(0,20);ax.set_ylim(3.2,0);ax.axis("off")
ax.text(.1,.25,"Physical witness that the cycle record changes acceptance",fontsize=14,weight="bold")
ax.text(.1,1,"One faulty CX(s,A0) applies X_s X_A0. Reported root flags: f4 = f5 = 1 (word 48).",fontsize=11)
ax.text(.1,1.65,"Certified data syndrome = 0; cycle syndrome = 0. Graph-blind decoder: ambiguous. Joint decoder: unique class I.",fontsize=11)
ax.text(.1,2.4,"The code/graph measurements plus the next honest local Gauss certificates recover CZ magic; this flagged root is never a positive vote.",fontsize=10,color="#45652d")
fig.tight_layout(h_pad=1.6)
for ext in ("png","svg"):fig.savefig(out/f"16-graph-assisted-root-recovery.{ext}",dpi=150,bbox_inches="tight",facecolor="white")
plt.close(fig);print(out/"16-graph-assisted-root-recovery.png")
