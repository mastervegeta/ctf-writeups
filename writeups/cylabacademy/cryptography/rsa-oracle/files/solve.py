#!/usr/bin/env python3
"""RSA Oracle — recover the AES password from its RSA ciphertext.

Textbook RSA is multiplicative, so c_pw * c_space decrypts to 32 * m.
The oracle refuses c_pw itself, but the product is a different value.
"""

# ciphertext of ' ' (0x20 = 32), from the encrypt oracle
C_SPACE = 3970921715843088939034957324911350626212240950470862928977787663977406608468604142079377234654007309935996972791790270166961305129444105909465676647301056

# the intercepted password ciphertext (password.enc)
C_PW = 1634668422544022562287275254811184478161245548888973650857381112077711852144181630709254123963471597994127621183174673720047559236204808750789430675058597

print(f"send to decrypt oracle: {C_PW * C_SPACE}")

# what the oracle gave back, as hex
BLINDED = 0x68726A6ACA0

m = BLINDED // 32
password = bytes.fromhex(f"{m:x}")
print(f"password: {password.decode()}")
print("openssl enc -aes-256-cbc -d -in secret.enc -k " + password.decode())
