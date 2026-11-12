"""Matched four-arm compact Pauli-check comparison; user controls run length."""
from benchmark_single_cz_graph_stars import main

ARMS=(("gauging-rolling","gauging","bare","screen","rolling_flags"),
      ("gauging-compact","gauging","bare","screen","compact_flags"),
      ("cat-rolling","cat","flags","certified","rolling_flags"),
      ("cat-compact","cat","flags","certified","compact_flags"))

if __name__=="__main__":
    main(ARMS,__doc__,"Compact Pauli-data check comparison")
