# Individually dressed data ports on compact13

The new outer meter removes the two-data CNOT that produced the known Z hooks. All four outer meters have a unique correction class for every modeled record with up to two internal faults and ideal final diagnostics. Cycle bits are necessary for some of those corrections. The broader outside-fault test still leaves ten flagged records per check that require rejection. The clean three-round estimate is 1,985 CX and 448 T/T† before sector certification or conditional recovery. The round trip costs 1,889 CX and 256 T/T†.

## Circuit and signed instrument

Let $e=A_{av}$ be the tree edge for nonroot block $v$, $W_q=T^{-s_q}X_qT^{s_q}$, and $B_q=C_e(W_q)$. It is an involution. A nonroot site receives the following gates in chronological order, with all rotations on $D_q$.

```text
T^s_q   CX(e,D_q)   T^-s_q   CX(s,D_q)   T^s_q   CX(e,D_q)   T^-s_q
```

For $s=0$ the two $B_q$ cancel. For $s=1$ the action is $B_qX_qB_q$. A root site uses only `CX(s,D_q)`. Each $B_q$ commutes with the other data ports, including ports that share $e$. The full controlled action is therefore $C_s(VS_R^XV)$ on the whole input Hilbert space. This construction uses short basis sandwiches inside individual ports. The target register enters and leaves every port in gauged coordinates, with no shared coordinate pass or bare-syndrome measurement on a decoupled register. The pair sign $(-1)^{\frac12\sum_{q\in J}s_q}$ is retained on the edge-controlled branch.

The four flags use the compact eight-port pattern. After data port $j$, the meter couples to $f_{j\bmod 4}$. Each flag is prepared just before its first coupling and measured just after its second. The ideal pair of couplings returns each flag to zero for arbitrary target input. With the syndrome helper prepared and measured in X, the two Kraus operators are exactly $(I+(-1)^bQ_R)/2$. The integer phase/permutation oracle checks both control values, all involved data and tree bits, and two fillings of uninvolved data. Uninvolved data cancel analytically. The same compiler checks the five four-site inner instruments in both Z sectors. Outer generators use the previous $(1,3,4,8)$ basis, including its replacement for check 6.

## Reproduced fault witnesses

For old check 5, the two histories are a Z idle on $D_{16}$ and ZZ after the final `CX(D12,D15)`, or a Z idle on $D_{17}$ and ZZ after the final `CX(D10,D11)`. In diagnostic $V$ coordinates these yield $Z_{D12}Z_{D15}Z_{D16}Z_{A3}$ and $Z_{D10}Z_{D11}Z_{D17}Z_{A3}$. Both have zero flags and meter bit, zero data-Z and cycle syndromes, negative data-X checks 4, 7 and 8, and negative star at vertex e. The product is $\bar Z_0 S_4^Z S_5^Z$. Each branch has conditional probability one and the independent tableau restores both encoded Bell pairs and the graph with its own correction. Their difference changes a Bell stabilizer, so one correction cannot restore both. These histories each use an idle location. The saved noisy pilots used zero idle infidelity.

The positive witness in the old circuit uses $X_s$ after `CX(s,A0)` inside the first nonroot block. At the flagged branch with meter bit zero, data bit 6 and cycle word 71, cycles reduce the logical alternatives $\{0,2\}$ to $\{2\}$ even under the assumed outside envelope. The Bell tableau gives branch probability $1/4$.

The new circuit has no data-to-data CX or `CX(s,A0)`. The old collision record has an empty class set under the new two-fault lookup. A reachable replacement graph witness uses $X_{A0}X_{D6}$ after the first `CX(A0,D6)` of check 5. Its branch has zero flags, meter bit one, and cycle word 71. Under the two-fault isolated lookup, cycles reduce four logical classes $\{0,4,8,12\}$ to $\{8\}$; the independent tableau verifies both Bell pairs and the graph after correction at conditional probability $1/4$. These class integers encode logical commutation bits. The artifact gives exact operations, records and correction representatives.

## Finite audit

Each meter is audited separately over 2,327 elementary locations and 7,337 nonidentity one-location basis actions. The location list includes every live idle, prep and readout, joint measurement/report faults, individual T/T† gates, all four flags, and a terminal waiting interval on retained qubits. The propagator carries exact quadratic phases through the gate sequence and multiplies the phase operators in physical order. The signed Fourier support is mapped to syndrome/meter and logical bits only after coherent propagation. Distinct compatible logical classes reject. This support criterion also supplies a common correction for arbitrary coherent combinations within an accepted class. Equal report counts are unweighted support counts.

| Outer check | Unflagged two-fault queries | Unflagged saved by cycles | Flagged two-fault queries | Ambiguous with full diagnostics | Flagged ambiguous with outside envelope |
|---|---:|---:|---:|---:|---:|
| 5 | 60,786 | 8,175 | 16,562 | 0 | 10 |
| 6 | 60,694 | 8,169 | 16,562 | 0 | 10 |
| 7 | 60,786 | 8,175 | 16,562 | 0 | 10 |
| 8 | 60,694 | 8,169 | 16,562 | 0 | 10 |

The isolated two-fault lookup accepts the clean record as class I in every check. For check 5 it covers all 530 zero- and one-fault queries with cycles, including 42 that data alone would reject under that same two-fault budget. All 16,562 internally flagged queries per check already have a unique class with data alone. Star bits add zero unique classes for these four isolated circuits. On check 5 the old one- and two-flag direct circuits had respectively 113 and 97 ambiguous full records, including 81 unflagged each. The isolated round-trip reference also has zero ambiguous full records.

The outside test uses the same 43 block/edge/Gauss-hook cases as the hybrid audit. One current flagged fault can combine with one assumed outside error. Graph phases and the current meter bit are unrestricted for this extension. The reported 16,552 retained and ten rejected keys per check are on the internal flagged query set. The check-5 artifact includes all ten records and their competing classes. The assumed outside cases can overapproximate reachable faults. This test does not establish coverage of outside-only reports or two unflagged faults across meters.

For a cross-meter proof, one premise is available. Every coherent Pauli term from a one-location zero-flag outer fault has data support confined to one block modulo the measured X stabilizer. The independent edge X support has at most one edge. If that edge is a tree edge, the data cone is its own block. If it is a chord, the data cone is empty. The executable check verifies these restrictions on all four meters, allowing arbitrary edge Z. In diagnostic coordinates an ideal later dressed meter is a stabilizer projector. A prior Pauli component can reverse its sign through anticommutation. It cannot create a new data support or a nonzero ideal flag. This supplies a contribution to the outside envelope for earlier zero-flag outer meters. The proof still needs the two-fault compositions with noisy later records.

## Sector, recovery and original-code handoff

Graph gauging supplies the ideal measurement identity through the product of local Gauss checks. The spacetime analysis uses central commutator checks and clean cuts to control off-sector faults. Here the actual compact13 circuits and recovery history must supply the finite-size clean references. See [Non-Abelian Codes from Gauging with Graph States and Logical Clifford Measurement from Gauging and Ungauging](../../../arXiv-2602.12228v1/main.tex), [Magic Quantum Code Surgery, gauging procedure](../../../arXiv-2610.03920v1/Gauging-procedure.tex) and [spacetime analysis](../../../arXiv-2610.03920v1/spacetime.tex).

The 31 checks $Z_R,Q_R,B_f,G_{v\ne a}$ commute globally by conjugation through $V$. Measure the nine bare data-Z checks before the X record. A short bare inner-X gadget is valid in its actual positive inner-Z sector. Selecting that instrument from one noisy Z report can measure a different graph observable. In the two-data Bell+ example, a false negative ZZ report selects $XXZ_e$ and projects the edge in Z. The unconditional four-site compiler above eliminates this decision during commuting diagnostic acquisition. It does not eliminate the root sector condition.

Retain the local root observable $G_a=U_aX_{\mathrm{star}(a)}$ on four data and six edges. The group commutator of the root and $Q_R$ is $Z_R$. A complete clean Z record projects the actual Z sector, and an accepted nonzero syndrome needs a compatible correction before a root vote. For a proposed protected history, acquire complete commuting records without intervening correction or root measurements. Three identical reports supply a clean occurrence with two global faults. After an outer flag has charged one fault, two identical complete reports within four suffice for a clean occurrence under the one-remaining-fault bound. A clean occurrence can precede the last reported record. Faults after the reference, including during correction or between the final Z check and the root vote, must remain charged as a tail. A full proof needs accepted rounds in which the actual sector is restored and a clean positive root vote is guaranteed. Counting three reports as three clean votes would be invalid.

In gauged coordinates the four nonroot checks are $G_v=U_vX_{\mathrm{star}(v)}$. The bare prototype uses four W data ports and five edge ports per vertex. A graph-Z frame records known vertex and star sign corrections on the four tree edges. The applied or tracked Z reverses the intended nonroot sign and the root sign, so the corrected root/graph product has the logical $U$ sign in the code sector. Bare edge-X star meters implement $G_v$ only in diagnostic $V$ coordinates.

If the joint decoder chooses a Pauli $P$ in $V$ coordinates, the physical gauged correction is $VPV$. For nonroot data, $Z_q\mapsto Z_qZ_e$ and $X_q\mapsto X_qS_e^{-s_q}\mathrm{CZ}_{e,q}$, using $W_qX_qW_q=-s_qY_q$. Thus the latter uses one CZ, one edge S/S† and one data X. A graph $X_e$ on a tree edge carries $U_v$, four local W operations. Chord X and graph Z commute with $V$. The correction for the saved new cycle witness uses six data Zs, in same-block pairs whose tree Zs cancel, and four chord Xs. Its physical Pauli correction costs ten single-qubit gates before shortening by stabilizers. The expensive step is acquiring its reference. A software frame for data corrections would have to propagate through the root instrument as well as adjust the signs of the commuting checks.

At handoff, certify the final cycles and flatten them with chord corrections. Measure all thirteen edges in Z, decode a consistent cut using the compact13 radius-two cut decoder when its input promise holds, and apply the signed $U_v^{\eta_v}$ byproduct with the root bit fixed to zero. This is the original-code instrument on a clean cut. With faults, a bare Gauss controller can flip several incident edges. A full star is itself a cut, so zero cycle bits alone cannot license the terminal decoder. A proof must carry the correlated block/edge error and report history through cut decoding, byproduct and terminal data screen or recovery, and bound the accepted residual in the original code under the same two-location budget.

## Gate costs and decision

One new outer meter uses 28 CX, 24 T/T†, two H, five preparations and five readouts. It takes 64 serialized steps with five peak live helpers. The syndrome lives for 64 steps and the four flags for 32, 38, 38 and 38 steps, yielding 174 helper idles in the audit timing. Old check 5 uses 31 CX, 21 T/T†, two helpers with lifetimes 62 and 58, and 90 helper idles. The reference eight-site compact meter between shared V passes uses 16 CX, no T and five helpers. Its helper lifetimes are 28 and four times 14 steps. The scheduled graph preparation, rather than the new meter, sets the inherited 39-live-qubit clean-path peak.

| Data-syndrome record, excluding Gauss | CX | T/T† | Preparations and readouts, each |
|---|---:|---:|---:|
| Round trip including both V passes | 220 | 64 | 60 |
| Previous best direct | 248 | 84 | 48 |
| New direct, actual positive inner Z | 236 | 96 | 60 |
| New direct, unconditional inner meters | 268 | 160 | 60 |

Each round replaces 20 bare-star CX with 36 CX and 32 T/T† for direct nonroot Gauss. The inherited three-round costs are 2,021 CX and 412 T/T† for the previous direct circuit, 1,985 and 448 for the new positive-sector path, and 2,081 and 640 with unconditional inner meters. These are clean-path substitutions on the 1,889-CX and 256-T/T† round trip. One unconditional commuting diagnostic record costs 329 CX, 192 T/T†, 68 H and 73 preparations/readouts each, including 25 cycle CX and the bare nonroot Gauss meters. The proposed flagged recovery history therefore costs 658–1,316 CX and 384–768 T/T† before its correction gates. This prices the actual proposed acquisitions with the prototype meters. Further diagnostic protection or an extra sector confirmation would add cost.

The 200-shot matched round-trip comparison measured 94 accepted and 94 decoded target matches, at 5,459.2 CX per accepted output. Its joint-data fallback accepted the same 94 at 5,466.2 CX per accepted output. In the later pilot the tuned five-parity GHZ20 cat cost 1,126 CX and 120 T/T† on the clean path and produced 121 decoded target matches in 200 attempts, at 3,059.3 CX per accepted output. The first-vote tree4 and direct flagged-U pilots used 1,123 and 1,129 clean CX with 101 and 93 accepted out of 200. The noisy runs include retries and use a stochastic gate/report model with zero idle noise. This experiment establishes a local improvement over the old direct meter. The gate counts and conditional recovery cost give no case for displacing the cat on the current schedule. See the [joint comparison](../../../output/cz-joint-graph-data-200-20261119/comparison.md) and the [tuned cat pilot](../../../output/cz-review-noisy-200.asMApC/cat-five-parity-run/cat-five-parity/summary.json).

The completion construction would add one qubit and one pinning check per noncommuting pair. Here there are nine root/dressed-X pairs, with central labels $Z_R$ of total weight 52. Orienting conflicts from the root adds nine CX and nine ports to the root. Computing, controlling via CCZ, and uncomputing each endpoint parity adds 158 CX and 63 T/T† across the data X checks. Standalone pinning checks add 106 CX and 63 T/T†, or 54 CX and 63 T/T† incremental when sharing unflagged central-Z parity readouts. These are unprotected elementary counts before fault-tolerant flagging, for one specific completion circuit. The root couples to 19 targets under this orientation, so the route does not meet the four-data-plus-incident-edges constraint. See [Commuting-check gauging, section S1.2](https://arxiv.org/html/2611.12236v1#S1.SS2).

## Reproduce and extend

```sh
py=/Users/kevinhemery/pytket-venv/bin/python
audit_dir=$(mktemp -d /private/tmp/cz-direct-ports.XXXXXX)
"$py" -B verification/single_block_cz/check_single_cz_hybrid_study.py --output "$audit_dir/ideal.json"
"$py" -B verification/single_block_cz/check_single_cz_hybrid_faults.py --checks 5 --routes hybrid,hybrid_two_flags,reference --output "$audit_dir/old-faults.json"
PYTHONPATH=src/single_block_cz:verification/single_block_cz "$py" -B -m pytest -p no:cacheprovider -q tests/single_block_cz/test_single_cz_hybrid_faults.py
"$py" -B verification/single_block_cz/check_single_cz_direct_outer_ports.py --output "$audit_dir/direct-ports.json"
```

The exact gate lists, class counts, Bell witnesses and source hashes are in the [saved audit](../../../output/single-cz-direct-outer-ports.json). Use `--checks 5` for the smoke run. The remaining work is to compose faults across outer, inner, cycle, Gauss and feedback meters, including late faults and incorrect reports. The confined outer cones and commuting reference family give interfaces for that proof. Joint recovery must then be tested through destructive handoff and the terminal residual bound before any accepted-output comparison is meaningful. The repository has proofs for the [round-trip root recovery](../current/single_block_cz_graph_assisted_root_recovery_proof.md), [joint graph/data fallback](../components/single_block_cz_joint_graph_data_recovery_proof.md) and [compact Pauli meters](../components/single_block_cz_compact_checks_proof.md).
