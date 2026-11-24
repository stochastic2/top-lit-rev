# Two-location accepted-output guarantee for the five-leaf cat schedules

For the implemented BlockCat and PostBlockCat controllers, every accepting branch with at most two faulty elementary locations has decoded output on the target CZ magic line. The proof uses the same source, decoder, participant-local fault model, reliable classical controller, and global budget across retries as the [twenty-leaf certificate](../tree4_cat_fairness/PROOF.md). Only the ordinary direct-U instrument changes. The footprint allowed before the terminal screen is measured in four-site inner blocks. After the last screen the footprint is measured in physical sites.

## Five-leaf instrument

Write V_j for the product of the four signed W operators in block j, so U is the product of the five V_j. The ideal cat controls either no blocks or all five. Conditional on a string of X readouts, the two branches have relative sign given by their XOR. The ideal data operator is therefore proportional to I+U or I−U, with exactly the sign convention of the twenty-leaf meter.

After an accepted resource check with p prefix faults, expand the ancilla into complementary computational words d and its complement, term by term, choosing the smaller word as d. Its weight is at most p. For p=0 this is the GHZ pair. For p=1 the Clifford prefix admits an exact Pauli propagation check: among all signatures with zero reported verifier parity the largest smaller word has weight one. This includes waits on the resource and helper and faulty reports. For p=2 the bound follows already from the length five. The signature check below also enumerates cancelling flag pairs. Phases and environment coefficients can differ between the two words. Linearity extends the Pauli calculation to arbitrary participant-local faults. Data waits during resource preparation are charged separately to their sites.

After the parity check, each leaf interacts only with its own block. Fix one computational input word b and the reported outcomes. For every block free of further faults its data operator is proportional to the ideal factor V_j raised to b_j. On a faulty block the conditional operator can be arbitrary on that block. Factor out its ideal factor on the right, which is possible because that factor is unitary. The resulting operator on all data is a sum of terms F times the ideal word operator, where F occupies at most r blocks for r additional faulty locations. Faulty measurements and classical report flips may change the coefficients. A common environment is allowed by expanding each local fault in a system operator basis. No product-noise assumption is needed.

The ideal word operator for either member of the pair is the product on d, possibly times global U. The product on d occupies at most p blocks. Global U preserves both the logical sign span and the positive magic line, and conjugating any inherited block error by U preserves its support. Thus on either underlying subspace J, a dirty vote with k faults maps an incoming h-block error span into the (h+k)-block error span on every report, for h+k at most two. This argument allows different F for the two complementary words.

## Composition

The preceding clean projector and dirty block bound supply precisely the ordinary-vote hypotheses in sections 3–4 of the twenty-leaf certificate. The same short syndrome checks, recovery, and inner-X sign frame apply. Three recorded positives in distinct slots imply at least one fault-free positive slot under the shared two-location budget. Its framed projector selects the underlying magic line even with inherited charged blocks. Subsequent dirty slots preserve that line with the stated support.

* **PostBlockCat.** The screen after the third positive converts the block error span on the magic line to the physical-site error span under the remaining budget, by section 5 of the certificate.
* **BlockCat.** Every slot entered with two positives starts with the inherited ordered screen and uses the original twenty-leaf finishing meter. A negative result requires a fresh screen before another deciding vote. On the accepting slot the screen supplies the site bound and the twenty-leaf meter adds at most one physical site per new fault. The same honest-positive argument fixes the magic line. Both schedules include the final single-site waits in the shared budget.

The five-leaf instrument alone has a block guarantee. For example, a leaf flip just after its first data CX changes the control on its three remaining ports. The screen placement is essential to this proof.

## Implementation checks

[The trace and signature check](check_block_vote.py) compares the elementary five-leaf circuits to the block partition and signed rotations, checks all 58 resource-prefix locations, and compares the clean hybrid deciding meter gate for gate to its certified parent. The branch rule for later deciding slots is in [the controller](block_cat_probe.py).

Additional seed-2 injections, with stochastic noise disabled, exercised both controllers. X on L2 just after the entry chain CX(L1,L2) rejected at the resource flag. Adding a flip of the helper report let the resource pass and both controllers rejected at data ambiguity. X on L1 just after CX(L1,D4) was accepted with decoded fidelity one in both schedules, injected in the first vote for BlockCat and in the deciding vote for PostBlockCat. These replays illustrate the propagation and rejection paths. The guarantee across fault locations and outcomes follows from the composition argument above.
