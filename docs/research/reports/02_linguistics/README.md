# 02 — Linguistics

## Purpose of this document

This directory holds full Analyst-stage research reports for **02 — Linguistics**.

It establishes the linguistic facts about Tigrinya that drive technical design: morphology, orthography, syntax, dialectal variation, and how the Ge'ez script behaves computationally.

## Why this domain exists

Language technology built without understanding the language fails in ways that are hard to diagnose from metrics alone. Tigrinya's root-and-pattern morphology and Ge'ez abugida script both have direct consequences for tokenization, embeddings, and retrieval. Assumption **A-007** — that morphological complexity is a first-order design constraint — sits upstream of several architectural choices and is currently unverified. Resolving it early is high-value.

## Research questions this domain must answer

- How does Tigrinya morphology work, and what does it imply for tokenization and lemmatization?
- How productive is the morphology? How large is the realistic inflected-form space per lemma?
- How does the Ge'ez script behave computationally? Unicode ranges, normalisation, encoding pitfalls, common variant spellings?
- What orthographic variation exists in real text, and how much normalisation is needed before anything else works?
- What are the significant dialectal differences, and do they matter for our use cases?
- What syntactic features affect parsing, NER, and translation?
- What linguistic resources exist — grammars, lexicons, annotated corpora, existing analysers?
- What have Amharic and other Ethio-Semitic NLP efforts learned that transfers?
- How do speakers actually write online, versus formal written standards?

Every report in this directory must also answer the nine questions in
[`../../CHECKLIST.md`](../../CHECKLIST.md).

## How to use this directory

1. Check [`../../summaries/`](../../summaries/) first — the answer may already exist.
2. Run a **Scout** pass to map the option space; write the short summary.
3. Run an **Analyst** pass on the shortlist using
   [`../../templates/research_report_template.md`](../../templates/research_report_template.md).
4. Write the report here as `NNN-slug.md`.
5. Write the ≤2-page summary to `../../summaries/NNN-slug.md`. **The report is
   not finished without it.**
6. Hand to the **Architect** stage: record decisions in
   [`../../../decisions/DECISIONS.md`](../../../decisions/DECISIONS.md).

## Dependencies

**Depends on:** `00_project_definition`.

**Gates:** `03_data_strategy`, `04_model_strategy`, `06_ml_pipeline`, and the tokenizer/morphology/spellcheck services.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**1 report complete.** `001-morphology-script-and-tokenization.md` (2026-07-29)
confirmed **A-007** and identified its mechanism: Tigrinya's templatic morphology
operates on consonants and vowels separately while the Ge'ez abugida fuses them,
so **morpheme boundaries can fall inside a single character**. Produced DEC-007.
See `../../summaries/003-morphology-script-and-tokenization.md`.

**Open:** orthographic-variation corpus survey (blocked on `03_data_strategy`),
HornMorpho verification, whether the two varieties differ orthographically, and
register distance.
