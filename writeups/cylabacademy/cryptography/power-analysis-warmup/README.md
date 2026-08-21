---
title: "Power Analysis: Warmup"
event: cylabacademy
category: cryptography
points:
difficulty: hard
date: 2026-08-22
tags: [side-channel, aes, sbox, pwntools, python]
status: published
---

# Power Analysis: Warmup

> **Event:** cylabacademy · **Category:** cryptography

## Challenge

> `nc saturn.picoctf.net 49572`
>
> (the port changes per instance)

A service runs one round of AES-like encryption over a plaintext you supply and
tells you nothing about the ciphertext — only how many of the 16 SBox outputs
had their lowest bit set. Recover the key.

The handout source is the whole attack surface:

```python
def leaky_aes_secret(data_byte, key_byte):
    out = Sbox[data_byte ^ key_byte]
    leak_buf.append(out & 0x01)
    return out

def encrypt(plaintext, key):
    return [leaky_aes_secret(plaintext[i], key[i]) for i in range(16)]

def encrypt_and_leak(plaintext):
    encrypt(plaintext, SECRET_KEY)
    return leak_buf.count(1)
```

## TL;DR

There is no diffusion: byte `i` of the plaintext only ever meets byte `i` of the
key, so the 16 bytes are 16 independent 8-bit problems. Find a plaintext that
leaks `0`, then vary one byte through all 256 values. The leak count is now
exactly `Sbox[v ^ k] & 1` for that position, and the 256-bit response pattern is
unique to `k`.

## Approach

### 1. Talk to the service with pwntools

Connect, wait for the prompt, send hex, parse the number back out.

```python
connection = remote("saturn.picoctf.net", port)
connection.recvuntil("Please")
connection.sendline(payload)
result = int(connection.recvline().strip().decode().split("result: ")[1])
```

### 2. Find an anchor plaintext that leaks 0

The leak sums all 16 positions, so a varying byte is buried in noise from the
other 15 — unless they all contribute 0. Since each contributes 0 or 1, a total
of 0 means every position is silent.

Found by hill-climbing one byte at a time: change a byte, and if the count went
*up*, keep the old value; if it went *down*, keep the new one.

```
00ff00f100ffeef100eef1eef11a0000  ->  leakage result: 0
```

### 3. Fingerprint each position

Offline, build what the 256 responses would look like for every candidate key
byte, then probe the real thing and match:

```python
comparisonmap_dict[f"{candidate:02x}"] = [Sbox[candidate ^ i] & 0x01 for i in range(256)]
```

All 256 patterns are distinct, so a match is unambiguous.

```bash
python3 solve_byte.py 49572 0 2
```

```
bytes 0-2 of the key = 81
```

<details>
<summary>What didn't work here</summary>

**Tried:** looping all 16 positions inside one script and printing the whole key
at the end.

**Why it failed:** that's 16 × 256 = 4096 connections in a row, and the server
starts refusing them partway through — the run dies on a closed connection with
nothing to show. Running one position per invocation is 256 connections, which
survives. `sys.argv` for the byte offsets, because editing the constants in
`nano` sixteen times gets old fast.

</details>

### 4. Repeat for all 16 positions

```
81 80 8c 36 fc a7 28 8b 8a 57 f9 09 07 cc ba e6
```

```
81808c36fca7288b8a57f90907ccbae6
```

## Flag

```
picoCTF{81808c36fca7288b8a57f90907ccbae6}
```

## Learn more

This is differential power analysis with the measurement noise removed. Real DPA
scopes a chip's power draw during encryption — the Hamming weight of an SBox
output shows up as a tiny current difference — and needs statistics over
thousands of traces to pull the key byte out. Here the oracle just hands you one
clean bit per SBox call, so the same key-byte-at-a-time structure works with no
averaging.

Two things make it cheap. Only the first round is implemented, so there is no
diffusion to spread a key byte across the block. And the SBox low bit is
balanced — 128 of the 256 entries have it set — so an anchor plaintext leaking 0
exists for any key, and the response pattern carries real information at every
probe.

All 256 probes per byte are overkill: the first 22 values (`0x00`–`0x15`) already
separate all 256 candidates, which would have brought the full key down to 352
connections and made the one-shot script viable.

- [picoCTF: Power Analysis](https://play.picoctf.org/practice?search=power%20analysis) — the follow-up challenges add the noise back

## Tools

`pwntools`, `python3`
