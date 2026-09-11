# MULTIMIND — DEEP DEBATE REVISION SEMANTICS

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-11
Entering baseline: `main@ed18dfe0a839755d88f0391de1593441947a8e06`
Owning workstream: AI / Deliberation Semantics

## Why this workstream exists

The previously accepted deliberation correction (PR #107) is CLOSED and remains authoritative for its bounded contract. Current repository reality already provides:

- N selected participants = N traceable participant attempts;
- honest participant/provider provenance;
- real critique rounds for `rounds > 1`;
- synthesis/judge distinct from Release Gate;
- persistence of structured deliberation truth.

The accepted AI Product DNA also describes a deeper optional destination where a deep debate can include explicit **revision** after critique. Current `main` did not yet contain a distinct post-critique participant revision artifact. This workstream adds that capability without reopening or weakening PR #107.

## Finite corrected contract

1. `rounds = 1` remains PANEL semantics: independent participants then synthesis.
2. `rounds = 2` remains DELIBERATE semantics: independent participants, one critique round, then synthesis.
3. `rounds >= 3` becomes DEEP DEBATE semantics while preserving all existing critique rounds. After critiques, every successful participant receives one explicit post-deliberation revision opportunity.
4. Revision must execute through the same selected provider identity as the participant. No cross-provider fallback may impersonate a participant revision.
5. A revision receives the original task, that participant's original contribution, the full participant panel, and accumulated critiques.
6. Revision may correct itself, adopt stronger reasoning/evidence, or preserve justified disagreement. Convergence must not be forced.
7. Every revision attempt is separately attributable and persisted in `debate_data["revisions"]` with participant/provider/model/status/failure/tokens/cost provenance.
8. Revision failure is explicit and does not invalidate the participant's original successful contribution.
9. The synthesis judge receives originals, critiques, and revisions. Winner identity remains the existing exact participant ID; revision does not invent a second participant identity.
10. If judge/synthesis fails during deep debate, fallback prefers the first successful participant's successful revision when one exists; otherwise it falls back to that participant's original candidate.
11. Existing explicit participant roster, provider independence, user/session isolation, persistence, Release Gate, direct Unified/Remote compatibility paths, and presentation boundaries remain unchanged.

## Cost / depth semantics

This is intentionally bounded rather than all-to-all recursive debate.

For `N` successful participants:

- round 1: approximately `N + judge` calls;
- round 2: approximately `N candidates + N critiques + judge`;
- round 3: approximately `N candidates + 2N critiques + N revisions + judge`.

Rounds 4–5 preserve their additional critique rounds and still perform one final revision pass before synthesis. This keeps the existing numeric rounds control behavior monotonic while making deep debate materially different.

## Scope protection

This workstream does **not**:

- reopen the already-closed PR #107 semantic correction;
- add a new agent framework/service/database/transport;
- add providers or credentials;
- change Design-DNA or Theme Studio;
- implement user-verdict persistence (separate bounded workstream);
- authorize Railway integration or production cutover.

## Verification requirements

Prove at minimum:

- rounds 1/2 do not gain hidden revision calls;
- rounds 3+ produce one revision attempt per successful participant;
- all historical critique rounds remain intact;
- revision receives original contribution + full panel + critiques;
- revision is executed only by its participant's provider;
- failed revision remains explicit and cannot be replaced by another provider;
- judge receives revision artifacts;
- judge-failure fallback prefers a successful revision;
- revisions remain serializable/persistable inside existing debate data;
- existing deliberation and full regression tests remain green.

## Exit condition

Inspect → implement → targeted semantic tests → adversarial review → repair → Python/RJ5/RJ6/Final Gate → expected-head merge → exact-main verification → durable closure evidence.

`PRODUCTION_CUTOVER_AUTHORIZED = NO`
