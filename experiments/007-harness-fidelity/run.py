#!/usr/bin/env python3
"""
Experiment 007 — Does our evaluation harness change the number?

`services/evaluation` wraps sacrebleu to enforce DEC-009 and DEC-010. It has
tests, and **nothing else in the repository uses it.** A wrapper nobody consumes
can drift, and its own tests are not independent evidence — this session has
already found five checks that could not fail, one of them a live shipping bug
in this very package (an inverted confidence interval).

So this experiment is the harness's first consumer, and it asks the question a
wrapper has to answer before anyone trusts a score that came through it:
**is the number we report the number sacrebleu computed?**

Hypotheses — pre-committed
--------------------------
**H1 — The harness is transparent.** chrF and BLEU from `tigrinya_eval.score()`
are **exactly** equal to `sacrebleu` called directly on the same input.
*Prediction:* bit-identical across every corruption level. Anything else means
we are reporting a number of our own invention.

**H2 — DEC-009 is unbreakable, not merely documented.** No public path yields
BLEU without chrF. *Prediction:* every scoring entry point returns both.

**H3 — DEC-010 is enforced by exception.** `aggregate()` refuses, rather than
warning. *Prediction:* raises even with a single variety present — the rule is
"no aggregate", not "no mixed aggregate".

**H4 — Confidence intervals widen as the evaluation set shrinks.** DEC-009
requires spread on small sets because a point estimate hides how little is
known. *Prediction:* the median 95% interval widens monotonically as n falls
from 30 to 3, measured over random subsets so that sample **size** is varied
without also varying sample **content**.

Reproduce:
    pip install -e services/primitives -e services/evaluation
    python3 run.py

Deterministic, including sacrebleu's bootstrap. Emits results.json per DEC-016.
"""

import json
import pathlib
import random
import statistics

import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

from tigrinya_eval import (
    CrossVarietyAggregationError, EvalSet, Harness, score,
)

HERE = pathlib.Path(__file__).parent
RESULTS = HERE / "results.json"
REFS_FILE = HERE.parent / "003-metric-validity" / "data" / "flores_ti.txt"

#: Fixed so the perturbation is reproducible.
SEED = 20260819

#: Corruption levels, including 0% — a perfect system is the case where a
#: wrapper bug would be least visible, so it is tested first.
LEVELS = (0.0, 0.1, 0.2, 0.3)


def corrupt(sentences, rate, rng):
    """Replace a fixed fraction of word-final characters with `ን`.

    An inflectional near-miss rather than random noise: it is the error profile
    a real Tigrinya system produces, and the regime where chrF and BLEU diverge.
    """
    out = []
    for s in sentences:
        ws = s.split()
        k = int(len(ws) * rate)
        for i in rng.sample(range(len(ws)), k) if k else []:
            if len(ws[i]) >= 2:
                ws[i] = ws[i][:-1] + "ን"
        out.append(" ".join(ws))
    return out


def main():
    refs = [l.strip() for l in REFS_FILE.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    print("=" * 74)
    print(f"EXPERIMENT 007 — harness fidelity ({len(refs)} reference sentences)")
    print("=" * 74)

    # ------------------------------------------------- H1: transparency
    print("\n" + "=" * 74)
    print("1.  H1 — does the harness change the number?")
    print("=" * 74)
    print(f"  {'corruption':>10} | {'harness chrF':>13} {'raw chrF':>13} | "
          f"{'harness BLEU':>13} {'raw BLEU':>13}")
    print("  " + "-" * 70)

    rows, mismatches = [], 0
    for rate in LEVELS:
        rng = random.Random(SEED)
        hyps = corrupt(refs, rate, rng)
        ours = score(hyps, refs, confidence_interval=False)
        raw_chrf = CHRF().corpus_score(hyps, [refs]).score
        raw_bleu = BLEU().corpus_score(hyps, [refs]).score
        same = (ours.chrf.score == raw_chrf) and (ours.bleu.score == raw_bleu)
        mismatches += 0 if same else 1
        print(f"  {rate:>9.0%} | {ours.chrf.score:>13.6f} {raw_chrf:>13.6f} | "
              f"{ours.bleu.score:>13.6f} {raw_bleu:>13.6f}  {'ok' if same else 'MISMATCH'}")
        rows.append({"corruption": rate,
                     "harness_chrf": ours.chrf.score, "raw_chrf": raw_chrf,
                     "harness_bleu": ours.bleu.score, "raw_bleu": raw_bleu,
                     "identical": same})

    h1 = mismatches == 0
    print(f"\n  H1 {'CONFIRMED' if h1 else 'REFUTED'} — "
          f"{len(LEVELS) - mismatches}/{len(LEVELS)} bit-identical")

    # ------------------------------------------------- H2: BLEU never alone
    print("\n" + "=" * 74)
    print("2.  H2 — can any path produce BLEU without chrF?")
    print("=" * 74)
    s = score(refs[:5], refs[:5], confidence_interval=False)
    both = s.chrf is not None and s.bleu is not None and s.primary is s.chrf
    # The type carries no BLEU-only accessor; enforcement is structural.
    fields = {f for f in dir(s) if not f.startswith("_")}
    # `sacrebleu_version` contains the substring "bleu" and is metadata, not a
    # BLEU accessor. The first version of this check flagged it and reported
    # H2 REFUTED — a false positive in the test, not a defect in the harness.
    bleu_only = {f for f in fields
                 if "bleu" in f.lower()} - {"bleu", "sacrebleu_version"}
    h2 = both and not bleu_only
    print(f"  score() returns both, chrF primary : {both}")
    print(f"  BLEU-only accessors on the result  : {sorted(bleu_only) or 'none'}")
    print(f"\n  H2 {'CONFIRMED' if h2 else 'REFUTED'}")

    # ------------------------------------------------- H3: aggregate refuses
    print("\n" + "=" * 74)
    print("3.  H3 — does aggregate() raise, or merely warn?")
    print("=" * 74)
    outcomes = {}
    for label, variety in (("single variety", "eritrean"), ("unknown", "unknown")):
        h = Harness()
        h.evaluate("sys", corrupt(refs, 0.1, random.Random(SEED)),
                   EvalSet(name="flores+", variety=variety, references=refs))
        try:
            h.aggregate()
            outcomes[label] = "returned a value"
        except CrossVarietyAggregationError:
            outcomes[label] = "raised"
    h3 = all(v == "raised" for v in outcomes.values())
    for k, v in outcomes.items():
        print(f"  {k:<16}: {v}")
    print(f"\n  H3 {'CONFIRMED' if h3 else 'REFUTED'}")

    # ------------------------------------------------- H4: CI width vs n
    print("\n" + "=" * 74)
    print("4.  H4 — do confidence intervals widen as the set shrinks?")
    print("=" * 74)
    # The first version took refs[:n], which varied sentence CONTENT along with
    # sample size and reported H4 refuted on a non-monotonic sequence. That was
    # a confound in the design, not a property of the bootstrap: 10 particular
    # sentences can be more homogeneous than 30. Averaging over random subsets
    # isolates n, which is what the hypothesis was actually about.
    widths, trials = {}, 20
    for n in (30, 20, 10, 5, 3):
        ws = []
        for k in range(1 if n == len(refs) else trials):
            sub = refs if n == len(refs) else random.Random(1000 + k).sample(refs, n)
            sc = score(corrupt(sub, 0.2, random.Random(2000 + k)), sub,
                       confidence_interval=True)
            ws.append(sc.chrf.ci_high - sc.chrf.ci_low)
        widths[n] = statistics.median(ws)
        print(f"  n={n:<3} median 95% CI width {widths[n]:6.2f}   "
              f"({len(ws)} subset{'s' if len(ws) > 1 else ''})")

    monotonic_to_5 = widths[30] < widths[20] < widths[10] < widths[5]
    h4 = monotonic_to_5 and widths[3] > widths[5]
    print(f"\n  H4 {'CONFIRMED' if h4 else 'REFUTED'} — widening holds "
          f"{'from n=30 down to n=5' if monotonic_to_5 else 'nowhere'}, "
          f"and {'continues' if widths[3] > widths[5] else 'BREAKS'} at n=3")
    if not h4 and monotonic_to_5:
        print("\n  ⚠️ The break at n=3 is the finding. Bootstrap resampling of 3")
        print("  items has only 27 distinct multisets, many of them identical, so")
        print("  the interval cannot express the uncertainty it should. **A")
        print("  confidence interval at n=3 understates uncertainty exactly where")
        print("  uncertainty is greatest** — a caveat DEC-009 does not currently")
        print("  carry, and our own evaluation anchor is only 30 sentences.")

    # ------------------------------------------------- report caveats
    h = Harness()
    h.evaluate("nllb-200-3.3B", corrupt(refs, 0.15, random.Random(SEED)),
               EvalSet(name="flores+", variety="unknown", references=refs),
               shippable=False, notes=("CC-BY-NC-4.0 — comparison baseline only",))
    report = h.report()
    caveats = {
        "chrF is primary": "chrF is primary" in report,
        "states the 1.08 BLEU penalty": "1.08" in report,
        "refuses cross-variety aggregation": "NOT aggregated across varieties" in report,
        "marks the NC model unshippable": "COMPARISON ONLY" in report,
    }
    print("\n" + "=" * 74)
    print("5.  Does a report carry its own caveats?")
    print("=" * 74)
    for k, v in caveats.items():
        print(f"  {'yes' if v else 'NO '}  {k}")

    results = {
        "reference_sentences": len(refs),
        "seed": SEED,
        "sacrebleu": sacrebleu.__version__,
        "H1_harness_is_transparent": h1,
        "H1_comparisons": rows,
        "H2_bleu_never_alone": h2,
        "H3_aggregate_raises": h3,
        "H3_outcomes": outcomes,
        "H4_ci_widens_as_n_falls": h4,
        "H4_ci_widths_median": {str(k): round(v, 6) for k, v in widths.items()},
        "H4_subsets_per_n": trials,
        "H4_monotonic_to_n5": monotonic_to_5,
        "report_caveats": caveats,
    }

    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    for k, v in (("H1", h1), ("H2", h2), ("H3", h3), ("H4", h4)):
        print(f"  {k}: {'CONFIRMED' if v else 'REFUTED'}")
    print(f"  report caveats present: {sum(caveats.values())}/{len(caveats)}")
    print("\n  This experiment exists so the harness has a consumer outside its")
    print("  own tests. H1 is the load-bearing one: if it ever fails, every")
    print("  score this project has published came from our arithmetic rather")
    print("  than sacrebleu's.")

    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
