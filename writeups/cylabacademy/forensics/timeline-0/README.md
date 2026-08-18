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

Same shape as [Timeline 1](../timeline-1/) — a gzipped disk image, flag hidden
on it, hints pointing at timeline analysis.

```
https://challenge-files.picoctf.net/c_plain_mesa/aa1f8ba93409887e081435732d7037c45b30a8442853bf07c9e84fe4d0e0bc19/partition4.img.gz
```

## TL;DR

Build the timeline as in Timeline 1, then **sort by age instead of filtering on
MACB**. This image is a stock Alpine build where nearly every file is `macb`, so
that filter matches everything. The outlier is a file dated **1985** —
`/bin/bcab`.

## Approach

### 1. Fetch, confirm no partition table, build the timeline

```bash
cd /tmp && wget <url>/partition4.img.gz && gunzip partition4.img.gz
mmls partition4.img                      # no layout, so no -o offset needed
fls -m / -r partition4.img > body.txt
mactime -b body.txt -z UTC -y -d > timeline.csv
```

### 2. Try the Timeline 1 approach

```bash
cat timeline.csv              # thousands of lines, nothing obvious
grep macb timeline.csv
```

<details>
<summary>What didn't work here</summary>

**Tried:** `grep macb`, the filter that solved Timeline 1.

**Why it failed:** not by missing the file — `/bin/bcab` *is* `macb` and the grep
matched it. It failed as a discriminator. This image is a stock Alpine build
where essentially every file was written once and never touched, so almost the
whole filesystem is `macb`.

`macb` was informative in Timeline 1 because that system had been *used*, so real
timestamp drift existed and untouched files were the exception. Here there's no
drift to be an exception to. **A filter only works if the baseline makes it
rare.**

</details>

### 3. Sort by age

The hint: *"Sloppy timestomping can yield strange (very old) timestamps"*.
`mactime` output is already chronological, so the oldest entries are the top:

```bash
head -20 timeline.csv
```

```
Date,Size,Type,Mode,UID,GID,Meta,File Name
1985-01-01T17:00:00Z,41,macb,r/rrw-r--r--,0,0,4945,"/bin/bcab"
2021-10-18T17:54:17Z,451,ma..,r/rrw-r--r--,0,0,64994,"/usr/share/apk/keys/alpine-devel@...rsa.pub"
...
```

One file from 1985, then a hard jump to 2021 where the rest of the filesystem
lives. The gap is the finding. `/bin/bcab` also reads like a real binary, which
is the point.

### 4. Read it

The `Meta` column gives the inode:

```bash
icat partition4.img 4945 | base64 -d
```

```
71m311n3_0u7113r_h3r_43a2e7af
```

## Flag

```
picoCTF{71m311n3_0u7113r_h3r_...}
```

_Truncated — graded course. The trailing hex looks instance-specific anyway._

## Learn more

A round `1985-01-01` is not a value any filesystem produces on its own — it's a
hand-set constant, and it sorts to the very top of a chronological timeline.

The two challenges hide a file the same way, but the filter that finds it depends
on what the rest of the filesystem looks like:

| | Timeline 1 | Timeline 0 |
| --- | --- | --- |
| System state | used, timestamps drifted | stock build, all written at once |
| What's rare | all four timestamps identical | anything outside the install window |
| Filter | `grep macb` | `head` / sort by age |

An anomaly is defined against a baseline, not in isolation. Three cheap passes
before anything clever: `head` for implausibly old, `tail` for suspiciously
recent, and find where the bulk of the filesystem clusters to get the install
window.

- [Sleuth Kit — mactime](https://www.sleuthkit.org/sleuthkit/man/mactime.html)

## Tools

`mmls`, `fls`, `mactime`, `head`/`tail`, `icat`, `base64`
