---
title: "Power Analysis: Part 1"
event: cylabacademy
category: cryptography
points:
difficulty: hard
date: 2026-08-22
tags: [side-channel, aes, cpa, dpa, scared, pwntools, numpy, python]
status: published
---

# Power Analysis: Part 1

> **Event:** cylabacademy · **Category:** cryptography

## Challenge

> `nc saturn.picoctf.net 49404`
>
> (the port changes per instance)

Send a 16-byte plaintext as 32 hex chars, get back a power trace — a long list
of integers, one per sample, of the power drawn while the service encrypted it
under a fixed key. Recover the key.

## TL;DR

The warmup handed over one clean leak bit per call; here the leak is buried in a
noisy trace, so it is textbook CPA. Collect a few hundred (plaintext, trace)
pairs, correlate every trace sample against the Hamming weight of
`Sbox[plaintext ^ key]` for all 256 candidates at each of the 16 byte positions,
take the argmax. `scared` implements the whole attack — the work is plumbing.

## Approach

### 1. Reuse the warmup's I/O

Same protocol shape as [Power Analysis: Warmup](../power-analysis-warmup/), so
the connect/send/parse function carried over with only the parse changed: the
reply is a bracketed list instead of a single integer.

```python
connection = remote("saturn.picoctf.net", portnumber)
connection.recvuntil(b"hex: ")
connection.sendline(payload.encode())
readoutput = connection.recvline().strip().decode()

result_currently = readoutput.split("result:  ")[1]
result_without_braces = result_currently.strip("[").strip("]")
trace = [int(i) for i in result_without_braces.split(", ")]
```

One connection per trace, `context.log_level = "error"` to stop pwntools
printing 300 connection banners.

### 2. Random plaintexts

CPA needs the plaintext byte at each position to vary independently across
traces, which random 32-hex strings give for free.

```python
hex_alphabet = string.hexdigits[:16]   # drop uppercase ABCDEF
"".join(random.choices(hex_alphabet, k=32))
```

### 3. Hand it to scared

`estraces` wants the traces as a 2-D float array and the plaintexts as `uint8`,
one row per trace:

```python
heat_array = numpy.array(heat_data, dtype="float32")        # (300, samples)
plaintext_array = numpy.array(plaintexts, dtype="uint8")    # (300, 16)

ths = read_ths_from_ram(samples=heat_array, plaintext=plaintext_array)

attack = scared.CPAAttack(
    selection_function=scared.aes.selection_functions.encrypt.FirstSubBytes(),
    model=scared.HammingWeight(),
    discriminant=scared.maxabs,
)
attack.run(scared.Container(ths))
```

`FirstSubBytes` is the first-round SBox output, `HammingWeight` is the leakage
model, `maxabs` collapses each candidate's per-sample correlations to its
strongest peak. `attack.scores` comes back as 256 candidates × 16 byte
positions, so the key is one argmax down the candidate axis:

```python
key = numpy.abs(attack.scores).argmax(axis=0)
print(bytes(key.tolist()).hex())
```

```
recovered key:  4999139026d84bf29a279e48d4edec53
```

300 traces was enough. No plotting, no window-picking, no alignment — the
service's traces are already aligned and cheap.

<details>
<summary>What didn't work here</summary>

**Tried:** `pip install scared` into the venv on this machine (Intel macOS 26,
CPython 3.12).

**Why it failed:** scared pulls in numba, and numba/llvmlite stopped shipping
macOS x86_64 wheels after 0.61.x, so pip tries to compile llvmlite from source
and dies in `ffi/build.py`. `pip install "numba<0.62" scared` gets a prebuilt
wheel — which in turn caps numpy at 2.2.x.

</details>

## Flag

```
picoCTF{4999139026d84bf29a279e48d4edec53}
```

## Learn more

CPA (correlation power analysis) picks the intermediate value an attacker can
predict from a known plaintext and a guessed key byte — here the first-round
SBox output — models its power cost as the Hamming weight, and computes
Pearson correlation between that prediction and the measured samples, per
candidate per sample. The correct candidate is the only one whose prediction
lines up with reality at the moment the chip actually handles that byte, so it
spikes; the other 255 stay near zero. Each key byte is independent, which is
what makes 16 × 256 guesses tractable.

- [scared documentation](https://eshard.gitlab.io/scared/) — `Container`,
  selection functions, and the other distinguishers (DPA, MIA, template)

## Tools

`pwntools`, `scared`, `estraces`, `numpy`, `python3`
