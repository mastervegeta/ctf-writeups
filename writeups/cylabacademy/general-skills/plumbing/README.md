---
title: Plumbing
event: cylabacademy
category: general-skills
points:
difficulty: medium
date: 2026-08-19
tags: [netcat, grep, pipes, redirection]
status: published
---

# Plumbing

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

Connect with netcat. The service floods you with thousands of "this is not a
flag" lines, with the real flag buried somewhere in the stream.

```bash
nc fickle-tempest.picoctf.net 57974
```

## TL;DR

The output is too much to read by eye. Filter it: pipe netcat straight into
`grep picoCTF`, or redirect to a file and grep that.

## Approach

### 1. See the firehose

```bash
nc fickle-tempest.picoctf.net 57974
```

```
I don't think this is a flag either
Not a flag either
This is definitely not a flag
...
```

Endless decoy lines, scrolling faster than you can read. Watching for the flag to
fly past is hopeless — it needs filtering.

### 2. Filter for the flag

Redirect to a file, then grep it:

```bash
nc fickle-tempest.picoctf.net 57974 > output.txt   # ^C after a moment
grep picoCTF output.txt
```

```
picoCTF{digital_plumb3r_...}
```

## Flag

```
picoCTF{digital_plumb3r_...}
```

_Truncated — graded course._

## Learn more

The name ("Plumbing") and flag ("digital_plumb3r") are about pipes. The temp file
works, but the cleaner version pipes netcat's output directly into grep — no file,
and it prints the moment the flag appears:

```bash
nc fickle-tempest.picoctf.net 57974 | grep picoCTF
```

`grep --line-buffered picoCTF` forces a match to print immediately rather than
waiting for grep's output buffer to fill — worth it on a stream that never ends,
so you're not left wondering whether it hung. Either way the idea is the same:
when a program produces more output than you can read, don't read it — pipe it
through a filter that keeps only what you want.

`grep -a` is also handy if a stream contains binary bytes, which otherwise make
grep report "binary file matches" instead of printing the line.

## Tools

`nc`, `grep`
