# SDKs

## Purpose of this directory

Client libraries that let developers use the platform from their own code, plus
runnable examples.

## Why this directory exists

Infrastructure nobody can use is not infrastructure (**G-7**). The SDKs are what
turn an API into something a developer adopts. A platform with a good API and no
SDK gets evaluated; a platform with both gets used.

## Structure

| Directory | Contents |
| --- | --- |
| `python/` | Python client library |
| `javascript/` | JavaScript / TypeScript client library |
| `examples/` | Runnable examples for both, and for the MCP server |

## Design principles for SDKs

1. **Idiomatic in each language.** A Python SDK should feel like Python, not like
   a transliterated JavaScript library. Shared design, separate implementations.
2. **Thin.** SDKs wrap the API; they do not add logic. Business logic in an SDK
   is logic that drifts from the server.
3. **Honest about uncertainty.** Confidence scores and low-confidence warnings
   surface in the SDK, not just in the raw API response (**P-14**).
4. **Fast to first call.** Install to first successful call is a tracked metric
   — see `../docs/vision/success_metrics.md`.
5. **Typed.** Type hints in Python, TypeScript definitions in JavaScript.
6. **Versioned with the API.** Compatibility is explicit, and stated in the
   README.

## Examples

Examples are documentation that cannot go stale silently, because they either run
or they do not. Each should be self-contained, runnable, and cover one thing.

## Gated on

`../docs/research/reports/07_api_mcp/` and a working API. Building an SDK before
the API surface is settled means rewriting it.

## What future contributors should add

Implementations, once the API exists. Examples covering each capability. Keep
compatibility notes current — an SDK that silently mismatches its API is worse
than no SDK.

## Status

**Not implemented.** No API exists yet.
