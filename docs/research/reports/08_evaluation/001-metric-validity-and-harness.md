# Metric Validity for Tigrinya, and What the Evaluation Harness Must Do

| Field | Value |
| --- | --- |
| **Report ID** | `001-metric-validity-and-harness` |
| **Domain** | `08_evaluation` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/006-metric-validity-and-harness.md` |
| **Related decisions** | **DEC-009**, **DEC-010**; amends DEC-005; engages DEC-004, DEC-008 |
| **Experiments** | `experiments/003-metric-validity/` |

---

## Objective

Answer the question `docs/benchmarks/metrics.md` was written to hold open:
**are standard NLP metrics valid for Tigrinya?** Then specify what the evaluation
harness must do, because **P-4** blocks every capability behind it.

**Method note.** Papers on metric validity for morphologically rich languages are
egress-blocked (`RESEARCH_ACCESS.md`). Rather than cite what could not be read,
this report **measures** the question directly, using FLORES+ parallel data where
the same sentences exist in English and Tigrinya — content held constant,
language the only variable.

---

## Finding 1 — The worry about BLEU is real, and about half the size it is usually stated

`metrics.md` warns that "surface-form comparison penalises legitimate
inflectional variation." **Measured, that is directionally right and
quantitatively modest.**

Experiment 003 pre-committed four hypotheses and **refuted all four — while every
effect pointed in the predicted direction.**

| Claim | Predicted | Measured |
| --- | --- | --- |
| Tigrinya needs fewer words for the same content | < 0.80× | **0.93×** |
| Tigrinya type/token ratio is higher | > 1.3× | **1.18×** |
| **BLEU falls further on Tigrinya for the same error rate** | > 1.2× | **1.08×** |
| **chrF retains far more than BLEU under inflectional near-misses** | > 2.0× | **1.48×** |

**BLEU carries roughly an 8% harshness penalty on Tigrinya relative to English.**
Real, consistent, worth stating — and not grounds for abandoning BLEU.

**A check that hardens this.** Changing a word's final character is not an
equal-magnitude edit across the two languages: a Latin letter is one phoneme, a
Ge'ez character is a consonant+vowel pair. It destroys 27.1% of an average
Tigrinya word versus 18.8% of an English one — **~1.44× harsher on Tigrinya**,
biasing *toward* confirming the hypotheses. They were refuted anyway, so the true
BLEU penalty is if anything **smaller** than 8%.

**Why this matters more than a vindication would have.** Without pre-committed
thresholds this would have been written up as "BLEU is unsuitable for
morphologically rich languages" — defensible-sounding, widely repeated, and wrong
by a factor of two.

## Finding 2 — chrF is still the right primary metric, for a reason the thresholds missed

H4 was refuted, and chrF still wins. The case does not rest on clearing an
arbitrary bar:

| Near-miss corruption | BLEU retained | chrF retained | ratio |
| ---: | ---: | ---: | ---: |
| 10% | 77.8% | 91.6% | 1.18× |
| 20% | 56.5% | 82.5% | 1.46× |
| 30% | 41.5% | **74.9%** | **1.80×** |

**chrF's advantage widens as quality falls.** Low-resource MT lives in exactly
that low-quality regime — which is where BLEU carries least information and chrF
most. A metric chosen for a language with a 40M-token ceiling (**A-002**) should
be chosen for how it behaves when systems are weak, not when they are strong.

chrF is also less exposed to the tokenization choices Experiment 002 showed are
unsettled for Ge'ez — it never tokenizes into words at all.

→ **DEC-009.**

## Finding 3 — ⚠️ Our two evaluation anchors are not in the same variety

**This is the most consequential finding for evaluation design.**

DEC-005 names **FLORES-200/+** (translation) and **TiQuAD** (QA) as anchors.
Earlier research established `[verified]` that **TiQuAD is Eritrean-sourced**
(Eritrean Ministry of Information, *Hadas Ertra*).

The FLORES+ Tigrinya set carries **Ethiopian/Tigray markers**, measured over
30 sentences:

| Signal | Count |
| --- | ---: |
| `ጸ`-series tsade (Eritrean standard) | 28 |
| `ፀ`-series tsade (Ethiopian-common) | **8** |
| `ኣ` alef (Ge'ez) | 62 |
| `አ` alef (Amharic-style) | **8** |
| `እስካብ` (Ethiopian) vs `ክሳብ` (Eritrean) | **2** vs 0 |
| `ብሄራዊ` (Ethiopian) vs `ሃገራዊ` (Eritrean) | **1** vs 0 |
| `እንትኸውን` (Tigray converb) | 1 |

Two things follow, and they are different in kind:

1. **`[verified]` — the evaluation set is orthographically inconsistent with
   itself.** Both tsade series and both alef forms appear *in the same file*.
   This is measurement, not interpretation.
2. **`[strong signal]` — it leans Ethiopian.** The diagnostic lexical forms all
   appear in their Ethiopian variant with **zero** Eritrean counterparts. I am
   not a native speaker and 30 sentences is a small sample, so this needs
   native-speaker confirmation before being treated as settled.

**Consequence either way.** Under **DEC-004** we support both varieties and report
them separately. If our translation anchor is Ethiopian-leaning and our QA anchor
is Eritrean, then **an aggregate "Tigrinya score" across the two is measuring two
different things and must not be reported.**

Note also: naive tsade/alef normalisation collapses only **4 of 496** unique forms
(0.8%). Orthographic variation is real but **thin** at this sample size — a useful
calibration against overestimating the normalisation problem (**DEC-007**).

→ **DEC-010.**

## Finding 4 — Anchor accessibility is worse than DEC-005 assumed

| Resource | Status |
| --- | --- |
| `openlanguagedata/flores_plus` (canonical successor) | 🔒 **Gated** — requires an access request |
| `Muennighoff/flores200` | Has `tir`, CC-BY-SA-4.0, but **Dataset Viewer disabled** (runs arbitrary Python) |
| `haoranxu/FLORES-200` | Parquet and convenient — **drops every low-resource language, no Tigrinya** |
| `alexei-v-ivanov-amd/flores_plus` | ✅ Ungated parquet mirror, CC-BY-SA-4.0, **contains `tir_Ethi`** — used here |
| TiQuAD test split | 🔒 Request-gated (**A-04**) |

**Both DEC-005 anchors are gated or awkward.** The pattern is worth recording:
*the convenience mirrors of multilingual benchmarks systematically drop the
low-resource languages*, so a working pipeline for high-resource languages is no
evidence the data exists for ours.

The ungated mirror stores all languages in one flat table keyed by `iso_639_3`
with an aligned `id`, sorted alphabetically by language — `tir` begins at row
**188232**, `eng` at **53636**. Recorded so nobody has to re-derive it.

## Finding 5 — What the harness must therefore do

1. **Report chrF and BLEU together, never BLEU alone** (DEC-009).
2. **Never aggregate across anchors of different varieties** (DEC-010). Every
   score carries a variety label, or is marked unknown.
3. **Screen every evaluation set for contamination before use** (DEC-008) — and
   for *quality*, which Experiment 002 showed is a separate failure mode.
4. **Report variance and confidence intervals.** Evaluation sets here are ~1,000
   sentences; `metrics.md` already requires this, and it is not optional at that
   size.
5. **Pin metric implementations.** `sacrebleu` 2.6.0 here. chrF has parameters
   (character n-gram order, word n-gram order, β) that change the number.
6. **Keep the raw-Ge'ez baseline in every comparison** — Experiment 002's
   refutation was only visible because a baseline existed.

## Limits of this report

- **30 sentences.** Enough for structural effects with consistent direction; not
  a precise score estimate. FLORES+ devtest has 1,012 per language, reachable
  once egress allows (**A-09**).
- **Synthetic perturbation**, not real MT output. Direction is what is tested.
- **COMET untested.** Learned metrics need model downloads from the blocked
  domain, so whether COMET is trustworthy for Tigrinya is **explicitly open** —
  and it is the metric NLLB's published Tigrinya numbers use, so this matters.
- **Variety attribution needs a native speaker.** Stated as signal, not fact.

---

## Decisions arising

- **DEC-009** — chrF primary, BLEU for comparability only, both always reported.
- **DEC-010** — Evaluation results are variety-scoped; no cross-variety aggregate.

**Evidence:** `experiments/003-metric-validity/`; FLORES+ via
`alexei-v-ivanov-amd/flores_plus` `[verified]`; TiQuAD provenance `[verified]`
from `docs/research/summaries/001-tigrinya-nlp-ecosystem-scan.md`.
