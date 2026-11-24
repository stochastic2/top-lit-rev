# Proof: conditional joint graph/data recovery

This proves the [specified conditional branch](single_block_cz_joint_graph_data_recovery.md)
for the existing **round-trip** circuit. It uses the signed source/U/V,
source/graph preparation, flag-dependent recovery, bare-star and terminal
lemmas of the [local-Gauss proof](../current/single_block_cz_graph_assisted_root_recovery_proof.md).
It is an extension proof, not a new independent audit of those unchanged
upstream stages. Persistent and two-block SWAP proofs are not substituted.

## Extension theorem and model

Under those existing lemmas, adding `--joint-recovery fallback` preserves
the contract: with at most **two arbitrary faulty locations globally**,
every accepted output decodes to `(00+01+10)/sqrt(3)`, with residual error
in the correctable physical weight-at-most-two Pauli span. Every old
accepted quantum path is retained.

Locations are physical PREP/reset, each H/Pauli/S/Sdg/T/Tdg, each CX,
destructive MZ with its report, and each one-qubit waiting/boundary idle.
A fault acts arbitrarily on its listed participants; a measurement fault
can alter both quantum action and report. Classical processing is reliable.
T, CX and Tdg in controlled-W are separate locations. Corrections,
conditional records, failed resource attempts and helper reuse all share
the two-fault budget.

The finite certificate covers local spread and all generated class-table
decisions. Stage-to-envelope mapping and history/terminal composition are
analytical. We do **not** enumerate full-factory location pairs.

## 1. Trigger and remaining budget

In a fault-free attempt the source is in the code, and graph preparation,
enrichment, vertex frame and V map data back into that code in V coordinates.
Both logical U sectors remain there. Ideal accepted earlier corrections
restore a stabilizer class. The old protected eighteen-bit reference is
therefore zero unless a fault has already occurred.

The new branch starts only after that reference selects a nonzero syndrome
with multiple data-only logical classes. No quantum operation intervenes
between its completed acquisition and the branch. Even a falsely nonzero
report spends a location. At most one fault remains in the new history
and later work. No block identity is inferred from this fact.

## 2. Complete typed envelope

At a clean reference in V coordinates allow arbitrary graph Z. Let C(g)
be the cycle-Z syndrome of graph-X mask g, and t_v the root-tree edge of
block v. A block algebra is the full algebra on four sites, not weight one.

| Type | Data algebra | Graph-X cycle word |
|---|---|---|
| A_v | Full block v, including a | 0 |
| B_v, v=b..e | Full block v | C(t_v) |
| C_e | Identity | C(single edge e) |
| D_v,j | Identity | C(suffix j of incident-edge order at nonroot v) |
| Identity | Identity | 0 |

These are `external_cases` from the root proof. Compose them in pairs,
including identity: allow the full algebra on the union of their data
blocks and XOR of cycle words. Cycle words are Pauli graph-X parities;
this is **not** Pauli-XOR propagation through T.

The stage mapping is explicit:

* A clean source reference removes raw encoder hooks; its accepted tails
  obey the established one-block cone per fault. A clean graph parity
  reference removes raw resource bit patterns; surviving phases give
  arbitrary graph coefficients and source I/U branches. Its late resource
  bit faults enter the following edge cones.
* Enrichment and vertex faults act on their own data block (A). V controls
  and tree-edge bit faults have their own block/edge correlation (A/B).
  Data target faults can add control Z, not an unrelated graph X.
  Non-tree bit faults are C. Partial W hooks stay inside one block algebra.
* Accepted zero-flag ordinary data gadgets leave at most one physical
  port per fault modulo their measured stabilizer. **Two internal faults
  whose flags cancel** have a combined two-port bound; separate zero-flag
  assumptions on those two terms are unnecessary. Both compact and
  rolling local certificates establish this bound.
* An accepted zero-flag root likewise leaves at most two ports for two
  internal faults, modulo the full measured Gauss product. A root data
  port is in block a (A); a tree-edge port becomes its paired block plus
  that edge (A/B/C); a non-tree port is C. The opaque-port certificate
  includes cancelling flag pairs and physical T/CX/Tdg, preparation,
  readout/report and idle locations.
* Bare-star hooks are graph-only incident-edge suffixes, including the
  current target when appropriate (D); target/waiting faults give C.
  A star has only its own one tree edge. Across a clean V-return/root/
  V-entry sequence its associated U_v cancels. It does not become an
  arbitrary data block paired with an unrelated broad graph mask.
* A cycle meter adds at most one graph-X bit (C), though phase hooks can
  be broad. Conditional data gadgets have the one-site bound under the
  remaining-fault budget. Physical corrections and waiting idles have
  their actual one-site cones. A previous successful flag repair removes
  earlier errors at its reference; its late tails obey the same rows.

Full root-product factors must be retained: in V coordinates this product
is Q=U Xstar_a. Moving it right leaves graph operators and logical I/U
branch factors. Conjugation by U preserves each block algebra and every
graph-X cycle word. The typed envelope therefore remains closed without
discarding controlled phases or assuming U is scalar on the source.

Expand arbitrary local quantum faults on their actual participants while
retaining complex coefficients, environments and conditioning. A W hook
is coherent; its entire enclosing block algebra includes all its terms.
Disjoint exact involution hooks retain the opaque-port support bound.
Only **after** this reduction do Pauli class tables apply. Pauli-channel
sampling alone would not prove this statement.

## 3. Valid history and timing

The eighteen code Paulis and E-4 independent cycle-Z Paulis commute
globally and have rank 18+(E-4). Measurements are QND and there are no
inter-record corrections. No root or dressed non-Pauli check is included.
At most one new location can fail. Any new reported flag rejects, making
the conditional zero-flag one-site gadget bound applicable. The dual Z
program uses actual data-to-meter CXs and helper-only Hadamards.

Two identical consecutive complete records cannot both contain the one
fault. At least one is a clean occurrence of the selected value. After
the dirty record any later clean records are constant, so four records
suffice for a pair, or the implementation rejects. This argument is not
applied to the noncommuting root/data sequence.

## 4. Complete recovery decision

Each allowed block set B defines arbitrary X/Z on its sites. The class
map has eighteen syndrome and four logical commutation bits. Any fixed
set of at most two inner blocks has **no nonzero logical kernel**. This
code-specific erasure property is checked independently; distance six
alone would not justify it for eight sites.

For selected (s,c), solve every matching block-space syndrome equation
and union their logical labels. Reject zero or multiple labels. Otherwise
choose representative C with the common syndrome/class, shortened only
by stabilizers. Every compatible Pauli term E has CE in the stabilizer
group. The correction consequently works for every coherent term and
every compatible fault family at once.

The certificate independently enumerates 256 Paulis per inner block,
quotients them into 64 syndrome/class images and forms Cartesian products
for block pairs. It checks affine image equality, every family union,
all supported syndrome decisions, and stabilizer membership of each
chosen correction. Exact family/image equality excludes spurious absent
entries. There are 162 cycle contexts / 18 distinct data-family contexts
for compact13 and 684 / 17 for current20. At cycle zero, class counts
agree with the old data table on **every** syndrome.

The unique non-tree chord correction solves the full cycle parity system.
It commutes with V, all Gauss operators and the data checks. It acts on
graph only and never enacts unnoticed U_v on data. The later ordinary
star step restores four star signs. Star signs need not be in this
history because arbitrary graph Z was allowed in every candidate family.

On encoded data the resulting ideal map has only alpha I + beta U terms,
with arbitrary graph/environment coefficients. It preserves the source
I/U span, the already-selected positive magic line, and the genuine
negative logical |11> line separately. It cannot repair a negative branch
into magic.

## 5. Late faults and global composition

The selected value has a clean occurrence; its last occurrence may be
dirty. If the remaining fault is later, the decoder uses its identity
second-fault case at that reference. Planned Pauli and chord corrections
do not enlarge the late fault's support. A conditional data fault leaves
one site; a graph bit or star hook crosses V into at most its own block;
correction faults are charged at their actual participants. The next
checks must recover or reject these tails. Immediate physical weight-two
output is not claimed at this intermediate point.

Resume the same complete round. A round containing a fault in the branch
is a faulty round in the original count. Three positive complete rounds
within five still include a clean passing round. Its data restoration,
stars and local root G_a select the same magic line. Earlier votes can
remain because the accepted correction preserves both U eigenspaces;
late tails retain their original fault charge. A data-epoch increment
does not replenish the budget.

Final cycle flattening, cut decoding, physical byproducts and terminal
screen/full fallback receive exactly their established input envelope:
magic plus at most one block algebra per still-charged upstream fault.
Their existing tail lemmas, including faults after the last clean record
and final boundary, give the correctable physical weight-two span. This
proves the extension under the unchanged-stage premises stated above.

## Evidence and limits

`check_single_cz_joint_recovery.py` saves a hashed finite certificate with
cancelling two-fault root flags, compact-data local support and complete
generated class tables. It does not enumerate full-factory fault pairs.
Quantum regressions independently exercise the physical coordinate
witness, two coordinate faults, a second wrong cycle report, a late
second data idle, a rejecting new flag, a genuine negative branch and a
coherent single-location graph fault. They also check tampered classical
records and the saved-run verifier. These are numerical trajectory tests,
not an exhaustive arbitrary-fault proof. Reachable-context counts are
not probabilities; noisy benchmarking is needed to assess yield and cost.
