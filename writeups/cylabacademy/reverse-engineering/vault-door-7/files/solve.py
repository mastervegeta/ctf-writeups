#!/usr/bin/env python3
"""vault-door-7 — unpack the 8 check constants back into the 32-char password.

passwordToIntArray packs 4 ASCII bytes per int, big-endian, first char in the
high byte. It is a bijection, so the constants *are* the password.
"""

CONSTANTS = [
    1096770097, 1952395366, 1600270708, 1601398833,
    1716808014, 1734287392,  942891831,  876032566,
]

password = b"".join(n.to_bytes(4, "big") for n in CONSTANTS).decode("ascii")

for n in CONSTANTS:
    print(f"{n:>11}  0x{n:08X}  {format(n, '032b')}  {n.to_bytes(4, 'big').decode()!r}")

assert len(password) == 32, len(password)
print(f"\npassword: {password!r}")
print(f"flag:     picoCTF{{{password}}}")
