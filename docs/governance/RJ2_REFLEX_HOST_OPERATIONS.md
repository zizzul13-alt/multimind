# RJ-2 REFLEX PRODUCTION HOST — OPERATIONS NOTE

Status: RJ-2 implementation package. This document does not authorize production cutover or Design-DNA M0.

## Runtime

Pinned framework: `reflex==0.8.22`.

Development:

```bash
REFLEX_HOT_RELOAD_EXCLUDE_PATHS=data reflex run
```

The `data` hot-reload exclusion is development-only. It does not provide durability or production persistence.

## Deployment secret inputs

The Reflex edge converts environment variables into the generic RJ-1 configuration-source contract. Preferred names:

- `MULTIMIND_GEMINI_KEY`
- `MULTIMIND_DEEPSEEK_KEY`
- `MULTIMIND_GROQ_KEY`
- `MULTIMIND_CLOUDFLARE_KEY`
- `MULTIMIND_CLOUDFLARE_ACCOUNT_ID`
- `MULTIMIND_OPENROUTER_KEY`
- `MULTIMIND_HUGGINGFACE_KEY`
- `MULTIMIND_REMOTE_URL`

Common provider aliases are accepted where implemented in `multimind_reflex/bridge.py`.

Do not commit credentials.

## Architecture

```text
Reflex UI
  -> HostState
  -> build_host_application()
  -> build_application_for_user()
  -> MultiMindApplication
  -> existing core/providers/SQLite
```

There is no REST/FastAPI transport layer.

Long-running execution uses a supported Reflex background event. The event claims `busy` while holding the Reflex state lock before starting work, so concurrent duplicate triggers fail closed.

Uploads are consumed in a normal upload event. `rx.UploadFile` objects are converted to a small synchronous in-memory adapter before background execution, preserving the existing `FileHandler` contract and avoiding an unsupported background UploadFile lifetime.

## Scope boundary

RJ-2 includes only the production-host spine:

- identity
- application composition
- basic session create/list/select
- upload staging
- long-running execute
- busy state
- duplicate-run guard
- `ChatResult` rendering

RJ-3 owns full presentation parity, Theme Studio journey, advanced controls, responsive/browser parity and the complete frozen UI denominator.

RJ-4 owns durable deployment topology and restart/recreate persistence proof.
