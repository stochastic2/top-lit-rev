# Ordered terminal-screen comparison

All arms use decoded/rolling source selection consistently and flag-dependent data recovery; cat CZ is genuine GHZ20.

| Arm | Accepted / attempts | Target matches / assessed | Clean CX | Mean CX in successful attempt | Total CX / accepted output | Raw F |
|---|---:|---:|---:|---:|---:|---:|
| gauging-certified | 8 / 40 | 8 / 8 | 2665 | 5,216.0 | 20,109.0 | 0.875 |
| gauging-screen | 14 / 40 | 13 / 14 | 2129 | 4,015.4 | 9,591.7 | 0.9285714285714286 |
| cat-data | 16 / 40 | 16 / 16 | 1716 | 3,119.8 | 7,376.3 | 1.0 |

Clean CX is one complete no-fault/no-extra-recovery attempt. Successful-attempt means include conditional work within those attempts. Total CX/output includes all discarded attempts and fallbacks.

Raw physical fidelity includes correctable residual errors; the accepted-output contract is the decoded logical state.

Schedules differ: identical seeds do not represent identical fault trajectories. No monotone paired-acceptance assumption is made.

Finite samples do not establish equal population fidelity. T/memory noise are explicit parameters; the default pilot sets them to zero.
