# Scripts

## Purpose of this directory

Operational tooling: the scripts that process data, run evaluations, and handle
deployment.

## Why this directory exists

Reproducibility (**P-5**) requires that things be done by scripts rather than by
hand. A processing step performed manually once is a step that cannot be
repeated, audited, or trusted — and the person who performed it will not remember
what they did.

If `datasets/processed/` cannot be regenerated from `datasets/raw/` by running
something in here, the data pipeline is broken.

## Structure

| Directory | Contents |
| --- | --- |
| `data_processing/` | Ingestion, cleaning, normalisation, transformation |
| `evaluation/` | Evaluation harnesses and benchmark runners |
| `deployment/` | Build, release, and deployment automation |

## Rules

1. **Deterministic.** Same input, same output. Seed anything random.
2. **Idempotent where possible.** Re-running should be safe.
3. **Documented.** Every script has a header explaining what it does, what it
   expects, and what it produces.
4. **No secrets.** Read from environment; document required variables.
5. **Logged.** Record what ran, when, on what input, and with which version.
6. **Versioned outputs.** Processed data records the script and commit that
   produced it, so any artefact traces back to its lineage.

## Script header convention

```
Purpose:   What this does
Inputs:    What it expects, and where
Outputs:   What it produces, and where
Usage:     Exact invocation
Requires:  Environment variables, dependencies
```

## What future contributors should add

Scripts, as pipelines take shape. Prefer many small composable scripts over one
large one — pipelines change, and small pieces are easier to recombine than to
disentangle.

## Status

**Empty.** No pipelines exist yet.
