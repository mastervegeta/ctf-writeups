---
title: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped
event: portswiggeracademy
category: xss
points:
difficulty: practitioner
date: 2026-09-12
tags: [xss, reflected, javascript-context, backslash, string-breakout]
status: published
---

# Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab contains a reflected XSS vulnerability in the search query tracking
> functionality where angle brackets and double quotes are HTML-encoded and
> single quotes are escaped. To solve this lab, perform a cross-site scripting
> attack that breaks out of the JavaScript string and calls the `alert` function.

Input lands in a `'...'` JS string. `<`, `>`, `"` are HTML-encoded and `'` is
backslash-escaped — so closing the script tag (last lab's trick) is out, and a
raw `'` won't close the string. But the escaping itself is exploitable.

## TL;DR

The filter escapes `'` → `\'` but **doesn't escape the backslash**. So send `\'`:
the app escapes your quote, turning it into `\\'` — an escaped backslash followed
by a *live* quote that closes the string. Then `;alert(1)//` runs and comments
out the rest.

## Approach

### 1. Confirm the escaping

Reflected inside an inline script string:

```html
<script>
  ... = 'YOUR_INPUT';
</script>
```

Sending `'` comes back as `\'` (neutralised). `<`, `>`, `"` come back HTML-encoded.
So the only unfiltered character that matters is the **backslash**.

<details>
<summary>What didn't work here</summary>

**Tried:** `</script>`-style tag breakout, and a bare `';alert(1)//`.

**Why it failed:** angle brackets are HTML-encoded, so `</script>` never reaches
the parser as a tag. And a lone `'` is auto-escaped to `\'`, so it stays part of
the string instead of closing it.

</details>

### 2. Turn the escape against itself

Prefix the quote with your own backslash. The app then escapes the quote,
inserting a second backslash *before* yours:

- you send: `\'`
- app escapes the `'`: `\` + `\'` → `\\'`
- JS reads `\\` as one literal backslash, so the `'` is now unescaped and
  **closes the string**.

Full payload:

```
\';alert(1)//
```

reflects as:

```html
<script>
  ... = '\\';alert(1)//';
</script>
```

`\\` = literal backslash, `'` ends the string, `;alert(1)` executes, and `//`
comments out the trailing `';` so the script stays valid. `alert(1)` fires,
solving the lab.

## Flag

```
alert(1) fired from a broken-out JS string — lab solved
```

## Learn more

The general principle: **escaping is only safe if the escape character itself is
escaped.** Backslash-escaping `'` while leaving `\` untouched is self-defeating,
because an attacker supplies a backslash to consume the one the filter adds. The
correct rule is to escape `\` → `\\` *and* `'` → `\'` (or better, JSON/`<%= %>`-
style context-aware encoding).

This is the same class of bug as the previous JS-string lab, but here the tag
breakout is closed off (angle brackets encoded), forcing the pure string-context
solution instead.

- [PortSwigger — XSS in JavaScript contexts](https://portswigger.net/web-security/cross-site-scripting/contexts)

## Tools

browser
