# Experiment 006 — What does Tier 0 actually cost in time?

| Field | Value |
| --- | --- |
| **Experiment ID** | `006-tier0-latency` |
| **Date** | 2026-08-19 |
| **Author** | Research session |
| **Status** | **Complete — all four hypotheses confirmed** (see the caveat on that) |
| **Related decisions** | Feeds **DEC-019**; partially addresses **A-14**; occasions **DEC-016 Amendment 1** |
| **Determinism** | **Non-deterministic by declaration** — timings vary by host |

---

## Question

Two inputs to the DEC-019 break-even model are **assumed, not measured**:
**cold start**, left as a free parameter from 1 s to 60 s, and **service time**,
assumed at ~2 s. `10_infrastructure` says so in its own limits section, and
**A-14** exists because of it.

Tier 0 is now built, so its half is measurable.

## What this does not do

**It does not close A-14.** A-14 asks for **Tier 2**'s cold start, which needs a
translation model this environment cannot fetch (**A-09**). This is Tier 0 only
— and Tier 0 is the tier DEC-013 keeps *always warm*, so its cold start is the
one that matters least.

It is worth measuring anyway: the service-time input feeds the same model, and a
measured number beats an assumed one even when it is not the number you most
wanted.

## Hypotheses — pre-committed

Written into `run.py` before any measurement was taken.

- **H1** — cold start is dominated by the dependency, not our code. `epitran`
  pulls in `panphon`, 107.4 MB of the 113.4 MB footprint. *Prediction: ≥ 80%.*
- **H2** — Tier 0 cold start is far below the table's slow end (60 s).
  *Prediction: < 5 s.*
- **H3** — warm service time is orders of magnitude below the assumed 2 s.
  *Prediction: < 50 ms for a ~20-word sentence.*
- **H4** — the `lru_cache` on `transliterate_word` earns its place.
  *Prediction: ≥ 10× faster than uncached.*

## Results

Median of 5 cold runs (fresh interpreter each) and 200 warm runs. Cold start is
measured **out of process** — anything timed in-process has already paid the
import being measured.

### Cold start — 3.03 s, and 98.7% of it is one dependency

| Stage | Median |
| --- | ---: |
| Bare interpreter | 12.5 ms |
| `import tigrinya_primitives` | 53.0 ms — **ours: 40.5 ms** |
| First `transliterate()` (loads epitran) | 3,046.1 ms — **epitran: 2,993.0 ms** |
| First `normalise()` (no epitran) | 51.9 ms |
| **Cold start, excluding interpreter** | **3,033.5 ms (3.03 s)** |

**H1 CONFIRMED — 98.7%.** **H2 CONFIRMED — 3.03 s.**

Our own import is **40 ms**. Everything else is `epitran` → `panphon`. If cold
start ever needs to come down, **the lever is the dependency, not our code** —
which is the same conclusion the footprint measurement reached (107.4 MB of
113.4 MB), now independently reproduced in the time dimension.

### Service time — 0.045 ms, not 2 s

| Operation (20-word sentence) | Median |
| --- | ---: |
| `normalise` | **0.0086 ms** |
| `transliterate` (cache warm) | **0.0436 ms** |
| Tokenizer `encode` | **0.0454 ms** |

**H3 CONFIRMED — 0.045 ms**, about **44,000× below** the 2 s the model assumed.

⚠️ **This does not refute that assumption.** The 2 s figure in
`10_infrastructure` was for **Tier 2**, a 3B translation model on CPU. It says
nothing about Tier 0 and Tier 0 says nothing about it. What this establishes is
narrower and still useful: **for Tier 0 the break-even model reduces to cold
start alone**, because service time rounds to zero against it.

### Cache — 238.7×

| | Median (20 unique words) |
| --- | ---: |
| Cached | **0.0012 ms** |
| Uncached (`cache_clear()` each pass) | **0.2955 ms** |

**H4 CONFIRMED — 238.7×**, far past the 10× predicted. Experiment 005 confirmed
the cache is *sound* (left context is inert, 0 of 1,565); this shows it is also
worth having.

### What it does to the break-even model

| Input | Value |
| --- | ---: |
| Tier 0 footprint (measured) | 0.1134 GB |
| Always-warm | 82.8 GB-h/month |
| Per request (cold + service) | 3.034 s |
| **Break-even** | **866,306 req/month = 1,187/hour** |

Against the assumed table's 58 req/hour at a 60 s cold start. **This changes
nothing operationally** — DEC-013 keeps Tier 0 warm either way — but it shows
the model swings by ~20× on a parameter that was guessed, and Tier 2's value is
still guessed.

## What changed as a result

**`tigrinya_primitives.warmup()` was added.** Lazy loading is right for a
library, but it defers all 3.0 s onto whoever calls first. A service that
DEC-013 keeps always warm should call `warmup()` at boot rather than be
warm-except-once.

## The caveat on "all four confirmed"

**Four of four confirming is a weaker result than it looks.** Experiments 002,
003 and 005 each refuted something and were more informative for it. Here the
thresholds were set loosely enough (< 5 s, < 50 ms, ≥ 10×) that the measurements
cleared them by one to four orders of magnitude — a prediction beaten by 44,000×
was not a real test.

The findings that carry weight are the **magnitudes**, not the verdicts: 98.7%
attribution to one dependency, and a break-even that moves ~20× on an assumed
parameter. Those were not predicted in advance.

## Reproduce

```bash
pip install -e services/primitives
python3 run.py
```

**Non-deterministic by declaration (DEC-016 Amendment 1).** `results.json`
carries `"deterministic": false`; CI runs it and requires an artefact but does
not byte-compare. **The cost is that this experiment gets no drift detection** —
unlike 001–005, it would not catch `epitran` changing behaviour.

## Limits

- **One host, one Python.** Timings describe the machine that produced them and
  are not portable. Container cold start on a real platform adds image pull and
  runtime init, neither of which is measured here.
- **Tier 2 is entirely unmeasured**, which is the number DEC-019 actually needs.
- **No concurrency.** Single-threaded medians; contention is not modelled.
- The break-even arithmetic reuses `10_infrastructure`'s formula unchanged, so
  it inherits any error in it.
