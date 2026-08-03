#!/usr/bin/env python3
"""
Experiment 003 — Are standard MT metrics valid for Tigrinya?

Uses FLORES+ parallel data (same 30 sentences, English and Tigrinya) so that
content is held constant and differences are attributable to the language.
See README.md for pre-committed hypotheses.

Reproduce:
    pip install sacrebleu==2.6.0
    python3 run.py

Deterministic: perturbations use a fixed seed.
"""

import json
import pathlib
import random
import statistics
from collections import Counter

import sacrebleu

DATA = pathlib.Path(__file__).parent / "data"
RESULTS = pathlib.Path(__file__).parent / "results.json"
SEED = 20260803

PUNCT = set("።፡፣፤፥፦፧፨-–—''\"\"()[]{}/\\.,;:!?'\"«»%“”‘’")


def load(name):
    lines = [l.strip() for l in (DATA / name).read_text(encoding="utf-8").splitlines()]
    return [l for l in lines if l]


def words(sent):
    return [w for w in sent.split() if w]


def strip_punct(w):
    return "".join(c for c in w if c not in PUNCT)


def stats(sents, label):
    toks = [w for s in sents for w in words(s)]
    clean = [strip_punct(w) for w in toks]
    clean = [w for w in clean if w]
    ngrams = Counter()
    for s in sents:
        ws = [strip_punct(w) for w in words(s)]
        ws = [w for w in ws if w]
        for n in (4,):
            for i in range(len(ws) - n + 1):
                ngrams[tuple(ws[i:i + n])] += 1
    repeated = sum(1 for v in ngrams.values() if v > 1)
    return {
        "language": label,
        "sentences": len(sents),
        "words": len(clean),
        "words_per_sentence": round(len(clean) / len(sents), 2),
        "unique_words": len(set(clean)),
        "type_token_ratio": round(len(set(clean)) / len(clean), 4),
        "chars_per_word": round(statistics.mean(len(w) for w in clean), 2),
        "distinct_4grams": len(ngrams),
        "4grams_repeated": repeated,
        "4gram_repeat_pct": round(100 * repeated / max(len(ngrams), 1), 2),
    }


def perturb(sents, rate, mode, seed):
    """Corrupt `rate` of words in each sentence.

    near_miss : change the final character  -> right stem, wrong affix
    lexical   : replace the whole word      -> genuinely wrong word
    """
    rng = random.Random(seed)
    out = []
    for s in sents:
        ws = words(s)
        n = max(1, int(round(len(ws) * rate))) if ws else 0
        idx = rng.sample(range(len(ws)), min(n, len(ws))) if ws else []
        new = list(ws)
        for i in idx:
            w = ws[i]
            if mode == "near_miss":
                if len(w) >= 2:
                    # Replace final char with a different char drawn from the
                    # same sentence, so the alphabet stays language-appropriate.
                    pool = [c for c in s if c.strip() and c != w[-1] and c not in PUNCT]
                    if pool:
                        new[i] = w[:-1] + rng.choice(pool)
            else:  # lexical
                pool = [x for x in ws if x != w]
                if pool:
                    new[i] = rng.choice(pool)
        out.append(" ".join(new))
    return out


def score(hyps, refs):
    b = sacrebleu.corpus_bleu(hyps, [refs])
    c = sacrebleu.corpus_chrf(hyps, [refs])
    return b.score, c.score


def main():
    en, ti = load("flores_en.txt"), load("flores_ti.txt")
    assert len(en) == len(ti), f"misaligned: {len(en)} vs {len(ti)}"
    results = {"sentences": len(en), "seed": SEED,
               "sacrebleu_version": sacrebleu.__version__}

    print("=" * 74)
    print(f"FLORES+ parallel data — {len(en)} aligned sentence pairs")
    print("=" * 74)

    # ------------------------------------------------------ H1 / H2 structure
    print("\n" + "=" * 74)
    print("1.  H1 / H2 — STRUCTURAL STATISTICS ON IDENTICAL CONTENT")
    print("=" * 74)
    s_en, s_ti = stats(en, "English"), stats(ti, "Tigrinya")
    results["structure"] = {"en": s_en, "ti": s_ti}

    rows = [
        ("words total", s_en["words"], s_ti["words"]),
        ("words / sentence", s_en["words_per_sentence"], s_ti["words_per_sentence"]),
        ("unique word forms", s_en["unique_words"], s_ti["unique_words"]),
        ("type/token ratio", s_en["type_token_ratio"], s_ti["type_token_ratio"]),
        ("characters / word", s_en["chars_per_word"], s_ti["chars_per_word"]),
        ("distinct 4-grams", s_en["distinct_4grams"], s_ti["distinct_4grams"]),
        ("4-grams repeated %", s_en["4gram_repeat_pct"], s_ti["4gram_repeat_pct"]),
    ]
    print(f"\n  {'measure':<22} | {'English':>10} | {'Tigrinya':>10} | {'ti/en':>7}")
    print(f"  {'-'*22}-+-{'-'*10}-+-{'-'*10}-+-{'-'*7}")
    for name, a, b in rows:
        r = f"{b/a:.2f}x" if a else "—"
        print(f"  {name:<22} | {a:>10} | {b:>10} | {r:>7}")

    word_ratio = s_ti["words"] / s_en["words"]
    ttr_ratio = s_ti["type_token_ratio"] / s_en["type_token_ratio"]
    h1 = word_ratio < 0.80
    h2 = ttr_ratio > 1.3
    print(f"\n  H1 (ti words < 0.80x en): {word_ratio:.3f}x  -> "
          f"{'CONFIRMED' if h1 else 'REFUTED'}")
    print(f"  H2 (TTR ratio > 1.3x)   : {ttr_ratio:.3f}x  -> "
          f"{'CONFIRMED' if h2 else 'REFUTED'}")
    results["H1"] = {"word_ratio": round(word_ratio, 4), "confirmed": h1}
    results["H2"] = {"ttr_ratio": round(ttr_ratio, 4), "confirmed": h2}

    # ------------------------------------------------- H3 / H4 perturbation
    print("\n" + "=" * 74)
    print("2.  H3 / H4 — METRIC RESPONSE TO IDENTICAL CORRUPTION")
    print("=" * 74)
    print("\n  Perfect score sanity check (hypothesis == reference):")
    for lang, s in (("English", en), ("Tigrinya", ti)):
        b, c = score(s, s)
        print(f"    {lang:<9} BLEU={b:6.2f}  chrF={c:6.2f}")

    pert = {}
    for mode in ("near_miss", "lexical"):
        print(f"\n  --- {mode.replace('_', ' ')} corruption ---")
        print(f"  {'rate':>5} | {'lang':<9} | {'BLEU':>7} | {'chrF':>7} | "
              f"{'BLEU kept':>10} | {'chrF kept':>10}")
        print(f"  {'-'*5}-+-{'-'*9}-+-{'-'*7}-+-{'-'*7}-+-{'-'*10}-+-{'-'*10}")
        for rate in (0.10, 0.20, 0.30):
            for lang, s in (("English", en), ("Tigrinya", ti)):
                h = perturb(s, rate, mode, SEED)
                b, c = score(h, s)
                b0, c0 = score(s, s)
                kb, kc = 100 * b / b0, 100 * c / c0
                print(f"  {rate:>5.0%} | {lang:<9} | {b:>7.2f} | {c:>7.2f} | "
                      f"{kb:>9.1f}% | {kc:>9.1f}%")
                pert[f"{mode}_{rate}_{lang}"] = {
                    "bleu": round(b, 3), "chrf": round(c, 3),
                    "bleu_kept_pct": round(kb, 2), "chrf_kept_pct": round(kc, 2),
                }
    results["perturbation"] = pert

    # H3: BLEU falls further on Tigrinya at identical corruption rate
    print("\n  --- H3: is BLEU harsher on Tigrinya? ---")
    h3_ratios = []
    for mode in ("near_miss", "lexical"):
        for rate in (0.10, 0.20, 0.30):
            de = 100 - pert[f"{mode}_{rate}_English"]["bleu_kept_pct"]
            dt = 100 - pert[f"{mode}_{rate}_Tigrinya"]["bleu_kept_pct"]
            r = dt / de if de else float("nan")
            h3_ratios.append(r)
            print(f"    {mode:<10} {rate:>4.0%}  BLEU lost: en={de:5.1f}%  "
                  f"ti={dt:5.1f}%  ratio={r:.2f}x")
    mean_h3 = statistics.mean(h3_ratios)
    h3 = mean_h3 > 1.2
    print(f"\n  Mean ti/en BLEU-loss ratio: {mean_h3:.3f}x -> "
          f"H3 {'CONFIRMED' if h3 else 'REFUTED'}")
    results["H3"] = {"mean_loss_ratio": round(mean_h3, 4),
                     "ratios": [round(r, 4) for r in h3_ratios], "confirmed": h3}

    # H4: on Tigrinya near-misses, chrF retains far more than BLEU
    print("\n  --- H4: does chrF retain credit BLEU discards? (Tigrinya, near-miss) ---")
    h4_ratios = []
    for rate in (0.10, 0.20, 0.30):
        k = pert[f"near_miss_{rate}_Tigrinya"]
        r = k["chrf_kept_pct"] / k["bleu_kept_pct"] if k["bleu_kept_pct"] else float("inf")
        h4_ratios.append(r)
        print(f"    {rate:>4.0%}  BLEU kept={k['bleu_kept_pct']:5.1f}%  "
              f"chrF kept={k['chrf_kept_pct']:5.1f}%  ratio={r:.2f}x")
    mean_h4 = statistics.mean(h4_ratios)
    h4 = mean_h4 > 2.0
    print(f"\n  Mean chrF/BLEU retention: {mean_h4:.3f}x -> "
          f"H4 {'CONFIRMED' if h4 else 'REFUTED'}")
    results["H4"] = {"mean_retention_ratio": round(mean_h4, 4),
                     "ratios": [round(r, 4) for r in h4_ratios], "confirmed": h4}

    # -------------------------------------------------------------- summary
    print("\n" + "=" * 74)
    print("SUMMARY")
    print("=" * 74)
    for h in ("H1", "H2", "H3", "H4"):
        print(f"  {h}: {'CONFIRMED' if results[h]['confirmed'] else 'REFUTED'}")
    verdict = ("chrF PRIMARY, BLEU comparability-only"
               if results["H3"]["confirmed"] and results["H4"]["confirmed"]
               else "see analysis — criteria not cleanly met")
    print(f"\n  Metric recommendation: {verdict}")

    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
