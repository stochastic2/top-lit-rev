# Original ALP diagrams

These figures reproduce the unmodified TikZ picture bodies in
`arXiv-2602.12228v1/main.tex`, Section IV.A:

- `checks`: `eq:qubit-ALP-stabilizers` (two pictures, placed side by side).
- `cz-pairing`: `eq:cubic-CZ-sym`.
- `ccz-enrichment`: the first occurrence of `eq:cubic-symm-enrich`.

The standalone wrappers provide the original colour definitions and packages.
No qubit positions, connections or Pauli labels have been redrawn. PNGs were
rendered at 500 dpi. To regenerate from the repository root, compile each
`.tex` file with `pdflatex -output-directory=tmp/pdfs/alp-paper`, then use
`pdftoppm -png -singlefile -r 500` on the resulting PDF and output the PNG
into this directory. The Markdown note uses paths relative to `notes/`;
when compiling from the repository root, pass `--resource-path=notes` to Pandoc.
