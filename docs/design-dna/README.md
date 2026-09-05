# MultiMind Design DNA — Canonical Documentation Index

Status: RESEARCH CLOSED / DOCUMENTATION MERGED / MIGRATION PLANNING LOCKED
Date reconciled: 2026-09-05

This directory is the primary Design-DNA navigation surface for Governor, research and future implementation work.

Historical evidence is preserved in two explicitly different archive layers:

- `archive/raw/` — exact historical Markdown where the full source is retrievable.
- `archive/reconstructed-memory/` — clearly labeled non-verbatim surrogates where the full original is unavailable/truncated.

`RAW SOURCE != MEMORY SURROGATE != CURRENT CANON`.

## Current locked state

```text
GLOBAL_DENOMINATOR = 271
GLOBAL_EQ3 = 271 / 271 PASS
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
EQ4 = NOT_STARTED
```

Historical 273-era denominator records remain archived as superseded history.

## Documentation/archive state

```text
KNOWN_NAMED_SOURCE_CENSUS = COMPLETE
KNOWN_SOURCE_WITHOUT_DISPOSITION = 0
KNOWN_SOURCE_DISPOSITION_AUDIT = PASS
GLOBAL_CALIBRATION_ARTIFACT_FAMILIES = 9 / 9 DISPOSITIONED
CURRENTLY_DISCOVERED_CORPUS_ZERO_LOSS_AUDIT = PASS_WITH_EXPLICIT_RAW_EXACT_TEXT_EXCEPTIONS
DOCUMENTATION_CONTENT_ARCHIVE_BLOCKER = CLEARED
DOCUMENTATION_MERGE = COMPLETE
BRANCH_MERGED_TO_MAIN = YES
MIGRATION_PLANNING_GATE = PASS
DESIGN_DNA_IMPLEMENTATION = NOT_STARTED
MIGRATION_AUTHORIZED = NO
```

A surrogate-only source remains explicitly `RAW_EXACT_TEXT_UNAVAILABLE`; archival closure does not pretend otherwise.

## Governor / implementer read order — current truth first

Do not replay historical Markdown to infer current truth.

1. `governance/CANONICAL_CONSTITUTION.md` — current global laws, resolver, accessibility, Reading Sanctuary, provenance and safety.
2. `corpora/CORPUS_INDEX.md` — current corpus membership/grouping and additive/non-additive boundaries.
3. `calibration/GLOBAL_CALIBRATION_LEDGER.md` — current 271/271 arithmetic and batch state.
4. `calibration/GLOBAL_EQ3_CLOSURE.md` — exact meaning of current EQ3 closure.
5. `migration/DESIGN_DNA_MIGRATION_GATE_MASTER.md` — accepted migration-gate architecture and release condition.
6. `migration/DESIGN_DNA_PRE_IMPLEMENTATION_PACK.md` — M0/M1/M2 contracts, EQ4 protocol, failure law, synchronization and pre-Codex gate.
7. `migration/MIGRATION_BATCH_MAP.md` — dependency-oriented M0–M12 packaging; not authorization.
8. `TIMELINE_INDEX.md` — chronological lineage and final/current authority map.
9. `archive/RAW_SOURCE_MANIFEST_v2.md` — raw/surrogate/source-ID/duplicate disposition.
10. `archive/SOURCE_CENSUS_LEDGER_v1.md` — family-by-family source census.
11. `ZERO_LOSS_AUDIT.md` — archival closure and exact-text exception state.

Before Codex/M0 authorization, also read the current Reflex production migration master and verify the actual accepted/integrated RJ state in the repository. Design-DNA documents do not self-certify RJ completion.

Historical raw/surrogate files are supporting evidence only. Use them for provenance, failed-route knowledge, supersession history, contradiction review or a detail deliberately not duplicated in current canonical contracts.

## Timeline model

Every Design-DNA Markdown belongs to a chronology. `TIMELINE_INDEX.md` maps research history to current authority.

Status vocabulary includes:
- `FINAL_CURRENT`
- `MASTER_LOCK`
- `AUTHORITATIVE_SUPPORTING`
- `HISTORICAL_VALID`
- `SUPERSEDED_HISTORICAL`
- `BRANCH_BRIEF`
- `RAW_ARCHIVED_VERIFIED`
- `RAW_MIRRORED_PRESENT`
- `MEMORY_RECONSTRUCTED_SURROGATE`
- `DUPLICATE_CANDIDATE`
- `VARIANT_VERIFIED_DISTINCT`
- `SOURCE_NOT_YET_DISCOVERED`

## Source precedence

1. Current authoritative production repository/files where implementation facts are involved.
2. Latest explicit user/HQ decision.
3. Latest accepted MASTER LOCK/checkpoint.
4. Latest accepted research/calibration artifact.
5. Older artifacts for cumulative research and historical reconciliation.
6. Memory reconstruction only as historical recovery evidence where exact text is unavailable.

Memory surrogates never outrank exact current locks/canonical docs.

## Corpus arithmetic

REFERENCE:
`Cultural55 + Country-Web5 + Track M_R25 + Izzul36 + Miko23 + Track T-I16 = 160`

ENGINE:
`Material M1–M15 + Environment E1–E14 = 29`

PRIMITIVE:
`P01–P25 + MK01–MK25 + TP01–TP18 = 68`

FIXTURE:
`F01–F10 + F12–F15 = 14`

`160 + 29 + 68 + 14 = 271`.

TP19/TP20 are non-additive metadata/history. F11 is historical non-additive. Historical Track M remains an unknown-cardinality archival barrier.

## Global Calibration chronology

```text
Batch 1 Temporal               34 / 34
Batch 2 Material×Environment   29 / 29
Batch 3 Track M_R              25 / 25
Batch 4 P + Izzul              61 / 61
Batch 5 MK + Miko              48 / 48
Batch 6 Cultural               55 / 55
Batch 7 Country-Web             5 / 5
Batch 8 Fixtures               14 / 14
Batch 9 Manifest/License       non-additive reconciliation
--------------------------------------
GLOBAL EQ3                    271 / 271
```

The giant Batch1–9 artifact tables are currently represented by clearly marked memory surrogates because full File Library retrieval truncates them. Exact Batch2–9 lock/checkpoints are in the raw archive. Batch1 accepted lock state is preserved by a non-verbatim lock-state surrogate because an exact standalone Batch1 lock MD was not recovered.

## Permanent firewalls

- `HISTORICAL TRACK M != TRACK_M_R != M1–M15`.
- `REFERENCE != ENGINE != PRIMITIVE != FIXTURE != ASSET`.
- `SHARED PRIMITIVE != DUPLICATE REFERENCE`.
- `COUNTRY-WEB LINEAGE != CULTURAL LINEAGE`.
- `ASSET-OFF SURVIVAL = resilience floor, not fidelity ceiling`.
- `FREE / PERSONAL-USE / UNKNOWN RIGHTS != PRODUCTION_WEB_ELIGIBLE`.
- `EQ3 != implementation`.
- `EQ4 = real-host runtime/browser/acceptance evidence`.
- `271 calibrated units != 271 user-facing theme buttons`.
- `CALIBRATION BATCH != MIGRATION BATCH`.

## Archive model

### Canonical contracts
What is true/current now.

### Timeline
How the current state was reached and what superseded what.

### Raw archive
Exact recoverable historical source evidence.

### Reconstructed-memory archive
Non-verbatim source-level recovery when exact text cannot currently be retrieved.

For a truncated source:
`SURROGATE ACCOUNTED != RAW VERBATIM RECOVERED`.

If exact source access appears later, mirror it raw and mark the surrogate as superseded-by-raw-recovery for source-evidence purposes; do not delete the recovery history.

## Migration boundary

Documentation consolidation is merged. Migration planning and the non-code pre-implementation package are locked separately from implementation authorization.

Current sequence:

```text
RESEARCH / EQ3 CLOSURE
→ DOCUMENTATION CONSOLIDATION + MERGE
→ MIGRATION GATE / PRE-IMPLEMENTATION LOCK
→ RJ-1 CLOSED + INTEGRATED
→ RJ-2 CLOSED + ACCEPTED
→ EXPLICIT [4] CODEX AUTHORIZATION
→ DESIGN-DNA M0
→ M1–M12 UNDER SERIAL GOVERNANCE
→ EQ4 EVIDENCE
```

Current safety state:

```text
DOCUMENTATION_MERGE = COMPLETE
BRANCH_MERGED_TO_MAIN = YES
MIGRATION_PLANNING_GATE = PASS
PRE_IMPLEMENTATION_PACKAGE = PREPARED
DESIGN_DNA_IMPLEMENTATION = NOT_STARTED
CODEX_DESIGN_DNA_AUTHORIZED = NO
MIGRATION_AUTHORIZED = NO
PRODUCTION_MODIFIED_BY_DESIGN_DNA = NO
EQ4 = NOT_STARTED
```

Unknown historical artifacts that surface later are handled as condition-driven archival recovery, not as an infinite unnamed blocker.