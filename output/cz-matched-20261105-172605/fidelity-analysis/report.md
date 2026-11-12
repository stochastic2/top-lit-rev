# Fidelity analysis of matched CZ factory runs

All saved controller/report certificates and accepted complex-output diagnostics were rechecked.
Common source, noise, history and capacity settings match: **True**.
Shared runtime hashes match: **True**.

| Run | Acceptance | Mean decoded fidelity | Mismatches / accepted | 95% upper mismatch probability | CX / accepted |
|---|---:|---:|---:|---:|---:|
| cat-cats | 80/200 | 0.987500 | 1/80 | 5.79% | 15,680.3 |
| cat-flags | 45/200 | 1.000000 | 0/45 | 6.44% | 7,561.7 |
| gauging-cats | 52/200 | 1.000000 | 0/52 | 5.60% | 30,395.6 |
| gauging-flags | 13/200 | 1.000000 | 0/13 | 20.58% | 29,370.5 |

Fidelity is conditional on acceptance and uses the same ideal read-only decoder for every route.
The intervals bound the probability of a non-target accepted trajectory at tolerance; they are not
a claim that all possible infidelities are Bernoulli. Zero failures leave substantial uncertainty.
They are individual bounds, not a simultaneous four-way confidence statement.
Shared seeds couple simulations, so no unqualified independent-sample significance test is reported.
These bounds alone do not establish a between-protocol fidelity advantage.

cat-cats has the highest observed acceptance. cat-flags has the lowest observed CX cost per
accepted output. These are different objectives, and the outputs are not certified to matched
population fidelity. Fault-free diagnostics cannot be used to discard a bad accepted output
in the physical factory.

## Accepted mismatches

cat-cats, shot 27, seed 1027: decoded |11>, fidelity 0.0, 5 sampled faults.

| CZ check | Actual leaf parity bit | Reported parity bit |
|---|---:|---:|
| terminal/0/U | 1 | 0 |
| terminal/1/U | 1 | 0 |
| terminal/2/U | 0 | 0 |

Actual leaf parity is a trustworthy CZ sign only if cat phase is correct.
ZZ resource checks verify bits, not the cat phase. Faults above the two-fault
budget can therefore falsely certify a genuine negative logical branch.

## Raw physical overlap

| Run | Mean raw overlap | Correctable residuals with decoded fidelity one |
|---|---:|---:|
| cat-cats | 0.950000 | 3 |
| cat-flags | 1.000000 | 0 |
| gauging-cats | 1.000000 | 0 |
| gauging-flags | 1.000000 | 0 |

Low raw overlap with decoded fidelity one is a correctable physical residual, not a logical failure.
A low-weight representative for a syndrome does not itself certify the logical state.

## Resource scope

CX/accepted includes every completed rejected attempt and retry. T, preparation, readout and
serial idle costs remain separate metrics in the summaries. T/Clifford/memory/preparation
noise were zero in these runs; the comparison does not establish a hardware-level winner.
