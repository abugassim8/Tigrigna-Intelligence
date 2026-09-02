#!/usr/bin/env python3
"""Fetch the HornMT English–Tigrinya anchor, and refuse it if it has changed.

HornMT is the first **cleanly-licensed** parallel corpus this project has:
2,030 human-translated news snippets, CC-BY-4.0, multi-way parallel across six
Horn-of-Africa languages. It supersedes the 30-sentence FLORES sample as the
evaluation anchor — see `../../../docs/benchmarks/datasets.md`.

Why a fetcher and not just committed files
------------------------------------------
Both. The files are committed so evaluation works with no network — this
environment's egress is partial and `huggingface.co` is unreachable — and this
script exists so the committed copy can be **proved** to be the upstream one.
It re-downloads, compares SHA-256, and fails loudly on any drift. That is
DEC-016's reproducibility rule applied to data we did not produce.

The alignment trap this checks for
----------------------------------
A parallel corpus read as two independent files is only parallel if both sides
split into the same number of lines. `str.splitlines()` splits on more than
`\\n` — U+2028 LINE SEPARATOR, U+0085 NEL, \\x0b, \\x0c — so one stray separator
on one side silently shifts every later pair against its translation, and the
corpus goes on looking fine. The EnTiMT project hit exactly this in raw NLLB
bitext (84 U+2028 in English, 4 in Tigrinya).

**Measured for HornMT: it does not happen here** — `split("\\n")` and
`splitlines()` both give 2,030 on both sides, and no exotic separator is
present. Recorded as a negative result (P-13) so nobody re-derives it, and
checked on every fetch anyway, because it is one comparison and the failure is
invisible.

Usage:
    python3 fetch.py            # verify the committed copy against upstream
    python3 fetch.py --write    # refresh the committed copy (then commit it)
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent

BASE = "https://raw.githubusercontent.com/asmelashteka/HornMT/main/data"

#: Upstream SHA-256, recorded 2026-09-01. A mismatch is not automatically wrong
#: — upstream may have legitimately corrected the corpus — but it must be a
#: decision, not a silent change under an anchor everything else is scored on.
EXPECTED = {
    "eng.txt": "40c4dab6ac6bb0e3a3d49721e116d326ca95c44e640c42f8caca4593e47db584",
    "tir.txt": "017a35e3fad1f16c670cbc6b11967280ed5b39fd87d6c6722633a87136dca2c3",
}

EXPECTED_PAIRS = 2030

#: Everything `str.splitlines()` treats as a line break and `split("\n")` does
#: not. Any of these in a parallel file is an alignment hazard.
EXOTIC_BREAKS = (" ", " ", "\r", "\x0b", "\x0c", "\x85")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _lines(text: str) -> list[str]:
    """Split the way the corpus is actually delimited: on `\\n`, nothing else."""
    out = text.split("\n")
    if out and out[-1] == "":
        out.pop()
    return out


def check_alignment(sides: dict[str, str]) -> list[str]:
    """Return a list of problems; empty means the two sides are safely parallel."""
    problems: list[str] = []
    counts = {}
    for name, text in sides.items():
        exotic = {c: text.count(c) for c in EXOTIC_BREAKS if c in text}
        if exotic:
            named = ", ".join(f"U+{ord(c):04X}x{n}" for c, n in exotic.items())
            problems.append(f"{name}: exotic line separators present ({named}) "
                            f"— splitlines() would desync this file")
        naive, real = len(text.splitlines()), len(_lines(text))
        if naive != real:
            problems.append(f"{name}: splitlines()={naive} but split('\\n')={real}")
        counts[name] = real
        blank = sum(1 for ln in _lines(text) if not ln.strip())
        if blank:
            problems.append(f"{name}: {blank} blank line(s) — alignment is by "
                            f"line index, so a blank is a lost pair")

    if len(set(counts.values())) != 1:
        problems.append(f"line counts differ between sides: {counts}")
    elif next(iter(counts.values())) != EXPECTED_PAIRS:
        problems.append(f"expected {EXPECTED_PAIRS} pairs, found "
                        f"{next(iter(counts.values()))}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true",
                    help="overwrite the committed copy with what upstream serves")
    args = ap.parse_args()

    sides, failed = {}, False
    for filename, expected in EXPECTED.items():
        url = f"{BASE}/{filename}"
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                raw = response.read()
        except Exception as exc:                       # noqa: BLE001
            local = HERE / filename
            if local.is_file():
                print(f"{filename}: upstream unreachable ({exc}); "
                      f"verifying the committed copy instead")
                raw = local.read_bytes()
            else:
                print(f"::error::{filename}: unreachable and not committed — {exc}")
                return 2

        got = _sha(raw)
        if got != expected:
            print(f"::error::{filename}: SHA-256 {got}\n"
                  f"                 expected {expected}\n"
                  f"  Upstream changed, or the committed copy drifted. Decide "
                  f"which before re-recording — every score is relative to this.")
            failed = True
        else:
            print(f"{filename}: sha256 matches ({len(raw)} bytes)")

        sides[filename] = raw.decode("utf-8")
        if args.write:
            (HERE / filename).write_bytes(raw)

    problems = check_alignment(sides)
    for p in problems:
        print(f"::error::{p}")
    if not problems:
        print(f"alignment: {EXPECTED_PAIRS} pairs, both sides, no exotic "
              f"separators — safely parallel")

    return 1 if (failed or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
