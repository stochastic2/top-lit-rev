# Compact Pauli-data check comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-rolling | 2 / 20 | 2 / 2 | 2129 | 4,501.0 | 28,378.0 | 1.0 |
| gauging-compact | 7 / 20 | 7 / 7 | 1889 | 3,003.6 | 6,803.1 | 1.0 |
| cat-rolling | 9 / 20 | 9 / 9 | 1716 | 3,268.4 | 5,908.8 | 1.0 |
| cat-compact | 13 / 20 | 13 / 13 | 1476 | 2,825.5 | 3,788.0 | 0.9230769230769231 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.
