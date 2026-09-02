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
| DEC-007 | 2026-07-29 | Consonant–vowel decomposition as the substrate beneath tokenization | Accepted — **amended twice; token-efficiency rationale REFUTED 2026-08-03** |
| DEC-008 | 2026-07-29 | Mandatory contamination screening; unlicensed data quarantined | Accepted |
| DEC-009 | 2026-08-03 | chrF primary translation metric; BLEU for comparability only | Accepted — **caveat added by Amendment 1** |
| DEC-010 | 2026-08-03 | Evaluation results are variety-scoped; no cross-variety aggregate | Accepted |
| DEC-011 | 2026-08-10 | MADLAD-400-3B is the translation baseline; NC-licensed models are research-only | Accepted |
| DEC-012 | 2026-08-10 | Library-first; services are thin wrappers over libraries | Accepted |
| DEC-013 | 2026-08-10 | Tier by resource profile; never co-locate tiers in one process | Accepted |
| DEC-014 | 2026-08-10 | CTranslate2 is the single model runtime | Accepted |
| DEC-015 | 2026-08-13 | Screening is executable and mandatory; datasets carry a screening record | Accepted |
| DEC-016 | 2026-08-13 | Every experiment emits a machine-checkable artefact | Accepted |
| DEC-017 | 2026-08-17 | Training gated behind an adaptation ladder and measured triggers; from-scratch foreclosed | Accepted |
| DEC-018 | 2026-08-17 | CI enforces the machine-checkable rules in the decision log | Accepted — ⚠️ **workflow written, NOT YET ACTIVE (A-15)** |
| DEC-019 | 2026-08-17 | Tier 2 deployment mode set by measured duty cycle, not fixed in advance | Accepted |
| DEC-020 | 2026-08-17 | Licence by artefact class: Apache-2.0 code, CC-BY-4.0 docs, inherit for data | Accepted — closes A-12 |
| DEC-021 | 2026-08-17 | Extend evaluation anchors to the MVP primitives; next research is Tier 0 evaluation | Accepted |
| DEC-022 | 2026-08-18 | API response contract: code-point offsets, surface verbatim, variety label, tier disclosed | Accepted — **alignment clause corrected by DEC-023** |
| DEC-023 | 2026-08-18 | Primitive evaluation is intrinsic-first; alignment is word-level (corrects DEC-007, DEC-022) | Accepted — **evidence corrected by Amendment 1** |
| DEC-024 | 2026-08-19 | Load-bearing figures are registered; retired figures are machine-checked | Accepted |
| DEC-026 | 2026-08-23 | Embedding evaluation is intrinsic-first with a mandatory lexical baseline; cross-lingual retrieval needs a different model class | Accepted |

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

### Amendment — 2026-07-29 (same day, post-experiment)

**The decision's direction is unchanged; its implementation is now "buy, not
build", and its reversibility requirement is dropped as unachievable.**

`experiments/001-epitran-geez-decomposition/` measured **Epitran**
(`epitran` 1.35.2, MIT-Modern-Variant, last release 2026-06-18) against this
decision's four requirements. It ships **`tir-Ethi`**, a dedicated Tigrinya map.

| Requirement | Result |
| --- | --- |
| Decomposition | ✅ ካተበ → `katəbə` → consonants `[k,t,b]`, vowels `[a,ə,ə]`. The discontinuous root is extractable |
| Coverage | ✅ 384/384 core Ethiopic characters produce **non-empty** output — ⚠️ **refined 2026-08-18:** only **310** are transliterated to phonemes; 74 pass through, of which **19 are real characters** (16 syllables + 3 combining marks). Non-core blocks are **entirely** unmapped. See DEC-022 |
| Tigrinya-specific | ✅ 59/384 (15.4%) differ from Amharic, and correctly (pharyngeal ħ, uvular q) |
| **Lossless reversibility** | ❌ **384 chars → 362 outputs; 22 collisions** |

**1. Adopt Epitran rather than building the layer.** This decision originally
specified building a decomposition layer. That was a **P-1 failure — the
previous session did not check package registries before assuming "build."**
Epitran does it already, with better Tigrinya phonology than we would have
encoded unaided, under a clean licence.

**2. The reversibility requirement is withdrawn.** It cannot be met, and it
should not be. The 22 collisions are exactly the historically redundant Ge'ez
homophone pairs (ሀ/ኀ → `hə`, ሠ/ሰ → `sə`) — characters that are pronounced
identically in modern Tigrinya but written differently. **That is the
orthographic-variation problem, and the collapse normalises it for free.**

**3. Therefore: dual representation.** One representation cannot serve both
matching and output.

- **Surface form** — original Ge'ez, preserved verbatim, always. Source of truth
  for anything returned to a user.
- **Analysis form** — Epitran `tir-Ethi` decomposition. Used for matching,
  morphological analysis, retrieval, and embeddings. **Lossy by design; that
  loss is normalisation.**
- **Alignment offsets** maintained between them, so analysis results map back
  onto surface spans. ⚠️ **Corrected 2026-08-18 (DEC-023): these are WORD-LEVEL
  spans, not character offsets.** Character-level alignment is **measurably
  impossible** — only 23.89% of words align, because epitran resolves epenthetic
  `ɨ` from cross-character context supplying 16.3% of output symbols.
- **Never reconstruct surface text from the analysis form.**

**Revised consequences:**
- *Positive:* Cost of the substrate drops from days–weeks to `pip install`.
  Orthographic normalisation partly comes free. Net **less** work than before.
- *Negative:* A dependency on one external map for a core primitive. Mitigated
  by MIT licensing, small reviewable tables, and keeping the raw-Ge'ez baseline.
- *New work created:* the **surface↔analysis alignment layer** — now the only
  part of this we build.
- *New risk:* **we cannot currently detect systematic errors in `tir-Ethi`.**
  It would be silently wrong everywhere downstream. **Native-speaker validation
  is required before anything ships user-facing.**
- *Measured cost input:* **1.97× mean symbol expansion**, which feeds tokenizer
  fertility budgeting.

**Evidence:** `../research/summaries/004-geez-tooling-survey.md`;
`experiments/001-epitran-geez-decomposition/`

### Amendment 2 — 2026-08-03: the token-efficiency rationale is refuted

**`experiments/002-tokenizer-fertility/` measured the claim this decision rested
on. It does not hold. Decomposition makes token fertility *worse*, not better.**

BPE trained on identical text at matched vocabulary sizes, evaluated on held-out
text — the only variable being whether the input was decomposed:

| | char-level (V=2000) | byte-level (V=2000) |
| --- | ---: | ---: |
| Raw Ge'ez | **2.261** tokens/word | **3.106** tokens/word |
| Epitran-decomposed | 2.432 | 3.417 |
| **Δ** | **+0.171 (worse)** | **+0.312 (worse)** |

**Raw Ge'ez won 10/10 configurations and 5/5 rotating folds** (mean Δ +0.190,
≈ **8% worse** at realistic vocabulary size).

**Why.** Ge'ez is *already* a compression scheme — each character encodes a
consonant+vowel pair in one codepoint, which is exactly the structure BPE would
otherwise have to learn. Decomposition discards it, doubles sequence length
(**1.957×**, measured), and makes BPE spend its merge budget rebuilding the
syllables the script supplied for free. The smaller phoneme inventory
(155 → 35 symbols, also measured) does not compensate.

**What this changes:**

1. **Do not decompose for tokenization.** The tokenizer operates on **raw Ge'ez**.
   Option A — previously the baseline — is now the default for tokenization on
   measured grounds.
2. **The 1.97× cost figure is confirmed** at 1.957× on running text (median
   exactly 2.000×). That number was right; what it bought was not.
3. **The decision's direction survives for morphology, but demoted to untested.**
   Decomposition may still be correct for morphological *analysis*, where a
   phoneme representation is the point rather than a means to compression. That
   claim is now explicitly **unproven** — it must not be cited as settled, and it
   needs its own experiment.
4. **The surface↔analysis alignment layer is no longer on the critical path.**
   It was to be built for a tokenizer that will not use it. Build it when
   morphological analysis needs it, not before.

**Cost/benefit as it now stands:** decomposition costs 1.957× expansion **and**
~8% worse fertility, in exchange for a morphological-alignment benefit that has
not been demonstrated. That is not a trade worth making until the benefit is
measured.

**Limits of the refutation, stated plainly:** the corpus was **991 words** —
egress policy blocks bulk download (see `ACTIONS.md` **A-09**). The *direction* is
robust (10/10 configs, 5/5 folds, with an explicable mechanism); the *magnitude*
is indicative only. The char-level gap narrows with vocabulary before plateauing,
so a crossover at production scale is not excluded — but there is no evidence for
one, and at byte level the gap does not narrow at all.

**Evidence:** `experiments/002-tokenizer-fertility/`

---

## DEC-008 — Mandatory contamination screening; unlicensed data quarantined

**Decision ID:** DEC-008 · **Date:** 2026-07-29 · **Status:** Accepted

**Decision:**
Every dataset is screened for evaluation contamination **before** it enters any
training or tuning use, and datasets without a usable licence are **structurally
quarantined** to research-only use — never present in a shipped artefact.

**Context:**
The corpus inventory (`03_data_strategy/001`) measured what is actually
available and found two problems that are not about volume.

**First, probable contamination.** `farefaine/tigrinya-pretraining` is titled
*"Tigrinya Raw Pretraining Sources"* and tagged for pretraining, but its schema
is `id, question, context, answers, article_title, context_id` — TiQuAD's
extractive-QA schema, field for field — and its validation split is **exactly
934 rows, matching TiQuAD's validation split.** TiQuAD is our evaluation anchor
under DEC-005. Pretraining on this dataset would silently invalidate it.

**Second, licensing.** Of 1,519,253 rows measured, **~99% carry no stated
licence.** Cleanly licensed: 15,053 documents.

Neither problem is visible from a dataset card. Both were found only by querying
actual schemas and row counts.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Screen every dataset; quarantine unlicensed data structurally | Protects evaluation validity and licence position | Ongoing cost per dataset; reduces immediately usable data to ~15K documents |
| B | Screen only datasets that look like evaluation data | Cheaper | **The failure case here was a dataset that did not look like evaluation data.** Would have missed it |
| C | Trust dataset cards and metadata | Free | Cards were wrong on 2 of 4 sampled; size tags off by up to ~20× |
| D | Use everything, resolve later | Fastest | Retrofitting licence compliance means discarding trained artefacts; P-9 violation |

**Chosen:** Option A.

**Reason:**
Option B is disqualified by the very case that motivated this decision — the
contaminated dataset was labelled "pretraining sources", so a
looks-like-evaluation heuristic would have skipped it. Option C is disqualified
by measurement: metadata was wrong on half the sample. Option D trades a small
present saving for the possibility of discarding trained artefacts later, and
violates **P-9**.

Contamination is the one form of sloppiness that **invalidates everything
downstream of it** while leaving no visible symptom — the dashboard still shows
a number. That asymmetry justifies paying the screening cost on every dataset.

**Consequences:**
- *Positive:* Evaluation validity is protected. Licence position stays defensible.
  Screening is automatable, so the per-dataset cost falls over time.
- *Negative:* Immediately usable cleanly-licensed data drops to **15,053
  documents**. That is a real constraint on what can be built now.
- *Accepted tradeoff:* We will be slower than projects that skip this, and our
  numbers will be trustworthy where theirs may not be.
- *Newly constrained:* No dataset enters training use without a screening record.
  Unlicensed data requires structural separation — a directory convention is not
  sufficient.
- *Corollary for DEC-005:* **Externally reported Tigrinya QA scores must be
  treated as suspect** until the models behind them are shown to be
  uncontaminated. This affects how we read published baselines.
- *Revisit when:* screening finds nothing across many datasets, or tooling makes
  it near-free.

**Evidence:** `../research/summaries/005-corpus-inventory-and-contamination.md`

✅ **CONFIRMED same day.** The row-level check that was blocked has since been
run. `dataset_preview` on the validation split returned `article_title`
**ሃብቶም ክብረኣብ (ሞጀ)** with a context passage **identical to the sample entry
TiQuAD publishes on its own dataset card**, carrying three answer annotations
per question — TiQuAD's documented validation-set convention.

**The contamination is verified, not suspected.** The earlier hedge is
withdrawn. DEC-008 was justified by the possibility; it is now justified by
fact — and the DEC-005 corollary hardens accordingly: **any published Tigrinya
model trained on this corpus has a TiQuAD score that cannot be trusted.**

Reporting this upstream to the `farefaine` maintainer is now an action item
(**G-11**).

---

## DEC-009 — chrF is the primary translation metric; BLEU is reported for comparability only

**Decision ID:** DEC-009 · **Date:** 2026-08-03 · **Status:** Accepted

**Decision:**
**chrF** is the primary metric for translation and any surface-generation
capability. **BLEU is always reported alongside it**, never alone, and is
labelled as **not comparable across languages**. Neither is ever reported without
the other, and no capability decision rests on BLEU alone.

**Context:**
`docs/benchmarks/metrics.md` held this question open deliberately: standard
metrics were validated on high-resource, morphologically simple languages, and
whether they transfer to Tigrinya was unknown. DEC-005 named FLORES-200 as the
translation anchor without naming a metric. Literature on the question is
egress-blocked, so it was **measured** instead — Experiment 003, on FLORES+
parallel data where the same 30 sentences exist in both languages.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | BLEU primary | Universal; every published Tigrinya result uses it | Measurably harsher on Tigrinya; least informative exactly where low-resource systems sit |
| B | **chrF primary, BLEU alongside** | Degrades gracefully; advantage grows as quality falls; tokenization-independent | Less widely reported; parameters must be pinned |
| C | COMET primary | What NLLB's published Tigrinya numbers use | **Untestable here** — model downloads egress-blocked; adopting an unvalidated learned metric repeats the error this decision exists to avoid |
| D | Drop BLEU entirely | Avoids a biased metric | Overreaction; forfeits comparability with all published work |

**Chosen:** Option B.

**Reason:**
Measured, **BLEU carries only a ~1.08× harshness penalty** on Tigrinya — real but
about half the size the standard warning implies, and not grounds for discarding
it. What decides the matter is *how the metrics behave as quality falls*:

| Near-miss corruption | BLEU kept | chrF kept | ratio |
| ---: | ---: | ---: | ---: |
| 10% | 77.8% | 91.6% | 1.18× |
| 20% | 56.5% | 82.5% | 1.46× |
| 30% | 41.5% | **74.9%** | **1.80×** |

**chrF's advantage widens precisely where low-resource systems operate.** With a
40M-token data ceiling (**A-002**), our systems will live in the weak regime for
a long time, and the metric should be chosen for that regime. chrF is also
immune to the tokenization instability Experiment 002 exposed for Ge'ez.

Option D is rejected because the penalty is modest and BLEU is what every
published Tigrinya result reports; dropping it would make our numbers
incomparable to the field for no measured gain.

**Consequences:**
- *Positive:* A metric chosen on measured behaviour rather than convention.
  The BLEU bias is now **quantified**, so it can be stated rather than feared.
- *Negative:* Two metrics to report and reconcile; chrF parameters
  (char n-gram order, word n-gram order, β) become load-bearing and must be pinned.
- *Newly constrained:* **Cross-language BLEU comparisons are forbidden without
  stating the ~8% penalty.** Comparing our Tigrinya BLEU to an English BLEU
  without that caveat is now a documented error, not a judgement call.
- *Important limit:* **COMET remains unvalidated for Tigrinya** and is what
  NLLB's published numbers use — we cannot compare against them until this is
  resolved. Recorded as an open question, not quietly ignored.
- *Revisit when:* the full 1,012-sentence devtest can be measured (**A-09**), or
  COMET becomes testable, or real MT output replaces synthetic perturbation.

**Evidence:** `experiments/003-metric-validity/`;
`../research/summaries/006-metric-validity-and-harness.md`

---

### Amendment 1 — 2026-08-23: the interval itself stops being trustworthy below ~n=5

**DEC-009 requires confidence intervals on small evaluation sets** because a
point estimate hides how little is known. `experiments/007-harness-fidelity/`
measured whether the interval actually delivers that, over 20 random subsets per
size:

| n | Median 95% chrF CI width |
| ---: | ---: |
| 30 | **2.69** |
| 20 | 3.06 |
| 10 | 3.87 |
| **5** | **5.02** |
| **3** | **4.59** ⚠️ *narrower than n=5* |

Widening holds from 30 down to 5 and then **reverses**. Bootstrap resampling of
3 items has only **27 distinct multisets**, many yielding identical scores, so
the interval cannot express the uncertainty it should.

**The requirement stands; a caveat is added.** Report intervals as DEC-009
already requires, and **do not treat an interval below roughly n=5 as
meaningful** — it understates uncertainty exactly where uncertainty is greatest.
This is live rather than theoretical: our evaluation anchor is **30 sentences**,
so any per-variety or per-domain breakdown of it lands in that range.

*(Mechanism inferred from the resample-space arithmetic, not independently
proven.)*

**Evidence:** `experiments/007-harness-fidelity/` `[verified]` 2026-08-23

---

## DEC-010 — Evaluation results are variety-scoped; no cross-variety aggregate

**Decision ID:** DEC-010 · **Date:** 2026-08-03 · **Status:** Accepted

**Decision:**
Every evaluation result carries a **variety label** — Eritrean, Ethiopian, or
**unknown**. Scores from anchors of different varieties are **never aggregated
into a single "Tigrinya score."** Where the variety of an evaluation set is
unresolved, it is labelled `unknown` rather than assumed.

**Context:**
**DEC-004** commits us to supporting both varieties and reporting them
separately. **DEC-005** named two anchors without checking whether they are in
the same variety. They appear not to be:

- **TiQuAD** — `[verified]` Eritrean-sourced (Eritrean Ministry of Information,
  *Hadas Ertra*).
- **FLORES+ Tigrinya** — carries Ethiopian markers: `ፀ`-series tsade ×8,
  `አ` alef ×8, `እስካብ` ×2, `ብሄራዊ` ×1, `እንትኸውን` ×1, with **zero Eritrean
  counterparts** among the diagnostic forms.

Two claims of different strength, kept separate:
1. `[verified]` — the FLORES+ set is **orthographically inconsistent with
   itself**; both tsade series and both alef forms appear in one file. This is
   measurement.
2. `[strong signal]` — it leans Ethiopian. The author is not a native speaker and
   the sample is 30 sentences. **Native-speaker confirmation required.**

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Report one aggregate Tigrinya score | Simple; one headline number | Averages two varieties; the number describes nothing that exists |
| B | **Variety-scoped reporting, no aggregate** | Honest; satisfies DEC-004; makes variety gaps visible | More numbers to report; no single headline figure |
| C | Pick one variety and evaluate only it | Simplest | Contradicts DEC-004 and abandons half the speaker population |
| D | Wait for native-speaker confirmation before deciding | Maximum rigour | Blocks the harness indefinitely on an unscheduled dependency |

**Chosen:** Option B.

**Reason:**
Option B is correct **whether or not the Ethiopian attribution is confirmed** —
which is why it does not wait on Option D. If the signal holds, B prevents a
genuinely misleading aggregate. If it turns out FLORES+ is Eritrean after all,
B costs only a redundant label. **An asymmetric bet with a cheap downside.**

Option A is rejected for the reason **DEC-004** exists: an aggregate across
varieties reports a number for a language nobody speaks. Option C abandons users
we have committed to serving.

**Consequences:**
- *Positive:* Variety gaps become **visible rather than averaged away** — which is
  the measurement DEC-004 needs and nobody currently publishes.
- *Negative:* No single headline score. External comparisons get harder, because
  published Tigrinya results generally do not state variety.
- *Newly constrained:* Every evaluation set must be **variety-audited before
  use**, extending the DEC-008 screening gate — which now covers contamination,
  licence, quality, and variety.
- *New work created:* native-speaker variety audit of both anchors (**A-13**).
- *Important limit:* `unknown` is a real and expected label. **Most existing
  Tigrinya resources do not state their variety**, and guessing would defeat the
  purpose.
- *Revisit when:* native-speaker confirmation arrives, or an anchor's provenance
  is documented upstream.

**Evidence:** `experiments/003-metric-validity/`;
`../research/summaries/006-metric-validity-and-harness.md`;
TiQuAD provenance from `../research/summaries/001-tigrinya-nlp-ecosystem-scan.md`

---

## DEC-011 — MADLAD-400-3B is the translation baseline; NC-licensed models are quarantined

**Decision ID:** DEC-011 · **Date:** 2026-08-10 · **Status:** Accepted

**Decision:**
**`google/madlad400-3b-mt` (Apache-2.0)** is the translation model for anything we
ship. **Models under non-commercial licences — including every NLLB variant — are
structurally quarantined to research and comparison use**, never present in a
shipped artefact. This extends **DEC-008**'s quarantine rule from *data* to
*models*.

**Context:**
Translation is the first capability cleared by **P-4**, because `08_evaluation`
delivered a validated metric for it (DEC-009) and for nothing else yet.

Three facts decide it, all `[verified]` from Hub metadata:

1. **No Tigrinya-specific MT model exists.** The `fgaim`/GeezLab stack has none;
   a `language:ti` + `translation` search returns nothing.
2. **Every NLLB variant is CC-BY-NC-4.0** — 600M, 1.3B, and 3.3B alike. NLLB is
   the model behind essentially every published Tigrinya MT number, including
   the COMET figures underpinning **DEC-004**, and has 28M downloads.
3. **MADLAD-400 is Apache-2.0 and covers `ti`** at 2.94B / 8.3B / 10.7B, with
   published GGUF quantisations.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | NLLB-600M | Smallest; the field's baseline; best-documented Tigrinya quality | ⛔ **CC-BY-NC-4.0** — unshippable under P-9/A-009 |
| B | **MADLAD-400-3B** | **Apache-2.0**; covers `ti`; GGUF published; 1.4 GB at Q4 | 4.8× NLLB-600M's parameters; **Tigrinya quality unmeasured** |
| C | MADLAD-400-7B / 10B | Presumably better quality | 3.9–5.0 GB at Q4 with **no measured justification**; strains A-008 |
| D | NLLB now, replace later | Fastest to a demo | The replacement never happens on schedule; by then API, evals, and docs assume it |
| E | Commercial API | No hosting | Already rejected in DEC-003 — fails A-001, no cost control |

**Chosen:** Option B.

**Reason:**
Option A is disqualified on licensing, not on merit. We are building
infrastructure others build on; shipping an NC-licensed model passes a
restriction to our users that they inherit without knowing it — the same failure
mode as unlicensed data, one layer up. **P-9** and **A-009** do not admit an
exception for a model that is merely very popular.

Option B is the only Apache-2.0 path that includes Tigrinya at a servable size.
The licence costs **4.8× the parameters** (615M → 2,940M) — stated plainly as a
real cost — but **A-008 survives**: MADLAD-3B is **1.4 GB at Q4**, quantisations
already exist, and it remains within commodity CPU serving.

Option D deserves naming because it is the tempting one. Deferring a licence
problem does not shrink it; it moves it to the point where the API, the published
evaluations, and the documentation all assume the model that has to be removed.

**Consequences:**
- *Positive:* A shippable translation path with a clean licence, decided before
  anything depends on it.
- *Negative:* **4.8× the parameters**, and less A-008 headroom than DEC-003
  assumed when it cited 124M-parameter models.
- *⚠️ Newly constrained:* **our production model and our comparison baseline are
  different models.** NLLB permits research use, so evaluating it for
  comparability is legitimate — but **"we match published Tigrinya MT quality"
  is unfounded unless both are measured on the same harness.** The DEC-009
  harness must run both.
- *New work created:* measure MADLAD-400-3B on Tigrinya. It appears **nobody
  has** — the ecosystem cites NLLB — so this is also a contribution (**G-11**).
- *Important limit:* **no quality measurement backs this decision.** It is made
  on licensing and size, which are verified, while MADLAD's Tigrinya quality is
  unknown and NLLB's is `[reported]`. If MADLAD proves materially worse, the
  choice is between a weaker shippable model and no shippable model — not
  between MADLAD and NLLB.
- *Also unmeasured:* **latency.** Memory is arithmetic; speed is an experiment
  that egress policy prevented (**A-09**).
- *Revisit when:* MADLAD is measured on Tigrinya; a permissively-licensed
  Tigrinya MT model appears; or legal review (**A-06**) clarifies whether an NC
  model licence reaches a commercial downstream product.

**Evidence:** `../research/summaries/007-translation-model-selection.md`;
Hub metadata `[verified]` 2026-08-10

---

## DEC-012 — Library-first: services are thin wrappers over libraries

**Decision ID:** DEC-012 · **Date:** 2026-08-10 · **Status:** Accepted

**Decision:**
Every capability is implemented as an **importable library first**. Services
(HTTP API, MCP server) are **thin wrappers** that import those libraries and add
transport, auth, and validation — **no capability logic lives only behind a
network call.**

**Context:**
**DEC-002** makes application developers the primary users; **P-6**/**A-008**
require low-volume economy; **P-11** and `CONTRIBUTING.md` require services to be
independently runnable and testable.

Tier 0 is the decisive case. Normalisation, tokenization, transliteration and
morphology are pure computation over small data (72 MB estimated here; **113.4 MB measured** once built — DEC-013, amended).

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Library-first, services wrap** | Zero serving cost at zero volume; developers `pip install`; trivially testable | Two distribution surfaces to maintain |
| B | Service-first, extract libraries later | One surface initially | Imposes infrastructure on developer users; network latency on microsecond ops; **the extraction never happens once services exist** |
| C | Services only | Simplest operationally | Primitives unusable without infrastructure — fails the users who most need them |

**Chosen:** Option A.

**Reason:**
**A library has zero serving cost at zero volume**, which no service topology can
match — and that is precisely what A-008 asks for. Requiring a running service to
normalise a string would impose an operations burden on the exact users DEC-002
names as primary, and would add network latency to operations measured in
microseconds.

Option B is named explicitly because it is the default drift. Once an API exists
and works, the library extraction is always next quarter's task.

**Consequences:**
- *Positive:* Primitives usable with **no infrastructure at all**. Services become
  thin and testable. P-11 independence is structural, not aspirational.
- *Negative:* Two distribution surfaces (packages and services) to version and
  document.
- *Newly constrained:* **Cross-service imports are now not merely a smell but
  unnecessary** — shared logic goes in a library, never another service.
- *Revisit when:* a capability genuinely cannot be expressed as a library — for
  example one requiring a persistent shared index that cannot be embedded.

**Evidence:** `../research/summaries/008-architecture-tiers-and-runtime.md`

---

## DEC-013 — Tier by resource profile; never co-locate tiers in one process

**Decision ID:** DEC-013 · **Date:** 2026-08-10 · **Status:** Accepted

**Decision:**
The platform is decomposed by **resource profile**, not by domain:

| Tier | Contents | Cumulative | Behaviour |
| --- | --- | ---: | --- |
| **0** | normalisation, tokenization, transliteration, morphology | **72 MB** *(estimate)* | always warm |
| **1** | + embeddings | **191 MB** | warm |
| **2** | + translation | **1,593 MB** | lazily loaded; may scale to zero |

**Tiers are never co-located in a single process.** Model weights load lazily,
per tier, on first use.

⚠️ **Corrected 2026-08-18, on building Tier 0.** The 72 MB figure was arithmetic
from estimated component sizes. **Measured, Tier 0 is 113.4 MB — and that is
*without* morphology**, which the estimate included:

| Component | Marginal RSS |
| --- | ---: |
| normalisation | ~0 (pure `str.translate`) |
| tokenization (`tokenizers`) | **4.3 MB** |
| **transliteration (`epitran` → `panphon`)** | **107.4 MB** |

**One dependency is the entire budget** — `epitran` loads `panphon`'s
phonological feature tables on instantiation. Two consequences:

1. **Lazy loading is load-bearing, not tidiness.** Importing the package costs
   6.8 MB; the 107 MB is paid only if transliteration is used.
2. **Tier 0 is not homogeneous.** By this decision's own logic — tier by
   resource profile — normalisation+tokenization (~15 MB) and transliteration
   (~107 MB) are arguably different tiers. Lazy loading makes that a per-use
   cost rather than a resident one, so no re-tiering is proposed yet.

**DEC-019's derived figures shift**: the 22× standing-cost saving was computed
on 72 MB; at 113 MB it is closer to **14×**. The conclusion is unchanged —
tiering still dominates — but the number should not be quoted as 22×.

**Context:**
Measured footprints differ by **~150×** — normalisation is free, tokenization is
10 MB, and MADLAD-400-3B at Q4 (**DEC-011**) is 1,402 MB. Cold start differs by a
similar factor: seconds versus microseconds.

**A-008** requires low-volume affordability, which creates a bind for a 1.4 GB
model: kept warm it costs idle memory; scaled to zero it costs a multi-second
cold start on every request.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Decompose by domain | Matches how people describe capabilities | **Ignores the 150× spread** — the thing that actually determines cost and deployment |
| B | **Decompose by resource profile** | Each tier scales on its own economics; resolves the cold-start bind | Tier boundaries cut across domains, so they must be documented or they will be violated |
| C | One container for everything | Simplest to deploy | **1.6 GB resident to normalise a string**; multi-second cold start on microsecond operations |

**Chosen:** Option B.

**Reason:**
The cold-start tension is **only unresolvable if the tiers are merged**. Split,
each tier takes the deployment mode that suits it: Tier 0 is cheap enough
(113.4 MB measured; 72 MB was the estimate here)
to stay warm and serves the latency-sensitive calls; Tier 2 may scale to zero
because translation is a seconds-scale operation whose users already expect to
wait. **An architectural problem becomes a deployment parameter.**

Option C deserves naming because it is what convenience produces. The 150× spread
is the standing counter-argument.

**Consequences:**
- *Positive:* **DEC-006's minimum viable platform is Tier 0 + Tier 1 = 191 MB.**
  Adding translation is an 8.3× jump — now an explicit, visible boundary rather
  than a surprise.
- *Negative:* Tier boundaries cut across domain boundaries, so they are less
  intuitive and must be documented to survive.
- *Newly constrained:* **No single "do-everything" container**, and no capability
  may assume another tier is resident in-process.
- *Independent support for DEC-006:* that decision excluded translation from the
  MVP on gap-filling grounds; the cost arithmetic agrees for unrelated reasons.
- *Important limit:* **memory is arithmetic; latency is not measured.** No
  cold-start or throughput figure here is empirical (**A-09**).
- *Revisit when:* a capability appears that does not fit a tier, or measured cold
  start makes Tier 2 scale-to-zero untenable.

**Evidence:** `../research/summaries/008-architecture-tiers-and-runtime.md`

---

## DEC-014 — CTranslate2 is the single model runtime

**Decision ID:** DEC-014 · **Date:** 2026-08-10 · **Status:** Accepted

**Decision:**
**CTranslate2 (MIT)** is the inference runtime for every model-backed capability.
Alternative runtimes require a recorded decision.

**Context:**
`[verified]` by installing CTranslate2 4.8.1 and inspecting its converter
registry — 42 supported HuggingFace architectures, including all three we need:

| Config | Model | Capability |
| --- | --- | --- |
| `T5Config` | `google/madlad400-3b-mt` | translation (DEC-011) |
| `M2M100Config` | `facebook/nllb-200-*` | comparison baseline (DEC-011) |
| `RobertaConfig` | `fgaim/tiroberta-bi-encoder` | embeddings (DEC-003) |

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **CTranslate2** | One runtime for all three; native int8; CPU-optimised; MIT | Less widely known than `transformers` |
| B | `llama-cpp-python` | Runs the published MADLAD GGUFs directly | **Does not serve the Roberta encoder** — two runtimes |
| C | `transformers` | Most familiar; no conversion step | Heaviest; no native int8 CPU path; poorest fit for A-008 |
| D | ONNX Runtime + Optimum | Mature; portable | Conversion for seq2seq is fiddlier; two-package story |

**Chosen:** Option A.

**Reason:**
One dependency, one quantisation story, one operational surface, MIT throughout.
**P-7 (prefer boring technology)** favours fewer moving parts, and Option B's
convenience for MADLAD is outweighed by needing a second runtime for embeddings.

**Consequences:**
- *Positive:* A single runtime and quantisation path across all model-backed
  capabilities; native int8 suits **A-008**.
- *Negative:* A **conversion step** before serving, and CTranslate2 is less
  familiar than `transformers` — so onboarding docs must cover it.
- *Important limit:* **support is verified; conversion is not.** The registry
  lists these architectures; actually converting MADLAD-3B and
  `tiroberta-bi-encoder` is an experiment requiring the weights (**A-09**). If
  conversion fails, Option B plus `transformers` is the fallback — at the cost of
  two runtimes.
- *Revisit when:* conversion fails for a required checkpoint, or GPU serving
  becomes relevant.

**Evidence:** `../research/summaries/008-architecture-tiers-and-runtime.md`;
CTranslate2 converter registry inspected 2026-08-10 `[verified]`

---

## DEC-015 — Screening is executable and mandatory; datasets carry a screening record

**Decision ID:** DEC-015 · **Date:** 2026-08-13 · **Status:** Accepted

**Decision:**
The **DEC-008** gates are implemented as
`scripts/data_processing/screen_dataset.py` and are **mandatory**. No dataset
enters training, tuning, or evaluation use without a committed, machine-readable
**screening record**. The four gates are **licence**, **quality**, **variety**,
and **contamination**.

**Context:**
DEC-008 established the policy in July. Measured on 2026-08-13: it mentions
screening **seven times**, `scripts/data_processing/` contained **zero files**,
and screening logic had been **reimplemented in all three experiment scripts,
differently each time**.

**A gate that exists only in prose is not a gate.** Every dataset this project
touched was screened by hand, inconsistently, by whoever happened to be looking.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Keep screening as written policy | No work | **Measurably does not happen** — three ad-hoc reimplementations, zero enforcement |
| B | **Executable gates + committed record** | Enforceable; consistent; auditable; CI-wirable | Must be maintained; thresholds need tuning |
| C | Manual checklist per dataset | Cheap; flexible | Same failure as A with extra ceremony |

**Chosen:** Option B.

**Reason:**
The gap between DEC-008's intent and its practice was total, and the cause was
the absence of a mechanism rather than any disagreement about the policy.

Two design choices are deliberate and load-bearing:

- **Licence is asserted, never detected.** A licence is a legal fact about a
  dataset, not a property of its bytes. The tool records what is declared and
  checks it against the usable set; it never guesses.
- **Contamination fails closed.** Supplying no evaluation set is a **FAIL**, not
  a pass. **Silence must never read as clearance** — that is precisely the
  failure mode DEC-008 exists to prevent.

Validated against known results including a **positive control**: screening an
evaluation set against itself detects **652 shared 8-grams**. Without that
control, "no contamination found" would be indistinguishable from a broken
detector.

**Consequences:**
- *Positive:* Screening is consistent, auditable, and CI-wirable. The three
  ad-hoc implementations can collapse into one.
- *Negative:* A tool to maintain, with thresholds (currently 0.1% foreign
  characters) tuned on a small sample and likely to need revision.
- *Newly constrained:* **A dataset without a committed screening record may not
  be used.** This applies retrospectively — existing inventory needs records.
- *Important limits:* the quality gate detects **mojibake, not meaning**; the
  column-scramble signal is a **review flag, not a verdict**, because separating
  scrambled columns from unusual prose is not reliably automatable; the variety
  gate **never returns a verdict**, labelling `unknown` pending **A-13**; and
  contamination detection is **exact-match n-gram overlap**, which catches copied
  text but not paraphrase or translation.
- *Revisit when:* thresholds misfire on a real dataset, or paraphrase
  contamination becomes a live concern.

**Evidence:** `../research/summaries/009-pipeline-without-training.md`;
validation runs `[verified]` 2026-08-13

---

## DEC-016 — Every experiment emits a machine-checkable artefact

**Decision ID:** DEC-016 · **Date:** 2026-08-13 · **Status:** Accepted

**Decision:**
An experiment is not complete until it writes a **machine-readable results
artefact** (`results.json`) alongside its prose. Re-running an experiment must
reproduce that artefact **byte-identically**, and a mismatch is a finding to
investigate rather than a file to overwrite.

**Context:**
Re-running all three experiments and byte-comparing on 2026-08-13:

| Experiment | Artefact | Byte-identical |
| --- | --- | --- |
| 001 — epitran | ❌ **none** | **cannot be checked** |
| 002 — fertility | ✅ | ✅ |
| 003 — metrics | ✅ | ✅ |

**P-5 holds for 002 and 003 and cannot be evaluated for 001**, whose results
exist only as prose. **DEC-007's amended form rests on Experiment 001's
numbers** — and if `epitran` changed behaviour, nothing would detect it.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Prose results only | Fast to write | Undetectable drift; P-5 unverifiable — the measured state of Experiment 001 |
| B | **Mandatory machine-readable artefact** | Drift detectable; P-5 checkable; regression-testable | Slight authoring overhead |
| C | Full experiment-tracking system | Rich metadata | Far too heavy for three experiments; would be abandoned (see DEC-001's reasoning) |

**Chosen:** Option B.

**Reason:**
The measured evidence is that **reproducibility came from making the artefact
mandatory, not from intending to be careful.** Experiments 002 and 003 reproduce
exactly because they were written after the practice existed; 001 does not
because it predates it. The discipline works, and it works structurally.

Option C is rejected for the reason DEC-001 rejected heavy process: it would be
abandoned within weeks at this scale.

**Consequences:**
- *Positive:* Dependency drift becomes detectable. Experiments become regression
  tests for the libraries they depend on.
- *Negative:* Minor authoring overhead per experiment.
- *Newly constrained:* An experiment without an artefact is **incomplete**;
  `CONTRIBUTING.md` and the experiment template both need this.
- *Debt created:* **Experiment 001 needs a `results.json`** — DEC-007 depends on
  numbers nothing currently re-checks.

### Amendment 1 — 2026-08-19: experiments that measure time cannot be byte-identical

**The rule as written assumes every experiment is deterministic.** Experiment
006 measures latency, and no timing measurement reproduces byte-identically —
so under the original wording it would either fail CI forever or force the
timings out of the artefact, which defeats the point of having one.

**Amended rule.** `results.json` must declare `"deterministic": true|false`.

| Declared | CI requires |
| --- | --- |
| `true` (default; omitted counts as true) | re-runs and **byte-compares**, exactly as before |
| `false` | re-runs, requires **exit 0 and an artefact**; does **not** byte-compare |

**The cost, stated plainly: a non-deterministic experiment gets no drift
detection.** The reproducibility job is currently the only thing that would
catch `epitran` or `tokenizers` changing behaviour, and an experiment that opts
out is opting out of that too. So the flag is **not** a convenience for
experiments that are merely awkward to make deterministic — it is only for
those measuring a genuinely variable quantity, and their numbers are
**indicative of the host that produced them**, never portable.

Making CI gate on a *verdict* derived from timings was considered and rejected:
a loaded shared runner would flip it, and a check that fails for reasons
unrelated to the code is a check people learn to ignore — which is the DEC-008
failure this rule exists to prevent.

**Evidence:** `experiments/006-tier0-latency/` `[verified]` 2026-08-19
- *Revisit when:* experiments become numerous enough that a real tracking system
  earns its cost.

**Evidence:** `../research/summaries/009-pipeline-without-training.md`;
re-run and byte-comparison `[verified]` 2026-08-13

---

## DEC-017 — Training is gated behind an adaptation ladder and measured triggers

**Decision ID:** DEC-017 · **Date:** 2026-08-17 · **Status:** Accepted

**Decision:**
Model training is reached only by climbing an **adaptation ladder**, cheapest
rung first, and only after a **measured** deficit against a pre-committed
threshold. **Training from scratch is foreclosed.**

| Rung | Intervention | Training? | Blocked by |
| --- | --- | --- | --- |
| **0** | decoding config, prompting, beam/length tuning | No | nothing — **always first** |
| 1 | vocabulary / tokenizer adaptation | no gradients | nothing |
| 2 | **LoRA adapter** on the adopted model | 7.4M params | **parallel data (A-05)** |
| 3 | full fine-tune | 2,940M params | A-05 + hardware |
| 4 | from scratch | — | **foreclosed by A-002** |

**Context:**
**A-004** makes training a last resort and puts the burden of proof on whoever
proposes it. This decision makes that burden concrete, and audits what we could
actually do if the burden were met.

The audit produced the governing fact: ~~**we have zero cleanly-licensed
parallel training data.**~~

⚠️ **RETRACTED 2026-09-01 — this was false.** [HornMT](https://github.com/asmelashteka/HornMT) is **2,030 human-translated en–ti pairs under CC-BY-4.0**, now committed at `data/anchors/hornmt/`. The zero was measured behind an egress block that made GitHub unreadable; the corpus was public the whole time. DEC-017's conclusion is unchanged —
2,030 pairs is far below any training rung — but the premise as written was
wrong.
 The 1.4M en–ti pairs are unlicensed (**A-05**); FLORES+ and
TiQuAD are our evaluation anchors, so training on them is contamination
(**DEC-008**). Monolingual: 15,053 documents, both corpora carrying documented
defects.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Ladder with measured triggers** | Cheapest interventions tried first; training requires evidence; from-scratch closed once | Requires the harness to exist before any training |
| B | Train from scratch | Full control | **A-002's ~40M-token ceiling makes it impossible**, not merely expensive |
| C | Fine-tune now on available data | Fastest | The only sizeable parallel corpus is **unlicensed** (P-9/A-009); the licensed ones are our eval anchors |
| D | Full fine-tune as default adaptation | Familiar | 23× LoRA's memory for no measured benefit; fails A-008 |

**Chosen:** Option A.

**Reason:**
Rung 0 is not a formality — decoding parameters routinely move translation
quality more than expected, cost nothing, and are reversible. Nothing above it
should be entertained until rung 0 has been measured on the DEC-009 harness.

Where training is genuinely justified, **LoRA on a 4-bit base needs ~1.4 GB peak
memory against ~32.9 GB for a full fine-tune — ~23× less, and ~400× fewer
trainable parameters.** Under **A-008** that is the difference between renting
datacentre hardware and using a desktop, which decides the method.

Option B is foreclosed explicitly rather than left implicit, so it is not
re-proposed: **A-002's ceiling is the entire open Tigrinya corpus**, and our
lawful share is a fraction of it.

**Trigger conditions — all five required:**

1. **A measured deficit** on the DEC-009 harness against a **pre-committed**
   threshold. Not an impression of poor output.
2. **Rung 0 exhausted**, with the measurement recorded.
3. **Lawful data**, screened through DEC-015's gates.
4. **A stated evaluation plan** for the artefact, including regression detection
   (DEC-016).
5. **A named maintenance owner** — a trained model must be kept alive,
   re-evaluated, and eventually retrained.

**No training without a number.** The failure mode guarded against is training
because it feels like progress.

**Consequences:**
- *Positive:* Training proposals now have an explicit, checkable bar. The cheap
  interventions get tried first, which is where the easy wins usually are.
- *Negative:* Adds process before any training can start — deliberately.
- *⚠️ Newly exposed:* **DEC-011's fallback is currently unavailable.** DEC-011
  adopted MADLAD-400-3B *without quality measurement*, so the likeliest trigger
  is that MADLAD proves inadequate — and we could not fine-tune our way out,
  because rung 2 is blocked on parallel data we do not lawfully have.
  **This re-frames A-05 from "cheapest high-value action" to "the insurance
  policy on DEC-011."**
- *Important limit:* **no training was run.** Memory is arithmetic; training time
  and resulting quality are not estimated, because they cannot be known without
  the weights (**A-09**).
- *Revisit when:* A-05 resolves, A-06 changes what is trainable, or the harness
  measures MADLAD.

**Evidence:** `../research/summaries/010-training-triggers.md`; licence audit and
PyPI metadata `[verified]` 2026-08-17

---

## DEC-018 — CI enforces the machine-checkable rules in the decision log

**Decision ID:** DEC-018 · **Date:** 2026-08-17 · **Status:** Accepted

**Decision:**
Every decision-log rule that **can** be checked mechanically **is**, in
`ci/verify.yml`.

> ⚠️ **Status: written and locally verified, NOT YET RUNNING.** GitHub refused
> the push — an app token cannot create `.github/workflows/` files without
> `workflows` permission. The workflow therefore sits at `ci/verify.yml` awaiting
> a one-command install (**A-15**).
>
> **Until then this decision is itself policy without mechanism** — exactly the
> failure it exists to prevent. Recorded loudly rather than left to be found
> later. A rule that is checkable and unchecked is treated
as a defect in the rule, not a matter of discipline.

Currently enforced: experiments reproduce byte-identically (**DEC-016**),
screening fails closed (**DEC-015**), every report has a summary (**DEC-001**),
summaries stay within two pages (**DEC-001**), every decision names rejected
alternatives (**CONTRIBUTING**).

**Context:**
**DEC-008 spent 15 days as policy with no mechanism and was silently ignored
the entire time** — screening reimplemented three times, differently, with zero
files in `scripts/data_processing/`. It was found by measurement in
`06_ml_pipeline`, not by anyone noticing.

Several newer rules sat in exactly that position: true, agreed, and enforced by
nobody.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **CI enforces checkable rules** | Rules stop depending on vigilance; drift becomes visible | A workflow to maintain; CI minutes |
| B | Rely on review discipline | No setup | **Already measured to fail** — DEC-008 is the evidence |
| C | Enforce everything, including judgement calls | Maximum rigour | Judgement is not mechanically checkable; would produce false failures and get disabled |

**Chosen:** Option A.

**Reason:**
The DEC-008 failure was not carelessness — it was a rule with nothing behind it.
The distinction that matters is **checkable versus not**: reproducibility, word
counts, and file correspondence are mechanical; "is this research good?" is not,
and Option C's attempt to automate the latter would produce noise until someone
switched the workflow off.

**Every check was run locally before commit** — 3 experiments byte-identical,
screening fails closed, corrupted sample still detected, 10 summaries under
limit, 17 decisions with rejected alternatives. CI that does not work is worse
than none.

**Consequences:**
- *Positive:* Rules stop depending on whoever is paying attention. **The
  reproducibility job doubles as a dependency regression test** — if `epitran`,
  `tokenizers`, or `sacrebleu` changes behaviour, CI catches it, which is the
  only thing standing between DEC-007's amended numbers and silent drift.
- *Negative:* A workflow to maintain; experiments must stay fast enough to run in
  CI.
- *Newly constrained:* **A new checkable rule arrives with its check**, or it is
  not a rule.
- *⚠️ Important limit:* **verified locally, not on a runner, and not yet
  installed.** The shell logic and tools were exercised by hand; GitHub Actions
  has never executed it, and the workflow is not in `.github/workflows/`. **This
  decision is unenforced until A-15 is done.**
- *Revisit when:* experiments grow too slow for CI, or a rule proves checkable in
  principle but not in practice.

**Evidence:** `../research/summaries/011-cost-model-and-enforcement.md`;
local verification `[verified]` 2026-08-17

---

## DEC-019 — Tier 2's deployment mode is set by measured duty cycle, not fixed in advance

**Decision ID:** DEC-019 · **Date:** 2026-08-17 · **Status:** Accepted

**Decision:**
Tier 2 (translation, 1.593 GB) is deployed **scale-to-zero or always-warm
according to measured duty cycle**, by this rule:

> Keep Tier 2 warm when sustained request rate exceeds the break-even
> `3600 / (cold_start_seconds + service_seconds)` per hour. Below it, scale to
> zero.

**Neither mode is fixed now**, because `cold_start_seconds` has never been
measured (**A-14**).

**Context:**
DEC-013 stated Tier 2 "may scale to zero." Tested against arithmetic, that turns
out to be conditional:

| Cold start | Break-even | req/min |
| ---: | ---: | ---: |
| 5 s | 514/hour | 8.6 |
| 10 s | 300/hour | 5.0 |
| **60 s** | **58/hour** | **1.0** |

**A first pass at this concluded scale-to-zero "wins across the whole plausible
range." That was wrong and contradicted the table it accompanied** — at a 60 s
cold start the break-even is roughly **one request per minute**.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Fix as scale-to-zero | Cheapest when idle | Unfounded — break-even may be ~1 req/min, and above it this is slower *and* dearer |
| B | Fix as always-warm | Predictable latency | Wastes 1,162.9 GB-h/month at genuinely low volume (A-008) |
| C | **Decide by measured duty cycle against a stated rule** | Correct under either outcome; the rule is written now, the input arrives later | Requires a measurement we do not yet have |

**Chosen:** Option C.

**Reason:**
The honest position is that **the answer depends on a number we do not have.**
Fixing either mode now would be asserting a conclusion the arithmetic does not
support. Writing the *rule* costs nothing and makes the eventual decision
mechanical rather than a fresh argument.

The pathological case is worth naming: at ~1 req/min with a slow cold start,
Tier 2 is busy 100% of the hour — **warm in all but name, while also paying
cold-start latency on every request.** That is the worst of both, and it is
exactly what fixing Option A blindly would produce.

**Consequences:**
- *Positive:* Deployment mode becomes a measurement, not a preference. The rule
  survives changes in vendor, price, and model.
- *Negative:* Cannot finalise deployment until **A-14** is measured.
- *Does not affect DEC-013:* tiering itself stands on the 150× memory spread and
  the standing-cost saving (**~14×** measured; 22× was the pre-build estimate).
  **Only Tier 2's mode is contingent.**
- *Newly constrained:* **A-14 blocks the deployment target choice**, which also
  waits on A-02.
- *Revisit when:* cold start is measured, or the model or runtime changes enough
  to move it.

**Evidence:** `../research/summaries/011-cost-model-and-enforcement.md`

---

## DEC-020 — Licence by artefact class

**Decision ID:** DEC-020 · **Date:** 2026-08-17 · **Status:** Accepted · **Closes:** A-12

**Decision:**
Different artefact classes carry different licences, because their upstream
obligations differ:

| Artefact | Licence | Why |
| --- | --- | --- |
| **Source code** | **Apache-2.0** | No upstream code imposes copyleft; explicit patent grant matters for infrastructure |
| **Documentation** | **CC-BY-4.0** | Permissive, attribution-preserving, standard for docs |
| **Data derivatives** | **Inherit upstream** — CC-BY-SA-4.0 where required | Share-alike obligations are not ours to waive |
| **Model artefacts** | *(none produced)* | DEC-017 means we adopt rather than produce |

**Context:**
A-12 was deferred until the upstream licence map was known. It now is,
`[verified]`:

- **Code dependencies are uniformly permissive** — `ctranslate2` (MIT),
  `epitran` (MIT-Modern-Variant), `tokenizers`, `sacrebleu`,
  `sentence-transformers`, `peft`, `accelerate`, `datasets` (Apache-2.0),
  `fastapi` (MIT).
- **Both adopted models are Apache-2.0** — `madlad400-3b-mt`,
  `tiroberta-bi-encoder`.
- **Three of six datasets carry CC-BY-SA-4.0 share-alike** — `haddas`, FLORES+,
  TiQuAD.

**Nothing forces copyleft on our code.** Share-alike enters only through *data*
and binds only *derivatives of that data*; source code is not a derivative of a
corpus.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Licence by artefact class** | Honours upstream data terms without over-restricting code | Contributors must know which class they are touching |
| B | One project-wide licence | Simple to state | Either over-restricts code or under-honours upstream data terms |
| C | GPL/AGPL for code | Strong reciprocity | Nothing upstream requires it, and it restricts the application developers DEC-002 names as primary |
| D | MIT for code | Simplest permissive | No explicit patent grant — weaker for infrastructure others build on |

**Chosen:** Option A, with **Apache-2.0** for code.

**Reason:**
Option B fails in one direction or the other: a permissive project-wide licence
would silently under-honour the share-alike obligations on `haddas`, FLORES+, and
TiQuAD derivatives; a copyleft one would impose restrictions no upstream requires
on the developers we exist to serve.

Apache-2.0 over MIT because the **explicit patent grant** matters more for
infrastructure others build on than the marginal simplicity of MIT, and it
matches what the surrounding ecosystem already uses.

**Consequences:**
- *Positive:* Upstream obligations are honoured precisely rather than
  approximately. Code stays maximally usable by our primary users.
- *Negative:* Contributors must know which class an artefact belongs to; the
  distinction needs to live in `CONTRIBUTING.md`.
- *Newly constrained:* **Data derivatives inherit their source's terms.** Mixing
  a CC-BY-SA corpus into a derived artefact makes that artefact CC-BY-SA. This
  must be recorded per artefact, not remembered.
- *Not in force until the files exist:* `LICENSE` (Apache-2.0) and `LICENSE-docs`
  (CC-BY-4.0) must be added.
- *Important limit:* **this is a reading, not a ruling.** That share-alike binds
  data derivatives and not our code is the standard interpretation and the one I
  would act on, but **A-06** remains the authority.
- *Revisit when:* A-06 returns, or a dependency changes licence.

**Evidence:** `../research/summaries/012-licence-and-sustainability.md`;
licence metadata `[verified]` 2026-08-17

### Amendment 1 — 2026-09-01: a dependency on the critical path *does* impose copyleft

The decision stands. Its stated basis no longer holds unconditionally.

DEC-020 rests on **"no upstream code imposes copyleft"**, and *"revisit when a
dependency changes licence"*. Neither anticipated the actual case: a dependency
whose licence never changed, but which had never been read. **HornMorpho is
GPL-3.0** `[verified]` 2026-09-01 from its `LICENSE.txt` — and DEC-006 puts
morphology, which HornMorpho is the only established analyser for, on the
critical path.

The asymmetry is what bites. Apache-2.0 code may be taken into a GPLv3 work;
**GPLv3 code cannot be redistributed under Apache-2.0**. So "no dependency
imposes copyleft" is true **only while morphology stays unimplemented** — which
is to say, only while DEC-006's MVP stays incomplete.

**What is unchanged:** every dependency we actually ship is still permissive, so
Apache-2.0 remains correct today. **What is now conditional:** it stops being
correct the moment HornMorpho is linked and distributed.

**A-07 is the decision that resolves it**, and the recommended route keeps
DEC-020 intact — HornMorpho as an **optional dependency the user installs
themselves**, so the combination is never ours to distribute. The existing
`morphology.is_available()` stub already implements that shape.

⚠️ **The lesson for this register:** *"revisit when a dependency changes
licence"* is the wrong trigger. It assumes the licence was read once. The
trigger should be **"revisit when a dependency is adopted"**, because the
dangerous case is a licence that was never checked, not one that moved.

---

## DEC-021 — Extend the evaluation anchors to cover the MVP primitives

**Decision ID:** DEC-021 · **Date:** 2026-08-17 · **Status:** Accepted

**Decision:**
**DEC-005's anchors are extended.** FLORES+ and TiQuAD remain the anchors for
translation and QA, but evaluation must additionally cover the **DEC-006 minimum
viable platform** — tokenization, morphological analysis, transliteration, and
embeddings. **The next research domain is evaluation for those primitives**, not
another capability.

**Context:**
A readiness audit of `docs/benchmarks/metrics.md` against DEC-006 found:

| Capability | Metric validated? | In the MVP? |
| --- | --- | --- |
| **Translation** | ✅ Yes (DEC-009) | ❌ **excluded** |
| Embeddings · Tokenization · Morphology · Transliteration | ❌ TBD | ✅ **yes** |

**Capabilities with a validated metric: 1. Inside the MVP: 0.**

**P-4** gates capability work on evaluation existing, so **the only capability we
are cleared to build is the one DEC-006 decided not to build first.**

**The root cause is structural, not a sequencing accident.** DEC-005 named
FLORES-200 (translation) and TiQuAD (QA). **Neither evaluates tokenization,
morphology, transliteration, or embeddings.** DEC-005 and DEC-006 were taken the
same day; each was sound alone, and together they left the MVP unmeasurable. This
is the failure `DECISIONS.md` warns about in its preamble — not contradiction,
but two decisions that do not compose.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Extend the anchors; research primitive evaluation next** | Restores P-4 for the platform we actually chose; blocked by nothing | Primitive evaluation is genuinely harder — no Tigrinya benchmark exists for morphology or tokenization |
| B | Build translation next, since it is cleared | Follows P-4 literally | Abandons DEC-006's reasoning; the primitives gap is our differentiator and translation has a strong incumbent |
| C | Revisit DEC-006 to make translation the MVP | Removes the tension | The gap-filling argument still holds, and `05_architecture` independently confirmed the MVP is also the cheap tier — 191 MB against 1,593 MB |
| D | Build the primitives without evaluation | Fastest to code | **Violates P-4 directly.** Unmeasurable capabilities cannot be improved or defended |

**Chosen:** Option A.

**Reason:**
Option A is the only one that leaves both DEC-006 and P-4 intact. DEC-006's
reasoning has since gained independent support it did not originally have —
`05_architecture` found the MVP is also the cheapest tier by 8.3× — so weakening
it (Option C) would discard a decision that has grown *stronger*, not weaker.

Option D is the tempting one and the one P-4 exists to forbid: building
primitives we cannot measure would leave us unable to tell whether the
tokenizer, the morphology, or the normalisation is what is wrong when something
downstream fails.

**Consequences:**
- *Positive:* The MVP becomes buildable under P-4. The next work is **blocked by
  nothing** — no licence, no egress, no human decision.
- *Negative:* Primitive evaluation is harder than translation evaluation. **No
  Tigrinya benchmark exists for morphology or tokenization**, so some of it may
  have to be constructed, which **A-006** already anticipated.
- *Newly constrained:* **A capability may not enter the MVP without an evaluation
  method**, which now has teeth because `metrics.md` is audited.
- *Honest limit:* it is **not yet known whether usable metrics exist** for these
  primitives. If they do not, that is itself a finding, and it would force
  DEC-006 back open on evidence rather than preference.
- *Revisit when:* primitive evaluation is researched, or it proves impossible.

**Evidence:** `../research/summaries/013-state-of-play.md`; readiness audit
`[verified]` 2026-08-17

---

## DEC-022 — The API response contract

**Decision ID:** DEC-022 · **Date:** 2026-08-18 · **Status:** Accepted

**Decision:**
Every API and MCP response obeys this contract, independently of which endpoints
eventually exist:

1. **Offsets are Unicode code points**, and the response **states the unit
   explicitly** (`"offset_unit": "codepoint"`). Never implicit.
2. **The surface form is returned verbatim**, always. It is never reconstructed
   from the analysis form (DEC-007).
3. **The analysis form is declared non-phonemic.** It is a *mixed* string and
   consumers must not assume phonemes.
4. **A variety label is mandatory** on any analysis or score —
   `eritrean` / `ethiopian` / `unknown`. **`unknown` is a first-class value, never
   a null** (DEC-010).
5. **The serving tier is disclosed**, and Tier 2 endpoints document cold-start
   behaviour rather than hiding it in an average (DEC-013, DEC-019).

**Context:**
`07_api_mcp` was believed blocked on **A-02**. Testing that — after the same
claim proved wrong for `04_model_strategy` — showed **A-02 blocks the *surface*
(which endpoints, which SDKs, whether MCP ships), not the *contract***. The
contract is the part that is expensive to change once consumers depend on it.

Three measurements drove the clauses:

- **Ethiopic Extended-B (U+1E7E0–U+1E7FF) is above the BMP.** On three core
  characters plus one Extended-B character, Python `len()` gives **4** and
  JavaScript `.length` gives **5**. Same string, different offsets, silently, on
  characters unlikely to appear in a test fixture. **Absent from all our corpora
  — a contract risk, not a live bug.**
- **Ge'ez is normalisation-stable** — 0 of 384 core characters change under
  NFC/NFD, so offsets do not shift under normalisation.
- **epitran transliterates 310 of 384 core characters.** Of the 74
  pass-throughs, 26 are unassigned and 29 are punctuation/digits (both correct),
  but **16 real syllables and 3 combining marks** return as raw Ge'ez, and
  Supplement / Extended-A / Extended-B are **entirely** unmapped.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Decide the contract now; defer the surface** | Settles the expensive half; the measurements are available today | Half a domain remains open |
| B | Defer everything to A-02 | Simple | Leaves the hard-to-reverse part undecided while the easy part waits on a human |
| C | UTF-8 byte offsets | Natural in Python | Wrong for every JS client; 3–4 bytes per character makes them unreadable |
| D | UTF-16 code-unit offsets | Natural in JS | Wrong in Python, and inherits the surrogate split exactly at Extended-B |
| E | Leave the offset unit implicit | Less schema | **The worst failure profile available** — silent, and only on rare characters |

**Chosen:** Option A, with code-point offsets.

**Reason:**
Code points are the only unit where **neither** major client language is
silently wrong; both can convert if they state the unit. Stating it explicitly
costs one field and removes a class of bug that would otherwise surface as
mysterious off-by-N errors in production, on the rarest characters.

Clause 3 exists because **describing the analysis form as "phonemes" is
measurably false** for 19 characters and for three whole blocks. A contract that
overstates what it returns is worse than one that admits mixed content.

Clause 5 exists because a **150× latency spread** cannot be presented uniformly:
one client timeout either aborts valid translations or hangs on a tokenize call.

**Consequences:**
- *Positive:* The expensive half of the API is settled, on measurement, before
  any consumer exists.
- *Negative:* Slightly heavier responses — unit, tier, and variety fields on
  every payload.
- *Newly constrained:* **No endpoint may return an analysis form without also
  returning the surface form**, and none may omit the variety label.
- *Refines DEC-007:* its "384/384 coverage" is true for non-empty output but
  must not be read as full phonemic coverage. Corrected in that record and in
  Experiment 001.
- *New work:* a **test fixture containing Extended-B**, so the offset contract is
  exercised rather than assumed.
- *Important limit:* **the surface is not designed** — endpoints, SDK order, and
  whether MCP ships all wait on **A-02**. And no API code should be written until
  DEC-021's primitive evaluation lands, since **P-4** applies to endpoints too.
- *Revisit when:* A-02 lands, or the 19 unmapped characters are handled — possibly
  by contributing them upstream to epitran (**G-11**).

**Evidence:** `../research/summaries/014-api-response-contract.md`; encoding and
epitran measurements `[verified]` 2026-08-18

---

## DEC-023 — Primitive evaluation is intrinsic-first; alignment is word-level

**Decision ID:** DEC-023 · **Date:** 2026-08-18 · **Status:** Accepted
**Corrects:** DEC-007, DEC-022 · **Answers:** DEC-021

**Decision:**

**(a) Primitives are evaluated intrinsically first.** Idempotence, determinism,
reversibility, coverage, and alignment integrity are measured as **property tests
over real text**, requiring no annotated data. Gold-standard evaluation is
reserved for **accuracy**, which is the only property that needs it.

**(b) Surface↔analysis alignment is WORD-LEVEL.** Offsets map word spans, not
characters. **This corrects DEC-007's "alignment offsets" and DEC-022's
code-point offset clause**, both of which assumed a character-level alignment
that does not exist.

**Context:**
**DEC-021** asked how to evaluate the MVP primitives when no Tigrinya gold
standard exists for any of them. Experiment 004 pre-committed four hypotheses:

| Hypothesis | Prediction | Measured | Verdict |
| --- | --- | --- | --- |
| H1 — normalisation idempotent | 100% | 0 failures | ✅ |
| H2 — transliteration deterministic | 100% | 0 failures | ✅ |
| **H3 — character alignment recoverable** | ≥ 99% | **23.89%** | ❌ |
| H4 — tokenization reversible | ≥ 99% | 100.00%, 0 `[UNK]` | ✅ |

**Three of four hold, so P-4 is satisfiable for Tier 0 today.** H3's failure is
the substantive finding: `ር` transliterates to `r` alone but `rɨ` inside ሃገርነት,
because **Ge'ez 6th-order characters are ambiguous between "consonant + ɨ" and a
bare consonant** and epitran resolves that from neighbours. Context supplies
**1,375 of 8,430 output symbols — 16.3%**.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Intrinsic-first; word-level alignment** | Evaluable today with no annotation; alignment exact by construction | Catches *broken*, not *wrong*; morphology still needs gold data |
| B | Build a Tigrinya primitives benchmark first | Enables accuracy measurement | Months of work (A-006) before anything can be evaluated at all |
| C | Keep character-level offsets | Finest granularity | **Measurably impossible** — 23.89% |
| D | Accept a tradeoff: offsets *or* phonology | Seemed to follow from H3 | **Refuted by measurement** — a false dilemma; see below |
| E | Skip evaluation, build the primitives | Fastest | Violates P-4, and H3 is exactly the error that only checking finds |

**Chosen:** Option A.

**Reason:**
Primitives differ from translation in a way that turns out to matter: **most of
their correctness is a property of the function, not agreement with a human.**
That makes Option B's cost avoidable for everything except accuracy.

Option D deserves recording because **I proposed it and it was wrong.** The
first reading of H3 framed a tradeoff between exact offsets and faithful
phonemes. A follow-up measurement refuted it **before it reached this record**:

- ~~a word's transliteration is preserved inside a sentence: **1,639/1,639
  (100%)**~~ ⚠️ **RETRACTED by Amendment 1 — the real figure is 95.47%.**
- prepending a character changes **0 of 1,635** tokens *(holds; re-measured at
  0 of 1,565)*

~~Epenthesis resolves **within a word**; nothing crosses word boundaries. So
word-by-word transliteration gives **full fidelity *and* exact alignment**.~~
⚠️ **The fidelity half is retracted** — see Amendment 1. Word-by-word gives
**exact alignment**, and is correct because the running-text form depends on
arbitrarily distant text, not because the two agree. The decisions asked for the
wrong granularity, not for something unachievable.

**Consequences:**
- *Positive:* **P-4 is satisfied for Tier 0 now**, without building a benchmark.
  Tier 0 becomes buildable.
- *Positive:* the alignment layer gets **simpler** — word spans are exact by
  construction, so no alignment algorithm is needed at all.
- *Negative:* **no character-level offsets, ever**, with this transliterator.
  Consumers wanting sub-word alignment cannot be served.
- *⚠️ Important limit:* **intrinsic checks catch *broken*, not *wrong*.** A
  transliterator returning deterministically incorrect phonemes passes H2
  perfectly. These properties are necessary and nowhere near sufficient.
- *Remaining gap:* **morphology still needs gold data** — but it is now **one**
  capability needing annotation rather than four, which is what DEC-021 set out
  to establish. Its intrinsic properties are also **untested**, because
  HornMorpho is unresolved (**A-07**).
- *Untested:* **embeddings**. Tier 1, and `tiroberta-bi-encoder` is monolingual,
  so FLORES+ bitext retrieval does not directly apply.
- *Revisit when:* a transliterator exposing character alignment appears, or
  morphological gold data exists.

**Evidence:** `../research/summaries/015-primitive-evaluation.md`;
`experiments/004-primitive-evaluation/` `[verified]` 2026-08-18

### Amendment 1 — 2026-08-19: the supporting measurement was wrong; the decision survives

**The decision stands. The evidence given for it does not.**

This record justified word-level alignment by claiming word-by-word
transliteration is *lossless*, citing two figures:

> a word's transliteration is preserved inside a sentence: **1,639/1,639 (100%)**
> prepending a character changes **0 of 1,635** tokens

**Neither figure came from a committed script** — they were produced by an
ad-hoc probe during the session that recorded this decision, which is a
**DEC-016 violation**. `experiments/005-word-boundary-epenthesis/` re-measures
both.

**What was wrong.** The preservation figure came from a **containment** test
(`alone in in_context`). Containment cannot detect an *appended* character, and
an appended character is what **92%** of the failures are:

| Test | Result |
| --- | ---: |
| Containment — what was measured | **99.62%** (2,353/2,362) |
| **Exact equality — what was claimed** | **95.47%** (2,255/2,362) |

98 of 107 mismatches are the in-context form carrying one extra word-final `ɨ`
(`ʔɨzom` → `ʔɨzomɨ`). **The test could not fail in the direction that mattered.**

**What was right.** Prepending is genuinely inert — **0 of 1,565** unique words
change. Left context does not matter. This is what makes the `lru_cache` on
`transliterate_word` sound, so that claim is load-bearing and it holds.

**What is worse than expected.** The natural reading — "the final character is
sensitive to the next word" — is also false. Local context does not predict it:
the word alone, the word plus the next eight words, and six preceding words plus
the word all give `ʔɨzom`. **The full 128-word line gives `ʔɨzomɨ`.** Replacing
that line's *first* word — 72 words away — flips the result. The behaviour is
deterministic (byte-identical across calls and across a fresh instance) but is
**not a function of local linguistic context**, so it cannot be stated as a
phonological rule.

**Why the decision survives, on a better argument.** The original reasoning was
"word-by-word loses nothing." That is false. The correct reasoning is that
**whole-text output cannot serve an API contract**: a word's transliteration
would depend on text arbitrarily far away, so the same word in the same sentence
could return different answers as unrelated parts of a request changed.
Word-by-word makes the analysis form a function of the word alone. Word-level
spans remain exact by construction.

**Consequences added:**
- *Corrected:* the shipped analysis form is **not** what epitran produces on
  running text; it differs on **4.53%** of word tokens. Documented in
  `transliterate.py` and `types.py`, which both quoted the withdrawn figure.
- *New:* **which form is phonologically correct is unknown.** Word-final
  6th-order characters are usually bare consonants in Tigrinya, which would
  favour the shipped form — but that is a claim about the language, and it needs
  a speaker. Folded into the standing native-speaker validation gap.
- *New:* the position sensitivity is plausibly an upstream defect. Recorded as
  **A-16** (report to epitran), non-blocking.
- *Method:* a verification check must use **exact equality, never containment**.
  `tigrinya_eval.primitives` implements it that way, so this specific error
  cannot recur silently.

**Evidence:** `experiments/005-word-boundary-epenthesis/` `[verified]` 2026-08-19

---

## DEC-024 — Load-bearing figures are registered, and retired ones are checked

**Decision ID:** DEC-024 · **Date:** 2026-08-19 · **Status:** Accepted
**Enforces:** the correction discipline DEC-018 applies to rules

**Decision:**
Every load-bearing figure lives in **`docs/figures.json`** with its current
value, its basis, and any **retired** predecessors. `scripts/check_figures.py`
fails CI when a retired figure is quoted as current — that is, when it appears
without a retraction marker within 8 lines.

**Context:**
**Three figures were corrected in one place and left standing in others.** Each
was found by hand, weeks apart, and each sweep missed files the next one caught:

| Figure | Retired to | Files still asserting it when found |
| --- | --- | ---: |
| Tier 0 footprint **72 MB** | 113.4 MB | **5** |
| Tiering saving **22×** | ~14× | **4** |
| Transliteration preserved **1,639/1,639** | 95.47% | **3** |
| Coverage **99.72%** | 100.00% | **2** |

The final sweep found live claims in `docs/architecture/system_overview.md`, a
file never touched during any of the corrections that caused them. **Partial
correction is worse than no correction**: a document asserting a withdrawn
number reads as authoritative, and the reader has no way to know it is stale.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Keep correcting by hand | No new machinery | **The measured failure rate is 4 for 4** — every figure corrected so far was left standing somewhere |
| B | **Registry + CI check** | Catches the demonstrated failure; the registry doubles as a lookup table | Markers are heuristic; a determined author can satisfy them without retracting |
| C | Single-source every figure and transclude it | No duplication possible | No transclusion in plain Markdown; would require a build step (**P-7**) |
| D | Forbid quoting figures outside the registry | Airtight | Unreadable prose; nobody would comply |

**Chosen:** Option B.

**Reason:**
The failure is **demonstrated and repeated**, not hypothetical — which is
exactly the bar DEC-018 sets for turning a habit into a mechanism. Option A has
a measured 100% failure rate. Option C is the correct answer in a system with a
documentation build, and this project deliberately has none (**P-7**).

The markers are generous on purpose. A noisy check gets switched off, and a
switched-off check is the **DEC-008** failure this is meant to prevent. **The
cost of that generosity is real and is not hidden: this catches oversight, not
intent.**

**Consequences:**
- *Positive:* `docs/figures.json` is a single place to answer "what is the
  current value of X, and what did it used to be?"
- *Positive:* retiring a figure becomes a deliberate act with a place to record
  the reason and date.
- *Negative:* one more file to update, and the check can be satisfied
  superficially by writing a marker word nearby.
- *Newly constrained:* **a figure must be retired in the registry in the same
  change that corrects it**, or CI fails on the very edit that fixes it.
- *Limit:* the check does **not** verify that current figures are right —
  nothing here re-derives a measurement.
- *Revisit when:* the registry exceeds ~30 figures, or a documentation build
  exists and Option C becomes available.

### Extension, same day — derived counts

The registry handles figures that were *measured*. It does nothing for counts
that are **derived from the repository**, and those had rotted worse:

| Document | Claimed | Actual |
| --- | --- | ---: |
| `README.md` | "four research domains complete", "Eight decisions recorded" | **13**, **24** |
| `PROJECT_CONTEXT.md` | "Four research domains complete" | **13** |
| `summaries/README.md` | "5 summaries, 1 experiment" | **15**, **6** |
| `013-state-of-play.md` | "11 of 12" domains, "21" decisions | **13**, **24** |

The README also still said **"no service code written"** with two packages in
the tree. That is the first paragraph a reader sees.

**These need no registry** — the true value is computed from the tree, so a
document either agrees with it or does not. `check_figures.py` now derives four
counts and flags any claim that contradicts them.

**Volatile counts are deliberately excluded.** Test totals change on almost
every commit, so living documents say "both suites passing" and exact numbers
appear only in dated CHANGELOG entries, which are snapshots and stay true.

**⭐ The negative control earned its keep immediately.** The first planted
violation caught `**3** reproducible experiments` and **sailed straight past**
`four research domains complete` and `Eight decisions recorded` — spelled as
words, which is *verbatim* what the README said. **The check would have missed
the exact instance it was built for.** `_digitise()` normalises spelled-out
numbers before matching; the control then caught all three.

Then it happened **again**, in the same hour. Sharing one marker vocabulary
between both checks put `recorded` in scope for counts — and the claim being
checked is literally "N decisions recorded". **Every counts violation was
suppressed and the control went green.** The marker sets are now separate, and
neither may overlap the phrasings it guards.

So: **three checks in two days that looked correct and could not have failed on
the case that motivated them** — DEC-023's containment test, the
spelled-out-numbers gap, and the shared marker list. **Planting a failure is
not optional diligence; it is the only way to find out whether a check checks
anything.**

**One limitation is left in, knowingly.** A marker on a neighbouring line
suppresses a genuine violation within the 8-line window — verified: a bare
"72 MB" went unflagged eight lines below an unrelated sentence containing
"recorded". Narrowing the window would trade this for false positives on the
retraction blocks that already exist, and a noisy check gets switched off.
**This is a net, not a proof.**

**Evidence:** the four retirements and four count corrections above
`[verified]` 2026-08-19; negative controls planted and caught for both checks
before commit.

---

## DEC-026 — Embeddings are evaluated intrinsically, against a lexical floor

**Decision ID:** DEC-026 · **Date:** 2026-08-23 · **Status:** Accepted
**Extends:** DEC-023's method to Tier 1 · **Corrects:** the READINESS_PLAN
dependency graph

**Decision:**

**(a) Embeddings are evaluated intrinsically first** — six properties measured
without annotation: orthographic invariance, self-retrieval, discrimination,
corruption monotonicity, order sensitivity, length independence.

**(b) A lexical baseline is mandatory before the neural model is adopted.**
`tiroberta-bi-encoder` is 124.6M parameters and roughly doubles Tier 1's
footprint; under **P-6** and **P-7** it must beat a character n-gram TF-IDF
encoder that costs nothing.

**(c) Cross-lingual retrieval (G-4) is unreachable with this model** and needs a
different model class. Recorded now rather than discovered in implementation.

**Context:**
DEC-023 evaluated three of four primitives without gold data and **explicitly
excluded embeddings**, because the standard method — FLORES+ bitext retrieval —
needs one shared vector space and `tiroberta-bi-encoder` is monolingual.
Embeddings were therefore the second MVP capability with no evaluation path.

⚠️ **A licence correction fell out of this.** `READINESS_PLAN.md` and `ACTIONS.md`
both said A-01 blocks Tier 1. **`tiroberta-bi-encoder` and `tielectra-bi-encoder`
are Apache-2.0** — A-01's own text says so. **Tier 1 is blocked on A-09 (egress)
alone.**

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | **Intrinsic-first + lexical floor** | Evaluable today with no annotation; the floor answers whether 119 MB is earned | Catches *broken*, not *wrong* |
| B | Build a Tigrinya STS set first | Enables real similarity measurement | Months (**A-006**) before anything is evaluable |
| C | FLORES+ bitext retrieval | Standard, no annotation | **Impossible** — the model is monolingual; would measure tokenizer collisions |
| D | Adopt a multilingual encoder instead | Enables G-4 | A Tier 1 scope change nobody has decided, and abandons a cleared Apache-2.0 model |
| E | Ship embeddings unevaluated | Fastest | Violates **P-4**, on the capability where silent failure is least visible |

**Chosen:** Option A, with C recorded as impossible and D as an open question.

**Reason:**
The DEC-023 argument transfers: most of what makes an embedding model *usable*
is a property of the function. **E1 is the one that is specific to Tigrinya and
would not appear in a generic suite** — mixing ጸ/ፀ is normal practice, measured
at 1.0–3.8% in Eritrean newspapers, so an encoder that treats them as different
words fails retrieval **silently, for whichever spelling the user did not
type**.

The lexical floor is not a formality. Measured, it **passes the mechanical
properties and fails E1 at 0.2232 against a 0.80 floor** — so the neural model
has a specific, measurable job rather than a vague expectation of being better.

**Consequences:**
- *Positive:* Tier 1 is evaluable the moment weights are reachable; the bar is
  already recorded.
- *Positive:* if the neural model does not beat the baseline, that is a
  **decision made before building**, not after.
- *Negative:* the floors are **provisional** — set from one 30-sentence corpus
  and one lexical model, not earned by a model that passed them.
- *⚠️ Limit:* **catches *broken*, not *wrong*.** Whether two *different*
  sentences are genuinely similar still needs a speaker or an STS set.
- *Bridge recorded:* a sixth `validation/` sheet rating sentence pairs 0–4 would
  turn one reviewer session into a minimal Tigrinya STS set. **Deliberately not
  built** until A-13 returns — adding items risks the whole instrument going
  unanswered.
- *Revisit when:* weights are reachable (A-09), or G-4 forces a multilingual
  encoder.

**Evidence:** `../research/reports/08_evaluation/003-embedding-evaluation-without-gold-data.md`;
`experiments/008-embedding-baseline/` `[verified]` 2026-08-23

---

<!--
Append new decisions below this line. Copy the format from
../research/templates/decision_template.md and update the Index table above.
-->
