#!/usr/bin/env bash
# Scaffold a new challenge directory from the templates.
#
#   ./scripts/new-challenge.sh <event> <category> "<Title>"
#   ./scripts/new-challenge.sh picogym cryptography "Basic Mod 1"
#
# Creates writeups/<event>/<category>/<slug>/ containing:
#   README.md  — the writeup, status: draft (stays out of the index until published)
#   notes.md   — your gitignored scratch file; fill this in while you solve
#   files/     — challenge artifacts, if any

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  printf 'usage: %s <event> <category> "<Title>"\n\n' "$(basename "$0")"
  printf 'example: %s picogym cryptography "Basic Mod 1"\n' "$(basename "$0")"
  exit 64
}

[ "$#" -eq 3 ] || usage

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}

EVENT_RAW="$1"
CATEGORY_RAW="$2"
TITLE="$3"

EVENT="$(slugify "$EVENT_RAW")"
CATEGORY="$(slugify "$CATEGORY_RAW")"
SLUG="$(slugify "$TITLE")"

if [ -z "$EVENT" ] || [ -z "$CATEGORY" ] || [ -z "$SLUG" ]; then
  echo "error: event, category and title must each contain at least one alphanumeric character" >&2
  exit 65
fi

DEST="$REPO_ROOT/writeups/$EVENT/$CATEGORY/$SLUG"

if [ -e "$DEST" ]; then
  echo "error: $DEST already exists — refusing to overwrite" >&2
  exit 73
fi

TODAY="$(date +%F)"

mkdir -p "$DEST/files"

# Templates use __TOKEN__ placeholders so no shell/sed quoting hazards from the title.
fill() {
  sed -e "s|__TITLE__|$TITLE|g" \
      -e "s|__EVENT__|$EVENT|g" \
      -e "s|__CATEGORY__|$CATEGORY|g" \
      -e "s|__DATE__|$TODAY|g" \
      "$1"
}

fill "$REPO_ROOT/templates/writeup.md" > "$DEST/README.md"
fill "$REPO_ROOT/templates/notes.md"   > "$DEST/notes.md"

# Keep files/ in git even while empty, so the layout survives a clone.
cat > "$DEST/files/.gitkeep" <<'EOF'
EOF

REL="${DEST#"$REPO_ROOT"/}"

cat <<EOF
Created $REL/
  README.md   the writeup (status: draft)
  notes.md    scratch, gitignored — write here while you solve
  files/      challenge artifacts

Next:
  1. solve, dumping commands + output + dead ends into $REL/notes.md
  2. turn notes.md into README.md (see WORKFLOW.md)
  3. set 'status: published' in the frontmatter when it is ready
  4. python3 scripts/update_index.py && git add -A && git commit
EOF
