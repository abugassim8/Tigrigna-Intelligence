# Working in this repository

English → Tigrinya translation of **health information**. The goal is a tool
real people use, so a number nobody can read is not a result.

## Before any commit — all of these, all green

```bash
python -m pytest services -q                 # 187 pass, 4 skip
python scripts/tests/test_plants.py          # every planted case behaves
python scripts/check_figures.py              # derived counts match the tree
python scripts/check_dates.py
python scripts/check_commands.py             # documented commands are runnable
python scripts/check_definitions.py          # duplicate definitions agree
```

`check_figures.py` derives counts from the repository, so adding a plant or an
open action **will** fail it until the documents are updated. That is the check
working; fix the document, never the check.

## The rules that are not obvious from the code

⚠️ **Every behavioural change is verified by reverting it** and confirming the
matching plant fails — and fails for the right reason. A green run on a check
you just wrote is not evidence. **Twelve** checks here have been found that
could not fail; every one was written in good faith and none was caught by
review.

⚠️ **A declared flag is not an outcome.** Verify what actually loaded, never a
config field, a keyword name or a version number. Three instances:

| Trusted | Reality |
| --- | --- |
| `dtype=` vs `torch_dtype=` | `from_pretrained` forwards unknown keywords to the config and ignores them |
| `transformers.__version__ >= 5` | the rename landed in 4.56 |
| `config.tie_word_embeddings` | transformers 5.x overwrites it to `True` in `T5Config.__post_init__` |

The third reported a broken model healthy while it emitted noise.

⚠️ **A check that fires on correct input gets switched off** (DEC-008). Prefer
refusing loudly over guessing, and name what *is* accepted in every error — not
only what is not. `hm.download('ti')` survived six weeks in an error message
that named neither.

⚠️ **The decision log is append-only.** A decision that turns out wrong gets an
**Amendment**; the original text stays, marked superseded. Negative results are
recorded, not deleted (P-13).

⚠️ **Record negative and unflattering results.** A measurement that retires an
approach is a result. chrF alone is never the finding — two professional human
translators scored **≈ 24** against each other on this data (Experiment 011), so
the scale is not the one intuition suggests.

## Never

- **Never commit HornMorpho bytes** — GPL-3.0, user-installed, never
  distributed (DEC-028). Morphology checks SKIP when it is absent; they never
  silently pass.
- **Never ship an NLLB checkpoint.** Every variant is CC-BY-NC-4.0 and
  quarantined (DEC-011). `test_the_model_is_not_nllb` exists because that breach
  would otherwise be invisible — the code would work perfectly.
- **Never write an `HF_TOKEN` value** into any file. Name the variable only.
- **Never send `validation/key.json`** or `manifest.json` to a reviewer. The
  first line says so.
- **Never send email.** `ACTIONS.md` holds ready-to-send drafts; a person sends
  every one of them.
- **Never push to another branch** without being asked.

## The model

`google/madlad400-3b-mt` (Apache-2.0). The checkpoint is **float32, 11.76 GB**,
and stores `decoder.embed_tokens.weight` plus a separate trained
`lm_head.weight` — no `shared.weight`. It is **untied**.

⚠️ transformers 5.x ties `lm_head` anyway and discards the trained projection,
so the decoder projects through the input embedding and output degenerates to
one phrase repeated. `tigrinya_translate.head` detects this **from the
checkpoint** — two or more embedding-shaped matrices means untied — and repairs
it in memory, refusing rather than scoring noise when it cannot. Reported
upstream as **A-22**.

On 16 GB, convert first; the float32 file exhausts the Windows commit limit:

```bash
python scripts/shrink_checkpoint.py                              # 11.76 -> 5.88 GB
python scripts/repair_lm_head.py --model models/madlad400-3b-mt-bf16
```

⚠️ Read the **control languages** before the Tigrinya. Fluent Spanish and German
mean the pipeline works; poor Tigrinya after that is a finding about coverage,
not a bug.

⚠️ The model commands do not run in CI and must not be added to it — an 11.8 GB
download per run is a job that gets switched off within a week (DEC-008).

## Still open

- **`.github/workflows/` cannot be pushed by the GitHub App**, so CI enforces
  nothing until the YAML in `ACTIONS.md` is pasted by hand (A-15, A-21).
- **Gap #1: one named Tigrinya speaker.** The judgement sheet is the finding and
  it needs a reader. Nothing else substitutes for it.
