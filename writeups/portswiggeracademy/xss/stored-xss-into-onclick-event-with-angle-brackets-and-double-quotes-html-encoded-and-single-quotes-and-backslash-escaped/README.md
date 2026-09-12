---
title: Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped
event: portswiggeracademy
category: xss
points:
difficulty: practitioner
date: 2026-09-12
tags: [xss, stored, onclick, html-entities, javascript-context]
status: published
---

# Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab contains a stored XSS vulnerability in the comment functionality. To
> solve this lab, submit a comment that calls the `alert` function when the
> comment author name is clicked.

The commenter's **website** URL is reflected into the author link's `onclick`, as
the argument to `tracker.track('...')` — a single-quoted JS string, itself inside
a double-quoted HTML attribute. Angle brackets and double quotes are HTML-encoded;
single quotes and backslashes are escaped. So every literal breakout character is
neutralised.

## TL;DR

The escaper handles literal `'` and `\`, but it never encodes `&`. So feed it the
**HTML entity** `&#x27;` instead of a real quote: the escaper leaves it alone, and
the browser HTML-decodes the `onclick` attribute to a real `'` *before* the JS
parser runs — breaking the string. Then close the `track(` call, call `alert()`,
and comment out the tail:

```
&#x27;);alert()//
```

## Approach

### 1. Locate the sink

The website URL lands in the author `<a>` twice — in `href` and in `onclick`:

```html
<a id="author"
   href="https://LAB/post?postId=2WEBSITE"
   onclick="var tracker={track(){}};tracker.track('https://LAB/post?postId=2WEBSITE');">
```

The `onclick` string is the target: break out of `'...'` and append code.

<details>
<summary>What didn't work here — the whole filter, one character at a time</summary>

**Tried:** `<img src=1 onerror='alert()'>` as the name/website.
**Why it failed:** `<` and `>` are HTML-encoded (`&lt;`/`&gt;`), so it renders as
inert text — no new tag.

**Tried:** raw `'`, `\`, `"`, `<`, `>` to probe the filter (`\'ja"`, etc.).
**Why it failed:** `"`,`<`,`>` come back HTML-encoded; `'` and `\` come back
escaped. No literal character survives into the JS string as a delimiter.

**Tried:** `&#x27;;alert()//` and `&#x27;+alert()` — a decoded quote, then straight
into the payload.
**Why it failed:** the quote *does* close the string, but `tracker.track('...'`
still has an open paren. `tracker.track('...';alert()` is a syntax error, so the
handler never runs. You have to close the `track(` call too.

**Tried:** fully entity-encoding the payload (`&#x3b;&#x61;&#x6c;...` for
`;alert()`).
**Why it failed:** unnecessary — only the quote needs to be an entity to survive
the escaper; the rest of the JS can be literal.

</details>

### 2. Smuggle the quote as an HTML entity

The escaper only looks for a literal `'` (which it backslash-escapes). Give it
`&#x27;` — the hex entity for a single quote. There's no literal quote for it to
escape, and `&` is passed through unencoded, so `&#x27;` reaches the DOM intact.
When the browser parses the `onclick` attribute, it HTML-decodes `&#x27;` to a
real `'`, which the JS engine then sees as a string terminator.

### 3. Close the call, run alert, comment the rest

After the quote closes the string, close `track(`'s parenthesis with `)`, run
`;alert()`, and `//` out the trailing `');` the template appends. Winning
**website** value:

```
https://YOUR-LAB-ID.web-security-academy.net/post?postId=2&wtf=&#x27;);alert()//
```

(the URL just has to satisfy the `(http:|https:).+` field pattern; `&wtf=` is
filler). It reflects as:

```html
onclick="...tracker.track('https://LAB/post?postId=2&wtf=&#x27;);alert()//');"
```

which the browser reads as `tracker.track('...&wtf=')` then `;alert()` then a
comment. Clicking the author name fires `alert()`, solving the lab. The full
solved page is in [files/](files/solved-page.html).

## Flag

```
alert() fired on clicking the author name — lab solved
```

## Learn more

The bug is an **ordering / layering** mistake. The value passes through a JS-string
escaper (handles `'`, `\`) and an HTML encoder (handles `<`, `>`, `"`) — but
neither encodes `&`, and the HTML layer is *decoded by the browser after* the
escaping was applied. So an HTML entity for a quote sails past the JS escaper as
harmless text and is turned back into a live quote at parse time. Escaping is only
sound if every layer that will be decoded downstream is accounted for — here, `&`
had to be encoded too (`&amp;`).

The `)`-then-`//` shape is the reusable part for any injection into a *function-call
argument*: closing the string isn't enough, you also have to balance the call's
parenthesis before your statement, then comment away the template's leftovers.

- [PortSwigger — XSS in JavaScript contexts](https://portswigger.net/web-security/cross-site-scripting/contexts)

## Tools

browser
