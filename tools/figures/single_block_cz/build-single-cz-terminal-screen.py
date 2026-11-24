"""Render the ordered terminal schedule, actual inner gadget and feedback."""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from single_cz_terminal_screen import screen_checks
from single_cz_flagged import flagged_program

out=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"svg.fonttype":"none"})
fig,axes=plt.subplots(3,1,figsize=(17,12),gridspec_kw={"height_ratios":[1.15,3,1.8]})

ax=axes[0]
ax.set_xlim(-1,18)
ax.set_ylim(2,-1.5)
ax.axis("off")
ax.text(-.9,-1,"Ordered terminal screen: 268 CNOTs on the clean path",fontsize=17,weight="bold")
ax.text(-.9,-.35,"Each box is an existing flagged stabilizer primitive. All eighteen syndrome bits and every flag must report zero.",fontsize=10)
colors=["#dceaf9"]*4+["#dceaf9"]*4+["#e5f1df"]*5+["#e5f1df"]*5
ax.plot([-.6,17.6],[.6,.6],color="#536579")
for x,((axis,j),color) in enumerate(zip(screen_checks(),colors)):
    ax.add_patch(Rectangle((x-.35,.25),.7,.7,facecolor=color,edgecolor="#244466",zorder=2))
    ax.text(x,.6,f"{axis}{j}",ha="center",va="center")
for x,label in ((1.5,"Outer Z"),(5.5,"Outer X"),(10,"Inner Z"),(15,"Inner X")):
    ax.text(x,1.5,label,ha="center",weight="bold")

ax=axes[1]
ops=flagged_program(("X",)*4)
ax.set_xlim(-2.5,len(ops)+1)
ax.set_ylim(7,-1.4)
ax.axis("off")
ax.text(-2.4,-.9,"Expanded XXXX on R0: late inner checks catch errors missed by earlier outer meters",fontsize=14,weight="bold")
for q,label in enumerate(("D0","D1","D2","D3","s","f")):
    ax.plot([-.4,len(ops)+.5],[q,q],color="#63748a",lw=.8)
    ax.text(-.7,q,label,ha="right",va="center")
for x,(op,qs) in enumerate(ops):
    if op=="CX":
        c,t=qs
        ax.plot([x,x],[c,t],color="#244466",lw=1)
        ax.add_patch(Circle((x,c),.07,color="#244466",zorder=5))
        ax.add_patch(Circle((x,t),.18,facecolor="white",edgecolor="#244466",zorder=6))
        ax.plot([x-.12,x+.12],[t,t],color="#244466",zorder=7)
        ax.plot([x,x],[t-.12,t+.12],color="#244466",zorder=7)
    else:
        q=qs[0]
        ax.add_patch(Rectangle((x-.32,q-.27),.64,.54,facecolor="#fff0d5" if op=="MZ" else "#eaf2fc",edgecolor="#244466",zorder=8))
        ax.text(x,q,{"PREP":"|0>","MZ":"MZ"}.get(op,op),ha="center",va="center",fontsize=10,zorder=9)
        if op=="MZ":
            ax.text(x,q+.48,"reported b" if q==4 else "reported f",ha="center",color="#995014",fontsize=10)
            ax.add_patch(Rectangle((x+.34,q-.07),len(ops)+.16-x,.14,color="white",zorder=5))
            for d in (-.035,.035):ax.plot([x+.34,len(ops)+.5],[q+d,q+d],color="#63748a",lw=.8,zorder=6)
ax.text(5.5,6.4,"Six CNOTs. H(s) then MZ(s) is an X readout. Neither the data nor a logical X is measured destructively.",ha="center",fontsize=10)

ax=axes[2]
ax.set_xlim(0,16)
ax.set_ylim(4,0)
ax.axis("off")
def box(x,y,w,h,text,color="#fff5e5"):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor="#8f521d"))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=10)
def arrow(a,b,label=None):
    ax.annotate("",xy=b,xytext=a,arrowprops={"arrowstyle":"->","color":"#8f521d"})
    if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2-.12,label,ha="center",fontsize=9)
box(.1,.3,3.3,1,"All first-screen reports zero\nRetain; correctable E2 span", "#e5f1df")
box(4,.3,4.9,1,"Data flag: flag-conditioned Pauli repair\nNonzero syndrome: original full recovery")
box(9.6,.3,3.2,1,"Fresh ordered screen\nZero: retain", "#e5f1df")
box(9.6,2.1,5.9,1.1,"Certified full history\nUnique-class repair or reject")
arrow((8.9,.8),(9.6,.8),"flag")
arrow((6.4,1.3),(9.6,2.65),"syndrome")
arrow((11.2,1.3),(11.2,2.1),"nonzero")
ax.text(.1,3.65,"No data reset, no extra CZ measurement, and one global two-fault budget across every branch.",fontsize=11)
fig.tight_layout(h_pad=1.4)
for ext in ("svg","png"):
    fig.savefig(out/f"13-ordered-terminal-screen.{ext}",dpi=150,bbox_inches="tight",facecolor="white")
plt.close(fig)
print(out/"13-ordered-terminal-screen.png")
