---
title: Reflected XSS with AngularJS sandbox escape without strings
event: portswiggeracademy
category: xss
points:
difficulty: expert
date: 2026-09-13
tags: [xss, angularjs, sandbox-escape, csti, fromcharcode]
status: published
---

# Reflected XSS with AngularJS sandbox escape without strings

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab uses AngularJS in an unusual way where the `$eval` function is not
> available and you will be unable to use any strings in AngularJS. To solve the
> lab, perform a cross-site scripting attack that escapes the sandbox and executes
> the `alert` function without using the `$eval` function.

The input is reflected inside an AngularJS expression context, so it's evaluated
by Angular's expression parser (a client-side template injection). Two extra
constraints make it *expert*: no `$eval`, and **no string literals** allowed.

## TL;DR

Two moves. First neutralise the sandbox's character inspection by overwriting
`String.prototype.charAt` with `[].join`. Then, since you can't type strings,
build the code `x=alert(1)` out of `String.fromCharCode(...)` and feed it to the
`orderBy` filter, which compiles and evaluates it — firing `alert(1)`.

Working payload (the `search` parameter):

```
1&toString().constructor.prototype.charAt=[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
```

## Approach

### 1. Disable the sandbox's char-by-char checks

AngularJS's expression sandbox validates tokens by walking the string one
character at a time via `charAt`. Reassign it to `[].join`:

```js
toString().constructor.prototype.charAt = [].join;
```

`toString().constructor` is `String` (no string literal used), so this sets
`String.prototype.charAt = [].join`. With `charAt` returning the whole joined
value instead of single characters, the sandbox's per-character guard is defeated.

### 2. Build the payload without strings, via fromCharCode

Strings are banned, so spell the code with char codes.
`String.fromCharCode(120,61,97,108,101,114,116,40,49,41)` decodes to:

```
x=alert(1)
```

Again `toString().constructor.fromCharCode(...)` reaches `String.fromCharCode`
without a literal.

### 3. Get it evaluated with orderBy

The `orderBy` filter takes an expression argument, which Angular compiles and
evaluates. Feed it the assembled `x=alert(1)`:

```
[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
```

Angular evaluates the assignment `x=alert(1)` against the scope, calling
`alert(1)` and solving the lab. (Writing it as an assignment `x=...` makes it a
valid assignable expression for the parser.)

<details>
<summary>What didn't work — my own attempt</summary>

**Tried:** the classic Function-constructor route —

```js
toString().constructor.prototype.charAt=[].join;
(1).constructor.constructor(toString().constructor.fromCharCode(97,108,101,114,116,40,41))()
```

i.e. reach `Function` via `(1).constructor.constructor` and call
`Function("alert()")()`.

**Why it failed:** this version of the AngularJS sandbox specifically blocks
access to `Function`/`constructor.constructor` as a call target, so the escape
dies before `alert` runs. The `orderBy` route sidesteps it by having *Angular
itself* evaluate an ordinary assignment expression, rather than us invoking the
Function constructor. I couldn't derive the `orderBy` version unaided — it's the
known intended solution.

</details>

## Flag

```
alert(1) fired after the sandbox escape — lab solved
```

## Learn more

This is **client-side template injection**: user input lands where AngularJS
evaluates it as an expression, so the game is escaping Angular's expression
*sandbox* rather than breaking out of HTML. That sandbox was always a fragile idea
— the AngularJS team eventually [removed it entirely](https://sites.google.com/site/bughunteruniversity/nonvuln/angularjs-expression-sandbox-bypass)
in 1.6, conceding it was not a real security boundary.

Two reusable ideas: (1) `toString().constructor` is a string-literal-free handle
on `String`, giving you `fromCharCode` to synthesise any code as char codes; and
(2) overwriting a primitive the sandbox *depends on* (`charAt`) turns its own
validation against it. The real fix is not to evaluate untrusted input as an
Angular expression at all — modern Angular (2+) doesn't have this sink.

- [PortSwigger — AngularJS sandbox](https://portswigger.net/web-security/cross-site-scripting/client-side-template-injection)

## Tools

browser
