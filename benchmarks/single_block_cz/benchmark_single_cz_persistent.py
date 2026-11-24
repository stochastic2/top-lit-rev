"""Matched old / persistent compact13 / persistent tree4 / GHZ20 / direct flags.

Graphs are fixed per arm; source, extraction, noise and bounded recovery match.
No long campaign is launched automatically. Old shared-check modes remain.
"""
from benchmark_single_cz_graph_stars import main

ARMS=(("gauging-round-trip","gauging","bare","screen","compact_flags","round_trip","compact13"),
      ("gauging-persistent13","gauging","bare","intrinsic","compact_flags","persistent","compact13"),
      ("gauging-persistent4","gauging","bare","intrinsic","compact_flags","persistent","tree4"),
      ("cat-compact","cat","flags","certified","compact_flags","round_trip","compact13"),
      ("direct-flags","direct_flags","flags","certified","compact_flags","round_trip","compact13"))

if __name__=="__main__":main(ARMS,__doc__,"Persistent gauging coordinates comparison")
