---
title: Timeline 0
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-18
tags: [sleuthkit, mactime, timeline, timestomping, base64, disk-image]
status: published
---

# Timeline 0

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A gzipped disk image, with the flag hidden somewhere on it. Same shape as
[Timeline 1](../timeline-1/), and the hints again point at filesystem timeline
analysis.

```
https://challenge-files.picoctf.net/c_plain_mesa/aa1f8ba93409887e081435732d7037c45b30a8442853bf07c9e84fe4d0e0bc19/partition4.img.gz
```

_(Paraphrased — the original prompt is behind the course login.)_

## TL;DR

Build the timeline the same way as Timeline 1, then **sort by age instead of
filtering by MACB**. The image is a stock Alpine build where nearly every file
was installed in the same instant, so the `macb` filter that cracked Timeline 1
matches almost everything and discriminates nothing. What stands out instead is
a single file dated **1985** — `/bin/bcab`, holding a base64-encoded flag.

## Approach

### 1. Fetch and decompress the image

```bash
cd /tmp
wget https://challenge-files.picoctf.net/c_plain_mesa/aa1f8ba93409887e081435732d7037c45b30a8442853bf07c9e84fe4d0e0bc19/partition4.img.gz
gunzip partition4.img.gz
```

### 2. Confirm there's no partition table

```bash
mmls partition4.img
```

No partition layout, so the image *is* the filesystem and no `-o` offset is
needed anywhere. `fls partition4.img` returns a file tree, which confirms it.
Identical to Timeline 1 — see that writeup for why an empty `mmls` is a result
rather than a failure.

### 3. Build the timeline

Having solved Timeline 1 first, this part needed no discovery:

```bash
fls -m / -r partition4.img > body.txt
mactime -b body.txt -z UTC -y -d > timeline.csv
```

`fls -m /` emits a body file with all four timestamps per file; `mactime` sorts
it chronologically, `-z UTC` sets the collection timezone, `-y` gives ISO 8601
dates and `-d` makes it comma-delimited.

### 4. Try to read the timeline directly

```bash
cat timeline.csv
```

Thousands of lines, nothing obviously wrong. Reading a timeline top to bottom
does not scale, and there was no visible anomaly to catch by eye.

<details>
<summary>What didn't work here</summary>

**Tried:** `cat timeline.csv | grep macb` — the filter that solved Timeline 1,
where files with all four timestamps identical stood out as recently planted.

**Why it failed:** it *didn't* fail in the sense of missing the file — `/bin/bcab`
is `macb`, and that grep did match it. It failed as a **discriminator**. This
image is a stock Alpine build where essentially every file was written once at
image-build time and never read or modified since, so almost the entire
filesystem is `macb`. The signal drowns in a wall of legitimate matches.

That's the real lesson: `macb` is not intrinsically suspicious. It was
informative in Timeline 1 because that system had been *used*, so genuine
timestamp drift existed and the untouched files were the exception. Here there's
no drift to be the exception to. **A filter only works if the baseline makes it
rare.**

</details>

### 5. Sort by age instead

The hint that unblocked this:

> Sloppy timestomping can yield strange (very old) timestamps

`mactime` output is already in chronological order, so the oldest entries are
simply the top of the file:

```bash
head -20 timeline.csv
```

```
Date,Size,Type,Mode,UID,GID,Meta,File Name
1985-01-01T17:00:00Z,41,macb,r/rrw-r--r--,0,0,4945,"/bin/bcab"
2021-10-18T17:54:17Z,451,ma..,r/rrw-r--r--,0,0,64994,"/usr/share/apk/keys/alpine-devel@lists.alpinelinux.org-4a6a0840.rsa.pub"
2021-10-18T17:54:17Z,451,ma..,r/rrw-r--r--,0,0,64995,"/usr/share/apk/keys/alpine-devel@lists.alpinelinux.org-5243ef4b.rsa.pub"
...
```

One file from **1985**, and then a hard jump to 2021 where the entire rest of the
filesystem lives. The gap is the finding. `/bin/bcab` is also a plausible-looking
name in a directory full of real binaries — it reads like something you'd scroll
past, which is the point.

The corresponding check for the other end is `tail`, for a file touched after
everything else.

### 6. Read the planted file

The `Meta` column gives the inode, `4945`:

```bash
icat partition4.img 4945 | base64 -d
```

```
71m311n3_0u7113r_h3r_43a2e7af
```

Leetspeak for "timeline outlier", plus a hex suffix, wrapped in `picoCTF{}`.

## Flag

```
picoCTF{71m311n3_0u7113r_h3r_...}
```

_Truncated, matching the convention used in [Timeline 1](../timeline-1/) — these
come through a graded course. The trailing hex looks instance-specific in any
case._

## Learn more

**Why timestomping leaves outliers.** Anti-forensics tools rewrite a file's
timestamps to blend in with its neighbours. Doing that well means matching the
surrounding directory's era; doing it sloppily means whatever value the tool
defaulted to. A round `1985-01-01` is not a value any filesystem produces on its
own — it's a hand-set constant, and it sorts to the very top of a chronological
timeline, which is the least subtle place to be.

**The two filters are opposites, and that's the point.**

| | Timeline 1 | Timeline 0 |
| --- | --- | --- |
| System state | used, so timestamps had drifted apart | stock build, everything written at once |
| What's rare | files with all four timestamps identical | a file outside the install window |
| Filter that works | `grep macb` | `head` / sort by age |
| Why the other fails | most files had drifted, so `head` shows only install-era files | nearly everything is `macb` |

Both challenges hide a file the same way. The technique that finds it depends
entirely on what the rest of the filesystem looks like — **an anomaly is defined
against a baseline, not in isolation.** Reaching for `grep macb` here because it
worked last time is the mistake the challenge is built to punish, and it's why
solving Timeline 1 first made this one *harder* to see, not easier.

**Reading a timeline in practice.** Three cheap passes before anything clever:
`head` for implausibly old, `tail` for suspiciously recent, and a look at where
the bulk of the filesystem clusters to establish the install window. Anything
outside that window is worth a look regardless of its MACB flags.

- [Sleuth Kit — mactime](https://www.sleuthkit.org/sleuthkit/man/mactime.html)
- [Timeline 1](../timeline-1/) — same image family, opposite filter

## Tools

- `mmls` — confirm there's no partition table
- `fls` — file tree; `-m` emits a mactime body file
- `mactime` — render the body file as a chronological timeline
- `head` / `tail` — oldest and newest entries, since the timeline is sorted
- `icat` — read file contents by inode
- `base64` — decode the payload
