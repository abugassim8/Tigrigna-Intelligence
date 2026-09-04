# `tigrinya-primitives` — Tier 0

Ge'ez normalisation, tokenization, and transliteration for Tigrinya.
**The first working code in this repository.**

```bash
pip install -e ".[dev]"
pytest            # 61 property tests, no gold standard required
```

```python
from tigrinya_primitives import normalise, transliterate, GeezTokenizer

normalise("ፀሓይ")                      # 'ጸሓይ'  — orthographic variants collapse

a = transliterate("ሰላም ዓለም")
a.surface                              # 'ሰላም ዓለም'  — verbatim, always
a.analysis                             # 'səlam ʕaləm'
[(s.start, s.end, s.surface) for s in a.spans]
                                       # [(0, 4, 'ሰላም'), (5, 9, 'ዓለም')]
a.analysis_is_phonemic                 # False — declared, not implied
```

## What this is and is not

| Capability | Status |
| --- | --- |
| Ge'ez orthographic normalisation | ✅ working |
| Ge'ez → phoneme transliteration, word-aligned | ✅ working |
| Subword tokenization (raw Ge'ez, byte-level BPE) | ✅ working |
| **Morphological analysis** | ⚠️ **implemented, dependency not bundled** — needs a user-installed HornMorpho (**DEC-028**) |

Morphology is implemented as an **adapter, not a dependency**. HornMorpho is the
only established Tigrinya analyser, and its licence is **GPL-3.0** `[verified]`
from its `LICENSE.txt`. That is worse than unresolved for our
purposes — **DEC-020 chose Apache-2.0 precisely because no dependency imposed
copyleft**, and GPLv3 cannot be redistributed under Apache-2.0.

`morphology.is_available()` returns `False` unless you installed it, so callers
degrade rather than crash. **DEC-028 made that the permanent design** rather
than a placeholder:

```bash
pip install git+https://github.com/hltdi/HornMorpho
python -c "import hm; hm.download('ti')"     # not optional — separate download
```

Both lines are needed, and `is_available()` checks both: `import hm` succeeds on
a fresh install with no language packs, and HornMorpho then returns `None` for
every word rather than raising. Mapped naively that reads as "this corpus has no
morphology", so the adapter treats it as a broken install and says so.

| | |
| --- | --- |
| **You may** | install HornMorpho yourself and get morphology; run it behind a hosted API |
| **We may not** | depend on it, vendor it, or ship it inside a container image |

The asymmetry is real and not a technicality: HornMorpho is **GPL-3.0, not
AGPL-3.0**, so network use is not distribution. We can run it for you; we cannot
hand it to you. It is also **not on PyPI**, so it could not be a dependency in
any case.

## Design, and why

Every choice here traces to a decision that was **measured**, not assumed.

**Tokenization runs on raw Ge'ez, not decomposed phonemes** (DEC-007 amendment 2).
BPE over Epitran-decomposed text was **worse in 10 of 10 configurations and 5 of 5
folds** — about 8% worse fertility. Ge'ez already encodes consonant+vowel per
character, which is the structure BPE would otherwise have to learn.

**Alignment is word-level, not character-level** (DEC-023). Character alignment is
*measurably impossible*: only **23.89%** of words align, because Ge'ez 6th-order
characters are ambiguous between "consonant + ɨ" and a bare consonant and epitran
resolves that from neighbours — context supplies **16.3%** of output symbols. But
word spans are **exact by construction** — the analysis form *is* the
concatenation. ⚠️ They are **not** fully faithful to epitran's running-text
output: that claim rested on a containment test and is retracted (DEC-023
Amendment 1). Measured by exact equality, word-by-word matches running text for
**95.47%** of tokens; word-by-word is correct because the running-text form
depends on text arbitrarily far away and so cannot be a stable contract.

**Offsets are code points, and the unit is stated in the response** (DEC-022).
Ethiopic Extended-B lies above the BMP, so JavaScript `.length` and Python `len`
disagree about the same string — silently, and only on rare characters.

**The analysis form is declared non-phonemic.** 19 real Ethiopic characters pass
through untransliterated and three blocks are entirely unmapped, so a consumer
assuming IPA would be silently wrong.

## Measured footprint

⚠️ **113.4 MB — higher than DEC-013's 72 MB estimate**, and that estimate
*included* morphology, which is not built.

| Component | Marginal RSS |
| --- | ---: |
| normalisation | ~0 (pure `str.translate`) |
| tokenization (`tokenizers`) | **4.3 MB** |
| **transliteration (`epitran` → `panphon`)** | **107.4 MB** |

**One dependency is the entire budget.** `epitran` loads `panphon`'s phonological
feature tables on instantiation. That is why `transliterate.py` loads it lazily:
importing this package costs **6.8 MB**, and you pay the rest only if you
transliterate.

DEC-013's arithmetic is corrected accordingly. By its own logic — tier by
resource profile — normalisation+tokenization (~15 MB) and transliteration
(~107 MB) are arguably different tiers; lazy loading makes that a per-use cost
rather than a resident one.

## Evaluation

`tests/test_properties.py` is the P-4 evaluation, made executable. **61 property
tests, no gold standard**: idempotence, determinism, reversibility, alignment
integrity, coverage, contract enforcement.

**They caught a real bug on the first run.** `test_tokenizer_round_trips_unseen_text`
failed: byte-level BPE only learns bytes it *sees*, so unseen bytes became
`[UNK]` and `decode()` mangled ordinary Tigrinya the tokenizer had not been
trained on — which would have broken DEC-022's verbatim-surface guarantee in
production on the first unusual word. Fixed by passing
`initial_alphabet=ByteLevel.alphabet()`. **"Byte-level means reversible" is only
true when the alphabet is complete.**

### What these tests do not do

**They catch *broken*, not *wrong*.** A transliterator that deterministically
returns the wrong phoneme passes every one of them. Phonemic and morphological
accuracy need gold data and a native speaker (**A-07**, **A-13**). A green suite
is not linguistic validation.

## Note on placement

`services/` is organised **one directory per capability**, which predates
**DEC-013** and is the decomposition DEC-013 explicitly rejected in favour of
resource tiers. This package is the Tier 0 *tier*, so it spans what the scaffold
calls `tokenizer/`, `morphology/`, and part of `spellcheck/`. Reconciling the
directory layout with DEC-013 is outstanding.
