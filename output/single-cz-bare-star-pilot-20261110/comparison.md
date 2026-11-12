# Bare graph-star comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output |
|---|---:|---:|---:|---:|---:|
| gauging-flags | 7 / 40 | 7 / 7 | 2809 | 5,821.0 | 21,563.0 |
| gauging-bare | 8 / 40 | 8 / 8 | 2665 | 5,216.0 | 20,109.0 |
| cat-data | 16 / 40 | 16 / 16 | 1716 | 3,119.8 | 7,376.3 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. T/memory noise are explicit parameters; the default pilot sets them to zero.
