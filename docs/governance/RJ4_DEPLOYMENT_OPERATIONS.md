# RJ-4 — DURABLE SELF-HOST OPERATIONS

Status: implementation contract; production cutover is NOT authorized by this document.

## Topology

One application container only:

```text
browser
  -> Reflex frontend :3000
  -> Reflex backend  :8000
  -> MultiMindApplication
  -> existing providers / memory / SQLite
  -> /app/data (named durable Docker volume)
```

No FastAPI, REST glue, Redis requirement, PostgreSQL migration, sidecar DB, or second persistence owner is introduced.

## Data durability

The authoritative application data root inside the container remains `/app/data`, matching the repository's existing relative `data/` contract under `WORKDIR /app`.

`compose.yml` mounts the named volume `multimind-data` at `/app/data`. Container replacement must preserve that volume. Deleting/recreating the container is allowed; deleting the volume is destructive and is never part of normal deploy/rollback.

The RJ-4 CI proof seeds SQLite in one container and verifies the same state from a fresh second container using the same named volume.

## Public / neutral build

The base image requires no private repository credentials and MultiMind remains operational with neutral Design-DNA fallback:

```bash
docker compose build
docker compose up -d
```

## Private Design-DNA build

Private DNA is an optional server-side package. Do not place a GitHub token in source, `.env`, build args, image labels, or browser storage.

Place a least-privilege token in a local file outside source control (default path `.secrets/github_token`) and build using the private override:

```bash
DOCKER_BUILDKIT=1 docker compose -f compose.yml -f compose.private-dna.yml build
docker compose -f compose.yml -f compose.private-dna.yml up -d
```

The Dockerfile consumes the token as a BuildKit secret, clones the private repository into a temporary build path, removes `.git`, installs from that local path, removes the temporary source, and never declares the token as `ARG` or `ENV`.

## Runtime secrets

Provider credentials remain server-side environment inputs:

- `MULTIMIND_GEMINI_KEY`
- `MULTIMIND_DEEPSEEK_KEY`
- `MULTIMIND_GROQ_KEY`
- `MULTIMIND_CLOUDFLARE_KEY`
- `MULTIMIND_CLOUDFLARE_ACCOUNT_ID`
- `MULTIMIND_OPENROUTER_KEY`
- `MULTIMIND_HUGGINGFACE_KEY`
- `MULTIMIND_REMOTE_URL`

Do not commit values.

## Origin contract

Production must explicitly set:

- `MULTIMIND_DEPLOY_URL` to the real browser-visible frontend origin;
- `MULTIMIND_API_URL` to the browser-reachable Reflex backend URL;
- `MULTIMIND_CORS_ALLOWED_ORIGINS` to the real allowed frontend origin(s), comma-separated.

The repository default is localhost-only. Wildcard `*` is not the production default.

## Health / restart

The image exposes ports 3000 and 8000 and checks Reflex backend `/_health`. Compose uses `restart: unless-stopped`.

Normal deploy/restart must preserve the named data volume:

```bash
docker compose up -d --build
```

Never add `-v` to `docker compose down` during routine deploy/rollback because `-v` removes named volumes.

## Backup / restore

User-facing backup/export and restore continue through `MultiMindApplication`; no presentation host owns SQLite paths.

RJ-4 hardens `DatabaseManager.export_bytes()` to use SQLite's backup API into an isolated validated snapshot instead of reading a live SQLite file directly.

Before a risky operator action, obtain an application backup or a stopped-container volume backup. Restore continues to use the existing staged validation + atomic replacement path; no schema conversion is required.

## Rollback invariant

Application rollback is image/code rollback only. The same named `multimind-data` volume is remounted. No database conversion is part of Reflex↔Streamlit or version rollback.

Production cutover remains reserved for the Final Governor Migration Gate after RJ-5 and RJ-6 evidence.
