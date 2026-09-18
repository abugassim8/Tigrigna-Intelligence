#!/usr/bin/env python3
"""Fail when this repository documents a command that cannot run.

Why this exists
---------------
**Two of the commands this repository printed did not work, and one of them was
printed as an error message.**

- ``python -c "import hm; hm.download('ti')"`` appeared in five places,
  including the text shown to a user at the exact moment HornMorpho's language
  data is missing. ``hm.download()`` rejects ``'ti'`` — only the canonical
  ``'t'`` is accepted (**A-20**). It was never executed here, because this
  sandbox cannot reach the host that serves it.
- A migration guide told a user to pass ``--verify`` to
  ``data/anchors/tico19/fetch.py``. **There is no such flag.** Both
  ``fetch.py`` scripts define only ``--write``; bare invocation *is* the
  verify mode.

⚠️ Note how those two examples are written: as a path and a flag, never spelled
out as a runnable command line. This checker holds its own prose to the rule it
enforces, and the alternative — an "ignore this one" marker — is refused on
purpose. Marker vocabularies have silently disabled four checks in this
repository already.

The repository checks figures, dates, derived counts and planted behaviour. It
had never checked that **the instructions it prints can be executed** — so
every other claim was enforced and the ones a human follows by hand were not.

What this checks, and what it deliberately does not
---------------------------------------------------
⚠️ It does **not** run anything. A check that executed documented commands
would need the network and a 159 MB download, would be slow and flaky, and
would be switched off within a week — the failure mode **DEC-008** exists to
prevent. Instead it checks the two things most likely to be wrong and cheapest
to verify: **a flag name** and **a script path**.

Flags are read with ``ast``, never by importing, so no module-level code runs.
Importing ``screen_dataset`` or an experiment's ``run.py`` to inspect its parser
would execute it, and a checker with side effects is worse than the defect.

``**kwargs``-style parsers defeat static reading; a script whose ``main`` builds
arguments dynamically is reported as unreadable rather than silently passing.

Usage:
    python3 scripts/check_commands.py
    python3 scripts/check_commands.py --list    # print every command found
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Where instructions live: prose, script docstrings, and CI.
INCLUDE_GLOBS = ("**/*.md", "**/*.py", ".github/workflows/*.yml")

#: Not searched — the same exclusions, and for the same stated reason, as
#: `check_figures.py`, which quotes retired figures for exactly this purpose.
EXCLUDE_PARTS = (
    ".git/", ".venv/", "__pycache__/", ".pytest_cache/", "node_modules/",
    # The plant suite asserts this checker can still fail, so it necessarily
    # spells out commands that do not work. The exclusion is safe because every
    # plant's expected exit status is asserted: a plant that stopped being
    # detected fails the suite rather than passing quietly.
    "scripts/tests/",
)

#: An interpreter, a ``.py`` path, then one or more ``--flags``. The
#: interpreter spelling varies across documents written at different times, so
#: python, python3 and py are all accepted.
COMMAND = re.compile(
    r"(?:python3?|py)\s+([\w./\\-]+\.py)((?:\s+--[\w-]+)+)")

FLAG = re.compile(r"--[\w-]+")

#: Always available, never declared by a script's own parser.
BUILTIN_FLAGS = frozenset({"--help"})

#: Flags belonging to the *interpreter* or to a tool the line pipes into, not to
#: the script. Kept explicit and tiny; anything else must be declared.
NOT_SCRIPT_FLAGS = frozenset({"--version"})


def _files() -> list[pathlib.Path]:
    seen: set[pathlib.Path] = set()
    for pattern in INCLUDE_GLOBS:
        for f in REPO.glob(pattern):
            rel = f.relative_to(REPO).as_posix()
            if any(part in rel + "/" for part in EXCLUDE_PARTS):
                continue
            if f.is_file():
                seen.add(f)
    return sorted(seen)


def declared_flags(script: pathlib.Path) -> set[str] | None:
    """Every ``--flag`` the script passes to ``add_argument``.

    Returns ``None`` when the source cannot be read statically, so the caller
    can say "unreadable" instead of "no flags declared" — those mean opposite
    things and conflating them would make this check pass on anything.
    """
    try:
        tree = ast.parse(script.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None

    flags: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Attribute) and fn.attr == "add_argument"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if arg.value.startswith("--"):
                    flags.add(arg.value)
    return flags


def _resolve(doc: pathlib.Path, script: str) -> pathlib.Path | None:
    """A documented path is relative to the document, or to the repository.

    ``experiments/010-.../README.md`` names ``run.py`` bare and means the one
    beside it; ``CHANGELOG.md`` spells paths from the repository root. Both are
    legitimate, so both are tried.
    """
    for base in (doc.parent, REPO):
        candidate = (base / script).resolve()
        try:
            candidate.relative_to(REPO)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


def check(list_only: bool = False) -> int:
    problems: list[str] = []
    found = 0

    for doc in _files():
        try:
            text = doc.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for match in COMMAND.finditer(text):
            script_str, flag_blob = match.group(1), match.group(2)
            flags = {f for f in FLAG.findall(flag_blob)
                     if f not in BUILTIN_FLAGS and f not in NOT_SCRIPT_FLAGS}
            if not flags:
                continue
            found += 1
            rel = doc.relative_to(REPO).as_posix()
            line = text[:match.start()].count("\n") + 1

            if list_only:
                print(f"  {rel}:{line}  {script_str} {' '.join(sorted(flags))}")
                continue

            script = _resolve(doc, script_str)
            if script is None:
                # A path that resolves nowhere is a broken instruction too.
                problems.append(
                    f"::error file={rel},line={line}::documents "
                    f"`{script_str}`, which does not exist relative to "
                    f"{doc.parent.relative_to(REPO).as_posix() or '.'} or to "
                    f"the repository root")
                continue

            declared = declared_flags(script)
            if declared is None:
                problems.append(
                    f"::error file={rel},line={line}::"
                    f"{script.relative_to(REPO).as_posix()} could not be read "
                    f"statically, so its flags cannot be checked")
                continue

            for flag in sorted(flags - declared):
                problems.append(
                    f"::error file={rel},line={line}::`{script_str} {flag}` — "
                    f"{script.relative_to(REPO).as_posix()} declares no "
                    f"{flag}. It accepts: "
                    f"{', '.join(sorted(declared)) or '(no flags)'}")

    if list_only:
        print(f"\n{found} documented command(s) with flags")
        return 0

    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} documented command(s) cannot run as written")
        return 1

    print(f"OK — {found} documented command(s) checked; every flag exists")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true",
                    help="print every documented command instead of checking")
    args = ap.parse_args(argv)
    return check(args.list)


if __name__ == "__main__":
    # ⚠️ Windows writes to a pipe or a redirect with the locale codec
    # (cp1252), not the console's. Without this, printing `⚠️` or `—`
    # raises UnicodeEncodeError — including while printing a traceback.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
