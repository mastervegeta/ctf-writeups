---
title: Reflected XSS in canonical link tag
event: portswiggeracademy
category: xss
points:
difficulty: practitioner
date: 2026-09-12
tags: [xss, reflected, canonical-link, accesskey, chrome]
status: published
---

# Reflected XSS in canonical link tag

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab reflects user input in a canonical link tag and escapes angle
> brackets. To solve the lab, perform a cross-site scripting attack on the home
> page that injects an attribute that calls the `alert` function.
>
> To assist with your exploit, you can assume that the simulated user will press
> the following key combinations: `ALT+SHIFT+X`, `CTRL+ALT+X`, `Alt+X`. The
> intended solution is only possible in Chrome.

Input is reflected into `<link rel="canonical" href="...">` and angle brackets
are escaped, so you can't open a new tag. You have to inject a new *attribute*
into the existing `<link>` element instead.

## TL;DR

Angle brackets are escaped but the single quote isn't, so `'` closes the `href`
value and lets you add attributes to the `<link>` tag. Add an `accesskey="X"` and
an `onclick="alert()"`; when the simulated victim presses the access-key combo
(`Alt+Shift+X` in Chrome), the element is "clicked" and `alert()` fires.

## Approach

### 1. See where input lands and what's filtered

The `search` value is reflected into the canonical link tag:

```html
<link rel="canonical" href="https://LAB/?search=YOUR_INPUT">
```

`<` and `>` are HTML-escaped, so a new tag is impossible. But the `'` delimiting
the `href` attribute is reflected raw — that's the way out of the value.

<details>
<summary>What didn't work here</summary>

**Tried:** the usual `"><script>` / `"><svg onload=...>` tag-injection payloads.

**Why it failed:** angle brackets are escaped, so you can never start a new
element. The only lever is adding attributes to the `<link>` tag that's already
there — a different class of injection.

</details>

### 2. Break out of href and add attributes

A single quote closes the `href` value; everything after it becomes new
attributes on the same `<link>` element. The winning payload:

```
/?search='accesskey='X'onclick='alert()
```

which reflects as:

```html
<link rel="canonical" href="https://LAB/?search='accesskey='X'onclick='alert()">
```

That gives the `<link>` an `accesskey="X"` and an `onclick="alert()"`.

### 3. Let the victim trigger the access key

An HTML **access key** lets a keypress activate an element — pressing the key
"clicks" it, firing `onclick`. In Chrome the combo is `Alt+Shift+X`, one of the
key presses the simulated user performs. When they do, `alert()` runs, solving
the lab.

## Flag

```
alert() fired via accesskey onclick — lab solved
```

## Learn more

This is the pattern for injections into an existing tag when you can't open a new
one: if the attribute *quote* is reflected unescaped, you can append arbitrary
attributes even with angle brackets locked down. `accesskey` is the key that
turns a normally passive element like `<link>` into something the user can
"activate", giving you an event to hang `onclick` on.

The Chrome-only note is about access-key modifiers: browsers differ, and the lab
fixes the combos to Chrome's `Alt+Shift+<key>`. The real fix is escaping *all*
reflected characters for the attribute-value context — quotes included — not just
angle brackets.

- [PortSwigger — accesskey XSS technique](https://portswigger.net/web-security/cross-site-scripting/contexts)
- [MDN — accesskey](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/accesskey)

## Tools

browser (Chrome)
