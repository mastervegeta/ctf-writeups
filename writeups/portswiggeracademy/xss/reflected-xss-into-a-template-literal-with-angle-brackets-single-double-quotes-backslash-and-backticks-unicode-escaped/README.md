---
title: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped
event: portswiggeracademy
category: xss
points:
difficulty: practitioner
date: 2026-09-12
tags: [xss, reflected, template-literal, javascript-context]
status: published
---

# Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab contains a reflected XSS vulnerability in the search blog
> functionality. The reflection occurs inside a template string with angle
> brackets, single, and double quotes HTML-encoded, and backticks escaped. To
> solve this lab, perform a cross-site scripting attack that calls the `alert`
> function inside the template string.

The search term is reflected inside a JavaScript **template literal** — a
`` `...` ``-quoted string. Angle brackets, both quote types, the backslash and
the backtick are all escaped, so you can't close the string or open a tag.

## TL;DR

Template literals interpolate expressions with `${ ... }`, and that syntax needs
none of the blocked characters. You don't have to break out of the string at all
— just inject `${alert()}` and it runs as an expression *inside* the string:

```
${alert()}
```

## Approach

### 1. See the context

The value lands inside backticks in an inline script:

```html
<script>
  ... = `YOUR_INPUT`;
</script>
```

Everything you'd normally use to escape a JS string is neutralised: `` ` ``, `'`,
`"`, `\`, `<`, `>` are all Unicode/HTML-escaped.

<details>
<summary>What didn't work here</summary>

**Tried:** closing the string with a backtick (`` `-alert()-` ``) and the
tag-breakout `</script>`.

**Why it failed:** the backtick is escaped, so the template literal can't be
closed; angle brackets are encoded, so no new tag. Any technique that depends on
*terminating* the string is dead here.

</details>

### 2. Interpolate instead of escape

A template literal evaluates any `${expression}` embedded in it — the same idea
as a Python f-string. `$`, `{`, `}` and the letters of `alert()` are all
untouched by the filter, so the payload lives happily inside the backticks and
still executes:

```
/?search=${alert()}
```

reflects as:

```html
<script>
  ... = `${alert()}`;
</script>
```

The engine evaluates `alert()` while building the string, firing the alert and
solving the lab. No breakout required.

## Flag

```
alert() evaluated inside the template literal — lab solved
```

## Learn more

The lesson is that the dangerous character set is **context-specific**. Filters
built for ordinary quoted strings escape quotes, backslashes and backticks — and
miss that a template literal has a second, first-class way to run code:
`${ ... }` interpolation, which uses only `$`, `{`, `}`. Blocking string
terminators does nothing about it.

Correct handling means escaping for the *template-literal* context specifically —
neutralise `${` (e.g. encode `$` or `{`) as well as the backtick — or, better,
don't drop untrusted input into executable JS at all; pass it as data (JSON,
`textContent`) instead.

- [MDN — Template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals)
- [PortSwigger — XSS in JavaScript contexts](https://portswigger.net/web-security/cross-site-scripting/contexts)

## Tools

browser
