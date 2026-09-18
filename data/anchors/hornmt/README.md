# HornMT — English–Tigrinya evaluation anchor

## What this is

**2,030 human-translated news snippets**, aligned line-for-line between English
and Tigrinya, from the HornMT multi-way parallel benchmark for languages of the
Horn of Africa.

| | English | Tigrinya |
| --- | ---: | ---: |
| Segments | 2,030 | 2,030 |
| Words | 47,627 | 43,511 |
| Mean words per segment | 23.5 | 21.4 |
| Non-script characters | 0.00% | 0.026% |

## Attribution

> HornMT — Machine Translation Benchmark Dataset for Languages in the Horn of
> Africa. <https://github.com/asmelashteka/HornMT> · project page
> <https://lesan.ai/benchmark>
>
> Licensed under a **Creative Commons Attribution 4.0 International License**
> (CC-BY-4.0).

Attribution is a **condition of the licence**, not a courtesy. Anything derived
from this corpus and published carries it forward.

## Why this matters more than its size suggests

The project recorded, `[verified]`, that there were **0 cleanly-licensed
parallel sentences** for Tigrinya. That was false, and it was false because the
research that established it ran behind an egress block that made GitHub
unreadable. HornMT is CC-BY-4.0, human-translated, and was a single `curl` away
the whole time.

It also replaces something much weaker. The evaluation anchor in use was a
**30-sentence FLORES sample** — GAP-3 in the readiness plan, "the anchors are
hollow". This is **68× larger** and independent of it: contamination screening
found **0 shared 8-grams and 0 exact segments** against the FLORES sample and
against both committed monolingual corpora.

⚠️ **It does not close GAP-3 by itself.** 2,030 news segments is one domain,
sourced from news sites and multi-way translated. Full FLORES+ (997 dev / 1,012
devtest) remains gated behind an HF token — **A-08**.

## Screening (DEC-015)

Both sides are screened and cleared. `screening/tir.json` and `screening/eng.json`.

| Gate | Tigrinya | English |
| --- | --- | --- |
| Script | ✅ geez, verified from contents | ✅ latin, verified from contents |
| Licence | ✅ cc-by-4.0 | ✅ cc-by-4.0 |
| Quality | ✅ 0.026% foreign | ✅ **0 Ge'ez characters** — the sides are not crossed |
| Variety | ⚠️ **signal only** | n/a — Latin carries no Ge'ez variety markers |
| Contamination | ✅ 0 overlaps vs FLORES sample, TLT, Haddas | ✅ 0 overlaps vs FLORES English |

**The variety signal is the interesting one, and this file used to read it
backwards.**

> *Superseded (2026-09-02).* This section reported "**6,237 Eritrean-standard
> markers against 2,181 Ethiopian** — 74/26" and read it as an Eritrean lean,
> hedged as "evidence, not a verdict". **The hedge was right and the direction
> was wrong.**

[Experiment 010](../../../experiments/010-variety-marker-calibration/)
calibrated those markers against TICO-19, which declares its variety at source.
The pooled ratio turned out to be dominated by ኣ — one of the commonest letters
in Tigrinya, used by *both* standards, appearing ~4,500 times either way. It
buries the discriminative markers under a constant, and it scores TICO-19's
**declared-Ethiopian** corpus at 91–95% "Eritrean". The 74/26 was that artefact,
not a lean.

Measured the calibrated way — segments carrying an **Ethiopian-only** form
(ፀ-series, `እስካብ`, `ብሄራዊ`), which fired on 0 of 3,071 declared-Eritrean
segments:

| corpus | segments with an Ethiopian-only form |
| --- | ---: |
| TICO-19, **declared Eritrean** | 0 / 3,071 — 0.0% |
| TICO-19, **declared Ethiopian** | 303 / 3,071 — 9.9% |
| **HornMT (this corpus)** | **1,127 / 2,030 — 55.5%** |

**HornMT is Ethiopian-consistent, at six times the rate of the corpus TICO-19
labels Ethiopian.** Under DEC-010 the label still stays `unknown` until a speaker
rules (**A-13**) — but this is now the evidence that speaker is shown, and it
points the opposite way from what this file said when it was written earlier the
same day. The corpus that corrected it was one `curl` away throughout, which is
the second time on this anchor that the binding constraint was a stale belief
about reachability rather than the data.

That matters beyond bookkeeping: HornMT is the primary evaluation anchor, so a
model tuned against it is being tuned toward whatever variety it is written in.

## Reproducing the committed copy

```bash
python3 fetch.py            # verify committed bytes against upstream
python3 fetch.py --write    # refresh, then commit the result
```

`fetch.py` compares SHA-256 against a recorded digest and re-checks alignment.
If upstream is unreachable it verifies the committed copy instead and says so.

### The alignment trap it checks for, and does not find here

Two files are only parallel if both split into the same number of lines.
`str.splitlines()` breaks on more than `\n` — U+2028, U+0085, `\x0b`, `\x0c` —
so one stray separator on one side shifts every later pair against its
translation and the corpus still looks fine. EnTiMT hit exactly this in raw NLLB
bitext: 84 U+2028 in the English file, 4 in the Tigrinya.

**Measured here: it does not happen.** Both sides give 2,030 under
`split("\n")` and `splitlines()` alike, no exotic separator is present, and no
line is blank. Recorded as a negative result (**P-13**) so nobody re-derives it,
and re-checked on every fetch anyway — it is one comparison and the failure mode
is invisible.

## What this is not

- **Not training data.** It is an anchor; training on it destroys it (DEC-008).
- **Not variety-labelled.** See above.
- **Not a licence opinion on the underlying news.** HornMT declares CC-BY-4.0
  over snippets extracted from news sources listed in its own `metadata.tsv`.
  We record what upstream declares; the position on third-party source text is
  the same open question **A-06** raises for TiQuAD.
