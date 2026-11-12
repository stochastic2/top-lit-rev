# Compact Pauli-data check comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-rolling | 61 / 200 | 61 / 61 | 2129 | 3,747.1 | 9,883.3 | 1.0 |
| gauging-compact | 75 / 200 | 75 / 75 | 1889 | 2,800.7 | 6,538.3 | 0.9866666666666667 |
| cat-rolling | 89 / 200 | 89 / 89 | 1716 | 3,060.2 | 6,297.5 | 0.9887640449438202 |
| cat-compact | 115 / 200 | 115 / 115 | 1476 | 2,281.0 | 3,766.8 | 0.9478260869565217 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.
