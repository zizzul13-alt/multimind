# 🤖 MultiMind AI

Multi-agent AI debate system with session memory, provider fallback, file handling, and presentation-independent application semantics.

## Current production direction

MultiMind's accepted production presentation direction is **Reflex**, running in-process through the existing application boundary:

```text
Browser
→ Reflex presentation host
→ MultiMindApplication / shared composition boundary
→ existing orchestration / providers / files / memory / SQLite
```

SQLite remains authoritative. The production container persists `/app/data` through a durable Docker volume.

**Streamlit remains the reference/rollback host until an explicitly authorized production cutover is completed.** Do not remove it or migrate data merely because the presentation host changes.

## Features

- Multi-agent debate and provider fallback
- Prompt compression and token/cost estimates
- Multi-file uploads
- Session memory with Continue / Standalone behavior
- Per-user SQLite persistence
- Seven presentation archetypes and Theme Studio composition
- Optional private Design-DNA package with neutral safe fallback
- Backup / restore through the application boundary

## Local / neutral container run

The public repository can run without private Design-DNA credentials:

```bash
docker compose build
docker compose up -d
```

Local defaults expose Reflex frontend on port `3000` and backend on port `8000`.

For real production deployment, do **not** rely on localhost defaults. Production must supply the real frontend/backend origins, restricted CORS origins, durable volume selection, and server-side provider credentials.

## Private Design-DNA build

Private Design-DNA is optional and server-side. When enabled, use the BuildKit-secret flow documented in:

`docs/governance/RJ4_DEPLOYMENT_OPERATIONS.md`

Never commit the private-repository token or provider credentials. `.secrets/`, `.env`, and `.env.*` are excluded from Git; `.env.example` contains names only.

## Production / cutover status

The migration implementation and evidence chain through RJ-6 is complete and Governor-accepted. The Final Governor Migration Gate is ready, but **production cutover is not authorized by repository state alone**.

Before any real cutover, use:

- `docs/governance/REFLEX_MIGRATION_FINAL_GATE_REPORT.md`
- `docs/governance/RJ4_DEPLOYMENT_OPERATIONS.md`
- `docs/governance/FINAL_CUTOVER_RUNBOOK.md`
- `python scripts/final_gate_preflight.py`

A real cutover still requires actual deployment-environment facts and explicit Governor/user authorization.

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
- SQLite per-user persistence
- Existing provider abstraction / routing / fallback
- Docker Compose self-host deployment direction
