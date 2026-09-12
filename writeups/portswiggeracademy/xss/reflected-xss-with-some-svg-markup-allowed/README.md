---
title: Reflected XSS with some SVG markup allowed
event: portswiggeracademy
category: xss
points:
difficulty: practitioner
date: 2026-09-12
tags: [xss, svg, reflected, waf, intruder, burp]
status: published
---

# Reflected XSS with some SVG markup allowed

> **Event:** portswiggeracademy · **Category:** xss

## Challenge

> This lab has a simple reflected XSS vulnerability. The site is blocking common
> tags but misses some SVG tags and events. To solve the lab, perform a
> cross-site scripting attack that calls the `alert()` function.

The `search` parameter reflects into HTML. A filter blocks the usual vectors, but
its coverage of the SVG namespace is incomplete — the task is to find the SVG
tag/event pair it forgot.

## TL;DR

`<svg>` is allowed, but the common SVG event carriers (`<svg onload>`,
`<animate>`, `<set>`) are blocked. `<animateTransform>` slips through, and its
`onbegin` event fires as soon as the animation starts — no interaction needed.

## Approach

### 1. Confirm svg is allowed but the obvious events aren't

`<svg onload=alert()>` and `<script>` are blocked, but a bare `<svg>` reflects
intact. So the filter is a tag/attribute blocklist with gaps in the SVG
namespace — worth enumerating rather than guessing.

<details>
<summary>What didn't work here</summary>

**Tried:** `<svg onload=alert()>` and `<image>`/`<animate>` handlers.

**Why it failed:** those tag/event names are on the blocklist. A tag being
allowed (`<svg>`) says nothing about the events allowed on it or its children —
the two are filtered separately.

</details>

### 2. Brute-force allowed tags, then allowed events

Use Burp Intruder with PortSwigger's [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet):
first fuzz `<TAG>` to see which tags reflect, then fuzz events on an allowed tag.
`<animateTransform>` survives the tag filter, and `onbegin` survives the event
filter.

### 3. Fire onbegin

`onbegin` runs when the SVG animation begins, which happens automatically on
render — so placing `animateTransform` inside `<svg>` fires without any user
action:

```
/?search=<svg><animateTransform onbegin=alert()></svg>
```

Submitting that search calls `alert()` in the reflected context, solving the lab.

## Flag

```
alert() fired in the reflected context — lab solved
```

## Learn more

The transferable idea: SVG is a whole second markup language embedded in HTML,
with its own tags and its own animation events (`onbegin`, `onend`,
`onrepeat`) — and blocklist filters routinely under-cover it. `<animateTransform>`
with `onbegin` is valuable because the event self-fires the instant the element
renders, so it needs no click, hover, or resize to trigger.

As with every WAF-bypass lab, the blocklist is the wrong control. The fix is
context-aware output encoding of the reflected value, or stripping to an
allowlist of known-safe elements — not chasing individual tag names.

- [PortSwigger — XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)

## Tools

`burp` (Intruder)
