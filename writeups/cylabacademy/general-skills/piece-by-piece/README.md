---
title: Piece by Piece
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [ssh, cat, unzip, file-reassembly]
status: published
---

# Piece by Piece

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

SSH into a box where a password-protected zip has been split into pieces
(`part_aa` … `part_ae`). Reassemble it, unzip with the given password, read the
flag.

```
ssh -p 63345 ctf-player@dolphin-cove.picoctf.net    # password provided
```

## TL;DR

`cat part_a* > combined` joins the pieces back into one zip, then
`unzip combined` with the password `supersecret` extracts `flag.txt`. The split
is just a byte-wise cut — concatenation in order rebuilds the original.

## Approach

### 1. Get the SSH invocation right

```bash
ssh -p 63345 ctf-player@dolphin-cove.picoctf.net
```

<details>
<summary>What didn't work here</summary>

**Tried:** `ssh dolphin-cove.picoctf.net:63345`, then `ssh
dolphin-cove.picoctf.net@ctf-player -p 63345`, and other orderings.

```
ssh: Could not resolve hostname ctf-player: Name or service not known
```

**Why it failed:** two rules. The port is a flag, `-p 63345` — never `host:port`
(that's HTTP/URL syntax, not SSH). And the connection target is
`user@host`, so it's `ctf-player@dolphin-cove.picoctf.net`, not the reverse.
Every failure was the shell trying to resolve whatever landed in the host
position — `ctf-player` — as a hostname.

</details>

### 2. Read the instructions

```
ctf-player@pico-chall$ ls
instructions.txt  part_aa  part_ab  part_ac  part_ad  part_ae
```

`instructions.txt` says the pieces are a split zip, password `supersecret`.
The `part_aa`, `part_ab`, … naming is the default output of `split`.

### 3. Reassemble and extract

Concatenate in order — the glob sorts alphabetically, which is the right order:

```bash
cat part_a* > combined
unzip combined        # password: supersecret
cat flag.txt
```

<details>
<summary>What didn't work here</summary>

**Tried:** `cat part_ab` on a single piece to see what was in it.

**Why it failed:** it prints binary garbage. Each part is a raw byte-slice of a
zip, not a file on its own — only `part_aa` even begins with the `PK` zip magic.
A middle slice has no header and no structure; it's meaningless until joined back
to its neighbours.

</details>

## Flag

```
picoCTF{z1p_and_spl1t_f1l3s_4r3_fun_...}
```

_Truncated — graded course._

## Learn more

Splitting a file is a plain byte-wise cut, usually `split -b <size> bigfile
part_`, which emits `part_aa`, `part_ab`, … in order. There's no per-piece
header or checksum — the pieces only mean something reassembled, and
concatenation in the right order *is* the reassembly:

```bash
cat part_a* > combined     # relies on alphabetical glob order
```

If the pieces were numbered oddly you'd sort explicitly, but `split`'s `aa/ab/ac`
suffixes are designed so a shell glob already orders them correctly.

`unzip` handling the password inline (prompting once) is the last step; the flag
being `z1p_and_spl1t_f1l3s` spells out the two ideas — a zip, split.

## Tools

`ssh`, `cat`, `unzip`
