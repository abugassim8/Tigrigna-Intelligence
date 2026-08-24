#!/usr/bin/env python3
"""Fail when new work is stamped with an older date than the commit that made it.

The problem this catches
------------------------
Dates in this repository are typed by hand. On 2026-08-24 an audit of the plan
of record found that **every document date written since 2026-08-21 said
`2026-08-19`** — six commits' worth of work stamped with the date of the last
session rather than its own.

Measuring it found the habit is older and worse than that one session:
**71 stamps across 34 files** are earlier than the commit carrying them, and the
gap reaches **15 days**. Ten research summaries and eleven reports are dated
2026-08-03 but were committed on the 17th and 18th. The drift is not an
occasional slip; it is how this record has been dated throughout.

That matters more here than it would elsewhere. This project's method is that
the record is true and corrections are dated, and several arguments turn on
elapsed time — "DEC-022 clause 5 sat unimplemented for 5 days", "the register
was frozen for 25 days". Those intervals are computed from stamps that are
themselves unreliable.

Why this is a ratchet and not a clean gate
------------------------------------------
The 71 existing stamps cannot be fixed mechanically. Some are event dates that
two documents record differently, and choosing between them is a judgement per
line, not a rewrite. Grandfathering them all into an allowlist would make the
check unable to fail, which is the failure mode this repository keeps finding in
its own tooling.

So it enforces a **ceiling**: drift may not grow. New drift fails; the recorded
backlog is debt, visible in the output every run, and shrinking it lowers the
ceiling. The check was validated the only way that works here — by planting a
drifted date and watching it fail.

Only self-referential stamps are considered
-------------------------------------------
The first version compared **every** date against its commit and reported 228
lines — because a decision table written in August correctly cites DEC-007's
date of 2026-07-29, and that is not drift. A check whose output is mostly
legitimate is a check that gets ignored.

So it looks only at dates that claim *this was written or done then*: a report's
`| **Date** |` header, an `**Updated:**` field, a CHANGELOG or amendment heading,
`corrected/updated/refreshed/verified <date>`. A backward citation of someone
else's date is not a stamp and is not examined.

What it does NOT do
-------------------
It does not verify a stamp is *right*, only that it is not older than the commit
carrying it. A stamp that is too *recent* — work dated tomorrow — is invisible
here, and so is a wholly invented date on a commit made the same day.

Usage:
    python3 scripts/check_dates.py            # check against the ceiling
    python3 scripts/check_dates.py --list     # print every drifted line
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Maximum drifted stamps tolerated. Measured at 71 on 2026-08-24; lower it
#: whenever the backlog is worked down. Never raise it.
CEILING = 71

#: A stamp older than its commit by at most this many days is not reported.
#: One day absorbs the ordinary case of writing in the evening and committing
#: after midnight UTC. It is not there to be lenient about the real failure —
#: the backlog this found runs 2 to 15 days behind.
GRACE_DAYS = 1

_DATE = r"(20\d{2}-\d{2}-\d{2})"

#: Contexts in which a date asserts *when this line's work happened*. Anything
#: else — a decision's date quoted in a table, a corpus's publication year — is
#: a citation, not a stamp, and is out of scope.
STAMP_PATTERNS = tuple(re.compile(p) for p in (
    rf"\|\s*\*\*Date\*\*\s*\|\s*{_DATE}",
    rf"\*\*Updated:?\*\*\s*{_DATE}",
    rf"^###\s.*—\s*{_DATE}\s*$",
    rf"^###\s*Amendment[^—]*—\s*{_DATE}",
    rf"(?:[Cc]orrected|[Uu]pdated|[Rr]efreshed|[Ww]idened|[Ss]harpened"
    rf"|[Aa]dded|[Vv]erified|[Rr]e-audited on)\s+{_DATE}",
))

INCLUDE_GLOBS = ("**/*.md", "**/*.py", "**/*.json", "**/*.yml")

EXCLUDE_PARTS = (
    ".git", "__pycache__", ".pytest_cache", "node_modules",
    # Frozen artefacts: an experiment's results.json records the run, and
    # rewriting it would break DEC-016's byte-identical reproduction.
    "results.json",
    # This file quotes the measurement it exists to explain.
    "scripts/check_dates.py",
)


def _files() -> list[pathlib.Path]:
    seen: set[pathlib.Path] = set()
    for pattern in INCLUDE_GLOBS:
        for f in REPO.glob(pattern):
            rel = f.relative_to(REPO).as_posix()
            if any(part in rel for part in EXCLUDE_PARTS):
                continue
            seen.add(f)
    return sorted(seen)


def _blame_dates(path: pathlib.Path) -> dict[int, datetime.date]:
    """line number -> author date of the commit that last touched that line."""
    try:
        out = subprocess.run(
            ["git", "blame", "--line-porcelain", "--", str(path)],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}

    dates: dict[int, datetime.date] = {}
    line_no, stamp = None, None
    for line in out.split("\n"):
        header = re.match(r"^[0-9a-f]{40} \d+ (\d+)", line)
        if header:
            line_no = int(header.group(1))
        elif line.startswith("author-time "):
            stamp = int(line.split()[1])
        elif line.startswith("\t") and line_no is not None and stamp is not None:
            dates[line_no] = datetime.datetime.fromtimestamp(
                stamp, datetime.timezone.utc).date()
    return dates


class NoHistoryError(RuntimeError):
    """Raised when the repository cannot answer "which commit wrote this line".

    Two ways that happens, and they fail differently, which is why both are
    caught explicitly rather than trusted to surface on their own:

      - **git blame returns nothing** (not a repository, git absent). Every file
        gets an empty blame, `drifted()` finds nothing, `0 <= CEILING`, green.
        CI would report the rule enforced while reading no history at all.
      - **a shallow clone** — the default `actions/checkout` depth. Blame still
        *works*, but attributes every line to the one commit present, so every
        stamp older than HEAD looks like drift and the check fails with a number
        that means nothing.

    The first is the more dangerous: it is the eighth instance of the failure
    this repository keeps finding, and it would have been introduced by the
    check written to stop dates drifting.
    """


def _is_shallow() -> bool:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--is-shallow-repository"],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return out == "true"


def drifted() -> list[tuple[str, int, str, str, int, str]]:
    """(file, line, stamped, committed, days_behind, text)"""
    if _is_shallow():
        raise NoHistoryError(
            "this is a shallow clone — git blame would attribute every line to "
            "the single commit present, making the result meaningless. "
            "Use fetch-depth: 0."
        )

    out = []
    scanned = blamed = 0
    for path in _files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        if not any(rx.search(ln) for ln in lines for rx in STAMP_PATTERNS):
            continue

        scanned += 1
        blame = _blame_dates(path)
        if not blame:
            continue
        blamed += 1

        rel = path.relative_to(REPO).as_posix()
        for i, text in enumerate(lines, start=1):
            committed = blame.get(i)
            if committed is None:
                continue  # uncommitted line — nothing to compare against yet
            for rx in STAMP_PATTERNS:
                m = rx.search(text)
                if not m:
                    continue
                try:
                    stamped = datetime.date.fromisoformat(m.group(1))
                except ValueError:
                    continue
                behind = (committed - stamped).days
                if behind > GRACE_DAYS:
                    out.append((rel, i, m.group(1), committed.isoformat(),
                                behind, text.strip()[:90]))
                break  # one stamp per line is enough

    if scanned and not blamed:
        raise NoHistoryError(
            f"{scanned} file(s) carry date stamps and git blame returned "
            f"nothing for any of them — a shallow clone cannot run this check. "
            f"Use fetch-depth: 0."
        )
    return out


def check(show_all: bool) -> int:
    try:
        hits = drifted()
    except NoHistoryError as exc:
        print(f"::error::{exc}")
        return 2
    n = len(hits)

    if show_all:
        for rel, ln, stamped, committed, behind, text in hits:
            print(f"{rel}:{ln}  stamped {stamped}  committed {committed}  "
                  f"({behind}d behind)\n    {text}")

    if n > CEILING:
        # Newest commits first. The excess is whatever was added most recently,
        # and reporting by file order would name an unrelated old line instead —
        # a check that fails while pointing at the wrong place teaches nothing.
        newest = sorted(hits, key=lambda h: h[3], reverse=True)
        print(f"\n{n - CEILING} new drifted date(s) — ceiling is {CEILING}:\n")
        for rel, ln, stamped, committed, behind, text in newest[:n - CEILING]:
            print(f"::error file={rel},line={ln}::date stamped {stamped} but "
                  f"committed {committed} ({behind} days behind)")
            print(f"  {rel}:{ln}\n    {text}\n")
        print("Stamp the date the work was actually done, or lower nothing — "
              "the ceiling only moves down.")
        return 1

    slack = CEILING - n
    note = f" — ceiling can drop to {n}" if slack else ""
    print(f"OK — {n} drifted date(s), ceiling {CEILING}{note}")
    if n and not show_all:
        print("     run with --list to see the backlog")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true",
                    help="print every drifted line, not just new ones")
    args = ap.parse_args()
    return check(args.list)


if __name__ == "__main__":
    sys.exit(main())
