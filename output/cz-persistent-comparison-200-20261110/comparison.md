# Persistent gauging coordinates comparison

All arms use matched source selection and flag-dependent data recovery. Cat-labelled CZ uses genuine GHZ20; direct-flags is a separate global flagged-U comparator when present.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-round-trip | 75 / 200 | 75 / 75 | 1889 | 2,800.7 | 6,538.3 | 0.9866666666666667 |
| gauging-persistent13 | 79 / 200 | 78 / 79 | 1574 | 2,400.9 | 5,295.5 | 0.9746835443037974 |
| gauging-persistent4 | 87 / 200 | 87 / 87 | 1421 | 2,068.6 | 4,494.9 | 0.9770114942528736 |
| cat-compact | 115 / 200 | 115 / 115 | 1476 | 2,281.0 | 3,766.8 | 0.9478260869565217 |
| direct-flags | 94 / 200 | 94 / 94 | 1317 | 1,994.1 | 3,984.9 | 0.9787234042553191 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. All noise settings, including Clifford/T/memory rates, are recorded in each manifest.
