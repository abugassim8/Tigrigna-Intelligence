# The API Contract Is Decidable; Only the Surface Is Blocked

| Field | Value |
| --- | --- |
| **Report ID** | `001-response-contract-before-surface` |
| **Domain** | `07_api_mcp` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted — **partial**, surface deferred to A-02 |
| **Summary** | `docs/research/summaries/014-api-response-contract.md` |
| **Related decisions** | **DEC-022**; refines DEC-007; applies DEC-010, DEC-012, DEC-013 |

---

## Objective

Design the developer-facing API and MCP surface. `api_architecture.md` is gated
on this report, and this report was itself believed blocked on **A-02**.

**Method note.** I claimed `04_model_strategy` was blocked on A-01 and it was
not. That prompted the same test here — **and again, less is blocked than
claimed.** A-02 (who our users are) determines *which endpoints exist and in what
order*. It does not determine what a response must contain, and that is where the
expensive, hard-to-reverse decisions live.

---

## Finding 1 — A-02 blocks the surface, not the contract

| Question | Depends on A-02? | Why |
| --- | --- | --- |
| Which endpoints, in what priority | ✅ **Yes** | Developers and researchers want different things first |
| Which SDK languages first | ✅ **Yes** | Same |
| Whether MCP is a priority | ✅ **Yes** | MCP serves agents, not app developers directly |
| **What a response must contain** | ❌ No | Determined by DEC-007, DEC-010, DEC-013 |
| **Offset semantics** | ❌ No | A property of Ge'ez and Unicode |
| **How latency is communicated** | ❌ No | Determined by DEC-013's tier spread |
| Library-first shape | ❌ No | **Already decided** in DEC-012 |

**The contract is the part that is expensive to change once consumers depend on
it** — precisely what `api_architecture.md` says makes early care valuable. It is
also the part that is decidable now.

## Finding 2 — ⚠️ Offsets need an explicit unit, and Ge'ez has a trap above the BMP

**DEC-007** requires "alignment offsets maintained between surface and analysis
forms." It does not say offsets *in what unit*, and for Ge'ez that is not
academic.

| Ethiopic block | Range | UTF-8 bytes | UTF-16 units | Above BMP? |
| --- | --- | ---: | ---: | --- |
| Ethiopic (core) | U+1200–U+137F | 3 | 1 | no |
| Supplement | U+1380–U+139F | 3 | 1 | no |
| Extended | U+2D80–U+2DDF | 3 | 1 | no |
| Extended-A | U+AB00–U+AB2F | 3 | 1 | no |
| **Extended-B** | **U+1E7E0–U+1E7FF** | **4** | **2** | ⚠️ **YES** |

**Ethiopic Extended-B lies above the BMP**, so it requires a surrogate pair in
UTF-16. Measured on a string of three core characters plus one Extended-B
character:

- Python `len()` → **4** (code points)
- UTF-8 bytes → **13**
- **UTF-16 code units (JavaScript `.length`) → 5**

**A JavaScript client and a Python client disagree about the same string** — and
only for the characters least likely to appear in a test fixture. Extended-B is
absent from all five of our current corpora, so this is a **contract risk, not a
live bug** — which is exactly when it is cheap to fix.

→ **DEC-022**: offsets are **Unicode code points**, and the response states the
unit explicitly rather than leaving clients to assume.

## Finding 3 — Good news: Ge'ez is normalisation-stable

Across all 384 core Ethiopic characters, **NFC == NFD == the character itself**.
**Zero** characters change under Unicode normalisation.

This is a genuinely favourable property and worth recording, because it is *not*
true of many scripts. It means **offsets do not shift under normalisation**, so
the API need not pin a normalisation form to keep alignment valid — one whole
class of API bug does not exist here.

## Finding 4 — ⚠️ The analysis form is not guaranteed phonemic (a DEC-007 refinement)

DEC-007's amendment records epitran coverage as **"✅ 384/384 core Ethiopic
characters."** That is **true as stated** — Experiment 001 counted characters
producing *non-empty* output. But the natural reading, *all 384 are
transliterated to phonemes*, is **not** what happens:

| Outcome | Count |
| --- | ---: |
| Transliterated to phonemes | **310** |
| Passed through as the character itself | **74** |
| Empty output | 0 |

Breaking down the 74:

| Category | Count | Correct to pass through? |
| --- | ---: | --- |
| Unassigned code points | 26 | ✅ yes |
| Punctuation and digits (`።` `፣` `፩`–`፼`) | 29 | ✅ yes |
| **Real syllables** — HOA, QOA, XOA, KOA, WOA, YOA, GOA, TZOA, the DD- series | **16** | ❌ **no** |
| **Combining marks** — gemination, vowel length | **3** | ❌ **no** |

**19 characters carrying real phonological content come back as raw Ge'ez.**
Outside the core block the pass-through is total: Supplement, Extended-A, and
Extended-B are **entirely** unmapped.

**Consequence for the API:** the analysis form is a **mixed string**, not a
phoneme string. Any consumer that assumes phonemes will silently mishandle these
characters. This is not a contradiction of Experiment 001 — which explicitly
scoped to `ETHIOPIC_CORE` and reported non-empty output — but **the implication
was never drawn**, and an API contract is where it becomes load-bearing.

Recorded as a correction in Experiment 001 and DEC-007.

## Finding 5 — The 150× tier spread breaks the uniform-API assumption

**DEC-013** measured a ~150× memory spread and, with **DEC-019**, a cold start
that may reach tens of seconds for Tier 2. A conventional API presents every
endpoint as equivalent. Ours are not:

| Tier | Example call | Realistic latency |
| --- | --- | --- |
| **0** | tokenize, normalise | microseconds |
| **1** | embed | milliseconds |
| **2** | translate | seconds — **plus possible cold start** |

**Presenting these uniformly would be a lie the client pays for.** A caller
setting one timeout for "the Tigrinya API" will either abort valid translations
or wait absurdly long on a tokenize call.

→ **DEC-022**: responses carry the serving tier, and Tier 2 endpoints document
cold-start behaviour rather than hiding it behind an average.

## Finding 6 — DEC-010 puts a variety label in the response schema

**DEC-010** forbids aggregating results across Tigrinya varieties. For an API
that means **every response carrying an analysis or score states its variety** —
`eritrean`, `ethiopian`, or `unknown`.

`unknown` will be the common case and must be a **first-class value, not a null**.
Most Tigrinya resources do not state their variety, and a null would invite
clients to ignore the distinction the decision exists to preserve.

## Finding 7 — What genuinely needs A-02

Deferred, honestly:

- **Endpoint priority.** Developers want capability endpoints; researchers want
  batch and reproducibility. The order differs.
- **SDK languages.** Python is obvious for researchers; developers may need
  JavaScript first — and Finding 2 says the JS client is exactly where the offset
  trap bites.
- **Whether MCP ships early.** MCP serves AI agents. Under DEC-002-as-proposed
  they are not our primary users, so MCP would be a later deliverable — but that
  is a direct consequence of the decision A-02 confirms.
- **Auth model.** **N-9** says no hosted service yet, so this is doubly deferred.

## Limits of this report

- **The surface is not designed.** That is the larger half of `07_api_mcp` and it
  waits on **A-02**.
- **No API code exists**, and none should until DEC-021's primitive evaluation
  lands — **P-4** applies to endpoints as much as to capabilities.
- **The offset trap is unexercised.** Extended-B is absent from our corpora, so
  the finding is arithmetic about encodings, not an observed failure.
- **MCP specifics are not researched** — tool granularity and schema conventions
  depend on whether MCP ships at all.

---

## Decision arising

**DEC-022** — The API response contract: code-point offsets with an explicit
unit, surface form always returned verbatim, analysis form declared non-phonemic,
variety label mandatory, serving tier disclosed.

**Evidence:** encoding arithmetic and epitran behaviour `[verified]` 2026-08-03;
DEC-007, DEC-010, DEC-012, DEC-013.
