# Improving acceptance with gate and readout errors

This analysis concerns the retained Z-output profile. The
[new Y-output profile](magic_y_preparation.md) has a different final
measurement: in particular, the harmless-B-phase simplification proposed
below must be re-derived for Y and is not used by the implemented strict
joint decoder.

The present adaptive-history circuit has a useful improvement over consecutive
triples, but it still needs better recovery and cheaper extraction to operate
well near two-qubit average infidelity 10⁻³ with readout errors. This note
records the next concrete opportunities. It does not change the simulator's
acceptance rules or claim a new stochastic-noise guarantee.

## What the existing runs show

At gate infidelity 8 × 10⁻⁴ and ideal meters, adaptive history accepted
17/50 outputs, with 16 decoding exactly and one having fidelity 4/5.
Of 33 rejections, 11 were terminal ambiguities and 7 had no terminal
candidate. In every ambiguous case the present decoder found four distinct
logical correction classes.

The [new illustrative baseline](../output/c4-helix-adaptive-1e-3-readout-1e-3-baseline20/summary.json)
uses gate infidelity 10⁻³ and independent classical report flips with
probability 10⁻³ after destructive meters. All other noise rates remain
zero, including atomic Fredkins. It accepted 1/20, with decoded fidelity
one. Rejections were 6 absent terminal candidates, 3 terminal ambiguities,
3 source retry limits, 4 negative-SWAP decisions, and one each of cycle
limit, cycle-syndrome failure, and B-one. There were no computational failures.
The rejection Wilson 95% interval is 76.4–99.1%; twenty attempts cannot
establish a precise yield or isolate the effects of the two changed rates.

A clean accepted schedule has about 8,050 two-qubit gates and 3,675
destructive meters. With the infidelity convention used here, gate
infidelity 10⁻³ means nonidentity-pair probability 1.25 × 10⁻³: roughly
10 sampled gate faults on that clean schedule, plus 3.7 report flips
at the illustrative readout rate. Adaptive retries can add further locations.
The global two-fault theorem remains valuable, but does not predict typical
performance at these rates.

## 1. Recover only what the final extraction needs

`decode_joint` currently demands one correction class modulo the full
stabilizer group of **both** copies. That is appropriate before another
gauging cycle, when both logical states must be retained. It is stronger
than necessary on a positively certified final cycle: B will be measured
in Z and discarded, and only its logical Z₀ result determines selection.

For example, suppose two candidate corrections differ only by logical Z₀
on B. Their B Z-meter probabilities are identical. On the selected B₀=0
branch the phase is +1, so C is unchanged. Rejecting that difference is
unnecessary for this output task.

At the ideal logical level, positive SWAP certification gives

\[
|\Phi_+\rangle\propto
(2|00\rangle+|01\rangle+|10\rangle)_{B_0C_0}
\otimes|0\rangle_{B_1}\otimes|0\rangle_{C_1}.
\]

Measuring B₀=0 leaves C₀ proportional to 2|0⟩+|1⟩. The following
logical Pauli differences between same-syndrome candidates are harmless
for that final extraction:

- B₀: I or Z, preserving the selected B₀ outcome.
- B₁: any Pauli, because this logical qubit is discarded.
- C₀: I, preserving the magic state.
- C₁: I or Z, preserving its known zero state.

An independent dense logical calculation checked all 256 four-qubit
Paulis and found exactly these 16 harmless differences. For every measured
B₁ outcome on B₀=0, the remaining C vector is either zero or proportional
to the target. Linearity handles coherent sums within this harmless set.

For candidate error masks (x_B,z_B),(x_C,z_C), a sufficient equivalence
signature therefore consists of just four commutation bits:

\[
(x_B\cdot\overline Z_0,\;
 x_C\cdot\overline Z_0,\;
 z_C\cdot\overline X_0,\;
 x_C\cdot\overline Z_1)\pmod2.
\]

Comparing these signatures is valid because same-syndrome candidates
differ by logical Paulis. It identifies two potentially avoidable
rejections in the previous 50-shot run: shots 2 and 11 have positively
certified cycles and four full logical classes, but only one such
output-relevant signature. This is a report-only diagnostic, not a replay
of the rest of those trajectories or a prediction that both would accept.

Before enabling this rule, the proof must incorporate the actual destructive
B decoder and its late faults. The existing strict equivalence rule must
remain on every recovery followed by re-gauging: harmless final B phases
need not preserve the logical span required for another cycle. This is a
small, concrete first optimization with no added measurement gates.

## 2. Decode where and when an error could have happened

The current terminal lookup uses one selected 36-bit syndrome. It ignores
the earlier vectors, the timing of changes, and much upstream information.
Two different logical correction classes can share that last syndrome
but have different compatible histories or different minimum fault counts.

Retain candidate error paths across successive measurements, including
readout flips and correlations created by a faulty two-qubit gate. A
single transient report and a persistent change across several checks
then supply different evidence. This is not permission to assume that
every transient is a meter error: gate faults can mimic it.

A guarantee-preserving decoder must retain **all** histories allowed by
the bounded-fault model, accepting only if their actions on the required
output agree. A probability-weighted choice with a tunable confidence
threshold is an additional option for unrestricted stochastic noise; it
needs separate acceptance/fidelity calibration. Merely choosing the lightest
correction among ambiguous classes is not the same guarantee.

Start with the ordinary Pauli recovery circuit after ungauging, which is
Clifford. Extending an ordinary binary detector-error model through
Fredkins and non-Pauli Gauss measurements requires extra work. A global
Pauli detector model must not simply be assumed for the whole factory.

The original C4-Helix paper uses circuit-wide decoding and confidence-based
postselection; see its [Appendix C](https://arxiv.org/abs/2609.03194).
Tools for combining flag information, fault-count constraints and adaptive
histories are developed in
[Pato et al.](https://arxiv.org/abs/2306.12862). Those results motivate this
direction; they do not establish this factory's performance.

## 3. Reduce terminal gadget cost together with its decoder

The current terminal extraction costs 534 two-qubit gates per copy per
round, or 1,068 for B and C. Across three clean rounds this is 3,204 gates.
The compact source shapes cost 152 per copy, or 304 for both, for the same
18 Pauli-check supports. The raw extraction saving is about 72%.

Counting the physical Z meters in those existing shapes gives:

| One clean complete B/C extraction round | Protected terminal shapes | Compact source-shaped footprint |
|---|---:|---:|
| Two-qubit gates | 1,068 | 304 |
| Destructive Z meters | 552 | 84 |

The meter reduction is about 85%, which matters directly for report-flip
noise. The compact column is a cost target computed from current source
circuits, not the cost of a proven replacement recovery circuit. Any
additional flags or cleanup needed by its proof must be added.

This is an opportunity, not a certified terminal replacement. The source
circuits deliberately permit error spread within a C4 block; an unused
known source can be rebuilt when flagged. An unknown final C state cannot
be discarded and rebuilt. Terminal flags must instead constrain the
recovery, and missed/false flags and late correlated errors must be included
in the proof and decoder. In particular the physical weight-two residual
guarantee cannot be inherited just by copying the source circuit.

Develop compact **flagged recovery** for the ordinary Pauli checks while
initially retaining the protected non-Pauli Gauss gadgets. Reducing both
gate and meter locations helps at the intended combined-noise target.
The paper's low-level two-ancilla flagged circuit also differs from the
bare inner-block source checks, even where their gate totals match.

## Suggested order and success criteria

First implement the final-output equivalence test with its proof and
regressions. Then build history-aware terminal recovery and compact flagged
extraction together, before attempting a direct recovery inside the gauged
code. The existing graph and gauging/ungauging circuit can be retained.

Benchmark gate infidelity 10⁻³ with readout-flip probabilities 0, 10⁻⁴,
and 10⁻³. Record acceptance, mean accepted decoded infidelity, imperfect
accepted trajectories, and gate cost per useful output. Preserve the
two-fault theorem with readout faults included, and separately test the
unrestricted stochastic regime. Specify the desired accepted-output error
target before selecting any probability-based acceptance threshold.

The noiseless design still has acceptance 5/8. This work concerns physical
rejection overhead; it does not remove the intrinsic logical selection.
