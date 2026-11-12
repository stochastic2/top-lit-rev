# Completed four-configuration comparison with Fredkin noise

Batch: `c4-helix-comparison-200-fredkin-H5Yeky`. Each run processed 200 attempts, seeds 1000–1199. All four runs passed the saved-run verifier.

The noise settings are average two-qubit gate infidelity 10^-3, average atomic three-qubit Fredkin infidelity 9×10^-3, and independent readout-report flips with probability 10^-3. Single-qubit, idle and preparation noise are zero. The Fredkin channel approximates the scale of a decomposition; it does not simulate its internal gates.

## Fidelity definitions

Both fidelities are diagnostic quantities after perfect syndrome measurement and the specified fixed decoder. This ideal recovery is not a hidden circuit operation. Y outputs are interpreted in their recorded Clifford frames.

- Magic-qubit fidelity is overlap with the desired pure magic state after tracing out the spare logical qubit.
- Full-output fidelity is overlap with the desired magic state tensor the spare logical state |0>.
- Exact counts are trajectories with fidelity exactly one. Mean fidelity is not the fraction of exact trajectories.
- All fidelity averages below condition on known accepted outputs; unresolved computational attempts are excluded.

The Z target is (2|0>+|1>)/sqrt(5). The Y target is ((1-i)|0>+|1>)/sqrt(3). These are different resource states.

## Results

| Configuration | Known accepted / 200 | Unresolved | Mean magic fidelity | Mean full-output fidelity | Exact magic / accepted | Exact full / accepted |
|---|---:|---:|---:|---:|---:|---:|
| current20-z | 14/200 (7.0%) | 23 | 97.43% | 92.86% | 13/14 | 13/14 |
| current20-y | 17/200 (8.5%) | 27 | 84.97% | 84.97% | 12/17 | 12/17 |
| compact13-z | 8/200 (4.0%) | 27 | 95.50% | 95.50% | 7/8 | 7/8 |
| compact13-y | 11/200 (5.5%) | 28 | 93.94% | 89.90% | 9/11 | 9/11 |

Current20 Z has the largest observed mean magic-qubit fidelity and the largest known exact-magic yield (13/200). Compact13 Z has the largest observed mean full-output fidelity. Current20 Y has the largest known acceptance yield, but its exact-magic yield is 12/200. These are descriptive rankings of small, computationally selected samples, not established population rankings.

## Imperfect accepted trajectories

Shot indices are zero based. Fault counts are sampled faulty locations, not the number of affected qubits.

| Configuration | Shot | Seed | Magic fidelity | Full fidelity | Faults |
|---|---:|---:|---:|---:|---:|
| current20-z | 180 | 1180 | 16/25 | 0 | 20 |
| current20-y | 18 | 1018 | 4/9 | 4/9 | 26 |
| current20-y | 123 | 1123 | 5/9 | 5/9 | 16 |
| current20-y | 130 | 1130 | 4/9 | 4/9 | 36 |
| current20-y | 133 | 1133 | 4/9 | 4/9 | 12 |
| current20-y | 186 | 1186 | 5/9 | 5/9 | 22 |
| compact13-z | 90 | 1090 | 16/25 | 16/25 | 12 |
| compact13-y | 83 | 1083 | 8/9 | 8/9 | 36 |
| compact13-y | 157 | 1157 | 4/9 | 0 | 24 |

All nine imperfect accepted trajectories have 12–36 sampled faults. There are no observed accepted failures at zero, one or two faults. No accepted trajectory in these runs has at most two faults, so these samples do not directly test the positive accepted-output conclusion within that budget. They neither contradict nor independently certify the analytical two-fault theorem.

## Computational limitations

105/800 attempts are unresolved: 76 exceeded the coherent-term limit and 29 timed out. These are not physical rejections. Unknown outcomes can affect both yield and accepted-state fidelity. The possible acceptance intervals below allow every unresolved attempt either to reject or accept; they are not confidence intervals.

| Configuration | Acceptance bounds over all 200 attempts |
|---|---:|
| current20-z | 7.0–18.5% |
| current20-y | 8.5–22.0% |
| compact13-z | 4.0–17.5% |
| compact13-y | 5.5–19.5% |

Only 8–17 outputs were accepted per configuration. Statistical uncertainty remains large even before addressing unresolved attempts. In particular, the reported fidelities do not establish low logical error rates. Identical seed ranges across configurations do not imply identical fault histories because the operation schedules and random-number consumption differ.

The largest physical rejection category is an absent terminal correction candidate (104–109 per run). Increasing the simulator resource limit would address missing computations; it would not repair that decoder rejection mechanism.

Exact fractions, all accepted-trajectory diagnostics, fault-channel counts and numerical details are in [logical_fidelity_analysis.json](logical_fidelity_analysis.json).
