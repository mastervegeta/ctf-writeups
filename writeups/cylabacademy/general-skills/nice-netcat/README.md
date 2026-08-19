---
title: Nice Netcat
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [netcat, ascii, decimal, python]
status: published
---

# Nice Netcat

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

Connect with netcat and the service streams a list of numbers. They're ASCII
decimal codes — convert them to characters to get the flag.

```bash
nc wily-courier.picoctf.net 59928
```

## TL;DR

The numbers (`112 105 99 111 67 84 70 123 …`) are decimal ASCII. `112` = `p`,
`105` = `i`, `99` = `c`… = `pico…`. Convert the whole list to text.

## Approach

### 1. Capture the output

```bash
nc wily-courier.picoctf.net 59928 > numbers.txt
```

```
112
105
99
111
67
84
70
123
...
10
```

The service doesn't close on its own, so `^C` once the numbers stop. The first
few — `112 105 99 111 67 84 70 123` — decode to `picoCTF{`, which confirms
they're decimal ASCII and that the flag starts here. The trailing `10` is a
newline (`\n`).

### 2. Convert to text

```bash
python3 -c "print(''.join(chr(int(n)) for n in open('numbers.txt')))"
```

```
picoCTF{g00d_k1tty!_n1c3_k1tty!_...}
```

## Flag

```
picoCTF{g00d_k1tty!_n1c3_k1tty!_...}
```

_Truncated — graded course._

## Learn more

I originally pasted the numbers into an online decimal-to-ASCII converter, which
works but hands the flag to a third-party site and doesn't scale past copy-paste.
The conversion is one line locally:

```bash
python3 -c "print(''.join(chr(int(n)) for n in open('numbers.txt')))"
```

Or capture and convert without a temp file:

```bash
nc wily-courier.picoctf.net 59928 | python3 -c "import sys; print(''.join(chr(int(n)) for n in sys.stdin))"
```

The whole point of the challenge is redirecting netcat's output somewhere you can
process it (`> numbers.txt`) rather than just reading it off the screen — once
it's in a file or a pipe, decoding is trivial. Worth having a local
decimal→ASCII one-liner in muscle memory; you'll hit this format constantly.

## Tools

`nc`, `python3`
