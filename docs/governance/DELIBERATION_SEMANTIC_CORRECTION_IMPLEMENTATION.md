# MULTIMIND — DELIBERATION SEMANTIC CORRECTION

Status: **USER-AUTHORIZED / BOUNDED IMPLEMENTATION — PRE-MERGE CLEAN**
Date: 2026-09-08
Baseline: `main@72d1b71db4553ddd7b6fe32a18dbb9a7b2aa4deb`
Companion product contract: `docs/governance/MULTIMIND_AI_PRODUCT_DNA_MASTER.md`

## Mission

Correct the AI deliberation semantics so the current implementation faithfully realizes the accepted AI Product DNA without reopening unrelated closed gates.

The accepted user sequencing is:

`HOLD FINAL RAILWAY INTEGRATION → IMPLEMENT DELIBERATION SEMANTICS → VERIFY/REPAIR UNTIL NO IN-SCOPE RESIDUALS → MERGE TO EXACT CORRECTED MAIN → ONLY THEN BUILD FINAL RAILWAY CANDIDATE.`

This workstream **must not perform final Railway integration or production cutover**.

## Bounded implementation destination

The implementation provides:

1. `N selected participants = N traceable participant attempts`.
2. Participant calls do not silently fall through to a different provider and masquerade as the selected participant.
3. Participant failure remains explicitly attributable to the selected participant.
4. Successful participant contributions remain inspectable in debate data/history.
5. Deliberation depth/rounds change real execution behavior.
6. Judge/synthesis is utility machinery distinct from participant identity.
7. Judge fallback is restricted to explicitly selected providers that successfully participated and reports the actual provider used; configured-but-unselected resources are never silently consumed.
8. Release Gate remains distinct from judge/synthesis.
9. Existing direct Unified/Remote compatibility paths remain direct compatibility paths and are not represented as multi-mind deliberation.
10. Existing `MultiMindApplication`, persistence, security, Reflex, and Design-DNA boundaries remain intact.
11. An explicitly empty participant roster remains empty; it cannot silently inject a default provider.

## Verification matrix

Deterministic proof includes:

- 1 selected participant;
- 2 selected participants;
- 3 selected participants;
- 6 selected participants;
- explicit zero-participant roster;
- selected participant success/failure;
- no participant identity substitution;
- no hidden configured/unselected provider use by judge fallback;
- partial participant failure with surviving synthesis;
- all participant failure terminal behavior;
- rounds/depth 1, 2, 3 with measurably different call graphs;
- actual provider provenance for judge/synthesis;
- Release Gate on final synthesis/fallback candidate;
- persistence of structured debate data through `MultiMindApplication`;
- Reflex and presentation projection of inspectable contribution/debate metadata without duplicating business logic;
- regression compatibility for existing provider resilience and persistence guarantees.

## Latest clean pre-merge evidence

Branch head before this governance checkpoint: `de1217549ab3d1e0dac5ba6fe75818158e468341`.

All required workflows were green on that head after repeated residual repair:

- Python Regression #229 — PASS;
- RJ5 Dual-Host Torture #19 — PASS;
- RJ6 Cutover Rollback Proof #30 — PASS;
- Final Gate Operator Readiness #59 — PASS.

Adversarial review after an earlier green state found and repaired two concrete residuals:

1. judge fallback could otherwise consume a configured but unselected resource;
2. an explicit empty roster could otherwise acquire the legacy Cloudflare default.

Both have deterministic regression coverage. This governance checkpoint changes the branch head, so the required workflows must pass again on the exact new head before merge.

## Implementation discipline

Use the smallest coherent correction. Do not introduce FastAPI, CrewAI, LangChain, AutoGen, new databases, network boundaries, or provider redesign.

Normal loop:

`inspect → implement → targeted tests → adversarial tests → repair → full regression → diff review → merge with expected-head guard → exact-main verification`.

If a test/residual exposes an in-scope defect, repair and repeat without returning for routine permission.

Stop and escalate only for a true blocker, material scope expansion, destructive decision, or conflict with a currently authoritative lock.

## Status vocabulary

A green proving test is not full completion.

Use:

- `TEST / PROOF`
- `PARTIAL IMPLEMENTATION`
- `FULL FEATURE IMPLEMENTATION`
- `FULL OPERATIONAL VERIFICATION`
- `PRODUCTION CUTOVER`

This branch targets **FULL FEATURE IMPLEMENTATION of bounded deliberation semantics**. Final Railway integration remains HOLD.
