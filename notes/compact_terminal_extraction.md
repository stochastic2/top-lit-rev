# Compact flagged terminal extraction for gauging and ungauging

The counts and saved experiments below use the retained `--magic-output z`
profile. The new [Y-output profile](magic_y_preparation.md) is now the
simulator default; it adds one logical-Y check to final terminal rounds
and keeps both outcomes in a tracked Clifford frame.

This implements the terminal-gadget optimization proposed in
[the higher-noise note](higher_noise_rejection_options.md). It retains
the current graph, gauged verification, ungauging, original-code checks,
joint B/C correction table, and logical selection. The option is
`--terminal-extraction compact_flagged`; the previous default is `protected`.
Both history policies work, and `adaptive` is used in the noisy comparison.

The original 304-gate footprint copied from source extraction was not a
safe terminal replacement. Extra flags and guards produce a certified
**408-gate** complete B/C extraction round, compared with 1,068 previously.
Nonzero flags are repaired and followed by protected recovery, without
resetting either unknown data copy.

## 1. What is saved

These counts describe complete clean extraction, excluding data correction
gates selected by nonzero syndromes:

| Quantity | Protected | Compact flagged |
|---|---:|---:|
| Weight-four check: two-qubit gates | 19 | 6 |
| Weight-four check: meters | 10 | 2 |
| Weight-eight check: two-qubit gates | 43 | 18 |
| Weight-eight check: meters | 22 | 6 |
| Complete B/C round: two-qubit gates | 1,068 | 408 |
| Complete B/C round: meters | 552 | 136 |
| Three clean B/C rounds: two-qubit gates | 3,204 | 1,224 |
| Full current-graph schedule before ungauging SWAPs | 8,040 | 6,060 |

There are ten weight-four and eight weight-eight checks on each copy.
The terminal gate saving is 61.8%; its meter saving is 75.4%. The full
clean two-qubit saving is 24.6%. The 80 atomic Fredkins and peak 75 live
qubits are unchanged. Add the selected ordinary ungauging SWAPs to both
full-schedule counts. A flag fallback adds a protected recovery pass;
these clean counts are not noisy averages.

## 2. Weight-four check: one flag around the dangerous middle

Write P for X or Z, and let cP mean CX or CZ from syndrome ancilla a
to a data target. Prepare a in |+⟩ and flag f in |0⟩:

```text
cP(a, q0)
CX(a, f)
cP(a, q1)
cP(a, q2)
CX(a, f)
cP(a, q3)
measure f in Z                    # flag
measure a in X                    # syndrome
```

There are four data couplings and two flag CNOTs. An ancilla X fault
in the dangerous middle can spread to two data targets, and is flagged.
An earlier ancilla X can spread to three targets, but multiplying by the
measured four-body check makes that equivalent to a single-target defect
on the projected branch. The finite audit includes target errors occurring
at the same faulty gate and pairs of faults that hide a flag.

## 3. Weight-eight check: decoded four-leaf cat with two guards

Each leaf controls two targets in a single inner C4 block. Number the
four participating blocks 0–3 and their two targets q[j,0], q[j,1].

```text
prepare L0 in |+⟩ and L1,L2,L3 in |0⟩
CX(L0,L1), CX(L0,L2), CX(L0,L3)
cP(L0,q[0,0]), ..., cP(L3,q[3,0])
cP(L0,q[0,1]), ..., cP(L3,q[3,1])

measure Z(L0) Z(L1) with a fresh parity helper    # g01
measure Z(L1) Z(L2) with a fresh parity helper    # g12

CX(L0,L3), CX(L0,L2), CX(L0,L1)
measure L1,L2,L3 in Z                            # f1,f2,f3
measure L0 in X                                  # syndrome
```

Each guard costs two CNOTs and one helper meter. The total is
8 data couplings + 3 fanout + 3 uncompute + 4 guard CNOTs = 18.
No separate parity test involving L3 is needed: the two guards connect
three leaves and eliminate every two-versus-two cat pattern, while the
decoded flags still observe all three non-root leaves.

Without these guards, two root faults can produce a four-target hook
and hide all decoded flags. That is acceptable for the source's weaker
block-support proof, but not for the terminal physical-weight proof.

## 4. Zero flags: continue compact acquisition

If all flags are zero, retain either syndrome sign and continue the
complete-record history. The audit establishes physical data weight
at most k for k≤2 local faults, modulo the measured check Q. On a
projected Q branch, multiplying an error by Q changes only a scalar phase.

The bound is in physical qubits, not merely inner blocks. It is precisely
what the old terminal proof needs for faults after its clean reference.
All selected complete records and all compact flag reports are saved.

## 5. Nonzero flags: repair, then protected recovery

Flag order for an upper check is `(g01,g12,f1,f2,f3)`. Bit zero is the
first entry when converting to an integer.

- For `(1,0,1,1,0)`, word 13, apply P independently to both targets of
  leaf 1 and both targets of leaf 2: four single-qubit gates.
- Every other reachable flag vector uses the identity repair.
- Word 19, `(1,1,0,0,1)`, cannot arise from at most two gadget faults
  in the audited model. It rejects as `terminal_flag_unsupported`.
- A weight-four flag needs no preliminary Pauli repair.

For every reachable flag vector, the audited repair leaves at most one
affected matched block per local fault, modulo Q. A nonzero flag does
**not** certify the stronger physical-weight bound, even when its repair
is the identity. Therefore:

```text
finish reading and removing the compact helpers
apply the certified preliminary repair
retain B and C, discarding only the unfinished compact classical history
restart complete syndrome acquisition with protected terminal cats
apply the existing joint B/C correction to its certified record
continue final extraction or the existing re-gauging fallback
```

Only the current terminal stage switches to protected extraction. A later
fresh gauging cycle may try compact extraction again. The data are never
re-encoded or reset because of a terminal flag.

For example, a single incorrect flag-meter report usually applies no
Pauli, then invokes protected recovery. A raw cat fault producing word
13 may spread to four targets, but the four-gate repair removes the bulk
hook before that recovery. False flags and hidden pairs of faults are
included in the same certificate.

## 6. Guarantee and implementation

The [accompanying proof](compact_terminal_extraction_proof.md) extends
the existing accepted-output theorem: with at most two faulty locations
in the full schedule, every accepted C output decodes to the intended
magic state, with at most two correctable physical errors per copy.
It includes noisy single-qubit repair gates and readout faults. It is
not an unconditional stochastic-noise guarantee.

The primitive program and runtime are in
[c4_helix_compact_terminal.py](../src/c4_helix_compact_terminal.py).
The [finite audit](../src/check_compact_terminal.py) checks all local
Pauli faults and single-qubit idles, then all pairs of merged signatures.
Its [saved certificate](../output/c4-helix-compact-terminal-certificates.json)
checks 2,496 zero-flag signature pairs for the physical bound and 9,188
ordered pairs for the flag-repair block bound, across X/Z and both weights.
This is gadget-local enumeration plus a composition proof, not enumeration
of all fault pairs in the full factory.

Run with the existing sparse simulator:

```sh
"$HOME/pytket-venv/bin/python" src/simulate_c4_helix_depolarizing.py \
    --shots 50 --seed 0 --two-qubit-infidelity 1e-3 \
    --readout-flip-probability 1e-3 --history-policy adaptive \
    --terminal-extraction compact_flagged --output-dir output/my-compact-terminal

"$HOME/pytket-venv/bin/python" src/verify_c4_helix_depolarizing_run.py \
    output/my-compact-terminal
```

The noiseless runner accepts the same terminal option. Saved records
include every flag, preliminary repair, compact history, and protected
fallback history. The verifier checks the reported control flow and
recomputes accepted-state diagnostics. Other noise channels remain ideal
in this example; Fredkins remain atomic.

## 7. Validation and measured noisy result

The combined suite passed **117 tests**, covering dense-projector agreement
for all four shapes, exact primitive schedules, the local fault certificates,
a four-target hook repaired from word 13, false-flag protected recovery,
no resetting of B/C during fallback, corrupted flag metadata, and exact
noiseless outputs on both graph choices. Existing tests for the previous
profiles continue to pass.

The [new noiseless run](../output/c4-helix-compact-terminal-noiseless-v2/summary.json)
has two accepted outputs and two intrinsic negative-SWAP rejections for
seeds 0–3, with exact accepted states. Its saved flags, histories, counts,
and amplitudes passed the read-only verifier.

For the intended combined-noise test, both profiles used two-qubit average
infidelity 10⁻³, independent readout-flip probability 10⁻³, the current
graph, optimized upstream gadgets, adaptive history, and seeds 0–49.
The protected baseline combines the earlier seed-0–19 pilot and a new
seed-20–49 batch. The new compact run uses all fifty in one batch. See
the [complete comparison](../output/c4-helix-compact-terminal-comparison.json)
and [compact run](../output/c4-helix-compact-recovery-1e-3-readout-1e-3-50/summary.json).

| Observed statistic | Protected | Compact with flag recovery |
|---|---:|---:|
| Accepted / attempted | 5 / 50 | 8 / 50 |
| Accepted fraction | 10% | 16% |
| Acceptance Wilson 95% interval | 4.3–21.4% | 8.3–28.5% |
| Accepted decoded fidelity exactly one | 5 | 8 |
| Accepted imperfect outputs | 0 | 0 |
| Two-qubit gates across all attempts | 738,793 | 665,761 |
| Meters across all attempts | 340,524 | 294,414 |
| Two-qubit gates per accepted output | 147,759 | 83,220 |
| Computational failures | 0 | 0 |

The noisy average used 9.9% fewer two-qubit gates and 13.5% fewer meters.
Cost per accepted output was about 44% lower in this sample. These
numbers include failed attempts and all adaptive/protected recovery work.
The lower average saving than the clean count is explained by 35
protected fallbacks among 54 reached terminal stages. Six of the eight
accepted compact outputs used such a fallback; two nontrivial four-gate
preliminary repairs occurred across all attempts. Flags did not cause
an additional terminal-flag rejection in this run.

Both profiles' accepted-state diagnostics were complete and all final
artifacts passed their verifiers. The compact run took 494 seconds, with
3.06 GiB peak worker RSS and at most 2,048 coherent terms. Concurrent
validation jobs prevent treating its wall time as a controlled speed test.

The observed acceptance increase is promising, not statistically decisive
at fifty attempts. Zero observed accepted errors does not establish a rare
logical-error rate. Equal seed ranges also do not pair identical physical
fault trajectories after the circuits take different branches. The rigorous
result is the clean cost reduction and retained bounded-fault guarantee;
the unrestricted-noise yield and quality require larger experiments.
