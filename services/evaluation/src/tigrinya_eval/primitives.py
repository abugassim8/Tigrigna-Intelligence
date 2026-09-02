"""Intrinsic evaluation for the Tier 0 primitives (DEC-023a).

Why this module exists
----------------------
**DEC-021** found that every capability DEC-006 put in the MVP had no way to
tell whether it worked, while translation — which the MVP *excludes* — had a
validated metric. The first version of this package reproduced exactly that
error in code: `metrics.py` and `harness.py` score chrF and BLEU, which measure
translation and nothing else.

This module closes that gap. **DEC-023(a)** established that primitives are
evaluated *intrinsically* first: idempotence, determinism, reversibility,
coverage and alignment integrity are properties of the function, so they need
**no annotated data** — which is the whole reason Tier 0 could be evaluated
without first spending months building a Tigrinya benchmark (**A-006**).

What these checks are worth, stated up front
--------------------------------------------
**They catch *broken*, not *wrong*.** A transliterator returning confidently
incorrect phonemes passes determinism perfectly. Every check here is necessary
and none is sufficient; accuracy still needs a gold standard and a speaker.
`IntrinsicReport.report()` carries that caveat so it cannot travel without it.

Two traps these checks are shaped to avoid
------------------------------------------
1. **Never test containment where you mean equality.** DEC-023 originally
   recorded that a word's transliteration survives a sentence "1,639/1,639
   (100%)". That came from `alone in in_context`, which cannot detect an
   appended character — and an appended character is 92% of the real failures.
   By exact equality the figure is **95.47%**. See `check_context_divergence`,
   which pins the corrected number so the error cannot recur silently.
2. **Never let a cache answer the question.** `transliterate_word` is
   `@lru_cache`d, so "call it twice and compare" reads the memo table on the
   second call and can only ever pass. `check_determinism` clears the cache
   between passes and re-runs in a different order.

`[verified]` experiments 004 and 005.
"""

from __future__ import annotations

import json
import pathlib
import random
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from tigrinya_primitives import (
    GeezTokenizer,
    normalise,
    transliterate,
)
from tigrinya_primitives.transliterate import transliterate_word

# --------------------------------------------------------------- thresholds
#
# Pre-committed, each carrying the measurement it came from. A threshold chosen
# after seeing the number it judges is not a threshold.

#: Experiment 004 H1: 0 failures. Non-idempotent normalisation compounds.
IDEMPOTENCE_THRESHOLD = 1.0

#: Experiment 004 H2: 0 failures, and experiment 005 C2: prepending changes
#: 0 of 1,565 words. Anything below 1.0 makes every downstream number unstable.
DETERMINISM_THRESHOLD = 1.0

#: Experiment 004 H4 predicted >= 99%, measured 100.00% with zero [UNK].
#: DEC-022's verbatim-surface guarantee is unimplementable below this.
REVERSIBILITY_THRESHOLD = 0.99

#: Exact by construction — the analysis form *is* the concatenation of its
#: spans. Not a prediction about the world, so anything under 1.0 is a bug.
ALIGNMENT_THRESHOLD = 1.0

#: A regression guard, NOT a pre-committed prediction, and labelled as such.
#: Measured over Ethiopic **letters and combining marks**: punctuation, digits
#: and Latin are meant to pass through, and counting them measures the corpus
#: instead of the transliterator. 19 real Ethiopic characters are unmapped by
#: `tir-Ethi`, plus three whole blocks — none of them in the current corpus.
COVERAGE_FLOOR = 0.99

#: Experiment 005: word-by-word output differs from epitran's running-text
#: output on 4.53% of word tokens. A ceiling, so a dependency change that moves
#: it is visible. Not a target to improve — see `check_context_divergence`.
CONTEXT_DIVERGENCE_CEILING = 0.06

_CAVEAT = (
    "INTRINSIC CHECKS CATCH *BROKEN*, NOT *WRONG*. A transliterator returning "
    "deterministically incorrect phonemes passes every check here. These "
    "properties are necessary and nowhere near sufficient: accuracy needs a "
    "gold standard and a native speaker, neither of which exists yet (A-006)."
)

#: The Ethiopic blocks. Coverage is measured over these and nothing else.
_ETHIOPIC_BLOCKS = (
    (0x1200, 0x137F),   # Ethiopic
    (0x1380, 0x139F),   # Ethiopic Supplement
    (0x2D80, 0x2DDF),   # Ethiopic Extended
    (0xAB00, 0xAB2F),   # Ethiopic Extended-A
    (0x1E7E0, 0x1E7FF),  # Ethiopic Extended-B — above the BMP
)


def is_ethiopic(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _ETHIOPIC_BLOCKS)


# ------------------------------------------------------------------- results

@dataclass(frozen=True)
class PropertyResult:
    """One intrinsic property, measured over real text."""

    name: str
    passed: int
    total: int
    threshold: float
    #: True when the threshold is a floor/ceiling for catching regressions
    #: rather than a prediction the measurement is testing. The distinction is
    #: recorded because presenting a post-hoc floor as a passed hypothesis is
    #: precisely the overclaiming these experiments exist to prevent.
    regression_guard: bool = False
    failures: tuple[Any, ...] = ()
    note: str = ""

    @property
    def rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    @property
    def holds(self) -> bool:
        return self.total > 0 and self.rate >= self.threshold

    def __str__(self) -> str:
        kind = "floor" if self.regression_guard else "threshold"
        return (
            f"{'PASS' if self.holds else 'FAIL'}  {self.name:24s} "
            f"{self.passed:,}/{self.total:,} = {100 * self.rate:6.2f}%  "
            f"({kind} {100 * self.threshold:.2f}%)"
        )


@dataclass(frozen=True)
class IntrinsicReport:
    """The full Tier 0 intrinsic evaluation."""

    results: tuple[PropertyResult, ...]
    texts: int
    words: int
    unique_words: int
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def holds(self) -> bool:
        return all(r.holds for r in self.results)

    def failures(self) -> tuple[PropertyResult, ...]:
        return tuple(r for r in self.results if not r.holds)

    def report(self) -> str:
        lines = [
            "Tier 0 intrinsic evaluation (DEC-023a)",
            f"  corpus: {self.texts:,} texts, {self.words:,} words, "
            f"{self.unique_words:,} unique",
            "",
        ]
        lines += [f"  {r}" for r in self.results]
        for r in self.results:
            if r.note:
                lines.append(f"      note: {r.note}")
        lines += ["", f"  VERDICT: {'PASS' if self.holds else 'FAIL'}"]
        if not self.holds:
            lines.append("  failing: " + ", ".join(r.name for r in self.failures()))
        # The caveat travels with the report, because a report that leaves its
        # caveats behind will be quoted without them.
        lines += ["", "  " + _CAVEAT]
        if self.notes:
            lines += [""] + [f"  {n}" for n in self.notes]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "texts": self.texts,
            "words": self.words,
            "unique_words": self.unique_words,
            "holds": self.holds,
            "caveat": _CAVEAT,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "total": r.total,
                    "rate": round(r.rate, 6),
                    "threshold": r.threshold,
                    "regression_guard": r.regression_guard,
                    "holds": r.holds,
                    "note": r.note,
                    "failures": [
                        list(f) if isinstance(f, tuple) else f
                        for f in r.failures[:8]
                    ],
                }
                for r in self.results
            ],
            "notes": list(self.notes),
        }

    def save(self, path: str | pathlib.Path) -> None:
        pathlib.Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def caveat() -> str:
        return _CAVEAT


# -------------------------------------------------------------------- checks

def check_idempotence(texts: Sequence[str]) -> PropertyResult:
    """`normalise(normalise(x)) == normalise(x)` (DEC-023a, experiment 004 H1).

    Also verifies normalisation is **length-preserving**, which the offsets in
    DEC-022 depend on: every substitution is 1:1, so an offset computed on the
    input stays valid on the output. That is a separate promise from
    idempotence and it is checked separately.
    """
    ok = 0
    failures: list[tuple[str, str]] = []
    for t in texts:
        once = normalise(t)
        if normalise(once) == once and len(once) == len(t):
            ok += 1
        elif len(failures) < 8:
            failures.append((t[:40], once[:40]))
    return PropertyResult(
        name="normalisation.idempotent",
        passed=ok,
        total=len(texts),
        threshold=IDEMPOTENCE_THRESHOLD,
        failures=tuple(failures),
        note="also asserts length preservation, which DEC-022's offsets rely on",
    )


def check_determinism(words: Sequence[str], seed: int = 20260818) -> PropertyResult:
    """Transliteration is deterministic (DEC-023a, experiment 004 H2).

    The cache is cleared between passes and the second pass runs in a shuffled
    order. Without both, this check is worthless: `transliterate_word` is
    `@lru_cache`d, so a naive repeat-call comparison reads the memo table and
    passes unconditionally, and a same-order re-run cannot expose order
    dependence in the underlying map.
    """
    transliterate_word.cache_clear()
    first = {w: transliterate_word(w) for w in words}

    shuffled = list(words)
    random.Random(seed).shuffle(shuffled)
    transliterate_word.cache_clear()

    ok = 0
    failures: list[tuple[str, str, str]] = []
    for w in shuffled:
        again = transliterate_word(w)
        if again == first[w]:
            ok += 1
        elif len(failures) < 8:
            failures.append((w, first[w], again))
    return PropertyResult(
        name="transliteration.deterministic",
        passed=ok,
        total=len(words),
        threshold=DETERMINISM_THRESHOLD,
        failures=tuple(failures),
        note="cache cleared between passes and order shuffled; without both "
             "this check cannot fail",
    )


def check_alignment_integrity(texts: Sequence[str]) -> PropertyResult:
    """Spans index back into the surface, and reproduce the analysis form.

    DEC-023 calls word-level alignment "exact by construction". This checks it
    rather than trusting it — the DEC-018 lesson is that a rule nothing
    verifies is a rule that silently stops holding.

    Two distinct promises, both required:

      - every span's offsets index back to its own surface text (DEC-022)
      - concatenating the spans, with the original whitespace restored,
        reproduces `analysis` exactly — **equality, never containment**
    """
    ok = 0
    failures: list[tuple[str, str]] = []
    for t in texts:
        a = transliterate(t)
        try:
            a.verify_offsets()
        except ValueError as e:  # pragma: no cover - a real failure path
            if len(failures) < 8:
                failures.append((t[:40], str(e)[:80]))
            continue

        # Rebuild the analysis form from the spans plus the whitespace between
        # them, exactly as `transliterate` composes it.
        parts: list[str] = []
        cursor = 0
        for s in a.spans:
            parts.append(t[cursor:s.start])   # the untouched whitespace
            parts.append(s.analysis)
            cursor = s.end
        parts.append(t[cursor:])
        rebuilt = "".join(parts)

        surface_ok = all(t[s.start:s.end] == s.surface for s in a.spans)
        if rebuilt == a.analysis and surface_ok and a.surface == t:
            ok += 1
        elif len(failures) < 8:
            failures.append((t[:40], rebuilt[:60]))
    return PropertyResult(
        name="alignment.integrity",
        passed=ok,
        total=len(texts),
        threshold=ALIGNMENT_THRESHOLD,
        failures=tuple(failures),
        note="exact equality on the rebuilt analysis form, never containment",
    )


def check_reversibility(texts: Sequence[str],
                        tokenizer: GeezTokenizer | None = None) -> PropertyResult:
    """`decode(encode(x)) == x` with no `[UNK]` (DEC-023a, experiment 004 H4).

    DEC-022 obliges the API to return surface forms verbatim, which is
    impossible if the tokenizer cannot reconstruct its input. This is the check
    that caught the byte-level BPE `[UNK]` bug: a tokenizer trained without a
    complete initial alphabet mangled ordinary Tigrinya it had not seen.
    """
    if tokenizer is None:
        tokenizer = GeezTokenizer.train(texts, vocab_size=2000, min_frequency=1)
    ok = 0
    unk = 0
    failures: list[tuple[str, str]] = []
    for t in texts:
        unk += sum(1 for tok in tokenizer.tokens(t) if tok == "[UNK]")
        if tokenizer.round_trips(t):
            ok += 1
        elif len(failures) < 8:
            failures.append((t[:40], tokenizer.decode(tokenizer.encode(t))[:40]))
    return PropertyResult(
        name="tokenization.reversible",
        passed=ok,
        total=len(texts),
        threshold=REVERSIBILITY_THRESHOLD,
        failures=tuple(failures),
        note=f"{unk} [UNK] tokens produced" + (" — must be 0" if unk else ""),
    )


def check_coverage(texts: Sequence[str]) -> PropertyResult:
    """What share of Ethiopic **letters and marks** the transliterator maps.

    The denominator took two corrections, and both were the same mistake:
    counting characters that are *supposed* to pass through unchanged.

      - Experiment 004 measured **99.72%** over all characters. The five misses
        were **digits**. A transliterator that left `1960` alone was being
        marked down for correct behaviour.
      - Restricting to Ethiopic codepoints still gave **96.86%**, and all 197
        misses were **Ethiopic punctuation** — `።` `፡` `፣` `፤` `፥`. Same error,
        one category further in.

    Restricted to general categories `Lo` and `Mn` — letters and combining
    marks — the corpus figure is **100.00%**. That is the number that means
    "every character that should have been transliterated was."

    This is a **regression guard**, not a hypothesis: the floor exists so a
    dependency change that stops mapping a syllable is visible. It is not
    evidence that coverage is complete — DEC-007 records 19 Ethiopic characters
    (16 syllables, 3 combining marks) that `tir-Ethi` does not map, plus three
    entire blocks. **None of them appears in this corpus**, which is a fact
    about the corpus, not about the map.
    """
    mapped = total = 0
    unmapped: dict[str, int] = {}
    for t in texts:
        for ch in t:
            # Letters and combining marks only. Punctuation, digits and Latin
            # are meant to pass through, so including them measures the corpus
            # rather than the transliterator.
            if not is_ethiopic(ch) or unicodedata.category(ch) not in ("Lo", "Mn"):
                continue
            total += 1
            if transliterate_word(ch) != ch:
                mapped += 1
            else:
                unmapped[ch] = unmapped.get(ch, 0) + 1
    worst = sorted(unmapped.items(), key=lambda kv: -kv[1])[:8]
    return PropertyResult(
        name="transliteration.coverage",
        passed=mapped,
        total=total,
        threshold=COVERAGE_FLOOR,
        regression_guard=True,
        failures=tuple(
            (ch, unicodedata.name(ch, "?"), n) for ch, n in worst
        ),
        note="Ethiopic letters and combining marks only; punctuation, digits "
             "and Latin are meant to pass through and are not counted",
    )


def check_context_divergence(texts: Sequence[str]) -> PropertyResult:
    """Pin how far word-by-word output sits from epitran's running-text output.

    This is the check DEC-023 needed and did not have. It measures the thing
    the original claim got wrong, **by exact equality**, and treats the measured
    4.53% as a ceiling so a dependency change that moves it is visible.

    It is a *ceiling*, not a target. The divergence is not a defect to close:
    experiment 005 showed the running-text form depends on text arbitrarily far
    away — a distant edit flips a word 72 positions later — so it cannot serve
    an API contract, and word-by-word is the correct behaviour precisely
    because it does not reproduce it.

    Reaches past the public API to `_epi` deliberately. The whole-text path is
    not exposed, and should not be; but a verification harness whose job is to
    test the assumption the public API rests on has to be able to see it.
    """
    from tigrinya_primitives.transliterate import _epi

    epi = _epi()
    same = total = 0
    failures: list[tuple[str, str, str]] = []
    for t in texts:
        for line in t.splitlines():
            if not line.strip():
                continue
            words = line.split()
            in_context = epi.transliterate(line).split()
            if len(in_context) != len(words):
                # Token counts disagree, so words cannot be paired. Counted as
                # divergent rather than skipped: a skipped case is a hidden one.
                total += len(words)
                continue
            for w, ctx in zip(words, in_context):
                total += 1
                if transliterate_word(w) == ctx:
                    same += 1
                elif len(failures) < 8:
                    failures.append((w, transliterate_word(w), ctx))
    diverged = total - same
    rate = diverged / total if total else 0.0
    # Expressed as "tokens within the ceiling" so it reads like the others.
    within = total if rate <= CONTEXT_DIVERGENCE_CEILING else same
    return PropertyResult(
        name="transliteration.context_divergence",
        passed=within,
        total=total,
        threshold=1.0,
        regression_guard=True,
        failures=tuple(failures),
        note=f"{diverged:,}/{total:,} = {100 * rate:.2f}% of word tokens differ "
             f"from running-text output (ceiling "
             f"{100 * CONTEXT_DIVERGENCE_CEILING:.0f}%); expected and correct — "
             f"see DEC-023 Amendment 1",
    )


# ------------------------------------------------------------------ harness

def evaluate_primitives(texts: Sequence[str],
                        tokenizer: GeezTokenizer | None = None,
                        include_context_divergence: bool = True
                        ) -> IntrinsicReport:
    """Run every intrinsic check over `texts` and return one report.

    `texts` should be real Tigrinya. These are property checks over running
    text, not unit tests over fixtures: the properties are cheap to satisfy on
    curated input and the point is to find where real text breaks them.
    """
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        raise ValueError("nothing to evaluate — pass real Tigrinya text")

    words = [w for t in texts for w in t.split()]
    unique = sorted(set(words))

    results = [
        check_idempotence(texts),
        check_determinism(unique),
        check_alignment_integrity(texts),
        check_reversibility(texts, tokenizer),
        check_coverage(texts),
    ]
    if include_context_divergence:
        results.append(check_context_divergence(texts))

    notes = (
        "Morphology is not evaluated here. It is now implemented as an adapter "
        "(DEC-028), but HornMorpho is GPL-3.0 and is never bundled, so it is "
        "absent unless the user installed it. Nothing to measure without an "
        "analyser present. See tigrinya_primitives.morphology.",
    )
    return IntrinsicReport(
        results=tuple(results),
        texts=len(texts),
        words=len(words),
        unique_words=len(unique),
        notes=notes,
    )


def load_corpus(paths: Iterable[str | pathlib.Path],
                skip_marker: str = "CORRUPTED") -> list[str]:
    """Read `.txt` files from files or directories.

    `skip_marker` excludes the deliberately-corrupted sample by filename, the
    same exclusion DEC-015's quality gate applies.
    """
    texts: list[str] = []
    for p in paths:
        p = pathlib.Path(p)
        files = sorted(p.glob("*.txt")) if p.is_dir() else [p]
        for f in files:
            if skip_marker in f.name:
                continue
            texts.append(f.read_text(encoding="utf-8"))
    return texts


def _main(argv: Sequence[str] | None = None) -> int:
    """Run the intrinsic evaluation over corpus paths and exit non-zero on
    failure, so CI enforces DEC-023(a) rather than merely recording it."""
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m tigrinya_eval.primitives",
        description="Intrinsic evaluation of the Tier 0 primitives (DEC-023a).",
    )
    ap.add_argument("paths", nargs="+",
                    help="corpus files or directories of .txt")
    ap.add_argument("--json", metavar="PATH",
                    help="also write the report as JSON")
    ap.add_argument("--no-context-divergence", action="store_true",
                    help="skip the running-text comparison (slow on big corpora)")
    args = ap.parse_args(argv)

    texts = load_corpus(args.paths)
    if not texts:
        print("no .txt found under: " + ", ".join(args.paths))
        return 2

    # Evaluate line by line. Properties are cheap to satisfy on a handful of
    # large blobs and the failures live in individual sentences.
    lines = [ln for t in texts for ln in t.splitlines() if ln.strip()]
    report = evaluate_primitives(
        lines, include_context_divergence=not args.no_context_divergence
    )
    print(report.report())
    if args.json:
        report.save(args.json)
        print(f"\n  wrote {args.json}")
    return 0 if report.holds else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
