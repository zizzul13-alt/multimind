# MULTIMIND — AI IDENTITY FIRST / PROVIDER ROUTING TRANSPARENCY

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-12
Inspected current base: `main@59195067b78a1d473e09dc5be71ea52d4b3183f7`
Owning workstream: AI Identity / Provider Routing UX

## Product law

`USER SELECTS AI IDENTITY → APPLICATION RESOLVES ACCEPTED ROUTE → PROVIDER ADAPTER EXECUTES`

Infrastructure may be abstracted. AI/model identity may not be falsified.

A response may be presented as an identity only after returned model/family provenance is compatible with that identity. Unknown or mismatched identity fails closed rather than producing a labelled impostor result.

## Repository audit

### 1. What did the user select at entry?

Provider/gateway-oriented identifiers. Reflex exposed `gemini`, `deepseek`, `groq`, `cloudflare`, `openrouter`, and `huggingface` as checkbox participants. Streamlit reference settings also exposed provider/compatibility identifiers. This mixed model identity with inference route identity.

### 2. Where was routing resolved?

Provider construction lives in `core/composition.py`. Concrete provider model resolution lives behind provider adapters and `providers/model_registry.py`. `MultiMindApplication` owns execution and hands an explicit participant roster to `DebateOrchestrator`.

### 3. Can multiple routes serve one AI/model today?

Yes, where repository truth supports it. GPT-OSS is currently available through Groq and Hugging Face model-registry routes. Other currently pin-able identities in this bounded patch have one accepted route. OpenRouter's `openrouter/free` route is dynamic and therefore is not exposed as a stable AI identity by itself.

### 4. Did fallback preserve requested vs effective identity?

Before this workstream there was no first-class requested/effective **AI identity** pair. Closed deliberation semantics already prevented participant cross-provider impersonation and persisted requested/actual provider provenance. This workstream adds identity provenance above that existing guarantee.

### 5. Could UI misrepresent who the participant was?

The UI truthfully displayed provider provenance, but provider brands such as Groq, Cloudflare, or OpenRouter were presented as logical participant choices. That is semantically wrong for an AI-identity-first product even when low-level provider provenance is accurate.

### 6. Did persisted history retain provenance?

It retained participant/provider/model data in `debate_data`, including dynamic adapter model provenance where available. It did not persist first-class `requested_identity` / `effective_identity` / route-fallback semantics.

### 7. Did debate participant identity survive fallback truthfully?

Provider participant identity was protected by the already-closed deliberation invariant: selected participants do not silently fall back to another selected provider. This workstream preserves that invariant and permits only same-AI route fallback inside one identity participant.

### 8. Smallest coherent change

Add a small application-level identity routing seam over the existing provider adapters; keep `DebateOrchestrator`, provider adapters, persistence, credential pools, and model registry in place. Production Reflex selects identity IDs. Same-identity route fallback is resolved behind the application seam and verified from returned model provenance.

### 9. Ownership map

- **CORE:** identity catalogue/inference and truthful same-identity route wrapper.
- **APPLICATION BOUNDARY:** translate selected identities into stable execution slots while preserving existing orchestration.
- **PROVIDER LAYER:** unchanged; existing adapters/model registry remain route/model truth.
- **PRESENTATION:** identity-first selectors and progressive provenance rendering only; no routing decisions.

### 10. Closed-governance compatibility

No closed gate needs wholesale reopening. The accepted AI Product DNA already distinguishes provider, model, participant, and utility and explicitly says gateways such as OpenRouter should not automatically be logical minds. Closed deliberation semantics prohibit participant impersonation; therefore cross-identity participant fallback remains disabled in this bounded workstream.

## Current bounded identity catalogue

Only identities that current repository routes can truthfully pin are selectable:

| AI identity | Current accepted route(s) | Notes |
| --- | --- | --- |
| Gemini | Gemini adapter | provider/model alias provenance verified by adapter |
| GPT-OSS | Groq → Hugging Face | same-identity route fallback allowed |
| Llama | Cloudflare | current Workers AI route pins Llama family |
| DeepSeek | DeepSeek adapter | optional/credential-dependent route |

Claude, proprietary GPT, Grok, Qwen, and Kimi are recognized as future identity families for provenance inference but are **not exposed as selectable identities yet** because this task does not add providers/routes and current repository reality does not provide a truthfully pinned accepted route for them.

OpenRouter, Cloudflare, Groq, Hugging Face, NVIDIA, and similar infrastructure brands are not AI identities. A future curated route through any of them may serve an identity only when the concrete requested/effective model can be proven.

## Fallback contract

### Same-identity route fallback

Allowed:

`GPT-OSS via Groq fails → GPT-OSS via Hugging Face succeeds`

Persist:

- requested identity;
- effective identity;
- actual model when known;
- actual route provider;
- route fallback flag/reason.

### Cross-identity fallback

Disabled for participant execution in this workstream.

`Claude unavailable → GPT answers but remains labelled Claude` is forbidden.

Clear identity-unavailable failure is the accepted behavior until a separately governed, explicitly visible cross-identity fallback contract exists.

## Persistence / presentation truth

Participant records gain additive identity fields inside existing `debate_data`; no new table/schema/database is introduced. History projection reads persisted truth and remains backward-compatible with old provider-only chat rows.

Primary presentation shows AI identity. Model and route are secondary provenance. Presentation never decides route or rewrites application truth.

## Security

No API key or credential value enters browser state or persisted provenance. Existing per-user provider resource pools and server-side credential boundaries remain unchanged.

## Verification target

Prove:

1. selected identity + primary route success;
2. same-identity secondary route success after primary failure;
3. all routes fail → clear identity failure, no impersonation;
4. cross-identity route is not silently used;
5. multi-AI participant provenance remains independently truthful;
6. provider-route change does not change selected identity semantics;
7. identity/model/route provenance survives persistence reload;
8. production Reflex primary selector exposes identities rather than gateway brands;
9. legacy provider-keyed application callers remain compatible where required for rollback/tests;
10. full regression/host/rollback gates remain green.

## Non-goals

No provider expansion, billing engine, quota scheduler, new database, microservice, REST/RPC layer, marketplace, autonomous provider optimizer, Streamlit removal, Railway final integration, or production cutover.

## Cutover law

`FULL_OPERATIONAL_PROVIDER_VERIFICATION = NOT CLAIMED BY THIS WORKSTREAM`

`RAILWAY_FINAL_INTEGRATION = HOLD`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`
