# API Architecture

> **Status: the response contract is decided and implemented; the surface is
> not designed.** That split is deliberate, not partial work — **A-02 blocks
> which endpoints exist, not what a response must contain**, and the contract is
> the expensive-to-change half.
>
> **Decided:** DEC-022 (response contract, alignment clause corrected by
> DEC-023), DEC-012 (library-first), DEC-010 (variety label), DEC-013 (tier
> disclosed).
> **Blocked on A-02:** endpoint grouping, SDK order, whether MCP ships early.
>
> **Evidence:** `../research/reports/07_api_mcp/001-response-contract-before-surface.md`,
> `../research/summaries/014-api-response-contract.md`

## Purpose of this document

The design of the developer-facing HTTP API: surface, conventions, versioning, authentication, error handling, and the contract we offer consumers.

## Why this document exists

Infrastructure nobody can use is not infrastructure. The API is where the platform meets its users, and it is unusually expensive to change once external consumers depend on it — which makes early care here disproportionately valuable.

## How to use it

- **Reading:** this is the current design of record for this area. Where it
  conflicts with a decision in
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), the decision wins and
  this document needs updating.
- **Writing:** update it when an Architect-stage decision changes the design. Do
  not use it as a scratchpad for ideas — exploratory thinking belongs in
  `../research/`. This document holds what we have *decided*, not what we are
  *considering*.
- **Every design element here must trace to a decision record.** Design without a
  recorded decision behind it is how projects end up unable to explain
  themselves.

## Relevant principles

**P-7** prefer boring technology · **P-8** measure before claiming · **P-14** state uncertainty honestly

---

## The response contract (DEC-022, amended by DEC-023)

**Decided, implemented, and under test** in
`services/primitives/src/tigrinya_primitives/types.py`. This is the real output
of `transliterate("ሰላም ዓለም", variety=ERITREAN)`:

```json
{
  "surface": "ሰላም ዓለም",
  "analysis": "səlam ʕaləm",
  "spans": [
    {"start": 0, "end": 3, "surface": "ሰላም", "analysis": "səlam"},
    {"start": 4, "end": 7, "surface": "ዓለም", "analysis": "ʕaləm"}
  ],
  "variety": "eritrean",
  "offset_unit": "codepoint",
  "analysis_is_phonemic": false,
  "warnings": []
}
```

Every field earns its place, and three of them exist because of a measurement:

| Field | Why it is in the contract |
| --- | --- |
| `surface` | Returned **verbatim**, never reconstructed from `analysis` (DEC-007). It is the source of truth for anything shown to a user. |
| `spans` | **Word-level**, not character-level. Character alignment is *measurably impossible* — only **23.89%** of words align, because Ge'ez 6th-order characters are ambiguous between "consonant + ɨ" and a bare consonant (DEC-023). |
| `offset_unit` | Stated explicitly, never assumed. **Ethiopic Extended-B (U+1E7E0–U+1E7FF) is above the BMP**, so a JavaScript client counting `.length` and a Python client counting `len()` disagree about the same string. |
| `variety` | Mandatory, and `unknown` is a **first-class value, not a null** (DEC-010). Most Tigrinya resources do not state their variety, and a null invites callers to ignore the distinction. |
| `analysis_is_phonemic` | **Declared false**, because it is. 16 real syllables and 3 combining marks pass through untransliterated, and three Ethiopic blocks are unmapped entirely. A consumer expecting IPA must not be silently wrong. |
| `warnings` | Carries the unmapped-block notices, so a caller learns about degraded output from the response rather than from a support ticket. |

### The offset trap, and why it is fixed now

Measured on three core characters plus one Extended-B character:

| Measure | Value |
| --- | ---: |
| Python `len()` (code points) | **4** |
| UTF-8 bytes | 13 |
| **UTF-16 units (JS `.length`)** | **5** |

**Extended-B is absent from all five of our corpora.** That makes this a
contract risk rather than a live bug — which is exactly when it is cheap to fix,
and exactly when it is easiest to skip.

### One class of bug that does not exist here

**Ge'ez is normalisation-stable**: across all 384 core characters,
NFC == NFD == identity, **zero change**. Offsets do not shift under Unicode
normalisation, so the API need not pin a normalisation form to keep spans valid.
That is not true of many scripts and is worth knowing.

## Latency is part of the contract (DEC-013, DEC-019)

The tier spread is **~150×** in memory and larger in time. Measured:

| Operation | Tier | Time |
| --- | --- | ---: |
| `normalise` | 0 | **0.0086 ms** |
| `transliterate` | 0 | **0.0436 ms** |
| Tier 0 cold start | 0 | **3.03 s** (98.7% is loading `epitran`) |
| Translation | 2 | seconds, **plus possible cold start** |

**Presenting these uniformly is a lie the client pays for**: one timeout either
aborts valid translations or hangs waiting on a tokenize call. So **responses
disclose the serving tier**, and a client can set its own expectations.

Tier 0 services should call `tigrinya_primitives.warmup()` at boot. Loading is
lazy by default — correct for a library — but that defers all 3.0 s onto
whichever request arrives first.

## Library-first, and what that means for the API (DEC-012)

**No capability logic lives only behind a network call.** The HTTP layer is a
thin wrapper over `tigrinya-primitives` and `tigrinya-eval`, both installable and
usable with no infrastructure at all. Consequences worth stating:

- anything the API can do, a `pip install` can do;
- the API cannot drift from the library, because it has no logic of its own;
- an offline or air-gapped consumer is a first-class case, not a special one.

## Blocked on A-02 — deliberately not designed

**A-02 determines endpoint priority, SDK order, and whether MCP ships early.**
It does *not* determine anything above, which is why the contract could be
settled first. These remain open, and guessing them now would be the expensive
kind of wrong:

### API surface
Endpoint grouping per capability. **Gated on A-02.**

### Versioning strategy
How the API evolves without breaking consumers. Cheap now, expensive after
consumers exist — but the shape depends on the surface.

### Authentication and authorisation
See **N-9**: there is no hosted commercial service, so this is not yet needed.

### Rate limiting and quotas
**Not needed until there is a hosted service.** Recorded so it is not built
speculatively (**P-7**).

### Batch and streaming
Which capabilities need which. Tier 0 is fast enough that batching is a
throughput question, not a latency one; Tier 2 is where streaming would matter.

### Documentation and discoverability
Including the install-to-first-successful-call path.

### SDK alignment
How the Python and JavaScript SDKs map onto this surface. **The UTF-16 offset
divergence above makes the JavaScript SDK the one that needs care** — it must
either convert offsets or state that it reports code points.

## Error handling

Decided in part, by the shape of the types:

- **Misaligned spans fail immediately.** `Analysis.verify_offsets()` raises
  rather than returning a subtly wrong response, so the failure this contract
  exists to prevent cannot be served.
- **Degraded output is declared, not hidden** — `analysis_is_phonemic` and
  `warnings` carry it in-band.
- **Morphology is honestly unavailable.** `morphology.is_available()` returns
  `False` and calls raise `NotImplementedError` naming **A-07**, so a caller
  degrades deliberately rather than receiving something plausible and wrong.

## Open questions

- **Who are the users?** — **A-02**, the one blocker on the surface.
- Should the JavaScript SDK convert offsets to UTF-16, or report code points and
  say so? Converting is friendlier; reporting is honest and cheaper to keep
  correct.
- Does anyone actually need character-level alignment? DEC-023 forecloses it with
  the current transliterator, and **no consumer has asked** — recorded so the
  cost is revisited only if a real need appears.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| API response contract | **DEC-022** | 2026-08-18 | Code-point offsets, surface verbatim, variety label, tier disclosed — **alignment clause corrected by DEC-023** |
| Primitive evaluation; word-level alignment | **DEC-023** | 2026-08-18 | Corrects DEC-022's offset clause to word-level spans; **evidence retracted and re-measured by Amendment 1** |
| Library-first | **DEC-012** | 2026-08-10 | Services are thin wrappers; no capability lives only behind a network call |
| Variety-scoped results | **DEC-010** | 2026-08-03 | Variety is mandatory in the schema; `unknown` is first-class |
| Tier by resource profile | **DEC-013** | 2026-08-10 | The ~150× spread is why responses disclose the serving tier |
| Primary users | **DEC-002** | 2026-07-29 | ⚠️ **Proposed, not accepted** — the open blocker on the surface (**A-02**) |

## What future contributors should add

The endpoint surface, once **A-02** lands. Keep the contract section anchored to
the code in `services/primitives/src/tigrinya_primitives/types.py` — if the two
disagree, the code is what ships and this document is wrong. An architecture
document that has drifted from reality is worse than none, because people trust
it.
