#!/usr/bin/env bash
set -euo pipefail

NOTE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$NOTE_DIR/.." && pwd)"

INPUT="$NOTE_DIR/non-abelian-anyons-from-gauging-v2.md"
OUTPUT_DIR="$REPO_ROOT/output/pdf"
OUTPUT="$OUTPUT_DIR/non-abelian-anyons-from-gauging-v2.pdf"

if ! command -v pandoc >/dev/null 2>&1; then
    echo "Error: pandoc is required to compile the note." >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

pandoc \
    --from=markdown+tex_math_single_backslash \
    --resource-path="$NOTE_DIR" \
    --standalone \
    --number-sections \
    -H "$NOTE_DIR/tex-header.tex" \
    --pdf-engine=xelatex \
    -V geometry:margin=0.85in \
    -V colorlinks=true \
    -V linkcolor=blue \
    -V urlcolor=blue \
    -V fontsize=11pt \
    -V documentclass=article \
    "$INPUT" \
    -o "$OUTPUT"

printf 'Wrote %s\n' "$OUTPUT"
