---
title: Bytemancy 0
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [ascii, encoding, python, source-review]
status: published
---

# Bytemancy 0

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

A network service asks for "ASCII DECIMAL 101, 101, 101, side-by-side, no
space." Source is provided as `app.py`.

```bash
nc candy-mountain.picoctf.net 58955
```

## TL;DR

ASCII decimal 101 is the letter `e`. The answer is `eee`. The source confirms it:
the check is against `"\x65\x65\x65"`, which Python turns into `"eee"` at parse
time — `0x65` = 101.

## Approach

### 1. Read the source

```bash
wget <url>/app.py && cat app.py
```

```python
user_input = input('==> ')
if user_input == "\x65\x65\x65":
    print(open("./flag.txt", "r").read())
```

The comparison target is `"\x65\x65\x65"`. Those are hex escapes in a Python
string literal, so the interpreter has already converted them before the
comparison runs — `0x65` is 101 decimal, which is `e`. The string is literally
`"eee"`.

### 2. Send it

```
==> eee
picoCTF{pr1n74813_ch4r5_...}
```

<details>
<summary>What didn't work here</summary>

**Tried:** typing `\x65\x65\x65` literally.

```
==> \x65\x65\x65
That wasn't it. I got: \x65\x65\x65
```

**Why it failed:** `\x65` is an escape sequence *inside Python source*, resolved
when the file is parsed. Typed at a prompt it's just twelve characters —
backslash, `x`, `6`, `5`, repeated. The server even echoes back exactly what it
received (`I got: \x65\x65\x65`), showing the backslashes arrived verbatim. You
have to send the character the escape *represents*, not the escape.

</details>

## Flag

```
picoCTF{pr1n74813_ch4r5_...}
```

_Truncated — graded course._

## Learn more

Three names for the same byte, `0x65` = `101` = `e`:

- **hex** `\x65` — a byte written base-16, as in Python/C string literals
- **decimal** `101` — the same byte base-10, how the prompt phrased it
- **character** `e` — what that byte renders as in ASCII

The flag, `pr1n74813_ch4r5` ("printable chars"), is the point: byte 101 happens
to be a printable character, so you can just type it. The dead end is the whole
lesson — a `\xNN` escape only means a byte inside a language that parses it. Sent
as keystrokes it's plain text, which is why the server echoed the backslashes
straight back.

`python3 -c "print(chr(101))"` or `man ascii` both confirm the mapping in a
second.

## Tools

`nc`, `wget`
