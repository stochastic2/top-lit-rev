# Flag-dependent recovery comparison

Same source, physical noise, graph, capacities, and seeds. Cat arms use a genuine GHZ20 CZ measurement.

| Arm | Accepted / attempts | Target matches / assessed | Mean decoded F | CX / accepted | Recovered episodes |
|---|---:|---:|---:|---:|---:|
| gauging-reject | 2 / 40 | 2 / 2 | 1.0000 | 37245.5000 | 0 |
| gauging-data | 3 / 40 | 3 / 3 | 1.0000 | 35851.3333 | 18 |
| cat-reject | 5 / 40 | 5 / 5 | 1.0000 | 14631.8000 | 0 |
| cat-data | 10 / 40 | 10 / 10 | 1.0000 | 10276.7000 | 16 |

Executed CX counts include rejected attempts and all fallback operations. Missing computational results remain unresolved.

Paired-seed changes: `{"cat": {"completed_pairs": 40, "gained_acceptances": 5, "lost_acceptances": 0, "strict_acceptances_preserved": 5}, "gauging": {"completed_pairs": 40, "gained_acceptances": 1, "lost_acceptances": 0, "strict_acceptances_preserved": 2}}`.

This sample does not establish equal population fidelity. Inspect fidelity and cost together, and increase shots before drawing performance conclusions.
