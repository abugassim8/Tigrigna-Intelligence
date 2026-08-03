# Experiments

## Purpose of this directory

Exploratory work: notebooks, trial runs, quick tests, and the results and logs
they produce.

## Why this directory exists

Research needs somewhere to be messy. Experiments try things that will not work,
take shortcuts, and get abandoned halfway — and that is exactly what they are
for. Keeping this separate from `services/` means production design can stay
disciplined while exploration stays fast.

**Experimentation is separate from production design.** This directory is the
former. Nothing here is production code, and nothing here should be depended on.

## Structure

| Directory | Contents | Tracked in git |
| --- | --- | --- |
| `notebooks/` | Jupyter notebooks and exploratory scripts | Yes |
| `results/` | Experiment outputs | Small structured files only |
| `logs/` | Run logs | No |

## Rules

1. **Use the experiment template** — `../docs/research/templates/experiment_template.md`.
   Copy it to `NNN-slug/README.md` **before** running anything.
2. **State the hypothesis and success criteria before running.** A hypothesis
   recorded afterwards is not a hypothesis, and without a pre-committed threshold
   every result looks like a partial success.
3. **Record negative results.** A refuted hypothesis that is written down saves
   the next person from running the same experiment (**P-13**).
4. **Reproducibility still applies.** Seeds, versions, hardware, exact command.
   Messy is fine; irreproducible is not (**P-5**).
5. **Promotion requires evaluation.** Work moves to `services/` only after a
   result recorded in `models/evaluations/` and a decision in `DECISIONS.md`.
6. **Notebooks are not production.** If a notebook does something valuable, the
   valuable part gets rewritten properly. Notebooks are for finding out, not for
   running.

## Naming

`NNN-slug/` — e.g. `001-tokenizer-fertility/`, `002-embedding-morphology-probe/`

## What is tracked

Notebooks and small structured results are tracked. Bulk outputs and logs are
not — see `.gitignore`. The rule of thumb: track what tells you *what was
learned*, not what the run *produced*.

## What future contributors should add

Experiments, each with its template filled in. Especially the ones that failed —
those are the ones nobody writes up, and the ones most likely to be repeated.

## Status

**1 experiment complete.**

- [`001-epitran-geez-decomposition/`](001-epitran-geez-decomposition/) —
  tested whether Epitran satisfies DEC-007's requirements for a Ge'ez
  consonant–vowel decomposition substrate. **3 of 4 criteria passed; the
  reversibility failure turned out to be the most useful result** and amended
  DEC-007. Reproducible: `run.py` re-executed and reproduces exactly.

## Completed experiments

| ID | Question | Result |
| --- | --- | --- |
| `001-epitran-geez-decomposition` | Does Epitran satisfy DEC-007's decomposition requirements? | Partly — adopt it, but lossless reversibility is unachievable (22 collisions). Amended DEC-007 |
| `002-tokenizer-fertility` | Does decomposition lower BPE token fertility? | **No — it raises it ~8%.** Raw Ge'ez won 10/10 configs, 5/5 folds. Refuted DEC-007's token-efficiency rationale |
