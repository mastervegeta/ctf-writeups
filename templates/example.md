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
An illustrative example, not a real challenge. Lives in templates/ so it stays
out of the index. Shows the shape of a finished writeup — especially where dead
ends go, and how short one should be. Every command below was actually run.
-->

# Wrapped Up

> **Event:** example · **Category:** cryptography

## Challenge

> We intercepted this message but it's been through the wringer. Can you unwrap it?
>
> `Y3ZwYlBHU3tlMGdfMTNfdmZfYTBnX3JhcGVsY2d2MGF9`

## TL;DR

Base64 on the outside. Decoding it gives an intact flag shape with
unpronounceable contents, which means the inner layer substitutes letters rather
than re-encoding bytes. It's ROT13.

## Approach

### 1. Recognise the outer layer

Mixed case, digits, nothing outside the base64 alphabet, length a multiple of
four.

```bash
echo 'Y3ZwYlBHU3tlMGdfMTNfdmZfYTBnX3JhcGVsY2d2MGF9' | base64 -d
```

```
cvpbPGS{e0g_13_vf_a0g_rapelcgv0a}
```

The `XXX{...}` structure survived, but the wrapper reads `cvpbPGS` where a
picoCTF flag reads `picoCTF`.

<details>
<summary>What didn't work here</summary>

**Tried:** piping that through `base64 -d` again, reading "through the wringer"
as nested base64.

```
base64: stdin: (null): error decoding base64 input stream
```

**Why it failed:** `{`, `}` and `_` aren't in the base64 alphabet, so a second
decode could never be well-formed. Their presence is the evidence that the inner
layer is a cipher over text, not an encoding of bytes.

</details>

### 2. Undo the inner layer

Only letters are scrambled; digits and `_{}` pass through untouched. That's a
substitution over `[A-Za-z]`, and ROT13 is the one CTFs use.

```bash
echo 'cvpbPGS{e0g_13_vf_a0g_rapelcgv0a}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

```
picoCTF{r0t_13_is_n0t_encrypti0n}
```

<details>
<summary>What didn't work here</summary>

**Tried:** writing the replacement set as `'n-za-mN-ZA-M'`.

```
PICOctf{R0T_13_IS_N0T_ENCRYPTI0N}
```

**Why it failed:** `tr` maps the two sets positionally. The search set `A-Za-z`
starts with uppercase, so the replacement must too (`N-ZA-M`) or every letter
gets its case flipped along with its position. A correct rotation with inverted
case looks like a near miss, which is what makes it a time sink — read it as a
case bug, not a cipher bug.

</details>

## Flag

```
picoCTF{r0t_13_is_n0t_encrypti0n}
```

## Learn more

ROT13 is a Caesar shift of 13 over 26 letters, making it its own inverse —
applying it twice returns the original. That's why it survives as an obfuscation
convention rather than a security measure.

The transferable lesson is from step 1: **which characters survive a
transformation tells you what kind it was.** An encoding maps bytes into a
restricted alphabet, so structural characters disappear. A substitution cipher
maps letters to letters, so structure survives.

- [CyberChef](https://gchq.github.io/CyberChef/) — its "Magic" operation detects
  both layers automatically

## Tools

`base64`, `tr`
