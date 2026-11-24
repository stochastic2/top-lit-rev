"""Local-Gauss recovery ablation, shared cat optimization and direct control.

Blind and joint gauging arms have identical quantum fallback diagnostics; the blind
decoder deliberately ignores graph cycle information. Genuine cat gets
the same dual-basis conditional-gadget optimization, without a fictitious
used-root flag mechanism. Direct global flagged CZ has its own control.
"""
from benchmark_single_cz_graph_stars import main

ARMS=(("gauging-reject","gauging","bare","screen","compact_flags","round_trip",None,"dual_flags","reject"),
      ("gauging-blind","gauging","bare","screen","compact_flags","round_trip",None,"dual_flags","data"),
      ("gauging-joint","gauging","bare","screen","compact_flags","round_trip",None,"dual_flags","joint"),
      ("cat-legacy","cat","flags","certified","compact_flags","round_trip",None,"legacy","reject"),
      ("cat-dual","cat","flags","certified","compact_flags","round_trip",None,"dual_flags","reject"),
      ("direct-reject","direct_flags","flags","certified","compact_flags","round_trip",None,"dual_flags","reject"),
      ("direct-recover","direct_flags","flags","certified","compact_flags","round_trip",None,"dual_flags","data"))

if __name__=="__main__":main(ARMS,__doc__,"Local-Gauss graph-assisted root recovery")
