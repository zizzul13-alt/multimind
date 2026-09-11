# MULTIMIND — DEEP DEBATE REVISION + USER VERDICT COMPLETION

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-11
Entering baseline: `main@ed18dfe0a839755d88f0391de1593441947a8e06`

## Why this is a new bounded workstream

The earlier deliberation semantic correction is CLOSED and remains closed. Current repository reality already proves independent participant attempts, real critique rounds, honest participant failure/provenance, bounded judge fallback, synthesis, Release Gate separation, and persisted debate truth.

Two accepted AI Product DNA capabilities remain outside that closed finite contract and are now explicitly authorized:

1. **Deep Debate revision semantics** — a participant must be able to react to panel criticism by producing a traceable revised position before final synthesis at deeper execution depth.
2. **Persistent user verdict** — `SYSTEM WINNER` and `USER WINNER` are separate application truths; the user's winner must survive persistence/reload without overwriting the system verdict.

This workstream does not reopen the closed PR #107 contract wholesale.

## Finite contract

### Deep Debate

- Rounds 1–2 preserve current behavior: independent candidates, then bounded critique when round 2 exists.
- Rounds >=3 are explicitly classified as `deep_debate` and add a revision phase after each deep round's critiques.
- A revision is produced by the same participant through its own selected provider route; there is no cross-provider impersonation/fallback.
- Revision input includes the original task, current panel positions, and the critique evidence available for that round.
- Initial contributions remain immutable historical artifacts. Revisions are separately recorded with participant/provider/model/round/status provenance.
- A failed revision does not erase the participant's last successful position; later deliberation and judge/synthesis use the latest successful position.
- Judge/synthesis receives initial contributions, successful revisions, and critiques. System winner remains an exact original participant identity.
- Useful disagreement may remain unresolved and must not be forced away by the revision contract.

### User verdict

- Application exposes a bounded operation to record a user's chosen successful participant for one persisted chat.
- The operation validates `session_id`, `chat_id`, and exact successful participant identity against that chat's persisted `debate_data`.
- `system_verdict` is never overwritten by `user_verdict`.
- User verdict is stored inside the existing `debate_data` JSON, avoiding a database migration or second source of truth.
- SQLite and Turso adapters provide equivalent user-scoped chat read/update seams.
- Reflex may project and mutate verdict only through `MultiMindApplication`; presentation does not own verdict truth.
- History/reload exposes both system and user verdicts.

## Token/call observability

Pre-send estimates must reflect deep revision calls rather than underestimating rounds >=3.

## Verification

Prove at minimum:

- rounds 1 and 2 retain existing candidate/critique call semantics;
- rounds 3+ create participant-specific revision calls;
- revision sees panel + critiques and cannot cross-provider fallback;
- failed revision preserves last successful position;
- later round and judge consume latest successful revisions;
- revision provenance is persisted/reloaded;
- system verdict survives recording a different user verdict;
- failed/nonexistent participant cannot become user verdict;
- chat/session scoping prevents cross-session mutation;
- SQLite and Turso verdict update semantics match;
- Reflex projection/history exposes user verdict without owning it;
- call/token estimator accounts for revision phase;
- full regression and migration/cutover proof workflows remain green.

## Scope protection

No new service, HTTP/RPC layer, agent framework, database, schema migration, provider redesign, Design-DNA logic, provider expansion, Railway deployment, or production cutover.

Provider expansion and real-runtime operational verification remain separate workstreams.

## Exit

Inspect → implement → targeted semantic tests → adversarial review → repair → full regression/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure.

`PRODUCTION_CUTOVER_AUTHORIZED = NO`
