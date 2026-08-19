#!/usr/bin/env python3
"""Fail when a retired figure is quoted as though it were still true.

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
switched-off check is the DEC-008 failure this is meant to prevent. The cost of
that generosity is real: a determined author can satisfy the marker without
actually retracting anything. This catches oversight, not intent.

Usage:
    python3 scripts/check_figures.py            # check, exit 1 on violation
    python3 scripts/check_figures.py --list     # print the current figures
"""

from __future__ import annotations

import argparse
import json
import pathlib
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
MARKERS = (
    "⚠️", "~~",
    "retract", "supersede", "superseded", "amendment", "amended",
    "estimate", "est;", "should not be quoted", "no longer", "was wrong",
    "withdrawn", "corrected", "correction", "misleading", "diluted", "containment",
    "pre-build", "wrongly", "recorded", "originally", "first reported",
    "came from", "used to", "previously",
)

#: Searched for quoted figures.
INCLUDE_GLOBS = ("**/*.md", "**/*.py")

#: Not searched. The registry names every retired figure by definition, and the
#: checker quotes them in its own tests.
EXCLUDE_PARTS = (
    ".git", "__pycache__", ".pytest_cache", "node_modules",
    "docs/figures.json", "scripts/check_figures.py",
)


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
                lo = max(0, i - WINDOW)
                hi = min(len(lines), i + WINDOW + 1)
                context = "\n".join(lowered[lo:hi])
                if any(m in context for m in MARKERS):
                    continue
                violations.append(
                    (path.relative_to(REPO).as_posix(), i + 1, pat,
                     name, retired, current, line.strip()[:100])
                )

    if not violations:
        n = len(patterns)
        print(f"OK — {n} retired figure pattern(s) checked across "
              f"{len(_files())} files; none quoted as current")
        return 0

    print(f"{len(violations)} retired figure(s) quoted as current:\n")
    for path, ln, pat, name, retired, current, text in violations:
        print(f"::error file={path},line={ln}::"
              f"{name}: '{retired}' is retired — current value is '{current}'")
        print(f"  {path}:{ln}")
        print(f"    {text}")
        print(f"    matched {pat!r}; retired {retired!r} -> current {current!r}")
        print(f"    if this is a retraction, say so within {WINDOW} lines "
              f"(e.g. mark it superseded)\n")
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
