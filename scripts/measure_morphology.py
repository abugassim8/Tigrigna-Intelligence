#!/usr/bin/env python3
"""Measure morphology over a large corpus without paying to analyse it 11 times.

Why this exists
---------------
`python -m tigrinya_eval.morphology` calls the analyser once per word **per
check**. Over the full TICO-19 anchor that is ~650,800 analyses:

    surface + alignment + coverage   3 x 194,590 = 583,770
    determinism                      2 x  32,992 =  65,984
    normalisation                    2 x     530 =   1,060

HornMorpho does **not** memoise usefully — measured 2026-09-11, re-analysing the
same 60 words costs **77%** of the first pass, so a repeat is nearly full price.
At the 0.171 s/analysis the 900-segment run actually achieved, that is **~31
hours**: all-or-nothing, no progress output, against a container that can be
reclaimed.

The idea
--------
**`check_determinism` already analyses every unique word twice** — forward, then
in reverse order. Nothing else needs to touch the live analyser at all. So:

1. Wrap the live analyser in a **recorder** that always calls through and keeps
   the *first* result seen for each word.
2. Run `check_determinism` live. Pass 1 fills the table; pass 2 re-analyses
   every word in reverse order and compares.
3. Serve `surface`, `alignment` and `coverage` from the table.

Cost: **2 x unique words** instead of 3 x tokens + 2 x unique — ~65,984 analyses,
about **3-5 hours**, for a result that is not an approximation.

⚠️ The contract that makes this honest
--------------------------------------
**Determinism at 100% is exactly the proof that a table lookup returns what a
live call would have returned.** The substitution is licensed by a *measured*
property, not an assumed one. So if determinism is anything less than perfect
this writes **nothing at all** — not a partial report, because every other
number would then be derived from a table known to be unreliable.

That promotes `check_determinism` from one reported property among five into
**the precondition for the whole measurement**. Wherever these numbers are
quoted, that has to be said.

⚠️ The one line that must never be "optimised"
----------------------------------------------
`_Recorder.__call__` **always calls the live analyser**, even for a word it has
already seen. Serving a cached value there would make `check_determinism`
compare a value against itself, and the check would silently stop being able to
fail — the single failure mode this repository has found ten times. It is
planted against in `scripts/tests/test_plants.py`; if you change it, that plant
must fail.

Normalisation runs **live**, not from the table: it analyses `normalise(w)`,
which need not be a corpus word at all, so the table cannot be assumed to cover
it. At ~1,060 analyses that is about three minutes and not worth a special case.

Not a replacement for the CLI
-----------------------------
This measures the same five properties with the same five checks. It exists only
because the corpus is too big to analyse the naive way. For anything small
enough, use `python -m tigrinya_eval.morphology` — fewer moving parts, and no
contract to honour.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Any, Callable

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "services" / "evaluation" / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent
                       / "services" / "primitives" / "src"))

from tigrinya_primitives import morphology                       # noqa: E402
from tigrinya_eval.morphology import (                           # noqa: E402
    check_alignment, check_coverage, check_determinism,
    check_normalisation, check_surface,
)
from tigrinya_eval.primitives import (                           # noqa: E402
    IntrinsicReport, is_ethiopic, load_corpus,
)

#: How often to write the table to disk, in words. A crash inside a three-hour
#: pass should not cost the whole pass.
CHECKPOINT_EVERY = 500

#: Above this share of unique words, an analyser that raises is not hitting
#: edge cases — it is broken, and measuring around it would be dishonest.
CRASH_ABORT_FRACTION = 0.01


class _Recorder:
    """Wraps the live analyser; keeps the first result seen for each word.

    ⚠️ **`__call__` always calls through.** See the module docstring: returning
    a stored value here would make `check_determinism` compare a value to
    itself. The stored table is a *byproduct* of the check, never an input to
    it.
    """

    def __init__(self, live: Callable[[str], Any], *,
                 replay: dict[str, str] | None = None,
                 checkpoint: pathlib.Path | None = None,
                 total: int = 0) -> None:
        self._live = live
        self._checkpoint = checkpoint
        self.table: dict[str, str] = {}
        self.warnings: list[str] = []
        #: Words the analyser *raised* on. Kept apart from words it simply
        #: found nothing for: "the analyser threw" and "there is no analysis"
        #: are different facts, and reporting them as one number is the
        #: conflation this repository keeps finding.
        self.crashed: dict[str, str] = {}
        #: Words whose *first* analysis comes from a previous process, for
        #: --resume. Popped on first use, so the second (reverse-order) pass
        #: still goes live and determinism still compares two real analyses.
        self._replay = dict(replay or {})
        self.replayed = 0
        self.calls = 0
        self._total = total
        self._started = time.time()
        self._last_report = 0.0

    def __call__(self, word: str) -> Any:
        self.calls += 1
        self._progress()
        if word in self._replay:
            # A checkpointed pass-1 result. The reverse pass is live, so
            # determinism compares an earlier process's analysis against this
            # one — a stronger independence claim than within one process.
            self.replayed += 1
            replayed = self._replay.pop(word)
            self.table.setdefault(word, replayed)
            return [replayed]
        try:
            raw = self._live(word)                # ALWAYS live. See docstring.
        except Exception as exc:                  # noqa: BLE001 — see below
            # HornMorpho 5.3.6 raises on some tokens: `analyze_unanalyzed5`
            # handles a lexicon entry of length 1, then assumes length 2, so
            # any longer entry is a ValueError. Its Tigrinya lexicon has one —
            # `'#' -> ['Light', 'verb', 'particles']`, a comment header parsed
            # as a word — and the anchor contains a bare `#`.
            #
            # Dying here would mean no measurement at all because of one
            # token. Swallowing it would turn an upstream defect into a
            # coverage statistic. So: recorded by name, reported loudly, and
            # counted as unanalysable — which is what an empty result already
            # means to `analyse`.
            self.crashed.setdefault(word, f"{type(exc).__name__}: {exc}")
            self.table.setdefault(word, word)
            return []
        if word not in self.table:
            self._store(word, raw)
        return raw

    def _store(self, word: str, raw: Any) -> None:
        # Render through the public path so the stored string is exactly what
        # `analyse` would have produced — `_render` passes bare strings
        # through, so `[stored]` replays identically.
        rendered = morphology.analyse(word, analyser=lambda _w: raw)
        if rendered.warnings:
            # Replay would silently drop these. Refuse rather than lose them.
            self.warnings.extend(rendered.warnings)
        self.table[word] = rendered.analysis
        if self._checkpoint and len(self.table) % CHECKPOINT_EVERY == 0:
            self.save()

    def _progress(self) -> None:
        now = time.time()
        if now - self._last_report < 30:
            return
        self._last_report = now
        elapsed = now - self._started
        rate = self.calls / elapsed if elapsed else 0
        expected = self._total * 2 if self._total else 0
        eta = ((expected - self.calls) / rate / 60) if rate and expected else 0
        print(f"    {self.calls:,}/{expected:,} analyses  "
              f"{rate:.1f}/s  {elapsed/60:.0f}m elapsed  ~{eta:.0f}m left",
              flush=True)

    def save(self) -> None:
        if not self._checkpoint:
            return
        tmp = self._checkpoint.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.table, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(self._checkpoint)


def table_analyser(table: dict[str, str]) -> Callable[[str], Any]:
    """Serve a stored analysis. `_render` passes bare strings through."""
    def lookup(word: str) -> Any:
        return [table[word]]
    return lookup


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="scripts/measure_morphology.py",
        description="Morphology intrinsic evaluation over a large corpus "
                    "(DEC-023a, DEC-028).")
    ap.add_argument("paths", nargs="+", help="corpus files or directories")
    ap.add_argument("--json", metavar="PATH", help="write the report as JSON")
    ap.add_argument("--checkpoint", metavar="PATH",
                    help="write the analysis table here as it is built")
    ap.add_argument("--resume", action="store_true",
                    help="reuse a checkpoint as the first determinism pass; "
                         "the reverse pass still runs live")
    ap.add_argument("--expect", metavar="NAME=PASSED/TOTAL", action="append",
                    default=[],
                    help="require a check to produce exactly this result; "
                         "used to validate this harness against a known run")
    args = ap.parse_args(argv)

    if not morphology.is_available():
        print("::error::HornMorpho is not installed, so nothing can be "
              "measured. This harness never skips — see DEC-028.")
        return 2

    texts = load_corpus(args.paths)
    lines = [ln for t in texts for ln in t.splitlines() if ln.strip()]
    # Same filter as the CLI: a parallel anchor carries its source language.
    tigrinya = [ln for ln in lines if any(is_ethiopic(c) for c in ln)]
    if skipped := len(lines) - len(tigrinya):
        print(f"  {skipped} of {len(lines)} lines contain no Ethiopic script "
              f"and were not analysed; {len(tigrinya)} lines measured.\n")
    if not tigrinya:
        print("no Ethiopic text found under: " + ", ".join(args.paths))
        return 2

    # Mirrors evaluate_morphology exactly: texts to surface/alignment/coverage,
    # sorted unique words to determinism/normalisation.
    words = [w for t in tigrinya for w in t.split()]
    unique = sorted(set(words))
    print(f"  {len(tigrinya):,} texts, {len(words):,} words, "
          f"{len(unique):,} unique")
    print(f"  ~{len(unique) * 2:,} analyses to run "
          f"(the naive path would run ~{len(words) * 3 + len(unique) * 2:,})\n")

    checkpoint = pathlib.Path(args.checkpoint) if args.checkpoint else None
    replay = None
    if args.resume and checkpoint and checkpoint.exists():
        replay = json.loads(checkpoint.read_text(encoding="utf-8"))
        print(f"  resuming: {len(replay):,} words replayed from {checkpoint}\n")

    live = morphology._analyser()
    rec = _Recorder(live, replay=replay, checkpoint=checkpoint,
                    total=len(unique))

    print("  [1/3] determinism — both passes live, and this is what licenses "
          "the table")
    determinism = check_determinism(unique, analyser=rec)
    rec.save()

    if rec.crashed:
        share = len(rec.crashed) / len(unique)
        print(f"\n  ⚠️  the analyser RAISED on {len(rec.crashed)} of "
              f"{len(unique):,} unique words ({share:.3%}). These are counted "
              f"as unanalysable, and named here so they are never mistaken "
              f"for words it simply had no analysis for:")
        for w, err in list(rec.crashed.items())[:10]:
            print(f"        {w!r}  {err}")
        if share > CRASH_ABORT_FRACTION:
            print(f"\n::error::that is above {CRASH_ABORT_FRACTION:.0%} — the "
                  f"analyser is broken here, not meeting edge cases, and "
                  f"measuring around it would be dishonest. Nothing written.")
            return 1
        print()

    if rec.warnings:
        print("\n::error::the analyser produced warnings that a replayed "
              "table would silently drop:")
        for w in dict.fromkeys(rec.warnings):
            print(f"::error::  {w}")
        return 1

    if not determinism.holds or determinism.passed != determinism.total:
        print(f"\n::error::determinism is {determinism.passed}/"
              f"{determinism.total}, not perfect. The analysis table is "
              f"therefore unreliable and EVERY other number derived from it "
              f"would be meaningless. Nothing written.")
        for f in determinism.failures:
            print(f"::error::  {f}")
        return 1
    print(f"        {determinism.passed:,}/{determinism.total:,} — table is "
          f"licensed\n")

    missing = [w for w in unique if w not in rec.table]
    if missing:
        print(f"::error::{len(missing)} words never reached the table "
              f"(e.g. {missing[:3]}). Refusing to measure from it.")
        return 1

    served = table_analyser(rec.table)
    print("  [2/3] surface, alignment, coverage — served from the table")
    results = [
        check_surface(tigrinya, analyser=served),
        check_alignment(tigrinya, analyser=served),
        determinism,
        check_coverage(tigrinya, analyser=served),
    ]
    print("  [3/3] normalisation — live, because normalise(w) need not be a "
          "corpus word\n")
    results.append(check_normalisation(unique, analyser=live))

    notes = [
        "MEASURED THROUGH scripts/measure_morphology.py, not the CLI. The "
        "analyser was called twice per unique word — by check_determinism — "
        "and surface/alignment/coverage were served from the table that built. "
        "Determinism at 100% is what licenses that substitution; at anything "
        "less the run aborts and writes nothing.",
        "Accuracy is not measured here and cannot be. Experiment 004 found "
        "morphology is the Tier 0 primitive that genuinely needs gold data "
        "(A-006) and a speaker (A-13).",
    ]
    if rec.crashed:
        notes.append(
            f"THE ANALYSER RAISED on {len(rec.crashed)} of {len(unique):,} "
            f"unique words and they are counted as unanalysable: "
            f"{sorted(rec.crashed)[:10]}. HornMorpho 5.3.6's "
            f"analyze_unanalyzed5 unpacks a lexicon entry as exactly two "
            f"fields after handling length 1, so a longer entry raises "
            f"ValueError; its Tigrinya lexicon contains one — '#' mapped to "
            f"['Light', 'verb', 'particles'], a comment header parsed as a "
            f"word entry. This depresses coverage by that many tokens and is "
            f"an upstream defect, not a property of Tigrinya.")
    if rec.replayed:
        notes.append(
            f"RESUMED: {rec.replayed:,} first-pass analyses came from a "
            f"previous process, so determinism compared analyses across two "
            f"interpreter runs rather than within one.")

    report = IntrinsicReport(results=tuple(results), texts=len(tigrinya),
                             words=len(words), unique_words=len(unique),
                             notes=tuple(notes))
    print(report.report())

    for expectation in args.expect:
        name, _, wanted = expectation.partition("=")
        got = next((f"{r.passed}/{r.total}" for r in results
                    if r.name.endswith(name)), None)
        if got != wanted:
            print(f"\n::error::{name}: expected {wanted}, measured {got}. "
                  f"This harness must reproduce a known run exactly before "
                  f"its numbers can be trusted. Nothing written.")
            return 1
        print(f"  ✅ {name} reproduced exactly: {got}")

    if args.json:
        report.save(args.json)
        print(f"\n  wrote {args.json}")
    return 0 if report.holds else 1


if __name__ == "__main__":                                 # pragma: no cover
    raise SystemExit(main())
