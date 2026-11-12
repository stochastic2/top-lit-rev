# Bare graph-star comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output |
|---|---:|---:|---:|---:|---:|
| gauging-flags | 54 / 200 | 54 / 54 | 2809 | 4,743.0 | 12,755.2 |
| gauging-bare | 60 / 200 | 60 / 60 | 2665 | 4,534.4 | 12,062.5 |
| cat-data | 94 / 200 | 94 / 94 | 1716 | 2,705.7 | 5,752.7 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. T/memory noise are explicit parameters; the default pilot sets them to zero.
