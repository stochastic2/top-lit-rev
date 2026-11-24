"""Readable figures for the original graph circuit with temporal repetition."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/c4-helix-matplotlib')
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT=Path(__file__).resolve().parent/'figures/c4-helix/repeated-gauging'
OUT.mkdir(parents=True,exist_ok=True)
ink,blue,purple,green,gray='#233444','#2473A6','#7755A4','#26836D','#687784'
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
def canvas(w,h,title,subtitle):
    fig,ax=plt.subplots(figsize=(w,h));ax.set(xlim=(0,w),ylim=(0,h));ax.axis('off')
    fig.subplots_adjust(left=.02,right=.98,bottom=.02,top=.98)
    ax.text(.3,h-.3,title,fontsize=19,weight='bold',color=ink,va='top')
    ax.text(.3,h-.85,subtitle,fontsize=12,color=gray,va='top')
    return fig,ax
def box(ax,x,y,w,h,label,color=blue,size=13):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.04',fc='white',ec=color,lw=1.7))
    ax.text(x,y,label,ha='center',va='center',fontsize=size,color=color)
def arrow(ax,a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.6,'color':gray})
def save(fig,name):
    for ext in ('png','svg'):fig.savefig(OUT/f'{name}.{ext}',dpi=180,facecolor='white')
    plt.close(fig)

fig,ax=canvas(13,9.6,'Repeat the actual gauging and ungauging construction',
              'Each cycle uses the same graph, a fresh resource, and the original twenty enrichment Fredkins.')
labels=[('Original B/C code checks',blue),('Prepare and verify\nfresh 25-qubit graph resource',purple),
        ('Gauge: twenty\ncontrolled-SWAP gates',purple),('Measure vertices in X;\nrequire reported product +1',purple),
        ('Measure gauge edges in Z;\ndecode full record and correct',purple),('Original B/C code checks',blue)]
for j,x in enumerate((2.25,6.5,10.75)):
    ax.text(x,7.96,f'Cycle {j+1}',ha='center',fontsize=17,color=ink,weight='bold')
    for k,(label,color) in enumerate(labels):
        y=7.1-.91*k
        box(ax,x,y,3.8,.70,label,color,12)
        if k<5:arrow(ax,(x,y-.39),(x,y-.51))
for start,channel,end in [(4.20,4.375,4.54),(8.45,8.625,8.79)]:
    ax.plot([start,channel,channel],[2.55,2.55,7.10],color=gray,lw=1.3)
    arrow(ax,(channel,7.10),(end,7.10))
box(ax,6.5,1.13,11.9,.78,'Two more Pauli code scans → physical recovery → decoded logical readout → encoded magic',green,13)
arrow(ax,(10.75,2.13),(10.75,1.58))
ax.text(.4,.35,'The last cycle’s final code scan plus the two extra scans form a three-pass terminal verification.',fontsize=11.5,color=gray)
save(fig,'01-three-cycles')

fig,ax=canvas(13,7.4,'Where the two faults can go',
              'One clean cycle fixes the logical projection. A later clean Pauli pass removes remaining inner-block errors.')
items=[(2.25,5.25,'Before a clean cycle\nerrors on at most\ntwo inner C4 groups',blue),
       (6.5,5.25,'One clean, genuine\ngauging/ungauging cycle\nprepares the target branch',green),
       (10.75,5.25,'Later faulty cycles\ncan again affect at most\ntwo inner C4 groups',blue),
       (10.75,2.55,'Three terminal Pauli passes\ncontain a clean code projection\nthat removes those errors',green),
       (6.5,2.55,'After that clean pass\nonly Pauli-check circuits remain:\nat most two physical errors',blue),
       (2.25,2.55,'Protected ordinary recovery\nand decoded B readout\nhand out encoded magic in C',green)]
for x,y,label,color in items:box(ax,x,y,3.8,1.40,label,color,12)
for a,b in [((4.2,5.25),(4.55,5.25)),((8.45,5.25),(8.8,5.25)),
            ((10.75,4.5),(10.75,3.3)),((8.8,2.55),(8.45,2.55)),((4.55,2.55),(4.2,2.55))]:arrow(ax,a,b)
ax.text(.4,.80,'All phases, wrong reports, and residual errors share one total budget of two faulty locations.',fontsize=12,color=ink)
ax.text(.4,.31,'There is no independent whole-block SWAP measurement, and no coherent-F correction circuit.',fontsize=12,color=gray)
save(fig,'02-proof-flow')
print('Saved two PNG/SVG figure pairs to',OUT)
