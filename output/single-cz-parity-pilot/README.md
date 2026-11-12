# Direct Z-parity graph verification: saved implementation pilot

Current controller: three complete zero scans of
Z_(a_u) Z_(A_e) Z_(a_v), with one helper per check and resource-to-meter
CNOTs. Nonzero scans trigger a bounded local graph rebuild before enrichment.
No preparation-stage K_v measurement or verification cat remains.

See the [procedure](../../notes/full_procedure_single_block_cz.md),
[C3 proof](../../notes/full_procedure_single_block_cz_proof.md#c3-known-source-and-graph-verification),
[simulation guide](../../src/SINGLE_BLOCK_CZ_SIMULATION.md), and
[interpretation](../../notes/single_block_cz_simulation_results.md).

| Run | Attempts | Accepted | Target matches |
|---|---:|---:|---:|
| compact13-recovery | 8 | 3 | 2 |
| current20-recovery | 8 | 3 | 3 |

Rates: CX average infidelity 1e-3, report-flip probability 1e-3;
one-qubit, T, memory and preparation channels explicitly zero.
All sixteen attempts completed; no computational failures were counted
as rejections. The seed rule, limits, versions and actual runtime sources
are saved separately in each manifest and source_snapshot directory.

**Compact13 shot 7 is an accepted logical failure**, decoded |11>, with
23 sampled noise events. It is included in the summary, not discarded.
The two-fault theorem does not guarantee perfect outputs on trajectories
with more faults. This small pilot is not a graph ranking, a measured
population fidelity, or a matched-fidelity resource comparison.

Recompute all saved control/report certificates, noise accounting and
complex output diagnostics without resampling:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/compare_single_cz_runs.py \
  output/single-cz-parity-pilot
```

The verifier checks saved certificates and outputs; it does not replay
every elementary quantum gate. Earlier runs under single-cz-validated-pilot
use the previous cat-based graph verifier and remain unmodified.
