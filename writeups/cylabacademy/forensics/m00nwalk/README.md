---
title: m00nwalk
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-09-03
tags: [sstv, audio, ham-radio, gimp, steganography]
status: published
---

# m00nwalk

> **Event:** cylabacademy · **Category:** forensics

## Challenge

> Decode this message from the moon.

A single `.wav`. Playing it gives warbling beeps and sweeps — no speech, no
obvious carrier text. The challenge title and "from the moon" are the hint: this
is a radio transmission, and the payload is a *picture*, not a sound.

## TL;DR

The audio is **SSTV** (slow-scan television) — the format used to send still
images over voice-bandwidth radio, including from spacecraft. Feed the `.wav` to
an SSTV decoder and it draws the flag as an image. Mine came out sideways;
rotating it in GIMP made it readable.

## Approach

### 1. Identify the noise

The waveform is continuous tones, not modem-like bursts, with a repeating
per-line rhythm — about one "sweep" per fraction of a second, over ~1–2 minutes.
That periodicity is the tell: each sweep is one *scan line* of an image.

The challenge hints confirmed it: **SSTV**, the mode amateur radio operators
(and the ISS, on 145.800 MHz) use to send pictures over an audio channel.

<details>
<summary>What didn't work here</summary>

**Tried:** treating it as a normal forensics audio file — `strings`, spectrogram
inspection in Audacity looking for text drawn into the spectrum.

**Why it failed:** spectrogram-text is the *other* common audio-stego trick, so
it's a reasonable first swing, but SSTV doesn't hide anything in the spectrum —
the tones **are** the encoding. A spectrogram of SSTV shows the scan-line
sawtooth pattern, not letters. Once the sweeps are recognised as scan lines,
the answer is "decode it", not "look harder".

</details>

### 2. Decode the SSTV

No install needed — a browser decoder takes the file directly:

<https://sstv-decoder.mathieurenaud.fr/>

Upload the `.wav`, let it run to the end of the transmission, and the image
renders line by line. (Local equivalents: `qsstv` on Linux, or the `sstv` Python
decoder; both want the transmission played into them or handed a WAV.)

### 3. Rotate to read it

The decoded image came out rotated — the flag text ran vertically. Opened it in
GIMP and used **Image → Transform → Rotate 90°** until it read left-to-right.

The flag is printed in the image itself.

## Flag

```
picoCTF{...}
```

_Truncated — graded course._

## Learn more

**SSTV** encodes an image into audio by mapping each pixel's brightness to a
frequency (roughly 1500 Hz = black, 2300 Hz = white) and sending one scan line at
a time, separated by sync pulses — so a full frame takes tens of seconds to
minutes. That slowness is the whole point: it fits an image into the ~3 kHz of a
voice radio channel. There are several incompatible modes (Robot 36, Martin 1/2,
Scottie 1/2 …) differing in line timing, colour encoding and frame duration; a
decoder set to the wrong mode still produces an image, just skewed, mis-coloured
or garbled — which is a useful signal that you picked wrong, not that the file is
broken. Most decoders auto-detect from the VIS header at the start of the
transmission, which is why "just upload it" works here.

The moon framing is not decoration: SSTV is genuinely how still images have come
back from crewed missions and how the ISS runs its periodic
[ARISS SSTV events](https://www.ariss.org/) that anyone with a handheld radio can
receive.

- Decoder used: <https://sstv-decoder.mathieurenaud.fr/>

## Tools

Browser SSTV decoder, GIMP
