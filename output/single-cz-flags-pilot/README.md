# Flagged verification pilot: no separately prepared verification cats

Default recovery mode: `--verification-extraction flags`, source
`rolling_flags`. Product checks use one syndrome ancilla and at most
three live flags; uniform weight-four Pauli checks use one flag.
Cycle Z checks and resource Z checks use direct parity meters.
Small flags are temporarily entangled. No large cat preparation or cat
verification scan is executed, and there is no cat fallback.

| Graph | Clean CX | T/T† | Peak qubits | Accepted / attempts | Target matches |
|---|---:|---:|---:|---:|---:|
| compact13 | 3217 | 256 | 39 | 2 / 16 | 2 / 2 |
| current20 | 3459 | 256 | 46 | 2 / 16 | 2 / 2 |

Both runs use average CX infidelity r2=1e-3 and independent report flips
q=1e-3. Clifford, T, preparation and serial memory noise are explicitly
zero. No sampled-fault cap is imposed. All 32 attempts completed, with
no unresolved calculations. Born seeds are 0..15; noise seeds use the
documented independent hash rule. Manifests and runtime source snapshots
are immutable; all actual/reported outcomes and sampled errors are retained.

The observed acceptance is **12.5%**, with Wilson95 interval
[0.0350,0.3602]. The earlier cat-extraction pilot accepted 3/8 on each
graph, with different trajectories. Thus this implementation pilot does
**not** show an acceptance boost. Strict rejection on flags is the main
new bottleneck. All four accepted outputs matched the decoded target
within 1e-10, which does not establish the population output error rate.
Cost per nominal accepted output is 21127.5 / 23137 CX respectively;
these are small-sample values, not matched-fidelity cost claims.

Reverify saved report/control certificates and complex output diagnostics:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/compare_single_cz_runs.py \
  output/single-cz-flags-pilot
```

See the [primitive and composition proof](../../notes/single_block_cz_flagged_verification_proof.md),
[simulation guide](../../src/SINGLE_BLOCK_CZ_SIMULATION.md), and
[current/historical results](../../notes/single_block_cz_simulation_results.md).
The finite certificate covers the stated local support domains; it is
not a whole-factory fault-pair enumeration. The saved-run verifier is
not full elementary-gate replay.
