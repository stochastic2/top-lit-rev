"""Compare certified terminal history, ordered terminal screen, and genuine cat.

Both gauging arms use bare stars and the same flag-dependent data recovery.
All noise channels and counts are supplied by the shared comparison runner.
"""
from benchmark_single_cz_graph_stars import main as shared_main,analyze as shared_analyze

ARMS=(("gauging-certified","gauging","bare","certified"),
      ("gauging-screen","gauging","bare","screen"),
      ("cat-data","cat","flags","certified"))


def analyze(directory):
    return shared_analyze(directory,ARMS,"Ordered terminal-screen comparison")


if __name__=="__main__":
    shared_main(ARMS,__doc__,"Ordered terminal-screen comparison")
