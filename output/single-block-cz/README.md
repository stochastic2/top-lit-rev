# Single-block CZ factory: reproducible verification bundle

Start with [the integrated procedure](../../notes/full_procedure_single_block_cz.md)
and [its proof](../../notes/full_procedure_single_block_cz_proof.md).
The construction is conservative and postselected. The original two-block
SWAP files are not modified.

The current simulator default instead uses
[flagged verification](../../notes/single_block_cz_flagged_verification_proof.md)
throughout: one syndrome ancilla and up to three live flags, without
separately prepared verification cats. The conservative certificates below
remain available; `recovery-resources.json` contains current default counts.

From `/Users/kevinhemery/quanti/top-order-lit-rev`:

```sh
python3 -B src/check_single_block_cz.py
python3 -B src/check_single_cz_graph_parity.py --output output/single-cz-graph-parity-certificates.json
python3 -B src/check_single_block_cz_cyclotomic.py
python3 -B src/run_single_block_cz_controller.py --control-flow-check
python3 -B src/c4_helix_single_block_cz.py \
  --schedule output/single-block-cz/schedule-zero-record.json
MPLCONFIGDIR=/private/tmp/c4-cz-mpl \
  /Users/kevinhemery/pytket-venv/bin/python -B notes/build-single-block-cz.py
```

All mathematical verification and gate-list accounting use the Python
standard library. Figure generation alone needs matplotlib. The separate
[simulation guide](../../src/SINGLE_BLOCK_CZ_SIMULATION.md) covers the
exact coherent noisy backend and the less rejecting recovery profile.

Graph preparation now uses three direct Z-parity scans with one helper.
It verifies the rank-32 cut subspace; graph phases remain unrestricted.
No verification cats or preparation-stage K_v checks are used. The
updated C3 proof explains why later combined Gauss certification suffices.

- `certificates.json`: authoritative-code comparison, ranks, source state,
  signed logical phases, all 655360 fixed-two-block Paulis, all 1771
  physical-radius-two errors, graph properties and Clifford cat audits.
- `physical-recovery-table.json`: 1726 syndrome classes with [X mask,Z mask]
  correction representatives, physical qubit q in integer bit q.
  **Syndrome convention:** Z-check bits 0–8, X-check bits 9–17.
- `edge-decisions.json`: array indexed by every 13-bit reported edge word;
  value is root-zero eta (vertex a in bit 0), or -1 for rejection.
- `ideal-records.json`: all 512 bare vertex/edge records, including both
  genuine sectors, measurement probabilities and all three phase conventions
  (bare correction, vertex Gauss frame, physical S/X byproduct).
- `cyclotomic.json`: exact Q(zeta8) identities and controlled-W port faults.
  Per sign: 27 single Pauli-basis faults, 234 pairs on distinct local
  locations, including control idles. Also verifies all 64 input/readout
  pairs in each of two mixed three-port check circuits.
- `controller.json`: record-driven execution agrees with the separate clean
  builder, including nonzero source/vertex/edge feedback, unused-cat retry,
  negative rejection and the two-report-fault Gauss history. The record
  backend is a classical control check, not quantum simulation.
- `resources.json`: counts elementary locations, helper peaks, explicit
  serial idle convention and a loose bounded-retry operation envelope.
- `recovery-resources.json`: current simulator clean counts, including
  both graphs/profiles and stage-by-stage accounting from actual gate lists.
- `recovery-resources-cats.json`: retained cat-extraction comparison.
- `recovery-resources-decoded-source.json`: flagged checks with the earlier
  small grouped/decoded known-source gadget (2809 CX on compact13).
- `cat-baseline-resources.json`: genuine twenty-leaf-cat CZ measurement
  with matched current source and Pauli checks (2124 CX, 120 T/T†).
- `ideal-cost.json`: exact zero-noise repeat-until-success costs, including
  early negative-attempt disposal. These are not noisy yield estimates.
- `schedule-zero-record.json`: full elementary accepted-path list, including
  boundary markers. During each operation, each other live qubit has one
  separate idle. A boundary means an idle on every live qubit.

The **analytical** theorem covers arbitrary local faults at up to two
locations globally, including all preparation, T/CX/T† pieces, reports,
corrections, resets, retries and idles. A clean gauged reference certifies
the positive resource; a clean terminal reference removes inherited errors
on two inner blocks; later faults leave the correctable weight-two span.

The certificates are exhaustive only in their named finite domains.
They do not enumerate pairs of locations in the entire factory, and do
not justify treating T-containing propagation as Pauli XOR. Coherent
coefficients are kept in the exact matrix audit and the proof uses an
operator-span composition argument.

Accepted conservative clean attempt: 8724 CX, 256 T/T†, mean 2712 one-qubit
Cliffords, 4399 preparations, 4379 measurements, peak 44 live physical qubits.
The equally protected direct-cat construction uses 5780 CX, 120 T/T†,
1712 one-qubit Cliffords and peak 41 qubits. Ideal acceptance is 3/4
for both. The default flagged recovery uses 3217 clean CX, 256 T/T†,
1172 preparations, 1152 measurements and 39 peak qubits on compact13.
Its direct flagged comparator uses 1965 CX and 24 peak qubits. The previous
cat-recovery mode remains at 4810 CX. Saved pilots are reported separately
from exact clean counts; the strict-flag pilot did not show an acceptance boost.
