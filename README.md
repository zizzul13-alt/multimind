# 🤖 MultiMind AI

Multi-agent AI debate system with session memory, provider fallback, file handling, and presentation-independent application semantics.

## Current production direction

MultiMind's accepted production presentation direction is **Reflex**, running in-process through the existing application boundary:

```text
Browser
→ Reflex presentation host
→ MultiMindApplication / shared composition boundary
→ existing orchestration / providers / files / memory / persistence
```

The persistence boundary supports two deliberately bounded modes:

- **Turso remote persistence** when both `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` are configured. This is the current real Railway deployment-candidate direction.
- **SQLite per-user persistence** when both Turso variables are absent. SQLite remains the local/rollback path and the portable backup format.

Partial Turso configuration fails closed. Presentation code does not own persistence selection and no database network/API layer has been added.

**Streamlit remains the reference/rollback host until an explicitly authorized production cutover is completed.** Do not remove it merely because the presentation host changes.

## Features

- Multi-agent debate and provider fallback
- Prompt compression and token/cost estimates
- Multi-file uploads processed transiently in-memory for the active request
- Session memory with Continue / Standalone behavior
- User-scoped Turso remote persistence with SQLite fallback/rollback
- Seven presentation archetypes and Theme Studio composition
- Optional private Design-DNA package with neutral safe fallback
- Portable SQLite backup / restore through the application boundary

## Local / neutral container run

The public repository can run without private Design-DNA credentials:

```bash
docker compose build
docker compose up -d
```

Local defaults expose Reflex frontend on port `3000` and backend on port `8000`.

For real production deployment, do **not** rely on localhost defaults. Production must supply the real frontend/backend origins, restricted CORS origins, server-side persistence credentials or an accepted durable local-storage arrangement, and server-side provider credentials.

## Private Design-DNA build

Private Design-DNA is optional and server-side. When enabled, use the BuildKit-secret flow documented in:

`docs/governance/RJ4_DEPLOYMENT_OPERATIONS.md`

Never commit the private-repository token or provider credentials. `.secrets/`, `.env`, and `.env.*` are excluded from Git; `.env.example` contains names only.

## Production / cutover status

The migration implementation and evidence chain through RJ-6 is complete and Governor-accepted. A real Railway + Turso deployment candidate now exists, but **production cutover is not authorized by repository state alone**.

Current deployment-candidate evidence and remaining external proofs are tracked in:

- `docs/governance/REAL_DEPLOYMENT_CANDIDATE_STATUS.md`
- `docs/governance/REFLEX_MIGRATION_FINAL_GATE_REPORT.md`
- `docs/governance/RJ4_DEPLOYMENT_OPERATIONS.md`
- `docs/governance/FINAL_CUTOVER_RUNBOOK.md`
- `python scripts/final_gate_preflight.py`

A real cutover still requires the remaining runtime evidence plus explicit Governor/user authorization.

## Provider credentials

The Reflex host accepts server-side deployment environment inputs for supported providers, including Cloudflare, Groq, OpenRouter, Hugging Face, DeepSeek, Gemini, and an optional remote provider URL. At least one usable provider path is required for actual AI execution.

Do not put credentials in source control or browser-side storage.

## Usage

1. Login as a user.
2. Select/apply presentation composition as desired.
3. Create or select a session.
4. Configure prompt/session/debate options.
5. Run MultiMind.

## Tech stack

- Python
- Reflex production presentation host
- Streamlit rollback/reference presentation
- Turso/libSQL remote persistence for the real deployment candidate
- SQLite local/rollback persistence and portable backup format
- Existing provider abstraction / routing / fallback
- Container deployment with external-host compatibility
