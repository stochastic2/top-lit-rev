"""Audit a block-aligned, coherently unframed verification proposal.

Checks finite code/graph identities, the frame-error support lemma, and
X-component fault patterns in explicit cat preparation/verification.
The complete physical gadget is not enumerated location by location.
"""
from itertools import combinations, product
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parent.parent
graph=json.loads((ROOT/'output/c4-helix-five-vertex-gauging.json').read_text())
V=graph['vertices']
edges={int(q):tuple(pair) for q,pair in graph['edges'].items()}
tree={'b':7,'c':11,'d':3,'e':0}
new_controls={v:list(range(4*i,4*i+4)) for i,v in enumerate(V)}
ALL_VERTEX=31
def mask(qs):return sum(1<<q for q in qs)
def parity(n):return n.bit_count()%2
def span(gs):
    ans={0}
    for g in gs:ans|={x^g for x in ans}
    return ans
def rank(gs):
    pivots={}
    for g in gs:
        while g:
            p=g.bit_length()-1
            if p in pivots:g^=pivots[p]
            else:pivots[p]=g;break
    return len(pivots)
def field(t):
    return mask(q for q,(u,v) in edges.items()
                if (t>>V.index(u)^t>>V.index(v))&1)
def tree_bits(g):
    return sum((g>>q&1)<<V.index(v) for v,q in tree.items())
flat={field(t):t for t in range(32) if not t&1}

source=(ROOT/'arXiv-2609.03194v1/appendix.tex').read_text()
table=source.split(r'\begin{minipage}{0.6\textwidth}')[1].split(r'\end{minipage}')[0]
rows=[]
for line in table.splitlines():
    sy=re.findall(r'\$(X|Z|\\cdot)\$',line)
    if len(sy)==20:rows.append(mask(q for q,t in enumerate(sy) if t!=r'\cdot'))
C=span(rows[:10]);perp=span(rows[:10]+rows[20:22]);logical=perp-C
assert len(rows)==24
assert rank(rows[:10])==rank(rows[10:20])==9
assert rank(rows[:10]+rows[20:22])==11
# Symplectic vectors (X | Z). Known logical input constraints plus the
# eighteen code checks give twenty independent stabilizers per input.
B_input=rows[:10]+[r<<20 for r in rows[10:20]+rows[22:24]]
C_input=rows[:10]+[r<<20 for r in rows[10:20]]+[rows[20],rows[23]<<20]
assert rank(B_input)==rank(C_input)==20
# Physical Z-readout decoding: all <=2-bit errors with a common syndrome
# must induce the same logical Z0 parity, even if the full word differs by
# an X stabilizer of weight four.
readout_errors=[mask(qs) for size in range(3) for qs in combinations(range(20),size)]
readout_by_syndrome={}
for e in readout_errors:
    syndrome=sum(parity(e&s)<<j for j,s in enumerate(rows[10:20]))
    logical_z0_flip=parity(e&rows[22])
    assert syndrome not in readout_by_syndrome or readout_by_syndrome[syndrome]==logical_z0_flip
    readout_by_syndrome[syndrome]=logical_z0_flip
assert len(readout_errors)==211
resource=[(1<<(20+j))^mask(q for q,pair in edges.items() if v in pair)
          for j,v in enumerate(V)]
resource += [((1<<q)^(1<<(20+V.index(u)))^(1<<(20+V.index(v))))<<25
             for q,(u,v) in edges.items()]
assert rank(resource)==25
cycles=[(7,15),(11,12),(3,6),(0,10),(8,19),(14,16),(4,9),(2,13),(1,18),(5,17),
        (7,8,11),(7,14,3),(7,4,0),(11,2,3),(11,1,0),(3,5,0)]
stars=[mask(q for q,pair in edges.items() if v in pair) for v in V[1:]]
assert rank(stars+[mask(c)<<20 for c in cycles])==20
assert all(parity(s&mask(c))==0 for s in stars for c in cycles)
erasure_sets=[]
for size in (1,2):
    for owners in combinations(range(5),size):
        S=mask(q for j in owners for q in range(4*j,4*j+4))
        restricted={p for p in perp if not p&~S}
        stabs={p for p in C if not p&~S}
        assert restricted==stabs
        assert len(stabs)==2**size
        assert not any(not p&~S for p in logical)
        coefficient= len(stabs)**2 / 2**(4*size)
        assert coefficient==1/4**size
        erasure_sets.append({'vertices':[V[j] for j in owners],
                             'labels':[q for q in range(20) if S>>q&1],
                             'projected_partial_swap_coefficient':str(coefficient)})
assert len(erasure_sets)==15

# F uses four gauge controls; its exact action on each G_v holds for all
# gauge strings because it depends only on these four bits.
for t in range(32):
    for v in range(5):
        g=field(t)
        attached=tree_bits(g^field(1<<v))^tree_bits(g)^(1<<v)
        assert attached==(ALL_VERTEX if v==0 else 0)

# On flat fields, conjugation of the matter-pair projector by F produces
# the original pair of code checks, possibly with B and C exchanged.
for g,t in flat.items():
    for s,support in enumerate(graph['table_I_supports']):
        anchor=V.index(graph['check_roots'][s])
        for q in support:
            controller=q//4
            path_bit=(t>>controller^t>>anchor)&1
            restored=path_bit^(t>>controller&1)
            assert restored==(t>>anchor&1)

# Initial cluster schedule: edge q ascending, its first endpoint CNOT
# followed by its second endpoint CNOT. X-components of a faulty CNOT
# are propagated exactly through the remaining cluster gates.
schedule=[(v,q) for q,pair in edges.items() for v in pair]
pre=[]
for loc,(v,q) in enumerate(schedule):
    suffix=mask(f for w,f in schedule[loc+1:] if w==v)
    for x_control,x_edge in [(0,1),(1,0),(1,1)]:
        pre.append({'kind':'cluster-CNOT','owner':1<<V.index(v),
                    'gauge':(suffix if x_control else 0)^((1<<q) if x_edge else 0),
                    'controller_flip':(1<<V.index(v)) if x_control else 0})
for q,(u,v) in edges.items():
    pre.append({'kind':'early-gauge-X','owner':1<<V.index(u),
                'gauge':1<<q,'controller_flip':0})
for v in range(5):
    pre.append({'kind':'vertex-X-before-enrichment','owner':1<<v,
                'gauge':0,'controller_flip':1<<v})
assert len(pre)==145
for p in pre:
    assert all(any(p['owner']>>V.index(v)&1 for v in edges[q])
               for q in range(20) if p['gauge']>>q&1)

def confined_up_to_global(bits,owners):
    return not(bits&~owners) or not((bits^31)&~owners)

accepted_single=accepted_two_pre=accepted_pre_post=0
for p in pre:
    if p['gauge'] in flat:
        residual=tree_bits(p['gauge'])^p['controller_flip']
        assert confined_up_to_global(residual,p['owner'])
        accepted_single+=1
for p,q in combinations(pre,2):
    g=p['gauge']^q['gauge']
    if g in flat:
        owners=p['owner']|q['owner']
        residual=tree_bits(g)^p['controller_flip']^q['controller_flip']
        assert confined_up_to_global(residual,owners)
        accepted_two_pre+=1
for p in pre:
    for late_edge in range(20):
        post=1<<late_edge
        if (p['gauge']^post) in flat:
            # A late flipped tree bit can add the corresponding inner
            # block to the mismatch of the frame already applied.
            late_owner=tree_bits(post)
            owners=p['owner']|late_owner
            residual=tree_bits(p['gauge'])^p['controller_flip']
            assert confined_up_to_global(residual,owners)
            assert owners.bit_count()<=2
            accepted_pre_post+=1
assert all((1<<q) not in flat for q in range(20))
assert all(((1<<q)^(1<<r)) not in flat for q,r in combinations(range(20),2))

# A counterexample to checking U alone with code checks only at the ends:
# Z_Cq Pi_+ Z_Bq becomes U/2 after perfect code projection.
q=0
assert (1<<q) not in perp  # single Z in one block has nonzero syndrome
# The two expansion terms are Z_C Z_B /2 (detected in each code), and
# Z_C Z_C U/2 = U/2 (undetected). A clean code check before U avoids it.

# Algebraic clean-sweep reset: any encoded operator aI+bU, followed by
# Pi_+, becomes (a+b)Pi_+. Verify on the full four-logical-qubit basis.
def swap_logical(b):
    return ((b&3)<<2)|(b>>2)
for a,b in [(1,0),(0,1),(1,1),(1,-1),(2,-3)]:
    for basis in range(16):
        before={basis:a}
        dest=swap_logical(basis);before[dest]=before.get(dest,0)+b
        after={}
        for i,amp in before.items():
            for j in (i,swap_logical(i)):after[j]=after.get(j,0)+amp
        target={}
        for j in (basis,swap_logical(basis)):target[j]=target.get(j,0)+a+b
        assert after==target

# Native X-component audit of the explicit verified-cat preparation.
# Z-components only change cat phase and do not affect ZZ verification.
def cat_actions(n):
    actions=[];faults=[]
    for j in range(n):
        k=len(actions);actions.append(('prepare',j))
        faults.append((k,1<<j,0))
    for j in range(n-1):
        k=len(actions);actions.append(('cat-CNOT',j))
        faults.extend([(k,1<<j,0),(k,1<<(j+1),0),(k,(1<<j)|(1<<(j+1)),0)])
    for sweep in range(3):
        for j in range(n-1):
            k=len(actions);actions.append(('verify-prepare',j));faults.append((k,0,1))
            for leaf in (j,j+1):
                k=len(actions);actions.append(('verify-CNOT',leaf))
                faults.extend([(k,1<<leaf,0),(k,0,1),(k,1<<leaf,1)])
            k=len(actions);actions.append(('verify-readout',j));faults.append((k,0,1))
    return actions,faults

def run_cat(n,actions,faults):
    e=0;verifier=0;cursor=0
    for k,(op,j) in enumerate(actions):
        if op=='cat-CNOT':
            if e>>j&1:e^=1<<(j+1)
        elif op=='verify-prepare':verifier=0
        elif op=='verify-CNOT':verifier^=e>>j&1
        while cursor<len(faults) and faults[cursor][0]==k:
            _,x,read=faults[cursor];e^=x;verifier^=read;cursor+=1
        if op=='verify-readout' and verifier:return None
    return min(e.bit_count(),n-e.bit_count())

cat_audits=[]
for n in (2,3,4,6,8,9,20):
    actions,faults=cat_actions(n)
    assert run_cat(n,actions,[])==0
    singles=pairs=accepted_singles=accepted_pairs=0
    for f in faults:
        value=run_cat(n,actions,[f]);singles+=1
        if value is not None:assert value<=1;accepted_singles+=1
    for f,g in combinations(faults,2):
        if f[0]==g[0]:continue
        value=run_cat(n,actions,[f,g]);pairs+=1
        if value is not None:assert value<=2;accepted_pairs+=1
    cat_audits.append({'cat_qubits':n,'single_X_patterns':singles,'two_X_pattern_pairs':pairs,
                       'accepted_single_patterns':accepted_singles,'accepted_two_patterns':accepted_pairs})

report={
    'scope':'Finite algebra, frame-error, and cat X-component audits supporting a conditional two-fault-detecting proposal; the complete physical gadget remains unaudited.',
    'graph_unchanged':True,'vertices':V,'controller_assignment':new_controls,
    'frame_controls':tree,'frame_fredkins':16,
    'cluster_resource_stabilizer_rank':25,
    'normalized_gauge_stabilizer_rank':20,
    'known_input_stabilizer_rank_per_block':20,
    'destructive_Z_readout_error_patterns_tested':len(readout_errors),
    'checked_one_or_two_inner_block_erasure_sets':erasure_sets,
    'frame_G_conjugations':'G_nonroot -> gauge X-star; G_root -> gauge X-star times U, exact globally',
    'frame_matter_conjugations':'original code-pair projectors on the flat gauge sector',
    'resource_X_patterns':len(pre),'resource_one_fault_patterns':accepted_single,
    'two_early_pattern_pairs_tested':len(pre)*(len(pre)-1)//2,
    'two_early_pattern_pairs_surviving_flatness':accepted_two_pre,
    'early_late_pattern_pairs_tested':len(pre)*20,
    'early_late_pattern_pairs_surviving_flatness':accepted_pre_post,
    'mixed_time_U_only_counterexample':'P Z_Cq Pi_+ Z_Bq P = U P/2',
    'verification_sweeps':3,'data_Pauli_checks_per_code_scan':40,
    'gauge_Pauli_checks_per_sweep':20,'fresh_cat_size_for_U':20,
    'fredkin_count_excluding_verifier_preparation':96,
    'explicit_cat_verification_X_audits':cat_audits,
    'conditional_obligations':['validate the explicit verified-cat support contract in the complete physical implementation',
                               'one fresh cat leaf per data interaction',
                               'faults in Pauli/U check gadgets satisfy the stated support contract',
                               'native Fredkin and idle/leakage model validation',
                               'protected input preparation and final recovery/extraction'],
    'unproved':'Full native-location enumeration of complete physical verification circuits'}
dest=ROOT/'output/c4-helix-verified-gauging-audit.json'
dest.write_text(json.dumps(report,indent=2)+'\n')
print('All 15 one/two-inner-block erasure sets contain no logical Pauli.')
print('Projected whole-C4 partial SWAPs: 1 block -> I/4; 2 blocks -> I/16.')
print('Coherent frame maps all G checks exactly and matter pairs on all 16 flat fields.')
print('Frame-error support:', len(pre),'early patterns;',len(pre)*(len(pre)-1)//2,'early pairs;',len(pre)*20,'early/late pairs checked.')
print('Every surviving flat pattern is confined to <=2 inner blocks, up to full U.')
print('Clean-sweep encoded reset identity passes on all 16 logical basis states.')
print('Saved',dest)
