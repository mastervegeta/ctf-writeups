---
title: Wrapped Up
event: example
category: cryptography
points: 50
difficulty: easy
date: 2026-08-18
tags: [base64, rot13, cyberchef]
status: published
---

<!--
This is an illustrative example, not a real challenge. It lives in templates/
so it stays out of the index. It exists to show the shape of a finished
writeup — especially where dead ends go.
Every command and output below was actually run.
-->

# Wrapped Up

> **Event:** example · **Category:** cryptography

## Challenge

> We intercepted this message but it's been through the wringer. Can you unwrap it?
>
> `Y3ZwYlBHU3tlMGdfMTNfdmZfYTBnX3JhcGVsY2d2MGF9`

Two layers, and the challenge text says so ("been through the wringer") without
saying which two.

## TL;DR

The string is base64. Decoding it yields something with an intact flag shape but
unpronounceable contents, which means the inner layer substitutes letters rather
than re-encoding bytes. It's ROT13.

## Approach

### 1. Recognise the outer layer

Mixed case, digits, no characters outside the base64 alphabet, length a multiple
of four. That's base64 with high confidence before running anything.

```bash
echo 'Y3ZwYlBHU3tlMGdfMTNfdmZfYTBnX3JhcGVsY2d2MGF9' | base64 -d
```

```
cvpbPGS{e0g_13_vf_a0g_rapelcgv0a}
```

The `XXX{...}` flag structure survived, so the layout is intact. But the wrapper
reads `cvpbPGS` where a picoCTF flag reads `picoCTF`, and the body is
unpronounceable.

<details>
<summary>What didn't work here</summary>

**Tried:** piping the result through `base64 -d` again, on the assumption that
"through the wringer" meant nested base64.

```
base64: stdin: (null): error decoding base64 input stream
```

**Why it failed:** `{`, `}` and `_` are not in the base64 alphabet, so a second
decode could never be well-formed. The presence of structural characters is
itself the evidence that the inner layer is a *cipher over text*, not an
*encoding of bytes* — which is the observation that picks step 2.

</details>

### 2. Identify and undo the inner layer

Only letters are scrambled; digits, `_`, `{` and `}` pass through untouched. That
rules out anything byte-oriented and points at a substitution over `[A-Za-z]`.
ROT13 is the one to try first, because it is the one CTFs use.

```bash
echo 'cvpbPGS{e0g_13_vf_a0g_rapelcgv0a}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

```
picoCTF{r0t_13_is_n0t_encrypti0n}
```

<details>
<summary>What didn't work here</summary>

**Tried:** writing the replacement set as `'n-za-mN-ZA-M'`, which looks like the
same rotation and is easy to reach for if you think of ROT13 as "shift the
letters and it'll sort itself out."

```
PICOctf{R0T_13_IS_N0T_ENCRYPTI0N}
```

**Why it failed:** `tr` maps the two sets positionally, character by character.
The search set `A-Za-z` starts with uppercase, so the replacement set must also
start with uppercase (`N-ZA-M`) or every letter gets its case flipped along with
its position. The output is a correct rotation with inverted case — close enough
to look like a near miss, which is exactly what makes it a time sink. Read it as
a case bug, not a cipher bug.

</details>

## Flag

```
picoCTF{r0t_13_is_n0t_encrypti0n}
```

## Learn more

ROT13 is a Caesar shift of 13 over a 26-letter alphabet, which makes it its own
inverse: applying it twice returns the original. That self-inverse property is
why it survives as an obfuscation convention rather than a security measure — it
was a Usenet habit for hiding punchlines and spoilers, where the goal was
stopping accidental reading, not determined reading.

The transferable lesson is the one from step 1: **which characters survive a
transformation tells you what kind of transformation it was.** An encoding maps
arbitrary bytes into a restricted alphabet, so structural characters like `{`
disappear. A substitution cipher maps letters to letters, so structure survives.
You can usually tell which layer you are looking at before running anything.

- [CyberChef](https://gchq.github.io/CyberChef/) — its "Magic" operation detects
  both of these layers automatically, and is worth trying before hand-writing a
  pipeline.

## Tools

- `base64` — decoding the outer layer
- `tr` — ROT13 as a positional character-range translation
