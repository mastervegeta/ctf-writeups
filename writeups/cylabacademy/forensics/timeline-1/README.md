---
title: Timeline 1
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-18
tags: [sleuthkit, mactime, timeline, disk-image, base64]
status: published
---

# Timeline 1

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A gzipped disk image with the flag hidden on it. Hints point at filesystem
timeline analysis.

```
https://challenge-files.picoctf.net/c_plain_mesa/fef9e3937fced503da228c6affaea69ed51d6234ed8fde14a52b573777b869e7/partition4.img.gz
```

## TL;DR

Build a MACB timeline and filter for entries where all four timestamps fire at
once. On a used system those are the files that arrived and were never touched
again — `/etc/chat`, holding a base64 flag.

## Approach

### 1. Fetch and check for a partition table

```bash
wget <url>/partition4.img.gz && gunzip partition4.img.gz
mmls partition4.img
```

`mmls` returns no partition layout. That's the answer, not a failure: the image
*is* the filesystem, so no `-o` offset is needed anywhere.

### 2. List the file tree

```bash
fls -r partition4.img
fls -r partition4.img | grep picoCTF   # nothing
```

<details>
<summary>What didn't work here</summary>

**Tried:** grepping the `fls` output for the flag.

**Why it failed:** `fls` prints filenames and metadata, never file contents. And
a grep over the raw image would also have missed it — the flag is base64-encoded
on disk, so the string `picoCTF` never appears.

</details>

### 3. Poke around by hand

`icat` reads by inode, so look it up first:

```bash
fls -r partition4.img | grep ash_history
icat partition4.img <that inode>
```

```
poweroff
```

A root shell history containing one command reads as a cleared history. That
signals tampering but names no file — which is what the timeline is for.

### 4. Build the timeline

```bash
fls -m / -r partition4.img > body.txt
mactime -b body.txt -z UTC -y -d > timeline.csv
```

> `-z` consumes the next argument as its timezone. `-z -y -d UTC` makes `-y` the
> timezone and `UTC` a date range. Keep the value attached: `-z UTC`.

### 5. Filter for all-four-timestamps entries

```bash
grep macb timeline.csv
```

`macb` means all four timestamps are identical — created then never touched.
`/etc/chat` is not a standard path, which makes it the one to read.

<details>
<summary>What didn't work here</summary>

**Tried:** opening the first few `macb` hits expecting the flag.

**Why it failed:** `macb` narrows, it doesn't identify. Anything laid down at
install time and never opened matches too. It's a shortlist, not an answer.

</details>

### 6. Read it

```bash
icat partition4.img 32716 | base64 -d
```

```
573417h13r_7h4n_7h3_1457_...
```

## Flag

```
picoCTF{573417h13r_7h4n_7h3_1457_...}
```

_Truncated — graded course._

## Learn more

| | Name | Updated when |
| --- | --- | --- |
| **M** | Modified | contents change |
| **A** | Accessed | file is read |
| **C** | Changed | inode metadata changes (permissions, owner) |
| **B** | Birth | file is created |

C is the one people misread: it's *metadata* changed, not contents, and unlike
the others it can't be set backwards through normal syscalls. A file claiming a
2019 mtime with a last-Tuesday ctime has been timestomped.

Birth time isn't universal — ext4, NTFS and APFS have it; ext3 doesn't, so
`...b` entries simply won't appear there.

- [Sleuth Kit — mactime](https://www.sleuthkit.org/sleuthkit/man/mactime.html) · [fls](https://www.sleuthkit.org/sleuthkit/man/fls.html)
- [Timeline 0](../timeline-0/) — same image family, where this `macb` filter stops working

## Tools

`mmls`, `fls`, `mactime`, `icat`, `base64`
