# Success Metrics

## Purpose of this document

How we will know whether this project is working.

**Why it exists:** Without agreed metrics, "is it working?" gets answered by
whoever is most optimistic, and projects sustain themselves on activity rather
than results. Metrics defined in advance are the defence against measuring
ourselves by effort expended.

**How to use it:** Review against these periodically. When a metric consistently
fails to reflect reality, change the metric deliberately — but notice that
changing a metric because you are failing it is a specific and common
self-deception.

**What future contributors should add:** Concrete targets, once research
establishes what is achievable. Baselines, once measured. Replace the
placeholders below with real numbers — and record the basis for each target.

> **Status:** **No targets are set, and that is still deliberate** — but four
> capabilities are now measured, which this table denied until 2026-08-23.
>
> Setting numeric targets before knowing the state of the art for Tigrinya would
> produce numbers with no basis, either trivially achievable or impossible with
> no way to tell which. **A baseline is not a target**, and the rows below now
> distinguish the two.
>
> ⚠️ **Every row read `TBD / Unknown / Unset / Not measured` — including
> transliteration and tokenization, which experiment 004 measured, and
> translation, whose metric DEC-009 validated.** Found by audit, the same class
> of error as `metrics.md` claiming morphology was validated when nothing had
> tested it.

---

## Tier 1 — Capability metrics

*Does the technology work?*

These are measured through the evaluation infrastructure defined in
`../benchmarks/`. Every one requires a Tigrinya-specific evaluation set to be
meaningful; multilingual benchmark averages that may not even include Tigrinya
do not count.

| Capability | Metric | Baseline | Target | Status |
| --- | --- | --- | --- | --- |
| **Tokenization** | **Reversibility + fertility + `[UNK]` rate** (DEC-023) | **100.00%** round-trip, **0** `[UNK]` | Unset | ✅ **measured — intrinsic** |
| **Transliteration** | **Determinism + coverage + word-level alignment** (DEC-023) | **100%** deterministic, **100.00%** letter coverage | Unset | ✅ **measured — intrinsic** |
| **Normalisation** | **Idempotence + collapse rate** | **0** non-idempotent, **4** forms collapsed | Unset | ✅ **measured — intrinsic** |
| **Translation (→ Tigrinya)** | **chrF primary, BLEU alongside** (DEC-009) | ⚠️ **none — no model has been scored** (A-09) | Unset | ⚠️ **metric validated, nothing measured** |
| Translation (Tigrinya →) | chrF primary, BLEU alongside (DEC-009) | ⚠️ none — no model scored | Unset | ⚠️ metric validated, nothing measured |
| **Morphological analysis** | Consistency + coverage; accuracy needs gold data | — | Unset | ❌ **not implemented** (A-07) and **not measured** |
| Embeddings / semantic similarity | ⚠️ **TBD and genuinely unsolved** — `tiroberta-bi-encoder` is monolingual, so FLORES+ bitext retrieval does not apply | — | Unset | ❌ Tier 1, unbuilt (A-01) |
| Semantic search | TBD | — | Unset | ❌ not researched |
| Cross-language retrieval | TBD | — | Unset | ❌ not researched |
| Lemmatization | TBD | — | Unset | ❌ not researched |
| Spell correction | TBD | — | Unset | ❌ not researched |
| Grammar checking | TBD | — | Unset | ❌ not researched |
| Named entity recognition | TBD | — | Unset | ❌ not researched |
| Entity linking | TBD | — | Unset | ❌ not researched |
| Summarization | TBD | — | Unset | ❌ not researched |
| Question answering | TBD | — | Unset | ❌ not researched |

⚠️ **"Measured — intrinsic" is a weaker claim than it looks.** Intrinsic checks
catch *broken*, not *wrong*: a transliterator returning deterministically
incorrect phonemes passes every one of them. **No baseline here has been seen by
a Tigrinya speaker** — `validation/` holds the instrument for that, awaiting
**A-13**. Until it returns, "measured" means *self-consistent*, not *correct*.

**Metric selection is itself a research question.** Standard metrics were mostly
validated on high-resource, morphologically simple languages. Whether they mean
anything for Tigrinya must be established, not assumed — see
`../research/reports/08_evaluation/`.

---

## Tier 2 — Platform metrics

*Is it usable and affordable?*

| Metric | Why it matters | Target | Status |
| --- | --- | --- | --- |
| API p50 / p95 latency | Usability floor | Unset | Not measured |
| Uptime | Infrastructure others depend on must be dependable | Unset | Not measured |
| Monthly operating cost at current volume | Sustainability — see A-008 | Unset | Not measured |
| Cost per 1k requests | Unit economics | Unset | Not measured |
| Time from install to first successful call | Developer experience | Unset | Not measured |
| Reproducibility rate of published results | Non-negotiable | 100% | Not measured |

---

## Tier 3 — Adoption metrics

*Is anyone using it?*

Deliberately last. Adoption metrics are easy to game and easy to mistake for
progress. They are tracked, not optimised.

| Metric | Notes |
| --- | --- |
| Applications built on the platform | The metric that matters most — infrastructure succeeds when others build on it |
| API consumers | Distinct users making real calls, not signups |
| SDK installs | Weak signal; tracked, not trusted |
| External contributions | Community health |
| Datasets and tools released and reused | Ecosystem contribution — G-11 |
| Citations / references by other work | Slow-moving but genuine signal |

---

## Anti-metrics

Things we deliberately do **not** optimise for, because optimising them makes the
project worse:

- **Model size or parameter count.** Bigger is not better; cheaper and adequate
  beats larger and unaffordable.
- **Number of capabilities shipped.** Ten mediocre capabilities are worth less
  than three good ones, and cost more to maintain.
- **Benchmark scores on non-Tigrinya benchmarks.** Multilingual averages are not
  evidence about Tigrinya.
- **Lines of code, commits, or documents written.** Activity, not progress.
- **Training runs completed.** See A-004 — a training run is a cost until proven
  otherwise.

---

## The honest test

Beyond any dashboard, the question that matters:

> **Can someone build something genuinely useful in Tigrinya, quickly, because
> this platform exists — without needing to understand tokenization, morphology,
> or evaluation to do it?**

If yes, the project works. If no, the metrics above are measuring the wrong
things and should be revised.
