#!/usr/bin/env python3
"""Experiment 010 — calibrate the variety markers against source-declared labels.

The variety gate has reported `eritrean_markers` / `ethiopian_markers` since
DEC-010, and no corpus with a **declared** variety existed to check it against.
TICO-19 ships one: 3,071 English segments translated twice, once as `ti-ER` and
once as `ti-ET`, same source text, same domain, same length. That is a
controlled comparison — the only variable is the variety.

Everything here reads committed files only, so it reproduces offline.

    python3 run.py            # print the report, rewrite results.json
    python3 run.py --check    # verify results.json still matches (CI)
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "data_processing"))

from screen_dataset import (TSADE_ER, TSADE_ET, ALEF_GE,  # noqa: E402
                            ALEF_AM, LEXEMES)

#: Markers that occur in the Ethiopian standard and not the Eritrean one.
#: Kept separate from the ER markers deliberately — the whole finding is that
#: pooling them destroys the signal.
ET_LEXEMES = tuple(LEXEMES.values())

#: Pre-committed, before looking at the labelled data.
#:
#: H1 is the one that matters: an instrument whose reported ratio moves less
#: than 10 points between two corpora that differ *only* in declared variety is
#: not measuring variety.
THRESHOLDS = {
    "H1_ratio_separates": 10.0,      # percentage points of ER-share separation
    "H2_precision": 0.99,            # ET-only markers, precision on labelled ER
    "H3_recall": 0.50,               # ET-only markers, per-segment recall on ET
}

LABELLED = {
    "ER": "data/anchors/tico19/{split}.tir_er.txt",
    "ET": "data/anchors/tico19/{split}.tir_et.txt",
    "ti": "data/anchors/tico19/{split}.tir_ti.txt",
}

UNLABELLED = {
    "HornMT": "data/anchors/hornmt/tir.txt",
    "FLORES sample": "experiments/003-metric-validity/data/flores_ti.txt",
    "TLT clean": "experiments/002-tokenizer-fertility/corpus/tlt_000_clean.txt",
    "Haddas": "experiments/002-tokenizer-fertility/corpus/haddas_001_colscrambled.txt",
}


def segments(rel: str) -> list[str]:
    text = (REPO / rel).read_text(encoding="utf-8")
    return [ln for ln in text.split("\n") if ln.strip()]


def has_et_marker(seg: str) -> bool:
    """The discriminative test: an Ethiopian-only orthographic marker."""
    return (any(c in seg for c in TSADE_ET)
            or any(lex in seg for lex in ET_LEXEMES))


def marker_counts(segs: list[str]) -> dict[str, int]:
    text = "\n".join(segs)
    return {
        "tsade_er": sum(text.count(c) for c in TSADE_ER),
        "tsade_et": sum(text.count(c) for c in TSADE_ET),
        "alef_er": text.count(ALEF_GE),
        "alef_et": text.count(ALEF_AM),
        "lex_er": sum(text.count(a) for a in LEXEMES),
        "lex_et": sum(text.count(b) for b in ET_LEXEMES),
    }


def er_share(counts: dict[str, int]) -> float:
    """What the variety gate reports today: pooled ER markers over all markers."""
    er = counts["tsade_er"] + counts["alef_er"] + counts["lex_er"]
    et = counts["tsade_et"] + counts["alef_et"] + counts["lex_et"]
    return 100 * er / (er + et) if er + et else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="compare against the committed results.json and fail on drift")
    args = ap.parse_args()

    out: dict = {"thresholds": THRESHOLDS, "labelled": {}, "unlabelled": {},
                 "findings": {}}

    # --- the controlled comparison ------------------------------------------
    tp = fp = n_et = n_er = 0
    for split in ("dev", "test"):
        for label, tmpl in LABELLED.items():
            segs = segments(tmpl.format(split=split))
            counts = marker_counts(segs)
            fired = sum(1 for s in segs if has_et_marker(s))
            out["labelled"][f"{split}.{label}"] = {
                "segments": len(segs),
                "marker_counts": counts,
                "pooled_er_share_pct": round(er_share(counts), 1),
                "segments_with_et_marker": fired,
                "et_marker_rate_pct": round(100 * fired / len(segs), 1),
            }
            if label == "ET":
                tp += fired
                n_et += len(segs)
            elif label == "ER":
                fp += fired
                n_er += len(segs)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / n_et if n_et else 0.0

    # H1 — does the pooled ratio the gate reports separate the two?
    seps = [abs(out["labelled"][f"{s}.ER"]["pooled_er_share_pct"]
                - out["labelled"][f"{s}.ET"]["pooled_er_share_pct"])
            for s in ("dev", "test")]
    worst_sep = min(seps)

    out["findings"] = {
        "H1_pooled_ratio_separates_varieties": {
            "threshold_points": THRESHOLDS["H1_ratio_separates"],
            "separation_points": [round(s, 1) for s in seps],
            "worst": round(worst_sep, 1),
            "verdict": "CONFIRMED" if worst_sep >= THRESHOLDS["H1_ratio_separates"]
                       else "REFUTED",
        },
        "H2_et_markers_are_precise": {
            "threshold": THRESHOLDS["H2_precision"],
            "false_positives": fp,
            "labelled_eritrean_segments": n_er,
            "precision": round(precision, 4),
            "verdict": "CONFIRMED" if precision >= THRESHOLDS["H2_precision"]
                       else "REFUTED",
        },
        "H3_et_markers_have_recall": {
            "threshold": THRESHOLDS["H3_recall"],
            "true_positives": tp,
            "labelled_ethiopian_segments": n_et,
            "recall": round(recall, 4),
            "verdict": "CONFIRMED" if recall >= THRESHOLDS["H3_recall"]
                       else "REFUTED",
        },
    }

    # --- what the calibrated rule says about corpora with no label ----------
    for name, rel in UNLABELLED.items():
        segs = segments(rel)
        fired = sum(1 for s in segs if has_et_marker(s))
        counts = marker_counts(segs)
        out["unlabelled"][name] = {
            "segments": len(segs),
            "segments_with_et_marker": fired,
            "et_marker_rate_pct": round(100 * fired / len(segs), 1),
            "pooled_er_share_pct": round(er_share(counts), 1),
        }

    results = HERE / "results.json"
    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not results.is_file():
            print("::error::results.json is missing")
            return 2
        if results.read_text(encoding="utf-8") != rendered:
            print("::error::results.json does not match a fresh run — the "
                  "committed corpora or the marker set changed under it")
            return 1
        print("results.json reproduces exactly")
        return 0

    results.write_text(rendered, encoding="utf-8")

    print(f"{'corpus':26}{'segs':>7}{'ET-marked':>11}{'rate':>8}{'pooled ER%':>12}")
    for split in ("dev", "test"):
        for label in LABELLED:
            k = f"{split}.{label}"
            r = out["labelled"][k]
            print(f"{k:26}{r['segments']:>7,}{r['segments_with_et_marker']:>11,}"
                  f"{r['et_marker_rate_pct']:>7.1f}%{r['pooled_er_share_pct']:>11.1f}%")
    for name, r in out["unlabelled"].items():
        print(f"{name:26}{r['segments']:>7,}{r['segments_with_et_marker']:>11,}"
              f"{r['et_marker_rate_pct']:>7.1f}%{r['pooled_er_share_pct']:>11.1f}%")

    print()
    for name, f in out["findings"].items():
        print(f"  {f['verdict']:9} {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
