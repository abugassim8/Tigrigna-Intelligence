# Models

## Purpose of this directory

Model artefacts, experiment records, and evaluation results.

## Why this directory exists

Models are the most visible part of a language platform and the least valuable
part in isolation. What makes a model useful is knowing how it was produced, what
it scores, and whether that score can be trusted. This directory is organised
around that: the evaluations are the point, the weights are an implementation
detail.

## Structure

| Directory | Contents |
| --- | --- |
| `experiments/` | Per-experiment model artefacts and configs. Messy is fine here. |
| `checkpoints/` | Model weights and serialised artefacts. Not tracked in git. |
| `evaluations/` | Evaluation results. **Tracked in git — this is the record.** |

## The asymmetry that matters

`checkpoints/` contains large binaries that git cannot usefully hold and that can
usually be regenerated or re-downloaded.

`evaluations/` contains small JSON and markdown files that constitute the
project's entire empirical record. **These are tracked, permanently.** If we lose
a checkpoint we retrain or re-download. If we lose an evaluation we lose the
knowledge of whether anything ever worked.

## Before adding any model

Two questions, in order:

1. **Can we reuse something instead?** (**P-1**) The default is to adopt an
   existing model. Building or training requires justification.
2. **Do we have a way to evaluate it?** (**P-4**) A model with no evaluation
   cannot be compared, improved, or honestly described. Evaluation comes first.

Any model in this directory must trace back to a decision in
`docs/decisions/DECISIONS.md`.

## Model card requirement

Every model — adopted, adapted, or trained — has a card:

```markdown
# Model: <name>

- **Source:** original model / fine-tune of X / trained from scratch
- **Licence:** and what it permits (mandatory — P-9)
- **Capability:** what it serves
- **Base model:** and its licence, if derived
- **Training data:** with lineage to `datasets/`, if trained or tuned
- **Evaluation:** scores, on which set, with which metric, on what date
- **Known limitations:** be specific
- **Inference requirements:** hardware, memory, latency
- **Cost per 1k requests:** measured, not estimated
- **Decision record:** DEC-NNN
- **Maintainer:**
```

Store as `<name>.card.json` or `README.md` alongside the artefact. Cards are
tracked in git.

## Evaluation record format

Results in `evaluations/` must record the model version, evaluation set version,
metric implementation and version, date, and the command that produced them.
A score without those is not reproducible and therefore does not count (**P-5**).

## On training

The default answer to "should we train this?" is **no** — see **A-004**, **P-2**,
and **N-5**. Training carries data cost, compute cost, evaluation cost, and
permanent maintenance burden.

If you are proposing training, the case belongs in
`docs/research/reports/09_training_strategy/` and must articulate the proprietary
advantage created and cost the alternative of not training.

## What future contributors should add

Model cards, evaluation results, and experiment records. Record models that were
**evaluated and rejected** in `docs/research/references/models.md` — knowing that
a model produces unusable Tigrinya output is a finding worth keeping (**P-13**).

## Status

**Empty.** No models selected. Model strategy is
`docs/research/reports/04_model_strategy/`, which is gated on evaluation research.
