# Candidates for substantially higher acceptance

The numerical baseline here is the retained `--magic-output z` profile.
The [Y-output extension](magic_y_preparation.md) changes the ideal acceptance
benchmark from 5/8 to 3/4; its noisy performance needs separate assessment.

The current procedure is not known to be close to optimal. The earlier
work optimized conservative gadget implementations and stopping rules;
the principal recovery decoder is still a static two-matched-block lookup.
Large gains would require changes to recovery information and control
flow, or to the error-correction architecture, rather than only a few
more gate cancellations.

## Evidence from the latest combined-noise run

At two-qubit infidelity 10⁻³ and independent readout flips of probability
10⁻³, compact extraction accepted 8/50. All eight decoded exactly in
this sample. The [headroom audit](../output/c4-helix-acceptance-headroom-audit.json)
and [full comparison](../output/c4-helix-compact-terminal-comparison.json)
identify:

- 18 attempts stopped at absent or ambiguous terminal correction candidates.
- Only 10 reached final B selection: eight accepted and two selected B one.
- There were 35 protected terminal restarts among 54 reached terminal stages.
- There were 25 extra gauging cycles beyond the first cycles.
- Across fifty attempts, 1,037 sampled gate/readout faults occurred.

Thus the global two-fault theorem is a correctness certificate for an
important limiting case, not a description of typical stochastic fault
counts at these rates. Nor do eighteen decoder failures mean eighteen
recoverable states: some histories can be genuinely ambiguous or the
logical resource may already have been damaged.

The ideal acceptance benchmark remains 5/8. The current 16% observation
does not establish a fundamental limit near that value.

## 1. Best next investment: history-aware, repeated recovery

Use the sequence of individual syndrome and flag measurements, the gates
between them, readout-flip possibilities, and their correlations. Track
candidate fault paths and logical classes. The present decoder uses one
selected vector and assumes the accumulated error fits two common blocks;
it can miss recoverable errors distributed across several times.

The goal is genuine repeated error correction, removing or tracking
errors before they accumulate, rather than repeatedly measuring a large
family until a record is selected and making one broad final correction.
Start in the Clifford Pauli-recovery segments after ungauging. Extending
through Fredkins and non-Pauli Gauss checks requires a different argument
from an ordinary binary detector-error model.

A bounded-fault certificate must include all compatible low-fault paths,
not just the most likely one. Probability-weighted decoding and a
confidence threshold can then address the unrestricted-noise regime,
with accepted-output fidelity measured separately. The original C4-Helix
paper already uses circuit-wide decoding and confidence-based selection;
our implementation has not reproduced that decoder. See
[its Appendix C](https://arxiv.org/abs/2609.03194) and the flag/time-decoder
tools of [Pato et al.](https://arxiv.org/abs/2306.12862).

This targets the largest direct rejection category. A factor-of-two yield
gain is a meaningful experimental objective, not an established prediction.

## 2. Stop paying for full restarts when the record permits local recovery

The compact controller conservatively invokes protected recovery on every
nonzero flag. A local follow-up audit finds that some upper-check nonzero
flag vectors already have the same physical-weight-per-fault bound as
zero flags, without a preliminary repair. Ten of the 35 observed restarts
had such vectors. The audit checks X and Z and every merged one-/two-fault
path, including false flags; the controller has not been changed here.

More generally, use flags to select a small follow-up measurement set or
to constrain recovery, keeping the other acquired information. This can
avoid restarting all 36 original-code checks. It should be developed
with the history decoder, rather than justified by assuming a flag locates
every error perfectly.

The larger extension is correcting an error while the data remain gauged,
avoiding another graph preparation and gauging/ungauging cycle. That
requires proving preservation of the logical sector and handling ambiguity
about which copy was damaged. Measuring arbitrary original-code checks
while gauged is not valid. This is harder than terminal recovery, but
the 25 observed extra cycles make it a substantial target.

## 3. Larger gadget redesign: encoded-ancilla error correction

Steane-style correction uses a suitably prepared encoded auxiliary block
and transversal coupling to extract many syndrome bits together. Knill-style
correction instead teleports into a fresh encoded block while extracting
recovery information. Either can be used before/after the present gauging
and ungauging, rather than replacing that operation by a direct SWAP test.

For a twenty-qubit CSS block, a transversal coupling is twenty CNOTs.
Two bases on both B and C therefore have eighty data–ancilla CNOTs,
before counting auxiliary preparation, verification, and any repetitions.
Those additional costs are essential; eighty is not a full recovery cost.

Known auxiliary states can be prepared and retried separately. Their
readout has spatial code redundancy, offering a different way to handle
meter noise than long cat-parity histories. The tradeoffs are additional
qubits, potentially costly auxiliary verification, and a new compositional
proof. Auxiliary preparation failures must still count in resources per
useful output, even when they do not discard the retained data.

[Experimental Steane QEC](https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.5.030326)
demonstrates that this is a substantive alternative to flag-based extraction,
not evidence that it will automatically outperform our particular factory.
Its suitability and sparse-simulation cost need to be checked here.

## How to decide which direction can deliver a large gain

First perform a diagnostic study of rejected trajectories: how many still
contain a correctable logical resource, as opposed to information already
lost by noisy measurements or logical errors? A state-aware or fault-aware
oracle may be used to estimate recovery headroom in this diagnostic, but
must never be used by the implemented controller to accept or correct.

If recoverable headroom is large, invest first in the full-history decoder
and selective recovery. If even an ideal diagnostic recovery has little
headroom, move to encoded ancillas, better gauged recovery, or other changes
that prevent damage. This test avoids mistaking a poor decoder for a
fundamental circuit limitation, or trying to decode information that has
already been irreversibly lost.

Compare acceptance at a specified accepted-output error target and count
all auxiliary retries and extra recovery work. No current experiment proves
that high acceptance with high fidelity at the target rates is impossible,
and none yet establishes a large-gain replacement.
