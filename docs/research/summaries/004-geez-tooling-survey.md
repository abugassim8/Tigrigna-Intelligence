# Summary: Ge'ez-Script Tooling Survey and the HornMorpho Question

| Field | Value |
| --- | --- |
| **Summary ID** | `004-geez-tooling-survey` |
| **Full report** | `docs/research/reports/02_linguistics/002-geez-tooling-survey.md` |
| **Experiment** | `experiments/001-epitran-geez-decomposition/` |
| **Date** | 2026-07-29 |
| **Status** | Current |
| **Confidence** | High on Epitran (measured) · Medium on HornMorpho (indirect) |

**One-line answer:** The consonant–vowel decomposition layer DEC-007 said we
should build **already exists** — Epitran's `tir-Ethi` map, MIT-licensed and
actively maintained — so we adopt it for analysis, keep the original Ge'ez
alongside for output, and build only the alignment between them.

---

## Key Findings

- **Epitran ships `tir-Ethi`, a genuine Tigrinya map.** Measured, not claimed
  (`experiments/001`): `[verified]`
  - **Decomposition ✅** ካተበ → `katəbə` → consonants `[k,t,b]`, vowels
    `[a,ə,ə]`. **The discontinuous K-T-B root becomes extractable** — exactly
    what DEC-007 required.
  - **Coverage ⚠️** — ~~384/384, zero gaps~~ **corrected 2026-08-23.** That counted
  *non-empty output*. Only **310 of 384** produce phonemes; **16 real syllables
  and 3 combining marks** come back as raw Ge'ez, and three whole blocks are
  unmapped. This is why DEC-022 declares the analysis form non-phonemic.
  - **Language-specific ✅** 59/384 (15.4%) differ from Amharic, *correctly*:
    ሐ → `ħə` (Tigrinya pharyngeal) vs Amharic `hə`; ቀ → `qə` (uvular) vs `kʼə`
    (ejective). Real Tigrinya phonology, not an Amharic alias.
  - **Reversibility ❌** 384 chars → 362 outputs. **22 collisions. Round-trip is
    lossy.**
- **The reversibility failure is the most useful result.** The 22 collisions are
  exactly the Ge'ez homophone pairs (ሀ/ኀ → `hə`, ሠ/ሰ → `sə`) — historically
  distinct, now identically pronounced. **That is the orthographic-variation
  problem, and Epitran normalises it for free.** Good for matching; wrong for
  user-facing output. **One representation cannot do both.**
- **Mean symbol expansion 1.97×** — the cost side; feeds tokenizer fertility.
- **HornMorpho is riskier than assumed.** `[verified]` it is **not on PyPI** —
  GitHub-only, hand-built wheel, no standard versioning. `[reported]` v5.3.5
  covers Tigrinya, but docs say *"Version 5 replaces Version 4.5 for Amharic.
  For other languages, see Version 4.3"* — **Tigrinya support may lag.** Licence
  unknown.
- **`fgaim/HornMorpho` is a GeezLab fork.** The same group behind our other
  reuse candidates forked it — investigate the fork before upstream.
- **Other clean MIT tooling exists:** `abyssinica` (Ge'ez numerals, Ethiopic
  calendar, Eritrea+Ethiopia), `amseg` (Ge'ez-script segmentation, UHH-LT),
  `pyicu` + `unicodedata2` (Unicode normalisation).
- **Confirmed dead-end:** `morfessor` last released **2019-07-31**. R-007 stands.
- **Two new leads:** **HornMT** corpus (`github.com/gebre/HornMT`) and
  `tigrinyanlp.github.io` (a Tigrinya NLP hub — **blocked by egress**).

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| **DEC-007 amended** — dual representation: adopt Epitran for analysis, preserve surface Ge'ez, build only the alignment layer | DEC-007 | Amended |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Build the CV decomposition layer ourselves *(the original DEC-007 plan)* | Epitran already does it, with better Tigrinya phonology than we would encode unaided, MIT, maintained. Building it would have been a **P-1 violation caused by not checking a package registry** |
| Adopt Epitran as the *single* representation | Not reversible — any user-facing text output would be corrupted |
| Build a reverse mapping (analysis → Ge'ez) | Ambiguous by construction: 22 outputs have two valid sources. Preserve the surface form instead |
| Use `fidel` for transliteration | **No stated licence** (P-9); v0.1.0; Amharic-oriented. Revisit if clarified |
| Adopt HornMorpho as low-risk | Not on PyPI, licence unknown, possible Tigrinya version lag. Still the leading candidate — but not a free win |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Epitran Ethiopic **phoneme** coverage | **310 of 384** chars — *corrected; the 384/384 figure counted non-empty output* | `[verified]` measured |
| Distinct IPA outputs | **362** (22 collisions) | `[verified]` measured |
| tir vs amh divergence | **59/384 = 15.4%** | `[verified]` measured |
| Mean symbol expansion | **1.97×** | `[verified]` measured, n=7 |
| Epitran language maps | 158 | `[verified]` |
| Epitran / licence / last release | 1.35.2 · MIT-Modern-Variant · 2026-06-18 | `[verified]` |
| HornMorpho latest | 5.3.5, **not on PyPI** | `[reported]` / `[verified]` |
| Morfessor last release | **2019-07-31** | `[verified]` |
| Cost to build CV layer | **~0 — `pip install epitran`** (was: days–2 weeks) | — |

## Recommended Next Steps

1. Sweep the other three Ethiopic Unicode blocks for Epitran coverage.
2. Evaluate `tir-Ethi-pp` and `tir-Ethi-red` variants.
3. **Build the surface↔analysis alignment layer** — the one piece that is ours.
4. Measure tokenizer fertility: decomposed vs raw Ge'ez (the MoVoC comparison,
   on our data).
5. Investigate `fgaim/HornMorpho`; resolve the v5.3-vs-v4.3 Tigrinya question
   and the licence.
6. **Native-speaker validation of the IPA map before anything ships.**

## References

1. `experiments/001-epitran-geez-decomposition/` — measurements, reproducible
2. PyPI JSON API, accessed 2026-07-29 `[verified]`
3. Epitran — github.com/dmort27/epitran (MIT-Modern-Variant)
4. `abyssinica` (MIT) · `amseg` (MIT, UHH-LT)
5. HornMorpho — `hltdi/HornMorpho`, fork `fgaim/HornMorpho`

---

**Open questions / uncertainty:** Is Epitran's `tir-Ethi` speaker-validated or
grammar-derived? **We cannot currently detect systematic errors in it** — the
main risk, since it would be silently wrong everywhere downstream. HornMorpho's
licence, maintenance, and Tigrinya version status remain unresolved because
GitHub is unreachable from this session (see `RESEARCH_ACCESS.md`).
