# MULTIMIND — PER-USER PROVIDER RESOURCE POOLS

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-10
Baseline: `main@4b7ebcc2719422a06ef17de6edd5915eb927a2a9`

## Mission

Make provider credentials user-scoped at the deployment boundary while preserving a small boring runtime contract, provider independence, explicit participant truth, and the existing persistence/security boundaries.

Accepted shape:

`LOGIN USER → USER RESOURCE POOL → SELECTED PROVIDER → PRIMARY RESOURCE → MODEL RESOLUTION → PROVIDER CALL`

The deployment-level `default` pool remains available only for explicit operator/default execution and compatibility proof. It must not silently become every authenticated user's credential pool.

## Finite contract

1. Railway/server-side secrets remain authoritative; no credential may be persisted into application/session/database truth.
2. Environment secrets support named user slots, each mapped to one validated MultiMind user id.
3. A user receives only the credentials mapped to that exact user id. No cross-user fallback is allowed.
4. Existing global `MULTIMIND_*` provider variables remain the `default` operator pool for compatibility and smoke proof.
5. Generic non-deployment `Config.get_api_keys` mappings preserve their historical optional `default` fallback unless the source explicitly declares strict user isolation.
6. Deployment environment source explicitly declares strict user isolation.
7. A provider may expose more than one configured resource for the same user. Multiple resources are represented explicitly and deterministically; they are not treated as automatic quota multiplication.
8. The first configured resource is the primary runtime credential. Additional same-provider resources are retained as metadata for future explicit resource selection/failover policy but are not automatically rotated on rate limit or failure in this bounded workstream.
9. Cloudflare account id remains paired with the chosen Cloudflare credential resource.
10. Missing user-specific credentials fail boringly to an empty provider set rather than borrowing another user's/default credentials.
11. No new database, secret service, network layer, auth framework, or external vault is introduced.
12. Railway final integration and production cutover remain out of scope.

## Environment naming contract

User slots are operational labels and are deliberately separate from user ids:

```text
MULTIMIND_USER_A_ID=alice
MULTIMIND_USER_A_GEMINI_KEY=...
MULTIMIND_USER_A_GEMINI_KEY_2=...
MULTIMIND_USER_A_GROQ_KEY=...

MULTIMIND_USER_B_ID=bob
MULTIMIND_USER_B_GEMINI_KEY=...
```

The `_ID` value is validated with the existing `Config.validate_user_id` law. Slot names use `[A-Z0-9_]+` and exist only so Railway environment variable names remain simple. Numbered resources use `_2`, `_3`, ... after the canonical key suffix.

## Required proof

- exact user match returns only that user's credentials;
- user A cannot see user B credentials;
- unknown user cannot fall back to deployment `default`;
- explicit `default` user can still use global operator pool;
- generic mapping compatibility retains historical default fallback;
- invalid/duplicate user-slot ids fail closed;
- same-user multi-resource ordering is deterministic;
- primary runtime key is the first configured resource;
- extra resources are retained without automatic rate-limit rotation;
- provider/model/deliberation semantics remain unchanged;
- Python regression, RJ5, RJ6, Final Gate remain green.

## Exit

Inspect → implement → targeted isolation tests → adversarial review → repair → full regression/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure → STOP before Railway final integration.
