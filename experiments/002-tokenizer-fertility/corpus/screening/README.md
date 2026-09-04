# Screening records (DEC-015)

One record per committed corpus file, produced by
`scripts/data_processing/screen_dataset.py`. **DEC-015 requires datasets to
carry a screening record**; until 2026-08-22 the rule had none — five corpus
files were committed with zero records, while the CI job was *named* after the
rule but only tested that the tool fails closed.

Regenerate:

```bash
python3 scripts/data_processing/screen_dataset.py <corpus.txt> \
    --licence <spdx-id> --eval-set <other-corpus.txt> \
    --json screening/<corpus>.json
```

## Reading a verdict

- **`CLEARED for use`** — all four gates pass.
- **`BLOCKED — quality`** on `tlt_001_CORRUPTED_sample.txt` is **intended**. It
  is the deliberately corrupted sample kept as a negative control; if it ever
  clears, the quality gate has stopped working.
- **`BLOCKED — quality`** on `flores_en.txt` is **also expected and not a
  defect**. It is the *English* side of the FLORES+ parallel pair, and the
  quality gate measures non-Ethiopic characters, so English scores ~100%
  foreign. The gate is Tigrinya-specific by design; the record documents the
  file rather than endorsing it as a Tigrinya corpus.

Licences are **asserted, never detected** (P-9, A-009): `mit` for
`mewaeltsegay/TigrinyaLargeText`, `cc-by-sa-4.0` for
`SIMBA9657/haddas-tigrinya-corpus` and FLORES+.
