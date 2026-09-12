# MULTIMIND — DYNAMIC RESOURCE DISCOVERY IMPLEMENTATION

Status: IMPLEMENTATION CANDIDATE / PR VERIFICATION REQUIRED
Date: 2026-09-12
Entering baseline: `main@21f7f986f35b2e0b719402fb5ef4aac61dbcad09`
Authority: AI identity-first routing + dynamic provider/model resolution + server-side credential isolation.

## Contract

`SERVER-SIDE RESOURCE SPEC → AUTHENTICATED MODEL CATALOG DISCOVERY → MODEL-ID NORMALIZATION → CONSERVATIVE AI FAMILY CLASSIFICATION → SAME-IDENTITY ROUTE → RESPONSE IDENTITY RECHECK → PROVENANCE`

This extends the already-closed dynamic model resolver instead of replacing it. Built-in direct providers remain first-class. A kios/gateway is one possible resource source, not MultiMind's internal architecture.

## Implemented candidate

- Generic OpenAI-compatible resource adapter using the existing `openai` dependency.
- Operator resources via `MULTIMIND_OPENAI_COMPATIBLE_RESOURCES_JSON` and per-user selected custom resources through the existing server-side pool JSON.
- `/models`-style discovery through the existing OpenAI catalogue seam.
- Runtime identity vocabulary can classify Gemini, GPT-OSS, Llama, DeepSeek, Claude, GPT, Qwen, Kimi and Grok; only identities with an actual composed route are available to execution.
- Unknown model IDs remain unclassified/inert rather than being guessed.
- Multiple discovered routes of one family become same-identity routes; cross-identity fallback remains disabled.
- Successful calls re-check returned model identity before carrying the selected identity.
- Generic-resource provenance is `declared_by_provider_catalog`, deliberately weaker than verified upstream-vendor identity.
- API keys remain server-side and are not added to response/provenance structures.
- Discovery failure contributes zero routes and does not break built-in MultiMind operation.
- The closed primary identity catalogue remains unchanged for compatibility; runtime availability is a separate application projection.

## Presentation boundary

The presentation host must consume application/runtime identity availability rather than perform provider discovery itself. A static list may show stable vocabulary only when unavailable state is represented truthfully; it must not imply that an unconfigured Claude/GPT/Qwen/etc route exists.

## Non-goals

No price optimizer, autonomous marketplace routing, automatic purchasing, credential rotation, new database, HTTP service, microservice, browser-side secret entry, Design-DNA changes, or production cutover.

## Security / truth law

An opaque API key is not an identity signal. Base URL/API dialect/catalog response can establish what an endpoint declares, but a proxy can lie about its upstream. MultiMind labels generic discovery as provider-declared provenance and never upgrades that claim to verified Anthropic/OpenAI/etc merely from output style.

## Verification target

Discovery of known/unknown catalogue models; unknown identity fail-closed; post-generation identity recheck; malformed resource fail-closed; operator parsing; per-user isolation; primary catalogue compatibility; identity routing/provider/deliberation regressions green.

Production/Railway secrets and real external-resource smoke remain operator-environment evidence and are not fabricated by repository tests.
