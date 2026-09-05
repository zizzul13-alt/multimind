# MULTIMIND DESIGN DNA — M10 IMPLEMENTATION REPORT

Status: IMPLEMENTED / PENDING GOVERNOR ACCEPTANCE  
Batch: M10  
Scope: Track M_R reconstructed named-material references — 25 additive members  
Base: `main@3b95ae1155bae7b5a37d646a46ba21c1964b6953`

## 1. Scope

M10 implements the locked 25-member `TRACK_M_R` corpus as declarative, host-neutral `DNAUnit(kind=REFERENCE)` contracts:

`MR-001` through `MR-025` exactly, retaining the historical hyphenated IDs.

The membership is:

1. MR-001 Aklan Piña
2. MR-002 Batik
3. MR-003 Khayamiya
4. MR-004 Damascene metal inlay
5. MR-005 Masi
6. MR-006 Siapo
7. MR-007 Ngatu
8. MR-008 Tukutuku
9. MR-009 Jamdani
10. MR-010 Shyrdak
11. MR-011 Zellij
12. MR-012 Kente
13. MR-013 Adire
14. MR-014 Kuba textile
15. MR-015 Bògòlanfini
16. MR-016 Guna Mola
17. MR-017 Yakan weaving
18. MR-018 Turkmen carpet
19. MR-019 Baganda barkcloth
20. MR-020 Sekishu-Banshi / Washi
21. MR-021 Traditional Japanese wooden-architecture conservation skills
22. MR-022 Art of dry stone construction
23. MR-023 Japanese urushi
24. MR-024 Raku ware
25. MR-025 Murano mezza filigrana

## 2. Permanent ontology firewalls

M10 preserves the locked research separation:

```text
M1–M15 NORMALIZED MATERIAL ENGINES
    !=
TRACK_M_R RECONSTRUCTED NAMED REFERENCES
    !=
LOST HISTORICAL TRACK M CORPUS
```

Engine mapping never substitutes named-reference identity. M10 does not claim recovery of the lost historical Track M denominator.

Six evaluated but non-additive/routed candidates remain outside M10: Kanga, Māori Wharenui, Dumbara, Liyelaa, generic Barkcloth, and Bidri ware comparator.

## 3. Epistemic partition

The runtime exposes the research mode in each reference identity trace rather than flattening all 25 rows into the same confidence class:

- 8 `RECOVERED_MECHANISM_EXAMPLE`
- 7 `V6_SELECTOR_HARDENED`
- 10 `BOUNDED_EQ3_TRANSLATION`

The seven v6-hardened references are MR-004, MR-005, MR-006, MR-012, MR-014, MR-018, and MR-021.

## 4. Selector / UNKNOWN law

M10 deliberately does **not** change the M0 resolver and does **not** claim `CompositionRequest.modifiers` activate reference branches. Selector-sensitive rows carry static accepted-scope policy metadata and fail-closed wording.

Locked v6 contracts and M10 project selections are:

- Damascene: true/mechanical inlay only; painted or overlay line is not inlay.
- Masi: `MASI_KESA_STENCIL`; mask/stencil is above the sheet; underlying rubbing is a causal mismatch.
- Siapo collision slice: Tasina/Elei rubbing; relief source is below the sheet; stencil-above causality is a mismatch.
- Kente: safe shared invariant is narrow woven strips sewn into macro-cloth; branch-specific weaving details require evidence.
- Kuba: M10 fixes the supported multi-panel stitched/appliquéd wrapper branch; single-panel cut-pile/embroidery behavior is explicitly excluded from that selected construction. This is a project slice, not a universal Kuba grammar.
- Turkmen: object-level technical selector is required; subgroup or gul/motif identity cannot infer knot type.
- Japanese wooden-architecture conservation: M10 fixes the supported structural-woodwork conservation operation; roofing/thatching, plastering, lacquer painting, tatami, and other inventory skills are not synthesized into it. There is no universal “Japanese joint” abstraction.

Arbitrary runtime modifiers may change the deterministic request fingerprint, as they already did in M0, but they do not alter the reference-owned mechanism set or activate a hidden alternate branch.

## 5. Asset policy

All 25 Track M_R references are locked as asset-applicable for later enrichment, but M10 adds no asset files and no mandatory asset intents.

```text
ASSET_APPLICABLE = 25 / 25
ACTUAL_ASSET_FILES_ADDED = 0
MANDATORY_ASSET_SLOTS = 0
```

All 25 must retain construction identity in AVAILABLE, LOADING, PARTIAL, and OFF asset states. M12 owns canonical 271-unit asset-policy reconciliation.

## 6. Accessibility / Reading Sanctuary

Construction cues are presentation-only and may not outrank semantic truth, accessibility, or Reading Sanctuary. Urushi reflectivity and Murano transparency/refraction receive explicit structural low-glare/high-contrast demotion directives. Mobile adaptation serializes joints/layers/process cues rather than shrinking texture.

## 7. Deep torture matrix

`tests/test_design_dna_m10_track_m_r.py` proves at minimum:

- exact 25-member denominator and routed non-member firewall;
- combined M0–M10 registry = 160 references + 29 engines + 68 primitives = 257 unique units;
- 25 × 3 viewport projections;
- 25 × 4 asset-state projections;
- 25 × 68 reference/primitive compositions;
- 25 × 29 reference/engine compositions;
- each reference with all 68 primitives simultaneously;
- each reference with all 29 engines simultaneously;
- all 300 Track M_R pair differentiations;
- all 300 A→B→A deterministic switches;
- 25 × 135 prior-reference identity firewalls;
- Reading Sanctuary + accessibility survival for all 25;
- reduced-motion neutrality for all 25;
- exact epistemic partition;
- exact selector-policy trace;
- Masi/Siapo causal distinction;
- Damascene inlay negative;
- Kente shared-invariant guard;
- fixed Kuba branch + variant non-synthesis;
- Turkmen subgroup/knot firewall;
- fixed structural-woodwork Japanese conservation operation + no-universal-joint firewall;
- optical accessibility demotion for urushi and mezza filigrana;
- arbitrary modifiers cannot activate a hidden selector branch.

The first full torture run (#101) intentionally exposed three wording/trace misses (MR-004 inlay token, MR-017 weave token, MR-021 process token). The contracts were strengthened rather than weakening the guard. Final clean-head and post-merge counts are recorded only after those proofs complete.

## 8. Low-maintenance result

M10 adds one declarative corpus module, not 25 reference classes/components and not host-specific branches. It introduces no Streamlit/Reflex dependency, no database schema change, no provider/AI-core change, and no application-state mutation.

## 9. Non-claims

M10 does not claim:

- Q3 completion;
- fixture implementation (M11);
- Q4 private-ready cut;
- asset final approval/enrichment (M12);
- EQ4 credit;
- RJ3 start;
- production cutover.

Governor acceptance, merge SHA, exact-main proof, and `M10_ACC.yaml` must be recorded only after the implementation PR is merged and post-merge evidence is green.
