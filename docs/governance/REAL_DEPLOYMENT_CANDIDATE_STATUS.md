# MULTIMIND — REAL DEPLOYMENT CANDIDATE STATUS

Status date: 2026-09-07
Owning workstream: REAL DEPLOYMENT ARCHITECTURE / PRODUCTION READINESS
Production cutover authorized by this document: NO

## 1. PURPOSE

This document records the real deployment candidate that now exists outside CI and separates proven runtime facts from remaining operator-held proofs.

It supplements the historical RJ migration reports. It does not rewrite their closed evidence. Where older operator text assumes local SQLite is the only production persistence path, current repository implementation and this deployment-candidate record govern the real Railway candidate.

## 2. EXACT REPOSITORY BASELINE

Accepted deployment-candidate implementation baseline before this status update:

```text
12c8b54f8081b20561d544dccdd623102c350254
```

That commit includes the bounded Turso persistence adapter merged in PR #99.

## 3. FROZEN CANDIDATE TOPOLOGY

The smallest accepted candidate topology is:

```text
Browser
→ Railway public HTTPS
→ Reflex frontend/backend
→ MultiMindApplication / composition boundary
→ existing orchestration / provider routing / file handling / memory
→ Turso remote user-scoped persistence
```

with:

```text
Turso credentials absent together
→ SQLite fallback/rollback persistence
```

and:

```text
private Design-DNA absent / failing / incompatible
→ neutral safe presentation
→ application remains operational
```

No FastAPI/REST/RPC glue, second application truth, second provider router, or presentation-owned persistence has been introduced.

## 4. REAL RUNTIME EVIDENCE ALREADY PROVEN

The real Railway service has already demonstrated:

```text
Railway build/deploy                         PASS
Public HTTPS frontend                       PASS
Public HTTPS backend /_health               PASS
Reflex rendering                            PASS
Login/event path                            PASS
Restricted CORS/WebSocket event path        PASS
Private-DNA-absent neutral fallback         PASS
Workspace navigation                        PASS
```

The original Railway-local SQLite experiment deliberately created a dummy session and then redeployed the same service. The dummy session disappeared.

```text
RAILWAY_LOCAL_SQLITE_DURABILITY = FAIL
```

That failure is accepted evidence that the current Railway filesystem cannot be treated as authoritative durable user persistence.

The accepted bounded repair moved the real deployment candidate to external Turso persistence. A new dummy session was then created under the Turso-backed deployment and the Railway service was redeployed. The same session remained visible after redeploy.

```text
REAL_TURSO_REDEPLOY_DURABILITY = PASS
```

This proves the application is no longer relying on Railway-local ephemeral SQLite for authoritative session durability when both Turso runtime credentials are present.

## 5. FILE / UPLOAD DURABILITY DECISION

Repository inspection closes the file-storage question for the current feature contract.

`MultiMindApplication.execute_chat()` passes uploaded objects directly to `FileHandler.handle()`. `FileHandler` validates and extracts bounded content in memory. The extracted file context is prepended only to the active request context sent to the provider/debate layer.

The persisted chat record contains the original typed prompt, compressed-prompt metadata when applicable, final answer, debate data, tokens and cost. It does not persist the uploaded binary, an upload pathname, or the extracted file body as a separate durable artifact.

Therefore the current upload contract is:

```text
UPLOAD_BYTES = TRANSIENT REQUEST INPUT
EXTRACTED_FILE_CONTEXT = TRANSIENT REQUEST CONTEXT
DURABLE_FILE_LIBRARY = NOT AN EXISTING FEATURE CONTRACT
OBJECT_STORAGE = NOT REQUIRED FOR CURRENT PRODUCTION CUTOVER
```

A future retrievable file-library feature would be a separate product/storage decision and must not be smuggled into this deployment gate.

`/app/data` may still be used by the SQLite fallback/rollback path and other local operational artifacts, but it is not required to preserve the current normal chat-upload input after a request finishes.

## 6. BACKUP / RESTORE CONTRACT STATUS

The Turso adapter preserves the existing portable SQLite backup format rather than inventing a second backup API.

Current implementation evidence proves:

- user-scoped Turso rows can export to validated SQLite bytes;
- those bytes can restore into the legacy SQLite manager;
- restoring a portable SQLite snapshot into Turso replaces only the active user's remote rows;
- another user's rows remain isolated;
- restore verification compares exact session/chat ID sets;
- partial Turso credentials fail closed in composition;
- explicit database-factory seams remain authoritative for tests/rollback.

Automated contract status:

```text
PORTABLE_BACKUP_FORMAT = PASS
USER_SCOPED_RESTORE_SEMANTICS = PASS
CROSS_USER_ISOLATION = PASS
SQLITE_ROLLBACK_PORTABILITY = PASS
```

A real destructive remote restore against the live candidate has not been claimed by repository tests. Before cutover authorization, perform one bounded dummy-user export/restore round trip or equivalent isolated real-Turso recovery proof. Do not use real valuable user data for the destructive portion of that test.

## 7. RAILWAY SERVERLESS / ZERO-CARD ECONOMIC CONTRACT

Current Railway documentation records:

- Free plan price: $0/month with $1 monthly resource credit;
- Trial: one-time $5 grant, then reverts to Free after trial/credit exhaustion;
- Serverless detects inactivity from outbound traffic;
- a service becomes sleep-eligible after an outbound-quiet interval and incoming Internet traffic wakes it automatically;
- the first wake request can incur cold-start latency and may return an initial 502;
- open/background database or telemetry traffic can prevent sleep;
- Free-tier deployments in Southeast Asia are restricted during 08:00–20:00 SGT peak hours;
- existing running services are not described as being shut down merely because a deploy is peak-hour restricted.

The Turso adapter is sleep-friendly at the persistence layer because each operation opens a connection, performs bounded work, and closes the connection in `finally`; it does not maintain a repository-defined permanent DB pool.

This establishes the architecture contract but not the real runtime/economic proof.

Still required before environment acceptance:

```text
REAL_SERVERLESS_SLEEP_OBSERVED = PENDING
NORMAL_BROWSER_REQUEST_AUTO_WAKES = PENDING
NO_MANUAL_RESUME_REQUIRED = PENDING
REAL_USAGE_FITS_ZERO_CARD_BUDGET = PENDING
```

Do not infer these from documentation alone. Observe the actual Railway service and usage meter.

## 8. PROVIDER SMOKE STATUS

Provider routing remains behind the existing application/provider boundaries. The `UnifiedAgent` priority order is currently:

```text
Cloudflare → Groq → OpenRouter → Hugging Face → DeepSeek → Gemini
```

The deployment preflight requires at least one provider credential or remote-provider URL, but a non-empty secret is not provider usability proof.

Still required:

```text
ONE_REAL_PROVIDER_SECRET_STAGED_SERVER_SIDE = PENDING
REAL_OUTBOUND_PROVIDER_CALL = PENDING
SUCCESS_RESPONSE_VISIBLE_IN_REFLEX = PENDING
RESPONSE_PERSISTED_TO_TURSO = PENDING
RESPONSE_SURVIVES_REDEPLOY = PENDING
```

This is an operator-held secret/runtime action. Real credential values must never be pasted into repository governance, issues, PRs, or chat transcripts.

## 9. PREFLIGHT RESIDUAL FOUND AND REPAIRED

Repository inspection found a fail-closed gap: application composition rejected partial Turso credentials, but `final_gate_preflight.py` did not detect that configuration before runtime.

The current bounded repair adds the same pair invariant to the operator preflight:

```text
TURSO_DATABASE_URL present XOR TURSO_AUTH_TOKEN present
→ TURSO_CREDENTIAL_PAIR_INCOMPLETE
→ PREFLIGHT FAIL
```

Both absent remains the accepted SQLite fallback/rollback mode. Both present remains the accepted Turso mode.

## 10. STEP 3–8 STATUS

```text
STEP 3  REAL PROVIDER SMOKE
        PENDING — operator secret/runtime proof only

STEP 4  FILE/UPLOAD DURABILITY SEMANTICS
        PASS — transient request input; no object storage required

STEP 5  RAILWAY SLEEP/AUTO-WAKE + ECONOMICS
        CONTRACT PASS / REAL RUNTIME PROOF PENDING

STEP 6  BACKUP/RESTORE/RECOVERY
        AUTOMATED CONTRACT PASS / REAL TURSO ROUND-TRIP PENDING

STEP 7  FINAL DEPLOYMENT EVIDENCE + ENVIRONMENT FREEZE
        TOPOLOGY FROZEN / FINAL ACCEPTANCE PENDING STEPS 3, 5, 6 RUNTIME PROOFS

STEP 8  EXPLICIT PRODUCTION CUTOVER DECISION
        NOT GRANTED / GOVERNOR-USER RESERVED
```

## 11. REMAINING HUMAN ACTIONS — MINIMUM SET

Only actions requiring real account secrets or observation remain human-held:

1. stage exactly one provider credential in Railway and run one low-cost real prompt;
2. verify the resulting chat is persisted in Turso and remains after redeploy;
3. enable/use the accepted Railway Serverless configuration when appropriate, allow the service to become idle, then prove a normal browser request wakes it without dashboard intervention;
4. inspect real Railway usage after representative use and confirm the hard Rp0/no-card constraint remains viable;
5. perform one isolated real-Turso dummy-user export/restore recovery round trip.

Everything else should remain automated or repository-governed.

## 12. GOVERNOR DELEGATION — NON-USER-HELD AUTO-PASS

Accepted on 2026-09-07 by the user/Governor for this deployment workstream:

```text
ALL NON-USER-HELD EVIDENCE IN STEPS 3 / 5 / 6 / 7
→ inspect autonomously
→ repair bounded repository residuals autonomously
→ rerun/review until green when tooling permits
→ record PASS without asking the user to repeat mechanical repository work
```

This delegation does not waive evidence requirements. It only removes unnecessary operator handoffs.

The following remain user-held because they require real account secrets, external dashboard state, destructive confirmation, or direct real-runtime observation:

```text
STEP 3: stage one real provider secret and perform/observe the real provider smoke
STEP 5: observe actual sleep/auto-wake behavior and real Railway usage/cost
STEP 6: authorize/perform one isolated real-Turso dummy restore round trip
STEP 8: explicit production cutover decision
```

For Steps 3, 5, 6 and 7, any repository-only, CI-only, documentation, contract, regression, static-analysis, composition, routing, persistence, backup-format, or deployment-artifact evidence is now owned by this workstream and should be closed without further user intervention unless a true blocker or scope-expanding decision appears.

This delegation does not authorize production cutover and does not permit weakening tests, bypassing fail-closed checks, adding new infrastructure, or changing accepted architecture merely to obtain a green result.

## 13. CUTOVER LAW

No result above independently authorizes production cutover.

Until the remaining runtime proofs are green and an explicit Governor/user authorization is issued:

```text
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```

Streamlit remains the rollback/reference presentation. No destructive cleanup, provider redesign, database rewrite, or old-host retirement is authorized here.
