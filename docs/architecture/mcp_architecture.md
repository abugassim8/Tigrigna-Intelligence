# MCP Architecture

> **Status: not designed, and deliberately so.** **A-02 determines whether MCP
> ships early at all** — it is the surface question, and the surface is the part
> that depends on who the users are.
>
> **What is already settled and constrains any MCP server we build:** DEC-012
> (library-first, so MCP is a wrapper and never a reimplementation), DEC-022
> (the response contract), DEC-013 (tier disclosed, because the latency spread
> is ~150×).
>
> **Evidence:** `../research/summaries/014-api-response-contract.md`

## Purpose of this document

The design of the Model Context Protocol server: which tools it exposes, how they map onto platform capabilities, and how AI assistants interact with the platform through it.

## Why this document exists

MCP is how AI assistants consume this platform. It is a distinct interface from the HTTP API with different design constraints — tools must be self-describing, appropriately granular, and safe to call without the caller fully understanding Tigrinya linguistics. A well-designed MCP surface makes the platform usable by any AI agent; a poorly designed one makes it usable by none.

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

**P-7** prefer boring technology · **P-14** state uncertainty honestly · **P-11** services are independent

## What is already decided, and binds MCP

MCP is not a separate design problem from the HTTP API. **DEC-012 makes both
thin wrappers over the same libraries**, so anything true of the contract is true
here:

| Constraint | Source | Why it matters to a tool caller |
| --- | --- | --- |
| Surface text returned **verbatim** | DEC-007, DEC-022 | A model consuming the output must never see reconstructed text presented as the original |
| Spans are **word-level** | DEC-023 | Character alignment is measurably impossible (23.89%); a tool promising it would be lying |
| Offsets are **code points**, unit stated | DEC-022 | Ethiopic Extended-B is above the BMP; a JavaScript-based client disagrees with a Python one |
| `analysis_is_phonemic: false` | DEC-022 | An LLM told it is receiving IPA will reason confidently about a mixed string |
| Variety label mandatory | DEC-010 | `unknown` is first-class; a null invites the caller to ignore the distinction |
| Serving tier disclosed | DEC-013, DEC-019 | Tokenize is ~0.04 ms; translate is seconds plus possible cold start |

**The uncertainty-communication problem is sharper for MCP than for HTTP.** An
application developer calling the HTTP API can inspect a response. **A model
calling an MCP tool cannot evaluate Tigrinya output, and neither can the person
reading its answer.** So degraded output has to be *structurally* visible —
`analysis_is_phonemic`, `warnings`, and morphology raising rather than returning
something plausible — not merely documented.

## Deliberately not designed

Each of these depends on the surface, and the surface depends on **A-02**.
Guessing them now is the expensive kind of wrong:

### Tool inventory
Which capabilities are exposed, and which are deliberately not. **The instinct
to expose everything should be resisted** — a tool a model cannot use correctly
is worse than an absent one.

### Tool granularity
One broad `analyze` tool versus several narrow ones. This is the decision most
sensitive to who is calling, which is precisely what A-02 settles.

### Tool descriptions and schemas
How tools describe themselves well enough to be used correctly with no prior
knowledge of Tigrinya. **This is where the Ge'ez-specific traps have to be
stated**, because the caller has no way to discover them.

### Resources and prompts
Whether the server exposes anything beyond tools.

### Transport and deployment
How the server runs and is connected to. Tier 0's **3.03 s cold start** argues
for a long-lived process calling `warmup()` at boot rather than per-invocation
startup.

### Authentication
Not needed — **N-9**, there is no hosted commercial service.

## Relationship to the HTTP API

**Shared implementation, not a parallel one.** DEC-012 settles this: both are
thin wrappers over `tigrinya-primitives` and `tigrinya-eval`. An MCP server with
its own capability logic would drift from the API, and the two would disagree
about Tigrinya in ways no test would catch.

## Open questions

- **Does MCP ship early?** — **A-02**. If the primary users are application
  developers, MCP is secondary; if the value is exposing Tigrinya to models that
  cannot otherwise handle it, MCP may be the *first* surface.
- How does a tool communicate "this is transliteration, not IPA" to a model in a
  way that actually changes its behaviour? Schema fields are read; prose in a
  description may not be.
- Should morphology appear in the inventory at all while it raises
  `NotImplementedError` (**A-07**)? An advertised tool that always fails is a
  worse experience than an absent one.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| Library-first | **DEC-012** | 2026-08-10 | MCP is a thin wrapper over the same libraries as the HTTP API — never a second implementation |
| API response contract | **DEC-022** | 2026-08-18 | Binds MCP too: verbatim surface, code-point offsets, variety label, tier disclosed |
| Primitive evaluation; word-level alignment | **DEC-023** | 2026-08-18 | Spans are word-level; character alignment must not be promised |
| Tier by resource profile | **DEC-013** | 2026-08-10 | The ~150× latency spread is why a tool result discloses its tier |
| Primary users | **DEC-002** | 2026-07-29 | ⚠️ **Proposed, not accepted** — decides whether MCP ships early (**A-02**) |

## What future contributors should add

The actual design, once research supports it. Diagrams where they clarify.
Rationale linked to decision records. Keep it current — an architecture document
that has drifted from reality is worse than none, because people trust it.
