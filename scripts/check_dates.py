#!/usr/bin/env python3
"""Fail when work is stamped with an older date than the commit that made it.

The rule
--------
**The commit date wins** (A-17). When a document says it was written on one day
and the commit carrying that line landed on another, the commit is right — it is
the only one of the two that cannot be typed wrong.

What this was written for
-------------------------
On 2026-08-24 an audit of the plan of record found that **every document date
written between 2026-08-21 and 2026-08-23 said `2026-08-19`** — six commits of
work stamped with the previous session's date. Measuring it found the habit was
older and wider: **71 stamps across 34 files** were earlier than the commit
carrying them, and the gap reached **15 days**. Ten of the 16 summaries and
eleven reports were dated 2026-08-03 and committed on the 17th and 18th.

That mattered here more than it would elsewhere. This project's method is that
the record is true and corrections are dated, and several arguments are computed
from elapsed time. Recomputing them found one wrong by a factor of six,
independently of the drift: *"DEC-008 spent three months as policy with no
mechanism"* appeared in eleven places, and the real interval is **15 days** —
three months was never possible in a repository whose first commit is
2026-07-29.

**All 71 were corrected on 2026-08-24 and the ceiling is now 0.**

Why the correction does not trip this check
-------------------------------------------
Blame attributes a line to whatever commit last touched it, so the commit that
*fixed* 257 dates would otherwise look like the commit that wrote every one of
them — and each correctly restored stamp would read as fresh drift. The
correction is listed in `.git-blame-ignore-revs`, which blame skips, so each
line reports the commit that actually wrote it. Nothing is exempted by content:
a mechanical commit is made invisible to blame, and that is all.

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

**Known limit: it cannot tell a stamp from a quotation of one.** Prose that
discusses a stamp — a changelog entry quoting the line it corrected — reads as
a stale stamp and fails. That is deliberate: `check_figures.py` solved the same
problem with a marker vocabulary, and that vocabulary made its checks unable to
fail **twice**. A false positive you reword around is cheaper than a suppression
path that silently covers real drift. If this becomes frequent, fix it by
narrowing the stamp patterns, not by adding an escape hatch.

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

#: Maximum drifted stamps tolerated. The backlog of 71 was corrected on
#: 2026-08-24 (A-17), so this is 0 and every new drift fails. Never raise it —
#: a ceiling above the true count is an allowlist, and an allowlist that covers
#: everything is a check that cannot fail.
CEILING = 0

#: A stamp older than its commit by at most this many days is not reported.
#: One day absorbs the ordinary case of writing in the evening and committing
#: after midnight UTC. It is not there to be lenient about the real failure —
#: the backlog this found ran 2 to 15 days behind.
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


#: Commits that only changed how something is written. Blame skips them, so a
#: mechanical pass does not claim authorship of every line it touched.
#:
#: Without this the check eats its own tail: the commit that CORRECTED 257 dates
#: becomes, to blame, the commit that wrote every one of them — and every
#: correctly restored stamp reads as fresh drift.
IGNORE_REVS = REPO / ".git-blame-ignore-revs"


def _blame_dates(path: pathlib.Path) -> dict[int, datetime.date]:
    """line number -> author date of the commit that last wrote that line."""
    cmd = ["git", "blame", "--line-porcelain"]
    if IGNORE_REVS.is_file():
        cmd += ["--ignore-revs-file", str(IGNORE_REVS)]
    try:
        out = subprocess.run(
            cmd + ["--", str(path)],
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
            # Every stamp on the line, not just the first. A line that accrues
            # corrections carries several — "Corrected 2026-08-22 … Updated
            # 2026-09-02" — and a table row cannot be split across lines to
            # separate them. It is correctly dated if ANY stamp matches the
            # commit that wrote it; the older ones are that line's own history.
            # Found when this check flagged an edit made to satisfy it.
            stamps: list[datetime.date] = []
            for rx in STAMP_PATTERNS:
                for m in rx.finditer(text):
                    try:
                        stamps.append(datetime.date.fromisoformat(m.group(1)))
                    except ValueError:
                        continue
            if not stamps:
                continue
            if any((committed - s).days <= GRACE_DAYS for s in stamps):
                continue
            newest = max(stamps)
            out.append((rel, i, newest.isoformat(), committed.isoformat(),
                        (committed - newest).days, text.strip()[:90]))

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
        # With CEILING at 0 this is simply every hit, newest first.
        newest = sorted(hits, key=lambda h: h[3], reverse=True)
        print(f"\n{n - CEILING} new drifted date(s) — ceiling is {CEILING}:\n")
        for rel, ln, stamped, committed, behind, text in newest[:n - CEILING]:
            print(f"::error file={rel},line={ln}::date stamped {stamped} but "
                  f"committed {committed} ({behind} days behind)")
            print(f"  {rel}:{ln}\n    {text}\n")
        print("A-17: the commit date wins. Stamp the day the work lands, or — "
              "if this was a mechanical rewrite that changed no meaning — add "
              "the commit to .git-blame-ignore-revs.")
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
