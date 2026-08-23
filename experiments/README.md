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

**8 experiments complete.** Five of them **refuted** something the project had
already written down — which is the point of the directory, and why rule 3
exists.

## Completed experiments

| ID | Question | Result |
| --- | --- | --- |
| `001-epitran-geez-decomposition` | Does Epitran satisfy DEC-007's decomposition requirements? | Partly — adopt it, but lossless reversibility is unachievable (22 collisions). Amended DEC-007 |
| `002-tokenizer-fertility` | Does decomposition lower BPE token fertility? | **No — it raises it ~8%.** Raw Ge'ez won 10/10 configs, 5/5 folds. Refuted DEC-007's token-efficiency rationale |
| `003-metric-validity` | Are standard MT metrics valid for Tigrinya? | **BLEU is ~8% harsher, not catastrophic.** All 4 hypotheses refuted, all 4 directions correct. chrF adopted primary (DEC-009) |
| `004-primitive-evaluation` | Can the MVP primitives be evaluated without a gold standard? | **Yes — 3 of 4 intrinsic properties hold.** The 4th refuted character-level alignment (23.89%), correcting DEC-007 and DEC-022 to word-level spans |
| `005-word-boundary-epenthesis` | Does a word's transliteration survive being put in a sentence? | **No — 95.47%, not the 100% DEC-023 recorded.** That figure came from a containment test that cannot fail on an appended character. Retracts DEC-023's evidence; the decision survives on a stronger argument |
| `006-tier0-latency` | What does Tier 0 cost in time? | **Cold start 3.03 s, 98.7% of it `epitran`; service time 0.045 ms.** All 4 hypotheses confirmed — loosely enough that the magnitudes matter more than the verdicts. Does **not** close A-14 (Tier 2) |
| `007-harness-fidelity` | Does our evaluation harness change the number? | **No — bit-identical to raw sacrebleu at 4/4 corruption levels.** But H4 refuted: CI width widens from n=30 to n=5 and then **reverses at n=3** — the bootstrap understates uncertainty where it matters most. Two hypotheses first produced wrong verdicts through defects in the experiment, both recorded |
| `008-embedding-baseline` | What must a Tigrinya embedding model beat? | **A free lexical baseline passes the mechanical properties and FAILS orthographic invariance at 0.2232** (floor 0.80). All 4 hypotheses confirmed. The bar for `tiroberta-bi-encoder` is recorded; nothing has been run against it (A-09) |

**001–005, 007 and 008 emit `results.json` and reproduce byte-identically** (DEC-016,
verified 2026-08-19). **006 declares `"deterministic": false`** — it measures
time, so it is run and required to emit an artefact but is not byte-compared
(DEC-016 Amendment 1), and gets no drift detection in exchange.
