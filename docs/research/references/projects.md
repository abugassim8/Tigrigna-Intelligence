# References — Open Source Projects

---

### HornMorpho

- **Type:** Project (library) · **Link:** https://github.com/hltdi/HornMorpho
- **Maintainer:** HLTDI (Indiana University)
- **Relevance:** **Direct — critical path**
- **Summary:** Morphological analysis, segmentation, **and generation** for
  Amharic, Oromo, and Tigrinya. Rule-based. Yields grammatical features plus
  stem and affixes.
- **Verdict:** **Very useful — the only established Tigrinya morphological
  analyser found.** But see risk below.
- ⚠️ **Maintenance status UNVERIFIED.** GitHub was not reachable in the
  2026-07-29 session. A single-lab academic project is a classic abandonment
  risk, and this sits on our critical path.
  **Verifying this is a top action item.**
- **Licence:** Not verified.
- **⚠️ Update 2026-07-29:** `[verified]` **not published on PyPI** — GitHub-only
  distribution via a hand-built wheel (`HornMorpho-5.3.5-py3-none-any.whl` in
  `dist/`). No standard versioning or dependency resolution; a real integration
  cost under **P-7**. `[reported]` v5.3 covers Amharic, Oromo, Tigrinya, Tigre —
  but documentation states *"Version 5 replaces Version 4.5 for Amharic. For
  other languages, see Version 4.3,"* so **Tigrinya support may lag.**
  **A fork exists at `fgaim/HornMorpho`** — same group as our primary model
  candidates; investigate the fork before upstream.

### TiQuAD

- **Type:** Project + dataset · **Link:** https://github.com/fgaim/TiQuAD
- **Relevance:** Direct · **Licence:** CC-BY-SA-4.0 (per HF dataset card)
- **Verdict:** **Useful** — the QA benchmark, ACL 2023 Outstanding Paper.

### flores-OLDI (FLORES+)

- **Type:** Project · **Link:** https://github.com/avidale/flores-OLDI
- **Relevance:** High — MT evaluation
- **Summary:** Community-maintained continuation of the FLORES MT benchmark
  under the Open Language Data Initiative.
- **Verdict:** **Useful** — likely access route for the Tigrinya FLORES split.
- **Note:** `[reported]` there is published work on *correcting* FLORES for four
  African languages (arXiv 2409.00626) — check whether Tigrinya is among them
  before trusting the split blindly.

### Morfessor

- **Type:** Project · **Relevance:** Low
- **Verdict:** **Not useful as a starting point.** `[reported]` unsupervised
  statistical segmentation performs **poorly** on Tigrinya compared to
  linguistic rule-based approaches. Recorded so the experiment is not repeated
  (**P-13**).

### Epitran — **adopted** (DEC-007)

- **Type:** Project (PyPI: `epitran` 1.35.2) · **Licence:** MIT-Modern-Variant
- **Link:** https://github.com/dmort27/epitran · **Last release:** 2026-06-18
- **Relevance:** **Direct — the DEC-007 analysis substrate**
- **Summary:** Transcribes orthography to IPA across 158 language maps,
  **including a dedicated `tir-Ethi` Tigrinya map** (plus `-pp`, `-red`).
- **Measured** (`experiments/001`): 59/384 characters differ from Amharic and do
  so correctly (pharyngeal ħ, uvular q); ካተበ → `katəbə` yields root `[k,t,b]`;
  **22 collisions → not reversible**; 1.97× mean expansion.
- ⚠️ **"384/384 Ethiopic coverage" was recorded here and is misleading**
  (corrected 2026-08-19). Experiment 001 counted **non-empty output**. Of the 384
  core characters, **310 transliterate to phonemes and 74 pass through** — 26
  unassigned and 29 punctuation/digits, both correct, but **16 real syllables and
  3 combining marks come back as raw Ge'ez**. Supplement, Extended-A and
  Extended-B are **entirely unmapped**. This is why DEC-022 declares the analysis
  form **non-phonemic**.
- ⚠️ **Do not decompose for tokenization** (`experiments/002`). BPE on
  epitran-decomposed text produced **worse** fertility than raw Ge'ez in **10 of
  10** configurations — mean **+0.190 tokens/word, ~8% worse**. DEC-007's
  token-efficiency rationale was withdrawn on that evidence.
- ⚠️ **Output depends on text arbitrarily far away** (`experiments/005`).
  Transliterating a whole line differs from transliterating word by word on
  **4.53%** of tokens, and the trigger is not local context — for a word at index
  72 of a 128-word line, replacing the line's **first** word flips the result.
  Deterministic, but not statable as a phonological rule, so we transliterate
  **word by word** to get an answer that is a function of the word alone.
  Reporting this upstream is **A-16**.
- **Verdict:** **Very useful — adopted**, with three caveats above. Replaces a
  layer we planned to build. ⚠️ Not reversible; must be paired with surface-form
  preservation. **Whether its phonemes are correct is unknown** — that needs a
  speaker (**A-13**), and no automated check can substitute.

### abyssinica

- **PyPI:** `abyssinica` 2.0.0 · **MIT** · 2024-01-01 ·
  https://github.com/ebenh/abyssinica
- **Summary:** Locale library for **Eritrea and Ethiopia**. Ge'ez ↔ Arabic
  numeral conversion, Ethiopic ↔ Gregorian calendar.
- **Verdict:** **Useful** — numeral handling is a genuine normalisation need.
  Also surfaced the **HornMT** corpus lead.

### amseg (Amharic Segmenter)

- **PyPI:** `amseg` 2.3 · **MIT** · 2023-05-03 ·
  https://github.com/uhh-lt/amharicprocessor
- **Summary:** Amharic sentence/word segmentation and normalisation, from UHH-LT
  (Hamburg). Part of the "Semantic Models for Amharic" project.
- **Verdict:** **Useful reference implementation** — same script; Tigrinya
  transfer plausible. Study its normalisation rules.

### fidel

- **PyPI:** `fidel` 0.1.0 · **NO LICENCE STATED** ⚠️ · 2024-09-17 ·
  https://github.com/nypava/Fidel
- **Summary:** Ge'ez ↔ Latin transliteration with autocorrect (via symspellpy).
- **Verdict:** **Blocked on licence (P-9).** v0.1.0, Amharic-oriented examples.
  Revisit if licensing is clarified.

### etnltk (Ethiopian NLP Toolkit)

- **PyPI:** `etnltk` 0.0.22 · **NO LICENCE STATED** ⚠️ · 2022-05-17
- **Verdict:** **Weak** — pre-1.0, stale, unlicensed. Not a dependency candidate.

### pyicu / unicodedata2

- `pyicu` 2.16.2 (MIT, 2026-03-20) · `unicodedata2` 17.0.1 (Apache-2.0, 2026-02-12)
- **Verdict:** **Useful** — Unicode normalisation, collation, and current Ge'ez
  block data. Both actively maintained.

### HornMT

- **Link:** https://github.com/gebre/HornMT `[reported]`
- **Summary:** "A machine-learning corpus for the Horn of Africa region",
  referenced by `abyssinica`.
- **Verdict:** **Unassessed lead** → `03_data_strategy`.

### tigrinyanlp.github.io

- **Link:** https://tigrinyanlp.github.io — a Tigrinya NLP resource hub with a
  corpus page.
- **Verdict:** **High-value target, BLOCKED** by egress policy (403). See
  `../RESEARCH_ACCESS.md`.

---

## Not found

- No open source **Tigrinya API server**, **MCP server**, or **SDK**.
- No open source **Tigrinya spell checker** library (consumer apps exist — see
  `commercial.md`).
- No open source **Tigrinya grammar checker**.
- No open source **Tigrinya knowledge graph** or entity-linking tooling.

**This absence is the project's opportunity** and is the basis of DEC-003.
