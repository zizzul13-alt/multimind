# MULTIMIND DESIGN DNA — Q4 PRIVATE-READY CUT IMPLEMENTATION REPORT

Status at authoring: implementation candidate; Governor ACC requires merge plus exact-main proof.

## Mission

Q4 makes the current public repository structurally ready for later extraction of Design-DNA / Theme Studio into a private repository. Q4 does **not** perform that extraction and does not rewrite public Git history.

## Reverse-dependency repair

The Q2 deferred debt is closed. Quarantined implementation no longer self-imports through public compatibility shims:

- `dna_quarantine/legacy_ui_dna/**` now uses private-relative imports for its own models, registry, mapper and proof definitions;
- `dna_quarantine/theme_studio/state.py` consumes the quarantine-owned legacy DNA implementation directly;
- `dna_quarantine/theme_studio/surface.py` consumes quarantine-owned DNA and Theme Studio state directly;
- `ui/dna/**` and `ui/theme_studio/**` remain compatibility surfaces only.

The private candidate may still use genuine presentation-host adapter contracts such as `ui.themes`, `ui.presentation`, `ui.foundation`, and the preview spike where the legacy adapter/Theme Studio surface actually renders into the current host. These are explicitly classified as host-owned adapter dependencies rather than hidden DNA ownership. Q4 does not pull provider, core, or database layers into the DNA package.

## Public bridge / absence behavior

The application-facing entry remains the small stable `ui/dna_bridge.py` established by Q3. It lazy-loads the quarantine/private candidate. Q4 tests simulate the entire `dna_quarantine` candidate being unavailable and prove that the public bridge still returns neutral material/identity fallbacks, optional bootstrap returns false, and Theme Studio is reported unavailable instead of breaking public startup behavior.

## Machine-readable extraction ownership

`docs/design-dna/quarantine/PRIVATE_EXTRACTION_INVENTORY.yaml` is now the extraction ownership source of truth. It classifies:

- private-owned runtime roots;
- legacy public compatibility shims;
- the public bridge;
- host-owned consumers/adapters;
- DNA-owned tests and docs;
- canonical fixtures;
- asset policy/manifests and current proof-material directories.

The inventory explicitly records that current material directories are **not** production-approved assets, actual private-repository extraction is still false, public history is not sanitized, and destructive history rewriting is not authorized.

## Q4 guards

The Q4 test suite adds AST-level checks that:

1. `design_dna/**` and `dna_quarantine/**` do not reverse-import `ui.dna` or `ui.theme_studio`;
2. the private candidate does not import `core`, `providers`, or `database` layers;
3. Theme Studio implementation remains quarantine-owned;
4. public legacy paths remain thin compatibility shims;
5. Q2's deferred reverse-import marker is replaced by an explicit Q4 resolved marker;
6. the private extraction inventory contains all required ownership categories and does not overclaim extraction/history sanitization;
7. the public bridge survives private-candidate absence.

## Low-maintenance result

Q4 does not create per-reference host branches or a second resolver. The boundary remains:

`PUBLIC APP → SMALL PUBLIC DNA BRIDGE → QUARANTINED/PRIVATE CANDIDATE`

with a boring safe default when the private candidate is unavailable.

## Non-claims

Q4 implementation does not claim:

- actual private repository extraction;
- public Git history sanitization;
- M12 completion;
- EQ4 credit;
- RJ3 start;
- production cutover authorization.
