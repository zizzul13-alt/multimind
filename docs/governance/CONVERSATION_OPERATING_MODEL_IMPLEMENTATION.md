# MultiMind Conversation Operating Model — Implementation Candidate

Status: **IMPLEMENTATION CANDIDATE / PR VERIFICATION REQUIRED**

Baseline: `main@339aa37e6d695d6420d535deb61ff33e8fbb415e`.

This package implements the accepted bounded path through **Auto/Manual AI selection**. It does not authorize production cutover or real external-resource smoke.

## Implemented chain

`CONVERSATION → USER-SCOPED RELEVANT-HISTORY RETRIEVAL → EXPLICIT TASK CRYSTALLIZATION → AUTO/MANUAL WORK MODE → AUTO/MANUAL AI IDENTITY → EXISTING IDENTITY ROUTING → COUNCIL/DELIBERATION → PERSISTED RESULT + TASK CHECKPOINT`

### Laws preserved

- Manual work-mode selection overrides automatic inference in its scope.
- Auto work mode chooses only Coding / Research / Thinking; Council is not a mode.
- Work-mode selection and AI/model selection are independent axes.
- Manual AI identity remains explicit execution truth.
- Auto AI chooses only identities backed by the runtime eligible identity inventory. It never invents an identity.
- Provider/gateway routing remains below identity selection and may not silently cross identities.
- Auto selection does **not** escalate authority. This package keeps presentation execution authority at `think`; capability/action authority is a later bounded workstream.
- Retrieval is user-scoped through the already user-scoped database manager. No new database, vector service, HTTP service, or frontend source of truth is introduced.
- Task state crystallizes only on explicit execution intent and is checkpointed inside the already durable chat `debate_data.product_semantics` record.
- Repository/governance truth remains authoritative over retrieved conversational memory.

## Persistence/recovery

No schema migration is required. Existing SQLite/Turso session/chat persistence and backup/restore continue to carry the operating checkpoint because it is stored in existing debate JSON. Runtime memory remains a cache, not authoritative persistence.

## Deferred deliberately

- real external API/resource smoke;
- production cutover;
- capability/plugin action authority;
- media-understanding expansion;
- semantic/vector embeddings or a separate memory database;
- Design-DNA changes.

Acceptance requires targeted tests plus the repository regression/host/recovery gates. Plans or this document alone do not establish closure.
