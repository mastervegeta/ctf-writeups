---
title: New Ceasar
event: cylabacademy
category: cryptography
points:
difficulty: medium
date: 2026-08-20
tags: [python, ciphers, caesar, brute-force, encoding]
status: published
---

# New Ceasar

> **Event:** cylabacademy · **Category:** cryptography

## Challenge

Source is provided, with the flag and key redacted. The ciphertext:

```
fegdeogdgecoeocgcgchcfcffccfca
```

```python
LOWERCASE_OFFSET = ord("a")
ALPHABET = string.ascii_lowercase[:16]      # a..p

def b16_encode(plain):
        enc = ""
        for c in plain:
                binary = "{0:08b}".format(ord(c))
                enc += ALPHABET[int(binary[:4], 2)]   # high nibble
                enc += ALPHABET[int(binary[4:], 2)]   # low nibble
        return enc

def shift(c, k):
        t1 = ord(c) - LOWERCASE_OFFSET
        t2 = ord(k) - LOWERCASE_OFFSET
        return ALPHABET[(t1 + t2) % len(ALPHABET)]

assert all([k in ALPHABET for k in key])
assert len(key) == 1
```

Each plaintext byte becomes two letters from `a`–`p` — one per nibble — and then
every letter is Caesar-shifted by the key, mod 16.

## TL;DR

The two `assert` lines are the whole challenge. They pin the key to **one**
character drawn from `a`–`p`, so the keyspace is 16. Brute force all of them,
undo the shift, then undo the base-16 encoding. Key is `p`.

## Approach

### 1. Reverse `b16_encode`

`a` is `01100001`, split into `0110` and `0001`, so it encodes to `gb`. Going
back: map each letter to its 4-bit index, glue pairs together, `chr()` the byte.

```python
reverse_alphabet = {c: "{0:04b}".format(i) for i, c in enumerate(ALPHABET)}

def b16_decode(encoded):
    out = ""
    for i in range(0, len(encoded), 2):
        hi = reverse_alphabet[encoded[i]]
        lo = reverse_alphabet[encoded[i + 1]]
        out += chr(int(hi + lo, 2))
    return out
```

30 ciphertext characters → 15 plaintext bytes.

### 2. Get stuck on the key, then read the asserts

This is where it stalled. `shift` is reversible only if you know `k`, and a key
like `keythatsimpossibletobruteforce` would end the attempt right there.

<details>
<summary>What didn't work here</summary>

**Tried:** treating the key as an arbitrary-length string and looking for a way
to recover it from the ciphertext alone — a Vigenère-style attack.

**Why it failed:** nothing was wrong with the reasoning, only with the
assumption. 15 bytes is far too little for frequency analysis against an
unknown-length key. The two `assert` lines sitting above the redacted `key = `
answer the question the attack was trying to answer: every key character is in
`a`–`p`, and there is exactly one of them. Read the constraints before attacking
the algorithm — a repeating-key cipher with a length-1 key is just Caesar.

</details>

### 3. Invert the shift and brute force 16 keys

```python
def reverse_shift(letter, key):
    t3 = ord(letter) - LOWERCASE_OFFSET
    t2 = ord(key) - LOWERCASE_OFFSET
    return ALPHABET[(t3 - t2) % 16]

for key in ALPHABET:
    unshifted = "".join(reverse_shift(c, key) for c in encoded_and_ciphered)
    print(key, repr(b16_decode(unshifted)))
```

Order matters: shift last means un-shift first, then `b16_decode`. Only two of
the 16 keys decode to entirely printable bytes, and one of those is the flag.

```
a  "TcNcd.N&&'%%R% "
...
o  'v\x85`\x85\x86@`HHIGGtGB'
p  'et_tu?_77866c61'
```

## Flag

```
picoCTF{et_tu?_77866c61}
```

## Learn more

The interesting move here is *where* the shift is applied. Caesar normally acts
on the plaintext; this one acts on the nibble stream after encoding, adding the
key to each 4-bit half of a byte separately and dropping the carry between them.
So a wrong key doesn't produce a uniformly offset copy of the plaintext: each
byte moves by `17k`, `17k-16`, `17k-256` or `17k-272` depending on which of its
two nibbles wrap. That's why the 16 candidate lines read as noise instead of as
16 legible near-misses.

Printability is enough of a filter to skip eyeballing all 16 lines:

```python
if all(32 <= ord(ch) < 127 for ch in decoded): print(key, decoded)
```

That leaves `a` and `p`; `a` is `TcNcd.N&&'%%R% `, which is printable but not
words. With a keyspace of 16 there is no need to be clever, but the habit
matters when the space is 2²⁴ instead.

- ["Et tu, Brute?"](https://en.wikipedia.org/wiki/Et_tu,_Brute%3F) — the flag
  text, from Shakespeare's *Julius Caesar*, hence the challenge name.

## Tools

`python3`
