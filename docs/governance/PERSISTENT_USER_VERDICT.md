# MULTIMIND — PERSISTENT USER VERDICT

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-11
Entering baseline: `main@f7e996b123a838394f92d850a8d47a043cc03ead`
Owning workstream: AI / Deliberation Semantics

## Product intent

The accepted AI Product DNA distinguishes system judgment from human judgment:

`SYSTEM WINNER = A`

`USER WINNER = B`

Both are application truth. A user may agree with the synthesis judge or prefer another successful participant. Recording that preference must never rewrite the system verdict, participant contribution, final synthesis, eligibility, or future routing automatically.

## Current gap at entry

Current repository state persists `system_verdict` inside each chat's `debate_data`, but there is no application mutation that records an independent user verdict. Reflex can display the system winner but cannot persist a user's participant preference. The existing chat row already owns structured `debate_data`, so a new table/database/service is unnecessary.

## Finite implementation contract

1. Add application-level user-verdict mutation behind `MultiMindApplication`; presentation must not mutate database JSON directly.
2. Verdict target is one persisted chat owned by the current user/session database namespace.
3. A non-empty user verdict must reference a **successful participant ID from that chat's persisted debate_data**.
4. User verdict is stored independently as `debate_data.user_verdict`; `system_verdict` is never overwritten.
5. User may replace their verdict with another successful participant or clear it.
6. Invalid chat IDs, invalid participant IDs, malformed debate data, or failed participants must fail closed without corrupting the chat.
7. SQLite and Turso adapters implement the same bounded update contract. Turso update must remain scoped by `user_id`; no cross-user mutation is possible.
8. Existing backup/export/restore remains compatible because verdict lives inside the already-authoritative `debate_data` field rather than requiring a schema migration.
9. Runtime/result projection and history expose system verdict and user verdict separately.
10. Reflex provides a small explicit participant-level "My winner" action only for successful contributions, shows the currently recorded user verdict, and permits clearing it. Presentation state reflects application truth after persistence.
11. User verdict is observation/preference only. It must not change capability eligibility, participant selection, model resolution, routing, judge behavior, or future recommendations in this workstream.
12. Streamlit/reference and generic presentation readers must remain able to read chats with or without `user_verdict`; absence is backward-compatible.

## Verification

Prove at minimum:

- system and user verdict can disagree and both persist;
- user verdict survives application reconstruction/history reload;
- replacing and clearing verdict works;
- failed/nonexistent participant cannot be chosen;
- malformed/foreign chat update fails closed;
- SQLite mutation only touches requested chat;
- Turso mutation includes `user_id` scope and cannot touch another user;
- backup/restore carries verdict unchanged through existing debate_data;
- Reflex projection exposes both truths without inventing them;
- existing AI/persistence/security/host regressions remain green.

## Scope protection

No new database, table, network service, framework, preference-learning loop, scoring system, or automatic future-roster bias. No provider expansion. No Design-DNA redesign. No Railway integration or production cutover.

## Exit

Inspect → implement → targeted semantic/persistence tests → adversarial review → repair → Python/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure.

`PRODUCTION_CUTOVER_AUTHORIZED = NO`
