# MULTIMIND — DEEP DEBATE REVISION + USER VERDICT COMPLETION

Status: **IMPLEMENTED / PR VERIFICATION PENDING**
Date: 2026-09-11
Entering baseline: `main@ed18dfe0a839755d88f0391de1593441947a8e06`
Implementation PR: #128

## Why this is a new bounded workstream

The earlier deliberation semantic correction is CLOSED and remains closed. Current repository reality already proves independent participant attempts, real critique rounds, honest participant failure/provenance, bounded judge fallback, synthesis, Release Gate separation, and persisted debate truth.

Two accepted AI Product DNA capabilities remained outside that closed finite contract and were explicitly authorized:

1. **Deep Debate revision semantics** — a participant can react to panel criticism by producing a traceable revised position before final synthesis at deeper execution depth.
2. **Persistent user verdict** — `SYSTEM WINNER` and `USER WINNER` are separate application truths; the user's winner survives persistence/reload without overwriting the system verdict.

This workstream does not reopen the closed PR #107 contract wholesale.

## Implemented contract

### Deep Debate

- Rounds 1–2 preserve the previously closed behavior: independent candidates, then bounded critique when round 2 exists.
- Rounds >=3 are classified as `deep_debate` and add a revision phase after each deep round's critiques.
- Each revision is produced by the same participant through that participant's own selected provider route. There is no cross-provider participant fallback or impersonation.
- Revision input includes the original task, current panel positions, accumulated critiques, and the participant's own current position.
- Initial contributions remain immutable historical artifacts. Revisions are separately recorded with participant/provider/model/round/status provenance.
- A failed revision does not erase the participant's last successful position. Later critiques and judge/synthesis consume the latest successful position.
- Judge/synthesis receives initial contributions, latest participant positions, critiques, and traceable revisions. System winner remains an exact original participant identity.
- Revision and judge prompts explicitly permit justified dissent and prohibit manufactured consensus.

### User verdict

- `MultiMindApplication.record_user_verdict()` records a user's chosen successful participant for one persisted chat.
- The operation validates `session_id`, `chat_id`, and exact successful participant identity against that chat's persisted `debate_data`.
- `system_verdict` is never overwritten by `user_verdict`.
- The persisted user verdict includes participant identity plus requested provider, actual provider, model, role, and recording timestamp.
- Verdict truth remains inside existing `chats.debate_data`; no schema migration or second source of truth was introduced.
- SQLite mutations are session-scoped. Turso mutations are user + session + chat scoped.
- Renderer-neutral Streamlit/Reflex projections expose user verdict, deep-debate depth, and revision count without owning deliberation truth.
- Existing legacy string-form user verdict projection remains readable while the canonical new write format is structured provenance.

## Token/call observability

The pre-send estimate now models the actual bounded call graph:

`candidates + critiques for rounds >1 + revisions for rounds >2 + one judge`

For example, six surviving participants at round depth 3 estimate 25 calls:

`6 candidates + 12 critiques + 6 revisions + 1 judge`.

## Adversarial implementation repair

During implementation, an initial extension/subclass approach duplicated application, orchestrator, and database behavior. It was rejected during diff review because it increased long-term maintenance cost and duplicated closed semantics.

The final implementation instead extends the existing stable boundaries directly:

- `DebateOrchestrator` owns the additional revision phase;
- `MultiMindApplication` owns the user-verdict mutation operation;
- existing SQLite/Turso managers expose the minimal scoped read/update seams;
- no new framework, service, transport, database, or parallel orchestration stack remains.

This preserves the project's BORING / LOW-MAINTENANCE law while keeping the finite PR #107 invariants intact.

## Verification matrix

Deterministic tests now cover:

- rounds 1 and 2 retaining candidate/critique semantics;
- rounds 3+ creating participant-specific same-provider revision calls;
- revision prompts receiving panel positions and critique evidence;
- failed revision preserving the last successful position;
- judge receiving immutable initial contributions plus latest revisions;
- system verdict surviving a different persisted user verdict;
- failed/nonexistent participant rejection;
- cross-session verdict mutation rejection;
- SQLite verdict persistence and provenance;
- Turso user isolation and cross-session failure;
- renderer-neutral revision/user-verdict projection and history reload;
- deep revision call-estimation semantics.

Full Python/RJ4/RJ5/RJ6/Final Gate evidence must be attached to the exact final PR head before merge. Exact-main verification remains required after merge.

## Scope protection

No new service, HTTP/RPC layer, agent framework, database, schema migration, provider redesign, Design-DNA logic, provider expansion, Railway deployment, or production cutover.

Provider expansion and real-runtime operational verification remain separate workstreams.

## Exit

Inspect → implement → targeted semantic tests → adversarial review → repair → full regression/RJ4/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure.

`FULL_OPERATIONAL_PROVIDER_VERIFICATION = NO`

`RAILWAY_FINAL_INTEGRATION = HOLD`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`
