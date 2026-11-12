# Actual GHZ20 CZ baseline: execution smoke checks

These are two **single-attempt execution checks**, not a benchmark or a
protocol ranking. The user will run the statistical comparison.

- `noiseless`: seed 0, zero CX/report noise, accepted; decoded fidelity one
  within tolerance. Executes three actual twenty-leaf cat measurements:
  2124 CX, 120 T/T†, 842 preparations, 822 readouts and 41 peak qubits.
  Its trace records every physical operation and measurement.
- `noisy`: seed 100, r2=q=1e-3, other channels zero. It rejected at a
  flagged terminal data check before the first CZ cat was prepared. It
  checks noise-channel/CLI/output execution, not noisy cat performance.

The unit tests separately inject a broad cat-preparation hook, a wrong
cat-leaf report and two late data errors. Saved snapshots contain the
new cat runner as well as the shared physical simulator. The read-only
verifier checks controller/report certificates and output diagnostics;
it is not full quantum gate replay.

See [matched benchmark commands and protocol details](../../src/SINGLE_BLOCK_CZ_CAT_BASELINE.md).
