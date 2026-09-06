# M12 — Final 271-Unit Asset-Policy Reconciliation

Status: **IMPLEMENTED CANDIDATE — AWAITING CLEAN-HEAD / MERGE / EXACT-MAIN / ACC**

Date: 2026-09-06

## 1. Entering gate

M12 started only after Q4 closure was merged and exact-main proved green:

- Q4 runtime PR: #88
- Q4 runtime integration: `0cdbc62eb5819f7a65213e031657610f6dd4ca5a`
- Q4 clean-head regression: run #127, 37,776 passed, `pip check` clean
- Q4 runtime exact-main: run #128, 37,776 passed, `pip check` clean
- Q4 closure PR: #89
- Q4 closure integration: `ac9c494e4fcac0c6fde8759a311f791efcae806e`
- Q4 closure clean-head: run #132, success
- Q4 closure exact-main: run #134, 37,776 passed, `pip check` clean
- `PRIVATE_EXTRACTION_INVENTORY.yaml`: `q4_state: PRIVATE_READY`
- actual private extraction: **false**

M12 does not authorize or perform private-repository extraction, public-history rewrite, EQ4, RJ3, or production cutover.

## 2. Canonical runtime and ledger

The final policy is owned by:

- runtime source of truth: `design_dna/asset_policy.py`
- checked-in deterministic snapshot: `docs/design-dna/migration/status/ASSET_POLICY_271.json`

The JSON ledger is generated from the runtime source, not manually authored as a second policy engine. Tests require the checked-in snapshot to equal `asset_policy_ledger_payload()` exactly.

The builder reconstructs the same additive registry proven by M11:

| Kind | Count |
| --- | ---: |
| REFERENCE | 160 |
| ENGINE | 29 |
| PRIMITIVE | 68 |
| FIXTURE | 14 |
| **TOTAL** | **271** |

This avoids 271 bespoke decision branches. One classifier applies final M12 policy by canonical unit kind and small explicit exception sets.

## 3. Final applicability arithmetic

M12 locks the final arithmetic to:

| Kind | Applicable | N/A | Total |
| --- | ---: | ---: | ---: |
| REFERENCE | 159 | 1 | 160 |
| ENGINE | 27 | 2 | 29 |
| PRIMITIVE | 12 | 56 | 68 |
| FIXTURE | 9 | 5 | 14 |
| **TOTAL** | **207** | **64** | **271** |

Exact N/A rules:

- reference N/A: `CW02` only
- engine N/A: `E1`, `E5` only
- fixture N/A: `F03 F05 F06 F10 F14`
- primitive applicable: exactly the twelve final M12 corrections below

## 4. M4 historical semantics remain untouched

M12 deliberately does **not** change `design_dna.primitives.primitive_asset_on_applicable()`.

Historical M4 semantics therefore remain what M4 recorded: all M4 primitive lookups return `False` from that historical helper.

The final M12 policy layer applies the correction only to these twelve primitives:

`MK01 MK04 MK05 MK06 MK12 MK13 MK14 MK16 MK18 MK22 MK23 MK25`

For these rows:

- `asset_applicable = true`
- `policy_basis = M12_FINAL_PRIMITIVE_CORRECTION__M4_HISTORY_UNCHANGED`

This is an additive final reconciliation, not a retroactive rewrite of M4 evidence or acceptance records.

## 5. Direct-IP rights gate

The final direct-IP gate is the exact union of:

- Izzul: 36 references
- Miko: 23 references
- Track T-I: 16 references
- **total: 75**

All 75 are asset-applicable but remain unselected and unapproved.

Their current license state is:

`DIRECT_IP_RIGHTS_EVIDENCE_REQUIRED`

This means asset applicability is not permission to ship copyrighted material.

## 6. Structural asset law

Every one of the 271 records currently has:

- `asset_required = false`
- `fallback_required = true`
- `selected_asset = null`
- `final_approved = false`
- `rights_evidence_pointer = null`
- non-empty canonical unit provenance

Applicable, non-direct-IP rows use `UNVERIFIED_NO_SELECTED_ASSET` until actual rights/provenance evidence selects an asset.

N/A rows use `NOT_APPLICABLE`.

The four existing public proof-material directories remain inventory evidence only; none is assigned to a final policy row and final-approved count remains zero.

## 7. AVAILABLE / LOADING / PARTIAL / OFF torture

`project_asset_policy()` is host-neutral and accepts every additive unit plus each `AssetState`:

- `AVAILABLE`
- `LOADING`
- `PARTIAL`
- `OFF`

The M12 torture suite evaluates all 271 units across all four states.

Because no row has both selected asset and approved rights evidence, even `AVAILABLE` cannot activate enrichment. It must use structural fallback.

For every state and every unit:

- structural identity survives
- no asset becomes required for identity
- fallback remains active
- no unapproved asset can become active

This preserves the existing asset-off identity law rather than making M12 an asset dependency layer.

## 8. Accessibility and Reading Sanctuary

Policy projection carries independent hard vetoes for:

- accessibility
- Reading Sanctuary

Either veto disables aesthetic theatricality. Both can be active simultaneously. Neither is averaged into asset availability or rights status.

Tests also cover the four boolean combinations to prove that the two vetoes are independent and deterministic.

## 9. Private-ready boundary

`design_dna/asset_policy.py` imports only standard-library and `design_dna.*` modules.

The M12 test guard forbids new imports from:

- `core`
- `providers`
- `database`
- `ui.dna`
- `ui.theme_studio`

This keeps the policy inside the private-candidate package boundary established by Q4.

`PRIVATE_EXTRACTION_INVENTORY.yaml` now inventories both the runtime policy and the 271-entry ledger while retaining:

- `q4_state: PRIVATE_READY`
- `actual_private_repository_extraction_completed: false`
- `public_history_sanitized: false`

## 10. Maintenance budget

M12 intentionally uses:

1. the existing canonical registry to obtain the 271 additive units;
2. four compact kind-level applicability rules;
3. one explicit twelve-ID MK correction set;
4. one explicit 75-ID direct-IP union generated from the existing Izzul/Miko/Track T-I ID tuples;
5. one generated ledger snapshot checked against runtime output.

No 271-row handwritten policy implementation exists. The large JSON file is evidence/output, not executable policy logic.

## 11. Acceptance required before closure

M12 cannot be accepted from this implementation report alone. Required sequence remains:

1. final runtime PR diff audit
2. full regression
3. `pip check`
4. expected-head guarded merge
5. exact-main regression + `pip check`
6. `M12_ACC.yaml`
7. closure ledger/state update
8. closure full regression
9. closure expected-head guarded merge
10. closure exact-main regression + `pip check`
11. **STOP**

After durable M12 closure, the next chapter may be private-repository extraction only under the already-authorized project sequence. This implementation does not start that chapter.
