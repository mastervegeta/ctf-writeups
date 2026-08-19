---
title: Extensions
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-19
tags: [file-signatures, magic-bytes, png, file-command]
status: published
---

# Extensions

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A file named with a `.txt` extension that doesn't behave like text. Figure out
what it really is.

## TL;DR

The file's contents are a PNG despite the `.txt` name. The extension is a lie —
identify the file by its magic bytes, rename it to `.png`, open it, and the flag
is in the image.

## Approach

### 1. Notice it isn't text

```bash
cat flag.txt        # binary garbage, not readable text
exiftool flag.txt
file flag.txt
```

`exiftool` reports PNG properties (dimensions, colour type), and `file` says
`PNG image data` — both ignore the extension and read the actual bytes. The first
eight bytes are the PNG signature `89 50 4E 47 0D 0A 1A 0A` (`.PNG....`), which is
what gives it away.

### 2. Rename and open

```bash
mv flag.txt flag.png
```

Open `flag.png` in an image viewer — the flag is rendered in the picture.

## Flag

```
picoCTF{...}
```

_Not recorded in my notes; redacted anyway — graded course._

## Learn more

**The extension is metadata, not identity.** A filename's suffix is just a hint to
the OS about which program to open it with — it has no bearing on what the bytes
actually are. Renaming `.png` to `.txt` doesn't change a single byte of content;
it only changes what double-clicking does.

What *does* identify a file is its **magic number** — a signature in the first few
bytes:

| Type | Magic bytes | ASCII |
| --- | --- | --- |
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `.PNG....` |
| JPEG | `FF D8 FF` | `ÿØÿ` |
| GIF | `47 49 46 38` | `GIF8` |
| PDF | `25 50 44 46` | `%PDF` |
| ZIP | `50 4B 03 04` | `PK..` |

`file` reads these and tells you the real type in one command — always the first
thing to run on any unknown or suspiciously-named file. `xxd flag.txt | head`
shows the raw bytes if you want to confirm the signature by eye. Renaming is
almost never even necessary: most viewers open a correct PNG regardless of its
extension, since they check the bytes too.

## Tools

`file`, `exiftool`, `xxd`, `mv`
