"""Readable figures for fault examples, proposed repairs, and distillation."""
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/c4-helix-matplotlib')
from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyBboxPatch,Polygon,Rectangle

ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'output/c4-helix-fault-tolerance-audit.json').read_text())
OUT=ROOT/'notes/figures/c4-helix/fault-tolerance'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
ink,purple,red,blue,green,gray='#233444','#7755A4','#AD3F58','#2473A6','#26836D','#687784'
def canvas(w,h,title,subtitle=''):
    fig,ax=plt.subplots(figsize=(w,h));fig.patch.set_facecolor('white')
    ax.set_xlim(0,w);ax.set_ylim(0,h);ax.axis('off')
    fig.subplots_adjust(left=.025,right=.975,bottom=.025,top=.975)
    ax.text(.25,h-.35,title,fontsize=19,color=ink,weight='bold',va='top')
    if subtitle:ax.text(.25,h-.87,subtitle,fontsize=12,color=gray,va='top')
    return fig,ax
def box(ax,x,y,w,h,label,color=blue,fontsize=14):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.05',fc='white',ec=color,lw=1.8,zorder=3))
    ax.text(x,y,label,ha='center',va='center',fontsize=fontsize,color=color,zorder=4)
def arrow(ax,start,end,color=gray):
    ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':1.8,'color':color})
def node(ax,x,y,label,color=purple):
    ax.add_patch(Circle((x,y),.26,fc=color,ec='white',lw=2,zorder=3))
    ax.text(x,y,label,ha='center',va='center',fontsize=16,color='white',zorder=4)
def save(fig,name):
    for ext in ('png','svg'):fig.savefig(OUT/f'{name}.{ext}',dpi=180,facecolor='white')
    plt.close(fig)

fig,ax=canvas(12,7,'A single vertex phase fault can create an accepted wrong state',
              'A Z fault before enrichment reverses the relation between the reported parity and the actual SWAP sector.')
steps=[(2,5.0,'One fault:\n'+r'$Z_b$',red),(6,5.0,'Reported outcome\n'+r'$r=+1$',purple),
       (10,5.0,'Actual data sector\nSWAP eigenvalue −1',red),
       (10,2.5,'Original code checks\nall pass',blue),
       (6,2.5,'Logical B0 readout\n'+r'$m=+1$',purple),
       (2,2.5,'Accepted C0 output\n'+r'$|1\rangle_L$',red)]
for x,y,label,color in steps:box(ax,x,y,3.2,1.1,label,color)
for start,end in [((3.7,5),(4.3,5)),((7.7,5),(8.3,5)),((10,4.4),(10,3.1)),
                 ((8.3,2.5),(7.7,2.5)),((4.3,2.5),(3.7,2.5))]:arrow(ax,start,end)
ax.text(.35,.65,r'Target: $(2|0\rangle_L+|1\rangle_L)/\sqrt{5}$. Wrong acceptance probability with this fault: $1/8$.',fontsize=14,color=ink)
save(fig,'01-phase-fault')

fig,ax=canvas(12,6.2,'One reused controller can spread a fault to four data pairs',
              'For a bit flip before its enrichment gates, controller b leaves the physical partial SWAP Tb on the data.')
node(ax,.9,3.5,'b')
ax.text(.9,4.25,r'$X_b$',ha='center',fontsize=18,color=red)
ax.plot([.9,.9,10.2],[3.8,4.05,4.05],color=red,lw=2)
for i,q in enumerate([7,9,15,16]):
    x=2.3+2.5*i
    ax.plot([x,x],[4.05,3.85],color=red,lw=2)
    box(ax,x,3.35,1.9,1.0,rf'SWAP($B_{{{q}}},C_{{{q}}}$)',red,13)
ax.text(.4,1.9,r'$T_b=\mathrm{SWAP}_7\mathrm{SWAP}_9\mathrm{SWAP}_{15}\mathrm{SWAP}_{16}$',fontsize=19,color=ink)
ax.text(.4,.78,r'Each SWAP equals $(II+XX+YY+ZZ)/2$: propagate the coherent operator, not one Pauli string.',fontsize=13,color=gray)
save(fig,'02-controller-spread')

fig,ax=canvas(12,7,'The gauge record is a classical error-correcting code',
              'The doubled K5 graph gives a [20,4,8] cut code: 16 ideal records, minimum nonzero cut size 8.')
node(ax,3.2,5.1,'b',red)
for i,(v,labels) in enumerate([('a','7, 15'),('c','8, 19'),('d','14, 16'),('e','4, 9')]):
    x=.8+1.6*i
    ax.plot([3.2,x],[5.1,2.85],color=red,lw=2)
    mx,my=(3.2+x)/2,3.975
    ax.text(mx,my,labels,fontsize=12,ha='center',va='center',color=red,
            bbox={'facecolor':'white','edgecolor':'none','pad':2},zorder=2)
    node(ax,x,2.85,v)
ax.text(.45,1.65,'Flip the reconstructed bit at b:\nall eight incident edge bits change.',fontsize=13,color=gray)
box(ax,9.1,4.75,4.7,1.1,'Use all twenty outcomes\nto choose the nearest valid record',blue,14)
box(ax,9.1,2.95,4.7,1.1,'Correct any three flipped\nreadout bits',green,14)
ax.text(6.8,1.2,'This protects the edge readout.\nIt does not detect vertex phase faults.',fontsize=13,color=gray)
ax.text(.4,.45,'A line labelled with two numbers represents two parallel edges.',fontsize=12,color=gray)
save(fig,'03-cut-code')

fig,ax=canvas(12,7.2,'Decode the whole record; reject ambiguous records',
              'Worked example: the true twenty-bit gauge word is all zero.')
for row,(y,label,ones) in enumerate([(5.05,'True record',set()),(3.85,'One readout flip',{7}),
                                    (2.65,'Decoded record',set())]):
    ax.text(.35,y,label,fontsize=13,color=ink,va='center')
    for q in range(20):
        x=2.5+.44*q
        ax.add_patch(Rectangle((x,y-.20),.36,.40,fc='#FCE8ED' if q in ones else '#EEF3F7',ec='white'))
        ax.text(x+.18,y,str(int(q in ones)),ha='center',va='center',fontsize=12,color=red if q in ones else blue)
        if row==0:ax.text(x+.18,y+.37,str(q),ha='center',fontsize=9,color=gray)
ax.text(.4,1.62,'Nearest-word distance = 1: correct g7 and apply no spurious Tb correction.',fontsize=13,color=green)
ax.text(.4,.98,'Four flips at 4, 7, 8, 9: distance 4 from both zero and the b-cut record.',fontsize=13,color=red)
ax.text(.4,.45,'A tie is a rejection, not a guessed physical correction.',fontsize=13,color=gray)
save(fig,'04-readout-example')

fig,ax=canvas(12,7.4,'Flags can identify erasures, but two flagged controllers can be too much',
              'A known error location is an erasure. The rows show possible affected labels within one C4-Helix block.')
sets=[set([7,9,15,16]),set([3,5,14,17])]
L=set([5,7,14,15,16,17])
for i,(label,S,color) in enumerate([('Flag b',sets[0],purple),('Flag d',sets[1],blue),
                                  ('Union',sets[0]|sets[1],red)]):
    y=5.15-i*1.1
    ax.text(.4,y,label,fontsize=14,color=color,va='center')
    for q in range(20):
        x=2.0+.47*q
        ax.add_patch(Rectangle((x,y-.23),.40,.46,fc=color if q in S else '#EEF2F5',
                              ec=ink if i==2 and q in L else 'white',lw=2 if i==2 and q in L else 1))
        ax.text(x+.20,y,str(q),ha='center',va='center',fontsize=10,color='white' if q in S else gray)
ax.text(.4,1.85,'Black outlines: labels 5, 7, 14, 15, 16, 17 support an undetectable logical operator.',fontsize=12,color=ink)
ax.text(.4,1.07,'One correctly flagged controller set is recoverable. The b+d union is not a correctable erasure set.',fontsize=12,color=gray)
ax.text(.4,.45,'The note derives a two-fault example that passes perfect code checks and yields an accepted stabilizer state.',fontsize=12,color=red)
save(fig,'05-erasure-locations')

fig,ax=canvas(13,7.0,'Protect Pauli parity measurements with a verified cat state',
              'Example: logical Z0 is the product of data Z at labels 0, 3, 6, 7, 18, 19. Each cat qubit meets one data qubit.')
qs=[0,3,6,7,18,19]
ax.text(.35,4.65,'Verified cat',fontsize=13,color=purple,va='center')
ax.text(.35,2.45,'Block-B data',fontsize=13,color=blue,va='center')
ax.plot([2.7,11.8],[4.65,4.65],color=purple,lw=1.2)
for i,q in enumerate(qs):
    x=2.9+1.7*i
    node(ax,x,4.65,rf'$c_{i}$')
    ax.plot([x,x],[4.38,2.95],color=gray,lw=1.4)
    ax.text(x,3.63,'CZ',fontsize=12,ha='center',color=ink,bbox={'facecolor':'white','edgecolor':'none','pad':2})
    box(ax,x,2.45,1.15,.88,rf'$B_{{{q}}}$',blue,17)
    ax.text(x,5.38,'Measure X',ha='center',fontsize=11,color=purple)
ax.text(.4,1.17,r'Cat state: $(|0\rangle^{\otimes6}+|1\rangle^{\otimes6})/\sqrt{2}$. Product of X outcomes measures the logical parity.',fontsize=13,color=ink)
ax.text(.4,.47,'Verification, fresh repetitions and data error correction are part of the gadget, not optional extras.',fontsize=12,color=gray)
save(fig,'06-protected-parity')

fig,ax=canvas(12,7.0,'A larger graph can give each physical SWAP its own controller',
              'Drawn below: only the neighbourhood of controller p7. Every other physical label has its own analogous controller.')
node(ax,5.15,3.8,r'$p_7$')
for i,(hub,y) in enumerate([(1,5.6),(5,3.8),(6,2.0)]):
    node(ax,1.35,y,rf'$h_{{{hub}}}$')
    ax.plot([1.65,4.85],[y,3.8],color=gray,lw=1.5)
    ax.text(3.1,(y+3.8)/2,rf'$A_{{{hub},7}}$',ha='center',fontsize=14,color=red,
            bbox={'facecolor':'white','edgecolor':'none','pad':2})
arrow(ax,(5.5,3.8),(6.35,3.8),purple)
box(ax,8.8,3.8,4.65,1.15,r'One controlled SWAP: $(B_7,C_7)$',blue,16)
ax.text(6.52,5.45,'Full graph: 30 temporary vertices\n60 gauge qubits · 20 Fredkin gates',fontsize=14,color=ink)
ax.text(.4,.98,'Short dressing paths remain. Controller reuse falls from four SWAPs to one.',fontsize=13,color=gray)
ax.text(.4,.43,'Its classical cut-code distance is 3, rather than 8. More vertices do not solve the phase-outcome problem.',fontsize=12,color=gray)
save(fig,'07-split-controllers')

fig,ax=canvas(12,7.1,'A fault-tolerant architecture can use the gauging circuit as a raw source',
              'Logical errors in raw magic states are removed by distillation, not by ordinary C4-Helix syndrome correction.')
steps=[(2,5.0,'1. Gauging + ungauging\nproduces raw encoded M',purple),
       (6,5.0,'2. Protected code recovery\nand logical parity readout',blue),
       (10,5.0,'3. Logical Hadamard twirl\nsets a known magic direction',blue),
       (10,2.6,'4. Independent accepted copies\nenter a distillation batch',gray),
       (6,2.6,'5. Protected Clifford circuit\nand logical Pauli checks',blue),
       (2,2.6,'6. Retain a purified\nencoded H-type magic state',green)]
for x,y,label,color in steps:box(ax,x,y,3.25,1.1,label,color,13)
for start,end in [((3.7,5),(4.3,5)),((7.7,5),(8.3,5)),((10,4.4),(10,3.2)),
                 ((8.3,2.6),(7.7,2.6)),((4.3,2.6),(3.7,2.6))]:arrow(ax,start,end)
ax.text(.35,.63,'Required: sufficiently good raw outputs and a fault-tolerant logical Clifford/measurement layer.',fontsize=13,color=ink)
save(fig,'08-factory')

fig,ax=canvas(12,7.5,'A Clifford twirl places the raw state in the Hadamard magic direction',
              'Randomly apply I or logical H with probability 1/2. The average Bloch vector is (0.7, 0, 0.7).')
cx,cz,R=3.1,3.55,2.15
ax.add_patch(Circle((cx,cz),R,fc='#F8FAFC',ec='#CAD4DD',lw=1.5))
ax.add_patch(Polygon([(cx+R,cz),(cx,cz+R),(cx-R,cz),(cx,cz-R)],fc='#E8EDF2',ec='#B6C2CD',lw=1.2))
ax.plot([cx-R,cx+R],[cz,cz],color=gray,lw=1)
ax.plot([cx,cx],[cz-R,cz+R],color=gray,lw=1)
for x,z,label,color in [(.8,.6,'M',purple),(.6,.8,'HM',blue),(.7,.7,'',green)]:
    px,pz=cx+R*x,cz+R*z
    ax.plot(px,pz,'o',color=color,ms=8)
    if label:ax.text(px+(.16 if label=='M' else -.33),pz+(.04 if label=='M' else .18),label,fontsize=13,color=color)
ax.plot([cx+R*.8,cx+R*.6],[cz+R*.6,cz+R*.8],color=green,lw=2)
ax.text(6.7,5.03,'Ideal raw output:',fontsize=13,color=gray)
ax.text(6.7,4.42,r'$\rho_M:\ (x,z)=(4/5,3/5)$',fontsize=17,color=purple)
ax.text(6.7,3.61,r'$H\rho_MH:\ (x,z)=(3/5,4/5)$',fontsize=17,color=blue)
ax.text(6.7,2.80,r'$\rho_{\rm twirl}:\ (x,z)=(7/10,7/10)$',fontsize=17,color=green)
ax.text(6.7,1.82,r'$\epsilon_H=(1-0.7\sqrt{2})/2\approx0.00503$',fontsize=17,color=ink)
ax.text(.4,.61,'Shaded diamond: mixtures of Pauli eigenstates in the X–Z plane. The twirled state lies outside it.',fontsize=12,color=gray)
save(fig,'09-twirl')

fig,ax=plt.subplots(figsize=(11,6))
fig.patch.set_facecolor('white');fig.subplots_adjust(left=.12,right=.95,bottom=.19,top=.78)
errors=[float(DATA['twirled_ideal_magic']['H_error'])]+[float(d['error']) for d in DATA['BK15_ideal_independent_inputs']]
ax.semilogy(range(3),errors,'o-',color=green,lw=2,ms=8)
ax.set_xticks(range(3),['Twirled raw output','One 15-to-1 round','Two 15-to-1 rounds'],fontsize=12)
ax.set_ylim(1e-16,1e-1);ax.set_yticks([1e-2,1e-6,1e-10,1e-14]);ax.grid(axis='y',alpha=.25)
ax.set_xlim(-.35,2.35)
ax.set_ylabel('H-type state error',fontsize=13)
for i,(error,label) in enumerate(zip(errors,['5.03 × 10⁻³','4.51 × 10⁻⁶','3.21 × 10⁻¹⁵'])):
    ax.annotate(label,(i,error),xytext=(0,12),textcoords='offset points',ha='center',fontsize=13,color=ink)
fig.text(.055,.94,'What ideal magic-state distillation can suppress',fontsize=20,color=ink,weight='bold')
fig.text(.055,.86,'Independent identical inputs and perfect logical Clifford circuits; these are not physical-device predictions.',fontsize=12,color=gray)
fig.text(.12,.065,'Noise in the protected distillation circuit sets an additional floor that must be included in a device analysis.',fontsize=12,color=gray)
save(fig,'10-distillation')
print('Saved ten PNG/SVG figure pairs to',OUT)
