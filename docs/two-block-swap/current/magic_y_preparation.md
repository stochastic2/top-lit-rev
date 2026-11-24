# Gauging/ungauging preparation with both logical-Y outcomes retained

The simulator's new default is `--magic-output y`. It keeps the current
sources, graph, gauging, positive-SWAP certification, ungauging and recovery,
then measures B's first logical qubit in Y. Both outcomes are retained.
An explicit logical Clifford frame on C represents the corrected output as

\[
|m_Y\rangle=\frac{(1-i)|0\rangle+|1\rangle}{\sqrt3}.
\]

The other logical qubit of C remains in |0⟩. The previous Z-output
preparation remains available as `--magic-output z`.

**Ideal acceptance is now 3/4, instead of 5/8.** This removes the final
logical-outcome rejection; it does not remove noisy recovery failures.
The final correction is tracked in software, as requested, and contributes
no physical gates. The Y measurement itself is physically simulated.

## 1. Why both outcomes give the same resource after a Clifford

On the active first logical qubits, the sources are |0⟩ on B and |+⟩ on C.
Positive-SWAP projection, implemented by the gauging/ungauging circuit,
succeeds with probability 3/4 and produces

\[
|\Phi_+\rangle=\frac{2|00\rangle+|01\rangle+|10\rangle}{\sqrt6}.
\]

Here B is the first entry. Measuring its logical Y gives each eigenvalue
with probability 1/2, conditioned on the positive-SWAP branch:

| Logical Y outcome | Raw remaining C state | Clifford gates in application order |
|---|---|---|
| +1, stored bit 0 | `((2-i)|0>+|1>)/sqrt(6)` | S†, then H |
| −1, stored bit 1 | `((2+i)|0>+|1>)/sqrt(6)` | H, then S†, then H |

The first row's matrix is HS†, and the second is HS†H. Both map their
raw state to |m_Y⟩, up to an irrelevant overall phase. Equivalently, an
outcome-dependent H first makes both raw branches equal, followed by the
fixed HS† change of basis.

Therefore the ideal total probability is

\[
\tfrac34(\tfrac12+\tfrac12)=\tfrac34.
\]

The saved physical C amplitudes are those of the raw branch. They are
not silently replaced by frame-corrected amplitudes. The saved
`output_clifford_frame` tells downstream operations how to interpret and
consume that physical state as |m_Y⟩.

## 2. Full procedure and the point where Y is measured

| Stage | Action |
|---|---|
| B/C preparation | Same encoded known states, source flags and local source retries |
| Graph preparation | Same chosen current20 or compact13 graph and known-state recovery |
| Gauging | Same enrichment Fredkins, vertex-X meters and gauge-Z frame corrections |
| Gauged verification | Same paired, cycle and Gauss checks; retain only positively certified final cycles |
| Ungauging | Same gauge-Z readout, cut decoding and physical data SWAPs |
| Uncertified-cycle recovery | Same original 36-check joint recovery, with **no Y measurement**, then the existing re-gauging fallback |
| Positively certified final recovery | Measure the original 36 checks **plus one logical-Y word on B** as a joint commuting family |
| Joint decoding | Decode the first 36 bits with the unchanged B/C lookup; use its B correction to interpret the Y sign |
| Output | Discard B with physical meters; retain either decoded Y outcome and its Clifford frame on the unmeasured C state |

Deferring Y until a positively certified final cycle is essential. An
earlier logical measurement would disturb the logical input needed for
a possible re-gauging cycle.

Measuring Y alongside recovery is also important: simply measuring a
logical-Y representative after recovery would let a remaining correctable
B error flip its sign. The joint record supplies B's syndrome at the
same clean reference time, allowing that sign to be corrected.

## 3. Physical logical-Y word and corrected outcome

The following weight-nine Hermitian Pauli word is used:

```text
P = Y0 Z1 X2 X4 Y5 Z6 Y8 Z9 X10    on B
```

On the original code, P equals **−logical Y₀**, modulo stabilizers.
It has three physical Y factors. A protected cat has one leaf per target,
with the existing verified-cat or two-initial-zero-scan preparation.
For a Y port, its controlled operation is physically executed as

```text
CZ(leaf,target)
CX(leaf,target)
S(leaf)
```

This equals controlled-Y. All three operations have their own noise
locations; it is not treated as a free basis change. Each leaf still
touches only one data target.

Let r be P's reported parity in the selected joint record, and R_B the
joint decoder's B Pauli correction. The logical Y bit used for the frame is

\[
y=r\oplus1\oplus\operatorname{anti}(R_B,P),
\]

where `anti` is one exactly when the two Paulis anticommute. The constant
one accounts for P's minus sign. Multiplying P by code stabilizers does
not justify ignoring this correction on a nonzero-syndrome state.

For compact terminal extraction, the original 36 checks use the compact
gadgets, while this mixed-axis Y word uses a protected cat. A compact flag
still triggers its certified preliminary repair and a fresh protected
acquisition of the same **37** observables. Y outcomes measured in an
earlier incomplete history need not be separately selected away.

## 4. Cost and guarantee

On a clean final terminal stage, the extra Y check uses 52 two-qubit
gates, three physical S gates, and 25 meters per round. Three rounds add
156 two-qubit gates, nine S gates and 75 meters. Peak live qubits stay
75 on current20 and 66 on compact13; the graph stage still sets the peak.
The 80 clean atomic Fredkins are unchanged.

For current20 with compact terminal extraction, the clean two-qubit count
before selected ungauging SWAPs is now 6,216 instead of 6,060. With the
protected terminal profile it is 8,196 instead of 8,040. The extra cost is
real: 75% is a noiseless acceptance probability, not a prediction that a
noisy run will accept more often by exactly the same factor.

The [extended proof](magic_y_preparation_proof.md) preserves the global
two-fault accepted-output guarantee. In that model, every accepted output,
after correctable physical errors are decoded and its recorded Clifford
frame is interpreted, has logical state |m_Y⟩|0⟩. Readout faults are included.
The final B Z reports are used only for discarding B and never for selection.

The original strict joint decoder is retained. In particular, a logical Z
ambiguity on B that was harmless for a final Z measurement cannot simply
be assumed harmless for Y measurement.

## 5. Simulator and saved outputs

See [the simulation guide](../src/MAGIC_Y_SIMULATION.md) for commands and
validation. Exact relative phases use Gaussian integers a+ib; no floating
wavefunction evolution or density matrix is introduced. All data factors
remain explicit sparse dictionaries, with exact complex coefficients in
their coherent sum. Output states include a tagged complex-amplitude format
that the saved-run verifiers understand. Legacy real-state files still load.
