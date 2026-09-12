---
title: Reflected XSS into a JavaScript string with single quote and backslash escaped
event: portswiggeracademy
category: xss
points:
difficulty: practitioner
date: 2026-09-12
tags: [xss, reflected, javascript-context, script-breakout]
status: published
---

# Reflected XSS into a JavaScript string with single quote and backslash escaped

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab contains a reflected XSS vulnerability in the search query tracking
> functionality. The reflection occurs inside a JavaScript string with single
> quotes and backslashes escaped. To solve this lab, perform a cross-site
> scripting attack that breaks out of the JavaScript string and calls the `alert`
> function.

Input lands inside a `'...'` string in an inline `<script>`. Both `'` and `\` are
escaped, so you can't close the string the normal way. The trick is to leave the
string alone and attack the tag that contains it.

## TL;DR

You can't break the JS string — `'` and `\` are neutralised. But `<` and `>`
aren't, and the HTML parser sees `</script>` *before* the JS parser runs. Close
the existing script element and open your own: `</script><script>alert()</script>`.

## Approach

### 1. See the context

The search term is reflected inside a quoted string in an inline script:

```html
<script>
  ... = 'YOUR_INPUT';
</script>
```

Sending `'` or `\` shows them escaped (`\'`, `\\`), so string breakout is dead.

<details>
<summary>What didn't work here</summary>

**Tried:** classic JS-string breakouts — `'-alert()-'`, `\'; alert();//`, and
`"` / `</`-only variants.

**Why it failed:** the app escapes `'` and `\`, so the quote can't be closed and
the backslash can't be used to smuggle one. Staying *inside* the string context
is a dead end by design.

</details>

### 2. Break out of the script element, not the string

HTML parsing happens before JavaScript parsing. The parser ends the current
script at the first `</script>` it sees — regardless of JS quoting — so injecting
that sequence terminates the inline script early, and a fresh `<script>` after it
runs as new code:

```
/?search=</script><script>alert()</script>
```

Reflected:

```html
<script>
  ... = '</script><script>alert()</script>';
</script>
```

The browser closes the first script at `</script>`, then executes
`<script>alert()</script>`, firing `alert()` and solving the lab. Angle brackets
being unescaped is what makes this possible.

## Flag

```
alert() fired from an injected script element — lab solved
```

## Learn more

The lesson is about *layered parsers*: content inside `<script>` is first tokenised
by the HTML parser, which knows nothing about JavaScript string state. So even a
perfectly-escaped JS string is escapable if `</script>` reaches the page intact —
the HTML layer closes the element out from under the JS layer. Escaping `'` and
`\` addresses the wrong layer.

The correct defense escapes for *both* contexts: block/encode `<` and `>` (or the
`/` in `</script>`) so the script element can't be closed, in addition to the
string-level escaping already present.

- [PortSwigger — XSS in JavaScript contexts](https://portswigger.net/web-security/cross-site-scripting/contexts)

## Tools

browser
