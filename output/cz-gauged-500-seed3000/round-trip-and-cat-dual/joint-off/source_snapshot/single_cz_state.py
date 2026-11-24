"""Coherent one-block simulator with exact Z[zeta_8] coefficients.

One term is c |helper-basis> |data-factor>. Data factors are flat sparse
unitary kets with eighth-root phases. In the factory every data H occurs
outside a completed T/CX/Tdg port: each factor is then a stabilizer ket.
T intermediates are retained explicitly, never replaced by Clifford gates.
No amplitudes are truncated. Unsupported nonflat factors raise, rather than
silently approximate a general Clifford+T circuit. Born norms and draws are
exact: irrational probabilities use lazy random bits and integer sign tests.
"""
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import reduce
from math import gcd
import numpy as np


class C8(tuple):
    def __new__(cls, a=0, b=0, c=0, d=0):
        if isinstance(a, C8):
            return a
        return tuple.__new__(cls, (int(a), int(b), int(c), int(d)))

    def __add__(self, other):
        other = C8(other)
        return C8(*(a+b for a, b in zip(self, other)))
    __radd__ = __add__

    def __neg__(self):
        return C8(*(-a for a in self))

    def __sub__(self, other):
        return self + -C8(other)

    def __mul__(self, other):
        if isinstance(other, int):
            return C8(*(a*other for a in self))
        a,b,c,d = self
        e,f,g,h = C8(other)
        return C8(a*e-b*h-c*g-d*f, a*f+b*e-c*h-d*g,
                  a*g+b*f+c*e-d*h, a*h+b*g+c*f+d*e)
    __rmul__ = __mul__

    def __bool__(self):
        return any(self)

    def conj(self):
        a,b,c,d = self
        return C8(a,-d,-c,-b)

    def decimal_real(self):
        a,b,c,d = self
        if c or d != -b:
            raise ArithmeticError(f"Non-real norm {self}")
        with localcontext() as ctx:
            ctx.prec = max(100, int(max(abs(a).bit_length(), abs(b).bit_length())*.61)+80)
            return +(Decimal(a)+Decimal(b)*Decimal(2).sqrt())

    def real_sign(self):
        a,b,c,d=self
        if c or d != -b:
            raise ArithmeticError("Sign of a non-real cyclotomic number")
        if not b:return (a>0)-(a<0)
        if not a:return (b>0)-(b<0)
        if a>0 and b>0:return 1
        if a<0 and b<0:return -1
        delta=a*a-2*b*b if a>0 else 2*b*b-a*a
        return (delta>0)-(delta<0)

    def complex(self, divisor=1):
        a,b,c,d = (float(Fraction(v, divisor)) for v in self)
        return complex(a+(b-d)/np.sqrt(2), c+(b+d)/np.sqrt(2))

    def rotate(self,k):
        out=[0]*4
        k%=8
        for j,value in enumerate(self):
            power=j+k
            out[power%4] += value*(-1 if (power//4)%2 else 1)
        return C8(*out)

    @staticmethod
    def phase(k):
        k %= 8
        row = [0]*4
        row[k % 4] = 1 if k < 4 else -1
        return C8(*row)


SQRT2 = C8(0,1,0,-1)
ZERO, ONE = C8(), C8(1)


@dataclass
class Factor:
    labels: tuple
    indices: np.ndarray
    phases: np.ndarray
    signature: tuple


class FactorStore:
    def __init__(self, max_factors=4096):
        self.factors, self.identities, self.actions, self.overlaps = {}, {}, {}, {}
        self.next_id = 0
        self.max_factors = max_factors
        self.peak_factors = 0
        self.collections = 0

    def intern(self, labels, indices, phases):
        indices = np.asarray(indices, dtype=np.uint32)
        phases = np.asarray(phases, dtype=np.int16) % 8
        if not len(indices):
            return None, ZERO
        order = np.argsort(indices)
        indices, phases = indices[order], phases[order]
        if len(indices) > 1 and np.any(indices[1:] == indices[:-1]):
            raise ArithmeticError("Duplicate data-factor basis coordinates")
        phase = int(phases[0])
        phases = ((phases-phase) % 8).astype(np.uint8)
        signature = tuple(labels), indices.tobytes(), phases.tobytes()
        fid = self.identities.get(signature)
        if fid is None:
            fid = self.next_id
            self.next_id += 1
            self.identities[signature] = fid
            self.factors[fid] = Factor(tuple(labels), indices, phases, signature)
            self.peak_factors = max(self.peak_factors, len(self.factors))
        return fid, C8.phase(phase)

    def action(self, fid, op, targets):
        key = fid, op, tuple(targets)
        if key in self.actions:
            return self.actions[key]
        f = self.factors[fid]
        indices, phases, scale = f.indices, f.phases.astype(np.int16), ONE
        q = f.labels.index(targets[0])
        bit = np.uint32(1 << q)
        value = ((indices >> q) & 1).astype(np.int16)
        if op == "H":
            lows = np.unique(indices & ~bit)
            p0, p1 = np.searchsorted(indices, lows), np.searchsorted(indices, lows | bit)
            have0 = (p0 < len(indices)) & (indices[np.minimum(p0,len(indices)-1)] == lows)
            have1 = (p1 < len(indices)) & (indices[np.minimum(p1,len(indices)-1)] == (lows | bit))
            if np.all(have0 ^ have1):
                base = phases[np.where(have0,p0,p1)]
                indices = np.concatenate((lows, lows | bit))
                phases = np.concatenate((base, base+4*have1))
            elif np.all(have0 & have1):
                base = phases[p0]
                delta = (phases[p1]-base) % 8
                if np.all((delta == 0) | (delta == 4)):
                    indices, phases, scale = lows | ((delta == 4).astype(np.uint32)*bit), base, C8(2)
                elif np.all((delta == 2) | (delta == 6)):
                    shift = np.where(delta == 2,1,-1)
                    indices = np.concatenate((lows,lows | bit))
                    phases = np.concatenate((base+shift,base-shift))
                    scale = SQRT2
                else:
                    raise ArithmeticError("Nonflat factor at H: outside factory port-order invariant")
            else:
                raise ArithmeticError("Nonaffine factor at H: outside factory port-order invariant")
        elif op in ("X","Y","Z","S","SDG","T","TDG"):
            if op in ("X","Y"):
                indices = indices ^ bit
            phases = phases + {"X":0, "Y":2+4*value, "Z":4*value,
                               "S":2*value, "SDG":6*value, "T":value, "TDG":7*value}[op]
        elif op == "CX":
            target = f.labels.index(targets[1])
            indices = indices ^ (((indices >> q) & 1) << target)
        else:
            raise ValueError(op)
        new, phase = self.intern(f.labels,indices,phases)
        answer = new, scale*phase
        self.actions[key] = answer
        return answer

    def project(self, fid, label, outcome, remove=True):
        key = fid, "MZ" if remove else "FILTER", label, outcome
        if key not in self.actions:
            f = self.factors[fid]
            q = f.labels.index(label)
            selected = ((f.indices >> q) & 1) == outcome
            indices = f.indices[selected]
            labels = f.labels
            if remove:
                indices = (indices & ((1 << q)-1)) | ((indices >> (q+1)) << q)
                labels = labels[:q]+labels[q+1:]
            self.actions[key] = self.intern(labels, indices, f.phases[selected])
        return self.actions[key]

    def overlap(self, a, b):
        if a == b:
            return C8(len(self.factors[a].indices))
        key = a,b
        if key not in self.overlaps:
            f,g = self.factors[a],self.factors[b]
            if f.labels != g.labels:
                raise ValueError("Incompatible data-factor partitions")
            _, left, right = np.intersect1d(f.indices,g.indices,assume_unique=True,return_indices=True)
            counts = np.bincount((g.phases[right].astype(np.int16)-f.phases[left]) % 8,minlength=8)
            v = C8(*(int(counts[j])-int(counts[j+4]) for j in range(4)))
            self.overlaps[key], self.overlaps[b,a] = v,v.conj()
        return self.overlaps[key]

    def collect(self, live):
        if len(self.factors) <= self.max_factors:
            return
        live = set(live)
        recent = min(256,max(0,self.max_factors-len(live)))
        keep = live | (set(sorted(self.factors)[-recent:]) if recent else set())
        if len(keep) > self.max_factors:
            raise MemoryError("Live exact data-factor limit exceeded")
        self.factors = {k:v for k,v in self.factors.items() if k in keep}
        self.identities = {v.signature:k for k,v in self.factors.items()}
        self.actions = {k:v for k,v in self.actions.items() if k[0] in keep and (v[0] is None or v[0] in keep)}
        self.overlaps = {k:v for k,v in self.overlaps.items() if k[0] in keep and k[1] in keep}
        self.collections += 1


class CoherentState:
    def __init__(self, data_labels, max_terms=4096, max_factors=4096):
        self.store = FactorStore(max_factors)
        fid,_ = self.store.intern(data_labels,[0],[0])
        self.terms = {(0,fid):ONE}
        self.basis_labels = []
        self.max_terms, self.peak_terms = max_terms,1
        self.css_compressions = 0

    def combine(self, rows, reduce_common=False):
        out = {}
        for basis,fid,c in rows:
            key = basis,fid
            value = out.get(key,ZERO)+c
            if value:
                out[key] = value
            else:
                out.pop(key,None)
        if len(out) > self.max_terms:
            raise MemoryError(f"Coherent term limit exceeded: {len(out)} > {self.max_terms}")
        if reduce_common and out:
            divisor = reduce(gcd,(abs(v) for c in out.values() for v in c))
            if divisor > 1:
                out = {k:C8(*(v//divisor for v in c)) for k,c in out.items()}
        self.terms = out
        self.peak_terms = max(self.peak_terms,len(out))

    def labels(self):
        return tuple(self.basis_labels)+self.store.factors[next(iter(self.terms))[1]].labels

    def allocate(self,label):
        if label in self.labels():
            raise ValueError("Qubit already represented")
        self.basis_labels.append(label)

    def absorb_basis_label(self,label):
        """Exact tensor regrouping: move one helper into each sparse factor.

        No gate, projection, truncation or noise location. This avoids splitting
        a data factor into 2**ports pieces for data-controlled parity CXs.
        Destructive measurement later removes the helper from the factor.
        """
        q=self.basis_labels.index(label)
        rows=[]
        for (word,fid),c in self.terms.items():
            f=self.store.factors[fid]
            if len(f.labels)>=32:raise ValueError("Sparse-factor coordinate capacity exceeded")
            indices=f.indices | np.uint32(((word >> q)&1) << len(f.labels))
            new,phase=self.store.intern(f.labels+(label,),indices,f.phases)
            rest=(word & ((1 << q)-1)) | ((word >> (q+1)) << q)
            rows.append((rest,new,c*phase))
        self.basis_labels.remove(label)
        self.combine(rows)

    def gate(self,op,*targets):
        basis_pos = {q:j for j,q in enumerate(self.basis_labels)}
        rows = []
        for (word,fid),c in self.terms.items():
            if op == "CX":
                control,target = targets
                if control in basis_pos:
                    if word >> basis_pos[control] & 1:
                        if target in basis_pos:
                            word ^= 1 << basis_pos[target]
                        else:
                            fid,scale = self.store.action(fid,"X",(target,))
                            c *= scale
                elif target not in basis_pos:
                    fid,scale = self.store.action(fid,op,targets)
                    c *= scale
                else:
                    for bit in (0,1):
                        f,s = self.store.project(fid,control,bit,remove=False)
                        if f is not None:
                            rows.append((word ^ (bit << basis_pos[target]),f,c*s))
                    continue
            elif targets[0] in basis_pos:
                q = basis_pos[targets[0]]
                bit = (word >> q) & 1
                if op == "H":
                    low = word & ~(1 << q)
                    rows.extend(((low,fid,c),(low | (1 << q),fid,c*(-1 if bit else 1))))
                    continue
                if op in ("X","Y"):
                    word ^= 1 << q
                exponent = {"X":0,"Y":2+4*bit,"Z":4*bit,"S":2*bit,"SDG":6*bit,"T":bit,"TDG":7*bit}[op]
                c *= C8.phase(exponent)
            else:
                fid,scale = self.store.action(fid,op,targets)
                c *= scale
            rows.append((word,fid,c))
        self.combine(rows)

    def norm(self,terms=None):
        groups = defaultdict(list)
        for (word,fid),c in (self.terms if terms is None else terms).items():
            groups[word].append((fid,c))
        result = ZERO
        for values in groups.values():
            for j,(fid,c) in enumerate(values):
                result += c.conj()*c*len(self.store.factors[fid].indices)
                for other,d in values[j+1:]:
                    v = c.conj()*d*self.store.overlap(fid,other)
                    result += v+v.conj()
        if result[2] or result[3] != -result[1]:
            raise ArithmeticError("Non-real coherent norm")
        return result

    def measurement_branch(self,label,bit):
        rows = []
        if label in self.basis_labels:
            q = self.basis_labels.index(label)
            for (word,fid),c in self.terms.items():
                if (word >> q) & 1 == bit:
                    rows.append(((word & ((1 << q)-1)) | ((word >> (q+1)) << q),fid,c))
        else:
            for (word,fid),c in self.terms.items():
                f,s = self.store.project(fid,label,bit)
                if f is not None:
                    rows.append((word,f,c*s))
        out = {}
        for word,f,c in rows:
            key = word,f
            value = out.get(key,ZERO)+c
            if value:
                out[key] = value
            else:
                out.pop(key,None)
        return out

    def measure_z(self,label,rng):
        branches = [self.measurement_branch(label,bit) for bit in (0,1)]
        norms = [self.norm(branch) if branch else ZERO for branch in branches]
        if not norms[0] and not norms[1]:
            raise ArithmeticError("Both Born branches vanished")
        if not norms[0]:
            bit,p1 = 1,1.0
        elif not norms[1]:
            bit,p1 = 0,0.0
        elif not norms[0][1] and not norms[1][1]:
            p = Fraction(norms[1][0],norms[0][0]+norms[1][0])
            bit,p1 = int(rng.randrange(p.denominator) < p.numerator),float(p)
        else:
            total=norms[0]+norms[1]
            if norms[0].real_sign()<=0 or norms[1].real_sign()<=0:
                raise ArithmeticError("Negative algebraic Born norm")
            bits=128
            uniform=rng.getrandbits(bits)
            while True:
                lower=(norms[1]*(1 << bits)-total*uniform).real_sign()
                upper=(norms[1]*(1 << bits)-total*(uniform+1)).real_sign()
                if lower<=0:
                    bit=0;break
                if upper>=0:
                    bit=1;break
                uniform=(uniform << 64)|rng.getrandbits(64)
                bits+=64
            with localcontext() as ctx:
                ctx.prec = 100
                p = norms[1].decimal_real()/(norms[0]+norms[1]).decimal_real()
                if not 0 <= p <= 1:
                    raise ArithmeticError("Invalid algebraic Born probability")
                p1=float(p)  # display only; never used to choose the branch
        if label in self.basis_labels:
            self.basis_labels.remove(label)
        self.combine(((w,f,c) for (w,f),c in branches[bit].items()),reduce_common=True)
        self.store.collect(f for w,f in self.terms)
        return bit,{"probability_one":p1,"norms_zeta8":[list(n) for n in norms]}

    def sparse_output(self,expected_labels):
        if self.basis_labels or self.store.factors[next(iter(self.terms))[1]].labels != tuple(expected_labels):
            raise ValueError("Output has the wrong live quantum registers")
        amplitudes = {}
        for (word,fid),c in self.terms.items():
            f = self.store.factors[fid]
            for index,p in zip(f.indices,f.phases):
                key = int(index)
                amplitudes[key] = amplitudes.get(key,ZERO)+c*C8.phase(int(p))
        amplitudes = {w:c for w,c in amplitudes.items() if c}
        indices = np.array(sorted(amplitudes),dtype=np.uint32)
        exact_norm=sum((c.conj()*c for c in amplitudes.values()),ZERO)
        if exact_norm.real_sign()<=0:
            raise ArithmeticError("Invalid exact output norm")
        # Normalize BEFORE double conversion, avoiding cancellation of large
        # cyclotomic coefficients or underflow of a globally tiny ket.
        bits=max((abs(v).bit_length() for c in amplitudes.values() for v in c),default=1)
        converted=[]
        with localcontext() as ctx:
            ctx.prec=max(100,int(bits*.61)+100)
            invsqrt2=1/Decimal(2).sqrt()
            scale=exact_norm.decimal_real().sqrt()
            for index in indices:
                a,b,c,d=map(Decimal,amplitudes[int(index)])
                converted.append(complex(float((a+(b-d)*invsqrt2)/scale),
                                         float((c+(b+d)*invsqrt2)/scale)))
        values = np.array(converted,dtype=np.complex128)
        norm = float(np.vdot(values,values).real)
        if not np.isfinite(norm) or norm <= 0:
            raise ArithmeticError("Invalid diagnostic conversion norm")
        return indices,values/np.sqrt(norm)

    def compress_css(self,min_terms=64):
        """Exact change of representation, NOT measurement or recovery.

        Expand every helper-conditioned data ket in the complete CSS syndrome /
        logical computational stabilizer basis. Walsh inversion is an identity
        on the FULL 20-qubit Hilbert space; no syndrome or amplitude is dropped.
        Use the result only if it has fewer coherent terms. The common 1/512
        scalar can be omitted from an unnormalized ket. All amplitudes remain C8.
        """
        if len(self.terms)<min_terms or len(self.store.factors[next(iter(self.terms))[1]].labels)!=20:
            return
        from single_cz_diagnostics import coordinates,solve,X0,X1,Z0,Z1
        from single_cz_recovery import syndrome_component
        groups=defaultdict(dict)
        labels=self.store.factors[next(iter(self.terms))[1]].labels
        for (word,fid),c in self.terms.items():
            f=self.store.factors[fid]
            for index,phase in zip(f.indices,f.phases):
                w=int(index)
                value=groups[word].get(w,ZERO)+c.rotate(int(phase))
                if value:groups[word][w]=value
                else:groups[word].pop(w,None)
        coord=coordinates()
        logical_x=(0,X0,X1,X0^X1)
        vectors={}
        for helper,amps in groups.items():
            for w,c in amps.items():
                zs=syndrome_component(w)
                shifted=w^solve(zs)
                logical=((shifted&Z0).bit_count()%2)|(((shifted&Z1).bit_count()%2)<<1)
                h=coord[shifted^logical_x[logical]]
                key=helper,zs,logical
                if key not in vectors:vectors[key]=[ZERO]*512
                vectors[key][h] += c
        candidates=[]
        for (helper,zs,logical),vector in vectors.items():
            step=1
            while step<512:
                for start in range(0,512,2*step):
                    for j in range(start,start+step):
                        a,b=vector[j],vector[j+step]
                        vector[j],vector[j+step]=a+b,a-b
                step*=2
            for xs,c in enumerate(vector):
                if c:candidates.append((helper,zs,logical,xs,c))
        if len(candidates)>=len(self.terms):return
        hs=np.zeros(512,dtype=np.uint32)
        for h,u in coord.items():hs[u]=h
        parity=np.array([u.bit_count()%2 for u in range(512)],dtype=np.uint8)
        us=np.arange(512)
        rows=[]
        for helper,zs,logical,xs,c in candidates:
            fid,phase=self.store.intern(labels,hs^solve(zs)^logical_x[logical],
                                        4*parity[us&xs])
            rows.append((helper,fid,c*phase))
        self.combine(rows,reduce_common=True)
        self.store.collect(fid for helper,fid in self.terms)
        self.css_compressions+=1
