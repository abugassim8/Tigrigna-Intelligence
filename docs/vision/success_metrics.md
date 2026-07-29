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

> **Status:** No targets are set. Setting numeric targets before knowing the
> current state of the art for Tigrinya would produce numbers with no basis —
> either trivially achievable or impossible, with no way to tell which. Targets
> get set after `08_evaluation` research establishes baselines.

---

## Tier 1 — Capability metrics

*Does the technology work?*

These are measured through the evaluation infrastructure defined in
`../benchmarks/`. Every one requires a Tigrinya-specific evaluation set to be
meaningful; multilingual benchmark averages that may not even include Tigrinya
do not count.

| Capability | Metric | Baseline | Target | Status |
| --- | --- | --- | --- | --- |
| Translation (→ Tigrinya) | TBD — see `08_evaluation` | Unknown | Unset | Not measured |
| Translation (Tigrinya →) | TBD | Unknown | Unset | Not measured |
| Embeddings / semantic similarity | TBD | Unknown | Unset | Not measured |
| Semantic search | TBD | Unknown | Unset | Not measured |
| Cross-language retrieval | TBD | Unknown | Unset | Not measured |
| Morphological analysis | TBD | Unknown | Unset | Not measured |
| Lemmatization | TBD | Unknown | Unset | Not measured |
| Tokenization quality | TBD | Unknown | Unset | Not measured |
| Spell correction | TBD | Unknown | Unset | Not measured |
| Grammar checking | TBD | Unknown | Unset | Not measured |
| Transliteration | TBD | Unknown | Unset | Not measured |
| Named entity recognition | TBD | Unknown | Unset | Not measured |
| Entity linking | TBD | Unknown | Unset | Not measured |
| Summarization | TBD | Unknown | Unset | Not measured |
| Question answering | TBD | Unknown | Unset | Not measured |

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
