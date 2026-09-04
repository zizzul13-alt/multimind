# MULTIMIND — REFLEX PRODUCTION MIGRATION MASTER LEDGER

Status: GOVERNOR MASTER / ACC KEEP MASTER
Last updated: 2026-09-04
Production migration authorized: NO

## Governance

This file is the cumulative authoritative ledger for Governor decisions accepted with `ACC KEEP MASTER` in the Reflex Production Migration Track.

Source-of-truth priority remains:
1. current repository/files
2. merged implementation evidence
3. current artifacts
4. this Governor master ledger
5. older chat assumptions

Latest explicit accepted decision supersedes conflicting older decisions. Supersession must be recorded rather than silently erasing history.

### Mandatory result persistence rule

For every substantive Governor result/decision:
- `[1] ACC KEEP MASTER` means the accepted result MUST be persisted to Markdown in the repository before it is treated as a durable master checkpoint.
- `[2] NEXT` proceeds without locking the current result.
- `[3] DEEP` requests deeper/aggressive audit/research and does not itself lock the result.
- `[4] CODEX` authorizes sending the currently accepted work package to Codex; it does not itself change governance.
- ACC KEEP MASTER does NOT authorize production migration.
- Accepted state is cumulative. Prior accepted state may only be superseded by newer evidence plus explicit acceptance.

## Accepted Master Implementation Brief

`docs/governance/REFLEX_RORO_JONGGRANG_MIGRATION_BRIEF.md` is the accepted **MULTIMIND REFLEX — RORO JONGGRANG PRODUCTION MIGRATION BRIEF v1** and is the cumulative implementation instruction for RJ-0 through RJ-6.

Status: `ACC KEEP MASTER`.

The brief inherits this ledger and all compatible locked decisions below. It does NOT authorize Codex by itself and does NOT authorize production cutover. Codex dispatch still requires explicit `[4]`/user authorization; production replacement still requires the Final Governor Migration Gate.

## Locked production baseline

- Repository: `zizzul13-alt/multimind`
- Baseline: `main@6a040a7f53b77e54d0b4f695e2eefd67b3fa1046`
- Current presentation: Streamlit.
- `MultiMindApplication` remains the presentation-independent application boundary.
- Target architecture remains direct in-process Python: Reflex → application/composition boundary → existing core/providers/SQLite.
- FastAPI/REST/HTTP glue is not required and must not be introduced absent new evidence.
- Streamlit remains the rollback/baseline presentation until explicit cutover authorization.

## Closed inherited evidence

Do not reopen without specific counter-evidence:
- Reflex platform battle / platform selection.
- Pseudo-MultiMind framework stress testing.
- Reflex basic viability.
- Reflex Production Integration Proof.
- Direct in-process application integration.
- busy/duplicate-run behavior.
- A→B→A session behavior.
- upload feasibility.
- browser/mobile feasibility.
- IP-27 PASS.
- IP-28 PASS.
- previously closed Core, Security, Hardening/Reliability, QA/Testing and UI/UX gates.

Reflex Production Integration Proof remains CLOSED / CONDITIONAL_PASS with zero hard integration blockers.

## Production Architecture locked decisions

### Framework
- Migration baseline: Reflex `0.8.22`, matching the closed integration proof.
- Do not silently upgrade Reflex during migration. Framework upgrade is separate work unless new evidence makes 0.8.22 unsuitable.

### Configuration / secrets
Current `Config.get_api_keys()` Streamlit-secret coupling must be removed from the generic production path.

Locked shape:
`Presentation/Deployment → Configuration Source → per-user/default resolution → agent construction → MultiMindApplication`

Required semantics:
- Streamlit may use a Streamlit secrets adapter.
- Reflex/container deployment may use environment/deployment secrets.
- tests may inject a mapping/source.
- existing per-user → `default` fallback semantics must remain.
- identity validation and DB path containment remain generic and preserved.

### SQLite / persistence
- Preserve SQLite and existing per-user database namespace/schema.
- No DB schema conversion is required merely for Reflex migration.
- Production requires writable, restart-safe durable storage for authoritative SQLite data.
- Reflex Cloud `include_db` local SQLite is rejected as the authoritative production database for the current architecture because its local database persistence contract does not satisfy MultiMind requirements.
- `REFLEX_HOT_RELOAD_EXCLUDE_PATHS=data` is a development watcher contract, not a production persistence mechanism.
- Self-host/container is the leading deployment architecture; no hosting vendor is locked yet.

### Rollback
Reflex and Streamlit must preserve the same application/provider/persistence semantics and DB namespace/schema so rollback requires no data conversion.

### CORS
Production Reflex runtime must restrict CORS to the actual frontend origin rather than leaving an unrestricted default. This is a migration runtime acceptance criterion, not a reopening of the closed Security gate.

### IP-17
IP-17 remains `REQUIRES_GENERIC_SEAM / DEFERRED / NON-BLOCKING`.
Initial production migration may use run → busy → background execution → `ChatResult` → render.
Any future granular event/progress stream must be presentation-independent and contain no Reflex-specific core types.

## Roro Jonggrang migration strategy v3

Status: ACC KEEP MASTER.

Roro Jonggrang means one inherited migration program executed serially through hard bundle gates. It does NOT mean a one-shot uncontrolled rewrite.

Canonical chain:
1. RJ-0 — Reconcile / Freeze / Parity Census
2. RJ-1 — Portability + Application Boundary
3. RJ-2 — Reflex Production Host
4. RJ-3 — Functional Presentation Parity
5. RJ-4 — Durable Persistence + Deployment
6. RJ-5 — Torture / Dual-Host Parity
7. RJ-6 — Cutover + Rollback Proof
8. FINAL GOVERNOR MIGRATION GATE

Production migration remains unauthorized until the final Governor gate.

### Serial-first law
Bundle N+1 must not silently compensate for a failed or incomplete bundle N. If a downstream bundle exposes an upstream defect, stop, repair the owning bundle, rerun its verification, then continue.

Expected bundle loop:
`inspect → implement → targeted tests → adversarial/self-review → repair → full regression → diff review → report → STOP`

### Scope classification law
A discovery during implementation does not automatically expand scope:
- Required for Reflex parity → repair within the owning RJ bundle.
- Existing unrelated bug → record/defer unless it invalidates migration evidence.
- Nice refactor → reject/defer.
- New evidence invalidating a closed assumption → STOP for Governor review.

### Implementation execution model — LOCKED
Selected model: **B — One Master Brief + serial PR/bundle execution.**

- One cumulative Roro Jonggrang Master Implementation Brief governs the entire RJ-0 → RJ-6 campaign.
- Do not regenerate/re-research the migration architecture from zero for every bundle.
- Implementation nevertheless proceeds through separate serial bundle checkpoints.
- Each implementation bundle must end with its own report/evidence and STOP for Governor review before the next implementation bundle proceeds.
- Prefer a separately reviewable PR/change package per implementation bundle rather than one mega-PR spanning RJ-1 through RJ-6.
- RJ-0 is reconciliation/freeze rather than a feature implementation bundle; it may feed the first implementation package without requiring a meaningless code PR when no code changes are necessary.
- A later bundle may not silently repair an earlier failed bundle; ownership returns to the earlier bundle and its verification is rerun.
- One mega-session/mega-PR for the full migration is rejected as the canonical execution model.
- One long continuous implementation branch with only commit checkpoints is not the canonical model because it weakens review and rollback clarity.
- This execution-model lock does NOT itself authorize Codex or production cutover. Codex still requires explicit `[4]`/user authorization; production cutover still requires the Final Governor Migration Gate.

### Serial branch / PR discipline — LOCKED

- RJ-N starts from the latest accepted migration baseline produced by the preceding accepted bundle/checkpoint.
- Only one implementation bundle is active at a time under the canonical migration flow.
- Do not implement RJ-(N+1) in parallel with an unaccepted RJ-N.
- Every PR or reviewable change package must identify its starting commit/baseline.
- Changes must remain attributable to the owning RJ bundle; downstream work must not hide or absorb upstream defects.
- Governor acceptance of the current bundle precedes progression to RJ-(N+1).
- When repository merge/rebase drift occurs between accepted bundles, reconcile that drift before beginning the next implementation bundle.
- When a bundle changes repository code/configuration/artifacts that need integration, use a separately reviewable PR/change package rather than accumulating the whole migration into one branch.
- A bundle that genuinely requires no repository change does not need a meaningless code PR. RJ-0 may consist of reconciliation/census/evidence only; later proof-heavy bundles may likewise produce evidence/deployment artifacts rather than feature code when appropriate.
- The canonical unit is therefore a reviewable **change/evidence package**, with a PR required when repository changes need to be merged.

Canonical progression:
`RJ-0 → Governor acceptance → RJ-1 package/PR → STOP → Governor acceptance → accepted integration → RJ-2 from that accepted baseline → ... → RJ-6 → Final Governor Migration Gate`.

## RJ-0 — Reconcile / Freeze / Parity Census — LOCKED

RJ-0 is the execution-start reconciliation and denominator freeze. It is not a rerun of closed platform research.

Required work:
1. Reconcile actual current production `main` HEAD.
2. Compare current repository state against this Governor Master and inherited closed evidence.
3. Distinguish governance/documentation-only drift from implementation drift.
4. Detect material repository drift that affects locked migration boundaries or assumptions.
5. Inventory the actual production-facing user journey and capabilities present at execution start.
6. Freeze the RJ-3 functional parity denominator from that census plus explicitly locked intended migration requirements.
7. Record the exact starting commit.

RJ-0 must distinguish two categories rather than falsifying parity:
- capability/surface already present in the production implementation → existing baseline behavior to preserve/migrate.
- explicitly locked intended production requirement not yet fully implemented in the Streamlit baseline → migration requirement/gap, not falsely described as existing parity.

Minimum census scope includes:
- locked journey: `LOGIN → SELECT THEME + THEME STUDIO → APPLY → MULTIMIND + THEME STUDIO`.
- identity/login/logout.
- session creation/listing/selection/history.
- chat execution.
- continue/standalone context behavior.
- session mode.
- compressor.
- active-agent selection.
- debate rounds.
- selected skill.
- uploads.
- busy/duplicate-run behavior.
- warnings/errors.
- final answer/debate rendering.
- token/cost rendering where production exposes it.
- backup/restore.
- mobile/tablet/browser production usability surfaces.

RJ-0 output must record:
- CURRENT HEAD.
- MASTER COMPATIBILITY.
- PRODUCTION-FACING CAPABILITY CENSUS.
- RJ-3 PARITY DENOMINATOR.
- DRIFT = YES/NO, with classification if YES.

STOP condition:
If current implementation drift materially invalidates a locked architecture assumption or closed evidence, do not silently adapt the migration. STOP for Governor review.

## Standard RJ bundle completion evidence — LOCKED

Every implementation bundle RJ-1 through RJ-6 must end with a standardized completion report/evidence package and STOP before the next bundle begins.

Required report structure:

### BASE
- starting commit.
- branch / PR or reviewable change package.
- inherited previous RJ PASS/checkpoint.

### IMPLEMENTATION
- files changed.
- contracts changed.
- dependencies changed.
- explicitly preserved/non-changed components where relevant.

### VERIFICATION
- targeted tests.
- adversarial tests/review appropriate to the bundle.
- full regression.
- runtime/browser/deployment proof where applicable.

### DIFF AUDIT
- unexpected changes.
- DB/schema changes.
- core/provider changes.
- dependency/version drift.

Any unexpected DB schema, core/provider, or framework-version change requires explicit explanation and must not be normalized as incidental migration work.

### RESIDUALS
- blockers.
- non-blockers.
- deferred items.
- scope discoveries classified under the locked A/B/C/D scope law.

### VERDICT
One of:
- PASS.
- FAIL.
- GOVERNOR_REVIEW_REQUIRED.

### STOP
Do not begin RJ-(N+1) until the current bundle has been reviewed/accepted under the serial execution model.

The purpose of the standardized report is to preserve comparable evidence across bundles and avoid repeating migration research/interrogation from zero at every checkpoint.

## Production user journey / Theme Studio — LOCKED

Theme Studio is a first-class production user surface in the intended MultiMind journey. It is not merely an internal Design-DNA research/tooling surface and must not be silently deferred from the Reflex migration.

Locked intended journey:
`LOGIN → SELECT THEME + THEME STUDIO → APPLY → MULTIMIND + THEME STUDIO`

Required migration behavior includes:
- theme selection after login.
- Theme Studio access in the pre-MultiMind selection/studio stage.
- applying the selected theme.
- entering MultiMind with the applied theme.
- preserving/applying the selected theme across the handoff as required by the production behavior.
- Theme Studio remaining accessible from the MultiMind experience.

Theme selection, Theme Studio, apply-theme behavior, theme-to-MultiMind handoff, and MultiMind-to-Theme-Studio access are therefore required production parity surfaces for the Reflex migration.

Design-DNA research/specification work must not be conflated with the production Theme Studio surface. This lock does not create or imply a separate "Design machinery" subsystem.

## RJ-1 stable scope

RJ-1 is not merely a `list_sessions()` patch. Production presentation currently contains persistence/configuration coupling that must be replaced by narrow presentation-independent use-case seams.

### RJ-1A — Config portability
- generic secret/config source.
- preserve per-user/default semantics.
- preserve validated identity semantics and DB path containment.

### RJ-1B — Composition root
Create/reuse one presentation-independent application composition path for a validated user, responsible for configuration resolution, agent construction, database construction and application/runtime wiring.

Do not duplicate provider/database setup separately in Streamlit and Reflex.

### RJ-1C — Application read boundary
Required presentation use cases include:
- `create_session()`
- `list_sessions()`
- `select_session()`
- session chat/history retrieval through a generic seam such as `get_session_chats()`.

Exact names may change if implementation evidence requires it, but the capability/boundary is locked.

### RJ-1D — Backup boundary
Presentation must not own direct SQLite backup-file reading.
Provide a narrow generic database export/backup operation while preserving the existing safe restore application contract.

### RJ-1E — Compatibility
RJ-1 must preserve:
- runnable Streamlit baseline.
- DB paths and schema.
- user isolation.
- provider configuration behavior.
- identity behavior.
- persistence semantics.

### Boundary law
Presentation MAY own visual/navigation/form/busy/theme/archetype state.

Presentation MUST NOT own:
- DB path resolution semantics.
- direct DB session/history reads.
- direct DB backup-file reads.
- persistence lifecycle.
- provider routing/orchestration.
- memory persistence.
- restore mechanics.

Do not expose `MultiMindApplication._database()` to presentation and do not turn `DatabaseManager` into a new presentation API. Add the smallest generic use-case seam when evidence shows a presentation operation requires persistence access.

### Anti-overengineering law
Do not create abstraction merely for architectural aesthetics. A new seam is justified only when current presentation directly owns persistence, a presentation-specific dependency blocks Reflex portability, or migration proof supplies a concrete requirement.

## Remaining migration residuals

- RJ-1: generic config/secrets portability.
- RJ-1: production application read/export seams and shared composition root.
- RJ-3: preserve the locked Theme Studio production journey and functional parity.
- RJ-4: exact durable production storage/runtime deployment contract.
- RJ-4/RJ-6: production restart/recreate persistence proof.
- RJ-6: explicit rollback drill.
- IP-17: deferred generic streaming/progress seam; non-blocking.

Current known hard blockers: 0.
