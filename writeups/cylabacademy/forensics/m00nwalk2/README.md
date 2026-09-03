---
title: m00nwalk2
event: cylabacademy
category: forensics
points:
difficulty: hard
date: 2026-09-03
tags: [sstv, steganography, steghide, audio, wav]
status: published
---

# m00nwalk2

> **Event:** cylabacademy · **Category:** forensics

## Challenge

The same moon transmission as [m00nwalk](../m00nwalk/) — one `message.wav` —
plus **three clue files**. Decoding the message alone doesn't give a flag this
time; the clues have to be decoded first, and they describe how to get at it.

## TL;DR

Every clue is itself an SSTV transmission. Decoded, they give a password
(`hidden_stegosaurus`), a nudge toward the audio, and a name — *Alan Eliasen,
the Future Boy*, whose site hosts an online **steghide** front-end. Run
`message.wav` through it with that password and the flag falls out. The wav is
the carrier, not the picture inside it.

## Approach

### 1. Decode the three clues as SSTV

Same routine as m00nwalk: each clue goes through the SSTV decoder
(<https://sstv-decoder.mathieurenaud.fr/>) and comes back as an image with text
on it.

| Clue | What the image said | What it meant |
| --- | --- | --- |
| 1 | `hidden_stegosaurus` | the passphrase |
| 2 | *"The quieter you are the more you HEAR"* | the carrier is the audio |
| 3 | *"Alan Eliasen, the future boy"* | the tool |

Clue 2 is the one that reads like filler. It's the Kali Linux tagline ("The
quieter you become, the more you are able to hear"), and — read straight —
it's telling you to keep working on the **sound file**, not on the image the
sound file decodes to. That distinction is the whole challenge.

<details>
<summary>What didn't work here</summary>

**Tried:** decoding `message.wav` as SSTV first and hunting for a flag in the
resulting picture, the way m00nwalk worked.

**Why it failed:** the SSTV image is a decoy in this challenge. The flag was
never drawn into the picture — it's embedded *in the WAV file itself*, which is
a different layer entirely. Decoding the SSTV throws away the container the flag
lives in.

</details>

### 2. Google clue 3

"Alan Eliasen the future boy" → <https://futureboy.us/stegano/>. His page is a
web front-end to **steghide**, and it accepts audio as well as images — exactly
the file type in hand.

That is the only place the tool name appears; nothing in `message.wav` announces
that it's a steghide carrier. Two of the three clues exist purely to name the
tool and its password.

### 3. Extract with the password

Upload `message.wav` to the decode form, give `hidden_stegosaurus` as the
passphrase, submit — the extracted text payload contains the flag.

The command-line equivalent, if you'd rather not use the web form:

```bash
steghide extract -sf message.wav -p hidden_stegosaurus
cat steganopayload*.txt
```

## Flag

```
picoCTF{the_answer_lies_hidden_in_...}
```

_Truncated — graded course._

## Learn more

**steghide works on WAV, not just images.** It embeds password-protected data in
JPEG, BMP, WAV and AU carriers, and it survives being a "valid" file of its type
— the wav still plays as a normal SSTV transmission with the payload inside it.
This is the same tool as
[Trivial Flag Transfer Protocol](../trivial-flag-transfer-protocol/); the reflex
worth building is that once a passphrase turns up in a forensics challenge,
steghide is the tool it probably belongs to, whatever the file extension is.

**Two layers, not one.** The trap here is finishing the first layer and assuming
you're done. SSTV-decoding the message gives you a picture, which *feels* like
the answer because that's how m00nwalk ended — but decoding is a lossy
interpretation of the audio, and the flag lives in bytes the interpretation
discards. When a challenge hands you extra clue files, that's the signal that
the obvious decode is only step one.

Worth noting for accuracy: futureboy.us is Alan Eliasen's site and it drives
steghide; SNOW, the *other* tool his name gets associated with in writeups, is
whitespace steganography by Matthew Kwan and is not what solves this one.

- <https://futureboy.us/stegano/>

## Tools

Browser SSTV decoder, `steghide` (via futureboy.us/stegano/)
