# An accepted two-location logical error in the screened tree4 factory

The 616-CX `ScreenTree` controller fails the proposed accepted-output theorem. Two independent single-qubit Pauli faults, each on the syndrome participant immediately after an ordinary CX, give a positive-probability branch that accepts with decoded target fidelity $1/9$. The full physical trajectory uses Born seed 4 and zero background noise. The entry vote is positive, so the optional negative-entry filter would also retain this branch. Neither fault occurs in source preparation, at the root Gauss meter, or at handoff.

## The two locations

| Location in the first routine vote | Fault | Effect |
|---|---|---|
| Outer Z check 5, immediately after CX(D3,s), the second data port | Z on s | Propagates Z to the remaining six data ports. Both flag taps still follow the fault and the flag reports zero. Modulo the just-measured outer Z generator this is $Z_0 Z_3$. |
| Inner X check 1, immediately after the first CX(s,f0) | X on s | Propagates X to D5, D6 and D7 and flips the closing flag. The flagged recovery obtains two identical complete references in diagnostic V coordinates. |

At the nonroot leaf, the change of coordinates is controlled by its tree edge. On the edge-one component, conjugating a physical X through the local W sends it to Y up to sign. Thus the same physical hook supplies the data component $Y_5Y_6Y_7$ up to phase. Together with the first fault, the corresponding diagnostic Pauli has X mask 224 and Z mask 233. The acquired data syndrome is 164930, with the nine Z reports occupying the low bits. The confirmed record selects this component. Representatives related by an inner stabilizer give the same argument.

The recovery calls the flag-conditioned table for the physical X meter with a syndrome acquired **after** the coordinate change. The table declares a unique correction with data masks $x=224$, $z=196640$. The controller also applies an edge Z according to the star record. The data X support cancels. The data Z residual is

$$Z_0 Z_3 Z_6 Z_7 Z_{16} Z_{17}.$$

It has zero syndrome and anticommutes with the first logical X while commuting with the second. All subsequent routine votes and the terminal screen can therefore report success. The operation is a logical Z on the target $(|00⟩+|01⟩+|10⟩)/√3$. Its overlap with that target is $1/3$, giving squared fidelity $1/9$. The exact trajectory backend produces the same decoded fidelity. The terminal result on this branch is `zero_accept`. A more accurate repetition of the same reference would confirm the same syndrome.

## Controls

| Injected locations on seed 4 | Original tree outcome |
|---|---|
| Neither | Accept, decoded fidelity 1 |
| Outer Z meter only | Reject at terminal data ambiguity |
| Inner X meter only | Accept, decoded fidelity 1 |
| Both | Accept, decoded fidelity 1/9 |

The witness is minimal under deletion of either of its locations on this trajectory. It suffices to refute a universal theorem for arbitrary faults, since a Pauli fault is an allowed fault and the claim covers every accepted measurement branch. The stochastic rates and efficiencies previously measured are observations of the implemented controller. They do not supply a distance or a two-fault guarantee. [Physical events, controller records, and decoded states](../../../output/cz-gauged-flag-composition/witness.json)

## A conservative recovery guard

The guarded experimental controller retains the physical instruments. Before allowing a flag-conditioned correction, it looks up the measured data syndrome in the existing unrestricted two-inner-block table. If that table gives no unique stabilizer class, it rejects. This syndrome admits **four** classes, so the guarded run rejects before applying the wrong correction. For every retained entry of the ten inner X/Z flag tables, the verifier checks agreement of the proposed correction and the unrestricted correction modulo the full code stabilizer.

The resulting local implication is precise. If the state at a clean full reference is in the span of Paulis supported on at most two inner blocks acting on the intended encoded input, then every retained correction removes its data Pauli up to a stabilizer at that reference. Uniqueness covers every component of a coherent error in that span. Later faults have to be accounted for separately. The guard establishes this decoder implication and removes the exhibited failure. A universal accepted-output theorem for the guarded factory still needs a proof of its incoming envelopes, honest passing vote, and closure through later recovery, feedback and the terminal screen. [Guard, table check and reproduction runner](../../../verification/single_block_cz/check_single_cz_gauged_flag_composition.py)

On fresh seeds 101000–101063, the original controller accepted 36 attempts with 36 decoded matches. The guard accepted 35 with 35 matches. It vetoed one formerly successful attempt. This small comparison measures the price of conservative rejection. [Paired noisy runs](../../../output/cz-gauged-flag-composition/shots.jsonl)

Run from the repository root with an unused output directory.

~~~sh
/Users/kevinhemery/pytket-venv/bin/python -B verification/single_block_cz/check_single_cz_gauged_flag_composition.py --folder output/cz-gauged-flag-composition-repro
~~~
