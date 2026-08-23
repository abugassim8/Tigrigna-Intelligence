#!/usr/bin/env python3
"""
Build the native-speaker validation instrument (READINESS_PLAN 1.1, A-13).

Why this exists
---------------
**Every intrinsic check this project runs catches *broken*, not *wrong*.** A
transliterator returning confidently incorrect phonemes passes all six of them.
Nothing here has ever been seen by someone who reads Tigrinya, and DEC-007 says
plainly that native-speaker validation is required before anything ships
user-facing.

This script turns that from "find someone" into "send them this."

Design decisions worth knowing
------------------------------
**Stratified, not random.** A random sample would spend a volunteer's scarce
time on easy cases. Each stratum answers one specific open question, and each is
independently analysable, so **partial completion is still useful** — a reviewer
who stops after sheet 1 has still settled the most valuable question.

**Forced choice with the answer hidden.** For the word-final `ɨ` question the
two candidate forms are shown in **randomised order with no indication of which
one we produce**. Asking "is our output right?" invites agreement; asking "which
of these is right?" does not. The mapping is written to `key.json`, which is for
analysis and must never be sent to the reviewer.

**IPA is a barrier, so it gets a key.** Our output uses `ʔ ɨ ə ħ ʕ t͡sʼ` and a
fluent speaker who is not a linguist has no reason to read those. The
pronunciation key is generated **from the corpus** — each symbol is anchored to
a real Ge'ez character that produces it — rather than written from assumption.

Reproduce:
    pip install -e services/primitives
    python3 validation/generate.py
"""

from __future__ import annotations

import csv
import json
import pathlib
import random
import unicodedata
from collections import Counter

from tigrinya_primitives import NORMALISED_CHARS, normalise
from tigrinya_primitives.transliterate import _epi, transliterate_word

HERE = pathlib.Path(__file__).parent
SHEETS = HERE / "sheets"
REPO = HERE.parent

#: Fixed so the instrument is reproducible and two reviewers can be given the
#: same sheets (DEC-016's spirit; this emits a manifest rather than results).
SEED = 20260819

#: Sized to respect a volunteer's time. ~135 items at roughly 10 seconds each is
#: under half an hour, and the sheets are ordered most-informative-first.
TARGET = {"A_vowel": 25, "B_frequent": 35, "C_normalisation": None, "E_random": 40,
          "F_variety": 20}

CORPORA = {
    "tlt": REPO / "experiments/002-tokenizer-fertility/corpus/tlt_000_clean.txt",
    "haddas": REPO / "experiments/002-tokenizer-fertility/corpus/haddas_001_colscrambled.txt",
    "flores": REPO / "experiments/003-metric-validity/data/flores_ti.txt",
}
#: `haddas` is column-scrambled, so it supplies words but never sentences.
SENTENCE_SOURCES = ("flores",)


def load():
    return {k: p.read_text(encoding="utf-8") for k, p in CORPORA.items()}


# ------------------------------------------------------ pronunciation key

def _units(s: str) -> list[str]:
    """Split a transliteration into units a reader would treat as one sound.

    A base letter plus any following combining marks and modifier letters is one
    unit, so `t͡sʼ` is presented as itself rather than as three mysterious
    characters — which is how it would look split apart.
    """
    out = []
    for ch in s:
        # U+0361 COMBINING DOUBLE INVERTED BREVE *joins* two letters, so the
        # character after it belongs to the same unit: `t͡s`, not `t͡` + `s`.
        if out and out[-1].endswith("\u0361"):
            out[-1] += ch
        elif out and unicodedata.category(ch) in ("Mn", "Lm"):
            out[-1] += ch
        else:
            out.append(ch)
    return out


def pronunciation_key(words) -> list[dict]:
    """Anchor every non-obvious unit to Ge'ez text that produces it.

    Built from the corpus, not from a textbook: if a unit never appears in our
    output there is no reason to explain it, and if it does the reviewer should
    see it beside something they recognise.
    """
    counts = Counter(u for w in words for u in _units(transliterate_word(w)))
    interesting = [u for u in counts
                   if not all(c.isascii() for c in u)
                   and unicodedata.category(u[0])[0] in "LM"]

    chars = sorted({ch for w in words for ch in w if 0x1200 <= ord(ch) <= 0x137F})
    short_words = sorted(words, key=lambda w: (len(w), w))

    anchors = {}
    for u in interesting:
        # A single character is the clearest anchor when one exists.
        for g in chars:
            if u in _units(transliterate_word(g)):
                anchors[u] = g
                break
        else:
            # `ɨ` has no single-character anchor — it is epenthetic, which is
            # precisely why sheet 1 exists — so fall back to the shortest word
            # that produces it. Without this the key omitted its most important
            # entry, the one appearing 1,419 times.
            for w in short_words:
                if u in _units(transliterate_word(w)):
                    anchors[u] = w
                    break

    rows = []
    # Tie-break on the unit itself: `words` is a set, so equal-count entries
    # would otherwise order by hash and the manifest would not reproduce.
    for u in sorted(interesting, key=lambda x: (-counts[x], x)):
        g = anchors.get(u, "")
        rows.append({
            "unit": u,
            "appears": counts[u],
            "example_geez": g,
            "example_reading": transliterate_word(g) if g else "",
        })
    return rows


# ------------------------------------------------------------------ strata

def stratum_a(texts, rng, n):
    """The word-final `ɨ` question — the single most valuable items here.

    Experiment 005 found word-by-word and running-text transliteration disagree
    on 4.53% of word tokens, almost always by one word-final `ɨ`, and **we do
    not know which is correct**. The API ships the word-alone form.
    """
    epi = _epi()
    cands = {}
    for t in texts.values():
        for line in t.splitlines():
            if not line.strip():
                continue
            ws, ctx = line.split(), epi.transliterate(line).split()
            if len(ws) != len(ctx):
                continue
            for w, c in zip(ws, ctx):
                alone = transliterate_word(w)
                if alone != c:
                    cands.setdefault(w, (alone, c))

    picked = rng.sample(sorted(cands), min(n, len(cands)))
    rows, key = [], {}
    for i, w in enumerate(sorted(picked), 1):
        alone, ctx = cands[w]
        # Randomise which form is shown first, and record it out of band.
        flip = rng.random() < 0.5
        opt1, opt2 = (ctx, alone) if flip else (alone, ctx)
        iid = f"A{i:02d}"
        rows.append({"id": iid, "tigrinya": w, "option_1": opt1, "option_2": opt2,
                     "your_answer": "", "comment": ""})
        key[iid] = {"word": w, "word_alone": alone, "in_context": ctx,
                    "option_1_is": "in_context" if flip else "word_alone",
                    "option_2_is": "word_alone" if flip else "in_context",
                    "shipped": "word_alone"}
    return rows, key


def stratum_b(texts, rng, n):
    """Transliteration of the most frequent words — widest blast radius."""
    freq = Counter(w for t in texts.values() for w in t.split())
    common = [w for w, c in freq.most_common() if c >= 3]
    picked = rng.sample(common, min(n, len(common)))
    return [{"id": f"B{i:02d}", "tigrinya": w, "our_reading": transliterate_word(w),
             "your_answer": "", "correction": "", "comment": ""}
            for i, w in enumerate(sorted(picked), 1)], {}


def stratum_c(texts):
    """Orthographic normalisation — is collapsing ፀ→ጸ and አ→ኣ acceptable?

    Every affected form is included; there are few, and the question is about
    acceptability rather than an accuracy rate, so sampling would only lose
    information.
    """
    uniq = sorted({w for t in texts.values() for w in t.split()})
    affected = [w for w in uniq if NORMALISED_CHARS & set(w)]
    return [{"id": f"C{i:02d}", "as_written": w, "we_treat_it_as": normalise(w),
             "same_word": "", "acceptable": "", "comment": ""}
            for i, w in enumerate(affected, 1)], {}


def stratum_e(texts, rng, n, exclude):
    """Unbiased control — the only stratum that estimates an overall rate.

    A, B and C are deliberately selected for difficulty, so none of them can
    answer "how often is the transliteration right?" This one can.
    """
    uniq = sorted({w for t in texts.values() for w in t.split()} - exclude)
    picked = rng.sample(uniq, min(n, len(uniq)))
    return [{"id": f"E{i:02d}", "tigrinya": w, "our_reading": transliterate_word(w),
             "your_answer": "", "correction": "", "comment": ""}
            for i, w in enumerate(sorted(picked), 1)], {}


def stratum_f(texts, rng, n):
    """Variety judgement — A-13's original scope, and DEC-010's premise.

    DEC-010 forbids aggregating scores across varieties. If our evaluation
    anchor turns out to be mixed, that is a live correction rather than a
    precaution.
    """
    sents = [l.strip() for k in SENTENCE_SOURCES
             for l in texts[k].splitlines() if l.strip()]
    picked = rng.sample(sents, min(n, len(sents)))
    return [{"id": f"F{i:02d}", "sentence": s, "variety": "", "natural": "", "comment": ""}
            for i, s in enumerate(picked, 1)], {}


# ------------------------------------------------------------------ output

def write_sheet(name, rows, header_note):
    """One CSV per stratum: each sheet asks exactly one question.

    `utf-8-sig` because the reviewer will most likely open this in Excel, which
    mis-decodes plain UTF-8 and would render Ge'ez as mojibake — an ironic way
    to lose a script-fidelity study.
    """
    SHEETS.mkdir(parents=True, exist_ok=True)
    path = SHEETS / f"{name}.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        f.write(f"# {header_note}\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return path


def main():
    rng = random.Random(SEED)
    texts = load()
    words = {w for t in texts.values() for w in t.split()}

    a_rows, a_key = stratum_a(texts, rng, TARGET["A_vowel"])
    b_rows, _ = stratum_b(texts, rng, TARGET["B_frequent"])
    c_rows, _ = stratum_c(texts)
    used = {r["tigrinya"] for r in a_rows} | {r["tigrinya"] for r in b_rows}
    e_rows, _ = stratum_e(texts, rng, TARGET["E_random"], used)
    f_rows, _ = stratum_f(texts, rng, TARGET["F_variety"])

    sheets = [
        ("1_which_is_right", a_rows,
         "Two readings of the same word. Which matches how you say it? "
         "Answer 1, 2, both, neither, or unsure."),
        ("2_common_words", b_rows,
         "Is our reading of this word correct? Answer yes, no, close, or unsure. "
         "If no or close, please write what it should be."),
        ("3_spelling_variants", c_rows,
         "We treat these two spellings as the same word for searching. "
         "same_word: yes/no/unsure. acceptable: yes/no/unsure."),
        ("4_random_sample", e_rows,
         "Same question as sheet 2, on a random sample. "
         "Answer yes, no, close, or unsure."),
        ("5_which_variety", f_rows,
         "Which variety does this sentence read as? eritrean / ethiopian / "
         "either / unsure. natural: does it read like real Tigrinya? yes/no."),
    ]
    written = [write_sheet(n, r, note) for n, r, note in sheets if r]

    (HERE / "key.json").write_text(
        json.dumps({"_warning": "ANSWER KEY — do not send to the reviewer.",
                    "seed": SEED, "A": a_key}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    key_rows = pronunciation_key(words)
    manifest = {
        "seed": SEED,
        "corpora": {k: str(v.relative_to(REPO)) for k, v in CORPORA.items()},
        "items": {"A_vowel": len(a_rows), "B_frequent": len(b_rows),
                  "C_normalisation": len(c_rows), "D_passthrough": 0,
                  "E_random": len(e_rows), "F_variety": len(f_rows)},
        "total_items": sum(len(r) for _, r, _ in sheets),
        "pronunciation_key": key_rows,
        "notes": {
            "D_passthrough": "EMPTY BY MEASUREMENT, not by omission. Coverage over "
                             "Ethiopic letters is 100% on this corpus, so there are "
                             "no unmapped-letter words to review.",
            "bias_control": "Sheet 1 randomises option order; key.json records which "
                            "form is which and is never sent to the reviewer.",
        },
    }
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 66)
    print("NATIVE-SPEAKER VALIDATION INSTRUMENT")
    print("=" * 66)
    for name, rows, _ in sheets:
        print(f"  sheets/{name}.csv{'':<6} {len(rows):>3} items")
    print(f"  {'TOTAL':<28} {manifest['total_items']:>3} items")
    print(f"\n  pronunciation key: {len(key_rows)} symbols anchored to Ge'ez examples")
    print("  answer key written to key.json — DO NOT SEND TO THE REVIEWER")
    print(f"\n  D (pass-through) is empty: {manifest['notes']['D_passthrough'][:60]}...")


if __name__ == "__main__":
    main()
