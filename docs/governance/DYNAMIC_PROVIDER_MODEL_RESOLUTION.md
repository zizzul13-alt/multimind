# MULTIMIND — DYNAMIC PROVIDER / MODEL RESOLUTION

Status: **CLOSED / FULL FEATURE IMPLEMENTATION OF THIS BOUNDED CONTRACT**
Date: 2026-09-09
Entering baseline: `main@2435ada2099c6529e02667ed850994afaf6a0c0e`
Implementation: PR #109
Final PR head: `e869ac28dafa2edd2d4f53b9653bfabcb991f96b`
Implementation exact-main: `39c1f5b50d0fef2eb02798df5f9134e2e0ea5d9a`

## Accepted architecture

`TASK MODE → CAPABILITY REQUIREMENTS → SELECTED PROVIDER → MODEL REGISTRY / PROVIDER DISCOVERY → MODEL RESOLUTION → PROVIDER CALL → PROVIDER + MODEL PROVENANCE`

Provider identity is durable. Model identity is replaceable runtime state. Participant identity remains deliberation truth.

## Implemented behavior

- Added `providers/model_registry.py` as the small in-process model-policy/resolution boundary. No service, database, framework, or transport layer was added.
- Groq and explicitly selected DeepSeek validate centralized candidates against provider model catalog discovery. Discovery failure degrades to the bounded registry candidate; an authoritative catalog that lacks the candidate fails with `no_eligible_model` rather than calling a known-stale ID.
- Groq/DeepSeek cache a successful discovered catalog for the lifetime of the composed provider instance so deliberation rounds do not spend an extra model-list request on every participant/critique/judge call.
- OpenRouter no longer carries stale Coding/Research/Thinking model IDs in its adapter. It calls the provider-maintained `openrouter/free` dynamic router and records the concrete response model when OpenRouter exposes it.
- Cloudflare and Hugging Face use centralized registry fallback policy because this bounded implementation does not depend on a separate live catalog service for them.
- The composed Gemini agent resolves its provider-maintained `gemini-flash-latest` alias through the central registry. The alias is intentionally treated as provider-side dynamic resolution. When the Google response path does not expose a concrete underlying version through the existing compatibility adapter, `actual_model` remains unknown rather than fabricated.
- Provider adapters no longer own permanent product model choice for the active Groq, Cloudflare, OpenRouter, Hugging Face and DeepSeek execution paths; bounded bootstrap candidates live centrally.
- DeepSeek remains `paid_optional`: its candidate is not eligible through generic free-first resolution and is enabled only inside the explicitly selected DeepSeek provider path.
- Successful dynamic adapters report `resolved_model`, `actual_model` when known, `model_resolution_source`, and `model_family`. Existing deliberation participant records continue to persist the provider's post-call model label, preserving participant/provider identity guarantees.
- Explicit user provider selection is never rewritten by model resolution. There is no cross-provider model fallback.
- If an authoritative same-provider catalog invalidates the bounded candidate and no accepted alternative exists, that selected participant fails honestly. This is preferred over inventing a replacement or silently consuming a paid/unselected resource.

## Adversarial repair loop

The first implementation was not accepted after first green attempt.

Python Regression #261 exposed two stale tests that encoded Groq's old adapter-owned `MODEL`/`provider.model` contract. The implementation did not restore the hardcode merely to satisfy those tests. Instead, the tests were repaired to enforce the new architectural invariant: protocol ownership remains in the adapter while model policy belongs to the resolver/registry.

Additional adversarial work then added:

- discovery-success proof;
- discovery-error → registry-fallback proof;
- authoritative-catalog-missing → explicit no-model proof;
- paid-optional isolation proof;
- deterministic resolution proof;
- OpenRouter free-router churn/provenance proof;
- Groq actual-model provenance proof;
- bounded Groq catalog-call proof;
- retired/stale OpenRouter per-mode ID guards;
- provider changes as explicit RJ5/RJ6 workflow triggers, closing a CI path-filter blind spot discovered during this workstream.

No closed deliberation, mode/capability, Prompt Style, compressor, persistence, security, or presentation contract was weakened.

## Verification evidence

Final PR head:

`e869ac28dafa2edd2d4f53b9653bfabcb991f96b`

PR-head verification:

- Python Regression #268 — SUCCESS
- RJ5 Dual-Host Torture #38 — SUCCESS
- RJ6 Cutover Rollback Proof #48 — SUCCESS
- Final Gate Operator Readiness #98 — SUCCESS

PR #109 was squash-merged with expected-head guard against exactly `e869ac28dafa2edd2d4f53b9653bfabcb991f96b`.

Implementation exact-main:

`39c1f5b50d0fef2eb02798df5f9134e2e0ea5d9a`

Exact-main verification:

- Python Regression #269 — SUCCESS
- RJ5 Dual-Host Torture #39 — SUCCESS
- RJ6 Cutover Rollback Proof #49 — SUCCESS
- Final Gate Operator Readiness #99 — SUCCESS

Known in-scope residuals after final adversarial review: **0**.

## Important interpretation

"Dynamic" does not mean every provider can be called with no model selector at the HTTP/API level. Some provider APIs require a model identifier. MultiMind now separates that replaceable selector from durable provider/application truth: live/provider-side resolution is used where available, and centralized bounded registry candidates are used where an API still requires an explicit selector.

This workstream does not claim that every possible model in every provider is automatically safe/free/eligible. New models still require policy classification before they may become bounded candidates. That protects free-first semantics from silently drifting into paid usage.

## Status

`DYNAMIC_PROVIDER_MODEL_RESOLUTION = FULL FEATURE IMPLEMENTATION / CLOSED`

`KNOWN_IN_SCOPE_RESIDUALS = 0`

`FULL_OPERATIONAL_PROVIDER_VERIFICATION = NOT CLAIMED BY THIS WORKSTREAM`

`RAILWAY_FINAL_INTEGRATION = HOLD`

`FINAL_RAILWAY_CANDIDATE = NOT BUILT BY THIS WORKSTREAM`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`

STOP before Railway final integration.
