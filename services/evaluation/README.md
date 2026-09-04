# `tigrinya-eval` — variety-scoped translation evaluation

Implements **DEC-009** (chrF primary, BLEU alongside) and **DEC-010**
(variety-scoped, never aggregated).

```bash
pip install -e ".[dev]"
pytest          # 14 tests
```

```python
from tigrinya_eval import EvalSet, Harness

flores = EvalSet(name="flores+_devtest", variety="unknown",
                 references=refs, licence="CC-BY-SA-4.0")

h = Harness()
h.evaluate("madlad400-3b-mt", madlad_output, flores)
h.evaluate("nllb-200-3.3B", nllb_output, flores, shippable=False,
           notes=("CC-BY-NC-4.0 — comparison baseline only",))
print(h.report())
```

## Two rules it makes structurally impossible to break

**BLEU cannot be obtained alone.** `score()` always returns both metrics.
DEC-009 forbids reporting BLEU by itself, and the cheapest enforcement is to
make the alternative unrepresentable rather than a convention someone must
remember.

**`aggregate()` raises.** Our two DEC-005 anchors appear to be in **different
Tigrinya varieties** — TiQuAD is verified Eritrean-sourced, while FLORES+ shows
Ethiopian markers at a 15.1% rate against 1.0–3.8% for Eritrean sources. A
combined score would describe a language nobody speaks. An exception, not a
warning: a warning would be ignored exactly when it mattered.

## Why chrF is primary

Measured, not assumed (Experiment 003, on FLORES+ parallel data where the same
sentences exist in both languages so language is the only variable):

| Near-miss corruption | BLEU kept | chrF kept | ratio |
| ---: | ---: | ---: | ---: |
| 10% | 77.8% | 91.6% | 1.18× |
| 30% | 41.5% | **74.9%** | **1.80×** |

**chrF's advantage widens as quality falls** — and low-resource MT lives in the
low-quality regime. The metric is chosen for how it behaves when systems are
weak, not when they are strong.

BLEU is kept because it is what every published Tigrinya result reports, and
dropping it would forfeit comparability. But it is **~1.08× harsher on Tigrinya
than English**, and the report says so on every run: comparing a Tigrinya BLEU
to another language's without that caveat is a documented error.

## Confidence intervals are on by default

DEC-009 requires spread on small evaluation sets, and ours are small — FLORES+
devtest is 1,012 sentences and we have often had far fewer. On three sentences
the harness reports `chrF 59.33 [30.62, 88.05]`, which is the point: a bare
point estimate would look authoritative.

## `shippable=False`

Marks a system that may be **measured but never deployed**. Every NLLB variant
is CC-BY-NC-4.0 (**DEC-011**), and it is the baseline the published Tigrinya
literature uses — so our production model and our comparison baseline are
different models, and any claim to match published quality requires running both
here.

## Status

**The harness works; no model has been run through it.** Model weights are
behind an egress block (**A-09**), so MADLAD-400-3B's Tigrinya quality — which
appears to be **unpublished** — is still unmeasured. When it can be run, this is
what runs it.

A bug caught during development is worth recording: sacrebleu returns numpy
`float32`, which is not JSON-serialisable, so `save()` would have failed the
first time anyone persisted a real run.
