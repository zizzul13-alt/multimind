# MULTIMIND — DYNAMIC PROVIDER / MODEL RESOLUTION

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-09
Baseline: `main@2435ada2099c6529e02667ed850994afaf6a0c0e`

## Mission

Remove model identity as a permanent hard-coded product assumption while preserving provider adapters as durable integration boundaries.

Accepted architecture:

`TASK MODE → CAPABILITY REQUIREMENTS → PROVIDER RESOURCE → MODEL DISCOVERY/REGISTRY → MODEL RESOLUTION → PROVIDER CALL → ACTUAL PROVIDER+MODEL PROVENANCE`

Provider is durable identity. Model is replaceable runtime resource. Participant is the deliberation identity exposed to application/presentation truth.

## Entry finding

Current adapters still contain model IDs or mode→model maps directly in provider code, including Groq, Gemini, Cloudflare, DeepSeek, Hugging Face, and OpenRouter. This is operationally brittle under model deprecation/free-tier churn and can reduce model-family diversity even when provider diversity exists.

## Finite implementation contract

1. Add a small in-process model registry/resolver behind stable application/provider boundaries. No network service, database, framework, or transport layer.
2. Provider adapters own protocol/auth/request mechanics, not permanent product model choice.
3. Resolver input includes provider, task mode/capabilities, configured/available resource state, and optional discovered catalog evidence.
4. Support dynamic provider catalog discovery where the provider exposes a safe model-list/catalog API; cache results with boring bounded failure semantics.
5. Where discovery is unavailable/fails, use explicit registry policy/default candidates as a safe fallback. A fallback is not the source of truth and must be attributable.
6. Model selection must be deterministic for equivalent registry/catalog state and must never silently switch provider identity.
7. Persist/report requested provider, actual provider, resolved model, resolution source (discovered/registry/fallback), and relevant capability/mode provenance.
8. Preserve explicit user participant roster and all closed deliberation semantics.
9. Model churn/deprecation must degrade to another eligible model within the same selected provider when policy allows; otherwise that participant fails honestly.
10. Do not silently consume paid-only resources merely because a model is newer. Free-first/paid-optional policy remains authoritative.
11. Diversity policy should avoid unnecessary same-model-family duplication when equivalent eligible alternatives exist, without overriding explicit user participant choices.
12. Existing hard-coded IDs may remain only as bounded bootstrap/fallback candidates where necessary, centralized in registry policy rather than scattered product truth in adapters.

## Verification matrix

At minimum prove:
- coding/research/thinking resolve through registry rather than adapter constants;
- catalog discovery success;
- discovery timeout/error/malformed response → bounded registry fallback;
- deprecated/missing preferred model → next eligible same-provider model;
- no eligible same-provider model → explicit participant failure, no provider impersonation;
- deterministic selection;
- free-first filtering and paid-optional isolation;
- actual model provenance persisted through deliberation/history/projection;
- explicit roster unchanged;
- model-family diversity preference does not falsify participant identity;
- OpenRouter free-model churn scenario;
- provider with no discovery endpoint remains operational through registry candidates;
- existing deliberation, mode/capability, prompt normalization, compressor, persistence, security and presentation regression remains green.

## Scope protection

Do not add FastAPI, REST/RPC glue, microservices, a new database, LangChain, CrewAI, AutoGen, or a remote registry service. Do not redesign closed provider abstraction wholesale. Do not activate NVIDIA NIM merely because its credential exists; adapter/onboarding remains separately governed unless required by this bounded contract.

## Exit

Inspect → implement → targeted tests → adversarial review → repair until known in-scope residuals are zero → full Python/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure.

STOP before Railway final integration. Production cutover remains unauthorized.
