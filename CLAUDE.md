# Working in this repository

English → Tigrinya translation of **health information**. The goal is a tool
real people use, so a number nobody can read is not a result.

## Before any commit — all of these, all green

```bash
python scripts/check_environment.py          # am I set up? one verdict
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
you just wrote is not evidence. **Thirteen** checks here have been found that
could not fail; every one was written in good faith and none was caught by
review. The thirteenth reported `REPAIR: APPLIED` while making the model worse,
because it asked whether the weights had *changed* and not whether they had
changed to the right thing.

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

New machine, or a fresh editor? **`docs/guides/LOCAL_SETUP.md`** has the
Cursor + Windows sequence.

## The model

`google/madlad400-3b-mt` (Apache-2.0). The checkpoint is **float32, 11.76 GB**,
and stores `decoder.embed_tokens.weight` plus a separate trained
`lm_head.weight` — no `shared.weight`. It is **untied**.

⚠️ **transformers 5.x loads `lm_head.weight` into `shared.weight`** and ties
`lm_head` to it — so the **encoder embeds its input with the output
projection**, and the decoder projects through it too. Output degenerates to one
token repeated. `tigrinya_translate.head` detects this **from the checkpoint**
(two or more embedding-shaped matrices means untied) and restores **both**
matrices **by name**: `lm_head.weight` is the output projection because that is
what the file calls it. Repairing only the head leaves the encoder reading the
wrong matrix — that mistake is the thirteenth entry above. Reported upstream as
**A-22**.

⚠️ **Never infer a tensor's role from the loaded model.** The loaded model is
the thing that is wrong. Read the names in the checkpoint.

⚠️ `looks_degenerate` refuses output that is a repeated token rather than a
translation. Every failure here took that shape, and nothing caught it: the
segment count is right and chrF is real. Repeated *Ethiopic* passes a script
check, so the script gate is not a substitute.

On 16 GB, convert first; the float32 file exhausts the Windows commit limit:

```bash
python scripts/shrink_checkpoint.py                              # 11.76 -> 5.88 GB
python scripts/repair_lm_head.py --model models/madlad400-3b-mt-bf16
python scripts/translate_tico19.py --model models/madlad400-3b-mt-bf16 --smoke
```

⚠️ **Pass `--model` to the measurement too.** Without it `translate_tico19.py`
loads the 11.76 GB float32 original, which is the file that will not fit.

⚠️ bfloat16 here is **storage precision, not quantisation** — the model already
loaded at that precision, and convert-then-load is bit-identical to
load-then-convert. The Q4 GGUF *is* quantisation and would be a different
measurement (DEC-011). `services/translation/README.md` has the detail.

⚠️ Read the **control languages** before the Tigrinya. Fluent Spanish and German
mean the pipeline works; poor Tigrinya after that is a finding about coverage,
not a bug.

⚠️ The model commands do not run in CI and must not be added to it — an 11.8 GB
download per run is a job that gets switched off within a week (DEC-008).

## Still open — read `ACTIONS.md`, do not restate it here

⚠️ **This section used to list the open work and was wrong within a day.** It
claimed CI enforced nothing (A-15 was completed 2026-09-04 and
`.github/workflows/verify.yml` runs the plants, `check_figures`,
`check_definitions` and `check_dates`), and it claimed no Tigrinya speaker had
been found (one had, and the validation sheets were sent to the owner on
2026-09-04 to forward). Both came from writing this file from memory instead of
reading the register — the same mistake as quoting a docstring from memory.

So this file does not hold that list:

- **`ACTIONS.md`** is the register of everything needing a person, with
  ready-to-send drafts and current status.
- **`docs/roadmap/READINESS_PLAN.md`** is the order to do them in and what each
  unblocks.
- **`PROJECT_CONTEXT.md`** holds the standing constraints.

The one genuinely repository-side item: **`check_commands.py` is not in
`.github/workflows/verify.yml`** (A-21), so it is the only checker not enforced
on a push.
