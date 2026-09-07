# Step 3 Provider Runtime Residual

Date: 2026-09-07

Real Railway runtime smoke reached the Groq API but failed with `NotFoundError`; the UI correctly surfaced `No usable provider response was returned.`

This proves the provider path and outbound attempt were exercised, but does **not** satisfy Step 3 provider success.

The prior smoke target `llama-3.1-8b-instant` is currently documented by Groq as an Enterprise production model. The bounded repair selects `openai/gpt-oss-20b`, which Groq currently documents as an active hosted model with public per-token pricing and OpenAI-compatible chat-completions examples.

Acceptance remains:

```text
REAL_PROVIDER_RESPONSE = PENDING
RESPONSE_PERSISTED_TO_TURSO = PENDING
REDEPLOY_SURVIVAL = PENDING
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```
