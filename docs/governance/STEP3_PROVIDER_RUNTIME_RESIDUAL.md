# Step 3 Provider Runtime Residual

Date: 2026-09-07

## Repository-side closure

Provider/API repository residual repair is CLOSED/PASS on main.

Accepted merge:

- PR #105 — `Repair provider deployment residuals and retired model paths (rebased)`
- merged main commit: `0ff4d6a48938b83de9ef3d4e2e49b3f824f4d84a`
- PR-head Python Regression #204: PASS
- PR-head Final Gate Operator Readiness #34: PASS
- exact-main Python Regression #205: PASS
- exact-main Final Gate Operator Readiness #35: PASS

The merged package:

- replaces retired/deprecated Groq, DeepSeek, and Cloudflare model paths;
- migrates Hugging Face away from the legacy `api-inference` endpoint to the current router endpoint;
- preserves bounded fallback and sanitized rate-limit detection, including legacy text-only 429 compatibility;
- aligns UnifiedAgent priority with the Gemini production proving path while preserving provider fallback independence;
- removes the stale Streamlit-specific OpenRouter `HTTP-Referer` coupling so the provider adapter is presentation-host neutral;
- adds regression locks for the repaired deployment contracts.

`REPOSITORY_PROVIDER_RESIDUALS = CLOSED/PASS`

## Real-runtime evidence still required

A prior real Railway runtime smoke reached the Groq API but failed with `NotFoundError`; the UI correctly surfaced `No usable provider response was returned.` That attempt proved outbound provider-path exercise but did not satisfy successful provider generation.

The repository repair now selects `openai/gpt-oss-20b` for Groq. Successful authenticated generation must still be proven against the real deployed candidate with a real server-side credential. Repository CI cannot substitute for that evidence.

Acceptance remains:

```text
REPOSITORY_PROVIDER_RESIDUALS = CLOSED/PASS
REAL_PROVIDER_RESPONSE = PENDING USER-HELD REAL SECRET/RUNTIME
RESPONSE_PERSISTED_TO_TURSO = PENDING
REDEPLOY_SURVIVAL = PENDING
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```

This document does not authorize production cutover.
