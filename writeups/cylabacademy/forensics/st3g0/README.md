---
title: St3g0
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-19
tags: [steganography, zsteg, lsb, png, encoding]
status: published
---

# St3g0

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A PNG with a flag hidden in the pixel data by LSB steganography.

```bash
wget https://artifacts.picoctf.net/c/215/pico.flag.png
```

## TL;DR

`zsteg` reads the least-significant bits of the image and pulls the flag straight
out of the `b1,rgb,lsb` channel.

## Approach

### 1. Confirm it's a valid PNG, not extension trickery

```bash
exiftool pico.flag.png       # PNG, 585x172, RGB with Alpha
```

RGB **with alpha** is worth noting — four channels means more bits to hide data
in, and a hint that LSB steganography is in play.

### 2. Run zsteg

```bash
zsteg pico.flag.png
```

```
b1,rgb,lsb,xy   .. text: "picoCTF{7h3r3_15_n0_5p00n_96ae0ac1}st3g0"
b1,r,lsb,xy     .. text: "~__B>wV_G@"
b2,b,lsb,xy     .. file: ...
```

`zsteg` tries every bit-plane / channel / ordering combination automatically. The
`b1,rgb,lsb,xy` line — the 1 least-significant bit of the R, G, B channels read in
pixel order — is the hit. The other lines are `zsteg` finding coincidental
patterns in the noise; the readable `picoCTF{...}` is the real one.

### 3. Clean the extracted string

The raw match is `picoCTF{7h3r3_15_n0_5p00n_96ae0ac1}st3g0`. Two things to trim:

- **Trailing `st3g0`** — LSB extraction keeps reading bits past the closing `}`,
  so whatever bytes follow the flag come along. Anything after `}` is noise.
- The flag itself ends at the `}`.

```
picoCTF{7h3r3_15_n0_5p00n_...}
```

## Flag

```
picoCTF{7h3r3_15_n0_5p00n_...}
```

_Truncated — graded course._

## Learn more

**On the "ä" and "å" I saw in the output.** My webshell rendered the flag as
`picoCTFä7h3r3..._96ae0ac1å$t3g0`, and I stripped the `ä`/`å` as junk. They
weren't junk — they were `{` and `}` mangled by a character-encoding mismatch
between the tool's output and the terminal. The same session mangled `@` → `É`
and `~` → `ü` (visible in the prompt `academyÉwebshell:ü$`), so this was
consistent, not random. The lesson: when a byte renders as an unexpected accented
character, suspect a **display encoding problem**, not corrupt data — pipe through
`xxd` or `zsteg ... | xxd` to see the true bytes before deciding what to strip.
Had I stripped the braces for real, the flag would have been rejected.

**Why `b1,rgb,lsb`.** LSB steganography flips the lowest bit of each colour value —
invisible to the eye (a value of 138 vs 139 is imperceptible) but a clean channel
to smuggle bytes. `b1` = one bit, `lsb` = least-significant, `rgb` = across those
three channels, `xy` = row-major pixel order. `zsteg` brute-forces all of these
because the hider could have used any combination.

- [zsteg](https://github.com/zed-0xff/zsteg) — LSB/bit-plane analysis for PNG/BMP
- `zsteg -a` runs every method; `zsteg -E b1,rgb,lsb,xy pico.flag.png` extracts one channel raw

## Tools

`zsteg`, `exiftool`, `xxd`
