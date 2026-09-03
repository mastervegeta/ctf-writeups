---
title: Ready Gladiator 1
event: cylabacademy
category: reverse-engineering
points:
difficulty: medium
date: 2026-09-03
tags: [corewars, redcode, assembly, dwarf, bomber]
status: published
---

# Ready Gladiator 1

> **Event:** cylabacademy · **Category:** reverse-engineering

## Challenge

> Can you make a CoreWars warrior that wins?

Same service, inverted goal from [Ready Gladiator 0](../ready-gladiator-0/): the
opponent is still an Imp, and this time warrior 1 must **win at least one round**
out of 100.

## TL;DR

Losing needs one instruction; winning needs an actual warrior. **Dwarf** — the
classic four-line bomber that walks `DAT` bombs around core every 4 cells — takes
19 of 100 rounds against the Imp. One win is the bar, so 19 clears it.

## Approach

### 1. Confirm the Imp can't win this one for you

```bash
nc saturn.picoctf.net 55760 < imp.red
```

```
Rounds: 100
Warrior 1 wins: 0    Warrior 2 wins: 0    Ties: 100
Try again. Your warrior (warrior 1) must win at least once.
```

Unchanged from RG0 — Imp vs Imp is 100 ties. And the RG0 trick inverts too: an
empty warrior loses 100–0, which is the wrong end of the scoreboard now.

<details>
<summary>What didn't work here</summary>

**Tried:** `mov 0 -1` — an Imp walking backwards.

**Why it failed:** two separate problems. The syntax is wrong (no comma), so the
assembler rejected it outright:

```
Error in line 4: 'mov 0 -1'
        Incomplete operand at instruction 'MOV'
A subprocess got an error
```

Redcode operands are comma-separated; `mov 0, -1` assembles. But it wouldn't have
helped either — a reversed Imp is still an Imp, and still just ties.

**Also tried:** piping a file whose last line isn't `end`, then typing `end` at
the prompt. The submission never closed cleanly and the run had to be killed with
`^C`. Put `end` **inside** the `.red` file and the redirect works in one shot.

</details>

### 2. Assemble the Dwarf

Dwarf is the standard first bomber: it keeps a `DAT` at the bottom, adds 4 to that
`DAT`'s B-field each pass, and copies it to the address the B-field now points at.
Net effect: it stands still and drops a bomb every 4th cell around the core,
looping forever.

```
;redcode
;name warrior
;assert 1
ADD #4, 3
MOV 2, @2
JMP -2
DAT #0, #0
end
```

Line by line: `ADD #4, 3` adds the literal 4 to the B-field of the instruction 3
cells ahead (the `DAT`); `MOV 2, @2` copies that `DAT` to the address held
*indirectly* in its own B-field — the `@` is what turns the counter into a moving
target; `JMP -2` loops back to the `ADD`.

```bash
nc saturn.picoctf.net 55760 < warrior.red
```

```
Rounds: 100
Warrior 1 wins: 19    Warrior 2 wins: 0    Ties: 81
You did it!
```

19 wins, 81 ties, and — worth noticing — **zero losses**. The Imp never kills
Dwarf; Dwarf just usually fails to kill the Imp before the cycle limit.

## Flag

```
picoCTF{1mp_1n_7h3_cr055h41r5_...}
```

_Truncated — graded course._

## Learn more

**Why only 19%.** An Imp (`MOV 0, 1`) copies itself into the cell ahead and then
steps into that copy, so it repairs its own path one cycle before walking it —
bombing the ground in front of an Imp is useless, the Imp overwrites the bomb.
The only bomb that kills is one that lands on the exact cell the Imp is about to
execute in that same cycle, before it executes it. Dwarf bombs one cell every few
cycles at a fixed stride, so whether that coincidence happens depends on where the
two warriors were loaded relative to each other — hence a scoreline of "wins
sometimes, ties the rest", and never a loss.

**Addressing modes are the whole language.** Redcode has no registers; what
distinguishes instructions is how each operand is interpreted. `#4` is immediate
(the literal 4), a bare `3` is a relative address (3 cells forward), and `@2` is
indirect (go to the cell 2 ahead, read *its* B-field, use that as the address).
Dwarf is four instructions long and needs three of those modes — `MOV 2, @2` with
a plain `2` instead of `@2` would copy the bomb to a fixed spot forever.

Getting from "ties every time" to "wins every time" is [Ready Gladiator
2](../ready-gladiator-2/), which needs a different mechanism entirely.

- [Dwarf and other classic warriors](https://en.wikipedia.org/wiki/Core_War)

## Tools

`nc`, `nano`, Redcode
