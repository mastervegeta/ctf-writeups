---
title: Static ain't always noise
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [strings, objdump, elf, binary, reverse-engineering]
status: published
---

# Static ain't always noise

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

A compiled binary called `static` and a helper script `ltdis.sh`. The flag is a
plaintext string embedded in the binary.

```bash
wget <url>/static
wget <url>/ltdis.sh
```

## TL;DR

Run `strings static` (or `strings -a -t x static`) to pull the printable text out
of the binary. The flag is sitting there among the symbol names.

## Approach

### 1. Look at what the helper does

```bash
cat ltdis.sh
```

Two things: `objdump -Dj .text` to disassemble the `.text` section, and

```bash
strings -a -t x static > static.ltdis.strings.txt
```

to rip printable strings with their file offsets (`-t x` = offset in hex, `-a` =
scan the whole file). The flag isn't in the code — it's in the strings.

### 2. Pull the strings

```bash
strings static | grep -i pico
```

```
Oh hai! Wait what? A flag? Yes, it's around here somewhere!
picoCTF{d15a5m_t34s3r_...}
```

The binary stores the flag as a literal string, so `strings` finds it with no
disassembly needed. `grep pico` skips straight past the ELF symbol names and
library references.

## Flag

```
picoCTF{d15a5m_t34s3r_...}
```

_Truncated — graded course._

## Learn more

`strings` scans a file for runs of printable characters and prints them, which is
the fastest first look at any unknown binary — flags, URLs, error messages and
format strings all fall out for free. The title is the lesson: a binary looks
like "static" noise in a terminal (`cat static` is mostly garbage), but embedded
in that noise is readable text.

Useful flags: `-n <len>` sets the minimum run length (default 4), and `-t x`
prints each string's file offset so you can find it again in a hex editor or
`objdump` view.

The provided `ltdis.sh` also runs `objdump -Dj .text` — that's for when the
interesting data *isn't* a plaintext string and you have to read the
disassembly. Here `strings` alone was enough, but the script hands you both
starting points.

## Tools

`strings`, `objdump`, `grep`
