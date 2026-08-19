---
title: convertme.py
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [python, binary, number-bases]
status: published
---

# convertme.py

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

Run the given `convertme.py`. It asks for one decimal→binary conversion and
prints the flag if you get it right.

```bash
wget https://artifacts.picoctf.net/c/22/convertme.py
python convertme.py
```

## TL;DR

Answer the decimal number in binary. `18` → `10010`. Get it right and it prints
the flag.

## Approach

### 1. Read the script

```python
if ans_num == num:
    flag = str_xor(flag_enc, 'enkidu')
    print("... your flag: " + flag)
```

It picks a random `num` in 10–100, reads your answer with `int(ans, base=2)`, and
if it matches, decrypts the flag. Nothing adversarial — just convert correctly.

### 2. Answer in binary

```
If 18 is in decimal base, what is it in binary base?
Answer: 10010
That is correct! Here's your flag: picoCTF{4ll_y0ur_b4535_...}
```

<details>
<summary>What didn't work here</summary>

**Tried:** answering `10100` for `19`.

```
20 and 19 are not equal.
```

**Why it failed:** a conversion slip. `19` is `10011` (16+2+1); `10100` is `20`.
The script confirms exactly what it read back as decimal, which makes the
off-by-one obvious. The number is re-randomised each run, so there's nothing to
memorise — just convert the one you're shown.

</details>

## Flag

```
picoCTF{4ll_y0ur_b4535_...}
```

_Truncated — graded course._

## Learn more

`num` is randomised per run, but the flag isn't — it's a fixed XOR of `flag_enc`
against the hardcoded key `'enkidu'`. So you never actually need to answer the
question; the key is right there in the source. Lifting the two functions:

```python
print(str_xor(flag_enc, 'enkidu'))   # prints the flag directly
```

Answering the prompt is the intended path and takes ten seconds, but noticing
that the "gate" and the "secret" are independent — the check gates nothing, the
key is in the file — is the more useful habit for later challenges where the gate
is the whole point.

Quick conversions: `python -c "print(bin(18))"` gives `0b10010`, or
`printf '%b' ...` / `echo "obase=2;18" | bc`.

## Tools

`python`, `wget`
