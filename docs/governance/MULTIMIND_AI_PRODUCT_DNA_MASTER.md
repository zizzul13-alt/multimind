# MULTIMIND — AI PRODUCT DNA MASTER

Status: **ACC KEEP MASTER**
Accepted by user: 2026-09-08
Updated acceptance: 2026-09-12 — conversation-first operation and independent Auto/Manual work-mode + AI/model selection locked.
Scope: durable product intent for MultiMind's AI/chat/debate/provider/capability layer.

This document records product DNA. It is not a claim that the current implementation already satisfies every item below, and it does not authorize production cutover.

## 1. Product identity

MultiMind is not intended to collapse into an ordinary single-model chatbot with fallback.

Its defining product is a **free-first, paid-optional, provider-independent, deliberation-centered, conversation-first AI workspace**. Multiple legitimate AI resources may independently contribute to the same task, inspectably deliberate/review, and produce a final synthesis while preserving the individual contributions and their provenance. Conversation may remain exploratory for as long as needed, then crystallize into bounded work without requiring the user to reconstruct context or surrender authority.

Inspiration includes the useful product ideas behind AI councils / multi-model comparison: many minds contribute, disagreement is useful, the system may recommend a result, and the human retains final judgment. MultiMind does not need to copy another product's architecture or feature set.

Economic doctrine:

`FREE-FIRST → PAID-OPTIONAL → PROVIDER-INDEPENDENT → DELIBERATION-CENTERED`

The baseline application must remain useful without requiring paid AI APIs. Reasonably priced paid APIs are welcome as optional participants/resources that raise the ceiling rather than define the floor. Price/free status is not an intelligence score and must not bias evaluation of answer quality.

## 2. Canonical user flow

Target product semantics:

`LOGIN PROFILE → RAW TASK/IDEA/CONVERSATION → AUTO OR MANUAL TASK MODE → AUTO OR MANUAL AI/MODEL SELECTION → PROMPT NORMALIZATION → OPTIONAL SEMANTIC COMPRESSION → CAPABILITY/AVAILABILITY FILTER → EXPLICIT PARTICIPANTS → INDEPENDENT CONTRIBUTIONS → DELIBERATION/REVIEW → JUDGE/SYNTHESIS → RELEASE GATE → FINAL ANSWER + HISTORY + USER VERDICT`

This is product truth. Exact implementation may evolve behind stable application boundaries.

Conversation-first operation does not require every message to become a task. Exploratory conversation may span topics. When intent becomes sufficiently explicit, the application may crystallize relevant conversation into bounded task state: objective, constraints, accepted/rejected decisions, open questions, authority, and exit condition. Crystallization must preserve user control and must not manufacture authority.

## 3. Participant contract

The central deliberation invariant is:

`N SELECTED PARTICIPANTS = N TRACEABLE PARTICIPANT ATTEMPTS/CONTRIBUTIONS`

Selecting multiple AIs means the user is asking multiple distinct participants to contribute, not asking one router to silently choose one of them.

Every attempted participant must retain honest provenance. If Gemini was selected and Gemini fails, history must say Gemini failed. A Groq fallback must never be presented as Gemini's contribution.

Fallback remains valuable reliability machinery, but availability recovery and participant identity are separate concerns.

A participant that fails may be degraded/skipped according to the accepted execution contract without destroying the successful participants' work.

## 4. Provider, model, participant, and utility are different concepts

Keep these concepts distinct:

`PROVIDER → MODEL → PARTICIPANT`

A provider is an inference/vendor/gateway boundary. A model is a replaceable inference resource. A participant is an identifiable mind/resource taking part in deliberation.

Therefore a gateway such as OpenRouter should not automatically be treated as one logical mind. A meaningful participant can instead be a curated model through OpenRouter, with both model and provider provenance retained.

Internal machinery is not automatically a participant. Examples include router/fallback machinery, UnifiedAgent compatibility machinery, DebateOrchestrator, compressor, prompt normalizer, judge/synthesizer, context processors, and release gates.

The same underlying model may serve both participant and utility roles, but those roles remain semantically distinct.

## 5. Deliberation and human judgment

MultiMind may recommend a winner or synthesize a final answer, but it must not erase the participants.

Participant answers/history are a core product feature rather than debug-only data.

The final answer may combine useful contributions from multiple participants, including a participant that did not win the system judgment.

System judgment and human judgment are separate truths. The product must permit semantics such as:

`SYSTEM WINNER = A`

`USER WINNER = B`

Both can coexist and be persisted. Historical user preference may inform soft recommendations but must not silently turn eligibility into an echo chamber or remove diversity/user choice.

Useful final-answer provenance may identify which participant supplied a base approach, correction, evidence, concern, or other material contribution.

## 6. Deliberation depth and token economics

MultiMind must preserve a useful middle ground between an ordinary one-model chatbot and an unnecessarily expensive all-to-all debate.

Conceptual execution depths may include:

- SOLO — one selected participant, direct response;
- PANEL / EFFICIENT — independent candidates plus synthesis;
- DELIBERATE — candidates plus bounded critique/review plus synthesis;
- DEEP DEBATE — deeper critique/revision/consensus, explicitly more expensive.

Exact names/algorithms may be refined, but a UI control representing rounds/depth must have real execution semantics rather than being decorative.

Before execution, where practical, MultiMind should make participant count and expected call/token/cost implications understandable to the user.

Deliberation/council is not a peer task mode. It is machinery that may operate within Chat/General, Thinking, Research, Coding, and future compatible work modes at an appropriate depth.

## 7. Task modes are capabilities, not cosmetic prompt styles

Coding, Research, and Thinking are task/capability modes. Chat/General is the ordinary conversational path.

- CODING should identify coding-ready participants and produce implementation/code-focused work.
- RESEARCH should identify research-ready participants and support evidence/cross-checking semantics appropriate to research.
- THINKING should support reasoning/planning/analysis without being silently equated to deep research.

Mode selection should determine eligibility/readiness and recommendations. It must not silently hide participant identity or remove user control.

Desired interaction:

`MODE → ELIGIBLE/READY PARTICIPANTS → RECOMMENDED ROSTER / SELECT ALL READY → USER MAY CHECK/UNCHECK`

Capability registry determines eligibility. Historical performance provides evidence. User preference provides personal judgment. These must not be collapsed into one field.

### 7.1 Auto/Manual work-mode selection

MultiMind may provide a Lazy/Auto policy that infers the appropriate work mode from the current conversation/task. Explicit manual mode selection remains available at all times and overrides automatic selection for the scope selected by the user.

Lazy/Auto is a selector/policy, not a replacement for task modes and not a new deliberation mode.

Automatic work-mode escalation does **not** imply automatic authority escalation. Selecting or inferring Coding may authorize coding-oriented reasoning/capability selection, but edit/commit/merge/deploy/delete/production authority remains governed independently by the accepted authority boundary.

## 8. Prompt Style is universal task normalization

Prompt Style is not merely decorative wording and does not select a provider.

Its intended purpose is to turn a short/raw idea into a common task specification that every selected participant receives consistently.

Example:

`raw idea: database + Coding + System Design → normalized requirements/schema/persistence/failure/migration/testing brief → same normalized brief to participants`

This reduces divergent interpretations of underspecified user prompts while preserving the user's intent.

## 9. Compressor is token-economy machinery

Compressor exists primarily to control multiplied token/context cost, not as a cosmetic summary feature.

It may semantically compress shared input/context and/or bound intermediate outputs while preserving material requirements, code, numbers, filenames, errors, constraints, evidence, and other task-critical information.

Historical use of Gemini as a compressor/workhorse was an economic optimization based on available quota/context, not an architectural law that Gemini must permanently occupy that role.

Compressor should remain an application-level utility capability that can evolve independently of participant identity.

## 10. Provider/model resource strategy

Providers/models/credentials/pricing/availability are replaceable resources behind MultiMind.

The system should prefer legitimate free allocations as its baseline resource pool and may incorporate optional paid resources when the user chooses them.

Free access must be classified more precisely than a boolean. Useful semantic classes include:

- permanent/free allocation;
- rate-limited free;
- monthly/free credit;
- development/testing-only free;
- temporary trial;
- paid optional.

Provider/model eligibility should account for capability, availability, terms, cost class, model/provider diversity, and current operational health.

MultiMind should seek **model diversity + provider diversity + capability diversity**, not inflate council size by running the same model family through many gateways and pretending they are independent minds.

A new API credential should conceptually enter through:

`REGISTER PROVIDER/RESOURCE → DISCOVER/EVALUATE MODELS → ASSIGN CAPABILITIES/ELIGIBILITY → CURATE PARTICIPANTS → EXPOSE TO USER`

not merely become another anonymous fallback slot.

### 10.1 Independent Auto/Manual AI/model selection

AI/model selection is a separate control axis from work-mode selection.

The product must support both:

- **AUTO AI/MODEL** — MultiMind selects an eligible available AI/model/resource according to task suitability, capability, availability, accepted cost/resource policy, operational health, diversity needs, and user preferences; and
- **MANUAL AI/MODEL** — the user explicitly selects the desired AI/model/participant identity.

The two axes may be combined independently. Examples include `Lazy + Auto AI`, `Research + Auto AI`, `Lazy + Claude`, and `Coding + Qwen`.

A manual AI/model choice outranks automatic model selection. If that requested identity is unavailable, MultiMind must report/offer an honest fallback according to accepted semantics rather than silently substituting another identity.

Adaptive resource routing remains distinct from AI/model identity. The same selected AI/model identity may have multiple legitimate provider/gateway routes, but route provenance must remain truthful. Provider/resource discovery must not invent upstream model identity when an endpoint only declares an unverifiable label.

Auto selection may change computational strategy across turns/stages as task requirements change, while preserving conversation/task continuity. It must obey hard user resource policies such as no-paid-API constraints.

## 11. Current provider doctrine / non-binding roster direction

The durable doctrine is more important than any September 2026 vendor roster because free tiers and models change.

Current research direction identifies Gemini, Groq, Cloudflare Workers AI, and curated OpenRouter free models as high-value free-first resource paths subject to real runtime/terms verification.

NVIDIA NIM is a useful development/test resource candidate. The user's current NVIDIA key explicitly states API testing use only and six-month validity, so it must not be treated as a mandatory production backbone. NVIDIA expiry/unavailability must be survivable.

Hugging Face, DeepSeek, Cohere, Cerebras, and other providers may remain lab/optional/paid/parked depending on actual access economics and terms. MultiMind completion does **not** require paying every provider merely to turn every adapter green.

Provider roster classifications are mutable Layer-B state and must be reverified when implementation/runtime decisions depend on them.

## 12. Credential ownership and multi-user resource pools

Separate users may own separate credential/resource pools. The safe default is user-owned resources remaining attributable to that user.

Credentials must remain server-side and secret.

Do not implicitly use multiple accounts/projects/keys to circumvent provider quotas or terms. Multiple API keys do not inherently imply multiple quotas. Shared resource pools, if ever enabled, must be explicit, provider-compliant, and preserve ownership/isolation.

Per-user profiles may include preferred modes, credential references/resource pools, sessions/files/memory, and soft recommendations. Preferences are defaults, not prohibitions: one user may still use Research or Coding even if another mode is their usual default.

## 13. Chatbot/fallback behavior remains useful but is not the product identity

A direct/solo answer path is legitimate when one participant is selected or a task explicitly calls for it.

Sequential fallback remains legitimate infrastructure for availability/reliability.

However, sequential fallback alone must never be represented as full MultiMind deliberation. The system must distinguish:

`ONE MIND, MANY FALLBACK PROVIDERS`

from

`MANY TRACEABLE MINDS DELIBERATING`.

UnifiedAgent may remain compatibility/reliability machinery where useful, but should not be presented as an additional seventh AI merely because it can route among providers.

## 14. Judge, synthesis, and release gate

Judge/synthesis and Release Gate are conceptually separate responsibilities.

The judge/synthesizer evaluates participant contributions and produces/recommends the final deliberative result.

The Release Gate evaluates whether the resulting output meets the accepted quality/safety/format/release criteria.

A release-quality mechanism must not erase the underlying debate/provenance.

## 15. History, persistence, memory, and presentation

Debate history, participant provenance, system judgment, user judgment, final synthesis, accepted decisions, and active task state are application truth and should remain persistable/reloadable according to the accepted persistence model.

Conversation history may span multiple topics/projects/tasks. Retrieval/indexing should therefore be capable of separating relevant topic/project/decision/task context rather than treating an entire conversation as one undifferentiated summary blob. Retrieved memory aids continuity; current repository/filesystem and authoritative governance remain superior implementation truth.

Presentation may render the same truth differently through Reflex/Design-DNA themes, but presentation must not invent or mutate participant/debate/task truth.

Design-DNA remains presentation intelligence. It may project deliberation as council, laboratory, courtroom, editorial room, or another archetype without moving deliberation business logic into the theme package.

## 16. Full-feature destination law

For this AI product layer, a proving slice or minimum acceptance test must never be described as full implementation.

Use explicit status vocabulary:

- TEST / PROOF
- MINIMUM ACCEPTANCE / GATE PASS
- PARTIAL IMPLEMENTATION
- FULL FEATURE IMPLEMENTATION
- FULL OPERATIONAL VERIFICATION
- PRODUCTION CUTOVER

Once a finite semantic contract is accepted for implementation, the implementation workstream should continue through implementation, targeted verification, adversarial review, repair, regression, UI/application integration, and real-runtime verification until the accepted scope is fully satisfied or an explicit blocker remains.

A blocker/residual must remain visibly OPEN/BLOCKED rather than being hidden behind a generic PASS label.

Full MultiMind does not mean every known provider in the world must be active. It means the accepted product contract is fully implemented and the mandatory active roster is operational; optional/paid/lab/parked resources may remain honestly classified as such.

## 17. Current known semantic concern — not yet an implementation claim

Repository investigation during reconstruction produced evidence that current deliberation behavior may not yet satisfy this accepted product DNA, including possible fixed-stage participant limits, fallback/participant attribution overlap, and a rounds value that may not alter actual execution depth.

Those are implementation findings to be independently verified against current repository reality before correction. This master document does not itself declare the owning closed Core gate reopened.

Per the Project Operating Constitution, concrete invalidating evidence should be routed to the Project Governor for a bounded decision rather than triggering a wholesale redesign.

## 18. Scope protection

This master does not authorize FastAPI, REST/RPC glue, CrewAI, LangChain, AutoGen, Dify, Quivr, new databases, microservices, or other historical framework ideas merely because they once appeared in roadmap discussions.

Preserve the current MultiMindApplication boundary, provider abstraction, persistence/security guarantees, Reflex direction, and Design-DNA separation unless independent accepted evidence requires a change.

Historical ideas such as code execution, autonomous self-loops, marketplace, visual workflow, and large-user scaling remain outside this lock unless separately accepted.

Auto mode/model selection, conversation crystallization, or richer retrieval do not by themselves authorize those parked features or new infrastructure.

## 19. Acceptance

`AI_PRODUCT_DNA = ACC KEEP MASTER`

Accepted addition 2026-09-12:

`WORK MODE SELECTION = AUTO OR MANUAL`

`AI/MODEL SELECTION = AUTO OR MANUAL`

These are independent axes. Manual selection overrides automatic selection within its selected scope. Deliberation/council remains cross-mode machinery rather than a peer mode. Automatic selection never implies automatic authority escalation.

This document supersedes conflicting informal/historical interpretations of MultiMind's AI/chat/debate product intent while preserving repository reality as the authority for what is actually implemented today.

It does not authorize production cutover.
