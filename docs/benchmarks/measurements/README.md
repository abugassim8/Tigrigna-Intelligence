# Measurements

Numbers produced by running an instrument over a corpus, where the run is
**too expensive or too dependency-bound for CI to re-derive**. Everything CI
*can* re-derive lives in `experiments/` instead, and DEC-016 requires those to
reproduce byte-identically on every push.

This directory exists because morphology is the first thing in the project that
does not fit that rule, and pretending otherwise would have meant either
dropping the measurement or putting a number in `metrics.md` that nothing
re-checks.

## The second thing that does not fit: translation

**`translation-en-ti-*.json`**, produced by `scripts/translate_tico19.py`, is
here for the same reason and a different dependency: `google/madlad400-3b-mt` is
**~12 GB to download and 6 GB resident**. CI re-runs every `experiments/*/run.py`
and byte-compares its artefact; it cannot do that with a model of this size.

⚠️ **The model is Apache-2.0, which is the whole point.** DEC-011 quarantines
every NLLB variant as CC-BY-NC-4.0 — *"never present in a shipped artefact"* —
and NLLB is behind essentially every published Tigrinya MT number. A score
measured on MADLAD describes something that could actually ship; the published
NLLB numbers do not.

### Reproducing it

```bash
pip install -e "services/translation[madlad]"
python3 scripts/translate_tico19.py --self-test
python3 scripts/translate_tico19.py --json docs/benchmarks/measurements/translation-en-ti-DATE.json --sheet validation/sheets/6_translation_judgement.csv
```

`--self-test` runs the whole pipeline against an injected stub — no model, no
network — and is what CI and this sandbox can exercise. Run it first: it proves
the sampling, alignment, scoring and sheet-writing work, so a failure in the
real run is the model's and not the plumbing's.

| Guarantee | Held by |
| --- | --- |
| Sampling is reproducible | seed `20260915`, and the selected ids are recorded in the artefact |
| Decoding is reproducible | greedy — `num_beams=1`, `do_sample=False` |
| Varieties are not conflated | scored against `tir_er` and `tir_et` separately (**DEC-010**) |
| The output is actually Tigrinya | two independent gates — the language token is checked against the tokenizer's vocabulary, and the output against Ethiopic blocks. Below 50% Ethiopic the run **aborts and writes nothing** |

⚠️ **chrF is not the finding, and reading it as one will mislead you.**
Experiment 011 measured two professional human translators agreeing with *each
other* at **chrF ≈ 24** on this same data. The finding is the judgement sheet,
whose threshold — fewer than 40 of 100 usable retires the approach — is written
into the artefact before any output exists.

## Why morphology cannot be an `experiments/` entry

| Constraint | Value, measured 2026-09-07 |
| --- | --- |
| Dependency | **HornMorpho 5.3.6, GPL-3.0** — never installed in CI (**DEC-028**) |
| Throughput | **~0.85 s per word token**, all five checks included — 17,135 tokens is ~4 h |
| Resident memory | **~4.1 GB** once the Tigrinya FST is loaded |
| Cold start | **~20 s** to load the language |

CI installs neither the analyser nor its 159 MB of language data, and the
`intrinsic` job deliberately asserts that morphology **SKIPs** there — that
assertion is what stops a skip from quietly reading as a pass. A reproducibility
job that re-ran this would take hours and would have to install a GPL-3.0
package into the build, which is the one thing DEC-028 forbids.

⚠️ **So these numbers carry a weaker guarantee than any experiment in this
repository**, and that is a real cost, recorded rather than hidden. What is
guaranteed instead: the corpus is committed, the sample is derived by a stated
command, the instrument is committed and unit-tested, and the sample's SHA-256
is recorded below so a re-run can prove it measured the same bytes.

## `morphology-2026-09-11.json` — the full anchor

**Every Tigrinya segment in TICO-19**: 9,212 texts, **194,588 word tokens,
32,990 unique**, across both splits and all three references. This supersedes
the 900-segment sample below as the headline measurement.

| Check | Result |
| --- | --- |
| `surface` | **9,212/9,212 = 100%** |
| `alignment` | **9,212/9,212 = 100%** |
| `determinism` | **32,990/32,990 = 100%** |
| `coverage` | **116,583/194,588 = 59.91%** — MEAS, a lower bound |
| `normalisation` | **144/197 = 73.10%** — MEAS |

### What the sample could not see

The 900-segment sample is not wrong, but it was **optimistic**, and in one place
it was qualitatively misleading:

| | Sample (900 seg) | Full anchor | |
| --- | ---: | ---: | --- |
| coverage | 62.27% | **59.91%** | 2.4 points lower |
| words changed by normalisation | 72 | **477** | |
| … **rescued** (working) | 7 | **22** | |
| … **lost** (a distinction destroyed) | **0** | **2** | ⚠️ |
| … **differs** (both analyse, differently) | 3 | **29** | |

⚠️ **The sample reported that normalisation never destroys anything. It does.**
Both cases are the same shape, and both are lexical:

| Word | Normalised | Analysis before | After |
| --- | --- | --- | --- |
| ኣአንጋዲ | ኣኣንጋዲ | `-<ኣአንጋዲ>--` | none |
| ኣአንገድቲ | ኣኣንገድቲ | `-<ኣአንጋዲ>--` | none |

Normalising ኣ/አ turns the sequence **ኣአ into ኣኣ**, and the lemma itself is
ኣአንጋዲ — so normalisation rewrites the word out of the lexicon. This is exactly
the cost **DEC-010** anticipated without evidence, now a named, reproducible
instance. **Only a speaker can rule on it (A-13).**

Direction still favours normalising on this corpus — 22 rescued against 2 lost
and 29 changed — but "never harmful" is no longer available as a claim.

**Every one of those cases is listed in
`morphology-2026-09-11-normalisation-cases.json`** — all 2 lost, 29 differs and
22 rescued, with the analysis before and after. The run's own `results.json`
caps its examples at eight, and these are the sharpest question **A-13** can be
asked, so they are kept in full rather than left to be re-derived from a
three-hour run.

⚠️ **Held, not sent.** Whether the reviewer sees a second round is the owner's
call.

### Corpus

`data/anchors/tico19`, all six Tigrinya reference files. The directory also
holds the English source, which the CLI's script filter drops, along with
`dev.tir_et.txt:201` (`{to remove}`) — 6,143 lines filtered, 9,212 measured.

| File | SHA-256 |
| --- | --- |
| `dev.tir_er.txt` | `0177c1965714997b1d960b1334fb9534645ab5a31f91f099c84a133414169877` |
| `dev.tir_et.txt` | `17ed98c8261d7173a66a630e8381109eabdc5d57575017df5e53bd90a9bf89f9` |
| `dev.tir_ti.txt` | `fa3bbf7afe95201bb4459974fcff1b7379a73a59ef307849e9e91fa1f252f1e6` |
| `test.tir_er.txt` | `72d077fe9107e13ed85aa9c7cdde19560ced2b4060f877eb363cf945fbc57114` |
| `test.tir_et.txt` | `1002828fccdde9731d6b819bc2577d0c2b3acb11b5feb1012d79e1358f6913fd` |
| `test.tir_ti.txt` | `585bd74968632e7cb61aaf116185fa4049ba3cb8569da1b60ef45dca6ed979ce` |

⚠️ **`tir_er` is the only independent translation.** `tir_ti` and `tir_et` are
one lineage (chrF 83.65 between them), so this is not three independent samples
of Tigrinya.

### One word crashes the analyser

`hm.analyze('ti', '#')` raises `ValueError`. HornMorpho's lexicon loader parses
comment lines as entries, so `# Light verb particles` becomes the key `'#'` with
a three-field value, and `analyze_unanalyzed5` unpacks it as two. The anchor has
**nine bare `#`**, in medical product codes like `N95 (series # 1860)`.

Counted as unanalysable and **named in the report's own notes**, never folded
into "no analysis found" — *the analyser threw* and *there is no analysis* are
different facts. It costs 9 of 194,588 tokens (0.005%), so it does not move
59.91%, and it is an **upstream defect, not a property of Tigrinya**. Reported
as **A-19**.

### How it was run

Not the CLI — `scripts/measure_morphology.py`, because the naive path is
~650,800 analyses (**~31 hours**) and this is ~65,980 (**~3.3 hours**). The
saving comes from one observation: `check_determinism` already analyses every
unique word twice, so `surface`, `alignment` and `coverage` can be served from
the table its first pass builds.

⚠️ **Determinism at 100% is what licenses that**, and the harness aborts writing
anything at all if it is less. So `check_determinism` is not one result among
five here — **it is the precondition for the other four.**

**Validated before use, twice**, by re-running the 900-segment corpus below and
requiring it to reproduce all five numbers exactly — which it did, including the
whole normalisation breakdown. Three planted cases guard it, one of which breaks
the recorder's call-through and proves a real failure then becomes invisible.

```bash
/tmp/venv312/bin/python scripts/measure_morphology.py data/anchors/tico19 \
  --json docs/benchmarks/measurements/morphology-2026-09-11.json \
  --checkpoint /tmp/anchor-table.json
```

---

## `morphology-2026-09-08.json`

**The first time any morphological property of Tigrinya was measured in this
project.** Before this, all five checks had only ever reported SKIP.
**Superseded as the headline 2026-09-11** by the full anchor above, and kept for
two reasons: it is the project's only cross-run reproduction evidence — two
independent three-hour runs agreeing to the token — and it is now the fixture
that validates `scripts/measure_morphology.py`.

⚠️ **This is the second run. The first one's headline was wrong**, and the way
it was wrong is worth more than the number.

`check_normalisation` compares the analysis of a word against the analysis of
its normalised form. But `analyse` falls back to the **surface form** when
nothing is renderable — so when *neither* form is analysable, the two
"analyses" are the two surfaces, and those differ **by construction**, because
differing is precisely what normalisation just did. Every such pair was being
counted as a disagreement.

On this corpus that artefact was **31 of 41 apparent disagreements**. It
dragged the reported agreement from 76% down to **43.06%**, a number that would
have gone into `metrics.md` and read as *"normalisation changes the morphology
of most words it touches"* — the opposite of what the data says.

The check now excludes pairs that are unanalysable in both forms, and splits
the rest four ways — **same**, **rescued**, **lost**, **differs** — because
those mean different things and a single ratio hides it. Only `lost` and
`differs` are costs. The first run's output was discarded rather than kept
alongside: it is the output of an instrument now known to be wrong, and keeping
it invites someone to quote it.

*(Same class as the two defects the install itself exposed: not a wrong
threshold, but the instrument measuring something other than what it named.)*

### Corpus

TICO-19 dev, the **first 300 segments** of each of the three Tigrinya
references — the same 300 English source segments rendered three ways, so
coverage is comparable across varieties and the ጸ/ፀ · ኣ/አ normalisation check
has both an Eritrean and an Ethiopian rendering to compare.

| File | SHA-256 of the 300-line sample |
| --- | --- |
| `dev.tir_er.txt` | `afedd0a64ef541c5e5a44770eb043e3e0cce34375e1bbbb7eaba4b790b991b80` |
| `dev.tir_et.txt` | `ccba5bbf147518dd1681fbe7f4260a5f6a80649f6f5b674e6fb3d16539647d33` |
| `dev.tir_ti.txt` | `3976a1470f80068903f59dd19e4f4b813827072939b7924ec2249f11f4901222` |

⚠️ **A sample, not the anchor.** 900 of the anchor's 9,213 Tigrinya segments —
**17,135 word tokens, 4,437 of them distinct**. At 0.85 s/word the full anchor
is roughly **40 hours**; that is the only reason it is a sample. The sample is
the *head* of each file, not a random draw, so it is trivially reproducible and
equally trivially non-representative of anything the head does not contain.

⚠️ **One segment in the sample is not Tigrinya.** `dev.tir_et.txt:201` is the
literal string `{to remove}`, an editor's note that survived into the published
reference — see the anchor's README. The CLI's script filter drops it, which is
how it was found, so the run measures **899** segments.

⚠️ **Only `tir_er` is an independent translation.** `tir_ti` and `tir_et` are
one translation lineage (chrF **83.65** between them — see
`NEXT_SESSION.md` Part 3), so the three files are **not** three independent
samples of Tigrinya.

### Reproducing it

Needs a Python with `tkinter` — `import hm` fails without it, which is a
property of HornMorpho, not of any one machine (see
`docs/research/RESEARCH_ACCESS.md`, and **A-18**).

```bash
# 1. an interpreter with tkinter. Ubuntu noble: python3-tk is for 3.12.
apt-get install -y python3-tk
python3.12 -m venv /tmp/venv312

# 2. the analyser. NOT into the project venv, and never committed (DEC-028).
/tmp/venv312/bin/pip install "git+https://github.com/hltdi/HornMorpho"
/tmp/venv312/bin/pip install -e services/primitives -e services/evaluation

# 3. the Tigrinya language data, 158,902,071 bytes. HornMorpho's own
#    get_language_url() builds a github.com/.../raw/... URL, which is 403 from
#    this network; the LFS media host serves the same bytes.
LD=/tmp/venv312/lib/python3.12/site-packages/hm/languages
curl -sSL -o $LD/t.tgz \
  https://media.githubusercontent.com/media/hltdi/HornMorpho/master/src/hm/languages/t.tgz
/tmp/venv312/bin/python -c "from hm.morpho.languages import uncompress_lang; uncompress_lang('t')"

# 4. the sample, and the run
mkdir -p /tmp/morph-sample
for v in tir_er tir_et tir_ti; do
  head -300 data/anchors/tico19/dev.$v.txt > /tmp/morph-sample/dev.$v.txt
done
/tmp/venv312/bin/python -m tigrinya_eval.morphology --require /tmp/morph-sample \
  --json docs/benchmarks/measurements/morphology-2026-09-08.json
```

**Expect it to take about four hours.** The sample is **17,135 word tokens**
(4,437 unique) across 900 segments — TICO-19 is medical prose and averages 19
words a segment, which is roughly three times what a general-domain corpus of
the same line count would give. `--require` is what makes a SKIP a failure, so
if the analyser is not actually reachable the run fails instead of quietly
reporting nothing.

⚠️ **There is no progress output**, and the checks are sequential, so nothing is
written until all five finish. Run it detached.

### Worth sharpening next

**`morphology.coverage` has the same shape of conflation** that
`check_normalisation` was just fixed for — but *documented*, which is the whole
difference. It counts "analysis equals surface" as uncovered, which merges two
populations: words HornMorpho could not analyse, and words it analysed correctly
whose analysis simply *is* the surface form (a genuinely uninflected word). That
is why it is reported as a **lower bound** with no threshold.

It could now be decomposed the same four-way way, by asking whether the analyser
returned anything at all rather than comparing strings. That would turn a lower
bound into a real number. It needs a pass over the uncovered tokens (~90 min),
and it is **not** urgent: unlike the normalisation artefact, this one is stated
plainly wherever the number appears and does not distort the headline in a
misleading direction.

**Dated by completion, not by start.** The run began 2026-09-07 and finished
after midnight UTC; A-17's rule is that the commit date wins, so the file
carries **2026-09-08**.

⚠️ **Exact reproduction is not guaranteed** the way an `experiments/` entry's
is. HornMorpho is installed from `master`, not a tag — `5.3.6` is the version it
declared on 2026-09-07 — so an upstream change can move these numbers with no
signal here. If a re-run disagrees, check the upstream commit before assuming a
regression on this side.
