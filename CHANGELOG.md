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

### The repair ran out of memory — my regression — 2026-09-18 (evening)

Every diagnostic line was **correct**: `TIED_WRONGLY`, input
`decoder.embed_tokens.weight`, output `lm_head.weight`. Then the process exited
**silently** — no traceback, no `REPAIR: APPLIED`. On Windows that is a native
kill, not a Python error.

⚠️ **I caused it.** Restoring *both* matrices meant holding two 0.49 GB tensors
and memory-mapping the 5.88 GB checkpoint, on top of a 5.48 GB resident model:
**13.62 GB peak on a 16 GB machine**. The version that survived read one tensor.
I changed a memory-constrained path without checking its memory cost, in a
repository that contains `shrink_checkpoint.py` precisely because 16 GB is tight.

**Fixed with the technique one file away.** `read_tensor` reads a single tensor
by plain file I/O at the offset the header already gives — no mapping — and
`tensor_digest` streams a sha256 so the "tied after all" check never holds both
matrices. One tensor is resident at a time: read, install, verify, drop, next.

**A silent exit must never cost a round trip again.** The repair now prints a
line naming each tensor and its size *before* allocating, so the last line
printed localises any crash, and catches `MemoryError` with what it was
attempting.

### ⚠️ Two plants that could not fail, caught before they were relied on

Writing the regression test took three attempts, and the first two were worthless:

1. **`ru_maxrss` in-process.** It is a high-water mark that never decreases, so
   the fixture's own peak masked the repair's entirely — the measurement read
   zero whatever the repair did.
2. **Peak RSS in a child process, differential.** Better, and still could not
   fail: **RSS on Linux does not reflect a Windows commit limit.** The mapping is
   lazy and the allocator reuses freed blocks, so the broken version measured
   *cheaper* than the budget.

Both caught in the verification pass before anything relied on them, so by the
standing convention the count stays at **thirteen** — but a plant that cannot
fail on the platform it runs on is worse than no plant, so the RSS one was
deleted rather than kept as a green light.

**Replaced with two structural invariants**, deterministic on every platform:
`the_repair_never_maps_the_checkpoint` makes `safetensors.safe_open` raise and
requires the repair to succeed anyway, and
`the_repair_holds_one_checkpoint_tensor` holds weak references and fails if a
previous tensor is still alive when the next is read. Both verified against
tonight's exact code; the second also catches holding both without mapping.

**`check_environment.py` now reports total and available memory**, with a
warning when available is below the ~7.7 GB a model run needs. Offered earlier
and declined; this is the second failure it would have pre-empted. ⚠️ It reports
and never refuses — a readiness check that fails because a browser is open gets
switched off.

⚠️ **The identification was right all along**, and nothing about it changed.
There is **still no Tigrinya measurement**.

113 planted cases, up from 109. 187 tests pass, 4 skip.

### The two matrices are swapped, and my repair had made it worse — 2026-09-18

The repair ran on the owner's machine, printed `REPAIR: APPLIED`, and the output
got worse. The decisive line was `output projection is
'decoder.embed_tokens.weight'` — a fallback that only fires when the
checkpoint's `lm_head.weight` **equals the loaded input embedding**.

⚠️ **So transformers loads `lm_head.weight` into `shared.weight`.** The encoder
embeds English with the **output projection**; the input is corrupted before
decoding begins. Amendment 3 had the direction backwards, and no amount of
fixing `lm_head` could have helped.

| tensor | transformers loads | should be |
| --- | --- | --- |
| `model.shared.weight` | the **output projection** ✗ | `decoder.embed_tokens.weight` |
| `model.lm_head.weight` | tied to shared ✗ | `lm_head.weight` |

### ⚠️ A thirteenth check that could not fail

The repair identified the output projection by asking **which stored tensor
differed from the model's loaded input embedding** — valid only if that
embedding is correct, and here it is not. It chose the *input* embedding, bound
it to `lm_head`, and reported success. `RepairFailedError` asked whether the
weights had **changed**; they had. Nothing asked whether they had changed to the
right thing.

**Fixed by reading the names in the file.** `lm_head.weight` is the output
projection because that is what it is called; the loaded model is the thing that
is wrong, so it cannot be the authority. Both matrices are restored, and the
repair now verifies that the input embedding, the encoder and decoder token
embeddings and `lm_head` each hold what the checkpoint says — and that the first
and last are no longer identical.

⚠️ **Added `looks_degenerate`, which should have existed from the start.** Every
failure in this line of work was one token repeated to the limit — `Sally
Hansen` nine times, one glyph thirty-two times, Syriac to the token limit — at
**0.03–0.08** distinct characters per character against **0.5–0.8** for real
text. Nothing caught it: degenerate output has the right segment count and a
real chrF. `translate_tico19.py` now refuses a run where a quarter or more of
the segments are degenerate. ⚠️ The script gate is not a substitute — repeated
Ethiopic passes it, and the plant for the new guard uses exactly that case.

⚠️ **Six plant fixtures encoded the old, wrong rule and passed.** One asserted
that an `lm_head.weight` matching the loaded input embedding must be *rejected*
in favour of the tensor that differed — which is precisely the bug. Rewritten to
the real checkpoint's layout.

⚠️ **Still no Tigrinya measurement exists.** All of this is pipeline. The
pre-committed threshold is untouched. **DEC-011 Amendment 5** records the
mechanism; **A-22** is sharpened — the matrices are swapped, not merely tied.

109 planted cases, up from 107, each new guard verified by reverting it. 187
tests pass, 4 skip.

### The checkers were reading the virtualenv — 2026-09-18

The first real local run surfaced three bugs that CI structurally cannot see,
because CI has no virtualenv inside the tree.

⚠️ **`check_figures.py` and `check_dates.py` globbed `**/*.py` from the
repository root with no exclusion**, so on a machine with `.venv/` in the tree
they read every file in torch and transformers. `check_figures.py` **timed out
after 180 seconds** on a healthy repository, and `check_environment.py` reported
`NOT READY` because of it. Slowness was the smaller half: a retired figure
quoted in a third-party docstring would have been reported as a stale claim
here — a check firing on correct input, which is how checks get switched off
(DEC-008). `check_commands.py` excluded `.venv/`; the other two never did.

**Fixed by asking git, not by lengthening a list.** New `scripts/repo_files.py`
returns what `git ls-files` tracks, falling back to a filesystem walk with
exclusions only when git cannot answer. A denylist answers *"is it `.venv`?"*
when the question is *"is it ours?"*, and the next directory to appear beside
the source would need its own entry and would not get one until it broke
something.

⚠️ **`.gitignore` line 241 was `*.model          # SentencePiece`.** Git has no
inline comments, so that was a literal pattern matching nothing and
`spiece.model` was never ignored. Fixed, with the comment on its own line.

⚠️ **A converted checkpoint was committable.** Only `model.safetensors` was
caught, by `*.safetensors`. The tokenizer that travels beside it is **16.6 MB**
and is a `.json`, so nothing stopped `git add -A` from staging it. Now covered
by `models/*-bf16/` — and `shrink_checkpoint.py` writes a `.gitignore`
containing `*` into whatever directory it writes, so an unconventional `--out`
is covered too.

`check_environment.py`'s checker timeout is raised to 900s and a timeout now
reports as *"a finding about the checker, not about this repository"* rather
than as an ordinary failure.

107 planted cases, up from 102. The `.venv` plant builds a real virtualenv
directory rather than trusting the exclusion list, and
`the_repository_still_sees_its_own_files` is its control — excluding everything
would pass the other two and silently stop the checkers checking anything. Each
verified by reverting it. 187 tests pass, 4 skip.

### The measurement can finally use the converted model — 2026-09-18

A question — *does shrinking the checkpoint hurt accuracy?* — found a gap that
would have cost another failed run.

**The answer first.** Nothing was removed: the same 2,940,374,016 parameters,
742 tensors, same shapes. bfloat16 is the top 16 bits of a float32 with the
**same 8 exponent bits**, so the range is unchanged and only precision within it
drops. ⚠️ And the model already loaded at `dtype=torch.bfloat16`, so the float32
file was being rounded at load time anyway. ✅ Verified bit-identical,
max difference `0.0`. **DEC-011 Amendment 4** records it, and why the Q4 GGUF
is still a different measurement while this is not.

### ⛔ The gap: `translate_tico19.py` had no `--model`

The script that produces the actual result could only load the module-level
`MODEL` — the Hub id, resolving to the **11.76 GB float32 file that crashes this
machine**. Convert, verify with `repair_lm_head.py`, then run the measurement
and hit `os error 1455` again. The path was built to the last step and stopped
one command short.

⚠️ **Eight places hardcoded `MODEL`**, not one — the fingerprint, the rejected
file, the Harness `system`, the artefact, the smoke print, and `--diagnose`'s
slow tokenizer. A `--model` flag threaded only into the constructor would have
loaded one model and recorded another: a provenance lie in a file whose whole
purpose is provenance. All eight now derive from the translator.

### ⚠️ And the fingerprint would have blocked the first correct run

It covered the sample and the model name only. It now also covers **dtype,
language token, and whether the output projection was repaired** — without the
last, the wrong-language rejections of 2026-09-15 and -16, produced by a model
whose trained `lm_head` the loader had discarded, would have refused the first
*correct* measurement as a known failure.

⚠️ The paired plant `an_identical_configuration_is_still_blocked` exists because
loosening a fingerprint until nothing is ever blocked passes the other plant and
destroys the guard.

**Provenance now travels inside the file.** `shrink_checkpoint.py` writes
`converted_from` into the safetensors `__metadata__`, and `source_model_id`
resolves a converted copy and its original to the same id — so they share a
fingerprint, as they must, being bit-identical. Keying on the path would have
silently unblocked a known failure.

Artefacts record `model_name`, `source_model`, `checkpoint`, `checkpoint_bytes`
and `converted_from`; a cache run and a converted run were previously
indistinguishable.

102 planted cases, up from 96, each new guard verified by reverting it. 187
tests pass, 4 skip. 38 documented commands checked.

### Moving the work to a local editor, and two stale claims corrected — 2026-09-17

⚠️ **`CLAUDE.md`, written yesterday, was wrong in two places** — both from
writing it from memory instead of reading `ACTIONS.md`, the same mistake as
quoting a docstring from memory earlier in this project:

- it claimed **CI enforces nothing**. **A-15 was completed 2026-09-04**:
  `.github/workflows/verify.yml` exists and runs the plants, `check_figures`,
  `check_definitions` and `check_dates`. Only `check_commands.py` is missing
  from it (**A-21**);
- it claimed **no Tigrinya speaker had been found**. One had, and the validation
  sheets were sent to the owner on 2026-09-04 to forward (**A-13**). The open
  item is the forward and the filled-in sheets coming back.

**Fixed structurally, not just textually:** that section now *points at*
`ACTIONS.md` and `READINESS_PLAN.md` rather than restating them, with a note
saying it went stale within a day by doing exactly that.

**Added `scripts/check_environment.py`** — one command, one verdict on whether a
workstation is ready: interpreter, the editable installs, model packages,
`HF_TOKEN` **presence only**, checkpoints by path and size, HornMorpho as SKIP
(DEC-028), and the four checkers by exit code.

⚠️ **It reports and never installs**, and ⚠️ **never loads the model** — that
costs ~6 GB and a readiness check needing 6 GB stops being run (DEC-008). A
missing model is still `READY`, deliberately: most work here needs none, and
failing on it is how a check becomes noise.

### ⚠️ It found a bug on its first real run

`locate_checkpoint`'s new "looks like a path" guard tested for `os.sep` or
`os.altsep` anywhere in the argument — and **a Hub id contains a slash**, so
`google/madlad400-3b-mt` was rejected as a nonexistent path. On every platform:
`/` is `os.sep` on POSIX and `os.altsep` on Windows. Shipped yesterday.

**The plan named a plant for "a Hub id still resolves through the cache" and it
was never written.** The plants that were written covered the new local-path
cases and none of the old behaviour. A Hub id is now distinguished from a path
by shape — one slash, no OS separator, no leading dot, and a parent that is not
an existing directory — and the missing plant exists, verified by reverting to
yesterday's test.

**Added `docs/guides/LOCAL_SETUP.md`** — the Cursor + Windows sequence, and why
the round trips existed at all: `huggingface.co` is blocked from the assistant's
environment by org egress policy, so every model command had to run on the
owner's machine.

96 planted cases, up from 89. 187 tests pass, 4 skip. 37 documented commands
checked.

### The converter worked; the command it printed did not — 2026-09-16

The conversion ran clean on the owner's machine: 742 tensors,
**11.76 GB → 5.88 GB**, names and shapes identical to the source, every tensor
`BF16`. Then the command the script itself printed failed — `repair_lm_head.py`
with `--model` pointing at the converted directory, answered with *"no cached
model.safetensors for models/madlad400-3b-mt-bf16"*.

⚠️ Written as a path and a flag rather than as a runnable command line, because
`check_commands.py` reads command lines in documents and checks them — and it
caught this entry when the failing command was pasted verbatim. That is the
checker holding this file to the rule it enforces, which is the point of it.

`locate_checkpoint` searched the Hugging Face cache and nothing else — no branch
for a local directory. `from_pretrained` handles local paths, so the lookup was
the only thing that did not.

⚠️ **This is the defect `check_commands.py` was built to stop**, recurring
against the checker. It verifies that a script exists and a flag is declared;
`--model` is declared, so it passed. It cannot know an argument *value* is
unsupported. Not a check that could not fail — it catches real things, and the
count stays at **twelve** — but a documented scope limit with a second instance
against it.

**Fixed both halves.** `locate_checkpoint` now resolves a local directory or a
`.safetensors` file before the cache. ⚠️ And a path-shaped argument that does
not exist is **refused rather than falling through to the cache glob**, which
would have silently resolved a typo to whatever MADLAD copy it found first and
reported success against a different model than the one loaded.

**`shrink_checkpoint.py` now proves the command it prints** — it resolves the
directory it just wrote, and checks the result is the file it wrote, before
telling anyone to run anything. That is the runtime half of `check_commands.py`,
and it would have caught this before the owner saw it.

**Added `CLAUDE.md`** so the work can move to a local editor: the check
commands, the revert-to-verify rule, the three times a declared flag was trusted
over a loaded outcome, the append-only decision log, and the never-do list
(HornMorpho bytes, NLLB, `HF_TOKEN` values, `validation/key.json`, email).

89 planted cases, up from 83; the new ones verified by reverting each guard. 187
tests pass, 4 skip. 34 documented commands checked.

### 16 GB could not load the float32 checkpoint; convert it once instead — 2026-09-16

```
OSError: The paging file is too small for this operation to complete. (os error 1455)
```

The Windows **commit limit** — RAM plus pagefile — exhausted inside
`transformers`' own loader while memory-mapping the 11.76 GB float32 checkpoint.
Not a regression: the identical pre-load step ran in the load that succeeded an
hour earlier. The machine was always within a few hundred MB of its ceiling, and
nothing in the plan had accounted for that despite both numbers — 16 GB of RAM,
an 11.76 GB file — being recorded here from the start.

**Added `scripts/shrink_checkpoint.py`** — rewrites the checkpoint as bfloat16,
**11.76 GB → 5.9 GB**, so the loader no longer converts dtype while mapping.

⚠️ **Peak memory is one tensor, not one model** (~1 GB).
`safetensors.torch.save_file` wants every tensor at once, which is the same
problem in a new place, so the container is assembled by hand: an 8-byte length,
the JSON header, then each tensor appended in source-offset order, with the
source read at the offsets its own header gives rather than mapped. Measured:
**zero peak-RSS growth** converting a 384 MB file.

A plant measures peak RSS and **fails if the streaming write is replaced with
`save_file`** — verified by doing exactly that. Every other check passes on that
rewrite, which is what makes the plant worth having.

The conversion is verified against the source before use: identical names and
shapes, every output `BF16`, largest tensors re-read from both files and compared
within bfloat16 rounding, and the result reopened with the real `safetensors`
library — a hand-written container is worth nothing if the library cannot read it.

**Added `read_safetensors_header`** — names, dtypes and shapes from two `read()`
calls. A safetensors header is **92 KB** in front of this 11.76 GB file, and two
callers were mapping the whole thing to learn what was in it. `repair_head` still
opens the file properly, because it genuinely needs values.

**`repair_head`'s own peak trimmed**: proving the repair did not touch the input
embedding used a full clone (~0.5 GB at bfloat16); it now compares row norms
(~1 MB). Verified still to catch a write-through by reverting the fix it guards.

⚠️ **None of this changes the forced tie**, which is a loader behaviour rather
than a file property. The converted model still needs the in-memory repair.

83 planted cases, up from 77. 187 tests pass, 4 skip. 33 documented commands
checked.

### The projection was loaded, then thrown away by a forced tie — 2026-09-16

**The model ran, and the answer was not the one recorded earlier the same day.**
`lm_head` is **not** randomly initialised. It is trained, present in the
checkpoint, loaded — and then discarded, because transformers 5.x ties it to the
input embedding regardless of what the checkpoint says.

**What the file holds** [measured from the safetensors header]:

```
decoder.embed_tokens.weight   (256000, 1024) F32
lm_head.weight                (256000, 1024) F32
```

No `shared.weight`, and a separate trained `lm_head.weight`. A tied model has no
second matrix to store, so this checkpoint is untied **by construction**.

⚠️ **Cause** [verified, `configuration_t5.py` v5.17.0]: `T5Config.__post_init__`
repurposes `tie_word_embeddings` as a decoder-scaling hint and then sets
`self.tie_word_embeddings = True` unconditionally, assuming every T5-family
checkpoint ties. The decoder ends up projecting through the *input* embedding —
`Sally Hansen Sally Hansen …`, identical for Spanish, German, Amharic and
Tigrinya.

### ⚠️ A twelfth check that could not fail — the first not caught by planting

The detection shipped hours earlier asked `model.config.tie_word_embeddings`,
**the exact field transformers overwrites**. It ran on the real model, printed
`VERDICT : TRAINED — nothing is wrong here`, and skipped its own repair. Every
plant behind it passed, because every plant supplied the fixture the check asked
for.

**Planting proves a check fires on the failure you imagined. It cannot prove you
imagined the right failure, or that the check is reading a trustworthy input.**
Only running the real thing found this — which is the argument for the control
languages, and for reading them before the result.

**Third instance of the same error**, after the dtype keyword and the
`major >= 5` version gate: **a declared flag is not an outcome.**

**Fixed** by deciding from the checkpoint — two or more embedding-shaped
matrices means untied, whatever any config says. `config.tie_word_embeddings` is
still printed, labelled `NOT used`, with the reason. The regression plant
reproduces the real checkpoint's exact shape and fails if the config is consulted
again — verified by reverting it.

**DEC-011 Amendment 3** records the mechanism and marks Amendment 2's cause
superseded rather than deleting it (P-13). **A-22** is rewritten: the defect is
not MADLAD-specific, it silently breaks every T5-architecture checkpoint with an
untied output projection. 77 planted cases, up from 74. 187 tests pass, 4 skip.

### The decoder was emitting noise: `lm_head` was never loaded — 2026-09-16

**The junk output has a mechanism, and it is not a mistranslation.** The decoder
emitted a single token repeated to `max_new_tokens`, differing per input — a
working encoder in front of a **randomly initialised output projection**.

⚠️ **Cause** [verified against `modeling_t5.py` at v4.35.0, v4.44.0, v4.56.0,
v4.57.1, v5.0.0, v5.17.0]: `T5ForConditionalGeneration` declares
`lm_head.weight` tied to `shared.weight` as a **class attribute**, fixed before
any config is read, in every one of those versions. MADLAD sets
`tie_word_embeddings: false`, and the same module gives `lm_head` a fresh
`normal_(0, 1)` precisely when that flag is false. A key in the tied mapping is
**suppressed from the missing-weights report**, so it loads with no warning.

**Two branches investigated and closed as negative results (P-13):**

- **`jbochi/madlad400-3b-mt` is byte-identical to `google/`** — all 13 files the
  same size, `config.json` the same 749 bytes. Switching repositories would have
  cost a second 11.8 GB download and changed nothing.
- ⚠️ **"the tensors differ ⇒ bad checkpoint" was backwards.** With
  `tie_word_embeddings: false` the second stored matrix **is** the untied output
  projection, so differing is correct. That check would have fired on a healthy
  file — the DEC-008 failure mode, caught before anything relied on it, so the
  **count of checks that could not fail stays at eleven**.

**Added:** `tigrinya_translate.head` — detection and repair in the package, not
in a script, because the measurement runs through `MadladTranslator`. It decides
**from the weights** (row-norm spread, with the bound **derived from the matrix
shape** rather than hard-coded), repairs **only** when they say so, refuses with
`RandomHeadError` rather than scoring noise, and records `head_state`,
`head_repaired` and `head_source` on every artefact — because a score from a
repaired model is **not the same measurement**. Plus `scripts/repair_lm_head.py`
as a CLI over it.

**Two bugs caught by exercising the real path rather than reasoning about it:**
`copy_` into a head aliased to the input embedding destroys the input embedding
too (now rebinds); and comparing a float32 checkpoint against a bfloat16 model in
float32 makes every candidate "differ" by rounding, which would have raised
`AmbiguousProjectionError` on a healthy checkpoint.

**DEC-011 Amendment 2** records all of it. **A-22** reports the tying conflict
upstream. 74 planted cases, up from 63 — each verified by reverting it. 187
tests pass, 4 skip. 28 documented commands checked.

### One command, one report — after six round trips that should have been one — 2026-09-16

⚠️ **This entry records a process failure, not a code one.** Diagnosing the
wrong-language output took **six round trips and two ninety-minute runs** to
produce one line of usable evidence, because each attempt answered one question
and then asked for another command. The owner's terminal was being used as a
REPL, and the environment ended up **worse** than it started: a `transformers`
downgrade broke the `tokenizers==0.23.1` pin, moved `huggingface_hub` from 1.31
to 0.36, and left the model unable to load at all — header, deprecation warning,
then a **silent exit**. No traceback, no progress bar, nothing.

**A silent exit is a native crash or an OOM kill**, and in a single process it
destroys the whole diagnostic. That is why each attempt cost a round trip.

**`scripts/diagnose_environment.py`** answers everything at once:

| Stage | Question |
| --- | --- |
| 1 | versions, platform, **total RAM** |
| 2 | **do `shared.weight` and `decoder.embed_tokens.weight` actually differ?** |
| 3 | `<2ti>` in vocab; fast vs slow tokenization |
| 4 | does it load, and **in the dtype that was asked for?** |
| 5 | generation into `<2es>`, `<2de>`, `<2am>`, `<2ti>` |

⚠️ **Every stage runs in its own subprocess**, so a crash is a recorded line and
the later stages still run. ⚠️ **The report is written even when every stage
fails** — that is the case it exists for. Both are planted, and both plants fail
when reverted.

⚠️ **Stage 2 is decisive and nearly free.** `safetensors.safe_open` reads
individual tensors without materialising 11.8 GB, so the tied-weights hypothesis
is settled in seconds instead of inferred from garbage output. It does not care
which `transformers` is installed, so the report is useful even when the
environment is broken — which it currently is.

#### Two bugs from guessing a keyword, replaced by checking the outcome

`torch_dtype` → `dtype` was handled first with `try/except TypeError` — **which
never fires**, because `from_pretrained` forwards unknown keywords to the config.
Then with a version gate on `major >= 5` — **also wrong**, because the rename
landed in **4.56**, not 5.0. Either would have loaded float32 silently: 11.8 GB
resident instead of 6, thrashing the 16 GB machine and looking like a slow run.

`DtypeIgnoredError` now raises when the **loaded** model's dtype differs from the
requested one. Asking the model what it actually is cannot be wrong; guessing
which keyword a library wants produced two bugs in two days.

63 planted cases, up from 60. 191 tests. 24 documented commands checked.

⚠️ **Still no diagnosis.** This is scaffolding, and the two previous attempts
were too. The difference is that this one costs about two minutes and produces
the whole picture, rather than ninety minutes and one line.

### The model is broken, not the language selection — 2026-09-16

The preserved rejected output finally showed what MADLAD produced. It is not a
mistranslation:

| English | Output |
| --- | --- |
| but if you have the cough | `៍៍ ៍៍ ៍៍ ៍៍ ៍៍ …` (Khmer marks, to the token limit) |
| do your relatives have the same symptoms | `ەەەەەەەەەە…` (Arabic ae) |
| i had a short sharp pain in my chest | `ėėėėėėėėėė…` |
| i will send you an image on your screen | `2019-01-19T00:00:00Z` repeated |
| my sister has similar symptoms | `te te te te te…` |
| Reports from China and Italy … | `ะะะะ…ตตตต` (Thai) |
| Case report forms were submitted … | `1000000000000000♠0.00000…` |

**Single junk tokens repeated to `max_new_tokens`.** A working MADLAD emits
fluent text in *some* language; this is noise. The language token was never the
problem, and neither is MADLAD's Tigrinya coverage — **nothing about this output
is a translation.**

⚠️ **The junk differs per input**, so the encoder is responding to the text
while the decoder emits noise. That is precisely what the load-time warning
describes: `shared.weight` and `decoder.embed_tokens.weight` *"present in the
checkpoints with different values"*, and `transformers` **5.17.0** declining to
tie them on a checkpoint written for **4.23.1**.

**The hypothesis recorded yesterday now has evidence.** It is still a hypothesis
— the test is downgrading `transformers` below 5, which needs no re-download
because the weights are cached.

#### A trap in the way of that test, removed first

`_loaded` chose the dtype keyword with `try: dtype=… except TypeError:
torch_dtype=…`. **The `TypeError` never fires.** `from_pretrained` forwards
unknown keywords to the *config* rather than raising, so on `transformers` 4.x
the dtype would have been **silently ignored** and the model loaded in float32 —
11.8 GB resident instead of 6, enough to thrash the 16 GB machine it runs on,
and it would have looked like a slow run rather than a bug.

Now selected by `transformers.__version__`, explicitly. ⚠️ A fallback that
cannot fire is the same defect as a check that cannot fail, and it was written
one day after the entry above about exactly that.

### The same failed run was repeated, because nothing read the rejected file — 2026-09-16

The wrong-language run was launched a second time, unchanged. **Same seed
(`20260915`), same 100 segments, same model, `num_beams=1`, `do_sample=False`.**
It is deterministic. It reproduced the same failure for roughly ninety minutes
to learn what `--diagnose` answers in four.

⚠️ **The rejected file existed and nothing read it.** The mechanism added
yesterday to preserve evidence recorded the failure faithfully and then let the
identical command run again. Preserving a finding is not the same as acting on
one.

**A run whose fingerprint matches a rejected one is now refused**, naming the
date, the reason, the previous environment, and `--diagnose` as the next step.
`--force` overrides it once a cause is fixed.

⚠️ **Matched on the fingerprint, never on the filename** — a changed seed,
sample size or model is a different run and must not be blocked. The
`a_different_run_is_not_blocked` plant is the one keeping this honest: a block
that fired on everything would be switched off within a week, which is the
failure DEC-008 exists to prevent.

#### The advice in the rejection message had gone stale

It said *"check `tigrinya_translate.LANGUAGE_TOKEN`"*. That was right when
written and **wrong by the next morning**: `<2ti>` was verified against the
model's own `tokenizer.json` on 2026-09-15. An error message that names the
wrong suspect sends the reader in the wrong direction at the one moment they are
certain to follow it. It now names `--diagnose`, and says explicitly that the
token is not the suspect.

#### Neither artefact recorded what actually ran

⚠️ **A rejected file was on disk and could not say which `transformers`
produced it** — and that is the prime suspect. The run printed:

```
The tied weights mapping and config for this model specifies to tie
shared.weight to decoder.embed_tokens.weight, but both are present in the
checkpoints with different values, so we will NOT tie them.
```

`config.json` already declares `"tie_word_embeddings": false`, so the config and
the loader disagree about what the config says. In HF's T5, `shared`,
`encoder.embed_tokens` and `decoder.embed_tokens` are **the same `nn.Embedding`
object**; two differing tensors for them means one overwrites the other. The
MADLAD paper states the vocabulary is *"shared on both the encoder and decoder
side"*, so they should be identical — their differing is itself the anomaly.
`transformers` **5.17.0** loading a checkpoint written for **4.23.1** is the
combination most likely to produce it.

⚠️ **That is a hypothesis and is recorded as one.** It has not been tested. Both
artefacts now carry the `transformers` and `torch` versions, the dtype and the
platform, **read from the imported modules rather than `pyproject.toml`** — the
pinned range and the installed build are different facts, and the gap between
them may be this whole failure.

#### The cost is now stated before it is spent

`measure()` printed the sample size and not the ninety minutes. It now prints
the estimate and the cheaper alternatives before the first batch.

60 planted cases, up from 56. 191 tests. 23 documented commands checked.

⚠️ **The cause is still unknown.** Nothing here diagnoses it; all of it makes the
next attempt cheaper and the evidence legible. `--diagnose` remains the thing
that has not yet been run.

### The diagnostic is a command now, not a paste from a chat window — 2026-09-16

The wrong-language run needs diagnosing, and **this environment cannot do it**:
`huggingface.co` returns `CONNECT tunnel failed, response 403` under the org
egress policy — which must not be retried or routed around — and neither `torch`
nor `transformers` is installed here. The 11.8 GB model exists on exactly one
machine, and it is not this one.

So the diagnostic runs on the owner's machine either way. The only choice was
whether it arrives as a **paste from chat** or as a **committed command**, and
this week has already answered that: `hm.download('ti')`, `fetch.py --verify`,
and the missing `HF_TOKEN` were all instructions living outside the repository —
unversioned, unchecked by `check_commands.py`, and wrong.

**`--diagnose`** translates the same segments into Tigrinya **and controls**
(`<2am>`, `<2es>`) on **one model load**, and prints the fast and slow
tokenizations of the prompt.

⚠️ **The control is the entire point.** "The output is not Tigrinya" and "this
model's Tigrinya is poor" demand opposite responses, and no amount of staring at
Tigrinya output distinguishes them. Amharic is the sharp control: same Ge'ez
script, far more training data, so Ge'ez for Amharic but not Tigrinya isolates
the problem to Tigrinya *coverage* rather than to generating the script.

#### A gap found while building it

`_assert_language_token` runs inside `_loaded`, which is a `cached_property`. So
`translator.language_token = "<2xx>"` after loading would **skip the gate
entirely** — the one check standing between a typo'd control language and a
fluent, scoreable translation into something else.

`use_language()` re-validates against the loaded tokenizer and refuses without
changing anything. Swapping tokens is worth supporting — comparing against a
control is how a pipeline defect is told from a finding — but reloading 11.8 GB
per language to do it is absurd, so the switch is a method, not an attribute.

#### The plant that matters

⚠️ **If the token were captured at load time rather than read per call, every
control language would emit identical output** and `--diagnose` would report
"Tigrinya and Spanish both fail" — a false *pipeline* diagnosis produced by a
check that ran perfectly. `diagnose_actually_changes_the_language` asserts the
prompts actually differ. Verified by reverting: with the switch removed, it
fails, and so does the refused-language plant.

Three more: the model is loaded **once** for N languages; `--diagnose` writes
nothing (the same `builtins.open` / `Path.write_text` interception that caught
the `--smoke` ornament); and a refused control language is reported and skipped
rather than aborting the run.

#### Two mistakes of my own, both caught by running things

`_Probe` was inserted into `HARNESS_PLANT` instead of `TRANSLATE_PLANT` —
anchored on `cached_call`, which belongs to the morphology plant. All four new
plants failed with `NameError` on the first run. Caught immediately because the
plants were executed rather than reviewed.

And the earlier claim that `translate_tico19.py`'s docstring promised
checkpointing was **wrong** — that sentence was in the plan document, not the
file. Corrected in the entry below rather than dropped.

#### The ASCII-locale plant caught a regression in today's code

⚠️ All four new plants **passed normally and failed under an ASCII locale.**
`diagnose()` prints Ge'ez and the metaspace marker `\u2581`, and — reachable by
import, like `smoke()` — the `main()` guard never covered it. On Windows a child
writing to a pipe encodes with cp1252 whatever the console is, so this is the
same defect as two days ago, reintroduced in code written today, and caught by
the whole-suite ASCII pass written for exactly that.

Both now call `force_utf8_stdio()` themselves, which is the rule already
recorded: entry **functions** force their own stdio, because a `__main__` guard
does not run for a caller that imports them.

56 planted cases, up from 52. 191 tests. 23 documented commands checked.

⚠️ **Nothing here is proven against the model.** Every path is exercised with
injected stubs; `--diagnose` reaches real weights for the first time on the
owner's machine. Saying so is not modesty — `MadladTranslator.__call__` has
still never executed in this environment.

### The language gate caught a wrong-language run — and everything around it failed — 2026-09-16

**The first real translation run produced 0 Ethiopic characters in 100
segments.** `WrongLanguageError` fired and refused to write a scored artefact.

✅ **That gate did exactly its job**, and it is the first check in this project
to catch a real failure in production rather than a planted one. Without it this
repository would now hold `translation-en-ti-2026-09-15.json` carrying a chrF
number for a language nobody asked for, and **every other check would have
passed it** — the shape, the segment count and the score are all well-formed.

⚠️ **Everything around the gate failed the owner**, and all of it was mine.

**1. The abort destroyed the evidence.** 46 minutes of CPU produced the one
artefact that could explain the failure, and `measure()` raised before writing
anything. Refusing to record a *measurement* was right; discarding the *output*
was not. A rejected run now writes `PATH-REJECTED.json` carrying
`"is_a_measurement": false`, never at the `--json` path and never read by the
scoring path.

**2. There was no cheap way to look.** The only route from "model loaded" to
"see output" was the full 100-segment run. **`--smoke`** now translates three
segments and prints them — no scoring, no files, no gates. It deliberately does
**not** check or abort: a diagnostic that hides the symptom is worthless. This
should have existed before the first run, and its absence is why a one-minute
observation cost an hour.

**3. There was no checkpointing.** Now there is: hypotheses are written to
`PATH.partial.json` after every validated batch and resumed automatically.

⚠️ **A fingerprint guards the resume.** Without it, changing the seed, the sample
size or the model and re-running would graft old hypotheses onto a new sample —
well-formed and completely wrong, the same failure shape as the language gate
one layer up. A resumed run also records `resumed_from_partial`, because a
measurement stitched from two sessions is not the same evidence as one clean
pass.

⚠️ **The checkpoint fires only after the count check.** A batch that failed
alignment must never reach disk, or a resumed run rebuilds itself from corrupt
state.

#### ⚠️ A correction: the false claim was in the plan, not the code

This was announced as *"a false claim in my own docstring — it says the script
checkpoints and it does not."* **That was wrong.** `grep` finds no occurrence of
"checkpoint" in `scripts/translate_tico19.py` at all; the sentence lived in the
*plan document*, and the shipped docstring never claimed it.

The substance held — there was no checkpointing, and the 46 minutes were
unrecoverable — but the specific accusation was made **by quoting a file from
memory instead of reading it**, one day after shipping a checker built for
exactly that failure. Recorded rather than quietly dropped, because the whole
point of `check_commands.py` is that unverified claims about this repository are
the recurring defect, and this one was mine about my own file.

#### The twelfth ornament, caught by reverting

⚠️ **The plant asserting `--smoke` writes nothing could not fail.** It listed the
temp directory before and after — and `smoke()` has no reason to write *there*,
so it passed happily when `smoke()` was modified to write into the repository
root. Found by reverting it, never by reading it.

It now forbids writing outright: `builtins.open` in any write mode and
`Path.write_text` both raise for the duration of the call, so a leak anywhere is
caught. **Not counted among the checks that could not fail** — it was caught
during the mandatory both-directions pass before anything relied on it, the same
convention applied to the `open_actions` and `LC_ALL` near-misses. The count
stands at **eleven**.

#### A plant that caught a flaw in itself

The resume plant first used a 6-segment run. `translate_all` batches by 8, so
that is a **single** batch which died before completing — and a failed batch
must not checkpoint. Nothing was written, the plant failed, and the fix was to
the plant: twelve segments, two batches, interrupt after the first.

52 planted cases, up from 48. 188 tests. 20 documented commands checked.

**The cause of the wrong-language output is still unknown** and is not guessed at
here. A control-language diagnostic — the same sentence into Tigrinya, Amharic
and Spanish — will separate a pipeline defect from a finding about MADLAD's
Tigrinya.

### `<2ti>` verified, DEC-011's size corrected, and a token my guide never mentioned — 2026-09-15

Three corrections, all from reading the Hub listing while the owner's first
model download was in progress.

**✅ `<2ti>` is right.** The entry below records it as *"an unverified guess,
checked against nothing"*, which was true when written. It is not now: MADLAD's
language tokens are ordinary Unigram vocab pieces from index 4, sorted
alphabetically, and `"<2ti>"` sits between `<2tet>` and `<2tiv>`.

⚠️ **The gate stays, and the near-miss is the interesting part.**
`tokenizer_config.json` has `"additional_special_tokens": []` and
`tokenizer.json` has `"added_tokens": []`. Had the `<2xx>` prefixes been split
into subwords rather than being real vocab entries, `get_vocab()` would not
contain `"<2ti>"` and the check would have **rejected a valid token and blocked
the run after an 11.8 GB download** — a check firing on correct input, which is
how checks get switched off. They are real pieces, so it does not.

**⚠️ DEC-011 states a size the artefact contradicts.** It says MADLAD-400-3B is
*"1.4 GB at Q4"*, in three places. `model-q4k.gguf` is **1,654,597,280 bytes —
1.65 GB**, and the model card itself says *"1.65 GB vs the original 11.8 GB
file"*. Recorded as **DEC-011 Amendment 1**; the decision is unaffected, since
1.65 GB is still within commodity CPU serving and A-008 still survives.

**This is a figure nothing here could have caught.** `check_figures.py` enforces
every derived count against the tree, and `1.4 GB` was invisible to it because
the ground truth lives on a remote host. It went eight weeks unchallenged inside
an accepted decision.

**⚠️ The migration guide never mentioned `HF_TOKEN`, and it cost an hour.** The
owner's download crawled at **57 kB/s** — about **47 hours** for the remaining
9.3 GB — because the Hub throttles unauthenticated requests. Hugging Face printed
the fix in its own warning, and **the project already knew**: `ACTIONS.md`
records **A-08 — "Set an `HF_TOKEN`" — owner set it 2026-09-03**.

So the information existed, in this repository, and the guide sent them into an
11.8 GB download without it. **That is `hm.download('ti')` again** — a step the
repo knew about, missing from the instructions a person actually follows. The
guide now sets the token *before* any model download, and records that partial
downloads resume so an interrupted fetch costs nothing.

**The real download size is now written down**: `model.safetensors` is
**11,761,587,872 bytes (11.76 GB)** plus ~21 MB of tokenizer. It had never been
stated at all, which is why nobody could have budgeted for it.

**Also fixed from the owner's terminal output:** `transformers` 5.x renamed
`torch_dtype=` to `dtype=` and warns on the old spelling, while 4.x accepts only
the old one. The pyproject floor is `>=4.40`, so both are live — the loader now
tries the new keyword and falls back, rather than pinning the floor upward for a
rename.

No behaviour changed. 48 planted cases, 188 tests, unchanged.

### A model can finally be scored — and it is MADLAD, not NLLB — 2026-09-15

**Nothing in this project had ever loaded a model.** Eleven experiments, a
measurement harness, twenty-nine decisions and a native-speaker instrument, all
built around scoring a translation system, and not one score had ever been
produced. That was the audit's central finding and it is now addressable:
`services/translation/` and `scripts/translate_tico19.py` exist, are tested, and
need only a machine that can download weights.

The product is now defined — **English → Tigrinya health information** — which
settles two questions the audit left open. **TICO-19 is the right anchor rather
than a convenient one**: COVID/medical prose, English source, three independent
Tigrinya references. And the German-vs-English worry is closed.

⚠️ **The 2026-09-13 report recommended NLLB-200. DEC-011 forbids it**, and I did
not check before recommending. Every NLLB variant is CC-BY-NC-4.0, quarantined
as *"never present in a shipped artefact"*. NLLB is behind essentially every
published Tigrinya MT number, which is exactly what makes it the tempting
default for a tool real people use. The baseline is
**`google/madlad400-3b-mt`** (Apache-2.0), chosen by DEC-011 with its *"Tigrinya
quality unmeasured"* recorded at the time. `test_the_model_is_not_nllb` now
fails if `MODEL` is ever repointed, because that breach would otherwise be
invisible — the code would work perfectly.

**The interface is injectable, so the pipeline is tested where the model cannot
load.** `Translator` mirrors `morphology.Analyser` for the same reason: a suite
needing a 12 GB download is a suite that stops being run. Everything but the
model call is covered.

⚠️ **`LANGUAGE_TOKEN` is an unverified guess** — `"<2ti>"`, from the ISO code,
checked against nothing, because `huggingface.co` is unreachable here. That is
the exact shape of `hm.download('ti')` one day earlier. **The translation case
is worse:** an unknown prefix does not fail, it becomes ordinary text, and the
model emits *some* language — fluently, with the right segment count and a
perfectly scoreable chrF. Every check in this repository would pass it.

So there are **two independent gates**, and neither is a warning:

| Gate | Behaviour |
| --- | --- |
| Token not in the tokenizer's vocabulary | refuses at load, **naming what is accepted** |
| Under 50% of non-empty output is Ethiopic | **aborts and writes nothing** |

The second is checked against the model's own vocabulary, never a list chosen
here — the mistake that let `hm.download('ti')` survive six weeks.

**A plant caught a real defect in the second gate.** `ethiopic / non_empty` was
guarded with `if non_empty`, which silently skipped the entire check when the
model returned **nothing at all**. chrF of empty against a reference is 0.00, so
an artefact would have recorded the strongest possible failure as "terrible
translation quality". Found by planting it, not by reading it.

**A second defect, also found by planting:** `main()` passed `out_json`
positionally to a keyword-only parameter. `--self-test` bypasses `main()`, so it
would have surfaced only after a 12 GB download on the owner's machine. There is
now a plant that drives the CLI wiring end to end.

**The judgement sheet is blind.** The human reference is used for chrF and never
shown — including it turns *"is this usable health information"* into *"does it
match the other translation"*, the question chrF already answers. Planted:
putting the reference into the sheet fails the check.

⚠️ **The threshold is pre-committed, in the artefact, before any output exists.**
Fewer than **40 of 100** segments judged usable retires this approach in favour
of DEC-017's ladder with a measured reason. 40 comes from experiment 011: two
professional human translators agree with *each other* at **chrF ≈ 24** on this
same data, so chrF here is not on the scale intuition suggests — and demanding
near-perfect machine output would not be reasonable.

"Usable" is also fixed in advance: *a Tigrinya speaker would come away with the
correct instruction and would not be misled about a dose, a symptom, or a risk.*
Clumsy phrasing is usable; a wrong number is not.

**Scored against `tir_er` and `tir_et` separately** (DEC-010), on `dev` with a
recorded seed, greedy decoding, `shippable=True` — the flag DEC-011 added, used
for the first time on a model that genuinely could ship.

⚠️ **`MadladTranslator.__call__` has never been executed.** It was written with
no access to the weights. Its first run on the owner's machine is its first
test, which is why the token gate is loud and comes first.

48 planted cases, up from 41. 188 tests. 19 documented commands checked.

### Two of the commands this repository printed could not run — 2026-09-15

Every claim here was enforced — figures, dates, derived counts, planted
behaviour — except **the instructions a human follows by hand**. Two of them
were wrong, and one was an error message.

**1. `hm.download('ti')` cannot work, in any version.**
`hm/morpho/languages.py` keeps two mappings: `CODES` maps aliases onto canonical
codes (`'ti'` → `'t'`), and `ABBREV2LANG` holds only the canonical keys.
`hm.analyze()` normalises through `CODES`. **`hm.download()` does not** — it
tests raw membership at `hm/__init__.py:276`. Verified against 5.3.6:

| | |
| --- | --- |
| `'ti' in ABBREV2LANG` | **False** |
| `'t' in ABBREV2LANG` | True |
| `hm.analyze('ti', 'ሰላም')` | `Word`, 1 analysis |
| `hm.analyze('t', 'ሰላም')` | `Word`, 1 analysis |

So `'ti'` analysed fine and downloaded nothing. It appeared in **five** places,
including `_NOT_INSTALLED` and `_NO_LANGUAGE` — **the text shown at the exact
moment a user's language data is missing**, which is the worst place in the
repository for a command that fails. Reported upstream as **A-20**.

⚠️ **The right answer was already in this repository.**
`docs/benchmarks/measurements/README.md` fetches `languages/t.tgz` — the manual
recipe was verified, the printed command was not, and the two were never
cross-read. It survived six weeks because the only environment that could have
run it is blocked from the host that serves the data.

**2. `fetch.py --verify` does not exist.** The Windows migration guide told the
owner to run it. Both `fetch.py` scripts define only `--write`; **bare
invocation is the verify mode.** The line was hedged rather than checked, and a
hedge is not a verified command.

**`LANGUAGE` is now `'t'`** — the canonical form, the one the library uses on
disk, and the only one that works for **both** `analyze()` and `download()`, so
the asymmetry is removed rather than documented. ✅ Measured not to move
anything: over **800 unique TICO-19 anchor words, `'ti'` and `'t'` produce 0
differing analyses**, and the rendered forms our measurements store are
identical.

⚠️ `repr()` was the wrong way to compare them and said all 800 differed.
HornMorpho's `Word.__repr__` embeds a global counter (`W0:`, `W1:`), so
comparing reprs measures the order calls were made in. **Any determinism check
built on `repr()` of a `Word` would report constant false non-determinism** —
ours renders the analysis dicts instead, which is why it does not.

**`scripts/check_commands.py`** now enforces the class: every documented
`python <script>.py --flag` must name a script that exists and a flag that
script declares. Flags are read with **`ast`, never by importing** — importing
`screen_dataset` or an experiment's `run.py` to inspect its parser would execute
it, and a checker with side effects is worse than the defect it catches.

⚠️ **It deliberately does not run anything.** A check that executed documented
commands would need the network and a 159 MB download, and would be switched off
within a week — the failure mode DEC-008 exists to prevent. It checks the two
things most likely to be wrong and cheapest to verify: a flag name and a path.

⚠️ **The checker failed on its own docstring first**, which is the correct
behaviour — and the fix was to stop spelling the examples as command lines, not
to add an "ignore this" marker. Marker vocabularies have silently disabled four
checks here already. The one exclusion, `scripts/tests/`, follows
`check_figures.py`'s existing precedent and for its stated reason: the plant
suite must contain broken commands, and every plant's expected exit status is
itself asserted.

**Planted in both directions.** Six command plants — two defects restored
verbatim, four real commands that must still pass. Two pytest checks assert the
printed abbreviation against **HornMorpho's own `ABBREV2LANG`**, never against a
literal chosen here; with `'ti'` restored they fail with the user's exact error
text.

⚠️ **The checker is not in CI yet, so it enforces nothing on a push.** A commit
touching `.github/workflows/` is rejected here — the GitHub App has no
`workflows` permission — so the step is written out in **A-21** for the owner to
paste. Until then it is exactly the state A-15 existed to fix for the other 28
checks, and saying so is better than implying it is live.

41 planted cases, up from 35. 28 CI checks, unchanged. 178 tests — 174 pass and **4 skip** where 2 did before, because both new abbreviation checks consult HornMorpho's registry and refuse to pretend they ran without it (DEC-028).

### The plant written to close the encoding class missed the next instance — 2026-09-14

The entry below claims *"the fix is the plant, not the eighteen edits"* and that
`ENCODING_PLANTS` *"reruns the entry points with an ASCII default."* Both are
**overstated, and the same day proved it.** It reran **three** entry points from
a hand-written list, and five plants went on failing on Windows.

⚠️ The claim is left standing rather than edited away. Under **DEC-024** a dated
entry is a snapshot, and the overclaim is the useful part of the record: a check
was declared to close a class on the strength of covering three named cases.

**The guard was in a place that does not always run.** `sys.stdout.reconfigure`
went into `if __name__ == "__main__":` in all 23 entry points. But
`scripts/tests/test_plants.py` does:

```python
import measure_morphology as mm
code = mm.main([str(corpus), "--json", str(out)])
```

`main()` **called by import** — so the guard never executes, `main()` prints
Ge'ez into a pipe, and on Windows a pipe is cp1252 whatever the console is.

Reproduced on Linux against the commit that claimed the fix, which is the only
reason it was found at all:

```
env -u PYTHONIOENCODING PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 LC_ALL=C LANG=C \
    python scripts/tests/test_plants.py
```

→ the same five failures, and nothing else. Isolated to stdout and nothing else
by forcing only the child's stdout to UTF-8 under the same ASCII locale: all
five green. The `--json` write path was already correct.

**`force_utf8_stdio()` goes at the top of the entry FUNCTION**, not in the
guard, for the three entry functions reachable by import — `measure_morphology.
main`, `tigrinya_eval.morphology._main`, `tigrinya_eval.primitives._main`. It
no-ops when the stream is already UTF-8, and when the stream has no
`reconfigure` at all, so pytest's `capsys` is left exactly as the caller set it
up. The 23 guard lines stay: they correctly serve a process *launched* as a
script, which is a different situation.

✅ **The proof it is in the right layer: the five plants went green with
`test_plants.py` untouched.** Had the plant needed editing, the fix would have
been papering over the symptom.

**The hand-written list is replaced by the suite itself.** A 35th plant re-runs
**every** plant under an ASCII locale and requires identical behaviour —
measured to reproduce those five failures and nothing else. Whatever is planted
next is covered the day it is added, with no list to maintain. A
`TIGRINYA_PLANTS_ASCII_PASS` variable stops the re-run re-running itself.

Verified in both directions: with `force_utf8_stdio()` removed from
`measure_morphology.main()` alone, the new plant fails — and **only** it —
reporting "5 planted failure(s) did not behave as specified".

⚠️ **Not a twelfth check that could not fail.** `ENCODING_PLANTS` *can* fail; it
was verified three ways the day it was written. It was **incomplete**, which is
a different defect, and the running count stays at **eleven**. Counting it would
repeat the error this entry exists to correct.

⚠️ **Cost: the plant suite now runs roughly twice as long** — it runs itself
twice, once per locale. That is the price of the only check that has caught this
class.

35 planted cases. 174 passed, 2 skipped. No experiment artefact changed —
confirmed rather than assumed.

### The Windows encoding defect was ours too — eighteen sites, one plant — 2026-09-14

Fixing `panphon` cured the **dependency**. Two days later `check_dates.py` and
`test_plants.py` crashed on Windows with the same defect **in this repository's
own code**, and the audit that should have followed the panphon fix had not been
done.

```
UnicodeDecodeError: 'charmap' codec ...   in Thread-7
AttributeError: 'NoneType' object has no attribute 'split'   at check_dates.py:157
```

**Two errors, one cause, and the second one lies.** `subprocess.run(text=True)`
decodes with the locale codec — cp1252 on Windows — and `git blame
--line-porcelain` emits the *content* of every line, which here includes Ge'ez,
`—` and `⚠️`. The decode runs in a **reader thread**: that thread dies, `stdout`
becomes `None`, and `check=True` still sees a process that exited 0. The
traceback then lands sixty lines away, pointing at innocent code.

**The audit found three groups, not two symptoms.**

| Defect | Sites | Consequence on Windows |
| --- | ---: | --- |
| `subprocess.run(text=True)`, no `encoding` | 6 | Decode crash on any non-ASCII child output |
| `write_text(...)`, no `encoding` | 10 | `UnicodeEncodeError` **on write** |
| stdout/stderr not forced to UTF-8 | 23 | `print("⚠️")` fails into a pipe or a redirect |

**The write side was the serious one.** Eight `experiments/*/run.py` could not
rewrite their own `results.json` under a non-UTF-8 locale, so **DEC-016
byte-identity was uncheckable on Windows** — `run.py --check` would crash before
comparing anything.

✅ **The read side was already correct** — every `read_text`/`open` passed an
explicit encoding. A one-directional gap, not rot.

⚠️ **The reported "11 of 30 plants passed" could not be trusted.** A plant
expecting exit 1 **still passes when the child dies of an encoding crash**,
because a crash also exits non-zero. That is precisely the failure this suite
exists to prevent, so it had to be fixed rather than worked around.

**The fix is the plant, not the eighteen edits.** `ENCODING_PLANTS` reruns the
entry points with an **ASCII** default — stricter than cp1252, so anything
Windows rejects is rejected here — and CI catches the regression on Linux.

⚠️ **`LC_ALL=C` alone would have been an ornament.** PEP 538 coerces the C
locale to C.UTF-8 and PEP 540 has a UTF-8 mode, so Python hands back UTF-8
anyway and the plant would pass on every input. `PYTHONCOERCECLOCALE=0`,
`PYTHONUTF8=0` and an unset `PYTHONIOENCODING` are each required; together they
were verified to yield `ANSI_X3.4-1968`, and the write plant now **aborts
loudly** if the locale is ever UTF-8 rather than passing. Caught while writing
it, so it is **not** counted among the checks that could not fail — the count
stands at eleven.

**Verified in both directions, one revert at a time.** Each revert failed
**exactly one** plant, with the error class that revert predicts:

| Reverted | Plant that failed | Error |
| --- | --- | --- |
| stdout reconfigure in `check_figures.py` | `check_figures.py` prints | `UnicodeEncodeError` |
| `encoding=` in `Harness.save()` | `Harness.save()` writes Ge'ez | `UnicodeEncodeError` |
| subprocess `encoding=` in `check_dates.py` | `check_dates.py` prints | `UnicodeDecodeError` |

34 planted cases, up from 30.

**`.gitattributes` removes the line-ending trap** rather than documenting it.
`* -text` stops Git for Windows rewriting LF to CRLF on checkout, which would
break the SHA-256 anchor verification, DEC-016 byte-identity, and the mixed-ending
`validation/sheets/*.csv`. Verified to change no committed byte
(`git add --renormalize` staged nothing new). The migration guide's step 0 now
documents a setting the repository enforces.

**`check_dates.py` also raises `NoHistoryError` when blame output is `None`** —
so a decode failure says *what* failed instead of surfacing as `AttributeError`
in unrelated code.

All 11 experiments re-run: **byte-identical except `006-tier0-latency`**, which
is declared `"deterministic": false` under DEC-016 Amendment 1. 174 passed, 2
skipped.

### Tigrinya transliteration was broken on Windows, from one missing word — 2026-09-14

Following the migration guide on Windows produced **53 failures from a single
root cause**: 6 errors in `test_contract.py`, 47 failures across
`test_primitives.py`, `test_contract.py` and `test_properties.py`. Every one was
downstream of `epitran.Epitran("tir-Ethi")` refusing to construct.

```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 970
```

**The cause is one missing argument in a dependency.** `panphon`
(`featuretable.py:83`) reads its IPA feature table as:

```python
with files("panphon").joinpath(fn).open() as f:
    df = pd.read_csv(f)
```

`.open()` without `encoding` uses the **locale default** — UTF-8 on Linux and
macOS, **cp1252 on Windows**. `ipa_all.csv` has **6,368 lines** containing IPA
characters cp1252 cannot decode, so the table never loads and nothing
transliterates.

Reproduced here before fixing, by forcing a non-UTF-8 locale
(`PYTHONUTF8=0 LC_ALL=C`), which gives the identical failure class under ASCII —
a stricter condition than Windows.

**No upstream fix to take.** `panphon` **0.22.2** is the latest release, checked
against PyPI. A version bump was not an option.

`transliterate._utf8_resource_reads()` now scopes a `pathlib.Path.open` patch
around the epitran load: text-mode opens with no encoding get UTF-8, restored in
`finally`.

- **`pathlib.Path.open`, not panphon's method** — `importlib.resources.files()`
  returns a real `Path`, so that call is what decides the encoding. Wrapping the
  method would mean copying an upstream body and re-copying it every release.
- **Not `PYTHONUTF8=1`** — it works, but it makes correctness depend on how the
  interpreter was launched. A library should not fail because someone opened a
  different terminal.
- **Only one file was ever at risk.** `feature_weights.csv`, read by the same
  pattern at line 105, is pure ASCII — checked rather than assumed, so the fix
  is not guarding something that never needed it.

**Planted, not just tested.** `test_transliteration_survives_a_non_utf8_default_
encoding` forces cp1252 on every platform. Verified in both directions: with the
fix removed it fails with `UnicodeDecodeError` inside pandas; restored, it
passes. 176 tests.

⚠️ **Worth reporting upstream** — one `encoding="utf-8"` in panphon fixes this
for every Windows user of epitran, not just this project.

### Two humans agree at chrF 24 — and measuring it found an eleventh check that could not fail — 2026-09-12

**Experiment 011.** When A-09 lands and the first model is scored, "chrF 30"
needs something to be read against. Now it has one.

| Pair | dev | test |
| --- | ---: | ---: |
| **ER vs ET** — independent translators | **23.84** | **24.58** |
| ti vs ET — one lineage | 85.59 | 83.65 |

All three pre-registered hypotheses confirmed. The `test` figures were seen
during planning so are recorded as MEAS, not as predictions met; that they
reproduced to the decimal is an implementation check.

**H3 is the one that changes how the number reads.** A corpus chrF of ~24 could
be every segment at 24, or half at 5 and half at 45. **It is neither and much
closer to the first:** 80% of segments fall between 13 and 37, only ~3% below 10
and ~2% above 50. So ~24 is the *typical* segment — which makes it a far
stronger reference point.

⚠️ **Not a ceiling.** chrF between two translations and chrF between a system
and a reference are different quantities. ⚠️ **The pair varies twice over** —
translator *and* standard (ER vs ET) — and this cannot separate them. **A-13**
is what would.

**HornMT cannot contribute at all**: one Tigrinya reference, so no second
translator. The handoff said to pre-commit on it; that was wrong and is
corrected.

### ⚠️ An eleventh check that could not fail — the plan of record's own Basis line

Adding the experiment moved the `experiments` count 10 → 11, which should have
flagged the plan's `| **Basis** |` row. **It did not.** A markdown table is one
paragraph, so the `⚠️` in the adjacent `| **Live handoff** |` row exempted every
row of that table. Measured: the Basis line could claim **99 decisions and 77
experiments** and `check_figures.py` exited **0**.

**This is the seventh and the ninth failing together.** The seventh was *"the
plan of record was the one file whose headline numbers nothing verified"*, fixed
by adding the phrasings the plan uses. The ninth narrowed marker scope so a
marker could not reach into the next paragraph — and inside a table there is no
next paragraph. So the phrasings matched, the marker exempted them anyway, and
the plan of record was again the one file whose headline numbers nothing
verified. **Seven of the eleven are in the audit tooling.**

Fixed with the ninth's own asymmetry one level down: **backwards stays generous,
forwards stops at the end of the row.** Scoping strictly to the row was tried
first and **broke every retraction table in the repository**, whose markers
legitimately sit in a header row or the prose above — so the asymmetry is doing
real work, not decoration. Planted; 30 cases now.

### A correction to this session's own verification

A loop here claimed "all 11 experiments reproduce" by running `run.py --check`.
**Nine of them have no `--check` flag**, so the argument was ignored and they
ran in write mode — verifying nothing. It rewrote `006-tier0-latency`, which
measures latency and is declared non-deterministic under DEC-016 Amendment 1
precisely so it is *not* byte-compared. Reverted, and re-verified the way CI
actually does it: **10 byte-identical, 1 exempt by declaration, 0 drifted.**


### The last hand-maintained counts are derived — and doing it wrote the tenth check that could not fail — 2026-09-12

`check_figures.py` now derives **nine** counts, up from seven. The two added
were the last a human kept by hand, and both had already drifted:

| Count | Was | Mechanism |
| --- | --- | --- |
| `plants` | 22 in one document, 25 in another, suite running 27 | new `python_list_lengths` kind — `ast`-parses `test_plants.py`, sums every `*_PLANTS` list |
| `open_actions` | "fourteen … thirteen" against a register holding twelve | new `between` option on `grep_count`, scoping to the register's at-a-glance section |

### ⚠️ A tenth check that could not fail — in the audit tooling, and the ninth's component again

**Registering the plant count produced a check that passed on 29 and on 31.**
`planted` is itself a COUNT_MARKER — prose describing a planted failure quotes a
deliberately wrong number and must not be flagged — so the sentence stating how
many planted cases there are **exempted itself**. Green on any number.

**This is the ninth failing again, not a new kind.** The ninth was
`check_figures.py` suppressing a claim because a `⚠️` sat within ±8 lines, and
it was fixed by narrowing the marker's *window*. Narrowing the window could
never have caught a marker that matches the claim's own **subject**. Six of the
ten are now in the audit tooling.

**The first of the ten caught before it was committed**, and only because it was
tested against a wrong number. A green run on a check you have just written is
not evidence of anything — that is the whole lesson of the other nine, and it
took a deliberate by-hand failure to apply it here.

⚠️ **The 2026-09-02 entry above predicted this**: *"Building blind is how the
tenth gets written."* Half right. There was a tenth. It was not written by
building blind — it was written while building a check **against** drift, by
someone being careful. The wrong half is the more useful one.

**The open-action count would have been an eleventh** — a `⚠️` sat on its claim
line — but it was caught by reading `_has_marker` before the check was ever
registered, so no unfailable check existed. **Not counted**, on the same
principle that kept the variety gate out of the tally.

### Two counts, two different fixes

- `plants` **needs** `ignore_markers`: its subject *is* the marker word.
- `open_actions` **does not** — rewording its claim line to drop the ⚠️ makes it
  fail correctly, measured. Its flag is insurance against a future marker
  landing within eight lines, and is recorded as such rather than left looking
  necessary.

Both flags **remove** a suppression rather than adding one, so the worst they
cost is a false positive.

### One number was deleted rather than derived

*"Twelve need a human"* is 13 minus A-14 — a judgement recorded nowhere
machine-readable. The handoff now names the exception instead of counting it,
which tells a reader *which one* rather than *how many*. Automating a number is
not always the fix; sometimes the number should not be there.

**Also:** both derives **raise** rather than returning 0 or silently widening
when their file, pattern or section boundary goes missing. A derivation that
quietly returns 0 agrees with nothing and is the same defect one level down.
Planted-case count now **29**, guarded by two plants that each move the number
they guard.


### Morphology measured over the whole anchor — and the sample was optimistic — 2026-09-11

**All 9,212 Tigrinya segments of TICO-19**: 194,588 word tokens, 32,990 unique.
11× the 900-segment sample, which this supersedes as the headline.

| Check | Full anchor | Sample (2026-09-08) |
| --- | --- | --- |
| `surface` · `alignment` · `determinism` | **100%** | 100% |
| `coverage` | **116,583/194,588 = 59.91%** | 62.27% |
| `normalisation` | **144/197 = 73.10%** | 31/41 = 75.61% |

### ⚠️ The sample said normalisation never destroys anything. It does.

That is the finding, and no sample was going to produce it. Of 477 words changed
by ጸ/ፀ · ኣ/አ normalisation, 280 are unanalysable either way; of the **197**
informative pairs: **144 unchanged, 22 rescued, 2 LOST, 29 differ** — against
the sample's 31 / 7 / **0** / 3.

Both losses are one shape: normalising ኣ/አ turns **ኣአ into ኣኣ**, and the lemma
*is* ኣአንጋዲ, so the word is rewritten out of the lexicon.

| Word | Normalised | Before | After |
| --- | --- | --- | --- |
| ኣአንጋዲ | ኣኣንጋዲ | `-<ኣአንጋዲ>--` | none |
| ኣአንገድቲ | ኣኣንገድቲ | `-<ኣአንጋዲ>--` | none |

**DEC-010** anticipated this cost without evidence. There is now a named,
reproducible instance, and **only a speaker can rule on it (A-13)** — a far
sharper question than the validation sheets could pose. Direction still favours
normalising (22 rescued against 2 lost, 29 changed), but *"never harmful"* is no
longer available as a claim.

### Running it at all needed a 10× saving

The naive path is ~650,800 analyses — **~31 hours**, all-or-nothing. Measured
first, because the code assumed otherwise: `check_determinism`'s docstring says
*"HornMorpho memoises internally"*; **it does not.** Re-analysing the same 60
words costs **77%** of the first pass.

`scripts/measure_morphology.py` gets it to ~65,980 analyses (**~3.3 h**) from one
observation: `check_determinism` already analyses every unique word twice, so
`surface`, `alignment` and `coverage` can be served from the table its first pass
builds. ⚠️ **Determinism at 100% is what licenses that**, and below 100% the
harness writes nothing at all — which promotes it from one result among five into
**the precondition for the other four**.

**Validated before use, twice**: re-running the 900-segment corpus reproduced all
five numbers exactly, including the whole normalisation breakdown. Five plants
guard the harness — one breaks the recorder's call-through and proves that a real
non-determinism then becomes invisible; two cover a crashing analyser. 27 planted
cases now.

### A second upstream bug — A-19

`hm.analyze('ti', '#')` raises `ValueError`. HornMorpho's lexicon loader parses
comment lines as entries, so `# Light verb particles` becomes the key `'#'` with
three fields and `analyze_unanalyzed5` unpacks it as two. The anchor has nine
bare `#`, in medical product codes like `N95 (series # 1860)` — so the full
corpus hits it and the sample never did.

⚠️ **Two commented-out lexicon entries are also loaded as live data** (`#ዋላ`,
`#ወላ`), silently. Drafted for the owner to send, like A-18.

Counted as unanalysable and **named in the report's notes**, never folded into
"no analysis found": *the analyser threw* and *there is no analysis* are
different facts. 9 of 194,588 tokens, so it does not move 59.91%.


### Morphology is measured — and the analyser found three defects on the way — 2026-09-08

**The first time any morphological property of Tigrinya was measured in this
project.** Until now all five intrinsic checks had only ever reported SKIP.

| Check | Result |
| --- | --- |
| `morphology.surface` | **899/899 = 100%** |
| `morphology.alignment` | **899/899 = 100%** |
| `morphology.determinism` | **4,435/4,435 = 100%** |
| `morphology.coverage` | **10,668/17,133 = 62.27%** — MEAS, a lower bound |
| `morphology.normalisation` | **31/41 = 75.61%** — MEAS |

**The install everyone assumed was impossible took one command.**
`pip install git+https://github.com/hltdi/HornMorpho` — 5.3.6. `NEXT_SESSION.md`
had named that line *"the one untested link and the most likely failure point"*.
It was neither. **Fifth instance** of a block that was assumed rather than
measured.

⚠️ **`import hm` needs `tkinter`**, via an unconditional `from .gui import *`
whose entire package-wide justification is one call site in
`Corpus.disambiguate()`. HornMorpho 5.3.6 cannot be imported headlessly at all —
a fact about the dependency, not about this machine. Now **A-18**. Getting Tk
was its own lesson: `python3.11-tk` lives on the deadsnakes PPA, which the proxy
403s, and the way through was not a workaround but a **permitted source** —
Ubuntu's own `python3-tk` for 3.12, from `archive.ubuntu.com`.

### Three defects, none of them a wrong threshold

Each lived exactly where the injected fake stopped and the real analyser began,
which is why a 175-test suite could not have caught any of them.

1. **`_render` mixed two axes.** A POS tag and a segmentation rendered into the
   same `|`-separated slot — ኣብ came out `ADP|-<ኣብ>--`. **Every** fixture
   supplied `seg`, so the fallback branch had never once executed. Tags are now
   braced. *(Upstream's "contradictory" docstrings were the same thing said
   twice: `Word` subclasses `list`, so it is a list of dicts.)*

2. **The morphology CLI measured English.** `load_corpus` on a parallel anchor
   sweeps in the source language. `data/anchors/tico19` is 6,142 lines of
   English beside 9,213 of Tigrinya — and `experiments/003-metric-validity/data`,
   which **CI has been running morphology over**, is **50% English**.

3. **`check_normalisation` counted an artefact as a finding.** `analyse` falls
   back to the surface form, so a pair where *neither* form is analysable
   compares two surfaces — which differ **by construction**, because differing
   is what normalisation just did. That was **31 of 41** apparent disagreements
   and dragged the headline to **43.06%**, which would have read as
   *"normalisation changes the morphology of most words it touches"* — the
   opposite of the truth. Excluded now, and the rest split four ways.

**What normalisation actually does**, on the 41 informative pairs: **31
unchanged, 7 rescued** (analysable only *after* normalising — it is working),
**0 lost**, **3 differ** (all word-final `አ`→`ኣ`). It helps seven, changes
three, harms none. Only a speaker can rule on the three (**A-13**).

**And a fourth, in the tooling itself:** five tests and **two planted cases**
asserted that HornMorpho is *absent* — assertions about the environment, not the
code. The plant harness announced *"a check has stopped being able to fail"*
when nothing had: **a false alarm inside the one tool whose entire job is to be
trusted about real alarms.** All gated on `is_available()` now, with
present-path mirrors, and skips reported loudly.

### A new category: `docs/benchmarks/measurements/`

For numbers **CI cannot re-derive**. Morphology is the first: GPL-3.0 (never
installed in CI, DEC-028), **~4.1 GB** resident, **~0.85 s per word token** — so
the full anchor is ~40 hours and the measurement is a **900-segment sample**
with each file's SHA-256 recorded.

⚠️ **These carry a weaker guarantee than any `experiments/` entry**, and that
cost is written down rather than hidden. What replaces it: the corpus is
committed, the sample derives from a stated command, the instrument is
unit-tested, and **`coverage` reproduced to the token — 10,668/17,133 — across
two independent three-hour runs.**

### Also found: a TICO-19 reference segment that is not a translation

`dev.tir_et.txt:201` is the literal string **`{to remove}`** — an editor's note
in a published reference. The English is a real sentence and both other Tigrinya
references translate it. It is the **only** such segment in all 9,213. Screening
could not see it: every gate is file-level, and 11 Latin characters in 76,752 are
invisible at that resolution. Honest for a corpus; one level too coarse for an
evaluation anchor, where every score is per segment.

**Also:** `metrics.md`'s morphology row leaves ❌ after 17 days; GAP-5's
measurement half closes; the open-action count in `NEXT_SESSION.md` corrected
from "fourteen" to **twelve** (it had drifted, and nothing derives it).


### The validation sheets are sent — A-13 moves after five weeks — 2026-09-04

**A speaker was found, and the instrument has left the building.** Six files —
`PROTOCOL.md` and the five sheets — sent to the project owner for forwarding
(Gmail `1a06ea200e45622d`).

⚠️ **The last email an agent will send on this project.** That one was
authorised step by step; immediately afterwards the owner set a standing rule
that **no agent sends email, ever**. Drafts are prepared, the owner transmits.
Recorded in `PROJECT_CONTEXT.md` → Standing constraints, and at the head of
`ACTIONS.md` where every draft lives.

⚠️ **A-13 is not closed.** Nothing is validated until filled-in sheets come
back, and the forward itself is not observable from here. The action moves from
*READY TO SEND* to *SENT — AWAITING RETURNED SHEETS*, which is a different
thing.

**`key.json` was excluded by construction, not by care.** The attachment list is
six explicit paths with an assertion that none contains `key.json` or
`manifest.json` — never a directory glob, because `key.json` sits one level
above the sheets and its own first line reads *"ANSWER KEY — do not send to the
reviewer."* Routing through the owner **raised** that risk rather than lowering
it: the mail is forwarded, so a wrong attachment would travel onward in one
click.

#### The reviewer writes the Eritrean standard, and that constrains the result

This must travel with the answers rather than sit implicit. Experiment 010 found
TICO-19's declared-Eritrean side carries **zero** Ethiopian-only markers across
3,071 segments, while **HornMT is Ethiopian-consistent at 55.5%**. An Eritrean
reviewer may therefore mark forms "wrong" that are correct in the other
standard.

**That is a variety difference, not an error.** DEC-010 forbids pooling the two,
so **DEC-025 must attribute every judgement to an Eritrean reviewer** and must
not generalise it to Tigrinya as a whole. One reviewer of one variety **does not
close GAP-1** — it is a large step, and an Ethiopian-standard reviewer remains
valuable.

When the sheets return, `validation/analyse.py` scores them, and its own warning
has to survive into the decision: **accuracy comes only from sheet 4.** Sheets
1–3 deliberately select hard cases, so a headline number drawn from them would
overstate the failure rate.

### CI is green — GAP-2 closed on evidence — 2026-09-04

**All six jobs pass, in 6 check runs rather than 12.** It took two runs, and the
first one is the more valuable of the two.

⚠️ **A standing constraint arrived with activation, unforeseen by anyone.**
Moving `verify.yml` into `.github/workflows/` put it in the one directory an app
token may not write. **Before activation an agent could edit the workflow and
not run it; after activation it can run it and not edit it.** Every future CI
change now needs a human. The working pattern — agent prepares and verifies a
patch outside `.github/`, human runs `git apply` and pushes — was used for this
fix and is documented in `ci/README.md`.

That is the cost of activation, and it was worth paying: the checks have now
been observed both failing and passing, which is the only thing that
distinguishes CI from decoration.

### CI ran for the first time and failed three ways — 2026-09-04

**A-15 is done.** The owner moved `ci/verify.yml` to
`.github/workflows/verify.yml` (`888633d`) — the one step no agent could take,
confirmed twice: `git push` carrying the file is rejected for lacking
`workflows` permission, and the REST contents API returns 403.

**GAP-2 closes.** 28 checks are enforcing rather than merely written. DEC-018
had spent its entire life as policy without mechanism — the exact failure it
exists to prevent.

**The first run failed three of six jobs.** None was a flake.

| Failure | Cause | Fix |
| --- | --- | --- |
| `DEC-027 has no entry in rejected_options.md` | The check iterated every DEC-NNN **mentioned**, not **defined** | Iterate `^## DEC-NNN` headings |
| `ModuleNotFoundError: tigrinya_eval` | `reproducibility` never installed `services/evaluation`; experiment 007 imports it | Add the install |
| 4 planted morphology cases misbehaved | `screening` had **no install at all**, so `sacrebleu` was missing | Add the install |

#### The instructive part is why local pre-flight missed two of them

Before activation, all 28 non-install `run:` blocks were extracted and executed
locally — **28 run, 0 failed**, twice over. That harness **skipped the 7 `pip
install` steps by design**, because the local venv already had everything. So it
was structurally incapable of detecting an install step that installs the wrong
things, and **two of the three failures were precisely that**.

The third was self-inflicted and arrived after the pre-flight finished: a
DEC-002 amendment written minutes earlier cited **DEC-027**, a reserved id for
the endpoint surface that is blocked on A-02 and does not exist as a decision.
The check could not tell a forward reference from a decision — the same
citation-vs-definition confusion already fixed for `G-n`/`GAP-n`. Both
directions are now planted: a real undocumented decision fails, a forward
reference does not.

✅ **The plant suite behaved correctly throughout.** It reported four
`ModuleNotFoundError` failures rather than passing quietly. The environment was
wrong, not the check — which is the outcome the suite exists to produce.

**Also fixed: everything ran twice.** `push: branches: ["**"]` plus
`pull_request` gave 12 check runs for 6 jobs. `push` is now restricted to the
default branch; branch work is already covered by `pull_request`.

**"Verified locally" and "verified" are different claims**, and this is the
first hard evidence of the size of the gap: seven steps a local harness cannot
honestly run, and two real defects hiding in them.

### The readiness plan's autonomous backlog reached zero — 2026-09-02

**§12, "What I can do without you", is empty for the first time.** The plan is
refreshed across phases A–**E** to match, rather than patching the one section.

**What an empty list means, and mostly does not mean.** Not that the project is
nearly finished — the *unblocked* work has run out, which is a much narrower
claim. Two consequences, the second more important than the first:

1. Everything remaining needs a person: send an email, install a workflow,
   obtain a token, read Tigrinya. §4 is now the whole plan.
2. ⚠️ **This is the point of maximum risk of doing harm.** With nothing left to
   unblock, the pull is to build the API surface before A-02 says who it is
   for, or Tier 1 before A-09 lets it be measured — producing more unmeasured
   artefacts. Nine checks in this repository have been found that could not
   fail, every one written in good faith. **Building blind is how the tenth
   gets written.** Stopping is recorded as a deliberate choice, not a default.

**A risk was missing from §11 and is now in it.** Experiment 010 made it
visible: DEC-004 commits this project to both Tigrinya standards, but **55.5% of
HornMT's segments carry an Ethiopian-only marker** while TICO-19's Eritrean side
carries none in 3,071. DEC-010's no-aggregate rule cannot fix a *corpus* that is
skewed — it only stops the skew being averaged away. Rated **Severe**.

#### The plan's own Basis line had an unverified number

As of this entry, the plan's Basis line read
`28 decisions · 10 experiments · 16 summaries · **145 tests** · 5 audits` — the
decisions, experiments and summaries counts are all derived and checked. **The
test count was not**, appeared exactly once in the repository, and had drifted
to 161 unnoticed. That is the same failure this document already records about
its own Basis line, in the one field that escaped the fix.

It is now enforced in CI rather than by `check_figures.py`, deliberately:
deriving it needs pytest to collect, because parametrised cases make a static
`def test_` count wrong (**123 against 161**), and `check_figures.py` has to keep
running with no install. Verified by planting — a wrong count is caught, and so
is the **claim being reworded away entirely**, which is how a check like this
normally dies quietly.

**CI reaches 28 checks.**

### Morphology intrinsic checks — and a third state that is not a pass — 2026-09-02

**`tigrinya_eval.morphology`: five intrinsic checks over morphological
analysis** — surface, alignment, determinism, coverage, normalisation. The last
item in the readiness plan's "what I can do without you" is done.

#### The design problem was not the checks

HornMorpho is GPL-3.0 and never bundled (DEC-028), so it is absent here and on
any clean install. The obvious way to handle that — return early when the
analyser is missing — **manufactures a tenth check that could not fail**, and a
uniquely bad one: the `metrics.md` morphology row would flip from ❌ to ✅ on a
machine where morphology had never once executed.

So `PropertyResult` grew two states that are neither pass nor fail:

| State | Meaning | Behaviour |
| --- | --- | --- |
| **SKIP** | the analyser is genuinely absent | does not fail the build, but the verdict line reads `PASS (with N check(s) NOT RUN)` and a NOT MEASURED block prints. `--require` converts it to a failure |
| **MEAS** | a number with no threshold judging it | reported, never counted as a pass |

`IntrinsicReport.complete` was added alongside `holds`: `holds` answers "should
the build go green", `complete` answers "was the thing measured". They differ
exactly when an optional analyser is missing, and conflating them is how
"morphology is fine" would come to mean "morphology was never looked at".

**Coverage and normalisation are MEAS, not thresholds.** Nothing has ever
measured Tigrinya morphological coverage, so any floor written before the first
real run would be a guess wearing the clothes of a pre-commitment. Coverage is
also explicitly a **lower bound** — `analyse` falls back to the surface form,
which conflates "the analyser could not handle this" with "this word is
genuinely uninflected", and the check says so rather than pretending otherwise.

#### These are tested today, not waiting for an install

Every failure path runs against an **injected analyser**, the same mechanism
`morphology.analyse` already provides for exactly this reason. 16 new tests plus
**6 new planted cases** in `scripts/tests/test_plants.py`: a moving analyser
must fail determinism, a mangled surface must fail the DEC-022 guarantee,
well-formed spans must still pass, and a skip must never read as complete.

Two CI steps guard the distinction itself — one asserts the NOT MEASURED block
is present in the build log, the other asserts `--require` still *fails* with no
analyser. If that second one ever goes green, SKIP has collapsed into PASS and
every morphology property is silently "verified".

**What genuinely waits for an install** is the measurement, and one thing more:
`morphology._render` is written against HornMorpho's *documented* output shape,
which upstream's own docstrings contradict. The report says so on any run where
an analyser is present.

**CI reaches 27 checks.** The `metrics.md` morphology row stays ❌ — by design.

### TICO-19 ingested — and it proved the variety gate was reading backwards — 2026-09-02

**A second clean anchor, and a bigger finding than the anchor.**

TICO-19 is **3,071 English segments** (971 dev, 2,100 test) translated into
Tigrinya three times, CC0-1.0, licence confirmed at source (DEC-030). It is now
committed under `data/anchors/tico19/` with a fetcher, eight screening records,
and a README. `tico-19.github.io` is egress-blocked; `raw.githubusercontent.com`
serves the same bytes.

⚠️ **It is 3,071 segments with 3 references, not 9,213 pairs**, and `fetch.py`
asserts that rather than assuming it — all three Tigrinya files translate
identical English, checked on every fetch.

**Two of the three declare a regional standard at source: `ti-ER` and `ti-ET`.**
No other corpus this project can reach declares variety at all, which is why
DEC-010 has held every corpus at `unknown` for a month. Same source text, same
domain, one variable — a controlled comparison.

#### The variety gate was mostly measuring how much Tigrinya was in the file

[Experiment 010](experiments/010-variety-marker-calibration/) ran that
comparison against three thresholds fixed before looking. **Two were refuted.**

| | Hypothesis | Threshold | Result |
| --- | --- | --- | --- |
| H1 | The reported ratio separates the declared varieties | ≥ 10 points | **REFUTED — 3.3** |
| H2 | Ethiopian-only markers do not fire on Eritrean text | precision ≥ 0.99 | **CONFIRMED — 1.000** |
| H3 | They fire often enough to label a segment | recall ≥ 0.50 | **REFUTED — 0.099** |

The gate scored TICO-19's **declared-Ethiopian** corpus at **91–95%
"Eritrean"**. The ratio pooled ኣ — one of the commonest letters in Tigrinya,
used by both standards, ~4,500 occurrences either side — with the 261 genuinely
discriminative ፀ-series counts. One marker, አ, pointed the wrong way outright.

**This is not a ninth "check that could not fail" and is not counted as one.**
Those were tests that passed regardless of input. This was a *measurement*: the
gate never blocked anything, printed a number faithfully on every corpus for a
month, and the number was noise. Planting a failure would not have caught it —
only a corpus with a known answer could, and the project had assumed none
existed.

#### The consequence reached the primary anchor

**HornMT's README read its own variety numbers backwards.** It recorded "6,237
Eritrean-standard markers against 2,181 Ethiopian — 74/26" as an Eritrean lean.
Calibrated: **55.5% of HornMT segments carry an Ethiopian-only marker, six times
the rate of the corpus TICO-19 declares Ethiopian.** Corrected in place.

DEC-010 is unchanged and **A-13 is still open** — a speaker still rules. What
changed is that the evidence put in front of that speaker now points the right
way.

#### Two screening blocks, both real, neither waved through

- **`test.tir_er` — quality.** The Eritrean test file uses `` ` `` (U+0060) as an
  apostrophe in **215 places** while spelling the same word with U+2019
  elsewhere, and carries **6 × U+2D4F TIFINAGH LETTER YAN** standing in for the
  Roman numeral II. Genuine upstream defects. **Deliberately not repaired** —
  normalising an anchor silently changes every score computed against it.
- **`test.eng` — contamination.** 3 shared 8-grams with HornMT, 0 exact
  segments; all three are the names of the WHO and the CDC. Recorded as a
  *training* prohibition, which is what the gate means and which anchors are
  exempt from by never being trained on.

#### Two defects found in the screening gate itself

- **`×` was a "DECODING FAILURE".** `is_mojibake` tested the raw range
  0x00C0–0x024F, which contains × (U+00D7) and ÷ — maths symbols, category
  `Sm`. Its docstring had said "letters" from the start; the code never did, and
  nothing measured the difference until a corpus with arithmetic arrived.
- **Corruption cannot be decided per character.** `ዘñዘሮን` (the known-corrupted
  sample) and `Vò፥` (the Italian town of Vò, confirmed against the English side)
  are both "an accented Latin letter next to Ge'ez", and are opposite verdicts.
  What separates them is the neighbour's kind: corruption adjoins an Ethiopic
  *syllable*, a borrowed proper noun may abut Ethiopic *punctuation*. The gate
  now tests context, clearing TICO-19's 12 legitimate hits while still catching
  the corrupted sample's single ñ.

#### A ninth check that could not fail — in the audit tooling, again

`check_figures.py` suppressed a claim if a retraction marker sat within ±8 lines
**in either direction**. A `⚠️` opening the *next* paragraph, seven lines below,
silently exempted the claim above it — and one was wrong behind exactly that:
**"Seven decisions now carry amendments"** when the answer was eight. In a
document that uses ⚠️ as often as the readiness plan, whole regions were exempt.

Scope is now **backwards 8 lines, forwards only to the end of the paragraph**.
Two tighter rules were tried and rejected by measurement (43 and 22 false
positives). The fix surfaced 18 further suppressed claims, each triaged: most
were legitimate retraction prose needing marker vocabulary this repo actually
uses ("overturned", "left standing", "retired"), and the rest were genuinely
stale and are fixed.

**Planting is now the test, not a diagnostic.** `scripts/tests/test_plants.py`
commits **16 planted cases** — 7 against the mojibake gate, 9 against
`check_figures` — asserting both that each check fires and that it does not fire
on legitimate text. It runs in CI.

**CI reaches 27 checks.**

### The `G-n` collision resolved across the repository — 2026-09-02

`goals.md` numbers goals **G-1…G-11**; the readiness plan numbered its gaps
**G-1…G-5**. So `G-4` meant *"deliver semantic search and retrieval"* in one
place and *"nothing measured end to end"* in another, and the plan used both
senses four lines apart. The plan's gaps became `GAP-n` yesterday; the other
files are now done.

**22 gap-meaning citations across 6 files**, reclassified **one at a time**:

| File | Renamed |
| --- | ---: |
| `CHANGELOG.md` | 7 |
| `ACTIONS.md` | 6 |
| `docs/decisions/DECISIONS.md` | 5 |
| `data/anchors/hornmt/README.md` | 2 |
| `docs/decisions/rejected_options.md` | 1 |
| `validation/README.md` | 1 |

**A blind substitution was never available.** **13 genuine `G-4` citations mean
the goal** — in the embeddings service README, the ecosystem scan, DEC-026 and
its rejected options, summary 016 — and `sed` would have corrupted every one.
Each site was read and classified: goal or gap.

**Applied retroactively to earlier CHANGELOG entries**, disclosed here because
it edits the record: the rename changes *notation*, not any claim. The entries
refer to the same gaps they always did, under a name that now means one thing.

**Made checkable.** `check_figures.py` gains a third check: every cited `G-n`
and `GAP-n` must resolve to one that is actually defined — goals from
`goals.md`'s `### G-n.` headings, gaps from the plan's table. Validated by
planting one out-of-range id of each kind (both caught), by confirming a valid
gap id is not misread as a goal id (no false positive), and by deleting the gap
table to confirm the check **refuses to run** rather than passing vacuously when
its own definitions vanish.

> The planted ids are described rather than quoted, because naming them here
> would trip the check — a document cannot cite an id that does not exist, even
> to say it does not exist. That is the same trade `check_dates.py` records:
> **reword around a false positive rather than add a suppression path**, since
> a marker vocabulary is what made two earlier checks unable to fail.

⚠️ **What it cannot catch:** a citation pointing at a *real* id with the *wrong
meaning* — precisely the defect just fixed — still resolves. This catches the
cheaper successor: an id nobody defines, which is what a typo or a renumbering
leaves behind.

### Readiness plan refreshed across phases A–D — 2026-09-02

The plan had been patched incrementally through four phases and had stopped
reading as one document. Reconciled, and three inconsistencies fell out of the
reconciliation rather than out of the work.

**⚠️ `G-4` meant two different things in the same document.** `goals.md` numbers
goals `G-1…G-11`; the plan numbered its gaps `G-1…G-5`. So **`G-4` was both
"nothing measured end to end" and "deliver semantic search and retrieval"** —
and the plan used *both senses*, four lines apart. The plan's gaps are now
`GAP-n`.

The collision persists in **~50 citations across 13 other files with the two
meanings mixed**, so it is **recorded, not mass-renamed**: a blind substitution
would corrupt every site that means the goal. Listed in §12 as work outstanding.

**Also reconciled:** the header claimed *fourteen* work items over a section
listing *fifteen* (now sixteen, with Phase D); Tier 0 was still described as
"3 of 4 — morphology is a stub" after DEC-028 and the adapter landed; Phase 2
was still headed "blocked on A-07" after A-07 closed; Phase 4 still warned that
*"if MADLAD underperforms, A-05 is the only remedy"*, which experiment 009 had
just measured as worth about a fifth of its face value; and the count of checks
found unable to fail was **seven** in a document whose own changelog had already
recorded an **eighth**.

**The through-line, now stated in §13.** Across phases A–D the register
described a world that had stopped being true: five actions waiting on emails
whose answers were public, two blockers that were one blocker each, and the
corpus at the centre of the longest-running Blocking item **57% empty**. What
kept those standing was not difficulty — a `curl`, a licence file, a dataset
preview — but a **stale assumption about access**. The register said the answer
was unreachable, so nobody reached.

**And the counterweight, also now stated:** four phases made the *record* true
and moved the *platform* very little. The anchor got 68× bigger and morphology
got an adapter, and **neither is measured**. No speaker has validated a single
output; no model has been scored.

### Experiment 009 — the 1.4M "parallel" corpus is 57% not parallel — 2026-09-02

Phase D. Both Phase D experiments were parked behind **A-09**. Re-testing that
assumption — the Phase B lesson — found the **Hugging Face Dataset Viewer**
serves rows through the connector even though downloads are blocked. So the
corpus nobody had looked at became sampleable.

**A-05 spent months filed as Blocking**, described as the insurance policy on
DEC-011: licence the 1.4M pairs and the training ladder opens. The licence was
argued about for months. **The content was taken on trust from a row count.**

| Hypothesis | Result |
| --- | --- |
| **H1** — a material share of rows have no English side | ✅ **56.9%** — ~794,900 of 1,398,177 rows carry the literal string `nan` |
| **H2** — sorted by similarity, so any prefix flatters it | ✅ monotone 1.2471 → 1.0500 across ten offsets |
| **H3** — the columns are desynced by a constant lag | ❌ **REFUTED by its own threshold** |
| **H4** — one target reused for several sources | ✅ confirmed |

**It is not 1.4M parallel sentences.** It is roughly **603,000 pairs and
795,000 orphaned Tigrinya sentences**, sorted so the readable top is the best of
it. A fifth of the original claim disappears before licensing is even discussed.
**A-05 drops to Medium**, and DEC-030's quarantine now rests on content as well
as licence (**Amendment 1**).

That also makes the published **en→ti chrF 4.99** DEC-030 cites stop looking
like a tokenizer accident.

#### H3 is the honest part

At offset 300000, the English at row *i* appeared to translate the Tigrinya at
row *i−26* — twice, in one 40-row window, at the identical lag, with the
same-row English scoring **zero** anchors both times. The anchors are
language-independent: a shared leading verse number, and proper nouns matched by
transliterating the Tigrinya with **our own Tier 0 primitive** (`ጃፓንን` →
`d͡ʒapanɨn` → skeleton `jpn`).

**It still failed.** The threshold demanded two anchors per candidate and each
yielded one. Two data points at one offset are not evidence of a corpus-wide
defect. **The threshold was not moved**, and the suspicion is recorded as
unproven rather than quietly promoted.

> ⚠️ **An instrument defect, found and recorded.** The anchor test excluded the
> sentence-initial word, reasoning that a capital there proves nothing — but
> *"**Japan** and North Korea…"* begins with its strongest anchor. Fixed by
> dropping the positional rule for a longer-skeleton requirement, which *costs*
> `Korea` and *gains* `Japan`. **The verdict did not change.** Fixing a flaw and
> finding the answer unchanged is worth more than either alone.

**Experiment 009 also gives Tier 0 a second consumer** outside its own tests —
the transliterator is what makes the cross-script anchor test possible, and CI's
reproducibility job now installs `services/primitives` for it.

### Morphology implemented behind the stub — 2026-09-02

`morphology.py` now implements DEC-028: an **adapter over a user-installed
HornMorpho**, never a dependency. 16 new tests, **145 passing overall**.

**Nothing GPL-3.0 is present, and that is not a compromise.** The analyser is
injected, so every path that has to be *correct* — word-level spans, offset
alignment, whitespace preservation, warning suppression, each failure mode — is
exercised deterministically without HornMorpho. Verified by planting three
defects and watching the right test catch each.

**Two upstream traps found by reading HornMorpho 5.3.6's source**, not by
hitting them:

1. **`hm.analyze()` returns `None` when a language cannot be loaded.** Its body
   is `language = morpho.get_language(...)` then `if language:` with no `else`.
   Mapped naively that becomes *"this word has no analysis"* — quietly, for
   every word in a corpus. The adapter treats `None` as a broken install and
   raises with the fix.
2. **Language data is a separate download.** `import hm` succeeds on a fresh
   install with no packs, so `is_available()` checks **both** the import and
   the Tigrinya data. Checking only the import is the mistake that would have
   made trap 1 unavoidable.

⚠️ **One part is explicitly unverified: the shape of an individual analysis.**
HornMorpho's own docstrings contradict each other — `hm.analyze` says *"a list
of dicts"*, the `Language.analyze` it delegates to says *"a Word object"* — and
nothing in this environment can install it to settle the question. So `_render`
accepts either, and when it recognises **neither** it returns the surface form
unchanged **plus a warning naming the keys it actually saw**, rather than
building a confident string out of `str(obj)`. A plausible-looking wrong answer
is worse here than an admitted gap, and the first real install settles it in a
minute.

**GAP-5 does not close.** A clean `pip install` still cannot analyse morphology,
and the `metrics.md` row stays ❌ — implementing a capability is not measuring
it, and a module that exists invites the assumption that it was.

**Also corrected:** three tests and a report note still pointed at **A-07**,
which DEC-028 closed. The evaluation report's morphology note now says why it is
unevaluated (the analyser is GPL-3.0 and never bundled) rather than naming a
resolved blocker.

#### The date check flagged an edit made to satisfy it

Appending a fresh `Updated` stamp to a `metrics.md` table row that already
carried an older `Corrected` one tripped `check_dates.py`: it read only the
**first** stamp on a line. A table row cannot be split to separate its corrections, so a
row that accrues them would fail forever. It now considers **every** stamp on a
line and passes if any matches the commit — the older ones being that line's own
history. Re-verified that a lone stale stamp still fails.

### Three decisions the findings forced — DEC-028, DEC-029, DEC-030 — 2026-09-02

Phase C. Every one of these was research-complete before it was written; none
needed anything from outside.

**DEC-028 — morphology adopts HornMorpho as a user-installed dependency we
never distribute.** The asymmetry is the whole decision: HornMorpho is
**GPL-3.0, not AGPL-3.0** — its §13 is *"Use with the GNU Affero General Public
License"*, not AGPL's *"Remote Network Interaction"*. **Network use is not
distribution**, so a hosted API may call it server-side; the package and any
container image may not contain it. **We may run it for users; we may not hand
it to them.** Without checking which GPL it is, we would have concluded that a
hosted Tigrinya morphology service was closed to us, which is false.

One fact made the choice nearly forced: **HornMorpho is not on PyPI**, so there
is no name pip could resolve. The packaging constraint and the licence
constraint point the same way, and the existing `morphology.is_available()`
stub already has the right shape — this decision adds no machinery, it makes
the placeholder permanent. **A CI check now fails if HornMorpho ever appears in
anything we package or deploy**, verified by planting it in a real
`pyproject.toml`.

⚠️ **GAP-5 does not close.** A clean `pip install` still cannot analyse
morphology. The path is decided, not walked.

**DEC-029 — evaluation anchors v2.** **HornMT is the primary translation
anchor** as of today; **FLORES+ is the comparability anchor**, gated behind one
token (**A-08**); **TiQuAD leaves the MVP anchor set**. It evaluates extractive
QA, and DEC-006's MVP contains no QA — keeping it reproduced the exact mismatch
**DEC-021** was raised to fix. Four conditions now define an anchor: obtainable
without special permission, licence identified at source, screened under
DEC-015, variety-signalled under DEC-010.

> DEC-005 named FLORES-200 and TiQuAD four months ago. **Neither was in usable
> service**: TiQuAD's test set is withheld by design, and FLORES+ had been
> reduced to a **30-sentence sample**. An anchor that cannot be obtained is not
> a weaker anchor — it is not one. Under that test DEC-005's set was empty.

**DEC-030 — parallel data is clean, quarantined, or refused.** The rule that
does the work: **a licence is identified at its source, never from a
re-upload.** Both problem corpora fail it in opposite directions — the 1.4M lost
its licence *to* a re-upload, and Travis Foundation declares CC-BY-SA-4.0 over
material its own authors say they do not own. **A rule that read Hub tags would
have cleared the second and blocked the first**, which is exactly backwards.
Quarantine is explicitly not a queue: the 1.4M leaves it only when upstream
terms are read at source, a contamination screen runs, and provenance is
recorded — none of which is possible today.

**None of this unblocks training.** 2,030 clean pairs is far below any rung of
DEC-017's ladder, and **DEC-017 stands unchanged**.

**A-07 closes**, resolved by DEC-028 rather than by the email it was waiting
for. CI reaches **21 checks** *(the count as of this entry; it has since
grown — a changelog records what was true on the day)*.

### Five actions described a world that had changed — 2026-09-01

Phase B: correcting the record against what is now measurable. Five register
entries were rewritten, and **not one of them needed the email it was waiting
for.**

**A-07 — HornMorpho's licence is answered: GPL-3.0.** `[verified]` from
[`LICENSE.txt`](https://raw.githubusercontent.com/hltdi/HornMorpho/master/LICENSE.txt),
the full GPLv3 text. v5.3.6 (April 2026), Tigrinya and Tigre supported, **not on
PyPI**, and `setup.py` declares no licence metadata at all. The action said
*"GitHub is unreachable from my session"*; `raw.githubusercontent.com` responds
200 and does today. **A blocker sat on the register for weeks because an access
assumption was never re-tested.**

It stops being a question and becomes a decision — and a collision. **DEC-020
chose Apache-2.0 explicitly because "no upstream code imposes copyleft".**
HornMorpho does, and GPLv3 cannot be redistributed under Apache-2.0. → **DEC-020
Amendment 1**, the sixth decision to carry one. The recommended resolution keeps
DEC-020 intact: HornMorpho as an **optional dependency the user installs
themselves**, which is the shape `morphology.is_available()` already has.

> ⚠️ **The amendment's real lesson is about the trigger.** DEC-020 said *"revisit
> when a dependency changes licence"*. That assumes the licence was read once.
> HornMorpho's never changed — it had never been read. The trigger should be
> **"revisit when a dependency is adopted"**.

**A-09 was one action covering two different blockers.** Re-measured: *reading
about* models is open through the Hugging Face connector and was open all along;
PyPI installs `torch` and `sentence-transformers`; **`huggingface.co` direct
downloads are refused**. So A-09 is now exactly one thing — we have the runtime
and cannot get the weights.

⚠️ **And it cost us something concrete.** A-09's own backlog listed *"HornMT — an
unassessed corpus lead"*, under the wrong owner. It was never assessed because
the register said GitHub was unreachable. It is CC-BY-4.0, took one `curl`, and
falsifies the `[verified]` claim that we had 0 cleanly-licensed parallel
sentences.

**A-08 guards a gate, not a rate limit.** `openlanguagedata/flores_plus` returns
**401** — a gated repo, not an egress denial. A read-scope token is what unlocks
the full 997/1,012 devtest. Medium → **High**.

**A-05 is re-uploaded OPUS NLLB bitext.** 1,398,177 rows against EnTiMT's
independently listed 1,398,173. The terms that matter are OPUS's and NLLB's, not
an uploader's permission. Blocking → **High**.

**A-01 reaches Tier 1 after all — through the chain, not the tag.** The
2026-08-23 correction ("Tier 1 is blocked on A-09 alone") was right about the
bi-encoders' declared Apache-2.0 and silent on what they are built from:
`fgaim/tiroberta-base` carries **no licence at all**. Correcting a dependency
error by loosening it too far is its own failure mode, and it took nine days to
notice.

**A-04 gains an alternative and A-11 gains certainty.** TIGQA (arXiv 2404.17194)
is a second expert-annotated Tigrinya QA set the original research never located
— worth assessing before pressing on TiQuAD, since it may not carry A-06's
unresolved-copyright problem. `fidel` re-checked live: `license` null,
`license_expression` null, **no licence classifiers** — `[reported]` becomes
`[verified]`.

**Also corrected:** `services/primitives/README.md`, `PROJECT_CONTEXT.md` and
`RESEARCH_ACCESS.md` all described HornMorpho's licence as unresolved. The
access page additionally records that its clever GitHub workaround was solving a
restriction that **had stopped applying** — a fallback that works becomes a
reason never to re-test the direct route.

### First cleanly-licensed parallel corpus; "zero" was false — 2026-09-01

**HornMT is committed at `data/anchors/hornmt/`** — **2,030 human-translated
English–Tigrinya news pairs under CC-BY-4.0**, screened and cleared on both
sides. It is **68× larger** than the 30-sentence FLORES sample that has served
as the translation anchor, and independent of it: contamination screening found
**0 shared 8-grams and 0 exact segments** against that sample and both committed
monolingual corpora.

**⚠️ It retracts a `[verified]` claim.** The record said, in nine places, that
there were **0 cleanly-licensed parallel sentences**. That was false. HornMT was
public and CC-BY-4.0 the whole time; the zero was measured behind an egress
block that made GitHub unreadable, and never revisited when the block changed.
Registered as a retired figure so `check_figures.py` catches any site still
quoting it.

**What it does not fix.** 2,030 news segments is one domain. Full FLORES+ (997
dev / 1,012 devtest) is what makes our numbers comparable to published work, and
it turns out to be **gated, not blocked** — `401 Unauthorized`, fixed by a
read-scope token. **A-08 moves from Medium to High**; it was filed as "removes
anonymous rate limits".

**A-05 is re-scoped from Blocking to High.** The "1.4M unlicensed pairs" is
`michsethowusu/english-tigrinya_sentence-pairs`, **1,398,177** rows with no
licence and no provenance — and EnTiMT's independent source table lists **"OPUS
NLLB (mined) — 1,398,173"**. It is re-uploaded web-mined bitext, so the question
is OPUS/NLLB's terms, not an uploader's permission. It has also **already been
tried**: a published fine-tune of NLLB-600M on 1.14M cleaned pairs from this
pool scores **en→ti BLEU 0.133, chrF 4.99** with severe repetition. Calling A-05
"the only remedy if MADLAD underperforms" no longer survives contact.

#### Screening could not see the Latin half of a parallel corpus

Pointing the DEC-015 gates at HornMT's English side **blocked a correct file**.
The quality gate reads "foreign" as "not Ethiopic" and treats Latin-1/Extended
letters as decoding failure, so 47 characters in 302,570 — `é í ü á ó ō ı ô ñ ğ
Č Ç`, every one inside a proper noun (Peña, Erdoğan, São) — read as corruption.
That is the identical mistake this gate's own docstring records for ASCII Latin
inside Tigrinya, one script over.

`--script {geez,latin}` fixes it, and is **detected, not asserted**: unlike
licence, script is measurable from the bytes, so a Tigrinya corpus declared
`latin` fails the new script gate before it can skip the Ge'ez gates. On a Latin
side the tests invert and stay strict — corruption is the replacement character
and C1 controls, and "foreign" means **Ge'ez**, which is the signature of
crossed or mis-split parallel files. Four planted failures confirm each path.

**This had already bitten us.** `flores_en.json`, the screening record for the
English half of DEC-005's own anchor, has been sitting in the repo recording
**`BLOCKED — quality`** over a single `ğ`. All five existing records were
regenerated; the known-corrupted sample still blocks, as it should.

#### The counts check could not see a claim that wrapped

`check_figures.py` compares documents line by line, and prose wraps. The README
said **"\*\*24\*\* decisions\nrecorded"** while the repository had 25 — the claim
straddled a line break, so no pattern could match it and the check **could not
fail on the file most people read first**. It now also tests each line joined
with the next. Found by hand; the eighth check found unable to fail.

#### Licence chains, audited against the live Hub

A declared licence on a fine-tune is not a licence for what it was built from.

| Model | Declares | Base | Base declares | Chain |
| --- | --- | --- | --- | --- |
| `tiroberta-bi-encoder` | apache-2.0 | `tiroberta-base` | **NOT STATED** | ⚠️ unresolved |
| `tielectra-bi-encoder` | apache-2.0 | TiELECTRA | **NOT STATED** | ⚠️ unresolved |
| `Hailay/entimt-en-tigrinya-mt` | cc-by-4.0 | `nllb-200-distilled-600M` | **cc-by-nc-4.0** | ❌ conflict |

**A-01 does touch Tier 1 after all** — through the chain, not the tag. The
2026-08-23 correction ("Tier 1 is blocked on A-09 alone") was right about the
bi-encoder's declared licence and incomplete about the weights it was fine-tuned
from. Also recorded: the bi-encoder card says it was trained on "Tigrinya
question-answering and information retrieval datasets", plausibly TiQuAD — which
is one of DEC-005's evaluation anchors, so **scoring it on TiQuAD-derived data
would be contaminated**.

#### Egress re-measured after a month

`RESEARCH_ACCESS.md` was written 2026-07-29 and not re-checked while five
actions leaned on it. `api.github.com` now returns **403** where it returned
200; PyPI installs **torch** and **sentence-transformers**; `huggingface.co`
direct downloads are **refused**. So A-09 was one blocker covering two things:
*reading about* models is open and was open all along, *running* them is not.

### A-17 answered: the commit date wins; 71 dates corrected — 2026-08-24

**The rule: when a document's stamp and the commit carrying it disagree, the
commit is right** — it is the only one of the two that cannot be typed wrong.
**257 corrections across 56 files**, and `scripts/check_dates.py` now holds the
count at **0**.

**Decision dates are pinned to each decision's own record**, not to the blame of
whatever line quotes it. Index rows and `rejected_options.md` entries get edited
long after a decision is taken — DEC-009's row was touched when its amendment
landed — so their blame is the edit, not the decision. Only two shapes bind an
id to a date: a table row where the id sits in the column before it, and the
`DEC-014 — 2026-08-03` form. **Prose does not bind**, and an earlier
id-anywhere rule proved it: *"DEC-008 established the policy in July. Measured
on 2026-08-03"* names an id and a date with nothing to do with each other, and
the rule dated that measurement to DEC-008's day three weeks earlier. Every
`DEC-NNN` date mention now agrees with its decision's record.

**⚠️ One claim was wrong by a factor of six, independently of the drift.**
*"DEC-008 spent three months as policy with no mechanism"* appeared in **eleven
places** — in DECISIONS.md, two summaries, a report, the architecture tree, the
action register and the CI header. DEC-008 is dated 2026-07-29 and the
measurement that found it ignored ran 2026-08-13. That is **15 days**, and three
months was never possible: this repository's first commit is 2026-07-29. Every
interval computed from a corrected date was recomputed:

| Claim | Was | Is |
| --- | --- | --- |
| DEC-008 without a mechanism | three months | **15 days** |
| DEC-022 clause 5 unimplemented | 16 days | **5 days** |
| Assumptions register frozen | three weeks | **25 days** |
| README claimed no licence chosen | sixteen days | **six days** |
| `A-01 → Tier 1` dependency error | three weeks | **25 days** |
| "384/384, zero gaps" left standing | three weeks | **25 days** |
| `is_ethiopic` missing Extended-B | three weeks | **19 days** |

**None of these changed a conclusion.** Each is an argument about how long
something went unnoticed, and each is *stronger* stated correctly — "unenforced
policy is ignored within a fortnight" needs no exaggeration to land.

**The fix would otherwise have tripped its own check.** Blame attributes a line
to whatever commit last touched it, so the commit that corrected 257 dates would
read as the commit that wrote every one of them, and each correctly restored
stamp would look like fresh drift. `.git-blame-ignore-revs` lists it, and
`check_dates.py` passes `--ignore-revs-file`. **Nothing is exempted by content**
— a mechanical commit is made invisible to blame, and that is all; a commit that
changes meaning must stay visible.

**Four lines deliberately keep the old dates.** They state the finding itself
(*"every document date written between 2026-08-21 and 2026-08-23 said
`2026-08-19`"*), and rewriting them would make the record contradict its own
correction.

### Readiness plan refreshed; the dates on this record are wrong — 2026-08-24

**The plan of record now states measured state rather than intent.** Its v0.1
exit criteria are run rather than estimated: **two of six are met outright**
(every MVP capability has a metric; install-to-first-call works), Tier 0 is
three-quarters done, and the two fully open criteria are the two needing a
person. A new §10 lists the ten items delivered since the plan was written.

**⚠️ The plan of record was the one document whose headline numbers nothing
checked.** `check_figures.py` verifies claims like "N decisions recorded", but
the plan states its basis as `25 decisions · 8 experiments · 16 summaries`, a
phrasing no registered pattern matched. **The seventh check found unable to
fail** — and it was wrong when finally checked: the plan claimed **six decisions
carry amendments** when the answer is **five** (DEC-005, 007, 009, 016, 023).
DEC-007 has two amendments and must still count once, which `grep_count` cannot
express.

Three derived counts added, each validated by planting a violation:

| Count | Derived from | Now pinned in |
| --- | --- | --- |
| Decisions carrying amendments | distinct `## DEC-` sections containing `### Amendment` | 1 place |
| CI checks | non-install named steps in `ci/verify.yml` | 6 places, **three of them stale at 14** |
| Native-speaker validation items | data rows across `validation/sheets/*.csv` | 6 places |

**⚠️ The date stamps in this repository are unreliable — 71 of them.** Auditing
this refresh's own timestamp found that **every document date written between
2026-08-21 and 2026-08-23 said `2026-08-19`**: six commits of work stamped with
the previous session's date. Measuring it found the habit is older and wider —
**71 stamps across 34 files are earlier than the commit carrying them, by up to
15 days**. Ten of the 16 summaries and eleven reports are dated 2026-08-03 and
were committed on the 17th and 18th.

It is load-bearing. Arguments here are computed from elapsed time — *"DEC-022
clause 5 sat unimplemented for 5 days"*, *"the register was frozen for 25
days"*, *"DEC-008 spent 15 days as policy with no mechanism"*. **No
conclusion is known to be wrong**; what is gone is the ability to say so without
re-deriving each interval from git.

`scripts/check_dates.py` holds it at a **ceiling of 71** — drift may not grow —
rather than allowlisting the backlog, which would have made the check unable to
fail for the eighth time. Two design errors on the way, both recorded: the first
version compared *every* date against its commit and reported **228** lines,
most of them legitimate backward citations; and the first negative-control file
**suppressed itself**, because its heading contained "planted" and "negative
control", both of which are `COUNT_MARKERS`. That is exactly the marker
generosity `check_figures.py`'s own docstring warns about, demonstrated against
the person who wrote the warning.

**A-17 raised:** decide whether the commit date or the earliest recording
document is authoritative. The backlog is not mechanically fixable until that is
answered — two documents already date the same event differently.

### Embedding evaluation designed; Tier 1 was never blocked on A-01 — 2026-08-23

**Embeddings were the second MVP capability with no evaluation path.** DEC-023
solved three of four primitives intrinsically and explicitly excluded this one,
because the standard method — FLORES+ bitext retrieval — needs one shared vector
space and `tiroberta-bi-encoder` is monolingual. → **DEC-026**

**⚠️ A dependency error, live for 25 days.** `READINESS_PLAN.md` and
`ACTIONS.md` both routed **A-01 → Tier 1 embeddings**. `tiroberta-bi-encoder`
and `tielectra-bi-encoder` are **Apache-2.0** — A-01's own text says so in
parentheses. **Tier 1 is blocked on A-09 (egress) alone.** A graph that
overstates a blocker makes the wrong thing look urgent; A-09 is raised to High.

**Six properties measurable with no annotation**, plus a mandatory lexical
floor. `tiroberta-bi-encoder` is 124.6M parameters and roughly doubles Tier 1's
footprint, so under P-6 and P-7 the question is not "does it work?" but **"does
it beat something free?"**

| Property | Char n-gram baseline | Floor |
| --- | ---: | ---: |
| **E1 orthographic invariance** | **0.2232** | **0.80** ❌ |
| E2 self-retrieval | 1.0000 | 1.00 ✅ |
| E3 discrimination | 1.0000 | 0.95 ✅ |
| E4 corruption monotonicity | 1.0000 | 1.00 ✅ |

**The baseline is a working encoder that cannot handle Tigrinya spelling
variation** — which is precisely the job the neural model has to do. Mixing ጸ/ፀ
is normal practice (1.0–3.8% in Eritrean newspapers), and an encoder that
separates them **fails retrieval silently, for whichever spelling the user did
not type.**

**⚠️ The first version of E1 could not fail.** Measured at *sentence* level, one
substituted character sits among hundreds of features: a deliberately
spelling-blind control scored **identically** to a correct one, 0.9282 both.
Moved to word level, where a correct encoder scores **1.0000**. **The sixth
check in this project found unable to fail on the case that motivated it.**

**Also corrected mid-build:** I wrote that character n-grams are "order-blind by
construction and should score 0" on E5. **Measured 0.2246** — padded n-grams
span word boundaries, so shuffling destroys some. The claim was wrong and the
number is more useful than the claim would have been.

**G-4 is unreachable with this model.** Cross-language retrieval needs a
different model class — an undecided Tier 1 scope question, recorded now rather
than discovered during implementation.

### Duplicate definitions checked; the harness gets its first consumer — 2026-08-23

The last two cross-cutting debt items.

**`is_ethiopic` exists five times and two copies were wrong.**
`experiments/002-tokenizer-fertility/run.py` omitted **Ethiopic Extended-B**
exactly as `screen_dataset.py` had — the defect whose measured consequence was
real Tigrinya failing the quality gate as *"likely mojibake"* at 1.444%. Fixed,
after verifying the experiment's artefact still reproduces byte-identically.

**The duplicates stay, deliberately.** `screen_dataset.py` is stdlib-only
because it decides whether data may enter the project and should run anywhere;
experiments are frozen records whose dependency surface is part of their meaning
as evidence. So `scripts/check_definitions.py` compares every copy over **606
codepoints** and every Ethiopic character, and CI runs it. Negative control:
reintroducing the historical omission is caught on all 32 Extended-B codepoints.

**⭐ `experiments/007-harness-fidelity` is the evaluation harness's first
consumer.** It had tests and nothing else used it — and its own tests are not
independent evidence, having already missed a live inverted-CI bug.

| Hypothesis | Verdict |
| --- | --- |
| **H1 — the harness does not change the number** | ✅ **bit-identical to raw sacrebleu, 4/4 corruption levels** |
| H2 — BLEU never obtainable alone | ✅ |
| H3 — `aggregate()` raises rather than warns | ✅ |
| **H4 — CIs widen as *n* falls** | ❌ **widening breaks at n=3** |

**H4's refutation is the finding.** Median 95% chrF interval width over 20
random subsets: **2.69 (n=30) → 3.06 → 3.87 → 5.02 (n=5) → 4.59 (n=3)**.
Bootstrap resampling of 3 items has only **27 distinct multisets**, so the
interval cannot express the uncertainty it should. **A CI below roughly n=5
understates uncertainty exactly where uncertainty is greatest** — live rather
than theoretical, since our evaluation anchor is 30 sentences and any
per-variety breakdown lands in that range. → **DEC-009 Amendment 1**

**Two of four hypotheses first produced wrong verdicts through defects in the
experiment, not the subject**, and both are recorded rather than quietly fixed:
H2 flagged `sacrebleu_version` because the name contains "bleu"; H4's first
design took `refs[:n]`, varying sentence **content** along with sample size and
producing a false non-monotonic refutation. **Correcting the design changed the
answer** — from "CIs do not widen" to "CIs widen down to n=5 and then break."

### Contract conformance suite; last three doc trees audited — 2026-08-23

Plan items 2 and 3. **The audit found a coverage claim that had been quoted as
"zero gaps" for 25 days while 19 characters were unmapped.**

**⭐ The conformance suite reads the decision, not my memory of it.** DEC-022
clause 5 — "the serving tier is disclosed" — was decided on 2026-08-23 and still
unimplemented on 2026-08-23, surviving a build, a test suite, two audits and a
documentation pass that asserted it. Testing the clauses I happened to recall
would reproduce exactly that. So `test_contract.py` **counts the numbered
clauses in DEC-022 itself** and fails if its map falls behind — verified by
planting a sixth clause — and **pins the payload's exact field set**, so drift
fails in both directions. It found one immediately: `to_dict()` normalised
`spans` to a list but left `warnings` a tuple, so the payload was **not equal to
its own JSON round-trip**.

**⚠️ "384/384 core Ethiopic characters mapped, zero gaps" was wrong.**
Experiment 001 counted **non-empty output**, not phonemes. Only **310 of 384**
transliterate; of the 74 pass-throughs, 26 are unassigned and 29 are
punctuation/digits (both correct), but **16 real syllables and 3 combining marks
come back as raw Ge'ez**. DEC-022 had already drawn the implication; the tooling
survey, its summary and the CHANGELOG had not. Registering the figure surfaced
**five** live occurrences at once.

**`success_metrics.md` marked every capability "Not measured"** — including
transliteration and tokenization, which experiment 004 measured, and
translation, whose metric DEC-009 validated. Same class as `metrics.md` claiming
morphology was validated. Corrected, with the caveat that "measured — intrinsic"
means *self-consistent*, not *correct*, until **A-13** returns.

**`references/models.md` omitted MADLAD-400-3B** — the model DEC-011 adopted —
and listed **NLLB-200 without its CC-BY-NC-4.0 constraint**. That is a licensing
trap in the document someone consults when choosing a model, in a project where
licensing is the binding constraint.

**`goals.md` still said "these goals are pre-research"** with all 13 domains
complete. Updated with what research did to each: G-1 partly delivered, G-2
redefined by DEC-023, G-3 deprioritised by DEC-006, G-8 harder than assumed
(~99% unlicensed), G-11 overdue.

**The five horizon roadmaps now carry supersession banners.** The finding in
`30_days.md` is that **its blocking items are still blocking**: A-01, A-07,
A-02 and A-09 were open on day one and are open now. They were never engineering
problems.

### Native-speaker validation instrument built — 2026-08-23

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

### Readiness plan of record; README claimed no licence was chosen — 2026-08-23

**`docs/roadmap/READINESS_PLAN.md`** is now the execution plan. The horizon
documents (`30_days` … `2_years`) were written **before any research** and are
kept as direction, not sequence.

**What it settles:** "ready" is defined at three levels with **exit tests that
can be run**, rather than left to interpretation. Against v0.1 the project is at
**≈40%** — two of four Tier 0 capabilities, a harness nothing has run through,
and zero speaker validation.

**The five gaps that matter**, separated from the backlog: no native-speaker
validation (**GAP-1**), 14 checks enforcing nothing (**GAP-2**), hollow evaluation
anchors (**GAP-3**), nothing measured end to end (**GAP-4**), and an MVP incomplete
by DEC-006's own definition (**GAP-5**).

**⚠️ A-13 was too narrow and the plan says so.** It covered only a variety audit
of the evaluation anchors. What actually needs a speaker also includes: whether
the phonemes are right at all, the word-final `ɨ` disagreement experiment 005
could not settle (4.53% of tokens, and **we do not know which form is correct**),
and whether normalising ፀ→ጸ reads as a *correction* to Ethiopian-variety users.

**More stale front-door content, same class as the assumptions register.**
`README.md` said **"Licence: Not yet selected"** — six days after DEC-020
chose Apache-2.0 / CC-BY-4.0 and both LICENSE files were committed. It also
cited "DEC-001 … DEC-008", listed completed research as next steps, called four
items blocking when three are, and **had no `pip install` line at all** despite
two installable packages. Fixed, with a real install-to-first-call path.

### Assumptions re-audited; a CI check that could not count — 2026-08-23

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
| **Deferred list** | Still called the project licence "Open, deliberately deferred" — **DEC-020 closed it six days earlier** |

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

### Gap audit: 12 findings, one shipping bug, four checks that could not fail — 2026-08-22

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

### Four architecture documents were empty scaffolds — 2026-08-21

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

### Intrinsic evaluation for Tier 0, and DEC-023's supporting measurement retracted — 2026-08-19

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

### CI extended to the packages; stale cost figures fixed in place — 2026-08-18

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

### Evaluation harness built; DEC-013 cost figures corrected — 2026-08-18

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

### DEC-021 answered: primitive evaluation; DEC-023 — 2026-08-18

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
*(The 99.72% was later **retired** to 100.00% — the five misses were digits, which
a transliterator is supposed to pass through. Left in place as the record of what
was believed on the day; see `figures.json`.)*

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
⚠️ **That follow-up was itself wrong — corrected 2026-08-19, see below.** It
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

### 07_api_mcp researched (partial); DEC-022 — 2026-08-18

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

### 12_master_blueprint — the synthesis; DEC-021 — 2026-08-17

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

### 11_business researched; DEC-020 — A-12 closed — 2026-08-17

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

### 10_infrastructure researched; DEC-018, DEC-019 — 2026-08-17

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

**DEC-018** puts CI behind the decision log. **DEC-008 spent 15 days as
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

### 09_training_strategy researched; DEC-017 — 2026-08-17

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

### 06_ml_pipeline researched; DEC-015, DEC-016 — 2026-08-13

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

### 05_architecture researched; DEC-012, DEC-013, DEC-014 — 2026-08-10

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

### 04_model_strategy researched; DEC-011 — 2026-08-10

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
| Coverage | ✅ 384/384 core Ethiopic characters ⚠️ *superseded — counts non-empty output; phoneme coverage is 310/384 (DEC-022)* |
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
