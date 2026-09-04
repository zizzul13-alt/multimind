# MultiMind Design DNA — Documentation Consolidation Protocol

Status: GOVERNOR MASTER RULE — ACTIVE / KNOWN-SOURCE DISPOSITION CLOSED
Date: 2026-09-04

## Decision

The Design DNA corpus is consolidated into the MultiMind GitHub repository as a modular, navigable knowledge base rather than depending on unordered chat-local Markdown or one lossy monolithic summary.

Working branch:

`docs/design-dna-consolidation`

Target root:

`docs/design-dna/`

Documentation consolidation is separate from production migration. No Codex/production work is authorized merely because archival closure is achieved.

## Objective

Preserve all recoverable historical Design-DNA detail while making current truth easy to navigate.

Hard law:

`NO DETAIL LOSS BY CLEANUP`

Cleanup means classification, indexing, reconciliation, modularization and explicit supersession. It does not mean deleting inconvenient history.

## Three-layer preservation model

### Layer A — Canonical current truth

Current governance, corpus membership, calibration state and migration packaging.

Primary files:
- `README.md`
- `governance/CANONICAL_CONSTITUTION.md`
- `corpora/CORPUS_INDEX.md`
- `calibration/GLOBAL_CALIBRATION_LEDGER.md`
- `calibration/GLOBAL_EQ3_CLOSURE.md`
- `migration/MIGRATION_BATCH_MAP.md`
- `TIMELINE_INDEX.md`

### Layer B — Raw historical archive

`archive/raw/`

Exact source text where the complete original is retrievable. Raw files are never rewritten to look current.

### Layer C — Memory-reconstructed archive

`archive/reconstructed-memory/`

Explicitly non-verbatim surrogates for historical sources whose full original text is unavailable/truncated.

Hard distinction:

`RAW VERBATIM SOURCE != MEMORY RECONSTRUCTION != CURRENT CANON`

A memory surrogate preserves only safely recoverable decisions, counters, relationships, chronology and governance meaning. It never claims to reproduce missing original prose.

## Required source-disposition workflow

```text
DISCOVER
→ INVENTORY
→ CLASSIFY
→ TRY FULL RETRIEVAL

IF FULL:
  RAW MIRROR
  → VERIFY WHEN POSSIBLE

IF TRUNCATED:
  CHECK SURVIVING SOURCE + CUMULATIVE PROJECT MEMORY
  → MEMORY_RECONSTRUCTED_SURROGATE

IF MEMORY/EVIDENCE INSUFFICIENT:
  RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS

THEN:
  RECONCILE
  → CROSS-LINK
  → TIMELINE
  → ZERO-LOSS AUDIT
```

## Source precedence

1. Current authoritative repository/files for implementation facts.
2. Latest explicit user/HQ decision.
3. Latest accepted MASTER LOCK/checkpoint.
4. Latest accepted research/calibration artifact.
5. Older artifacts as cumulative history.
6. Memory reconstruction only for historical recovery where exact source is unavailable.

A memory surrogate never outranks a later exact source or current canon.

## Duplicate rule

Same filename is not sufficient evidence of duplication.

- equality proven → `DUPLICATE_VERIFIED`;
- difference proven → `VARIANT_VERIFIED_DISTINCT`;
- full comparison unavailable → `DUPLICATE_CANDIDATE` and preserve all known source identities.

`DUPLICATE_CANDIDATE != SOURCE_UNACCOUNTED`.

Do not delete a candidate merely to make the manifest cleaner.

## Supersession rule

A later accepted state may supersede status, denominator or interpretation without deleting the historical artifact.

Canonical example:

`273 historical denominator → HQ-corrected 271 → Global Calibration 271/271`.

All states remain historically traceable; only 271 is current implementation truth.

## Cumulative research inheritance

Failed methods, dead routes, false positives, evidence traps, negative fixtures, acquisition lessons, reformulations and historical barriers remain project knowledge.

A failed research route is not documentation garbage.

## Current closure anchor

Accepted current state:

```text
GLOBAL_DENOMINATOR = 271
GLOBAL_EQ3 = 271 / 271
REFERENCE = 160
ENGINE = 29
PRIMITIVE = 68
FIXTURE = 14
MANIFEST_RESIDUAL = 0
RESEARCH_REOPEN = 0
ASSET_APPLICABLE = 207
ASSET_NOT_APPLICABLE = 64
ASSET_FINAL_APPROVED = 0
DIRECT_IP_GATED = 75
MIGRATION_AUTHORIZED = NO
PRODUCTION_MIGRATION_PERFORMED = NO
EQ4 = NOT_STARTED
```

## Current archival closure state

The known named/source-known Design-DNA corpus now has a durable disposition.

```text
KNOWN_NAMED_SOURCE_CENSUS = COMPLETE
KNOWN_SOURCE_WITHOUT_DISPOSITION = 0
KNOWN_SOURCE_DISPOSITION_AUDIT = PASS
GLOBAL_CALIBRATION_ARTIFACT_FAMILIES = 9 / 9 DISPOSITIONED
CURRENTLY_DISCOVERED_CORPUS_ZERO_LOSS_AUDIT = PASS_WITH_EXPLICIT_RAW_EXACT_TEXT_EXCEPTIONS
```

Unknown historical artifacts that may surface later are handled as condition-driven archival recovery. They are not an infinite unnamed blocker.

## Git / merge policy

Consolidation remains on its dedicated documentation branch until the user/Governor explicitly merges it.

The existing production `docs/design_dna.md` is not silently overwritten by consolidation.

Current state:

```text
BRANCH = docs/design-dna-consolidation
BRANCH_MERGED_TO_MAIN = NO
DOCUMENTATION_CONTENT_ARCHIVE_BLOCKER = CLEARED
```

A merge is now a separate user/Governor action, not an archival-research task.

## Migration firewall

Documentation closure is NOT migration authorization.

Required order:

`DOCUMENTATION CLOSURE → USER/GOVERNOR ACCEPTANCE + MERGE → MIGRATION GATE REVIEW → SEPARATE AUTHORIZATION → IMPLEMENTATION → EQ4`

No Design-DNA runtime migration, Reflex production work or EQ4 claim follows automatically from this protocol.

## Future-chat operating rule

Future sessions begin at `docs/design-dna/README.md` and load only the relevant current canonical documents.

Use `TIMELINE_INDEX.md` for chronology.
Use `archive/RAW_SOURCE_MANIFEST_v2.md` + `SOURCE_CENSUS_LEDGER_v1.md` for source status.
Use raw/surrogate historical files only when provenance, contradiction, cumulative research or forensic detail requires them.

This removes dependence on giant chat context without pretending historical source loss never occurred.