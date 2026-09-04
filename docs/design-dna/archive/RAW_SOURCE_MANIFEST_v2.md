# MULTIMIND DESIGN DNA — RAW SOURCE MANIFEST v2

STATUS: KNOWN-SOURCE DISPOSITION RECONCILED — EXACT RAW RECOVERY REMAINS OPEN WHERE ORIGINAL TEXT IS UNAVAILABLE
DATE: 2026-09-04
BRANCH: `docs/design-dna-consolidation`
SUPERSEDES FOR OPERATIONAL TRACKING: `RAW_SOURCE_MANIFEST.md` v1

# 0. GOVERNING LAW

`ALL WORDS FROM ALL RECOVERABLE HISTORICAL DESIGN-DNA MARKDOWN ARTIFACTS MUST BE PRESERVED IN GITHUB.`

`SEMANTIC CONSOLIDATION != VERBATIM ARCHIVE COMPLETION`

`RAW VERBATIM SOURCE != MEMORY RECONSTRUCTION`

`RAW FILE PRESENT != SOURCE VERIFIED`

`DUPLICATE CANDIDATE != DUPLICATE VERIFIED`

`SAME TITLE != SAME CONTENT`

`SUPERSEDED != DELETE`

`TRUNCATED RETRIEVAL != FULL SOURCE`

For every known source the disposition order is now:

```text
FULL RETRIEVABLE
→ RAW MIRROR
→ FETCH-BACK / SOURCE COMPARISON WHEN AVAILABLE

TRUNCATED / FULL TEXT UNAVAILABLE
→ USE SURVIVING SOURCE + CUMULATIVE PROJECT MEMORY
→ MEMORY_RECONSTRUCTED_SURROGATE
→ NEVER CLAIM VERBATIM RECOVERY

NO SAFE MEMORY / EVIDENCE
→ RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS
```

# 1. STATUS ENUMS

- `RAW_ARCHIVED_VERIFIED` — complete source retrieved and GitHub copy compared as matching.
- `RAW_MIRRORED_PRESENT` — exact raw source was written to GitHub, but this manifest does not claim a fresh comparison in the current reconciliation pass.
- `RAW_ARCHIVED_AWAITING_VERIFICATION` — raw mirror exists but explicit source↔GitHub verification remains to be recorded.
- `MEMORY_RECONSTRUCTED_SURROGATE` — original source is truncated/unavailable; a clearly marked non-verbatim surrogate preserves recoverable decisions, counters, chronology and governance meaning.
- `RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS` — source exists but neither complete text nor sufficiently safe reconstruction is available.
- `SOURCE_NOT_YET_DISCOVERED` — lineage indicates a possible historical source but no exact source identity is recoverable.
- `DUPLICATE_CANDIDATE` — multiple source objects appear related but full-content equality has not been proven.
- `DUPLICATE_VERIFIED` — full-content identity proven.
- `VARIANT_VERIFIED_DISTINCT` — same/similar title proven materially distinct; preserve separately.
- `SUPERSEDED_HISTORICAL` — historical state superseded by later accepted state but retained.
- `SUPERSEDED_BY_RAW_RECOVERY` — a reconstruction surrogate remains as recovery history after exact raw source is later recovered.

# 2. BRANCH ARCHIVE INVENTORY AFTER RECONCILIATION

A recursive GitHub tree audit on this branch records:

```text
RAW_FILES_PRESENT_IN_ARCHIVE_RAW = 56
MEMORY_RECONSTRUCTED_SOURCE_RECORDS = 61
MEMORY_SURROGATE_POLICY_FILES = 1
GLOBAL_CALIBRATION_ARTIFACT_FAMILIES_DISPOSITIONED = 9 / 9
GLOBAL_CALIBRATION_LOCK_STATES_DISPOSITIONED = 9 / 9
```

Important: `56 raw files present` is a repository inventory count, NOT a claim that every one of the 56 has been re-verified against its original source during this single pass. The original verified baseline of 36 remains valid; subsequent exact raw mirrors are present and retain their individual audit trail.

The source-disposition count is intentionally separate from the raw-file count because a single historical source family may have multiple File Library IDs, duplicate candidates, raw variants, or a non-verbatim recovery surrogate.

# 3. GLOBAL CALIBRATION BATCH 1–9 — FINAL SOURCE DISPOSITION

The requested giant calibration artifacts are all now dispositioned. All nine artifact sources are too large/truncated for a defensible verbatim mirror through current retrieval, so each has a dedicated non-verbatim recovery surrogate. No table tail was invented.

| Batch | Giant artifact | Source identity / duplicate state | Durable disposition | Accepted lock state |
|---|---|---|---|---|
| B1 | `GLOBAL_CALIBRATION_BATCH_1_TEMPORAL_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | `reconstructed-memory/...BATCH_1_TEMPORAL_v1__MEMORY_RECONSTRUCTION.md` | exact standalone lock MD not recovered; accepted state preserved in `...BATCH_1_LOCK_STATE__MEMORY_RECONSTRUCTION.md` |
| B2 | `...BATCH_2_MATERIAL_ENVIRONMENT_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-2 lock present |
| B3 | `...BATCH_3_TRACK_M_R_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-3 lock present |
| B4 | `...BATCH_4_IZZUL_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-4 lock present |
| B5 | `...BATCH_5_MIKO_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-5 lock present |
| B6 | `...BATCH_6_CULTURAL_v1` | at least two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-6 lock present |
| B7 | `...BATCH_7_COUNTRY_WEB_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-7 lock present |
| B8 | `...BATCH_8_FIXTURES_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-8 lock present |
| B9 | `...BATCH_9_MANIFEST_LICENSE_v1` | two same-title IDs; `DUPLICATE_CANDIDATE` | memory surrogate | exact raw Batch-9 lock present |

## 3.1 Batch arithmetic preserved

```text
B1 TEMPORAL               = 34 / 34
B2 MATERIAL × ENVIRONMENT = 29 / 29
B3 TRACK_M_R              = 25 / 25
B4 P + IZZUL              = 61 / 61
B5 MK + MIKO              = 48 / 48
B6 CULTURAL               = 55 / 55
B7 COUNTRY-WEB            = 5 / 5
B8 FIXTURES               = 14 / 14
B9 MANIFEST/LICENSE       = NON-ADDITIVE RECONCILIATION

GLOBAL_EQ3                = 271 / 271
GLOBAL_EQ3_RESIDUAL       = 0
RESEARCH_REOPEN           = 0
```

Batch 9 final manifest invariants remain:

```text
REFERENCE = 160
ENGINE = 29
PRIMITIVE = 68
FIXTURE = 14
TOTAL = 271

ASSET_APPLICABLE = 207
ASSET_NOT_APPLICABLE = 64
ASSET_FINAL_APPROVED = 0
DIRECT_IP_GATED = 75
```

# 4. PREVIOUS HIGH-PRIORITY JUMBO DEBT — DISPOSITION RECONCILED

The earlier P0/P1/P2 lists are no longer vague active TODOs. The named source families below have durable dispositions.

## Final Census 273 → 271 lineage

- historical `FINAL_GLOBAL_RESIDUAL_CENSUS_v1` 273 state → `MEMORY_RECONSTRUCTED_SURROGATE + SUPERSEDED_HISTORICAL`.
- `FINAL_GLOBAL_RESIDUAL_CENSUS_v1-1` → `MEMORY_RECONSTRUCTED_SURROGATE + DUPLICATE_CANDIDATE + SUPERSEDED_HISTORICAL`.
- `FINAL_GLOBAL_RESIDUAL_CENSUS_v1_1_HQ_PATCHED` multi-ID family → `MEMORY_RECONSTRUCTED_SURROGATE + DUPLICATE_CANDIDATE`.
- `HQ_PATCHED-2` → separate `MEMORY_RECONSTRUCTED_SURROGATE + DUPLICATE_CANDIDATE` until relation is proven.

The old 273 denominator is retained as historical truth; it is not rewritten into 271.

## Wave / Track jumbo results

Durable memory surrogates now exist for the formerly blocking jumbo result families across:

- Wave E v1/v2/v3 and v6 final result lineage;
- Wave F v1/v2/v3/v4 result lineage;
- Wave G v1/v2/v3 result lineage;
- Wave H v1/v2 result lineage;
- Historical Track M v1/v2;
- Track M_R v3/v4/v5/v6;
- Track T dual-lane census v1, T-I v2 result, T-I v3 hardening;
- B1–B10 / recovery-ledger / Wave-B / Wave-C historical sources where exact full source remains unavailable;
- Canonical Master Index historical source;
- Global Calibration Batch1–9 giant artifacts.

Where exact raw Markdown is present, it remains the higher-fidelity archive source. Where only a surrogate exists, the surrogate is explicitly non-verbatim and does not satisfy byte/text-exact recovery of the original.

# 5. DUPLICATE / VARIANT RECONCILIATION

## Wave G lock variants — resolved distinct

Three Wave-G lock source objects were compared sufficiently and remain:

`VARIANT_VERIFIED_DISTINCT`

Safe dedup = NO.

## Calibration artifacts — unresolved duplicates, but no longer undispositioned

Batch1–9 same-title multi-ID families remain `DUPLICATE_CANDIDATE` because retrieval does not provide a complete byte/text comparison. They are nevertheless fully accounted in the source census through one family surrogate plus all known source IDs.

This means:

`DUPLICATE_RELATION_UNRESOLVED != SOURCE_UNACCOUNTED`

No candidate pair is silently collapsed.

# 6. KNOWN-SOURCE DISPOSITION CLOSURE

For the source families explicitly enumerated by the current archive program — Foundation/B-series, Wave E/F/G/H, Historical Track M, Track M_R, Track T, Final Census lineage, and Global Calibration Batch1–9 — every known source now has one of the following durable states:

```text
RAW_ARCHIVED_VERIFIED / RAW_MIRRORED_PRESENT
MEMORY_RECONSTRUCTED_SURROGATE
DUPLICATE_CANDIDATE + one of the above
VARIANT_VERIFIED_DISTINCT
SUPERSEDED_HISTORICAL + one of the above
SOURCE_NOT_YET_DISCOVERED
RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS
```

Therefore:

```text
KNOWN_SOURCE_DISPOSITION_TRANCHE = PASS
KNOWN_CALIBRATION_SOURCE_DISPOSITION = 9 / 9 PASS
KNOWN_FINAL_CENSUS_LINEAGE_DISPOSITION = PASS
KNOWN_WAVE_TRACK_JUMBO_DISPOSITION = PASS
```

This closes the previously open *known-source limbo*.

It does NOT assert that an unrecovered original has magically become verbatim. It also does not prove that no entirely unknown historical MD can ever surface later.

# 7. REMAINING TRUE ARCHIVAL UNCERTAINTY

Only two kinds of uncertainty remain legitimate:

1. **exact-text recovery uncertainty** — a known source is represented by a memory surrogate because current retrieval truncates the original;
2. **historical-discovery uncertainty** — a source is only lineage-implied or completely unknown and therefore remains `SOURCE_NOT_YET_DISCOVERED` rather than fabricated.

Neither category may mutate current canonical Design-DNA truth.

A newly recovered exact original must be mirrored raw and may supersede the corresponding surrogate as source evidence.

# 8. IMPLEMENTATION / MIGRATION BOUNDARY

Current implementation truth remains in the canonical layer, not in memory surrogates:

- `governance/CANONICAL_CONSTITUTION.md`
- `corpora/CORPUS_INDEX.md`
- `calibration/GLOBAL_CALIBRATION_LEDGER.md`
- `calibration/GLOBAL_EQ3_CLOSURE.md`
- `migration/MIGRATION_BATCH_MAP.md`
- `TIMELINE_INDEX.md`

```text
CANONICAL_SEMANTIC_CONSOLIDATION = PASS
KNOWN_SOURCE_DISPOSITION = PASS
GLOBAL_EQ3 = 271 / 271
MIGRATION_AUTHORIZED = NO
PRODUCTION_MODIFIED = NO
EQ4_PERFORMED = NO
```

Documentation exact-text limitations remain explicitly auditable; they are not permission to invent missing DNA.