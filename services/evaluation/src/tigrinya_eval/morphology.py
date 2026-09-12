"""Intrinsic evaluation for morphological analysis (DEC-023a, DEC-028).

Why this is a separate module
-----------------------------
Every other Tier 0 primitive is evaluated against a dependency this package
requires. Morphology is not: HornMorpho is **GPL-3.0** and this platform is
Apache-2.0, so it is never bundled (**DEC-028**, **DEC-020 Amendment 1**). It is
present only if the user installed it themselves.

That single fact shapes everything here.

The problem this module is mostly about
---------------------------------------
**A check that cannot run must not report a pass.** Eleven checks in this
repository have been found that could not fail, seven of them in the audit
tooling. The obvious way to write morphology evaluation — "if the analyser is
missing, return early" — manufactures a tenth, and a particularly bad one: the
`metrics.md` morphology row would flip from ❌ to ✅ on a machine where
morphology had never once been executed.

So `PropertyResult` grew two states that are neither pass nor fail:

  - **SKIP** — the analyser is genuinely absent. Does not fail the build,
    because failing over an optional dependency is how a check gets deleted.
    Made loud instead: the verdict line reads ``PASS (with N check(s) NOT
    RUN)``, `report()` prints a NOT MEASURED block, and `require=True` turns it
    into a failure for anyone who has installed the analyser.
  - **MEAS** — a number recorded with no threshold, because **nothing has ever
    measured Tigrinya morphological coverage**. Inventing a floor and calling it
    pre-committed is the overclaiming DEC-016 exists to stop. A floor chosen
    before any measurement is not a prediction; it is a number that cannot fail.

How these are verified without the GPL-3.0 dependency
-----------------------------------------------------
The same way `morphology.analyse` is: **an injected analyser**. Every check here
takes `analyser=`, so a fake one exercises every path, and a deliberately
*broken* one proves each check still fails. `scripts/tests/test_plants.py` plants
five broken analysers — misaligned spans, non-deterministic output, a mangled
surface — and asserts each is caught.

That is the whole point. These checks are **not** unverified code waiting for an
install: their failure modes are tested today. What waited for an install was
the *measurement* — the coverage number, and whether `_render` mapped live
HornMorpho output at all.

✅ **Both settled 2026-09-07**, on the first run with HornMorpho present. Two
things the injected-analyser suite could not have caught, and did not:

  - **`_render` was wrong.** `pos` sat in the same fallback chain as `seg`, so
    a word with both a segmented and an unsegmented reading rendered as
    ``ADP|-<ኣብ>--`` — a POS tag and a segmentation in the same slot. Every
    fixture supplied `seg`, so the branch never ran until real data reached it.
  - **The CLI measured English.** `load_corpus` on a parallel anchor directory
    sweeps in the source language: `data/anchors/tico19` is 6,142 lines of
    English beside 9,213 of Tigrinya. `_main` now filters by script and prints
    what it dropped.

Neither was a wrong *threshold*. Both were the instrument measuring something
other than what it named — which is the failure this repository keeps finding,
and the reason a measurement is not real until it has been run once.

What is checked, and what each is worth
---------------------------------------
| Check | Kind | Catches |
| --- | --- | --- |
| `morphology.surface` | threshold 1.0 | DEC-022's verbatim-surface guarantee broken |
| `morphology.alignment` | threshold 1.0 | spans that do not index back, or do not rebuild the analysis form |
| `morphology.determinism` | threshold 1.0 | an analyser whose output moves between calls |
| `morphology.coverage` | **measurement** | how much of real Tigrinya gets an analysis at all |
| `morphology.normalisation` | **measurement** | ጸ/ፀ collapse changing the morphology |

**They catch *broken*, not *wrong*** — the caveat `primitives.py` carries applies
here with more force, not less. An analyser returning confident nonsense with
correct offsets passes every threshold above. Morphological *accuracy* is the
one Tier 0 property experiment 004 found genuinely needs gold data and a speaker
(**A-006**, **A-13**).
"""

from __future__ import annotations

import pathlib
from typing import Any, Callable, Sequence

from tigrinya_primitives import morphology, normalise

from .primitives import (IntrinsicReport, PropertyResult, is_ethiopic,
                         load_corpus)

Analyser = Callable[[str], Any]

# --------------------------------------------------------------- thresholds
#
# Pre-committed. Two of the five are deliberately absent, and that absence is
# recorded rather than filled in with a plausible number.

#: DEC-022 obliges the API to return the surface form verbatim. Exact by
#: construction — `analyse` copies its input — so anything below 1.0 is a bug,
#: not a regression.
SURFACE_THRESHOLD = 1.0

#: DEC-023 calls word-level alignment "exact by construction"; `analyse` already
#: calls `verify_offsets()`. This checks the claim rather than trusting it,
#: including the rebuild-by-equality that `check_alignment_integrity` documents:
#: containment cannot detect an appended character.
ALIGNMENT_THRESHOLD = 1.0

#: An analyser that moves between calls makes every downstream number unstable.
DETERMINISM_THRESHOLD = 1.0

_SKIP_REASON = (
    "HornMorpho is not installed. It is GPL-3.0 and this package is Apache-2.0, "
    "so it is never bundled (DEC-028). This property is UNVERIFIED — not "
    "verified-true. Install it and re-run to measure:\n"
    "        pip install git+https://github.com/hltdi/HornMorpho\n"
    '        python -c "import hm; hm.download(\'ti\')"'
)

_COVERAGE_NOTE = (
    "LOWER BOUND, and no threshold. An analysis identical to the surface form "
    "is counted as uncovered, which also catches genuinely uninflected words — "
    "so the true rate is at least this. No floor is set because nothing has "
    "ever measured Tigrinya morphological coverage; the first real install "
    "sets one."
)

_NORMALISATION_NOTE = (
    "SIGNAL, not a threshold. Measures how often normalising ጸ/ፀ and ኣ/አ "
    "changes the analysis. Disagreement is not automatically a defect: if a "
    "lexicon holds only one variant, normalisation legitimately *rescues* a "
    "word. Direction matters and only a speaker can rule (A-13)."
)


def _resolve(analyser: Analyser | None) -> tuple[Analyser | None, str]:
    """Return (analyser, skip_reason). A reason means: do not run.

    Deliberately narrow. The only thing that produces a skip is the analyser
    being **absent**, established by `morphology.is_available()`, which checks
    both the import and the language data. An analyser that is present and
    broken must fail, never skip — swallowing an exception into a skip is how a
    check stops being able to fail.
    """
    if analyser is not None:
        return analyser, ""
    if morphology.is_available():
        return None, ""          # None here means "use the real one"
    return None, _SKIP_REASON


def _skip(name: str, reason: str) -> PropertyResult:
    return PropertyResult(name=name, passed=0, total=0, threshold=0.0,
                          skipped=True, skip_reason=reason)


def _analyse(text: str, analyser: Analyser | None):
    return morphology.analyse(text, analyser=analyser)


# -------------------------------------------------------------------- checks

def check_surface(texts: Sequence[str], *,
                  analyser: Analyser | None = None) -> PropertyResult:
    """`analyse(t).surface == t`, byte for byte (DEC-022).

    The cheapest check here and the one whose failure is worst: if the surface
    form is not returned verbatim, every offset a caller computed against its
    own input is silently wrong.
    """
    analyser, reason = _resolve(analyser)
    if reason:
        return _skip("morphology.surface", reason)

    ok, failures = 0, []
    for t in texts:
        try:
            a = _analyse(t, analyser)
        except NotImplementedError:                        # pragma: no cover
            return _skip("morphology.surface", _SKIP_REASON)
        if a.surface == t:
            ok += 1
        elif len(failures) < 8:
            failures.append((t[:40], a.surface[:40]))
    return PropertyResult(
        name="morphology.surface", passed=ok, total=len(texts),
        threshold=SURFACE_THRESHOLD, failures=tuple(failures),
        note="DEC-022 verbatim-surface guarantee",
    )


def check_alignment(texts: Sequence[str], *,
                    analyser: Analyser | None = None) -> PropertyResult:
    """Spans index back into the surface, and rebuild the analysis form exactly.

    Mirrors `primitives.check_alignment_integrity`, including its hard-won rule:
    **equality, never containment.** DEC-023 once recorded 1,639/1,639 (100%)
    from an `in` test that could not detect an appended character, and appended
    characters were 92% of the real failures.
    """
    analyser, reason = _resolve(analyser)
    if reason:
        return _skip("morphology.alignment", reason)

    ok, failures = 0, []
    for t in texts:
        try:
            a = _analyse(t, analyser)
        except NotImplementedError:                        # pragma: no cover
            return _skip("morphology.alignment", _SKIP_REASON)
        except ValueError as e:
            # verify_offsets() raised — a real alignment failure, not a skip.
            if len(failures) < 8:
                failures.append((t[:40], str(e)[:80]))
            continue

        parts, cursor = [], 0
        for s in a.spans:
            parts.append(t[cursor:s.start])      # untouched whitespace
            parts.append(s.analysis)
            cursor = s.end
        parts.append(t[cursor:])
        rebuilt = "".join(parts)

        surface_ok = all(t[s.start:s.end] == s.surface for s in a.spans)
        if rebuilt == a.analysis and surface_ok:
            ok += 1
        elif len(failures) < 8:
            failures.append((t[:40], rebuilt[:60]))
    return PropertyResult(
        name="morphology.alignment", passed=ok, total=len(texts),
        threshold=ALIGNMENT_THRESHOLD, failures=tuple(failures),
        note="exact equality on the rebuilt analysis form, never containment",
    )


def check_determinism(words: Sequence[str], *,
                      analyser: Analyser | None = None) -> PropertyResult:
    """The same word analysed twice gives the same analysis.

    Re-run in **reverse order** rather than back to back. Adjacent repeat calls
    are what a warm cache answers best, and `primitives.check_determinism`
    exists because exactly that made a determinism check unable to fail. Here
    the risk is upstream: HornMorpho memoises internally and we cannot clear it,
    so changing the order is the strongest lever available.
    """
    analyser, reason = _resolve(analyser)
    if reason:
        return _skip("morphology.determinism", reason)

    words = list(words)
    try:
        first = {w: _analyse(w, analyser).analysis for w in words}
        second = {w: _analyse(w, analyser).analysis for w in reversed(words)}
    except NotImplementedError:                            # pragma: no cover
        return _skip("morphology.determinism", _SKIP_REASON)

    ok, failures = 0, []
    for w in words:
        if first[w] == second[w]:
            ok += 1
        elif len(failures) < 8:
            failures.append((w, first[w][:30], second[w][:30]))
    return PropertyResult(
        name="morphology.determinism", passed=ok, total=len(words),
        threshold=DETERMINISM_THRESHOLD, failures=tuple(failures),
        note="second pass runs in reverse order, not back to back",
    )


def check_coverage(texts: Sequence[str], *,
                   analyser: Analyser | None = None) -> PropertyResult:
    """Share of word tokens receiving an analysis distinct from their surface.

    **A lower bound, and reported with no threshold.** `analyse` falls back to
    the surface form when HornMorpho returns nothing renderable, so "analysis
    equals surface" conflates two cases: a word the analyser could not handle,
    and a word that is genuinely uninflected. This measure cannot separate them
    and does not pretend to.

    No floor is set. Nothing has ever measured Tigrinya morphological coverage,
    so any number written here before the first real run would be a guess
    wearing the clothes of a pre-commitment.
    """
    analyser, reason = _resolve(analyser)
    if reason:
        return _skip("morphology.coverage", reason)

    covered = total = 0
    uncovered: list[str] = []
    for t in texts:
        try:
            a = _analyse(t, analyser)
        except NotImplementedError:                        # pragma: no cover
            return _skip("morphology.coverage", _SKIP_REASON)
        for s in a.spans:
            total += 1
            if s.analysis and s.analysis != s.surface:
                covered += 1
            elif len(uncovered) < 8:
                uncovered.append(s.surface)
    return PropertyResult(
        name="morphology.coverage", passed=covered, total=total,
        threshold=0.0, measurement_only=True,
        failures=tuple(uncovered), note=_COVERAGE_NOTE,
    )


def check_normalisation(words: Sequence[str], *,
                        analyser: Analyser | None = None) -> PropertyResult:
    """Does normalising ጸ/ፀ and ኣ/አ change the morphological analysis?

    Reported as a **signal, not a threshold**, and the direction is the
    interesting part. If a lexicon holds only the Eritrean tsade, normalisation
    *rescues* words that would otherwise fail — that is normalisation working.
    If it destroys a distinction the analyser relied on, that is a real cost.
    Only a speaker can say which (**A-13**), so this counts and does not judge.

    Restricted to words normalisation actually changes; counting words it leaves
    alone would inflate agreement toward 100% and measure the corpus.

    ⚠️ **And restricted again, after the first real run.** `analyse` falls back
    to the surface form when nothing is analysable, so a pair where **neither**
    word is analysed disagrees automatically — the two surfaces differ, because
    differing is what normalisation just did to them. On the first live corpus
    that artefact was **31 of 41 apparent disagreements**, and it dragged the
    headline from 76% to 43%. Such a pair says nothing about whether
    normalisation changes morphology; it is a *coverage* fact wearing a
    normalisation number. Those pairs are now excluded from the denominator and
    counted separately.

    The remaining pairs are split four ways, because they mean different things
    and a single ratio hides it:

    | Outcome | Meaning |
    | --- | --- |
    | **same** | Normalisation left the analysis alone. The only one counted as agreement |
    | **rescued** | Only the normalised form analyses — normalisation *working* |
    | **lost** | Only the raw form analyses — normalisation destroying a distinction |
    | **differs** | Both analyse, differently — the case that needs a speaker |
    """
    analyser, reason = _resolve(analyser)
    if reason:
        return _skip("morphology.normalisation", reason)

    pairs = [(w, normalise(w)) for w in words]
    pairs = [(raw, norm) for raw, norm in pairs if raw != norm]
    if not pairs:
        return PropertyResult(
            name="morphology.normalisation", passed=0, total=0,
            threshold=0.0, measurement_only=True,
            note="no word in this corpus changes under normalisation — "
                 "nothing to compare. " + _NORMALISATION_NOTE,
        )

    same = rescued = lost = differs = neither = 0
    reportable: list[tuple[str, str, str, str]] = []
    for raw, norm in pairs:
        try:
            a, b = _analyse(raw, analyser), _analyse(norm, analyser)
        except NotImplementedError:                        # pragma: no cover
            return _skip("morphology.normalisation", _SKIP_REASON)
        # `analyse` returns the surface form when nothing was renderable, so
        # "analysis == surface" is the uncovered signal check_coverage uses.
        raw_uncovered, norm_uncovered = a.analysis == raw, b.analysis == norm
        if raw_uncovered and norm_uncovered:
            neither += 1
            continue
        if raw_uncovered:
            kind = "rescued"
            rescued += 1
        elif norm_uncovered:
            kind = "lost"
            lost += 1
        elif a.analysis == b.analysis:
            same += 1
            continue
        else:
            kind = "differs"
            differs += 1
        if len(reportable) < 8:
            reportable.append((kind, raw, a.analysis[:24], b.analysis[:24]))

    informative = len(pairs) - neither
    if not informative:
        return PropertyResult(
            name="morphology.normalisation", passed=0, total=0,
            threshold=0.0, measurement_only=True,
            note=f"all {len(pairs)} words that change under normalisation are "
                 f"unanalysable in both forms — this measures coverage, not "
                 f"normalisation, and no comparison is possible. "
                 + _NORMALISATION_NOTE,
        )

    return PropertyResult(
        name="morphology.normalisation", passed=same, total=informative,
        threshold=0.0, measurement_only=True,
        failures=tuple(reportable),
        note=(f"{len(pairs)} words change under normalisation; {neither} are "
              f"unanalysable in BOTH forms and are excluded — they would "
              f"disagree by construction. Of the {informative} informative "
              f"pairs: {same} unchanged, {rescued} analysable only AFTER "
              f"normalisation (it is working), {lost} only BEFORE (it is "
              f"destroying a distinction), {differs} analysed differently by "
              f"both. Only the last two are costs, and only a speaker can rule "
              f"(A-13). " + _NORMALISATION_NOTE),
    )


# -------------------------------------------------------------------- runner

def evaluate_morphology(texts: Sequence[str], *,
                        analyser: Analyser | None = None,
                        require: bool = False) -> IntrinsicReport:
    """Run every morphology intrinsic check and return one report.

    `require=True` converts a missing analyser from SKIP into FAIL. It is for
    anyone who *has* installed HornMorpho and wants the checks enforced — CI on
    such a machine, or the first person to run this for real. The default is
    False because this package must install and test with no GPL-3.0 dependency
    anywhere near it.
    """
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        raise ValueError("nothing to evaluate — pass real Tigrinya text")

    words = [w for t in texts for w in t.split()]
    unique = sorted(set(words))

    results = [
        check_surface(texts, analyser=analyser),
        check_alignment(texts, analyser=analyser),
        check_determinism(unique, analyser=analyser),
        check_coverage(texts, analyser=analyser),
        check_normalisation(unique, analyser=analyser),
    ]

    if require:
        results = [
            PropertyResult(
                name=r.name, passed=0, total=1, threshold=1.0,
                note="REQUIRED but not runnable: " + r.skip_reason,
            ) if r.skipped else r
            for r in results
        ]

    notes: list[str] = []
    if any(r.skipped for r in results):
        notes.append(
            "Morphology was NOT measured. HornMorpho is GPL-3.0 and never "
            "bundled (DEC-028), so it is absent unless installed. The "
            "metrics.md morphology row stays ❌ — a skipped check is not "
            "evidence the property holds. Pass --require to make this fail."
        )
    else:
        notes.append(
            "Measured with an analyser present. `morphology._render` was "
            "checked against live HornMorpho 5.3.6 output on 2026-09-07 and "
            "corrected: a segmentation and a bare part-of-speech tag were "
            "rendering into the same `|`-separated slot. Segmentations are "
            "bare, tags are braced. If you are running against a different "
            "analyser, or a newer HornMorpho, re-check it — no test can "
            "settle the shape of an analysis without an install."
        )
    notes.append(
        "Accuracy is not measured here and cannot be. Experiment 004 found "
        "morphology is the Tier 0 primitive that genuinely needs gold data "
        "(A-006) and a speaker (A-13)."
    )

    return IntrinsicReport(
        results=tuple(results), texts=len(texts), words=len(words),
        unique_words=len(unique), notes=tuple(notes),
    )


def _main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m tigrinya_eval.morphology",
        description="Intrinsic evaluation of morphological analysis "
                    "(DEC-023a, DEC-028).",
    )
    ap.add_argument("paths", nargs="+", help="corpus files or directories of .txt")
    ap.add_argument("--json", metavar="PATH", help="also write the report as JSON")
    ap.add_argument("--require", action="store_true",
                    help="fail instead of skipping when HornMorpho is absent")
    args = ap.parse_args(argv)

    texts = load_corpus(args.paths)
    if not texts:
        print("no .txt found under: " + ", ".join(args.paths))
        return 2

    lines = [ln for t in texts for ln in t.splitlines() if ln.strip()]

    # A parallel anchor directory holds its *source* language too:
    # `data/anchors/tico19` is 6,142 lines of English beside 9,213 of
    # Tigrinya. Analysing English with a Tigrinya FST yields no analysis for
    # every token, so an unfiltered run reports a coverage figure roughly 40%
    # of which is a measurement of English. Found 2026-09-07, on the first run
    # against a real anchor.
    #
    # Dropped rather than refused, because a mixed-script directory is the
    # normal shape of a parallel corpus — but never silently: the count is
    # printed, so a filter that starts eating the corpus is visible instead of
    # inferred from a suspiciously round number.
    tigrinya = [ln for ln in lines if any(is_ethiopic(c) for c in ln)]
    skipped = len(lines) - len(tigrinya)
    if skipped:
        print(f"  {skipped} of {len(lines)} lines contain no Ethiopic script "
              f"and were not analysed (a parallel corpus carries its source "
              f"language too); {len(tigrinya)} lines measured.\n")
    if not tigrinya:
        print("no Ethiopic text found under: " + ", ".join(args.paths))
        return 2

    report = evaluate_morphology(tigrinya, require=args.require)
    print(report.report())
    if args.json:
        report.save(args.json)
        print(f"\n  wrote {args.json}")
    return 0 if report.holds else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
