# MULTIMIND — PER-USER PROVIDER RESOURCE POOLS

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-10
Baseline: `main@4b7ebcc2719422a06ef17de6edd5915eb927a2a9`

## Mission

Prevent deployment-level provider credentials from becoming an implicit shared quota/source of truth across authenticated users while preserving the existing composition boundary, provider adapters, dynamic model resolution, and low-maintenance deployment.

Accepted direction:

`AUTHENTICATED USER → USER-SCOPED PROVIDER RESOURCE POOL → EXPLICIT DEFAULT RESOURCE PER PROVIDER → PROVIDER ADAPTER → MODEL RESOLVER`

The existing deployment-level `MULTIMIND_*` provider variables remain useful as an operator/default proof pool, but authenticated user composition must not silently fall back across users.

## Finite contract

1. Add a server-side per-user credential source that can represent one or more named credential resources for the same provider.
2. Keep secrets out of source, browser state, persisted chat/session data, and presentation truth.
3. Do not add a new database, network service, secret manager service, or transport layer.
4. Preserve existing deployment-level `MULTIMIND_*` variables as the operator/default pool for explicit use and backwards-compatible proof paths.
5. Reflex authenticated composition must resolve a user-specific pool first and fail closed to empty provider credentials when no pool exists, unless an explicit operator/default-fallback policy is enabled.
6. No implicit fallback from Izzul's resources to Miko's resources or vice versa.
7. Multiple resources for one provider are allowed as named resources, but MultiMind must not automatically rotate credentials to evade quotas/rate limits. One resource is explicitly designated `default` for current provider construction.
8. Resource selection must be deterministic and attributable. Current provider adapters continue receiving only the selected credential value; credential values themselves are never exposed in provenance.
9. Invalid/malformed resource-pool configuration must fail boringly without leaking secret material.
10. User IDs remain validated by the existing canonical identity boundary.
11. Preserve Streamlit/reference compatibility and existing generic `Config.get_api_keys` behavior unless a caller opts into strict user isolation.
12. Railway final integration and production cutover remain out of scope.

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

Authenticated Reflex user composition does not consume this pool unless `MULTIMIND_ALLOW_DEFAULT_CREDENTIALS_FOR_USERS=true` is explicitly set.

## Verification matrix

At minimum prove:

- two users with same provider get different credentials;
- missing user does not inherit another user's pool;
- missing user does not inherit deployment default under strict mode;
- explicit default-fallback policy restores deployment default only when enabled;
- multiple named same-provider resources resolve the declared default deterministically;
- malformed JSON fails to empty user pool without exposing data;
- malformed provider resource fails closed;
- Cloudflare paired key/account resource resolution;
- no automatic quota/rate-limit key rotation;
- existing generic default fallback tests remain valid;
- Streamlit and Reflex composition remain presentation-independent;
- full Python regression + RJ5 + RJ6 + Final Gate.

## Exit

Inspect → implement → targeted/adversarial tests → repair until known in-scope residuals are zero → full regression/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure.

STOP before Railway final integration. Production cutover remains unauthorized.
