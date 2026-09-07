# Measurements

Numbers produced by running an instrument over a corpus, where the run is
**too expensive or too dependency-bound for CI to re-derive**. Everything CI
*can* re-derive lives in `experiments/` instead, and DEC-016 requires those to
reproduce byte-identically on every push.

This directory exists because morphology is the first thing in the project that
does not fit that rule, and pretending otherwise would have meant either
dropping the measurement or putting a number in `metrics.md` that nothing
re-checks.

## Why morphology cannot be an `experiments/` entry

| Constraint | Value, measured 2026-09-07 |
| --- | --- |
| Dependency | **HornMorpho 5.3.6, GPL-3.0** — never installed in CI (**DEC-028**) |
| Throughput | **~0.85 s per word token**, all five checks included |
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

## `morphology-2026-09-07.json`

**The first time any morphological property of Tigrinya was measured in this
project.** Before this, all five checks had only ever reported SKIP.

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

⚠️ **A sample, not the anchor.** 900 of the anchor's 9,213 Tigrinya segments.
At 0.85 s/word the full anchor is roughly **42 hours**; that is the only reason
it is a sample, and the sample is the *head* of the file, not a random draw, so
it is trivially reproducible and equally trivially non-representative of
anything the head does not contain.

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
  --json docs/benchmarks/measurements/morphology-2026-09-07.json
```

**Expect it to take about an hour.** `--require` is what makes a SKIP a failure,
so if the analyser is not actually reachable the run fails instead of quietly
reporting nothing.

⚠️ **Exact reproduction is not guaranteed** the way an `experiments/` entry's
is. HornMorpho is installed from `master`, not a tag — `5.3.6` is the version it
declared on 2026-09-07 — so an upstream change can move these numbers with no
signal here. If a re-run disagrees, check the upstream commit before assuming a
regression on this side.
