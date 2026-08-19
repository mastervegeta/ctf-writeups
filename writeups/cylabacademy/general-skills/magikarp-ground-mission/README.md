---
title: Magikarp Ground Mission
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [ssh, filesystem, navigation]
status: published
---

# Magikarp Ground Mission

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

SSH in. The flag is split into three parts, each in a different directory, with a
breadcrumb file at each stop telling you where the next one is.

```bash
ssh -p 64179 ctf-player@wily-courier.picoctf.net    # password provided
```

## TL;DR

Part 1 is in your home directory, part 2 at `/` (filesystem root), part 3 back at
`~`. `cat` each `Nof3.flag.txt` and concatenate.

## Approach

### 1. Part 1 — where you land

```bash
ls                              # 1of3.flag.txt  instructions-to-2of3.txt
cat 1of3.flag.txt               # picoCTF{xxsh_
cat instructions-to-2of3.txt    # go to the root of all things, `/`
```

### 2. Part 2 — the root directory

```bash
cd /
cat 2of3.flag.txt               # 0ut_0f_//4t3r_
cat instructions-to-3of3.txt    # go home... `~`
```

### 3. Part 3 — home

```bash
cd ~
cat 3of3.flag.txt               # 0b24fc4f}
```

Join the three parts in order for the flag.

## Flag

```
picoCTF{xxsh_0ut_0f_//4t3r_...}
```

_Truncated — graded course._

## Learn more

The whole challenge is two navigation shortcuts, which is the point:

- **`/`** is the filesystem root — the top of everything, an absolute path that
  means the same thing from any directory.
- **`~`** is your home directory (`/home/ctf-player` here), where an SSH session
  drops you by default.

`cd` with no argument also goes home, and `cd -` returns to the previous
directory. The flag text — "xxsh out of water" — is a Magikarp joke; the
challenge just wants you comfortable moving around a filesystem by absolute path
and shortcut rather than only relative `cd foldername` steps.

## Tools

`ssh`, `cd`, `cat`
