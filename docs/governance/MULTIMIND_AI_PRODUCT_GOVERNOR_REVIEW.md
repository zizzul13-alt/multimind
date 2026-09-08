# MULTIMIND — AI PRODUCT / DELIBERATION RECONCILIATION
## PROJECT GOVERNOR REVIEW BRIEF

Date: 2026-09-08
Status: **REVIEW REQUEST — AI PRODUCT DNA IS ALREADY ACC KEEP MASTER**
Companion master: `docs/governance/MULTIMIND_AI_PRODUCT_DNA_MASTER.md`

## Governor: read this distinction first

The user has now explicitly accepted the reconstructed **AI product intent** as durable Project DNA. The question is therefore **not** whether the Governor should invent or approve a new product vision.

The accepted product intent is already recorded in `MULTIMIND_AI_PRODUCT_DNA_MASTER.md`.

The Governor's job here is narrower:

1. reconcile that accepted product contract with current repository behavior;
2. determine whether concrete evidence is sufficient to open a **bounded semantic correction** despite the existing closed-Core law;
3. define the smallest coherent implementation package if correction is warranted;
4. preserve all unrelated closed gates and production/cutover protections.

Do not interpret this brief as a request for wholesale Core redesign, a provider deployment report, or a request to choose an AI vendor roster.

---

## 1. Accepted destination in one paragraph

MultiMind's defining AI product is a **free-first, paid-optional, provider-independent, deliberation-centered workspace**. If the user explicitly selects N AI participants, MultiMind should obtain N traceable participant attempts/contributions, preserve honest provider/model provenance and failures, allow bounded review/deliberation, synthesize/recommend a final result without erasing participant history, and preserve the user's ability to disagree with the system judge. Routing/fallback, compression, normalization, judge/synthesis, and release gates are supporting machinery, not substitute participants.

The full accepted detail is in the companion master and should be treated as the product semantic authority while repository/filesystem remains authority for implementation reality.

---

## 2. Why this reached Governor now

The project is already late in migration/deployment testing. During provider/API preparation, the user and workstream reconstructed the original reason MultiMind exists and compared it with current execution semantics.

The concern is not that the application lacks providers or that deployment is merely unfinished. The concern is that the mature infrastructure may currently realize **fallback-oriented chatbot behavior more completely than the intended multi-mind deliberation behavior**.

This was discovered before production cutover, which is the correct time to reconcile it.

---

## 3. Current repository evidence already observed

The following findings came from inspection of current repository components during reconstruction and must be reverified by the Governor/owning implementation workstream before modification:

### 3.1 Two execution paradigms coexist

`UnifiedAgent` / generic routing provides bounded sequential provider fallback and returns the first usable response. This is valid reliability machinery.

Named-provider execution routes through `DebateOrchestrator`, which implements staged candidate/judge behavior.

These are not equivalent product semantics.

### 3.2 Fixed-stage debate appears to constrain participant identity

Observed debate structure is four stages:

- stage 0: candidate/draft;
- stage 1: candidate;
- stage 2: candidate;
- stage 3: judge.

Stage primary selection is based on configured agent index, while each stage also has fallback access to other configured providers.

Potential consequences:

- six selected providers may not yield six primary participant contributions;
- providers beyond available primary stages may never act as primary participants;
- if a primary fails, another provider may service the stage;
- unless provenance explicitly records this distinction, the logical participant and actual executor can drift.

This directly touches the accepted invariant:

`N SELECTED PARTICIPANTS = N TRACEABLE PARTICIPANT ATTEMPTS/CONTRIBUTIONS`.

### 3.3 `debate_rounds` may currently be observational rather than behavioral

Application requests carry a debate-round count. The observed orchestrator records the value but appears to execute the same fixed four-stage structure rather than loop according to the selected depth.

Do not accept this as final until behavioral tests prove it, but if confirmed it means the visible Rounds control does not currently express real deliberation depth.

### 3.4 Composition still exposes historical compatibility machinery

Composition can build `unified` and named providers. Application routing sends unified/remote through a direct path while named providers use debate orchestration.

This is compatible with historical evolution: provider failover was implemented as stabilization machinery while the deeper collaboration concept remained only partially realized.

---

## 4. Historical evidence that matters

Historical MultiMind descriptions consistently contain the useful intent:

`multiple AI agents → independent work/review → best answer`.

Historical scaling notes explicitly described a desired transition from sequential agents toward collaboration, role-based work, and task delegation.

Historical architecture also accumulated UnifiedAgent, templates, skills, compressor, memory, release gates, remote APIs, and framework inspirations.

Governor should distinguish:

- **ORIGINAL/STILL-VALID INTENT** — multi-mind contribution, comparison, deliberation, final synthesis, history;
- **IMPLEMENTATION ARTIFACT** — sequential fallback used to make the system reliably answer;
- **HISTORICAL OPTIMIZATION** — Gemini as compressor/workhorse because quota/context economics were favorable;
- **SUPERSEDED** — large-user scaling assumptions, PlanetScale/FastAPI as default direction, Streamlit as production destination;
- **PARK** — code execution, marketplace, autonomous loops, visual workflow, broad framework adoption.

Do not revive historical frameworks merely because historical documents mention them.

---

## 5. Semantic model Governor should preserve

### Participant plane

`PROVIDER → MODEL → PARTICIPANT`

Provider/gateway identity and model identity should both be traceable. OpenRouter is not inherently one mind; a curated model via OpenRouter can be a participant.

### Utility plane

Router/fallback, prompt normalizer, compressor, judge/synthesizer, Release Gate, context processing, and UnifiedAgent compatibility behavior are utilities/machinery.

They may use AI models internally but are not automatically participant checkboxes.

### Task plane

Coding / Research / Thinking are capability/task modes.

They should help determine READY/ELIGIBLE participants and recommended rosters while retaining explicit user check/uncheck control.

### Prompt plane

Prompt Style is common task normalization. The same normalized task should be supplied to participants; it should not secretly choose the provider.

### Deliberation plane

One selected participant can legitimately be SOLO.

Multiple selected participants should produce independent traceable contributions before whatever bounded critique/synthesis policy is selected.

System winner and user winner are distinct and may disagree.

---

## 6. Provider economics are context, not the Core decision

Accepted doctrine is free-first and paid-optional. The mandatory production roster should be intentionally finite and provider-compliant; full MultiMind does not require every adapter/vendor to be paid/active.

Current preparation facts include Groq already configured on Railway and an NVIDIA API testing key entered as `MULTIMIND_NVIDIA_KEY`. The NVIDIA key explicitly has six-month validity and testing-only status, so NVIDIA is a development/test resource rather than a production dependency. Gemini, Cloudflare, and OpenRouter credential activation remains separate operational work.

Do not let mutable September-2026 provider availability define the durable deliberation architecture.

---

## 7. Exact Governor decision requested

Please determine whether the repository evidence is sufficient to authorize a narrowly scoped workstream such as:

**MULTIMIND DELIBERATION SEMANTIC CORRECTION**

This should be treated as a bounded exception/reopening only to the extent concrete evidence demonstrates current Core behavior violates the newly persisted accepted AI Product DNA.

It must NOT reopen Security, Hardening/Reliability, persistence, Reflex platform selection, Design-DNA research/migration, provider abstraction wholesale, or deployment architecture.

If evidence is insufficient, require behavioral proof first rather than rejecting the accepted product contract.

---

## 8. Required pre-implementation behavioral matrix

Before broad code changes, prove current behavior for at least:

- 1 selected participant;
- 2 selected participants;
- 3 selected participants;
- 6 selected participants;
- selected participant success;
- selected participant failure;
- fallback attribution after participant failure;
- Rounds/depth values 1, 2, and 3;
- Coding mode;
- Research mode;
- Thinking mode;
- Prompt Style normalization;
- Compressor behavior;
- judge/synthesis;
- Release Gate;
- debate/history persistence and reload;
- provider/model provenance.

For each item produce:

`ACCEPTED INTENT → CURRENT BEHAVIOR → GAP/PASS → SMALLEST COHERENT FIX`.

The matrix is diagnostic evidence, not an excuse to stop at a proving slice.

---

## 9. Implementation destination if Governor authorizes it

The user explicitly rejected a pattern where a minimum proof/gate is reported as though the feature were complete.

If implementation is authorized, the destination is **FULL FEATURE IMPLEMENTATION against the finite accepted semantic contract**, followed by full operational verification of the mandatory active provider roster.

A sensible bounded destination should include, where confirmed by the contract/matrix:

- N selected = N traceable participant attempts/contributions;
- honest participant failure/provenance;
- fallback that preserves reliability without falsifying identity;
- real task-mode capability semantics;
- prompt normalization;
- token-economy compressor semantics;
- explicit/manual participant control plus readiness recommendations;
- meaningful deliberation depth;
- judge/synthesis;
- separate Release Gate;
- inspectable debate history;
- system verdict and user verdict;
- persistence/reload;
- provider/model provenance;
- token/call/cost observability appropriate to the UI contract;
- graceful degradation;
- application-boundary compliance;
- Reflex/presentation projection without duplicated business truth;
- targeted + adversarial + regression verification;
- real-runtime verification against the mandatory active roster.

The workstream should autonomously repair in-scope residuals and continue until the accepted scope is complete or a genuine blocker/material scope expansion appears.

---

## 10. Status vocabulary is mandatory

Do not use generic `PASS` as a synonym for finished product.

Use:

- `TEST / PROOF`
- `MINIMUM ACCEPTANCE / GATE PASS`
- `PARTIAL IMPLEMENTATION`
- `FULL FEATURE IMPLEMENTATION`
- `FULL OPERATIONAL VERIFICATION`
- `PRODUCTION CUTOVER`

Any unimplemented accepted capability must remain visibly OPEN/BLOCKED/DEFERRED with its effect on completion stated.

---

## 11. Architecture protections

Even if semantic correction is authorized:

- keep `MultiMindApplication` as presentation-independent boundary;
- do not introduce HTTP/REST/RPC merely as frontend glue;
- preserve provider abstraction;
- preserve existing persistence/user isolation/security guarantees;
- preserve Reflex production-host direction;
- preserve Streamlit rollback/reference until cutover;
- keep Design-DNA as presentation intelligence;
- do not make private DNA required for Core correctness;
- do not introduce CrewAI/LangChain/AutoGen/Dify/Quivr/FastAPI/new DBs without separate concrete necessity and governance approval.

Prefer the smallest coherent correction to existing components rather than a rewrite.

---

## 12. Current deployment meaning

The current deployment/testing candidate remains useful as a baseline and should not be discarded merely because semantic correction may be needed.

However, until the accepted AI product contract is reconciled and the mandatory active provider roster is operationally verified:

`DEPLOYMENT_LEVEL = TEST / PARTIAL`

`AI_PRODUCT_FULL_FEATURE_IMPLEMENTATION = NO`

`FULL_PROVIDER_RUNTIME_MATRIX = NO`

`READY_FOR_NORMAL_USE AGAINST ACCEPTED FULL AI PRODUCT DNA = NO`

`PRODUCTION_CUTOVER_AUTHORIZED = NO`

---

## 13. Requested Governor output

Return one of:

### A. ACC — BOUNDED SEMANTIC CORRECTION AUTHORIZED

Persist the bounded reopening/exception, owning workstream, exact implementation destination, inherited locks, required behavioral evidence, and return condition.

### B. DEEP — MORE BEHAVIORAL EVIDENCE REQUIRED

Specify only the missing evidence required to decide. Do not reopen unrelated architecture research.

### C. REJECT BOUNDED REOPENING

Only if repository evidence proves current implementation already satisfies the accepted AI Product DNA or if another accepted current artifact supersedes the product contract. Cite that evidence explicitly.

Production cutover remains separately reserved regardless of A/B/C.
