#!/usr/bin/env python3
"""Experiment 009 — is the 1.4M "parallel" corpus parallel?

Analyses `sample/observations.json`, which records what the Hugging Face
Dataset Viewer returned for `michsethowusu/english-tigrinya_sentence-pairs` on
2026-09-02. The corpus itself cannot be downloaded here (**A-09**), so the
sample was recorded by hand; **this script reads only the committed file**, so
the analysis reproduces byte-identically even though the fetch does not.

Four pre-committed hypotheses, thresholds fixed before the numbers were looked
at. See README.md.

Run:  python3 run.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OBS = json.loads((HERE / "sample" / "observations.json").read_text(encoding="utf-8"))

#: H1 — if more than this share of rows carry no English side, calling the
#: corpus "1.4M parallel sentences" materially overstates it.
H1_THRESHOLD = 0.25

#: H3 — a candidate counts as evidence of desync only if the lagged English
#: shares at least this many anchors with the Tigrinya while the same-row
#: English shares strictly fewer.
H3_MIN_ANCHORS = 2

# --------------------------------------------------------------- transliteration

def _skeleton(text: str) -> str:
    """Reduce a string to a rough consonant skeleton for cross-script matching.

    Deliberately crude. It exists to answer one question — does this English
    proper noun appear, transliterated, in this Tigrinya sentence — without
    needing to read Tigrinya. Over-matching would be a problem if it were used
    to *confirm* alignment; it is used to compare two candidates against the
    same Tigrinya string, so a shared bias cancels.
    """
    text = text.lower()
    # IPA affricates and ejectives our transliterator emits, to plain letters.
    for src, dst in (("d͡ʒ", "j"), ("t͡s", "ts"), ("t͡ʃ", "ch"),
                     ("ʼ", ""), ("ʔ", ""), ("ʕ", ""), ("ħ", "h"), ("ʃ", "sh")):
        text = text.replace(src, dst)
    text = text.replace("c", "k").replace("q", "k").replace("x", "ks")
    # Drop vowels, Latin and IPA alike.
    return re.sub(r"[aeiouɨəɛɔʊɪ\W_0-9]", "", text)


#: Minimum consonant-skeleton length for a proper-noun match to count.
#:
#: ⚠️ **This replaces a defective rule, and the defect is recorded because it
#: cost a real anchor.** The first version excluded the sentence-initial word,
#: reasoning that a capital there is not evidence of a proper noun. But
#: "Japan and North Korea have never established diplomatic relations" begins
#: with its strongest anchor, and the rule silently discarded it.
#:
#: The principled fix is not to special-case position but to demand a longer
#: skeleton, which is what makes a match informative wherever it sits: "Japan"
#: gives `jpn` and qualifies; "The" gives `th` and does not. Note this *costs*
#: "Korea" (`kr`, 2), so it is not a loosening chosen to rescue the hypothesis
#: — it trades one anchor for another and the verdict below is unchanged.
MIN_SKELETON = 3


def _proper_nouns(english: str) -> list[str]:
    """Capitalised words of 4+ letters, wherever they occur in the sentence."""
    return re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", english)


def _leading_number(text: str) -> str | None:
    m = re.match(r"\s*(\d+)", text)
    return m.group(1) if m else None


def _anchors(english: str, tigrinya_ipa: str, tigrinya: str) -> list[str]:
    """Language-independent signals that `english` translates `tigrinya`."""
    found = []
    skeleton = _skeleton(tigrinya_ipa)
    for noun in _proper_nouns(english):
        stem = _skeleton(noun)
        if len(stem) >= MIN_SKELETON and stem in skeleton:
            found.append(f"proper-noun:{noun}")
    en_num, ti_num = _leading_number(english), _leading_number(tigrinya)
    if en_num is not None and en_num == ti_num:
        found.append(f"leading-number:{en_num}")
    return found


# ------------------------------------------------------------------ hypotheses

def h1_english_column() -> dict:
    """Is the English side present at all?"""
    bracket = OBS["english_present_bracket"]
    lo, hi = bracket["last_present"], bracket["first_absent"]
    boundary = (lo + hi) / 2
    total = OBS["total_rows"]
    missing = (total - boundary) / total
    return {
        "boundary_row": boundary,
        "bracket": [lo, hi],
        "uncertainty_rows": hi - lo,
        "share_without_english": round(missing, 4),
        "rows_without_english": int(total - boundary),
        "threshold": H1_THRESHOLD,
        "confirmed": missing > H1_THRESHOLD,
    }


def h2_sorted_by_similarity() -> dict:
    """Is the corpus ordered, so that any prefix flatters it?"""
    seq = OBS["similarity_by_offset"]
    sims = [r["similarity"] for r in seq]
    monotone = all(a >= b for a, b in zip(sims, sims[1:]))
    return {
        "offsets": [r["offset"] for r in seq],
        "similarities": sims,
        "monotone_non_increasing": monotone,
        "range": [min(sims), max(sims)],
        "confirmed": monotone,
    }


def h3_columns_desynced() -> dict:
    """Do the two columns line up with each other?"""
    from tigrinya_primitives import transliterate

    findings = []
    for c in OBS["desync_candidates"]:
        ipa = transliterate(c["tigrinya"]).analysis
        same = _anchors(c["english_same_row"], ipa, c["tigrinya"])
        lagged = _anchors(c["english_lagged"], ipa, c["tigrinya"])
        findings.append({
            "tigrinya_row": c["tigrinya_row"],
            "english_row": c["english_row"],
            "lag": c["english_row"] - c["tigrinya_row"],
            "anchors_same_row": same,
            "anchors_lagged": lagged,
            "lagged_wins": len(lagged) >= H3_MIN_ANCHORS and len(lagged) > len(same),
        })
    lags = {f["lag"] for f in findings if f["lagged_wins"]}
    return {
        "candidates": findings,
        "min_anchors": H3_MIN_ANCHORS,
        "constant_lag": sorted(lags)[0] if len(lags) == 1 else None,
        "confirmed": bool(findings) and all(f["lagged_wins"] for f in findings),
    }


def h4_duplicate_targets() -> dict:
    """Is one Tigrinya sentence reused for several English sources?"""
    rows = OBS["near_duplicate_targets"]
    normalised = [" ".join(r["tigrinya"].split()) for r in rows]
    english = [r["english"] for r in rows]
    return {
        "rows": [r["row"] for r in rows],
        "tigrinya_identical_after_whitespace_normalisation":
            len(set(normalised)) == 1,
        "tigrinya_identical_verbatim": len({r["tigrinya"] for r in rows}) == 1,
        "english_distinct": len(set(english)) == len(english),
        "confirmed": len(set(normalised)) == 1 and len(set(english)) == len(english),
    }


def main() -> int:
    results = {
        "experiment": "009-mined-corpus-probe",
        "source": OBS["source"],
        "total_rows": OBS["total_rows"],
        "observed": OBS["observed"],
        "deterministic": True,
        "sampling": "hand-recorded from the HF Dataset Viewer; not exhaustive",
        "H1_english_column_missing": h1_english_column(),
        "H2_sorted_by_similarity": h2_sorted_by_similarity(),
        "H3_columns_desynced": h3_columns_desynced(),
        "H4_duplicate_targets": h4_duplicate_targets(),
    }
    (HERE / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for key in ("H1_english_column_missing", "H2_sorted_by_similarity",
                "H3_columns_desynced", "H4_duplicate_targets"):
        verdict = "CONFIRMED" if results[key]["confirmed"] else "REFUTED"
        print(f"{key:34s} {verdict}")
    h1 = results["H1_english_column_missing"]
    print(f"\n  {h1['share_without_english']:.1%} of rows carry no English side "
          f"(~{h1['rows_without_english']:,} of {OBS['total_rows']:,})")
    h3 = results["H3_columns_desynced"]
    if h3["constant_lag"] is not None:
        print(f"  both desync candidates align at a constant lag of "
              f"{h3['constant_lag']} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
