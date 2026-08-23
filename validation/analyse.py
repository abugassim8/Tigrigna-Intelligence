#!/usr/bin/env python3
"""
Score returned validation sheets (READINESS_PLAN 1.3–1.5).

Turns a reviewer's answers into numbers that can go in `metrics.md` and settle
DEC-025. Run it against a directory of filled-in sheets:

    python3 validation/analyse.py returned/reviewer-01/

What it will and will not conclude
----------------------------------
**Accuracy comes only from sheet 4.** Sheets 1–3 deliberately select hard cases,
so an accuracy rate computed over them would describe our sampling rather than
the transliterator. Reporting a headline number from the difficult sheets is the
easiest way to produce a confidently wrong figure, so it is refused here rather
than left to discipline.

**`unsure` is never counted as agreement.** It is reported as its own outcome.
A reviewer who declines to guess is giving information, and folding that into
either "correct" or "incorrect" throws it away.

**One reviewer is not a consensus.** With a single respondent every figure here
is one person's judgement — real evidence, and not a measurement of the
language. The output says so rather than assuming the reader remembers.
"""

from __future__ import annotations

import csv
import json
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).parent

#: Accepted answers per sheet. Anything else is reported as unparsed rather than
#: silently dropped — a reviewer writing "probably" is data, not noise.
VOCAB = {
    "1_which_is_right": {"1", "2", "both", "neither", "unsure"},
    "2_common_words": {"yes", "no", "close", "unsure"},
    "3_spelling_variants": {"yes", "no", "unsure"},
    "4_random_sample": {"yes", "no", "close", "unsure"},
    "5_which_variety": {"eritrean", "ethiopian", "either", "unsure"},
}


def read_sheet(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        lines = [l for l in f if not l.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def norm(v: str) -> str:
    return (v or "").strip().lower()


def _tally(rows, field, vocab):
    counts, unparsed = Counter(), []
    for r in rows:
        v = norm(r.get(field, ""))
        if not v:
            counts["(blank)"] += 1
        elif v in vocab:
            counts[v] += 1
        else:
            counts["(unparsed)"] += 1
            unparsed.append((r.get("id", "?"), v))
    return counts, unparsed


def analyse(folder: pathlib.Path) -> dict:
    key = json.loads((HERE / "key.json").read_text(encoding="utf-8"))["A"]
    out: dict = {"source": str(folder), "sheets": {}, "caveats": []}

    # ---- Sheet 1: which form is right? Unblinded here, never to the reviewer.
    p = folder / "1_which_is_right.csv"
    if p.exists():
        rows = read_sheet(p)
        counts, unparsed = _tally(rows, "your_answer", VOCAB["1_which_is_right"])
        verdicts = Counter()
        for r in rows:
            v, k = norm(r.get("your_answer", "")), key.get(r.get("id", ""))
            if not k or v not in {"1", "2", "both", "neither"}:
                continue
            if v in {"1", "2"}:
                verdicts[k[f"option_{v}_is"]] += 1
            else:
                verdicts[v] += 1
        decided = verdicts["word_alone"] + verdicts["in_context"]
        out["sheets"]["1_which_is_right"] = {
            "answers": dict(counts),
            "prefers_word_alone_SHIPPED": verdicts["word_alone"],
            "prefers_in_context": verdicts["in_context"],
            "both_acceptable": verdicts["both"],
            "neither": verdicts["neither"],
            "decided": decided,
            "shipped_form_preferred_pct": (
                round(100 * verdicts["word_alone"] / decided, 1) if decided else None),
            "unparsed": unparsed,
        }

    # ---- Sheets 2 and 4: is our reading correct?
    for name in ("2_common_words", "4_random_sample"):
        p = folder / f"{name}.csv"
        if not p.exists():
            continue
        rows = read_sheet(p)
        counts, unparsed = _tally(rows, "your_answer", VOCAB[name])
        judged = counts["yes"] + counts["no"] + counts["close"]
        res = {"answers": dict(counts), "judged": judged,
               "corrections": [(r.get("id"), r.get("tigrinya"), r.get("our_reading"),
                                r.get("correction"))
                               for r in rows if norm(r.get("correction", ""))],
               "unparsed": unparsed}
        if judged:
            res["correct_pct"] = round(100 * counts["yes"] / judged, 1)
            res["correct_or_close_pct"] = round(
                100 * (counts["yes"] + counts["close"]) / judged, 1)
        # Only the random sheet estimates a rate that describes the system.
        res["is_accuracy_estimate"] = (name == "4_random_sample")
        if name == "2_common_words":
            res["note"] = ("Frequency-weighted and deliberately not random — this "
                           "is impact, NOT an accuracy estimate. Use sheet 4 for that.")
        out["sheets"][name] = res

    # ---- Sheet 3: is normalisation acceptable?
    p = folder / "3_spelling_variants.csv"
    if p.exists():
        rows = read_sheet(p)
        same, unp_s = _tally(rows, "same_word", VOCAB["3_spelling_variants"])
        acc, unp_a = _tally(rows, "acceptable", VOCAB["3_spelling_variants"])
        out["sheets"]["3_spelling_variants"] = {
            "same_word": dict(same), "acceptable": dict(acc),
            "unparsed": unp_s + unp_a,
            "note": ("Any `no` on `acceptable` is a finding, not noise: DEC-007 "
                     "records normalisation as a matching aid, never a correction."),
        }

    # ---- Sheet 5: variety of the evaluation material.
    p = folder / "5_which_variety.csv"
    if p.exists():
        rows = read_sheet(p)
        counts, unparsed = _tally(rows, "variety", VOCAB["5_which_variety"])
        nat, _ = _tally(rows, "natural", {"yes", "no", "unsure"})
        labelled = counts["eritrean"] + counts["ethiopian"]
        out["sheets"]["5_which_variety"] = {
            "variety": dict(counts), "natural": dict(nat),
            "mixed": labelled > 0 and counts["eritrean"] > 0 and counts["ethiopian"] > 0,
            "unparsed": unparsed,
            "note": ("If both varieties appear, DEC-010 stops being a precaution "
                     "and becomes a live correction to our evaluation set."),
        }

    if not out["sheets"]:
        raise SystemExit(f"no recognised sheets found in {folder}")

    out["caveats"] = [
        "ONE REVIEWER IS NOT A CONSENSUS. Every figure here is one person's "
        "judgement — real evidence, not a measurement of the language.",
        "Accuracy comes from sheet 4 only. Sheets 1-3 select hard cases on "
        "purpose, so a rate over them describes our sampling.",
        "`unsure` is reported separately and never counted as agreement.",
    ]
    return out


def report(d: dict) -> str:
    L = ["=" * 68, "NATIVE-SPEAKER VALIDATION — RESULTS", "=" * 68,
         f"  source: {d['source']}", ""]
    s = d["sheets"]

    if "1_which_is_right" in s:
        r = s["1_which_is_right"]
        L += ["  SHEET 1 — the word-final ɨ question",
              f"    prefers word-alone (what we ship) : {r['prefers_word_alone_SHIPPED']}",
              f"    prefers in-context               : {r['prefers_in_context']}",
              f"    both acceptable                  : {r['both_acceptable']}",
              f"    neither                          : {r['neither']}",
              f"    blank/unsure                     : "
              f"{r['answers'].get('(blank)', 0) + r['answers'].get('unsure', 0)}"]
        if r["shipped_form_preferred_pct"] is not None:
            L.append(f"    -> shipped form preferred in {r['shipped_form_preferred_pct']}% "
                     f"of {r['decided']} decided items")
        L.append("")

    for name, label in (("4_random_sample", "SHEET 4 — accuracy (the estimate)"),
                        ("2_common_words", "SHEET 2 — frequent words (impact, not a rate)")):
        if name not in s:
            continue
        r = s[name]
        L.append(f"  {label}")
        for k in ("yes", "close", "no", "unsure", "(blank)", "(unparsed)"):
            if r["answers"].get(k):
                L.append(f"    {k:<12} {r['answers'][k]}")
        if "correct_pct" in r:
            L.append(f"    -> correct {r['correct_pct']}%, correct-or-close "
                     f"{r['correct_or_close_pct']}% of {r['judged']} judged")
        if r.get("note"):
            L.append(f"    NOTE: {r['note']}")
        if r["corrections"]:
            L.append(f"    {len(r['corrections'])} correction(s) supplied:")
            for cid, w, ours, fix in r["corrections"][:8]:
                L.append(f"      {cid} {w!r}: we said {ours!r} -> {fix!r}")
        L.append("")

    if "3_spelling_variants" in s:
        r = s["3_spelling_variants"]
        L += ["  SHEET 3 — normalisation",
              f"    same word?  {dict(r['same_word'])}",
              f"    acceptable? {dict(r['acceptable'])}"]
        if r["acceptable"].get("no"):
            L.append(f"    ⚠ {r['acceptable']['no']} item(s) marked NOT acceptable — "
                     "this contradicts DEC-007's 'matching aid, never a correction'")
        L.append("")

    if "5_which_variety" in s:
        r = s["5_which_variety"]
        L += ["  SHEET 5 — variety", f"    {dict(r['variety'])}",
              f"    reads as natural Tigrinya: {dict(r['natural'])}"]
        if r["mixed"]:
            L.append("    ⚠ BOTH varieties present — DEC-010 becomes a live correction")
        L.append("")

    L += ["  CAVEATS"] + [f"    - {c}" for c in d["caveats"]]
    return "\n".join(L)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip().split("\n\n")[0])
        print("\nusage: python3 validation/analyse.py <folder-of-returned-sheets>")
        return 2
    d = analyse(pathlib.Path(sys.argv[1]))
    print(report(d))
    out = pathlib.Path(sys.argv[1]) / "results.json"
    out.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
