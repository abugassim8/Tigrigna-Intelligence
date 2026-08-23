# Ge'ez-Script Tooling Survey and the HornMorpho Question

| Field | Value |
| --- | --- |
| **Report ID** | `002-geez-tooling-survey` |
| **Domain** | `02_linguistics` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/004-geez-tooling-survey.md` |
| **Experiment** | `experiments/001-epitran-geez-decomposition/` |
| **Related decisions** | DEC-007 (amended as a result) |

---

## Objective

Resolve two standing blockers:

1. **Is HornMorpho maintained?** It is the only established Tigrinya
   morphological analyser and sits on the critical path via DEC-006.
2. **Does tooling already exist for DEC-007's consonant–vowel decomposition
   layer**, or must we build it?

Prompted by the observation that the previous session had assumed "build" for the
decomposition layer without first checking package registries — a **P-1**
failure on my own part.

---

## Finding 1 — HornMorpho: partially resolved, and the news is mixed

GitHub is unreachable from this session (see `RESEARCH_ACCESS.md`), and
`add_repo` refuses cross-owner attachments. So this was answered indirectly.

| Question | Answer | Confidence |
| --- | --- | --- |
| Published on PyPI? | **No.** Not under `hornmorpho` or `HornMorpho` | `[verified]` |
| Latest version | **5.3.5**, distributed as a wheel in the repo's `dist/` folder | `[reported]` |
| Tigrinya supported? | **Yes** — v5.3 covers Amharic, Oromo, Tigrinya, **and Tigre** | `[reported]` |
| Actively maintained? | **Unresolved** | — |
| Licence | **Unknown** | — |

### Three things that matter

**a) Not on PyPI is itself a finding.** GitHub-only distribution with a
hand-built wheel means no versioned releases through standard channels, no
dependency resolution, and a heavier integration and maintenance burden than the
"just adopt it" framing assumed. Under **P-7** (prefer boring technology) this
counts against it.

**b) ⚠️ Tigrinya support may lag Amharic.** Documentation states *"Version 5
replaces Version 4.5 for Amharic. For other languages, see Version 4.3."* If
Tigrinya users are directed to an older branch, the newest version's improvements
may not apply to us. **This must be verified before adopting.** `[reported]`

**c) `fgaim/HornMorpho` exists — a fork by GeezLab.** The same group behind our
primary reuse candidates (DEC-003) maintains a HornMorpho fork. This is a
strong signal: they likely hit the same integration issues, and their fork may be
the Tigrinya-relevant line of development. **Investigate the fork before the
upstream.**

**Net:** HornMorpho remains the leading candidate but is **not** the low-risk
adoption the previous report implied. Version confusion, unclear licensing, and
non-standard distribution are real integration costs.

---

## Finding 2 — Ge'ez tooling already exists on PyPI

The previous session assumed the decomposition layer had to be built. **It did
not check.** All rows `[verified]` from the PyPI JSON API, 2026-07-29.

| Package | Version | Last release | Licence | What it does | Verdict |
| --- | --- | --- | --- | --- | --- |
| **`epitran`** | 1.35.2 | **2026-06-18** | MIT-Modern-Variant | Orthography → IPA, 158 language maps **including `tir-Ethi`** | **Adopt — see Finding 3** |
| `abyssinica` | 2.0.0 | 2024-01-01 | **MIT** | Locale library for **Eritrea and Ethiopia**; Ge'ez ↔ Arabic numerals, Ethiopic calendar | **Useful** — numerals are a real normalisation need |
| `amseg` | 2.3 | 2023-05-03 | **MIT** | Amharic sentence/word segmentation and normalisation, from UHH-LT (Hamburg) | **Useful reference** — same script, Tigrinya transfer plausible |
| `fidel` | 0.1.0 | 2024-09-17 | **NOT STATED** ⚠️ | Ge'ez ↔ Latin transliteration, with autocorrect via symspellpy | **Blocked on licence**; v0.1.0, examples are Amharic |
| `etnltk` | 0.0.22 | 2022-05-17 | **NOT STATED** ⚠️ | "Ethiopian NLP Toolkit", spaCy/NLTK-inspired | **Weak** — pre-1.0, stale, unlicensed |
| `pyicu` | 2.16.2 | 2026-03-20 | MIT | ICU wrapper — Unicode normalisation, collation | **Useful** for normalisation and sorting |
| `unicodedata2` | 17.0.1 | 2026-02-12 | Apache-2.0 | Latest Unicode character data | **Useful** — Ge'ez block coverage |
| `morfessor` | 2.0.6 | **2019-07-31** | BSD | Unsupervised morphological segmentation | **Confirmed dead-end** — 7 years stale, and already rejected (R-007) |

**Two new leads surfaced from package descriptions:**
- **HornMT** (`github.com/gebre/HornMT`) — "a machine-learning corpus for the
  Horn of Africa region", referenced by `abyssinica`. → `03_data_strategy`.
- **`tigrinyanlp.github.io`** — a dedicated Tigrinya NLP resource hub with a
  corpus page. **Blocked by egress**, but recorded as a high-value target.

---

## Finding 3 — Epitran implements DEC-007's substrate. Verified by experiment.

Full record: `experiments/001-epitran-geez-decomposition/` (reproducible; the
committed `run.py` was re-executed and reproduces exactly).

Epitran ships **`tir-Ethi`**, a dedicated Tigrinya map (plus `-pp` and `-red`
variants). Tested against DEC-007's four requirements:

| Criterion | Result | Detail |
| --- | --- | --- |
| **Decomposition** | ✅ **PASS** | ካተበ → `katəbə`; consonants `[k,t,b]`, vowels `[a,ə,ə]`. **The discontinuous K-T-B root becomes extractable.** |
| **Coverage** | ⚠️ **QUALIFIED** | **384/384** produce output, but that is **not phoneme coverage** — corrected 2026-08-19. Only **310 of 384** transliterate to phonemes; 74 pass through, of which **16 real syllables and 3 combining marks** are genuinely unmapped (DEC-022). "Zero gaps" was wrong |
| **Language specificity** | ✅ **PASS** | **59/384 (15.4%)** differ from Amharic, and correctly: ሐ → `ħə` (Tigrinya pharyngeal) vs `hə`; ቀ → `qə` (uvular) vs `kʼə` (ejective) |
| **Reversibility** | ❌ **FAIL** | 384 chars → **362** distinct outputs. **22 collisions.** Round-trip is lossy |

Mean symbol expansion: **1.97×**.

### The failure is the most useful result

The 22 collisions are **exactly the historically redundant Ge'ez homophone
pairs** — ሀ/ኀ both → `hə`, ሠ/ሰ both → `sə`, and so on. Characters phonemically
distinct in ancient Ge'ez that merged in modern pronunciation.

**That is precisely the orthographic-variation problem** flagged as open in
`02_linguistics/001`. So the same property that breaks reversibility
**performs orthographic normalisation for free**:

- **Matching, search, retrieval, embeddings** — collapsing ሀ/ኀ is *exactly
  right*. Two spellings of one word should match. Here the lossiness is the
  feature.
- **Text returned to a user** — spell-correction output, transliteration display
  — collapsing is *wrong*; we cannot reconstruct the correct spelling.

**One representation cannot serve both.** That is the architectural conclusion,
and it is what amends DEC-007.

---

## Alternatives Considered

**A — Build the CV decomposition layer ourselves** *(the previous DEC-007 plan)*.
Rejected as the primary path: Epitran already does it, with better Tigrinya
phonology than we would encode unaided, under MIT, actively maintained. Building
would have been a **P-1** violation made out of not checking.

**B — Adopt Epitran wholesale as the single representation.** Rejected: not
reversible, so any user-facing text output would be corrupted.

**C — Adopt Epitran for analysis; keep surface text alongside.** **Recommended.**
Gets the decomposition and free normalisation without losing the ability to
return correct text.

**D — Use `fidel` for transliteration.** Deferred: no stated licence (**P-9**),
v0.1.0, Amharic-oriented examples. Revisit if licensing is clarified.

---

## Cost Analysis

| Item | Before this report | After |
| --- | --- | --- |
| CV decomposition layer | Days–2 weeks to build | **~0 — `pip install epitran`** |
| Tigrinya phonological mapping | Weeks of linguistic work | **Already done, 384 chars** |
| Orthographic normalisation | 1–2 weeks | **Partly free** (22 homophone pairs collapse automatically) |
| Surface↔analysis alignment | Not previously scoped | **Days — new work this creates** |
| Morphological analyser | Days if HornMorpho works, else months | Unchanged; HornMorpho riskier than assumed |

**Net: this report removes more work than it adds.** The main new obligation is
the alignment layer, which is smaller than what it replaces.

Runtime cost: pure-CPU table lookup, negligible. The 1.97× expansion is the real
consideration — it feeds tokenizer fertility budgeting.

---

## Build vs Buy Decision

| Component | Verdict | Change |
| --- | --- | --- |
| CV decomposition | **Buy — `epitran` (MIT)** | ⬅ was *build* |
| Tigrinya phonological map | **Buy — `tir-Ethi`** | ⬅ was *build* |
| Ge'ez numerals, Ethiopic calendar | **Buy — `abyssinica` (MIT)** | new |
| Unicode normalisation | **Buy — `pyicu` / `unicodedata2`** | new |
| Ge'ez-script segmentation reference | **Study `amseg` (MIT)** | new |
| **Surface↔analysis alignment** | **Build** | **new — our work** |
| Reverse mapping (analysis → Ge'ez) | **Do not build** | Ambiguous by construction; preserve surface instead |
| Morphological analysis | **Evaluate `fgaim/HornMorpho` fork first** | refined |

---

## Recommended Approach

**Amend DEC-007 to a dual-representation architecture.** Confidence: **high** for
the decomposition finding (measured), **medium** for HornMorpho (indirect).

1. **Surface form** — original Ge'ez, preserved verbatim, always. Source of truth
   for anything returned to a user.
2. **Analysis form** — Epitran `tir-Ethi` decomposition. Used for matching,
   morphological analysis, retrieval, and embeddings. Lossy by design; that loss
   is normalisation.
3. **Alignment offsets** maintained between them, so analysis results map back
   onto surface spans.
4. **Never reconstruct surface text from the analysis form.**

---

## Implementation Plan

1. Amend DEC-007. ✅ *done*
2. Sweep the remaining three Ethiopic Unicode blocks for Epitran coverage.
3. Evaluate `tir-Ethi-pp` and `tir-Ethi-red` variants.
4. Build the surface↔analysis alignment layer. *(The main new work.)*
5. Measure tokenizer fertility: decomposed vs raw Ge'ez — the MoVoC comparison
   on our own data.
6. Investigate `fgaim/HornMorpho`, then upstream; resolve the v5.3-vs-v4.3
   Tigrinya question and the licence.
7. Check `abyssinica` and `amseg` for directly reusable normalisation logic.
8. **Native-speaker validation of the IPA mapping before anything ships
   user-facing.**

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Epitran's Tigrinya map has errors we cannot detect | Medium | **High** — silently wrong everywhere downstream | Native-speaker validation before shipping; it is a small table and reviewable |
| Epitran maintenance lapses | Low | Medium | MIT-licensed, small data tables — forkable |
| The 22-collision normalisation is sometimes wrong | Medium | Medium | Surface form is always preserved; nothing is destroyed |
| HornMorpho Tigrinya support lags Amharic | **Medium-high** | High | Verify before adopting; check the `fgaim` fork |
| 1.97× expansion hurts tokenizer fertility | Medium | Medium | Measure it — step 5 |
| Over-trusting a single tool for a core primitive | Medium | High | Keep raw-Ge'ez baseline; the substrate is swappable |

---

## Open Questions

- Is `fgaim/HornMorpho` more current than upstream for Tigrinya?
- Does Epitran cover the Supplement / Extended / Extended-A blocks?
- Is `tir-Ethi` validated by a Tigrinya speaker, or derived from a grammar?
- What is HornMorpho's licence?
- What does `tigrinyanlp.github.io` list? (Blocked.)
- What is in HornMT?

---

## References

1. `experiments/001-epitran-geez-decomposition/` — the measurements
2. PyPI JSON API — `epitran`, `abyssinica`, `amseg`, `fidel`, `etnltk`,
   `morfessor`, `pyicu`, `unicodedata2`, accessed 2026-07-29 `[verified]`
3. Epitran — https://github.com/dmort27/epitran (MIT-Modern-Variant)
4. `abyssinica` — https://github.com/ebenh/abyssinica (MIT)
5. `amseg` — https://github.com/uhh-lt/amharicprocessor (MIT)
6. HornMorpho — `hltdi/HornMorpho`; fork `fgaim/HornMorpho` `[reported]`
7. HornMT — `github.com/gebre/HornMT` `[reported]`, not yet examined

---

## Checklist

- [x] **What exists?** Epitran with a real Tigrinya map; `abyssinica`; `amseg`; `pyicu`; `fidel`; `etnltk`. HornMorpho, GitHub-only.
- [x] **What can be reused?** Epitran for decomposition **(measured)**, `abyssinica` for numerals/calendar, `pyicu` for Unicode normalisation, `amseg` as a segmentation reference.
- [x] **What should be built?** Only the surface↔analysis alignment layer.
- [x] **What should not be built?** A CV decomposition layer from scratch; a reverse mapping; anything on `morfessor`.
- [x] **Cost estimate?** Net **negative** — removes more work than it adds. Runtime negligible.
- [x] **Maintenance burden?** Low: Epitran and `pyicu` are actively maintained and MIT. HornMorpho is the real exposure.
- [x] **Licensing?** Epitran MIT-Modern-Variant, `abyssinica`/`amseg`/`pyicu` MIT, `unicodedata2` Apache-2.0 — all clean. ⚠️ `fidel` and `etnltk` unlicensed; HornMorpho unknown.
- [x] **Technical risks?** Undetectable map errors; HornMorpho version confusion; expansion cost; single-tool dependence on a core primitive.
- [x] **Final recommendation?** Adopt Epitran as the analysis substrate under a dual-representation architecture; build only the alignment layer.

## Completion

- [x] Summary at `docs/research/summaries/004-geez-tooling-survey.md`
- [x] Experiment recorded and reproduced
- [x] DEC-007 amended
- [x] Rejected options logged (R-016 … R-018)
- [x] References updated
