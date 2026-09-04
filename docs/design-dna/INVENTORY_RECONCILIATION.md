# Design DNA — Inventory & Reconciliation Ledger

Status: ACTIVE INVENTORY. This ledger is intentionally conservative: a source is not deleted merely because a newer file exists.

## Confirmed authoritative anchors

| Surface | Current authority / anchor | Disposition |
|---|---|---|
| Global manifest | `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_9_MANIFEST_LICENSE_v1.md` + Batch 9 lock | AUTHORITATIVE_CURRENT |
| Global final state | Batch 9 lock checkpoint | AUTHORITATIVE_CURRENT |
| Temporal calibration | Global Calibration Batch 1 Temporal v1, accepted 34/34 | AUTHORITATIVE_CURRENT; duplicate copies observed |
| Material × Environment | Global Calibration Batch 2, 29/29 as inherited by later locks | AUTHORITATIVE_CURRENT; source artifact still to index explicitly |
| Track M_R | Global Calibration Batch 3 + lock; Track M_R full-pass lock | AUTHORITATIVE_CURRENT |
| Izzul | Global Calibration Batch 4 + lock; Wave E lock as research lineage | AUTHORITATIVE_CURRENT + SUPPORTING_HISTORY |
| Miko | Global Calibration Batch 5 + lock; Wave F lock as research lineage | AUTHORITATIVE_CURRENT + SUPPORTING_HISTORY |
| Cultural | Global Calibration Batch 6 + lock | AUTHORITATIVE_CURRENT |
| Country-Web | Global Calibration Batch 7 + lock | AUTHORITATIVE_CURRENT |
| Fixtures | Global Calibration Batch 8 + lock | AUTHORITATIVE_CURRENT |
| Migration organization | `MULTIMIND_DESIGN_DNA_MIGRATION_BATCH_MAP_v1.md` plus user-accepted lock checkpoint | AUTHORITATIVE_CURRENT operational packaging; NOT ontology change |
| Asset shipping law | Production-Web Asset Eligibility Amendment v1 | AUTHORITATIVE_GOVERNANCE |
| Final census sequencing | Final Global Residual Census Brief v1.1 and later accepted census/calibration | SUPPORTING / earlier stage |

## Confirmed historical / superseded examples

| Artifact / family | Why retained | Classification |
|---|---|---|
| Final Global Residual Census Brief v1 | Carries sequencing and census methodology but predates v1.1 asset clarification/final calibration | SUPERSEDED_TRACE / HISTORICAL_VALID |
| Final Global Residual Census v1 / v1-1 | Pre-calibration maturity/status ledger; useful for evolution, not current EQ3 state | SUPERSEDED_TRACE |
| Wave G v2 eight-country equalization | Records why Poland/Italy were demoted and why denominator changed; later Country-Web lock governs active 5 | HISTORICAL_VALID |
| Track M archival recovery v2 | Preserves failed archival routes and exact recovery barrier | HISTORICAL_VALID; mandatory cumulative inheritance |
| Track M_R v3 census checkpoint | Preserves Route-B denominator formation and six dispositions; later v6/global calibration governs maturity | HISTORICAL_VALID |
| Wave C/D branch briefs | Instructions/non-canon branch topology; useful audit trail | BRANCH_BRIEF / NON_CANONICAL |
| Track T activation checkpoint | Records activation boundary; later Track T locks govern current corpus | HISTORICAL_VALID |

## Duplicate hazards already observed

- Multiple File Library objects exist with the exact title `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_1_TEMPORAL_v1.md`.
- Multiple File Library objects exist with the exact title `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_9_MANIFEST_LICENSE_v1.md`.
- Duplicate filename alone is not enough to delete: compare content and timestamps; retain one canonical copy and record other file IDs as duplicate provenance.

## Current truth that supersedes older aggregates

```text
GLOBAL_DENOMINATOR = 271
REFERENCE = 160
ENGINE = 29
PRIMITIVE = 68
FIXTURE = 14
GLOBAL_EQ3_PASS = 271/271
GLOBAL_EQ3_RESIDUAL = 0
ASSET_APPLICABLE = 207
ASSET_NOT_APPLICABLE = 64
ASSET_FINAL_APPROVED = 0
DIRECT_IP_GATED = 75
MIGRATION_AUTHORIZED = NO
EQ4 = NOT_STARTED
```

The older asset aggregate 203/68 is superseded by accepted per-unit Batch 1–8 reconciliation. Historical artifacts carrying it remain traceable.

## Non-additive preservation requirements

Do not erase or accidentally add to denominator:

- TP19 / TP20 metadata / sequence-contract history.
- F11 historical negative/refusal fixture.
- Six historical Country-Web UNKNOWN slots.
- At least two historical Cultural UNKNOWN slots.
- Historical Track M unknown-cardinality barrier.
- Optional/nonblocking records from historical cultural/country work.
- Known routed records, including cultural/material/interaction-process routes.

Batch 9 records 35 explicit non-additive manifest records, minimum 8 unknown-not-recovered identity slots, 5 known routed records, 2 metadata records, 19 optional/nonblocking records, and one historical unknown-cardinality barrier. These categories overlap and are not a denominator equation.

## Dependency map

```text
GLOBAL GOVERNANCE
  ├─ Full-Pass / cumulative inheritance
  ├─ Canonical schema + 15 axes
  ├─ Resolver / Marriage Engine
  ├─ Reading Sanctuary + accessibility veto
  ├─ EQ3 implementation-ready law
  └─ Asset/license laws
        ↓
RESEARCH CORPORA / ENGINES / PRIMITIVES
        ↓
WAVE/TRACK CLOSURE LOCKS
        ↓
FINAL GLOBAL RESIDUAL CENSUS
        ↓
GLOBAL CALIBRATION B1–B8
        ↓
B9 MANIFEST/LICENSE RECONCILIATION
        ↓
271/271 MASTER STATE
        ↓
MIGRATION BATCH MAP
        ↓
DOCUMENTATION CONSOLIDATION (CURRENT)
        ↓
MIGRATION GATE REVIEW
        ↓ only after explicit authorization
REAL REFLEX MIGRATION → EQ4
```

## Zero-loss consolidation policy

Canonical docs may remove repetition but not unique information. Before an old source is relegated to archive, verify that every unique item belongs to at least one of:

1. current canonical statement;
2. historical decision/evolution ledger;
3. evidence/provenance ledger;
4. failure/dead-route/counterexample ledger;
5. explicit supersession record;
6. archive source pointer.

If none applies, the artifact remains `UNKNOWN_REQUIRES_RECONCILIATION` and must not be discarded.

## Remaining inventory work

This initial pass confirms the final arithmetic and major wave/track lineage, but is not yet a claim that every File Library artifact has been enumerated. Continue searching by family and exact artifact names, then build a complete source registry before any destructive deduplication or archival cleanup.
