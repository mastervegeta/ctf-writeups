#!/usr/bin/env python3
"""New Ceasar — brute force the single-character key over ALPHABET (a..p).

The key is asserted to be one character from a..p, so there are 16 candidates.
Un-shift first, then reverse the base-16 encoding.
"""
import string

ALPHABET = string.ascii_lowercase[:16]
CIPHERTEXT = "fegdeogdgecoeocgcgchcfcffccfca"


def reverse_shift(letter, key):
    return ALPHABET[(ALPHABET.index(letter) - ALPHABET.index(key)) % 16]


def b16_decode(encoded):
    out = ""
    for i in range(0, len(encoded), 2):
        hi, lo = ALPHABET.index(encoded[i]), ALPHABET.index(encoded[i + 1])
        out += chr(hi * 16 + lo)
    return out


for key in ALPHABET:
    decoded = b16_decode("".join(reverse_shift(c, key) for c in CIPHERTEXT))
    printable = all(32 <= ord(ch) < 127 for ch in decoded)
    print(f"{key}  {'*' if printable else ' '}  {decoded!r}")
