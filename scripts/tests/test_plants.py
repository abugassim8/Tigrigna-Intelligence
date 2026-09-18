#!/usr/bin/env python3
"""Plant known failures and assert the audit tooling reports them.

Eleven checks in this repository have been found that **could not fail** — seven of
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

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]

#: How every plant subprocess decodes its child.
#:
#: ⚠️ `text=True` on its own decodes with the *locale* default — UTF-8 on Linux
#: but **cp1252 on Windows** — and every script planted here prints `⚠️`, `—`
#: and Ge'ez. The decode runs in a reader thread, so a failure there does not
#: raise at the call: the thread dies, `.stdout` becomes None, and the plant
#: reports a misleading exit status instead of a decode error.
#:
#: That is the failure mode this suite exists to prevent, so it must not be the
#: suite's own. ⚠️ A plant expecting exit 1 **still "passes" when the child died
#: of an encoding crash**, because a crash also exits non-zero.
#:
#: This is only half the fix. The other half is in the children: a Python
#: process writing to a *pipe* on Windows encodes with cp1252 regardless of the
#: console, so each entry point forces its own stdout to UTF-8.
CHILD_IO = {"text": True, "encoding": "utf-8", "errors": "replace"}

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
                capture_output=True, **CHILD_IO)
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
    # The count of plants is itself a derived count now. This plant is the
    # reason that is worth anything — and note it changes the very number it
    # guards, which is the cleanest evidence the derivation is live.
    ("planted-case count contradicting the suite",
     "\n\nThe planted-failure suite is (3 cases, CI).\n", 1),
    # The other derived count that documents kept getting wrong by hand. Its
    # claim pattern is anchored tightly *and* its markers are switched off, so
    # this is the only thing standing between it and a silent pass.
    ("open-action count contradicting the register",
     "\n\n**3 open actions.**\n", 1),
    # A markdown table is one paragraph, so a ⚠️ in ANY row used to exempt
    # EVERY row — which left the plan of record's `| **Basis** |` line free to
    # claim 99 decisions and 77 experiments. The marked row here must not
    # protect the row above it.
    ("table row exempted by a marker in a sibling row",
     "\n\n| x | y |\n| --- | --- |\n| Basis | 3 reproducible experiments |\n"
     "| Note | ⚠️ superseded |\n", 1),
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
                               cwd=work, capture_output=True, **CHILD_IO)
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
from tigrinya_primitives import morphology as _m

# Exit 77 means "this plant could not be run here", the autotools convention.
# Two of these cases assert the *skip* path, which only exists when the
# analyser is absent — on a machine that has HornMorpho they are not failures,
# they are inapplicable. Reporting them as failures would make the one tool
# whose job is to be trusted about real alarms cry wolf.
SKIP = 77

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
    if _m.is_available():
        sys.exit(SKIP)
    r = evaluate_morphology(TEXTS)
    ok = not r.complete and bool(r.skipped())
elif CASE == "require_fails_when_absent":
    if _m.is_available():
        sys.exit(SKIP)
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


#: Mirrors `SKIP` inside MORPH_PLANT. See the note there.
PLANT_SKIP = 77

#: Filled by `run_morphology_plants`, read by `main` so the summary line can
#: never say "all N behaved as specified" when some of them did not run.
skipped: list[str] = []


# --------------------------------------------------------------------------
# scripts/measure_morphology.py — the large-corpus harness
#
# This harness serves surface/alignment/coverage from a table built during
# check_determinism's first pass, which is only legitimate because determinism
# is measured at 100%. That makes `_Recorder.__call__`'s unconditional
# call-through the single line the whole measurement rests on: serve a cached
# value there and determinism compares a value to itself, reports a perfect
# score, and licenses a table nobody checked.
#
# So two plants, and the second is the interesting one. It does not test the
# harness — it tests that the safeguard is load-bearing, by breaking it and
# showing a real failure becomes invisible.
#
# HornMorpho is absent here (DEC-028), so both patch `is_available` and
# `_analyser` to inject a fake. Nothing GPL-3.0 is needed to run them.
# --------------------------------------------------------------------------

HARNESS_PLANT = '''
import pathlib, sys, tempfile
sys.path.insert(0, "scripts")
sys.path.insert(0, "services/evaluation/src")
sys.path.insert(0, "services/primitives/src")
from tigrinya_primitives import morphology as _m

n = [0]
def steady(w):
    return [{"seg": "<" + w + ">"}]
def crashes_on_one(w):
    if w == "ዓለም":
        raise ValueError("too many values to unpack (expected 2)")
    return [{"seg": "<" + w + ">"}]
def always_crashes(w):
    raise ValueError("too many values to unpack (expected 2)")
def moving(w):                      # a different answer every call
    n[0] += 1
    return [{"seg": "<" + w + ":" + str(n[0]) + ">"}]

def run(analyser, corpus, out, recorder_call=None):
    """Run the harness with `analyser` injected. Returns (exit code, wrote?)."""
    n[0] = 0
    _m.is_available = lambda: True
    _m._analyser = lambda: analyser
    import measure_morphology as mm
    original = mm._Recorder.__call__
    if recorder_call:
        mm._Recorder.__call__ = recorder_call
    try:
        code = mm.main([str(corpus), "--json", str(out)])
    finally:
        mm._Recorder.__call__ = original
    return code, pathlib.Path(out).exists()

def cached_call(self, word):
    """The mutation: serve a stored value instead of calling through."""
    self.calls += 1
    if word in self.table:
        return [self.table[word]]
    raw = self._live(word)
    self._store(word, raw)
    return raw

CASE = sys.argv[1]
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    (tmp / "c.txt").write_text("ሰላም ዓለም\\nፀሓይ ትወጽእ ኣላ\\n", encoding="utf-8")
    # 300 distinct Ethiopic words, so a single crashing word is 0.3% — under
    # CRASH_ABORT_FRACTION, which is the case worth testing.
    big = tmp / "big"
    big.mkdir()
    filler = " ".join("ቃል" + chr(0x1200 + i) for i in range(300))
    (big / "c.txt").write_text("ሰላም ዓለም\\n" + filler + "\\n", encoding="utf-8")

    if CASE == "harness_measures_with_a_steady_analyser":
        code, wrote = run(steady, tmp, tmp / "a.json")
        ok = code == 0 and wrote

    elif CASE == "harness_aborts_and_writes_nothing_on_nondeterminism":
        code, wrote = run(moving, tmp, tmp / "b.json")
        # Not merely non-zero: it must not leave a partial artefact behind.
        ok = code != 0 and not wrote

    elif CASE == "call_through_is_load_bearing":
        honest, honest_wrote = run(moving, tmp, tmp / "c.json")
        broken, broken_wrote = run(moving, tmp, tmp / "d.json",
                                   recorder_call=cached_call)
        # Same broken analyser, one line changed: the honest recorder catches
        # it and writes nothing; the caching one reports a clean run.
        ok = (honest != 0 and not honest_wrote) and (broken == 0 and broken_wrote)
        if not ok:
            print("honest:", honest, honest_wrote, "broken:", broken, broken_wrote)

    elif CASE == "a_crashing_word_is_recorded_not_fatal":
        code, wrote = run(crashes_on_one, big, tmp / "e.json")
        # One pathological token must not cost the whole measurement — but it
        # must be named, never folded into "no analysis found".
        ok = code == 0 and wrote

    elif CASE == "an_analyser_that_always_raises_aborts":
        code, wrote = run(always_crashes, big, tmp / "f.json")
        # Past the threshold this is a broken analyser, not an edge case, and
        # measuring around it would be dishonest.
        ok = code != 0 and not wrote

    else:
        raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
'''

HARNESS_PLANTS = [
    ("measures with a steady analyser", "harness_measures_with_a_steady_analyser", 0),
    ("aborts and writes NOTHING on non-determinism",
     "harness_aborts_and_writes_nothing_on_nondeterminism", 0),
    ("a caching recorder hides non-determinism (the safeguard is real)",
     "call_through_is_load_bearing", 0),
    ("one crashing word is recorded, not fatal",
     "a_crashing_word_is_recorded_not_fatal", 0),
    ("an analyser that always raises aborts and writes nothing",
     "an_analyser_that_always_raises_aborts", 0),
]


def run_harness_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "harness_plant.py"
        script.write_text(HARNESS_PLANT, encoding="utf-8")
        for label, case, expect in HARNESS_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] measure_morphology: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"measure_morphology plant misbehaved: {label} — {detail[0]}")
    return problems


def run_morphology_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "plant.py"
        script.write_text(MORPH_PLANT, encoding="utf-8")
        for label, case, expect in MORPH_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            if r.returncode == PLANT_SKIP:
                skipped.append(label)
                print(f"  [SKIP] morphology: {label} — needs HornMorpho ABSENT; "
                      f"it is installed here, so this plant verified nothing")
                continue
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] morphology: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(f"morphology plant misbehaved: {label} — {detail[0]}")
    return problems


# --------------------------------------------------------------------------
# translate_tico19.py — the first measurement that loads a model
#
# Three of these cases are silent failures: the pipeline completes, the segment
# count is right, and chrF computes to a plausible number. Nothing else in this
# repository would notice, because the output is perfectly well-formed — it is
# just not a translation of what was asked, or not into Tigrinya.
#
# ⚠️ The model itself is never loaded here. `Translator` is injected exactly as
# `morphology.Analyser` is, which is what makes this testable in an environment
# that cannot reach huggingface.co — and what makes the argparse wiring in
# `main()` testable at all. That wiring had a real bug (a positional argument to
# a keyword-only parameter) that the self-test did not reach.
# --------------------------------------------------------------------------

TRANSLATE_PLANT = r'''
import json, pathlib, sys, tempfile
sys.path.insert(0, "scripts")
import translate_tico19 as t

GEEZ = "ሰላም ዓለም"      # "selam alem"

def steady(batch):
    return [GEEZ for _ in batch]
def drops_one(batch):
    return [GEEZ for _ in batch][:-1] or [GEEZ]
def english(batch):
    return ["Wash your hands often." for _ in batch]
def empties(batch):
    return ["" for _ in batch]
def degenerate_geez(batch):
    # ⚠️ Ethiopic AND degenerate: sails through the script gate. Every failure
    # this project had took this shape in some script or other.
    return ["\u1230" * 40 for _ in batch]

class _Probe:
    """A translator that records how often it loaded and which tokens it used."""

    def __init__(self, known=("<2ti>", "<2am>", "<2es>")):
        from tigrinya_translate.translate import (MadladTranslator,
                                                  UnknownLanguageTokenError)
        self._known = set(known)
        self._err = UnknownLanguageTokenError
        self._assert = MadladTranslator._assert_language_token
        self.language_token = "<2ti>"
        self.loads = 0
        self.tokens_used = []

    class _Tok:
        name_or_path = "probe"
        def __init__(self, known): self._k = known
        def get_vocab(self): return {t: i for i, t in enumerate(sorted(self._k))}
        def tokenize(self, s): return ["\u2581", "<2ti>", "\u2581Wash"]

    @property
    def _loaded(self):
        self.loads += 1
        return self._Tok(self._known), None

    def use_language(self, token):
        tok, _ = self._loaded
        self.loads -= 1                 # this access is bookkeeping, not a load
        self._assert(tok, token)
        self.language_token = token

    def __call__(self, segments):
        self.tokens_used.append(self.language_token)
        return ["\u12a2\u12f5\u12ab \u1270\u1213\u1338\u1265\u1362"
                for _ in segments]


CASE = sys.argv[1]

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    js, sheet = tmp / "r.json", tmp / "s.csv"

    if CASE == "scores_and_writes_with_a_steady_translator":
        out = t.measure(steady, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        ok = (js.exists() and sheet.exists()
              and len(out["scores"]) == 2
              and out["output_shape"]["ethiopic"] == 6)

    elif CASE == "the_cli_wiring_reaches_measure":
        # main() with the model class replaced. Catches argument-passing bugs
        # that --self-test cannot, because --self-test bypasses main()'s body.
        import tigrinya_translate.translate as tt
        tt.MadladTranslator = lambda *a, **k: type(
            "Stub", (), {"_loaded": (None, None), "__call__":
                         staticmethod(lambda b: steady(b))})()
        code = t.main(["--json", str(js), "--sheet", str(sheet), "--limit", "4"])
        ok = code == 0 and js.exists() and sheet.exists()

    elif CASE == "a_dropped_segment_aborts_and_writes_nothing":
        # chrF pairs by position: one dropped segment shifts every later pair
        # and the result reads as poor quality rather than as a bug.
        try:
            t.measure(drops_one, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.SegmentCountError:
            ok = not js.exists() and not sheet.exists()

    elif CASE == "output_in_the_wrong_language_aborts_and_writes_nothing":
        # The failure an unknown language token produces: fluent, right count,
        # scoreable, and about a language nobody asked for.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            ok = not js.exists() and not sheet.exists()

    elif CASE == "empty_output_aborts_rather_than_scoring_nothing":
        try:
            t.measure(empties, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            ok = not js.exists() and not sheet.exists()

    elif CASE == "the_sheet_never_leaks_the_reference":
        # Showing the human reference turns "is this usable health information"
        # into "does it match the other translation" -- the question chrF is
        # already answering.
        t.measure(steady, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        text = sheet.read_text(encoding="utf-8")
        refs = t._anchor("tir_et")
        ids = t.sample_indices(len(t._anchor("eng")))[:6]
        ok = all(refs[i] not in text for i in ids)

    elif CASE == "a_rejected_run_preserves_its_output":
        # A 46-minute run was correctly rejected and then discarded the only
        # evidence that could explain why. Refusing to record a MEASUREMENT was
        # right; throwing away the OUTPUT was not.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            rej = js.with_name(js.stem + "-REJECTED.json")
            ok = rej.exists() and not js.exists() and not sheet.exists()
            if ok:
                d = json.loads(rej.read_text(encoding="utf-8"))
                ok = (d["is_a_measurement"] is False
                      and len(d["pairs"]) == 6
                      and "chrf" not in json.dumps(d)
                      and d["pairs"][0]["output"] == "Wash your hands often.")

    elif CASE == "a_resumed_run_matches_an_uninterrupted_one":
        # The whole point of checkpointing: the same hypotheses, and an honest
        # record that the run was stitched from two sessions.
        # ⚠️ 12, not 6. translate_all batches by 8, so a 6-segment run is a
        # SINGLE batch that dies before any batch completes — and a batch that
        # failed must never reach disk. Testing resume needs two batches, and
        # the first version of this plant did not have them.
        clean = t.measure(steady, out_json=js, out_sheet=None, limit=12, quiet=True)

        calls = [0]
        def dies_after_first_batch(batch):
            calls[0] += len(batch)
            if calls[0] > 8:
                raise RuntimeError("simulated interruption")
            return steady(batch)

        js2 = tmp / "r2.json"
        try:
            t.measure(dies_after_first_batch, out_json=js2, out_sheet=None,
                      limit=12, quiet=True)
        except RuntimeError:
            pass
        partial = t._partial_path(js2)
        held = json.loads(partial.read_text(encoding="utf-8"))["hypotheses"]
        resumed = t.measure(steady, out_json=js2, out_sheet=None, limit=12,
                            quiet=True)
        ok = (len(held) == 8                                 # one batch survived
              and partial.exists() is False                  # spent on success
              and resumed["scores"] == clean["scores"]       # same result
              and resumed["resumed_from_partial"] == 8)      # and says so

    elif CASE == "a_resume_refuses_a_different_run":
        # ⚠️ Grafting old hypotheses onto a new sample would be well-formed and
        # completely wrong. The fingerprint is what stops it.
        t.measure(steady, out_json=js, out_sheet=None, limit=6, quiet=True)
        t._save_partial(t._partial_path(js), "not-this-run", ["x", "y"])
        got = t._load_partial(t._partial_path(js), t._fingerprint(["a"], t.MODEL))
        ok = got == []

    elif CASE == "smoke_writes_nothing_at_all":
        # ⚠️ The first version of this plant listed the temp directory before
        # and after. smoke() has no reason to write THERE, so it passed even
        # when smoke() was made to write into the repository root -- a check
        # that could not fail, found by reverting it rather than by reading it.
        #
        # Writing is now forbidden outright, wherever it is aimed.
        import builtins
        real_open, real_write = builtins.open, pathlib.Path.write_text
        def no_open(f, mode="r", *a, **k):
            if any(c in mode for c in "wxa+"):
                raise AssertionError(f"smoke() opened {f} for writing")
            return real_open(f, mode, *a, **k)
        def no_write(self, *a, **k):
            raise AssertionError(f"smoke() wrote {self}")
        builtins.open, pathlib.Path.write_text = no_open, no_write
        try:
            out = t.smoke(steady, 3, quiet=True)
            ok = len(out) == 3
        finally:
            builtins.open, pathlib.Path.write_text = real_open, real_write

    elif CASE == "the_diagnostic_survives_a_hard_crash":
        # ⚠️ The property the last real attempt lacked. A stage that segfaults
        # or is OOM-killed emits no Python traceback; in one process it takes
        # the whole report with it, which is exactly what happened.
        import diagnose_environment as dg
        text = dg.collect((
            ("ok", "print('first')"),
            ("hard crash", "import os; os._exit(3)"),
            ("after", "print('still ran')"),
        ))
        ok = ("first" in text and "still ran" in text
              and "NO output at all" in text and "exit 3" in text)

    elif CASE == "the_diagnostic_records_a_timeout_as_a_finding":
        import diagnose_environment as dg
        real = dg.TIMEOUT_SECONDS
        dg.TIMEOUT_SECONDS = 1
        try:
            text = dg.collect((("hangs", "import time; time.sleep(30)"),
                               ("after", "print('still ran')")))
        finally:
            dg.TIMEOUT_SECONDS = real
        ok = "TIMED OUT" in text and "still ran" in text

    elif CASE == "the_report_is_written_even_when_everything_fails":
        # A diagnostic that produces nothing when everything is broken is
        # worthless -- and that is the case it exists for.
        import diagnose_environment as dg
        text = dg.collect((("a", "import os; os._exit(1)"),
                           ("b", "raise SystemExit(9)")))
        ok = len(text) > 200 and "TRANSLATION DIAGNOSTIC" in text

    elif CASE == "a_rejected_run_blocks_an_identical_rerun":
        # The second wrong-language run cost ninety minutes to learn nothing,
        # because the rejected file recorded the failure and nothing read it.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        except t.WrongLanguageError:
            pass
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.AlreadyRejectedError as exc:
            ok = "--diagnose" in str(exc) and "--force" in str(exc)

    elif CASE == "a_different_run_is_not_blocked":
        # ⚠️ The negative case, and the one that keeps this check alive. A
        # block that fired on everything would be switched off within a week.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        except t.WrongLanguageError:
            pass
        # Same output path, DIFFERENT sample -> different fingerprint.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=8, quiet=True)
            ok = False
        except t.AlreadyRejectedError:
            ok = False                      # blocked a run it has never seen
        except t.WrongLanguageError:
            ok = True                       # ran, and failed on its own merits

    elif CASE == "force_overrides_the_block":
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        except t.WrongLanguageError:
            pass
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True,
                      force=True)
            ok = False
        except t.AlreadyRejectedError:
            ok = False                      # --force did not override
        except t.WrongLanguageError:
            ok = True

    elif CASE == "both_artefacts_record_the_environment":
        # ⚠️ A rejected run whose environment is unknown cannot be diagnosed --
        # exactly the position the second run left us in. transformers 5.17
        # loading a 4.23-era checkpoint is the live suspect, and nothing
        # recorded which transformers ran.
        good = t.measure(steady, out_json=js, out_sheet=None, limit=6, quiet=True)
        js2 = tmp / "bad.json"
        try:
            t.measure(english, out_json=js2, out_sheet=None, limit=6, quiet=True)
        except t.WrongLanguageError:
            pass
        rej = json.loads(
            js2.with_name(js2.stem + "-REJECTED.json").read_text(encoding="utf-8"))
        ok = ("transformers" in good["environment"]
              and "transformers" in rej["environment"]
              and rej["fingerprint"])

    elif CASE == "diagnose_loads_the_model_once_for_every_language":
        # ⚠️ Reloading 11.8 GB per control language would take longer than the
        # failure being diagnosed.
        probe = _Probe()
        t.diagnose(probe, 2)
        ok = probe.loads == 1 and len(probe.tokens_used) == 3

    elif CASE == "diagnose_actually_changes_the_language":
        # ⚠️ THE one that matters. `_loaded` is a cached_property; if the token
        # were captured at load time instead of read per call, every control
        # language would emit identical output and the diagnostic would report
        # "Tigrinya and Spanish both fail" -- a false pipeline diagnosis from a
        # check that ran perfectly.
        probe = _Probe()
        t.diagnose(probe, 2)
        ok = probe.tokens_used == ["<2ti>", "<2am>", "<2es>"]

    elif CASE == "diagnose_writes_nothing_at_all":
        import builtins
        real_open, real_write = builtins.open, pathlib.Path.write_text
        def no_open(f, mode="r", *a, **k):
            if any(c in mode for c in "wxa+"):
                raise AssertionError(f"diagnose() opened {f} for writing")
            return real_open(f, mode, *a, **k)
        def no_write(self, *a, **k):
            raise AssertionError(f"diagnose() wrote {self}")
        builtins.open, pathlib.Path.write_text = no_open, no_write
        try:
            t.diagnose(_Probe(), 2)
            ok = True
        finally:
            builtins.open, pathlib.Path.write_text = real_open, real_write

    elif CASE == "diagnose_survives_a_refused_language":
        # A control language the model does not know must be reported and
        # skipped, never abort the whole diagnostic.
        probe = _Probe(known=("<2ti>", "<2es>"))
        res = t.diagnose(probe, 2)
        ok = res["<2am>"] is None and res["<2ti>"] == 2

    elif CASE == "the_model_flag_reaches_the_translator":
        # ⚠️ Wiring. A flag can exist, be declared, pass check_commands.py and
        # be ignored — which is the `out_json` positional bug in another suit.
        import tigrinya_translate.translate as tt
        seen = {}

        def factory(*a, **k):
            seen.update(k)
            return type("Stub", (), {
                "_loaded": (None, None),
                "model_name": k.get("model_name"),
                "dtype": k.get("dtype"),
                "__call__": staticmethod(lambda b: steady(b))})()

        tt.MadladTranslator = factory
        code = t.main(["--model", "some/where", "--json", str(js),
                       "--sheet", str(sheet), "--limit", "4"])
        saved = json.loads(js.read_text(encoding="utf-8"))
        ok = (code == 0 and seen.get("model_name") == "some/where"
              and saved["model"] == "some/where"
              and saved["environment"]["model_name"] == "some/where")

    elif CASE == "a_pre_repair_rejection_does_not_block_a_repaired_run":
        # ⚠️ The one that decides whether the first correct measurement can run
        # at all. The wrong-language rejections of 2026-09-15 and -16 came from
        # a model whose trained lm_head had been discarded by the loader. A
        # repaired model is a different configuration and must not be refused
        # as a known failure.
        class Broken:
            dtype, language_token, head_state = "bfloat16", "<2ti>", "TIED_WRONGLY"
            def __call__(self, batch):
                return english(batch)

        class Repaired:
            dtype, language_token, head_state = "bfloat16", "<2ti>", "TRAINED"
            def __call__(self, batch):
                return steady(batch)

        try:
            t.measure(Broken(), out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            out = t.measure(Repaired(), out_json=js, out_sheet=sheet, limit=6,
                            quiet=True)
            ok = bool(out["scores"])

    elif CASE == "an_identical_configuration_is_still_blocked":
        # ⚠️ The control for the case above. Loosening the fingerprint until
        # nothing is ever blocked would pass that plant and destroy the guard.
        class Broken:
            dtype, language_token, head_state = "bfloat16", "<2ti>", "TIED_WRONGLY"
            def __call__(self, batch):
                return english(batch)

        try:
            t.measure(Broken(), out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            try:
                t.measure(Broken(), out_json=js, out_sheet=sheet, limit=6,
                          quiet=True)
                ok = False
            except t.AlreadyRejectedError:
                ok = True

    elif CASE == "a_different_dtype_is_not_blocked":
        class Broken:
            dtype, language_token, head_state = "bfloat16", "<2ti>", "TRAINED"
            def __call__(self, batch):
                return english(batch)

        class Float32:
            dtype, language_token, head_state = "float32", "<2ti>", "TRAINED"
            def __call__(self, batch):
                return steady(batch)

        try:
            t.measure(Broken(), out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            out = t.measure(Float32(), out_json=js, out_sheet=sheet, limit=6,
                            quiet=True)
            ok = bool(out["scores"])

    elif CASE == "the_artefact_records_the_checkpoint_it_opened":
        # A run from the cache and a run from the converted directory were
        # previously indistinguishable in the recorded result.
        import tigrinya_translate.head as head
        from safetensors.torch import save_file
        import torch as _torch

        d = pathlib.Path(tmp) / "conv"
        d.mkdir()
        save_file({"w": _torch.randn(4, 4)}, str(d / "model.safetensors"))

        class Local:
            dtype, language_token, head_state = "bfloat16", "<2ti>", "TRAINED"
            model_name = str(d)
            def __call__(self, batch):
                return steady(batch)

        t.measure(Local(), out_json=js, out_sheet=sheet, limit=4, quiet=True)
        env = json.loads(js.read_text(encoding="utf-8"))["environment"]
        ok = (env["checkpoint"] == str(d / "model.safetensors")
              and env["checkpoint_bytes"] > 0
              and env["model_name"] == str(d))

    elif CASE == "a_converted_checkpoint_keeps_its_source_identity":
        # ⚠️ Converted and original hold bit-identical weights, so they are the
        # same measurement and must share a fingerprint. Keying on the path
        # would unblock a configuration already known to fail.
        import sys as _sys
        _sys.path.insert(0, "scripts")
        import shrink_checkpoint as sc
        import tigrinya_translate.head as head
        from safetensors.torch import save_file
        import torch as _torch

        base = pathlib.Path(tmp) / "orig"
        base.mkdir()
        save_file({"decoder.embed_tokens.weight": _torch.randn(40, 8),
                   "lm_head.weight": _torch.randn(40, 8)},
                  str(base / "model.safetensors"))
        sc.convert(str(base / "model.safetensors"),
                   str(pathlib.Path(tmp) / "c.safetensors"),
                   metadata={"converted_from": "google/madlad400-3b-mt"})
        ident = head.source_model_id(str(pathlib.Path(tmp) / "c.safetensors"),
                                     "some/local/path")
        original = head.source_model_id(str(base / "model.safetensors"),
                                        "google/madlad400-3b-mt")
        ok = ident == original == "google/madlad400-3b-mt"

    elif CASE == "degenerate_output_aborts_even_when_it_is_ethiopic":
        try:
            t.measure(degenerate_geez, out_json=js, out_sheet=sheet, limit=6,
                      quiet=True)
            ok = False
        except t.WrongLanguageError as exc:
            ok = ("repeated token" in str(exc)
                  and not js.exists() and not sheet.exists())

    elif CASE == "real_translations_do_not_trip_the_degeneracy_guard":
        # ⚠️ The control. A guard that fired on real text would be switched off
        # within a week, which is the whole of DEC-008.
        out = t.measure(steady, out_json=js, out_sheet=sheet, limit=6,
                        quiet=True)
        ok = bool(out["scores"]) and js.exists()

    elif CASE == "the_threshold_is_recorded_before_judging":
        out = t.measure(steady, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        saved = json.loads(js.read_text(encoding="utf-8"))
        ok = (saved["pre_committed"]["usable_threshold"] == t.USABLE_THRESHOLD
              and saved["judgement"].startswith("PENDING"))

    else:
        raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
'''

TRANSLATE_PLANTS = [
    ("scores and writes with a steady translator",
     "scores_and_writes_with_a_steady_translator", 0),
    ("the CLI wiring actually reaches measure()",
     "the_cli_wiring_reaches_measure", 0),
    ("a dropped segment aborts and writes NOTHING",
     "a_dropped_segment_aborts_and_writes_nothing", 0),
    ("output in the wrong language aborts and writes NOTHING",
     "output_in_the_wrong_language_aborts_and_writes_nothing", 0),
    ("empty output aborts rather than scoring nothing",
     "empty_output_aborts_rather_than_scoring_nothing", 0),
    ("the judgement sheet never leaks the reference",
     "the_sheet_never_leaks_the_reference", 0),
    ("the threshold is recorded before judging",
     "the_threshold_is_recorded_before_judging", 0),
    ("degenerate output aborts even when it is Ethiopic",
     "degenerate_output_aborts_even_when_it_is_ethiopic", 0),
    ("real translations do not trip the degeneracy guard",
     "real_translations_do_not_trip_the_degeneracy_guard", 0),
    ("--model reaches the translator and the artefact",
     "the_model_flag_reaches_the_translator", 0),
    ("a pre-repair rejection does not block a repaired run",
     "a_pre_repair_rejection_does_not_block_a_repaired_run", 0),
    ("an identical configuration is still blocked",
     "an_identical_configuration_is_still_blocked", 0),
    ("a different dtype is not blocked",
     "a_different_dtype_is_not_blocked", 0),
    ("the artefact records the checkpoint it opened",
     "the_artefact_records_the_checkpoint_it_opened", 0),
    ("a converted checkpoint keeps its source identity",
     "a_converted_checkpoint_keeps_its_source_identity", 0),
    ("a rejected run preserves its output for diagnosis",
     "a_rejected_run_preserves_its_output", 0),
    ("a resumed run matches an uninterrupted one, and says it resumed",
     "a_resumed_run_matches_an_uninterrupted_one", 0),
    ("a resume refuses a partial from a different run",
     "a_resume_refuses_a_different_run", 0),
    ("--smoke writes nothing at all",
     "smoke_writes_nothing_at_all", 0),
    ("--diagnose loads the model once for every language",
     "diagnose_loads_the_model_once_for_every_language", 0),
    ("--diagnose actually changes the language between runs",
     "diagnose_actually_changes_the_language", 0),
    ("--diagnose writes nothing at all",
     "diagnose_writes_nothing_at_all", 0),
    ("--diagnose survives a refused control language",
     "diagnose_survives_a_refused_language", 0),
    ("a rejected run blocks an identical re-run",
     "a_rejected_run_blocks_an_identical_rerun", 0),
    ("a DIFFERENT run is not blocked",
     "a_different_run_is_not_blocked", 0),
    ("--force overrides the block",
     "force_overrides_the_block", 0),
    ("both artefacts record which transformers ran",
     "both_artefacts_record_the_environment", 0),
    ("the diagnostic survives a hard crash in one stage",
     "the_diagnostic_survives_a_hard_crash", 0),
    ("the diagnostic records a timeout as a finding",
     "the_diagnostic_records_a_timeout_as_a_finding", 0),
    ("the report is written even when every stage fails",
     "the_report_is_written_even_when_everything_fails", 0),
]


def run_translate_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "translate_plant.py"
        script.write_text(TRANSLATE_PLANT, encoding="utf-8")
        for label, case, expect in TRANSLATE_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] translate_tico19: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"translate_tico19 plant misbehaved: {label} — {detail[0]}")
    return problems


# --------------------------------------------------------------------------
# repair_lm_head.py — the one that must NOT fire on a healthy model
#
# `T5ForConditionalGeneration` declares `lm_head.weight` tied in every
# transformers from 4.35 to 5.17, unconditionally, while MADLAD's config says
# `tie_word_embeddings: false`. A key in that mapping is suppressed from the
# missing-weights warning, so a randomly-initialised output projection loads
# silently and the decoder emits one token repeated to `max_new_tokens`.
#
# ⚠️ The dangerous plant here is `a_trained_head_is_left_alone`. Everything
# else guards against failing to repair; that one guards against repairing a
# model that was fine, which no output would reveal — the failure mode this
# repository has already hit four times.
#
# These need torch and safetensors. They build a 50x8 model and a 3 KB
# checkpoint, so they exercise the real code path without the 11.8 GB
# download — and SKIP rather than pass when the libraries are absent, the
# convention DEC-028 set for HornMorpho.
# --------------------------------------------------------------------------

REPAIR_PLANT = r"""
import pathlib, sys, tempfile
import torch
from safetensors.torch import save_file
sys.path.insert(0, "scripts")
import repair_lm_head as r

VOCAB, DIM = 50, 8
torch.manual_seed(20260916)


def noise():
    # Rows of near-equal norm: what `init.normal_` leaves behind.
    return torch.randn(VOCAB, DIM)


def trained():
    # Rows of wildly differing norm, including near-dead rare tokens.
    w = torch.randn(VOCAB, DIM)
    scale = torch.cat([torch.full((VOCAB - 5,), 1.0), torch.full((5,), 1e-4)])
    return w * scale.unsqueeze(1)


class Cfg:
    def __init__(self, tie):
        self.tie_word_embeddings = tie


class Stub(torch.nn.Module):
    # The smallest thing `repair()` can work on: same attribute surface as a
    # real T5ForConditionalGeneration, 50x8 instead of 256000x1024.

    def __init__(self, shared_w, head_w, tie=False, alias=False):
        super().__init__()
        self.shared = torch.nn.Embedding(VOCAB, DIM)
        with torch.no_grad():
            self.shared.weight.copy_(shared_w)
        self.lm_head = torch.nn.Linear(DIM, VOCAB, bias=False)
        if alias:
            self.lm_head.weight = self.shared.weight      # one Parameter, tied
        else:
            with torch.no_grad():
                self.lm_head.weight.copy_(head_w)
        self.config = Cfg(tie)

    def get_input_embeddings(self):
        return self.shared


CASE = sys.argv[1]

with tempfile.TemporaryDirectory() as tmp:
    ckpt = str(pathlib.Path(tmp) / "model.safetensors")
    shared_w, projection = trained(), trained()

    if CASE == "a_random_head_is_detected_and_repaired":
        save_file({"shared.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, noise())
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["verdict"] == "RANDOM" and rec["repaired"]
              and rec["source_key"] == "lm_head.weight"
              and rec["input_key"] == "shared.weight"
              and torch.equal(m.lm_head.weight.detach(), projection))

    elif CASE == "a_trained_head_is_left_alone":
        # ⚠️ The one that matters. An unconditional repair would overwrite a
        # correctly-loaded model and nothing downstream would ever show it.
        save_file({"shared.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        head = trained()
        m = Stub(shared_w, head)
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["verdict"] == "TRAINED" and not rec["repaired"]
              and rec["source_key"] is None
              and torch.equal(m.lm_head.weight.detach(), head))

    elif CASE == "a_wrongly_tied_head_is_caught_and_untied":
        save_file({"shared.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, None, tie=False, alias=True)
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["verdict"] == "TIED_WRONGLY" and rec["repaired"]
              and torch.equal(m.lm_head.weight.detach(), projection)
              # ⚠️ and the input embedding is restored from the checkpoint,
              # not merely left alone: the loader may have put the projection
              # there, which is exactly what it does with the real model.
              and torch.equal(m.shared.weight.detach(), shared_w))

    elif CASE == "a_genuinely_tied_model_is_not_touched":
        # ⚠️ A genuinely tied checkpoint stores ONE embedding matrix -- there is
        # no second one to store. The earlier fixture here stored two and still
        # expected "leave it alone", which encoded the config-based rule that
        # reported the real model healthy. Two distinct embedding matrices mean
        # untied, whatever the config says.
        #
        # This case and `a_checkpoint_with_no_separate_head_stays_tied` are the
        # pair: same single-matrix checkpoint, config True here and False there,
        # and the flag changes nothing either way.
        save_file({"shared.weight": shared_w}, ckpt)
        m = Stub(shared_w, None, tie=True, alias=True)
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["verdict"] == "TRAINED" and not rec["repaired"]
              and torch.equal(m.lm_head.weight.detach(), shared_w))

    elif CASE == "a_checkpoint_with_no_projection_is_refused":
        # Every stored matrix is the input embedding: nothing to recover.
        save_file({"shared.weight": shared_w,
                   "encoder.embed_tokens.weight": shared_w.clone()}, ckpt)
        m = Stub(shared_w, noise())
        try:
            r.repair(m, ckpt, quiet=True)
            ok = False
        except r.RandomHeadError:
            ok = True

    elif CASE == "an_ambiguous_checkpoint_is_refused":
        # Two candidates, neither named lm_head: picking one would be a guess.
        # ⚠️ Ambiguity is now on the input side: lm_head.weight names itself,
        # but two tensors could be the embedding the encoder should use.
        save_file({"shared.weight": shared_w,
                   "decoder.embed_tokens.weight": trained(),
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, noise())
        try:
            r.repair(m, ckpt, quiet=True)
            ok = False
        except r.AmbiguousProjectionError:
            ok = True

    elif CASE == "a_repair_that_changes_nothing_raises":
        # The projection already equals the head, so the write is a no-op.
        head = noise()
        save_file({"shared.weight": shared_w,
                   "lm_head.weight": shared_w.clone()}, ckpt)
        m = Stub(shared_w, head)
        try:
            r.repair(m, ckpt, quiet=True)
            ok = False
        except r.RepairFailedError:
            ok = True

    elif CASE == "an_explicit_lm_head_key_wins":
        # When the checkpoint names it outright, no inference is needed.
        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, noise())
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["source_key"] == "lm_head.weight"
              and torch.equal(m.lm_head.weight.detach(), projection))

    elif CASE == "a_bfloat16_model_resolves_a_float32_checkpoint":
        # ⚠️ The real run's shape: checkpoint float32, model bfloat16.
        # Comparing in float32 makes EVERY candidate differ by rounding and
        # raises AmbiguousProjectionError on a healthy checkpoint -- a check
        # firing on correct input, which is how checks get switched off.
        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, noise()).to(torch.bfloat16)
        rec = r.repair(m, ckpt, quiet=True)
        ok = rec["repaired"] and rec["source_key"] == "lm_head.weight"

    elif CASE == "the_translator_repairs_at_load":
        # ⚠️ Wiring, not logic. `_loaded` could hold a perfect check that is
        # never called -- this repository has shipped that exact bug twice.
        import types
        import tigrinya_translate.head as head
        import tigrinya_translate.translate as tt

        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        head.locate_checkpoint = lambda name: ckpt

        class Tok:
            name_or_path = "stub"
            def get_vocab(self):
                return {"<2ti>": 0}

        stub = Stub(shared_w, noise()).to(torch.bfloat16)
        fake = types.ModuleType("transformers")
        fake.AutoTokenizer = type("A", (), {
            "from_pretrained": staticmethod(lambda *a, **k: Tok())})
        fake.AutoModelForSeq2SeqLM = type("B", (), {
            "from_pretrained": staticmethod(lambda *a, **k: stub)})
        fake.__version__ = "0"
        sys.modules["transformers"] = fake

        tr = tt.MadladTranslator()
        tr._loaded
        ok = (tr.head_state == "RANDOM" and tr.head_repaired
              and tr.head_source == "lm_head.weight"
              and torch.equal(stub.lm_head.weight.detach(),
                              projection.to(torch.bfloat16))
              # ⚠️ and the input embedding is restored too — repairing only
              # the head leaves the encoder reading the wrong matrix.
              and torch.equal(stub.shared.weight.detach(),
                              shared_w.to(torch.bfloat16)))

    elif CASE == "the_translator_refuses_when_it_cannot_repair":
        # No checkpoint to recover from: refuse, never score noise.
        import types
        import tigrinya_translate.head as head
        import tigrinya_translate.translate as tt

        def missing(name):
            raise FileNotFoundError("no cached checkpoint")
        head.locate_checkpoint = missing

        class Tok:
            name_or_path = "stub"
            def get_vocab(self):
                return {"<2ti>": 0}

        stub = Stub(shared_w, noise()).to(torch.bfloat16)
        fake = types.ModuleType("transformers")
        fake.AutoTokenizer = type("A", (), {
            "from_pretrained": staticmethod(lambda *a, **k: Tok())})
        fake.AutoModelForSeq2SeqLM = type("B", (), {
            "from_pretrained": staticmethod(lambda *a, **k: stub)})
        fake.__version__ = "0"
        sys.modules["transformers"] = fake

        try:
            tt.MadladTranslator()._loaded
            ok = False
        except head.RandomHeadError:
            ok = True

    elif CASE == "the_real_shape_a_forced_tie_with_config_saying_tied":
        # ⚠️ **The regression test for 2026-09-16.** This is the real
        # checkpoint's exact shape: decoder.embed_tokens.weight AND a separate
        # trained lm_head.weight, no shared.weight -- with the loaded model
        # reporting config.tie_word_embeddings=True, because transformers 5.x
        # overwrites it in T5Config.__post_init__ regardless of the file.
        #
        # The first version of this check asked the config, believed it, and
        # printed "TRAINED -- nothing is wrong here" while the decoder emitted
        # `Sally Hansen Sally Hansen ...`. It must never do that again.
        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, None, tie=True, alias=True)
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["verdict"] == "TIED_WRONGLY" and rec["repaired"]
              and rec["source_key"] == "lm_head.weight"
              and torch.equal(m.lm_head.weight.detach(), projection)
              and torch.equal(m.shared.weight.detach(), shared_w))

    elif CASE == "a_checkpoint_with_no_separate_head_stays_tied":
        # The mirror. No stored lm_head.weight means tying is correct, and the
        # config saying False must not provoke a repair either.
        save_file({"decoder.embed_tokens.weight": shared_w}, ckpt)
        m = Stub(shared_w, None, tie=False, alias=True)
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["verdict"] == "TRAINED" and not rec["repaired"]
              and torch.equal(m.lm_head.weight.detach(), shared_w))

    elif CASE == "the_explicit_key_wins_even_when_the_model_disagrees":
        # ⚠️ **This plant asserted the opposite rule and passed, and the rule
        # was wrong.** It required that an `lm_head.weight` matching the loaded
        # input embedding be rejected in favour of the tensor that differed.
        # But on the real model the loader puts `lm_head.weight` INTO the input
        # embedding, so "matches the input" is the signature of the bug rather
        # than evidence against the name. The file's names decide.
        save_file({"decoder.embed_tokens.weight": projection,
                   "lm_head.weight": shared_w.clone()}, ckpt)
        m = Stub(shared_w, None, tie=True, alias=True)
        rec = r.repair(m, ckpt, quiet=True)
        ok = (rec["source_key"] == "lm_head.weight"
              and rec["input_key"] == "decoder.embed_tokens.weight"
              and torch.equal(m.lm_head.weight.detach(), shared_w)
              and torch.equal(m.shared.weight.detach(), projection))

    elif CASE == "the_repair_never_maps_the_checkpoint":
        # ⚠️ **The regression test for 2026-09-18.** The repair mapped the whole
        # 5.88 GB checkpoint to fetch two 0.49 GB matrices, on top of a 5.48 GB
        # resident model, and was killed by the Windows commit limit with no
        # traceback at all.
        #
        # ⚠️ Asserted structurally, not by measuring memory. The first version
        # of this plant measured peak RSS — and could not fail, because RSS on
        # Linux does not reflect a Windows commit limit: the mapping is lazy and
        # the allocator reuses freed blocks, so the broken version measured
        # cheaper than the budget. A plant that cannot fail on the platform it
        # runs on is worse than no plant.
        import safetensors
        import tigrinya_translate.head as head

        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, None, tie=True, alias=True).to(torch.bfloat16)

        def forbidden(*a, **k):
            raise AssertionError("the repair memory-mapped the checkpoint")

        real_open, safetensors.safe_open = safetensors.safe_open, forbidden
        try:
            rec = r.repair(m, ckpt, quiet=True)
            ok = rec["repaired"] and rec["source_key"] == "lm_head.weight"
        finally:
            safetensors.safe_open = real_open

    elif CASE == "the_repair_holds_one_checkpoint_tensor":
        # ⚠️ The other half of the same invariant: even without mapping, holding
        # both matrices doubled the resident cost on a machine with none spare.
        # Each tensor must be released before the next is read.
        import weakref
        import tigrinya_translate.head as head

        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        m = Stub(shared_w, None, tie=True, alias=True).to(torch.bfloat16)

        live = []
        real_read = head.read_tensor
        problem = []

        def counting_read(*a, **k):
            for ref in live:
                if ref() is not None:
                    problem.append("a previous checkpoint tensor was still live")
            tensor = real_read(*a, **k)
            live.append(weakref.ref(tensor))
            return tensor

        head.read_tensor = counting_read
        try:
            rec = r.repair(m, ckpt, quiet=True)
            ok = rec["repaired"] and not problem and len(live) >= 2
            if problem:
                print(problem[0], file=sys.stderr)
        finally:
            head.read_tensor = real_read

    elif CASE == "read_tensor_matches_safe_open":
        # ⚠️ The cheap path must not be a different path.
        from safetensors import safe_open
        import tigrinya_translate.head as head

        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, ckpt)
        hdr = head.read_safetensors_header(ckpt)
        with safe_open(ckpt, framework="pt") as f:
            ok = all(torch.equal(head.read_tensor(ckpt, hdr, k), f.get_tensor(k))
                     for k in ("decoder.embed_tokens.weight", "lm_head.weight"))

    elif CASE == "a_local_directory_resolves":
        # ⚠️ shrink_checkpoint.py writes a directory and prints a command using
        # it. That command failed, because the lookup only searched the HF cache.
        d = pathlib.Path(tmp) / "conv"
        d.mkdir()
        save_file({"w": torch.randn(4, 4)}, str(d / "model.safetensors"))
        ok = r.locate_checkpoint(str(d)) == str(d / "model.safetensors")

    elif CASE == "a_local_safetensors_file_resolves":
        f = pathlib.Path(tmp) / "explicit.safetensors"
        save_file({"w": torch.randn(4, 4)}, str(f))
        ok = r.locate_checkpoint(str(f)) == str(f)

    elif CASE == "a_mistyped_local_path_is_refused_not_globbed":
        # ⚠️ The dangerous one. A path-shaped argument that does not exist must
        # NOT fall through to the cache glob -- that would silently resolve to
        # whatever model was found first and report success against a different
        # checkpoint than the one loaded.
        try:
            r.locate_checkpoint(str(pathlib.Path(tmp) / "no" / "such" / "dir"))
            ok = False
        except FileNotFoundError as exc:
            ok = "looks like a path" in str(exc)

    elif CASE == "a_hub_id_still_reaches_the_cache":
        # ⚠️ **The plant the plan named and the first version did not have.**
        # A Hub id is `namespace/name` and contains a slash, so a "looks like a
        # path" test written as `os.sep in name` rejected the default model on
        # every platform. This must reach the cache lookup and fail there --
        # with the cache message, not the path message.
        try:
            r.locate_checkpoint("google/madlad400-3b-mt")
            ok = True                       # a real cache is fine too
        except FileNotFoundError as exc:
            ok = "no cached model.safetensors" in str(exc)

    elif CASE == "a_missing_path_under_a_real_directory_is_refused":
        # `models/typo` where `models` exists: local, and must not fall through
        # to the glob, which would resolve to some other MADLAD copy.
        base = pathlib.Path(tmp) / "models"
        base.mkdir()
        try:
            r.locate_checkpoint(str(base / "typo"))
            ok = False
        except FileNotFoundError as exc:
            ok = "looks like a path" in str(exc)

    elif CASE == "a_directory_without_weights_names_itself":
        try:
            r.locate_checkpoint(str(tmp))
            ok = False
        except FileNotFoundError as exc:
            ok = "no model.safetensors" in str(exc) and str(tmp) in str(exc)

    elif CASE == "the_translator_accepts_a_local_directory":
        import types
        import tigrinya_translate.translate as tt

        d = pathlib.Path(tmp) / "local"
        d.mkdir()
        save_file({"decoder.embed_tokens.weight": shared_w,
                   "lm_head.weight": projection}, str(d / "model.safetensors"))

        class Tok:
            name_or_path = "stub"
            def get_vocab(self):
                return {"<2ti>": 0}

        stub = Stub(shared_w, None, tie=True, alias=True).to(torch.bfloat16)
        fake = types.ModuleType("transformers")
        fake.AutoTokenizer = type("A", (), {
            "from_pretrained": staticmethod(lambda *a, **k: Tok())})
        fake.AutoModelForSeq2SeqLM = type("B", (), {
            "from_pretrained": staticmethod(lambda *a, **k: stub)})
        fake.__version__ = "0"
        sys.modules["transformers"] = fake

        tr = tt.MadladTranslator(model_name=str(d))
        tr._loaded
        ok = (tr.head_state == "TIED_WRONGLY" and tr.head_repaired
              and torch.equal(stub.lm_head.weight.detach(),
                              projection.to(torch.bfloat16)))

    else:
        raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
"""

REPAIR_PLANTS = [
    ("a random head is detected and repaired",
     "a_random_head_is_detected_and_repaired", 0),
    ("a TRAINED head is left alone",
     "a_trained_head_is_left_alone", 0),
    ("a wrongly-tied head is untied without destroying the input embedding",
     "a_wrongly_tied_head_is_caught_and_untied", 0),
    ("a genuinely tied model is not touched",
     "a_genuinely_tied_model_is_not_touched", 0),
    ("a checkpoint with no output projection is refused",
     "a_checkpoint_with_no_projection_is_refused", 0),
    ("an ambiguous checkpoint is refused rather than guessed",
     "an_ambiguous_checkpoint_is_refused", 0),
    ("a repair that changes nothing raises",
     "a_repair_that_changes_nothing_raises", 0),
    ("an explicit lm_head.weight key wins",
     "an_explicit_lm_head_key_wins", 0),
    ("a bfloat16 model resolves a float32 checkpoint",
     "a_bfloat16_model_resolves_a_float32_checkpoint", 0),
    ("MadladTranslator actually repairs at load",
     "the_translator_repairs_at_load", 0),
    ("MadladTranslator refuses when it cannot repair",
     "the_translator_refuses_when_it_cannot_repair", 0),
    ("the real shape: a forced tie while the config claims tied",
     "the_real_shape_a_forced_tie_with_config_saying_tied", 0),
    ("a checkpoint with no separate head stays tied",
     "a_checkpoint_with_no_separate_head_stays_tied", 0),
    ("the explicit lm_head key wins even when the model disagrees",
     "the_explicit_key_wins_even_when_the_model_disagrees", 0),
    ("the repair never maps the checkpoint",
     "the_repair_never_maps_the_checkpoint", 0),
    ("the repair holds one checkpoint tensor at a time",
     "the_repair_holds_one_checkpoint_tensor", 0),
    ("read_tensor matches safe_open byte for byte",
     "read_tensor_matches_safe_open", 0),
    ("a local model directory resolves",
     "a_local_directory_resolves", 0),
    ("a local .safetensors file resolves",
     "a_local_safetensors_file_resolves", 0),
    ("a mistyped local path is refused, never globbed to another model",
     "a_mistyped_local_path_is_refused_not_globbed", 0),
    ("a Hub id still reaches the cache, not the path branch",
     "a_hub_id_still_reaches_the_cache", 0),
    ("a missing path under a real directory is refused",
     "a_missing_path_under_a_real_directory_is_refused", 0),
    ("a directory without weights names itself in the error",
     "a_directory_without_weights_names_itself", 0),
    ("MadladTranslator accepts a local model directory",
     "the_translator_accepts_a_local_directory", 0),
]


def run_repair_plants() -> list[str]:
    try:
        import torch                                       # noqa: F401
        import safetensors                                 # noqa: F401
    except ImportError as exc:
        # ⚠️ SKIP, never pass. DEC-028's rule: a check that cannot run must say
        # so out loud, because a silent pass is indistinguishable from a real
        # one and that is how a check stops being able to fail.
        # `exc.name` is None when the import failed for a reason other than
        # absence, and "None not installed" tells a reader nothing.
        skipped.append(f"repair_lm_head ({exc.name or exc} — torch and "
                       f"safetensors needed)")
        for label, _case, _expect in REPAIR_PLANTS:
            print(f"  [SKIP] repair_lm_head: {label}")
        return []

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "repair_plant.py"
        script.write_text(REPAIR_PLANT, encoding="utf-8")
        for label, case, expect in REPAIR_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] repair_lm_head: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"repair_lm_head plant misbehaved: {label} — {detail[0]}")
    return problems



# --------------------------------------------------------------------------
# shrink_checkpoint.py — the container it writes by hand
#
# The converter assembles a safetensors file itself, because
# `safetensors.torch.save_file` wants every tensor in memory at once and that
# is the problem it exists to solve. A hand-written container is worth nothing
# if the real library cannot read it, so that is the first plant.
#
# ⚠️ `peak_memory_stays_bounded` is the one that guards the *reason* for the
# script. Replacing the streaming write with `save_file` would pass every other
# check here and reintroduce the out-of-memory crash on the owner's machine.
# --------------------------------------------------------------------------

SHRINK_PLANT = r"""
import os, pathlib, resource, sys, tempfile
import torch
from safetensors.torch import save_file
sys.path.insert(0, "scripts")
sys.path.insert(0, "services/translation/src")
import shrink_checkpoint as sc

CASE = sys.argv[1]
torch.manual_seed(20260916)

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    src, dst = str(tmp / "s.safetensors"), str(tmp / "d.safetensors")

    if CASE == "the_real_library_can_read_what_we_wrote":
        tensors = {"shared.weight": torch.randn(64, 8),
                   "lm_head.weight": torch.randn(64, 8) * 7.5}
        save_file(tensors, src)
        sc.convert(src, dst)
        from safetensors import safe_open
        with safe_open(dst, framework="pt") as f:
            ok = sorted(f.keys()) == sorted(tensors)
            for name, original in tensors.items():
                got = f.get_tensor(name)
                ok = ok and got.dtype is torch.bfloat16
                ok = ok and torch.equal(got, original.to(torch.bfloat16))

    elif CASE == "the_output_is_half_the_size":
        save_file({"w": torch.randn(1000, 64)}, src)
        stats = sc.convert(src, dst)
        # float32 -> bfloat16 halves the data; headers differ slightly.
        ok = 0.45 < stats["file_bytes"] / os.path.getsize(src) < 0.55

    elif CASE == "a_corrupted_conversion_is_rejected":
        save_file({"w": torch.randn(200, 8)}, src)
        sc.convert(src, dst)
        raw = bytearray(pathlib.Path(dst).read_bytes())
        raw[-2:] = b"\xff\xff"
        pathlib.Path(dst).write_bytes(raw)
        try:
            sc.verify(src, dst, samples=1)
            ok = False
        except OSError:
            ok = True

    elif CASE == "an_unknown_dtype_is_refused":
        try:
            sc.plan_output(
                {"x": {"dtype": "I64", "shape": [2], "data_offsets": [0, 16]}})
            ok = False
        except sc.UnreadableDtypeError:
            ok = True

    elif CASE == "tensors_are_planned_in_source_offset_order":
        # Read the source front to back rather than seeking over 11.76 GB.
        header = {"z": {"dtype": "F32", "shape": [4], "data_offsets": [64, 80]},
                  "a": {"dtype": "F32", "shape": [16], "data_offsets": [0, 64]}}
        names, _new, _total = sc.plan_output(header)
        ok = names == ["a", "z"]

    elif CASE == "peak_memory_stays_bounded":
        # ⚠️ The reason the script exists. Six 32 MB tensors: a converter that
        # materialised the whole model would grow by ~192 MB, a streaming one
        # by at most one tensor. The ceiling is deliberately loose so this
        # fails on a rewrite, not on allocator noise.
        tensors = {f"t{i}.weight": torch.randn(2_000_000, 4) for i in range(6)}
        save_file(tensors, src)
        del tensors
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        sc.convert(src, dst)
        after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        growth = (after - before) * 1024
        total = os.path.getsize(src)
        ok = growth < total // 2
        if not ok:
            print(f"peak grew {growth} bytes converting {total}", file=sys.stderr)

    elif CASE == "an_unprintable_command_is_not_printed":
        # ⚠️ The runtime half of check_commands.py. If the directory just
        # written does not resolve as a checkpoint, the script must fail rather
        # than print an instruction it never tried -- which is exactly what it
        # did before, and the owner ran the failing command.
        save_file({"w": torch.randn(64, 8)}, src)
        out = tmp / "out"
        def refuse(name):
            # main() resolves the source through this too, so answer for it and
            # refuse only the freshly written output directory.
            if name == src:
                return src
            raise FileNotFoundError("deliberately unresolvable")
        sc.locate_checkpoint = refuse
        code = sc.main(["--model", src, "--out", str(out)])
        ok = code == 1 and (out / "model.safetensors").exists()

    else:
        raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
"""

SHRINK_PLANTS = [
    ("the real safetensors library reads what we wrote by hand",
     "the_real_library_can_read_what_we_wrote", 0),
    ("the output is about half the size",
     "the_output_is_half_the_size", 0),
    ("a corrupted conversion is rejected",
     "a_corrupted_conversion_is_rejected", 0),
    ("an unknown dtype is refused rather than guessed",
     "an_unknown_dtype_is_refused", 0),
    ("tensors are planned in source-offset order",
     "tensors_are_planned_in_source_offset_order", 0),
    ("peak memory stays bounded by one tensor",
     "peak_memory_stays_bounded", 0),
    ("a next command that would fail is not printed",
     "an_unprintable_command_is_not_printed", 0),
]


def run_shrink_plants() -> list[str]:
    try:
        import torch                                       # noqa: F401
        import safetensors                                 # noqa: F401
    except ImportError as exc:
        skipped.append(f"shrink_checkpoint ({exc.name or exc} — torch and "
                       f"safetensors needed)")
        for label, _case, _expect in SHRINK_PLANTS:
            print(f"  [SKIP] shrink_checkpoint: {label}")
        return []

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "shrink_plant.py"
        script.write_text(SHRINK_PLANT, encoding="utf-8")
        for label, case, expect in SHRINK_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] shrink_checkpoint: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"shrink_checkpoint plant misbehaved: {label} — {detail[0]}")
    return problems


# --------------------------------------------------------------------------
# check_environment.py — the readiness report, and the value it must never print
#
# ⚠️ `the_token_value_never_reaches_the_report` is the one that matters. This
# script's output is meant to be pasted into a chat window when setup goes
# wrong, so a token appearing in it travels further than a token in a file.
# It is checked against the REAL printed output, not against the probe.
# --------------------------------------------------------------------------

ENVIRONMENT_PLANT = r"""
import os, subprocess, sys
sys.path.insert(0, "scripts")
sys.path.insert(0, "services/evaluation/src")
sys.path.insert(0, "services/translation/src")
import check_environment as ce

CASE = sys.argv[1]
SECRET = "hf_thisvaluemustnevertravel"

if CASE == "the_token_value_never_reaches_the_report":
    env = dict(os.environ, HF_TOKEN=SECRET)
    r = subprocess.run([sys.executable, "scripts/check_environment.py",
                        "--skip-checkers"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    blob = (r.stdout or "") + (r.stderr or "")
    ok = (SECRET not in blob) and ("HF_TOKEN is set" in blob)

elif CASE == "the_report_is_produced_when_everything_is_missing":
    # ⚠️ The case it exists for. A readiness check that produces nothing on a
    # broken machine is worthless.
    code, lines = ce.collect(environ={}, skip_checkers=True)
    text = "\n".join(lines)
    ok = all(s in text for s in ("required packages", "credentials",
                                 "checkpoints", "python"))

elif CASE == "hornmorpho_absent_is_skip_not_fail":
    # DEC-028: absent is a normal machine, not a failure.
    code, lines = ce.collect(environ={}, skip_checkers=True)
    line = [l for l in lines if " hm " in l][0]
    ok = ("SKIP" in line or "OK" in line) and "FAIL" not in line

elif CASE == "a_missing_model_is_still_ready":
    # Most work here needs no model; failing on it teaches people to ignore
    # the check (DEC-008).
    code, sentence = ce.verdict(True, True, False)
    ok = code == 0 and "except the model" in sentence

elif CASE == "low_memory_is_reported_not_refused":
    # ⚠️ Reported, never a refusal. A readiness check that fails because a
    # browser is open is one people learn to ignore (DEC-008).
    total, available = ce.probe_memory()
    if not total:
        ok = True                       # platform cannot answer; not a failure
    else:
        code, lines = ce.collect(environ={}, skip_checkers=True)
        line = [l for l in lines if l.startswith("  memory")][0]
        ok = ("GB total" in line and "available" in line
              and ce.verdict(True, True, False)[0] == 0)

elif CASE == "a_failing_checker_is_not_ready":
    code, _ = ce.verdict(True, False, True)
    ok = code == 1

else:
    raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
"""

ENVIRONMENT_PLANTS = [
    ("the HF_TOKEN value never reaches the printed report",
     "the_token_value_never_reaches_the_report", 0),
    ("the report is produced when everything is missing",
     "the_report_is_produced_when_everything_is_missing", 0),
    ("HornMorpho absent is SKIP, not FAIL",
     "hornmorpho_absent_is_skip_not_fail", 0),
    ("a missing model is still READY",
     "a_missing_model_is_still_ready", 0),
    ("a failing checker is NOT READY",
     "a_failing_checker_is_not_ready", 0),
    ("low memory is reported, never a refusal",
     "low_memory_is_reported_not_refused", 0),
]


def run_environment_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "environment_plant.py"
        script.write_text(ENVIRONMENT_PLANT, encoding="utf-8")
        for label, case, expect in ENVIRONMENT_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] check_environment: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"check_environment plant misbehaved: {label} — {detail[0]}")
    return problems


# --------------------------------------------------------------------------
# repo_files.py and .gitignore — the repository's own boundary
#
# `check_figures.py` and `check_dates.py` globbed `**/*.py` from the root with
# no virtualenv exclusion. In CI and the sandbox that is invisible; on a machine
# with `.venv/` in the tree it read all of torch and transformers, timed out at
# 180s, and could have reported a retired figure quoted in a third-party
# docstring as a stale claim here.
#
# ⚠️ `a_venv_inside_the_tree_is_not_scanned` is the regression test for that,
# and it builds a real `.venv` rather than trusting the exclusion list.
# --------------------------------------------------------------------------

BOUNDARY_PLANT = r"""
import pathlib, subprocess, sys, tempfile
sys.path.insert(0, "scripts")
import repo_files

CASE = sys.argv[1]
REPO = pathlib.Path(".").resolve()

if CASE == "a_venv_inside_the_tree_is_not_scanned":
    # A file planted inside a .venv must not be returned. Built for real, so
    # this fails if the mechanism changes rather than only if a name changes.
    venv = REPO / ".venv" / "Lib" / "site-packages" / "notmine"
    created = not (REPO / ".venv").exists()
    venv.mkdir(parents=True, exist_ok=True)
    stray = venv / "stray_module.py"
    stray.write_text("# not ours\n", encoding="utf-8")
    try:
        got = repo_files.tracked_files(REPO, ("**/*.py",))
        ok = stray.resolve() not in {p.resolve() for p in got}
    finally:
        stray.unlink()
        if created:
            import shutil
            shutil.rmtree(REPO / ".venv", ignore_errors=True)

elif CASE == "the_fallback_also_excludes_a_venv":
    # ⚠️ git answers today, but the fallback must not be a trapdoor.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "src").mkdir()
        (root / "src" / "mine.py").write_text("x = 1\n", encoding="utf-8")
        (root / ".venv" / "lib").mkdir(parents=True)
        (root / ".venv" / "lib" / "theirs.py").write_text("y = 2\n",
                                                          encoding="utf-8")
        got = repo_files._from_walk(root, ("**/*.py",))
        names = {p.name for p in got}
        ok = "mine.py" in names and "theirs.py" not in names

elif CASE == "the_repository_still_sees_its_own_files":
    # ⚠️ The control. Excluding everything would pass the two plants above and
    # silently stop the checkers from checking anything.
    got = repo_files.tracked_files(REPO, ("**/*.md", "**/*.py"))
    names = {p.name for p in got}
    ok = ("CLAUDE.md" in names and "check_figures.py" in names
          and len(got) > 100)

elif CASE == "a_converted_checkpoint_is_not_committable":
    # ⚠️ Only model.safetensors was ever ignored. tokenizer.json is 16.6 MB and
    # is a .json, and `*.model` never matched because the pattern carried an
    # inline comment that git does not strip.
    target = REPO / "models" / "madlad400-3b-mt-bf16"
    created = not target.exists()
    target.mkdir(parents=True, exist_ok=True)
    checked = ("tokenizer.json", "spiece.model", "config.json",
               "model.safetensors")
    try:
        for name in checked:
            (target / name).touch()
        results = [subprocess.run(
            ["git", "check-ignore", "-q", f"models/madlad400-3b-mt-bf16/{name}"],
            cwd=REPO).returncode for name in checked]
        ok = all(code == 0 for code in results)
    finally:
        if created:
            import shutil
            shutil.rmtree(target, ignore_errors=True)

elif CASE == "the_converter_writes_its_own_gitignore":
    # `--out` can point anywhere, so the directory ignores itself.
    import torch
    from safetensors.torch import save_file
    sys.path.insert(0, "services/translation/src")
    import shrink_checkpoint as sc
    import tigrinya_translate.head as head
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        src = tmp / "model.safetensors"
        save_file({"w": torch.randn(8, 4)}, str(src))
        real = head.locate_checkpoint
        sc.locate_checkpoint = lambda n: str(src) if n == "stub" else real(n)
        sc.main(["--model", "stub", "--out", str(tmp / "out")])
        ignore = tmp / "out" / ".gitignore"
        ok = ignore.is_file() and ignore.read_text(encoding="utf-8").strip().endswith("*")

else:
    raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
"""

BOUNDARY_PLANTS = [
    ("a .venv inside the tree is not scanned",
     "a_venv_inside_the_tree_is_not_scanned", 0),
    ("the fallback walk also excludes a .venv",
     "the_fallback_also_excludes_a_venv", 0),
    ("the repository still sees its own files",
     "the_repository_still_sees_its_own_files", 0),
    ("a converted checkpoint is not committable",
     "a_converted_checkpoint_is_not_committable", 0),
    ("the converter writes its own .gitignore",
     "the_converter_writes_its_own_gitignore", 0),
]


def run_boundary_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "boundary_plant.py"
        script.write_text(BOUNDARY_PLANT, encoding="utf-8")
        for label, case, expect in BOUNDARY_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] repo boundary: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"repo boundary plant misbehaved: {label} — {detail[0]}")
    return problems

# --------------------------------------------------------------------------
# check_commands.py — the instructions a human follows by hand
#
# Every other claim in this repository was enforced: figures, dates, derived
# counts, planted behaviour. The commands it *prints* were not, and two of them
# did not work — one of them the error message shown at the exact moment a user
# needs the right answer (`hm.download('ti')`, A-20), and one a `--verify` flag
# that no script has ever defined.
#
# ⚠️ The negative cases matter more than usual here. A checker that flagged
# every `--flag` it saw would fire on `--write`, `--check` and `--list`, all of
# which are real, and would be switched off the same day.
# --------------------------------------------------------------------------

COMMAND_PLANTS = [
    # The two defects that prompted this, restored verbatim.
    ("a flag no script declares",
     "\n\nRun `python data/anchors/tico19/fetch.py --verify` to check.\n", 1),
    ("a script path that resolves nowhere",
     "\n\nRun `python scripts/check_nothing.py --list` first.\n", 1),
    # Negative cases: every one of these is a real, working command today.
    ("a real flag on a repo-root path", "\n\n`python scripts/check_dates.py --list`\n", 0),
    ("a real flag on a script beside the document",
     "\n\n`python3 scripts/check_figures.py --list`\n", 0),
    ("a flag that is argparse's own", "\n\n`python scripts/check_dates.py --help`\n", 0),
    ("untouched control", "", 0),
]


def run_command_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "repo"
        shutil.copytree(REPO, work,
                        ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                      ".pytest_cache"))
        target = work / "docs" / "vision" / "goals.md"
        original = target.read_text(encoding="utf-8")
        for label, plant, expect in COMMAND_PLANTS:
            target.write_text(original + plant, encoding="utf-8")
            r = subprocess.run([sys.executable, "scripts/check_commands.py"],
                               cwd=work, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] check_commands: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"check_commands plant misbehaved: {label} — {detail[0]}")
    return problems

# --------------------------------------------------------------------------
# The whole Windows text-encoding class
#
# Two of these scripts were reported crashing on Windows, and both were the
# same defect: text I/O with no explicit encoding, which uses the **locale
# default** — UTF-8 on Linux, cp1252 on Windows. Fixing the eighteen call
# sites is not the fix; this is. It reruns the entry points with an ASCII
# default, which is *stricter* than cp1252, so anything Windows would reject
# is rejected here too and CI catches the regression on Linux.
#
# ⚠️ `LC_ALL=C` alone is not enough. PEP 538 coerces the C locale to C.UTF-8
# and PEP 540 has a UTF-8 mode, so Python quietly hands back UTF-8 anyway and
# the plant would pass on every input — the very failure this file exists to
# catch. `PYTHONCOERCECLOCALE=0`, `PYTHONUTF8=0` and an unset
# `PYTHONIOENCODING` are each required; together they were verified to yield
# `ANSI_X3.4-1968`, and the write plant aborts loudly if they ever stop.
#
# The two halves are tested separately and both are needed:
#   - **printing** — the three checkers emit `⚠️` and `—` into a pipe;
#   - **writing**  — `Harness.save()` writes Ge'ez to a file.
# --------------------------------------------------------------------------

ASCII_ENV = {"PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0",
             "LC_ALL": "C", "LANG": "C", "LC_CTYPE": "C"}

#: Set in the child when this suite re-runs *itself* under ASCII, so the
#: re-run does not re-run itself for ever.
ASCII_PASS = "TIGRINYA_PLANTS_ASCII_PASS"

#: Written to a temp file rather than passed with `-c`: under an ASCII locale
#: Python decodes a `-c` argument with the filesystem encoding, so Ge'ez on the
#: command line would fail for a reason that has nothing to do with the code
#: under test. A `.py` file is UTF-8 by default whatever the locale is.
ENCODING_WRITE_PLANT = r'''
"""Round-trip Ge'ez through Harness.save() with no UTF-8 anywhere in the env.

PRINTS ASCII ONLY, on purpose. The *printing* half of this defect is covered
by running the real checkers; this plant isolates the *writing* half, and a
print failure here would mask it.
"""
import json, locale, pathlib, sys, tempfile

if locale.getpreferredencoding(False).lower().replace("-", "") in (
        "utf8", "cp65001"):
    print("ABORT: the locale is still UTF-8, so this plant proves nothing")
    sys.exit(3)

from tigrinya_eval.harness import EvalSet, Harness

GEEZ = ["ሰላም ዓለም"]           # "selam alem"
EM_DASH = "—"

h = Harness()
h.evaluate("plant", GEEZ, EvalSet("plant", "unknown", GEEZ), notes=(EM_DASH,))

with tempfile.TemporaryDirectory() as tmp:
    out = pathlib.Path(tmp) / "r.json"
    h.save(out)                      # UnicodeEncodeError here if unfixed
    back = json.loads(out.read_text(encoding="utf-8"))

assert back["results"][0]["notes"] == [EM_DASH], back
print("OK: non-ASCII round-tripped under", locale.getpreferredencoding(False))
'''

#: (label, argv after the interpreter, expected exit). `None` marks the case
#: that runs ENCODING_WRITE_PLANT from a temp file.
ENCODING_PLANTS = [
    ("check_dates.py prints under an ASCII locale",       ["scripts/check_dates.py"], 0),
    ("check_figures.py prints under an ASCII locale",     ["scripts/check_figures.py"], 0),
    ("check_definitions.py prints under an ASCII locale", ["scripts/check_definitions.py"], 0),
    ("Harness.save() writes Ge'ez under an ASCII locale", None, 0),
    # ⚠️ The one that matters, and the one that was missing. The four above are
    # a HAND-WRITTEN LIST, and a hand-written list is exactly what failed: it
    # did not name `measure_morphology`, which imports nothing of the sort but
    # is reached through `mm.main()` from HARNESS_PLANT — so five plants went on
    # failing on Windows while this group reported the class closed.
    #
    # This entry needs no list. It re-runs *every* plant under ASCII and
    # requires identical behaviour, which reproduces those five failures and
    # nothing else. Whatever is planted next is covered the day it is added.
    ("every plant behaves identically under an ASCII locale", [__file__], 0),
]


def run_encoding_plants() -> list[str]:
    problems = []
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)          # would defeat the whole check
    env.update(ASCII_ENV)
    env[ASCII_PASS] = "1"

    #: True when we ARE the ASCII re-run. Everything still runs; only the entry
    #: that would spawn another copy of this file is held back.
    inner = bool(os.environ.get(ASCII_PASS))

    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "encoding_plant.py"
        script.write_text(ENCODING_WRITE_PLANT, encoding="utf-8")
        for label, argv, expect in ENCODING_PLANTS:
            if inner and argv == [__file__]:
                skipped.append(label)
                print(f"  [SKIP] ascii-locale: {label} — this IS the ASCII "
                      f"re-run; nesting it would not terminate")
                continue
            argv = [str(script)] if argv is None else argv
            r = subprocess.run([sys.executable, *argv], cwd=REPO, env=env,
                               capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] ascii-locale: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"ascii-locale plant misbehaved: {label} — {detail[0]}")
    return problems


def main() -> int:
    problems = (run_screen_plants() + run_figure_plants()
                + run_morphology_plants() + run_harness_plants()
                + run_translate_plants() + run_repair_plants()
                + run_shrink_plants() + run_environment_plants()
                + run_boundary_plants()
                + run_command_plants() + run_encoding_plants())
    print()
    for p in problems:
        print(f"::error::{p}")
    if problems:
        print(f"{len(problems)} planted failure(s) did not behave as specified — "
              f"a check has stopped being able to fail")
        return 1
    # Summed by convention rather than by name, so a fifth *_PLANTS list is
    # counted here the day it is added. `docs/figures.json` derives the same
    # number the same way; listing the four names in both places is how the
    # printed total and the documented one would quietly come to disagree.
    total = sum(len(v) for k, v in sorted(globals().items())
                if k.endswith("_PLANTS") and isinstance(v, list))
    if skipped:
        print(f"{total - len(skipped)} of {total} planted cases behaved as "
              f"specified; {len(skipped)} NOT RUN — {', '.join(skipped)}")
        return 0
    print(f"all {total} planted cases behaved as specified")
    return 0


if __name__ == "__main__":
    # ⚠️ Windows writes to a pipe or a redirect with the locale codec
    # (cp1252), not the console's. Without this, printing `⚠️` or `—`
    # raises UnicodeEncodeError — including while printing a traceback.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
