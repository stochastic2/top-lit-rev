# Joint graph/data recovery in the existing circuit

This adds an **optional recovery branch** to the round-trip, local-Gauss
circuit. Enable `--joint-recovery fallback`. It changes neither the graph
nor successful baseline paths. The default remains `--joint-recovery off`
for comparison. Persistent, cat, and two-block SWAP schedules are retained.

Start with the [local-Gauss procedure](../current/single_block_cz_graph_assisted_root_recovery.md).
Its existing `--root-recovery joint` uses graph information after a **root
flag**. This new option uses graph information after an **ambiguous
ordinary data syndrome**. Both can be enabled together. The
[companion proof](single_block_cz_joint_graph_data_recovery_proof.md)
states the extension theorem and scope of the finite verification.

## What the graph tells us

The eighteen data checks alone cannot always distinguish two unknown
inner-block errors. In V coordinates, an X on tree edge (a,v) is accompanied
by an operator on data block v. Its cycle syndrome restricts possible
data blocks. The decoder considers **all** compatible explanations with
zero, one or two global faults. A cycle value is not an infallible block
label: a second fault can alter it, and bare-star hooks can affect several
edges. Graph phase errors are unrestricted. Accept only when every
compatible data Pauli has one common class modulo code stabilizers.

For compact13, an actual fault X(A0) immediately after `CX(A0,D5)` in
the first `coordinates/V` pass gives a useful example:

* The protected data syndrome is 320: bits 6 and 8 are negative, where
  bits 0..8 are Z checks and 9..17 are X checks.
* The old data table has four logical classes and rejects.
* Certified cycle syndrome 71 (bits 0,1,2,6) leaves one common class
  across all compatible two-fault families. Apply X(D4) X(D5), then
  the non-tree graph-X correction for that cycle vector.
* Existing star repairs and local root measurements resume. Quantum
  regression seed 2 accepts with decoded target fidelity one.

Cycle zero with the same data syndrome remains ambiguous and rejects.
The decoder never guesses the most probable logical class to gain yield.

## Exact conditional circuit

The ordinary round is unchanged until its protected data recovery would
reject `data_ambiguity`. The selected eighteen-bit syndrome must be
nonzero. A fault-free attempt has all eighteen checks positive in V
coordinates, so at least one global fault has already occurred. At most
one remains in the following conditional work.

1. Stay in V coordinates; add no coordinate pass. Keep the unknown data.
2. Measure a complete record: eighteen bare code stabilizers in existing
   Z-then-X support order, followed by all independent cycle-Z checks in
   graph order. Apply **no corrections between complete records**.
3. Use the existing one-remaining-fault data gadgets. With
   `--conditional-checks dual_flags`, their executable programs are
   `dual_single_fault_pauli_program(axis,n)` in
   `src/single_block_cz/single_cz_flagged.py`. For X: prepare s in plus,
   f in zero; apply CX(s,Dq) in support order, with CX(s,f) after ports
   0 and n-2; read f in Z, s in X. For Z: prepare s in zero, f in plus;
   use CX(Dq,s) and CX(f,s) at the same positions; read f in X, s in Z.
   X readout means H followed by destructive MZ. Finish both helper
   readouts before acting on their reports. **Any new flag rejects.**
4. For each cycle C: prepare w in zero, apply CX(Ae,w) in its listed
   cycle order, then destructive MZ(w). This measures Z(C), without a
   helper cat or flag. Freshly prepare the helper before each use.
5. Stop at the first two equal consecutive **complete** records, within
   four records. Reject if none match. Actual outcomes and noisy reports
   remain separate in the runtime; the controller uses reported bits.
   This history contains only globally commuting Paulis.
6. Decode data and cycles jointly. Reject absent or ambiguous entries.
   Apply the chosen data Pauli as individually noisy X/Y/Z gates. Solve
   the cycle equations with all tree columns fixed to zero; apply X on
   the resulting non-tree edges. These graph corrections commute with V.
7. Increment the data epoch, then continue the same round's four nonroot
   stars and sign repairs, V return and four-data local root Gauss check.
   Star signs did not narrow data classes; arbitrary graph Z remains
   allowed and the existing star step restores its signs.

The original three positive complete rounds within five, terminal cycle
flattening, cut decoding, physical byproducts and terminal screen remain.
The fallback itself supplies no positive CZ vote. A genuine negative
branch is still rejected; its sign is not repaired into magic. Unknown
data are never reset and source logical X is never measured again.

There is at most one joint branch per gauged round, hence five per attempt,
each with at most four records. Existing bounded resource retries and
the configured flag-recovery cap remain, sharing the same global fault
budget. This first version does not rescue absent data rows, terminal
ambiguities or ambiguous **flag-dependent** data recoveries.

## Costs

These counts use decoded source extraction, compact ordinary data checks,
bare graph stars, terminal screen, dual conditional checks and joint root
recovery. Controlled-W is physically T/CX/Tdg, never an atomic location.
The clean ledger uses zero reports; measurement-dependent sign/byproduct
gates are additional in executed-shot counts, even without noise.

| Method | Clean CX | T/Tdg | One-qubit Clifford | Peak live qubits |
|---|---:|---:|---:|---:|
| Round-trip compact13, joint off or fallback | 1,889 | 256 | 803 | 39 |
| Round-trip current20, joint off or fallback | 2,059 | 256 | 803 | 46 |
| Genuine GHZ20-cat comparator | 1,476 | 120 | 686 | 41 |

One conditional data record is 140 CX, 36 H, 36 preparations and 36 MZ.
Compact13 adds 25 CX and nine preparations/MZ for cycles; current20 adds
38 CX and sixteen preparations/MZ. The **minimum added** branch cost,
beyond the already acquired protected data history, is:

| Graph | Two complete records: CX | H | Preparations / MZ | Extra T |
|---|---:|---:|---:|---:|---:|
| compact13 | 330 | 72 | 90 / 90 | 0 |
| current20 | 356 | 72 | 104 / 104 | 0 |

Four records double those diagnostic costs. Record-dependent corrections
and waiting idles are additional and counted. No extra simultaneous
helper is needed. This saves no clean gates: it spends bounded extra work
on otherwise rejected attempts.

Old accepted paths see the same quantum operations and random draws, so
their acceptance and output are preserved at the same seed, subject to
capacity/timeout limits. Newly continued paths can encounter more noise,
rejection or capacity limits. Table sizes are not probabilities and do
not establish a population yield or matched-fidelity cost advantage.

## Reproduce and benchmark

The reorganized driver supplies all flat-import paths. Fish-compatible
command, with genuine GHZ20 as the third arm:

```sh
/Users/kevinhemery/pytket-venv/bin/python /Users/kevinhemery/quanti/top-order-lit-rev/benchmarks/single_block_cz/benchmark_single_cz_joint_recovery.py \
    --shots 200 --seed 1000 --workers 2 \
    --graph compact13 --max-flag-recoveries 8 \
    --two-qubit-infidelity 1e-3 --readout-flip-probability 1e-3 \
    --one-qubit-infidelity 1e-4 --t-infidelity 1e-4 \
    --output-dir /Users/kevinhemery/quanti/top-order-lit-rev/output/cz-joint-graph-data-200-20261119
```

Use a new output directory each time. Compare `joint-off`, `joint-fallback`
and `cat-dual` in `comparison.md`. Per-arm summaries report joint episodes,
successful joint recoveries, acceptance after joint recovery and executed
gate costs including rejected attempts. Gauging arms agree until the first
otherwise-rejecting ambiguity; cat has a different trajectory at the same
seed. `pairing.json` lists same-seed gained/lost acceptances among completed
pairs, excluding unresolved attempts.

Finite certificate, without environment setup:

```sh
/Users/kevinhemery/pytket-venv/bin/python /Users/kevinhemery/quanti/top-order-lit-rev/verification/single_block_cz/check_single_cz_joint_recovery.py
```

It saves `output/single-cz-joint-recovery-certificates.json`, distinguishing
finite class checks from analytical composition. Decoder source:
`src/single_block_cz/single_cz_joint_recovery.py`; controller integration:
`src/single_block_cz/single_cz_controller.py`; quantum regressions:
`tests/single_block_cz/test_single_cz_joint_recovery.py`.
