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

Four scripts, all enforcement rather than pipeline.

| Script | Purpose | Enforces |
| --- | --- | --- |
| `data_processing/screen_dataset.py` | Runs DEC-008's four screening gates over a corpus; fails closed with no licence or eval set | **DEC-015** |
| `check_figures.py` | Fails when a retired figure is quoted as current, or a document contradicts the repository about a count; `--list` prints the register in `docs/figures.json` | **DEC-024** |
| `check_definitions.py` | Fails when the duplicate copies of `is_ethiopic` or `normalise` disagree on any codepoint | **DEC-022** |
| `check_dates.py` | Fails when a date stamp is older than the commit carrying it, above a recorded ceiling; `--list` prints the backlog | **A-17** |

All four run in CI (`ci/verify.yml`), which is **not yet installed** — see **A-15**.

**`check_dates.py` needs full git history.** Its job in CI sets
`fetch-depth: 0`; the default shallow checkout has no blame to read and the
check would silently see nothing.

No data pipelines exist yet.
