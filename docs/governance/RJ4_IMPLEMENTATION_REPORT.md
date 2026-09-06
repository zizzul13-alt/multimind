# RJ-4 — DURABLE PERSISTENCE + DEPLOYMENT — IMPLEMENTATION REPORT

Status: IMPLEMENTED ON REVIEW BRANCH / PENDING CI / NOT MERGED
Production cutover authorized: NO

## BASE

Starting accepted baseline: RJ-3 closure `e9cc60b29852fc33b885cad5771decb0765eca28`.

## IMPLEMENTATION

RJ-4 adds the smallest self-host/container deployment boundary that preserves existing application and SQLite ownership:

- single Reflex application container;
- `reflex run --env prod` with pinned repository `reflex==0.8.22`;
- named durable Docker volume mounted at `/app/data`;
- `restart: unless-stopped` and backend health check;
- server-side provider environment inputs;
- explicit browser/backend deploy URLs and restricted CORS origin configuration;
- neutral base image with no private-repository credential requirement;
- optional private Design-DNA build override using a BuildKit secret rather than a token build arg/env;
- `.dockerignore` excludes local data, databases, env files and secret paths;
- two-phase persistence probe for process/container recreation;
- dedicated container CI building the neutral image and proving a fresh second container sees data seeded by the first through the same named volume.

RJ-4 also hardens `DatabaseManager.export_bytes()` to use SQLite's transactional backup API into an isolated validated snapshot. Schema and restore format are unchanged.

## PRESERVATION

- SQLite remains authoritative;
- user DB namespace/path model remains unchanged;
- DB schema remains unchanged;
- provider/debate/memory semantics remain unchanged;
- `MultiMindApplication` remains backup/restore presentation boundary;
- no database/service migration;
- no FastAPI/REST/RPC/microservice;
- Streamlit remains rollback/reference presentation;
- private DNA remains optional and server-side.

## REQUIRED VERIFICATION

Before closure:

- full Python regression PASS;
- `pip check` clean;
- RJ-4 targeted tests PASS;
- neutral Docker image builds;
- neutral container imports Reflex host with private DNA absent;
- named-volume seed in container A PASS;
- fresh container B against the same volume verifies persisted state PASS;
- CORS default is not wildcard;
- diff audit finds no unowned architecture changes;
- expected-head guarded merge;
- exact-main Python + container closure CI PASS.

## RESIDUALS

- actual internet-facing hostname/origin values are deployment-environment facts and are not invented in source;
- real browser/device and dual-host torture belongs to RJ-5;
- RJ-6 owns cutover/rollback rehearsal;
- Final Governor Migration Gate still owns production cutover authorization.

## VERDICT

PENDING CI / REVIEW.
