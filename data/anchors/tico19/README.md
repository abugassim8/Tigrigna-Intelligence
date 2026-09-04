# TICO-19 — English–Tigrinya evaluation anchor, **variety-labelled**

## What this is

**3,071 English segments** (971 dev, 2,100 test) from the TICO-19 COVID-19
translation benchmark, each translated into Tigrinya **three separate times** —
and two of those three carry a **regional standard declared at source**.

| | segments | declared | translators |
| --- | ---: | --- | ---: |
| `*.eng.txt` | 3,071 | English source | — |
| `*.tir_er.txt` | 3,071 | **`ti-ER`** — Eritrean | 2 |
| `*.tir_et.txt` | 3,071 | **`ti-ET`** — Ethiopian | 1 |
| `*.tir_ti.txt` | 3,071 | `ti` — unspecified | 3 |

⚠️ **This is 3,071 segments with 3 references, not 9,213 pairs.** All three
Tigrinya files translate the identical English; `fetch.py` asserts that rather
than assuming it. Counting them as separate data would inflate the corpus 3×.

## Why this is the most useful corpus the project has found

**No other reachable Tigrinya corpus declares its variety.** DEC-010 has had to
hold every corpus at `unknown` because nobody upstream said which standard they
were writing. TICO-19 says, on the same source text, twice.

That makes it a **controlled comparison** — same English, same domain, same
lengths, one variable — and the first opportunity to check whether this
project's variety markers measure variety at all.

**They largely did not.** [Experiment 010](../../../experiments/010-variety-marker-calibration/)
used this corpus and found the screening gate's marker ratio scores the
**declared-Ethiopian** file at **91–95% "Eritrean"**. The ratio was pooling a
swamping non-discriminative letter (ኣ, ~4,500 counts in both files) with the 261
genuinely discriminative ones, and one marker pointed the wrong way outright.

The consequence reached the primary anchor: **HornMT's README read its own
variety numbers backwards**, and has been corrected. Ingesting this corpus was
worth it for that alone.

## Attribution and licence

> TICO-19 — Translation Initiative for COvid-19.
> <https://tico-19.github.io> · repository
> <https://github.com/tico-19/tico-19.github.io>
>
> "All content is made publicly available through a Creative Commons CC0
> license." — the project's own `index.md`, corroborated by `LICENSE.md`
> (full CC0 1.0 Universal text).

Licence identified **at source**, as DEC-030 requires — not inferred from an
aggregator.

⚠️ **The row-level `license` column describes the English source text, not the
translations.** Upstream records the provenance of every segment, and it is
mostly share-alike:

| declared over the source string | segments (per variant) |
| --- | ---: |
| CC_BY-SA_3.0 (Wikipedia, Wikivoyage, Wikinews) | 1,903 |
| CC BY 4.0 (PubMed / NCBI) | 939 |
| CC_BY-SA_2.5 | 88 |
| public (CMU medical sentences) | 141 |

So TICO-19 declares CC0 over translations of text that is itself CC-BY-SA-3.0.
We record what upstream declares (DEC-020). The open question about third-party
source text is the same one **A-06** raises for TiQuAD and the HornMT README
raises for news snippets — it is not resolved here, and this corpus is used as
an **evaluation anchor**, never redistributed as source text.

## Screening (DEC-015)

Eight records in `screening/`. Six clear; **two are blocked and both blocks are
real.** They are recorded rather than waved through.

| file | verdict | note |
| --- | --- | --- |
| `dev.eng` · `dev.tir_er` · `dev.tir_et` · `dev.tir_ti` | ✅ CLEARED | |
| `test.tir_et` · `test.tir_ti` | ✅ CLEARED | |
| `test.tir_er` | ⚠️ **BLOCKED — quality** | 0.152% foreign, threshold 0.1% |
| `test.eng` | ⚠️ **BLOCKED — contamination** | 3 shared 8-grams with HornMT |

### `test.tir_er` — an orthographic defect in upstream, left unrepaired

The Eritrean test file uses **`` ` `` (U+0060 GRAVE ACCENT) as an apostrophe in
215 places** — `ከምኡ`ውን` — while spelling the same word `ከምኡ’ውን` with U+2019
elsewhere in the same file. It also carries **6 × U+2D4F TIFINAGH LETTER YAN**
standing in for the Roman numeral II (`ታይፕ ⵏⵏ` for "type II pneumocytes"), and
some zero-width spaces.

These are genuine upstream defects, not decoding damage. **They are deliberately
not repaired**: normalising an evaluation anchor silently changes every score
ever computed against it. The block is recorded, explained, and left standing.

### `test.eng` — three shared 8-grams, all of them organisation names

```
director general of the world health organization who
the united states centers for disease control and
united states centers for disease control and prevention
```

Two of the three are the same name at different offsets, and **0 exact segments
match**. Two COVID-era corpora both naming the WHO and the CDC is not shared
provenance. The gate's verdict — "CONTAMINATED, do not train on this" — is a
*training* prohibition, and TICO-19 is an anchor that is never trained on
(DEC-008). It stands as recorded: anyone who does train on TICO-19's English has
contaminated HornMT as an evaluation set.

## What the variety evidence actually says

| file | segments carrying an Ethiopian-only form | reading |
| --- | ---: | --- |
| `test.tir_er` *(declared Eritrean)* | **0 / 2,100** | eritrean-consistent |
| `test.tir_et` *(declared Ethiopian)* | 184 / 2,100 = 8.8% | ethiopian-consistent |
| `test.tir_ti` *(unspecified)* | 214 / 2,100 = 10.2% | ethiopian-consistent |

The Eritrean side contains **zero** ፀ-series characters, `እስካብ` or `ብሄራዊ` across
3,071 segments. Under DEC-010 the label still stays `unknown` until a speaker
rules (**A-13**) — but the evidence is now calibrated rather than backwards.

The unlabelled `ti` file tracks the Ethiopian one, consistent with the other
measurement here. After normalising whitespace and apostrophes, over all 3,071
segments:

| pair | identical renderings |
| --- | ---: |
| `ti` vs `ti_ET` | **1,240** (40%) |
| `ti_ER` vs `ti_ET` | **2** |
| `ti_ER` vs `ti` | **0** |

`ti` and `ti_ET` are the same translation lineage; `ti_ER` is independent of
both, agreeing with four other translators on 2 segments out of 3,071.

## Reproducing the committed copy

```bash
python3 fetch.py            # verify committed bytes against upstream
python3 fetch.py --write    # refresh, then commit the result
```

Upstream is a ZIP of TSVs; the committed files are line-per-segment text, so the
**derivation is part of the artefact** and is re-run and compared byte-for-byte,
not merely hashed. `fetch.py` verifies the archive digest, all six member
digests, asserts the three references share one English source, and re-checks
line alignment. Five planted failures confirmed each check fires.

`tico-19.github.io` is egress-blocked here; `raw.githubusercontent.com` serves
the same bytes — see `docs/research/RESEARCH_ACCESS.md`.

### A trap worth knowing about

`dev.en-ti.tsv` and `test.en-ti.tsv` spell the translator column
**`translator_ID`**; the four variety files spell it **`translator_id`**. A
loader that hardcodes one reads five files and fails on the sixth — or silently
gets nothing.

## What this is not

- **Not training data.** It is an anchor; training on it destroys it (DEC-008).
- **Not variety-*labelled* by us.** The labels are TICO-19's. They calibrate our
  instrument; they do not discharge **A-13**.
- **Not a general-domain corpus.** It is COVID-19 and medical text, from
  Wikipedia, PubMed, Wikivoyage and CMU medical sentences. One domain, and a
  narrow one.
