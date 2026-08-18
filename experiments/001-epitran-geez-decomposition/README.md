# Experiment 001 — Epitran as the Ge'ez consonant–vowel decomposition substrate

| Field | Value |
| --- | --- |
| **Experiment ID** | `001-epitran-geez-decomposition` |
| **Date** | 2026-07-29 |
| **Status** | Complete |
| **Related report** | `docs/research/reports/02_linguistics/002-geez-tooling-survey.md` |
| **Related decision** | DEC-007 (amended as a result) |

---

## Question

Does an existing, maintained, openly-licensed tool already implement the
consonant–vowel decomposition of Ge'ez that DEC-007 requires — and does it meet
DEC-007's stated requirement of being **deterministic and losslessly
reversible**?

## Hypothesis

*Recorded before running.* **Epitran** (`epitran`, MIT-Modern-Variant, actively
maintained — last release 2026-06-18) transcribes orthography to IPA. Because
IPA represents consonants and vowels as separate symbols, transcribing Ge'ez to
IPA should inherently decompose the consonant–vowel fusion that DEC-007
identifies as the core problem.

**Expected:** Epitran has a Tigrinya map, and it separates the triconsonantal
root from its vowel pattern.

**Uncertain in advance:** whether the mapping is reversible, and whether a
Tigrinya map exists at all as distinct from Amharic.

## Success Criteria

*Pre-committed.*

1. **Decomposition** — a Tigrinya map exists and separates C from V. Success:
   ካተበ yields a form from which the root {k, t, b} is extractable.
2. **Coverage** — ≥95% of the core Ethiopic block (U+1200–U+137F) maps to
   non-empty output.
3. **Language specificity** — `tir-Ethi` is genuinely distinct from `amh-Ethi`,
   not an alias. Success: >0 characters differ, and differences are
   linguistically motivated.
4. **Reversibility** — the mapping is injective, so Ge'ez → IPA → Ge'ez is
   lossless. Success: zero colliding outputs.

## Setup

- **Package:** `epitran` 1.35.2 (PyPI, MIT-Modern-Variant), installed in a clean
  venv. No other dependencies used.
- **Python:** 3.x system interpreter, fresh `venv`.
- **Data:** none external — the Unicode Ethiopic block U+1200–U+137F swept
  exhaustively, plus seven hand-chosen Tigrinya words.
- **Randomness:** none. Fully deterministic; no seed required.

### Command to reproduce

```bash
python3 -m venv .v && . .v/bin/activate
pip install epitran==1.35.2
python3 run.py   # see run.py in this directory
```

## Method

1. Enumerated Epitran's bundled language maps; searched for Ge'ez-script maps.
2. Swept U+1200–U+137F through `tir-Ethi`, recording output coverage.
3. Compared `tir-Ethi` against `amh-Ethi` character-by-character over the same
   range.
4. Transcribed seven Tigrinya words; measured symbol expansion.
5. Extracted consonants vs vowels from the K-T-B example.
6. Built the inverse map to count collisions.

## Results

### Maps present
`amh-Ethi`, `amh-Ethi-pp`, `amh-Ethi-red`, **`tir-Ethi`**, `tir-Ethi-pp`,
`tir-Ethi-red` — out of 158 language maps total. **A dedicated Tigrinya map
exists.**

### 1. Decomposition — ✅ PASS

```
ካተበ  (3 Ge'ez chars)  ->  katəbə  (6 IPA symbols)
   consonants: ['k', 't', 'b']   <- the discontinuous triconsonantal root
   vowels    : ['a', 'ə', 'ə']   <- the templatic pattern
```

**The K-T-B root is now extractable as a contiguous consonant sequence.** This is
the exact operation DEC-007 called for, working on the canonical example.

### 2. Coverage — ✅ PASS

**384 / 384 characters mapped, 0 unmapped (100%).** Exceeds the 95% criterion.

### 3. Language specificity — ✅ PASS

**59 of 384 characters (15.4%) differ between `tir-Ethi` and `amh-Ethi`**, and
the differences are linguistically correct:

| Char | `tir-Ethi` | `amh-Ethi` | Linguistic basis |
| --- | --- | --- | --- |
| ሐ | `ħə` | `hə` | Tigrinya preserves the Semitic **pharyngeal** fricative that Amharic merged to glottal |
| ቀ | `qə` | `kʼə` | Tigrinya **uvular** vs Amharic **ejective** |
| ሧ | `sʷa` | `swa` | Labialisation encoded as a modifier vs a segment |

This is genuine Tigrinya phonological knowledge, not an Amharic alias.

### 4. Reversibility — ❌ **FAIL**

| Metric | Value |
| --- | --- |
| Distinct Ge'ez chars mapped | 384 |
| Distinct IPA outputs | **362** |
| Colliding outputs | **22** |
| Characters lost to collision | **22** |

The forward map is **many-to-one**. Round-trip Ge'ez → IPA → Ge'ez is **lossy**.

**But the collisions are not arbitrary.** They are precisely the historically
redundant Ge'ez homophone pairs:

```
'hə' <- ሀ ኀ        'sə' <- ሠ ሰ
'ha' <- ሃ ኃ        'sa' <- ሣ ሳ
's'  <- ሥ ስ        'sʷa' <- ሧ ሷ    … (22 total)
```

These characters were phonemically distinct in ancient Ge'ez and have merged in
modern pronunciation.

### 5. Symbol expansion

| Word | Ge'ez chars | IPA symbols | Factor |
| --- | --- | --- | --- |
| ትግርኛ | 4 | 8 | 2.00× |
| ካተበ | 3 | 6 | 2.00× |
| ሰላም | 3 | 5 | 1.67× |
| ኤርትራ | 4 | 8 | 2.00× |
| መንእሰይ | 5 | 9 | 1.80× |
| ዓቕሚ | 3 | 7 | 2.33× |
| ተራእዩ | 4 | 8 | 2.00× |

**Mean expansion ≈ 1.97×.** Decomposition roughly doubles sequence length — the
cost side of the ledger, and a real input to tokenizer fertility budgeting.

### ⚠️ Refinement — 2026-08-03, from `07_api_mcp`

**"Coverage 384/384" is true, and it does not mean what it looks like.**

This experiment counted characters producing **non-empty** output. Measured
again by *what* the output is:

| Outcome | Count |
| --- | ---: |
| Transliterated to phonemes | **310** |
| Passed through as the character itself | **74** |
| Empty | 0 |

Of the 74 pass-throughs: **26 unassigned** code points and **29
punctuation/digits** (both correct to pass through), but **16 real syllables**
(HOA, QOA, XOA, KOA, WOA, YOA, GOA, TZOA, and the DD- series) and **3 combining
marks** (gemination, vowel length) return as raw Ge'ez.

Outside the core block the pass-through is **total** — Ethiopic Supplement,
Extended-A, and Extended-B are entirely unmapped.

**Consequence:** the DEC-007 analysis form is a **mixed string, not a phoneme
string.** Recorded in **DEC-022** as an explicit API contract clause, because a
consumer expecting phonemes would mishandle these silently.

Nothing here contradicts the original run, which scoped to `ETHIOPIC_CORE` and
reported non-empty output honestly. **The implication was simply never drawn.**

---

## Analysis

**Three of four criteria pass decisively. The fourth fails — and the failure is
the most useful result.**

The 22 collisions are exactly the ሀ/ኀ and ሠ/ሰ-type pairs that are
**pronounced identically in modern Tigrinya but written differently**. That is
the primary source of the orthographic variation flagged as an open question in
`02_linguistics/001`.

So the same property that breaks reversibility **performs orthographic
normalisation for free**:

- **For matching, search, retrieval, and embeddings** — collapsing ሀ/ኀ is
  *exactly what we want*. Two spellings of the same word should match. Here the
  "lossiness" is the feature.
- **For text transformation output** — spell-correction suggestions,
  transliteration display, anything returned to a user — collapsing is
  **wrong**, because we cannot reconstruct the correct spelling.

**These are two different requirements, and one representation cannot satisfy
both.** That is the architectural conclusion.

## Conclusion

**Hypothesis confirmed for decomposition; refuted for reversibility.**

Epitran `tir-Ethi` is a viable, maintained, MIT-licensed implementation of
DEC-007's decomposition substrate — but it **cannot be the whole answer**,
because DEC-007 as written requires lossless reversibility and Epitran does not
provide it (no reverse mapping ships, and the forward map is not injective).

**Recommended architecture — dual representation:**

1. **Surface form** — original Ge'ez, preserved verbatim, always. The source of
   truth for any output returned to a user.
2. **Analysis form** — Epitran-derived CV decomposition, used for matching,
   morphological analysis, retrieval, and embeddings. Lossy by design, and that
   loss is normalisation.

Alignment offsets between the two must be maintained so analysis results can be
mapped back onto surface spans. **Do not attempt to reconstruct surface text
from the analysis form.**

This changes DEC-007 from "build a reversible decomposition layer" to "adopt
Epitran for analysis, keep surface text alongside" — which is both cheaper and
more correct. DEC-007 has been amended.

## Threats to Validity

- **Seven test words** is a small sample for the expansion measurement. The
  coverage and collision results are exhaustive over the block and are not
  affected.
- **Tested only the core Ethiopic block** (U+1200–U+137F). The Supplement,
  Extended, and Extended-A blocks were not swept — those carry characters for
  other Ge'ez-script languages and may behave differently.
- **No native-speaker validation** of the IPA output's accuracy. Epitran's
  Tigrinya map is trusted on its authorship and on the linguistic coherence of
  the tir/amh differences, not on independent verification.
- **`-pp` and `-red` variants untested.** These likely offer preprocessing and
  reduced representations that may change the picture.
- Epitran's own Tigrinya coverage claims were not cross-checked against a
  reference grammar.

## Next Steps

1. Amend DEC-007 for dual representation. ✅ *done*
2. Sweep the remaining three Ethiopic Unicode blocks.
3. Evaluate `tir-Ethi-pp` and `tir-Ethi-red`.
4. Build the surface↔analysis alignment layer.
5. Measure tokenizer fertility on the decomposed form vs raw Ge'ez — the
   MoVoC comparison, on our own data.
6. Get native-speaker validation of the IPA mapping before shipping anything
   user-facing.

## Reproducibility

- [x] Deterministic — no randomness, no seed needed
- [x] Version pinned — `epitran==1.35.2`
- [x] Data: Unicode block sweep, no external data
- [x] Exact command recorded
- [x] Hardware irrelevant (pure CPU, sub-second)
- [x] Script committed as `run.py`
