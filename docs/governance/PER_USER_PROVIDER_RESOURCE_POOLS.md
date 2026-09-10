# MULTIMIND — PER-USER PROVIDER RESOURCE POOLS

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-10
Baseline: `main@4b7ebcc2719422a06ef17de6edd5915eb927a2a9`

## Mission

Prevent deployment-level provider credentials from becoming an implicit shared quota/source of truth across authenticated users while preserving the existing composition boundary, provider adapters, dynamic model resolution, and low-maintenance deployment.

Accepted direction:

`AUTHENTICATED USER → USER-SCOPED PROVIDER RESOURCE POOL → EXPLICIT DEFAULT RESOURCE PER PROVIDER → PROVIDER ADAPTER → MODEL RESOLVER`

The existing deployment-level `MULTIMIND_*` provider variables remain useful as an operator/default proof pool. Existing deployments stay migration-compatible until a per-user pool is actually configured; once that pool is present, authenticated user composition becomes strict by default and does not silently inherit deployment credentials.

## Finite contract

1. Add a server-side per-user credential source that can represent one or more named credential resources for the same provider.
2. Keep secrets out of source, browser state, persisted chat/session data, and presentation truth.
3. Do not add a new database, network service, secret manager service, or transport layer.
4. Preserve existing deployment-level `MULTIMIND_*` variables as the operator/default pool for explicit use and backwards-compatible proof paths.
5. Before per-user pools are configured, preserve the currently deployed default-pool behavior so merging implementation cannot silently disable a running deployment.
6. Once `MULTIMIND_USER_PROVIDER_POOLS_JSON` is nonblank, Reflex authenticated composition resolves user-specific pools and fails closed to empty provider credentials when a user pool is absent, unless an explicit default-fallback policy is enabled.
7. No implicit fallback from Izzul's resources to Miko's resources or vice versa.
8. Multiple resources for one provider are allowed as named resources, but MultiMind must not automatically rotate credentials to evade quotas/rate limits. One resource is explicitly designated `default` for current provider construction.
9. Resource selection must be deterministic and attributable. Current provider adapters continue receiving only the selected credential value; credential values themselves are never exposed in provenance.
10. Invalid/malformed resource-pool configuration must fail boringly without leaking secret material. A nonblank malformed pool activates strict mode rather than falling back to operator credentials.
11. User IDs remain validated by the existing canonical identity boundary. The `default` user namespace is reserved for deployment/operator credentials and cannot be overridden through the per-user JSON.
12. Preserve Streamlit/reference compatibility and existing generic `Config.get_api_keys` behavior unless a caller opts into strict user isolation.
13. Railway final integration and production cutover remain out of scope.

## Server-side format

Canonical deployment variable:

`MULTIMIND_USER_PROVIDER_POOLS_JSON`

Shape:

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

This variable is a server-side secret. No real value belongs in repository Markdown or examples beyond redacted placeholders.

## Default/operator pool

Existing variables remain canonical for the explicit deployment-level pool:

- `MULTIMIND_GEMINI_KEY`
- `MULTIMIND_DEEPSEEK_KEY`
- `MULTIMIND_GROQ_KEY`
- `MULTIMIND_CLOUDFLARE_KEY`
- `MULTIMIND_CLOUDFLARE_ACCOUNT_ID`
- `MULTIMIND_OPENROUTER_KEY`
- `MULTIMIND_HUGGINGFACE_KEY`
- `MULTIMIND_REMOTE_URL`

Fallback policy is controlled by `MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS`:

- blank + no per-user JSON: legacy/default pool remains active for migration compatibility;
- blank + nonblank per-user JSON: strict authenticated-user isolation;
- `true`: explicitly allow deployment/default fallback;
- `false`: explicitly require strict isolation even before per-user JSON exists.

This makes per-user-pool activation atomic: adding the pool JSON switches authenticated users into strict mode without requiring a simultaneous code deployment, while the implementation can be merged safely before the operator has entered the new secret.

## Verification matrix

At minimum prove:

- two users with same provider get different credentials;
- missing user does not inherit another user's pool;
- missing user does not inherit deployment default under strict mode;
- pre-configuration deployment remains migration-compatible;
- adding nonblank per-user JSON activates strict mode by default;
- malformed nonblank JSON activates strict fail-closed behavior;
- explicit default-fallback policy overrides inferred migration state only when deliberately configured;
- multiple named same-provider resources resolve the declared default deterministically;
- malformed provider resource fails closed;
- Cloudflare paired key/account resource resolution;
- reserved `default` user namespace cannot replace the operator pool;
- no automatic quota/rate-limit key rotation;
- existing generic default fallback tests remain valid;
- Streamlit and Reflex composition remain presentation-independent;
- full Python regression + RJ5 + RJ6 + Final Gate.

## Adversarial finding already repaired

The first implementation made authenticated Reflex fallback strict immediately after merge. Because the currently connected deployment still uses deployment-level provider variables, that would have allowed a code merge to disable all provider access before `MULTIMIND_USER_PROVIDER_POOLS_JSON` had been entered. The implementation was repaired so strict isolation activates when the per-user pool is configured, while the existing deployment remains usable beforehand. This preserves both security intent and recoverable migration behavior.

## Exit

Inspect → implement → targeted/adversarial tests → repair until known in-scope residuals are zero → full regression/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure.

STOP before Railway final integration. Production cutover remains unauthorized.
