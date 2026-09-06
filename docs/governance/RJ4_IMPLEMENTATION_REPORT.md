# RJ-4 — DURABLE PERSISTENCE + DEPLOYMENT — CLOSURE REPORT

Status: GOVERNOR ACCEPTED / PASS / CLOSED / INTEGRATED
Accepted: 2026-09-06
Production cutover authorized: NO

## BASE

Starting accepted baseline: RJ-3 closure `e9cc60b29852fc33b885cad5771decb0765eca28`.

## IMPLEMENTATION

RJ-4 added the smallest self-host/container deployment boundary that preserves existing application and SQLite ownership:

- single Reflex application container;
- `reflex run --env prod` with pinned repository `reflex==0.8.22`;
- named durable Docker volume mounted at `/app/data`;
- `restart: unless-stopped` and backend health check;
- server-side provider environment inputs;
- explicit browser/backend deploy URLs and restricted CORS origin configuration;
- neutral base image with no private-repository credential requirement;
- optional private Design-DNA build override using a BuildKit secret rather than token build args/env;
- `.dockerignore` excludes local data, databases, env files and secret paths;
- two-phase persistence probe for process/container recreation;
- dedicated container CI proving a fresh second container sees data seeded by the first through the same named volume.

RJ-4 also hardened `DatabaseManager.export_bytes()` to use SQLite's backup API into an isolated validated snapshot. Existing database API, schema, restore format and memory-hydration ordering remain unchanged.

## REPAIR HISTORY

The first verification attempt exposed an implementation-editing error: a partial-file rewrite of `database/manager.py` accidentally dropped existing methods/signatures. The failure was not accepted or merged. The file was reconciled against authoritative main, all existing methods/signatures restored, and only the bounded SQLite backup export change retained. A separate direct-script import-path issue in the persistence probe was also repaired. No test or guarantee was weakened.

## VERIFICATION

PR #94 final exact head: `e49e21e450aa22b97af490dc614ec80ee1e57b50`.

Final PR-head gates:
- Python Regression #158 / run `34025746660`: SUCCESS;
- full pytest regression: PASS;
- dependency sanity / `pip check`: PASS;
- RJ4 Container Durability #4 / run `34025746672`: SUCCESS;
- neutral production image build: PASS;
- neutral host import with private DNA absent: PASS;
- durable-volume seed in container A: PASS;
- fresh container B against the same named volume: PASS;
- cleanup: PASS.

PR #94 merged with expected-head guard:
- merge commit `33a710bf57e3ff94ccac199acbff1cf0bd420e2c`.

Exact merged-main closure gates:
- Python Regression #159 / run `34025824838`: SUCCESS;
- RJ4 Container Durability #5 / run `34025824832`: SUCCESS;
- fresh-container recreation against the same durable named volume: PASS.

## DIFF AUDIT

Final RJ-4 diff is bounded to 11 owned paths:
- `.dockerignore`;
- `.github/workflows/rj4-container-proof.yml`;
- `Dockerfile`;
- `compose.private-dna.yml`;
- `compose.yml`;
- `database/manager.py`;
- `docs/governance/RJ4_DEPLOYMENT_OPERATIONS.md`;
- this report;
- `rxconfig.py`;
- `scripts/rj4_persistence_probe.py`;
- `tests/test_rj4_durable_deployment.py`.

Preserved:
- SQLite authority and DB schema;
- per-user namespace/path semantics;
- provider routing/behavior;
- debate/core-memory semantics;
- `MultiMindApplication` backup/restore boundary;
- Reflex 0.8.22 pin;
- Streamlit rollback/reference host;
- optional private DNA boundary;
- no FastAPI/REST/RPC/microservice or second persistence owner.

## RESIDUALS

- actual internet-facing hostname/origin values remain deployment-environment facts and are not invented in source;
- runtime dual-host/device torture belongs to RJ-5;
- RJ-6 owns cutover/rollback rehearsal;
- Final Governor Migration Gate alone owns production cutover authorization.

## VERDICT

`PASS / CLOSED / INTEGRATED`.

RJ-5 Torture / Dual-Host Parity is the next authorized serial bundle.
