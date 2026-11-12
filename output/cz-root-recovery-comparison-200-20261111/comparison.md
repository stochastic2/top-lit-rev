# Local-Gauss graph-assisted root recovery

All arms use matched source selection and flag-dependent data recovery. Cat-labelled CZ uses genuine GHZ20; direct-flags is a separate global flagged-U comparator when present.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-reject | 83 / 200 | 83 / 83 | 1889 | 2,902.1 | 5,778.1 | 1.0 |
| gauging-blind | 94 / 200 | 94 / 94 | 1889 | 3,022.5 | 5,459.2 | 1.0 |
| gauging-joint | 94 / 200 | 94 / 94 | 1889 | 3,022.5 | 5,459.2 | 1.0 |
| cat-legacy | 115 / 200 | 115 / 115 | 1476 | 2,281.0 | 3,766.8 | 0.9478260869565217 |
| cat-dual | 120 / 200 | 120 / 120 | 1476 | 2,340.4 | 3,788.4 | 0.9583333333333334 |
| direct-reject | 87 / 200 | 87 / 87 | 1317 | 1,979.2 | 4,373.6 | 1.0 |
| direct-recover | 99 / 200 | 99 / 99 | 1317 | 2,070.7 | 4,098.5 | 1.0 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.
