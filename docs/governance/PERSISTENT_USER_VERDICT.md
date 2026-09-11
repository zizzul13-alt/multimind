# MULTIMIND — PERSISTENT USER VERDICT

Status: **CLOSED / FULL FEATURE IMPLEMENTATION OF THIS BOUNDED CONTRACT**
Date: 2026-09-11
Entering baseline: `main@f7e996b123a838394f92d850a8d47a043cc03ead`
Implementation: PR #129
Final PR head: `f77f8bf45ff228fab803cd9e2fe4e2f531842ed6`
Implementation exact-main: `959a848958e53040456bcf522e33220e2c5b67d6`
Owning workstream: AI / Deliberation Semantics

## Product intent

The accepted AI Product DNA distinguishes system judgment from human judgment:

`SYSTEM WINNER = A`

`USER WINNER = B`

Both are application truth. A user may agree with the synthesis judge or prefer another successful participant. Recording that preference must never rewrite the system verdict, participant contribution, final synthesis, eligibility, or future routing automatically.

## Implemented contract

1. Human judgment is mutated only through `MultiMindApplication.set_user_verdict`; presentation does not edit persisted debate JSON directly.
2. Verdict mutation targets an exact persisted `session_id + chat_id` within the active database namespace.
3. A non-empty verdict is accepted only when it references a successful participant ID from that chat's persisted `debate_data`.
4. Human judgment is stored independently as `debate_data.user_verdict`; `system_verdict` remains unchanged.
5. A user may replace their verdict with another successful participant or clear it.
6. Invalid chat IDs, failed/nonexistent participant IDs, malformed debate data, and wrong-session lookups fail closed without corrupting the persisted chat.
7. SQLite and Turso expose the same bounded read/update contract. Turso queries include `user_id + session_id + chat_id`, preventing cross-user verdict mutation.
8. No database/table migration was introduced. Existing backup/export/restore carries the verdict inside the already-authoritative `debate_data` field.
9. Runtime and history projection expose system and user verdicts separately.
10. Reflex exposes a participant-level `My winner` action only on successful participants, a `MY WINNER` marker for the chosen participant, a clear action, and separate history display for system vs human judgment.
11. Reflex binds the vote to the exact `ChatResult.chat_id` returned after durable persistence. It does not infer the target from the latest history row.
12. User verdict remains observation/preference only. It does not alter capability eligibility, participant selection, model resolution, provider routing, judge behavior, or future recommendations.
13. Chats without `user_verdict` remain backward compatible and project an empty human verdict.
14. The accepted Reflex mobile entry remains the single production host entry and the same `rx.App` instance. Verdict presentation wiring extends it without creating a second application tree or moving application truth into presentation.

## Adversarial repair history

The workstream deliberately did not treat the first green-looking implementation as closure.

### Repair 1 — stale projection assertion

Python Regression #355 produced **411 passed / 1 failed** because an older Reflex projection test asserted an exact summary shape that predated the new independent `user_verdict` field. The repair updated the semantic expectation to include an empty backward-compatible human verdict and added malformed-data/history coverage. The implementation contract was not weakened.

### Repair 2 — accepted mobile-host ownership

A first attempt switched `rxconfig.app_module_import` from `multimind_reflex.mobile_entry` to a new verdict entry. Python Regression #359 correctly rejected that change because the accepted mobile-host contract requires `mobile_entry` to remain the production entry and preserve the same app instance.

The repair restored the accepted entry instead of weakening the closed presentation invariant. Verdict wiring now patches the existing workspace presentation through `mobile_entry`, retains `mobile_entry.app is surface.app`, and creates no second `rx.App`.

### Repair 3 — exact verdict target

An intermediate presentation implementation inferred the verdict target from the latest history row. That was rejected as semantically unsafe because ordering/refresh behavior should not determine mutation identity. The final implementation retains the exact persisted `ChatResult.chat_id` and sends that ID through the application mutation path. Tests explicitly forbid `history[-1]` inference.

## Verification evidence

Behavioral and adversarial tests prove:

- system and user verdicts may disagree and both persist;
- verdict survives application reconstruction/history reload;
- replacing and clearing the verdict works;
- failed/nonexistent participants cannot be selected;
- malformed or wrong-session records fail closed;
- SQLite mutation is exact-chat/session scoped;
- Turso mutation is exact user/session/chat scoped and cannot mutate another user;
- backup/restore preserves the verdict without schema migration;
- Reflex projection keeps system and user judgments separate;
- `My winner` is available only for successful participants;
- Reflex targets the exact persisted chat ID rather than an inferred latest row;
- the accepted mobile entry and single-app ownership remain intact.

### Final PR-head verification

Exact final PR head:

`f77f8bf45ff228fab803cd9e2fe4e2f531842ed6`

- Python Regression #363 — **SUCCESS**;
- RJ4 Container Durability #55 — **SUCCESS**;
- RJ5 Dual-Host Torture #125 — **SUCCESS**;
- RJ6 Cutover Rollback Proof #134 — **SUCCESS**;
- Final Gate Operator Readiness #193 — **SUCCESS**.

PR #129 was marked ready only after those final-head gates were clean and was squash-merged with an expected-head guard against exactly `f77f8bf45ff228fab803cd9e2fe4e2f531842ed6`.

### Exact-main implementation verification

Implementation exact-main:

`959a848958e53040456bcf522e33220e2c5b67d6`

- Python Regression #364 — **SUCCESS**;
- RJ4 Container Durability #56 — **SUCCESS**;
- RJ5 Dual-Host Torture #126 — **SUCCESS**;
- RJ6 Cutover Rollback Proof #135 — **SUCCESS**;
- Final Gate Operator Readiness #194 — **SUCCESS**.

Known in-scope residuals after exact-main verification: **0**.

## Scope protection

This workstream did **not** introduce a new database, table, service, transport, agent framework, preference-learning loop, scoring system, or automatic future-roster bias. It did not add providers, redesign Design-DNA, authorize Railway integration, or authorize production cutover.

## Closure classification

`PERSISTENT_USER_VERDICT = FULL FEATURE IMPLEMENTATION / CLOSED`

`KNOWN_IN_SCOPE_RESIDUALS = 0`

`FULL_OPERATIONAL_PROVIDER_VERIFICATION = NOT CLAIMED BY THIS WORKSTREAM`

`RAILWAY_FINAL_INTEGRATION = HOLD`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`

This closure applies only to the finite persistent independent user-verdict contract. It does not claim that every remaining AI Product DNA destination item is implemented or operationally verified.
