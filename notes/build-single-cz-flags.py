"""Render actual flagged verification programs as editable SVG and PNG.

/Users/kevinhemery/pytket-venv/bin/python -B notes/build-single-cz-flags.py
"""
import os
os.environ.setdefault("MPLCONFIGDIR","/private/tmp/c4-cz-mpl")
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from single_cz_flagged import flagged_program

OUT=Path(__file__).resolve().parent/"figures/c4-helix/single-block-cz"
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"svg.fonttype":"none"})


def draw(axes,targets,title,name,feedback=False):
    n=len(axes);ops=flagged_program(axes)
    compact=n==4 and len(set(axes))==1 and axes[0] in ("X","Z")
    labels=list(targets)+["s (syndrome)"]+[f"f{j} (reused flag)" for j in range(1 if compact else 3)]
    columns=len(ops)+4
    fig,ax=plt.subplots(figsize=(max(13,.42*columns+3),.52*len(labels)+2.3))
    ax.set_xlim(-5,columns);ax.set_ylim(len(labels)+1.1,-2.4);ax.axis("off")
    for j,label in enumerate(labels):
        ax.plot([-.5,columns-.5],[j,j],color="#536171",lw=.75)
        ax.text(-.8,j,label,ha="right",va="center")
    ax.text(-4.8,-1.8,title,fontsize=14,weight="bold")
    ax.text(-4.8,-1.05,"Exact serial program. A fresh |0> resets each reused flag; no separately verified cat.",fontsize=10)
    def box(x,q,text,color="#e9f0fa"):
        ax.add_patch(Rectangle((x-.38,q-.29),.76,.58,facecolor=color,edgecolor="#304761",zorder=100))
        ax.text(x,q,text,ha="center",va="center",fontsize=8,zorder=101)
    def segment(x,q,classical):
        z=10+x*.01
        ax.add_patch(Rectangle((x+.4,q-.09),columns-x-.9,.18,facecolor="white",edgecolor="none",zorder=z))
        for delta in ((-.035,.035) if classical else (0,)):
            ax.plot([x+.4,columns-.5],[q+delta,q+delta],color="#536171",lw=.65,zorder=z+.001)
    def slot(q):return q if q<=n else n+1+(q-n-1)%3
    flag=0;readout=None
    for x,(op,qs) in enumerate(ops):
        wires=[slot(q) for q in qs]
        if op=="CX":
            c,t=wires
            ax.plot([x,x],[c,t],color="#26394e",lw=.9,zorder=90)
            ax.add_patch(Circle((x,c),.065,facecolor="#26394e",zorder=100))
            ax.add_patch(Circle((x,t),.16,facecolor="white",edgecolor="#26394e",zorder=100))
            ax.plot([x-.11,x+.11],[t,t],color="#26394e",zorder=101)
            ax.plot([x,x],[t-.11,t+.11],color="#26394e",zorder=101)
        elif op=="PREP":
            box(x,wires[0],"|0>","#e7f5ea");segment(x,wires[0],False)
        elif op=="MZ":
            box(x,wires[0],"MZ","#fff0dc");segment(x,wires[0],True)
            label="b" if qs[0]==n else f"r{flag}"
            if qs[0]!=n:flag+=1
            else:readout=(x,wires[0])
            ax.text(x,wires[0]+.45,label,fontsize=8,color="#a24317",ha="center")
        else:box(x,wires[0],op)
    if feedback:
        x=columns-2;box(x,0,"Z^b","#fff0dc")
        ax.annotate("",xy=(x,0.35),xytext=(readout[0]+.4,readout[1]),
                    arrowprops={"arrowstyle":"->","linestyle":"--","color":"#a24317"})
    ax.text((columns-5)/2,len(labels)+.4,
            "Any reported flag rj=1: reject this magic-data attempt. Otherwise use b in the controller.",
            ha="center",fontsize=10,color="#a24317")
    fig.tight_layout()
    for ext in ("png","svg"):fig.savefig(OUT/f"{name}.{ext}",dpi=160,bbox_inches="tight",facecolor="white")
    plt.close(fig)


draw(["X"]*5,["A0","A4","A5","A6","A10"],
     "Compact13 nonroot X star: rolling flags and root-tree Z feedback","09-rolling-star",True)
draw(["X"]*4,[f"D{j}" for j in range(4)],
     "Terminal XXXX: one syndrome ancilla and one flag (six CNOTs)","10-flagged-terminal")
print(f"Wrote flagged circuits to {OUT}")
