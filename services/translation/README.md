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

## ⚠️ Where these commands can run

| Command | Needs the model | Needs network | Sandbox / CI |
| --- | --- | --- | --- |
| `--self-test` | no | no | ✅ |
| `--smoke` | **yes** | first run only | ❌ |
| `--diagnose` | **yes** | first run only | ❌ |
| `--json … --sheet …` | **yes** | first run only | ❌ |

**`huggingface.co` is blocked by org egress policy in the assistant's
environment** — `CONNECT tunnel failed, response 403`. That is a standing policy,
not an outage to wait out, and installing `transformers` there does not help
because the weights themselves are behind the same 403.

So **every command in the bottom three rows runs on the owner's machine.** This
is written down because it was asked and answered three times in chat, which is
what a fact belonging in the repository looks like.

⚠️ **Do not add a CI job that runs them.** It would need an 11.8 GB download per
run and would be switched off within a week — the failure DEC-008 exists to
prevent, and the reason these are measurements rather than `experiments/`
entries.

## When something is wrong: one command, one report

```bash
python3 scripts/diagnose_environment.py
```

Writes `diagnostic-report.txt`. **Every stage runs in its own subprocess**, so a
native crash or an out-of-memory kill becomes a recorded line rather than ending
the run — the property the six-round-trip debugging session lacked, where a
silent exit destroyed the evidence each time.

⚠️ **Stage 2 is the decisive one and costs seconds.** It opens the checkpoint
with `safetensors.safe_open` and lists every `shared` / `embed_tokens` /
`lm_head` tensor with its shape, **without materialising 11.8 GB**.

⚠️ **Differing tensors are not the defect — that reading was backwards.** An
earlier version of this section said that if `shared.weight` and
`decoder.embed_tokens.weight` differ, the checkpoint is wrong. `config.json`
sets `tie_word_embeddings: false`, so the second matrix **is** the untied output
projection and differing is the *correct* state. The check would have fired on a
healthy file and sent the owner after a second 11.8 GB download — and
`jbochi/madlad400-3b-mt` is byte-identical to `google/` (all 13 files, same
sizes, same `config.json`, ✅ verified 2026-09-16), so that download never had
anything to offer.

What stage 2 is really counting is **how many** of the four matrices are there.
The Hub reports **2940.4M** parameters; the non-embedding parameters are
2,416,086,016 and one 256000×1024 matrix is 262,144,000, so 2940.4M fits exactly
**two** and no other count. HF's T5 wants four, so at least one is invented at
load time — see the next section.

It does not care which `transformers` is installed, so the report is useful even
when the environment is broken.

## ⚠️ The output projection is loaded, then thrown away

**This is why the decoder emitted one phrase repeated to `max_new_tokens`,
identical in every target language.** `lm_head` is not random. It is trained,
present in the checkpoint, loaded — and then discarded by a forced tie.

The checkpoint holds two embedding-shaped tensors and no `shared.weight`:

```
decoder.embed_tokens.weight   (256000, 1024) F32
lm_head.weight                (256000, 1024) F32
```

A tied model has no second matrix to store, so this checkpoint is untied **by
construction**. But `T5Config.__post_init__` in transformers 5.x says:

```python
# But in fact we tie weights always and force it to be `True`
self.scale_decoder_outputs = kwargs.pop("tie_word_embeddings", None) is not False
self.tie_word_embeddings = True
```

It repurposes `tie_word_embeddings` as a decoder-scaling hint and forces tying
on. The trained projection is loaded and overwritten, and the decoder projects
through the **input** embedding. (`scale_decoder_outputs` resolves correctly to
False here, so the scaling is right; only the tie is wrong.)

⚠️ **Do not decide this from `config.tie_word_embeddings`.** A check that did
reported `TRAINED — nothing is wrong here` on a model emitting noise, because
the loaded config reads `True` while `config.json` on disk says `false`. That
was the **twelfth** check found here that could not fail, and the third instance
of one error: **a declared flag is not an outcome**, after the dtype keyword and
a `major >= 5` version gate.

`head.py` decides from the checkpoint instead:

- **two or more embedding-shaped matrices in the file ⇒ untied**, whatever any
  config says. A tied model has nothing to store twice;
- if the head is also *random* — row norms all within a bound **derived from the
  matrix shape**, not hard-coded — that is caught too;
- it repairs **only** when the weights say so. An unconditional overwrite would
  corrupt a correctly-loaded model invisibly;
- it **refuses** (`RandomHeadError`) rather than scoring noise when the
  projection cannot be recovered;
- it records `head_state`, `head_repaired` and `head_source` in the artefact,
  because a score from a repaired model is **not the same measurement**.

```bash
python3 scripts/repair_lm_head.py --dry-run      # verdict only, changes nothing
python3 scripts/repair_lm_head.py                # repair, then translate with controls
python3 scripts/repair_lm_head.py --self-test    # no model, no network
```

⚠️ **Read the controls first.** Fluent Spanish and German mean the repair took.
Tigrinya being poor *after* that is a **finding** about coverage, not a bug — and
it is the finding this service exists to produce.

⚠️ Reported upstream as **A-22**. It is not MADLAD-specific: it silently breaks
every T5-architecture checkpoint with an untied output projection.

## ⚠️ 16 GB is not enough for the float32 checkpoint — convert it first

A load on a 16 GB Windows machine died with:

```
OSError: The paging file is too small for this operation to complete. (os error 1455)
```

That is the Windows **commit limit** — physical RAM plus pagefile — exhausted
while `transformers` memory-maps the 11.76 GB float32 file and converts it to
bfloat16 on the way in. The same machine had loaded it successfully an hour
earlier: it fits, with nothing to spare.

**Two fixes, and the second is the durable one.**

**Raise the pagefile** (two minutes, no download): `sysdm.cpl` → Advanced →
Performance Settings → Advanced → Virtual memory Change → untick *Automatically
manage*, select C:, Custom size, Initial `16384` / Maximum `49152` → Set → OK →
restart.

**Or convert the checkpoint once and stop fighting it:**

```bash
python3 scripts/shrink_checkpoint.py
python3 scripts/repair_lm_head.py --model models/madlad400-3b-mt-bf16
```

**11.76 GB → 5.9 GB on disk**, and the loader no longer converts dtype while
mapping.

⚠️ **Peak memory during the conversion is one tensor, not one model** — about
1 GB. `safetensors.torch.save_file` takes every tensor at once, which is the
same problem in a new place, so the container is assembled by hand: an 8-byte
length, the JSON header, then each tensor appended in order, with the source
read at the offsets its own header gives rather than mapped. A plant measures
peak RSS and **fails if anyone replaces the streaming write with `save_file`**,
because every other check would pass on that rewrite.

The conversion is verified against the source before it is used: identical
tensor names and shapes, every output `BF16`, and the largest tensors re-read
from both files and compared within bfloat16 rounding.

⚠️ **This does not fix the forced tie.** That is a loader behaviour, not a file
property, so the converted model still needs the in-memory repair above. This
only makes it small enough to load.

⚠️ **Reading a header does not need the file.** A safetensors file opens with an
8-byte length and that many bytes of JSON — **92 KB** in front of 11.76 GB here.
`read_safetensors_header` uses two `read()` calls; `safe_open` would map the
whole file, which on a machine this close to its ceiling is not free.

## ⚠️ bfloat16 is a storage change, not quantisation

Asked directly, so it belongs here: **does converting the checkpoint cost
accuracy?**

**Nothing is removed.** The converted file holds the same 2,940,374,016 numbers
in the same 742 tensors with the same shapes — the conversion verifies exactly
that. What changes is bytes per number: **4 → 2**.

`bfloat16` is the top 16 bits of a `float32`:

```
float32   01000000010010010000111111011011   3.14159274
bfloat16  0100000001001001                   3.14062500
```

| | exponent | mantissa | |
| --- | --- | --- | --- |
| float32 | **8** | 23 | ~7 significant digits |
| bfloat16 | **8** | 7 | ~3 significant digits |

Same exponent width, so the **range** is identical — nothing overflows and
nothing underflows to zero. Only precision within that range drops.

⚠️ **And the model already ran in bfloat16.** `MadladTranslator` loads with
`dtype=torch.bfloat16`, so the float32 file was rounded at load time anyway.
The conversion moves that rounding from every load to one disk write.
✅ **Verified:** convert-then-load and load-then-convert give bit-identical
tensors, max difference exactly `0.0`. **The shrink costs nothing that was not
already being paid**, and the original file is untouched in the cache.

⚠️ **The Q4 GGUF is a different thing entirely.** That is real quantisation —
4 bits, a genuine quality trade — and DEC-011 records that using it is **a
different measurement**. Storage precision matching what the model already runs
at is not that, and the two must not be filed together.

⚠️ **What is unmeasured:** whether float32 would give better Tigrinya than
bfloat16 on this model. It stays unmeasured because float32 needs ~12 GB
resident and does not fit in 16 GB — so it is not a choice being made, it is a
constraint. Recorded rather than glossed (P-13).

**Because the two are the same measurement, they share a run fingerprint.** The
converted file carries `converted_from` in its safetensors `__metadata__`, and
`source_model_id` resolves both to the same id — so a run rejected from the
cache stays blocked when re-run from the converted directory. Keying on the
file path would have silently unblocked a known failure.

## Running the measurement

In this order. Each one costs more than the last, and each rules out a class of
failure the next would otherwise waste time on:

```bash
python3 scripts/translate_tico19.py --self-test    # no model, no network
python3 scripts/translate_tico19.py --diagnose     # Tigrinya + controls
python3 scripts/translate_tico19.py --smoke        # 3 segments, printed
python3 scripts/translate_tico19.py --json PATH --sheet PATH
```

⚠️ On 16 GB, pass `--model` so the measurement reads the converted checkpoint
rather than the 11.76 GB float32 original, which will not load:

```bash
python3 scripts/translate_tico19.py --model models/madlad400-3b-mt-bf16 --smoke
```

Every artefact records `model_name`, `source_model`, the resolved `checkpoint`
path and its size, so a result always names the file it came from.

⚠️ **`--diagnose` is the one to reach for when output looks wrong.** It
translates the same segments into Tigrinya **and control languages** — `<2am>`
Amharic and `<2es>` Spanish — on a single model load, and prints the fast and
slow tokenizations of the prompt.

Without a control, "the output is not Tigrinya" cannot be told apart from "this
model's Tigrinya is poor", and those need opposite responses. Amharic is the
sharp control: same Ge'ez script, far more training data, so Ge'ez for Amharic
but not Tigrinya isolates the problem to Tigrinya *coverage* rather than to
generating the script at all.

`--dtype float32` retries in full precision. ⚠️ ~12 GB resident; it will thrash
a 16 GB machine.

⚠️ **A rejected run blocks an identical re-run.** Decoding is greedy and the
sample is seeded, so the same command reproduces the same failure exactly — the
second wrong-language run cost ninety minutes to learn nothing. The block is
matched on a fingerprint of the sample and model, never on a filename, so a
changed seed or model is not affected. `--force` overrides it once the cause is
genuinely fixed.

Both the measurement and the rejected file record **which `transformers` and
`torch` actually ran**, read from the imported modules rather than from
`pyproject.toml`. A rejected run whose environment is unknown cannot be
diagnosed.

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
