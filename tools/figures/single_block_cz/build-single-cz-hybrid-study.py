"""Editable circuit drawing for the hybrid design audit; no noisy simulation."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"src/single_block_cz"))
from single_cz_hybrid_study import ccz
OUT=ROOT/"notes/figures/c4-helix/single-block-cz"

def setup(ax,n,labels,width):
    ax.set_xlim(-1.1,width);ax.set_ylim(-.7,n-.3);ax.invert_yaxis();ax.axis("off")
    for j,label in enumerate(labels):
        ax.plot([-.1,width-.3],[j,j],color="#9aabb9",lw=1)
        ax.text(-.25,j,label,ha="right",va="center",fontsize=12)

def gate(ax,x,y,text):
    ax.add_patch(Rectangle((x-.24,y-.22),.48,.44,color="#eaf1fa",ec="#31577c",zorder=3))
    ax.text(x,y,text,ha="center",va="center",fontsize=10,zorder=4)

def cx(ax,x,a,b):
    ax.plot([x,x],[a,b],color="#31577c",lw=1.5)
    ax.add_patch(Circle((x,a),.055,color="#31577c",zorder=3))
    ax.add_patch(Circle((x,b),.12,fc="white",ec="#31577c",lw=1.5,zorder=3))
    ax.plot([x-.12,x+.12],[b,b],color="#31577c",zorder=4)
    ax.plot([x,x],[b-.12,b+.12],color="#31577c",zorder=4)

fig=plt.figure(figsize=(16,11))
gs=fig.add_gridspec(3,1,height_ratios=(1.4,1.1,1.2),hspace=.48)
ax=fig.add_subplot(gs[0]);setup(ax,4,["meter s","tree edge e","data i","data j"],9)
cx(ax,.7,2,3);cx(ax,1.7,0,2);gate(ax,2.7,3,"X*")
ax.plot([4,4],[0,3],color="#31577c",lw=1.5)
for y in [0,1,3]:ax.add_patch(Circle((4,y),.07,color="#31577c",zorder=3))
ax.text(4,-.43,"CCZ macro",ha="center",fontsize=11)
gate(ax,5.3,3,"X*");cx(ax,6.8,2,3)
ax.set_title("Direct block factor: X_i X_j C_e[(-1)^h Z_i Z_j] controlled by meter s",loc="left",fontsize=15,pad=18)
ax.text(.1,3.6,"Both X* gates are present iff h=1. Three CX outside the macro; nine CX and seven T/T† total. Flags bracket block ports.",fontsize=11)
ax=fig.add_subplot(gs[1]);setup(ax,3,["a","b","c"],14)
for j,(op,qs) in enumerate(ccz("a","b","c")):
    x=.6+j*.95
    if op=="CX":cx(ax,x,"abc".index(qs[0]),"abc".index(qs[1]))
    else:gate(ax,x,"abc".index(qs[0]),"T" if op=="T" else "T†")
ax.set_title("Exact elementary CCZ expansion: six CX and seven T/T† (no atomic three-qubit location)",loc="left",fontsize=15,pad=16)
ax=fig.add_subplot(gs[2]);ax.axis("off")
table=ax.table(cellText=[["Shared V + compact record","220","64","60"],
                         ["Direct outer checks, one CCZ per CZ factor","330","182","48"],
                         ["Parity-compressed outer checks","278","91","48"],
                         ["Shared parity basis and absorbed signs","255","91","48"],
                         ["Best outer basis in this compiler family","248","84","48"]],
               colLabels=["Data-check subcircuit only; nonroot Gauss excluded","CX","T/T†","PREP and MZ (each)"],
               colWidths=[.56,.12,.12,.20],loc="center")
table.auto_set_font_size(False);table.set_fontsize(11);table.scale(1,1.5)
fig.suptitle("Hybrid gauged-check design study: ideal circuits verified; new factory fault tolerance is NOT established",fontsize=16,y=.995)
fig.subplots_adjust(left=.08,right=.98,top=.92,bottom=.04)
OUT.mkdir(parents=True,exist_ok=True)
for ext in ("svg","png"):fig.savefig(OUT/f"17-hybrid-check-study.{ext}",dpi=150)
print(OUT/"17-hybrid-check-study.png")
