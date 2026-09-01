---
title: vault-door-8
event: cylabacademy
category: reverse-engineering
points:
difficulty: hard
date: 2026-09-01
tags: [java, bit-manipulation, involution, permutation, char-vs-byte]
status: published
---

# vault-door-8

> **Event:** cylabacademy · **Category:** reverse-engineering

## Challenge

> These pesky special agents keep reverse engineering our source code and then
> breaking into our secret vaults. THIS will teach those sneaky sneaks a lesson.
>
> Source: [`VaultDoor8.java`](files/VaultDoor8.java)

`scramble()` transposes pairs of bits in each character and the result is
compared against a hardcoded array. Recover the input.

Originally picoCTF 2019, reverse engineering, 450 points — hence the `picoCTF{}`
flag format.

## TL;DR

`switchBits` swaps two bits, so it is its own inverse. `scramble` is eight of
them composed, and the inverse of a composition of involutions is the same list
**applied in reverse order**. Paste the eight calls backwards into a
`reverse_scramble`, run the `expected[]` array through it, print the result.

## Approach

### 1. Confirm `switchBits` is an involution

```java
char rest  = (char)(c & ~(mask1 | mask2));
char shift = (char)(p2 - p1);
return (char)((bit1 << shift) | (bit2 >> shift) | rest);
```

`bit1` is either `0` or `1<<p1`, so shifting left by `p2-p1` puts it exactly at
`p2`, and `bit2` moves the other way. Everything else passes through `rest`
untouched. Applying it twice returns the original — verified over all 256 bytes.

### 2. Reverse the call list

`scramble` runs `(1,2) (0,3) (5,6) (4,7) (0,1) (3,4) (2,5) (6,7)`. Since each
step undoes itself, the inverse is that list read bottom-to-top:

```java
c = switchBits(c, 6, 7);  c = switchBits(c, 2, 5);  c = switchBits(c, 3, 4);
c = switchBits(c, 0, 1);  c = switchBits(c, 4, 7);  c = switchBits(c, 5, 6);
c = switchBits(c, 0, 3);  c = switchBits(c, 1, 2);
```

No algebra, no brute force over 256 candidates per position — and no need to
work out what the composite permutation actually is. (It's
`0→4 1→5 2→0 3→1 4→6 5→7 6→2 7→3`, if you want it.)

<details>
<summary>What didn't work here</summary>

**Tried:** writing the inverse steps as `switchBits(c, 2, 0)` and
`switchBits(c, 14, 3)`, i.e. naming the positions in "undo" order with the larger
index first.

**Why it failed:** the method's stated precondition is `p1 < p2`, and it is load-
bearing. `shift = (char)(p2 - p1)` on a negative difference wraps: `(char)(-2)`
is `65534`, and Java masks `int` shift distances to their low 5 bits, so
`65534 & 31 = 30` — you shift by 30 instead of 2. `switchBits('a', 2, 0)` returns
`0x60`: bit 0 is *destroyed*, not swapped, and the operation is no longer
self-inverse. `switchBits('i', 14, 3)` similarly just clears bit 3 and hands back
`'a'`. Both fail silently and still produce plausible-looking characters, which
is why they cost time.

</details>

### 3. Feed `expected[]` back through

```java
String expected_in_string = new String(expected);
System.out.println(new String(reverse_scramble(expected_in_string)));
```

```
s0m3_m0r3_b1t_sh1fTiNg_789e13a7e
```

Round-tripping it through `scramble` reproduces `expected[]` exactly.

## Flag

```
picoCTF{s0m3_m0r3_b1t_sh1fTiNg_789e13a7e}
```

## Learn more

Staying in `char` for step 3 is what makes it work. `expected[]` holds values
like `0xF4` and `0xC0`; a Java `char` is an unsigned 16-bit unit, so
`new String(char[])` carries them through unchanged. Route the same array
through `byte[]` or any charset conversion and everything above `0x7F` becomes
`?` or a two-byte UTF-8 pair, and the unscramble silently produces mush.

The structural idea is worth more than the challenge: a self-inverse operation
is an **involution**, and for a composition `f = tₙ ∘ … ∘ t₁` of involutions the
inverse is `t₁ ∘ … ∘ tₙ`. Recognising that turns "reverse this bit-twiddling
routine" into "retype these lines upside down" — the same reason
[vault-door-7](../vault-door-7/) falls apart the moment you notice its packing is
a bijection.

- [Java Language Specification §15.19, shift operators](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.19)
  — where the "low 5 bits" masking rule is defined

## Tools

`javac`, `java`, `python3`
