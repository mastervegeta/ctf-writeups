---
title: Wireshark doo dooo do doo...
event: cylabacademy
category: forensics
points:
difficulty: medium
date: 2026-08-19
tags: [wireshark, pcap, protocol-hierarchy, rot13, http]
status: published
---

# Wireshark doo dooo do doo...

> **Event:** cylabacademy · **Category:** forensics

## Challenge

A packet capture of ~970 packets. The flag is in there, ROT13-encoded.

## TL;DR

**Statistics → Protocol Hierarchy** shows two `Line-based text data` packets among
the 970. One holds `Gur synt vf cvpbPGS{...}` — ROT13. Decode it to get the flag.

## Approach

### 1. Narrow 970 packets down

Scrolling 970 packets by hand is hopeless. Instead:

**Statistics → Protocol Hierarchy** — a per-protocol breakdown of the whole
capture. Two packets sit under **Line-based text data (text/html / text/plain)**,
which is where actual page content lives, not headers. Those two are the only
ones carrying human-readable payload worth reading.

Right-click → Apply as Filter, or just open them. One (frame 827) contains:

```
Gur synt vf cvpbPGS{c33xno00_1_f33_h_qrnqorrs}
```

### 2. Recognise and decode ROT13

`cvpbPGS` where a flag should read `picoCTF` is the giveaway — same letter
distances, shifted by 13. So is `Gur synt vf` ("The flag is"). Decode:

```bash
echo 'Gur synt vf cvpbPGS{c33xno00_1_f33_h_qrnqorrs}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

```
The flag is picoCTF{p33kab00_1_s33_u_deadbeef}
```

## Flag

```
picoCTF{p33kab00_1_s33_u_...}
```

_Truncated — graded course._

## Learn more

**Protocol Hierarchy is the move for a big capture.** Rather than reading packets,
ask "what protocols are even in here, and which carry payload?" Line-based text
data, HTTP object exports (File → Export Objects → HTTP), and Follow → TCP Stream
are the three fastest ways to surface content from noise. Two text packets out of
970 is exactly the needle-in-haystack this view is built for.

**ROT13 by eye.** You don't need to decode to recognise it — `cvpbPGS` and
`picoCTF` have identical letter-to-letter gaps, and CTFs use ROT13 far more than
any other rotation, so it's the first thing to try on scrambled-but-pronounceable
text. `tr 'A-Za-z' 'N-ZA-Mn-za-m'` does it locally in one line; no need to paste
a flag into a web decoder. (The uppercase range must lead the replacement set —
see the example writeup for why `tr` ordering bites.)

- Wireshark → Statistics → Protocol Hierarchy

## Tools

Wireshark, `tr`
