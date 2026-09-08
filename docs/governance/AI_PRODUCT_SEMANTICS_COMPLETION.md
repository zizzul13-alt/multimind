# MULTIMIND — AI PRODUCT SEMANTICS COMPLETION

Status: **USER-AUTHORIZED / IMPLEMENTATION OPEN**
Date: 2026-09-09
Baseline: `main@75711f5ac8a6255dc65d40c94c16705ab2b32d25`
Authority: `docs/governance/MULTIMIND_AI_PRODUCT_DNA_MASTER.md`

## Mission

Complete the remaining accepted AI Product DNA semantics that were intentionally outside the bounded Deliberation Semantic Correction.

The previous workstream remains CLOSED and is not reopened. Its participant identity, rounds, judge/synthesis, Release Gate, persistence, and resource-boundary guarantees are entering invariants.

Railway final integration remains HOLD.

## Repository findings at entry

Current repository evidence shows material semantic drift still exists:

1. `ChatRequest.session_mode` defaults to `coding` and is passed to providers/debate, but there is no application-level capability registry that makes Coding/Research/Thinking determine participant eligibility/readiness/recommendation.
2. `selected_skill` is forwarded to `DebateOrchestrator`; `SkillsManager` is a prompt-prefix system. This is useful but is not the accepted universal Prompt Style normalization contract.
3. `PromptCompressor` is hard-wired through the Gemini agent in `MultiMindApplication.execute_chat`, while accepted DNA defines compressor as provider-independent application utility machinery.
4. Compression currently trusts `gemini_agent.compress_prompt()` output without an application-level preservation contract for code, numbers, filenames, errors, constraints, and evidence.
5. Current application routing receives explicit active agents, but mode/capability eligibility and recommended roster are not first-class application truth.

## Finite implementation contract

Implement the smallest coherent completion of the accepted product semantics:

### A. Task modes / capability registry

- Canonical modes: `coding`, `research`, `thinking`.
- Capability/readiness is application truth, separate from historical performance and user preference.
- A mode resolves eligible/ready participants and a deterministic recommended roster from currently configured resources.
- User explicit participant selection remains authoritative; mode recommendations never silently replace/check/uncheck the user's explicit roster.
- Execution records mode and eligibility/recommendation provenance.
- No hidden provider consumption.

### B. Prompt Style / normalization

- Prompt Style is a common task-normalization layer, not provider selection.
- The same normalized task is supplied to every selected participant.
- Skills/templates may remain compatibility inputs, but their semantics must be reconciled behind the application normalization boundary rather than independently changing provider identity.
- Normalization must preserve the raw user prompt in persisted truth and expose normalized prompt/provenance separately.

### C. Compressor

- Compressor is an application utility capability, not permanently Gemini-specific.
- Utility provider selection must be explicit/bounded and attributable; absence/failure degrades to the uncompressed normalized prompt.
- Compression must have a preservation guard for task-critical literals/structures including code, numbers, filenames/paths, errors, explicit constraints, and evidence/source markers where present.
- Compression may reduce multiplied context/token cost but must never silently change participant roster or task mode.
- Compression metadata (applied/not applied, utility provider when used, token savings where known, fallback reason) is application truth.

### D. Integration / persistence / presentation

- Canonical flow becomes operationally meaningful: raw task → mode → normalization → optional compression → capability/readiness → explicit participants → deliberation.
- Preserve `MultiMindApplication` as the boundary.
- Persist enough structured metadata to reload/audit raw prompt, normalized/effective prompt semantics, mode, capability/recommendation state, compressor state, participants, and debate provenance without creating a second presentation truth.
- Reflex/Streamlit may project this truth but must not implement separate mode/normalizer/compressor business logic.

## Verification matrix

At minimum test:

- Coding, Research, Thinking each produce distinct semantic mode instructions and capability results;
- eligible vs ineligible/unavailable participant classification;
- recommended roster deterministic and explicit user override preserved;
- zero explicit participants remains zero;
- same normalized prompt reaches all participants;
- prompt-style/skill compatibility does not select providers;
- raw prompt remains intact for history;
- compressor disabled;
- compressor enabled and successful;
- compressor utility unavailable/fails → safe uncompressed degradation;
- preservation of code blocks, numeric literals, filenames/paths, error strings, MUST/DO NOT constraints, and source/evidence markers;
- compressor cannot alter participant identity/roster;
- no hidden paid/unselected provider use;
- persistence/reload/projection metadata;
- existing deliberation semantic correction regression remains green;
- full Python regression + RJ5 + RJ6 + Final Gate on exact branch head, expected-head merge, then exact-main verification.

## Scope protection

Do not add FastAPI, REST/RPC glue, CrewAI, LangChain, AutoGen, new databases, microservices, external prompt services, or provider redesign.

Do not reopen Security, persistence, Design-DNA, Reflex platform selection, or the closed Deliberation Semantic Correction absent concrete invalidating evidence.

## Exit condition

Continue inspect → implement → targeted/adversarial test → repair → full regression → diff review until known in-scope residuals are zero.

Only then merge with expected-head guard and verify exact `main`.

STOP before final Railway integration. Production cutover remains unauthorized.
