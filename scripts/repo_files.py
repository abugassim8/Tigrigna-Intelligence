"""Which files belong to *this repository* — not to whatever sits beside them.

Why this exists
---------------
`check_figures.py` and `check_dates.py` globbed `**/*.py` from the repository
root with no exclusions. In CI and in the assistant's sandbox that is harmless,
because neither has a virtualenv inside the tree. On the owner's machine
`.venv/` holds torch and transformers — tens of thousands of Python files — and
`check_figures.py` **timed out after 180 seconds** reading them.

⚠️ **Slowness was the smaller half.** A retired figure or an undefined goal id
quoted in a third-party docstring would have been reported as a stale claim in
this repository. A checker that fires on correct input is one that gets switched
off (DEC-008), and this one was about to.

⚠️ **Asking git is the fix, not a longer exclusion list.** A denylist answers
"is it `.venv`?" when the question is "is it ours?", and the next directory to
appear beside the source — `models/`, `node_modules/`, a sibling clone — would
need its own entry and would not get one until it broke something.
"""

from __future__ import annotations

import fnmatch
import pathlib
import subprocess

#: Used only when git cannot answer — an unpacked tarball, or a clone so broken
#: that `git ls-files` fails. Deliberately short: it is a fallback, not the
#: mechanism, and a long list here would invite trusting it.
FALLBACK_EXCLUDE = (".git/", ".venv/", "venv/", "env/", "site-packages/",
                    "node_modules/", "__pycache__/", ".pytest_cache/",
                    ".mypy_cache/", ".ruff_cache/", "models/")


def tracked_files(repo: pathlib.Path, patterns) -> list[pathlib.Path]:
    """Files git tracks in `repo` matching any of `patterns`, sorted.

    Falls back to a filesystem walk with `FALLBACK_EXCLUDE` when git cannot
    answer. ⚠️ The fallback is **reported by returning it**, not by raising:
    a checker that refused to run outside a git clone would be worse than one
    that scans a little too much.
    """
    files = _from_git(repo)
    if files is None:
        files = _from_walk(repo, patterns)
    else:
        files = [f for f in files
                 if any(fnmatch.fnmatch(f.name, _tail(p)) for p in patterns)]
    return sorted(set(files))


def _tail(pattern: str) -> str:
    """`**/*.md` -> `*.md`; git already handled the directory part."""
    return pattern.rsplit("/", 1)[-1]


def _from_git(repo: pathlib.Path) -> list[pathlib.Path] | None:
    try:
        r = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                           capture_output=True, timeout=60)
    except Exception:                                     # noqa: BLE001
        return None
    if r.returncode != 0:
        return None
    names = [n for n in r.stdout.decode("utf-8", "replace").split("\0") if n]
    # ⚠️ `ls-files` lists deleted-but-staged paths too; keep only what exists,
    # or a checker would crash reading a file that is not there.
    return [repo / n for n in names if (repo / n).is_file()]


def _from_walk(repo: pathlib.Path, patterns) -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for pattern in patterns:
        for f in repo.glob(pattern):
            rel = f.relative_to(repo).as_posix()
            if any(part in rel for part in FALLBACK_EXCLUDE):
                continue
            found.append(f)
    return found
