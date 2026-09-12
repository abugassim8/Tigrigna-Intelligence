#!/usr/bin/env python3
"""Experiment 011 — what score do two human translators get against each other?

The question this answers before it is asked
--------------------------------------------
When **A-09** lands and the first model is finally scored on these anchors,
someone will read a number like "chrF 30" and have to decide whether it is good.
Nothing in this repository currently says what good looks like. This does: it
measures what two *professional human translators* score against each other,
translating the same English, in the same domain.

⚠️ **This is not a ceiling.** chrF between two translations and chrF between a
system and a reference are different quantities — the first has no privileged
"correct" side. A model can legitimately exceed it. The number is a *reference
point* for reading scores, and a write-up that calls it a ceiling is wrong.

Why only TICO-19, and only one pair
-----------------------------------
Inter-translator agreement needs two independent translations of the same
source. **`data/anchors/hornmt/` has one Tigrinya reference**, so it cannot
contribute at all — an earlier draft of the handoff said otherwise and was
wrong.

TICO-19 ships three Tigrinya references, but `tir_ti` and `tir_et` are **one
translation lineage** (chrF 83.65 between them), so the only genuinely
independent pair in the project is **`tir_er` vs `tir_et`**.

⚠️ That pair varies in *two* ways at once — different translators **and**
different standards (Eritrean vs Ethiopian). This experiment cannot separate
them, and does not try. **A-13** is what would.

What was already seen, and what is being predicted
--------------------------------------------------
The `test`-split numbers were observed during planning, so under **DEC-016**
they are recorded as **MEAS** and are *not* hypotheses met. The pre-registered
predictions are all on quantities nobody has looked at: the **dev** split, and
the **per-segment distribution** on both.

**H3 is the one worth running.** A corpus chrF of ~25 could be every segment
scoring 25, or half scoring 5 and half scoring 45. Those mean completely
different things when reading a model score, and nobody has looked.

Reproducibility
---------------
Reads committed files only. sacrebleu's bootstrap is **seeded** — verified
identical across separate processes, 2026-09-12 — which is why confidence
intervals can appear in a DEC-016 artefact at all.

    python3 run.py            # print the report, rewrite results.json
    python3 run.py --check    # verify results.json still matches (CI)
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "services" / "evaluation" / "src"))
sys.path.insert(0, str(REPO / "services" / "primitives" / "src"))

from sacrebleu.metrics import CHRF                        # noqa: E402
from tigrinya_eval.metrics import score                   # noqa: E402
from tigrinya_primitives import normalise                 # noqa: E402

#: Pre-committed, before looking at the dev split or any per-segment number.
#:
#: H1 says agreement is a property of the translator pair, not of the split.
#: H2 says the single-lineage relationship holds on dev as it did on test.
#: H3 says the corpus mean hides a skewed distribution — the interesting one.
THRESHOLDS = {
    "H1_dev_er_et_within_of_test": 3.0,
    "H2_dev_ti_et_above": 75.0,
    "H3_median_below_mean": True,
}

#: Observed on `test` during planning, so recorded and never presented as a
#: prediction (DEC-016).
ALREADY_SEEN_ON_TEST = {"er_vs_et": 24.58, "ti_vs_et": 83.65, "ti_vs_er": 23.95}

REFS = ("tir_er", "tir_et", "tir_ti")
#: hypothesis, reference. chrF is F-score based and beta-weighted, so it is
#: NOT symmetric; the direction is fixed here and stated in the artefact.
PAIRS = (("er_vs_et", "tir_er", "tir_et"),
         ("ti_vs_et", "tir_ti", "tir_et"),
         ("ti_vs_er", "tir_ti", "tir_er"))


def segments(split: str, ref: str) -> list[str]:
    path = REPO / "data" / "anchors" / "tico19" / f"{split}.{ref}.txt"
    return [ln for ln in path.read_text(encoding="utf-8").split("\n") if ln.strip()]


def per_segment(hyp: list[str], ref: list[str]) -> dict:
    """chrF segment by segment — the shape the corpus figure hides."""
    m = CHRF()
    scores = sorted(m.sentence_score(h, [r]).score for h, r in zip(hyp, ref))
    n = len(scores)
    return {
        "segments": n,
        "mean": round(statistics.fmean(scores), 2),
        "median": round(statistics.median(scores), 2),
        "p10": round(scores[int(0.10 * n)], 2),
        "p25": round(scores[int(0.25 * n)], 2),
        "p75": round(scores[int(0.75 * n)], 2),
        "p90": round(scores[int(0.90 * n)], 2),
        "below_10": sum(1 for s in scores if s < 10),
        "above_50": sum(1 for s in scores if s > 50),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify results.json reproduces, do not rewrite it")
    args = ap.parse_args(argv)

    out: dict = {
        "experiment": "011-inter-translator-agreement",
        "caveat": (
            "chrF between two human translations is NOT a ceiling for a "
            "system-vs-reference score: they are different quantities and the "
            "first has no privileged correct side. This is a reference point "
            "for reading model scores, nothing more. The only independent pair "
            "is tir_er vs tir_et, which varies by translator AND by standard "
            "at once; this cannot separate them and A-13 is what would."
        ),
        "direction": "chrF(hypothesis=first, reference=second); chrF is not symmetric",
        "already_seen_on_test": ALREADY_SEEN_ON_TEST,
        "thresholds": THRESHOLDS,
        "corpus": {},
        "per_segment": {},
        "findings": {},
    }

    for split in ("dev", "test"):
        loaded = {r: segments(split, r) for r in REFS}
        for name, a, b in PAIRS:
            hyp, ref = loaded[a], loaded[b]
            s = score(hyp, ref)
            nrm = score([normalise(x) for x in hyp], [normalise(x) for x in ref])
            out["corpus"][f"{split}.{name}"] = {
                "chrf": round(s.chrf.score, 2),
                "ci_low": round(s.chrf.ci_low, 2) if s.chrf.ci_low else None,
                "ci_high": round(s.chrf.ci_high, 2) if s.chrf.ci_high else None,
                "chrf_normalised": round(nrm.chrf.score, 2),
                "normalisation_delta": round(nrm.chrf.score - s.chrf.score, 2),
                "segments": len(hyp),
            }
        out["per_segment"][f"{split}.er_vs_et"] = per_segment(
            loaded["tir_er"], loaded["tir_et"])

    # ---- H1: dev agreement matches test, so it is the pair not the split ----
    dev_er_et = out["corpus"]["dev.er_vs_et"]["chrf"]
    delta = abs(dev_er_et - ALREADY_SEEN_ON_TEST["er_vs_et"])
    out["findings"]["H1_agreement_is_a_property_of_the_pair"] = {
        "dev_chrf": dev_er_et,
        "test_chrf_already_seen": ALREADY_SEEN_ON_TEST["er_vs_et"],
        "absolute_difference": round(delta, 2),
        "threshold": THRESHOLDS["H1_dev_er_et_within_of_test"],
        "verdict": "CONFIRMED" if delta <= THRESHOLDS[
            "H1_dev_er_et_within_of_test"] else "REFUTED",
    }

    # ---- H2: the single-lineage relationship holds on dev too --------------
    dev_ti_et = out["corpus"]["dev.ti_vs_et"]["chrf"]
    out["findings"]["H2_ti_and_et_are_one_lineage_on_dev"] = {
        "dev_chrf": dev_ti_et,
        "threshold": THRESHOLDS["H2_dev_ti_et_above"],
        "verdict": "CONFIRMED" if dev_ti_et > THRESHOLDS[
            "H2_dev_ti_et_above"] else "REFUTED",
    }

    # ---- H3: the corpus mean hides a skewed distribution -------------------
    skewed = {sp: out["per_segment"][f"{sp}.er_vs_et"]["median"]
                  < out["per_segment"][f"{sp}.er_vs_et"]["mean"]
              for sp in ("dev", "test")}
    out["findings"]["H3_per_segment_is_right_skewed"] = {
        "dev": out["per_segment"]["dev.er_vs_et"],
        "test": out["per_segment"]["test.er_vs_et"],
        "median_below_mean": skewed,
        "verdict": "CONFIRMED" if all(skewed.values()) else "REFUTED",
    }

    results = HERE / "results.json"
    rendered = json.dumps(out, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not results.is_file():
            print("::error::results.json is missing")
            return 2
        if results.read_text(encoding="utf-8") != rendered:
            print("::error::results.json does not match a fresh run — the "
                  "committed anchors or sacrebleu changed under it")
            return 1
        print("results.json reproduces exactly")
        return 0

    results.write_text(rendered, encoding="utf-8")

    print(f"{'pair':22}{'chrF':>8}{'95% CI':>18}{'normalised':>13}{'Δ':>7}")
    for k, r in out["corpus"].items():
        ci = (f"[{r['ci_low']:.2f}, {r['ci_high']:.2f}]"
              if r["ci_low"] is not None else "—")
        print(f"{k:22}{r['chrf']:>8.2f}{ci:>18}{r['chrf_normalised']:>13.2f}"
              f"{r['normalisation_delta']:>7.2f}")

    print(f"\n{'per-segment (er_vs_et)':22}{'mean':>8}{'median':>8}{'p10':>7}"
          f"{'p90':>7}{'<10':>7}{'>50':>7}")
    for sp in ("dev", "test"):
        d = out["per_segment"][f"{sp}.er_vs_et"]
        print(f"{sp:22}{d['mean']:>8.2f}{d['median']:>8.2f}{d['p10']:>7.2f}"
              f"{d['p90']:>7.2f}{d['below_10']:>7,}{d['above_50']:>7,}")

    print()
    for name, f in out["findings"].items():
        print(f"  {f['verdict']:9} {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
