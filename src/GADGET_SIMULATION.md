# Full C4-Helix gadgets and Pauli-fault experiments

This is a **separate implementation** from the noiseless sparse simulator.
It follows the physical circuits in
[`full_procedure_integrated_v2.md`](../notes/full_procedure_integrated_v2.md),
including the error-detection, filtering, and recovery gadgets. It uses
ordinary sparse basis amplitudes, integer arithmetic, and exact rational
Born probabilities. The earlier Guppy and sparse implementations are unchanged.

## Run a complete physical attempt

From the repository root:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_gadgets.py \
    --seed 1 --trace --output-dir output/my-gadget-run
```

Use a new output directory. The result is one attempt, which can accept or
reject. The output contains:

- `result.json`: reports, decoder decisions, recovery history, rejection
  reason if any, applied/unreached fault indices, and resource measurements.
- `events.jsonl`, when `--trace` is set: every physical preparation, H,
  CNOT, CZ, Fredkin, SWAP, correction, and Z meter, plus each completed
  check's leaf reports and parity. H and the following Z meter are separate
  fault locations, including when implementing an X measurement.
- `c_state.json`, only on acceptance: the unmeasured physical C state as
  explicit integer amplitudes and its squared normalization.

No early gauge measurement is used. The Gauss gadgets contain X on A,
so the earlier noiseless simulator's reordering is not valid here.

## What is actually executed

The check gadget in integrated V2 Section 4 measures an involution
\(Q=Q_0\cdots Q_{m-1}\), where each port is one X target, one Z target,
or one SWAP pair. The simulator executes:

1. Prepare m fresh leaves, apply H to leaf 0, and chain m-1 CNOTs.
2. Verify every adjacent leaf pair three times. Each verification prepares
   w in zero, applies two CNOTs into w, and measures w in Z. Require every
   **reported** raw bit to be zero.
3. Couple leaf j to its own port, using CNOT, CZ, or Fredkin.
4. Only after all couplings, measure every leaf in X as a physical H/Z pair.
5. Compute the XOR of the leaf reports. Require this parity to be zero for
   a positive check; individual leaf reports may be one.

The ideal equation is

\[
K_\lambda(Q)=2^{-(m+1)/2}(I+(-1)^y Q),
\qquad y=\sum_j\lambda_j\pmod2.
\]

This equation documents the ideal action. The implementation executes
the faulty physical gadget; it does not substitute this projector or
force a desired result. Failed cat verification rejects immediately.

The full attempt has the following stages:

| Stage | Implemented schedule |
|---|---|
| Source verification, Section 5 | B then C, three rounds of eighteen checks plus two known-state logical checks |
| Graph source, Section 6 | Five H gates, forty graph CNOTs; three positive rounds of 5 vertex and 20 edge checks |
| Enrichment, Section 7 | Twenty Fredkins, with the contiguous four-qubit block controllers |
| Vertex readout/frame, Section 8 | Five H gates, five Z meters, even **reported** parity, physical gauge-Z feedforward |
| Gauged checks, Sections 9--11 | Three rounds, each 18 paired, 16 cycle, and 5 Gauss gadgets |
| Ungauging, Sections 12--13 | Twenty physical gauge meters; unique distance-two cut decoding; ordinary correcting SWAPs |
| Original-code filtering, Section 14 | Three positive rounds of B-X, B-Z, C-X, C-Z, nine supports each |
| Recovery, Section 15 | Retain either sign, stop at the first three identical 36-bit reports, at most nine rounds; apply the selected physical Paulis |
| Logical extraction, Section 16 | Twenty B meters; correct up to two reported-bit flips before evaluating logical Z0 |

In particular, while gauged:

\[
N_s^P=S_{B,s}^P S_{C,s}^P,\quad
L_\eta=\prod_{q\in\eta}Z_{A_q},\quad
G_v=\left(\prod_{q\in E_v}X_{A_q}\right)T_v.
\]

One Gauss gadget has eight gauge-X ports followed by four data-SWAP ports.
It uses one twelve-leaf cat; all twelve X reports form **one** parity.
The full accepted no-fault schedule has 528 check gadgets, 80 Fredkins,
and at most 77 simultaneously live physical qubits.

### Two source-preparation modes

The default `--source-mode encoded` uses the H/CNOT encoder already in
the Guppy source, then executes all three source-verification rounds.
Integrated V2 Section 5 explicitly allows this unitary-preparation
alternative. Encoder gates are also injectable physical locations.
Its ideal total success is 5/8.

`--source-mode projected` instead implements the note's literal illustrative
source: reset the data to zero and execute the three positive source
families without an encoder. The ideal source-preparation probability
alone is \(2^{-19}\); most naturally sampled attempts reject early.
Its ideal total success is \(2^{-19}(5/8)\). It is available for studying
that precise schedule, not as an efficient way to generate many resources.
The tests replay a legal all-zero trajectory through this complete mode
and check its source probability relative to the encoded mode.

## Why the representation still fits in memory

Each data factor is an explicit sparse ket

\[
|f\rangle=\sum_x f(x)|x\rangle.
\]

The simulator stores the whole state as a coherent sum

\[
|\eta\rangle=\sum_{z,F}c_{z,F}|z\rangle
\bigotimes_{f\in F}|f\rangle.
\]

Here z contains explicit quantum basis values of the live vertices,
gauge qubits, and helpers. The factors carry physical data-coordinate
names, explicit bit-string dictionaries, and integer weights. The factors
of one term have disjoint coordinates. Different terms need not be
orthogonal. All terms are retained; z is never sampled by a gate.

The initial B and C factors have 512 and 1024 entries. A data SWAP
exchanges physical coordinate names on the factors instead of expanding
their full tensor product. Pauli gates permute or sign their explicit
amplitudes. Helper H gates expand the coherent sum; helper CNOTs and
controlled couplings act on each component's explicit control bit.

For the full state, probabilities use

\[
N=\langle\eta|\eta\rangle
=\sum_{z,F,F'}c_{z,F}c_{z,F'}
\left\langle\bigotimes_{f\in F}f\middle|
\bigotimes_{g\in F'}g\right\rangle.
\]

Matching physical factor partitions reduce the overlap to sparse dictionary
dot products. If a fault produces different partitions, a cached exact
product-enumeration fallback computes the overlap. It does not assume
orthogonality or discard interference. Identical product terms merge.

Z readout builds both projections and samples their exact norms. Integer
coefficient GCDs are removed only as a common state normalization; no
relative amplitude is changed. Literal raw-source projections are absorbed
back into a sparse source factor by adding their amplitudes explicitly.

This representation is not an affine-space or stabilizer-tableau backend.
It avoids the large flattened wavefunction while using the same explicit
sparse data amplitudes. NumPy/SciPy are used by the existing sparse-vector
exports and independent comparisons. The final C state is flattened only
after the other registers are measured.

Memoized factors and overlaps consume memory. Some fault patterns can
increase their number and make the exact fallback expensive. `--max-terms`
is a checked limit (default 4096): exceeding it raises an error instead
of truncating the state or pretending that a report rejected the attempt.

## Insert a concrete Pauli fault

For example, run a late C error that the recovery circuit must handle:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_gadgets.py \
    --seed 1 --faults src/gadget_fault_examples/late_c_x.json \
    --probes src/gadget_fault_examples/probes.json --trace \
    --output-dir output/my-late-x-run
```

The fault file contains:

```json
[
  {
    "location": "filter/round/2/C/Z/8/readout/7/measure",
    "when": "idle",
    "paulis": {"C_0": "X"}
  }
]
```

That location is the final cat-leaf meter of the last filter check.
C_0 is waiting, so the Pauli is inserted before this operation's serial
idle interval completes. It occurs after the last filtering interaction
that would detect it. In the demonstrated run:

1. The `filtered` probe reports \(\langle Z_{C_0}Z_{C_1}Z_{C_2}Z_{C_3}\rangle=-1\).
2. Recovery records the same nonzero C syndrome three times: C Z-checks
   s=0 and s=5 report one.
3. The decoder chooses X on C_0, executed at `recovery/correction/C/0`.
4. The `recovered` probe returns +1, and C is the expected encoded magic state.

The `--probes` file maps names to Pauli products. These are exact read-only
expectations at stage boundaries, not additional physical measurements.
An absent qubit makes a probe null, as with B after final readout.

### Fault timing and scope

| `when` | Meaning | Allowed targets |
|---|---|---|
| `after` (default) | Pauli product after the ideal preparation/gate | That operation's physical participants |
| `before` | Pauli product immediately before a gate or measurement | That operation's participants |
| `idle` | One Pauli on a waiting qubit before this serial operation | One live nonparticipant |
| `report` | Flip a classical report after the actual quantum measurement | No Pauli dictionary; use `flip_report: true` |

A three-qubit gate fault can contain a Pauli on any subset of its three
participants. A Y is applied as Y=iXZ; the real XZ action is carried by
the sparse weights and the common i phase is tracked in `global_i_power`.
Physical recovery Y is likewise one gate/event, not two fault locations.
Fredkins are atomic three-qubit locations in this implementation, as
permitted by the integrated note; faults inside a native Fredkin
decomposition would require expanding that operation into separate events.
Saved C states use a canonical overall phase, while the runtime retains
phase bookkeeping during the trajectory.

For an X measurement, the named `/H` gate and `/measure` meter are separate
locations. After a destructive meter, the qubit is gone; use `before` for
a quantum measurement error and `report` for a false reported bit.
Preparation faults use `after`.

The event stream supplies the exact location strings. Trace records include
actual and reported measurement bits separately. The decoders receive only
reported bits, never the actual bits, fault list, or a clean-round oracle.
The actual bits are diagnostic output for the human investigating the run.

All unused live qubits have implicit serial idle locations at every physical
event. They are not expanded into millions of redundant trace records:
the event's preparation/measurement history identifies the live set, and
its `targets` identify the participants. Use its same location with
`when: "idle"` to select one waiting qubit.

Feedforward gates that are not selected and later recovery rounds that
are not reached have no executed locations. `unreached_fault_indices`
reports requested faults that did not fire. Always inspect that field;
it can also identify a misspelled location. A fault is never silently
retargeted to the nearest gate.

### Additional supplied fault example

`gadget_fault_examples/vertex_report.json` flips the root vertex report.
With seed 0, the actual vertex parity is odd but the reported parity is
even. The classical selection passes, while the physical state still has
the negative SWAP sign. The first root Gauss gadget then rejects at
`gauged/round/0/gauss/a`. This tests actual Gauss enforcement, not just a
classical parity condition.

`gadget_fault_examples/cat_phase.json` applies Z to the first cat leaf
after its preparation H. Raw adjacent-ZZ verification passes, but the
measured check parity is reversed and the positive check rejects.

## Python API and read-only propagation probes

With `src` on the Python import path:

```python
from c4_helix_fault_runtime import PauliFault
from simulate_c4_helix_gadgets import GadgetSimulator

fault = PauliFault(
    location="filter/round/2/C/Z/8/readout/7/measure",
    paulis={"C_0": "X"},
    when="idle",
)
probes = {"C_inner_Z0": {f"C_{q}": "Z" for q in range(4)}}
result = GadgetSimulator(seed=1, faults=[fault], probes=probes).run()
print(result["recovery_decoding"])
print(result["probe_history"])
```

An optional `trace(event)` callback can stream events to a database or file.
An optional `observer(stage, runtime)` callback can inspect the compressed
state. `runtime.state.expectation_pauli({qubit: axis, ...})` computes an
exact expectation using coherent overlaps. Avoid flattening a gauged
state with `to_sparse()`; it has an explicit export limit.

## Validation and limits

Run:

```sh
"$HOME/pytket-venv/bin/python" -m pytest -q src/test_c4_helix_gadgets.py
```

The tests compare the sparse product sum against flattened exact states,
including incompatible factor partitions, physical Y phases, and coherent
SWAP projections. They exercise cat-bit, cat-phase, and report faults;
full late-X/Y/Z recovery; a false vertex report detected by Gauss; two
corrupt gauge reports decoded before SWAP correction; and the literal
raw-zero source mode through a complete legal measurement trajectory.

Saved demonstrations are in `output/c4-helix-gadgets-clean/`,
`output/c4-helix-gadgets-late-x/`, and
`output/c4-helix-gadgets-vertex-report/`. The original clean run completed
47,982 physical events in about 3.8 seconds and had about 636 MiB process
peak RSS on this machine, including memoized sparse factors. Performance
for other fault patterns can differ substantially.

An accepted faulty attempt can leave correctable physical errors on C,
as the integrated note explicitly allows. `physical_C_diagnostics` describes
that physical output; it does not insert an extra ideal final recovery.
The current experiments are explicit Pauli trajectories and report flips,
not arbitrary coherent gate errors, exhaustive fault-pair enumeration,
or a new proof of the note's global two-fault claim. More than two faults
can be explored, but that claim does not apply to them.
