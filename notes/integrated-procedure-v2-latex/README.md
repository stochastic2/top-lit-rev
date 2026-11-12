# Expanded integrated procedure and proof - V2

The prose source is the adjacent full_procedure_integrated_v2.md file.
This project is independent of the preserved V1 Markdown, PDF, LaTeX
project, and circuit images.

From the repository root, generate the LaTeX with:

    python3 -B notes/build-integrated-procedure-v2.py

Compile the PDF and export the V2 Markdown circuit images with:

    python3 -B notes/build-integrated-procedure-v2.py --render

Rendering requires pdfLaTeX, Poppler, Pillow, and pdfplumber. The Codex
bundled Python supplies the Python dependencies. The output PDF is
output/pdf/full_procedure_integrated_v2.pdf. Circuit images are under
notes/figures/c4-helix/integrated-v2/. Scratch compilation and review
files use tmp/pdfs/integrated-procedure-v2/.

Open this directory in the LaTeX editor for a live preview of main.tex.
Its circuits/ directory contains vector quantikz snippets read from the
existing atlas. The images/ directory holds the graph and worked
ungauging illustration. No V1 generator is executed during this build.
