# Ordered terminal-screen comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-certified | 60 / 200 | 60 / 60 | 2665 | 4,534.4 | 12,062.5 | 0.9833333333333333 |
| gauging-screen | 83 / 200 | 83 / 83 | 2129 | 3,341.5 | 7,222.9 | 1.0 |
| cat-data | 94 / 200 | 94 / 94 | 1716 | 2,705.7 | 5,752.7 | 1.0 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. T/memory noise are explicit parameters; the default pilot sets them to zero.
