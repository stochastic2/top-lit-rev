# Single-block CZ circuit figures

Editable generator: [build-single-block-cz.py](../../../build-single-block-cz.py).
Each panel is supplied as SVG and a rendered PNG. The source uses the
same signed physical W pattern and graph labels as the schedule module.

1. `01-source-1/2`: every data wire and all 51 source CNOTs.
2. `02-enrichment`: one shared vertex and four actual T/CX/T† ports.
3. `03-graph-resource`: all eighteen graph-resource wires and 26 CNOTs.
   `03b-graph-parity`: the replacement verifier, one fresh helper, three
   resource-to-meter CNOTs, Z readout and classical local-rebuild decision.
   Scan all thirteen L_e checks three times; no preparation-stage K_v checks.
4. `04-cat-verification`: actual fanout and one full parity scan; repeat
   the scan three times before any data coupling.
5. `05-coordinate-checks`: both coordinate passes on one inner block;
   the middle check box expands into the primitive cats specified in the note.
6. `06-root-gauss`: all ten physical targets, ten distinct leaves,
   normalized controlled-W decompositions and X-basis leaf readout.
7. `07-ungauging-feedback`: every destructive edge Z meter and an explicit
   nonzero decoded byproduct on block b, with classical feedback.
8. `08-terminal-check`: four independent data ports and actual bases.

The default flagged recovery profile replaces the cat-check panels with:

- `09-rolling-star`: the actual compact13 five-edge nonroot star, one
  syndrome qubit, three reused flag slots, and root-tree Z feedback.
- `10-flagged-terminal`: actual four-data X check, one flag and six CX.

Editable generator: [build-single-cz-flags.py](../../../build-single-cz-flags.py).
Flags are temporarily entangled; no separately verified large cat is used.
The cat panels remain the explicitly retained conservative/cats option.

Single lines are quantum wires; double lines following MZ are classical
reports. A fresh |0> on reused verifier w begins a new quantum segment.
Aligned gates are a drawing convenience; the executable list specifies
the serial order and idle accounting. Figure time runs left to right.

These PNGs were visually inspected. Source and circuit edits should be
followed by regeneration and renewed visual inspection. The integrated
note and proof specify ordering, repetition, flags, rejection and feedback
which cannot all be represented in a single static panel.
