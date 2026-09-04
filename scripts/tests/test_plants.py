#!/usr/bin/env python3
"""Plant known failures and assert the audit tooling reports them.

Nine checks in this repository have been found that **could not fail** — five of
them inside the audit tooling itself. Every one was written in good faith,
reviewed, and passing; none was caught by reading the code. They were caught by
planting a failure and watching nothing happen.

So the planting is not a one-off diagnostic. It is the test, and it runs in CI.

Each case below is a (text, expected exit status) pair. A case expecting **1**
proves the checker can fail; a case expecting **0** proves it has not become so
strict it rejects legitimate text. Both directions matter: a check that fires on
everything gets switched off, and a switched-off check is the failure mode
DEC-008 exists to prevent.

Usage:
    python3 scripts/tests/test_plants.py        # exit 1 if any plant misbehaves
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------
# screen_dataset.py — the Ge'ez mojibake gate
#
# The rule under test is context-sensitive: an accented Latin letter is
# corruption when it adjoins an Ethiopic *syllable* and a borrowed proper noun
# when it does not. Both halves need a plant, because a rule that called
# everything corruption would block TICO-19 and a rule that called nothing
# corruption would pass the known-corrupted sample.
# --------------------------------------------------------------------------

SCREEN = REPO / "scripts" / "data_processing" / "screen_dataset.py"
EVAL_SET = REPO / "experiments/003-metric-validity/data/flores_ti.txt"
CLEAN = REPO / "experiments/002-tokenizer-fertility/corpus/tlt_000_clean.txt"

SCREEN_PLANTS = [
    # (label, text inserted mid-word between two Ge'ez syllables, expected exit)
    ("accented Latin letter between Ge'ez syllables", "ñ", 1),
    ("U+FFFD replacement character", "�", 1),
    ("U+0085 C1 control", "", 1),
    ("U+009D C1 control", "", 1),
    ("borrowed proper noun (Erdoğan)", " Erdoğan ", 0),
    ("multiplication sign in arithmetic (4×109)", " 4×109 ", 0),
    ("untouched control", "", 0),
]


def run_screen_plants() -> list[str]:
    text = CLEAN.read_text(encoding="utf-8")
    cut = text.index("ን")            # a Ge'ez syllable, mid-word
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        corpus = pathlib.Path(tmp) / "corpus.txt"
        for label, plant, expect in SCREEN_PLANTS:
            corpus.write_text(text[:cut] + plant + text[cut:], encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(SCREEN), str(corpus), "--licence", "mit",
                 "--script", "geez", "--eval-set", str(EVAL_SET)],
                capture_output=True, text=True)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] screen_dataset: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                problems.append(f"screen_dataset plant misbehaved: {label}")
    return problems


# --------------------------------------------------------------------------
# check_figures.py — retired figures, derived counts, identifier integrity
#
# The marker-scope case is the one that already cost something. A `⚠️` in the
# *following* paragraph used to suppress a live claim, and "Seven decisions now
# carry amendments" sat unchecked and wrong behind one.
# --------------------------------------------------------------------------

FIGURES = REPO / "scripts" / "check_figures.py"

FIGURE_PLANTS = [
    ("bare retired figure", "\n\nTier 0 resident footprint is 72 MB.\n", 1),
    ("bare retired figure, wrapped across lines",
     "\n\nThe standing-cost saving from tiering\ndelivers a 22x saving overall.\n", 1),
    ("derived count contradicting the tree",
     "\n\nThis project has 3 reproducible experiments.\n", 1),
    ("derived count, spelled out",
     "\n\nThis project has three reproducible experiments.\n", 1),
    ("undefined goal id", "\n\nSee G-99 for details.\n", 1),
    ("undefined gap id", "\n\nSee GAP-77 for details.\n", 1),
    ("retired figure with its own retraction marker",
     "\n\n⚠️ Superseded: Tier 0 footprint was 72 MB.\n", 0),
    ("marker in the NEXT paragraph must not suppress",
     "\n\nTier 0 resident footprint is 72 MB.\n\n⚠️ An unrelated warning.\n", 1),
    ("untouched control", "", 0),
]


def run_figure_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "repo"
        shutil.copytree(REPO, work,
                        ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                      ".pytest_cache"))
        target = work / "docs" / "vision" / "goals.md"
        original = target.read_text(encoding="utf-8")
        for label, plant, expect in FIGURE_PLANTS:
            target.write_text(original + plant, encoding="utf-8")
            r = subprocess.run([sys.executable, "scripts/check_figures.py"],
                               cwd=work, capture_output=True, text=True)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] check_figures: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                problems.append(f"check_figures plant misbehaved: {label}")
    return problems


# --------------------------------------------------------------------------
# tigrinya_eval.morphology — the intrinsic checks
#
# These are the checks most exposed to the failure this file exists to catch.
# Their analyser is GPL-3.0 and absent here (DEC-028), so all five SKIP, and a
# skip that quietly reads as a pass would flip the metrics.md morphology row to
# ✅ on a machine where morphology has never once run.
#
# Injected analysers make that testable today: a broken one must fail, and the
# skip must stay distinct from a pass.
# --------------------------------------------------------------------------

MORPH_PLANT = '''
import sys
sys.path.insert(0, "services/evaluation/src")
sys.path.insert(0, "services/primitives/src")
from tigrinya_eval.morphology import (
    check_surface, check_alignment, check_determinism, evaluate_morphology)

TEXTS = ["ሰላም ዓለም", "ፀሓይ ትወጽእ ኣላ"]
n = [0]

def good(w):
    return [{"seg": "<" + w + ">"}]

def moving(w):
    n[0] += 1
    return [{"seg": "<" + w + ":" + str(n[0]) + ">"}]

CASE = sys.argv[1]
if CASE == "determinism_broken":
    words = sorted({w for t in TEXTS for w in t.split()})
    ok = check_determinism(words, analyser=moving).holds
elif CASE == "determinism_good":
    words = sorted({w for t in TEXTS for w in t.split()})
    ok = check_determinism(words, analyser=good).holds
elif CASE == "surface_broken":
    import tigrinya_eval.morphology as m
    real = m._analyse
    m._analyse = lambda t, a: real(t, a).__class__(
        surface=real(t, a).surface + "!", analysis=real(t, a).analysis)
    ok = check_surface(TEXTS, analyser=good).holds
elif CASE == "alignment_good":
    ok = check_alignment(TEXTS, analyser=good).holds
elif CASE == "skip_is_not_complete":
    r = evaluate_morphology(TEXTS)
    ok = not r.complete and bool(r.skipped())
elif CASE == "require_fails_when_absent":
    ok = not evaluate_morphology(TEXTS, require=True).holds
else:
    raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
'''

MORPH_PLANTS = [
    ("determinism catches a moving analyser", "determinism_broken", 1),
    ("determinism passes a stable analyser", "determinism_good", 0),
    ("surface catches a mangled surface form", "surface_broken", 1),
    ("alignment passes well-formed spans", "alignment_good", 0),
    ("a skipped check is not 'complete'", "skip_is_not_complete", 0),
    ("--require fails when the analyser is absent", "require_fails_when_absent", 0),
]


def run_morphology_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "plant.py"
        script.write_text(MORPH_PLANT, encoding="utf-8")
        for label, case, expect in MORPH_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, text=True)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] morphology: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(f"morphology plant misbehaved: {label} — {detail[0]}")
    return problems


def main() -> int:
    problems = (run_screen_plants() + run_figure_plants()
                + run_morphology_plants())
    print()
    for p in problems:
        print(f"::error::{p}")
    if problems:
        print(f"{len(problems)} planted failure(s) did not behave as specified — "
              f"a check has stopped being able to fail")
        return 1
    total = len(SCREEN_PLANTS) + len(FIGURE_PLANTS) + len(MORPH_PLANTS)
    print(f"all {total} planted cases behaved as specified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
