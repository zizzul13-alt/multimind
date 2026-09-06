# MULTIMIND — FINAL GOVERNOR MIGRATION GATE / PRODUCTION CUTOVER RUNBOOK

Status: OPERATOR PREPARATION / REVIEW PACKAGE
Production cutover authorized by this document: NO

## 1. PURPOSE

This runbook converts the accepted RJ-0 → RJ-6 migration evidence into a boring, recoverable production procedure.

It does not reopen platform selection, Core, Security, Hardening/Reliability, QA/Testing, UI/UX, Design-DNA research, private extraction, or the accepted RJ migration bundles.

It does not authorize production cutover. The final traffic/user switch requires an explicit Governor/user authorization after the real deployment environment is known and the candidate deployment passes the checks below.

## 2. IMMUTABLE MIGRATION LOCKS

The final deployment must preserve:

```text
Browser
→ Reflex presentation host
→ MultiMindApplication / stable composition boundary
→ existing orchestration / providers / files / memory / SQLite
```

and:

```text
PUBLIC MULTIMIND
→ small stable DNA bridge
→ optional PRIVATE Design-DNA package
```

with:

```text
private DNA unavailable / failing / incompatible
→ neutral safe presentation
→ MultiMind remains operational
```

Hard laws:

- SQLite remains authoritative.
- No presentation-driven DB conversion.
- No FastAPI / REST / RPC glue.
- No second persistence owner.
- Provider routing/fallback remains behind existing boundaries.
- Real secrets stay server-side.
- Streamlit remains a rollback/reference presentation until later explicit retirement governance.
- Reflex remains pinned to the accepted migration version unless a separate upgrade is authorized.
- Routine deploy/rollback must never delete the authoritative data volume.

## 3. FINAL GATE STATE MACHINE

Do not collapse these states:

```text
REPOSITORY_READY
  ↓ real environment supplied
ENVIRONMENT_READY
  ↓ candidate deployed without traffic
CANDIDATE_READY
  ↓ explicit Governor/user authorization
CUTOVER_AUTHORIZED
  ↓ traffic/user switch
CUTOVER_ACTIVE
  ↓ observation + rollback window passed
CUTOVER_ACCEPTED
```

Current repository evidence establishes `REPOSITORY_READY`.

It does not fabricate `ENVIRONMENT_READY` or `CUTOVER_AUTHORIZED`.

## 4. REQUIRED REAL DEPLOYMENT INPUTS

Every item below must have a concrete answer before cutover authorization.

| Input | Required value | Current repository knowledge |
| --- | --- | --- |
| Production host/server | actual machine/runtime | NOT SPECIFIED |
| Current Streamlit production/data location | actual host/path/service | NOT SPECIFIED |
| Durable Reflex data storage | actual Docker volume/storage backing | logical volume contract exists; physical location NOT SPECIFIED |
| Browser-visible Reflex origin | real URL | NOT SPECIFIED |
| Browser-reachable Reflex API URL | real URL | NOT SPECIFIED |
| CORS allowed origin(s) | exact frontend origin(s) | NOT SPECIFIED |
| Internet exposure | public vs private/LAN | NOT SPECIFIED |
| TLS termination | actual TLS/reverse-proxy arrangement when public | NOT SPECIFIED |
| Provider credential delivery | server-side environment/secret mechanism | contract exists; actual deployment values NOT SPECIFIED |
| At least one usable provider path | concrete provider or remote path | NOT SPECIFIED |
| Private Design-DNA in production | explicit ENABLED or DISABLED | NOT SPECIFIED; optional by contract |
| Private-DNA BuildKit credential | least-privilege token file if enabled | NOT SPECIFIED |
| Pre-cutover backup artifact | complete recoverable production checkpoint + verification | NOT YET CREATED |
| Cutover window | operator-selected date/time | NOT SPECIFIED |
| Rollback traffic target | actual Streamlit endpoint/start procedure | semantics proven; environment-specific target NOT SPECIFIED |
| Explicit cutover authorization | Governor/user decision | NOT GRANTED |

Unknown environment values are blockers to real cutover, not reasons to redesign the repository.

## 5. REPOSITORY / VERSION FREEZE

Before preparing a real server:

1. Record the exact accepted `main` SHA that the Final Governor Gate authorizes.
2. Do not deploy an unreviewed later HEAD merely because it is newer.
3. Do not upgrade Reflex, provider libraries, Python major/minor, Docker topology, or database schema inside the cutover operation.
4. If repository drift appears after authorization, reconcile the diff before deployment.
5. Keep the Streamlit rollback path available.

The cutover should be boring: deployment of already-proven code, not a feature-development session.

## 6. SECRET / CONFIGURATION PREPARATION

The public repository tracks `.env.example` only. Real `.env`, `.env.*`, and `.secrets/` are Git-ignored and excluded from the Docker build context.

Populate equivalent server-side environment values without committing them:

```text
MULTIMIND_FRONTEND_PORT
MULTIMIND_BACKEND_PORT
MULTIMIND_DEPLOY_URL
MULTIMIND_API_URL
MULTIMIND_CORS_ALLOWED_ORIGINS
MULTIMIND_DATA_VOLUME
MULTIMIND_GEMINI_KEY
MULTIMIND_DEEPSEEK_KEY
MULTIMIND_GROQ_KEY
MULTIMIND_CLOUDFLARE_KEY
MULTIMIND_CLOUDFLARE_ACCOUNT_ID
MULTIMIND_OPENROUTER_KEY
MULTIMIND_HUGGINGFACE_KEY
MULTIMIND_REMOTE_URL
```

Rules:

- do not put secrets in source, image labels, build arguments, or browser storage;
- do not paste real secret values into issue/PR/governance Markdown;
- configure at least one provider credential or remote-provider path before declaring the candidate configured for AI execution;
- actual provider usability is proven later with the low-cost provider smoke, not inferred from a non-empty variable;
- if Cloudflare is configured, its account ID must also be configured;
- production CORS must not contain `*`;
- browser-visible deploy origin must be included in allowed CORS origins;
- internet-facing production should use HTTPS for both browser and browser-reachable API origins.

`docker compose` can consume an untracked `.env` for Compose interpolation, but `scripts/final_gate_preflight.py` reads the process environment. Before running the preflight, ensure the same deployment values have actually been exported/injected into the preflight process by the chosen server-side secret/environment mechanism. Do not assume a file sitting on disk has been loaded merely because Compose can read it.

## 7. OPTIONAL PRIVATE DESIGN-DNA DECISION

Private Design-DNA must be an explicit binary operator decision for the cutover:

```text
PRIVATE_DNA_PRODUCTION = ENABLED
```

or:

```text
PRIVATE_DNA_PRODUCTION = DISABLED
```

Do not leave it implicit.

If DISABLED:

```bash
docker compose build
```

The neutral safe presentation must remain operational.

If ENABLED:

1. create a least-privilege GitHub credential able to read only the required private repository;
2. place it in the configured server-side secret file, default `.secrets/github_token`;
3. never commit that file;
4. use the accepted BuildKit secret overlay:

```bash
DOCKER_BUILDKIT=1 docker compose -f compose.yml -f compose.private-dna.yml build
```

A private-DNA installation failure must fail the private build rather than silently inserting source credentials elsewhere. Neutral public build remains the fallback recovery option.

## 8. FAIL-CLOSED PREFLIGHT

From the exact deployment checkout, with the real server environment loaded into the preflight process, run:

```bash
python scripts/final_gate_preflight.py --production --check-docker
```

For a public internet-facing deployment:

```bash
python scripts/final_gate_preflight.py --production --public --check-docker
```

If private DNA is enabled, add `--private-dna` to the appropriate command.

Use `--public` only when the deployment is public; it requires HTTPS.

A PASS means configuration contracts are internally coherent. It does not prove provider credentials are accepted by external services and it does not authorize cutover.

A FAIL is a hard stop. Fix the environment/configuration issue and rerun. Do not bypass or weaken the preflight to obtain a green result.

The preflight intentionally does not print secret values.

## 9. DATA / BACKUP PRECONDITION

No production cutover may begin without a recoverable checkpoint covering **all authoritative production user data**, not merely the currently logged-in user.

Because the current real Streamlit hosting/data location and actual production-user set are not yet recorded, the backup command cannot be truthfully hard-coded here. Select the procedure that matches the real current environment.

### Option A — application-owned per-user backup/export

`MultiMindApplication.export_database()` is user-scoped through the existing composition/persistence boundary. If this method is used for the cutover checkpoint:

1. enumerate the complete known production-user set through the real deployment/operator records;
2. export one validated SQLite snapshot for **every** production user;
3. name/store those snapshots so the user mapping is unambiguous without placing secrets in filenames;
4. verify every snapshot is readable/restore-valid using the accepted restore semantics in an isolated verification context;
5. record the expected number of users and the number of successful backup artifacts;
6. do not declare the production backup complete if even one authoritative user database is missing.

Required accounting:

```text
PRODUCTION_USER_COUNT = <actual count>
USER_BACKUP_COUNT = <must equal production user count>
ALL_USER_BACKUPS_RESTORE_VERIFIED = TRUE
```

### Option B — stopped-writer full storage snapshot

For a tiny deployment, a stopped-writer snapshot of the complete authoritative storage may be simpler and less error-prone than coordinating separate per-user exports.

If taking a filesystem/volume-level copy:

1. stop the presentation/application writer first;
2. snapshot/copy the **entire authoritative `data/` root or durable volume**;
3. include every per-user database and any other authoritative persisted files under that root;
4. preserve file ownership/permissions needed for restore;
5. do not copy live SQLite files while they are being mutated;
6. record where the snapshot is stored;
7. verify the snapshot can be restored/read before proceeding.

Choose the smallest boring method that truthfully covers the whole production data set. Do not mix methods unless the operator can prove what each one covers.

Required evidence before authorization:

```text
BACKUP_CREATED = TRUE
BACKUP_SCOPE = ALL_PRODUCTION_USER_DATA
BACKUP_LOCATION = <operator record, not secret>
BACKUP_RESTORE_VERIFIED = TRUE
BACKUP_TIMESTAMP = <actual timestamp>
```

The backup must remain available through the rollback window.

## 10. DURABLE STORAGE PRECONDITION

The accepted container contract mounts:

```text
/app/data
```

from the named Docker volume selected by:

```text
MULTIMIND_DATA_VOLUME
```

Before deployment, inspect the actual selected volume/storage with the deployment environment loaded. If using a shell variable directly, confirm it is set before invoking a command such as:

```bash
docker volume inspect "$MULTIMIND_DATA_VOLUME"
```

If the volume does not yet exist, allow Docker Compose to create it or create it deliberately under the chosen production storage policy.

Never use routine commands that destroy the volume.

Specifically, do not use:

```bash
docker compose down -v
```

for normal deploy or rollback.

`-v` is destructive because it removes named volumes.

## 11. BUILD THE EXACT CANDIDATE

Neutral build:

```bash
docker compose build
```

Private-DNA build when explicitly enabled:

```bash
DOCKER_BUILDKIT=1 docker compose -f compose.yml -f compose.private-dna.yml build
```

Build failure is a hard stop.

Do not repair a production build by ad-hoc package installation inside a running container. Repair the owning repository artifact, test it, and return through review.

## 12. CANDIDATE DEPLOYMENT BEFORE TRAFFIC SWITCH

Where the environment permits, start the candidate without changing the public traffic target yet:

Neutral:

```bash
docker compose up -d
```

Private DNA enabled:

```bash
docker compose -f compose.yml -f compose.private-dna.yml up -d
```

Inspect status:

```bash
docker compose ps
```

Inspect bounded logs without publishing secrets:

```bash
docker compose logs --tail=200 multimind
```

Do not paste full environment dumps into logs or tickets.

## 13. CANDIDATE HEALTH / USABILITY CHECK

Once the candidate is reachable from its intended origin, run the same preflight with `--health` added. For example, a public deployment uses:

```bash
python scripts/final_gate_preflight.py --production --public --health
```

This checks frontend and backend reachability after configuration validation.

Then perform a browser smoke test against the real candidate:

1. login with a valid test user;
2. confirm the pre-workspace Theme/Theme Studio stage is reachable;
3. Apply a composition explicitly;
4. enter the MultiMind workspace;
5. confirm Theme Studio remains reachable;
6. create/select a session;
7. send one real low-cost prompt through the intended provider path;
8. confirm success/failure messaging is truthful;
9. switch A → B → A between two sessions and confirm continuity;
10. perform one representative file-upload flow if production users rely on uploads;
11. confirm history persists after a normal container restart;
12. perform/verify one application backup/export action for the smoke-test user without confusing it with the complete pre-cutover production backup required in section 9;
13. verify a neutral presentation remains available if private DNA is intentionally disabled or unavailable.

Do not turn the final smoke test into feature discovery. Any unrelated cosmetic issue is recorded separately unless it blocks required production use.

## 14. AUTHORIZATION STOP POINT

After candidate deployment and smoke verification, STOP.

Record:

```text
EXACT_DEPLOY_SHA = ...
ENVIRONMENT_PREFLIGHT = PASS
CANDIDATE_HEALTH = PASS
PROVIDER_SMOKE = PASS
SESSION_CONTINUITY_SMOKE = PASS
PERSISTENCE_RESTART_SMOKE = PASS
BACKUP_CREATED = TRUE
BACKUP_SCOPE = ALL_PRODUCTION_USER_DATA
BACKUP_RESTORE_VERIFIED = TRUE
ROLLBACK_TARGET_READY = TRUE
```

Only then may the Governor/user explicitly authorize production cutover.

Without explicit authorization:

```text
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```

and traffic/users remain on the existing production truth.

## 15. CUTOVER EXECUTION — ONLY AFTER EXPLICIT AUTHORIZATION

Once explicitly authorized:

1. announce/freeze the chosen cutover window if other users are active;
2. stop new writes on the old presentation if required by the environment;
3. take the final pre-switch data checkpoint if the previous backup is no longer current enough;
4. ensure Reflex mounts the exact authoritative data set/volume;
5. route the intended browser traffic to the accepted Reflex frontend/API origins;
6. confirm backend `/_health`;
7. repeat the minimal login/session/provider smoke;
8. verify new writes appear in the same authoritative SQLite data;
9. keep Streamlit rollback capability intact.

Do not delete old data, old images, rollback code, or Streamlit during the cutover itself.

## 16. IMMEDIATE ROLLBACK TRIGGERS

Rollback rather than debug live if any of these occur after traffic switch:

- Reflex frontend/backend cannot remain healthy;
- login or user isolation is broken;
- existing sessions/history are missing;
- normal writes do not persist;
- database/path namespace differs from the accepted production data;
- provider execution is broadly unusable despite valid credentials;
- repeated duplicate execution/busy-state corruption appears;
- restore/backup behavior indicates data risk;
- a required Theme Studio/workspace path is unreachable for normal use;
- deployment requires an unreviewed DB conversion or architecture change to continue.

A rollback trigger is not a reason to improvise schema migration in production.

## 17. ROLLBACK PROCEDURE

The invariant is:

```text
same application truth
+ same SQLite namespace/schema/data
+ different presentation host
```

Rollback actions:

1. stop or remove the failing Reflex candidate container as appropriate;
2. preserve the authoritative data volume;
3. do not run `docker compose down -v`;
4. restore traffic/start the proven Streamlit rollback presentation against the same authoritative data;
5. verify login;
6. verify existing user/session/history data;
7. perform one normal low-cost operation if safe;
8. verify the write persists;
9. only restore the pre-cutover backup if evidence shows the authoritative current data itself was damaged;
10. record the failure and return the defect to its owning layer.

RJ-6 already proved the semantic lifecycle:

```text
Streamlit
→ same data
→ Reflex
→ restart/recreate
→ same data
→ simulated Reflex failure
→ Streamlit
→ same data
```

The Final Gate supplies the real deployment endpoint and operator procedure; it must not weaken that invariant.

## 18. POST-CUTOVER OBSERVATION

After an authorized successful switch:

- watch application health and logs;
- verify data remains after at least one normal restart/recreate event appropriate to the environment;
- verify backup/export remains usable;
- keep the pre-cutover backup through the agreed rollback window;
- keep Streamlit rollback capability until a separate retirement decision;
- do not bundle unrelated upgrades into post-cutover stabilization.

## 19. STREAMLIT RETIREMENT IS SEPARATE

A successful Reflex cutover does not automatically authorize deleting Streamlit.

Retirement requires explicit later governance after:

- Reflex production has remained stable through the chosen observation window;
- data durability is demonstrated in the real environment;
- rollback risk is acceptably low;
- no unresolved production issue requires the reference host.

Until then Streamlit remains a rollback/reference asset, not production truth.

## 20. FINAL GATE PASS CONDITIONS

The Final Governor Migration Gate may authorize cutover only when all are true:

```text
RJ0_THROUGH_RJ6_ACCEPTED = TRUE
EXACT_DEPLOY_SHA_RECONCILED = TRUE
REAL_PRODUCTION_HOST_DEFINED = TRUE
REAL_DATA_STORAGE_DEFINED = TRUE
REAL_DEPLOY_ORIGIN_DEFINED = TRUE
REAL_API_ORIGIN_DEFINED = TRUE
RESTRICTED_CORS_DEFINED = TRUE
TLS_DECISION_DEFINED = TRUE
AT_LEAST_ONE_PROVIDER_PATH_CONFIGURED = TRUE
PROVIDER_SMOKE = PASS
PRIVATE_DNA_PRODUCTION_DECISION_DEFINED = TRUE
PRE_CUTOVER_BACKUP_CREATED = TRUE
PRE_CUTOVER_BACKUP_SCOPE = ALL_PRODUCTION_USER_DATA
PRE_CUTOVER_RESTORE_VERIFIED = TRUE
CANDIDATE_PREFLIGHT = PASS
CANDIDATE_HEALTH = PASS
CANDIDATE_BROWSER_SMOKE = PASS
ROLLBACK_TARGET_READY = TRUE
CUTOVER_WINDOW_DEFINED = TRUE
EXPLICIT_GOVERNOR_USER_AUTHORIZATION = TRUE
```

If any item is false or unknown, cutover remains unauthorized.

## 21. CURRENT VERDICT

Repository migration engineering through RJ-6 is accepted.

The operator package can prepare and validate the real environment, but the repository currently does not contain the real server/hostname/storage/secret/cutover-window facts.

Therefore:

```text
FINAL_GATE_REPOSITORY_READINESS = PASS
REAL_ENVIRONMENT_READINESS = PENDING_INPUT
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```
