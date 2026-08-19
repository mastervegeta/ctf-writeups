---
title: What Lies Within
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-19
tags: [steganography, zsteg, lsb, png]
status: published
---

# What Lies Within

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A PNG (`buildings.png`) with a flag hidden in the pixel data.

## TL;DR

`zsteg -a buildings.png` reveals the flag in the `b1,rgb,lsb` channel —
`picoCTF{h1d1ng_1n_th3_b1t5}`. Same technique as [St3g0](../st3g0/).

## Approach

I worked up the usual ladder, cheapest first:

```bash
cat buildings.png | grep pico     # nothing
strings buildings.png | grep pico # nothing
exiftool buildings.png            # PNG, 657x438, RGB with Alpha — no flag in metadata
```

None of those hit, which rules out a plaintext flag and points at the pixel data
itself. So, `zsteg` — and `-a` to try every method:

```bash
zsteg -a buildings.png
```

```
b1,rgb,lsb,xy   .. text: "picoCTF{h1d1ng_1n_th3_b1t5}"
b2,b,lsb,xy     .. text: "XuH}p#8Iy="
...
```

The `b1,rgb,lsb,xy` line is the flag. The rest are `zsteg` reporting coincidental
patterns from other bit-planes.

## Flag

```
picoCTF{h1d1ng_1n_th3_b1t5}
```

## Learn more

The value here is the **order of operations** on any suspicious image, cheapest
to most involved:

1. `grep` / `strings` — is the flag just sitting there in plaintext?
2. `exiftool` — is it in a metadata field (comment, author, description)?
3. `zsteg -a` — is it in the least-significant bits of the pixels?

Each step is seconds, and you only escalate when the previous comes up empty.
Here the first two were dead ends *in the useful sense* — their failure is what
told me the data was in the pixels, not the bytes or the metadata.

`-a` (all methods) vs plain `zsteg`: plain runs the common combinations, `-a`
runs everything including padded bit-planes and rarer channel orderings. Reach
for `-a` when the default finds nothing. See [St3g0](../st3g0/) for what the
`b1,rgb,lsb` channel spec actually means — this is the same hiding scheme, and the
flag (`h1d1ng_1n_th3_b1t5`) spells it out.

- [zsteg](https://github.com/zed-0xff/zsteg)

## Tools

`strings`, `exiftool`, `zsteg`
