# Decisions

## Purpose of this document

This is the authoritative log of every significant technical and strategic
decision made on this project. It is the answer to "why is it built this way?"

**Why it exists:** Undocumented decisions get re-litigated by people who cannot
engage with the original reasoning because they never saw it. Worse, they get
*silently reversed* — someone makes a locally sensible choice that contradicts a
deliberate earlier one, and nobody notices until it is expensive. This file
prevents both.

**How to use it:**
- **Read it before making any recommendation.** This is mandatory for AI
  assistants (see `../research/AI_RESEARCH_RULES.md`) and strongly expected of
  humans.
- Append a record when a choice is made that would be expensive to reverse or
  that someone would otherwise re-argue.
- Use the format below, from `../research/templates/decision_template.md`.

**What future contributors should add:** One record per decision, in sequence.
Do not batch several decisions into one record — they will need to be superseded
independently.

---

## Rules

1. **Append-only.** To change a decision, write a new record that supersedes it
   and mark the old one `Superseded by DEC-NNN`. Never edit or delete history —
   the record of a decision that turned out badly is more valuable than the
   record of one that went well.
2. **Sequential IDs.** `DEC-001`, `DEC-002`, … Never reuse, never renumber.
3. **Every decision names its rejected alternatives.** Log them in
   [`rejected_options.md`](rejected_options.md) too.
4. **Every decision links its evidence.** A decision with no link to research is
   a preference; label it as one rather than dressing it up.
5. **Every decision states its consequences honestly**, including the negative
   ones and what it forecloses.

---

## Record format

```
Decision ID:
Date:
Decision:
Context:
Options:
Chosen:
Reason:
Consequences:
```

Expanded records may add **Status**, **Evidence**, **Revisit when**, and
**Related**. See `../research/templates/decision_template.md`.

---

## Index

| ID | Date | Decision | Status |
| --- | --- | --- | --- |
| DEC-001 | 2026-07-29 | Adopt a research-first repository and decision-log workflow | Accepted |
| DEC-002 | 2026-07-29 | Primary users are application developers; researchers secondary | **Proposed — needs owner confirmation** |
| DEC-003 | 2026-07-29 | Adopt the existing Tigrinya model layer; build primitives, evaluation, and integration | Accepted |
| DEC-004 | 2026-07-29 | Support both Tigrinya varieties; evaluate and report them separately | Accepted |
| DEC-005 | 2026-07-29 | FLORES-200 and TiQuAD as initial evaluation anchors | Accepted |
| DEC-006 | 2026-07-29 | Minimum viable platform is the primitives layer, not translation | Accepted |
| DEC-007 | 2026-07-29 | Consonant–vowel decomposition as the substrate beneath tokenization | Accepted |

---

## DEC-001 — Adopt a research-first repository and decision-log workflow

**Decision ID:** DEC-001

**Date:** 2026-07-29

**Status:** Accepted

**Decision:**
The project will run on a documented research operating system
(Scout → Analyst → Architect) with a mandatory decision log, compressed
summaries, and a strict separation between research, decisions, experimentation,
and production design. The workspace is built before research begins.

**Context:**
This project has a very wide capability scope — translation, retrieval,
embeddings, morphology, NER, knowledge graph, RAG, APIs, MCP, SDKs — for a
low-resource language where authoritative information is scarce and scattered.
Much of the research will be conducted across many separate sessions, including
AI-assisted sessions that begin with no memory of prior work. Without a
structure that makes prior findings cheap to reload, each session would
re-derive the same conclusions at significant cost, and contradictory decisions
would accumulate unnoticed.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Structured research OS with decision log, templates, and mandatory summaries | Findings are durable and cheap to reload; decisions are traceable; contradictions surface early | Upfront setup cost; ongoing documentation discipline required |
| B | Ad-hoc notes; document once the design settles | No upfront cost; feels faster early | Findings get lost; research is repeated; decisions become archaeology; the "settle" point never arrives |
| C | Full formal process (RFCs, review gates, sign-off) | Maximum rigour | Far too heavy for current team size; process would be abandoned within weeks |

**Chosen:** Option A.

**Reason:**
The dominant cost in a project of this shape is not computation or even
engineering — it is repeatedly rediscovering things that were already known.
Option A targets that cost directly at modest ongoing expense. Option B fails
precisely when the project gets interesting, because that is when the volume of
findings exceeds what anyone can hold in their head. Option C imposes
coordination overhead that a project at this stage cannot absorb and would
therefore be quietly abandoned, leaving us at Option B with extra steps.

The two-page summary limit and the summaries-before-reports read order are the
load-bearing parts of this decision, not incidental details: they are what make
the accumulated research affordable to consult.

**Consequences:**

- *Positive:* Research findings survive across sessions and contributors.
  Decisions are traceable to evidence. Rejected options stay rejected.
  Contradictions surface at review rather than in production.
- *Negative:* Every research effort carries a documentation tax — the report is
  not done until the summary is written. Some contributors will find this
  slower.
- *Accepted tradeoff:* We spend time on documentation infrastructure before
  producing any technical output. This is deliberate.
- *Newly constrained:* Code cannot land in `services/` without a corresponding
  decision record; capabilities cannot be built before their evaluation method
  exists.
- *Revisit when:* Documentation overhead is demonstrably slowing delivery
  without a corresponding reduction in repeated work, or the team grows past the
  point where an append-only flat file is workable.

**Evidence:**
None — this is a process decision made on judgement, not a research finding. It
is recorded here so that the reasoning is visible and so the process itself can
be challenged on evidence later.

**Related:** `../research/README.md`, `../research/AI_RESEARCH_RULES.md`,
`assumptions.md`

---

## DEC-002 — Primary users are application developers

**Decision ID:** DEC-002 · **Date:** 2026-07-29
**Status:** **Proposed — requires project-owner confirmation**

**Decision:**
The platform's primary users are **application developers** building Tigrinya
language features. **Researchers** are the secondary audience. Institutions
(media, government, education, NGOs) are served indirectly, through the
applications developers build.

**Context:**
This question sat open in `assumptions.md` and gates API design, SDK
priorities, and capability sequencing. No direct user research was possible —
community forums were not reachable in this session — so the determination is
**inferential**, drawn from the ecosystem scan.

The evidence: multiple mature Ge'ez keyboard products (GeezIME, GeezKTB, Mesmer
Tigrinya, GeezWord) each independently re-solve word suggestion and dictionary
lookup. GeezKTB additionally advertises grammar checking and translation. These
teams are building Tigrinya language features today, without a shared
infrastructure layer beneath them.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Developers primary, researchers secondary | Matches the observed gap; developers are reachable; researcher needs (evaluation, datasets) overlap with work we must do anyway | Inferential — no direct user research |
| B | Researchers primary | Clearest existing community; easiest to reach | Smaller impact; risks drifting toward N-4 (a research-output project) |
| C | Institutions primary | Potential funding | Long sales cycles; needs applications that do not exist yet |
| D | Defer the decision | Avoids being wrong | Blocks API and SDK design indefinitely |

**Chosen:** Option A.

**Reason:**
The duplication across keyboard products is the clearest demand signal found for
a shared layer — it is several independent teams paying the same cost. Serving
researchers simultaneously is nearly free, because the evaluation harness and
datasets they need are things **G-2** and **G-8** require regardless. Option D
was rejected because the cost of deferring exceeds the cost of being wrong: this
decision is cheap to revisit before API design begins, and expensive to keep
open.

**Consequences:**
- *Positive:* Unblocks API, MCP, and SDK design. Gives a concrete first-user
  profile to design against.
- *Negative:* Built on inferential rather than direct evidence.
- *Newly constrained:* API ergonomics and SDK quality become first-order
  concerns rather than later polish.
- *Revisit when:* direct user research becomes possible, or before finalising
  the API surface in `07_api_mcp` — whichever comes first.

**Evidence:** `../research/summaries/002-scope-users-and-dialect.md`

---

## DEC-003 — Adopt the existing model layer; build primitives, evaluation, and integration

**Decision ID:** DEC-003 · **Date:** 2026-07-29 · **Status:** Accepted

**Decision:**
Adopt existing Tigrinya models — principally the GeezLab / `fgaim` stack — as
the default foundation for language modelling, embeddings, POS, and NER.
Concentrate our own build effort on **(a)** the primitives layer (Ge'ez
normalisation, tokenization, morphology), **(b)** the evaluation harness, and
**(c)** the integration surface (API, MCP server, SDKs).

**Context:**
The ecosystem scan found substantially more existing Tigrinya capability than a
"low-resource language" framing suggests. A single group has published a
coherent stack including `tiroberta-bi-encoder`, an Apache-2.0,
`sentence-transformers`-compatible embedding model at 124.6M parameters.

At the same time, the scan found **no** Tigrinya API, MCP server, or SDK, and no
production-ready morphology or morphology-aware tokenization service. The stack
has gaps at the bottom (Layer 0) and the top (Layer 5), not in the middle.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Build everything from scratch | Full control | Duplicates existing work; violates P-1 outright |
| B | Adopt existing models, build primitives + evaluation + integration | Fast; cheap; fills the real gap; no training needed | Depends on one group; licence exposure |
| C | Wrap commercial APIs | Fastest to a demo | No cost control; fails A-001; does nothing for the primitives gap |
| D | Fine-tune one large multilingual model for everything | Conceptually simple | No evidence it serves the primitives; conflicts with P-2; GPU cost |

**Chosen:** Option B.

**Reason:**
Option B is what **P-1** and **P-2** require once the artefacts are known to
exist. It is also the cheapest path: the candidate models are ~124M parameters
and CPU-servable, consistent with **P-6** and **A-008**. Most importantly, it
directs our limited effort at the layer nobody has built, which is both the real
gap and our only plausible differentiator. Options A and D would spend months
re-creating a middle layer that already exists.

**Consequences:**
- *Positive:* No model training required to reach a useful platform. Fast route
  to a first capability. Effort concentrated where it is differentiating.
- *Negative:* **Concentration risk** — significant dependence on one group's
  output. Mitigated by artefacts being downloadable and mostly openly licensed.
- *Accepted tradeoff:* We will not have "our own" models for some capabilities.
  That is the intended outcome of a reuse-first philosophy, not a shortfall.
- *Newly constrained:* **Licence resolution on the unlicensed `fgaim` models is
  now a blocking prerequisite** (P-9, A-009).
- *Revisit when:* licences prove unresolvable, or the models evaluate poorly
  outside their news-article training distribution.

**Evidence:** `../research/summaries/001-tigrinya-nlp-ecosystem-scan.md`

---

## DEC-004 — Support both Tigrinya varieties; evaluate and report them separately

**Decision ID:** DEC-004 · **Date:** 2026-07-29 · **Status:** Accepted

**Decision:**
The platform supports both the Eritrean and Ethiopian varieties of Tigrinya.
Evaluation is run **separately for each**, and **both scores are always
reported**. Aggregating them into a single "Tigrinya" number is prohibited.

**Context:**
Dialect scope sat open in `assumptions.md` and blocks data collection design.
The CoDET benchmark `[reported]` measures NLLB-3.3B at **COMET 0.82 on the
Ethiopian variety versus 0.80 on the Eritrean variety**. Speakers are split
roughly 60/40 Ethiopia/Eritrea, meaning millions of users sit on each side.
Corpus provenance is already skewed: `haddas-tigrinya-corpus` is explicitly
Eritrean while much other work is Ethiopian-sourced.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Both varieties, separate evaluation and reporting | Serves all users; makes the gap visible and fixable | Roughly doubles evaluation-set construction cost |
| B | Both varieties, single aggregate score | Cheaper evaluation | **Hides a measured, asymmetric gap** — under-serves Eritrean users invisibly |
| C | Pick one variety | Simplest | Excludes millions of speakers for no technical gain — the measured gap does not justify it |

**Chosen:** Option A.

**Reason:**
The measured gap is small enough that one model can plausibly serve both, so
Option C sacrifices a large user population for nothing. The decisive argument
is against Option B: because the gap is real, measurable, and asymmetric, a
single aggregate score would let quality degrade for Eritrean users while the
dashboard looked healthy. That is the exact failure `docs/benchmarks/metrics.md`
requires subset reporting to prevent, and here it is an equity problem rather
than merely a metrics problem.

**Consequences:**
- *Positive:* Both user populations are served and measured. Dialect regression
  becomes detectable.
- *Negative:* Evaluation-set construction cost roughly doubles.
- *Newly constrained:* Every dataset must record its dialect provenance. Every
  evaluation report must carry two numbers.
- *Revisit when:* evidence emerges that the varieties diverge far enough to need
  separate models — which would be a significant finding, not a routine update.

**Evidence:** `../research/summaries/002-scope-users-and-dialect.md`; CoDET,
arXiv 2305.17267 `[reported]`

---

## DEC-005 — FLORES-200 and TiQuAD as initial evaluation anchors

**Decision ID:** DEC-005 · **Date:** 2026-07-29 · **Status:** Accepted

**Decision:**
Build the first evaluation harness around **FLORES-200** (Tigrinya split, for
translation) and **TiQuAD** (for question answering and reading comprehension).

**Context:**
**P-4** requires evaluation before capability. Two credible Tigrinya evaluation
resources exist: FLORES-200, human-reviewed across 204 languages with a reported
~3K Tigrinya samples; and TiQuAD, human-annotated, CC-BY-SA-4.0, 10.6K QA pairs,
an ACL 2023 Outstanding Paper with a reported baseline F1 of 81% against
estimated human performance of 92%.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | FLORES-200 + TiQuAD | Both human-produced; TiQuAD openly licensed; published baselines exist | Neither covers retrieval, morphology, or correction |
| B | Build our own evaluation sets first | Exactly fits our capabilities | Months of work before anything can be measured |
| C | Use machine-translated benchmarks (e.g. `tigrinya-squad`) | Large and available | Silver-standard; unsuitable as ground truth |

**Chosen:** Option A, with Option B for the gaps as a later workstream.

**Reason:**
Option A gives a trustworthy, human-produced starting point immediately and
comes with published baselines, which means our numbers are comparable to
existing work from day one. Option C is disqualified for evaluation use —
machine-translated data cannot serve as ground truth. Option B remains necessary
for retrieval, morphology, and correction, where nothing was found, but it must
not block all measurement until it is done.

**Consequences:**
- *Positive:* Measurement can start immediately, against published baselines.
- *Negative:* No coverage yet for retrieval, morphology, spell, or grammar —
  these evaluation sets must be built (**G-2**).
- *Newly constrained:* **`fgaim/tigrinya-squad` (silver, machine-translated) must
  never be used as evaluation data.** It shares authorship and probable source
  overlap with TiQuAD — **contamination must be checked before TiQuAD is treated
  as held-out.**
- *Revisit when:* our own evaluation sets exist, or FLORES's Tigrinya split is
  shown to have quality problems (published corrections exist for some African
  languages — verify whether Tigrinya is affected).

**Evidence:** `../research/summaries/001-tigrinya-nlp-ecosystem-scan.md`

### Amendment — 2026-07-29 (same day, post-verification)

Three findings materially affect this decision's execution. The decision stands;
its operational detail changes.

1. **TiQuAD's test split is not public.** It is request-gated
   (`fitsum.gaim@kaist.ac.kr`) to prevent contamination from web-crawled
   training data. Public splits: train 4,452 / validation 934; test 1,122 held
   back. **We must complete the request process, or evaluate on validation and
   say so explicitly.** This is exemplary practice on their part, not a defect.
2. **Published baselines are lower than first recorded.** mBERT F1 58.6 / XLM-R
   F1 62.4 (validation) — **not the 81% originally cited.** Use 56–62 F1 as the
   reference range.
3. **TiQuAD is Eritrean-sourced** (Eritrean Ministry of Information; *Hadas
   Ertra*). Under DEC-004 this means our main QA anchor covers the **Eritrean**
   variety, and **Ethiopian-variety QA evaluation is an open gap** rather than a
   balanced pair. **TIGQA** (2.68K pairs, educational/textbook domain, arXiv
   2404.17194) is a candidate complement and should be assessed.
4. **Adopt TiQuAD's evaluation protocol exactly** — EM + token-level F1, max
   over references, official script for article normalisation — so our numbers
   are comparable to published work.

⚠️ **Licensing caveat (P-9):** TiQuAD's authors state they do not own the
copyright to the source news articles, which are used "under fair use principles
for academic research purposes only," with CC-BY-SA-4.0 applied on top. Academic
evaluation use is defensible; redistribution or use inside a commercial service
may not be. **Legal review required before any use beyond internal evaluation.**
Referred to `11_business`.

---

## DEC-006 — The minimum viable platform is the primitives layer, not translation

**Decision ID:** DEC-006 · **Date:** 2026-07-29 · **Status:** Accepted

**Decision:**
The minimum viable platform is **Ge'ez normalisation + tokenization +
morphological analysis + embeddings, behind an API, with a documented evaluation
harness.** Translation is explicitly **excluded** from the minimum platform.

**Context:**
The capability scope is wide and needs a starting point. The ecosystem scan
showed the stack has gaps at Layer 0 (primitives) and Layer 5 (integration),
while Layers 1–2 largely exist. Meanwhile Google Translate is an established
Tigrinya translation incumbent, `[reported]` outperforming open alternatives.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Primitives + embeddings + evaluation | Fills the real gap; unblocks everything above it; no training needed | Less visible than translation |
| B | Lead with translation | Highest visible demand | Strong incumbent; no advantage available; leaves the primitives gap unfilled |
| C | Lead with an end-user product | Demonstrable | Violates N-1 and N-2 |
| D | Lead with knowledge graph / RAG | Strategically interesting | Most dependency-heavy layer; no Tigrinya groundwork exists |

**Chosen:** Option A.

**Reason:**
Every capability above Layer 0 degrades if the primitives are wrong, usually in
ways that are hard to attribute back to their cause — so building anything else
first means building on an unmeasured foundation. Option A is also the only
option that requires no model training (**P-2**, **A-004**) and that every
identified first user (the keyboard products) could adopt immediately. Option B
was rejected as the *opening* move rather than as a capability: we should
measure against Google Translate before assuming we can improve on it.

**Consequences:**
- *Positive:* Fastest route to something genuinely useful. No training. Unblocks
  every downstream capability.
- *Negative:* Less immediately impressive than a translation demo.
- *Newly constrained:* HornMorpho's maintenance status becomes a critical-path
  risk, because morphology is now in the minimum platform.
- *Revisit when:* the primitives are shipped and measured, at which point
  capability priority is re-derived from `12_master_blueprint`.

**Evidence:** `../research/summaries/002-scope-users-and-dialect.md`

---

## DEC-007 — Consonant–vowel decomposition as the substrate beneath tokenization

**Decision ID:** DEC-007 · **Date:** 2026-07-29 · **Status:** Accepted

**Decision:**
Tokenization and morphological processing operate on an explicit
**consonant–vowel decomposition** of Ge'ez characters, not on raw Ge'ez
characters or bytes. A deterministic, losslessly reversible decomposition layer
sits beneath the tokenizer. Morpheme-aware vocabulary construction layers on top;
a standard subword tokenizer on raw Ge'ez is retained as a measured baseline.

**Context:**
Tigrinya morphology is **templatic and agglutinative simultaneously**.
Triconsonantal roots interleave with vowel patterns, so roots are
**discontinuous**. The Ge'ez script is an abugida in which each character encodes
a **consonant–vowel pair** as one indivisible unit (26 consonants × 7 vowel
orders ≈ 182 characters).

These two facts collide: templatic morphology operates on consonants and vowels
separately, while the script fuses them. **A morpheme boundary can therefore fall
inside a single Ge'ez character.** Researchers working on Tigrinya segmentation
already work around this by transliterating to Latin before segmenting, citing
character alteration at segmentation boundaries.

DEC-006 places tokenization and morphology in the minimum viable platform, so
this is the project's critical path.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Standard subword tokenizer on raw Ge'ez | Simplest; what most existing Tigrinya tokenizers do | **Structurally cannot** express discontinuous roots or sub-character boundaries |
| B | Transliterate to Latin, segment, map back | What researchers actually do; proven in practice | Scheme choice becomes load-bearing; round-trip loss risk |
| C | **Explicit consonant–vowel decomposition of Ge'ez** | Deterministic and trivially reversible; exploits the regular 26×7 grid; no external dependency; yields transliteration as a by-product | Must be built; assumes the grid is regular in practice |
| D | Byte-level BPE | No preprocessing | UTF-8 bytes are an encoding artefact carrying no linguistic decomposition — does not solve the problem |

**Chosen:** Option C as the substrate, with morpheme-aware vocabulary above it
and Option A retained as the baseline.

**Reason:**
Option A and Option D fail on representational grounds — not performance
grounds — and no amount of tuning fixes a representation that cannot express the
target. Option B works and is the empirical precedent, but imports
transliteration-scheme ambiguity and round-trip loss risk. Option C obtains the
same benefit deterministically by exploiting Ge'ez's regular structure, and
produces the transliteration capability our scope needs anyway as a by-product.

**Consequences:**
- *Positive:* Morpheme boundaries become expressible. Transliteration comes free.
  Token efficiency gains reduce inference cost (**P-6**) regardless of accuracy.
- *Negative:* A layer we must build and maintain. Adds a preprocessing stage to
  every text path.
- *Accepted tradeoff:* Slightly more complexity than a stock tokenizer, in
  exchange for a representation that can express the language's morphology.
- *Newly constrained:* **Transliteration is now core infrastructure**, not a
  peripheral user-facing feature. Its priority rises accordingly.
- *Important limit:* **Do not claim downstream accuracy gains from this.**
  Evidence is mixed — MoVoC found no significant MT gain from morpheme-aware
  vocabulary, while arXiv 2509.20209 found substantial gains from a custom
  tokenizer plus embedding initialisation. The reliable, defensible benefits are
  token efficiency and linguistic fidelity. Accuracy must be measured.
- *Revisit when:* a corpus survey shows Ge'ez decomposition is messier in
  practice than the 26×7 grid implies — Option B is the fallback.

**Evidence:** `../research/summaries/003-morphology-script-and-tokenization.md`

---

<!--
Append new decisions below this line. Copy the format from
../research/templates/decision_template.md and update the Index table above.
-->
