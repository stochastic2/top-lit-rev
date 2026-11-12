# Persistent gauging coordinates comparison

All arms use matched source selection and flag-dependent data recovery. Cat-labelled CZ uses genuine GHZ20; direct-flags is a separate global flagged-U comparator when present.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-round-trip | 7 / 20 | 7 / 7 | 1889 | 3,003.6 | 6,803.1 | 1.0 |
| gauging-persistent13 | 5 / 20 | 5 / 5 | 1574 | 2,636.2 | 8,364.4 | 1.0 |
| gauging-persistent4 | 9 / 20 | 9 / 9 | 1421 | 2,558.9 | 4,547.7 | 1.0 |
| cat-compact | 13 / 20 | 13 / 13 | 1476 | 2,825.5 | 3,788.0 | 0.9230769230769231 |
| direct-flags | 4 / 20 | 4 / 4 | 1317 | 2,531.5 | 9,812.2 | 1.0 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.
