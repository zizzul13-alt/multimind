# MULTIMIND DESIGN DNA — M11 FIXTURES 14 IMPLEMENTATION REPORT

Status at authoring: implementation candidate; Governor ACC requires merge + exact-main proof.

## Scope

M11 implements the 14 additive benchmark/marriage fixtures as `UnitKind.FIXTURE`:

`F01 F02 F03 F04 F05 F06 F07 F08 F09 F10 F12 F13 F14 F15`

`F11` remains historical/non-additive and is not registered.

Fixtures are benchmark contracts, not a new reference family and not selectable `CompositionRequest.selected_reference_id` values.

## Epistemic handling

Surviving repository evidence explicitly recovers the original composition descriptions for F02, F03, F05, F06, F12, F13, F14 and F15.

The surviving material does not provide sufficient original-composition truth for F01, F04, F07, F08, F09 and F10. M11 therefore records these as `UNKNOWN_ORIGINAL_COMPOSITION` / `BOUNDED_EVIDENCE_GAP` rather than inventing benchmark truth. F04 additionally records that its earlier CKT blocker was closed by accepted Wave H work without pretending the complete old fixture marriage was recovered.

## Runtime contract

The fixture layer provides:

- exact 14-unit additive registry membership;
- `UnitKind.FIXTURE` firewall;
- deterministic fixture projection contracts across desktop/tablet/mobile;
- deterministic AVAILABLE/LOADING/PARTIAL/OFF asset-state behavior;
- Reading Sanctuary precedence;
- reduced-motion demotion without fixture-identity mutation;
- semantic/application truth preservation;
- explicit evidence-gap failure-closed behavior;
- no fixture-owned collage assets;
- no fixture promotion into reference truth.

After registration the canonical census is:

- REFERENCE = 160
- ENGINE = 29
- PRIMITIVE = 68
- FIXTURE = 14
- TOTAL = 271

## Asset policy carried into M12

Fixture-level applicability is preserved as governance metadata:

Applicable (9): `F01 F02 F04 F07 F08 F09 F12 F13 F15`

Not applicable (5): `F03 F05 F06 F10 F14`

No asset is mandatory for structural fixture survival and no fixture owns a collage asset.

## Non-claims

M11 does not claim EQ4, private extraction readiness, Q4 closure, M12 closure, RJ3 authorization or production cutover.
