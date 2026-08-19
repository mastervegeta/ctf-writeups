---
title: SUDO MAKE ME A SANDWICH
event: cylabacademy
category: general-skills
points:
difficulty: easy
date: 2026-08-19
tags: [privilege-escalation, sudo, emacs, gtfobins]
status: published
---

# SUDO MAKE ME A SANDWICH

> **Event:** cylabacademy · **Category:** general-skills

## Challenge

A root-owned `flag.txt` you can't read as `ctf-player`. The name is [xkcd
#149](https://xkcd.com/149/) — the trick is finding what you're allowed to run
as root.

## TL;DR

`sudo -l` shows `ctf-player` may run `/bin/emacs` as root with no password. Emacs
can open any file, so run it under sudo and read the flag as root:
`sudo /bin/emacs flag.txt`.

## Approach

### 1. Try the obvious reads

```bash
cat flag.txt                # Permission denied
sudo cat flag.txt           # not permitted
chmod +r flag.txt           # not permitted (you don't own it)
```

<details>
<summary>What didn't work here</summary>

**Tried:** `sudo cat`, `sudo chmod +r`, other root commands.

**Why it failed:** sudo isn't all-or-nothing here — this user is allowed to run
*specific* programs as root, and `cat`/`chmod` aren't among them. `chmod +r`
without sudo fails too, because you can't change the mode of a file you don't
own. The question isn't "how do I force root" but "what am I *already* allowed to
run as root", which is exactly what `sudo -l` answers.

</details>

### 2. Check the sudo rights

```bash
sudo -l
```

```
User ctf-player may run the following commands on challenge:
    (ALL) NOPASSWD: /bin/emacs
```

Emacs, as root, no password. Emacs is a text editor — it can open any file — so
that single entry is enough to read a root-owned file.

### 3. Read the flag as root

```bash
sudo /bin/emacs flag.txt
```

Emacs opens `flag.txt` with root's privileges and the flag is on screen. `C-x
C-c` quits.

## Flag

```
picoCTF{...}
```

_Not captured in my notes; redacted anyway — graded course._

## Learn more

The real lesson: **any program that can open a file or spawn a shell becomes a
privilege-escalation primitive the moment it's in your sudo rights.** Emacs,
`vim`, `less`, `find`, `awk`, even `tar` with the right flags — a "harmless"
entry in `sudoers` is only harmless if the program can't be made to do anything
else, and almost all of them can.

[GTFOBins](https://gtfobins.org/gtfobins/emacs/) catalogues these. For emacs it
lists two moves:

```bash
sudo /bin/emacs flag.txt                              # read one file as root
sudo /bin/emacs -Q -nw --eval '(term "/bin/sh")'      # full root shell
```

The second is the general one — a root shell reads the flag and everything else
besides. Whenever `sudo -l` names a program, GTFOBins is the first place to
check what that program can be turned into.

- [GTFOBins — emacs](https://gtfobins.org/gtfobins/emacs/)
- [xkcd #149](https://xkcd.com/149/) — the joke the title is quoting

## Tools

`sudo`, `emacs`
