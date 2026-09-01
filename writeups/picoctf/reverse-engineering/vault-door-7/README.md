---
title: vault-door-7
event: picoctf
category: reverse-engineering
points: 400
difficulty: hard
date: 2026-09-01
tags: [java, bit-shifting, endianness, ascii, packing]
status: published
---

# vault-door-7

> **Event:** picoctf · **Category:** reverse-engineering

## Challenge

> This vault uses bit shifts to convert a password string into an array of
> integers.
>
> Source: [`VaultDoor7.java`](files/VaultDoor7.java)

Recover the 32-character password that makes `checkPassword` return true.

## TL;DR

`passwordToIntArray` doesn't encrypt anything — it *repacks*. Four ASCII bytes
go into one int, big-endian, and nothing is lost. So the eight constants the
check compares against **are** the password. Split each int back into four bytes
and read them as ASCII.

## Approach

### 1. Read the packing direction

```java
x[i] = hexBytes[i*4] << 24
     | hexBytes[i*4+1] << 16
     | hexBytes[i*4+2] << 8
     | hexBytes[i*4+3];
```

The first character lands in the *high* byte. That's big-endian, and it's a
bijection — 32 chars in, 8 ints out, zero collisions. Reversing it needs no
brute force, just the same shifts backwards.

### 2. Print the constants as binary

I added a `decode_everything()` to the challenge file so the numbers came out of
the same JVM that produced them:

```java
String binary_string = Integer.toBinaryString(int_array[i]);
binary_array[i] = String.format("%32s", binary_string).replace(' ', '0');
```

```
01000001010111110110001000110001
01110100010111110011000001100110
...
```

Then split each row into four 8-bit groups and read them as ASCII.

<details>
<summary>What didn't work here</summary>

**Tried:** `Integer.toBinaryString(int_array[i])` on its own, without the
`String.format("%32s", ...)` pad.

**Why it failed:** it emits the *shortest* representation, dropping leading
zeros. `942891831` comes back 30 bits wide, not 32, so slicing it into four
8-bit groups is off by two and every character in that word decodes to garbage.
The rows that happened to have a set high bit looked fine, which is what made it
confusing — only some of the output was wrong.

</details>

### 3. Same thing, checkable

```bash
python3 -c "print(b''.join(n.to_bytes(4,'big') for n in [1096770097,1952395366,1600270708,1601398833,1716808014,1734287392,942891831,876032566]).decode())"
```

```
A_b1t_0f_b1t_sh1fTiNg_  83c74726
```

### 4. Mind the two spaces

`1734287392` is `0x675F2020` — `g`, `_`, **space, space**. The password is 30
meaningful characters right-padded into 32 so it divides evenly into 8 ints, and
`checkPassword` rejects anything that isn't exactly 32 long. Other public
instances of this challenge have a 10-hex-character tail and need no padding, so
the spaces are easy to dismiss as a decoding bug rather than the answer.

## Flag

```
picoCTF{A_b1t_0f_b1t_sh1fTiNg_  83c74726}
```

(Two literal spaces before `83c74726`. Copy-paste through anything that collapses
whitespace and the vault denies you.)

## Learn more

Java's `byte` is signed. `hexBytes[i*4] << 24` promotes to `int` with sign
extension first, so a byte ≥ `0x80` would set the top 24 bits and corrupt its
neighbours through the `|`. The challenge gets away with it because ASCII is
7-bit — a real serializer would need `& 0xFF` on every term.

The transferable point: **shifting and masking rearrange bits, they don't hide
them.** Any transform that is a bijection on the input is invertible by
construction, so the question is never "can I break this" but "which direction do
I run it". `struct.unpack('>8I', ...)` or pwntools' `p32`/`u32` do step 3 in one
call.

- [Java Language Specification §5.6, numeric promotion](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html#jls-5.6)

## Tools

`javac`, `java`, `python3`
