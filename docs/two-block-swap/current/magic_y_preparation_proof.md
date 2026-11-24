# Accepted-output proof for logical-Y extraction

This extends the [existing full proof](full_procedure_reduced_rejection_proof.md)
and [compact terminal proof](compact_terminal_extraction_proof.md) to
[the Y-output procedure](magic_y_preparation.md). At most two faulty
locations are allowed across the full schedule, including all new S,
CX/CZ gates, cat scans, wrong reports and waiting-qubit idles. Classical
processing and the tracked output Clifford frame are reliable.

## 1. Positive final cycles and ideal branches

The original gauged-sector and ungauging arguments imply that a positively
certified final cycle reaches terminal recovery with bounded-error terms
multiplying |Φ₊⟩, with spectator logical qubits B₁,C₁ in zero. On B₀,C₀,

\[
|\Phi_+\rangle=(2|00\rangle+|01\rangle+|10\rangle)/\sqrt6.
\]

Projection on B₀'s Y eigenvalue (−1)^y leaves C₀ proportional to
`(2-(-1)^y i)|0>+|1>`. Its squared unnormalized norm is six in either
branch. Each outcome has conditional probability 1/2. The Clifford
U₀=HS† or U₁=HS†H maps the respective normalized state to
`((1-i)|0>+|1>)/sqrt(3)`, up to global phase. Hence ideal acceptance is
3/4; the negative-SWAP branch is still discarded.

## 2. The physical word and its sign

Let x₀,z₀ denote the original supports of logical X₀,Z₀. Their overlap
has one site, so logical Y₀ is exactly iX(x₀)Z(z₀). The selected word has
masks x=1333,z=867, with three Y sites. Both x⊕x₀ and z⊕z₀ belong to
the original check-support span. Since logical Z₀ commutes with every
X stabilizer, the extra commutation phase is +1, while i³/i=−1.
Thus P=−Y₀S for an original-code stabilizer S.

The original 36 check observables and P commute. Protected measurement
of this 37-element family therefore satisfies the same clean-reference
lemma as before. On a clean history, the stopping time remains three
complete rounds.

## 3. Local faults in the Y gadget

The ideal controlled-Y port is S(control)·CX·CZ, with the rightmost
operation first. A helper leaf controls only one physical data target,
even though a Y port uses two two-qubit gates. A fault within that port
can therefore add only one physical data position. The original cat
preparation/repair argument bounds additional bad leaves under the same
global two-fault budget. S is a physical one-qubit gate; its faults are
charged normally.

Consequently the same protected-gadget normal form applies, now allowing
complex coefficients: each term has a locally bounded data Pauli times
`aI+bP`. The simulator represents these coefficients exactly, but the
proof does not assume stochastic Pauli faults. Arbitrary local operators
expand in Pauli products with environmental coefficients.

## 4. Joint reference and outcome decoding

Previous terminal measurements were original-code stabilizers. The new
logical-Y word must instead be tracked as a genuine logical projection.
Expand `aI+bP` in the two logical-Y projectors and commute data Paulis
through them. Before a clean reference, each term has the form

\[
E_BE_C\Pi_y(Y_{B,0})|\Phi_+\rangle
\]

with the same bounded matched-label support on E as in the original
terminal input invariant. Coefficients can depend on y and on the environment.
This does not treat a full logical-Y operator as a small physical error.

Let r be P's clean reported bit. For an actual candidate E_B, projecting
P and then removing E_B leaves the ideal logical-Y bit

\[
y=r\oplus1\oplus\operatorname{anti}(E_B,P).
\]

The unchanged joint decoder chooses R_B with R_BE_B in the stabilizer
group whenever its candidate class is unique. Since P commutes with that
group, `anti(R_B,P)=anti(E_B,P)`. All candidates in the accepted class
therefore imply the same corrected logical outcome. This proves the
reported-bit formula, including a remaining correctable B error.

After the joint correction, the clean-reference logical state factorizes
as B's Y eigenstate times C's raw branch, with both spectators in zero.
Errors after that reference retain the old physical-weight bound. Further
B-only Y checks or errors can change B but cannot change C's logical
branch; C-only stabilizer gadgets add only their charged correctable
defects. No B–C quantum coupling occurs after ungauging.

Discarding B in Z, with either meter result, therefore leaves the same
raw C branch up to those correctable defects. Wrong discard reports do
not select a branch or modify the output frame. C waiting errors during
discard remain included in the global fault budget.

## 5. Compact flags and re-gauging

The compact original-code gadgets retain their existing zero-flag physical
bound. When a nonzero compact flag occurs, the certified preliminary
repair restores the two-matched-block input bound and protected acquisition
restarts the same 37-observable family. The normal form above still applies
if Y was projected in an earlier incomplete compact history; it need not
remain in the original pre-Y logical span on a final positive cycle.

For a cycle that has not certified a positive sector, Y is **not measured**.
Its terminal family remains the original 36 checks. Thus the old logical
span invariant and the bound on re-gauging cycles apply unchanged. This
separation is required for the argument; it is not valid to measure Y on
every cycle and then reuse the old re-gauging proof.

## 6. Tracked Clifford frame and scope

Once the corrected Y bit is known, applying U_y logically maps C's raw
branch to |m_Y⟩. The implementation records U_y as an explicit output
frame, with zero physical correction gates. No perfect quantum recovery
or encoded Clifford circuit is silently added to the physical schedule.
Consumers must use the recorded frame when interpreting later operations.

The conclusion is the same type of accepted-output guarantee as before:
under at most two global faults, ideal decoding of correctable residual
physical errors and interpretation of the classical frame gives
|m_Y⟩|0⟩. This says nothing unconditional about all accepted trajectories
with many stochastic faults. Their target fidelity is computed against
the reported frame, so an incorrect reported frame is not excused by the
diagnostic.
