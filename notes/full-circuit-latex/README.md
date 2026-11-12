# Circuit source

`main.tex` contains the editable `quantikz` diagrams for
[`full_circuit.md`](../full_circuit.md). Open this directory in the LaTeX
editor for a live compiled preview.

The generated source uses `quantikz` 0.9.6 notation and compiles with
pdfLaTeX; it also compiles with the desktop editor's compiler.

To regenerate the source and Markdown from the support data, run from the
repository root:

```sh
python3 -B notes/build-full-circuit.py
```

To also compile the PDF and export the cropped Markdown diagrams:

```sh
python3 -B notes/build-full-circuit.py --render
```

The rendering option requires `pdflatex`, `pdftoppm`, Pillow, and
`pdfplumber`. The Codex bundled Python has the two Python packages. The
final PDF is `output/pdf/full_circuit.pdf`; the images are under
`notes/figures/c4-helix/full-circuit/`. Compilation logs and full-page
previews stay under `tmp/pdfs/full-circuit/`.

The diagrams use shared cats across split panels. Their displayed ports
are expanded with the preparation, verification, and readout circuit on
the first page. The execution order and acceptance rules are those of
[`full_procedure.md`](../full_procedure.md).
