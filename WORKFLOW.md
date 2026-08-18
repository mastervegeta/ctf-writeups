# Workflow

The loop, once per challenge.

## 1. Scaffold, before you start solving

```bash
./scripts/new-challenge.sh picogym cryptography "Basic Mod 1"
```

Creates `writeups/picogym/cryptography/basic-mod-1/` with a draft `README.md`, a
scratch `notes.md`, and an empty `files/`.

Do this *first*, not after you've solved it. The whole value of the repo is the
record of the attempt, and that record cannot be reconstructed once you know the
answer — the wrong turns stop feeling like wrong turns.

## 2. Solve, writing into `notes.md`

`notes.md` is gitignored. It is deliberately not the writeup: it's messy, it's
unedited, and nobody reads it but you.

The one thing to be disciplined about is **recording failures as they happen**,
with the reason they failed. Everything else in the writeup can be reconstructed
afterwards from your shell history. Dead ends cannot — by the time you've solved
it, you have lost the state of mind in which the wrong approach looked right.

Paste liberally: commands, output, error messages, the thing you googled.

## 3. Turn notes into the writeup

Rewrite `notes.md` into `README.md`, following
[templates/example.md](templates/example.md).

The structure that matters:

- **TL;DR** — the observation that cracked it. A reader who already knows the
  technique should be able to stop here.
- **Approach**, as numbered steps. Each step: what you looked at, what you saw,
  the command.
- **Dead ends nested inside each step**, in a `<details>` block, as
  **Tried:** / **Why it failed:**.
- **Learn more** — the background that would have let you skip the dead ends.

That placement of dead ends is the one structural decision worth defending. A
"things that didn't work" pile at the bottom is never read, and even when it is,
the reader can't connect an entry back to the moment it mattered. Attached to
the step, a dead end reads as a fork in the path, which is what it was.

**Verify anything factual in "Learn more" before publishing.** Historical dates,
tool defaults, flag semantics, what an algorithm actually guarantees — that
section is where a confident-sounding wrong claim is most likely to survive, and
it's going out under your name. If you drafted it with an LLM, this is the part
to check line by line.

## 4. Publish

Set `status: published` in the frontmatter. Until you do, the writeup stays out
of the index.

```bash
python3 scripts/update_index.py
git add -A
git commit -m "writeup: Basic Mod 1"
git push
```

`update_index.py` reports anything it skipped and why, so a writeup that's
missing from the table always tells you the reason. CI runs
`update_index.py --check` and fails if the committed index is stale.

## Frontmatter reference

```yaml
---
title: Basic Mod 1          # required
event: picogym              # groups the index; slug-style
category: cryptography
points: 100
difficulty: easy
date: 2026-08-18
tags: [modular-arithmetic, python]
status: draft               # 'published' to appear in the index
---
```

`event` slugs get prettier names in the index via `EVENT_DISPLAY` in
[scripts/update_index.py](scripts/update_index.py) — add yours there.

## Redacting flags

This repo prints flags in the **Flag** section and nowhere else. Pick a
convention and hold to it, so a reader knows whether a missing flag means
"redacted" or "forgot".

And re-read the note at the end of [README.md](README.md) before publishing
anything from a live event or a graded course.
