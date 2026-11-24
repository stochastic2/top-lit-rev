"""Round-trip joint recovery off/on versus the genuine GHZ20 cat baseline.

Uses the shared reorganized benchmark driver and supplies its comparison mode.
All noise, worker, seed, graph, recovery-cap and output options are shared.
"""
import sys
from benchmark_single_cz_graph_z_frame import main

if __name__=='__main__':
    sys.argv += ['--comparison','joint-data']
    main()
