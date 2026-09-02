#!/usr/bin/env python3
"""Fetch the TICO-19 English–Tigrinya anchor, and refuse it if it has changed.

TICO-19 is the **variety-labelled** anchor. 3,071 English segments (971 dev,
2,100 test) translated into Tigrinya three separate times, and two of those
three carry a declared regional standard at source: `ti-ER` and `ti-ET`. No
other corpus this project has found labels the variety at all — DEC-010 has had
to hold every Tigrinya corpus at `unknown` because nobody upstream said.

Why a fetcher and not just committed files
------------------------------------------
Both, for the same reason as HornMT: the derived files are committed so
evaluation runs with no network, and this script exists so the committed copy
can be **proved** to be a faithful derivation of upstream. Here it has more work
to do than HornMT's, because upstream is a ZIP of TSVs and the committed files
are line-per-segment text. The derivation is therefore part of the artefact and
is re-run and compared byte-for-byte, not just downloaded and hashed.

What the derivation does, exactly
---------------------------------
For each of the six upstream TSVs: read column `sourceString` / `targetString`,
`str.strip()` each value, and write one segment per line. Stripping is the only
transformation, and it is not cosmetic — the `ti_ET` side pads every segment
with a leading and trailing space, so without it the ET file would differ from
the other two on every single line for no linguistic reason.

Three references, one source
----------------------------
The anchor is **3,071 segments with 3 references**, not 9,213 pairs. All three
Tigrinya files translate the identical English, which this script asserts rather
than assumes: if upstream ever ships a variant with different source text, the
multi-reference framing breaks and this fails instead of quietly inflating the
corpus by 3x.

The column name changes between files
-------------------------------------
`dev.en-ti.tsv` and `test.en-ti.tsv` spell the translator column
`translator_ID`; the four variety files spell it `translator_id`. Any loader
that hardcodes one spelling reads five files and crashes on the sixth, or worse,
silently gets `None`. Not used here, but recorded because it is the kind of
thing that costs an afternoon.

The alignment trap this checks for
----------------------------------
A parallel corpus read as independent files is only parallel if every side
splits into the same number of lines. `str.splitlines()` splits on more than
`\\n` — U+2028 LINE SEPARATOR, U+0085 NEL, \\x0b, \\x0c — so one stray separator
inside one segment silently shifts every later pair against its translation and
the corpus goes on looking fine. Deriving from TSV does not make this safe: a
separator living inside a field survives into the derived line and desyncs it.

Usage:
    python3 fetch.py            # verify the committed copy against upstream
    python3 fetch.py --write    # refresh the committed copy (then commit it)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import pathlib
import sys
import urllib.request
import zipfile

HERE = pathlib.Path(__file__).resolve().parent

#: The GitHub Pages repository behind tico-19.github.io, which is itself
#: egress-blocked from this environment. raw.githubusercontent.com serves the
#: same bytes and is reachable — see docs/research/RESEARCH_ACCESS.md.
ARCHIVE_URL = ("https://raw.githubusercontent.com/tico-19/tico-19.github.io"
               "/master/data/tico19-testset.zip")

#: SHA-256 of the archive, recorded 2026-09-02. A mismatch is not automatically
#: wrong — upstream may have corrected the corpus — but it must be a decision,
#: not a silent change under an anchor everything else is scored on.
ARCHIVE_SHA = "0e82fc7ceaa877606c8934f32ead185716c9d2c54b3818f2a7ae655f5e7a08d8"

#: Members we take, and their digests. Hashing the members and not only the
#: archive matters: a ZIP can be rebuilt with different compression or member
#: order and change digest while the contents are identical, and it can also
#: keep a stable name while a member changes underneath.
MEMBERS = {
    "tico19-testset/dev/dev.en-ti.tsv":
        "a1397c4986a918def1536c66440c569cf9ea44c12bc7512bad1c7dbadab70263",
    "tico19-testset/dev/dev.en-ti_ER.tsv":
        "9a63966bc441eab956bfe1d17f3315b61e811e2351013e72bc53e2a569f72702",
    "tico19-testset/dev/dev.en-ti_ET.tsv":
        "4a1fe89c7cfaf6a66a8abe253c380daa3df0d3ba4d0076c28f364ef95dd65132",
    "tico19-testset/test/test.en-ti.tsv":
        "a855282ff9afdca39c6da79c0187b785c0d84a3675ada9dba79fcd1f8951920a",
    "tico19-testset/test/test.en-ti_ER.tsv":
        "6ab24d67231f250413ecc3e16503ee95ad26709b99b858e4f7958e382af3e545",
    "tico19-testset/test/test.en-ti_ET.tsv":
        "064296be2b60296fe7f5fd8720ac180eae62eff21cd6d19fd31f6d80cf73cf90",
}

#: split -> (upstream member stem, expected segment count)
SPLITS = {"dev": 971, "test": 2100}

#: derived-file suffix -> upstream variant tag
VARIANTS = {"tir_ti": "", "tir_er": "_ER", "tir_et": "_ET"}

#: Everything `str.splitlines()` treats as a line break and `split("\n")` does
#: not. Any of these in a derived file is an alignment hazard.
EXOTIC_BREAKS = (" ", " ", "\r", "\x0b", "\x0c", "\x85")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _lines(text: str) -> list[str]:
    """Split the way the corpus is actually delimited: on `\\n`, nothing else."""
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out


def _rows(raw: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8")), delimiter="\t"))


def derive(members: dict[str, bytes]) -> tuple[dict[str, str], list[str]]:
    """Turn the six upstream TSVs into eight line-per-segment files.

    Returns (files, problems). A non-empty `problems` means the derivation is
    not safe to commit, not that it merely looks untidy.
    """
    files: dict[str, str] = {}
    problems: list[str] = []

    for split, expected in SPLITS.items():
        sources: dict[str, list[str]] = {}
        ids: dict[str, list[str]] = {}

        for suffix, tag in VARIANTS.items():
            name = f"tico19-testset/{split}/{split}.en-ti{tag}.tsv"
            rows = _rows(members[name])
            if len(rows) != expected:
                problems.append(f"{name}: {len(rows)} rows, expected {expected}")
                continue
            sources[suffix] = [r["sourceString"].strip() for r in rows]
            ids[suffix] = [r["stringID"] for r in rows]
            files[f"{split}.{suffix}.txt"] = "".join(
                r["targetString"].strip() + "\n" for r in rows)

        if len(sources) != len(VARIANTS):
            continue

        # The multi-reference claim, asserted rather than assumed.
        ref = VARIANTS and next(iter(sources))
        for suffix in sources:
            if sources[suffix] != sources[ref]:
                n = sum(1 for a, b in zip(sources[suffix], sources[ref]) if a != b)
                problems.append(
                    f"{split}: English differs between {ref} and {suffix} on {n} "
                    f"segment(s) — these are not three references over one source")
            if ids[suffix] != ids[ref]:
                problems.append(f"{split}: stringID order differs {ref} vs {suffix}")

        files[f"{split}.eng.txt"] = "".join(s + "\n" for s in sources[ref])

    return files, problems


def check_alignment(files: dict[str, str]) -> list[str]:
    """Return a list of problems; empty means every side is safely parallel."""
    problems: list[str] = []
    counts: dict[str, dict[str, int]] = {"dev": {}, "test": {}}

    for name, text in sorted(files.items()):
        exotic = {c: text.count(c) for c in EXOTIC_BREAKS if c in text}
        if exotic:
            named = ", ".join(f"U+{ord(c):04X}x{n}" for c, n in exotic.items())
            problems.append(f"{name}: exotic line separators present ({named}) "
                            f"— splitlines() would desync this file")
        naive, real = len(text.splitlines()), len(_lines(text))
        if naive != real:
            problems.append(f"{name}: splitlines()={naive} but split('\\n')={real}")
        blank = sum(1 for ln in _lines(text) if not ln.strip())
        if blank:
            problems.append(f"{name}: {blank} blank line(s) — alignment is by "
                            f"line index, so a blank is a lost pair")
        counts[name.split(".")[0]][name] = real

    for split, expected in SPLITS.items():
        got = counts[split]
        if len(set(got.values())) != 1:
            problems.append(f"{split}: line counts differ between sides: {got}")
        elif next(iter(got.values())) != expected:
            problems.append(f"{split}: expected {expected} segments, found "
                            f"{next(iter(got.values()))}")
    return problems


def _archive() -> bytes | None:
    """Upstream bytes, or None if upstream is unreachable."""
    try:
        with urllib.request.urlopen(ARCHIVE_URL, timeout=120) as response:
            return response.read()
    except Exception as exc:                               # noqa: BLE001
        print(f"upstream unreachable ({exc}); verifying the committed copy instead")
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true",
                    help="overwrite the committed copy with what upstream serves")
    args = ap.parse_args()

    failed = False
    raw = _archive()

    if raw is None:
        committed = sorted(HERE.glob("*.txt"))
        if not committed:
            print("::error::upstream unreachable and nothing is committed")
            return 2
        files = {p.name: p.read_text(encoding="utf-8") for p in committed}
        if args.write:
            print("::error::--write needs upstream; refusing to rewrite from itself")
            return 2
    else:
        got = _sha(raw)
        if got != ARCHIVE_SHA:
            print(f"::error::archive sha256 {got}\n"
                  f"                 expected {ARCHIVE_SHA}\n"
                  f"  Upstream changed, or the recorded digest is stale. Decide "
                  f"which before re-recording — every score is relative to this.")
            failed = True
        else:
            print(f"archive: sha256 matches ({len(raw)} bytes)")

        archive = zipfile.ZipFile(io.BytesIO(raw))
        present = set(archive.namelist())
        members: dict[str, bytes] = {}
        for name, expected in MEMBERS.items():
            if name not in present:
                print(f"::error::{name}: not in the archive")
                failed = True
                continue
            data = archive.read(name)
            digest = _sha(data)
            if digest != expected:
                print(f"::error::{name}: sha256 {digest}, expected {expected}")
                failed = True
            members[name] = data
        if len(members) != len(MEMBERS):
            return 2
        print(f"members: {len(members)} Tigrinya TSVs verified")

        files, derivation = derive(members)
        for p in derivation:
            print(f"::error::{p}")
        failed = failed or bool(derivation)
        if not derivation:
            print(f"derivation: 3 references over one English source, "
                  f"{sum(SPLITS.values())} segments, asserted identical")

        # The committed copy must be exactly what the derivation produces.
        for name, text in sorted(files.items()):
            local = HERE / name
            if args.write:
                local.write_text(text, encoding="utf-8")
            elif not local.is_file():
                print(f"::error::{name}: derived from upstream but not committed")
                failed = True
            elif local.read_text(encoding="utf-8") != text:
                print(f"::error::{name}: committed copy differs from the "
                      f"derivation of upstream")
                failed = True

    problems = check_alignment(files)
    for p in problems:
        print(f"::error::{p}")
    if not problems:
        print(f"alignment: {SPLITS['dev']} dev + {SPLITS['test']} test, all "
              f"four sides, no exotic separators — safely parallel")

    return 1 if (failed or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
