# Proof: persistent gauging coordinates and intrinsic terminal protection

The physical schedule is specified in the
[integrated note](single_block_cz_persistent_coordinates.md) and compiled
by `SimulationController.gauging_persistent`, version 2. This is a new
composition proof; merely deleting V passes or the terminal screen from
the earlier schedule would not have this guarantee.

## Theorem and assumptions

Use the signed [[20,2,6]] source/logicals, normalized W involutions,
individually compiled T/CX/Tdg interactions, and the original elementary
location model. Classical processing is reliable. Up to two faulty
locations in the **entire executed attempt** may have arbitrary local
quantum action on their participants and an environment; faulty physical
measurement locations may also misreport. Preparations, resets, every
one- and two-qubit gate, corrections, retries, fallback records and all
serial/boundary idles share that budget.

For tree4, compact13 or current20 under the persistent schedule, every
accepted output is in the correctable physical weight-at-most-two operator
span acting on encoded CZ_magic. Its decoded logical state is exactly
CZ_magic. Ideal success is 3/4. There is no claim of perfect fidelity for
unbounded-fault stochastic trajectories, nor a threshold or preservation
of the old gauged-code spatial distance for tree4.

The proof uses the independently checked prior source, resource-meter,
ordinary Pauli-check, code-decoder and flag-recovery lemmas:
[source/physical proof](full_procedure_single_block_cz_proof.md),
[recovery history](single_block_cz_simulation_recovery_proof.md),
[flag recovery](single_block_cz_flag_dependent_recovery.md),
[compact checks](single_block_cz_compact_checks_proof.md).
New graph/root/initial-entry premises are certified in
`check_single_cz_persistent.py`. Full-factory location pairs are not
enumerated; arbitrary-fault composition is analytical.

## Lemma 1: coherent correction and the exact ideal instrument

Let C_A prepare the graph, Omega=prod_v controlled_(a_v)(U_v), and
V=prod_(v>0) controlled_(A_tree(v))(U_v). The physical U_v are disjoint
products of normalized one-site Clifford involutions. On a constrained
resource word |t,dt>, V Omega acts on every block by exponent t_a:

    V Omega |t,dt>|psi> = |t,dt> U^(t_a)|psi>.

All root edges are (a,v). V commutes with vertex H/MZ operations, which
act on disjoint vertex registers, and with reported-sign Z corrections
on its edge controls. Consequently it may be executed before vertex
readout. This is the coherent edge-controlled form of the same ungauging
byproduct, not an extra application of U after measurement. Destructively
measured vertices are not assumed available for inverse enrichment.

The two controlled W gates on any nonroot data target have exact product

    T^-s X^edge T^s T^-s X^vertex T^s
      = T^-s X^edge X^vertex T^s.

The generator emits the four elementary gates in execution order. All
sixteen sign/control/target basis cases are checked with exact monomial
phases modulo eight, not up to a control-branch phase. It uses 36 CX and
40 T/Tdg, including the root block's single-control ports.

For vertex report s and any cut edge word d eta, eta_a=0, the two terms
t=eta and eta+1 give projector numerator I+(-1)^|s| U. The root-edge Z
feedback cancels the eta-dependent sign (-1)^(s dot eta). Source and
measurement normalization therefore give fixed-record Kraus operator
P_x/16 and probability <psi|P_x|psi>/256. There are 32 vertex vectors,
16 cut words per vector, and 16 vectors of each parity. For logical ++,
positive record probability is 3/1024, negative is 1/1024, summing to
3/4 and 1/4 respectively. The exact certificate enumerates all 512
joint branches for each graph. Subsequent ideal Gauss certification
retains exactly the positive branch.

Arbitrary graph phases replace the two coefficients in the I/U expression
by arbitrary graph/environment-dependent coefficients. They do not create
an additional logical direction. This source-specific invariant is
essential: measuring U=+ on arbitrary logical input is not a magic-state
preparation theorem.

## Lemma 2: initial faults have the charged block envelope

The resource verifier uses three all-zero L_e scans. Under two faults,
one accepted scan is clean and projects onto span{|t,dt>}; arbitrary
phase support remains. The independently audited resource-to-meter
directions give at most one resource bit discrepancy per later fault.
The same shared resource/source retry bound applies. None of this uses
cut distance or cycle decoding. The constraint rank is E and the cut
subspace dimension is 32 for every graph under consideration.

The fused gate network separates into five components: component v
acts on its four data qubits, its vertex a_v, and (for v>0) its root
edge. No component's controls are used for another block. Every
elementary gate fault has a forward participant cone in one such
component. The certificate checks all 76 gate cones. Waiting data/control
faults have the same bound, or are graph-only. Incoming resource bit X
on a vertex or tree edge belongs to one component; arbitrary control Z
strings commute with the entire fused network. Thus one charged initial
fault introduces at most one whole-inner-block algebra, with arbitrary
graph/vertex/environment factors. Two faults may involve eight physical
data sites, and are not replaced by a distance-six weight-two argument.

The existing signed source proof supplies the same input block envelope.
Conjugating an operator on a component through this network retains its
data support in that block. Vertex readout/edge sign feedback may reweight
the I/U coefficients but introduce no additional data component. Expanding
the resulting one/two-block algebras in Paulis gives precisely the
envelope of the existing unique-class code decoder. A syndrome whose
compatible two-block errors differ logically still rejects.

## Lemma 3: transported root support and ideal action

In V coordinates the measured operators are the eighteen bare data
checks, four nonroot X stars, and

    Q = V G_a V = U Xstar_a.

The edge identity Xstar_a=prod_(v>0) Xstar_v holds globally, independently
of cycles. Root-edge Z feedback changes exactly the intended nonroot
star sign, so a fault-free star sequence sets Xstar_a=+.

The root program measures Q by twenty controlled W ports with the
existing rolling flags, followed by the incident graph CXs, then X
readout of its controller. The flag pairs cancel ideally. It is the
signed product-Q projector, not a deterministic U application.

For arbitrary local faults at the separately listed T/CX/Tdg locations,
use the existing opaque-port normal form: a target fault is a one-site
operator algebra, and a controller X component appends the appropriate
local W to later data ports. Phases remain arbitrary conditioned
coefficients; no Pauli XOR through T is assumed. The finite certificate
retains unrestricted graph factors and checks, modulo the full Q:

* one zero-flag fault has data support <=1;
* two faults with cancelling flag vectors have data support <=2.

There are respectively 1,315 / 1,747 / 2,251 accepted equal-flag support
pairs for root degrees 4 / 6 / 8. Same-location pairs are conservatively
overincluded. All data/graph port idles, preparations, flag readouts,
controller readout/report actions and each elementary coupling are
included. Spectator edges are graph-only; spectator data are among the
twenty data ports. Graph ports occur strictly after the last data port;
a graph-tail fault creates no forward data hook. A root flag rejects
after completing helper readouts. It never invokes a Pauli-data decoder.

This lemma allows arbitrary graph support, not one edge per fault. The
remaining data checks and conditional recovery use their existing
physical-site and unique-class certificates unchanged.

## Lemma 4: a clean passing round certifies the desired line

Before certification, the conditional state is a sum of charged block
errors acting on alpha|++>+beta U|++>, with arbitrary graph coefficients.
This invariant is closed under ideal graph operations and root projection:
U is a product of one-site Cliffords, so U E U has the same block support
as E, and U interchanges the two source directions. Bare code projectors
select error syndromes. A certified unique-class correction restores
that source span or rejects, by the existing recovery proof.

In a fault-free complete passing round, data code restoration is honest,
all four stars are repaired, and the root report is honest. In the
restored code sector Q reduces to logical U, whose positive projector
maps both source directions to the same nonzero CZ_magic line. The data
therefore factor from the graph/environment as that line. A genuine
negative 11 branch has zero amplitude in this passing clean event.

Root and data checks are not treated as globally commuting projectors.
The full-code restoration occurs before the graph/root step, and
commuting-history rules are used only inside their original bare-Pauli
acquisitions. Three passing complete rounds among at most five contain
a round with no faulty location, because the entire schedule has at most
two faults. Failures inside an adaptive fallback belong to their enclosing
round; they do not create a fresh allowance. The finite passing-record
audit checks the stopping rule and every placement of up to two bad
rounds. Two wrong reports cannot certify a genuinely negative branch.

## Lemma 5: physical-site closure after the last clean passing round

Let |M> be the certified encoded CZ_magic state. For any graph state
|chi>, graph operator R and physical error E, an ideal root projector
acts as

    P_b(Q) (E|M> tensor R|chi>)
      = [ E|M> tensor R|chi>
          + (-1)^b (U E U)|M> tensor Xstar_a R|chi> ] / 2.

U|M>=|M>, and local Clifford conjugation preserves each physical error
site. Hence this identity preserves the entire fixed-site error algebra,
even when graph and data errors are coherently correlated. Ideal graph
operations act only on the graph. Ordinary Pauli checks do not spread
incoming data errors between sites. Lemma 3 adds at most one physical
data site per new zero-flag fault, with two-fault cancellations covered.
Multiplication by Q in that normal form is harmless by this same identity.

A flagged Pauli-data gadget instead invokes the unchanged conditional
decoder. Its envelope includes its exact gadget fault and a possible
other one-block fault; a unique-class correction preserves the unknown
logical state. Faults after its clean reference add one physical site
each. Pauli correction gates do not spread those sites. This is the
existing flag-recovery composition argument with the global budget,
not an assumption that every flagged hook itself has small weight.

Choose the last clean passing round. Its output is |M> tensor a graph
state. Every subsequent accepted operation satisfies the preceding
physical-site closure, including further rounds and their fallbacks.
No subsequent V or graph-controlled data correction occurs. Therefore
the final state lies in the weight<=2 physical operator span on |M>.
Destructive graph readout, even with wrong reports or arbitrary local
fault action, only conditions/traces its graph/environment coefficients.
Waiting-data and final-boundary faults remain charged single-site faults.
The distance-six code corrects that entire coherent span by Knill-Laflamme.
This proves the theorem without an extra terminal measurement family.

## Why tree4 is admissible, and what it does not claim

The proof requires a connected graph with the four root edges, independent
resource constraints and four independent nonroot stars. Tree4 meets
these requirements with E=4, the minimum for five connected vertices.
The graph's E-4 auxiliary degrees may be arbitrary; tree4 has none.
There is no noisy cut-word inference and therefore no radius-two cut
distance hypothesis. The old `Graph.validate()` distance requirement is
unchanged; a separate persistent-mode validator prevents a drop-in
substitution into the old schedule.

This is a fault-cone and accepted-output theorem, not correction of every
unknown eight-site error or a claim that the old gauged Hamiltonian has
distance six on this graph. Some two-block syndromes still reject. The
tradeoff is a less-local root measurement: twenty data targets rather
than four. Hardware routing and noise thresholds require separate work.

## Explicit failed shortcut and restricted representation audit

Keeping U_a Xstar_a after moving to V coordinates is incorrect. With
graph stars positive, the expectation of U_a on each encoded computational
basis state is 1/2. In particular it reports positive on genuine logical
11 with probability 3/4. The certificate computes this exactly on all
512 X-stabilizer words per logical coset. It is a counterexample to that
single-observable shortcut, not an asserted full-factory trajectory.

The certificate also searches all 512 X-stabilizer supports for the
necessary bilinear CSS conditions of a diagonal-S/Pauli-stabilizer
involution implementing logical CZ. Only the all-twenty odd-S support
survives. This rules out a support reduction within that restricted
family, not every possible physical logical-CZ circuit. It motivates
changing coordinates/certification rather than dropping W factors.
