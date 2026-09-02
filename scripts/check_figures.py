#!/usr/bin/env python3
"""Fail when a document contradicts the repository about a number or an id.

Three checks, aimed at the same failure: something that stopped being true and
nobody noticed.

  1. **Retired figures** — a value registered in `docs/figures.json` as
     superseded, still being asserted as current.
  2. **Derived counts** — a claim about how many decisions, experiments,
     summaries or research domains exist, compared against what is in the tree.
     Nothing is registered for these: the true value is computed.
  3. **Identifier integrity** — every cited `G-n` (a goal) and `GAP-n` (a
     readiness gap) resolves to one that is actually defined.

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
appear with a retraction marker **within `WINDOW` lines above it, or anywhere in
its own paragraph**. What is forbidden is quoting it bare, as current.

The scope is asymmetric on purpose. A marker in the *following* paragraph used
to suppress a live claim, and one did: see `_has_marker`.

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
    "retract", "retired", "supersede", "superseded", "amendment", "amended",
    "estimate", "est;", "should not be quoted", "no longer", "was wrong",
    "withdrawn", "corrected", "correction", "misleading", "diluted",
    "containment", "pre-build", "wrongly", "recorded", "originally",
    "first reported", "came from", "used to", "previously",
    "overturned", "left standing", "still asserting",
    "figures are quoted", "quote these",
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
    # A changelog records what was true on a date, so a count in a dated entry
    # is correct history the moment after it stops being current. Without a way
    # to say so, every CI-check tally ever written becomes a permanent error.
    # Deliberately a full phrase, not "entry" — a bare word would exempt most of
    # the file, which is the mistake COUNT_MARKERS exists to document.
    "as of this entry",
)

#: Searched for quoted figures.
INCLUDE_GLOBS = ("**/*.md", "**/*.py")

#: Not searched. The registry names every retired figure by definition, and the
#: checker quotes them in its own tests.
EXCLUDE_PARTS = (
    ".git", "__pycache__", ".pytest_cache", "node_modules",
    "docs/figures.json", "scripts/check_figures.py",
    # The plant suite asserts this checker can still fail, so it necessarily
    # quotes retired figures and undefined ids as literals. Same reason this
    # file is excluded — and the exclusion is safe because every plant's
    # expected exit status is asserted, so a plant that stopped being detected
    # fails the suite rather than passing quietly.
    "scripts/tests/",
)


def _para_end(lowered: list[str], i: int) -> int:
    """Last line of the blank-line-delimited block containing `i`."""
    hi = i
    while hi + 1 < len(lowered) and lowered[hi + 1].strip():
        hi += 1
    return hi


def _has_marker(lowered: list[str], i: int, markers: tuple) -> bool:
    """True if a retraction/quotation marker scopes line `i`.

    Shared by both checks. A document that *discusses* a wrong number — a
    retraction, a correction table, this project's own decision records — has
    to be able to name it. Only a bare assertion is a violation.

    **The scope is asymmetric, and that asymmetry is the fix.** It used to be
    ±WINDOW lines both ways, so a marker in an unrelated *following* paragraph
    suppressed a live claim. It cost exactly that: `Seven decisions now carry
    amendments` went unchecked — and was wrong — because a `⚠️` opened the next
    paragraph seven lines *below*. In a document that uses ⚠️ as often as the
    readiness plan, whole regions were silently exempt.

    So: **backwards WINDOW lines, forwards only to the end of the current
    paragraph.** Backwards stays generous because a retraction is normally
    written before the figure it retracts — "superseded:", "this used to say".
    Forwards stops at the blank line, which still catches the trailing
    `⚠️ **Superseded**` this repository attaches to a stale paragraph, and stops
    a marker from reaching across into the next one.

    Two tighter rules were tried and rejected by measurement: the paragraph
    alone in both directions (43 errors, breaking legitimate suppressions where
    the marker is a sentence earlier across a blank line) and a fixed one-line
    forward window (22 errors, breaking a trailing ⚠️ two lines down).

    This is the ninth check found unable to fail, and the fifth inside the audit
    tooling itself.
    """
    lo = max(0, i - WINDOW)
    hi = _para_end(lowered, i)
    context = "\n".join(lowered[lo:hi + 1])
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


def _unwrapped(lines: list[str], i: int) -> str:
    """Line `i` joined with the next, blockquote markers and wrapping removed.

    The counts check was line-based, and prose wraps. The README said
    "**24** decisions\n> recorded" while the repository had 25 — the claim
    straddled a line break, so the pattern `\*\*(\d+)\*\* decisions recorded`
    could not match it and the check could not fail on the one file most people
    read first. Found by hand, not by the checker.

    Joining two lines is enough for prose wrapped at 80 columns; a claim spread
    over three lines would still slip through, and that is a known limit rather
    than a solved problem.
    """
    joined = " ".join(lines[i:i + 2])
    return " ".join(joined.replace(">", " ").split())


def _derive(spec: dict) -> int:
    """Compute a count from the repository as it actually is."""
    kind = spec["kind"]
    if kind == "grep_count":
        text = (REPO / spec["file"]).read_text(encoding="utf-8")
        return len(re.findall(spec["pattern"], text, flags=re.MULTILINE))
    if kind == "dir_count":
        return len(list(REPO.glob(spec["glob"])))
    if kind == "section_owners":
        return _section_owners(spec)
    if kind == "csv_rows":
        return _csv_rows(spec)
    raise ValueError(f"unknown derivation kind: {kind}")


def _section_owners(spec: dict) -> int:
    """Count distinct outer sections containing at least one inner heading.

    For "how many decisions carry amendments" — `grep_count` cannot answer it,
    because DEC-007 has two amendments and must still count once. The readiness
    plan said **six** when the answer is five, and nothing could have caught it:
    the claim names no figure and matches no registered count.
    """
    text = (REPO / spec["file"]).read_text(encoding="utf-8")
    outer, inner = re.compile(spec["outer"]), re.compile(spec["inner"])
    current, owners = None, set()
    for line in text.splitlines():
        m = outer.match(line)
        if m:
            current = m.group(1)
        elif current and inner.match(line):
            owners.add(current)
    return len(owners)


def _csv_rows(spec: dict) -> int:
    """Total data rows across a glob — header and `#` instruction lines excluded.

    The validation sheets carry a leading `#` line of instructions for the
    reviewer, so a naive line count over-reports by one per sheet. This counts
    what a reviewer is actually asked to answer.
    """
    total = 0
    for path in sorted(REPO.glob(spec["glob"])):
        rows = [ln for ln in path.read_text(encoding="utf-8-sig").splitlines()
                if ln.strip() and not ln.startswith("#")]
        total += max(0, len(rows) - 1)  # minus the column header
    return total


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
                probes = {_digitise(line), _digitise(_unwrapped(lines, i))}
                for rx in claims:
                    m = next((hit for hit in (rx.search(p) for p in probes) if hit),
                             None)
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


GOALS = REPO / "docs" / "vision" / "goals.md"
PLAN = REPO / "docs" / "roadmap" / "READINESS_PLAN.md"

_GOAL_DEF = re.compile(r"^### (G-\d+)\.", re.MULTILINE)
_GAP_DEF = re.compile(r"^\| \*\*(GAP-\d+)\*\* \|", re.MULTILINE)
_GOAL_CITE = re.compile(r"(?<!GA)(?<!\w)(G-\d+)\b")
_GAP_CITE = re.compile(r"\b(GAP-\d+)\b")


def check_identifiers() -> list[str]:
    """Flag a cited goal or gap id that nothing defines.

    Why this exists: `goals.md` numbers goals **G-1…G-11** and the readiness
    plan numbered its gaps **G-1…G-5**, so `G-4` meant both *"deliver semantic
    search and retrieval"* and *"nothing measured end to end"* — and the plan
    used **both senses four lines apart**. The gaps are now `GAP-n`, and ~50
    citations across 13 files were reclassified by hand, because a blind
    substitution would have corrupted every site that meant the goal.

    This cannot detect *that* kind of mistake — a citation pointing at a real id
    with the wrong meaning still resolves. It catches the cheaper successor:
    an id nobody defines, which is what a typo or a renumbering leaves behind.

    **Known limit, deliberately unfixed:** a document cannot cite a non-existent
    id even to discuss one, so prose about a negative control has to describe
    the planted ids rather than quote them. There is no marker escape hatch on
    purpose — a marker vocabulary is what made two earlier checks in this file
    unable to fail. Reword around the false positive.
    """
    goals = set(_GOAL_DEF.findall(GOALS.read_text(encoding="utf-8")))
    gaps = set(_GAP_DEF.findall(PLAN.read_text(encoding="utf-8")))
    if not goals or not gaps:
        return [f"::error::identifier check found no definitions "
                f"(goals={len(goals)}, gaps={len(gaps)}) — it cannot fail, "
                f"so it is broken"]

    problems = []
    for path in _files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(REPO).as_posix()
        for i, line in enumerate(lines, 1):
            for cite, defined, kind in ((_GAP_CITE, gaps, "gap"),
                                        (_GOAL_CITE, goals, "goal")):
                for m in cite.finditer(line):
                    if m.group(1) not in defined:
                        problems.append(
                            f"::error file={rel},line={i}::"
                            f"{m.group(1)} is cited as a {kind} but nothing "
                            f"defines it\n  {rel}:{i}\n    {line.strip()[:100]}")
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

    count_problems = check_counts(reg) + check_identifiers()

    if not violations and not count_problems:
        n = len(patterns)
        goals = len(_GOAL_DEF.findall(GOALS.read_text(encoding="utf-8")))
        gaps = len(_GAP_DEF.findall(PLAN.read_text(encoding="utf-8")))
        print(f"OK — {n} retired figure pattern(s), "
              f"{len(reg.get('counts', []))} derived count(s) and "
              f"{goals} goal / {gaps} gap ids checked across "
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
