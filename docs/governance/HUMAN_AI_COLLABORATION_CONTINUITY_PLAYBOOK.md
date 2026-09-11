# MULTIMIND — HUMAN / AI COLLABORATION CONTINUITY PLAYBOOK

Status: DURABLE COLLABORATION AID  
Scope: MultiMind project collaboration behavior only  
Authority: subordinate to repository reality, `AGENTS.md`, and the Project Operating Constitution  
Mutable implementation state: **NOT STORED HERE**

## 1. Why this file exists

This file preserves the working contract that has repeatedly produced accepted results between the human operator and AI governors/implementers.

It exists so that a new model, a smaller-context model, or a fresh chat can recover **how to work on MultiMind** without reconstructing the interaction style from old conversations.

This is **not** a second constitution and **not** a current-state ledger.

For implementation truth, use this precedence:

`CURRENT REPOSITORY / FILESYSTEM > MERGED IMPLEMENTATION EVIDENCE > CURRENT GOVERNANCE / STATUS ARTIFACTS > ACCEPTED GOVERNOR STATE > OLD CHAT / MEMORY / HANDOFF ASSUMPTIONS`

This playbook describes collaboration semantics, not product or implementation truth.

## 2. Public-repository privacy boundary

Only project-operational collaboration patterns belong here.

Do **not** persist unrelated personal information, private-life context, health information, account secrets, credentials, precise location, or other sensitive chat material in this public repository.

A future agent may use private conversational context when available, but must not copy it into repository documentation unless it is explicitly project-relevant and safe for the repository's visibility.

## 3. The operator's recurring objective

The operator repeatedly prefers work that moves the project toward:

`DEPLOYABLE → RELIABLE → RECOVERABLE → BORING → LOW MAINTENANCE`

while preserving:

`DATA → CORE BEHAVIOR → PROVIDER INDEPENDENCE → RECOVERABILITY → PRESENTATION CONTRACTS`

This preference is already governed by the Project Operating Constitution. Its collaboration consequence is simple:

- finish useful bounded work instead of producing endless plans;
- do not introduce fashionable architecture without a concrete need;
- prefer reversible, inspectable, low-maintenance changes;
- close evidence gaps instead of merely describing them;
- distinguish a real blocker from optional cleanup.

## 4. First-response behavior for repository-dependent work

When the request depends on repository state, the expected behavior is:

1. inspect the actual repository first;
2. identify the current branch/head and relevant merged state;
3. read only the governance/status artifacts relevant to the task;
4. compare repository reality with the supplied handoff or chat assumption;
5. skip work that is already complete;
6. continue from the **first actual unfinished step**;
7. do not reopen closed gates without invalidating evidence.

When the operator says variants of:

- `cek repo dulu`
- `kalau sudah lewati, skip`
- `lanjutkan seadanya dari yang belum`
- `repository reality wins`

this is not decorative wording. It is the required recovery algorithm.

## 5. Common operator commands and their intended semantics

### `ACC` / `ACC KEEP MASTER`

Meaning:

- accept the substantive result;
- treat the accepted decision as durable;
- persist important governance/closure state in repository Markdown when applicable.

It does **not** mean:

- production cutover is automatically authorized;
- unrelated work may start;
- a plan may be recorded as if implemented.

### `NEXT`

Meaning:

- continue to the next logical investigation or bounded task;
- do not automatically lock the current result as master unless already accepted.

### `DEEP` / `mendalam`

Meaning:

- investigate more deeply and adversarially;
- challenge assumptions;
- inspect edge cases, failure paths, conflicts, and hidden dependencies;
- compare evidence against the current claim.

It does **not** by itself authorize implementation or acceptance.

### `CODEX`

Meaning:

- authorize the currently accepted bounded implementation package for Codex or equivalent implementation execution.

It does **not** authorize production cutover or architecture expansion.

### `gas` / `lanjut` / `ayo gas`

Default meaning:

- continue the already-understood bounded work;
- do not stop for low-value confirmation;
- make the next justified move and report evidence.

If the next step crosses a reserved governance boundary, destructive action, material scope expansion, or true blocker, stop and escalate instead of treating `gas` as unlimited authority.

### `gaspoll` / `roro jonggrang` / `was wes wos` / `sampai selesai`

Meaning:

- execute the whole **already bounded and authorized** chain autonomously;
- prefer serial completion over repeated permission prompts;
- inspect → implement → verify → repair → regress → review diff → persist closure evidence;
- if an intermediate defect is repairable within scope, repair it and continue;
- stop only at the defined exit condition or a genuine escalation condition.

This phrase means **more execution**, not broader scope.

### `coba`

Meaning:

- perform a bounded experiment, inspection, comparison, or proof;
- report what happened;
- do not silently promote the experiment into accepted architecture or production.

### `jangan implement dulu`

Meaning:

- research / inspect / compare only;
- no repository mutation unless later explicitly authorized.

### `real or fake?` / `rill apa fakes?`

Meaning:

- verify the claim against actual evidence;
- distinguish marketing/demo appearance from repository or production reality;
- kill weak interpretations/candidates early;
- give a verdict with evidence and uncertainty, not vibes.

### `udah?` / `selesai berarti?` / `sudah selesai?`

Meaning:

- give an evidence-backed status answer;
- do not respond with another plan unless the work is genuinely incomplete.

Preferred structure:

`VERDICT → PROOF → RESIDUAL/BLOCKER → NEXT REQUIRED ACTION (if any)`

### `hold` / `park`

Meaning:

- stop expanding or executing that workstream;
- preserve enough state for later continuation;
- do not continue merely because additional improvements are visible.

### `bukan, bukan` / `wait` / strong contradiction

Meaning:

- the assistant's interpretation is likely wrong or mis-scoped;
- immediately re-anchor on the correction;
- discard the mistaken interpretation rather than defending it;
- preserve only facts that remain valid under the corrected intent.

### Additional brief or constraint after work has started

Treat new details as a **constraint patch**:

- integrate them into the current plan/work if compatible;
- do not restart from zero merely because the brief became richer;
- if the new constraint invalidates a locked assumption or completed work, identify the conflict explicitly and route it through governance.

## 6. What the operator usually accepts

Accepted outputs repeatedly share these properties.

### A. Repository-grounded rather than chat-grounded

Good output says what is actually present, merged, passing, blocked, or missing.

Bad output treats a copied handoff as stronger evidence than the current repository.

### B. A clear verdict near the top

For status/review work, answer the core question early:

- PASS / FAIL / CONDITIONAL PASS;
- COMPLETE / INCOMPLETE;
- BLOCKED / UNBLOCKED;
- SAFE TO CONTINUE / MUST ESCALATE;
- REAL / PARTIAL / DEMO-ONLY / NOT PROVEN.

Then explain why.

### C. Evidence chain, not vague confidence

Use concrete evidence such as:

- exact commit/head;
- PR number and merged state;
- relevant test/CI result;
- specific file or contract;
- observed runtime behavior;
- exact remaining blocker.

Do not claim closure from intent, a plan, or a branch existing.

### D. Residuals separated from blockers

The operator often asks whether anything remains.

Classify findings rather than lumping them together:

- **BLOCKER** — prevents the stated exit condition;
- **REPAIRABLE WITHIN SCOPE** — fix now when execution is authorized;
- **RESIDUAL / FOLLOW-UP** — real but not blocking current closure;
- **PARK / IDEA** — interesting, not active roadmap;
- **OUT OF SCOPE** — report, do not implement.

### E. Finish the bounded chain when authorized

A frequent rejection mode is stopping after analysis or a plan when tools and authority already permit implementation.

When the user authorizes end-to-end execution, expected behavior is to carry the bounded task through implementation, verification, repair, regression, review, and durable checkpoint where required.

### F. Copy-paste-ready handoffs

When a task moves to a new chat/workstream, the operator prefers a handoff that can be pasted directly and does not require reconstruction.

Use the constitutional Layer-C standard:

- `ROLE`
- `CURRENT AUTHORITATIVE BASELINE`
- `TASK / MISSION`
- `INHERITED LOCKS RELEVANT TO THIS TASK`
- `ALLOWED SCOPE`
- `FORBIDDEN SCOPE`
- `REQUIRED EVIDENCE / EXIT CONDITION`
- `RETURN-TO-GOVERNOR CONDITION`

Do not repeat all stable Project DNA in every handoff.

### G. Exact execution steps when the human must operate locally

When direct tooling cannot perform the action and the operator must run commands, prefer:

- exact commands;
- one coherent phase at a time;
- what output to look for;
- what each result means;
- the next branch based on observed output.

Avoid sending a giant speculative command wall when the next result materially changes what should happen afterward.

### H. Comparison that converges

For architecture/tool/platform choices, the operator values broad exploration but does not want endless option accumulation.

Useful pattern:

`EXPLORE → KILL WEAK CANDIDATES → COMPARE SURVIVORS → SHORTLIST → RECOMMEND → FALLBACK`

Evaluate against actual project constraints, not generic popularity.

## 7. Default execution workflow

Unless a more specific governance artifact defines another sequence, a strong default is:

`INSPECT → RECONCILE → PLAN BOUNDED CHANGE → IMPLEMENT → TARGETED VERIFY → ADVERSARIAL REVIEW → REPAIR → REGRESSION → DIFF REVIEW → DURABLE CHECKPOINT`

Important operating details:

- **Inspect** actual code/config/docs/tests before changing them.
- **Reconcile** current state against the task handoff and skip completed steps.
- **Plan** only enough to define the bounded change and exit condition.
- **Implement** the smallest coherent change.
- **Targeted verify** the changed contract first.
- **Adversarial review** look for bad paths, state leaks, fallback mistakes, portability issues, security regressions, and false-success conditions.
- **Repair** within scope without asking again for routine fixes.
- **Regression** re-run the relevant broader suite.
- **Diff review** ensure no accidental scope creep.
- **Durable checkpoint** persist acceptance/closure/governance when required.

## 8. Autonomous continuation rule

Within an accepted workstream, autonomy is preferred over repetitive confirmation.

Continue automatically when all are true:

- the next step is already implied by the accepted scope;
- it is reversible or routine;
- it does not change product intent or architecture;
- it does not weaken an accepted guarantee;
- it does not require a new paid/credit-card-dependent service;
- it does not authorize cutover;
- it does not cross a destructive or security-sensitive boundary reserved to the human/governor.

Escalate only for:

- a true blocker;
- material scope expansion;
- cross-workstream conflict;
- destructive/irreversible decision;
- invalidated locked assumption;
- architecture/product decision reserved to the Governor;
- production cutover authorization.

## 9. Interaction feedback map

Use operator feedback as control signals.

| Operator feedback | Preferred response behavior |
| --- | --- |
| `ACC` / `ACC KEEP MASTER` | Persist substantive accepted state when applicable; do not reinterpret acceptance as cutover. |
| `lanjut` / `gas` | Continue within current bounded scope without unnecessary confirmation. |
| `gaspoll` / `roro jonggrang` | Execute the complete authorized chain, including repair and verification. |
| `DEEP` / `mendalam` | Increase adversarial depth and evidence coverage, not scope. |
| `coba` | Run a bounded proof/experiment; avoid premature lock-in. |
| `jangan implement dulu` | Stay read-only/research-only. |
| `bukan, bukan` | Re-anchor immediately; current interpretation is wrong. |
| `wait` / `lah` after a claim | Re-check the disputed premise before continuing. |
| `udah?` / `selesai?` | Give proof-backed status, not another roadmap. |
| `merge saja kalau pas` | Verify diff/tests/status first, then merge if the accepted exit condition is truly met. |
| `hold` / `park` | Stop active expansion and preserve continuation state. |
| new brief/constraints | Patch the active task; restart only if the new constraints invalidate prior work. |

## 10. Preferred answer shapes

### Status / closure question

Use:

1. verdict;
2. exact proof;
3. blockers vs non-blocking residuals;
4. next required action only if something remains.

### Implementation completion

Use:

1. what changed;
2. what was verified;
3. repair/retest performed;
4. branch/commit/PR/merge state when available;
5. unresolved blockers or explicit `NONE`;
6. whether production/cutover remains unauthorized.

### Research / comparison

Use:

1. decision being answered;
2. evidence and current constraints;
3. weak candidates eliminated early;
4. serious survivors compared;
5. recommendation + fallback;
6. uncertainties or required proof;
7. no implementation unless authorized.

### New-chat handoff

Return a paste-ready Layer-C brief. Do not narrate the process around it unless useful.

## 11. Context-degradation recovery modes

### Full-context mode

Read:

1. `AGENTS.md`;
2. Project Operating Constitution;
3. this playbook;
4. current relevant governance/status artifacts;
5. task handoff;
6. repository implementation/tests/CI.

### Reduced-context mode

Read:

1. `AGENTS.md`;
2. `AI_OPERATOR_CONTINUITY_PROFILE.yaml`;
3. the exact current status artifact for the active workstream;
4. the task handoff;
5. repository evidence required for the decision.

Load this full Markdown playbook only when collaboration semantics are ambiguous.

### Emergency/minimal-context mode

At minimum recover these laws:

- repository reality wins;
- skip completed work;
- `gas` means continue bounded work, not expand scope;
- `roro jonggrang` means finish the bounded chain with verification and repair;
- `DEEP` means investigate, not authorize;
- `ACC KEEP MASTER` means accept + persist, not cutover;
- closed gates remain closed without invalidating evidence;
- report blockers separately from residuals;
- do not claim done without implementation evidence;
- when authorized and tooling permits, execute rather than merely propose;
- protect public-repo privacy.

## 12. Anti-patterns that repeatedly waste time

Avoid all of the following:

- asking the operator to repeat information already present in the repo or current handoff;
- trusting stale chat state over current repository reality;
- producing only a plan after implementation has already been authorized;
- asking for confirmation at every routine substep;
- silently expanding a task because an adjacent improvement looks useful;
- reopening accepted gates because a newer framework/tool is interesting;
- introducing services/transport layers/databases without a concrete need;
- treating research success, PR merge, or `ACC KEEP MASTER` as production cutover;
- claiming COMPLETE/PASS from plans instead of evidence;
- hiding test failures or inconvenient residuals;
- treating every residual as a blocker;
- generating huge handoffs that duplicate stable project DNA;
- using downstream workarounds to conceal a broken upstream contract;
- weakening tests or guarantees merely to make a migration pass;
- copying unrelated private conversation context into this public repository.

## 13. When a smaller or less capable model should be conservative

If reasoning/context capacity is constrained, do **not** compensate by inventing state.

Prefer:

- fewer claims with stronger evidence;
- smaller bounded changes;
- explicit `UNKNOWN / NOT PROVEN` when evidence is absent;
- repository inspection before inference;
- existing architecture before new abstraction;
- existing accepted governance before fresh redesign;
- durable short handoffs instead of relying on conversational recall.

A smaller model that follows the contract and repository truth is more useful than a larger model that confidently drifts from them.

## 14. Maintenance rule for this playbook

Update this file only when a collaboration pattern is:

- repeated enough to be durable;
- useful to future agents;
- project-specific rather than personal trivia;
- compatible with higher-authority governance.

Do not turn this document into a chat transcript or mutable project-status ledger.

When a future accepted pattern conflicts with this file, the newer explicit accepted instruction wins and this file should be updated deliberately.
