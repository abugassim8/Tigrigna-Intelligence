#!/usr/bin/env python3
"""Translate TICO-19 English into Tigrinya, score it, and produce a judgement sheet.

What this answers
-----------------
**Whether the tool is possible at all.** The product is English → Tigrinya
health information; TICO-19 is COVID/medical prose with an English source and
three independent Tigrinya references, so the anchor already committed here is
the right one rather than a convenient one.

⚠️ **No model had ever been loaded in this project before this script.** Eleven
experiments, a measurement harness and twenty-nine decisions were built around
scoring a translation system, and none had ever scored one.

Why MADLAD and not NLLB
-----------------------
**DEC-011.** Every NLLB variant is CC-BY-NC-4.0 and is quarantined to research
and comparison use, *never present in a shipped artefact*. NLLB is behind
essentially every published Tigrinya MT number, which makes it the tempting
default and the one a tool real people use may not be built on.
`google/madlad400-3b-mt` is Apache-2.0, covers `ti`, and DEC-011 chose it while
recording that its **Tigrinya quality is unmeasured**. This measures it.

What the number means, and what it does not
-------------------------------------------
chrF is reported per reference and **never averaged across varieties** —
DEC-010, and `Harness.aggregate()` refuses anyway. `tir_er` and `tir_et` are
different varieties *and* different translators.

⚠️ **chrF is not the finding.** Experiment 011 measured two professional human
translators agreeing with each other at **chrF ≈ 24** on this exact data, so the
scale is not the one intuition suggests. The finding is the **judgement sheet**:
how many of 100 segments a Tigrinya speaker calls usable. The threshold is
pre-committed below, before any output exists.

Reproducibility
---------------
Greedy decoding (`num_beams=1`, `do_sample=False`) and a seeded sample, so a
re-run on the same machine reproduces. This is **not** a DEC-016 experiment:
CI runs every `experiments/*/run.py` and cannot download a 12 GB model. It
follows `measure_morphology.py` instead — heavy dependency, artefact committed
under `docs/benchmarks/measurements/`, recipe documented.

⚠️ **Run `--smoke` first.** It translates three segments and prints them, with
no scoring and no files. The first real run spent 46 minutes to discover the
output was not Tigrinya; a minute would have shown the same thing.

Usage:
    python3 scripts/translate_tico19.py --self-test     # no model, no network
    python3 scripts/translate_tico19.py --diagnose      # Tigrinya + controls
    python3 scripts/translate_tico19.py --smoke         # 3 segments, printed
    python3 scripts/translate_tico19.py --json PATH     # the real run

A long run **checkpoints** to `PATH.partial.json` after every batch and resumes
from it; `--no-resume` starts over. A rejected run's output is preserved to
`PATH-REJECTED.json`, which carries no score and is never read by the scoring
path.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import os
import pathlib
import random
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
for _pkg in ("evaluation", "primitives", "translation"):
    sys.path.insert(0, str(REPO / "services" / _pkg / "src"))

from tigrinya_eval.harness import EvalSet, Harness                # noqa: E402
from tigrinya_eval.primitives import force_utf8_stdio, is_ethiopic  # noqa: E402
from tigrinya_translate.head import looks_degenerate            # noqa: E402
from tigrinya_translate import (LANGUAGE_TOKEN, MODEL,            # noqa: E402
                                SegmentCountError, translate_all)

#: Pre-committed, before any translation existed. Recorded in the artefact so
#: the threshold cannot be chosen after the result is known.
#:
#: 40 comes from experiment 011: two professional human translators agree at
#: chrF ≈ 24 on this data, so demanding near-perfect machine output is not
#: reasonable. But under half the segments usable is not something prompting
#: fixes, and the honest response is DEC-017's ladder with a measured reason.
USABLE_THRESHOLD = 40

#: What "usable" means, fixed before judging rather than after. Health
#: information specifically: being misled about a dose is a different kind of
#: failure from being read clumsy prose.
USABLE_DEFINITION = (
    "A Tigrinya speaker would come away with the correct instruction, and "
    "would not be misled about a dose, a symptom, or a risk. Clumsy or "
    "unidiomatic phrasing is still usable. A wrong number, a negation flipped, "
    "or an invented instruction is not."
)

#: `dev`, never `test`. The test split stays held out; experiment 011 already
#: had to record three figures as `already_seen_on_test` for looking once.
SPLIT = "dev"
SAMPLE_SIZE = 100
SEED = 20260915

#: DEC-010: scored separately, never combined. These differ by translator AND
#: by variety at once, which A-13 is what would separate.
REFERENCES = {"tir_er": "eritrean", "tir_et": "ethiopian"}

CHECKPOINT_EVERY = 10

#: Below this share of non-empty output segments containing Ethiopic script,
#: the model was not emitting Tigrinya and the run is void.
#:
#: ⚠️ It **aborts and writes nothing**, exactly as `measure_morphology.py` does
#: on a non-deterministic analyser. Printing `::error::` and exiting 0 would
#: leave a scored artefact on disk describing a translation into some other
#: language — and every downstream check would pass it, because the shape,
#: the segment count and the chrF are all perfectly well-formed.
#:
#: Not 1.0: a handful of TICO-19 segments are bare numerals or URLs, and a
#: correct translation of those contains no Ethiopic at all.
ETHIOPIC_ABORT_FRACTION = 0.5

#: Fraction of degenerate segments at which the run is refused.
#:
#: ⚠️ Lower than the script floor on purpose. Wrong script can mean "this model
#: is poor at Tigrinya", which is a finding. Repeated-token output can only
#: mean the model is broken, so a quarter of them is already conclusive.
DEGENERATE_ABORT_FRACTION = 0.25


class AlreadyRejectedError(RuntimeError):
    """This exact run has already been rejected, so re-running learns nothing."""


class WrongLanguageError(RuntimeError):
    """The output is not Tigrinya, so nothing about the score means anything."""


def _anchor(name: str) -> list[str]:
    path = REPO / "data" / "anchors" / "tico19" / f"{SPLIT}.{name}.txt"
    return [ln for ln in path.read_text(encoding="utf-8").split("\n") if ln.strip()]


def sample_indices(total: int) -> list[int]:
    """A seeded sample, recorded in the artefact so the run is reproducible."""
    rng = random.Random(SEED)
    return sorted(rng.sample(range(total), min(SAMPLE_SIZE, total)))


def write_sheet(path: pathlib.Path, ids: list[int], english: list[str],
                tigrinya: list[str]) -> None:
    """The blind judgement sheet — the only part a machine cannot do.

    ⚠️ **The human reference is deliberately absent.** Including it turns "is
    this usable health information" into "does this match the other
    translation", which is a different question and the one chrF already
    answers. The references are used for scoring and are never shown here.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "english", "machine_tigrinya", "usable", "note"])
        for i, en, ti in zip(ids, english, tigrinya):
            w.writerow([i, en, ti, "", ""])


def _model_of(translator) -> str:
    """The model this translator was actually built for.

    ⚠️ Read from the translator, never from the module constant. Eight places
    here used `MODEL` directly, so pointing `--model` at the converted
    checkpoint would have loaded one model and recorded another — a provenance
    lie in a file whose whole purpose is provenance.
    """
    return getattr(translator, "model_name", None) or MODEL


def _source_model(translator) -> str:
    """What the loaded checkpoint *is*, independent of where it sits on disk.

    ⚠️ A bfloat16 copy made by `scripts/shrink_checkpoint.py` holds weights
    bit-identical to what the loader produces from the float32 original, so the
    two are the **same measurement**. Both resolve to the same id here, which
    is what keeps a rejected run blocked no matter which file it is re-run from.
    """
    name = _model_of(translator)
    try:
        from tigrinya_translate.head import locate_checkpoint, source_model_id
        return source_model_id(locate_checkpoint(name), name)
    except Exception:                                     # noqa: BLE001
        return name


def _environment(translator=None) -> dict:
    """What actually ran, read from the imported modules.

    ⚠️ **Never from `pyproject.toml`.** The pinned range and the installed build
    are different facts, and the gap between them is a live suspect: the first
    wrong-language run was `transformers` 5.17.0 loading a checkpoint written
    for 4.23.1, which printed a tied-weights warning about `shared.weight` and
    `decoder.embed_tokens.weight` holding different values.

    Recorded on the measurement *and* on the rejected file, because a rejected
    run whose environment is unknown cannot be diagnosed — which is exactly the
    position the second run left us in.
    """
    env = {"python": sys.version.split()[0], "platform": sys.platform}
    for name in ("transformers", "torch"):
        try:
            env[name] = __import__(name).__version__
        except Exception:                                 # noqa: BLE001
            env[name] = None
    if translator is not None:
        env["dtype"] = getattr(translator, "dtype", None)
        env["language_token"] = getattr(translator, "language_token", None)
        # ⚠️ Whether the output projection had to be repaired at load time.
        # A score from a repaired model and a score from an intact one are not
        # the same measurement, and an artefact that does not say which it is
        # cannot be compared with another one.
        env["head_state"] = getattr(translator, "head_state", None)
        env["head_repaired"] = getattr(translator, "head_repaired", None)
        env["head_source"] = getattr(translator, "head_source", None)
        # ⚠️ Which file was opened, not which name was typed. A run from the
        # Hugging Face cache and a run from models/madlad400-3b-mt-bf16 were
        # previously indistinguishable in the artefact.
        env["model_name"] = _model_of(translator)
        env["source_model"] = _source_model(translator)
        try:
            from tigrinya_translate.head import (locate_checkpoint,
                                                 read_safetensors_metadata)
            path = locate_checkpoint(env["model_name"])
            env["checkpoint"] = path
            env["checkpoint_bytes"] = os.path.getsize(path)
            env["converted_from"] = read_safetensors_metadata(path).get(
                "converted_from")
        except Exception as exc:                          # noqa: BLE001
            env["checkpoint"] = f"unresolved: {type(exc).__name__}"
            env["checkpoint_bytes"] = None
            env["converted_from"] = None
    return env


def _rejected_path(out_json: pathlib.Path | None) -> pathlib.Path | None:
    return (None if out_json is None
            else out_json.with_name(f"{out_json.stem}-REJECTED.json"))


def _previously_rejected(out_json: pathlib.Path | None,
                         fingerprint: str) -> dict | None:
    """The record of this exact run having already been rejected, if any.

    ⚠️ Matched on the **fingerprint**, never the filename. A changed seed,
    sample size or model is a different run and must not be blocked — a check
    that fires on everything gets deleted within a week, which is the failure
    DEC-008 exists to prevent.
    """
    path = _rejected_path(out_json)
    if path is None or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if data.get("fingerprint") == fingerprint else None


def _fingerprint(source: list[str], model: str, *, dtype: str = "",
                 language_token: str = "", head: str = "") -> str:
    """Identify *this* run, so a resume cannot stitch two different ones.

    ⚠️ Without it, changing SEED, SAMPLE_SIZE or the model and re-running would
    silently graft old hypotheses onto a new sample. The result would be
    perfectly well-formed and completely wrong — the same failure shape as the
    language gate, one layer up.

    ⚠️ **Everything that changes the output belongs here**, and three things
    were missing. `dtype` changes the arithmetic, so a float32 run is not the
    run a bfloat16 run was rejected for. `language_token` picks the target
    language. And `head` records whether the output projection had to be
    repaired — the wrong-language rejections of 2026-09-15 and 2026-09-16 were
    produced by a model whose trained `lm_head` had been discarded by the
    loader, so they must not block a run on a repaired model. Without that the
    first correct measurement would have been refused as a known failure.

    ⚠️ `model` must be the **source** id (`_source_model`), not a path: a
    converted bfloat16 copy holds bit-identical weights and is the same run.
    """
    h = hashlib.sha256(model.encode("utf-8"))
    for extra in (dtype, language_token, head):
        h.update(b"\x1f")
        h.update(extra.encode("utf-8"))
    for line in source:
        h.update(b"\x00")
        h.update(line.encode("utf-8"))
    return h.hexdigest()[:16]


def _partial_path(out_json: pathlib.Path | None) -> pathlib.Path | None:
    return None if out_json is None else out_json.with_suffix(".partial.json")


def _load_partial(path: pathlib.Path | None, fingerprint: str) -> list[str]:
    """Hypotheses already translated for *this exact* run, or nothing."""
    if path is None or not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if data.get("fingerprint") != fingerprint:
        return []
    got = data.get("hypotheses")
    return got if isinstance(got, list) else []


def _save_partial(path: pathlib.Path | None, fingerprint: str,
                  hypotheses: list[str]) -> None:
    """Write-then-replace, so an interruption mid-write cannot corrupt it."""
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(
        {"fingerprint": fingerprint, "hypotheses": hypotheses,
         "warning": "partial run, not a measurement"},
        ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _write_rejected(out_json: pathlib.Path | None, reason: str,
                    source: list[str], hypotheses: list[str],
                    ids: list[int], fingerprint: str = "",
                    translator=None) -> pathlib.Path | None:
    """Preserve a rejected run's output so it can be diagnosed.

    ⚠️ **Never at the `--json` path, and never scored.** The first real run
    produced 100 translations in 46 minutes, was correctly rejected for being
    in the wrong language, and then discarded the only evidence that could
    explain why. Refusing to record a *measurement* was right; throwing away the
    *output* was not.

    The name and the `is_a_measurement: false` field are both deliberate: this
    file must be impossible to mistake for a result, and nothing in the scoring
    path reads it.
    """
    path = _rejected_path(out_json)
    if path is None:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "is_a_measurement": False,
        "warning": ("REJECTED RUN. Kept only so the failure can be diagnosed. "
                    "It carries no score and must never be presented as one."),
        "reason": reason,
        "rejected_on": datetime.date.today().isoformat(),
        # Re-running this exact sample is blocked on the strength of this field.
        "fingerprint": fingerprint,
        "environment": _environment(translator),
        "model": _model_of(translator),
        "language_token": LANGUAGE_TOKEN,
        "segment_ids": ids,
        "pairs": [{"id": i, "english": e, "output": h}
                  for i, e, h in zip(ids, source, hypotheses)],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def measure(translator, *, out_json: pathlib.Path | None,
            out_sheet: pathlib.Path | None, limit: int | None = None,
            quiet: bool = False, resume: bool = True,
            force: bool = False) -> dict:
    """Translate, score per reference, and emit the artefact.

    `translator` is injected so this whole function is exercised without a
    model — the same reason `measure_morphology.py` takes an analyser.
    """
    english = _anchor("eng")
    refs = {name: _anchor(name) for name in REFERENCES}

    lengths = {"eng": len(english), **{k: len(v) for k, v in refs.items()}}
    if len(set(lengths.values())) != 1:
        print(f"::error::the anchor files disagree on length: {lengths}. "
              f"Segments are paired by position, so scoring would compare "
              f"unrelated sentences.")
        raise SystemExit(2)

    ids = sample_indices(len(english))
    if limit is not None:
        ids = ids[:limit]
    source = [english[i] for i in ids]

    model_name = _model_of(translator)
    fingerprint = _fingerprint(
        source, _source_model(translator), dtype=str(
            getattr(translator, "dtype", "")),
        language_token=str(getattr(translator, "language_token",
                                   LANGUAGE_TOKEN)),
        head=str(getattr(translator, "head_state", "")))

    # ------------------------------------------- already rejected once?
    #
    # ⚠️ Decoding here is greedy and the sample is seeded, so re-running an
    # identical fingerprint reproduces an identical failure. The second
    # wrong-language run cost ninety minutes to learn nothing, because the
    # rejected file recorded the failure and nothing read it.
    if not force:
        prior = _previously_rejected(out_json, fingerprint)
        if prior is not None:
            raise AlreadyRejectedError(
                f"this exact run was rejected on {prior.get('rejected_on', '?')}:\n"
                f"    {prior.get('reason', 'no reason recorded')}\n"
                f"  Same seed, same segments, same model, greedy decoding — it "
                f"will reproduce that failure exactly.\n"
                f"  Run `--diagnose` instead: it translates into Tigrinya AND "
                f"control languages on one model load, in about four minutes.\n"
                f"  Pass `--force` if the cause has actually been fixed.\n"
                f"  The previous output is in {_rejected_path(out_json).name}; "
                f"it ran under {prior.get('environment', {})}."
            )

    if not quiet:
        print(f"  {len(ids)} segment(s) sampled from {SPLIT} "
              f"(seed {SEED}, of {len(english)})")
        print(f"  model: {model_name}")
        env = _environment(translator)
        print(f"  transformers {env.get('transformers')}, torch "
              f"{env.get('torch')}, dtype {env.get('dtype')}")
        # ⚠️ State the cost BEFORE spending it. The first two runs each cost
        # most of an hour to reach a conclusion a one-minute command reaches.
        print(f"\n  ⚠️ this is the expensive path: roughly "
              f"{len(ids) * 30 // 60}-{len(ids) * 55 // 60} minutes on CPU.")
        print(f"     --smoke is about a minute, --diagnose about four.")
        print(f"  ⚠️ pre-committed: fewer than {USABLE_THRESHOLD} of "
              f"{len(ids)} usable retires this approach\n")

    started = time.time()

    # ---------------------------------------------------------- checkpointing
    #
    # ⚠️ Added after a 46-minute run was thrown away. The run was correctly
    # rejected — the output was not Tigrinya — but there was nothing on disk
    # afterwards, so the failure could not be diagnosed without paying the 46
    # minutes again. Neither the partial file nor the rejected file is a
    # measurement; both exist so a failure costs minutes instead of an hour.
    partial = _partial_path(out_json)
    done_already = _load_partial(partial, fingerprint) if resume else []
    done_already = done_already[:len(source)]
    remaining = source[len(done_already):]

    if done_already and not quiet:
        print(f"  resuming: {len(done_already)} of {len(source)} already "
              f"translated, from {partial.name}\n")

    def progress(done: int, total: int) -> None:
        if quiet or (done + len(done_already)) % CHECKPOINT_EVERY:
            return
        rate = (time.time() - started) / max(done, 1)
        print(f"    {done + len(done_already)}/{len(source)}  "
              f"~{rate * (total - done) / 60:.0f} min left")

    def checkpoint(so_far: list[str]) -> None:
        _save_partial(partial, fingerprint, done_already + so_far)

    try:
        hypotheses = done_already + translate_all(
            remaining, translator, progress=progress, checkpoint=checkpoint)
    except SegmentCountError as exc:
        _write_rejected(out_json, str(exc), source[:len(done_already)],
                        done_already, ids[:len(done_already)], fingerprint,
                        translator)
        raise

    # ------------------------------------------------ did it emit Tigrinya?
    #
    # ⚠️ A model given an unrecognised language token emits fluent text in the
    # wrong language, with the right segment count and a scoreable chrF. The
    # token check in MadladTranslator is the first line of defence; this is the
    # second, and it is the one that works for any translator.
    # `is_ethiopic` is per-CHARACTER — the same spelling `morphology._main`
    # uses at line 510 to pick Tigrinya lines out of a mixed corpus. There are
    # five copies of this predicate in the repository and `check_definitions.py`
    # exists because two of them once disagreed, so it is reused, never
    # reimplemented here.
    def has_ethiopic(text: str) -> bool:
        return any(is_ethiopic(c) for c in text)

    ethiopic = sum(1 for h in hypotheses if has_ethiopic(h))
    empty = sum(1 for h in hypotheses if not h.strip())

    non_empty = len(hypotheses) - empty

    def reject(reason: str) -> None:
        where = _write_rejected(out_json, reason, source, hypotheses, ids,
                                fingerprint, translator)
        if where and not quiet:
            print(f"\n  output preserved for diagnosis: {where}")
            print(f"  ⚠️ that file carries NO score and is not a measurement.")
        raise WrongLanguageError(reason)

    if not non_empty:
        # ⚠️ Caught by a plant, not by review. The fraction test below reads
        # `ethiopic / non_empty`, so it was guarded with `if non_empty` — which
        # silently skipped the whole check when the model returned nothing at
        # all. chrF of empty against a reference is 0.00, and the artefact would
        # have recorded the strongest possible failure as "terrible quality".
        reject(
            f"every one of {len(hypotheses)} output segment(s) is empty. The "
            f"model produced no text, which scores chrF 0.00 and would be "
            f"recorded as poor translation rather than as no translation. "
            f"Writing no measurement."
        )
    # ⚠️ **Degenerate output: one token repeated to the limit.** Every failure
    # this project has had took that shape — `Sally Hansen` nine times, a
    # single Ge'ez-adjacent glyph thirty-two times, Syriac to the token limit —
    # and nothing noticed, because degenerate output has the right segment
    # count and a real chrF. The script check below would not catch it either:
    # repeated *Ethiopic* would sail straight through.
    degenerate = sum(1 for h in hypotheses if looks_degenerate(h))
    if degenerate and degenerate / non_empty >= DEGENERATE_ABORT_FRACTION:
        worst = next(h for h in hypotheses if looks_degenerate(h))
        reject(
            f"{degenerate} of {non_empty} non-empty output segment(s) are a "
            f"repeated token rather than a translation, at or above the "
            f"{DEGENERATE_ABORT_FRACTION:.0%} floor. The model is broken, not "
            f"bad at Tigrinya. Run `--diagnose` and read the CONTROL languages "
            f"first.\n"
            f"  example: {ascii(worst[:80])}\n"
            f"  Writing no measurement."
        )

    if ethiopic / non_empty < ETHIOPIC_ABORT_FRACTION:
        reject(
            f"only {ethiopic} of {non_empty} non-empty output segment(s) "
            f"contain Ethiopic script, below the {ETHIOPIC_ABORT_FRACTION:.0%} "
            f"floor. The model was not emitting Tigrinya.\n"
            f"  ⚠️ Do NOT re-run this command — it is deterministic and will "
            f"fail identically. Run `--diagnose`: it translates the same "
            f"segments into Tigrinya AND control languages on one model load, "
            f"which is what separates a broken pipeline from a finding about "
            f"this model's Tigrinya.\n"
            f"  (LANGUAGE_TOKEN is not the suspect: '{LANGUAGE_TOKEN}' was "
            f"verified against the model's own tokenizer.json on 2026-09-15.)\n"
            f"  Writing no measurement: a scored artefact for the wrong "
            f"language would pass every check in this repository."
        )

    harness = Harness()
    for name, variety in REFERENCES.items():
        harness.evaluate(
            system=model_name,
            hypotheses=hypotheses,
            eval_set=EvalSet(name=f"tico19.{SPLIT}.{name}", variety=variety,
                             references=[refs[name][i] for i in ids],
                             source="TICO-19", licence="CC0-1.0"),
            # DEC-011: MADLAD is Apache-2.0, so unlike every NLLB number in the
            # literature this one describes something that could be shipped.
            shippable=True,
            notes=(f"greedy decoding; sample seed {SEED}",),
        )

    out = {
        "measurement": "translation-en-ti",
        "model": model_name,
        "licence": "Apache-2.0",
        "direction": "English -> Tigrinya",
        "split": SPLIT,
        "seed": SEED,
        "segment_ids": ids,
        "decoding": {"num_beams": 1, "do_sample": False},
        "pre_committed": {
            "usable_threshold": USABLE_THRESHOLD,
            "of": len(ids),
            "definition": USABLE_DEFINITION,
            "reference_point": (
                "Experiment 011: two professional human translators agree with "
                "each other at chrF 23.84 (dev) on this same data. chrF here is "
                "not on the scale intuition suggests."
            ),
        },
        "output_shape": {
            "segments": len(hypotheses),
            "ethiopic": ethiopic,
            "not_ethiopic": len(hypotheses) - ethiopic,
            "empty": empty,
        },
        "scores": {r.eval_set: r.to_dict() for r in harness.results},
        "elapsed_seconds": round(time.time() - started, 1),
        # ⚠️ A measurement stitched from two sessions is not the same
        # evidence as one clean pass, so it says so.
        "resumed_from_partial": len(done_already) or False,
        "environment": _environment(translator),
        "judgement": "PENDING — the sheet has not been returned",
    }

    if not quiet:
        print()
        for r in harness.results:
            print(f"  {r.eval_set:28} chrF {r.scores.chrf.score:6.2f}  "
                  f"({r.variety})")
        if ethiopic != len(hypotheses):
            print(f"\n  ⚠️ {len(hypotheses) - ethiopic} of {len(hypotheses)} "
                  f"output segment(s) contain no Ethiopic script. Above the "
                  f"{ETHIOPIC_ABORT_FRACTION:.0%} floor so the run stands, but "
                  f"look at them before trusting the scores.")

    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        if not quiet:
            print(f"\n  wrote {out_json}")

    if partial is not None and partial.is_file():
        partial.unlink()          # the run completed; the crutch is spent

    if out_sheet:
        write_sheet(out_sheet, ids, source, hypotheses)
        if not quiet:
            print(f"  wrote {out_sheet}  ← mark `usable` as y/n, then send it back")

    return out


def smoke(translator, n: int = 3, quiet: bool = False) -> list[str]:
    """Translate `n` segments and print them. No scoring, no files, no gates.

    ⚠️ **This is the thing that should have existed before the first full run.**
    The only path from "model loaded" to "see output" was a 100-segment,
    46-minute measurement. It failed, and the failure cost an hour to observe
    something a minute would have shown.

    ⚠️ It deliberately does **not** check the output or abort. Its entire job is
    to show what the model actually said, *including* when that is wrong — a
    diagnostic that hides the symptom is worthless.

    It routes through the same `translate_all` and the same translator as the
    real run. A smoke test that built its own prompt would stop testing the
    thing it is supposed to de-risk.

    ⚠️ Forces UTF-8 stdio itself. It prints Ge'ez, and it is reachable by
    import, so the `main()` guard does not cover it — the same rule that put
    `force_utf8_stdio()` inside entry FUNCTIONS rather than `__main__` blocks.
    """
    force_utf8_stdio()
    english = _anchor("eng")
    ids = sample_indices(len(english))[:n]
    source = [english[i] for i in ids]

    out = translate_all(source, translator)

    if not quiet:
        token = getattr(translator, "language_token", LANGUAGE_TOKEN)
        print(f"  {_model_of(translator)}  {token}\n")
        for i, en, ti in zip(ids, source, out):
            geez = sum(1 for c in ti if is_ethiopic(c))
            print(f"  [{i}] en: {en}")
            print(f"       ti: {ti}")
            print(f"           {geez} Ethiopic char(s) of {len(ti)}\n")
        print("  ⚠️ Nothing was scored and nothing was written. Look at the "
              "output above before running the full measurement.")
    return out


#: The control languages, and why each one is here.
#:
#: ⚠️ A diagnostic with no control cannot tell "my pipeline is broken" from
#: "this model's Tigrinya is poor", and those need opposite responses.
#:
#:   - `<2am>` Amharic — **the sharp one.** Same Ge'ez script, far more
#:     training data. Ge'ez for Amharic but not Tigrinya isolates the problem
#:     to Tigrinya *coverage* rather than to generating the script at all.
#:   - `<2es>` Spanish — high-resource, Latin script. If this fails too, the
#:     fault is the pipeline: precision, tokenizer, or weight loading.
CONTROL_LANGUAGES = ("<2ti>", "<2am>", "<2es>")


def diagnose(translator, n: int = 3, languages=CONTROL_LANGUAGES) -> dict:
    """Translate the same segments into several languages, and show the prompts.

    ⚠️ **One model load.** Reloading 11.8 GB per language to compare three of
    them would take longer than the failure it is diagnosing.

    Writes nothing, scores nothing, never aborts — same contract as `--smoke`.
    A diagnostic that hides the symptom is worthless.

    ⚠️ Forces UTF-8 stdio for the same reason `smoke()` does: it prints Ge'ez
    and the metaspace marker `\u2581`, and on Windows a child writing to a pipe
    encodes with cp1252 whatever the console is.
    """
    force_utf8_stdio()
    print("=" * 72)
    print("DIAGNOSTIC — not a measurement, nothing is written or scored")
    print("=" * 72)

    tok = None
    try:
        tok, _ = translator._loaded
    except Exception as exc:                              # noqa: BLE001
        print(f"  could not reach the tokenizer: {type(exc).__name__}: {exc}")

    if tok is not None:
        probe = f"{LANGUAGE_TOKEN} Wash your hands often."
        print(f"\n  prompt: {probe!r}")
        try:
            pieces = tok.tokenize(probe)
            print(f"  fast tokenizer: {pieces}")
            # ⚠️ The model card uses the SLOW T5Tokenizer. If the two disagree
            # about `<2ti>`, that difference is the whole bug.
            from transformers import T5Tokenizer
            slow = T5Tokenizer.from_pretrained(_model_of(translator))
            print(f"  slow tokenizer: {slow.tokenize(probe)}")
        except Exception as exc:                          # noqa: BLE001
            print(f"  tokenizer comparison unavailable: "
                  f"{type(exc).__name__}: {exc}")

    results = {}
    for token in languages:
        print(f"\n{'-' * 72}\n  {token}\n{'-' * 72}")
        try:
            translator.use_language(token)
        except Exception as exc:                          # noqa: BLE001
            print(f"  REFUSED: {type(exc).__name__}: {exc}")
            results[token] = None
            continue
        out = smoke(translator, n)
        results[token] = sum(
            1 for h in out if any(is_ethiopic(c) for c in h))

    print(f"\n{'=' * 72}\n  Ethiopic segments, of {n}:")
    for token, got in results.items():
        print(f"    {token:8} {'refused' if got is None else got}")
    print("""
  How to read this:
    Spanish works, Tigrinya does not   -> the pipeline is fine; this is a
                                          finding about MADLAD's Tigrinya
    Amharic gives Ge'ez, Tigrinya not  -> Tigrinya coverage, not the script
    Spanish fails too                  -> precision, tokenizer or weights
    fast and slow tokens differ        -> the tokenizer is the cause""")
    return results


def _self_test() -> int:
    """Run the whole pipeline with a stub translator: no model, no network.

    Exists so the script is exercisable in CI and on this sandbox, where the
    model cannot be downloaded. It proves the sampling, alignment, scoring and
    sheet-writing work; it proves nothing about MADLAD.
    """
    import tempfile

    def stub(batch: list[str]) -> list[str]:
        return ["ሰላም ዓለም" for _ in batch]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        out = measure(stub, out_json=tmp / "r.json", out_sheet=tmp / "s.csv",
                      limit=6, quiet=True)
        assert out["output_shape"]["segments"] == 6, out
        assert out["output_shape"]["ethiopic"] == 6, out
        assert len(out["scores"]) == 2, out
        rows = (tmp / "s.csv").read_text(encoding="utf-8").splitlines()
        assert len(rows) == 7, rows
        assert "usable" in rows[0]

    print("self-test passed: sampling, alignment, scoring and sheet all work "
          "with an injected translator")
    return 0


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", metavar="PATH",
                    help="write the measurement artefact here")
    ap.add_argument("--sheet", metavar="PATH",
                    help="write the blind judgement sheet here")
    ap.add_argument("--limit", type=int, metavar="N",
                    help="translate only the first N sampled segments")
    ap.add_argument("--smoke", type=int, nargs="?", const=3, metavar="N",
                    help="translate N segments (default 3) and print them; "
                         "no scoring, no files — run this FIRST")
    ap.add_argument("--diagnose", action="store_true",
                    help="translate a few segments into Tigrinya AND control "
                         "languages, with one model load; writes nothing")
    ap.add_argument("--model", default=MODEL, metavar="NAME_OR_PATH",
                    help="Hub id, or a local directory such as "
                         "models/madlad400-3b-mt-bf16 written by "
                         "scripts/shrink_checkpoint.py")
    ap.add_argument("--dtype", default="bfloat16", metavar="NAME",
                    help="torch dtype for the model (default bfloat16; "
                         "float32 is ~12 GB resident and will thrash 16 GB)")
    ap.add_argument("--force", action="store_true",
                    help="run even if this exact sample was rejected before")
    ap.add_argument("--no-resume", action="store_true",
                    help="ignore any partial run and start over")
    ap.add_argument("--self-test", action="store_true",
                    help="run the pipeline with a stub translator; no model")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    from tigrinya_translate.translate import MadladTranslator

    print("=" * 72)
    print("English -> Tigrinya, TICO-19 health information")
    print("=" * 72)

    try:
        translator = MadladTranslator(model_name=args.model,
                                      dtype=args.dtype)
        # Force the load now, so the language-token check fires before any
        # decoding rather than after the first batch.
        translator._loaded                                # noqa: B018
    except Exception as exc:                              # noqa: BLE001
        print(f"\n::error::{type(exc).__name__}: {exc}")
        return 2

    if args.diagnose:
        diagnose(translator, args.smoke or 3)
        return 0

    if args.smoke:
        smoke(translator, args.smoke)
        return 0

    try:
        measure(translator,
                out_json=pathlib.Path(args.json) if args.json else None,
                out_sheet=pathlib.Path(args.sheet) if args.sheet else None,
                limit=args.limit,
                resume=not args.no_resume,
                force=args.force)
    except (SegmentCountError, WrongLanguageError, AlreadyRejectedError) as exc:
        print(f"\n::error::{exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())       # main() calls force_utf8_stdio() itself
