---
title: Rogue Tower
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-18
tags: [wireshark, pcap, xor, known-plaintext, base64, imsi, python]
status: published
---

# Rogue Tower

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A packet capture, `rogue_tower.pcap`, downloaded from the challenge page. Find
the flag.

## TL;DR

One device in the capture associates with a cell tower broadcasting **PLMN
00101** — the reserved test-network code that IMSI catchers use — and then
exfiltrates a base64 payload to a different server than everyone else, split
across six HTTP POSTs. Reassembled and decoded it's XOR ciphertext, not text.
The key is the last 8 digits of the device's IMSI, but you never have to work
that out: because every flag starts `picoCTF{`, XORing the ciphertext against
that known prefix hands you the key directly.

## Approach

### 1. Survey the capture

![Wireshark packet list showing UDP tower beacons, DNS queries, and HTTP registration and upload traffic](files/wireshark-overview.png)

Even before filtering, the capture has an obvious rhythm. Most devices do the
same three things: a UDP broadcast on port 55000, a DNS lookup for
`device-<digits>.network.com`, then `GET /api/register` to **198.51.100.140**.

Two things break that pattern. Packets 17–22 are `POST /upload` — nothing else in
the capture uploads anything. And they go to **198.51.100.58**, a different host.

### 2. Find the rogue tower

The UDP broadcasts on port 55000 are tower beacons. There are only three:

```bash
tcpdump -r rogue_tower.pcap -A -n 'udp port 55000'
```

```
192.168.1.1.55000  > 255.255.255.255.55000: CARRIER: Verizon PLMN=310410 CELLID=15606
192.168.1.1.55000  > 255.255.255.255.55000: CARRIER: AT&T PLMN=310410 CELLID=15607
192.168.99.1.55000 > 255.255.255.255.55000: UNAUTHORIZED-TEST-NETWORK PLMN=00101 CELLID=92058
```

Two real carriers on **PLMN 310410**, broadcast from `192.168.1.1`. Then a third
beacon from a completely different source, `192.168.99.1`, announcing **PLMN
00101** — and it appears at t=16.4s, after which the anomalous traffic starts.

`00101` is not a carrier. MCC 001 / MNC 01 is the code reserved for test
networks, which is exactly what lab equipment and IMSI catchers broadcast.

### 3. Identify the compromised phone

The `GET /api/register` requests carry a revealing `User-Agent`. A normal one:

```
User-Agent: MobileDevice/1.0 (IMSI:310410955678402; CELL:15606)
```

And from `10.100.50.122`, the host doing the uploads:

```bash
tcpdump -r rogue_tower.pcap -A -n 'host 198.51.100.58'
```

```
GET /api/register HTTP/1.1
Host: network.carrier.com
User-Agent: MobileDevice/1.0 (IMSI:310410308555787; CELL:92058)
```

`CELL:92058` is the rogue tower's CELLID. That's the link, stated outright: this
device registered against the unauthorized tower, and its **IMSI is
310410308555787**. No need to correlate the DNS query — the User-Agent hands it
over.

### 4. Extract the exfiltrated payload

Six POSTs, each carrying a short base64 fragment as its body:

```
Content-Length: 9    QFFWWnZjf
Content-Length: 9    kxCCFJABm
Content-Length: 9    hbBFxUakE
Content-Length: 9    FQAtFb1xX
Content-Length: 9    VgEHAAQBR
Content-Length: 3    Q==
```

Note they're 9 characters each. Base64 decodes in 4-character groups, so **no
individual fragment is valid base64** — the chunk size is chosen so you have to
reassemble before decoding. Concatenated in packet order:

```
QFFWWnZjfkxCCFJABmhbBFxUakEFQAtFb1xXVgEHAAQBRQ==
```

<details>
<summary>What didn't work here</summary>

**Tried:** base64-decoding the reassembled string and reading the result.

**Why it failed:** it decodes cleanly — 34 bytes, no padding error — but the
output is binary garbage. That combination is the tell. A *malformed* base64
string means you reassembled it wrong; a *well-formed* one that decodes to
non-text means the base64 was only the transport, and there's another layer
underneath. Base64 is an encoding, not encryption, so garbage on the far side
means something encrypted it first.

</details>

<details>
<summary>What didn't work here (second attempt)</summary>

**Tried:** pasting the decoded bytes into online decryption tools with the IMSI
supplied as a "private key," after the hint said the IMSI was needed.

**Why it failed:** "private key" implies asymmetric crypto, and nothing here is
asymmetric — there's no keypair, no certificate, no handshake. The hint meant the
IMSI *is* the symmetric key material. Generic online tools also can't help when
you don't yet know the algorithm or which part of the IMSI to use. The step that
actually unblocks this is realising you can recover the key without guessing
either.

</details>

### 5. Recover the key with known plaintext

XOR has a property that makes it fragile here. If `c = p ^ k`, then
`k = c ^ p`. So any plaintext you already know reveals the key bytes underneath
it — and every picoCTF flag starts with the same 8 characters, `picoCTF{`.

XOR the first 8 ciphertext bytes against that crib:

```python
import base64

ct = base64.b64decode("QFFWWnZjfkxCCFJABmhbBFxUakEFQAtFb1xXVgEHAAQBRQ==")
crib = b"picoCTF{"

key = bytes(c ^ p for c, p in zip(ct, crib))
print(key)          # b'08555787'


def xor(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


print(xor(ct, key))
```

The recovered key is `08555787` — **the last 8 digits of IMSI 310410308555787**.
That's the confirmation the attack worked: an 8-byte key that turns out to be
meaningful, rather than 8 bytes of noise that happen to reproduce the crib.

Repeating it over the full 34 bytes gives the flag.

## Flag

```
picoCTF{r0gu3_c3ll_t0w3r_...}
```

_Truncated, matching the convention used across this repo._

## Learn more

**The key insight is that the crib attack skips the puzzle.** The hint pointed at
the IMSI, which invites you to guess *how* it becomes a key — all 15 digits? the
last 8? the MSIN? hashed? Known-plaintext XOR makes that question irrelevant. You
recover the key bytes from the ciphertext itself and only afterwards notice they
spell out part of the IMSI. When a scheme leaks its key to anyone who knows eight
bytes of plaintext, the derivation rule stops mattering.

**The limit worth knowing.** An `n`-character crib recovers exactly `n` key
bytes. Here the key was 8 bytes and `picoCTF{` is 8 characters, so one pass
recovered all of it — by design, but you should check rather than assume. Two
ways to tell you got it all: the decrypted output is entirely printable and reads
as sensible text, and it ends with the `}` you'd expect. If the key had been
longer, the first 8 characters would decode correctly and the rest would
degenerate into noise — a partial success that looks like a bug if you aren't
expecting it. The fix is a longer crib or trying candidate key lengths.

**Why the helper function.** In Python `^` works on integers, not `bytes`
objects, so `ct ^ key` raises `TypeError`. You have to iterate and XOR
byte-by-byte, and take the key modulo its length to repeat it across a longer
message — which is what `key[i % len(key)]` does.

**PLMN 001/01 is worth memorising.** MCC 001 / MNC 01 is reserved by the ITU for
test networks and never appears on a real commercial carrier. Seeing it in a
capture means lab equipment, a test rig, or an IMSI catcher. In this capture it's
the single fact that separates the rogue tower from the two real ones, and it
sits in plaintext in a UDP broadcast.

**Two smaller anomalies worth noticing.** The uploads run plaintext HTTP over
**port 443** — the port says TLS, the content says otherwise, and that mismatch
alone is worth a second look in any capture. And the exfil went to a different
destination IP than every legitimate registration, which is visible in the
packet list without decoding anything at all.

- [ITU-T E.212](https://www.itu.int/rec/T-REC-E.212) — the MCC/MNC assignments that reserve 001/01
- [Timeline 1](../timeline-1/), [Timeline 0](../timeline-0/) — other forensics writeups here

## Tools

- Wireshark — initial survey of the capture
- `tcpdump -A` — dumping payloads as ASCII from the command line
- Python — reassembly, base64 decode, and the XOR key recovery
