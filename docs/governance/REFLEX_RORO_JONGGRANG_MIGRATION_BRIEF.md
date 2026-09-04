# MULTIMIND REFLEX — RORO JONGGRANG PRODUCTION MIGRATION BRIEF v1

ROLE: Migration Implementation Engineer  
REPORTS TO: MultiMind Governor  
MODE: RORO JONGGRANG / SERIAL-FIRST  
STATUS: MASTER IMPLEMENTATION BRIEF — ACC KEEP MASTER  
PRODUCTION MIGRATION: NOT AUTHORIZED

## 0. Mission

Migrate MultiMind's production presentation from Streamlit toward Reflex while preserving the existing application/core/provider/persistence contracts and proving deployment, persistence, parity, and rollback before any production cutover is authorized.

Target conceptual path:

`Existing MultiMind / Streamlit → preserve application/core/provider/SQLite contracts → Reflex production presentation → deployment + persistence + rollback proof → FINAL GOVERNOR MIGRATION GATE`

This is one cumulative migration campaign executed as serial, independently reviewable bundles. Roro Jonggrang means speed through inherited evidence and elimination of repeated research. It does not mean skipping verification or performing one giant rewrite.

## 1. Authoritative baseline / source priority

Repository: `zizzul13-alt/multimind`

Historical production implementation baseline: `main@6a040a7f53b77e54d0b4f695e2eefd67b3fa1046`.

The current main HEAD may be ahead because Governor governance Markdown has been persisted after that implementation baseline. RJ-0 must reconcile the actual current HEAD before implementation and distinguish governance/documentation drift from implementation/runtime drift.

Source priority:
1. current repository/files
2. merged implementation evidence
3. current artifacts
4. Governor Master ledger
5. older chat assumptions

Latest explicitly accepted Governor decision supersedes conflicting older decisions.

## 2. Closed evidence — do not reopen

Do not repeat without specific new counter-evidence:
- Reflex platform battle / selection
- pseudo-MultiMind framework stress test
- Reflex basic viability
- Reflex Production Integration Proof
- direct in-process integration proof
- A → B → A session proof
- busy / duplicate-run feasibility
- upload feasibility
- browser/mobile feasibility
- IP-27
- IP-28
- closed Core gate
- closed Security gate
- closed Hardening/Reliability gate
- closed QA/Testing gate
- closed UI/UX gate

Reflex Production Integration Proof remains `CLOSED / CONDITIONAL_PASS`, hard integration blockers = 0.

The implementation question is no longer whether Reflex is better than alternatives. It is whether the accepted Reflex architecture can replace the production Streamlit presentation without violating MultiMind contracts.

## 3. Global hard laws

- NO CORE REWRITE.
- NO PROVIDER REWRITE merely for migration.
- NO DB SCHEMA MIGRATION merely for Reflex.
- NO FASTAPI / REST / HTTP GLUE merely to connect Reflex.
- NO DUPLICATED ORCHESTRATION.
- NO DUPLICATED PERSISTENCE OWNERSHIP.
- NO REFLEX TYPES INSIDE GENERIC CORE/APPLICATION CONTRACTS.
- NO PRESENTATION ACCESS TO `MultiMindApplication._database()`.
- DO NOT turn `DatabaseManager` into a presentation API.
- NO SILENT REFLEX VERSION UPGRADE.
- NO SILENT SCOPE EXPANSION.
- NO CUSTOM JS unless concrete implementation evidence demonstrates a real requirement and Governor reviews the deviation.
- STREAMLIT MUST remain viable as rollback/baseline until the Final Governor Migration Gate.
- PRODUCTION CUTOVER IS FORBIDDEN by this brief.

## 4. Framework contract

Migration baseline: `Reflex == 0.8.22`.

This is the version proven by the closed Integration Proof. Do not silently migrate to Reflex 0.9+. A framework upgrade is a separate future chapter unless concrete evidence proves 0.8.22 unsuitable for this migration.

Target interaction remains:

`Reflex → direct in-process Python → shared composition/application boundary → MultiMindApplication → existing core/providers → existing SQLite persistence`

## 5. Locked production user journey

Theme Studio is a first-class production surface.

Canonical intended journey:

`LOGIN → SELECT THEME + THEME STUDIO → APPLY → MULTIMIND + THEME STUDIO`

Required migration surfaces include:
- theme selection after login
- Theme Studio access before entering MultiMind
- apply-theme behavior
- theme → MultiMind handoff
- selected/applied theme behavior
- Theme Studio access from the MultiMind experience

Do not confuse production Theme Studio with Design-DNA research work.

If part of this intended journey is not yet implemented in the current Streamlit baseline, classify it as an explicit MIGRATION REQUIREMENT/GAP, not as imaginary existing parity.

## 6. Canonical migration chain

`RJ-0 RECONCILE / FREEZE / PARITY CENSUS`
→ `RJ-1 PORTABILITY + APPLICATION BOUNDARY`
→ `RJ-2 REFLEX PRODUCTION HOST`
→ `RJ-3 FUNCTIONAL PRESENTATION PARITY`
→ `RJ-4 DURABLE PERSISTENCE + DEPLOYMENT`
→ `RJ-5 TORTURE / DUAL-HOST PARITY`
→ `RJ-6 CUTOVER + ROLLBACK PROOF`
→ `FINAL GOVERNOR MIGRATION GATE`

## 7. Serial execution law

Only one implementation bundle is active at a time. RJ-(N+1) must not be implemented in parallel with an unaccepted RJ-N.

Each bundle uses:

`inspect → implement → targeted tests → adversarial/self-review → repair → full regression → diff review → report → STOP`

Governor acceptance precedes progression. RJ-N+1 begins from the latest accepted migration baseline.

A downstream bundle must not silently compensate for an upstream defect. If RJ-N+1 exposes a defect owned by RJ-N: STOP → return defect to RJ-N → repair → rerun RJ-N verification → Governor review → continue.

## 8. Change / PR discipline

Prefer independently reviewable change packages. When repository changes require integration, use a separately reviewable PR/change package, identify the exact starting commit, and keep changes attributable to the owning RJ bundle.

Do not accumulate RJ-1 → RJ-6 into one mega-PR. Do not use one long branch as the canonical migration model.

A meaningless PR is not required when a bundle genuinely changes no repository content. RJ-0 may be evidence-only. Proof-heavy later bundles may likewise produce deployment/evidence artifacts rather than feature code where appropriate.

Canonical unit: `REVIEWABLE CHANGE / EVIDENCE PACKAGE`.

## 9. Discovery / scope classification

Every implementation discovery must be classified:
- A. REQUIRED FOR REFLEX PARITY → repair within owning RJ bundle.
- B. EXISTING BUG UNRELATED TO MIGRATION → record/defer unless it invalidates migration evidence.
- C. NICE REFACTOR → reject/defer.
- D. NEW EVIDENCE INVALIDATING CLOSED ASSUMPTION → STOP + GOVERNOR REVIEW.

Discovery does not automatically authorize scope expansion.

## 10. RJ-0 — Reconcile / Freeze / Parity Census

Mission: establish the exact execution-start repository state and freeze the functional denominator for migration.

Do:
1. Inspect actual current main HEAD.
2. Record exact commit.
3. Compare it against Governor Master and accepted architecture.
4. Distinguish docs/governance drift from implementation drift.
5. Inspect current production-facing presentation capabilities.
6. Produce a production capability census.
7. Freeze the RJ-3 parity denominator.
8. Record intended locked requirements that are not yet implemented as migration gaps.

Minimum census — product journey:
- login
- theme selection
- Theme Studio
- apply
- enter MultiMind
- Theme Studio access from MultiMind

Minimum census — MultiMind:
- identity/login/logout
- create session
- list sessions
- select session
- session history
- chat execution
- continue/standalone context
- session mode
- compressor
- active agents
- debate rounds
- selected skill
- uploads
- busy state
- duplicate-run protection
- warnings/errors
- final answer
- debate rendering
- tokens/cost where exposed
- backup
- restore
- browser/mobile/tablet usability

Output:
- CURRENT HEAD
- MASTER COMPATIBILITY
- PRODUCTION-FACING CAPABILITY CENSUS
- LOCKED MIGRATION REQUIREMENT GAPS
- RJ-3 PARITY DENOMINATOR
- DRIFT = YES / NO

STOP immediately if implementation drift materially invalidates a locked architecture assumption.

## 11. RJ-1 — Portability + Application Boundary

Mission: remove presentation-specific blockers and persistence leakage without rewriting the application/core architecture.

### RJ-1A Config

Preserve:
- `validate_user_id`
- `resolve_supplied_identity`
- DB path containment
- current DB namespace

Extract/genericize configuration source.

Required semantics:
`Presentation/Deployment → Configuration Source → per-user → default resolution → agent construction`.

Streamlit may use a Streamlit secrets adapter. Reflex/container must support environment/deployment secrets without importing Streamlit. Tests must support injectable mapping/source. Do not rewrite individual providers merely to solve configuration portability.

### RJ-1B Composition

Create/reuse one presentation-independent composition path such as `build_application_for_user(...)` that resolves validated identity, configuration, agents, database and runtime into `MultiMindApplication`.

Streamlit and Reflex consume the same generic composition path. Do not duplicate provider/database setup in each frontend.

### RJ-1C Application read boundary

Application-level presentation capabilities must include:
- `create_session()`
- `list_sessions()`
- `select_session()`
- `get_session_chats()` or equivalent generic history seam
- `execute_chat()`

Exact names may differ when justified by repository evidence. Presentation must not use `_database()` or direct `DatabaseManager` session/history reads.

### RJ-1D Backup / restore

Presentation must not open/read the SQLite path directly merely to produce a backup. Provide a narrow generic export/backup operation such as `export_database()` or equivalent application-level contract. Preserve the existing safe restore contract.

### RJ-1E Compatibility

RJ-1 must preserve:
- Streamlit runnable
- existing DB paths
- existing DB schema
- user isolation
- identity behavior
- provider configuration semantics
- persistence semantics
- existing orchestration behavior

Attack tests should include invalid user ID, traversal attempts, user A/B isolation, missing per-user secrets, default secret fallback, empty secrets, session/history isolation, backup isolation, valid restore and invalid restore.

Exit: targeted tests PASS; full regression PASS; Streamlit remains operational; no unauthorized architectural expansion; REPORT; STOP.

## 12. RJ-2 — Reflex Production Host

Mission: create the real Reflex production host spine using the generic boundaries established in RJ-1.

Add/configure Reflex 0.8.22. The Reflex host must consume the shared composition/application path.

Minimum functional spine:
`identity → application composition → session runtime → execute → busy → ChatResult → render`.

Preserve accepted Integration Proof behavior:
- persistent Run control
- state-derived busy label/state
- disabled while running
- duplicate-run protection
- normal long-running chat execution through supported background task
- upload handling through the supported upload/FileHandler path
- no unsupported background UploadFile contract

Development only: `REFLEX_HOT_RELOAD_EXCLUDE_PATHS=data`. This solves development watcher invalidation; it is not production persistence.

No REST glue. No custom JS absent evidence + Governor review. RJ-2 must execute the real `MultiMindApplication` path, not mock the core.

Exit: real execution PASS; busy PASS; duplicate guard PASS; basic session operation PASS; upload path PASS; targeted tests PASS; full regression PASS; REPORT; STOP.

## 13. RJ-3 — Functional Presentation Parity

Mission: complete the production user-facing Reflex experience against the RJ-0 denominator. Behavioral parity matters more than pixel-copying Streamlit.

Required denominator includes the locked product journey plus current production capabilities established by RJ-0.

Expected functional surfaces include:
- login/logout
- theme selection
- Theme Studio
- apply theme
- theme → MultiMind handoff
- Theme Studio access from MultiMind
- create/list/select sessions
- session history
- prompt execution
- continue/standalone
- session mode
- compressor
- active agents
- debate rounds
- selected skill
- uploads
- busy state
- duplicate-run protection
- warnings
- errors
- final answer
- debate data/rendering
- tokens/cost where applicable
- backup
- restore
- browser usability
- phone usability
- tablet usability

Presentation must use application/composition seams established by earlier bundles. Do not reintroduce direct persistence access merely because Reflex UI needs data.

Exit: RJ-0 parity denominator satisfied or every unresolved item explicitly classified as blocker/residual; targeted tests PASS; full regression PASS; browser/mobile/tablet evidence PASS; REPORT; STOP.

## 14. RJ-4 — Durable Persistence + Deployment

Mission: prove a production-capable runtime around the Reflex application while preserving authoritative per-user SQLite.

Leading architecture:
`Internet → TLS/reverse proxy → Reflex production runtime → shared composition → MultiMindApplication → providers → durable SQLite volume`.

Self-host/container is the leading deployment model. No hosting vendor is locked by this brief.

Production requirements:
- writable durable storage
- restart-safe SQLite
- runtime/container recreation-safe SQLite
- environment/deployment secret injection
- correct Reflex 0.8.22 production frontend/backend topology
- WebSocket/reverse-proxy behavior as required
- `api_url`/`backend_path` configuration where applicable
- TLS
- restricted production CORS to actual frontend origin

Reflex Cloud local `include_db` must not be used as the authoritative current MultiMind SQLite database because its persistence contract does not satisfy this architecture.

Persistence torture:
1. create user A data
2. create user B data
3. stop runtime
4. restart runtime
5. verify A/B data
6. recreate runtime/container
7. verify A/B data
8. export backup
9. restore
10. verify integrity
11. verify user isolation

Any authoritative-data loss = FAIL.

Exit: persistence torture PASS; secret injection PASS; runtime topology PASS; CORS/origin configuration PASS; full regression PASS; REPORT; STOP.

## 15. RJ-5 — Torture / Dual-Host Parity

Mission: determine whether the actual Reflex implementation can replace the Streamlit presentation using the same MultiMind contracts. This is not another platform battle.

Compare `STREAMLIT BASELINE` vs `REFLEX CANDIDATE` using the same application/core/provider/persistence semantics.

Torture matrix should include:
- login/identity behavior
- locked theme/Theme Studio journey
- session creation
- repeated A → B → A switching
- history retrieval
- repeated runs
- duplicate click attacks
- slow provider
- provider failure
- upload success
- upload failure
- warnings/errors
- result/debate rendering
- backup
- valid restore
- invalid restore
- restore runtime invalidation
- user A/B isolation
- runtime restart
- browser
- phone
- tablet

Do not reopen Reflex vs SvelteKit, framework selection, or pseudo-MultiMind battle.

Question: can this Reflex implementation safely replace this Streamlit production presentation?

Exit: no unresolved hard parity blocker; full regression PASS; torture evidence documented; REPORT; STOP.

## 16. RJ-6 — Cutover + Rollback Proof

Mission: prove cutover readiness and rollback safety. THIS IS A DRILL. IT DOES NOT AUTHORIZE ACTUAL PRODUCTION CUTOVER.

Proof should cover:
- fresh deployment/startup
- production secret availability
- frontend/backend connectivity
- production CORS/origin
- existing user DB availability
- normal user operation
- restart
- runtime/container recreation
- persistence after restart/recreation
- backup
- restore
- user isolation
- startup/health behavior

Rollback drill:
`Streamlit baseline → preserve same data → Reflex candidate → exercise existing DB → restart/recreate → verify data → simulate Reflex failure → restore Streamlit presentation → same DB → same users/sessions/history`.

Rollback target: NO DB CONVERSION; NO CORE ROLLBACK; NO PROVIDER MIGRATION.

Exit: cutover proof PASS; rollback drill PASS; residuals documented; REPORT; STOP.

## 17. IP-17

IP-17 remains `REQUIRES_GENERIC_SEAM / DEFERRED / NON-BLOCKING`.

Initial migration may use `run → busy → background execute_chat → ChatResult → render`.

Do not invent a Reflex-specific streaming contract. If future product requirements need granular progress/events, create a generic presentation-independent event seam in a separately governed work item.

## 18. Standard RJ completion report

Every RJ-1 → RJ-6 package must report:

### BASE
- starting commit
- branch
- PR/change package
- inherited previous PASS

### IMPLEMENTATION
- files changed
- contracts changed
- dependencies changed
- explicitly preserved components

### VERIFICATION
- targeted tests
- adversarial tests/review
- full regression
- runtime/browser/deployment evidence where applicable

### DIFF AUDIT
- unexpected files/changes
- DB/schema changes
- core/provider changes
- dependency drift
- Reflex version drift

### RESIDUALS
- blockers
- non-blockers
- deferred
- A/B/C/D scope discoveries

### VERDICT
- PASS
- FAIL
- GOVERNOR_REVIEW_REQUIRED

### STOP
Do not begin the next RJ bundle.

## 19. Final Governor Migration Gate

RJ-6 PASS does not authorize production migration.

After RJ-0 → RJ-6 evidence is complete, submit:
- exact final commit
- PR/merge history
- RJ completion reports
- full regression status
- functional parity status
- persistence evidence
- deployment topology
- secret/config contract
- runtime-security migration deltas
- browser/mobile evidence
- rollback evidence
- remaining residuals

Governor then issues one of:
- AUTHORIZE CUTOVER
- CONDITIONAL / REPAIR
- REJECT

Only explicit AUTHORIZE CUTOVER permits production replacement.

## 20. Implementer stop law

When assigned one RJ bundle, do only that bundle. Finish its tests, audit, report and STOP. Do not proactively begin the next RJ bundle. Do not reinterpret this Master Brief as authorization for the entire migration in one session.

The speed mechanism is inherited context + no repeated research, not removal of Governor gates.

---

END — RORO JONGGRANG PRODUCTION MIGRATION BRIEF v1
