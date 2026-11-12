# Saved implementation pilot

These are small execution/verification checks, not a statistically powered
graph ranking. See [interpretation and resource counts](../../notes/single_block_cz_simulation_results.md)
and the [simulation guide](../../src/SINGLE_BLOCK_CZ_SIMULATION.md).

| Run | Attempts | Accepted | Noise |
|---|---:|---:|---|
| compact13-recovery | 8 | 3 | r2=q=1e-3 |
| current20-recovery | 8 | 3 | r2=q=1e-3 |
| compact13-conservative | 4 | 0 | r2=q=1e-3 |
| current20-conservative | 4 | 0 | r2=q=1e-3 |
| direct-cat | 2 | 0 | r2=q=1e-3 |
| multichannel | 2 | 1 | All channels nonzero; see manifest |

The first five runs set one-qubit, T, preparation and memory noise to zero.
All 28 attempts completed without a capacity failure. Every diagnosed
acceptance matched the decoded target within 1e-10; seven such outputs
do not establish a population logical-error rate. Both conservative runs
stopped in source preparation, before the graph was used.

Each directory contains an immutable runtime source snapshot, the noise
model, seeds, elementary counts, actual/reported measurement records,
controller decisions, all sampled errors and accepted complex outputs.
The run manifest records the precise version and parameters. Snapshots
can be executed directly with Python and NumPy, using a new output
directory; no circuit reconstruction from these notes is needed.

Reverify all saved report/control certificates and output diagnostics
without resampling:

```sh
/Users/kevinhemery/pytket-venv/bin/python -B src/compare_single_cz_runs.py \
  output/single-cz-validated-pilot
```

`comparison.json` records the results and the verifier's limited scope:
it checks saved certificates and noise accounting, not full gate replay.
Earlier exploratory outputs outside this directory used different source
versions and are not pooled here.
