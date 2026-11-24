# Hybrid fault distinguishability: graph information helps both constructions

This follows the [hybrid circuit study](single_block_cz_hybrid_study.md).
It implements the next proposed step: enumerate elementary-gate fault
signatures, retain their coherent T phases, and test joint data/graph
correction decisions. It is not a full-factory proof or noisy benchmark.

The positive result is concrete: graph information resolves some hybrid
fault histories that data-only recovery cannot resolve. The comparison
also finds graph-assisted recoveries in the coordinate-change circuit.
The hybrid has remaining ambiguities, including actual distinct Pauli
histories, so this audit does not establish a hybrid acceptance advantage.

## Precisely what is audited

The input is any encoded two-logical-qubit state and the standardized graph
state. The four outer generators use the optimized (1,3,4,8) basis from
the design study. Each generator is audited SEPARATELY, with up to two
faulty locations in its entire isolated circuit, including preparations,
each T/Tdg, each CX, each H/X, measurement quantum faults and wrong reports,
all live-qubit waiting locations and a final retained-qubit boundary.

There is NO fresh allowance at each stage of an isolated circuit. However,
four separate isolated audits are NOT a proof for a factory with faults
distributed across several meters. Recovery gates, noisy final diagnostics,
inner-sector selection, history certification and factory boundaries are
not included in this finite certificate.

The three extraction circuits are:

* `hybrid`: the direct dressed outer check with one syndrome-control flag.
* `hybrid_two_flags`: an additional overlapping block-window flag. Its
  windows cover block ports (0,1) and (1,2), respectively.
* `reference`: V, a current compact eight-data Pauli check with four flags,
  then V again, for the SAME dressed generator as the hybrid.

The reference V passes are normally SHARED across a complete record.
The isolated circuits here are used to compare error distinguishability;
their location counts must not be summed over four checks as factory costs.

After each faulty meter, the audit assumes IDEAL commuting diagnostics:
eighteen data checks, nine cycles and four nonroot stars in V coordinates.
All decoders also retain the current meter's reported parity and all flags.
The three information levels differ only in whether graph-cycle and graph-star
bits are retained. A mathematical V representation is used for the analysis;
this is not a physical coordinate pass secretly inserted into the hybrid.
Physically extracting these diagnostics in the gauged frame entails the
dressed checks and Gauss operations discussed below.
Known software graph-Z frames would be removed from the star/Gauss signs
before lookup. They commute with these outer dressed-X observables, whose
edge decorations contain only Z. This audit starts in the standardized
frame; it does not add source-logical-X measurements to a magic factory.

## Coherent fault calculation and accepted-class rule

Between the syndrome's initial and final H gates, all candidate programs
are CNOT/T/Tdg/X circuits. A propagated elementary Pauli fault has the form

    E|y> = zeta8^c i^[l.y + 2 sum_(i<j) A_ij y_i y_j] |y XOR x>.

The implementation retains c, all signed S coefficients l modulo four,
the binary quadratic form A and the fixed translation x. Two faults are
composed as these coherent operators, including translation of the later
quadratic phase. They are NOT XORed as Pauli errors through T gates.
Initial/final helper H gates and readout/report differences are handled
explicitly. Unused measured flags can be deferred algebraically because
they have no later coupling; operational live-qubit idles still follow
their actual destructive measurement times.

After fixing flag inputs to zero, the Fourier support of the diagonal
Clifford phase gives an exact affine set of Pauli-Z terms. If B has A
off diagonal and l mod two on its diagonal, that support is z0+image(B).
For every r in kernel(B), its affine constraint is

    r.z0 = (sum_i l_i r_i)/2 + sum_(i<j) A_ij r_i r_j  mod two.

The numerator is even for kernel vectors. These signed constraints retain
the phase cancellations that determine which Pauli terms actually exist.
The current reported parity is the Fourier bit on the syndrome helper,
XOR its explicit possible report flip. Logical labels are obtained only
AFTER this coherent calculation.

Every affine class image is enumerated. A decoder accepts a report only
if ALL compatible Pauli terms and fault histories have one data logical
class modulo code and graph stabilizers. Allowing arbitrary coefficients
within these supports is conservative; it can reject a known coherent
Clifford error that a more specialized recovery could invert. Such a
rejection alone is not an information-theoretic impossibility result.

For 33 retained data/graph qubits, the diagnostic/logical class map has
rank 35. Its rank-31 kernel equals the data/graph stabilizer span. Thus
the unique-class rule supplies a Pauli correction for every coherent
linear combination in its accepted family. This gives an arbitrary-local-
fault extension for the DECLARED isolated circuit with ideal diagnostics,
not a claim about the omitted factory operations.

Independent tests check integer phases against direct basis evolution,
all 512 three-variable diagonal-Clifford Fourier forms by exact integer
Gauss sums, signed helpers, and the two-flag ideal circuit on all involved
basis inputs. A second representation uses signed stabilizer tableaus to
verify physical witnesses. Each logical input is entangled with a reference
qubit: restoration of both encoded Bell pairs checks preservation of
unknown logical information, not just a known stabilizer source.
The Bell-pair stabilizer checks are classical verification on the audit's
tableau, not additional physical logical measurements in the protocol.

## Results

For representative outer check 5:

| Extraction | Modeled full flagged report tuples | Unresolved using data only | Unresolved after cycles | Unresolved after cycles and stars |
|---|---:|---:|---:|---:|
| Hybrid, one flag | 29,042 | 2,912 | 64 | 32 |
| Hybrid, two overlapping flags | 37,352 | 2,792 | 16 | 16 |
| Shared-coordinate comparator | 22,750 | 16 | 0 | 0 |

Columns within each row classify the SAME full report universe with
progressively more information. These are unweighted support-model tuples,
not shots, physically sampled frequencies, conditional probabilities or
acceptance rates. Different extraction circuits have different report
spaces and numbers of flags; their raw tuple counts must not be compared
as probability estimates. Some support tuples can cancel on a particular
input, which only actual witness calculations resolve.

All four outer checks were audited. The one-flag hybrid has 32 remaining
flagged ambiguities for each check; the two-flag version has 16; the
reference has none in this isolated ideal-diagnostic model. In addition,
both hybrid versions retain 81 ambiguous UNFLAGGED tuples per check,
whereas the reference has none. Clean zero records have only logical
class I for every audited circuit.

The extra controller flag therefore helps but does not solve the hybrid's
data-hook problem. This is a local recovery improvement, not a factory
yield result. In particular, the production decoder does not yet implement
these isolated lookup tables or a certified history that supplies their
ideal diagnostic reference.

## A real recovery enabled by graph information

The conservative outside-cone check below supplies a simple witness:
one faulty CX(s,A0) inside the first nonroot block port applies X_s after
that elementary gate. Its reported flag is one and current meter bit zero.
A branch has data syndrome bit 6 set (all other eighteen-data bits zero),
cycle word 71 (cycle bits 0,1,2,6 set), and zero star-sign bits.

Without cycles, compatible histories require two distinct logical
correction classes. With cycles, one remains. An independent tableau
calculation gives this branch conditional probability 1/4 and verifies
restoration of both logical Bell pairs and the graph after its Pauli
correction in V coordinates. The probability is CONDITIONAL on the
specified fault, not a factory success probability or its occurrence rate.

This example uses a CNOT Pauli fault with nonzero probability in our actual
depolarizing convention; it does not rely on the currently disabled memory
channel. Saved witnesses include the exact elementary instruction, fault
participants, reports, diagnostic syndrome and a correction representative.
Other witnesses contain two actual gate faults and retain the coherent
phases produced inside CCZ decompositions.

## A surviving genuine ambiguity

The audit also found two Pauli histories with zero flags and current meter
bit zero. In the diagnostic V coordinates their errors are

    E_A = Z_D12 Z_D15 Z_D16 Z_A3,
    E_B = Z_D10 Z_D11 Z_D17 Z_A3.

The first comes from an idle Z fault on D16 and a ZZ fault after the data
CX(D12,D15); the second uses an idle Z on D17 and ZZ after CX(D10,D11).
Both are actual two-location histories, not two formal components of a
single coherent expansion. They have the same complete diagnostic record:
data-X checks 4,7,8 are negative; all data-Z checks and cycles are positive;
the e-star is negative. Their difference is

    E_A E_B = Z_D(10,11,12,15,16,17) = Zbar_0 S_4^Z S_5^Z.

No single Pauli correction selected from this record can correct both.
Logical Zbar_0 also commutes with logical CZ, so another CZ-sector vote
after restoring the code does not identify this ambiguity. The extra
syndrome-control flag does not see it: the relevant hooks arise in the
data-parity circuitry. Protection or location information for those
operations is needed; extra controller flags alone are insufficient.

This particular witness uses an idle fault, whose stochastic rate is zero
in the current benchmark. It is a robustness/proof obstruction under our
specified arbitrary-idle-fault contract, not evidence of an observed
acceptance loss at zero memory noise. Faults in other factory stages and
their histories remain to be analyzed.

## Conditional outside-cone stress test

A separate optional audit allows one current flagged-meter fault and one
outside target error BEFORE ideal diagnostics. It assumes 43 conservative
block/edge/Gauss-hook cones, arbitrary graph Z action and arbitrary current
meter parity. These assumptions include known block/tree correlations and
direct nonroot Gauss controller suffixes; they are NOT a proven classification
of every location in the complete new factory.

On check 5's previously modeled internal report tuples, joint information
reduces unresolved cases from 5,330 to 1,582 for the one-flag hybrid, from
3,776 to 1,024 for the two-flag hybrid, and from 42 to 10 for the comparator.
The graph benefit therefore survives this deliberately broad target-error
envelope. Graph-star gains vanish here because arbitrary graph phases
were allowed. This says nothing about the value of star information under
a tighter physical fault model.

Outside-only report tuples are not included in these scores. Their affine
class unions are constructed, but scoring is restricted to the common
internal-query set. No noisy diagnostic reports, late recovery faults or
whole-record factory acceptance decisions are certified by this extension.

## Correction to the earlier hybrid resource budget

I previously treated nonroot graph-star extraction as unchanged. That was
incorrect: it is bare only in V coordinates. Staying gauged requires
G_v=U_v Xstar_v. Direct bare-controller implementations cost 36 CX and
32 T/Tdg across compact13's four nonroot vertices, compared with 20 CX
and no T for bare stars in the reference. Their ideal signed action is
now checked independently on 4096 basis cases. Their new block-hook
recovery still requires a fault-tolerance proof.

Consequently, the earlier 1973-CX / 316-T hybrid schematic becomes an
optimistic **2021 CX / 412 T/Tdg**; the two-flag version is **2045 / 412**.
The current local-Gauss reference remains **1889 / 256**. These are still
not matched-guarantee factory budgets: protecting sector selection and
diagnostics, and compiling gauged recovery, can add work. Retaining V
for the graph stars instead is a valid ideal option but restores the
coordinate changes we were trying to avoid.

## Reproduce

All commands work from any directory and launch no stochastic campaign:

```fish
/Users/kevinhemery/pytket-venv/bin/python /Users/kevinhemery/quanti/top-order-lit-rev/verification/single_block_cz/check_single_cz_hybrid_faults.py --routes hybrid,hybrid_two_flags,reference
```

This writes `output/single-cz-hybrid-fault-distinguishability.json`, including
complete class-union statistics and independent reachable recovery/ambiguity
witnesses. For the outside-envelope stress test:

```fish
/Users/kevinhemery/pytket-venv/bin/python /Users/kevinhemery/quanti/top-order-lit-rev/verification/single_block_cz/check_single_cz_hybrid_faults.py --checks 5 --routes hybrid,hybrid_two_flags,reference --outside-envelope --output /Users/kevinhemery/quanti/top-order-lit-rev/output/single-cz-hybrid-fault-robustness.json
```

The implementation is `src/single_block_cz/single_cz_hybrid_faults.py`;
tests are `tests/single_block_cz/test_single_cz_hybrid_faults.py`. Saved
source hashes are checked for stability during each complete run.
The current factory controllers and benchmarks are unchanged.

The practical conclusion is to retain joint graph/data decoding as a real
recovery opportunity, INCLUDING for the coordinate-change reference. The
hybrid still needs protected data-parity operations, actual dressed Gauss
extraction and a global history/recovery proof before a 200-shot factory
benchmark would have a defensible accepted-output interpretation.
