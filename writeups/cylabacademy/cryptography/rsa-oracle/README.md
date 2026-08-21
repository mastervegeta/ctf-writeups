---
title: RSA Oracle
event: cylabacademy
category: cryptography
points:
difficulty: medium
date: 2026-08-21
tags: [rsa, malleability, chosen-ciphertext, python, openssl]
status: published
---

# RSA Oracle

> **Event:** cylabacademy · **Category:** cryptography

## Challenge

An intercepted message (`secret.enc`, AES) plus the RSA-encrypted password used
to encrypt it (`password.enc`). A network service acts as an oracle: it will
encrypt anything you give it, and decrypt anything *except* the intercepted
ciphertext itself.

So: recover the AES password from its RSA ciphertext, using an oracle that
refuses to decrypt that one value.

## TL;DR

Textbook RSA is multiplicative: `(a·b)^e ≡ a^e · b^e (mod n)`. Encrypt a space
(`0x20` = 32) to get `32^e`, multiply it by the intercepted `c = m^e`, and hand
the product to the decrypt oracle. It's a different ciphertext, so the blocklist
doesn't fire, and it decrypts to `32m`. Divide by 32.

## Approach

### 1. Get `32^e mod n` from the encrypt oracle

Sending a space through the encryption side gives the ciphertext of 32:

```
' ' : 39709217158430889390349573249113506262122409504708629289777876639774066084
      68604142079377234654007309935996972791790270166961305129444105909465676647301056
```

512-bit modulus, so `n` is out of factoring range — no point trying.

<details>
<summary>What didn't work here</summary>

**Tried:** feeding `password.enc` straight to the decrypt oracle.

**Why it failed:** that exact ciphertext is blocklisted — it's the whole point
of the challenge. The blocklist is on the *ciphertext value*, though, not on the
plaintext behind it, and RSA malleability lets you change the value while
keeping control of the plaintext.

</details>

### 2. Multiply the two ciphertexts

```python
c_space = 3970921715843088939034957324911350626212240950470862928977787663977406608468604142079377234654007309935996972791790270166961305129444105909465676647301056
c_pw    = 1634668422544022562287275254811184478161245548888973650857381112077711852144181630709254123963471597994127621183174673720047559236204808750789430675058597
print(c_pw * c_space)   # 307 digits
```

No need to reduce mod `n` — the server does that itself before exponentiating.
Paste the product into the decrypt oracle:

```
68726a6aca0
```

### 3. Undo the multiply

The oracle returns hex. `0x68726a6aca0` is 11 hex digits — odd, so it won't
decode as bytes directly. That's the `×32` still in there (32 = 2⁵, a 5-bit
shift):

```python
m = 0x68726a6aca0 // 32     # 224298087781
bytes.fromhex(hex(m)[2:])   # b'4955e'
```

Password: `4955e`.

### 4. Decrypt the message

```bash
openssl enc -aes-256-cbc -d -in secret.enc -k 4955e
```

## Flag

```
picoCTF{su((3ss_(r@ck1ng_r3@_...}
```

## Learn more

Malleability is a property of *textbook* RSA — encryption with no padding. Real
RSA uses OAEP (PKCS#1 v2), which pads the message with randomness and a hash
before exponentiating; the product of two OAEP ciphertexts decrypts to garbage
that fails the padding check, so this attack dies there. PKCS#1 v1.5 padding
also breaks the multiplication, though it has [its own problem](https://en.wikipedia.org/wiki/Adaptive_chosen-ciphertext_attack).

Picking 32 rather than 2 was luck that paid off: the plaintext is ASCII, and
multiplying by 2⁵ shifts it off byte boundaries, which is exactly the clue that
the hex has an odd digit count. Any small factor works as long as you divide it
back out before decoding.

- [RSA blinding](https://en.wikipedia.org/wiki/Blinding_(cryptography)) — the
  same trick used defensively, to hide a message from the entity signing it.

## Tools

`python3`, `openssl`, `nc`
