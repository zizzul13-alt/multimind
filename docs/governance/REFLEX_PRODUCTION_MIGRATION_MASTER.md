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
- Historical code implementation baseline before governance-only commits: `main@6a040a7f53b77e54d0b4f695e2eefd67b3fa1046`.
- RJ-0 execution-start repository HEAD: `766717f2989e0dac3bcf7b5b809b9aa0996dcc6d`.
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
- Reflex/container deployment may use environment/secrets.
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

## RJ-0 — Reconcile / Freeze / Parity Census — CLOSED / PASS / LOCKED

RJ-0 is complete. It reconciled the actual repository, classified drift, inventoried the production-facing surface, and froze the RJ-3 parity denominator without reopening closed platform research.

### RJ-0 final status

- CURRENT HEAD at execution-start reconciliation: `766717f2989e0dac3bcf7b5b809b9aa0996dcc6d`.
- Historical code implementation baseline: `6a040a7f53b77e54d0b4f695e2eefd67b3fa1046`.
- Drift between those points: governance/documentation only.
- Implementation drift affecting locked migration assumptions: NO.
- Master compatibility: YES.
- Architecture invalidated: NO.
- STOP condition triggered: NO.
- Hard blockers: 0.
- Verdict: PASS.

Subsequent Governor Markdown persistence commits after the execution-start census do not alter the RJ-0 implementation denominator; they record accepted governance findings.

### Three-level parity model — LOCKED

RJ-3 parity is not satisfied merely because equivalent buttons exist.

Reflex must preserve three levels of accepted production contract:
1. **Capability parity** — production-facing capabilities remain available.
2. **Behavioral parity** — interaction and application semantics remain correct.
3. **Presentation-contract parity** — accepted archetype, Design-DNA, composition and projection semantics remain preserved.

Pixel-for-pixel reproduction of Streamlit is NOT required. Accepted presentation contracts are required.

This does not reopen the CLOSED UI/UX or Design-DNA work. Migration consumes those accepted production contracts as inherited evidence.

### RJ-3 parity denominator — FROZEN

#### A. Identity and navigation
- identity/login/logout semantics.
- session/workspace navigation.
- locked migration journey: `LOGIN → PRE-WORKSPACE THEME / THEME STUDIO STAGE → EXPLICIT APPLY → MULTIMIND WORKSPACE → THEME STUDIO REMAINS ACCESSIBLE`.

The pre-workspace stage/handoff is a locked migration requirement/gap rather than falsely claimed current Streamlit behavior.

#### B. Session lifecycle
- create session.
- list sessions.
- select session.
- session history retrieval/rendering.
- semantic continuity including A→B→A session switching behavior.

#### C. Input and composition
- prompt entry.
- prompt template selection.
- template description.
- template variable extraction/input.
- generated template preview.
- generated prompt remains editable before send.
- continue vs standalone context behavior.
- session mode.
- compressor control.
- active-agent selection.
- debate-round selection.
- selected skill.
- supported multi-file upload behavior.

#### D. Usage feedback
Current production exposes pre-send estimates, not a proven post-run actual-token/cost UI contract.
Required parity:
- estimated prompt tokens.
- estimated file tokens.
- estimated total tokens.
- estimated cost.
- moderate/high token-usage warnings.

Post-run actual token/cost display is NOT part of the frozen baseline denominator absent new evidence.

#### E. Execution and status semantics
- real `MultiMindApplication` execution.
- application warnings surfaced to presentation.
- terminal application/provider failure feedback.
- success feedback.
- truthful processing/busy feedback.
- Reflex migration additionally inherits the closed Integration Proof requirement for persistent busy state and duplicate-run protection.

The stronger Reflex busy/duplicate guard is a locked migration requirement; it must not be falsely described as existing sophisticated Streamlit busy-state behavior.

#### F. Persisted result lifecycle
The production contract is not merely immediate `ChatResult` rendering.

Required lifecycle semantics:
`ChatRequest → execute_chat() → persistence → success/rerun/state transition → session history read → PresentationSnapshot → projection → interaction-shell/history/result rendering`.

RJ-1 therefore must provide the generic history-read seam required by the Reflex host. Presentation must not bypass that need by reading private persistence directly.

#### G. Presentation contracts / archetypes
The existing production presentation architecture includes presentation models/builders/projections/resolution/shell behavior and seven canonical archetypes:
- `chat_first`
- `command_center`
- `ai_workspace`
- `ai_research_lab`
- `agent_canvas`
- `terminal_hacker`
- `minimal_saas`

Archetypes are not merely color themes. Existing presentation behavior includes archetype-aware composer morphology, grouping/disclosure behavior, wording and truthful processing labels while backend/application semantics remain presentation-independent.

Reflex must preserve accepted archetype/Design-DNA/projection semantics without moving archetype-specific branching into backend/core.

#### H. Theme Studio
Existing production baseline to preserve:
- production-accessible Theme Studio.
- role-based Identity/Cultural DNA composition.
- Web/Information DNA composition.
- archetype selection.
- editable presentation controls/tokens.
- isolated draft.
- live preview.
- explicit Apply Composition.
- explicit Discard/Reset.
- Apply promotes active theme.
- Apply promotes active archetype.
- Apply promotes active composition.
- applied custom-theme current-session isolation/discoverability semantics.
- Theme Studio remains reachable from the MultiMind experience.

Locked migration addition:
- after login, expose the pre-workspace Theme/Theme Studio stage.
- explicit Apply carries the selected composition into MultiMind workspace.
- Theme Studio remains accessible after handoff.

Theme Studio rebuild from zero is NOT required. Behavioral migration is required.

#### I. Data operations
- backup/export capability.
- safe restore capability and semantic result handling.
- user isolation.
- existing DB namespace/schema semantics.
- restore/runtime invalidation semantics as owned by the generic application boundary.

#### J. Runtime UX acceptance
- production browser usability.
- phone usability.
- tablet usability.
- no migration regression that makes required controls, busy state, result/history or Theme Studio unreachable.

Closed Reflex browser/mobile integration evidence is inherited; RJ-3/RJ-5 must validate the implemented production host rather than rerunning framework selection.

### Explicit exclusions from initial parity denominator

Unless new repository evidence or an explicitly accepted requirement changes them, these are NOT required initial RJ-3 parity:
- post-run actual token/cost UI.
- granular streaming/fine-grained progress events; IP-17 remains deferred/non-blocking.
- pixel-for-pixel Streamlit reproduction.
- literal Streamlit `st.session_state` implementation details.
- dev-only Theme Preview Spike guarded by `MULTIMIND_DEV_SPIKE`.

### Theme Studio state ownership clarification

Current Theme Studio uses Streamlit-hosted presentation state. Theme draft, active theme, active archetype, active composition, preview state and navigation/handoff remain presentation concerns.

Reflex may implement equivalent host-owned presentation state. Do not move these concerns into core merely to eliminate Streamlit imports from UI modules.

### RJ ownership after RJ-0 closure

RJ-1 remains focused on:
- config/secrets portability.
- shared application composition root.
- session/history read seams.
- backup/export seam.
- removal of presentation-owned persistence access while preserving Streamlit compatibility.

RJ-3 owns:
- full functional/behavioral/presentation-contract parity on Reflex.
- seven-archetype presentation behavior.
- Theme Studio presentation parity.
- locked pre-workspace Theme Studio entry/handoff journey.

RJ-0 found no reason to expand RJ-1 into a broad UI/core refactor.

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
Provide a narrow generic export/download operation while preserving the existing safe restore application contract.

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
- RJ-2: Reflex production host implementation on the accepted generic seams.
- RJ-3: full frozen three-level parity denominator including Theme Studio and pre-workspace handoff.
- RJ-4: exact durable production storage/runtime deployment contract.
- RJ-4/RJ-6: production restart/recreate persistence proof.
- RJ-5: dual-host/torture parity evidence.
- RJ-6: explicit cutover/rollback drill.
- IP-17: deferred generic streaming/progress seam; non-blocking.

Current known hard blockers: 0.
