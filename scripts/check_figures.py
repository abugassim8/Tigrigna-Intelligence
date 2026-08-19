#!/usr/bin/env python3
"""Fail when a document contradicts the repository about a number.

Two checks, both aimed at the same failure: a number that stopped being true
and nobody noticed.

  1. **Retired figures** — a value registered in `docs/figures.json` as
     superseded, still being asserted as current.
  2. **Derived counts** — a claim about how many decisions, experiments,
     summaries or research domains exist, compared against what is in the tree.
     Nothing is registered for these: the true value is computed.

Why this exists
---------------
Three load-bearing figures in this repo were corrected in one place and left
standing in others: **72 MB** in five documents, **22x** in four, and DEC-023's
**1,639/1,639** in three. Every one was found by hand, and each sweep missed
files the next sweep caught. DEC-018's whole argument is that a rule nothing
checks is a rule that quietly stops holding, and "remember to grep for the old
number" is exactly such a rule.

What it does NOT do
-------------------
It does not verify that current figures are correct — nothing here re-derives a
measurement. It catches one specific, demonstrated failure: a **retired** number
still being asserted somewhere nobody looked.

The retraction rule
-------------------
A retired figure may appear — retracting a number requires naming it. It must
appear **within `WINDOW` lines of a retraction marker**. What is forbidden is
quoting it bare, as current.

Deliberately generous markers, because a noisy check gets switched off, and a
switched-off check is the DEC-008 failure this is meant to prevent. Three costs
of that generosity, all real and all demonstrated:

  - a determined author can satisfy a marker without retracting anything;
  - a marker on a *neighbouring* line suppresses a genuine violation within the
    window — verified: a bare "72 MB" went unflagged eight lines under an
    unrelated sentence containing "recorded";
  - the two marker sets must not overlap the claim phrasings they guard, or the
    check silently cannot fail (see COUNT_MARKERS).

**This catches oversight, not intent**, and it is a net, not a proof.

Both checks were validated by planting violations and watching them fail. The
first counts control is why `_digitise` exists — see the note there.

Usage:
    python3 scripts/check_figures.py            # check, exit 1 on violation
    python3 scripts/check_figures.py --list     # print the current figures
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = REPO / "docs" / "figures.json"

#: Lines either side of a hit that may carry the retraction marker. Tuned to 8
#: against the retraction sites that already exist: a struck figure often sits
#: in a blockquote several lines below the heading that retracts it.
WINDOW = 8

#: Any of these near a retired figure means it is being retracted, not asserted.
#:
#: Chosen to be words that appear when *discussing* a figure's history rather
#: than asserting it. "measured" is deliberately absent — it appears everywhere
#: and would neuter the check.
FIGURE_MARKERS = (
    "⚠️", "~~",
    "retract", "supersede", "superseded", "amendment", "amended",
    "estimate", "est;", "should not be quoted", "no longer", "was wrong",
    "withdrawn", "corrected", "correction", "misleading", "diluted",
    "containment", "pre-build", "wrongly", "recorded", "originally",
    "first reported", "came from", "used to", "previously",
)

#: Markers for the COUNTS check — a deliberately different set.
#:
#: They must not overlap the claim phrasings themselves, and the first attempt
#: did: sharing one list put "recorded" in scope, and the claim being checked is
#: literally "N decisions recorded". Every counts violation was suppressed and
#: the negative control went green. **A shared vocabulary made the check unable
#: to fail** — the third time in two days, after DEC-023's containment test and
#: the spelled-out-numbers gap.
COUNT_MARKERS = (
    "⚠️", "~~",
    "claimed", "actual", "planted", "negative control", "rotted",
    "still said", "document says", "superseded", "corrected", "was wrong",
    "used to", "previously",
)

#: Searched for quoted figures.
INCLUDE_GLOBS = ("**/*.md", "**/*.py")

#: Not searched. The registry names every retired figure by definition, and the
#: checker quotes them in its own tests.
EXCLUDE_PARTS = (
    ".git", "__pycache__", ".pytest_cache", "node_modules",
    "docs/figures.json", "scripts/check_figures.py",
)


def _has_marker(lowered: list[str], i: int, markers: tuple) -> bool:
    """True if a retraction/quotation marker sits within WINDOW lines of `i`.

    Shared by both checks. A document that *discusses* a wrong number — a
    retraction, a correction table, this project's own decision records — has
    to be able to name it. Only a bare assertion is a violation.
    """
    lo = max(0, i - WINDOW)
    hi = min(len(lowered), i + WINDOW + 1)
    context = "\n".join(lowered[lo:hi])
    return any(m in context for m in markers)


def _load() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _files() -> list[pathlib.Path]:
    seen: list[pathlib.Path] = []
    for pattern in INCLUDE_GLOBS:
        for f in REPO.glob(pattern):
            rel = f.relative_to(REPO).as_posix()
            if any(part in rel for part in EXCLUDE_PARTS):
                continue
            seen.append(f)
    return sorted(seen)


#: Spelled-out numbers, normalised to digits before a claim is matched.
#:
#: Not an optional nicety. The first negative control caught a planted
#: "**3** reproducible experiments" and sailed straight past "four research
#: domains complete" and "Eight decisions recorded" — which is *verbatim* what
#: the README actually said while the repo had 13 and 24. Without this the
#: check would have missed the exact instance it was written for.
_WORD_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
}
_WORD_RX = re.compile(
    r"\b(" + "|".join(_WORD_NUMBERS) + r")\b", flags=re.IGNORECASE)


def _digitise(line: str) -> str:
    """Replace spelled-out numbers with digits, for matching only."""
    return _WORD_RX.sub(lambda m: str(_WORD_NUMBERS[m.group(1).lower()]), line)


def _derive(spec: dict) -> int:
    """Compute a count from the repository as it actually is."""
    kind = spec["kind"]
    if kind == "grep_count":
        text = (REPO / spec["file"]).read_text(encoding="utf-8")
        return len(re.findall(spec["pattern"], text, flags=re.MULTILINE))
    if kind == "dir_count":
        return len(list(REPO.glob(spec["glob"])))
    raise ValueError(f"unknown derivation kind: {kind}")


def check_counts(reg: dict) -> list[str]:
    """Flag documents asserting a count the repository contradicts.

    Nothing is registered here — the true value is computed, so a document
    either agrees with the repo or it does not. This is what caught the README
    claiming "four research domains complete, eight decisions recorded" when
    there were 13 and 24.
    """
    problems: list[str] = []
    for spec in reg.get("counts", []):
        actual = _derive(spec["derive"])
        claims = [re.compile(p) for p in spec["claims"]]
        for path in _files():
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            lowered = [ln.lower() for ln in lines]
            for i, line in enumerate(lines):
                probe = _digitise(line)
                for rx in claims:
                    m = rx.search(probe)
                    if not m:
                        continue
                    claimed = int(m.group(1))
                    if claimed == actual:
                        continue
                    if _has_marker(lowered, i, COUNT_MARKERS):
                        continue
                    rel = path.relative_to(REPO).as_posix()
                    problems.append(
                        f"::error file={rel},line={i+1}::"
                        f"{spec['name']}: document says {claimed}, "
                        f"repository has {actual}\n"
                        f"  {rel}:{i+1}\n    {line.strip()[:100]}"
                    )
    return problems


def _retired_patterns(reg: dict) -> list[tuple[str, str, str, str]]:
    """(pattern, figure_name, retired_value, current_value)"""
    out = []
    for fig in reg["figures"]:
        for r in fig.get("retired", []):
            for pat in r["patterns"]:
                out.append((pat, fig["name"], r["value"], fig["current"]))
    return out


def check() -> int:
    reg = _load()
    patterns = _retired_patterns(reg)
    if not patterns:
        print("no retired figures registered — nothing to check")
        return 0

    violations = []
    for path in _files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        lowered = [ln.lower() for ln in lines]
        for i, line in enumerate(lines):
            for pat, name, retired, current in patterns:
                if pat not in line:
                    continue
                if _has_marker(lowered, i, FIGURE_MARKERS):
                    continue
                violations.append(
                    (path.relative_to(REPO).as_posix(), i + 1, pat,
                     name, retired, current, line.strip()[:100])
                )

    count_problems = check_counts(reg)

    if not violations and not count_problems:
        n = len(patterns)
        print(f"OK — {n} retired figure pattern(s) and "
              f"{len(reg.get('counts', []))} derived count(s) checked across "
              f"{len(_files())} files; nothing stale")
        return 0

    if violations:
        print(f"{len(violations)} retired figure(s) quoted as current:\n")
    for path, ln, pat, name, retired, current, text in violations:
        print(f"::error file={path},line={ln}::"
              f"{name}: '{retired}' is retired — current value is '{current}'")
        print(f"  {path}:{ln}")
        print(f"    {text}")
        print(f"    matched {pat!r}; retired {retired!r} -> current {current!r}")
        print(f"    if this is a retraction, say so within {WINDOW} lines "
              f"(e.g. mark it superseded)\n")

    if count_problems:
        print(f"{len(count_problems)} count(s) the repository contradicts:\n")
        for p in count_problems:
            print(p + "\n")
    return 1


def show() -> int:
    reg = _load()
    print(f"{'FIGURE':44s} {'CURRENT':>26s}   BASIS")
    print("-" * 110)
    for fig in reg["figures"]:
        print(f"{fig['name']:44s} {fig['current']:>26s}   {fig['basis']}")
        for r in fig.get("retired", []):
            print(f"{'  retired: ' + r['value']:44s} {'':>26s}   "
                  f"{r['reason']} ({r['superseded']})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true",
                    help="print the register instead of checking")
    args = ap.parse_args()
    return show() if args.list else check()


if __name__ == "__main__":
    sys.exit(main())
