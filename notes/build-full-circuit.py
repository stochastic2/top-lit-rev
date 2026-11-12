"""Generate the quantikz source and Markdown companion; compile separately.

Run with python3 -B notes/build-full-circuit.py. Add --render in a Python
environment with Pillow and pdfplumber to compile and export the diagrams.
The circuit data come from the source-backed decoder used by full_procedure.md.
"""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE / 'full-circuit-latex'
FIGURES = HERE / 'figures/c4-helix/full-circuit'
spec = importlib.util.spec_from_file_location('decoder', HERE / 'c4_helix_intrinsic_decoder.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
VERTICES = 'abcde'
R = [tuple(q for q in range(20) if row >> q & 1) for row in d.H]
R.append(tuple(q for q in range(20) if 4 in d.EDGE_ENDPOINTS[q]))
colors = dict(a='groupa', b='groupb', c='groupc', d='groupd', e='groupe')
pages = []


def label(name, color=None):
    return (r'\color{' + color + '}' if color else '') + name


def grid(labels, columns, outputs=None, classical=(), row='.28cm', col='.26cm'):
    """Each dict is a gate column; unspecified entries continue their wire."""
    outputs = outputs or {}
    classical = set(classical)
    rows = []
    for i, name in enumerate(labels):
        is_classical = i in classical
        cells = [r'\lstick{$' + name + '$}']
        for column in columns:
            default = r'\cw' if is_classical else r'\qw'
            cell = column.get(i, default)
            cells.append(cell)
            if r'\meter' in cell:
                is_classical = True
            if r'\gate{\lvert0\rangle}' in cell:
                is_classical = False
        last = r'\cw' if is_classical else r'\qw'
        if i in outputs:
            last = r'\rstick{$' + outputs[i] + '$}' + last
        cells.append(last)
        rows.append(' & '.join(cells))
    return (r'\begin{quantikz}[row sep={' + row + r',between origins},column sep=' + col + ']\n'
            + ' \\\\\n'.join(rows) + '\n' + r'\end{quantikz}')


def reset(rows):
    return {i: r'\gate{\lvert0\rangle}' for i in rows}


def cnot(a, b):
    return {a: r'\ctrl{' + str(b-a) + '}', b: r'\targ{}'}


def cz(a, b):
    return {a: r'\ctrl{' + str(b-a) + '}', b: r'\control{}'}


def fredkin(c, a, b):
    return {c: r'\ctrl{' + str(a-c) + '}',
            a: r'\swap{' + str(b-a) + '}', b: r'\targX{}'}


def display(circuit, width=r'\linewidth'):
    # adjustbox max width scales only when necessary, preserving readable sizes.
    return '\n' + r'\begin{center}\begin{adjustbox}{max width=' + width + '}\n' + circuit + '\n' + r'\end{adjustbox}\end{center}' + '\n'


def pair(left, right, captions=('', '')):
    return (r'\par\noindent\begin{minipage}[t]{.485\linewidth}\centering\textbf{' + captions[0] + '}\n'
            + display(left) + r'\end{minipage}\hfill\begin{minipage}[t]{.485\linewidth}\centering\textbf{'
            + captions[1] + '}\n' + display(right) + r'\end{minipage}\par' + '\n')


def ports(port_list, P='X'):
    """Interleaved leaf/target ports from ONE joint cat; no cat re-preparation."""
    labels, cols, outputs = [], [], {}
    for j, target, color in port_list:
        labels += [label(r'\ell_{' + str(j) + '}', 'cat'), label(target, color)]
    for i, (j, _, _) in enumerate(port_list):
        cols.append((cnot if P == 'X' else cz)(2*i, 2*i+1))
    cols += [{2*i: r'\gate{H}' for i in range(len(port_list))},
             {2*i: r'\meter{}' for i in range(len(port_list))}]
    for i, (j, _, _) in enumerate(port_list):
        outputs[2*i] = r'\lambda_{' + str(j) + '}'
    return grid(labels, cols, outputs, row='.46cm', col='.22cm')


def swap_ports(port_list):
    labels, cols, outputs = [], [], {}
    for j, q, color in port_list:
        labels += [label(r'\ell_{' + str(j) + '}', 'cat'),
                   label('B_{' + str(q) + '}', color), label('C_{' + str(q) + '}', color)]
    for i in range(len(port_list)):
        cols.append(fredkin(3*i, 3*i+1, 3*i+2))
    cols += [{3*i: r'\gate{H}' for i in range(len(port_list))},
             {3*i: r'\meter{}' for i in range(len(port_list))}]
    for i, (j, _, _) in enumerate(port_list):
        outputs[3*i] = r'\lambda_{' + str(j) + '}'
    return grid(labels, cols, outputs, row='.46cm', col='.24cm')


def page(slug, title, body, md):
    pages.append(dict(slug=slug, title=title, body=body, md=md))


# 1. Shared helper preparation and reset/measurement legend.
cat_labels = [label(r'\ell_' + str(j), 'cat') for j in range(4)]
rawcat = grid(cat_labels,
              [reset(range(4)), {0:r'\gate{H}'}, cnot(0,1), cnot(1,2), cnot(2,3)],
              row='.65cm', col='.55cm')
verify = grid([label(r'\ell_j','cat'), label(r'\ell_{j+1}','cat'), label('w','cat')],
              [reset([2]), cnot(0,2), cnot(1,2), {2:r'\meter{}'}],
              {2:r'\nu_j^{(k)}'}, row='.6cm', col='.6cm')
page('01-helpers', 'Shared gadget: reset, cat preparation, and verification',
     r'''\small
Read every circuit left to right. A box $|0\rangle$ means reset, discarding
the previous state; it is not a projection with postselection. A meter
measures $Z$. The sequence $H$ then meter measures $X$.
Single wires are quantum; double wires carry classical bits.
\[
\mathcal R_0(\rho)=|0\rangle\langle0|\,\operatorname{Tr}\rho,
\qquad b=0\ \Longleftrightarrow\ \hbox{reported sign }+1.
\]
\subhead{Prepare a raw cat: the four-leaf example}
''' + display(rawcat) + r'''
For $m$ leaves, extend the chain through $\ell_{m-1}$:
$H_{\ell_0}$ followed by CNOTs $\ell_j\to\ell_{j+1}$, $j=0,\ldots,m-2$.
\subhead{One adjacent-$ZZ$ verification, with its own reset}
''' + display(verify) + r'''
\[
\text{For }k=1,2,3:\quad j=0,1,\ldots,m-2;\qquad
\text{require every }\nu_j^{(k)}=0.
\]
Reset $w$ before every pair. After verification, apply no further
leaf-to-leaf gates. Couple each leaf to one target port only, then measure
all leaves in $X$. The check bit is $y=\bigoplus_j\lambda_j$.
For a positive check require $y=0$, not every $\lambda_j=0$.
''',
     'Every later check starts with this fresh-cat circuit. Reset the parity helper before each adjacent pair; perform three complete verification scans. Reject any nonzero raw verification bit.')

# 2. Known sources, with four-body examples for X and Z.
srcreset = grid([label('B_q','groupa'), label('C_q','groupa')], [reset([0,1])],
                {0:r'q=0,\ldots,19',1:r'q=0,\ldots,19'}, row='.6cm', col='.6cm')
four = [(j, 'D_'+str(j), 'groupa') for j in range(4)]
page('02-inputs', '1. Prepare the encoded B and C inputs',
     display(srcreset) + r'''
The drawing represents an independent reset of every physical data qubit.
For each check below, prepare one fresh verified cat as on page 1.
The leaves in each panel are one joint cat, not independent plus states.
''' + pair(ports(four,'X'),ports(four,'Z'),('$X_{D_0}X_{D_1}X_{D_2}X_{D_3}$', '$Z_{D_0}Z_{D_1}Z_{D_2}Z_{D_3}$')) + r'''
\subhead{Full target lists and repetitions}
For $s=0,\ldots,8$, replace $(0,1,2,3)$ by the ordered support $R_s$
from page 13. An upper check has eight leaves. Logical checks have six.
\[
\begin{aligned}
\mathcal F_B={}&(S^X_{B,0:8},\ S^Z_{B,0:8},\ \overline Z^B_0,\overline Z^B_1),\\
\mathcal F_C={}&(S^X_{C,0:8},\ S^Z_{C,0:8},\ \overline X^C_0,\overline Z^C_1).
\end{aligned}
\]
The notation $0{:}8$ means all nine checks in increasing $s$ order.
Execute three complete positive rounds on B, then three on C.
Require all check bits zero, in addition to all cat-verification bits.
\[
|\psi\rangle=|\overline{00}\rangle_B|\overline{+0}\rangle_C.
\]
''',
     'Reset the 40 data qubits. Run the X/Z check circuits on the support lists, including the logical input checks: three positive rounds per block, B before C. The two panels are alternatives for the type of check being measured.')

# 3. All graph preparation gates are determined by the endpoint dictionary.
graph = grid([label('a','groupa'),label('c','groupc'),label('e','groupe'),label('A_0','gauge'),label('A_1','gauge')],
             [reset(range(5)),{0:r'\gate{H}',1:r'\gate{H}',2:r'\gate{H}'},
              cnot(0,3),cnot(2,3),cnot(1,4),cnot(2,4)], row='.65cm',col='.43cm')
k1=ports([(0,'c','groupc'),(1,'A_1','gauge'),(2,'e','groupe')],'Z')
edge_rows=[]
for u in range(5):
    for v in range(u+1,5):
        qs=[q for q, uv in d.EDGE_ENDPOINTS.items() if uv==(u,v)]
        edge_rows.append(VERTICES[u]+VERTICES[v]+' & '+','.join(map(str,qs))+r' \\')
page('03-resource', '2. Prepare the graph resource and verify its edge checks',
     r'''Reset $a,b,c,d,e$ and $A_0,\ldots,A_{19}$ to zero. Apply $H$
to each vertex. For every edge $q:u_q-v_q$, apply
CNOT$(u_q\to A_q)$ then CNOT$(v_q\to A_q)$, in increasing $q$.
\subhead{The gates for edges 0 and 1 (other edges continue the same wires)}
''' + display(graph) + r'''
\begin{center}\begin{tabular}{cc@{\qquad}cc}
Endpoints & Labels & Endpoints & Labels\\\hline
ab&7,15&bc&8,19\\ ac&11,12&bd&14,16\\
ad&3,6&be&4,9\\ ae&0,10&cd&2,13\\ ce&1,18&de&5,17
\end{tabular}\end{center}
\subhead{One edge-check measurement: $K_1=Z_cZ_{A_1}Z_e$}
''' + display(k1) + r'''
One three-leaf verified cat is shared by these three ports.
Set $y=\lambda_0\oplus\lambda_1\oplus\lambda_2$ and require zero.
For edge $q:u-v$, use targets $(u,A_q,v)$.
The vertex checks on the next page complete resource verification.
''',
     'Prepare all five vertices in plus and all twenty gauge qubits in zero. Apply the forty incidence CNOTs using the endpoint dictionary. Edge checks use a three-leaf cat and CZs.')

# 4. Explicit nine-port vertex resource check.
ea=R[5]
k_a=[(0,'a','groupa')]+[(j+1,'A_{'+str(q)+'}','gauge') for j,q in enumerate(ea)]
page('04-resource-check', '2 continued. Verify a resource vertex check',
     r'''
\[
K_a=X_aX_{A_0}X_{A_3}X_{A_6}X_{A_7}
X_{A_{10}}X_{A_{11}}X_{A_{12}}X_{A_{15}}.
\]
Prepare \textbf{one nine-leaf cat}. The two panels show its first five
and last four target ports. They do not prepare or measure two separate cats.
''' + pair(ports(k_a[:5]),ports(k_a[5:]),('Leaves 0--4','Leaves 5--8')) + r'''
\[
y(K_a)=\lambda_0\oplus\cdots\oplus\lambda_8;\qquad \text{require }y(K_a)=0.
\]
Use the same circuit for each vertex v, replacing a by v and
$E_a=R_5$ by $E_v$:
\[
K_v=X_v\prod_{q\in E_v}X_{A_q},\qquad
(E_a,E_b,E_c,E_d,E_e)=(R_5,R_6,R_7,R_8,R_9).
\]
\subhead{The complete resource-verification schedule}
Measure $(K_a,K_b,K_c,K_d,K_e,K_0,\ldots,K_{19})$ in that order,
with a fresh verified cat for every check. Execute three positive rounds.
These are $3\times25$ check results, all required zero.
The resource is $2^{-5/2}\sum_t|t\rangle_V|\delta t\rangle_A$.
''',
     'The resource vertex check has nine targets, including the still-live vertex. The two panels belong to one nine-leaf cat and produce one check bit. Together with the edge checks, measure the 25 resource checks in three positive rounds.')

# 5. Four genuine Fredkins, with the actual temporary vertex.
en_labels=[label('a','groupa')]+[label(D+'_'+str(q),'groupa') for q in range(4) for D in ('B','C')]
en_cols=[fredkin(0,1+2*q,2+2*q) for q in range(4)]
en_cols += [{0:r'\gate{H}'},{0:r'\meter{}'}]
enrich=grid(en_labels,en_cols,{0:'b_a'},row='.58cm',col='.55cm')
page('05-enrichment', '3. Enrich the symmetry and measure the temporary vertices',
     r'''The a vertex coherently controls four physical SWAPs. Each column
with one dot and two crosses is a three-qubit Fredkin.
''' + display(enrich) + r'''
\begin{center}\begin{tabular}{ccl}
Vertex & Data-pair labels $J_v$ & Quantum action before its $X$ readout\\\hline
a&0--3&$\mathrm C_a(T_a)$\\
b&4--7&$\mathrm C_b(T_b)$\\
c&8--11&$\mathrm C_c(T_c)$\\
d&12--15&$\mathrm C_d(T_d)$\\
e&16--19&$\mathrm C_e(T_e)$
\end{tabular}\end{center}
Apply \textbf{all twenty Fredkins first}, increasing q. Then read vertices
a,b,c,d,e in X. The meter in the panel shows the a readout; defer it until
all twenty enrichment Fredkins have finished. The gauge qubits are idle
during enrichment.
\[
r_{\rm bit}=b_a\oplus b_b\oplus b_c\oplus b_d\oplus b_e;
\qquad \text{require }r_{\rm bit}=0.
\]
''',
     'Apply twenty Fredkins, with the temporary vertex controlling its four data pairs. After all twenty gates, measure all five vertices in X. Keep only even parity of their five reported bits.')

# 6. Classical corrections on tree-edge gauge qubits; no second vertex measurement.
def frame(v, q):
    return grid([label('b_'+v,colors[v]),label('A_{'+str(q)+'}','gauge')],
                [{0:r'\cwbend{1}',1:r'\gate{Z}'}],classical=(0,),row='.65cm',col='.65cm')
page('06-vertex-frame','4. Use the vertex reports to fix the gauge signs',
     r'''The upper wires below are the already measured bits, not surviving
vertex qubits. A double-wire control applies Z when its bit is one.
''' + pair(frame('b',7),frame('c',11),('$b_b$ controls $Z_{A_7}$','$b_c$ controls $Z_{A_{11}}$'))
     + '\n\\vspace{8mm}\n' + pair(frame('d',3),frame('e',0),('$b_d$ controls $Z_{A_3}$','$b_e$ controls $Z_{A_0}$')) + r'''
\[
F_b=Z_{A_7}^{b_b}Z_{A_{11}}^{b_c}Z_{A_3}^{b_d}Z_{A_0}^{b_e}.
\]
Apply these four possible gates in the displayed order. There is no
root-a correction. The already imposed even-parity condition fixes its
remaining Gauss sign.
\subhead{Release the five vertex qubits}
''' + display(grid([label('v','groupa')],[reset([0])],{0:r'\text{helper pool}'},row='.5cm',col='.65cm')) + r'''
After their readout, all five vertices may be reset for helper reuse.
From this point on, a--e name graph locations and data groups; they are
not five live gauge-check ancillas.
\[
W=\frac14\sum_{t:t_a=0}|\delta t\rangle_A V_t,
\qquad |\text{gauged}\rangle\ \propto\ W\frac{I+U}{2}|\psi\rangle.
\]
''',
     'The vertex reports classically control physical Z gates on gauge qubits 7, 11, 3, and 0. Reset the measured vertices for reuse. The vertex readout is not repeated in this step.')

# 7. Paired check: a single eight-leaf cat across both blocks.
page('07-paired','5a. While gauged: measure the paired code checks',
     r'''
\[
N_0^X=X_{B_0}X_{B_1}X_{B_2}X_{B_3}
X_{C_0}X_{C_1}X_{C_2}X_{C_3}.
\]
Prepare \textbf{one eight-leaf cat} across both panels. These couplings
produce one eight-leaf parity, not two four-leaf results.
''' + pair(ports([(j,'B_'+str(j),'groupa') for j in range(4)]),
                  ports([(j+4,'C_'+str(j),'groupa') for j in range(4)]),('Leaves 0--3: B targets','Leaves 4--7: C targets')) + r'''
\[
y(N_0^X)=\bigoplus_{j=0}^{7}\lambda_j;\qquad \text{require }y(N_0^X)=0.
\]
\subhead{The complete family}
For $R_s=(q_0<\cdots<q_{h-1})$, use $2h$ leaves, with ports
\[
\ell_j\to B_{q_j},\qquad \ell_{h+j}\to C_{q_j},\qquad j=0,\ldots,h-1.
\]
For $N_s^X$ use CNOT; for $N_s^Z$ replace each CNOT target by a CZ dot.
Measure $N_0^X,\ldots,N_8^X$, then $N_0^Z,\ldots,N_8^Z$.
The largest such cat has sixteen leaves.
\medskip

Do not measure $S_{B,s}$ and $S_{C,s}$ separately while gauged. The
required observable is their product. Cycle and Gauss checks follow,
then the entire 39-check round is repeated, three complete rounds total.
''',
     'Measure 18 paired checks using one cat across both blocks for each check. The example shows all eight ports of the inner paired X check. For paired Z checks use CZs. All check parities must be zero.')

# 8. Cycle checks, all supports listed.
cycles=[(7,15),(11,12),(3,6),(0,10),(8,19),(14,16),(4,9),(2,13),(1,18),(5,17),
        (7,8,11),(7,14,3),(7,4,0),(11,2,3),(11,1,0),(3,5,0)]
page('08-cycles','5b. While gauged: measure the sixteen cycle checks',
     r'''Use one fresh verified cat for each cycle. All target gates are CZs.
The measurement acts only on gauge qubits.
''' + pair(ports([(0,'A_7','gauge'),(1,'A_{15}','gauge')],'Z'),
                  ports([(0,'A_7','gauge'),(1,'A_8','gauge'),(2,'A_{11}','gauge')],'Z'),
                  ('$L_{(7,15)}=Z_{A_7}Z_{A_{15}}$', '$L_{(7,8,11)}=Z_{A_7}Z_{A_8}Z_{A_{11}}$')) + r'''
\subhead{All sixteen supports, in measurement order}
\[
\begin{aligned}
&(7,15),\ (11,12),\ (3,6),\ (0,10),\ (8,19),\\
&(14,16),\ (4,9),\ (2,13),\ (1,18),\ (5,17),\\
&(7,8,11),\ (7,14,3),\ (7,4,0),\\
&(11,2,3),\ (11,1,0),\ (3,5,0).
\end{aligned}
\]
Within a check, couple ports in increasing edge-label order, then measure
the leaves. Require the single parity $y(L_\eta)=\bigoplus_j\lambda_j=0$.
The six triangles together with the ten parallel-edge pairs form a
cycle basis. After these sixteen checks, measure the five Gauss checks.
''',
     'Measure ten parallel-edge checks and six triangle checks, in the listed order. Each uses its own cat; retain only a zero leaf-X parity. The former graph vertices are absent.')

# 9. All twelve Gauss ports. Four panels share one cat.
gauge_ports=[(j,'A_{'+str(q)+'}','gauge') for j,q in enumerate(ea)]
page('09-gauss','5c. While gauged: the full local Gauss-check circuit',
     r'''
\[
G_a=(X_{A_0}X_{A_3}X_{A_6}X_{A_7}X_{A_{10}}X_{A_{11}}X_{A_{12}}X_{A_{15}})T_a.
\]
Prepare \textbf{one twelve-leaf cat} before all four panels. Eight ports
are CNOTs to gauge qubits; four are Fredkins to data pairs.
''' + pair(ports(gauge_ports[:4]),ports(gauge_ports[4:]),('Gauge ports 0--3','Gauge ports 4--7'))
     + '\n\\vspace{3mm}\n' + pair(swap_ports([(8,0,'groupa'),(9,1,'groupa')]),
                  swap_ports([(10,2,'groupa'),(11,3,'groupa')]),('Data-pair ports 8--9','Data-pair ports 10--11')) + r'''
\[
y(G_a)=\bigoplus_{j=0}^{11}\lambda_j;\qquad \text{require }y(G_a)=0.
\]
The panels are port fragments, not four check measurements. Execute all
twelve controlled factors before the leaf readout. For v=b,c,d,e replace
$(E_a,J_a)$ by $(E_v,J_v)$, retaining the same twelve-port pattern.
\[
G_v=X_{A,E_v}T_v,\qquad G_aG_bG_cG_dG_e=U.
\]
One full round is $18\ N$ checks, $16\ L$ checks, then $5\ G$ checks.
Repeat that entire round three times, using fresh cats throughout.
''',
     'The four panels belong to one twelve-leaf Gauss-check cat. Read out only after all controlled factors. Measure Ga through Ge after the paired and cycle checks; repeat the full 39-check round three times.')

# 10. Ungauging readout, real classical decoder, classically controlled SWAP.
gread=grid([label('A_q','gauge')],[{0:r'\meter{}'}],{0:'m_q'},row='.6cm',col='.7cm')
dec=grid([r'm_0,\ldots,m_{19}'],[{0:r'\gate[cwires={1}]{\operatorname{Dec}_{\mathcal W}}'}],
         {0:r'\widehat t_a,\ldots,\widehat t_e'}, classical=(0,),col='.8cm')
uswap=grid([r'\widehat t_v',label('B_q','groupa'),label('C_q','groupa')],
           [{0:r'\cwbend{1}',1:r'\swap{1}',2:r'\targX{}'}],
           classical=(0,),row='.65cm',col='.8cm')
page('10-ungauging','6. Ungauge: read all edges, decode, and correct',
     r'''Measure every $A_q$ in Z, increasing $q=0,\ldots,19$. Collect all
twenty reported bits before choosing any SWAP correction.
''' + display(gread) + display(dec) + r'''
The double-wire box is classical computation. Enumerate all sixteen cut
words $w=\delta t$, with $t_a=0$. Choose the word $\widehat w$ within
Hamming distance two of m, or reject if none exists.
\[
\widehat t_a=0,\quad\widehat t_b=\widehat w_7,\quad
\widehat t_c=\widehat w_{11},\quad\widehat t_d=\widehat w_3,\quad
\widehat t_e=\widehat w_0.
\]
\subhead{A classical bit controls each ordinary data SWAP}
''' + display(uswap) + r'''
For each $q\in J_v$, apply SWAP$(B_q,C_q)$ when $\widehat t_v=1$,
omitting it otherwise. Execute $q=0,\ldots,19$ in order. These are not
coherent Fredkins: their controls are classical bits. Discard/reset A.
\[
\text{Decode all twenty reports first; do not use the four raw tree bits.}
\]
''',
     'Measure all gauge qubits in Z. The classical decoder chooses a valid cut word within distance two, then derives the five group bits. Each decoded bit controls ordinary SWAPs in its four-qubit data group. Reject a word outside the decoding radius.')

# 11. Terminal filter and recovery; per-qubit correction uses classical bits.
correction=grid([r'x_{D,q},z_{D,q}',label('D_q','groupa')],
                [{0:r'\cw\vcw{1}',1:r'\gate{P_{x,z}}'}],
                classical=(0,),row='.65cm',col='.8cm')
page('11-recovery','7--8. Filter the original code, then recover',
     r'''Reuse the four-body Pauli circuit on page 2, extended to eight
targets for the upper checks. A fresh verified cat is required each time.
\[
\mathcal O=(S^X_{B,0:8},S^Z_{B,0:8},S^X_{C,0:8},S^Z_{C,0:8}).
\]
\subhead{7. Terminal positive filter}
Measure the complete 36-check family $\mathcal O$ in three rounds.
Require all $3\times36$ check bits zero. A nonzero syndrome rejects.
\subhead{8. Subsequent syndrome recovery}
Measure $\mathcal O$ repeatedly, retaining either check sign. Require
cat-verification bits zero. Apply no correction between rounds.
\[
\tau=\min\{r\in\{3,\ldots,9\}:\mathbf s^{(r)}=
\mathbf s^{(r-1)}=\mathbf s^{(r-2)}\}.
\]
Reject if there is no identical triple by round nine. For each block D,
choose a minimum-weight Pauli $R_D$, of weight at most two, matching its
eighteen stopping-syndrome bits; reject if none exists. Use the fixed
lookup in \texttt{c4\_helix\_intrinsic\_decoder.py}.
\subhead{The physical correction: one-qubit gates only}
''' + display(correction) + r'''
The classical pair selects $P_{0,0}=I$, $P_{1,0}=X$, $P_{0,1}=Z$,
or $P_{1,1}=Y$. Apply the selected single-qubit Pauli, visiting physical
labels in order, B then C; omit identity factors. For Y use one Y gate.
The gate acts on one data qubit; the syndrome lookup is classical.
''',
     'First take three positive rounds of original-code checks. Then perform syndrome recovery, which accepts either check sign and stops at the first identical triple, within nine rounds. Apply the selected Pauli through single-qubit gates, B then C.')

# 12. Full physical readout and classical decision. C stays quantum.
readout=grid([label('B_q','groupa'),label('C_q','groupa')],
             [{0:r'\meter{}'}],{0:'n_q',1:r'\text{retain}'},row='.65cm',col='.7cm')
finaldec=grid([r'n_0,\ldots,n_{19}'],
              [{0:r'\gate[cwires={1}]{\operatorname{Dec}_{B}}'},
               {0:r'\gate[cwires={1}]{\ell(n\oplus e)}'}],
              {0:r'\text{keep iff }0'},classical=(0,),col='.6cm')
page('12-extraction','9. Decode the final B readout and retain magic in C',
     r'''For $q=0,\ldots,19$, measure B in Z. C remains a quantum output.
The horizontal C wire also represents its counted waiting idles.
''' + display(readout) + display(finaldec) + r'''
\[
\begin{aligned}
h_s(n)&=\bigoplus_{q\in R_s}n_q,\qquad s=0,\ldots,8,\\
&\text{choose minimum-weight }e,\quad |e|\le2,\quad h(e)=h(n),\\
n'&=n\oplus e,\\
\ell(n')&=n'_0\oplus n'_3\oplus n'_6\oplus n'_7\oplus n'_{18}\oplus n'_{19}.
\end{aligned}
\]
Reject if the correction e does not exist. Fix readout ties by
lexicographic order of the flipped-position lists. Keep only
$\ell(n')=0$. Correction of n is classical; no postmeasurement X gates
are applied to B. Discard B and retain the twenty-qubit C block.
\subhead{Ideal logical output}
\[
\frac{2|00\rangle+|01\rangle+|10\rangle}{\sqrt6}
\ \xrightarrow{\ \overline Z^B_0=+1\ }\ 
|0\rangle_B\frac{2|0\rangle+|1\rangle}{\sqrt5}_C.
\]
Both second logical qubits are spectators in zero.
The retained output is $|\overline{M0}\rangle_C$, up to the physical
correctable errors allowed by the linked two-fault analysis.
''',
     'Measure all twenty B qubits in Z and decode the complete report. Keep logical Z0 equal to +1, discard B, and retain C. The final correction is to the classical word, not to already measured qubits.')

# 13. Self-contained data and concise schedule ledger.
support_rows='\n'.join(str(s)+' & '+', '.join(map(str,qs))+r' \\' for s,qs in enumerate(R))
page('13-reference','Reference: supports, order, and resources',
     r'''
Each support defines $S^X_{D,s}=\prod_{q\in R_s}X_{D_q}$ and
$S^Z_{D,s}=\prod_{q\in R_s}Z_{D_q}$. Measure only $s=0,\ldots,8$
as independent code checks; use row 9 for graph incidence.
\begin{center}\begin{tabular}{cl}\toprule
s & $R_s$\\\midrule
''' + support_rows + r'''
\bottomrule\end{tabular}\end{center}
\[
\begin{aligned}
\overline X_0&=X_{\{2,3,8,11,12,15\}},\\
\overline Z_0&=Z_{\{0,3,6,7,18,19\}},\qquad
\overline Z_1=Z_{\{2,3,8,11,12,15\}}.
\end{aligned}
\]
\subhead{One attempt, in execution order}
\begin{enumerate}\setlength\itemsep{1pt}
\item Prepare B, then C: three positive 20-check rounds each.
\item Prepare graph; three positive 25-check resource rounds.
\item Twenty enrichment Fredkins; measure the five vertices in X.
\item Require even vertex parity; apply the four possible gauge-Z gates.
\item Three positive gauged rounds: $18N$, $16L$, $5G$, in that order.
\item Gauge-Z readout; decode; apply ordinary data SWAPs.
\item Three positive 36-check original-code rounds.
\item Recovery: first identical syndrome triple, at most nine rounds.
\item Complete B-Z readout; decode; keep logical zero and retain C.
\end{enumerate}
\textbf{Allocation:} 40 data + 20 gauge + 17 reusable helpers = 77 qubits.
Five helpers initially serve as vertices. The largest cat has 16 leaves
plus one verifier. \textbf{Fredkins:} $20+3\times5\times4=80$.
\medskip

All gates and measurements are scheduled serially; paired panels are
fragments of a circuit, not additional parallel hardware. Unused live
qubits have counted idles. Any required failed test rejects the whole
attempt. The global fault allowance is two faulty locations total,
including helpers, reports, recovery, and readout, as specified in the
companion analysis. These drawings do not change that protocol or prove
a new fault-tolerance result.
''',
     'Complete support lists and the execution ledger. The protocol uses 77 physical qubits with serial helper reuse and 80 Fredkins. All rejection rules, waiting idles, recovery, and readout belong to the same attempt.')

preamble=r'''\documentclass[11pt]{article}
\usepackage[a4paper,margin=16mm,headheight=14pt,footskip=10mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype,amsmath,amssymb,booktabs,adjustbox,xcolor}
\usepackage{quantikz}
\usepackage{fancyhdr,hyperref}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,pdftitle={Full circuit: C4-Helix SWAP gauging},pdfauthor={}}
\definecolor{ink}{HTML}{203044}
\definecolor{cat}{HTML}{986F14}
\definecolor{gauge}{HTML}{148E9E}
\definecolor{groupa}{HTML}{367AAF}
\definecolor{groupb}{HTML}{D47D28}
\definecolor{groupc}{HTML}{378957}
\definecolor{groupd}{HTML}{8863AF}
\definecolor{groupe}{HTML}{CA5D85}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\abovedisplayskip}{7pt}
\setlength{\belowdisplayskip}{7pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{ink}C4-Helix / full circuit}
\fancyhead[R]{\small Companion to full\_procedure.md}
\fancyfoot[L]{\footnotesize Quantum controls: solid wire. Classical feedforward: double wire.}
\fancyfoot[R]{\thepage}
\renewcommand{\headrulewidth}{.3pt}
\newcommand{\subhead}[1]{\par\vspace{3mm}{\bfseries\color{ink}#1}\par}
\begin{document}
'''
parts=[preamble]
for i,p in enumerate(pages):
    if i: parts.append(r'\newpage'+'\n')
    parts.append(r'{\Large\bfseries\color{ink}'+p['title']+r'}\par\vspace{3mm}'+'\n')
    parts.append(p['body'])
parts.append('\n'+r'\end{document}'+'\n')
PROJECT.mkdir(parents=True,exist_ok=True)
FIGURES.mkdir(parents=True,exist_ok=True)
(PROJECT/'main.tex').write_text('\n'.join(parts))

intro='''# Full circuit: a graphical companion to the full procedure

This is the same **single-cycle, postselected 80-Fredkin circuit** as
[full_procedure.md](full_procedure.md), drawn using LaTeX `quantikz`.
The diagrams are embedded as images because Markdown math renderers
generally cannot execute TikZ circuit environments.

[Read the compiled PDF](../output/pdf/full_circuit.pdf) or edit the
[LaTeX source](full-circuit-latex/main.tex). Each image below is cropped
from a page of that PDF. The [build script](build-full-circuit.py) generates the
source and this companion from the source-backed decoder's support data.

Read left to right. A **|0⟩ box resets** its qubit; a meter measures Z;
**H followed by a meter measures X**. Solid wires carry qubits, double
wires carry classical reports. Turquoise labels are gauge qubits and
gold labels are cat leaves. A dot plus two crosses is a coherent Fredkin;
a double-wire control on two crosses is a classically chosen ordinary SWAP.

Split panels share **one** cat whenever the caption says so. Every check
uses a fresh cat, with the preparation and verification on the first page.
The drawings show port connections; the exact circuit schedule remains
serial. A meter shown on a port is read only after all that check's
controlled factors. This also applies to the five vertex readouts after
all twenty enrichment Fredkins.

'''
md=[intro]
for p in pages:
    md += ['## '+p['title']+'\n\n',p['md']+'\n\n',
           '!['+p['title']+'](figures/c4-helix/full-circuit/'+p['slug']+'.png)\n\n']
md += ['''The diagrams specify the operations and acceptance rules; the
[intrinsic-verification analysis](c4-helix-intrinsic-gauged-verification.md)
contains the associated fault-tolerance argument. The equations and
state-normalization checks remain in [full_procedure.md](full_procedure.md).
''']
(HERE/'full_circuit.md').write_text(''.join(md))
(FIGURES/'page-order.txt').write_text('\n'.join(p['slug'] for p in pages)+'\n')
print(f'Wrote {len(pages)} circuit pages to {PROJECT / "main.tex"}')
print(f'Wrote {HERE / "full_circuit.md"}')

if '--render' in sys.argv:
    import shutil
    import subprocess
    from PIL import Image
    import pdfplumber

    root = HERE.parent
    build = root / 'tmp/pdfs/full-circuit'
    build.mkdir(parents=True, exist_ok=True)
    with (build / 'compile.stdout').open('w') as log:
        subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                        f'-output-directory={build}', str(PROJECT / 'main.tex')],
                       cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
    assert 'Overfull' not in (build / 'main.log').read_text(), 'Inspect LaTeX layout warnings'
    output = root / 'output/pdf/full_circuit.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(build / 'main.pdf', output)
    subprocess.run(['pdftoppm', '-r', '180', '-png', str(output), str(build / 'page')], check=True)
    with pdfplumber.open(output) as document:
        assert len(document.pages) == len(pages)
        for i, (p, pdfpage) in enumerate(zip(pages, document.pages), 1):
            body = [c for c in pdfpage.chars if 40 < float(c['top']) < pdfpage.height - 45]
            bottom = max(float(c['bottom']) for c in body) + 12
            im = Image.open(build / f'page-{i:02}.png').convert('RGB')
            sx, sy = im.width / pdfpage.width, im.height / pdfpage.height
            box = (round(34*sx), round(40*sy), round((pdfpage.width-34)*sx), round(bottom*sy))
            im.crop(box).save(FIGURES / f'{p["slug"]}.png')
    print(f'Exported {output} and {len(pages)} cropped circuit images')
