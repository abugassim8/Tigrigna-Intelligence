#!/usr/bin/env python3
"""
Screen a Tigrinya dataset against the DEC-008 gates before it enters use.

DEC-008 requires contamination screening and licence quarantine; Experiment 002
added quality and DEC-010 added variety. This script makes those four gates
executable instead of prose, and emits a machine-readable screening record.

    python3 screen_dataset.py CORPUS... --licence mit [--eval-set FILE]...

Exit status is 0 when every gate passes and 1 when any gate fails, so this can
gate a pipeline step.

What this script does NOT do: decide anything a human must decide. Licence is
asserted, never detected. Variety and scramble findings are reported as signals
for review, not verdicts — see `report()`.
"""

import argparse
import json
import pathlib
import sys
import unicodedata
from collections import Counter

# --------------------------------------------------------------------- script

ETHIOPIC_RANGES = [
    (0x1200, 0x137F),  # Ethiopic
    (0x1380, 0x139F),  # Ethiopic Supplement
    (0x2D80, 0x2DDF),  # Ethiopic Extended
    (0xAB00, 0xAB2F),  # Ethiopic Extended-A
]
PUNCT = set("።፡፣፤፥፦፧፨፠-–—''\"\"()[]{}/\\.,;:!?'\"«»%“”‘’፥")

# Orthographic variety markers. Eritrean standard prefers the ጸ-series and the
# Ge'ez alef ኣ; Ethiopian/Tigray usage commonly prefers the ፀ-series and አ.
TSADE_ER, TSADE_ET = "ጸጹጺጻጼጽጾ", "ፀፁፂፃፄፅፆ"
ALEF_GE, ALEF_AM = "ኣ", "አ"
# Diagnostic lexemes, Eritrean form -> Ethiopian form.
LEXEMES = {"ክሳብ": "እስካብ", "ሃገራዊ": "ብሄራዊ"}

# Licences we consider usable for shipped artefacts (A-009, P-9). Non-commercial
# and unstated licences fail the gate; see DEC-011 for the model-side rule.
USABLE_LICENCES = {
    "mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause",
    "cc0-1.0", "cc-by-4.0", "cc-by-sa-4.0",
}


def is_ethiopic(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in ETHIOPIC_RANGES)


def load(paths):
    texts = {}
    for p in paths:
        path = pathlib.Path(p)
        if path.is_dir():
            for f in sorted(path.glob("*.txt")):
                texts[str(f)] = f.read_text(encoding="utf-8")
        else:
            texts[str(path)] = path.read_text(encoding="utf-8")
    return texts


def words(text):
    out = []
    for raw in text.split():
        w = "".join(c for c in raw if c not in PUNCT)
        if w:
            out.append(w)
    return out


# ---------------------------------------------------------------------- gates

def gate_licence(licence):
    """Gate 1 — asserted, never detected. An unstated licence fails (A-009)."""
    lic = (licence or "").strip().lower()
    ok = lic in USABLE_LICENCES
    return {
        "gate": "licence",
        "pass": ok,
        "declared": licence or None,
        "detail": ("usable for shipped artefacts" if ok else
                   "NOT usable — unstated, non-commercial, or unrecognised. "
                   "Quarantine to research-only use (DEC-008)"),
    }


def gate_quality(texts):
    """Gate 2 — encoding corruption and extraction damage.

    Foreign-character rate is a verdict; the scramble signal is a flag for
    human review, because distinguishing scrambled columns from unusual prose
    is not reliably automatable and a false verdict would be worse than none.
    """
    per_file, worst = {}, 0.0
    scramble_flags = []
    for name, text in texts.items():
        chars = [c for c in text if not c.isspace()]
        if not chars:
            continue
        foreign = [c for c in chars
                   if not is_ethiopic(c) and not c.isdigit() and c not in PUNCT]
        rate = 100 * len(foreign) / len(chars)
        worst = max(worst, rate)

        # Digit-bearing tokens wedged mid-prose are characteristic of PDF
        # multi-column extraction pulling mastheads into body text.
        ws = words(text)
        digity = sum(1 for w in ws if any(c.isdigit() for c in w)
                     and any(is_ethiopic(c) for c in w))
        digit_rate = 100 * digity / max(len(ws), 1)
        if digit_rate > 1.0:
            scramble_flags.append(f"{name}: {digit_rate:.1f}% mixed digit/Ge'ez tokens")

        per_file[name] = {
            "chars": len(chars),
            "ethiopic_pct": round(100 * sum(1 for c in chars if is_ethiopic(c)) / len(chars), 2),
            "foreign_pct": round(rate, 2),
            "foreign_sample": [f"{c}({unicodedata.name(c, '?')[:20]})"
                               for c, _ in Counter(foreign).most_common(5)],
        }

    ok = worst < 0.1  # anything above this carried real mojibake in practice
    return {
        "gate": "quality",
        "pass": ok,
        "worst_foreign_pct": round(worst, 3),
        "threshold_pct": 0.1,
        "per_file": per_file,
        "review_flags": scramble_flags,
        "detail": ("no encoding corruption detected" if ok else
                   "foreign characters inside Ge'ez text — likely mojibake"),
    }


def gate_variety(texts):
    """Gate 3 — orthographic variety signal (DEC-010).

    Never returns a verdict on variety. It reports the evidence and labels
    the set `unknown` unless the signal is unambiguous, because attributing a
    variety needs a native speaker (ACTIONS.md A-13).
    """
    text = "\n".join(texts.values())
    er = sum(text.count(c) for c in TSADE_ER) + text.count(ALEF_GE)
    et = sum(text.count(c) for c in TSADE_ET) + text.count(ALEF_AM)
    lex = {}
    for er_form, et_form in LEXEMES.items():
        a, b = text.count(er_form), text.count(et_form)
        if a or b:
            lex[f"{er_form}(ER) vs {et_form}(ET)"] = [a, b]

    mixed = er > 0 and et > 0
    if et == 0 and er > 0:
        signal = "eritrean-leaning"
    elif er == 0 and et > 0:
        signal = "ethiopian-leaning"
    elif mixed:
        signal = "MIXED — both orthographies present in one set"
    else:
        signal = "no signal"

    return {
        "gate": "variety",
        "pass": True,  # never blocks; DEC-010 requires a label, not a rejection
        "label": "unknown",
        "signal": signal,
        "eritrean_markers": er,
        "ethiopian_markers": et,
        "lexeme_counts": lex,
        "detail": "SIGNAL ONLY — variety attribution requires a native speaker (A-13). "
                  "Label stays `unknown` until confirmed (DEC-010).",
    }


def gate_contamination(texts, eval_paths, n=8):
    """Gate 4 — n-gram overlap against evaluation sets (DEC-008).

    Word 8-grams are long enough that incidental collision is implausible, so a
    hit is evidence of shared provenance rather than shared topic.
    """
    if not eval_paths:
        return {
            "gate": "contamination",
            "pass": False,
            "detail": "NOT CHECKED — no evaluation set supplied. DEC-008 requires "
                      "this check before training use; supply --eval-set.",
            "overlaps": 0,
        }

    def ngrams(t):
        ws = words(t)
        return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}

    corpus_ng = set()
    for t in texts.values():
        corpus_ng |= ngrams(t)

    hits, per_eval = 0, {}
    for name, t in load(eval_paths).items():
        shared = corpus_ng & ngrams(t)
        per_eval[name] = len(shared)
        hits += len(shared)

    return {
        "gate": "contamination",
        "pass": hits == 0,
        "ngram_size": n,
        "overlaps": hits,
        "per_eval_set": per_eval,
        "detail": ("no shared n-grams with the supplied evaluation sets"
                   if hits == 0 else
                   f"{hits} shared {n}-grams — CONTAMINATED, do not train on this"),
    }


# --------------------------------------------------------------------- report

def report(record):
    print("=" * 70)
    print(f"DEC-008 SCREENING — {record['corpus_files']} file(s), "
          f"{record['total_chars']:,} chars")
    print("=" * 70)
    for g in record["gates"]:
        mark = "PASS" if g["pass"] else "FAIL"
        print(f"\n  [{mark}] {g['gate'].upper()}")
        print(f"        {g['detail']}")
        for k in ("declared", "worst_foreign_pct", "signal",
                  "eritrean_markers", "ethiopian_markers", "overlaps"):
            if k in g:
                print(f"        {k}: {g[k]}")
        for flag in g.get("review_flags", []):
            print(f"        ⚠ review: {flag}")
    print("\n" + "=" * 70)
    print(f"VERDICT: {record['verdict']}")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser(description="Screen a dataset against the DEC-008 gates.")
    ap.add_argument("corpus", nargs="+", help="text file(s) or directory of .txt")
    ap.add_argument("--licence", default=None, help="declared licence, e.g. mit")
    ap.add_argument("--eval-set", action="append", default=[],
                    help="evaluation file to check contamination against (repeatable)")
    ap.add_argument("--json", help="write the screening record here")
    args = ap.parse_args()

    texts = load(args.corpus)
    if not texts:
        sys.exit("No corpus files found.")

    gates = [
        gate_licence(args.licence),
        gate_quality(texts),
        gate_variety(texts),
        gate_contamination(texts, args.eval_set),
    ]
    blocking = [g for g in gates if not g["pass"]]
    record = {
        "corpus": sorted(texts),
        "corpus_files": len(texts),
        "total_chars": sum(len(t) for t in texts.values()),
        "gates": gates,
        "verdict": ("CLEARED for use" if not blocking else
                    "BLOCKED — " + ", ".join(g["gate"] for g in blocking)),
    }
    report(record)
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(record, ensure_ascii=False, indent=2))
        print(f"\nWrote {args.json}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
