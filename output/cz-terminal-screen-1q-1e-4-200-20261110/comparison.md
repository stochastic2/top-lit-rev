# Ordered terminal-screen comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-certified | 54 / 200 | 53 / 54 | 2665 | 4,907.7 | 12,504.7 | 0.9897119341563786 |
| gauging-screen | 61 / 200 | 61 / 61 | 2129 | 3,747.1 | 9,883.3 | 1.0 |
| cat-data | 89 / 200 | 89 / 89 | 1716 | 3,060.2 | 6,297.5 | 0.9887640449438202 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. T/memory noise are explicit parameters; the default pilot sets them to zero.
