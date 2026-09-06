# MULTIMIND — PROJECT OPERATING CONSTITUTION

Status: GOVERNOR MASTER / ACC KEEP MASTER
Purpose: durable Layer-A project context for MultiMind chats and workstreams.

## Purpose

MultiMind is a personal/small-user AI platform intended to become the user's stable AI backbone: one application over multiple interchangeable AI providers/models, with orchestration, debate, memory, files, sessions, persistence, provider fallback, and rich presentation handled by MultiMind rather than by repeatedly moving between provider applications.

Providers are replaceable capabilities behind MultiMind. The application itself should remain stable when providers, models, credentials, pricing, or availability change.

Final priority:

`DEPLOYABLE → RELIABLE → RECOVERABLE → BORING → LOW MAINTENANCE`

Do not add architecture, services, frameworks, abstractions, or research unless they materially improve that objective. Technology curiosity is not roadmap authorization.

## Three context layers

### Layer A — Project DNA

This constitution contains stable project-wide laws and is inherited by MultiMind workstreams/chats.

### Layer B — Authoritative Current State

Mutable status belongs in repository governance/status Markdown. When exact current phase, baseline, gate status, migration bundle, or implementation state matters, inspect the repository and current governance artifacts. Do not infer mutable state from this constitution.

### Layer C — Task Handoff

Each branch/chat receives only the narrow mission, current baseline, relevant locks, allowed/forbidden scope, evidence requirements, and return condition. Do not recreate giant continuation briefs when Layers A+B already exist.

## Authority / evidence

For implementation facts, prefer:

`CURRENT REPOSITORY / FILESYSTEM > MERGED IMPLEMENTATION EVIDENCE > CURRENT REPOSITORY GOVERNANCE / STATUS ARTIFACTS > ACCEPTED GOVERNOR STATE > OLD CHAT / PROMPT ASSUMPTIONS`

Latest explicit accepted decision supersedes conflicting older decisions, but substantive supersession must be recorded durably rather than silently rewriting project history.

Never claim implementation, closure, migration, or deployment from plans alone.

## Governance roles

### Project Governor

Owns cross-workstream architecture, scope, sequencing, acceptance, closed gates, production/cutover authorization, and durable project coherence.

### Local workstream / branch governor

May autonomously inspect → design → implement → test → review → repair → PR/merge when explicitly authorized and within its inherited charter. Escalate only for genuine blockers, material scope expansion, cross-workstream conflict, destructive/irreversible decisions, invalidated locked assumptions, or decisions reserved to the Project Governor.

### Implementers / agents

Implement bounded accepted work. They do not silently redefine product architecture, reopen closed research, or promote experiments into production.

### Research

Answers a specific unresolved decision. Research does not itself authorize implementation or roadmap expansion.

## Governor interaction protocol

- `[1] ACC KEEP MASTER` — accept the substantive result and persist the accepted governance state in repository Markdown before treating it as a durable master checkpoint.
- `[2] NEXT` — continue to the next logical investigation/step without locking the current result as master.
- `[3] DEEP` — perform a deeper/adversarial investigation. DEEP does not itself lock a decision.
- `[4] CODEX` — authorize the accepted bounded implementation package for Codex. CODEX does not itself authorize production cutover or alter governance.

Important substantive governance must not exist only in chat. Persist accepted decisions, closures, supersessions, and durable ledgers in repository Markdown.

## Core architecture law

`MultiMindApplication` is the presentation-independent application boundary.

Presentation hosts should consume this boundary rather than reproduce application orchestration.

Target conceptual architecture:

`PRESENTATION HOST → MultiMindApplication / stable application + composition boundaries → existing orchestration / debate / providers / files / memory / persistence → authoritative durable data`

Frontend code must not duplicate provider routing, DebateOrchestrator, persistence semantics, memory rules, security boundaries, or application truth.

Core/application code must not acquire presentation-framework concerns merely for frontend convenience.

Frontend-independent does **not** mean HTTP. Do not introduce FastAPI, REST, JSON transport, RPC, microservices, or a network boundary merely to connect a presentation host when direct in-process Python remains sufficient.

## Provider / AI backbone law

Preserve MultiMind's provider abstraction, routing/fallback behavior, debate semantics, memory/session behavior, file handling, and failure contracts.

The long-term product should make providers replaceable and credentials/models easy to configure without redesigning MultiMind. Provider-specific concerns belong behind stable provider/application boundaries. A new provider must not require presentation-layer business logic.

Browser-backed chatbot automation is an `IDEA / PARK` concept, not an active production requirement. Official/compatible APIs are preferred for a low-maintenance backbone.

## Persistence / identity law

SQLite and the existing per-user persistence namespace remain authoritative unless new evidence justifies an explicit architecture change.

Do not migrate databases merely because a new frontend or hosting platform is introduced.

Presentation state must never become a shadow source of truth for sessions, memory, conversation history, provider results, or persisted application data.

Production deployment must provide restart-safe durable storage appropriate to the authoritative persistence model.

Preserve identity validation, user isolation, path containment, restore semantics, and existing Security/Hardening guarantees.

## Presentation host direction

Reflex is the accepted production-host direction unless newer accepted repository governance explicitly supersedes it.

The intended shape is direct in-process Python:

`Browser → Reflex presentation/state → MultiMindApplication / composition boundary → existing MultiMind core/providers/memory/persistence`

Do not reopen completed platform competition merely because another framework is interesting.

Streamlit remains the behavioral/reference host and rollback path until an explicit production cutover is authorized. Do not prematurely delete Streamlit or require data conversion merely to move presentation hosts.

## Design-DNA / Theme architecture

Design-DNA is presentation intelligence, not application business logic.

Preserve the established separation among application semantics, presentation/archetype projection, cultural/web identity, material/environment composition, accessibility/adaptation, and final rendering.

Accessibility/safety and application semantics outrank decorative identity. Theme/DNA switching must not corrupt application/session truth.

Do not implement per-theme applications, duplicate resolvers, brittle framework-specific DNA logic, or push DNA concerns into Core.

## Private Design-DNA direction

The private repository `zizzul13-alt/multimind-design-dna` is the intended private home for extracted Design-DNA / Theme Studio intellectual property when the repository's current migration/extraction governance authorizes the actual extraction.

Desired boundary:

`PUBLIC MULTIMIND → SMALL STABLE DNA BRIDGE → PRIVATE DESIGN-DNA PACKAGE`

This separation is a package/repository ownership boundary, not justification for a new network service or distributed system.

Public MultiMind must remain operational when the private DNA package is absent, unavailable, incompatible, or fails to load.

Required degradation:

- private DNA available → enhanced intended presentation;
- private DNA absent/failed → boring, neutral, safe default presentation → application remains usable.

Never make core/provider/persistence correctness depend on private Design-DNA.

Do not claim extraction is complete merely because the public repository is extraction-ready. Obtain current extraction status from repository governance.

## Closed-gate law

Previously accepted `CLOSED` / `PASS` gates remain closed.

Do not reopen Security, Hardening/Reliability, QA/Testing, Core, UI/UX/Design-DNA research, platform selection, or another completed gate because of curiosity, cleanup opportunities, or a new tool/framework.

Reopening requires specific new evidence that invalidates an accepted assumption or exposes a concrete defect owned by that gate. Route findings to their owning concern rather than expanding the active task.

## Implementation discipline

Before repository-dependent work:

1. verify repository identity and actual current baseline;
2. inspect relevant current governance/status artifacts;
3. distinguish implementation reality from historical prompts;
4. identify the owning workstream/bundle.

Prefer the smallest coherent change.

Normal implementation evidence loop:

`inspect → implement → targeted verification → adversarial/self-review → repair → regression verification → diff review → durable report/checkpoint where required`

A downstream task must not silently compensate for an incomplete upstream contract.

Do not weaken tests or established guarantees merely to make migration pass.

When implementation changes require integration, keep them reviewable and attributable to the owning task rather than accumulating uncontrolled mega-changes.

## Deployment / maintenance law

Optimize total human-attention cost, not merely technology count.

A larger stack that runs unattended may be preferable to a smaller stack that requires routine manual intervention, but every permanent service must justify its operational burden.

Prefer few routine dashboards, automated deployment/recovery, durable storage, safe secret handling, clear rollback, boring failure behavior, and minimal vendor-specific application coupling.

Avoid Kubernetes/microservices/extra databases/extra APIs merely for fashion; unnecessary transport layers; infrastructure that creates a second job for a tiny user base; and paid or credit-card-dependent services without explicit user approval.

Secrets must remain server-side and must never be committed to source control.

## Production / cutover law

Research success, proof success, implementation completion, PR merge, or `ACC KEEP MASTER` does **not** independently authorize production cutover.

Production replacement occurs only after the currently authoritative migration program reaches its required evidence gates and the Project Governor/user explicitly authorizes cutover.

Until then production truth remains protected, rollback remains available, Streamlit is not removed prematurely, and experiments/proofs do not become production by implication.

## New-chat task handoff standard

A task-specific handoff should contain only:

- `ROLE`
- `CURRENT AUTHORITATIVE BASELINE`
- `TASK / MISSION`
- `INHERITED LOCKS RELEVANT TO THIS TASK`
- `ALLOWED SCOPE`
- `FORBIDDEN SCOPE`
- `REQUIRED EVIDENCE / EXIT CONDITION`
- `RETURN-TO-GOVERNOR CONDITION`

Return to the Project Governor when the task/workstream reaches its exit condition, a true blocker appears, new evidence invalidates an inherited lock, or a material scope/cross-workstream/destructive decision is required. Do not return for routine within-scope implementation decisions.

## Context hygiene

- Stable project philosophy/architecture question → Project constitution is sufficient.
- Exact current phase/status/merged state → read current repository governance/status artifacts.
- Coding/review/audit dependent on implementation → inspect repository plus relevant current status artifacts first.
- New bounded task with known baseline → use this constitution plus a short Layer-C handoff.
- Continuation whose state was not durably persisted → request/use a continuation handoff.
- Historical chat conflicts with repository → repository reality wins; reconcile before proceeding.
- Accepted substantive Governor result → persist it to repository Markdown.
- Brainstorming/technology curiosity → do not silently turn it into roadmap or trigger broad repository work.
- New evidence potentially invalidating a closed gate → inspect owning evidence and escalate before reopening.

## Operating default

When uncertain, choose the path that most directly advances:

`DEPLOY + LOW MAINTENANCE`

while preserving:

`DATA → CORE BEHAVIOR → PROVIDER INDEPENDENCE → RECOVERABILITY → PRESENTATION CONTRACTS`

Do not solve hypothetical future scale at the expense of today's small, maintainable system.

For exact **CURRENT STATE**, read repository governance/status artifacts. Do not use this constitution as a mutable status ledger.
