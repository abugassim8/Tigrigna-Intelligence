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
| DEC-009 | 2026-08-03 | chrF primary translation metric; BLEU for comparability only | Accepted |
| DEC-010 | 2026-08-03 | Evaluation results are variety-scoped; no cross-variety aggregate | Accepted |
| DEC-011 | 2026-08-03 | MADLAD-400-3B is the translation baseline; NC-licensed models are research-only | Accepted |
| DEC-012 | 2026-08-03 | Library-first; services are thin wrappers over libraries | Accepted |
| DEC-013 | 2026-08-03 | Tier by resource profile; never co-locate tiers in one process | Accepted |
| DEC-014 | 2026-08-03 | CTranslate2 is the single model runtime | Accepted |
| DEC-015 | 2026-08-03 | Screening is executable and mandatory; datasets carry a screening record | Accepted |
| DEC-016 | 2026-08-03 | Every experiment emits a machine-checkable artefact | Accepted |

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
| Coverage | ✅ 384/384 core Ethiopic characters |
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
  onto surface spans.
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

**Decision ID:** DEC-011 · **Date:** 2026-08-03 · **Status:** Accepted

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
Hub metadata `[verified]` 2026-08-03

---

## DEC-012 — Library-first: services are thin wrappers over libraries

**Decision ID:** DEC-012 · **Date:** 2026-08-03 · **Status:** Accepted

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
morphology are pure computation over small data (72 MB total, DEC-013).

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

**Decision ID:** DEC-013 · **Date:** 2026-08-03 · **Status:** Accepted

**Decision:**
The platform is decomposed by **resource profile**, not by domain:

| Tier | Contents | Cumulative | Behaviour |
| --- | --- | ---: | --- |
| **0** | normalisation, tokenization, transliteration, morphology | **72 MB** | always warm |
| **1** | + embeddings | **191 MB** | warm |
| **2** | + translation | **1,593 MB** | lazily loaded; may scale to zero |

**Tiers are never co-located in a single process.** Model weights load lazily,
per tier, on first use.

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
each tier takes the deployment mode that suits it: Tier 0 is cheap enough (72 MB)
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

**Decision ID:** DEC-014 · **Date:** 2026-08-03 · **Status:** Accepted

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
CTranslate2 converter registry inspected 2026-08-03 `[verified]`

---

## DEC-015 — Screening is executable and mandatory; datasets carry a screening record

**Decision ID:** DEC-015 · **Date:** 2026-08-03 · **Status:** Accepted

**Decision:**
The **DEC-008** gates are implemented as
`scripts/data_processing/screen_dataset.py` and are **mandatory**. No dataset
enters training, tuning, or evaluation use without a committed, machine-readable
**screening record**. The four gates are **licence**, **quality**, **variety**,
and **contamination**.

**Context:**
DEC-008 established the policy in July. Measured on 2026-08-03: it mentions
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
validation runs `[verified]` 2026-08-03

---

## DEC-016 — Every experiment emits a machine-checkable artefact

**Decision ID:** DEC-016 · **Date:** 2026-08-03 · **Status:** Accepted

**Decision:**
An experiment is not complete until it writes a **machine-readable results
artefact** (`results.json`) alongside its prose. Re-running an experiment must
reproduce that artefact **byte-identically**, and a mismatch is a finding to
investigate rather than a file to overwrite.

**Context:**
Re-running all three experiments and byte-comparing on 2026-08-03:

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
- *Revisit when:* experiments become numerous enough that a real tracking system
  earns its cost.

**Evidence:** `../research/summaries/009-pipeline-without-training.md`;
re-run and byte-comparison `[verified]` 2026-08-03

---

<!--
Append new decisions below this line. Copy the format from
../research/templates/decision_template.md and update the Index table above.
-->
