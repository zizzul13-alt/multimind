# MULTIMIND — DEEP DEBATE REVISION SEMANTICS

Status: **CLOSED / FULL FEATURE IMPLEMENTATION OF THIS BOUNDED CONTRACT**
Date: 2026-09-11
Entering baseline: `main@ed18dfe0a839755d88f0391de1593441947a8e06`
Implementation: PR #127
Final PR head: `6ac091633ac3405b9b00e15f219be97861bb0d48`
Implementation exact-main: `a314c4f953f01f53bbe60b500a21a3903ae134b8`
Owning workstream: AI / Deliberation Semantics

## Why this workstream existed

The previously accepted deliberation correction (PR #107) remains CLOSED and authoritative for its bounded contract. It already provided:

- N selected participants = N traceable participant attempts;
- honest participant/provider provenance;
- real critique rounds for `rounds > 1`;
- synthesis/judge distinct from Release Gate;
- persistence of structured deliberation truth.

The accepted AI Product DNA also describes a deeper optional destination where a deep debate can include explicit **revision** after critique. The entering baseline did not yet contain a distinct post-critique participant revision artifact. PR #127 adds that capability without reopening or weakening PR #107.

## Implemented contract

1. `rounds = 1` remains PANEL semantics: independent participants then synthesis.
2. `rounds = 2` remains DELIBERATE semantics: independent participants, one critique round, then synthesis.
3. `rounds >= 3` is DEEP DEBATE semantics while preserving all existing critique rounds. After critiques, every successful participant receives one explicit post-deliberation revision opportunity.
4. Revision executes through the same selected provider identity as the participant. No cross-provider fallback may impersonate a participant revision.
5. A revision receives the original task, that participant's original contribution, the full participant panel, and accumulated critiques.
6. Revision may correct itself, adopt stronger reasoning/evidence, or preserve justified disagreement. Convergence is not forced.
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

## Adversarial repair loop

The first implementation was not accepted after its first green-looking stage. Full Python regression exposed a concrete provenance defect in the shared `ModelRouter`: provider failures were logged with sanitized `failure_category` metadata, but the terminal router result discarded that category. As a result, a failed participant revision could remain attributable to the correct provider while losing the precise sanitized failure reason.

The implementation repaired the router rather than weakening the new semantic test. `ModelRouter` now preserves only bounded/sanitized terminal failure metadata (`failure_category`, `status_code`, `exception_type`) while retaining the generic user-facing terminal error text. Raw provider errors are not exposed.

The workstream also found a CI path-filter blind spot: RJ5 and RJ6 did not trigger for changes to `core/debate.py`. Their path filters now include the deliberation orchestrator and its semantic tests so future Core deliberation changes cannot silently bypass those migration/recovery gates.

## Verification evidence

Behavioral proof covers:

- rounds 1/2 do not gain hidden revision calls;
- rounds 3+ produce one revision attempt per successful participant;
- all historical critique rounds remain intact;
- revision receives original contribution + full panel + critiques;
- revision is executed only by its participant's provider;
- failed revision remains explicit and cannot be replaced by another provider;
- judge receives revision artifacts;
- judge-failure fallback prefers a successful revision;
- revisions remain serializable/persistable inside existing debate data;
- existing deliberation and full regression behavior remains green.

An intermediate Python Regression run #341 intentionally remains part of the repair history: it failed 1 new semantic test while 404 tests passed, revealing the terminal failure-metadata defect described above.

Final PR head:

`6ac091633ac3405b9b00e15f219be97861bb0d48`

PR-head verification on that exact head:

- Python Regression #346 — SUCCESS;
- RJ5 Dual-Host Torture #109 — SUCCESS;
- RJ6 Cutover Rollback Proof #118 — SUCCESS;
- Final Gate Operator Readiness #176 — SUCCESS.

PR #127 was then squash-merged with expected-head guard against exactly `6ac091633ac3405b9b00e15f219be97861bb0d48`.

Implementation exact-main:

`a314c4f953f01f53bbe60b500a21a3903ae134b8`

Exact-main verification on that implementation commit:

- Python Regression #353 — SUCCESS;
- RJ5 Dual-Host Torture #116 — SUCCESS;
- RJ6 Cutover Rollback Proof #125 — SUCCESS;
- Final Gate Operator Readiness #183 — SUCCESS.

Known in-scope residuals after exact-main verification: **0**.

## Scope protection

This workstream did **not**:

- reopen the already-closed PR #107 semantic correction;
- add a new agent framework/service/database/transport;
- add providers or credentials;
- change Design-DNA or Theme Studio;
- implement user-verdict persistence (separate bounded workstream);
- authorize Railway integration or production cutover.

## Closure classification

`DEEP_DEBATE_REVISION_SEMANTICS = FULL FEATURE IMPLEMENTATION / CLOSED`

`KNOWN_IN_SCOPE_RESIDUALS = 0`

`FULL_OPERATIONAL_PROVIDER_VERIFICATION = NOT CLAIMED BY THIS WORKSTREAM`

`RAILWAY_FINAL_INTEGRATION = HOLD`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`

This closure is for the finite Deep Debate revision contract only. It does not claim that every remaining AI Product DNA destination item is implemented or operationally verified.
