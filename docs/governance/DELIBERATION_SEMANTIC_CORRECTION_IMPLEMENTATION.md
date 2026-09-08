# MULTIMIND — DELIBERATION SEMANTIC CORRECTION

Status: **USER-AUTHORIZED / BOUNDED IMPLEMENTATION**
Date: 2026-09-08
Baseline: `main@72d1b71db4553ddd7b6fe32a18dbb9a7b2aa4deb`
Companion product contract: `docs/governance/MULTIMIND_AI_PRODUCT_DNA_MASTER.md`

## Mission

Correct the AI deliberation semantics so the current implementation faithfully realizes the accepted AI Product DNA without reopening unrelated closed gates.

The accepted user sequencing is:

`HOLD FINAL RAILWAY INTEGRATION → IMPLEMENT DELIBERATION SEMANTICS → VERIFY/REPAIR UNTIL NO IN-SCOPE RESIDUALS → MERGE TO EXACT CORRECTED MAIN → ONLY THEN BUILD FINAL RAILWAY CANDIDATE.`

This workstream **must not perform final Railway integration or production cutover**.

## Bounded implementation destination

The implementation must provide at minimum:

1. `N selected participants = N traceable participant attempts`.
2. Participant calls must not silently fall through to a different provider and masquerade as the selected participant.
3. Participant failure must remain explicitly attributable to the selected participant.
4. Successful participant contributions must remain inspectable in debate data/history.
5. Deliberation depth/rounds must change real execution behavior.
6. Judge/synthesis is utility machinery distinct from participant identity.
7. Judge fallback may preserve synthesis availability but must report the actual provider used.
8. Release Gate remains distinct from judge/synthesis.
9. Existing direct Unified/Remote compatibility paths may remain but are not represented as multi-mind deliberation.
10. Existing `MultiMindApplication`, persistence, security, Reflex, and Design-DNA boundaries remain intact.

## Verification matrix

Required deterministic proof includes:

- 1 selected participant;
- 2 selected participants;
- 3 selected participants;
- 6 selected participants;
- selected participant success/failure;
- no participant identity substitution;
- partial participant failure with surviving synthesis;
- all participant failure terminal behavior;
- rounds/depth 1, 2, 3 with measurably different call graphs;
- actual provider provenance for judge/synthesis;
- Release Gate on final synthesis/fallback candidate;
- persistence of structured debate data through `MultiMindApplication`;
- Reflex projection of inspectable contribution/debate metadata without duplicating business logic;
- regression compatibility for existing provider resilience and persistence guarantees.

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
