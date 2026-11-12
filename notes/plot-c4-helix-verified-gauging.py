"""Figures for verification of gauging and coherent ungauging."""
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/c4-helix-matplotlib')
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyBboxPatch,Rectangle

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'notes/figures/c4-helix/verified-gauging'
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
def box(ax,x,y,w,h,label,color=blue,size=14):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.05',fc='white',ec=color,lw=1.8,zorder=3))
    ax.text(x,y,label,ha='center',va='center',fontsize=size,color=color,zorder=4)
def arrow(ax,start,end,color=gray):
    ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':1.8,'color':color})
def save(fig,name):
    for ext in ('png','svg'):fig.savefig(OUT/f'{name}.{ext}',dpi=180,facecolor='white')
    plt.close(fig)

fig,ax=canvas(12,7,'Keep the graph, but align each controller with one inner C4 block',
              'Only the data-controller assignment changes. The graph still has five vertices and twenty gauge edges.')
for y,label,selected,color in [(4.85,'Old controller b',{7,9,15,16},red),
                               (3.15,'New controller b',{4,5,6,7},green)]:
    ax.text(.35,y,label,fontsize=13,color=color,va='center')
    for q in range(20):
        x=2.75+.43*q
        ax.add_patch(Rectangle((x,y-.25),.36,.50,fc=color if q in selected else '#EDF2F5',ec='white'))
        ax.text(x+.18,y,str(q),ha='center',va='center',fontsize=10,color='white' if q in selected else gray)
        if q%4==0:
            ax.text(x+.82,y+.55,f'inner block {q//4}',ha='center',fontsize=11,color=gray)
ax.text(.4,1.69,'New assignments: a → 0–3; b → 4–7; c → 8–11; d → 12–15; e → 16–19.',fontsize=14,color=ink)
ax.text(.4,.94,'Any two complete inner blocks are correctable erasure locations for C4-Helix.',fontsize=13,color=green)
ax.text(.4,.42,'Perfect code postselection of the new TbTd gives I/16, not the logical filter found for the old assignment.',fontsize=12,color=gray)
save(fig,'01-alignment')

fig,ax=canvas(12,7.3,'Undo the gauge-dependent data frame coherently',
              'Gauge qubits act as quantum controls. They are not measured while these sixteen Fredkin gates are applied.')
for i,(g,v,lo,hi) in enumerate([(7,'b',4,7),(11,'c',8,11),(3,'d',12,15),(0,'e',16,19)]):
    y=5.4-1.08*i
    box(ax,1.15,y,1.05,.66,rf'$A_{{{g}}}$',red,17)
    arrow(ax,(1.8,y),(2.45,y),red)
    box(ax,6.65,y,8.0,.72,rf'Control the four SWAPs $(B_q,C_q)$ for $q={lo},\ldots,{hi}$',blue,15)
ax.text(.4,.68,'The root a needs no frame gate. Four gauge controls × four data-pair SWAPs = sixteen Fredkins.',fontsize=12,color=gray)
save(fig,'02-coherent-frame')

fig,ax=canvas(13,8.0,'The same gauged constraints become simpler in the new frame',
              'Conjugate by F. Measuring the right-hand constraints implements the corresponding gauged verification.')
rows=[(5.98,r'$G_v$ for $v=b,c,d,e$',r'$X_{\mathrm{star}(v)}^A$',purple),
      (4.60,r'$G_a$',r'$X_{\mathrm{star}(a)}^A U$',purple),
      (3.22,r'$L_\eta=Z_\eta^A$',r'$L_\eta=Z_\eta^A$',red),
      (1.84,'Dressed matter-pair projectors','Original B/C code projector',blue)]
for y,left,right,color in rows:
    box(ax,3.2,y,5.1,.90,left,color,17 if y!=1.84 else 14)
    box(ax,9.8,y,5.1,.90,right,color,17 if y!=1.84 else 14)
    arrow(ax,(5.86,y),(7.14,y),gray)
ax.text(.4,.48,'The vertex and flux identities are exact operators. The matter identity uses the zero-flux sector.',fontsize=12,color=gray)
save(fig,'03-constraint-dictionary')

fig,ax=canvas(12,6.7,'Verify a cat state without measuring its logical branch',
              r'Check every adjacent ZZ parity with a fresh $|0\rangle$ verifier; repeat three complete parity scans.')
ys=[4.85,3.65,2.45]
for y,label,color in zip(ys,[r'$c_j$',r'$c_{j+1}$',r'$w:\ |0\rangle$'],[purple,purple,blue]):
    ax.text(.45,y,label,fontsize=17,color=color,va='center')
    ax.plot([2.3,8.2],[y,y],color=gray,lw=1.3)
for x,y in [(3.6,4.85),(5.65,3.65)]:
    ax.plot([x,x],[y,2.45],color=ink,lw=1.5)
    ax.plot(x,y,'o',color=ink,ms=7)
    ax.add_patch(Circle((x,2.45),.14,fc='white',ec=ink,lw=1.6))
    ax.plot([x-.14,x+.14],[2.45,2.45],color=ink,lw=1.2)
    ax.plot([x,x],[2.31,2.59],color=ink,lw=1.2)
box(ax,7.55,2.45,1.15,.65,'Measure Z',blue,12)
ax.text(9.0,4.8,'Keep only\nparity +1',fontsize=16,color=green,va='top')
ax.text(9.0,3.25,'One faulty check\ncan add at most\none cat bit flip.',fontsize=13,color=gray,va='top')
ax.text(.4,1.36,'A clean complete scan projects onto the repetition-code space. Later faults leave at most two bit flips.',fontsize=12,color=gray)
ax.text(.4,.60,'ZZ checks do not protect the cat phase; fresh full verification sweeps handle erroneous parity reports.',fontsize=12,color=gray)
save(fig,'04-cat-verification')

fig,ax=canvas(12,7.0,'Measure the whole-block SWAP with one fresh cat leaf per data pair',
              'Use twenty cat qubits. Each one controls exactly one Fredkin gate, then is measured in X.')
for x,q in [(2.7,0),(4.8,1),(8.2,18),(10.3,19)]:
    box(ax,x,4.85,1.15,.65,rf'$c_{{{q}}}$',purple,16)
    ax.text(x,5.53,'Measure X',ha='center',fontsize=11,color=purple)
    ax.plot([x,x],[4.48,3.68],color=gray,lw=1.5)
    box(ax,x,3.1,1.95,1.0,rf'SWAP$(B_{{{q}}},C_{{{q}}})$',blue,12)
ax.text(6.5,4.85,'⋯',ha='center',va='center',fontsize=28,color=gray)
ax.text(6.5,3.1,'⋯',ha='center',va='center',fontsize=28,color=gray)
ax.text(.4,1.90,r'$|\mathrm{cat}_{20}\rangle=(|0\rangle^{\otimes20}+|1\rangle^{\otimes20})/\sqrt{2}$',fontsize=19,color=ink)
ax.text(.4,1.17,r'Product of X outcomes: the measurement of $U=\prod_q\mathrm{SWAP}(B_q,C_q)$.',fontsize=14,color=ink)
ax.text(.4,.48,'This verifier uses additional Fredkin resources. It is powerful enough to prepare the magic state on its own.',fontsize=12,color=gray)
save(fig,'05-swap-verifier')

fig,ax=canvas(13,8.0,'Three complete verification sweeps, accepting only the expected signs',
              'Each sweep uses fresh verified measurement ancillas. With at most two faults, at least one full sweep is clean.')
steps=[(1.8,'Gauge Pauli\nchecks: 20',red),(5.0,'Original B/C\nchecks: 40',blue),
       (8.2,'Whole-block\nSWAP: U = +1',purple),(11.4,'Original B/C\nchecks: 40',blue)]
for x,label,color in steps:box(ax,x,5.68,2.65,1.0,label,color,14)
for x in (3.2,6.4,9.6):arrow(ax,(x-.03,5.68),(x+.43,5.68))
ax.text(.4,4.50,'Repeat the entire sweep three times:',fontsize=15,color=ink)
for x,label,color in [(2.35,'Sweep 1\npossible fault',red),(6.5,'Sweep 2\nclean in this example',green),
                      (10.65,'Sweep 3\npossible fault',red)]:
    box(ax,x,3.2,3.4,1.1,label,color,15)
arrow(ax,(4.12,3.2),(4.75,3.2));arrow(ax,(8.27,3.2),(8.90,3.2))
ax.text(.4,1.76,'A clean code–SWAP–code sweep fixes the logical magic branch. Later faults remain ordinary correctable errors.',fontsize=12,color=gray)
ax.text(.4,.92,'Reject on any unexpected sign. Do not correct a suspicious record blindly back into the accepted sector.',fontsize=12,color=gray)
ax.text(.4,.42,'This is a heralded verification scheme; noise can reduce yield without causing an accepted logical failure.',fontsize=12,color=gray)
save(fig,'06-sweeps')

fig,ax=canvas(12,6.6,'Why one U test between distant endpoint checks is insufficient',
              'Two faults can leave no final code syndrome while erasing the intended projection.')
for x,label,color in [(2.0,'Code check\npasses',blue),(6.0,'Measure U\nrecord +1',purple),(10.0,'Code check\npasses',blue)]:
    box(ax,x,4.3,2.9,1.0,label,color,15)
arrow(ax,(3.52,4.3),(4.48,4.3));arrow(ax,(7.52,4.3),(8.48,4.3))
ax.text(4.0,5.05,r'$Z^B_q$',ha='center',fontsize=21,color=red)
ax.text(8.0,5.05,r'$Z^C_q$',ha='center',fontsize=21,color=red)
ax.text(6.0,2.65,r'$\mathcal{P}_{\mathrm{code}} Z^C_q\Pi_+ Z^B_q\mathcal{P}_{\mathrm{code}}=\frac{1}{2} U\mathcal{P}_{\mathrm{code}}$',ha='center',fontsize=22,color=ink)
ax.text(.4,1.35,'The surviving operation is U/2, not the projector (I + U)/2.',fontsize=14,color=red)
ax.text(.4,.55,'A complete clean sweep contains its own code checks immediately before and after the fresh U test.',fontsize=12,color=gray)
save(fig,'07-endpoint-counterexample')

fig,ax=canvas(12,7.2,'The proposed handoff from gauging to ordinary recovery',
              'Coherent ungauging keeps the gauge register available until all verification sweeps have completed.')
steps=[(2,5.2,'1. Prepare and verify\nthe cluster resource',purple),
       (6,5.2,'2. Gauge with the\nblock-aligned controllers',purple),
       (10,5.2,'3. Apply coherent frame F\nand gauge sign corrections',red),
       (10,2.8,'4. Three complete\nverification sweeps',blue),
       (6,2.8,'5. Discard gauge register;\nprotected ordinary recovery',blue),
       (2,2.8,'6. Protected logical readout\nextracts encoded M',green)]
for x,y,label,color in steps:box(ax,x,y,3.25,1.1,label,color,13)
for start,end in [((3.7,5.2),(4.3,5.2)),((7.7,5.2),(8.3,5.2)),((10,4.6),(10,3.4)),
                 ((8.3,2.8),(7.7,2.8)),((4.3,2.8),(3.7,2.8))]:arrow(ax,start,end)
ax.text(.35,.74,'96 Fredkin gates per ideal attempt, excluding ancilla preparation; all checks add substantial Clifford overhead.',fontsize=12,color=gray)
ax.text(.35,.30,'The fault-free single-qubit magic yield remains 5/8. A native hardware audit is still needed.',fontsize=12,color=gray)
save(fig,'08-handoff')
print('Saved eight PNG/SVG figure pairs to',OUT)
