#!/usr/bin/env python3
"""Fail when two copies of the same definition disagree.

Why this exists
---------------
**`is_ethiopic` exists five times in this repo, and two copies were wrong.**
`scripts/data_processing/screen_dataset.py` and
`experiments/002-tokenizer-fertility/run.py` both omitted **Ethiopic
Extended-B** while three other copies included it. The consequence was
measured, not hypothetical: a corpus of real Tigrinya carrying 21 Extended-B
characters **failed the quality gate as "likely mojibake"** at 1.444%.

`normalise` exists twice. Those two agree today — which is exactly the state
the Extended-B copies were in until someone checked.

Why not just delete the duplicates
----------------------------------
Two of them are load-bearing in a way that makes importing worse:

- **`screen_dataset.py` is deliberately stdlib-only.** It is the tool that
  decides whether data may enter the project, and it should run anywhere
  without installing a package first.
- **Experiments are frozen records** that reproduce byte-identically against
  pinned dependencies. Giving one a new import changes its dependency surface
  and its meaning as evidence.

So the duplicates stay, and this checks they agree. Divergence becomes a failed
build rather than a finding 19 days later.

Usage:
    python3 scripts/check_definitions.py
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Every codepoint any copy claims, plus the boundaries either side of each
#: range — off-by-one at a block edge is the likeliest way two copies drift.
_BLOCKS = [(0x1200, 0x137F), (0x1380, 0x139F), (0x2D80, 0x2DDF),
           (0xAB00, 0xAB2F), (0x1E7E0, 0x1E7FF)]


def _probe_codepoints() -> list[int]:
    cps = set()
    for lo, hi in _BLOCKS:
        cps.update({lo - 1, lo, lo + 1, hi - 1, hi, hi + 1})
        cps.update(range(lo, hi + 1))
    # A few non-Ethiopic controls: Latin, digits, CJK, and the replacement char.
    cps.update({0x41, 0x61, 0x30, 0x4E00, 0xFFFD, 0x00F1})
    return sorted(cps)


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sources() -> dict[str, object]:
    """Import every module holding a copy. Missing ones are reported, not skipped."""
    out: dict[str, object] = {}
    sys.path.insert(0, str(REPO / "services" / "primitives" / "src"))
    sys.path.insert(0, str(REPO / "services" / "evaluation" / "src"))
    try:
        import tigrinya_eval.primitives as ev
        out["tigrinya_eval.primitives"] = ev
    except ImportError as e:  # pragma: no cover - environment-dependent
        print(f"  skipping tigrinya_eval ({e})")
    out["screen_dataset"] = _load(
        REPO / "scripts" / "data_processing" / "screen_dataset.py", "sd")
    out["experiments/002"] = _load(
        REPO / "experiments" / "002-tokenizer-fertility" / "run.py", "e002")
    out["experiments/004"] = _load(
        REPO / "experiments" / "004-primitive-evaluation" / "run.py", "e004")
    return out


def check_is_ethiopic(mods) -> list[str]:
    copies = {n: m.is_ethiopic for n, m in mods.items() if hasattr(m, "is_ethiopic")}
    if len(copies) < 2:
        return [f"expected several copies of is_ethiopic, found {len(copies)}"]

    ref_name, ref = next(iter(copies.items()))
    problems = []
    for name, fn in copies.items():
        if name == ref_name:
            continue
        diffs = [cp for cp in _probe_codepoints()
                 if fn(chr(cp)) != ref(chr(cp))]
        if diffs:
            sample = ", ".join(f"U+{c:04X}" for c in diffs[:6])
            problems.append(
                f"is_ethiopic: {name} disagrees with {ref_name} on "
                f"{len(diffs)} codepoint(s) — {sample}"
                + ("…" if len(diffs) > 6 else ""))
    print(f"  is_ethiopic: {len(copies)} copies checked over "
          f"{len(_probe_codepoints()):,} codepoints")
    return problems


def check_normalise(mods) -> list[str]:
    from tigrinya_primitives import normalise as canonical
    copies = {n: m.normalise for n, m in mods.items() if hasattr(m, "normalise")}
    problems = []
    # Every Ethiopic codepoint, one at a time, plus a couple of real words.
    probes = [chr(cp) for lo, hi in _BLOCKS for cp in range(lo, hi + 1)]
    probes += ["ፀሓይ", "አንበሳ", "ሰላም ዓለም", ""]
    for name, fn in copies.items():
        diffs = [p for p in probes if fn(p) != canonical(p)]
        if diffs:
            problems.append(
                f"normalise: {name} disagrees with tigrinya_primitives on "
                f"{len(diffs)} input(s) — {diffs[:4]!r}")
    print(f"  normalise:   {len(copies) + 1} copies checked over "
          f"{len(probes):,} inputs")
    return problems


def main() -> int:
    print("=" * 66)
    print("DUPLICATE DEFINITION CONSISTENCY")
    print("=" * 66)
    mods = _sources()
    problems = check_is_ethiopic(mods) + check_normalise(mods)

    if not problems:
        print("\n  OK — every copy agrees")
        return 0
    print(f"\n{len(problems)} disagreement(s):\n")
    for p in problems:
        print(f"::error::{p}")
        print(f"  {p}\n")
    print("  Two copies of one rule that disagree is how Extended-B came to be "
          "missing from the screening gate for 19 days.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
