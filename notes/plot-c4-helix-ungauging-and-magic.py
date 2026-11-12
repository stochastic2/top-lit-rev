"""Draw the ideal ungauging and encoded magic-state preparation steps."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/c4-helix-matplotlib')
from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'output/c4-helix-ungauging-and-magic.json').read_text())
OUT = ROOT / 'notes/figures/c4-helix/ungauging-and-magic'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans', 'svg.fonttype':'none'})
ink, purple, red, blue, green, gray = '#233444', '#7755A4', '#AD3F58', '#2473A6', '#26836D', '#687784'

def canvas(w,h,title,subtitle=''):
    fig,ax=plt.subplots(figsize=(w,h))
    fig.patch.set_facecolor('white')
    ax.set_xlim(0,w);ax.set_ylim(0,h);ax.axis('off')
    fig.subplots_adjust(left=.025,right=.975,bottom=.025,top=.975)
    ax.text(.25,h-.35,title,fontsize=19,color=ink,weight='bold',va='top')
    if subtitle:ax.text(.25,h-.85,subtitle,fontsize=12,color=gray,va='top')
    return fig,ax

def arrow(ax,start,end,color=gray):
    ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':1.8,'color':color})

def box(ax,x,y,w,h,label,color=blue,fontsize=13):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.06',fc='white',ec=color,lw=1.8,zorder=4))
    ax.text(x,y,label,ha='center',va='center',fontsize=fontsize,color=color,zorder=5)

def node(ax,x,y,label,color=purple):
    ax.add_patch(Circle((x,y),.27,fc=color,ec='white',lw=2,zorder=4))
    ax.text(x,y,label,ha='center',va='center',fontsize=16,color='white',zorder=5)

def save(fig,name):
    for ext in ('png','svg'):fig.savefig(OUT/f'{name}.{ext}',dpi=180,facecolor='white')
    plt.close(fig)

# 1. The direct route starts with exactly the state established in note 1.
fig,ax=canvas(12,7,'From the gauged state back to the original code blocks',
              'The direct ideal route uses measured gauge bits to choose ordinary physical SWAP corrections.')
steps=[(2,5.0,'1. Gauged state\n40 data + 20 gauge qubits',purple),
       (6,5.0,'2. Measure all gauge qubits\nin the Z basis',red),
       (10,5.0,'3. Solve the edge parities\nfor five vertex bits',gray),
       (10,2.6,'4. Undo the selected\nphysical data SWAPs',blue),
       (6,2.6,'5. Original code blocks\nwith SWAP outcome r',blue),
       (2,2.6,'6. Retain the magic branch\nand extract one logical qubit',green)]
for x,y,label,color in steps:box(ax,x,y,3.25,1.10,label,color)
for start,end in [((3.70,5),(4.30,5)),((7.70,5),(8.30,5)),((10,4.4),(10,3.2)),
                  ((8.30,2.6),(7.70,2.6)),((4.30,2.6),(3.70,2.6))]:arrow(ax,start,end)
ax.text(.35,.65,r'Final data operation: $\Pi_r=(I+rU)/2$, with $r=x_ax_bx_cx_dx_e$.',fontsize=16,color=ink)
save(fig,'01-workflow')

# 2. Rooting at a makes the classical decoding entirely transparent.
fig,ax=canvas(12,7.2,'Decode the gauge record with a four-edge tree',
              'Example: the record gives t = (0, 1, 0, 1, 0), in vertex order a, b, c, d, e.')
node(ax,3.2,4.95,'a')
ax.text(3.2,5.55,r'$t_a=0$',ha='center',fontsize=15,color=purple)
for i,(v,q,t) in enumerate([('b',7,1),('c',11,0),('d',3,1),('e',0,0)]):
    x=.8+1.6*i
    ax.plot([3.2,x],[4.95,2.85],color=red if t else '#9CACB8',lw=2,zorder=1)
    mx,my=(3.2+x)/2,(4.95+2.85)/2
    ax.text(mx,my,rf'$g_{{{q}}}={t}$',fontsize=14,ha='center',va='center',color=red if t else gray,
            bbox={'facecolor':'white','edgecolor':'none','pad':2},zorder=3)
    node(ax,x,2.85,v,red if t else purple)
    ax.text(x,2.23,rf'$t_{v}={t}$',ha='center',fontsize=15,color=ink)
ax.text(.5,1.25,'Red vertices select the data correction:',fontsize=13,color=gray)
ax.text(.5,.63,r'$V_{t_0}=T_bT_d$',fontsize=19,color=blue)
box(ax,9.05,4.35,4.8,1.35,'b controls SWAP labels\n7, 9, 15, 16',blue,14)
box(ax,9.05,2.55,4.8,1.35,'d controls SWAP labels\n3, 5, 14, 17',blue,14)
ax.text(6.72,.90,'Validate the other sixteen edges\nusing their endpoint parities.',fontsize=13,color=gray)
save(fig,'02-decode')

# 3. One affected factor suffices to illustrate restoration of the code.
fig,ax=canvas(12,6.4,'Why the data correction restores the original checks',
              'For t = (0, 1, 0, 1, 0), the first inner check is partly in block C before correction.')
box(ax,3.0,4.08,4.9,1.3,r'$D^X_{B,0}=X^B_0X^B_1X^B_2X^C_3$',purple,19)
box(ax,9.0,4.08,4.9,1.3,r'$S^X_{B,0}=X^B_0X^B_1X^B_2X^B_3$',blue,19)
arrow(ax,(5.55,4.08),(6.45,4.08),blue)
ax.text(6,3.0,r'Apply $\mathrm{SWAP}(B_3,C_3)$',ha='center',fontsize=16,color=blue)
box(ax,3.0,1.85,4.9,1.3,r'$D^Z_{B,0}=Z^B_0Z^B_1Z^B_2Z^C_3$',purple,19)
box(ax,9.0,1.85,4.9,1.3,r'$S^Z_{B,0}=Z^B_0Z^B_1Z^B_2Z^B_3$',blue,19)
arrow(ax,(5.55,1.85),(6.45,1.85),blue)
ax.text(.4,.47,'The full correction also exchanges the other seven selected data pairs.',fontsize=12,color=gray)
save(fig,'03-check-restoration')

# 4. The spectators make a joint two-pair SWAP into an effective one-pair measurement.
fig,ax=canvas(12,6.7,'Choose encoded inputs that make the SWAP measurement useful',
              'All four boxes below are logical qubits. Each row occupies one twenty-qubit C4-Helix block.')
ax.text(.55,4.55,'Block B',fontsize=16,color=blue,va='center')
ax.text(.55,2.0,'Block C',fontsize=16,color=blue,va='center')
box(ax,4.2,4.55,2.2,.95,r'$B_0:\ |0\rangle_L$',blue,18)
box(ax,4.2,2.0,2.2,.95,r'$C_0:\ |+\rangle_L$',blue,18)
box(ax,9.1,4.55,2.2,.95,r'$B_1:\ |0\rangle_L$',gray,18)
box(ax,9.1,2.0,2.2,.95,r'$C_1:\ |0\rangle_L$',gray,18)
ax.annotate('',xy=(4.2,3.95),xytext=(4.2,2.6),arrowprops={'arrowstyle':'<->','lw':2,'color':purple})
ax.annotate('',xy=(9.1,3.95),xytext=(9.1,2.6),arrowprops={'arrowstyle':'<->','lw':2,'color':gray})
ax.text(4.2,3.28,'Active SWAP pair',ha='center',fontsize=13,color=purple,
        bbox={'facecolor':'white','edgecolor':'none','pad':3})
ax.text(9.1,3.28,'Identical spectators',ha='center',fontsize=13,color=gray,
        bbox={'facecolor':'white','edgecolor':'none','pad':3})
ax.text(.4,.62,r'On this input, $U=\mathrm{SWAP}(B_0,C_0)\mathrm{SWAP}(B_1,C_1)$ acts only on the active pair.',fontsize=14,color=ink)
save(fig,'04-logical-input')

# 5. Signed amplitude plots distinguish applying SWAP from measuring SWAP.
fig,axs=plt.subplots(1,3,figsize=(13,5.1))
fig.patch.set_facecolor('white')
fig.subplots_adjust(left=.06,right=.975,bottom=.20,top=.69,wspace=.30)
fig.text(.035,.94,'The two logical SWAP measurement branches',fontsize=20,weight='bold',color=ink)
fig.text(.035,.855,r'Basis labels refer to the active logical pair (B0, C0). Spectator qubits remain in $|0\rangle$.',fontsize=12,color=gray)
vectors=[[1/math.sqrt(2),1/math.sqrt(2),0,0],
         [2/math.sqrt(6),1/math.sqrt(6),1/math.sqrt(6),0],
         [0,1/math.sqrt(2),-1/math.sqrt(2),0]]
titles=[r'Input: $|0+\rangle_L$',r'$r=+1$: probability $3/4$',r'$r=-1$: probability $1/4$']
labels=[[r'$1/\sqrt{2}$',r'$1/\sqrt{2}$','',''],
        [r'$2/\sqrt{6}$',r'$1/\sqrt{6}$',r'$1/\sqrt{6}$',''],
        ['',r'$1/\sqrt{2}$',r'$-1/\sqrt{2}$','']]
for ax,vec,title,lab in zip(axs,vectors,titles,labels):
    ax.bar(range(4),vec,color=[blue if a>=0 else red for a in vec],width=.58)
    ax.axhline(0,color=gray,lw=1)
    ax.set_ylim(-1,1);ax.set_xticks(range(4),['00','01','10','11'],fontsize=12)
    ax.set_yticks([-1,0,1]);ax.tick_params(axis='y',labelsize=10)
    ax.set_title(title,fontsize=13,color=ink,pad=16)
    ax.spines[['top','right']].set_visible(False)
    for i,(a,label) in enumerate(zip(vec,lab)):
        if label:ax.text(i,a+(.06 if a>0 else -.08),label,ha='center',va='bottom' if a>0 else 'top',fontsize=13,color=ink)
axs[0].set_ylabel('Real amplitude',fontsize=12,color=gray)
fig.text(.06,.055,'The positive branch is magic. The negative branch is a logical singlet, which is a stabilizer state.',fontsize=12,color=gray)
save(fig,'05-amplitudes')

# 6. A readable branch diagram with unconditional probabilities in the final boxes.
fig,ax=canvas(13,8.6,'Heralding a single encoded magic qubit',
              'First keep the positive SWAP outcome; then measure the logical Z of B0.')
box(ax,2.0,4.85,3.0,1.15,'Input\n'+r'$|0\rangle_{B_0}|+\rangle_{C_0}$',blue,16)
box(ax,6.15,6.5,3.5,1.15,r'$r=+1$: keep'+'\nProbability 3/4',green,15)
box(ax,6.15,2.3,3.5,1.15,r'$r=-1$: restart'+'\nProbability 1/4',gray,15)
arrow(ax,(3.6,5.1),(4.35,6.25),green)
arrow(ax,(3.6,4.6),(4.35,2.6),gray)
box(ax,10.75,6.5,3.3,1.35,r'$Z^L_{B_0}=+1$'+'\n'+r'$|M\rangle_L=(2|0\rangle_L+|1\rangle_L)/\sqrt{5}$',green,12)
box(ax,10.75,3.9,3.3,1.20,r'$Z^L_{B_0}=-1$'+'\nRestart: output is a stabilizer state',gray,12)
arrow(ax,(7.98,6.5),(8.99,6.5),green)
arrow(ax,(7.95,6.0),(9.05,4.45),gray)
ax.text(8.45,7.11,'5/6',ha='center',fontsize=15,color=green)
ax.text(8.73,5.20,'1/6',ha='center',fontsize=15,color=gray)
ax.text(10.75,5.37,'Total success probability: 5/8',ha='center',fontsize=13,color=green,weight='bold')
ax.text(10.75,2.87,'Total probability: 1/8',ha='center',fontsize=13,color=gray)
ax.text(.45,1.03,'Probabilities on the right-hand arrows are conditional on r = +1.',fontsize=12,color=gray)
ax.text(.45,.49,'Failure is known from the measurement records. A fresh trial starts from the stabilizer inputs.',fontsize=12,color=gray)
save(fig,'06-heralding')

# 7. A Bloch slice proves non-stabilizerness without appealing to a named magic family.
fig,ax=canvas(11,7.4,'Why the extracted qubit is magic',
              'Pure one-qubit stabilizer states are the six Pauli eigenstates. The output lies at a different point.')
centre=(3.1,3.45); radius=2.05
ax.add_patch(Circle(centre,radius,fc='#F8FAFC',ec='#CAD4DD',lw=1.8))
ax.plot([3.1-radius,3.1+radius],[3.45,3.45],color=gray,lw=1.2)
ax.plot([3.1,3.1],[3.45-radius,3.45+radius],color=gray,lw=1.2)
for dx,dz,label in [(1,0,'+X'),(-1,0,'−X'),(0,1,'+Z'),(0,-1,'−Z')]:
    x,y=3.1+radius*dx,3.45+radius*dz
    ax.plot(x,y,'o',color=gray,ms=7)
    ax.text(x+.24*dx,y+.26*dz,label,ha='center',va='center',fontsize=13,color=gray,
            bbox={'facecolor':'white','edgecolor':'none','pad':1.5})
target=(3.1+radius*.8,3.45+radius*.6)
arrow(ax,centre,target,green);ax.plot(*target,'o',color=green,ms=9)
ax.text(target[0]+.18,target[1]+.25,'M',fontsize=16,color=green,weight='bold')
ax.text(6.25,4.98,r'$|M\rangle_L=\frac{2|0\rangle_L+|1\rangle_L}{\sqrt{5}}$',fontsize=21,color=green)
ax.text(6.25,3.68,r'$\langle X_L\rangle=4/5$',fontsize=19,color=ink)
ax.text(6.25,2.95,r'$\langle Y_L\rangle=0$',fontsize=19,color=ink)
ax.text(6.25,2.22,r'$\langle Z_L\rangle=3/5$',fontsize=19,color=ink)
ax.text(.4,.47,'X–Z plane of the logical Bloch sphere. The ±Y Pauli eigenstates lie outside this plane.',fontsize=12,color=gray)
save(fig,'07-bloch')

# 8. The literal paper route, distinguished from the shorter direct route.
fig,ax=canvas(12,7.0,'The paper route retains the five measured vertices',
              'This route has the same logical projector. It undoes the cluster circuit and then the enrichment circuit.')
steps=[(2,5.0,'1. Keep / reprepare vertices\nin their recorded X states',purple),
       (6,5.0,'2. Undo cluster circuit\n40 inverse CNOTs',red),
       (10,5.0,'3. Measure gauge qubits\nin Z',red),
       (10,2.6,'4. Solve the edge parities\nfor the offset t0',gray),
       (6,2.6,'5. Apply X on vertices\nwhose offset bit is 1',purple),
       (2,2.6,'6. Undo enrichment\n20 inverse Fredkin gates',blue)]
for x,y,label,color in steps:box(ax,x,y,3.25,1.10,label,color)
for start,end in [((3.70,5),(4.30,5)),((7.70,5),(8.30,5)),((10,4.4),(10,3.2)),
                  ((8.30,2.6),(7.70,2.6)),((4.30,2.6),(3.70,2.6))]:arrow(ax,start,end)
ax.text(.35,.65,r'Final state: $|+\rangle^{\otimes5}_{\rm vertices}\otimes |g\rangle_A\otimes \Pi_r|\psi\rangle_{BC}$, up to normalization.',fontsize=14,color=ink)
save(fig,'08-paper-route')
print('Saved eight PNG/SVG pairs to',OUT)
