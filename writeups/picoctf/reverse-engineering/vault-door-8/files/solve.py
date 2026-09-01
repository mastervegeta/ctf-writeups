#!/usr/bin/env python3
"""vault-door-8 — undo scramble() by replaying its swaps in reverse order.

switchBits(p1, p2) transposes two bits, so it is an involution. scramble is
eight of them composed; the inverse is the same list read bottom-to-top.
"""

SWAPS = [(1, 2), (0, 3), (5, 6), (4, 7), (0, 1), (3, 4), (2, 5), (6, 7)]

EXPECTED = [
    0xF4, 0xC0, 0x97, 0xF0, 0x77, 0x97, 0xC0, 0xE4,
    0xF0, 0x77, 0xA4, 0xD0, 0xC5, 0x77, 0xF4, 0x86,
    0xD0, 0xA5, 0x45, 0x96, 0x27, 0xB5, 0x77, 0xF1,
    0xC2, 0xD2, 0x95, 0xD0, 0xF0, 0x94, 0xF1, 0x95,
]


def switch_bits(c, p1, p2):
    """Java's switchBits. Precondition p1 < p2 — see the writeup for why."""
    mask1, mask2 = 1 << p1, 1 << p2
    bit1, bit2 = c & mask1, c & mask2
    rest = c & ~(mask1 | mask2) & 0xFFFF
    shift = p2 - p1
    return ((bit1 << shift) | (bit2 >> shift) | rest) & 0xFFFF


def scramble(c):
    for p1, p2 in SWAPS:
        c = switch_bits(c, p1, p2)
    return c


def unscramble(c):
    for p1, p2 in reversed(SWAPS):
        c = switch_bits(c, p1, p2)
    return c


password = "".join(chr(unscramble(c)) for c in EXPECTED)

assert [scramble(ord(ch)) for ch in password] == EXPECTED, "round-trip failed"
assert all(switch_bits(switch_bits(c, 2, 5), 2, 5) == c for c in range(256))

print("composite permutation (input bit -> output bit):")
print({i: scramble(1 << i).bit_length() - 1 for i in range(8)})
print(f"\npassword: {password!r}")
print(f"flag:     picoCTF{{{password}}}")
