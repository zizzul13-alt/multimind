# MULTIMIND — DYNAMIC RESOURCE DISCOVERY IMPLEMENTATION

Status: IMPLEMENTATION CANDIDATE / PR VERIFICATION REQUIRED
Date: 2026-09-12
Entering baseline: `main@2d05364713be280b0c86e7cd24afda72905697da`
Authority: AI identity-first routing + dynamic provider/model resolution + server-side credential isolation.

## Contract

`SERVER-SIDE RESOURCE SPEC → AUTHENTICATED MODEL CATALOG DISCOVERY → MODEL-ID NORMALIZATION → CONSERVATIVE AI FAMILY CLASSIFICATION → SAME-IDENTITY ROUTE → RESPONSE IDENTITY RECHECK → PROVENANCE`

This extends the already-closed dynamic model resolver instead of replacing it. Built-in providers remain intact.

## Implemented

- Generic OpenAI-compatible resource adapter using existing `openai` dependency.
- Deployment resources via `MULTIMIND_OPENAI_COMPATIBLE_RESOURCES_JSON`.
- Per-user selected custom resources through the existing server-side pool JSON.
- `/models`-style discovery through the OpenAI client catalogue interface.
- Recognized families: Gemini, GPT-OSS, Llama, DeepSeek, Claude, GPT, Qwen, Kimi, Grok.
- Unknown model IDs remain unclassified and are not exposed as runnable identities.
- Claude/GPT/Qwen/Kimi/Grok are now identity vocabulary in Reflex; without a discovered route they remain unavailable rather than silently borrowing another AI.
- Multiple discovered routes of one family become same-identity routes; cross-identity fallback remains disabled.
- A successful call re-checks the returned model identity before the result may carry the selected identity.
- Generic-resource provenance is `declared_by_provider_catalog`; this is deliberately weaker than claiming verified upstream vendor identity.
- API keys remain in server composition/provider objects and are never added to response/provenance structures.
- Discovery failure contributes zero routes and does not break built-in MultiMind operation.

## Non-goals

No price optimizer, autonomous marketplace routing, automatic purchasing, credential rotation, new database, HTTP service, microservice, frontend secret entry, or production cutover.

## Security / truth law

An opaque API key is not an identity signal. Base URL/API dialect/catalog response can establish what an endpoint declares, but a proxy can lie about its upstream. MultiMind therefore labels generic discovery as provider-declared provenance and never upgrades that claim to verified Anthropic/OpenAI/etc merely from output style.

## Verification target

- discovery of multiple known and unknown catalogue models;
- unknown identity fail-closed;
- post-generation identity recheck;
- malformed resource fail-closed;
- operator resource parsing;
- per-user custom-resource isolation;
- existing identity routing/provider/deliberation regression remains green.

Production/Railway secrets and real kios API smoke remain operator-environment evidence and are not fabricated by repository tests.
