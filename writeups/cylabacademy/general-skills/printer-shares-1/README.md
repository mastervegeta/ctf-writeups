---
title: Printer Shares 1
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [smb, smbclient, samba, enumeration, guest-access]
status: published
---

# Printer Shares 1

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

An SMB service on `mysterious-sea.picoctf.net`, reachable on a non-standard
port. Find the flag.

## TL;DR

SMB is on port **61829**, not 445. `smbclient -L` lists a guest-readable share
called `shares`; connect to it with `-N`, then `get flag.txt` and read it
locally. `smbclient` is an FTP-style client, not a shell — you can't `cat`
anything inside it.

## Approach

### 1. Confirm the service and rule out the standard ports

```bash
nc -vz mysterious-sea.picoctf.net 61829   # succeeded
nc -vz mysterious-sea.picoctf.net 445     # Connection refused
nc -vz mysterious-sea.picoctf.net 139     # Connection refused
```

Only the given port is open, so every `smbclient` call needs `-p 61829`.

### 2. Get the syntax right

```bash
smbclient mysterious-sea.picoctf.net 61829
```

```
mysterious-sea.picoctf.net: Not enough '\' characters in service
```

<details>
<summary>What didn't work here</summary>

**Tried:** passing the port as a second positional argument, then adding `-p`
but still giving a bare hostname.

**Why it failed:** two separate mistakes with the same error message. The usage
line reads `[OPTIONS] service <password>` — the second positional is the
**password**, not the port. And *service* means a UNC path, `//host/share`, so a
bare hostname has no share component to parse. Hence "not enough `\`
characters".

Confusingly, `-L` worked with a bare hostname throughout, because `-L` takes
`--list=HOST` — a host, not a service. That inconsistency is what made the real
problem hard to see.

</details>

### 3. List the shares

```bash
smbclient -L //mysterious-sea.picoctf.net -p 61829 -N
```

```
        Sharename       Type      Comment
        ---------       ----      -------
        shares          Disk      Public Share With Guests
        IPC$            IPC       IPC Service (Samba 4.19.5-Ubuntu)
```

`-N` suppresses the password prompt. The comment — *Public Share With Guests* —
says outright that anonymous access is expected.

### 4. Connect and look around

```bash
smbclient //mysterious-sea.picoctf.net/shares -p 61829 -N
```

```
smb: \> ls
  dummy.txt                           N     1142  Wed Feb  4 21:22:17 2026
  flag.txt                            N       37  Fri Mar  6 20:25:43 2026
```

<details>
<summary>What didn't work here</summary>

**Tried:** `cat flag.txt` at the `smb: \>` prompt.

```
cat: command not found
```

Then `open flag.txt`, which returns `fnum 1` and prints nothing; `echo flag.txt`,
which wants `<num> <data>`; and `rd flag.txt`, which returns
`NT_STATUS_NOT_A_DIRECTORY`.

**Why it failed:** the `smb: \>` prompt looks like a shell but isn't one. It's an
FTP-style client over SMB, and `help` lists its entire vocabulary — there is no
command that prints a file. You transfer the file down and read it on your own
machine.

</details>

### 5. Download and read it

```
smb: \> get flag.txt
getting file \flag.txt of size 37 as flag.txt (18.1 KiloBytes/sec)
smb: \> exit
```

```bash
cat flag.txt
```

## Flag

```
picoCTF{5mb_pr1nter_5h4re5_...}
```

_Truncated — graded course._

## Learn more

Three things generalise beyond this box. **SMB isn't always on 445** — CTFs and
real networks both remap it, so confirm with `nc -vz` before assuming the
protocol is absent. **`-N` is the null-session flag**, and getting a share
listing without credentials is itself the finding; a share commented "Public"
that answers an anonymous `-L` is misconfigured by definition. And **`smbclient`
sessions are transfer sessions** — `ls`, `cd`, `get`, `put`, `mget`, nothing that
reads a file in place.

The wasted time here came from one error string, `Not enough '\' characters in
service`, covering two unrelated mistakes. When the same message survives a fix,
the fix addressed a different bug than the one being reported.

- [smbclient(1)](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html)

## Tools

`nc`, `smbclient`
