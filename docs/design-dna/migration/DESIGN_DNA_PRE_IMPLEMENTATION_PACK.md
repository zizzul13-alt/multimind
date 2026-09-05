# MULTIMIND DESIGN-DNA — PRE-IMPLEMENTATION PACK

Status: GOVERNOR-READY / NON-CODE PACKAGE
Date: 2026-09-05
Depends on: `DESIGN_DNA_MIGRATION_GATE_MASTER.md`, `MIGRATION_BATCH_MAP.md`, Canonical Constitution, current Reflex migration governance.

Purpose: close the planning work that can be completed before Codex/runtime implementation. This document does NOT authorize Codex, M0 implementation, production migration, or EQ4 credit.

---

# 1. M0 CONTRACT FREEZE

## 1.1 Runtime responsibility

M0 converts canonical DNA definitions plus semantic presentation context into a deterministic, explainable, host-neutral presentation projection. It MUST NOT execute application/domain behavior.

Canonical flow:

```text
DNA Registry + Composition Request + Semantic UI Context + Runtime Constraints
→ validate
→ hard vetoes
→ relevance
→ ownership
→ dominance
→ compatibility / contradiction
→ demotion/rescope
→ semantic projection
→ survival checks
→ provenance trace
→ ThemeProjection
```

## 1.2 Required conceptual inputs

### DNA Registry
For each canonical unit required by the active composition:
- canonical ID;
- unit kind: REFERENCE / ENGINE / PRIMITIVE / FIXTURE;
- lineage/family;
- provenance pointer;
- license/IP metadata where applicable;
- 15-axis mechanism contracts;
- semantic-zone ownership/non-ownership;
- viewport/state scope;
- compatibility/conflict information;
- fallback/survival contract;
- accessibility/Reading-Sanctuary constraints;
- asset applicability metadata.

### Composition Request
- selected user-facing reference/family;
- resolved internal engines/primitives;
- archetype/presentation context;
- explicit composition modifiers, if canonical;
- asset mode/state;
- no application/domain payload mutation.

### Semantic UI Context
- canonical semantic zones U1–U9;
- surface/zone role;
- viewport class/capabilities;
- interaction/state context;
- reading-heavy status;
- content-language/script metadata where available;
- reduced-motion/accessibility context;
- host capability declaration.

### Runtime Constraints
- accessibility vetoes;
- Reading Sanctuary;
- performance/degradation constraints;
- asset availability/failure state;
- host-supported projection capabilities.

## 1.3 Required output: ThemeProjection

Host-neutral resolved projection containing, at minimum:
- composition identity and deterministic fingerprint/version;
- resolved mechanism set per axis × semantic zone × viewport/state;
- structural/morphology directives;
- spacing/density/layout directives;
- information hierarchy directives;
- material/construction directives;
- light/color directives;
- typography/script directives;
- motion/temporal directives;
- narrative/sequencing directives;
- interaction directives;
- atmosphere/environment directives;
- optional sound/rhythm directive only where applicable;
- adaptation/responsive directives;
- symbol/iconography directives;
- scale/granularity directives;
- asset slots/intents without requiring asset availability;
- fallback/degradation decisions;
- accessibility and Reading-Sanctuary decisions;
- provenance/explainability trace;
- warnings/rejections for invalid composition.

The projection MUST NOT contain Reflex-specific component objects, Streamlit objects, provider/core objects, database handles, or direct application mutation commands.

## 1.4 Determinism law

Equivalent canonical inputs + equivalent runtime constraints MUST resolve to semantically equivalent ThemeProjection. Hidden random aesthetic selection is forbidden in the canonical resolver. If controlled variation is later desired, it must be explicit input/seed and reproducible.

## 1.5 State law

Theme selection changes presentation state only. Application/session/provider/persistence state is not recreated or mutated merely because DNA changes. A→B→A must restore semantically equivalent A projection while preserving application state.

## 1.6 Provenance law

Every non-trivial resolved mechanism must be explainable back to owning DNA unit(s), axis/zone scope, conflict/demotion decision, fallback if any, and applicable asset/license decision.

## 1.7 Degradation law

Degradation is deterministic and identity-preserving:

```text
FULL ELIGIBLE ASSET
→ PARTIAL ASSET / SAFE SUBSTITUTE
→ ASSET-OFF STRUCTURAL PROJECTION
→ ACCESSIBILITY/PERFORMANCE DEMOTION
→ SAFE CANONICAL BASELINE
```

A degradation step may reduce richness but must not corrupt semantics, accessibility, application state, or provenance.

## 1.8 Accessibility law

Accessibility is a super-veto. WCAG 2.2 AA is the target where applicable. Resolver/projector must permit accessibility constraints to override aesthetic ownership. Reading Sanctuary similarly demotes aesthetic intensity on reading-heavy surfaces without deleting identity.

---

# 2. IMPLEMENTATION BOUNDARY MAP

| Owner | Owns | Must not own |
|---|---|---|
| Application/Core | semantic application state, chat/session execution, providers, persistence semantics, domain results | DNA-specific styling/archetype branching, Reflex components |
| Presentation semantic layer | U1–U9 semantic UI model, presentation snapshots, host-neutral presentation meaning | provider/domain execution |
| Design-DNA | registry, DNA contracts, resolver, ownership/conflict/dominance, projection, provenance, fallback rules | application mutation, DB ownership, host component lifecycle |
| Reflex host | component rendering, event wiring, browser lifecycle, responsive realization, host state adapter | inventing DNA rules, bypassing resolver, private persistence reads |
| Streamlit rollback host | existing presentation adapter/baseline only | second divergent DNA engine |
| Asset subsystem | eligible asset registry, provenance/license status, asset resolution, failure status | defining structural identity, bypassing production eligibility |
| Deployment | secrets/config source, persistence mount, origins/CORS, process/runtime concerns | DNA semantics |
| Tests/fixtures | contract, resolver, projection, browser and torture evidence | production-only hidden behavior |

Hard boundary failures:
- DNA import required inside provider/core logic;
- resolver directly reads/writes SQLite;
- canonical DNA model imports Reflex/Streamlit;
- Reflex renderer invents per-reference mechanisms absent from projection;
- asset availability determines whether reference identity exists;
- host switching changes canonical DNA meaning.

---

# 3. M0 ACCEPTANCE MATRIX

M0 is PASS only when all mandatory rows pass.

| Gate | PASS condition | Failure owner |
|---|---|---|
| Registry | canonical definitions load and invalid IDs/types fail clearly | M0 registry |
| Schema | required fields/states validate; explicit absence states preserved | M0 model |
| Type firewall | REFERENCE/ENGINE/PRIMITIVE/FIXTURE cannot silently substitute | M0 model |
| Resolver | deterministic for equivalent inputs | M0 resolver |
| Ownership | axis × zone × viewport/state ownership enforced | M0 resolver |
| Veto | accessibility/safety/semantic veto outranks aesthetics | M0 resolver |
| Dominance | caps prevent uncontrolled flattening | M0 resolver |
| Contradiction | overflow produces deterministic demotion/rescope/failure | M0 resolver |
| Projection | host-neutral ThemeProjection produced | M0 projection |
| Reading Sanctuary | reading-heavy zones are correctly demoted | M0 projection |
| Responsive | mobile is recomposed from contract, not a duplicated theme | M0 projection |
| Reduced motion | motion-sensitive path is deterministic | M0 projection |
| Asset states | loading/partial/off do not break structural identity contract | M0 asset seam |
| State continuity | A→B→A leaves semantic application state unchanged | integration seam |
| Provenance | resolved decisions trace to source unit/mechanism | M0 provenance |
| Explainable failure | canonical failure taxonomy emitted where applicable | M0 resolver |
| Host independence | no Reflex/Streamlit type in canonical contracts | boundary |
| Test harness | fixtures can invoke registry→resolver→projection without browser | M0 tests |

M1 is forbidden while any mandatory M0 row is FAIL. A row may be N/A only when its governing canonical contract explicitly says NOT_APPLICABLE.

---

# 4. M1 ACCEPTANCE CONTRACT — 29 ENGINES

Scope: Material M1–M15 + Environment E1–E14.

M1 proves engine reuse, not 29 decorative presets.

Each engine must demonstrate:
1. canonical ID and kind load correctly;
2. its owned axes/zones are explicit;
3. non-owned axes/zones remain untouched;
4. combination with at least representative compatible counterpart does not erase semantic hierarchy;
5. dominance/collision behavior is deterministic;
6. Reading Sanctuary and accessibility can demote it safely;
7. asset-off behavior remains valid;
8. mobile/adaptation behavior is derived from the same contract;
9. provenance survives composition;
10. engine can be reused by multiple references without reference-specific branching inside the engine.

Batch-level M1 PASS additionally requires:
- 29/29 registered and schema-valid;
- representative Material×Environment pair matrix covers normal, tension, and collision cases;
- no engine requires its own host component family merely to exist;
- no evidence of `if reference == ...` logic in reusable engine machinery;
- failure taxonomy behaves predictably;
- performance remains bounded enough for interactive host use.

M1 failure caused by shared machinery returns to M0. A defect isolated to one engine stays M1-owned.

---

# 5. M2 PROVING-SLICE PLAN

M2 must maximize architectural information, not reference count.

Mandatory set:
- all five Country-Web references: CW01 Switzerland, CW02 USA, CW03 Japan, CW04 China, CW05 Aotearoa New Zealand;
- a small adversarial subset of Cultural Tier-S references selected from canonical contracts at execution time;
- only primitives required by those references.

Cultural adversarial selection MUST collectively stress these dimensions:
- high vs low information density;
- strong vs restrained ornament/material expression;
- typography/script pressure where applicable;
- asymmetric vs orderly morphology;
- strong temporal/motion behavior vs calm/static behavior;
- Reading-Sanctuary conflict;
- mobile recomposition pressure;
- at least one composition with meaningful engine/reference ownership tension.

Do not select by popularity. Select by mechanism coverage from canonical metadata.

M2 PASS requires:
- each proving reference remains recognizably differentiated asset-off;
- differentiation is structural, not wallpaper/stereotype substitution;
- application semantics/state remain identical under theme switch;
- same semantic UI can project into materially different morphology;
- mobile projection is intentional rather than desktop shrink;
- accessibility and Reading Sanctuary survive every proving reference;
- resolver decisions remain deterministic/explainable;
- partial asset failure is safe;
- no growth of bespoke host/reference branching beyond the maintenance budget.

M2 is the scale-out gate. Failure here blocks M3+.

---

# 6. EQ4 EVIDENCE PROTOCOL

EQ4 credit is per canonical unit and requires real authorized host evidence. Documentation assertions are insufficient.

Each EQ4 evidence record must include:
- canonical unit ID and kind;
- implementation commit SHA;
- host/framework version;
- registry/schema validation result;
- resolver/projection contract test result;
- applicable desktop runtime/browser evidence;
- applicable mobile/responsive evidence;
- accessibility result;
- reduced-motion result where applicable;
- Reading-Sanctuary result where applicable;
- asset-off result;
- asset-on result only where production-eligible asset exists;
- partial/failure asset result where applicable;
- A→B→A/state-continuity result for selectable references/compositions;
- collision/fallback result where applicable;
- provenance/explainability result;
- fixture/regression references;
- explicit PASS / FAIL / NOT_APPLICABLE per required dimension;
- Governor acceptance checkpoint.

Rules:
- UNKNOWN is not PASS.
- NOT_APPLICABLE requires canonical justification.
- screenshot-only evidence cannot prove deterministic/state/provenance contracts.
- unit credit is revoked/reopened only by concrete evidence invalidating the accepted proof.
- `271/271 EQ3` never implies any EQ4 credit.

---

# 7. FAILURE / ROLLBACK RULES

Ownership-first repair:

```text
schema/registry defect → M0
resolver/projection/shared-state defect → M0
shared engine defect → M1
proving-reference contract translation defect → M2
canonical EQ3 ambiguity genuinely discovered → STOP / Governor; do not invent
host-only Reflex realization defect → owning RJ/DD integration package
asset eligibility/provenance defect → asset subsystem/M12 unless it exposes illegal dependency
application semantic regression → owning RJ/application bundle; DNA scale-out stops
```

Rollback principles:
- failed M2 does not erase accepted research/EQ3;
- failed M2 does not automatically reset a proven unrelated M1 engine;
- shared M0 defect discovered downstream reopens affected M0 evidence and all downstream evidence dependent on it;
- rollback presentation must not require DB conversion;
- Streamlit remains rollback host until RJ cutover governance says otherwise;
- fallback to asset-off is valid only if structural identity remains within contract;
- never hide a failed reference by silently genericizing it.

---

# 8. CODEX HANDOFF TEMPLATE — PREPARED, NOT AUTHORIZED

Use only after the Final Pre-Codex Gate passes and user explicitly authorizes `[4] CODEX`.

```text
ROLE: DESIGN-DNA M0 IMPLEMENTER
REPOSITORY: zizzul13-alt/multimind
STARTING BASELINE: <EXACT ACCEPTED SHA>
STATUS: AUTHORIZED ONLY WHEN THIS BRIEF IS EXPLICITLY RELEASED

READ FIRST:
1. docs/design-dna/README.md
2. docs/design-dna/migration/DESIGN_DNA_MIGRATION_GATE_MASTER.md
3. docs/design-dna/migration/DESIGN_DNA_PRE_IMPLEMENTATION_PACK.md
4. docs/design-dna/migration/MIGRATION_BATCH_MAP.md
5. docs/design-dna/governance/CANONICAL_CONSTITUTION.md
6. current accepted Reflex/RJ master and RJ-2 implementation evidence

MISSION:
Implement M0 runtime machinery only. Do not scale into M1 unless separately authorized.

HARD BOUNDARIES:
- no Design-DNA branching in AI/provider/core;
- no canonical Reflex/Streamlit types;
- no new HTTP/FastAPI service for DNA;
- no DB schema expansion merely for rendering;
- no 271 bespoke theme/component architecture;
- no mandatory asset dependency;
- preserve application state under theme changes;
- preserve rollback compatibility;
- deterministic resolver + provenance required.

DELIVERABLE:
reviewable M0 change/evidence package with exact baseline, files changed, architecture note, targeted tests, full relevant regression, self-review, unresolved residuals, and STOP.

STOP after M0 report. Do not self-authorize M1.
```

---

# 9. RJ ↔ DESIGN-DNA SYNCHRONIZATION MATRIX

| Concern | Primary owner | DNA evidence reused by RJ | RJ evidence reused by DNA |
|---|---|---|---|
| Generic application boundary | RJ-1 | no | yes |
| Reflex host skeleton/lifecycle | RJ-2 | no | yes |
| DNA registry/resolver/projection | DD M0 | yes | host seam only |
| Material/Environment engine semantics | DD M1 | yes | no |
| Proving reference projection | DD M2 | yes | browser/host realization |
| Functional UI capability parity | RJ-3 | no | application/presentation seam |
| Design-DNA presentation-contract parity | DD + RJ-3 integration | yes | yes |
| Theme Studio host UX/state wiring | RJ-3 | DNA selection/projection contract | yes |
| Durable SQLite/deployment | RJ-4 | no | yes |
| Resolver/fixture torture | DD M11 | yes | browser/runtime harness |
| Dual-host/application parity torture | RJ-5 | selected DNA cases | yes |
| Cutover/rollback | RJ-6 | state/theme continuity evidence | yes |
| Asset enrichment | DD M12 | eligible runtime assets | deployment/static asset behavior |

Dedup law: when one test genuinely proves both contracts, reference the same artifact from both ledgers rather than rerunning an identical test solely for governance aesthetics. Distinct contract dimensions still require distinct assertions.

---

# 10. MAINTENANCE-BUDGET RULES

Governor rejects architecture when any of these become systemic rather than exceptional:
- one new Python/host component per reference;
- one independent stylesheet/theme per reference;
- per-reference condition chains in resolver/renderer;
- repeated desktop/mobile definitions for the same mechanism;
- duplicate DNA engines per host;
- reference-specific DB schema/state;
- reference identity that fails without remote/local art assets;
- unexplained runtime heuristics/randomness;
- manual edits across many files to add one conforming reference.

Operational budget targets after M2:
- a normal new conforming reference should primarily add/update declarative DNA data plus tests/evidence;
- shared machinery changes require explicit justification and regression coverage;
- reference-specific code is exception-only and must document why existing mechanism vocabulary cannot express the canonical EQ3 contract;
- two similar exceptions trigger a shared-mechanism review;
- three or more similar exceptions are presumptive architecture debt and block scale-out until Governor review;
- host adapter should depend on projection vocabulary, not corpus size;
- runtime complexity and maintenance effort should scale mainly with mechanism/engine vocabulary, not linearly with 271 references.

No arbitrary LOC limit is locked before M0 implementation evidence exists. The structural budget above is the gate.

---

# 11. REPOSITORY PLACEMENT PLAN

Conceptual target only; exact filenames may change during M0 if repo conventions justify it.

```text
design_dna/
├── models/
│   ├── unit
│   ├── composition
│   ├── projection
│   └── provenance
├── registry/
│   ├── references
│   ├── engines
│   ├── primitives
│   └── fixtures
├── resolver/
│   ├── validation
│   ├── ownership
│   ├── dominance
│   ├── collision
│   └── resolve
├── projection/
│   ├── semantic_zones
│   ├── morphology
│   ├── typography
│   ├── motion
│   └── responsive
├── assets/
│   ├── registry
│   ├── eligibility
│   └── fallback
└── validation/
    └── contracts
```

Host-specific realization belongs with presentation/Reflex code, not inside canonical DNA models/resolver. Existing repository conventions should be reused rather than creating gratuitous package layers.

Canonical data format is intentionally NOT frozen here. M0 implementer may choose the simplest validated representation consistent with existing Python/tooling and low maintenance. Avoid introducing a new infrastructure dependency merely to store static DNA definitions.

Tests should mirror contract ownership: model/registry, resolver, projection, assets, integration/browser. Documentation/evidence ledgers remain under `docs/design-dna/`.

---

# 12. FINAL PRE-CODEX GATE CHECKLIST

All boxes required before M0 dispatch:

```text
[ ] RJ-1 is CLOSED / PASS / accepted and integrated into the exact M0 baseline.
[ ] RJ-2 is CLOSED / PASS / accepted and integrated into the exact M0 baseline.
[ ] Current repository HEAD/baseline SHA recorded.
[ ] No unresolved RJ-1/RJ-2 defect invalidates the generic application or Reflex host seam.
[ ] Design-DNA canonical documentation remains coherent at 271/271 EQ3.
[ ] DESIGN_DNA_MIGRATION_GATE_MASTER remains current.
[ ] This PRE_IMPLEMENTATION_PACK remains current.
[ ] M0 scope is runtime machinery only; M1+ not silently bundled.
[ ] Application/Core boundary remains host-neutral.
[ ] Reflex host seam is available without introducing a second backend.
[ ] Rollback/Streamlit compatibility remains preserved.
[ ] M0 acceptance matrix is attached to the implementation brief.
[ ] Exact test/evidence expectations are understood.
[ ] No production cutover is implied.
[ ] User/Governor explicitly authorizes [4] CODEX for M0.
```

Gate result semantics:
- any unchecked technical/governance prerequisite → HOLD;
- all prerequisites except explicit `[4]` → READY_FOR_CODEX / NOT_AUTHORIZED;
- all prerequisites + explicit `[4]` → CODEX_M0_AUTHORIZED;
- authorization applies to M0 only and ends at the mandatory STOP/report.

---

# PACKAGE CLOSURE

When accepted/persisted, the non-code Design-DNA preparation state becomes:

```text
RESEARCH = CLOSED
GLOBAL_EQ3 = 271/271
DOCUMENTATION CONSOLIDATION = CLOSED
MIGRATION PLANNING = CLOSED
M0 CONTRACT = FROZEN
BOUNDARY MAP = FROZEN
M0 ACCEPTANCE = FROZEN
M1 ACCEPTANCE CONTRACT = FROZEN
M2 PROVING PLAN = FROZEN
EQ4 EVIDENCE PROTOCOL = FROZEN
FAILURE/ROLLBACK LAW = FROZEN
CODEX M0 HANDOFF = PREPARED / NOT AUTHORIZED
RJ↔DNA SYNC = FROZEN
MAINTENANCE BUDGET = FROZEN
REPOSITORY PLACEMENT = PLANNED
PRE-CODEX CHECKLIST = FROZEN

DESIGN_DNA_IMPLEMENTATION = NOT_STARTED
EQ4 = 0/271
```

The remaining dependency before M0 is external execution progress: accepted/integrated RJ-1 and RJ-2, followed by explicit `[4] CODEX` authorization.
