#!/bin/bash
# Reviewable, move-only layout migration. Requires Bash 3.2 or later.
# Default: preview, with NO filesystem writes. No rm, overwrites, or content edits.
# This changes layout only: imports, relative links and commands need follow-up.
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd -P)
MANIFEST="$SCRIPT_DIR/reorganization-plan.tsv"
UNDO=""
APPLY=0
JOURNAL=""
SOURCES=(""); DESTINATIONS=(""); HASHES=(""); COUNT=0

usage() {
    cat <<'HELP'
Usage: bash scripts/reorganize_repository.sh [--apply] [--root DIR]
       bash scripts/reorganize_repository.sh --undo JOURNAL [--apply] [--root DIR]
Options:
  --apply           Perform the displayed moves. Otherwise preview only.
  --undo JOURNAL    Reverse moves recorded in a previous journal; preview by default.
  --manifest FILE   Use another reviewed two-column TSV move list.
  --root DIR        Repository root (default: parent of this script's directory).
  --help            Show this help.

No files are deleted, overwritten, copied, or edited. A move changes the old
pathname. Applying creates folders and a SHA-256 undo journal. Empty folders
remain after undo. Saved results, papers, figures and Git internals are excluded.

IMPORTANT: this is a structural migration, NOT a Python package conversion.
After moving files, imports, relative links, figure-generation paths and old
commands need updating before simulations/tests are used from the new layout.
Do not apply while a simulation or another migration is running.
HELP
}
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
exists() { [[ -e "$1" || -L "$1" ]]; }
while (( $# )); do
    case "$1" in
        --apply) APPLY=1; shift ;;
        --undo|--root|--manifest)
            (( $# >= 2 )) || die "Missing value for $1"
            case "$1" in
                --undo) UNDO=$2 ;;
                --root) ROOT=$2 ;;
                --manifest) MANIFEST=$2 ;;
            esac
            shift 2 ;;
        --help|-h) usage; exit 0 ;;
        *) die "Unknown argument: $1" ;;
    esac
done
ROOT=$(cd -- "$ROOT" && pwd -P) || die "Cannot open repository root"
[[ "$ROOT" != *$'\n'* && "$ROOT" != *$'\t'* ]] || die "Unsupported root pathname"
if command -v shasum >/dev/null 2>&1; then
    HASH_COMMAND=shasum
elif command -v sha256sum >/dev/null 2>&1; then
    HASH_COMMAND=sha256sum
else
    die "Need shasum or sha256sum for byte-preservation checks"
fi
hash_file() {
    local value
    if [[ "$HASH_COMMAND" == shasum ]]; then
        value=$(shasum -a 256 -- "$1") || die "Cannot hash $1"
    else
        value=$(sha256sum -- "$1") || die "Cannot hash $1"
    fi
    printf '%s\n' "${value%% *}"
}
valid_path() {
    local p=$1
    [[ "$p" != /* && "$p" != *$'\r'* && "$p" != *$'\t'* && "$p" != *$'\n'* ]] || die "Invalid path: $p"
    case "/$p/" in
        *'//'*|*'/../'*|*'/./'*|*'/.git/'*|*'/output/'*|*'/__pycache__/'*) die "Excluded path: $p" ;;
    esac
    case "$p" in
        notes/*|src/*|docs/*|tools/*|tests/*|verification/*|benchmarks/*) ;;
        *) die "Path outside the reviewed code/documentation roots: $p" ;;
    esac
    case "$p" in *.py|*.md) ;; *) die "Only individual .py and .md files may move: $p" ;; esac
}
check_parents() {
    local remaining=${1%/*} part current=$ROOT
    while [[ -n "$remaining" ]]; do
        part=${remaining%%/*}
        current="$current/$part"
        [[ ! -L "$current" ]] || die "Symlink parent refused: $current"
        if exists "$current"; then [[ -d "$current" ]] || die "Parent is not a directory: $current"; fi
        if [[ "$remaining" == */* ]]; then remaining=${remaining#*/}; else remaining=""; fi
    done
}
add_move() {
    local source=$1 destination=$2 expected=${3:-} digest j
    valid_path "$source"; valid_path "$destination"
    [[ "$source" != "$destination" ]] || die "Source equals destination: $source"
    check_parents "$source"; check_parents "$destination"
    [[ -f "$ROOT/$source" && ! -L "$ROOT/$source" ]] || die "Missing/nonregular/symlink source: $source"
    ! exists "$ROOT/$destination" || die "Destination already exists; no overwrite: $destination"
    for ((j=0; j<COUNT; j++)); do
        [[ "${SOURCES[j]}" != "$source" && "${DESTINATIONS[j]}" != "$destination" ]] || die "Duplicate move: $source -> $destination"
    done
    digest=$(hash_file "$ROOT/$source")
    [[ -z "$expected" || "$expected" == "$digest" ]] || die "Hash differs from journal: $source"
    SOURCES[COUNT]=$source; DESTINATIONS[COUNT]=$destination; HASHES[COUNT]=$digest
    COUNT=$((COUNT+1))
}
if [[ -n "$UNDO" ]]; then
    [[ -f "$UNDO" ]] || die "Cannot read journal: $UNDO"
    journal_root=""
    while IFS= read -r line || [[ -n "$line" ]]; do
        case "$line" in
            '# root:'$'\t'*) journal_root=${line#*$'\t'}; continue ;;
            '#'*|'') continue ;;
        esac
        IFS=$'\t' read -r digest source destination extra <<< "$line"
        [[ -z "${extra:-}" && "$digest" =~ ^[0-9a-f]{64}$ ]] || die "Malformed journal entry"
        valid_path "$source"; valid_path "$destination"
        check_parents "$source"; check_parents "$destination"
        if ! exists "$ROOT/$source" && exists "$ROOT/$destination"; then
            add_move "$destination" "$source" "$digest"
        elif exists "$ROOT/$source" && ! exists "$ROOT/$destination"; then
            [[ -f "$ROOT/$source" && ! -L "$ROOT/$source" ]] || die "Invalid unmoved source: $source"
            [[ "$(hash_file "$ROOT/$source")" == "$digest" ]] || die "Unmoved source changed: $source"
            printf 'Already at original path (or move never started): %s\n' "$source"
        else
            die "Undo requires exactly one of these paths to exist: $source ; $destination"
        fi
    done < "$UNDO"
    [[ "$journal_root" == "$ROOT" ]] || die "Journal root does not match --root"
else
    [[ -f "$MANIFEST" ]] || die "Cannot read manifest: $MANIFEST"
    while IFS= read -r line || [[ -n "$line" ]]; do
        case "$line" in '#'*|'') continue ;; esac
        IFS=$'\t' read -r source destination extra <<< "$line"
        [[ -n "$source" && -n "${destination:-}" && -z "${extra:-}" ]] || die "Need two TSV columns: $line"
        add_move "$source" "$destination"
    done < "$MANIFEST"
fi
printf '\nRoot: %s\nValidated moves: %s\n' "$ROOT" "$COUNT"
printf 'LAYOUT ONLY: imports, links and commands require follow-up after applying.\n'
for ((i=0; i<COUNT; i++)); do
    printf 'MOVE %q -> %q\n' "${SOURCES[i]}" "${DESTINATIONS[i]}"
done
if (( ! APPLY )); then
    printf '\nPREVIEW ONLY. No files or directories were created, moved or edited.\n'
    printf 'Review the TSV and REORGANIZATION.txt before considering --apply.\n'
    exit 0
fi
(( COUNT > 0 )) || { printf 'Nothing to move.\n'; exit 0; }

# All entries are preflighted before the first write. Never use force/clobber.
[[ ! -L "$ROOT/reorganization-logs" ]] || die "Symlink log directory refused"
mkdir -p -- "$ROOT/reorganization-logs"
JOURNAL="$ROOT/reorganization-logs/$(date -u +%Y%m%dT%H%M%SZ)-$$.tsv"
(set -o noclobber; printf '# Move journal v1\n# root:\t%s\n# SHA256\tsource\tdestination\n' "$ROOT" > "$JOURNAL") || die "Cannot create fresh journal"
trap 'printf "Interrupted. Preserve the journal: %s\n" "$JOURNAL" >&2; exit 130' INT
trap 'printf "Interrupted. Preserve the journal: %s\n" "$JOURNAL" >&2; exit 143' TERM
printf '\nUndo journal: %s\n' "$JOURNAL"
for ((i=0; i<COUNT; i++)); do
    source=${SOURCES[i]}; destination=${DESTINATIONS[i]}; digest=${HASHES[i]}
    check_parents "$source"; check_parents "$destination"
    [[ -f "$ROOT/$source" && ! -L "$ROOT/$source" ]] || die "Source changed: $source; journal: $JOURNAL"
    [[ "$(hash_file "$ROOT/$source")" == "$digest" ]] || die "Source contents changed; journal: $JOURNAL"
    ! exists "$ROOT/$destination" || die "Destination appeared; journal: $JOURNAL"
    mkdir -p -- "$ROOT/${destination%/*}"
    # Write intent BEFORE mv: undo handles an interruption on either side of mv.
    printf '%s\t%s\t%s\n' "$digest" "$source" "$destination" >> "$JOURNAL"
    mv -n -- "$ROOT/$source" "$ROOT/$destination"
    ! exists "$ROOT/$source" || die "Move did not complete; inspect journal: $JOURNAL"
    [[ -f "$ROOT/$destination" && ! -L "$ROOT/$destination" ]] || die "Unexpected target; inspect journal: $JOURNAL"
    [[ "$(hash_file "$ROOT/$destination")" == "$digest" ]] || die "Post-move hash mismatch; inspect journal: $JOURNAL"
done
printf '\nMoved and hash-verified %s files. No file contents were changed.\n' "$COUNT"
printf 'Preview reversal: bash %q --root %q --undo %q\n' "$SCRIPT_DIR/reorganize_repository.sh" "$ROOT" "$JOURNAL"
printf 'No imports/links were rewritten. Empty directories and every journal remain.\n'
