---
title: Ready Gladiator 0
event: cylabacademy
category: reverse-engineering
points:
difficulty: medium
date: 2026-09-03
tags: [corewars, redcode, assembly, mars, pmars]
status: published
---

# Ready Gladiator 0

> **Event:** cylabacademy · **Category:** reverse-engineering

## Challenge

> Can you make a CoreWars warrior that always loses, no ties?

You get `imp.red` — the classic one-line Core War warrior — and a service that
pits your warrior against a fixed opponent for 100 rounds. Submit over `nc`; the
flag comes when **warrior 1 loses all 100 rounds** with zero ties.

## TL;DR

The opponent is an Imp, and Imp vs Imp is a permanent stalemate — 100 ties, every
time. In Redcode the one instruction that kills the process executing it is
**`DAT`**, so a warrior whose entire body is `dat 0, 0` dies on its first cycle,
every round.

## Approach

### 1. Submit the given Imp and see the stalemate

```bash
nc saturn.picoctf.net 58465 < imp.red
```

```
;redcode
;name Imp Ex
;assert 1
mov 0, 1
end

Rounds: 100
Warrior 1 wins: 0    Warrior 2 wins: 0    Ties: 100
Try again. Your warrior (warrior 1) must lose all rounds, no ties.
```

`mov 0, 1` copies the instruction at the current cell into the next one, then the
program counter steps into the copy — an Imp walks forward through core forever
and never dies. The opponent is doing exactly the same thing. Neither dies, the
cycle limit runs out, and every round is a tie. Ties are explicitly disallowed,
so "survive worse" is not the goal — **dying is**.

### 2. The accidental solve: submit nothing

Fumbling the paste got the flag by accident. Pasting the source as one squashed
line, or commenting out the only instruction, both produce a warrior with an
empty body:

```
;redcode
;name BIGBOSS
;assert 1
;mov 0, 1        <- note the leading ';' — this is a comment, not code
end
```

```
Warning:
        No instructions
Number of warnings: 1

Rounds: 100
Warrior 1 wins: 0    Warrior 2 wins: 100    Ties: 0
You did it!
```

A warrior with no instructions has nothing to execute, so it is dead on arrival
and loses all 100. It works, but it wins by not being a warrior at all — the
checker only counts losses, and never checks that you lost *by playing*.

### 3. Lose on purpose instead

`DAT` is the halt instruction: a process that executes a `DAT` is removed, and a
warrior with no processes left has lost the round. So the shortest legitimate
loser is a single `DAT` as the entry point — the warrior starts, executes it, and
dies immediately.

```
;redcode
;name loser
;assert 1
dat 0, 0
end
```

```
Rounds: 100
Warrior 1 wins: 0    Warrior 2 wins: 100    Ties: 0
You did it!
```

<details>
<summary>What didn't work here</summary>

**Tried:** renaming the Imp and resubmitting it (`;name BIGBOSS`, same
`mov 0, 1`).

**Why it failed:** the outcome is decided by the code, not the metadata — Imp vs
Imp is still 100 ties. Worth stating because it's the check that confirms the
`;name` / `;assert` header lines are inert: only the instructions after them
matter.

</details>

## Flag

```
picoCTF{h3r0_t0_z3r0_4m1r1gh7_...}
```

_Truncated — graded course._

## Learn more

**Core War** (A. K. Dewdney, *Scientific American*, May 1984) is a game where two
programs written in the assembly language **Redcode** are loaded at random
positions into a shared circular memory — the *core* — and executed in turn by a
simulator called MARS. There are no registers and no I/O: an instruction's
operands are memory offsets relative to itself, and the only way to win is to make
every one of the opponent's processes execute an invalid instruction. A round that
hits the cycle limit with both warriors alive is a tie.

`DAT` is that invalid instruction. It's nominally "data, not code" — a cell you
use to store a value or as a bomb to copy onto the enemy — and executing one kills
the process, which is exactly what most warriors are trying to trick each other
into doing. Making it your own first instruction inverts the usual goal in one
line.

The **Imp** is Dewdney's own `MOV 0, 1`: it can't be killed by ordinary bombing,
because it rewrites the cell ahead of itself one step before stepping into it —
which is why two Imps stalemate, and why beating one needs a different idea
entirely (see [Ready Gladiator 1](../ready-gladiator-1/) and
[2](../ready-gladiator-2/)).

- [Core War on Wikipedia](https://en.wikipedia.org/wiki/Core_War)

## Tools

`nc`, Redcode
