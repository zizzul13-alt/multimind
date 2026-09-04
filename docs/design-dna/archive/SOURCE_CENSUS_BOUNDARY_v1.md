# MultiMind Design DNA — Source Census Boundary v1

STATUS: ACTIVE FORENSIC CENSUS BOUNDARY
DATE: 2026-09-04
BRANCH: `docs/design-dna-consolidation`
PURPOSE: define exactly what counts toward the Design-DNA Markdown archival census, what does not, and how each discovered source is dispositioned.

## 0. Core objective

The archival program is not a new research wave.

The job is:

`DISCOVER DESIGN-DNA MD → CLASSIFY → FULL-READ IF POSSIBLE → RAW-MIRROR VERBATIM → VERIFY → TIMELINE → FINAL/CURRENT POINTER`

If full retrieval is impossible after reasonable retries:

`PENDING_FULL_SOURCE_ACCESS`

No missing tail may be reconstructed from chat memory, summaries, or later artifacts.

## 1. Mandatory in-scope Markdown

A Markdown artifact is mandatory archival census scope when at least one is true:

1. its filename is in the `MULTIMIND_DESIGN_DNA_*` family;
2. its own contents explicitly declare Design-DNA research/governance/calibration/migration-documentation scope;
3. it is a Design-DNA brief, result, checkpoint, lock, amendment, census, equalization report, recovery ledger, gap ledger, canonical index, handoff checkpoint, calibration artifact, calibration lock, migration map, source manifest, timeline index, supersession ledger, or zero-loss audit;
4. it records a historical Design-DNA state later superseded by another Design-DNA artifact;
5. it is a same-title or near-title historical copy/variant that may contain materially different wording.

This includes unsuccessful and intermediate research. Failure/hold/superseded material is history, not trash.

## 2. Supporting-source Markdown — indexed but not automatically raw-canon

A Markdown file that is not itself a Design-DNA artifact but was used as evidence/input is classified `SUPPORTING_SOURCE`.

Examples include owner taste/checklist documents, source notes, general research notes, or project documents whose primary purpose is outside Design DNA but which supplied evidence to a Design-DNA census.

Supporting sources are referenced from provenance/timeline where needed. They do not automatically enter the mandatory verbatim Design-DNA raw mirror unless they themselves contain Design-DNA governance or canonical decisions.

This boundary prevents the archive from expanding into every source document ever cited by Design DNA.

## 3. Out of scope for this Markdown census

Not part of the mandatory MD denominator:

- production source code;
- security/QA/UI/UX/platform architecture documents with no Design-DNA governance role;
- Reflex integration-proof documentation unless it explicitly amends Design-DNA law;
- images, screenshots, PDFs, CSVs, diffs, binary assets, or code exports;
- web pages and external evidence sources;
- ordinary chat prose that was never made a durable Markdown artifact.

These may be separately indexed as `SUPPORTING_NON_MD` if historically useful, but they do not block the Markdown census.

## 4. Temporal boundary

The census begins at the earliest recoverable Design-DNA Markdown artifact in File Library / durable project history and continues through the latest Design-DNA documentation-consolidation artifact on `docs/design-dna-consolidation`.

The current known historical surface begins no later than the Recovery-Ledger/B-series era on 2026-09-01 and continues through Global Calibration, Migration Batch Map, and documentation consolidation on 2026-09-04.

Upload/CreatedAt metadata is a secondary ordering signal only. Preferred chronology:

1. explicit DATE inside artifact;
2. explicit version / predecessor / supersedes relationship;
3. program sequence (B-series → Waves/Tracks → Final Census → Global Calibration → Migration documentation → consolidation);
4. File Library CreatedAt/ModifiedAt only as tie-breaker.

## 5. Required per-source disposition

Every discovered in-scope MD must end in one primary archive state:

- `RAW_ARCHIVED_VERIFIED`
- `RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS`
- `DUPLICATE_VERIFIED`
- `VARIANT_VERIFIED_DISTINCT`
- `SUPERSEDED_HISTORICAL` combined with one retrieval state
- `SOURCE_NOT_YET_DISCOVERED` only when lineage proves an expected artifact but exact source cannot yet be found

No source may remain merely “TODO”.

## 6. Final/current authority labels

Separately from archive state, every in-scope MD receives a timeline authority label:

- `FINAL_CURRENT`
- `MASTER_LOCK`
- `AUTHORITATIVE_SUPPORTING`
- `HISTORICAL_VALID`
- `SUPERSEDED_HISTORICAL`
- `BRANCH_BRIEF`
- `NON_CANONICAL_SUPPORTING`

Archive state answers “did we preserve it?”
Authority state answers “should Codex implement from it?”

These are intentionally separate.

## 7. Current census families

The exhaustive census must search and reconcile at minimum:

### Foundation / recovery / B-series
- Recovery Ledger revisions
- Canonical Master Index
- Unresolved Gap Ledger
- Chat Handoff / durability checkpoints
- B1–B10 artifacts and lock/checkpoint variants

### Wave series
- Wave B
- Wave C
- Wave D
- Wave E
- Wave F
- Wave G
- Wave H

For every wave include briefs, results, continuation briefs, HQ stress tests, acceptance checkpoints and final locks where they exist.

### Material tracks
- historical Track M recovery chain
- Track M_R reconstructed census / EQ2 / EQ3 / final-seven / locks

### Music / Temporal
- Track T activation
- dual-lane governance/census
- membership master if Design-DNA-authored
- T-I equalization/hardening/results/locks
- temporal primitive reconciliation

### Global closure
- Final Global Residual Census brief/result variants
- 273-era historical state
- 271 HQ-patched state and copy/variant families

### Global Calibration
- Batch 1–9 briefs/artifacts/results
- Batch 1–9 lock checkpoints
- duplicate/copy variants

### Documentation / migration-facing Design DNA
- Global EQ3 amendments
- asset/provenance/license amendments
- Migration Batch Map
- canonical documentation index
- Timeline Index
- Raw Source Manifest
- Historical Supersession Ledger
- Zero-Loss Audit
- documentation consolidation protocol/checkpoints

## 8. Newly surfaced census targets from the current deep pass

The current File-Library sweep has confirmed additional in-scope artifacts beyond the previously verified raw set, including:

- `MULTIMIND_DESIGN_DNA_B1_TIER_S_v1.md`
- `MULTIMIND_DESIGN_DNA_B10_GLOBAL_EQUALIZATION_v1.md`
- `MULTIMIND_DESIGN_DNA_CHAT_HANDOFF_CHECKPOINT_v1.md`
- `MULTIMIND_DESIGN_DNA_RECOVERY_LEDGER_v4.md`
- `MULTIMIND_DESIGN_DNA_RECOVERY_LEDGER_v6.md`
- `MULTIMIND_DESIGN_DNA_RECOVERY_LEDGER_v7.md`
- `MULTIMIND_DESIGN_DNA_WAVE_D_EXPRESSIVE_TENSION_DEEP_v1.md`
- `MULTIMIND_DESIGN_DNA_WAVE_E_IZZUL_CORPUS_EQUALIZATION_v1.md`
- `MULTIMIND_DESIGN_DNA_WAVE_E_CONTINUATION_BRIEF_v2.md`
- `MULTIMIND_DESIGN_DNA_WAVE_F_MIKO_RESIDUAL_EQUALIZATION_v2.md`
- `MULTIMIND_DESIGN_DNA_WAVE_G_FULL_RESIDUAL_CENSUS_EQUALIZATION_v1.md`
- `MULTIMIND_DESIGN_DNA_WAVE_H_GLOBAL_RECOVERY_EVIDENCE_HOLD_CENSUS_v1.md`
- `MULTIMIND_DESIGN_DNA_TRACK_M_HISTORICAL_NAMED_MATERIAL_CORPUS_RECOVERY_v1.md`
- `MULTIMIND_DESIGN_DNA_TRACK_M_ARCHIVAL_RECOVERY_FORENSICS_v2.md`
- `MULTIMIND_DESIGN_DNA_TRACK_T_DUAL_LANE_CORPUS_ONTOLOGY_CENSUS_v1.md`
- `MULTIMIND_DESIGN_DNA_FINAL_GLOBAL_RESIDUAL_CENSUS_v1-1.md`
- `MULTIMIND_DESIGN_DNA_FINAL_GLOBAL_RESIDUAL_CENSUS_v1_1_HQ_PATCHED.md` (multiple File Library IDs)
- `MULTIMIND_DESIGN_DNA_FINAL_GLOBAL_RESIDUAL_CENSUS_v1_1_HQ_PATCHED-2.md`
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_1_TEMPORAL_v1.md` (multiple File Library IDs)
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_4_IZZUL_v1.md`
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_4_LOCK_CHECKPOINT_v1.md`
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_6_CULTURAL_v1.md`
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_7_COUNTRY_WEB_v1.md`
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_8_FIXTURES_v1.md` (multiple File Library IDs)
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_8_LOCK_CHECKPOINT_v1.md`
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_9_MANIFEST_LICENSE_v1.md` (multiple File Library IDs)
- `MULTIMIND_DESIGN_DNA_GLOBAL_CALIBRATION_BATCH_9_LOCK_CHECKPOINT_v1.md`
- `MULTIMIND_DESIGN_DNA_MIGRATION_BATCH_MAP_v1.md`

This list is a working census expansion, NOT the final denominator.

## 9. Retrieval observations from current pass

Current full-read attempts demonstrate three distinct cases:

1. source can be fully retrieved → raw mirror immediately;
2. source is found but mclick truncates because of size → mark `RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS`; do not reconstruct;
3. multiple File Library IDs expose same title → retain `DUPLICATE_CANDIDATE` until full comparison proves identical or distinct.

Examples currently observed as large/truncated include B1 Tier-S, Wave D deep result and Wave E v1 equalization. Their existence and lineage are census-closed; exact raw archival recovery remains pending until full source access succeeds.

## 10. Census exhaustion criterion

The source census is considered exhausted only after independent searches have been run across:

- exact known filenames;
- family prefixes;
- version numbers;
- brief/result/lock/checkpoint synonyms;
- recovery/ledger/index terms;
- wave/track names;
- calibration batch numbers;
- superseded/current denominator terms;
- duplicate same-title identities.

Two or more failed search formulations are required before an expected lineage artifact is marked `SOURCE_NOT_YET_DISCOVERED`.

A truncated artifact is not “undiscovered”; it is `PENDING_FULL_SOURCE_ACCESS`.

## 11. Finish line

The Markdown census does NOT require every jumbo file to become retrievable.

It requires every discoverable in-scope Design-DNA Markdown to have an explicit disposition.

Closure condition:

`EVERY DISCOVERED MD HAS ARCHIVE STATE + TIMELINE POSITION + AUTHORITY LABEL`

and every lineage-implied but undiscovered MD is explicitly recorded.

Only then may the final zero-loss audit decide whether unresolved full-source access is an accepted documented archival limitation or a remaining blocker.

Until that audit:

`FULL_DOCUMENTATION_ZERO_LOSS = OPEN`
`MIGRATION_GATE = BLOCKED`
`MIGRATION_AUTHORIZED = NO`
