"""Exact quadratic-phase fault normal forms for isolated hybrid outer meters.

Not a full-factory decoder. T faults are propagated as coherent operators,
not sampled Pauli terms. Diagonal-Clifford Fourier SUPPORTS are derived
analytically; class unions conservatively allow arbitrary coefficients.
"""
from dataclasses import dataclass
from itertools import product
from functools import lru_cache
import c4_helix_single_block_cz as m
import single_cz_hybrid_study as h
from single_cz_compact_checks import compact_pauli_program


def bits(x):
    while x:
        b=x & -x;yield b.bit_length()-1;x ^= b


def gate_report_noise_event(witness):
    if witness['operation']=='MZ':return witness['flip_report'] and not any(witness['paulis'])
    return witness['operation'] in ('CX','T','TDG','H','X')


def provenance_score(events):
    return sum(not gate_report_noise_event(e) for e in events),len(events)


def row_basis(words):
    rows={}
    for word in words:
        for k,p in sorted(rows.items(),reverse=True):
            if word >> k&1:word ^= p
        if word:
            k=word.bit_length()-1
            for j,p in list(rows.items()):
                if p >> k&1:rows[j]=p ^ word
            rows[k]=word
    return tuple(rows[k] for k in sorted(rows,reverse=True))


def reduce_word(word,rows):
    for r in rows:
        if word >> (r.bit_length()-1)&1:word ^= r
    return word


def solve_affine(equations,n):
    pivots={}
    for r,b in equations:
        for k,(p,c) in sorted(pivots.items(),reverse=True):
            if r >> k&1:r ^= p;b ^= c
        if not r:
            if b:return None
            continue
        k=r.bit_length()-1
        for j,(p,c) in list(pivots.items()):
            if p >> k&1:pivots[j]=(p ^ r,c ^ b)
        pivots[k]=(r,b)
    base=sum(b << k for k,(r,b) in pivots.items())
    generators=[]
    for j in range(n):
        if j not in pivots:
            generators.append((1 << j) | sum(((r >> j)&1) << k for k,(r,b) in pivots.items()))
    return base,tuple(generators)


@dataclass(frozen=True)
class Quadratic:
    # E|y> = zeta8^phase i^(l.y + 2 sum a_ij y_i y_j) |y XOR x>.
    x:int
    l:tuple
    a:tuple
    phase:int=0

    @classmethod
    def pauli(cls,n,assignments):
        x=0;l=[0]*n;phase=0
        for q,p in assignments:
            if p&1:x ^= 1 << q
            if p>>1:l[q] ^= 2
            if p==3:phase+=2
        return cls(x,tuple(l),(0,)*n,phase%8)

    @property
    def key(self):return self.x,self.l,self.a  # global phase does not affect recovery

    def conjugate(self,ops):
        x=self.x;l=list(self.l);a=list(self.a);phase=self.phase;n=len(l)
        for op,qs in ops:
            if op=="CX":
                c,t=qs;old=l[t];neighbours=a[t];ct=(neighbours >> c)&1
                l[c]=(l[c]+old+2*ct)%4
                for j in bits(neighbours & ~((1 << c)|(1 << t))):
                    a[c] ^= 1 << j;a[j] ^= 1 << c
                if old%2:a[c] ^= 1 << t;a[t] ^= 1 << c
                x ^= ((x >> c)&1) << t
            elif op in ("T","TDG"):
                q=qs[0]
                if x >> q&1:
                    sign=1 if op=="T" else -1
                    phase+=sign;l[q]=(l[q]-sign)%4
            elif op=="X":
                q=qs[0];phase+=2*l[q];l[q]=(-l[q])%4
                for j in bits(a[q]):l[j]=(l[j]+2)%4
            elif op=="H":
                q=qs[0]
                # Only the initial syndrome H is propagated here, before coupling.
                assert a[q]==0 and l[q]%2==0
                old=(x >> q)&1;z=l[q]//2
                phase+=4*old*z;x ^= (old ^ z) << q;l[q]=2*old
            else:raise ValueError(op)
        return Quadratic(x,tuple(l),tuple(a),phase%8)

    def after(self,earlier):
        """Exact operator product self * earlier, including coherent phases."""
        l=[];phase=self.phase+earlier.phase
        for q,value in enumerate(self.l):
            flip=(earlier.x >> q)&1
            phase+=2*value*flip
            phase+=4*flip*((self.a[q] & earlier.x & ((1 << q)-1)).bit_count()%2)
            value=(-value if flip else value)+2*(self.a[q] & earlier.x).bit_count()
            l.append((value+earlier.l[q])%4)
        return Quadratic(self.x ^ earlier.x,tuple(l),tuple(a ^ b for a,b in zip(self.a,earlier.a)),phase%8)

    def fourier_support(self,variables):
        """Exact affine Pauli-Z support after fixing omitted input variables to 0.

        For i^linear (-1)^quadratic, support is z0+image(B), where B is
        the symmetric binary quadratic form, with odd-S terms on its diagonal.
        Kernel constraints retain the signs (including negative S terms).
        """
        active=[q for q in variables if self.l[q] or any((self.a[q] >> j)&1 for j in variables)]
        n=len(active)
        B=[sum((((self.a[q] >> r)&1) if r!=q else self.l[q]%2) << j for j,r in enumerate(active)) for q in active]
        kernel=solve_affine([(r,0) for r in B],n)[1]
        equations=[]
        for r in kernel:
            total=sum(self.l[active[j]] for j in bits(r))
            assert total%2==0
            quad=sum((B[i] & r & ((1 << i)-1)).bit_count() for i in bits(r))%2
            equations.append((r,(total//2+quad)%2))
        base,_=solve_affine(equations,n)
        embed=lambda word:sum(1 << active[j] for j in bits(word))
        return embed(base),tuple(embed(r) for r in row_basis(B))


def coordinate_program(graph):
    ops=[]
    for v,e in enumerate(graph.tree,1):
        for q in range(4*v,4*v+4):
            first,last=("T","TDG") if m.SIGNS[q]==1 else ("TDG","T")
            ops += [(first,(f"D{q}",)),("CX",(f"A{e}",f"D{q}")),(last,(f"D{q}",))]
    return ops


def programs(ds,graph,route):
    if route=="hybrid":return h.outer_program(ds,optimized=True),1
    if route=="hybrid_two_flags":return h.outer_two_flag_program(ds),2
    if route!="reference":raise ValueError(route)
    pauli=compact_pauli_program("X",8)
    labels={j:f"D{q}" for j,q in enumerate(ds)}
    labels[8]="s";labels.update({9+j:f"f{j}" for j in range(4)})
    middle=[(op,tuple(labels[q] for q in qs)) for op,qs in pauli]
    V=coordinate_program(graph)
    return V+middle+V,4


def enumerate_faults(ds,graph,route):
    """All one-location Pauli basis faults, arbitrary measurement reports, idles.

    Graph/data input is encoded and clean in V coordinates. Final diagnostic
    readout is IDEAL and is NOT part of this circuit's fault set.
    """
    program,nf=programs(ds,graph,route)
    labels=[f"D{q}" for q in range(20)]+[f"A{e}" for e in range(len(graph.edges))]+["s"]
    labels += ["f"] if nf==1 else [f"f{j}" for j in range(nf)]
    index={q:j for j,q in enumerate(labels)};n=len(labels);syndrome=index["s"]
    flags=tuple(index[q] for q in labels if q.startswith("f"))
    V=[(op,tuple(index[q] for q in qs)) for op,qs in coordinate_program(graph)]
    initial_H=next(i for i,g in enumerate(program) if g==("H",("s",)))
    final_H=max(i for i,g in enumerate(program) if g==("H",("s",)))
    suffix=[]
    for i in range(len(program)+1):
        suffix.append([(op,tuple(index[q] for q in qs)) for j,(op,qs) in enumerate(program[i:],i)
                       if op not in ("PREP","MZ") and j!=final_H])
    events={};live=set(labels[:20+len(graph.edges)]);location=0;basis_cases=0
    def add(i,op,qs,start,after_H=False):
        nonlocal location,basis_cases
        here=location;location+=1
        for ps in product(range(4),repeat=len(qs)):
            for flip in range(2 if op=="MZ" else 1):
                if not any(ps) and not flip:continue
                basis_cases+=1
                assignments=[];extra_phase=0
                for q,p in zip(qs,ps):
                    if q=="s" and after_H:
                        if p==3:extra_phase+=4 # H Y H = -Y, including global basis coefficient
                        p=((p&1) << 1) | (p >> 1)
                    assignments.append((index[q],p))
                error=Quadratic.pauli(n,assignments)
                error=Quadratic(error.x,error.l,error.a,(error.phase+extra_phase)%8).conjugate(suffix[start]).conjugate(V)
                report=0
                if flip:
                    report=1 << (flags.index(index[qs[0]]) if qs[0].startswith("f") else nf)
                key=error.key+(report,)
                witness=dict(instruction=i,operation=op,targets=list(qs),paulis=list(ps),flip_report=bool(flip),location=here)
                if key not in events:events[key]=dict(error=error,report=report,first=here,last=here,witness=witness,last_witness=witness,
                                                      noise_first=witness if gate_report_noise_event(witness) else None,noise_last=None)
                else:events[key]["last"]=here;events[key]["last_witness"]=witness
                if gate_report_noise_event(witness):
                    if events[key]['noise_first'] is None:events[key]['noise_first']=witness
                    events[key]['noise_last']=witness
    for i,(op,qs) in enumerate(program):
        for q in sorted(live-set(qs)):
            add(i,"IDLE",(q,),i,i>final_H)
        add(i,op,qs,i if op=="MZ" else i+1,i>=final_H)
        if op=="PREP":live.update(qs)
        elif op=="MZ":live.difference_update(qs)
    # Explicit terminal waiting interval on every retained data/edge wire.
    for q in sorted(live):add(len(program),"BOUNDARY",(q,),len(program),True)
    return list(events.values()),dict(locations=location,pauli_basis_cases=basis_cases,unique_errors=len(events)),labels,flags


@lru_cache(maxsize=65536)
def classword(x,z,graph):
    data=(1 << 20)-1;xd=x & data;zd=z & data;gx=x >> 20;gz=z >> 20
    result=sum(((xd & m.mask(r)).bit_count()%2) << j for j,r in enumerate(m.SUPPORTS))
    result |= sum(((zd & m.mask(r)).bit_count()%2) << (9+j) for j,r in enumerate(m.SUPPORTS))
    result |= sum(((gx & m.mask(c)).bit_count()%2) << (18+j) for j,c in enumerate(graph.cycles))
    offset=18+len(graph.cycles)
    for v in range(1,5):
        star=sum(1 << e for e,ends in enumerate(graph.edges) if v in ends)
        result |= ((gz & star).bit_count()%2) << (offset+v-1)
    logical=sum(((word & m.mask(s)).bit_count()%2) << j for j,(word,s) in enumerate(((xd,m.Z0),(xd,m.Z1),(zd,m.X0),(zd,m.X1))))
    return result | (logical << (offset+4))


@lru_cache(maxsize=20000)
def phase_class_image(l,a,nvariables,graph):
    base,gens=Quadratic(0,l,a).fourier_support(range(nvariables))
    nc=18+len(graph.cycles)+4
    def mapped(z):
        word=classword(0,z,graph)
        return (word & ((1 << nc)-1)) | (((z >> (20+len(graph.edges)))&1) << nc) | ((word >> nc) << (nc+1))
    return mapped(base),row_basis(mapped(z) for z in gens)


def class_image(error,report,labels,flags,graph):
    base,image=phase_class_image(error.l,error.a,flags[0],graph)
    # Include the current meter's REPORTED X outcome, including its report fault.
    nc=18+len(graph.cycles)+4;nsyndrome=nc+1
    word=classword(error.x,0,graph)
    origin=(word & ((1 << nc)-1)) | ((word >> nc) << (nc+1))
    origin ^= ((report >> len(flags))&1) << nc
    origin=reduce_word(origin ^ base,image)
    flag=sum((((error.x >> q)&1) ^ ((report >> j)&1)) << j for j,q in enumerate(flags))
    return (flag,origin,image),nsyndrome


def image_words(origin,rows):
    words=[origin]
    for r in rows:words += [word ^ r for word in words]
    return words
