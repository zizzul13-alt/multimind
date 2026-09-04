# MultiMind Design DNA — Source Census Ledger v1

STATUS: KNOWN-SOURCE CENSUS DISPOSITION CLOSED — OPEN ONLY TO FUTURE/UNKNOWN HISTORICAL DISCOVERY
DATE: 2026-09-04
BRANCH: `docs/design-dna-consolidation`
BOUNDARY: `SOURCE_CENSUS_BOUNDARY_v1.md`

## 0. Purpose

This ledger records the archival disposition of known Design-DNA Markdown source families inside the agreed source-census boundary.

It is separate from `RAW_SOURCE_MANIFEST_v2.md`:

- this ledger answers **what historical source families exist / are implied and what happened to each**;
- the raw manifest answers **where the durable raw/surrogate representation lives and what exactness level it has**.

The current pass closes the previously open named-source limbo. It does not claim omniscience about an unknown historical file that may surface later.

## 1. Disposition law — final

```text
DISCOVERED + FULL RETRIEVABLE
→ RAW MIRROR
→ VERIFY AGAINST SOURCE WHEN POSSIBLE

DISCOVERED + TRUNCATED / FULL TEXT UNAVAILABLE
→ CHECK SURVIVING SOURCE + CUMULATIVE PROJECT MEMORY
→ MEMORY_RECONSTRUCTED_SURROGATE
→ LABEL NON-VERBATIM

DISCOVERED + NO SAFE MEMORY/EVIDENCE
→ RAW_ARCHIVE_PENDING_FULL_SOURCE_ACCESS

LINEAGE-IMPLIED BUT EXACT SOURCE NOT FOUND
→ SOURCE_NOT_YET_DISCOVERED

MULTIPLE SAME/NEAR TITLE IDS
→ DUPLICATE_CANDIDATE UNTIL FULL COMPARISON

DISTINCT CONTENT PROVEN
→ VARIANT_VERIFIED_DISTINCT

SUPERSEDED
→ PRESERVE; NEVER DELETE
```

`MEMORY_RECONSTRUCTED_SURROGATE != RAW SOURCE`.

The surrogate closes census/disposition ambiguity; it does not manufacture original prose.

## 2. Current repository census inventory

Recursive branch-tree reconciliation records:

```text
RAW_FILES_PRESENT_IN_ARCHIVE_RAW = 56
MEMORY_RECONSTRUCTED_SOURCE_RECORDS = 61
MEMORY_SURROGATE_POLICY_FILES = 1
```

These are repository artifact counts, not historical-source denominators. One source family can have multiple File Library IDs or GitHub variants.

## 3. Foundation / Recovery / B-series — reconciled

| Family | Current durable disposition | Authority role |
|---|---|---|
| Chat Handoff Checkpoint v1 | memory surrogate | historical/master handoff |
| Recovery Ledger v2/v3/v4/v5/v6/v7 | memory surrogates; v4/v6/v7 have known truncated source IDs | superseded/historical cumulative recovery |
| B1 Tier S | memory surrogate | historical membership lineage; later Batch6 |
| B2 Tier A | memory surrogate | historical membership lineage; later Batch6 |
| B3 Tier B + Routing | memory surrogate | historical routing lineage; later Batch6 |
| B4 Country-Web | memory surrogate | historical 14/20 lineage; later Wave G/Batch7 |
| B4D Web Corpus Deepening | memory surrogate | historical claim-scope law |
| B5 Material + Environment | memory surrogate | normalized engine lineage; later Wave C/Batch2 |
| B6 Benchmark Marriages | memory surrogate | historical F01–F15 fixture lineage |
| B7 Izzul Corpus | memory surrogate | exact 36 membership/primitive lineage |
| B8 Miko Corpus Deep v1 | memory surrogate | exact 23 membership/mechanism lineage |
| B8 Miko Evidence Closure v2 | exact raw mirror | historical evidence closure |
| B9 First Executable Projection Slice | memory surrogate | historical calibration slice |
| B10 Global Equalization v1 | memory surrogate | historical parity doctrine |
| B10 Torture + Lock v2 | memory surrogate | historical locked parity governance |
| Canonical Master Index v1 | memory surrogate | historical B0–B8 snapshot |
| Unresolved Gap Ledger v1 | exact raw mirror | historical debt ledger |
| HQ Wave Topology Audit / Wave-B lock | memory surrogate | historical topology governance |
| Wave-B Material Queue | memory surrogate | historical Track-M separation witness |
| Wave-B Deep Equalization | memory surrogate | historical archetype-diversity result |

Disposition result:

`FOUNDATION_B_SERIES_KNOWN_SOURCE_LIMBO = 0`.

## 4. Wave C / D — reconciled

### Wave C

- Branch Brief v1 → exact raw.
- Continuation Brief v2 → exact raw.
- Material/Environment Deep v1 → memory surrogate.
- Material/Environment Deep v2 → memory surrogate.

Final maturity authority is later Global Calibration Batch2, not the early Wave-C research artifacts.

### Wave D

- Branch Brief v1 → exact raw.
- expressive/productive-tension result lineage → preserved by historical Wave-D source/surviving governance.
- final Wave-D Lock Checkpoint v1 → exact raw / current final Wave-D authority.

`WAVE_C_D_KNOWN_SOURCE_LIMBO = 0`.

## 5. Wave E — full historical progression dispositioned

Historical maturity progression is now durably navigable:

```text
v1 = 6 / 36 EQ3
v2 = 29 / 36 EQ3
v3 = 34 / 36 EQ3
v4 = 34 / 36 EQ3 after final-two micro pass
v5 = 35 / 36 EQ3
v6 = 36 / 36 EQ3
```

Durable representations include:

- v1 result → memory surrogate;
- v2 result → memory surrogate;
- v2 continuation brief → exact raw;
- v3 result → memory surrogate;
- v3 continuation brief → exact raw;
- v4 brief → exact raw;
- v4 result → exact raw;
- v5 brief → exact raw;
- v5 result → exact raw;
- v6 brief → exact raw;
- v6 final result → memory surrogate;
- final Wave-E Lock → exact raw.

Final authority: `WAVE_E_LOCK_CHECKPOINT_v1` + current calibration/corpus docs.

`WAVE_E_KNOWN_SOURCE_LIMBO = 0`.

## 6. Wave F — full historical progression dispositioned

Durable progression:

```text
v1 = 5 / 23 EQ3
v2 = 10 / 23 EQ3
v3 = 20 / 23 EQ3
v4 = 23 / 23 EQ3
```

- v1 result → memory surrogate; v1 full-equalization brief → exact raw.
- v2 result → memory surrogate; v2 residual brief + HQ stress test → exact raw.
- v3 result → memory surrogate; v3 collision/evidence brief → exact raw.
- v4 result → memory surrogate; v4 final-three brief → exact raw.
- final Wave-F Lock → exact raw.

Final authority: `WAVE_F_LOCK_CHECKPOINT_v1` + current Batch5/corpus docs.

`WAVE_F_KNOWN_SOURCE_LIMBO = 0`.

## 7. Wave G — denominator evolution dispositioned

Historical evolution:

```text
v1 working EQ2 denominator = 8
v2 defensible confirmed EQ2 denominator = 6
v3 final additive Country-Web denominator = 5
final = 5 / 5 EQ3; residual = 0
```

- v1 full residual census result → memory surrogate.
- v2 eight/six-country result → memory surrogate; same-title source IDs remain `DUPLICATE_CANDIDATE`.
- v3 final-two brief → exact raw.
- v3 result → memory surrogate.
- three same/near Wave-G lock artifacts → all exact raw and `VARIANT_VERIFIED_DISTINCT`; safe dedup = NO.

Final authority: final Wave-G lock + Batch7 lock/current corpus/calibration docs.

`WAVE_G_KNOWN_SOURCE_LIMBO = 0`.

## 8. Wave H — historical reversal preserved

Two historically different states are intentionally retained:

```text
Wave H v1 census: WAVE_H_ELIGIBLE = 0
Wave H v2 evidence recovery: actionable denominator = 3
final research closure: CKT + Liyelaa + Dumbara = 3 / 3
```

- v1 census brief → exact raw.
- v1 result → memory surrogate.
- v2 MD-first forensics brief → exact raw.
- v2 result → memory surrogate.
- v2 HQ acceptance checkpoint → exact raw.
- final Wave-H research lock → exact raw.

The v1 zero-eligible state is not deleted simply because v2 found new evidence.

`WAVE_H_KNOWN_SOURCE_LIMBO = 0`.

## 9. Historical Track M / Track M_R — reconciled

### Historical Track M

- historical named-material recovery v1 → memory surrogate.
- v1 HQ stress test → exact raw.
- v1 acceptance checkpoint → exact raw.
- archival-recovery forensics brief v2 → exact raw.
- archival-recovery result v2 → memory surrogate.

Authoritative unresolved truth remains:

`HISTORICAL TRACK M CARDINALITY = UNKNOWN`.

`FILE LIBRARY EXHAUSTION != HISTORICAL CHAT EXHAUSTION`.

No surrogate claims a fabricated exact denominator.

### Track M_R

- reconstructed census/result v3 → memory surrogate.
- v4 brief → exact raw; v4 result → memory surrogate.
- v5 torture brief → exact raw; v5 result → memory surrogate.
- v6 final-seven result → memory surrogate.
- final Track-M_R full-pass lock → exact raw.
- Global Calibration Batch3 lock → later exact raw calibration authority.

Important historical discrepancy is preserved: v5 branch report claimed 25/25 while HQ accepted only 18/25 at that checkpoint; v6 closed the seven residuals to genuine 25/25.

`TRACK_M_AND_M_R_KNOWN_SOURCE_LIMBO = 0`.

## 10. Track T — dispositioned

- Music/Temporal Activation Brief v1 → exact raw.
- Activation Checkpoint v1 → exact raw.
- Dual-Lane Scope Amendment v1.1 → exact raw.
- Dual-Lane Census Brief v1.1 → exact raw.
- dual-lane census result v1 → memory surrogate.
- T-I 16/16 EQ3 brief v2 → exact raw.
- T-I v2 result → memory surrogate.
- T-I v3 projection-contract hardening → memory surrogate.
- final T-I v3 Full-Pass Lock → exact raw.

Final state:
- T-I = exact 16 references, 16/16 EQ3;
- TP01–TP18 additive;
- TP19/TP20 historical non-additive metadata/contract lineage;
- T-G exploratory/nonblocking.

`TRACK_T_KNOWN_SOURCE_LIMBO = 0`.

## 11. Final Global Census 273 → 271 — dispositioned

| Historical family | Durable state | Authority |
|---|---|---|
| Final Census v1 — 273 | memory surrogate | `SUPERSEDED_HISTORICAL` |
| Final Census v1-1 — 273 | memory surrogate + `DUPLICATE_CANDIDATE` | `SUPERSEDED_HISTORICAL` |
| Final Census Brief v1 | exact raw | historical branch instruction |
| HQ-patched v1.1 — 271 multi-ID family | memory surrogate + `DUPLICATE_CANDIDATE` | 271 correction lineage |
| HQ-patched-2 | separate memory surrogate + duplicate/variant relation unresolved | historical 271-family variant |

The current 271 denominator supersedes 273 for implementation truth without deleting the 273-era record.

`FINAL_CENSUS_KNOWN_SOURCE_LIMBO = 0`.

## 12. Global Calibration Batch1–9 — dispositioned 9/9

All giant artifact tables are truncated under current File Library retrieval. Each now has a dedicated memory surrogate; no missing tail was reconstructed as original prose.

| Batch | Additive scope | Giant artifact | Lock/checkpoint |
|---|---:|---|---|
| B1 | 34 | memory surrogate; duplicate-candidate source pair | exact standalone lock source not recovered; accepted lock state has a separate memory surrogate |
| B2 | 29 | memory surrogate; duplicate-candidate family | exact raw lock |
| B3 | 25 | memory surrogate; duplicate-candidate family | exact raw lock |
| B4 | 61 | memory surrogate; duplicate-candidate family | exact raw lock |
| B5 | 48 | memory surrogate; duplicate-candidate family | exact raw lock |
| B6 | 55 | memory surrogate; duplicate-candidate family | exact raw lock |
| B7 | 5 | memory surrogate; duplicate-candidate family | exact raw lock |
| B8 | 14 | memory surrogate; duplicate-candidate family | exact raw lock |
| B9 | non-additive | memory surrogate; duplicate-candidate family | exact raw lock |

Calibration endpoint:

```text
GLOBAL_EQ3 = 271 / 271
RESIDUAL = 0
RESEARCH_REOPEN = 0
ASSET_APPLICABLE = 207
ASSET_NOT_APPLICABLE = 64
DIRECT_IP_GATED = 75
```

`GLOBAL_CALIBRATION_KNOWN_SOURCE_LIMBO = 0`.

## 13. Duplicate-state interpretation

A duplicate candidate is no longer an unaccounted source.

For every known duplicate family we preserve all known File Library identities in the manifest/surrogate and refuse destructive dedup until complete equality evidence exists.

Therefore:

`DUPLICATE_CANDIDATE != SOURCE_CENSUS_FAILURE`.

It remains provenance uncertainty, not missing-source ambiguity.

## 14. Census closure statement

For every currently named and source-known Design-DNA artifact family inside the explicit census scope, a durable disposition now exists.

```text
KNOWN_NAMED_SOURCE_CENSUS = COMPLETE
KNOWN_SOURCE_DISPOSITION = PASS
KNOWN_SOURCE_WITHOUT_DISPOSITION = 0
GLOBAL_CALIBRATION_SOURCE_FAMILIES = 9 / 9 DISPOSITIONED
FINAL_CENSUS_LINEAGE = DISPOSITIONED
WAVE_TRACK_JUMBO_FAMILIES = DISPOSITIONED
```

The only legitimately open historical dimension is discovery of an artifact whose exact identity is not currently known or whose existence is only weakly implied. Such an item is not silently invented and does not reopen settled current canon unless new evidence materially contradicts it.

Thus future discovery operates as:

`CONDITION_DRIVEN_ARCHIVAL_RECOVERY`, not an indefinite active census backlog.

## 15. Boundary after this pass

```text
SOURCE_CENSUS_FOR_KNOWN_NAMED_ARTIFACTS = CLOSED
UNKNOWN_HISTORICAL_DISCOVERY = CONDITION_DRIVEN
RAW_EXACT_RECOVERY_FOR_SURROGATE_ONLY_SOURCES = OPEN IF BETTER ACCESS APPEARS
CANONICAL_SEMANTIC_CONSOLIDATION = PASS
GLOBAL_EQ3 = 271 / 271
MIGRATION_AUTHORIZED = NO
PRODUCTION = UNTOUCHED
EQ4 = NOT PERFORMED
```

No Codex invocation occurred in this census/reconciliation pass.