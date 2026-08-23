# Summary: The API Contract Is Decidable; Only the Surface Is Blocked

| Field | Value |
| --- | --- |
| **Summary ID** | `014-api-response-contract` |
| **Full report** | `docs/research/reports/07_api_mcp/001-response-contract-before-surface.md` |
| **Date** | 2026-08-03 |
| **Status** | Current — **partial**, surface deferred to A-02 |
| **Confidence** | High on the contract; **surface not designed** |

**One-line answer:** **A-02 blocks which endpoints exist, not what a response
must contain** — and the contract is the expensive-to-change part. Deciding it
found an offset trap above the BMP, a favourable normalisation property, and that
**DEC-007's analysis form is not guaranteed phonemic.**

---

## Key Findings

- **⭐ Less is blocked than claimed — again.** I said `04_model_strategy` was
  blocked on A-01 and it was not; the same test here gives the same answer.
  **A-02 determines endpoint priority, SDK order, and whether MCP ships early.**
  It does **not** determine response contents, offset semantics, or how latency
  is communicated — and DEC-012 already settled the library-first shape.

- **⚠️ Offsets need an explicit unit; Ge'ez has a trap above the BMP.**
  **Ethiopic Extended-B (U+1E7E0–U+1E7FF) is above the BMP**, so it needs a
  UTF-16 surrogate pair. On three core characters plus one Extended-B character:

  | Measure | Value |
  | --- | ---: |
  | Python `len()` (code points) | **4** |
  | UTF-8 bytes | 13 |
  | **UTF-16 units (JS `.length`)** | **5** |

  **A JavaScript and a Python client disagree about the same string**, only for
  characters unlikely to reach a test fixture. **Absent from all five of our
  corpora — a contract risk, not a live bug**, which is when it is cheap to fix.
  → **DEC-022**: code-point offsets, unit stated in the response.

- **✅ Ge'ez is normalisation-stable.** Across all 384 core characters,
  **NFC == NFD == identity; zero change**. Offsets do not shift under
  normalisation, so an entire class of API bug does not exist here. Not true of
  many scripts, and worth recording.

- **⚠️ The analysis form is not guaranteed phonemic — a DEC-007 refinement.**
  DEC-007 records coverage as "✅ 384/384". **True as stated** — Experiment 001
  counted *non-empty* output. But:

  | Outcome | Count |
  | --- | ---: |
  | Transliterated to phonemes | **310** |
  | Passed through as the character itself | **74** |

  Of the 74: 26 unassigned and 29 punctuation/digits (both correct), but
  **16 real syllables** (HOA, QOA, XOA, KOA, WOA, YOA, GOA, TZOA, the DD- series)
  and **3 combining marks** come back as raw Ge'ez. Outside the core block the
  pass-through is **total**.

  **So the analysis form is a mixed string, not a phoneme string.** Not a
  contradiction of Experiment 001 — which scoped to `ETHIOPIC_CORE` — but the
  implication was never drawn, and an API contract is where it bites.

- **The 150× tier spread breaks the uniform-API assumption.** Tokenize is
  microseconds; translate is seconds **plus possible cold start** (DEC-013,
  DEC-019). **Presenting them uniformly is a lie the client pays for** — one
  timeout either aborts valid translations or hangs on tokenize.
  → responses carry the serving tier.

- **DEC-010 puts a variety label in the schema.** Every response carrying an
  analysis or score states `eritrean` / `ethiopian` / `unknown`. **`unknown` must
  be a first-class value, not a null** — it is the common case, and a null invites
  clients to ignore the distinction DEC-010 exists to preserve.

- **What genuinely waits on A-02:** endpoint priority, SDK language order,
  whether MCP ships early (it serves agents, not app developers), and auth —
  which **N-9** defers anyway.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| API response contract: code-point offsets, surface form verbatim, analysis form declared non-phonemic, variety label, tier disclosed | DEC-022 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Deferring the whole domain to A-02 | A-02 blocks the surface, not the contract — and the contract is the part that is expensive to change once consumers exist |
| UTF-8 byte offsets | Natural for Python and wrong for every JS client; also 3–4 bytes per Ge'ez character makes them unreadable in debugging |
| UTF-16 code-unit offsets | Natural for JS, wrong for Python, and inherits the surrogate-pair split precisely at Extended-B |
| Leaving the offset unit implicit | The disagreement is silent and appears only on rare characters — the worst failure profile available |
| Presenting all endpoints with uniform latency expectations | A 150× spread; one timeout cannot serve both, and hiding it makes the client pay |
| `null` for unknown variety | Invites clients to ignore the distinction DEC-010 exists to preserve; `unknown` is the common case, not an absence |
| Describing the analysis form as phonemes | Measurably false for 19 real characters and for every non-core block |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Ethiopic blocks above the BMP | **1** (Extended-B) | `[verified]` |
| JS vs Python offset divergence, sample string | **5 vs 4** | `[verified]` |
| Core characters changed by NFC/NFD | **0 of 384** | `[verified]` |
| Core characters transliterated to phonemes | **310 of 384** | `[verified]` |
| **Real characters passing through unmapped** | **19** | `[verified]` |
| Non-core Ethiopic blocks fully unmapped | **3** | `[verified]` |
| Extended-B characters in our corpora | **0** | `[verified]` |

## Recommended Next Steps

1. **Answer A-02** — it is the only thing between here and a designed surface.
2. **Corrected DEC-007's coverage wording** so the superseded "384/384" is not read as full
   phonemic coverage. *(Done in this pass.)*
3. **Add a test fixture containing Extended-B** before any client exists, so the
   offset contract is exercised rather than assumed.
4. **Do not write API code yet** — P-4 applies to endpoints too, and DEC-021's
   primitive evaluation comes first.

## References

1. Unicode encoding arithmetic and epitran behaviour `[verified]` 2026-08-03
2. `experiments/001-epitran-geez-decomposition/` — the coverage figure refined here
3. DEC-007 · DEC-010 · DEC-012 · DEC-013 · DEC-019

---

**Open questions / uncertainty:** Which endpoints, in what order (**A-02**)? Does
MCP ship at all? Should the 19 unmapped characters be handled by us, or reported
upstream to epitran as a contribution (**G-11**)?
