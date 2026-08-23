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

### Native-speaker validation instrument built — 2026-08-19

**A-13 goes from "find someone and work out what to ask" to "send them these
five sheets."** `validation/` holds a **134-item instrument, ~25 minutes**,
closing plan steps 1.1 and 1.2 — the only part of the correctness gap that could
be built without a speaker.

**Stratified, because a random sample wastes scarce expert time.** Each stratum
settles one open question and is independently analysable, so **partial
completion is still useful**:

| Sheet | Items | Settles |
| --- | ---: | --- |
| **1 · which is right** | 25 | **The word-final `ɨ`** — experiment 005 found two forms differing on 4.53% of tokens and could not tell which is correct → **DEC-025** |
| 2 · common words | 35 | Accuracy where it has the widest blast radius |
| 3 · spelling variants | 14 | Is collapsing ጸ/ፀ a matching aid or a **correction** of how someone chose to write? |
| 4 · random sample | 40 | **The only unbiased accuracy estimate** |
| 5 · which variety | 20 | Eritrean, Ethiopian or mixed → tests **DEC-010** |

**⭐ Forced choice with the answer hidden.** Sheet 1 shows both candidate forms
in randomised order with no indication of which we produce — asking "is our
output right?" invites agreement, asking "which is right?" does not. Verified:
our form sits in position 1 for 11 items and position 2 for 14. `key.json` holds
the mapping and **is never sent to the reviewer**.

**IPA was a barrier, so the key is generated from the corpus.** Our output uses
`ʔ ɨ ə ħ ʕ t͡sʼ`; a fluent speaker who is not a linguist has no reason to read
those. Every symbol is anchored to a real Ge'ez character that produces it. An
earlier version **omitted `ɨ` entirely** — the symbol appearing **1,419 times**
and the one sheet 1 is entirely about — because it is epenthetic and has no
single-character anchor. It now falls back to the shortest word containing it.

**`analyse.py` refuses the tempting number.** Accuracy is computed from sheet 4
only; sheets 1–3 select hard cases on purpose, so a rate over them would
describe our sampling rather than the transliterator. `unsure` is reported
separately and never folded into agreement. Tested end to end against a
simulated response, including an unparseable answer, which is reported rather
than dropped.

**Stratum D is empty by measurement, not omission** — coverage over Ethiopic
letters is 100% on this corpus, so there are no unmapped-letter words to review.
Recorded as an empty stratum in the manifest.

**The instrument was not reproducible at first.** `words` is a set, so
equal-count entries in the pronunciation key ordered by hash and the manifest
drifted between runs — two reviewers could not have been given provably
identical material. Fixed with a deterministic tie-break and now verified in CI
across two `PYTHONHASHSEED` values.

**A-13 is re-scoped and upgraded to blocking**, and `PROTOCOL.md` invites the
reviewer to say if this should be paid work rather than a favour.

### Readiness plan of record; README claimed no licence was chosen — 2026-08-19

**`docs/roadmap/READINESS_PLAN.md`** is now the execution plan. The horizon
documents (`30_days` … `2_years`) were written **before any research** and are
kept as direction, not sequence.

**What it settles:** "ready" is defined at three levels with **exit tests that
can be run**, rather than left to interpretation. Against v0.1 the project is at
**≈40%** — two of four Tier 0 capabilities, a harness nothing has run through,
and zero speaker validation.

**The five gaps that matter**, separated from the backlog: no native-speaker
validation (**G-1**), 14 checks enforcing nothing (**G-2**), hollow evaluation
anchors (**G-3**), nothing measured end to end (**G-4**), and an MVP incomplete
by DEC-006's own definition (**G-5**).

**⚠️ A-13 was too narrow and the plan says so.** It covered only a variety audit
of the evaluation anchors. What actually needs a speaker also includes: whether
the phonemes are right at all, the word-final `ɨ` disagreement experiment 005
could not settle (4.53% of tokens, and **we do not know which form is correct**),
and whether normalising ፀ→ጸ reads as a *correction* to Ethiopian-variety users.

**More stale front-door content, same class as the assumptions register.**
`README.md` said **"Licence: Not yet selected"** — sixteen days after DEC-020
chose Apache-2.0 / CC-BY-4.0 and both LICENSE files were committed. It also
cited "DEC-001 … DEC-008", listed completed research as next steps, called four
items blocking when three are, and **had no `pip install` line at all** despite
two installable packages. Fixed, with a real install-to-first-call path.

### Assumptions re-audited; a CI check that could not count — 2026-08-19

Clearing the debt the gap audit declared: **all ten assumptions re-audited**,
and the two benchmark documents never opened.

**⭐ A CI check that miscounted by design.** `LANG` and `LC_ALL` are unset, so
`wc -w` runs in the **C locale and cannot split UTF-8**: a 661-word Tigrinya
file counted as **30**. For summaries — full of em-dashes, ⚠️, × and Ge'ez
samples — it **undercounted by 3–4%**, making DEC-001's 1,200-word limit
systematically lenient, and **most lenient for the most Tigrinya-heavy
summaries**, which is exactly backwards. Counting moved to Python, and the fix
**immediately surfaced a real violation the broken check had been hiding**:
summary 011 was 1,207 words. Trimmed.

**The register was wrong about its own confidence, not the project's
direction** — which is the quieter failure. An assumption marked `Unvalidated`
invites re-testing; one wrongly marked `Supported — High` closes the question.

| | |
| --- | --- |
| **A-002** | Status said `Unvalidated` while its own body said "CONFIRMED by measurement" |
| **A-003** | `Unvalidated` — experiment 006 shows the accuracy/speed tension **does not arise for Tier 0** at 0.045 ms; it constrains Tier 2 only |
| **A-005** | `Unvalidated` — **DEC-017 had settled it**: from-scratch foreclosed, ladder with measured triggers |
| **A-008** | `Unvalidated` — measured: 82.8 vs 1,193.1 GB-h/month, ~14× saving, break-even 1,187 req/hour |
| **A-004** | Upgraded "achievable" → **demonstrated**: Tier 0 shipped with **zero trained models** |
| **A-010** | Primitives built, so half the differentiator claim is discharged — **two of four** named components exist |
| **A-009** | Sharpened: verification is harder than assumed — HF tags wrong on 2 of 4 datasets, PyPI's legacy field wrongly reads "NOT STATED" for five packages |
| **Deferred list** | Still called the project licence "Open, deliberately deferred" — **DEC-020 closed it sixteen days earlier** |

**`datasets.md` said "Status: none — no evaluation datasets have been
identified, assembled, or built"** while a screened FLORES+ sample was committed
and had already produced DEC-009. Now a real register — and it makes the
position legible: **one of DEC-005's two anchors is unusable and the other is a
30-sentence sample.** TiQuAD has confirmed contamination, no public test set
(**A-04**) and unresolved copyright (**A-06**); FLORES+ devtest needs egress
(**A-09**). That is easy to lose behind the phrase "FLORES-200 and TiQuAD as
evaluation anchors."

`evaluation_strategy.md` still said other capabilities were unresearched, which
DEC-023 ended.

### Gap audit: 12 findings, one shipping bug, four checks that could not fail — 2026-08-19

A deliberate adversarial audit across seven dimensions. **Every check was
re-tested by planting a violation**, rather than read.

**⭐ A live bug in shipped code.** `score(..., confidence_interval=False)`
returned an **inverted interval** — `ci_low=60.33, ci_high=58.33` around a score
of 59.33. sacrebleu sets `_ci = -1` as a "not computed" sentinel, and `if ci:`
is true for -1, so `score - (-1)` became the *lower* bound. The fallback path
declines bootstrapping on any backend error, so this was reachable in normal
operation. Found by an audit test asserting `ci_low <= score <= ci_high`.

**Four checks that could not fail:**

| Check | Defect |
| --- | --- |
| Contamination gate | An eval segment shorter than 8 words yields no n-grams. **A byte-identical copy of a 2-line eval set was reported `CLEARED for use`.** TiQuAD is QA; questions are routinely under 8 words |
| "Every report has a summary" | Fell back to matching the *domain* name, so one summary satisfied every report in its directory. A planted orphan report passed |
| DEC-015 "datasets carry a screening record" | **Zero records existed** for five committed corpora, and the CI job was *named* for the rule while only testing that the tool fails closed |
| Contamination detection | No positive control anywhere — the gate could regress to always-pass with CI green |

**Two gates that rejected legitimate data:**

- `screen_dataset.py` omitted **Ethiopic Extended-B**, so real Tigrinya carrying
  those characters failed the quality gate as *"likely mojibake"* at 1.444%.
  Three definitions of "is Ethiopic" existed; one was wrong.
- **Our own evaluation anchor failed its own gate.** `flores_ti.txt` scored
  0.629% "foreign" — the offending characters were **Latin letters in proper
  nouns**. Mojibake detection is now a separate signature test (replacement
  chars, C1 controls, Latin-1/Extended), so legitimate Latin passes while the
  known-corrupted sample still fails on its stray `ñ`.

**A false validation claim in the register P-4 gates on.** `metrics.md` listed
**morphological analysis** as `Validated: Yes — intrinsic`, citing experiment
004. Experiment 004 never tested morphology — `grep -ci morph` returns **0** —
and DEC-023 itself records its intrinsic properties as untested. The capability
is not implemented (**A-07**).

**A decided contract clause never implemented.** DEC-022 requires the serving
tier in every response; six of seven clauses were enforced and `tier` silently
was not. Worse, the previous commit's `api_architecture.md` asserted it as part
of the contract — a doc/code divergence introduced by the documentation pass.

**The assumptions register was frozen** from 2026-07-29 through six experiments
and sixteen decisions, while its stated purpose is recording status updates as
evidence arrives. **A-007** was marked Supported with confidence *raised to High*
on `[reported]` paper evidence — MoVoC's "21 BPE tokens versus 6" — that our own
`[verified]` measurement contradicts: experiment 002 found decomposition **~8%
worse**, 10/10 configurations. Now scoped and lowered to Medium. **A-006** still
counted TiQuAD as available evaluation data despite confirmed contamination, no
public test set, and unresolved copyright.

**Not everything suspected was real.** Experiment 004's normalisation figures
looked irreproducible until it turned out the experiment strips punctuation and
includes the English file — its numbers are internally consistent. Its private
`normalise()` agrees with the shipped one on every core-block character.
`GeezTokenizer.save`/`load` were untested but correct.

### Four architecture documents were empty scaffolds — 2026-08-19

`api_`, `mcp_`, `data_` and `ml_architecture.md` were still the original
templates — "Sections to be completed", and a decision log reading
***No decisions recorded*** — while their domains had **completed research and
accepted decisions**. Each closes with the line "an architecture document that
has drifted from reality is worse than none, because people trust it."

All four now record what is decided, drawn from the decision log and the
research, with blocked areas named rather than invented:

| Document | Now records | Still open |
| --- | --- | --- |
| `api_architecture` | DEC-022's contract with the **real implemented JSON**, the UTF-16/BMP offset trap, latency as part of the contract | Endpoint surface (**A-02**) |
| `ml_architecture` | Model inventory with licences, CTranslate2, the adaptation ladder, evaluation gates | Nothing measured (**A-09**) |
| `data_architecture` | The four screening gates, why they fail closed, the TiQuAD contamination, licence-by-artefact | Parallel data (**A-05**) |
| `mcp_architecture` | What DEC-012/022/023 already bind, and why uncertainty is **sharper** for MCP than HTTP | Whether MCP ships early (**A-02**) |

**The MCP point is worth keeping:** an application developer calling the HTTP API
can inspect a response; **a model calling an MCP tool cannot evaluate Tigrinya
output, and neither can the person reading its answer.** Degraded output has to
be structurally visible, not merely documented.

`infrastructure_architecture.md` had **two** decision logs — an empty template
one above its real content, and a populated one below. The empty one is gone and
the scaffold replaced with the areas genuinely still undone.

CI now fails if any architecture document carries an empty decision log.

### Derived counts checked too; the README was badly wrong — 2026-08-19

The figures register covers numbers that were *measured*. It does nothing for
counts **derived from the repository**, and those had rotted further:

| Document | Claimed | Actual |
| --- | --- | ---: |
| `README.md` | "four research domains complete", "Eight decisions recorded" | **13**, **24** |
| `PROJECT_CONTEXT.md` | "Four research domains complete" | **13** |
| `summaries/README.md` | "5 summaries, 1 experiment" | **15**, **6** |
| `013-state-of-play.md` | "11 of 12" domains, "21" decisions | **13**, **24** |

The README also still said **"no service code written"** with two tested
packages in the tree — the first paragraph a reader sees. All fixed, and
`check_figures.py` now derives four counts from the tree and flags any claim
that contradicts them. **Volatile counts are deliberately excluded**: test
totals change on almost every commit, so living documents say "both suites
passing" and exact numbers stay in dated CHANGELOG entries.

**⭐ The negative controls caught the check failing twice, in the same hour.**

1. The first control caught `**3** reproducible experiments` and **sailed past**
   `four research domains complete` and `Eight decisions recorded` — spelled as
   words, which is *verbatim* what the README said. The check would have missed
   the exact instance it was built for. → `_digitise()`
2. Sharing one marker vocabulary between both checks put `recorded` in scope for
   counts — and the claim is literally "N decisions recorded". **Every counts
   violation was suppressed and the control went green.** → separate
   `FIGURE_MARKERS` and `COUNT_MARKERS`, neither overlapping the phrasings it
   guards.

That makes **three checks in two days that looked correct and could not have
failed** on the case that motivated them, counting DEC-023's containment test.

**One limitation left in knowingly:** a marker on a neighbouring line suppresses
a genuine violation inside the 8-line window — verified with a bare "72 MB"
eight lines under an unrelated "recorded". Narrowing the window trades it for
false positives on existing retraction blocks, and a noisy check gets switched
off. **A net, not a proof.**

### Figures registered and machine-checked; 10 stale claims found — 2026-08-19

**Correcting a figure in one place and leaving it standing in others has now
happened four times out of four.** Each was found by hand, weeks apart, and each
sweep missed files the next one caught:

| Figure | Retired to | Files still asserting it |
| --- | --- | ---: |
| Tier 0 footprint **72 MB** | 113.4 MB | **5** |
| Tiering saving **22×** | ~14× | **4** |
| Preserved **1,639/1,639** | 95.47% | **3** |
| Coverage **99.72%** | 100.00% | **2** |

This sweep found live claims in `docs/architecture/system_overview.md` and
`infrastructure_architecture.md` — **files never touched by any of the
corrections that caused them**, still stating 72 MB and 22× as current. Ten live
claims fixed in total, including one inside DEC-023's own body, where the
retracted figure stood un-struck above its own amendment.

**`docs/figures.json`** now registers every load-bearing figure with its value,
basis, and retired predecessors; **`scripts/check_figures.py`** fails CI when a
retired figure appears without a retraction marker nearby. `--list` prints the
register, so it doubles as the answer to "what is X now, and what was it?"

**A negative control was planted and caught** — three violations in a scratch
file — before the check was trusted. A check nobody has seen fail is worth
nothing, which is the lesson experiment 005 taught the hard way.

**Stated limits, not buried:** the markers are heuristic and deliberately
generous, because a noisy check gets switched off and a switched-off check is
the DEC-008 failure this prevents. **It catches oversight, not intent**, and it
does **not** verify that current figures are correct — nothing re-derives a
measurement. → **DEC-024**

### Tier 0's latency measured; DEC-016 amended for experiments that measure time — 2026-08-19

Two inputs to the DEC-019 break-even model were **assumed**: cold start (a free
parameter, 1–60 s) and service time (~2 s). Tier 0 is built, so
`experiments/006-tier0-latency/` measured its half.

| Input | Assumed | Measured (Tier 0) |
| --- | --- | ---: |
| Cold start | 1–60 s | **3.03 s** |
| Service time | ~2 s | **0.045 ms** |
| Break-even | 58–1,200 req/hour | **1,187 req/hour** |

**98.7% of that cold start is `epitran` loading** — our own import is 40 ms. The
same dependency is 107.4 MB of the 113.4 MB footprint, so footprint and latency
independently point at one lever. The `lru_cache` is **238.7×**, which
experiment 005 had already shown to be sound.

⚠️ **This does not close A-14 and does not refute the 2 s figure.** A-14 asks
for **Tier 2**, which needs a model this environment cannot fetch (**A-09**),
and the 2 s was a Tier 2 assumption that Tier 0 says nothing about. What it
shows is that **the model swings ~20× on a guessed parameter** — and Tier 2's
is still guessed. Tier 0 is kept warm regardless, so nothing operational
changes.

**All four hypotheses confirmed, which is the weakest outcome so far.**
Experiments 002, 003 and 005 each refuted something. Here the thresholds
(< 5 s, < 50 ms, ≥ 10×) were cleared by one to four orders of magnitude — a
prediction beaten by 44,000× was not a real test. The magnitudes carry the
weight, not the verdicts.

**Code change:** lazy loading defers all 3.0 s onto the first caller, so
`tigrinya_primitives.warmup()` now exists for an always-warm service to call at
boot rather than being warm-except-once.

**DEC-016 Amendment 1** — a timing experiment cannot reproduce byte-identically,
which the original rule did not anticipate. `results.json` now declares
`"deterministic": true|false`; CI byte-compares the former and only requires the
latter to run and emit an artefact. **The stated cost is that a
non-deterministic experiment gets no drift detection**, so the flag is only for
genuinely variable quantities. Gating CI on a timing-derived verdict was
considered and rejected — a loaded runner would flip it, and a check that fails
for unrelated reasons is one people learn to ignore.

### Intrinsic evaluation for Tier 0, and DEC-023's supporting measurement retracted — 2026-08-18

**The evaluation service scored translation only — the one capability DEC-006
excludes.** That reproduced DEC-021's structural error in code: the MVP
primitives had a decision saying how to evaluate them (DEC-023a) and nothing
that did it. `tigrinya_eval.primitives` now implements all five intrinsic
properties over real text — idempotence, determinism, alignment integrity,
reversibility, coverage — plus a sixth that pins the finding below. It runs as
`python -m tigrinya_eval.primitives <corpus>`, exits non-zero on failure, and
CI runs it (**DEC-023a job**). **21 new tests; 96 across both packages.**

**Half those tests are negative controls** — each check is fed a broken
primitive and watched failing. That is not ceremony. The finding that prompted
this module was a verification that *could not fail*:

**DEC-023's central measurement was wrong, and experiment 005 retracts it.**
The decision recorded that a word's transliteration survives a sentence
**1,639/1,639 (100%)**. That came from a **containment** test
(`alone in in_context`), blind to an *appended* character — and an appended
word-final `ɨ` is **92%** of the actual failures. By exact equality it is
**95.47%** (2,255/2,362); containment reports 99.62%.

Worse than a boundary effect: the running-text form is **not a function of
local context**. The word alone, the word plus its next eight words, and six
preceding words plus the word all give `ʔɨzom`; the full 128-word line gives
`ʔɨzomɨ`, and replacing that line's *first* word — 72 words away — flips it.
Deterministic, but not statable as a phonological rule.

**The decision survives on a better argument.** Word-by-word is right not
because it is lossless (it differs on **4.53%** of tokens) but because
running-text output depends on arbitrarily distant text and so cannot give an
API a stable answer. Prepending is genuinely inert (**0 of 1,565**), which is
what makes the `lru_cache` sound. → **DEC-023 Amendment 1**

**The evidence had been seen and explained away.** The original report noticed
the word-final `ɨ` and dismissed it as "a boundary artefact" — three lines below
a 100% figure that said there was nothing to explain. Two numbers from two
different tests read as one consistent picture.

**Also corrected, same error twice more:** coverage was reported at **99.72%**,
diluted by five **digits**; restricted to Ethiopic characters it was 96.86%,
diluted by 197 **punctuation** marks. Over Ethiopic letters and marks — the
characters that should be transliterated — it is **100.00%**. And Tier 0's
footprint in the package docstring still read the pre-build estimate of 72 MB
against the measured **113.4 MB**.

Withdrawn figures were corrected **in place** in DECISIONS.md, the report, the
summary, `transliterate.py` and `types.py` — not appended, so nothing reads as
self-contradictory. **A-16** files the epitran behaviour upstream.

### CI extended to the packages; stale cost figures fixed in place — 2026-08-03

`ci/verify.yml` predated both packages and did not test either. It now runs
**`services/primitives` (61 tests)** and **`services/evaluation` (14 tests)** in a
matrix alongside the experiment-reproducibility and documentation jobs. Verified
locally; still awaiting install (**A-15**).

**The 22× corrections were appended rather than applied**, leaving the original
claims standing above them so the documents read as self-contradictory. Fixed in
place: the tier table, the counterfactual, and the finding heading now all carry
the measured figures (Tier 0 **113.4 MB**, saving **~14×**), with a single note
recording that 22× came from the pre-build estimate and should not be quoted.

**`013-state-of-play.md` said "nothing has been built"**, which stopped being
true two commits ago. Superseded with the current position: two packages, 75
tests, and two shipping bugs caught by those tests.

### Evaluation harness built; DEC-013 cost figures corrected — 2026-08-03

**`services/evaluation/` implements DEC-009 and DEC-010 as enforced code rather
than documented intent.** 14 tests passing.

Two rules are made structurally unbreakable. **BLEU cannot be obtained alone** —
`score()` always returns both metrics, because DEC-009 forbids reporting BLEU by
itself and the cheapest enforcement is to make the alternative unrepresentable.
**`aggregate()` raises** rather than warns, because a warning would be ignored
exactly when it mattered: our two DEC-005 anchors appear to be in different
varieties, so a combined score would describe a language nobody speaks.

Confidence intervals are on by default. On three sentences the harness reports
`chrF 59.33 [30.62, 88.05]` — which is the point, since a bare point estimate on
a small set looks authoritative and is not.

**A second real bug caught by tests:** sacrebleu returns numpy `float32`, which
is not JSON-serialisable, so `save()` would have failed the first time anyone
persisted a real evaluation run. Fixed at the source.

**DEC-013's cost figures corrected against the Tier 0 measurement.** Tier 0 is
113.4 MB rather than the estimated 72 MB, so the standing-cost saving from
tiering is **~14×, not 22×** — 82.8 GB-h/month against 1,193.1. The conclusion
is unchanged and the figure should no longer be quoted as 22×.

**Status: the harness works; no model has been run through it.** Model weights
are behind the egress block (A-09), so MADLAD-400-3B's Tigrinya quality — which
appears to be unpublished — remains unmeasured.

### DEC-021 answered: primitive evaluation; DEC-023 — 2026-08-03

**Most of the primitives layer is evaluable with no annotated data at all.**
Primitives differ from translation in a way that matters: much of their
correctness is a property of the *function* — idempotence, determinism,
reversibility, coverage, alignment integrity — rather than agreement with a
human. Only **accuracy** needs gold data.

Experiment 004 pre-committed four hypotheses; **three hold**: normalisation is
idempotent (0 failures), transliteration is deterministic (0 failures),
tokenization round-trips at **100.00%** with zero `[UNK]`. Coverage is **99.72%**
of character tokens. **P-4 is therefore satisfiable for Tier 0 today**, without
building the benchmark A-006 anticipated.

**⚠️ The fourth hypothesis failed, and found a real error in two accepted
decisions.** DEC-007 requires surface↔analysis alignment offsets and DEC-022 made
them an API contract clause — **both assumed character-level alignment, which is
measurably impossible at 23.89%.** `ር` transliterates to `r` alone but `rɨ`
inside ሃገርነት, because Ge'ez 6th-order characters are ambiguous between
"consonant + ɨ" and a bare consonant and epitran resolves that from neighbours.
Context supplies **1,375 of 8,430 output symbols — 16.3%**.

**The fix is granularity, not engineering — and the first reading was wrong.**
I framed it as a tradeoff between exact offsets and faithful phonemes; a
follow-up measurement refuted that **before it reached a decision record**.
⚠️ **That follow-up was itself wrong — corrected 2026-08-18, see below.** It
reported the word transliteration preserved in a sentence **1,639/1,639 (100%)**;
measured by exact equality it is **95.47%**. Word-level spans give exact
alignment; they do **not** give full fidelity against running-text output.

**DEC-023** records both: intrinsic-first evaluation, and word-level alignment
correcting DEC-007 and DEC-022. `metrics.md` now has validated rows for
tokenization, transliteration, and morphology.

**Stated plainly:** intrinsic checks catch **broken, not wrong**. A
deterministically incorrect transliterator passes all of them. **Morphology still
needs gold data** — but it is now one capability needing annotation rather than
four, which is what DEC-021 set out to establish. Embeddings remain untested.

### 07_api_mcp researched (partial); DEC-022 — 2026-08-03

**Less was blocked than claimed — for the second time.** I said
`04_model_strategy` was blocked on A-01 and it was not; the same test here gives
the same answer. **A-02 blocks the API *surface* — which endpoints, which SDKs,
whether MCP ships early — not the *contract*.** The contract is the part that is
expensive to change once consumers depend on it, and it was decidable today.

Three measurements drove **DEC-022**:

**⚠️ Ethiopic Extended-B (U+1E7E0–U+1E7FF) is above the BMP.** On three core
characters plus one Extended-B character, Python `len()` gives 4 and JavaScript
`.length` gives 5 — same string, different offsets, silently, on characters
unlikely to reach a test fixture. Absent from all five of our corpora, so a
contract risk rather than a live bug. Offsets are therefore **code points, with
the unit stated explicitly in the response.**

**✅ Ge'ez is normalisation-stable** — 0 of 384 core characters change under
NFC/NFD, so offsets do not shift under normalisation. An entire class of API bug
does not exist here, which is not true of many scripts.

**⚠️ DEC-007's analysis form is not guaranteed phonemic.** Its "384/384 coverage"
is true for *non-empty* output, but only **310** characters are transliterated;
**19 real characters** (16 syllables, 3 combining marks) return as raw Ge'ez, and
three non-core blocks are entirely unmapped. Not a contradiction of Experiment
001, which scoped to the core block honestly — **the implication was never
drawn.** Corrected in DEC-007, Experiment 001, and stated as a contract clause.

Also in the contract: **the 150× tier spread means endpoints cannot present
uniform latency** (one timeout either aborts translations or hangs on tokenize),
and **DEC-010 puts a mandatory variety label in the schema** with `unknown` as a
first-class value rather than a null.

**The surface remains undesigned** and waits on A-02. No API code should be
written before DEC-021's primitive evaluation, since P-4 applies to endpoints too.

### 12_master_blueprint — the synthesis; DEC-021 — 2026-08-03

**Reading eleven domains together surfaced something invisible from inside any
one of them.**

**P-4 gates capability work on evaluation existing. Evaluation exists for exactly
one capability — translation — which DEC-006 explicitly excludes from the minimum
viable platform.** Capabilities with a validated metric: **1**. Inside the MVP:
**0**. Translation has a metric, a licensed model, a runtime and a tier, while
every capability DEC-006 actually named has no way to tell whether it works.

**The root cause is structural, not a sequencing accident.** DEC-005 named
FLORES-200 (translation) and TiQuAD (QA) as anchors, and **neither evaluates
tokenization, morphology, transliteration, or embeddings**. DEC-005 and DEC-006
were taken the same day; each was sound alone, and together they left the MVP
unmeasurable — the exact failure `DECISIONS.md` warns about in its own preamble.

**DEC-021** extends the anchors to cover the MVP primitives and makes primitive
evaluation the next research. It is the only option that leaves both DEC-006 and
P-4 intact — and DEC-006 has since gained independent support it did not
originally have, since `05_architecture` found its MVP is also the cheapest tier
by 8.3×.

**Step 1 on the critical path is blocked by nothing** — no licence, no egress, no
human decision. Everything else waits on **A-01**, **A-02**, or **A-05**, none of
which any amount of research can resolve.

Also recorded honestly: **nothing has been built.** Three experiments, one
screening tool, one uninstalled CI workflow. 80% of summary claims carry
`[verified]`. And five method findings worth transferring — measurement beat
citation, pre-committed thresholds caught overclaiming twice, policy without
mechanism fails silently, metadata is evidence rather than truth, and the
corrections improved the evidence rather than weakening the conclusions.

### 11_business researched; DEC-020 — A-12 closed — 2026-08-03

**A-12 (the project licence) is resolved and the files are in place.** It had
been deferred pending A-01/A-05/A-06; the code licence turns out to depend on
none of them.

Every upstream licence is now verified, and **nothing forces copyleft on our
code**: all code dependencies are MIT or Apache-2.0, both adopted models are
Apache-2.0, and share-alike enters only through *data* — three of six datasets
are CC-BY-SA-4.0. Share-alike binds derivatives of that data, not source code.

**DEC-020** therefore licenses **by artefact class**: Apache-2.0 for code
(`LICENSE`, canonical text verified against installed copies rather than
transcribed), CC-BY-4.0 for documentation (`LICENSE-docs`), and **inherit
upstream** for data derivatives. `CONTRIBUTING.md` now states which class a
contributor is touching, because the data row is the one that catches people.

**⚠️ A licence false-negative caught.** PyPI's legacy `license` field reads
"NOT STATED" for `sacrebleu`, `sentence-transformers`, `fastapi`, `trl` and
`bitsandbytes` — under P-9 that is disqualifying, and recording it would have
wrongly rejected four dependencies including the metric implementation DEC-009
relies on. They are licensed; the values live in PEP 639's newer
`license_expression` field. Same shape as HF `size_categories` being wrong on 2
of 4 datasets: **a single metadata field is not a check.**

**On sustainability, the report deliberately contains no revenue model** — N-9
forecloses a commercial service for now. What it establishes instead is that
**money is not the binding constraint**: no training, no GPU, no orchestration,
and 52.6 GB-h/month for the always-warm tier. **What this project can die of is
maintainer attention** — fifteen `ACTIONS.md` items need a human and three are
blocking, none resolvable by further research. The action register is the real
risk register.

### 10_infrastructure researched; DEC-018, DEC-019 — 2026-08-03

**No dollar figures appear in this domain, deliberately** — vendor pricing is
unverifiable from this environment and volatile, so cost is modelled in
**GB-hours** and **break-even rates**, arithmetic that survives price changes.

**Tiering cuts standing resource cost 22×**: 52.6 GB-h/month for a warm Tier 0
against 1,162.9 GB-h/month for one merged always-warm process. DEC-013 was
decided on the memory spread and holds on cost too. ⚠️ **Superseded — Tier 0
measured at 113.4 MB, so the saving is ~14× (82.8 vs 1,193.1 GB-h/month). The
conclusion holds; 22× should not be quoted.**

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
