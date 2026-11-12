# Flag-dependent recovery comparison

Same source, physical noise, graph, capacities, and seeds. Cat arms use a genuine GHZ20 CZ measurement.

| Arm | Accepted / attempts | Target matches / assessed | Mean decoded F | CX / accepted | Recovered episodes |
|---|---:|---:|---:|---:|---:|
| gauging-reject | 13 / 200 | 13 / 13 | 1.0000 | 29370.4615 | 0 |
| gauging-data | 54 / 200 | 54 / 54 | 1.0000 | 12755.2222 | 281 |
| cat-reject | 45 / 200 | 45 / 45 | 1.0000 | 7561.6889 | 0 |
| cat-data | 94 / 200 | 94 / 94 | 1.0000 | 5752.6596 | 176 |

Executed CX counts include rejected attempts and all fallback operations. Missing computational results remain unresolved.

Paired-seed changes: `{"cat": {"completed_pairs": 200, "gained_acceptances": 49, "lost_acceptances": 0, "strict_acceptances_preserved": 45}, "gauging": {"completed_pairs": 200, "gained_acceptances": 41, "lost_acceptances": 0, "strict_acceptances_preserved": 13}}`.

This sample does not establish equal population fidelity. Inspect fidelity and cost together, and increase shots before drawing performance conclusions.
