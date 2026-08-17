# Changelog

## Purpose of this document

This file records notable changes to the **project** — its structure, direction,
decisions, and capabilities. It is not a git log. Git already records every
commit; this file records the small subset of changes that a future contributor
would need to know about to understand how the project got to where it is.

**How to use it:** Read the top entries to understand recent direction. Add an
entry when you change project structure, supersede a decision, complete a
research phase, or ship a capability.

**What future contributors should add:** One entry per meaningful change, newest
first. If you find yourself writing "fixed typo" here, it does not belong here.

**Format:** Loosely [Keep a Changelog](https://keepachangelog.com/). Dates are
ISO-8601. The project is pre-release and unversioned; versioning begins when the
first service is deployed.

---

## [Unreleased]

### 10_infrastructure researched; DEC-018, DEC-019 — 2026-08-03

**No dollar figures appear in this domain, deliberately** — vendor pricing is
unverifiable from this environment and volatile, so cost is modelled in
**GB-hours** and **break-even rates**, arithmetic that survives price changes.

**Tiering cuts standing resource cost 22×**: 52.6 GB-h/month for a warm Tier 0
against 1,162.9 GB-h/month for one merged always-warm process. DEC-013 was
decided on the memory spread and holds on cost too.

**⚠️ A correction.** A first pass concluded scale-to-zero for Tier 2 "wins across
the whole plausible range." **That was wrong and contradicted the table it
accompanied.** At a 60 s cold start the break-even is roughly **one request per
minute** — above which always-warm is both cheaper *and* faster. The pathological
case is real: at ~1 req/min with slow cold start, Tier 2 is busy 100% of the hour,
warm in all but name while still paying cold-start latency on every request.

**DEC-019** therefore fixes neither mode. It states the rule — keep warm above
`3600 / (cold_start + service)` req/hour — and makes measuring cold start
**A-14**. DEC-013's tiering is unaffected; only Tier 2's *mode* was ever
contingent.

**DEC-018** puts CI behind the decision log. **DEC-008 spent three months as
policy with no mechanism and was silently ignored the whole time**; five newer
rules sat in exactly that position. `ci/verify.yml` implements all of them, and
**every check was run locally before commit** — 3 experiments byte-identical,
screening fails closed, corrupted sample still detected, 10 summaries under
limit, 17 decisions with rejected alternatives. The reproducibility job doubles
as a dependency regression test.

⚠️ **The workflow is NOT yet running.** GitHub refused the push — an app token
cannot create `.github/workflows/` files without `workflows` permission — so it
sits at `ci/verify.yml` awaiting a one-command install (**A-15**). **Until then
DEC-018 is itself policy without mechanism**, the very failure it was written to
prevent. That is recorded loudly in the decision, the report, the summary, and
`ci/README.md` rather than left to be discovered later.

Also recorded: what we deliberately **do not** build — no orchestration, no GPU,
no model registry, no vector DB, no autoscaling curves. A container runtime,
object storage, and CI.

### 09_training_strategy researched; DEC-017 — 2026-08-03

**The contingency plan has no fuel.** Auditing every dataset against licence
*and* role found **zero cleanly-licensed parallel training data**: the 1.4M en–ti
pairs are unlicensed, and FLORES+ and TiQuAD are our evaluation anchors, so
training on them is contamination. Monolingual comes to 15,053 documents, both
corpora carrying documented defects.

**This exposes a live risk in DEC-011.** That decision adopted MADLAD-400-3B on
licensing and size **without measuring its Tigrinya quality** — correctly, on the
evidence available. So the likeliest trigger for training is that MADLAD proves
inadequate, and **if that happens we could not fine-tune our way out**, because
there is no parallel data we may lawfully use.

**A-05 is therefore escalated to Blocking.** It was filed as "the cheapest
high-value action"; it is now **the only route to a remedy if our translation
model underperforms** — the insurance policy on DEC-011.

**DEC-017** gates training behind an adaptation ladder climbed cheapest-first
(decoding config → tokenizer adaptation → LoRA → full fine-tune), with
from-scratch **foreclosed** by A-002's ~40M-token ceiling and recorded once so it
is not re-proposed. Five trigger conditions are required, the first being a
measured deficit against a pre-committed threshold: **no training without a
number.**

If triggered, LoRA on a 4-bit base needs **~1.4 GB peak memory against ~32.9 GB**
for a full fine-tune — ~23× less, ~400× fewer trainable parameters, and under
A-008 the difference between renting datacentre hardware and using a desktop.
Tooling is available and Apache-licensed; **nothing is blocked on tooling**.
Memory is arithmetic; training time and quality are not estimated, because they
cannot be known without running it.

### 06_ml_pipeline researched; DEC-015, DEC-016 — 2026-08-03

**Two claims this repository makes about itself were tested. One held; one did
not.**

**Reproducibility held where it was designed in.** Re-running all experiments and
byte-comparing: 002 and 003 reproduced identically; **001 emitted no
machine-checkable artefact at all**, so P-5 could not even be evaluated for it —
and DEC-007's amended form rests on its numbers. **DEC-016** now requires every
experiment to emit `results.json`. The debt was paid immediately: Experiment 001
now emits one and reproduces byte-identically, and its recorded values (384/384
coverage, 59 Tigrinya-specific characters, 22 collisions, 1.9714× expansion)
match DEC-007's amendment exactly — that amendment is now regression-checked
rather than asserted.

**DEC-008 was policy without mechanism.** It mentions screening seven times;
`scripts/data_processing/` contained **zero files**; and screening logic had been
reimplemented in all three experiment scripts, differently each time.
**DEC-015** makes the four gates — licence, quality, variety, contamination —
executable via `screen_dataset.py`, with a machine-readable record and a
pipeline-usable exit status. Validated with four tests including a **positive
control**: screening an evaluation set against itself detects 652 shared
8-grams. Without that control, "no contamination found" is indistinguishable
from a broken detector.

Two deliberate design choices: **licence is asserted, never detected** (a licence
is a legal fact, not a property of bytes), and **contamination fails closed**
(silence must not read as clearance).

**The pipeline is also named correctly for the first time:** acquire → screen →
convert → evaluate → release, with **training as a contingency branch**. A
training-centred design would invest in labelling and checkpoint management we do
not need, while under-investing in screening and evaluation, which are where the
work has actually gone.

**Correction issued.** Building the screening tool produced a baseline
Experiment 003 lacked: orthographic mixing appears in **every** Tigrinya source
tested, including unambiguously Eritrean ones (1.0–3.8%). Calling FLORES+
"orthographically inconsistent with itself" was true but implied an anomaly the
baseline does not support — that framing is withdrawn. **DEC-010 strengthens
rather than weakens**: FLORES+'s ET-marker rate is 15.1%, ~4–15× Eritrean
sources, so the Ethiopian-leaning signal now rests on better evidence than when
first recorded.

### 05_architecture researched; DEC-012, DEC-013, DEC-014 — 2026-08-03

**The memory spread is the architecture.** Our capabilities differ by **~150×**:
normalising a string is free, tokenization is 10 MB, and MADLAD-400-3B at Q4 is
1,402 MB. Cold start differs by a similar factor. So the system decomposes **by
resource profile, not by domain** (**DEC-013**) — Tier 0 primitives at 72 MB,
Tier 1 adding embeddings at 191 MB, Tier 2 adding translation at 1,593 MB, never
co-located in one process.

That **independently validates DEC-006**: the minimum viable platform it chose on
gap-filling grounds is exactly Tier 0 + Tier 1, and adding translation is an
**8.3× jump**. A decision gets support from evidence it was not built on, and the
MVP boundary turns out to be a cost cliff rather than a roadmap preference.

Tiering also dissolves the **A-008** low-volume bind: a 1.4 GB model kept warm
costs idle memory, scaled to zero costs a cold start every request. Neither is
acceptable platform-wide; both are fine per tier. The tension only exists if the
tiers are merged.

**DEC-012** makes every capability an importable library with services as thin
wrappers — a library has zero serving cost at zero volume, which no service
topology matches, and DEC-002's developer users want `pip install`, not
infrastructure.

**DEC-014** adopts **CTranslate2 (MIT)** after installing it and inspecting its
converter registry: `T5Config` (MADLAD), `M2M100Config` (NLLB comparison), and
`RobertaConfig` (the embedding encoder) are all supported. One runtime, one
quantisation story, one operational surface. Support is verified; **conversion is
not** — that needs the weights.

`docs/architecture/system_overview.md` is written and is no longer a scaffold.
Memory throughout is arithmetic; **no latency figure appears anywhere**, because
none was measured.

### 04_model_strategy researched; DEC-011 — 2026-08-03

**The model behind essentially every published Tigrinya MT number cannot be
shipped.** Every NLLB-200 variant — 600M, 1.3B, 3.3B — is **CC-BY-NC-4.0**.
NLLB produced the COMET figures underpinning DEC-004 and has 28M downloads, and
under P-9/A-009 none of that survives an unshippable licence: we would be passing
a restriction to downstream users that they inherit without knowing it.

**DEC-011** adopts **`google/madlad400-3b-mt` (Apache-2.0)**, which covers `ti`,
and extends DEC-008's quarantine rule from data to models — **NC-licensed models
are research-and-comparison only, never shipped.**

Licence compliance costs **4.8× the parameters** (615M → 2,940M). A-008 survives
anyway: MADLAD-3B is **1.4 GB at Q4** with GGUF quantisations already published.
Memory is arithmetic and is stated; **latency is not measured** and is not
claimed — model downloads are egress-blocked.

Two consequences worth flagging. First, **our production model and our comparison
baseline are now different models**, so "we match published Tigrinya MT quality"
is unfounded unless the DEC-009 harness runs both. Second, **MADLAD-400's
Tigrinya quality appears to be unpublished** — measuring it would be a real
ecosystem contribution rather than an internal number.

Also recorded: `04_model_strategy` was believed blocked on A-01, and was not.
A-01 concerns the unlicensed `fgaim` models, and **`fgaim` publishes no MT
model** — translation was answerable the whole time. And a method lesson: MADLAD
never surfaced in the ecosystem scan because that scan searched for *Tigrinya*
resources, while MADLAD is a multilingual model that happens to include it.

### 08_evaluation researched; DEC-009, DEC-010 — 2026-08-03

**The question `metrics.md` was written to hold open is now answered — by
measurement rather than citation**, since the literature on metric validity is
egress-blocked.

**Experiment 003** used FLORES+ parallel data (the same 30 sentences in English
and Tigrinya, so language is the only variable) and pre-committed four
hypotheses. **All four were refuted; all four effects pointed in the predicted
direction.** BLEU is **~1.08× harsher** on Tigrinya — real, consistent, and about
half the size the standard warning implies. A methodological check showed the
test was itself ~1.44× harsher on Tigrinya by construction, biasing *toward*
confirmation, so ~8% is an upper bound.

**DEC-009** adopts **chrF as the primary translation metric**, with BLEU always
reported alongside for comparability and never alone. The case does not rest on
the refuted threshold: chrF's advantage *widens as quality falls* (1.18× → 1.80×
at 10% → 30% corruption), and low-resource systems live in that regime.
Cross-language BLEU comparison without stating the penalty is now a documented
error.

**DEC-010** makes evaluation results **variety-scoped**. The two DEC-005 anchors
appear to be in different varieties: TiQuAD is verified Eritrean-sourced, while
FLORES+ Tigrinya is verified orthographically inconsistent with itself and shows
Ethiopian markers with zero Eritrean counterparts. No aggregate "Tigrinya score"
may be reported. Native-speaker confirmation is now **A-13**.

Also recorded: both anchors are gated or awkward, and the convenient parquet
mirrors of FLORES **systematically drop low-resource languages** — a working
pipeline for high-resource languages is no evidence our data exists. The ungated
route and row offsets are written down so nobody re-derives them.

`docs/benchmarks/metrics.md` and `evaluation_strategy.md` are no longer scaffolds
for translation.

### ACTIONS.md added; summary 001 re-compressed — 2026-07-29

**`ACTIONS.md` — new.** Research kept producing blockers that need a *person*
rather than a research session, and they were scattered across five summaries
and eight decision records. They are now one prioritised register: twelve
actions, four of them blocking, each stating what to do, why, and what it
unblocks — **with ready-to-send message drafts** so they can be executed rather
than merely read.

Highlights: licence clarification on the `fgaim` models (blocks DEC-003, the
whole reuse plan); confirming DEC-002 (a product-owner call, not a research
finding); reporting the confirmed TiQuAD contamination upstream; requesting
TiQuAD's withheld test split; and a single message that could unlock **1.4M
en–ti parallel sentences**. Also legal review of TiQuAD's copyright position,
HornMorpho's licence, an `HF_TOKEN` to stop the anonymous rate-limiting that
disrupted this session, and a session with unrestricted egress to clear the
verification backlog.

Linked from `README.md`, `PROJECT_CONTEXT.md`, `CONTRIBUTING.md`, and the
summaries index.

**Summary 001 re-compressed**, 1,054 → ~850 words. The verification-corrections
block had bloated it past the 800–1,000 target; that detail is historical and
belongs in the report's addendum, so the summary now carries the current
conclusions plus a three-line pointer. Findings that need human action now cite
their `ACTIONS.md` ID directly.

### 03_data_strategy — corpus measured, contamination risk found — 2026-07-29

**The corpus is now measured rather than estimated.** Instead of reading dataset
cards, this pass queried the Hugging Face dataset API for actual row counts,
schemas, and parquet sizes. That distinction produced every finding below.

| Dataset | Rows | Parquet | Licence |
| --- | ---: | ---: | --- |
| `mewaeltsegay/TigrinyaLargeText` | 12,400 | 36.1 MB | **MIT** |
| `SIMBA9657/haddas-tigrinya-corpus` | 2,653 | 4.3 MB | **CC-BY-SA-4.0** |
| `farefaine/tigrinya-pretraining` | 52,100 | 15.7 MB | ⚠️ none |
| `michsethowusu/english-tigrinya_sentence-pairs` | **1,400,000** | 110.4 MB | ⚠️ none |

**Three findings**

1. **No hidden reservoir.** TiRoBERTa was pretrained on 40M tokens; the open
   monolingual corpus is 56 MB across ~67K documents — same order of magnitude.
   **A-002 confirmed.** (No MB→token conversion was attempted; Ge'ez parquet
   compression ratios are unknown and a fabricated figure would propagate.)

2. **Licensing, not volume, is the binding constraint.** Of 1,519,253 rows
   measured, **~99% carry no stated licence.** Cleanly licensed: **15,053
   documents.** The single largest resource — 1.4M parallel sentences — is
   unlicensed. **A-009 sharpened.**

3. **⛔ CONFIRMED evaluation contamination.**
   `farefaine/tigrinya-pretraining`, titled *"Tigrinya Raw Pretraining Sources"*,
   carries TiQuAD's extractive-QA schema field for field
   (`id, question, context, answers, article_title, context_id`), and its
   validation split is **exactly 934 rows — matching TiQuAD's validation split.**

   TiQuAD is our evaluation anchor under DEC-005. Anyone pretraining on this
   dataset would silently invalidate their own TiQuAD evaluation. Most likely an
   honest aggregation error; the downstream effect is identical.

   **Stated as a strong signal, not proof** — schema and split size are
   `[verified]`, row-level overlap is **not** (huggingface.co download is
   egress-blocked). A falsifiable check is specified in the report.

**Also found:** Hugging Face `size_categories` tags are unreliable — two of four
datasets sampled carry *internally contradictory* size metadata, one overstating
by up to ~20×. Query the API for real counts.

**DEC-008 recorded** — mandatory contamination screening before any dataset
enters training use, and structural quarantine of unlicensed data to
research-only. Notably rejected: screening *only* datasets that look like
evaluation data, since the founding case was labelled "pretraining sources" and
that heuristic would have missed it (R-019, R-020).

**DEC-005 corollary:** externally reported Tigrinya QA scores must now be treated
as suspect until the models behind them are shown to be uncontaminated.

**Cost note:** the highest-value action available is asking two maintainers to
add a licence file — potentially unlocking 1.4M parallel sentences for the price
of a few emails.

### Ge'ez tooling survey, first experiment, access playbook — 2026-07-29

**A P-1 violation found and corrected.** DEC-007 specified building a
consonant–vowel decomposition layer. Nobody had checked a package registry
first. **It already exists.**

**Experiment 001 — the project's first empirical result**

`experiments/001-epitran-geez-decomposition/` measured **Epitran**
(`epitran` 1.35.2, MIT-Modern-Variant, actively maintained) against DEC-007's
four requirements. It ships **`tir-Ethi`**, a dedicated Tigrinya map.

| Criterion | Result |
| --- | --- |
| Decomposition | ✅ ካተበ → `katəbə` → root `[k,t,b]`, pattern `[a,ə,ə]` |
| Coverage | ✅ 384/384 core Ethiopic characters |
| Tigrinya-specific | ✅ 59/384 (15.4%) differ from Amharic, correctly |
| Lossless reversibility | ❌ 384 chars → 362 outputs; **22 collisions** |

Mean symbol expansion **1.97×**. The committed `run.py` was re-executed and
reproduces exactly (**P-5** satisfied by verification, not assertion).

**The failure was the most useful result.** The 22 collisions are precisely the
historically redundant Ge'ez homophone pairs (ሀ/ኀ → `hə`, ሠ/ሰ → `sə`) — which
means **the lossiness performs orthographic normalisation for free.** Good for
matching and retrieval; wrong for user-facing output. One representation cannot
serve both.

**DEC-007 amended** to a **dual-representation** architecture:
- **Surface form** — original Ge'ez, preserved verbatim, source of truth for
  output.
- **Analysis form** — Epitran decomposition, for matching/morphology/retrieval.
  Lossy by design; that loss is normalisation.
- **Alignment offsets** between them — now the only part we build.
- The reversibility requirement is **withdrawn as unachievable**, and never
  reconstruct surface text from the analysis form.

Cost of the substrate drops from days–weeks to `pip install`. Three more
alternatives rejected (R-016 … R-018).

**HornMorpho: partially resolved, and riskier than assumed**
- `[verified]` **Not on PyPI** — GitHub-only, hand-built wheel, no standard
  versioning. A real integration cost under **P-7**.
- `[reported]` v5.3.5 covers Tigrinya, but docs say *"Version 5 replaces Version
  4.5 for Amharic. For other languages, see Version 4.3"* — **Tigrinya support
  may lag.**
- **A `fgaim/HornMorpho` fork exists** — same group as our primary model
  candidates. Investigate the fork before upstream.
- Licence still unknown; GitHub is unreachable from this session.

**Other clean tooling found:** `abyssinica` (MIT — Ge'ez numerals, Ethiopic
calendar), `amseg` (MIT — Ge'ez-script segmentation, UHH-LT), `pyicu` /
`unicodedata2` (Unicode normalisation). Confirmed dead-end: `morfessor`, last
released 2019-07-31.

**New leads:** HornMT corpus; `tigrinyanlp.github.io` (**blocked by egress**).

**`docs/research/RESEARCH_ACCESS.md` — new**

Roughly a third of the previous session's research effort went into discovering
*how to reach sources* rather than reading them. That is now written down: which
hosts are blocked, which routes work (`hf://` filesystem for papers and cards;
PyPI directly, including installing and measuring libraries), the evidence-marking
convention, and a standing verification backlog.

`AI_RESEARCH_RULES.md` gained two rules from this session's failures: read the
access playbook before searching, and **check package registries before assuming
you must build something.**

### Phase 2 critical path + Phase 1 verification — 2026-07-29

**Verification pass corrected two published figures.** A follow-up reached
primary artefact sources through the **Hugging Face filesystem API**
(`hf://models`, `hf://datasets`, `hf://papers`), which is not subject to the
egress block on arxiv and publisher domains. Four corrections to the Phase 1
ecosystem report, recorded in its verification addendum:

- **TiQuAD baselines are F1 56–62, not 81%.** mBERT F1 58.6 / XLM-R F1 62.4
  (validation). The state of the art for Tigrinya QA is lower than first
  recorded.
- **TiQuAD's test split is not public** — request-gated to prevent
  contamination. DEC-005 amended with the operational consequence.
- **TiQuAD is Eritrean-sourced** (Eritrean Ministry of Information, *Hadas
  Ertra*), so under DEC-004 **Ethiopian-variety QA evaluation is an open gap**,
  not a balanced pair.
- **TiQuAD's upstream copyright is unresolved** — its authors state they do not
  own the source-article copyright, which is used under fair use "for academic
  research purposes only" with CC-BY-SA-4.0 applied on top. **A genuine P-9 risk
  for infrastructure use.** Legal review required; referred to `11_business`.

**Newly verified facts**
- **The Tigrinya data ceiling is 40M tokens** — TiRoBERTa, the strongest
  available encoder, was pretrained on that. This is the number
  `03_data_strategy` must plan against.
- **TIGQA** — a *second*, distinct Tigrinya QA dataset (2.68K pairs, 122 topics,
  537 paragraphs from textbooks). Educational domain; complements TiQuAD's news.
- arXiv 2509.20209 abstract verified: a custom tokenizer **"substantially
  outperforms"** zero-shot baselines, Bonferroni-corrected with human
  validation — independent corroboration of A-007.

**`02_linguistics` complete — the critical path**

`reports/02_linguistics/001-morphology-script-and-tokenization.md` + summary
`003`. **A-007 confirmed, and its mechanism identified:**

Tigrinya is templatic *and* agglutinative, so triconsonantal roots are
**discontinuous**. The Ge'ez abugida **fuses consonant and vowel into a single
character** (26 × 7 ≈ 182 characters). Therefore **a morpheme boundary can fall
inside one character**, and no subword tokenizer operating on raw Ge'ez can
represent it — a representational limit, not a tuning problem. Byte-level BPE
does not help, since UTF-8 bytes carry no consonant/vowel decomposition.

- **DEC-007** — consonant–vowel decomposition as the substrate beneath
  tokenization, with morpheme-aware vocabulary layered on top and raw-Ge'ez
  subword retained as a measured baseline.
- **Transliteration is reclassified as core infrastructure**, not a peripheral
  user-facing feature, because other services depend on the decomposition.
- Three further alternatives rejected (R-013 … R-015).

**Honesty note carried into the decision:** evidence on whether morphology-aware
tokenization improves *downstream accuracy* is mixed — MoVoC found no
significant MT gain; 2509.20209 found substantial gains from a different
intervention. DEC-007 claims only the defensible benefits (token efficiency,
linguistic fidelity) and requires accuracy to be measured.

### Phase 1 research complete — 2026-07-29

The first two research domains were executed and documented. **This changed the
plan**, and the change is the most important entry in this file so far.

**Reports and summaries added**
- `docs/research/reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md`
  + summary `001-tigrinya-nlp-ecosystem-scan.md`
- `docs/research/reports/00_project_definition/001-scope-users-and-dialect.md`
  + summary `002-scope-users-and-dialect.md`
- `docs/research/references/` populated: `papers.md`, `models.md`,
  `datasets.md`, `projects.md`, `communities.md`, `commercial.md`

**The finding that changed the plan**

Most of the Tigrinya model layer we intended to build **already exists**. One
group (GeezLab / `fgaim`) has published a coherent stack — base language models,
an Apache-2.0 `sentence-transformers` embedding model, POS tagging, NER data,
human-annotated QA data. Meanwhile **no** Tigrinya API, MCP server, SDK, or
production morphology service exists anywhere.

The gaps are at the **bottom** (Ge'ez normalisation, tokenization, morphology)
and the **top** (API, MCP, SDKs) of the stack — not in the middle. This inverts
the naive build order and is now recorded as A-010.

**Decisions recorded**
- **DEC-002** *(Proposed — needs owner confirmation)* — primary users are
  application developers; researchers secondary.
- **DEC-003** — adopt the existing model layer; build primitives, evaluation,
  and integration.
- **DEC-004** — support both Tigrinya varieties; evaluate and report separately.
  Grounded in a measured dialect gap (COMET 0.82 Ethiopian vs 0.80 Eritrean).
- **DEC-005** — FLORES-200 and TiQuAD as initial evaluation anchors.
- **DEC-006** — the minimum viable platform is the primitives layer, **not**
  translation.

Nine alternatives rejected with reasons (R-004 … R-012).

**Assumptions updated**
- **A-006 partially invalidated** — more human-annotated Tigrinya evaluation
  data exists than assumed (FLORES-200, TiQuAD, TiALD). Narrowed: we must still
  build evaluation sets for retrieval, morphology, spell, and grammar, where
  nothing was found.
- **A-007 supported, confidence raised** — morphology-aware tokenization reduced
  one Tigrinya sentence from 21 tokens to 6. *But* the same source reports no
  significant downstream translation gain, so the benefit is cost and fidelity,
  not assumed accuracy.
- **A-009 escalated to an active blocker** — several key reuse candidates carry
  no stated licence.
- **A-001, A-004 supported.** **A-010 added.**
- Two previously-open scope questions closed (users, dialect); register scope,
  language pairs, deployment model, and diaspora needs remain open.

**Blocking items surfaced**
1. Licence resolution on the `fgaim` models — blocks DEC-003.
2. HornMorpho maintenance status — now on the critical path via DEC-006.
3. DEC-002 owner confirmation.

**Evidence limitation — recorded prominently**

The session's egress policy blocked `arxiv.org`, `aclanthology.org`, publisher
domains, and `api.semanticscholar.org` at the proxy. Hugging Face Hub data is
`[verified]` against the API; **all paper-derived figures are `[reported]` from
search-engine summaries and were not read from source.** This is flagged in both
summaries, both reports, and `references/README.md`. Re-verification is a
standing action item.

### Added — 2026-07-29

Initial repository scaffold and research operating system.

- Root documents: `README.md`, `PROJECT_CONTEXT.md`, `CONTRIBUTING.md`,
  `CHANGELOG.md`, `.gitignore`.
- **Vision layer** (`docs/vision/`): mission, goals, non-goals, success metrics,
  and engineering principles.
- **Research operating system** (`docs/research/`):
  - `README.md` defining the Scout → Analyst → Architect protocol.
  - `AI_RESEARCH_RULES.md` — mandatory operating rules for AI assistants,
    written to prevent duplicated research and unfounded recommendations.
  - `CHECKLIST.md` — the nine questions every research report must answer.
  - Four templates: research report, summary, decision, experiment.
  - Thirteen report domains (`00_project_definition` … `12_master_blueprint`),
    each with a scoping README.
  - `summaries/` and `references/` as the compressed, read-first layer.
- **Decision system** (`docs/decisions/`): `DECISIONS.md` with a fixed record
  format, `rejected_options.md`, and `assumptions.md` seeded with the project's
  standing assumptions.
- **Architecture placeholders** (`docs/architecture/`): system, data, ML, API,
  MCP, and infrastructure documents, each explicitly marked as un-designed and
  gated on research.
- **Benchmark layer** (`docs/benchmarks/`): evaluation strategy, datasets, and
  metrics scaffolds.
- **Roadmap horizons** (`docs/roadmap/`): 30 days, 90 days, 6 months, 1 year,
  2 years.
- **Working directories** with READMEs: `datasets/`, `models/`, `services/`
  (eleven capability services), `sdk/`, `infrastructure/`, `experiments/`,
  `scripts/`.

### Notes on this change

The tree specification placed the project under a
`tigrinya-language-intelligence/` root directory. That root is mapped onto the
repository root rather than nested inside it, since the repository *is* the
project. All paths below it match the specification exactly.

**No research was conducted, no technology evaluated, and no architecture
designed as part of this change.** Every technical document added is a scaffold
that explicitly states it contains no findings. This was deliberate: the
workspace is built before the research so that the research has somewhere
disciplined to land.
