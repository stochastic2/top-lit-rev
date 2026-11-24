"""One-block graph choices and report-only recovery; no quantum oracle.

Conventions: Z-check syndromes in bits 0..8, X-checks in 9..17.
The two-block decoder accepts only a UNIQUE stabilizer-equivalence class
over all ten possible pairs. It is not the old two-copy joint decoder.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
import c4_helix_single_block_cz as m


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


@dataclass(frozen=True)
class Graph:
    name: str
    edges: tuple
    cycles: tuple
    tree: tuple

    def cut(self,eta):
        return sum((((eta >> a) ^ (eta >> b)) & 1) << e for e,(a,b) in enumerate(self.edges))

    @property
    def distance(self):
        return min(self.cut(eta).bit_count() for eta in range(2,32,2))

    @property
    def radius(self):
        return (self.distance-1)//2

    def decode(self,word,radius=None):
        if not 0 <= word < 1 << len(self.edges):
            raise ValueError("Invalid edge word")
        r = self.radius if radius is None else radius
        if not 0 <= r <= self.radius:
            raise ValueError("Radius exceeds unique cut-decoding distance")
        candidates = [(eta,self.cut(eta)) for eta in range(0,32,2)
                      if (word ^ self.cut(eta)).bit_count() <= r]
        if len(candidates) != 1:
            return None
        eta,cut = candidates[0]
        return {"eta":eta,"corrected":cut,"report_error":word ^ cut,"radius":r}

    def validate(self):
        assert len(self.tree) == 4
        assert all(self.edges[e] == (0,v) for v,e in enumerate(self.tree,1))
        assert all(0 <= a < b < 5 for a,b in self.edges)
        cycles = list(map(m.mask,self.cycles))
        assert rank(cycles) == len(cycles) == len(self.edges)-4
        assert all((self.cut(eta)&c).bit_count()%2 == 0 for eta in range(32) for c in cycles)
        assert self.distance >= 5


COMPACT13 = Graph("compact13",m.EDGES,m.CYCLES,m.TREE)
CURRENT20 = Graph("current20",((0,4),(2,4),(2,3),(0,3),(1,4),(3,4),(0,3),(0,1),(1,2),(1,4),
                              (0,4),(0,2),(0,2),(2,3),(1,3),(0,1),(1,3),(3,4),(2,4),(1,2)),
                  ((7,15),(11,12),(3,6),(0,10),(8,19),(14,16),(4,9),(2,13),
                   (1,18),(5,17),(7,8,11),(7,14,3),(7,4,0),(11,2,3),(11,1,0),(3,5,0)),
                  (7,11,3,0))
GRAPHS = {g.name:g for g in (COMPACT13,CURRENT20)}

H = tuple(map(m.mask,m.SUPPORTS))
STABILIZERS = {0}
for h in H:
    STABILIZERS |= {w ^ h for w in tuple(STABILIZERS)}
REDUCTION = sorted(H,reverse=True)
# RREF basis for quotient class comparisons.
_pivots = {}
for row in H:
    while row:
        p = row.bit_length()-1
        if p in _pivots:
            row ^= _pivots[p]
        else:
            _pivots[p] = row
            break


def remainder(word):
    for p,h in sorted(_pivots.items(),reverse=True):
        if word >> p & 1:
            word ^= h
    return word


@lru_cache(maxsize=None)
def syndrome_component(w):
    return sum(((w & h).bit_count()%2) << j for j,h in enumerate(H))


def syndrome(x,z):
    return syndrome_component(x) | (syndrome_component(z) << 9)


@lru_cache(maxsize=1)
def data_table():
    local = {}
    for x,z in product(range(16),repeat=2):
        key = x ^ (15 if x & 8 else 0),z ^ (15 if z & 8 else 0)
        if key not in local or ((x|z).bit_count(),x,z) < ((local[key][0]|local[key][1]).bit_count(),*local[key]):
            local[key] = x,z
    table,classes = {},{}
    for a,b in combinations(range(5),2):
        for (xa,za),(xb,zb) in product(local.values(),repeat=2):
            x,z = (xa << (4*a)) | (xb << (4*b)),(za << (4*a)) | (zb << (4*b))
            s = syndrome(x,z)
            cls = remainder(x),remainder(z)
            classes.setdefault(s,set()).add(cls)
            if s not in table or ((x|z).bit_count(),x,z) < ((table[s][0]|table[s][1]).bit_count(),*table[s]):
                table[s] = x,z
    return {s:{"correction":table[s] if len(c)==1 else None,"classes":len(c)} for s,c in classes.items()}


@lru_cache(maxsize=1)
def physical_table():
    table = {}
    for w in range(3):
        for sites in combinations(range(20),w):
            for axes in product(range(1,4),repeat=w):
                x = sum((p&1) << q for p,q in zip(axes,sites))
                z = sum((p>>1) << q for p,q in zip(axes,sites))
                table.setdefault(syndrome(x,z),(x,z))
    return table


@lru_cache(maxsize=None)
def cycle_table(graph):
    table = {}
    for w in range(graph.radius+1):
        for sites in combinations(range(len(graph.edges)),w):
            pattern = m.mask(sites)
            s = tuple((pattern & m.mask(c)).bit_count()%2 for c in graph.cycles)
            if s in table:
                raise ArithmeticError("Ambiguous cycle correction")
            table[s] = sites
    return table


def pure_error(generators,bits,n):
    rows = [[z | (x << n),int(b)] for (x,z),b in zip(generators,bits)]
    used,pivots = 0,[]
    for col in range(2*n):
        found = next((j for j in range(used,len(rows)) if rows[j][0] >> col & 1),None)
        if found is None:
            continue
        rows[used],rows[found] = rows[found],rows[used]
        for j in range(len(rows)):
            if j != used and rows[j][0] >> col & 1:
                rows[j] = [rows[j][0]^rows[used][0],rows[j][1]^rows[used][1]]
        pivots.append(col)
        used += 1
    if any(not row and b for row,b in rows):
        raise ValueError("Inconsistent syndrome")
    w = sum(rows[j][1] << col for j,col in enumerate(pivots))
    return w & ((1 << n)-1),w >> n


def clean_reference(records):
    """Old adaptive combinatorial lemma, used ONLY for commuting subfamilies."""
    records = tuple(map(tuple,records))
    changes = [j for j in range(len(records)-1) if records[j] != records[j+1]]
    covers = [set(c) for n in range(3) for c in combinations(range(len(records)),n)
              if all(j in c or j+1 in c for j in changes)]
    for report in dict.fromkeys(reversed(records)):
        occurrences = {j for j,row in enumerate(records) if row == report}
        if covers and all(not occurrences <= bad for bad in covers):
            return {"selected":max(occurrences),"occurrences":sorted(occurrences),
                    "bad_round_covers":[sorted(c) for c in covers],"change_edges":changes}
    return None
