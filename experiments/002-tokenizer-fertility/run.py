#!/usr/bin/env python3
"""
Experiment 002 — Tokenizer fertility on Tigrinya: does decomposition help?

Tests DEC-007's untested claim that Epitran consonant-vowel decomposition
improves token efficiency. See README.md for pre-committed hypotheses.

Reproduce:
    pip install epitran==1.35.2 tokenizers==0.23.1
    python3 run.py

Deterministic: BPE training is deterministic given identical input and
settings; no randomness, no seed required.
"""

import json
import pathlib
import re
import statistics
import sys
import unicodedata
from collections import Counter

import epitran
from tokenizers import Tokenizer, models, pre_tokenizers, trainers

CORPUS_DIR = pathlib.Path(__file__).parent / "corpus"
RESULTS = pathlib.Path(__file__).parent / "results.json"

ETHIOPIC_RANGES = [
    (0x1200, 0x137F),  # Ethiopic
    (0x1380, 0x139F),  # Ethiopic Supplement
    (0x2D80, 0x2DDF),  # Ethiopic Extended
    (0xAB00, 0xAB2F),  # Ethiopic Extended-A
]
# Ge'ez punctuation and ASCII punctuation both legitimately appear.
PUNCT = set("።፡፣፤፥፦፧፨፠-–—''\"\"()[]{}/\\.,;:!?'\"«»%")


def is_ethiopic(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in ETHIOPIC_RANGES)


def screen(text):
    """Return corruption indicators for a text sample."""
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return None
    eth = sum(1 for c in chars if is_ethiopic(c))
    digit = sum(1 for c in chars if c.isdigit())
    punct = sum(1 for c in chars if c in PUNCT)
    # Anything else in a Tigrinya document is suspect: Latin letters, stray
    # diacritics, mojibake.
    foreign = [c for c in chars if not is_ethiopic(c) and not c.isdigit() and c not in PUNCT]
    return {
        "chars": len(chars),
        "ethiopic_pct": round(100 * eth / len(chars), 2),
        "digit_pct": round(100 * digit / len(chars), 2),
        "punct_pct": round(100 * punct / len(chars), 2),
        "foreign_pct": round(100 * len(foreign) / len(chars), 2),
        "foreign_chars": Counter(foreign).most_common(10),
    }


def words_of(text):
    """Whitespace-delimited words, stripped of punctuation. The standard
    denominator for fertility."""
    out = []
    for raw in text.split():
        w = "".join(c for c in raw if c not in PUNCT)
        if w and any(is_ethiopic(c) for c in w):
            out.append(w)
    return out


def main():
    ti = epitran.Epitran("tir-Ethi")
    results = {}

    # ---------------------------------------------------------------- corpus
    print("=" * 72)
    print("0.  CORPUS AND QUALITY SCREENING")
    print("=" * 72)

    files = sorted(CORPUS_DIR.glob("*.txt"))
    if not files:
        sys.exit("No corpus files found.")

    screening = {}
    clean_texts, excluded = [], []
    for f in files:
        text = f.read_text(encoding="utf-8")
        s = screen(text)
        screening[f.name] = s
        flag = "EXCLUDED" if "CORRUPTED" in f.name else "included"
        print(f"\n  {f.name}  [{flag}]")
        print(f"    chars={s['chars']:>7}  ethiopic={s['ethiopic_pct']:>6}%  "
              f"punct={s['punct_pct']:>5}%  foreign={s['foreign_pct']:>5}%")
        if s["foreign_chars"]:
            shown = " ".join(f"{c!r}x{n}" for c, n in s["foreign_chars"][:6])
            print(f"    foreign chars: {shown}")
        (excluded if "CORRUPTED" in f.name else clean_texts).append(text)

    results["screening"] = screening

    corpus = "\n".join(clean_texts)
    all_words = words_of(corpus)
    print(f"\n  Clean corpus: {len(corpus):,} chars, {len(all_words):,} words, "
          f"{len(set(all_words)):,} unique")
    print(f"  Type/token ratio: {len(set(all_words))/len(all_words):.3f}")

    # Held-out split: last 20% of words for evaluation, rest for training.
    split = int(0.8 * len(all_words))
    train_words, test_words = all_words[:split], all_words[split:]
    print(f"  Train: {len(train_words):,} words | Held-out: {len(test_words):,} words")

    results["corpus"] = {
        "chars": len(corpus),
        "words": len(all_words),
        "unique_words": len(set(all_words)),
        "type_token_ratio": round(len(set(all_words)) / len(all_words), 4),
        "train_words": len(train_words),
        "test_words": len(test_words),
    }

    # ------------------------------------------------------- H1: expansion
    print("\n" + "=" * 72)
    print("1.  H1 — CHARACTER EXPANSION RATIO ON RUNNING TEXT")
    print("     Predicted: 1.8x - 2.1x   (DEC-007 records 1.97x from 7 words)")
    print("=" * 72)

    decomp_cache = {}

    def decompose(word):
        if word not in decomp_cache:
            try:
                decomp_cache[word] = ti.transliterate(word)
            except Exception:
                decomp_cache[word] = ""
        return decomp_cache[word]

    raw_chars = sum(len(w) for w in all_words)
    dec_chars = sum(len(decompose(w)) for w in all_words)
    failed = sum(1 for w in all_words if not decompose(w))
    ratio = dec_chars / raw_chars

    # Per-word ratios, to see spread rather than just the aggregate.
    per_word = [len(decompose(w)) / len(w) for w in set(all_words) if decompose(w)]

    print(f"\n  Raw characters       : {raw_chars:,}")
    print(f"  Decomposed characters: {dec_chars:,}")
    print(f"  AGGREGATE RATIO      : {ratio:.3f}x")
    print(f"  Per-word median      : {statistics.median(per_word):.3f}x")
    print(f"  Per-word mean        : {statistics.mean(per_word):.3f}x")
    print(f"  Per-word range       : {min(per_word):.2f}x - {max(per_word):.2f}x")
    print(f"  Failed to decompose  : {failed} words")

    h1 = 1.8 <= ratio <= 2.1
    print(f"\n  H1 {'CONFIRMED' if h1 else 'REFUTED'} "
          f"(ratio {ratio:.3f} {'within' if h1 else 'OUTSIDE'} 1.8-2.1)")
    results["H1"] = {
        "raw_chars": raw_chars, "decomposed_chars": dec_chars,
        "aggregate_ratio": round(ratio, 4),
        "per_word_median": round(statistics.median(per_word), 4),
        "per_word_mean": round(statistics.mean(per_word), 4),
        "failed_words": failed, "confirmed": h1,
    }

    # ------------------------------------------------- H2: symbol inventory
    print("\n" + "=" * 72)
    print("2.  H2 — SYMBOL INVENTORY")
    print("     Predicted: decomposed unique symbols < 25% of raw")
    print("=" * 72)

    raw_syms = Counter(c for w in all_words for c in w)
    dec_syms = Counter(c for w in all_words for c in decompose(w))
    pct = 100 * len(dec_syms) / len(raw_syms)

    print(f"\n  Unique raw symbols (Ge'ez syllables): {len(raw_syms):,}")
    print(f"  Unique decomposed symbols (phonemes): {len(dec_syms):,}")
    print(f"  Decomposed as % of raw              : {pct:.1f}%")
    print(f"\n  Most common raw : {' '.join(c for c, _ in raw_syms.most_common(12))}")
    print(f"  Most common dec : {' '.join(c for c, _ in dec_syms.most_common(12))}")

    h2 = pct < 25
    print(f"\n  H2 {'CONFIRMED' if h2 else 'REFUTED'} ({pct:.1f}% {'<' if h2 else '>='} 25%)")
    results["H2"] = {
        "raw_unique": len(raw_syms), "decomposed_unique": len(dec_syms),
        "pct_of_raw": round(pct, 2), "confirmed": h2,
    }

    # ----------------------------------------------------- H3: BPE fertility
    print("\n" + "=" * 72)
    print("3.  H3 — BPE FERTILITY  [THE LOAD-BEARING HYPOTHESIS]")
    print("     Predicted: fertility(decomposed) < fertility(raw)")
    print("=" * 72)

    # min_frequency=1: with a corpus this small, min_frequency=2 saturates the
    # vocabulary far below the requested size (542 raw / 646 decomposed), which
    # makes "matched vocab size" a fiction. Setting it to 1 lets the requested
    # size actually be reached, and is the fairer comparison.
    def train_bpe(word_list, vocab_size, byte_level):
        tok = Tokenizer(models.BPE(unk_token="[UNK]"))
        tok.pre_tokenizer = (pre_tokenizers.ByteLevel(add_prefix_space=False)
                             if byte_level else pre_tokenizers.Whitespace())
        trainer = trainers.BpeTrainer(
            vocab_size=vocab_size, special_tokens=["[UNK]"],
            show_progress=False, min_frequency=1,
        )
        tok.train_from_iterator([" ".join(word_list)], trainer)
        return tok

    def fertility(tok, word_list, transform=None):
        """Tokens per word. Denominator is always the ORIGINAL word count, so
        raw and decomposed are directly comparable."""
        total = 0
        for w in word_list:
            s = transform(w) if transform else w
            if not s:
                continue
            total += len(tok.encode(s).tokens)
        return total / len(word_list)

    h3_rows = []
    for byte_level in (False, True):
        label = "byte-level BPE" if byte_level else "char-level BPE"
        print(f"\n  --- {label} ---")
        print(f"  {'vocab':>6} | {'raw':>8} | {'decomposed':>11} | {'delta':>8} | winner")
        print(f"  {'-'*6}-+-{'-'*8}-+-{'-'*11}-+-{'-'*8}-+-------")
        for V in (500, 1000, 2000, 4000, 8000):
            tok_raw = train_bpe(train_words, V, byte_level)
            tok_dec = train_bpe([decompose(w) for w in train_words if decompose(w)],
                                V, byte_level)
            f_raw = fertility(tok_raw, test_words)
            f_dec = fertility(tok_dec, test_words, transform=decompose)
            delta = f_dec - f_raw
            winner = "raw" if delta > 0 else "decomposed"
            print(f"  {V:>6} | {f_raw:>8.3f} | {f_dec:>11.3f} | {delta:>+8.3f} | {winner}")
            h3_rows.append({
                "vocab_size": V, "byte_level": byte_level,
                "fertility_raw": round(f_raw, 4),
                "fertility_decomposed": round(f_dec, 4),
                "delta": round(delta, 4), "winner": winner,
            })

    dec_wins = sum(1 for r in h3_rows if r["winner"] == "decomposed")
    h3 = dec_wins > len(h3_rows) / 2
    print(f"\n  Decomposition won {dec_wins}/{len(h3_rows)} configurations.")
    print(f"\n  H3 {'CONFIRMED' if h3 else 'REFUTED'}")

    # Robustness: is the direction an artefact of one arbitrary split?
    print("\n  --- robustness: 5 rotating train/test folds, char-level, V=2000 ---")
    deltas = []
    n = len(all_words)
    for i in range(5):
        s = (i * n) // 5
        te = all_words[s:s + n // 5]
        tr = all_words[:s] + all_words[s + n // 5:]
        f_raw = fertility(train_bpe(tr, 2000, False), te)
        f_dec = fertility(
            train_bpe([decompose(w) for w in tr if decompose(w)], 2000, False),
            te, transform=decompose)
        deltas.append(f_dec - f_raw)
        print(f"    fold {i}: raw={f_raw:.3f}  decomposed={f_dec:.3f}  "
              f"delta={f_dec - f_raw:+.3f}")
    worse = sum(1 for d in deltas if d > 0)
    print(f"    mean delta {statistics.mean(deltas):+.3f} | "
          f"decomposition worse in {worse}/5 folds")

    results["H3"] = {"rows": h3_rows, "decomposed_wins": dec_wins,
                     "total": len(h3_rows), "confirmed": h3,
                     "fold_deltas": [round(d, 4) for d in deltas],
                     "mean_fold_delta": round(statistics.mean(deltas), 4),
                     "folds_decomposition_worse": worse}

    # ----------------------------------------------------------- conclusion
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for h in ("H1", "H2", "H3"):
        print(f"  {h}: {'CONFIRMED' if results[h]['confirmed'] else 'REFUTED'}")
    print(f"\n  DEC-007 token-efficiency rationale: "
          f"{'SUPPORTED' if results['H3']['confirmed'] else 'NOT SUPPORTED'}")

    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
