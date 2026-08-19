---
title: Trivial Flag Transfer Protocol
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-19
tags: [wireshark, tftp, steghide, deb, caesar, steganography]
status: published
---

# Trivial Flag Transfer Protocol

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A packet capture. The name points at **TFTP** (Trivial File Transfer Protocol),
which is unencrypted, so files were transferred in the clear — but the flag was
disguised before sending.

## TL;DR

Filter to `tftp` and export the transferred files (Export Objects → TFTP): three
BMPs, a `plan`, and a `program.deb`. The `.deb` reveals the tool — **steghide** —
and the flag is embedded in `picture3.bmp` with the password `DUEDILIGENCE`:

```bash
steghide extract -sf picture3.bmp -p DUEDILIGENCE
# picoCTF{h1dd3n_1n_pLa1n_51GHT_...}
```

## Approach

### 1. Pull the files out of the capture

Filter `tftp`. The transfers are visible packet by packet — `instructions.txt`,
`plan`, three BMPs, and `program.deb`. The `plan` packet's payload is a run of
capitals that looks scrambled but pronounceable — a Caesar/ROT13 tell:

```
VHFRQGURCEBTENZNAQUVQVGJVGU-QHRQVYVTRAPR.PURPXBHGGURCUBGBF
```

```bash
echo 'VHFRQGURCEBTENZNAQUVQVGJVGU-QHRQVYVTRAPR.PURPXBHGGURCUBGBF' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
# IUSEDTHEPROGRAMANDHIDITWITH-DUEDILIGENCE.CHECKOUTTHEPHOTOS
```

> **I used the program and hid it with DUEDILIGENCE. Check out the photos.**

That single decoded line is the whole roadmap: a *program* was used, the photos
hold the data, and **`DUEDILIGENCE` is the steghide password** — right there in the
plan, no external lookup needed.

Reassembling raw packet bytes by hand is painful; let Wireshark do it:

**File → Export Objects → TFTP** lists every transferred file — Save All:

| Packet | Size | Filename |
| --- | --- | --- |
| 20 | 59 bytes | `plan` |
| 565 | 138 kB | `program.deb` |
| 3788 | 824 kB | `picture1.bmp` |
| 146679 | 36 MB | `picture2.bmp` |
| 152412 | 1466 kB | `picture3.bmp` |

<!-- Screenshots to add: drop the two PNGs into files/ and uncomment.
![TFTP packet list with the plan data packet selected](files/tftp-plan-packet.png)
![Wireshark Export Objects TFTP dialog listing the five files](files/tftp-export-objects.png)
-->

(`picture2.bmp` being 36 MB is a red herring — the flag is in the smallest of the
useful images, `picture3.bmp`.)

### 2. Find the tool (the hard part)

<details>
<summary>What didn't work here</summary>

**Tried, on the images:** eyeballing them (a 4-pixel black smudge in `picture1`
looked promising — it wasn't); `cat`/`strings`/`exiftool` + `grep`; and `zsteg`.
All empty.

**Why it failed:** `zsteg` detects *LSB* steganography. This challenge used
**steghide**, whose embedding is a different, password-protected algorithm that
`zsteg` can't see. Right tool category (steg), wrong specific tool — and nothing
in the images themselves announces which was used.

</details>

The `plan` said the info was in the pictures but not *how*. The `program.deb` is
the missing clue — inspect its metadata rather than just running `file` on it:

```bash
dpkg-deb --info program.deb
```

That shows the package is **steghide**. The `.deb` isn't a payload to install —
it's a hint naming the extraction tool.

### 3. Extract with steghide

<details>
<summary>What didn't work here</summary>

**Tried:** `steghide` on macOS, then `steghide extract -sf picture1.bmp` with no
password.

**Why it failed:** steghide was awkward to get running on the Mac (moved to a
Linux box to continue), and extraction needs the passphrase — a bare `extract`
prompts and rejects an empty one. Also, only `picture3.bmp` carries the flag;
`picture1`/`picture2` are decoys that fail extraction even with the right
password.

</details>

The passphrase is `DUEDILIGENCE`, straight from the ROT13-decoded plan in step 1.
Point steghide at the right image:

```bash
steghide extract -sf picture3.bmp -p DUEDILIGENCE
```

```
wrote extracted data to "...".
picoCTF{h1dd3n_1n_pLa1n_51GHT_...}
```

## Flag

```
picoCTF{h1dd3n_1n_pLa1n_51GHT_...}
```

_Truncated — graded course._

## Learn more

**steghide ≠ zsteg.** They're not interchangeable. `zsteg` reads
least-significant-bit patterns in PNG/BMP; `steghide` embeds password-protected
data (BMP/JPEG/WAV/AU) with a scheme `zsteg` won't detect. When `zsteg` finds
nothing on an image you're sure hides something, steghide is the next tool — and
it needs a passphrase, so the surrounding challenge always has to leak one.

**The `.deb` was a signpost, not a payload.** `file program.deb` just says "Debian
package" — useless. `dpkg-deb --info` prints the control metadata (package name,
description), which is where "this is steghide" lived. When an artifact seems
inert, read its metadata before dismissing it.

**Unencrypted protocols spill everything.** TFTP has no confidentiality, so every
byte of every file crossed the wire in plaintext — the entire attack surface here
is "reassemble what TFTP already handed you." Export Objects is the one-click way;
Follow → UDP Stream is the manual fallback.

- Wireshark → File → Export Objects → TFTP
- `dpkg-deb --info`, `steghide extract -sf <file> -p <pass>`

## Tools

Wireshark, `dpkg-deb`, `steghide`
