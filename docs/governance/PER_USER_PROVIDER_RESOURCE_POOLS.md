# MULTIMIND — PER-USER PROVIDER RESOURCE POOLS

Status: **CLOSED / FULL FEATURE IMPLEMENTATION OF THIS BOUNDED CONTRACT**
Date: 2026-09-10
Entering baseline: `main@4b7ebcc2719422a06ef17de6edd5915eb927a2a9`
Implementation: PR #110
Final PR head: `e20e649884718c35857824a068991089a7748e6c`
Implementation exact-main: `441543faf629258650398726606fb87fb94a4f59`

## Mission

Prevent deployment-level provider credentials from becoming an implicit shared quota/source of truth across authenticated users while preserving the existing composition boundary, provider adapters, dynamic model resolution, and low-maintenance deployment.

Accepted direction:

`AUTHENTICATED USER → USER-SCOPED PROVIDER RESOURCE POOL → EXPLICIT DEFAULT RESOURCE PER PROVIDER → PROVIDER ADAPTER → MODEL RESOLVER`

Provider resources are now selectable per canonical authenticated user. Existing deployment-level `MULTIMIND_*` credentials remain an explicit operator/default pool and migration path, not an automatic cross-user quota source once per-user pools are configured.

## Implemented behavior

- Added `utils/provider_resources.py` as a small server-side parser for per-user provider resource pools.
- Added canonical deployment secret `MULTIMIND_USER_PROVIDER_POOLS_JSON`.
- Added policy variable `MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS`.
- `Config.get_api_keys()` now supports strict lookup through `allow_default=False`; generic callers preserve the historical default-fallback behavior unless they opt into strict isolation.
- `build_application_for_user()` threads credential-fallback policy through the existing composition boundary without moving credential truth into presentation code.
- Reflex `environment_secrets_source()` now combines parsed user pools with the existing deployment/operator pool under the reserved `default` namespace.
- Authenticated Reflex composition uses the validated `user_id` already owned by the existing identity boundary.
- Once `MULTIMIND_USER_PROVIDER_POOLS_JSON` is nonblank, authenticated users enter strict isolation by default: a missing user pool resolves to empty provider credentials rather than another user's or the operator's credentials.
- Before a per-user pool is configured, the legacy deployment/default pool remains usable so merging this implementation cannot silently disable an already-running deployment.
- Operators may explicitly force either behavior with `MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS=true|false`.
- A nonblank malformed per-user pool activates strict fail-closed behavior rather than silently falling back to operator credentials.
- The `default` identity namespace is reserved for deployment/operator credentials and cannot be supplied through the per-user JSON.
- Multiple named resources for one provider are representable, but only the explicitly declared default resource is selected by current provider construction. Additional resources remain inert; there is no automatic quota/rate-limit key rotation.
- Cloudflare resources preserve the paired key/account-id requirement.
- No provider secret value is written to repository source, browser state, chat/session persistence, or presentation provenance.
- No database, network service, remote secret manager, framework, transport boundary, or provider-architecture redesign was introduced.

## Server-side format

Canonical deployment variable:

`MULTIMIND_USER_PROVIDER_POOLS_JSON`

Redacted shape:

```json
{
  "izzul": {
    "gemini": {"default": "personal", "resources": {"personal": "...", "project-b": "..."}},
    "groq": {"default": "personal", "resources": {"personal": "..."}},
    "cloudflare": {
      "default": "personal",
      "resources": {
        "personal": {"key": "...", "account_id": "..."}
      }
    }
  },
  "miko": {
    "gemini": {"default": "personal", "resources": {"personal": "..."}}
  }
}
```

Real values belong only in the server-side deployment environment.

## Default/operator pool

Existing deployment variables remain canonical for the explicit operator/default pool:

- `MULTIMIND_GEMINI_KEY`
- `MULTIMIND_DEEPSEEK_KEY`
- `MULTIMIND_GROQ_KEY`
- `MULTIMIND_CLOUDFLARE_KEY`
- `MULTIMIND_CLOUDFLARE_ACCOUNT_ID`
- `MULTIMIND_OPENROUTER_KEY`
- `MULTIMIND_HUGGINGFACE_KEY`
- `MULTIMIND_REMOTE_URL`

Fallback policy:

- blank policy + no per-user JSON → preserve legacy/default pool;
- blank policy + nonblank per-user JSON → strict authenticated-user isolation;
- `true` → explicitly allow deployment/default fallback;
- `false` → explicitly require strict isolation even before per-user JSON exists.

This gives migration-safe atomic activation: code may be merged first without breaking the current deployment, and adding the per-user JSON later activates strict isolation without requiring another code change.

## Adversarial repair loop

The first implementation made authenticated Reflex fallback strict immediately after merge. That would have been a deployment regression because the currently connected Railway configuration still relies on deployment-level provider credentials. A code merge could therefore have disabled AI access before the per-user pool secret was entered.

That residual was repaired before acceptance. Strict isolation now activates when per-user pool configuration is present, while pre-configuration behavior remains backwards compatible.

Additional adversarial protections prove:

- Izzul and Miko can receive different credentials for the same provider;
- a missing user cannot inherit another user's resource pool;
- a missing user does not inherit the operator/default pool in strict mode;
- malformed nonblank JSON is strict/fail-closed;
- malformed provider resources are ignored/fail-closed;
- the reserved `default` namespace cannot override deployment/operator credentials;
- multiple same-provider resources select only the declared default and do not auto-rotate;
- Cloudflare key/account pairing is enforced;
- explicit true/false fallback policy is deterministic;
- generic/default compatibility remains intact for rollback/reference callers.

Known in-scope residuals after final adversarial review: **0**.

## Verification evidence

Final PR head:

`e20e649884718c35857824a068991089a7748e6c`

PR-head verification:

- Python Regression #281 — SUCCESS
- RJ5 Dual-Host Torture #50 — SUCCESS
- RJ6 Cutover Rollback Proof #60 — SUCCESS
- Final Gate Operator Readiness #111 — SUCCESS

PR #110 was squash-merged with expected-head guard against exactly:

`e20e649884718c35857824a068991089a7748e6c`

Implementation exact-main:

`441543faf629258650398726606fb87fb94a4f59`

Exact-main verification:

- Python Regression #286 — SUCCESS
- RJ5 Dual-Host Torture #55 — SUCCESS
- RJ6 Cutover Rollback Proof #65 — SUCCESS
- Final Gate Operator Readiness #116 — SUCCESS

## Scope protection

This workstream did not:

- deploy or modify Railway runtime variables;
- enter any real provider key into repository content;
- authorize automatic credential rotation to evade provider limits;
- redesign provider/model resolution;
- add a new persistence system;
- authorize production cutover.

## Status

`PER_USER_PROVIDER_RESOURCE_POOLS = FULL FEATURE IMPLEMENTATION / CLOSED`

`KNOWN_IN_SCOPE_RESIDUALS = 0`

`FULL_OPERATIONAL_PROVIDER_VERIFICATION = NO`

`RAILWAY_FINAL_INTEGRATION = HOLD`

`FINAL_RAILWAY_CANDIDATE = NOT BUILT BY THIS WORKSTREAM`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`

STOP before Railway final integration.
