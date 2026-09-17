#!/usr/bin/env bash
set -euo pipefail

NOTE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$NOTE_DIR/.." && pwd)"

INPUT="$NOTE_DIR/non-abelian-anyons-from-gauging-v2.md"
OUTPUT_DIR="$REPO_ROOT/output/epub"
OUTPUT="$OUTPUT_DIR/non-abelian-anyons-from-gauging-v2.epub"

if ! command -v pandoc >/dev/null 2>&1; then
    echo "Error: pandoc is required to compile the note." >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

pandoc \
    --from=markdown+tex_math_single_backslash \
    --to=epub3 \
    --resource-path="$NOTE_DIR" \
    --toc \
    --toc-depth=3 \
    --split-level=2 \
    --mathml \
    --metadata title="Non-Abelian anyons from gauging logical gates" \
    --metadata lang=en-US \
    "$INPUT" \
    -o "$OUTPUT"

printf 'Wrote %s\n' "$OUTPUT"
