#!/usr/bin/env python3
"""Rebuild the writeup index table in the root README.

    python3 scripts/update_index.py            # rewrite README.md in place
    python3 scripts/update_index.py --check     # exit 1 if the index is stale (CI)

Reads the YAML-ish frontmatter from every writeups/**/README.md and renders one
table per event between the INDEX markers in the root README.

Two kinds of writeup are deliberately left out, and both are reported so they
are never silently dropped:

  * status is not 'published' — drafts in progress
  * the body still contains template placeholders — scaffolded but unwritten,
    which would otherwise appear in the index looking complete

No third-party dependencies: the frontmatter here is flat enough to parse
directly, and that keeps CI to a bare python3.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WRITEUPS_DIR = REPO_ROOT / "writeups"
README = REPO_ROOT / "README.md"

START_MARKER = "<!-- INDEX:START -->"
END_MARKER = "<!-- INDEX:END -->"

# Substrings that only ever appear in an unedited template body.
PLACEHOLDER_MARKERS = (
    "__TITLE__",
    "__EVENT__",
    "__CATEGORY__",
    "__DATE__",
    "_Paste the challenge prompt as given",
    "_Two or three sentences:",
    "### 1. __First step__",
    "command here",
    "relevant output here",
)

# Pretty names for events whose slug reads badly in a heading.
EVENT_DISPLAY = {
    "picogym": "picoGym",
    "picoctf": "picoCTF",
    "cylabacademy": "CyLab Academy",
    "cylab-africa": "CyLab-Africa",
}


class WriteupError(Exception):
    pass


def parse_frontmatter(text: str, source: Path) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Raises WriteupError if absent/malformed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise WriteupError("missing '---' frontmatter block at the top of the file")

    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise WriteupError("frontmatter block is never closed with '---'") from None

    data: dict[str, object] = {}
    for lineno, raw in enumerate(lines[1:end], start=2):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise WriteupError(f"line {lineno}: expected 'key: value', got {line!r}")
        key, _, value = line.partition(":")
        data[key.strip()] = parse_value(value.strip())

    return data, "\n".join(lines[end + 1 :])


def parse_value(value: str) -> object:
    """Scalars, quoted strings and flat [a, b] lists — the whole frontmatter dialect."""
    if not value:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def collect() -> tuple[list[dict], list[tuple[Path, str]]]:
    """Return (published writeups, [(path, reason skipped)])."""
    published: list[dict] = []
    skipped: list[tuple[Path, str]] = []

    if not WRITEUPS_DIR.is_dir():
        return published, skipped

    for path in sorted(WRITEUPS_DIR.rglob("README.md")):
        rel = path.relative_to(REPO_ROOT)
        try:
            data, body = parse_frontmatter(path.read_text(encoding="utf-8"), path)
        except WriteupError as exc:
            skipped.append((rel, f"unreadable frontmatter — {exc}"))
            continue

        status = str(data.get("status") or "").strip().lower()
        if status != "published":
            skipped.append((rel, f"status is {status or 'unset'!r}, not 'published'"))
            continue

        leftover = [m for m in PLACEHOLDER_MARKERS if m in body]
        if leftover:
            skipped.append(
                (rel, f"body still contains template placeholders ({leftover[0]!r})")
            )
            continue

        if not data.get("title"):
            skipped.append((rel, "no title in frontmatter"))
            continue

        data["_dir"] = path.parent.relative_to(REPO_ROOT).as_posix()
        published.append(data)

    return published, skipped


def cell(value: object) -> str:
    if value is None or value == "" or value == []:
        return "—"
    if isinstance(value, list):
        return ", ".join(f"`{v}`" for v in value)
    return str(value)


def render(writeups: list[dict]) -> str:
    if not writeups:
        return (
            "_No published writeups yet. Scaffold one with "
            "`./scripts/new-challenge.sh <event> <category> \"<Title>\"`._"
        )

    by_event: dict[str, list[dict]] = {}
    for w in writeups:
        by_event.setdefault(str(w.get("event") or "uncategorised"), []).append(w)

    out: list[str] = []
    total = len(writeups)
    out.append(f"**{total} writeup{'s' if total != 1 else ''}** across "
               f"{len(by_event)} event{'s' if len(by_event) != 1 else ''}.")
    out.append("")

    for event in sorted(by_event):
        rows = sorted(
            by_event[event],
            key=lambda w: (str(w.get("date") or ""), str(w.get("title"))),
            reverse=True,
        )
        out.append(f"### {EVENT_DISPLAY.get(event, event)}")
        out.append("")
        out.append("| Challenge | Category | Points | Difficulty | Tags |")
        out.append("| --- | --- | --- | --- | --- |")
        for w in rows:
            link = f"[{w['title']}]({w['_dir']}/)"
            out.append(
                "| {} | {} | {} | {} | {} |".format(
                    link,
                    cell(w.get("category")),
                    cell(w.get("points")),
                    cell(w.get("difficulty")),
                    cell(w.get("tags")),
                )
            )
        out.append("")

    return "\n".join(out).rstrip()


def splice(readme_text: str, table: str) -> str:
    start = readme_text.find(START_MARKER)
    end = readme_text.find(END_MARKER)
    if start == -1 or end == -1:
        raise SystemExit(
            f"error: {README.name} must contain both {START_MARKER} and {END_MARKER}"
        )
    if end < start:
        raise SystemExit(f"error: {END_MARKER} appears before {START_MARKER}")

    head = readme_text[: start + len(START_MARKER)]
    tail = readme_text[end:]
    return f"{head}\n\n{table}\n\n{tail}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if the index is out of date",
    )
    args = ap.parse_args()

    published, skipped = collect()
    updated = splice(README.read_text(encoding="utf-8"), render(published))
    current = README.read_text(encoding="utf-8")

    for rel, reason in skipped:
        print(f"skipped {rel}: {reason}")
    if skipped:
        print()

    if args.check:
        if updated != current:
            print("index is out of date — run: python3 scripts/update_index.py")
            return 1
        print(f"index is up to date ({len(published)} published).")
        return 0

    if updated == current:
        print(f"index already up to date ({len(published)} published).")
        return 0

    README.write_text(updated, encoding="utf-8")
    print(f"wrote {README.name} ({len(published)} published).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
