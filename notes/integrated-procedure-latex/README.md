# Integrated procedure and proof

The prose source is the adjacent full_procedure_integrated.md file.
The builder combines it with the existing quantikz circuits from
notes/full-circuit-latex/main.tex, reading the atlas without running
or changing its generator.

To regenerate the LaTeX from the repository root:

    python3 -B notes/build-integrated-procedure.py

To compile the PDF and export the Markdown circuit images:

    python3 -B notes/build-integrated-procedure.py --render

The render option requires pdfLaTeX, Poppler, Pillow, and pdfplumber.
The Codex bundled Python supplies the Python packages. The final PDF
is output/pdf/full_procedure_integrated.pdf. Circuit images are under
notes/figures/c4-helix/integrated/. Scratch previews and compilation
logs use tmp/pdfs/integrated-procedure/.

Open this directory in the LaTeX editor for a live preview. The project
main document is main.tex; the circuit snippets in circuits/ are vector
quantikz drawings. The prose, circuit snippets, and rendered images
should be regenerated together after an edit to the Markdown source.
