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
    (0x1200, 0x137F),   # Ethiopic
    (0x1380, 0x139F),   # Ethiopic Supplement
    (0x2D80, 0x2DDF),   # Ethiopic Extended
    (0xAB00, 0xAB2F),   # Ethiopic Extended-A
    # Extended-B was MISSING here until 2026-08-19, while the two other
    # definitions in the repo included it. Consequence, measured: a corpus of
    # real Tigrinya carrying 21 Extended-B characters failed the quality gate
    # at 1.444% "foreign" — legitimate Ge'ez rejected as mojibake. It is also
    # the one block above the BMP, which DEC-022 singles out as the offset trap.
    (0x1E7E0, 0x1E7FF),  # Ethiopic Extended-B
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


def is_mojibake(ch):
    """True for characters that indicate a decoding failure, not Tigrinya.

    Basic ASCII Latin is deliberately NOT here. Real Tigrinya carries Latin
    proper nouns and acronyms, and treating them as corruption made our own
    FLORES+ evaluation anchor fail this gate at 0.629% — the "foreign"
    characters were C, Q, V, P in proper nouns.

    What is left is what genuinely signals misdecoding: the replacement
    character, C1 controls, and Latin-1 Supplement / Latin Extended letters,
    which is what UTF-8 read as Latin-1 produces. The known-corrupted sample is
    caught by exactly this — a stray `ñ`.
    """
    cp = ord(ch)
    return (ch == "\ufffd"
            or 0x80 <= cp <= 0x9F                    # C1 controls
            or 0x00C0 <= cp <= 0x024F)               # Latin-1 Supplement, Latin Ext-A/B


def gate_quality(texts):
    """Gate 2 — encoding corruption and extraction damage.

    Two separate tests, because one number could not separate them:

      - **Mojibake signatures** are a hard verdict. Any replacement character,
        C1 control, or Latin-1/Extended letter is a decoding failure.
      - **Foreign-character rate** excludes basic ASCII Latin, which is
        legitimate in Tigrinya (proper nouns, acronyms). Counting it made
        `flores_ti.txt` — one of DEC-005's two evaluation anchors — fail its
        own quality gate.

    The scramble signal stays a flag for human review, because distinguishing
    scrambled columns from unusual prose is not reliably automatable and a false
    verdict would be worse than none.
    """
    per_file, worst = {}, 0.0
    scramble_flags = []
    mojibake_hits = {}
    for name, text in texts.items():
        chars = [c for c in text if not c.isspace()]
        if not chars:
            continue
        foreign = [c for c in chars
                   if not is_ethiopic(c) and not c.isdigit() and c not in PUNCT
                   and not (c.isascii() and c.isalpha())]
        rate = 100 * len(foreign) / len(chars)
        worst = max(worst, rate)
        moji = sorted({c for c in chars if is_mojibake(c)})
        if moji:
            mojibake_hits[name] = [f"{c} (U+{ord(c):04X} {unicodedata.name(c, '?')[:24]})"
                                   for c in moji[:8]]

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

    ok = worst < 0.1 and not mojibake_hits
    if mojibake_hits:
        detail = ("DECODING FAILURE — replacement or Latin-1/Extended characters "
                  "inside Ge'ez text")
    elif not ok:
        detail = "unexpected non-Latin foreign characters inside Ge'ez text"
    else:
        detail = "no encoding corruption detected"
    return {
        "gate": "quality",
        "pass": ok,
        "worst_foreign_pct": round(worst, 3),
        "threshold_pct": 0.1,
        "mojibake": mojibake_hits,
        "per_file": per_file,
        "review_flags": scramble_flags,
        "detail": detail,
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
    """Gate 4 — overlap against evaluation sets (DEC-008).

    **Two tests, because one was not enough.** Word 8-grams are long enough that
    incidental collision is implausible, so a hit is evidence of shared
    provenance rather than shared topic. But an evaluation segment shorter than
    8 words produces **no n-grams at all** and is therefore invisible to that
    test: a corpus that was a byte-identical copy of a 2-line evaluation set
    (4 and 3 words) was reported `[PASS] ... CLEARED for use`.

    That is not hypothetical — **TiQuAD is extractive QA, and questions are
    routinely under 8 words.** So exact whole-segment matching runs alongside,
    and short segments are counted and reported rather than silently skipped.
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

    def segments(t):
        """Normalised non-empty lines, for exact whole-segment matching."""
        return {" ".join(words(line)) for line in t.splitlines() if line.strip()}

    corpus_ng, corpus_seg = set(), set()
    for t in texts.values():
        corpus_ng |= ngrams(t)
        corpus_seg |= segments(t)

    hits, exact, short_unseen, per_eval = 0, 0, 0, {}
    for name, t in load(eval_paths).items():
        shared = corpus_ng & ngrams(t)
        seg = segments(t)
        shared_seg = corpus_seg & seg
        # Segments too short to produce any n-gram are invisible to the n-gram
        # test; exact matching is the only thing that can see them.
        too_short = {s for s in seg if len(s.split()) < n}
        hits += len(shared)
        exact += len(shared_seg)
        short_unseen += len(too_short - corpus_seg)
        per_eval[name] = {"shared_ngrams": len(shared),
                          "exact_segments": len(shared_seg),
                          "segments_below_ngram_size": len(too_short)}

    contaminated = hits > 0 or exact > 0
    detail = "no shared n-grams or exact segments with the supplied evaluation sets"
    if contaminated:
        detail = (f"{hits} shared {n}-grams and {exact} EXACT segment matches — "
                  f"CONTAMINATED, do not train on this")
    elif short_unseen:
        detail = (f"no overlap found, but {short_unseen} evaluation segment(s) are "
                  f"shorter than {n} words and are only covered by exact matching")

    return {
        "gate": "contamination",
        "pass": not contaminated,
        "ngram_size": n,
        "overlaps": hits,
        "exact_segment_matches": exact,
        "eval_segments_below_ngram_size": short_unseen,
        "per_eval_set": per_eval,
        "detail": detail,
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
