---
title: Ready Gladiator 2
event: cylabacademy
category: reverse-engineering
points:
difficulty: medium
date: 2026-09-03
tags: [corewars, redcode, assembly, imp-gate, addressing-modes]
status: published
---

# Ready Gladiator 2

> **Event:** cylabacademy · **Category:** reverse-engineering

## Challenge

> Can you make a CoreWars warrior that always wins?

The last step of the ladder. [RG1](../ready-gladiator-1/) needed **one** win in
100; RG2 needs **all 100**, against the same Imp, with no ties.

## TL;DR

Bombing an Imp only works by coincidence, so a bomber can't get to 100. The
counter is an **imp gate**: sit in one place and repeatedly decrement a cell in
the Imp's path, so that when the Imp walks onto it its `MOV 0, 1` has been
corrupted into `MOV 0, 0` and it stops laying its own track. One line does it:

```
JMP 0, <-3
```

## Approach

### 1. Why more bombing won't get there

Dwarf's 19–0–81 in RG1 is the ceiling for that whole family of ideas. An Imp
rewrites the cell in front of it one cycle before stepping into it, so any bomb
dropped ahead of it gets overwritten — the Imp is effectively immune to being
bombed, and Dwarf's 19 wins were the times the bomb happened to land on the exact
cell the Imp was about to execute. You cannot tune a stride to make a coincidence
happen 100 times out of 100. Killing an Imp reliably needs a different mechanism,
which is the thing to go and read about rather than guess at.

### 2. Build the gate

The instruction is doing two unrelated jobs at once:

```
;redcode
;name impcatcher
;assert 1
JMP 0, <-3
end
```

- **`JMP 0`** — jump to self. An infinite loop that never executes anything
  invalid, so this warrior cannot die. It also never moves, which is the point:
  it isn't hunting, it's a tripwire.
- **`<-3`** — the B operand, in *predecrement-indirect* mode. `JMP` ignores its B
  operand when choosing where to jump, so the operand's only effect is its side
  effect: **every cycle, decrement the B-field of the cell 3 before this one.**

The kill: an Imp at cell `X` executes `MOV 0, 1`, which writes a copy into `X+1`,
and then steps into `X+1` and runs it. If `X+1` is the gated cell, the gate's
decrement lands between those two events and turns the fresh copy from
`MOV 0, 1` into `MOV 0, 0`. The Imp then copies itself onto *itself* instead of
one cell forward — it never lays track into `X+2` — and steps into `X+2`, which
is untouched core, i.e. a `DAT`. It executes it and dies.

The Imp walks the whole circular core, so it reaches the gate in every round.

```bash
nc saturn.picoctf.net 58890 < impcatcher.red
```

```
Rounds: 100
Warrior 1 wins: 100    Warrior 2 wins: 0    Ties: 0
You did it!
```

## Flag

```
picoCTF{d3m0n_3xpung3r_...}
```

_Truncated — graded course._

## Learn more

**Imp gates are the standard answer to imps**, and the reason is structural rather
than clever-trick: an Imp's survival depends on writing a *correct copy of itself*
one cell ahead every single cycle. It defends the ground in front of it, so you
cannot attack it there — but it has no defence at all against its own copy being
edited after it's written. Decrementing the B-field is the smallest possible edit
that breaks the invariant, and `MOV 0, 0` is a legal instruction, so nothing
errors: the Imp simply stops advancing its own track and walks off the end of it.

**Predecrement-indirect (`<`) is the mode that makes it fit in one line.** In
ICWS'94 Redcode, `<x` means "go to the cell at offset `x`, subtract 1 from its
B-field, then use that value as the address". Real warriors use it for the
address arithmetic; here only the subtraction is wanted, and hanging it off a
`JMP` — an instruction that never reads its B operand — is how you get a pure
side effect for free. Distance `-3` is arbitrary: any offset that lands in core
the Imp will cross works, and gates are commonly written at `-2` or `-3`.

The three challenges in sequence are really one lesson about the same warrior:
[RG0](../ready-gladiator-0/) — an Imp can't be made to lose; RG1 — an Imp can't
reliably be bombed; RG2 — an Imp can be broken by editing what it wrote.

- [Core War / imp gates](https://en.wikipedia.org/wiki/Core_War)

## Tools

`nc`, `nano`, Redcode
