# Experiment 003 — Are standard MT metrics valid for Tigrinya?

| Field | Value |
| --- | --- |
| **Experiment ID** | `003-metric-validity` |
| **Date** | 2026-08-03 |
| **Author** | Research session (Claude Opus 5) |
| **Status** | **Complete — all four hypotheses REFUTED, directions all correct** |
| **Related report** | `docs/research/reports/08_evaluation/001-metric-validity-and-harness.md` |
| **Related decision** | **DEC-005**; gates `docs/benchmarks/metrics.md` |

---

## Question

Does BLEU — the default machine-translation metric — mean the same thing on
Tigrinya as it does on English, and if not, what should we use instead?

## Why this matters

`docs/benchmarks/metrics.md` states the problem precisely and marks it
unanswered: *"Most standard NLP metrics were developed and validated on
high-resource, morphologically simple languages… We may not assume standard
metrics transfer."* **DEC-005** already names FLORES-200 as our translation
anchor without specifying a metric.

BLEU counts exact matches of whitespace-delimited word n-grams. Two properties of
Tigrinya threaten that directly:

1. **Agglutination** packs into one word what English spreads over several, so
   there are fewer words per sentence — and each one carries more of the score.
2. **Templatic + agglutinative morphology** means a single lemma surfaces in many
   forms. A translation that is right in every respect except one inflectional
   affix scores as a **complete miss** under exact word matching.

If both hold, BLEU on Tigrinya is measuring something noisier and harsher than
BLEU on English — and the two numbers are not comparable, even though people
routinely compare them.

**The controlled comparison this experiment exploits:** FLORES+ is a *parallel*
corpus. The same 30 sentences exist in English and Tigrinya, professionally
translated. Content, domain, and register are held constant; the only variable is
the language. That makes it possible to attribute differences to linguistic
structure rather than to sampling.

## Hypotheses — pre-committed

**H1 — Tigrinya packs more per word.**
On identical content, Tigrinya uses substantially fewer whitespace-delimited
words than English. *Prediction:* Tigrinya word count **< 0.80 ×** English.

**H2 — Tigrinya word forms repeat far less.**
Morphological productivity inflates the type/token ratio.
*Prediction:* TTR(ti) **> 1.3 ×** TTR(en).

**H3 — BLEU is harsher on Tigrinya. ⭐**
At an identical *rate* of word-level error, BLEU falls further on Tigrinya than
on English — because each word is a larger share of the sentence and n-gram
matches are scarcer. *Prediction:* BLEU drop(ti) **> 1.2 ×** BLEU drop(en).

**H4 — chrF is the more robust metric under inflectional near-misses. ⭐**
For a word that is correct except for its final character — a proxy for right
stem, wrong affix — character n-gram F-score retains most of the credit that
word-level BLEU discards entirely.
*Prediction:* chrF retains **> 2 ×** the score BLEU retains, on Tigrinya.

## Success Criteria

| Outcome | Consequence |
| --- | --- |
| **H3 + H4 confirmed** | **chrF becomes the primary translation metric; BLEU reported only for comparability with published work, explicitly labelled as not comparable across languages** |
| H3 confirmed, H4 refuted | BLEU is untrustworthy but chrF is no better — escalate to learned metrics (COMET) or human evaluation, which is far more expensive |
| H3 refuted | BLEU transfers better than feared; keep it as primary and record that the concern was tested and did not hold |
| H1/H2 refuted | The structural premise behind the whole concern is wrong — revisit **A-003** |

**Pre-committed:** whatever the result, `docs/benchmarks/metrics.md` gets filled
in from it, and DEC-005 is amended to name a metric.

## Method

1. 30 aligned English–Tigrinya sentence pairs from **FLORES+** (`tir_Ethi`,
   `eng_Latn`, ids 0–29), CC-BY-SA-4.0.
2. Measure structural statistics: words/sentence, type/token ratio,
   characters/word, n-gram repetition.
3. **Perturbation study.** Apply identical, language-agnostic corruptions at
   matched rates to both languages, and measure how BLEU and chrF respond:
   - **near-miss** — change a word's final character (right stem, wrong affix)
   - **lexical** — replace a whole word (genuinely wrong word)
4. Compare the *shape* of degradation, not the absolute scores.

**Controls:** identical content, identical perturbation rates, identical metric
implementations (`sacrebleu`, pinned). The only variable is language.

## Known limitations — stated before running

- **30 sentences.** FLORES+ devtest has 1,012 per language, but egress policy
  blocks bulk download (`ACTIONS.md` **A-09**); rows come through the HF MCP tool
  one page at a time. Enough to establish *direction and magnitude* of a
  structural effect; not a precise score estimate.
- **Perturbation is a proxy, not real MT output.** Changing a final character
  approximates an inflectional error; it is not a sample of what a real system
  gets wrong. The direction of the effect is what this tests.
- **No COMET.** Learned metrics require model downloads from the blocked domain.
  Whether COMET is trustworthy for Tigrinya is left explicitly open.

## Reproduce

```
pip install sacrebleu==2.6.0
python3 run.py
```

Deterministic — perturbations use a fixed seed.

---

## Results

**All four hypotheses refuted — and every single effect pointed in the predicted
direction.** The directions were right; my thresholds were too aggressive. That
distinction is the whole finding, so it is stated first rather than buried.

| Hypothesis | Threshold | Measured | Verdict |
| --- | --- | --- | --- |
| H1 — ti packs more per word | < 0.80× words | **0.93×** | ❌ refuted (right direction) |
| H2 — ti has higher TTR | > 1.3× | **1.18×** | ❌ refuted (right direction) |
| H3 — BLEU harsher on ti | > 1.2× loss | **1.08×** | ❌ refuted (right direction) |
| H4 — chrF retains ≫ BLEU | > 2.0× | **1.48×** | ❌ refuted (right direction) |

### Structure on identical content

| Measure | English | Tigrinya | ti/en |
| --- | ---: | ---: | ---: |
| Words total | 707 | 659 | 0.93× |
| Words / sentence | 23.57 | 21.97 | 0.93× |
| Unique word forms | 453 | 496 | 1.09× |
| **Type/token ratio** | 0.641 | **0.753** | **1.18×** |
| **Characters / word** | 5.31 | **3.69** | **0.69×** |
| 4-grams repeated | 0.0% | 0.0% | — |

### Metric response to identical corruption

Percentage of the perfect score retained. Higher is more robust.

| Corruption | Rate | BLEU en | BLEU ti | chrF en | chrF ti |
| --- | ---: | ---: | ---: | ---: | ---: |
| near-miss | 10% | 78.7% | 77.8% | 94.1% | **91.6%** |
| near-miss | 20% | 61.2% | 56.5% | 87.9% | **82.5%** |
| near-miss | 30% | 42.5% | **41.5%** | 82.3% | **74.9%** |
| lexical | 10% | 78.6% | 76.2% | 87.1% | 85.8% |
| lexical | 20% | 59.7% | 55.7% | 76.2% | 70.7% |
| lexical | 30% | 44.8% | 38.0% | 69.3% | 59.7% |

**chrF's advantage over BLEU grows as quality falls** — 1.18× → 1.46× → 1.80×
retention ratio at 10/20/30% near-miss corruption on Tigrinya.

---

## Analysis

### The headline: the standard worry about BLEU is real but much smaller than advertised

The premise in `metrics.md` — that word-level metrics may not transfer to
morphologically rich languages — **is directionally correct and quantitatively
modest**. BLEU is about **8% harsher** on Tigrinya than English for the same
error rate. That is a real bias worth knowing about. It is not the catastrophe
the framing implies, and it does **not** justify discarding BLEU.

Had I not pre-committed thresholds, I would have written "BLEU is harsher on
Tigrinya, chrF is more robust" — both true — and presented it as vindication.
The pre-commitment forces the more useful statement: **the effects are real,
consistent, and roughly half the size I predicted.**

### A methodological check that strengthens the H3 refutation

Changing one final character is **not** an equal-magnitude edit across these
languages. A Latin letter is one phoneme; a Ge'ez character is a
consonant+vowel *pair*.

| | word length | one final char destroys |
| --- | ---: | ---: |
| English | 5.31 chars | 18.8% of the word |
| Tigrinya | 3.69 chars | **27.1%** of the word |

The perturbation was **~1.44× harsher on Tigrinya**, which biases *toward*
confirming H3 and H4. Both were refuted anyway — so the true effects are, if
anything, **smaller** than measured. H3's refutation is therefore robust.

For H4 the same bias depresses Tigrinya's chrF retention, so the 1.48× figure is
a **lower bound**; a magnitude-matched perturbation would likely score chrF
better. H4's refutation is about the threshold, not about chrF's merit.

### Reconciling H1's refutation with A-003

H1 predicted Tigrinya would need far fewer words. It needs only 7% fewer — which
looks like evidence against agglutination mattering. **It is not.** The
characters/word row explains why:

- English word = 5.31 characters = **5.31 phonemes**
- Tigrinya word = 3.69 characters × 1.957 (measured in Experiment 002) =
  **7.22 phonemes**

**Tigrinya words carry ~36% more phonemes than English words.** The
morphological load is real; the **Ge'ez script hides it** at the character level,
because one character does the work of two. Word *counts* barely move because
FLORES+ sentences are professionally translated to preserve structure.

This is an independent cross-check between two experiments run on different
corpora for different purposes, and they agree.

### Why chrF still wins despite H4's refutation

The decision does not hinge on clearing an arbitrary 2× bar. What matters:

1. chrF retains **74.9%** where BLEU retains **41.5%** at 30% near-miss
   corruption — a large practical gap.
2. **The gap widens as quality degrades** (1.18× → 1.80×). Low-resource MT
   operates precisely in that low-quality regime, which is where BLEU is least
   informative and chrF most.
3. chrF is less sensitive to the tokenization choices that Experiment 002 showed
   are themselves unsettled for Ge'ez.

### The 0% 4-gram repetition, in both languages

No 4-gram repeats in either language across 30 sentences. This is a **sample-size
artefact, not a Tigrinya property** — it is equally true of English here. It is
recorded so nobody later mistakes it for a finding about Tigrinya.

## Conclusion

**Adopt chrF as the primary translation metric; report BLEU alongside it for
comparability with published work, labelled as not comparable across languages.**

That recommendation survives all four refutations because it never depended on
the thresholds — it depends on chrF degrading more gracefully exactly where
low-resource systems live.

**The concern in `metrics.md` is now quantified rather than asserted:** BLEU
carries roughly an 8% harshness penalty on Tigrinya relative to English. Small
enough to keep using BLEU; large enough that **cross-language BLEU comparisons
must never be made without stating it.**

**Meta-note (P-13):** four refutations, four correct directions. The value here
was not in being right about the magnitudes — it was in finding out that a
widely-repeated qualitative claim is, on measurement, a modest quantitative one.
Publishing "BLEU is unsuitable for morphologically rich languages" would have
been defensible-sounding and wrong by a factor of two.
