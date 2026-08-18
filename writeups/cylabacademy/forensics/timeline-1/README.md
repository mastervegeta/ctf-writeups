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

A gzipped disk image is provided, and the flag is somewhere on it. The
challenge's hints steer you toward filesystem timeline analysis rather than
searching the image directly.

```
https://challenge-files.picoctf.net/c_plain_mesa/fef9e3937fced503da228c6affaea69ed51d6234ed8fde14a52b573777b869e7/partition4.img.gz
```

_(Paraphrased — the original prompt is behind the course login and isn't
reproduced here.)_

## TL;DR

The image is a bare filesystem with no partition table, so Sleuth Kit tools work
on it directly. Searching for the flag by filename finds nothing, because the
flag is *inside* a file and base64-encoded. Building a MACB timeline and
filtering for entries where all four timestamps fire at once narrows thousands
of files down to a handful of recently-created, never-touched ones — and
`/etc/chat` is among them.

## Approach

### 1. Fetch and decompress the image

```bash
wget https://challenge-files.picoctf.net/c_plain_mesa/fef9e3937fced503da228c6affaea69ed51d6234ed8fde14a52b573777b869e7/partition4.img.gz
gunzip partition4.img.gz
```

### 2. Check for a partition table

The `.img` name doesn't tell you whether this is a whole disk (with a partition
table, so every subsequent tool needs a byte offset) or a single filesystem.
`mmls` answers that.

```bash
mmls partition4.img
```

It returned no partition layout. That's not a failure — it's the answer. No
partition table means the image *is* the filesystem, starting at offset 0, so
every later command can skip `-o`.

<details>
<summary>What didn't work here</summary>

**Tried:** reading the empty `mmls` output as "this tool isn't working" and
looking for a different way in.

**Why it failed:** it wasn't an error, it was a negative result carrying real
information. `mmls` parses partition tables specifically; a bare ext filesystem
has none to parse. Knowing there's no offset is what makes the rest of the
commands simple. A tool returning nothing is evidence, not a dead end.

</details>

### 3. List the file tree

```bash
fls -r partition4.img
```

That opened up the whole directory tree. The obvious next move is to search it
for the flag:

```bash
fls -r partition4.img | grep picoCTF
```

No results.

<details>
<summary>What didn't work here</summary>

**Tried:** `fls -r partition4.img | grep picoCTF`, expecting to catch a file
named after the flag or containing it.

**Why it failed:** `fls` lists *filenames and metadata*, never file contents. The
grep was only ever searching a list of names. And even a grep over the raw image
would have missed this one, since the flag is base64-encoded on disk and the
literal string `picoCTF` never appears. Two independent reasons the same
instinct fails — worth internalising, because "grep for the flag" is the reflex
on every forensics challenge.

</details>

### 4. Poke around by hand

`/home` and `/root` are the usual first stops. In `/root` there's a
`.ash_history` — the shell history for `ash`, BusyBox's shell, which suggests a
small embedded or Alpine-style system.

`icat` reads by inode number, not by path, so look the inode up first:

```bash
fls -r partition4.img | grep ash_history   # the leading number is the inode
icat partition4.img <that inode>
```

```
poweroff
```

One command. A root shell history containing nothing but `poweroff` is not what
a real session leaves behind — it reads as a history that was cleared, with the
final command recorded after the wipe. That's a tampering signal, but it names
no file and doesn't say when.

<details>
<summary>What didn't work here</summary>

**Tried:** continuing to browse promising-looking directories by hand, hoping to
recognise the planted file by name.

**Why it failed:** manual browsing scales with the number of directories, and
gives you no way to rank what you find. The `.ash_history` finding is the pivot:
it establishes that *something was tampered with* without revealing what, which
is precisely the situation timeline analysis exists to resolve. Time is the
index that filenames can't give you.

</details>

### 5. Build a filesystem timeline

Two steps. `fls -m` writes a **body file** — one line per file with all four
timestamps — and `mactime` sorts that into chronological order.

```bash
fls -m / -r partition4.img > body.txt
mactime -b body.txt -z UTC -y -d > timeline.csv
```

- `-m /` sets the mount point prepended to each path
- `-z UTC` is the timezone the data was collected in
- `-y` prints ISO 8601 dates, `-d` makes the output comma-delimited

> **Flag ordering matters:** `-z` consumes the next argument as its timezone. Writing
> `-z -y -d UTC` makes `-y` the timezone and `UTC` a date range, which is not what
> you want. Keep the value attached: `-z UTC`.

### 6. Filter for entries where all four timestamps fire together

```bash
grep macb timeline.csv
```

The third column of `mactime` output records which of the four timestamps match
that moment: `m...`, `.a..`, `..c.`, `...b`, or combinations. A line reading
`macb` means **all four are identical** — the file was created at that instant
and nothing has read or modified it since.

On a system that has been used, timestamps drift apart. Files whose four
timestamps still coincide are files that arrived and were never touched again,
which is what a planted file looks like.

<details>
<summary>What didn't work here</summary>

**Tried:** opening the first few `macb` hits and expecting the flag immediately.

**Why it failed:** `macb` narrows, it doesn't identify. Plenty of legitimate
files — anything laid down at install time and never opened — match it too. It
took working through several candidates before `/etc/chat` turned up. Treat the
filter as a shortlist to read, not an answer.

</details>

### 7. Read the planted file

`/etc/chat` is not a standard path, which makes it the interesting one.

```bash
icat partition4.img 32716
```

It contained a base64 string. Rather than copying that anywhere, pipe `icat`
straight into the decoder:

```bash
icat partition4.img 32716 | base64 -d
```

```
573417h13r_7h4n_7h3_1457_...
```

Leetspeak for `stealthier_than_the_last_...`, wrapped in the standard
`picoCTF{}` format.

## Flag

```
picoCTF{573417h13r_7h4n_7h3_1457_...}
```

_Truncated deliberately — this came through a graded course, so the full flag
isn't published here._

## Learn more

**Why a timeline beats searching.** Grep answers "where is this string?" A
timeline answers "what happened, in what order?" When you know something was
tampered with but not what, the second question is the one with an answer. The
`.ash_history` in step 4 established tampering; only the timeline could say
which files arrived alongside it.

**What MACB actually means.** Every file carries four timestamps:

| | Name | Updated when |
| --- | --- | --- |
| **M** | Modified | file contents change |
| **A** | Accessed | file is read |
| **C** | Changed | inode metadata changes (permissions, owner, link count) |
| **B** | Birth | file is created |

C is the one people misread: it is *metadata* changed, not contents changed, and
unlike the other three it cannot be set backwards through normal filesystem
calls. That makes a mismatch between C and M a classic timestomping tell — if a
file claims it was modified in 2019 but its inode changed last Tuesday, someone
rewrote the timestamps.

Birth time is not universal. It exists on ext4, NTFS and APFS, but ext3 has no
field for it, and there `...b` entries simply won't appear.

**The body file** is Sleuth Kit's intermediate format, one pipe-delimited line
per file holding the path, inode and all four timestamps. Splitting the work in
two — `fls` extracts, `mactime` sorts and renders — means one expensive pass over
the image produces a `body.txt` you can re-render repeatedly with different
timezones or date ranges without touching the image again.

**One habit worth changing.** Decoding the base64 through a web tool works, but
`base64 -d` is already installed and doesn't hand challenge data to a third
party. On a real engagement that distinction matters; building the habit on
practice challenges is free.

- [Sleuth Kit — mactime](https://www.sleuthkit.org/sleuthkit/man/mactime.html)
- [Sleuth Kit — fls](https://www.sleuthkit.org/sleuthkit/man/fls.html)

## Tools

- `mmls` — check for a partition table (and confirm there isn't one)
- `fls` — list the file tree; `-m` emits a mactime body file
- `mactime` — render the body file as a chronological timeline
- `icat` — read a file's contents by inode number
- `base64` — decode the payload
