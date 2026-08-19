---
title: Disk, disk, sleuth!
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-19
tags: [disk-image, strings, mmls, sleuthkit, partitions]
status: published
---

# Disk, disk, sleuth!

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A gzipped disk image. The flag is somewhere on the filesystem; the challenge
name nudges you toward Sleuth Kit, but the flag is stored as plaintext.

```bash
wget <url>/dds1-alpine.flag.img.gz
gunzip dds1-alpine.flag.img.gz
```

## TL;DR

The flag is a literal string on the disk, so `strings img | grep picoCTF` finds
it directly — no filesystem walking required.

## Approach

### 1. Check the partition layout

```bash
mmls dds1-alpine.flag.img
```

The image has a partition table, with the filesystem starting at sector **2048**
(the standard first-partition offset). Sleuth Kit tools that read the filesystem
need that offset:

```bash
fls -o 2048 dds1-alpine.flag.img       # browse the file tree from here
```

`-o 2048` points the tool at where the actual filesystem begins, past the
partition table and boot area.

### 2. Just grep the strings

The flag is plaintext, so you don't need to navigate the filesystem at all:

```bash
strings dds1-alpine.flag.img | grep picoCTF
```

```
  SAY picoCTF{f0r3ns1c4t0r_n30phyt3_...}
```

`strings` scans the whole raw image — every partition, every file, slack space —
so a plaintext flag falls out regardless of where on the filesystem it lives.

## Flag

```
picoCTF{f0r3ns1c4t0r_n30phyt3_...}
```

_Truncated — graded course._

## Learn more

The intended path is Sleuth Kit — `mmls` to find the partition, then `fls -o
2048` and `icat` to walk the filesystem to the file holding the flag. That's the
skill the name ("sleuth") is teaching, and it's the right tool when the flag is
*inside* a specific file you need to locate.

But `strings | grep` is the pragmatic first move on any disk image, because it
searches the raw bytes and ignores filesystem structure entirely. If the flag is
plaintext anywhere on the disk — a file, a deleted file's leftover blocks, a log —
it appears. The offset (`-o 2048`) only matters for the structured tools;
`strings` reads the whole image linearly and doesn't care about partitions.

Rule of thumb: try `strings | grep` first (ten seconds, often done), and reach
for the Sleuth Kit walk when it comes up empty — which happens when the flag is
encoded, compressed, or split across non-contiguous blocks.

## Tools

`mmls`, `fls`, `strings`, `grep`
