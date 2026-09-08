# MULTIMIND — REAL DEPLOYMENT CANDIDATE STATUS

Status date: 2026-09-08
Owning workstream: REAL DEPLOYMENT ARCHITECTURE / PRODUCTION READINESS
Production cutover authorized by this document: NO

## 1. PURPOSE

This document records the real deployment candidate that exists outside CI and separates proven runtime facts from the one remaining observation gate. Repository/runtime reality governs over stale handoffs.

## 2. ACCEPTED CANDIDATE BASELINE

Current accepted candidate implementation includes Turso durable persistence, repaired Groq runtime target, and the mobile-friendly Step-6 restore picker through merged PR #106 / main `7a40f2ade5ffde331f44a6276c7267e508bd4260` before this governance-only reconciliation.

## 3. FROZEN CANDIDATE TOPOLOGY

```text
Browser
→ Railway public HTTPS
→ Reflex frontend/backend
→ MultiMindApplication / composition boundary
→ existing orchestration / provider routing / transient file handling / memory
→ Turso remote user-scoped persistence
→ external AI providers
```

Fallbacks remain:

```text
Turso credentials absent together → legacy SQLite fallback/rollback
private Design-DNA absent/failing/incompatible → neutral safe presentation
```

No transport service, second application truth, second provider router, object store, or presentation-owned persistence is required for this candidate.

## 4. REAL DEPLOYMENT / DURABILITY EVIDENCE

```text
Railway build/deploy                         PASS
Public HTTPS frontend/backend                PASS
Reflex rendering/login/event path            PASS
Restricted CORS/WebSocket path               PASS
Private-DNA-absent neutral fallback          PASS
Workspace navigation                         PASS
RAILWAY_LOCAL_SQLITE_DURABILITY              FAIL (accepted negative proof)
REAL_TURSO_REDEPLOY_DURABILITY               PASS
```

The local-SQLite failure is the evidence that Railway-local filesystem is not authoritative persistence. Turso is authoritative for the accepted candidate when both Turso credentials are present.

## 5. FILE / UPLOAD DURABILITY DECISION — CLOSED

```text
UPLOAD_BYTES = TRANSIENT REQUEST INPUT
EXTRACTED_FILE_CONTEXT = TRANSIENT REQUEST CONTEXT
DURABLE_FILE_LIBRARY = NOT AN EXISTING FEATURE CONTRACT
OBJECT_STORAGE = NOT REQUIRED FOR CURRENT PRODUCTION CUTOVER
```

A future retrievable file library is a separate product/storage decision.

## 6. STEP 3 — REAL PROVIDER SMOKE — PASS

A real Railway candidate with server-side Groq credentials completed the full path:

```text
Browser
→ Reflex
→ MultiMindApplication
→ existing provider router
→ Groq openai/gpt-oss-20b
→ expected MULTIMIND_GROQ_SMOKE_OK response visible
→ response persisted to Turso
→ Railway container replacement/redeploy
→ same chat rehydrated after login
```

```text
REAL_GROQ_OUTBOUND_CALL       PASS
EXPECTED_PROVIDER_RESPONSE    PASS
REFLEX_RESPONSE_VISIBLE       PASS
RESPONSE_PERSISTED_TO_TURSO   PASS
RESPONSE_SURVIVES_REDEPLOY    PASS
STEP_3_REAL_PROVIDER_SMOKE    PASS
```

No secret values are recorded here.

## 7. STEP 4 — FILE/UPLOAD SEMANTICS — PASS

The transient-upload contract above remains accepted and closed. No object-storage scope expansion is justified.

## 8. STEP 5 — SERVERLESS / ZERO-CARD ECONOMICS — OPEN OBSERVATION GATE

Serverless was enabled and a fresh container was deployed before the valid test. After a real idle interval the service did not reach Railway SLEEPING state.

```text
SERVERLESS_CONFIGURED             PASS
FRESH_CONTAINER_TEST              PASS
REAL_SERVERLESS_SLEEP_OBSERVED    FAIL / RESIDUAL CONFIRMED
AUTO_WAKE_PROOF                   NOT TESTABLE WITHOUT REAL SLEEP
NO_CARD_REQUIREMENT               PASS
REAL_STEADY_STATE_ECONOMICS       PENDING REPRESENTATIVE OBSERVATION
STEP_5_OVERALL                    OPEN
```

This residual is not currently a correctness, persistence, provider, recovery, or security failure. Do not redesign Reflex or add infrastructure merely to force sleep. Observe representative Railway usage after the deployment/test storm. If steady-state usage fits the accepted zero-card/free-credit constraint, accept sleep as a non-functional optimization residual. If economics violates the hard constraint, the residual becomes an economic blocker requiring the smallest coherent repair.

## 9. STEP 6 — BACKUP / RESTORE / RECOVERY — PASS

Automated contracts remain PASS for portable SQLite format, user-scoped restore semantics, cross-user isolation, and SQLite rollback portability.

A real destructive dummy-user recovery drill was completed against the live Railway + Turso candidate on 2026-09-08:

```text
Portable SQLite backup exported                 PASS
Pre-backup session/chat marker present           PASS
Post-backup mutation created                     PASS
Backup selected from Android                     PASS
Backup uploaded/staged through Reflex            PASS
Destructive restore executed against Turso       PASS
Pre-backup session recovered                     PASS
Pre-backup chat marker recovered                 PASS
Post-backup mutation removed                     PASS
Unrelated railway-smoke-01 data remained intact  PASS
REAL_TURSO_DUMMY_RESTORE                         PASS
```

During the drill, the original restore picker exposed a real mobile UX residual: the backup could be exported but selection/staging was not sufficiently explicit. The bounded repair was implemented, regression-tested, merged in PR #106, deployed as exact main `7a40f2ade5ffde331f44a6276c7267e508bd4260`, and then proven in the same live drill. Railway HTTP evidence showed the backup upload endpoint returning HTTP 200.

STEP 6 is therefore CLOSED PASS. No valuable production data was used for the destructive mutation.

## 10. STEP 7 — FINAL DEPLOYMENT EVIDENCE + ENVIRONMENT FREEZE

All non-Step-5 architecture, repository, CI, and required real-runtime evidence for the current candidate is reconciled.

Frozen environment contract:

```text
HOST                         Railway
PRESENTATION                 Reflex
APPLICATION BOUNDARY         MultiMindApplication
AUTHORITATIVE PERSISTENCE    Turso when credential pair present
ROLLBACK/PORTABLE FORMAT     SQLite
PROVIDER SMOKE               Groq via existing provider router
UPLOAD STORAGE               transient request context only
PRIVATE DESIGN-DNA           optional; neutral fallback mandatory
SECRETS                      Railway runtime secret store / process env
STREAMLIT                    retained rollback/reference presentation
```

```text
STEP_7_TOPOLOGY_FREEZE              PASS
STEP_7_REPOSITORY_CONTRACT          PASS
STEP_7_RUNTIME_EVIDENCE_RECONCILED  PASS
STEP_7_FINAL_ENVIRONMENT_ACCEPTANCE BLOCKED ONLY BY STEP_5 ECONOMIC OBSERVATION
```

No further architecture change is authorized by Step 7. New findings must be concrete blockers or accepted scope expansion; curiosity/cleanup does not reopen closed gates.

## 11. STEP 3–8 SUMMARY

```text
STEP 3  REAL PROVIDER SMOKE                    PASS
STEP 4  FILE/UPLOAD DURABILITY SEMANTICS       PASS
STEP 5  SERVERLESS / ZERO-CARD ECONOMICS       OPEN — observation gate
STEP 6  BACKUP / RESTORE / RECOVERY            PASS
STEP 7  ENVIRONMENT / TOPOLOGY FREEZE          PASS; final acceptance waits only Step 5
STEP 8  EXPLICIT PRODUCTION CUTOVER             NOT GRANTED / GOVERNOR-USER RESERVED
```

## 12. REMAINING HUMAN ACTIONS — MINIMUM SET

Only Step 5 observation and Step 8 decision remain user/Governor-held:

1. allow representative normal Railway operation long enough to avoid extrapolating the build/deploy/redeploy test storm;
2. inspect real Railway usage/burn rate against the hard zero-card/free-credit constraint;
3. if Step 5 is accepted, make a separate explicit Step-8 production cutover decision.

No additional provider, backup/restore, file-storage, or topology experiment is required unless new evidence invalidates a closed proof.

## 13. GOVERNOR DELEGATION — NON-USER-HELD AUTO-PASS

Accepted 2026-09-07: all non-user-held evidence in Steps 3/5/6/7 is owned by this workstream for autonomous inspection, bounded repair, rerun, review, reconciliation, and closure. Missing real-world proof may never be converted to PASS merely by delegation.

## 14. CUTOVER LAW

Step 7 freeze is not production cutover authorization. Until Step 5 is accepted and the Governor/user explicitly authorizes Step 8:

```text
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```

Streamlit remains rollback/reference presentation. No destructive cleanup, provider redesign, database rewrite, or old-host retirement is authorized.