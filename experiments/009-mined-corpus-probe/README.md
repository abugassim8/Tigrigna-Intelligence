# Experiment 009 — Is the 1.4M "parallel" corpus parallel?

| Field | Value |
| --- | --- |
| **Experiment ID** | `009-mined-corpus-probe` |
| **Date** | 2026-09-02 |
| **Status** | **Complete — H1, H2, H4 confirmed; H3 REFUTED by its own threshold** |
| **Related decisions** | Evidence for **DEC-030**; weakens **A-05** |
| **Determinism** | Byte-identical across runs and across `PYTHONHASHSEED` |

---

## Question

**A-05** spent months filed as *Blocking*, described as the insurance policy on
DEC-011: get a licence for **1.4M English–Tigrinya parallel sentences** and the
training ladder opens. DEC-030 re-scoped it after finding the corpus is
re-uploaded OPUS NLLB mined bitext, but left the substantive question alone:

**Is it actually 1.4M parallel sentences?**

Nobody had looked. The corpus was quarantined on *licence* grounds and its
*content* was taken on trust from a row count.

## Method, and its limits

`huggingface.co` downloads are blocked (**A-09**), but the **Dataset Viewer**
serves rows through the connector. Ten offsets were sampled across the corpus
and the observations recorded by hand in `sample/observations.json`; `run.py`
reads only that committed file, so **the analysis reproduces byte-identically
while the fetch does not**.

⚠️ **This is a probe, not a census.** Roughly 60 rows out of 1,398,177 were
seen. Findings are lower bounds: what is here is here, and absence of a defect
in the sample proves nothing.

## Hypotheses and thresholds, fixed before looking

| | Hypothesis | Pre-committed threshold |
| --- | --- | --- |
| **H1** | A material share of rows have **no English side** | Confirmed if **>25%** |
| **H2** | The corpus is **sorted by similarity**, so any prefix flatters it | Confirmed if similarity is monotone non-increasing across sampled offsets |
| **H3** | The two columns are **desynchronised** by a constant lag | Confirmed only if, for **every** candidate, the lagged English shares **≥2** language-independent anchors with the Tigrinya *and* strictly more than the same-row English |
| **H4** | One Tigrinya sentence is **reused** for several English sources | Confirmed if a target repeats with distinct sources |

**Anchors** are signals that survive translation and need no Tigrinya
competence: a shared leading verse number, or an English proper noun whose
consonant skeleton appears in the Tigrinya *after transliterating it with our
own Tier 0 primitive*. `ጃፓንን` transliterates to `d͡ʒapanɨn`, whose skeleton
contains `jpn`.

## Results

| Hypothesis | Measured | Verdict |
| --- | --- | --- |
| **H1** | The English column stops carrying text at row **~603,250** (bracketed 594,000–612,500). **56.9%** of rows — roughly **794,900** — have `nan` where English should be | ✅ **CONFIRMED** |
| **H2** | Similarity falls monotonically from **1.2471** at row 0 to **1.0500** at row 1,398,100 across all ten offsets | ✅ **CONFIRMED** |
| **H3** | Both candidates favour the lagged English, at the **same lag of 26 rows**, with the same-row English scoring **zero** anchors — but each yields only **one** anchor, and the threshold demanded two | ❌ **REFUTED** |
| **H4** | Rows 300017 and 300018 carry Tigrinya identical after whitespace normalisation, with unrelated English sources | ✅ **CONFIRMED** |

### H1 — the headline

**About 795,000 of the 1.4M rows are not pairs.** They are Tigrinya sentences
with the literal string `nan` in the English column. The corpus is more
accurately described as **~603,000 pairs and ~795,000 orphaned Tigrinya
sentences**.

### H3 — refuted, and the refutation is the honest part

At offset 300000 the English at row *i* appeared to translate the Tigrinya at
row *i−26*, twice, in a single 40-row window:

| Tigrinya row | Same-row English | English 26 rows later |
| --- | --- | --- |
| 300000 — *"**2** ሎሚ፡ … ብብከላን ብዓመጽን…"* | "**24** Joʹab the son of Zeruiah…" | *"**2** Today, we see mankind's home marred by **pollution, violence**…"* |
| 300001 — *"ኣሜሪካ … **ጃፓንን** ደቡብ **ኮርያን** … ዲፕሎማሲያዊ…"* | "Be still my heart...such LOVELIES!" | *"**Japan** and North **Korea** have never established **diplomatic** relations."* |

The pattern is visible and the lag is identical. **It still does not clear the
bar**, because a single sentence pair rarely carries two independent anchors,
and the threshold was set at two before any of this was seen.

**The threshold was not moved.** Two data points at one offset are not evidence
of a corpus-wide desync; they are a reason to look properly, which needs the
corpus itself (**A-09**).

> ### ⚠️ An instrument defect, found and recorded
>
> The first version of the anchor test **excluded the sentence-initial word**,
> on the reasoning that a capital there is not evidence of a proper noun. But
> *"**Japan** and North Korea…"* begins with its strongest anchor, and the rule
> silently discarded it.
>
> Fixed by dropping the positional rule and requiring a longer consonant
> skeleton instead — which costs `Korea` (`kr`, 2 characters) and gains `Japan`
> (`jpn`, 3). **The verdict did not change.** Recorded because fixing a flaw
> and finding the answer unchanged is worth more than either alone.

## What this changes

**A-05's premise is now measurably weaker than "unlicensed but large".** Even
granting a licence tomorrow, the corpus is:

1. **57% not parallel at all** (H1);
2. **sorted**, so the readable top is the best of it and everything sampled
   below row 200,000 sits at similarity ≤ 1.077 (H2);
3. **self-duplicating** at the target side (H4);
4. and **possibly column-desynced**, unproven (H3).

Points 1–3 are enough on their own to explain the published result DEC-030
records — a fine-tune of NLLB-600M on 1.14M cleaned pairs from this pool
scoring **en→ti chrF 4.99**. That number stops looking like a tokenizer
accident.

**DEC-030's quarantine stands, and its basis widens** from licence alone to
licence *and* content.

## Reproducing

```bash
cd experiments/009-mined-corpus-probe
python3 run.py          # needs tigrinya-primitives for the transliterator
```

Re-fetching the sample is **not** reproducible here — the Dataset Viewer is
reached through an MCP connector, not from this container. `sample/observations.json`
records the offsets so a session with corpus access can check every claim.

## What would settle H3

Download the corpus and test the lag properly: for each candidate lag *k*,
count rows where English *i* and Tigrinya *i−k* share an anchor, and compare
against lag 0. With ~600,000 usable pairs the signal would be unmistakable
either way. Blocked on **A-09**.
