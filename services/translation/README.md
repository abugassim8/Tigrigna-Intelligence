# `tigrinya-translate`

English → Tigrinya translation, behind an interface you can test without a model.

## Why this exists

**No model had ever been loaded in this project.** Eleven experiments, a
measurement harness and twenty-nine decisions were built around scoring a
translation system, and none had ever scored one. This package and
`scripts/translate_tico19.py` close that.

The product is **English → Tigrinya health information**, and TICO-19 —
committed here since 2026-09-02 — is COVID/medical prose with an English source
and three independent Tigrinya references. The anchor was already the right one.

## ⚠️ Not NLLB

**DEC-011** quarantines every NLLB variant: they are CC-BY-NC-4.0 and are
*"never present in a shipped artefact"*. NLLB is behind essentially every
published Tigrinya MT number, which makes it the tempting default and the one a
tool real people use may not be built on.

The baseline is **`google/madlad400-3b-mt`** — Apache-2.0, covers `ti`, chosen
by DEC-011 with its *"Tigrinya quality unmeasured"* written down at the time.

`test_the_model_is_not_nllb` fails if `MODEL` is ever pointed at an NLLB
checkpoint, because that breach would otherwise be invisible: the code would
work perfectly.

## The interface

```python
Translator = Callable[[list[str]], list[str]]     # cf. morphology.Analyser
```

A translator takes English segments and returns the same number of Tigrinya
ones. `MadladTranslator` is one implementation; tests and plants inject stubs.

This mirrors `tigrinya_primitives.morphology.Analyser` and for the same reason:
**a test suite that needs a 12 GB download is a test suite that stops being
run.** Everything except the model call itself is covered here.

```python
from tigrinya_translate import translate_all
from tigrinya_translate.translate import MadladTranslator

out = translate_all(["Wash your hands often."], MadladTranslator())
```

## The language token — verified, and the gate stays anyway

`LANGUAGE_TOKEN = "<2ti>"`. ✅ **Verified 2026-09-15** against the Hub's
`tokenizer.json`: MADLAD's language tokens are ordinary Unigram vocab pieces
from index 4, sorted alphabetically, and `"<2ti>"` sits between `<2tet>` and
`<2tiv>`. It was an unchecked guess for a day; it is not now.

⚠️ **The gate is not removed, and removing it would be the mistake.** The value
is verified for *this checkpoint*. An unknown prefix does not fail — it becomes
ordinary text, and the model emits *some* language, fluently, with the right
segment count and a perfectly scoreable chrF. That failure is invisible to every
other check here, so `MadladTranslator` checks the token against **the
tokenizer's own vocabulary** at load time and refuses to run if it is absent,
naming what is accepted; `scripts/translate_tico19.py` then checks the *output*
for Ethiopic script and aborts without writing if it is not there.

⚠️ **The gate nearly failed the other way, which is the more interesting risk.**
`tokenizer_config.json` has `"additional_special_tokens": []` and
`tokenizer.json` has `"added_tokens": []`. Had the `<2xx>` prefixes been split
into subwords rather than being real vocab entries, `get_vocab()` would not
contain `"<2ti>"` and this check would have **rejected a valid token and blocked
the run** after an 11.8 GB download — a check firing on correct input, which is
how checks get switched off. They are real pieces, so it does not.

## Installing

```bash
pip install -e "services/translation[dev]"        # interface + tests, no model
pip install -e "services/translation[madlad]"     # adds transformers + torch
```

`transformers` and `torch` are **optional on purpose**. They are not
dependencies of an interface.

On CPU with 16 GB, load in `bfloat16` (~6 GB); float32 is ~12 GB and will
thrash. Decoding is greedy so a re-run reproduces — beam search would score
better and make the artefact non-reproducible, which DEC-016 treats as the worse
trade.

## Running the measurement

```bash
python3 scripts/translate_tico19.py --self-test
python3 scripts/translate_tico19.py --json PATH --sheet PATH
```

The first needs no model and no network. The second downloads **11.76 GB**
(`model.safetensors`, 11,761,587,872 bytes) plus ~21 MB of tokenizer, and takes
tens of minutes on CPU for 100 segments.

⚠️ **Set `HF_TOKEN` first.** An unauthenticated Hub request is throttled hard —
measured at **57 kB/s**, which is about **47 hours** for this download. With a
token it is minutes. The project has had one since **A-08** (2026-09-03);
`pip install hf_transfer` and `HF_HUB_ENABLE_HF_TRANSFER=1` help further, and a
partial download resumes from the cache, so an interrupted fetch costs nothing.

⚠️ The three GGUF files in the same repo (965 MB / 1.26 GB / **1.65 GB** at Q4)
are **not** fetched by `transformers`. Using one means a different runtime
(llama.cpp or candle) and, because quantisation changes the output, **a
different measurement** — recorded as one, never swapped in silently.

⚠️ **chrF is not the finding.** Experiment 011 measured two professional human
translators agreeing with each other at **chrF ≈ 24** on this same data, so the
scale is not the one intuition suggests. The finding is the judgement sheet, and
the threshold — **fewer than 40 of 100 usable retires the approach** — is
recorded in the artefact before any output exists.

---

## The gates this service had to pass

⚠️ This README replaced a **scoping document** that had stood since the
repository was initialised, headed *"Status: not designed, not implemented."*
That document listed four preconditions for implementing this service and asked
to be replaced by the real design once they were met. They were met — and
checking rather than assuming is the point:

| Gate | Status |
| --- | --- |
| Research in `04_model_strategy/` and `03_data_strategy/` complete, **with a summary** | ✅ summaries `007-translation-model-selection.md` and `005-corpus-inventory-and-contamination.md` |
| A decision recorded covering the approach | ✅ **DEC-011** — MADLAD-400-3B; NC-licensed models quarantined |
| An evaluation method exists — *"a capability is not built before there is a way to measure it"* (**P-4**) | ✅ **DEC-009** chrF, and the `tigrinya_eval` harness |
| Independently runnable and testable (**P-11**) | ✅ own `pyproject.toml`, own tests, no repo-internal imports |

**Not built, from that document's expected layout:** `config/` and a
`Dockerfile`. Neither is needed to answer the question this service exists to
answer, and adding empty scaffolding is what the original document was.

## Commitments carried over

These were recorded before any of this existed and still bind:

- **Report confidence, and be honest when output is unreliable.** The two
  language gates above are the first instance; the judgement sheet is the
  second.
- **Expose quality per language pair.** Only English → Tigrinya is measured.
  Tigrinya → English is *not* implemented and must not be assumed to work.
- ⚠️ **"A BLEU score alone will not be sufficient evidence."** Still true, and
  now sharper: chrF alone is not either. Experiment 011 showed two human
  translators scoring ≈ 24 against each other, which is why the pre-committed
  threshold is a human judgement count and not a metric.
- **Reuse before training (P-1, P-2).** This service evaluates an existing
  multilingual model on Tigrinya rather than trusting its multilingual average
  — which is exactly what the measurement produces.
- **Parallel data availability is likely the binding constraint.** Untested.
  It becomes the live question only if the judgement sheet clears 40.

**Document-level input** and **Tigrinya → English** remain unimplemented.
