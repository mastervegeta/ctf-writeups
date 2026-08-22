---
title: "PowerAnalysis: Part 2"
event: cylabacademy
category: cryptography
points:
difficulty: hard
date: 2026-08-22
tags: [side-channel, aes, cpa, dpa, scared, numpy, python]
status: published
---

# PowerAnalysis: Part 2

> **Event:** cylabacademy · **Category:** cryptography

## Challenge

Instead of a service to query, this one ships a `traces/` folder — 100 captures,
`trace00.txt` … `trace99.txt`, each a plaintext and the power trace recorded
while it was encrypted under the fixed key. Recover the key.

```
Plaintext: d72123392ff65005c95467045e1b8dd7
Power trace: [41, 63, 94, 141, 105, 99, 81, 107, 92, 77, 50, ...]
```

2666 samples per trace.

## TL;DR

Same CPA as [Part 1](../power-analysis-part-1/), with the pwntools half deleted.
The traces are already captured, so the only new code is a parser; everything
from `read_ths_from_ram` down is copy-pasted. Rated hard, but it is the easiest
of the three — Part 1 does all the thinking, this one just changes where the
data comes from.

## Approach

### 1. Parse the folder

`sorted()` so trace order matches plaintext order, and one `split` on the
`Power trace: ` label cuts each file in two.

```python
for file in sorted(pathlib.Path("traces").iterdir()):
    plaintext_data, powerdata = file.read_text().split("Power trace: ")
    plaintext = plaintext_data.split(": ")[1].strip()
    power_list = [int(x) for x in powerdata.strip().strip("[").strip("]").split(", ")]
```

### 2. Run Part 1's attack unchanged

```python
heat_array = numpy.array(heat_data, dtype="float32")       # (100, 2666)
plaintext_array = numpy.array(plaintexts, dtype="uint8")   # (100, 16)

ths = read_ths_from_ram(samples=heat_array, plaintext=plaintext_array)
attack = scared.CPAAttack(
    selection_function=scared.aes.selection_functions.encrypt.FirstSubBytes(),
    model=scared.HammingWeight(),
    discriminant=scared.maxabs,
)
attack.run(scared.Container(ths))
key = numpy.abs(attack.scores).argmax(axis=0)
```

```
recovered key:  8eb5d06d8ad0aaebc7cc5a0b1ba5ed8c
```

100 traces is enough, and with no network in the loop the whole thing finishes
in about 5 seconds.

## Flag

```
picoCTF{8eb5d06d8ad0aaebc7cc5a0b1ba5ed8c}
```

## Learn more

Handing over a fixed trace set is how real DPA work actually looks — capture is
a separate, slow step done once on a scope, and the analysis is then re-run
offline against the same file set while tuning the model, the sample window, or
the distinguisher. Trace counts are not a difficulty signal either: 300 in
Part 1 was a guess that worked first try, not a measured minimum, and 100 is
simply what this capture shipped with.

- [scared documentation](https://eshard.gitlab.io/scared/) — `estraces` also has
  `read_ths_from_trs_file`, `read_ths_from_ets_file` and `read_ths_from_sqlite`
  for real capture formats, instead of arrays built in RAM

## Tools

`scared`, `estraces`, `numpy`, `python3`
