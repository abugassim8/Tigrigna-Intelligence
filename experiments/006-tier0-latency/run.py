#!/usr/bin/env python3
"""
Experiment 006 — What does Tier 0 actually cost in time?

Two numbers in the DEC-019 break-even model are **assumed, not measured**:

  - **cold start**, left as a free parameter from 1 s to 60 s
  - **service time**, assumed to be ~2 s

`10_infrastructure` says so explicitly, and A-14 exists because of it. Tier 0 is
now built, so its half is measurable today.

**This does NOT close A-14.** A-14 asks for **Tier 2**'s cold start, which needs
a translation model this environment cannot fetch (egress policy, A-09). What
follows is Tier 0 only, and Tier 0 is the tier DEC-013 keeps *always warm* —
so its cold start matters least. It is measured anyway because the *service
time* feeds the same model, and because a measured number beats an assumed one
even when it is not the number you most wanted.

Hypotheses — pre-committed, written before any measurement
-----------------------------------------------------------
**H1 — Cold start is dominated by the dependency, not by our code.**
`epitran` pulls in `panphon`, which is 107.4 MB of the 113.4 MB footprint.
*Prediction:* loading epitran is **>= 80%** of first-call latency.

**H2 — Tier 0 cold start is far below the break-even table's slow end.**
That table treats 60 s as the pessimistic case, at which break-even falls to
~1 request/minute. *Prediction:* Tier 0 cold start **< 5 s**.

**H3 — Warm service time is orders of magnitude below the assumed 2 s.**
Tier 0 is pure computation over small data. *Prediction:* a typical sentence
(~20 words) transliterates in **< 50 ms** warm.

**H4 — The `lru_cache` materially cuts repeat cost.**
`transliterate_word` is cached, and experiment 005 confirmed that is sound.
*Prediction:* cached lookup is **>= 10x** faster than uncached.

Reproduce:
    pip install -e services/primitives
    python3 run.py

**Non-deterministic by declaration (DEC-016 Amendment 1).** Timings vary by
host; `results.json` records `"deterministic": false` and CI does not
byte-compare it. The numbers describe the machine that produced them.
"""

import json
import pathlib
import statistics
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
RESULTS = HERE / "results.json"
REPO = HERE.parent.parent

#: A representative sentence: real Tigrinya, ~20 words (FLORES+, CC-BY-SA-4.0).
SENTENCE = (
    "ሪንግ ምስ እቲ መፎኻኽርቱ ዝኾነ፣ ኤዲቲ ኮርፖሬሽን፣ ዝነበሮ ክሲ ፈቲሑዎ እዩ። "
    "እዚ ዝተረኽበ ቅሪት ናይ ኣዕዋፍ መንፈሪ ዝረአ ለውጢ የመልክት።"
)

#: Timings are noisy; the median of several runs is far more stable than a mean.
COLD_REPS = 5
WARM_REPS = 200


def _time_subprocess(code: str, reps: int = COLD_REPS) -> float:
    """Median wall time of a FRESH interpreter running `code`, in seconds.

    Cold start has to be measured out-of-process. Anything measured in this
    interpreter has already paid the import cost, which is precisely the cost
    being measured.
    """
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, "-c", code],
                           capture_output=True, cwd=REPO)
        times.append(time.perf_counter() - t0)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode()[:500])
    return statistics.median(times)


def main():
    print("=" * 76)
    print("EXPERIMENT 006 — Tier 0 latency")
    print("=" * 76)
    print(f"  python {sys.version.split()[0]}")
    print(f"  cold-start reps {COLD_REPS}, warm reps {WARM_REPS} (median reported)")

    # ------------------------------------------------------- 1. cold start
    print("\n" + "=" * 76)
    print("1.  COLD START — a fresh interpreter to a first usable answer")
    print("=" * 76)

    bare = _time_subprocess("pass")
    import_only = _time_subprocess("import tigrinya_primitives")
    first_translit = _time_subprocess(
        "import tigrinya_primitives as t; t.transliterate('ሰላም ዓለም')")
    first_normalise = _time_subprocess(
        "import tigrinya_primitives as t; t.normalise('ፀሓይ')")

    # Attribute the cost. Interpreter startup is not ours; subtract it.
    ours = import_only - bare
    epitran_load = first_translit - import_only
    cold_total = first_translit - bare
    epitran_share = epitran_load / cold_total if cold_total else 0.0

    print(f"  bare interpreter                      : {bare*1000:8.1f} ms")
    print(f"  + import tigrinya_primitives          : {import_only*1000:8.1f} ms"
          f"   (ours: {ours*1000:.1f} ms)")
    print(f"  + first transliterate (loads epitran) : {first_translit*1000:8.1f} ms"
          f"   (epitran: {epitran_load*1000:.1f} ms)")
    print(f"  + first normalise (no epitran)        : {first_normalise*1000:8.1f} ms")
    print()
    print(f"  COLD START, excluding interpreter     : {cold_total*1000:8.1f} ms"
          f"  ({cold_total:.2f} s)")
    print(f"  share attributable to epitran         : {100*epitran_share:8.1f}%")

    h1 = epitran_share >= 0.80
    h2 = cold_total < 5.0
    print(f"\n  H1 (epitran >= 80% of cold start) {'CONFIRMED' if h1 else 'REFUTED'}"
          f"  — {100*epitran_share:.1f}%")
    print(f"  H2 (cold start < 5 s)             {'CONFIRMED' if h2 else 'REFUTED'}"
          f"  — {cold_total:.2f} s")

    # ------------------------------------------------------ 2. service time
    print("\n" + "=" * 76)
    print("2.  WARM SERVICE TIME — the number the break-even model assumed at 2 s")
    print("=" * 76)

    from tigrinya_primitives import GeezTokenizer, normalise, transliterate
    from tigrinya_primitives.transliterate import transliterate_word

    words = SENTENCE.split()
    transliterate(SENTENCE)          # warm the process and the cache

    def _median_ms(fn, reps=WARM_REPS):
        ts = []
        for _ in range(reps):
            t0 = time.perf_counter()
            fn()
            ts.append(time.perf_counter() - t0)
        return statistics.median(ts) * 1000

    translit_ms = _median_ms(lambda: transliterate(SENTENCE))
    normalise_ms = _median_ms(lambda: normalise(SENTENCE))

    tok = GeezTokenizer.train([SENTENCE], vocab_size=500, min_frequency=1)
    encode_ms = _median_ms(lambda: tok.encode(SENTENCE))

    print(f"  sentence: {len(words)} words, {len(SENTENCE)} characters")
    print(f"  normalise                : {normalise_ms:9.4f} ms")
    print(f"  transliterate (cached)   : {translit_ms:9.4f} ms")
    print(f"  tokenizer encode         : {encode_ms:9.4f} ms")

    slowest = max(translit_ms, normalise_ms, encode_ms)
    h3 = slowest < 50.0
    print(f"\n  H3 (slowest op < 50 ms)  {'CONFIRMED' if h3 else 'REFUTED'}"
          f"  — {slowest:.4f} ms")

    # ------------------------------------------------------------ 3. cache
    print("\n" + "=" * 76)
    print("3.  CACHE — does the lru_cache on transliterate_word earn its place?")
    print("=" * 76)

    uniq = sorted(set(words))

    def _cached():
        for w in uniq:
            transliterate_word(w)

    def _uncached():
        transliterate_word.cache_clear()
        for w in uniq:
            transliterate_word(w)

    for w in uniq:                    # ensure fully warm
        transliterate_word(w)
    cached_ms = _median_ms(_cached, reps=50)
    uncached_ms = _median_ms(_uncached, reps=50)
    speedup = uncached_ms / cached_ms if cached_ms else 0.0

    print(f"  {len(uniq)} unique words, cached   : {cached_ms:9.4f} ms")
    print(f"  {len(uniq)} unique words, uncached : {uncached_ms:9.4f} ms")
    print(f"  speedup                      : {speedup:9.1f}x")

    h4 = speedup >= 10.0
    print(f"\n  H4 (cache >= 10x) {'CONFIRMED' if h4 else 'REFUTED'}  — {speedup:.1f}x")

    # -------------------------------------------- 4. feed the DEC-019 model
    print("\n" + "=" * 76)
    print("4.  WHAT THIS DOES TO THE BREAK-EVEN MODEL")
    print("=" * 76)

    # Same arithmetic as 10_infrastructure, with measured Tier 0 inputs.
    #   always-warm  = footprint_GB * 730 h
    #   scale-to-zero = footprint_GB * (cold + service) s * requests / 3600
    tier0_gb = 0.1134
    warm_gb_h = tier0_gb * 730
    per_req_s = cold_total + (slowest / 1000)
    breakeven_req_month = (warm_gb_h * 3600) / (tier0_gb * per_req_s)

    print(f"  Tier 0 footprint (measured)   : {tier0_gb:.4f} GB")
    print(f"  always-warm                   : {warm_gb_h:.1f} GB-h/month")
    print(f"  per request (cold + service)  : {per_req_s:.3f} s")
    print(f"  break-even                    : {breakeven_req_month:,.0f} req/month"
          f"  = {breakeven_req_month/730:,.0f}/hour")
    print()
    print("  For comparison, the assumed figures in 10_infrastructure gave")
    print("  58 req/hour at a 60 s cold start. Tier 0's measured cold start is")
    print(f"  {cold_total:.2f} s, so its break-even is far higher — but DEC-013")
    print("  keeps Tier 0 warm regardless, so this changes nothing for Tier 0.")
    print("  It does show the model is sensitive to a number we can now measure")
    print("  rather than assume, and Tier 2 remains unmeasured (A-14).")

    results = {
        # DEC-016 Amendment 1: timings do not reproduce byte-identically.
        "deterministic": False,
        "python": sys.version.split()[0],
        "reps": {"cold": COLD_REPS, "warm": WARM_REPS},
        "cold_start_ms": {
            "bare_interpreter": round(bare * 1000, 1),
            "import_only": round(import_only * 1000, 1),
            "first_transliterate": round(first_translit * 1000, 1),
            "first_normalise": round(first_normalise * 1000, 1),
            "ours_only": round(ours * 1000, 1),
            "epitran_load": round(epitran_load * 1000, 1),
            "total_excluding_interpreter": round(cold_total * 1000, 1),
            "epitran_share_pct": round(100 * epitran_share, 1),
        },
        "service_ms": {
            "sentence_words": len(words),
            "normalise": round(normalise_ms, 4),
            "transliterate": round(translit_ms, 4),
            "encode": round(encode_ms, 4),
            "slowest": round(slowest, 4),
        },
        "cache": {
            "unique_words": len(uniq),
            "cached_ms": round(cached_ms, 4),
            "uncached_ms": round(uncached_ms, 4),
            "speedup": round(speedup, 1),
        },
        "breakeven": {
            "tier0_gb": tier0_gb,
            "always_warm_gb_h_month": round(warm_gb_h, 1),
            "per_request_s": round(per_req_s, 3),
            "req_per_month": round(breakeven_req_month),
            "req_per_hour": round(breakeven_req_month / 730),
        },
        "H1_epitran_dominates_cold_start": h1,
        "H2_cold_start_under_5s": h2,
        "H3_service_under_50ms": h3,
        "H4_cache_at_least_10x": h4,
        "closes_A14": False,
    }

    print("\n" + "=" * 76)
    print("SUMMARY")
    print("=" * 76)
    for k, v in (("H1", h1), ("H2", h2), ("H3", h3), ("H4", h4)):
        print(f"  {k}: {'CONFIRMED' if v else 'REFUTED'}")
    print("\n  A-14 is NOT closed: it asks for Tier 2, which needs a model this")
    print("  environment cannot fetch (A-09). This is Tier 0 only.")

    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
