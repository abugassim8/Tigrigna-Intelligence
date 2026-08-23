# Assumptions

## Purpose of this document

A register of the things this project takes as given — the beliefs that shape
decisions but have not themselves been proven.

**Why it exists:** Every project runs on assumptions. The dangerous ones are the
invisible ones: beliefs so embedded that nobody notices they are beliefs, which
therefore never get tested even when evidence starts contradicting them. Writing
them down converts an invisible assumption into a testable claim.

**How to use it:**
- Read this before making recommendations. Treat it as **a list of things that
  might be wrong**, not a list of things that are true.
- **Challenge these.** If you find evidence contradicting an assumption, say so
  prominently. An assumption overturned by evidence is a good outcome, not an
  embarrassment.
- Add new assumptions as you notice yourself relying on them.

**What future contributors should add:** New assumptions as they surface — and,
just as importantly, updates to the status of existing ones as evidence arrives.
An assumption that has been validated should say so and link the evidence.

---

> ⚠️ **This register was frozen from 2026-07-29 to 2026-08-19** — through six
> experiments and sixteen decisions — while its stated purpose is recording
> "updates to the status of existing ones as evidence arrives."
>
> **All ten entries were re-audited on 2026-08-19.** What the freeze had hidden:
>
> | | |
> | --- | --- |
> | **A-002** | Status said `Unvalidated` while its own body said "CONFIRMED by measurement" |
> | **A-003, A-005, A-008** | Marked `Unvalidated` when experiments 002/006 and DEC-017/DEC-019 had settled them |
> | **A-007** | Confidence *raised to High* on `[reported]` evidence our own `[verified]` measurement contradicts |
> | **A-006** | Counted TiQuAD as available despite confirmed contamination and unresolved copyright |
> | **Deferred list** | Still called the project licence "Open, deliberately deferred" **sixteen days after DEC-020 closed it** |
>
> **Nothing was invalidated outright**; the register was wrong about its own
> confidence, not about the project's direction. That is the quieter failure —
> an assumption marked `Unvalidated` invites re-testing, while one wrongly
> marked `Supported — High` closes the question.

## Status values

| Status | Meaning |
| --- | --- |
| **Unvalidated** | Believed, not tested. Default for new entries. |
| **Supported** | Evidence gathered that supports it; linked. |
| **Contested** | Evidence exists on both sides; needs resolution. |
| **Invalidated** | Shown to be false. Kept in the register with what replaced it. |

---

## Standing assumptions

### A-001 — We prefer open source before commercial APIs

**Status:** **Supported** · **Confidence:** High · **Since:** 2026-07-29
**Evidence:** `../research/summaries/001-tigrinya-nlp-ecosystem-scan.md` — viable
open Tigrinya models exist (Apache-2.0 embeddings, CC-BY datasets), so the
preference is actionable rather than aspirational. Commercial MT (Google)
`[reported]` still leads on translation quality specifically, and is retained as
a **baseline to measure against** rather than a dependency (R-005).

Open models and open source tooling are preferred over commercial APIs where
they are viable. Rationale: cost control at low volume, no vendor deprecation
risk, the ability to inspect and adapt behaviour, and the ability to run without
sending data to third parties.

*This is a preference, not an absolute.* A commercial API that is dramatically
better for a capability we cannot otherwise deliver should be evaluated on its
merits, and rejecting it reflexively would violate the reuse-first philosophy.

**Would be invalidated by:** open options proving unusable for Tigrinya
specifically, or total cost of self-hosting exceeding API cost at our realistic
volume.

---

### A-002 — We optimize for low-resource language capability

**Status:** **Supported — confirmed by measurement** · **Confidence:** High
**Since:** 2026-07-29 · **Updated:** 2026-08-19

> ⚠️ **Status corrected 2026-08-19.** This read `Unvalidated` while its own
> evidence block below said **"CONFIRMED 2026-07-29 by measurement"** with row
> counts. Anyone scanning the status column saw the opposite of what the entry
> actually establishes.

Techniques, models, and architectures are selected for how well they work under
data scarcity — not for how well they perform on high-resource benchmarks. A
method that is state-of-the-art with 10M training examples is irrelevant to us
if we have 50k.

**Implication:** multilingual benchmark averages are near-worthless as evidence
here. What matters is Tigrinya-specific performance, and where that is
unavailable, performance on Ge'ez-script or Ethio-Semitic languages as the
nearest proxy.

**Would be invalidated by:** discovering Tigrinya data resources far larger than
currently expected.

**CONFIRMED 2026-07-29 by measurement.** `03_data_strategy/001` queried actual
row counts: **67,153 monolingual/QA rows (56 MB parquet)** plus **1.4M parallel
pairs**. TiRoBERTa's training corpus is 40M tokens. The open monolingual corpus
is the **same order of magnitude, not larger** — there is no hidden reservoir.
Data-hungry methods remain off the table.

---

### A-003 — We prioritize accuracy over speed

**Status:** **Supported — and the tension does not arise for Tier 0**
**Confidence:** Medium-high · **Since:** 2026-07-29 · **Updated:** 2026-08-19

> **Updated 2026-08-19 with measurement.** The assumption was written as a
> hypothetical trade ("a wrong translation in 50 ms is worse than a right one in
> 500 ms"). `experiments/006-tier0-latency/` measured the tier we have built:
>
> | Operation | Median |
> | --- | ---: |
> | `normalise` | **0.0086 ms** |
> | `transliterate` | **0.0436 ms** |
> | Tier 0 cold start | **3.03 s** (98.7% of it loading `epitran`) |
>
> **At 0.045 ms there is no accuracy/speed trade to make** — the bounding clause
> ("marginally more accurate and 100× slower fails") cannot bite at this scale.
> The assumption therefore constrains **Tier 2 only**, where translation is
> seconds-scale, and Tier 2 is entirely unmeasured (**A-09**, **A-14**).
>
> ⚠️ **Note the asymmetry:** cold start is 67,000× the warm service time. The
> speed risk in Tier 0 is not computation, it is **process lifecycle** — which is
> why `warmup()` exists and why DEC-013 keeps the tier warm.

Where the two conflict, correctness wins. A wrong translation returned in 50ms
is worse than a right one in 500ms — for infrastructure that others build on,
errors propagate into every downstream product.

*Bounded:* this holds within reason. An approach that is marginally more
accurate and 100× slower fails the operating-cost priority. Specific latency
budgets are a per-service decision, not a global one.

**Would be invalidated by:** a target use case with a hard real-time
requirement.

---

### A-004 — We avoid unnecessary model training

**Status:** **Supported — demonstrated** · **Confidence:** High
**Since:** 2026-07-29 · **Updated:** 2026-08-19
**Evidence:** The ecosystem scan found existing Tigrinya models for language
modelling, embeddings, POS, NER, and translation. DEC-006's minimum viable
platform requires **no training at all**.

> **Upgraded from "achievable" to "demonstrated" 2026-08-19.** **Tier 0 is
> built and shipped zero trained models**: `services/primitives` is
> normalisation, tokenization and transliteration over `epitran` and
> `tokenizers`, and `services/evaluation` wraps `sacrebleu`. The default answer
> to "should we train this?" has been *no* for the entire build so far, and
> nothing has been given up for it. **DEC-017** turned the preference into
> policy.

Training is a last resort, not a first instinct. It carries data cost, compute
cost, evaluation cost, and permanent maintenance burden — a trained model is
something we must keep alive, re-evaluate, and eventually retrain.

The default answer to "should we train this?" is **no**. The burden of proof
sits with whoever proposes training, and the proposal must articulate the
proprietary advantage created and cost the alternative of not training.

**Would be invalidated by:** finding that no existing model handles Tigrinya
adequately for a core capability — which is a plausible outcome, and exactly the
case where training becomes justified.

---

### A-005 — Fine-tuning and adaptation are preferred over training from scratch

**Status:** **Supported — and now decided policy** · **Confidence:** High
**Since:** 2026-07-29 · **Updated:** 2026-08-19

> **Updated 2026-08-19.** **DEC-017 settled this and the register never
> recorded it.** From-scratch pretraining is **foreclosed**, not merely
> deprioritised, and adaptation is gated behind a ladder with measured triggers:
> rung 0 use the checkpoint → rung 1 prompt/decoding → rung 2 **LoRA (~23×
> cheaper than full fine-tuning)** → rung 3 full fine-tune.
>
> The justification is A-002's ceiling: **40M tokens** makes from-scratch
> indefensible regardless of preference.
>
> ⚠️ **The ladder is blocked at the bottom, and not by compute.** There are
> **0 cleanly-licensed parallel sentences** (**A-05**), so rungs 2 and 3 have
> nothing to train on. This assumption is *supported* but currently *untestable*.

Where model work is genuinely required, adapting an existing model is preferred
over training from scratch. Corollary of A-004 and the reuse-first philosophy.

**Would be invalidated by:** a fundamental incompatibility between available
base models and Tigrinya's script or morphology that adaptation cannot bridge.

---

### A-006 — Tigrinya-specific evaluation data is scarce and will need to be built

**Status:** **Partially invalidated — refined twice** · **Confidence:** Medium
**Since:** 2026-07-29 · **Updated:** 2026-08-19

> ⚠️ **Second refinement, 2026-08-19.** Two things changed after the text below
> was written, and neither was recorded until an audit found this file frozen.
>
> **1. Most of Tier 0 needs no annotation at all.** DEC-023 established that
> primitives are evaluated **intrinsically** — idempotence, determinism,
> reversibility, coverage and alignment integrity are properties of the
> function. Three of four held on real text, so **P-4 is satisfiable for Tier 0
> today without building a benchmark.** The gold-standard requirement narrowed
> from four capabilities to **one: morphology**, which is also unimplemented
> (**A-07**). ⚠️ Intrinsic checks catch *broken*, not *wrong*.
>
> **2. TiQuAD is less available than this entry implies.** Its contamination in
> a third-party pretraining corpus is **confirmed** `[verified]`, its test set is
> **not public** (**A-04**), and its copyright position is **unresolved**
> (**A-06**). Counting it as available evaluation data overstates the position.

~~We assume there is little high-quality Tigrinya evaluation data~~ — **this was
too pessimistic.** More human-annotated evaluation data exists than assumed:

- **FLORES-200** — human-reviewed, includes Tigrinya (~3K samples `[reported]`)
- **TiQuAD** — human-annotated, 6,508 questions / 10,637 answers, CC-BY-SA-4.0
  `[verified]`. Published baselines: **mBERT F1 58.6, XLM-R F1 62.4**
  `[verified]` — ⚠️ **corrected from the 81% figure first recorded here.**
- **TIGQA** — a *second*, distinct QA dataset: 2.68K pairs from Tigrinya and
  Biology textbooks `[verified]`. Educational domain, complements TiQuAD's news.
- **TiALD** — 13,717 annotated comments, CC-BY-4.0
- **TiNC24** — 200K+ words NER-annotated `[reported]`, not yet located

**A third caveat, and the most serious** `[verified]` 2026-07-29:
`farefaine/tigrinya-pretraining` — advertised as pretraining text — carries
TiQuAD's QA schema and a validation split of **exactly 934 rows, matching
TiQuAD's**. ✅ **CONFIRMED by row-level preview** — identical `article_title`
and `context` to TiQuAD's own published sample entry, with three answer
annotations per question (TiQuAD's validation convention). Anyone pretraining on
it invalidates their own TiQuAD evaluation. → **DEC-008** makes screening
mandatory, and externally reported Tigrinya QA scores are now suspect.

**Two further caveats** `[verified]`:
- **TiQuAD's test split is request-gated**, not public — so the canonical
  held-out set requires an access request.
- **TiQuAD is Eritrean-sourced**, so under DEC-004 **Ethiopian-variety QA
  evaluation remains a genuine gap.** TIGQA is a candidate complement.

**Refined form of the assumption:** evaluation data exists for *translation, QA,
NER, and classification*, but **nothing was found for retrieval/semantic search,
morphological analysis, spell correction, or grammar checking** — which are
precisely the capabilities DEC-006 puts in the minimum viable platform.

**So the workstream survives, but narrowed:** we build evaluation sets for the
primitives and retrieval, and adopt existing sets elsewhere (DEC-005).

**New risk surfaced:** `fgaim/tigrinya-squad` (silver, machine-translated) and
`fgaim/tiquad` (gold) share authorship and probable source overlap.
**Contamination must be checked before TiQuAD is used as held-out evaluation.**

---

### A-007 — Morphological complexity is a first-order design constraint

**Status:** **Supported for retrieval/embeddings (untested); REFUTED for
tokenization (measured)** · **Confidence:** Medium (lowered from High)
**Since:** 2026-07-29 · **Updated:** 2026-08-19

> ⚠️ **Updated 2026-08-19 after an audit found this register frozen.**
> Confidence had been *raised to High* on `[reported]` paper evidence — including
> MoVoC's "21 BPE tokens versus 6" — and **our own `[verified]` measurement
> points the other way on the one dimension we tested.**
>
> `experiments/002-tokenizer-fertility/` trained BPE on identical text at matched
> vocabulary sizes, varying only whether the input was morphologically
> decomposed. **Raw Ge'ez won 10 of 10 configurations and 5 of 5 folds**, mean
> **+0.190 tokens/word (~8% worse)** for decomposition. DEC-007's
> token-efficiency rationale was withdrawn on that evidence.
>
> **What survives:** the assumption's *scope beyond tokenization*. Retrieval,
> embeddings and search were never tested here, and the underlying linguistic
> fact — that Tigrinya is morphologically rich — is not in dispute. What is
> refuted is the inference that morphology-aware segmentation therefore helps
> tokenization, which is the form the assumption was being used in.
>
> **Limit on the refutation:** 991 words. The *direction* is robust (10/10, 5/5,
> with an explicable mechanism — Ge'ez already encodes consonant+vowel per
> character, so BPE need not learn it); the *magnitude* is indicative.

We assume Tigrinya's morphology materially affects tokenization, retrieval,
embeddings, and search quality — and that approaches designed around analytic
languages will underperform without adaptation.

**Evidence gathered** (all `[reported]` — see the egress caveat in summary 001):

- The **MoVoC** paper (ACL Findings EMNLP 2025) reports one Tigrinya sentence
  tokenizing to **21 BPE tokens versus 6** with morphology-aware segmentation.
  *(Illustrative single sentence, not a corpus average — do not quote as one.)*
- The **Tigrinya NLP survey** (arXiv 2507.17974) reports that complex morphology
  causes **high OOV rates and extreme data sparsity**, explicitly "challenging
  standard tokenization and modeling techniques".
- **Morfessor** (unsupervised) reportedly performs **poorly** versus rule-based
  approaches on Tigrinya — a negative result consistent with morphology being
  structurally important rather than statistically discoverable from small data.

**Important nuance — do not over-claim.** MoVoC also reports **no significant
gain in automatic translation quality** from morphology-aware tokenization. The
demonstrated benefits are token efficiency, MorphoScore, and Boundary Precision.
Morphology matters for **cost and linguistic fidelity**; its downstream accuracy
benefit is **not yet established** and should be measured, not assumed.

**CONFIRMED by `02_linguistics` (2026-07-29) — mechanism identified.**

The reason morphology is first-order is now specific rather than general:
Tigrinya is **templatic *and* agglutinative**, so triconsonantal roots are
**discontinuous**, while the Ge'ez abugida **fuses consonant and vowel into one
character**. Consequently **a morpheme boundary can fall inside a single
character**, and no subword tokenizer operating on raw Ge'ez can represent it.
This is a representational limit, not a performance one. → **DEC-007**.

Independent corroboration arrived from arXiv 2509.20209 (`[verified]` abstract),
which reports a custom tokenizer "substantially outperforms" zero-shot
baselines with Bonferroni-corrected significance and human validation.

**Still do not over-claim:** MoVoC found *no* significant downstream MT gain from
morpheme-aware vocabulary. The reliable benefits are token efficiency and
linguistic fidelity; accuracy gains must be measured, not assumed.

---

### A-008 — The platform must be affordable to run at low volume

**Status:** **Supported — measured for Tier 0** · **Confidence:** High
**Since:** 2026-07-29 · **Updated:** 2026-08-19

> **Updated 2026-08-19.** Costed in **GB-hours**, deliberately not dollars —
> vendor pricing is unverifiable from this environment and volatile, while the
> arithmetic survives price changes (DEC-019).
>
> | Shape | Standing cost |
> | --- | ---: |
> | Merged, always warm | **1,193.1 GB-h/month** |
> | Tier 0 warm + Tier 2 to zero | **82.8 GB-h/month** |
>
> **Tiering cuts standing cost ~14×** while keeping the latency-sensitive path
> warm, so the assumption is actionable rather than aspirational. Tier 0's
> break-even against scale-to-zero is **1,187 req/hour** (measured cold start
> 3.03 s).
>
> ⚠️ **Tier 2 is still unmeasured**, and DEC-019 makes its deployment mode a
> function of that number. At a 60 s cold start the break-even falls to roughly
> **one request per minute** — so affordability at low volume is established for
> the tier we have and assumed for the tier we do not (**A-14**).

We assume usage grows slowly and that the platform must be economically
sustainable at low request volumes for an extended period. Architectures that
only make economic sense at scale we do not have are rejected.

**Would be invalidated by:** funding or adoption arriving far faster than
expected.

---

### A-009 — Licensing and provenance must be verifiable for everything we adopt

**Status:** **Supported — and now an active blocker** · **Confidence:** High
**Since:** 2026-07-29 · **Updated:** 2026-07-29

**This assumption stopped being theoretical.** The ecosystem scan found that
several of the most important reuse candidates carry **no stated licence**,
including `fgaim/tiroberta-base` — the foundation of the model family DEC-003
depends on — and the largest English–Tigrinya parallel dataset found.

Resolving these licences is now the **single highest-priority action item** on
the project. Until resolved, the core reuse plan is blocked.

**Sharpened 2026-07-29 by measurement.** Of 1,519,253 dataset rows measured,
**~99% carry no stated licence.** Cleanly licensed: **15,053 documents.**
Combined with TiQuAD's unresolved upstream copyright, **licensing — not volume —
is the binding constraint on this project's data strategy.** → DEC-008.

We assume that unclear licensing is disqualifying. As infrastructure that others
will build on, we cannot pass on rights we do not have — a downstream user
inheriting a licensing problem from us is a serious failure, not an inconvenience.

> **Sharpened again 2026-08-19 — verification is harder than assumed.** This
> assumption requires licences to be *verifiable*, and metadata turns out to be
> evidence rather than truth **in both directions**:
>
> - **HF tags were wrong on 2 of 4 datasets** examined.
> - **PyPI's legacy `license` field reads "NOT STATED" for five packages** whose
>   licences are declared under PEP 639 `license_expression` —
>   `sacrebleu`, `fastapi`, `sentence-transformers`, `trl`, `bitsandbytes`.
>   Trusting it would have **wrongly disqualified four dependencies**.
>
> So "verifiable" means *read the actual licence text*, and the screening gate
> asserts licence from a human rather than detecting it
> (`scripts/data_processing/screen_dataset.py`).

**Would be invalidated by:** nothing foreseeable. This is close to a hard
constraint.

---

### A-010 — The primitives layer is our differentiator, not the models

**Status:** **Supported — partly demonstrated** · **Confidence:** High
**Since:** 2026-07-29 · **Updated:** 2026-08-19

> **Updated 2026-08-19.** The primitives layer is **built** (Tier 0, both test
> suites passing), which moves this from a claim about where value *would* sit
> to one where half the claim is discharged.
>
> ⚠️ **The other half is not.** No Tigrinya API, MCP server or SDK exists here
> either — the surface is blocked on **A-02** — and **morphology, named in this
> assumption, is a deliberate stub** blocked on **A-07**. So the differentiator
> is currently *two of four* named components.
>
> **A live risk this assumption understates:** DEC-021 found the evaluation
> harness scored only translation — the one capability DEC-006 excludes. If the
> primitives are the differentiator, they are also the thing most likely to go
> unmeasured, because the ready-made metrics all point elsewhere.

We assume the value this project adds is concentrated in **Layer 0** (Ge'ez
normalisation, tokenization, morphology), the **evaluation harness**, and
**Layer 5** (API, MCP, SDKs) — not in the model layer, which largely exists.

**Evidence:** the ecosystem scan found a coherent existing model stack but **no**
Tigrinya API, MCP server, SDK, or production morphology service.

**Would be invalidated by:** someone else shipping a Tigrinya infrastructure
layer, or the existing models proving unusable — which would push work back into
the model layer.

---

## Assumptions we have deliberately not yet made

Recorded so nobody mistakes silence for a decision:

- ~~**Target users.**~~ **CLOSED** by DEC-002 (Proposed): application developers
  primary, researchers secondary. Awaiting owner confirmation.
- ~~**Dialect scope.**~~ **CLOSED** by DEC-004: both varieties, evaluated and
  reported separately.
- **Register scope.** **Still open.** Data exists at both extremes (TiALD =
  YouTube/informal, TiQuAD = news/formal) but nothing was found characterising
  the distance between them for Tigrinya. → `02_linguistics`.
- **Deployment model.** Self-hosted, managed service, or both — **open**.
- **Language pairs.** Which translation directions matter most — **open**.
  En↔Ti is best resourced; Am↔Ti has data and cultural proximity. Lower priority
  now that DEC-006 excludes translation from the minimum platform.
- **Diaspora-specific needs.** Whether they differ from in-country users —
  **open**, and plausibly relevant to transliteration priority.
- ~~**Project licence.**~~ **CLOSED** by **DEC-020** (2026-08-03): Apache-2.0
  for code, CC-BY-4.0 for documentation, **inherit** for data. Resolved once the
  upstream licence map was complete — **no code dependency imposes copyleft**;
  share-alike enters only through data. Closes **A-12**.
  ⚠️ *This entry still read "Open, deliberately deferred" until 2026-08-19,
  sixteen days after the decision.*

---

<!--
Add new assumptions above, numbered sequentially. When evidence arrives, update
Status and link it. Do not delete invalidated assumptions — record what replaced
them.
-->
