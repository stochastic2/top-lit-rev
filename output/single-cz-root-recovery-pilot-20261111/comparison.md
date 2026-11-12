# Local-Gauss graph-assisted root recovery

All arms use matched source selection and flag-dependent data recovery. Cat-labelled CZ uses genuine GHZ20; direct-flags is a separate global flagged-U comparator when present.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-reject | 7 / 20 | 7 / 7 | 1889 | 3,922.0 | 7,425.3 | 1.0 |
| gauging-blind | 8 / 20 | 8 / 8 | 1889 | 4,207.4 | 7,105.5 | 1.0 |
| gauging-joint | 8 / 20 | 8 / 8 | 1889 | 4,207.4 | 7,105.5 | 1.0 |
| cat-legacy | 13 / 20 | 13 / 13 | 1476 | 2,825.5 | 3,788.0 | 0.9230769230769231 |
| cat-dual | 13 / 20 | 13 / 13 | 1476 | 2,909.4 | 4,070.7 | 1.0 |
| direct-reject | 5 / 20 | 5 / 5 | 1317 | 2,695.4 | 8,289.8 | 1.0 |
| direct-recover | 8 / 20 | 8 / 8 | 1317 | 2,696.6 | 5,736.6 | 1.0 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.
