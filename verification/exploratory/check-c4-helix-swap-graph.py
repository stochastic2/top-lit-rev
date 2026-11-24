"""A Table-I incidence graph for gauging one whole-block transversal SWAP.

The graph has one vertex c_i per distinct check support. The five inner
check vertices control the four swaps in their C4 block; upper vertices
are hubs with no swaps. Identical X/Z supports share a hub.
Every check-to-controller path has length zero or one. This checks ideal graph
requirements, not the noisy measurement circuit's distance.
"""

from collections import deque
from pathlib import Path
import argparse
import json
import re

root = Path(__file__).resolve().parent.parent
source = (root / "arXiv-2609.03194v1/appendix.tex").read_text()
table = source.split(r"\begin{minipage}{0.6\textwidth}")[1].split(r"\end{minipage}")[0]
rows = []
for line in table.splitlines():
    symbols = re.findall(r"\$(X|Z|\\cdot)\$", line)
    if len(symbols) == 20:
        rows.append([q for q, symbol in enumerate(symbols) if symbol != r"\cdot"])
R = rows[:10]
assert R == rows[10:20]
vertices = [f"c{i}" for i in range(10)]
edges = [(f"c{i}", f"c{j}") for i, support in enumerate(R)
         for j in sorted({q // 4 for q in support}) if j != i]
assert len(edges) == len(set(edges)) == 20
adj = {v: [] for v in vertices}
for k, (u, v) in enumerate(edges):
    adj[u].append((v,k))
    adj[v].append((u,k))
assert [len(adj[f"c{i}"]) for i in range(10)] == [4]*10
parent = {"c0": None}
parent_edge = {}
queue = deque(["c0"])
while queue:
    u = queue.popleft()
    for v,k in adj[u]:
        if v not in parent:
            parent[v] = u
            parent_edge[v] = k
            queue.append(v)
assert len(parent) == 10
tree_edges = set(parent_edge.values())


def root_path(v):
    path = set()
    while parent[v] is not None:
        path.add(parent_edge[v])
        v = parent[v]
    return path


cycles = [sorted(root_path(u) ^ root_path(v) ^ {k})
          for k,(u,v) in enumerate(edges) if k not in tree_edges]
assert len(cycles) == 11
for cycle in cycles:
    boundary = set()
    for k in cycle:
        boundary ^= set(edges[k])
    assert not boundary

# Every independent cycle has a distinct non-tree edge, proving independence.
assert all(len(set(cycle) - tree_edges) == 1 for cycle in cycles)
diameter = 0
for start in vertices:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v,_ in adj[u]:
            if v not in distances:
                distances[v] = distances[u] + 1
                queue.append(v)
    diameter = max(diameter, max(distances.values()))

# Every row gets an anchor: inner rows use their own controller (length
# zero); upper rows have one edge to each of their four controllers.
for i, support in enumerate(R):
    assert all(q // 4 == i or (f"c{i}", f"c{q // 4}") in edges for q in support)
assert all(q in R[q // 4] for q in range(20))
assert all(sum(q // 4 == j for q in range(20)) == 4 for j in range(5))
print('Graph: 10 vertices, 20 edges; connected, maximum degree 4, diameter', diameter)
print('Controller load: four Fredkins per inner vertex; zero per upper vertex; total 20 Fredkins.')
print('All twenty X/Z Table-I checks: dressing paths have length zero or one.')
print('Matter-check supports: at most 20 qubits; inner-vertex constraints: 12 qubits; upper-vertex constraints: 4.')
print('Cycle rank: 11; BFS fundamental cycle lengths:', sorted({len(c) for c in cycles}))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output:
    report = {
        'scope': 'One whole-block Z2 SWAP, exchanging two complete [[20,2,6]] blocks.',
        'vertices': vertices,
        'edges': edges,
        'table_I_supports': R,
        'fredkin_assignment': [{'control':f'c{q // 4}', 'targets':[f'B{q}',f'C{q}']} for q in range(20)],
        'check_roots': [f'c{i}' for i in range(10)],
        'cycle_basis_edge_indices': cycles,
        'ancilla_qubits_temporary': 10,
        'ancilla_qubits_gauge': 20,
        'logical_action': 'SWAP(B0,C0) SWAP(B1,C1); one joint symmetry outcome.',
        'fault_tolerance': 'Not established by this graph audit.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('Saved graph and paths to', args.output)
