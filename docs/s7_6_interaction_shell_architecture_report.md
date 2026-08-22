# S7.6 INTERACTION SHELL ARCHITECTURE REPORT

## 1. CURRENT MAIN VERIFIED
- **Commit SHA:** `4505acc1b3a5fc235c1c377300459e332852d360` (Merge pull request #28 from zizzul13-alt/plan-archetype-projection-refactor-17372634941333159536)
- **Inspected Files:**
  - `app.py`: Main application layout, state initialization, navigation (`show_sidebar()`), session view (`show_session()`), composer surface (`show_new_chat()`), execution processing (`process_chat()`), and entry point routing (`main()`).
  - `ui/presentation/resolver.py`: Archetype definitions, registry, safe fallback resolution (`resolve_archetype()`), and dispatch entry point (`render_archetype()`).
  - `ui/presentation/projections.py`: Projections for all 7 canonical archetypes (`render_chat_first`, `render_command_center`, `render_ai_workspace`, `render_ai_research_lab`, `render_agent_canvas`, `render_terminal_hacker`, `render_minimal_saas`).
  - `ui/presentation/models.py`: Immutable read-only `PresentationSnapshot`, `SessionSnapshot`, `MemorySnapshot`, `ChatSnapshot`, and `DebateDetailSnapshot`.
  - `ui/presentation/builder.py`: Snapshot factory (`build_presentation_snapshot()`).
  - `ui/foundation.py`, `ui/tokens.py`, `ui/style.css`: UI tokens, custom properties, status badges, card containers, and layout utilities.
  - `ui/dna/*`, `ui/themes/*`: Design DNA, mapped CSS themes, and registration bootstrap.
  - `docs/*`: Architecture documentation suite (`PLATFORM_CAPABILITY_AUDIT.md`, `RESPONSIVE_AUDIT.md`, `UI_AUDIT.md`, `design_dna.md`).
  - `tests/*`: 72 passing tests across architecture, projections, resolver, theme engine, and memory persistence.

---

## 2. CURRENT INTERACTION LIFECYCLE
The exact repository-backed user interaction flow on CURRENT MAIN proceeds through 9 sequential stages:

1. **Navigation / Session Selection:**
   - User opens sidebar (`show_sidebar()`).
   - Session buttons (`st.button(label, key=unique_key)`) trigger state update: `st.session_state.current_session = s`, followed by memory hydration `get_or_hydrate_session_memory()` and `st.rerun()`.
   - Archetype View selector in sidebar `st.selectbox("📐 Archetype View", ...)` sets `st.session_state.active_archetype`.

2. **Session View Rendering (Archetype-Aware):**
   - In `show_session()`, `build_presentation_snapshot()` creates an immutable `PresentationSnapshot`.
   - `render_archetype(active_archetype, snapshot)` routes to the corresponding projection renderer in `ui/presentation/projections.py`.
   - The session view renders history, metrics, and an archetype action button (`"➕ New Chat"`).

3. **Initiate New Turn / Interaction Surface Entry:**
   - User clicks `"➕ New Chat"` in the archetype projection container.
   - Button callback executes `st.session_state.new_chat = True` and calls `st.rerun()`.
   - `main()` evaluates `if st.session_state.new_chat:` and renders `show_new_chat()`.

4. **Composer Surface / Prompt Configuration (GLOBAL SURFACE CONVERGENCE):**
   - `show_new_chat()` renders a shared screen regardless of `st.session_state.active_archetype`.
   - **Template & Mode Controls:** `st.selectbox("📋 Template")` and `st.radio("Chat Mode", ["🧵 Continue", "📌 Standalone"])`.
   - **Prompt Input:** `st.text_area("Prompt:", height=150, key="prompt_main")`.
   - **Attachments:** `st.file_uploader("📎 Files", accept_multiple_files=True, key="new_chat_files")`.
   - **Token & Cost Metrics:** `TokenCounter.estimate_total(...)` rendered via `card_container()`.
   - **Action Triggers:** Primary button `"🚀 Send"` and secondary button `"❌ Cancel"`.

5. **Submission Trigger:**
   - Clicking `"🚀 Send"` validates `if prompt or uploaded_files:` and calls `process_chat(prompt, uploaded_files, context_mode)`.
   - Clicking `"❌ Cancel"` sets `st.session_state.new_chat = False` and calls `st.rerun()`.

6. **Processing & Execution Feedback:**
   - `process_chat()` enters `with st.spinner("🤖 Agents debating..."):`.
   - Optional prompt compression via `PromptCompressor.compress()`.
   - File extraction and hydration via `FileHandler.handle()`.
   - Context assembly from session memory (`memory.get_context()`).
   - Agent orchestration (`DebateOrchestrator.debate()` or `UnifiedAgent` / `RemoteAgent` dispatch).

7. **Database & Memory Persistence:**
   - `chat_data` dictionary populated and persisted via `persist_chat_and_update_memory()`.

8. **Result Transition:**
   - `st.session_state.new_chat = False`
   - `st.success("✅ Debate complete!")`
   - `st.rerun()` triggers full app rerun.

9. **Return to Archetype Session Projection:**
   - `main()` routes to `show_session()`, rendering updated snapshot through `render_archetype()`.

---

## 3. SHARED SURFACE INVENTORY

| Interaction Surface | Current Repository Implementation Location | Classification | Current Convergence Risk |
| :--- | :--- | :--- | :--- |
| **Sidebar / Navigation** | `app.py` -> `show_sidebar()` | **MIXED** (App Navigation + Global Settings) | High. Global sidebar contains session list, new session creator, system settings, backup/restore, theme, and archetype selectors without reflecting active archetype identity. |
| **New Session Creator** | `app.py` -> `show_sidebar()` (`st.expander("➕ New Session")`) | **APPLICATION TRUTH** | Low. Pure data creation (`db.create_session()`). |
| **Composer / Prompt Entry** | `app.py` -> `show_new_chat()` | **PRESENTATION** | Critical. Overwrites session projection view completely with generic 150px text area, global template picker, radio buttons, and standard file uploader. |
| **Template & Mode Selector** | `app.py` -> `show_new_chat()` | **MIXED** | High. Mode (`continue` vs `standalone`) is application truth, but selection UI control arrangement is strictly presentation. |
| **Token & Cost Estimator** | `app.py` -> `show_new_chat()` | **PRESENTATION** | Medium. Pure diagnostic calculation on unsubmitted user prompt. |
| **Processing / Spinner** | `app.py` -> `process_chat()` (`with st.spinner()`) | **PRESENTATION** | Critical. Replaces viewport with generic Streamlit loading spinner during agent debate, obscuring archetype identity during execution. |
| **Backend Execution** | `app.py` -> `process_chat()` (DebateOrchestrator) | **APPLICATION TRUTH** | None. Single authoritative orchestration path. |
| **Persistence & Hydration** | `app.py` -> `persist_chat_and_update_memory()` | **APPLICATION TRUTH** | None. Single database and memory state path. |
| **Result Transition / Rerun** | `app.py` -> `process_chat()` -> `st.rerun()` | **APPLICATION TRUTH** | Low. Rerun clears transient submission state and triggers archetype re-render. |

---

## 4. PROPOSED SMALLEST PRESENTATION SEAM

To eliminate interaction shell convergence without duplicating backend logic or state models, we introduce an **Interaction Shell Presentation Seam** located in `ui/presentation/shell.py`.

### Architecture Seam Boundary & Ownership

```
                   ┌──────────────────────────────────────────────┐
                   │          APPLICATION / BACKEND TRUTH         │
                   │  - Session DB & Memory Persistence           │
                   │  - Single DebateOrchestrator Execution       │
                   │  - Single Interaction State Model            │
                   └──────────────────────┬───────────────────────┘
                                          │
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │       INTERACTION SHELL ADAPTER LAYER        │
                   │           (ui/presentation/shell.py)         │
                   │  - Pure presentation dispatch                │
                   │  - Accepts InteractionContext snapshot       │
                   │  - Dispatches to Archetype Shell Policy       │
                   └──────────────────────┬───────────────────────┘
                                          │
               ┌──────────────────────────┼──────────────────────────┐
               ▼                          ▼                          ▼
    ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
    │  Chat-First Shell  │     │ Command Center     │     │ Minimal SaaS Shell │
    │  - Bottom Composer │     │ - Operational Bar  │     │ - Direct Task Card │
    │  - Continuous Feed │     │ - Action Matrix    │     │ - Progressive Disc.│
    └────────────────────┘     └────────────────────┘     └────────────────────┘
```

### Seam Specifications:
1. **Unchanged Backend Handler:**
   - `process_chat(prompt, files, mode)` remains the ONE authoritative backend execution handler in `app.py`.
2. **Immutable Interaction Context:**
   - Introduce `InteractionContext` dataclass in `ui/presentation/models.py`:
     ```python
     @dataclass(frozen=True)
     class InteractionContext:
         session: SessionSnapshot
         memory: Optional[MemorySnapshot]
         active_archetype: str
         new_chat_active: bool
         prompt_text: str
         selected_template: Optional[str]
         chat_mode: str
         uploaded_files: List[Any]
         is_processing: bool
     ```
3. **Archetype Shell Dispatcher:**
   - Introduce `render_interaction_shell(ctx: InteractionContext, callbacks: ShellCallbacks)` in `ui/presentation/shell.py`.
   - `ShellCallbacks` contains pure function callbacks for `on_submit`, `on_cancel`, `on_session_select`, `on_new_session`.
4. **Placement Rule:**
   - In `app.py`, instead of hardcoded conditional `if st.session_state.new_chat: show_new_chat() else: show_session()`, `app.py` builds `InteractionContext` and calls `render_interaction_shell()`.

---

## 5. ARCHETYPE INTERACTION MATRIX

| Archetype | Navigation Morphology | Composer Relationship | Processing Presentation | Result / Continuation Relationship | Desktop Morphology (1440px) | Mobile Morphology (390px) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. chat_first** | Standard left sidebar with session list & quick creator. | **Conversation-Attached Composer:** Positioned directly below the continuous feed in central reading column. | **Stream Indicator:** Active debate status indicator inline within conversation thread. | Appends new response to feed; automatically focuses input for next turn. | Single wide reading column with anchored bottom composer. | **FOCUS:** Full-width conversation stream with sticky bottom prompt bar. |
| **2. command_center** | Collapsible system drawer with high-density metrics badge header. | **Mission / Operational Action Surface:** Command-bar overlay with parameter dials and agent target indicators. | **Live Matrix Activity:** Real-time pulse badges on parallel agent grid columns. | Results populate execution log matrix; immediate operational trigger available. | Multi-column grid (System Status + Agent Matrix + Operational Console). | **SEQUENCE:** Stacked metrics top -> agent logs middle -> action bar bottom. |
| **3. ai_workspace** | Workspace object navigator sidebar with folder hierarchy. | **Anchored Work Object Composer:** Embedded pane attached to current active work object. | **Object Generating Overlay:** Progress card on target workspace object. | New object created or active object updated in workspace grid. | Dual-pane split screen (Active Object Left, Context Orbit Right). | **REFLOW:** Tabbed toggle between Active Object and Context Orbit. |
| **4. ai_research_lab** | Research query history sidebar with evidence indicators. | **Research Query Surface:** High-visibility query bar with claim filters & template variable fields. | **Evidence Assembly Indicator:** Step-by-step hypothesis synthesis progress. | Synthesized conclusion banner updated; claims linked to evidence tabs. | Top Query Bar + Center Thesis + Bottom Evidence Tabs. | **DISCLOSE:** Thesis prominent on top; evidence tabs collapsible below. |
| **5. agent_canvas** | Canvas node directory sidebar with workflow list. | **Input / Trigger Node Composer:** Styled as execution workflow entry node. | **Topology Flow Animation:** Node highlight along active agent workflow path. | Appends output node to canvas topology stream; ready for next step trigger. | Vertical step topology flow diagram with active step details. | **SEQUENCE:** Accordion sequence step flow with interactive step tabs. |
| **6. terminal_hacker** | Monospaced sys-log sidebar drawer. | **Command Line / Intent Surface:** Console prompt line (`$ MM_EXEC --mode coding`). | **Monospaced Stream Terminal:** Live execution log output lines (`[SYS_EXEC...]`). | Append log block to stream in monospaced sanctuary; clear console input. | Full-width high-contrast dark terminal stream container. | **FOCUS:** Monospaced stream full-screen, simple terminal command prompt. |
| **7. minimal_saas** | Compact header navigation / minimal sidebar. | **Direct Task Composer:** High-contrast single task input card. | **Clean Task Progress:** Minimalist horizontal loader line below card. | Active task output updates in main focus card; history moved to disclosure drawer. | Centered clean task container (max-width 800px). | **PRIORITIZE:** Direct single-column task card; all utility drawers closed. |

---

## 6. SHARED VS ARCHETYPE-SPECIFIC CONTRACT

### SHARED CONTRACT (MUST Remain Authoritative & Invariant Across All Archetypes)
1. **Single Database & Session Model:** SQLite database schema (`DatabaseManager`), session UUIDs, chat records, and memory snapshots (`get_or_hydrate_session_memory`).
2. **Single Orchestration Backend:** `DebateOrchestrator`, `UnifiedAgent`, and `RemoteAgent` generation pipelines. No archetype-specific execution branches.
3. **Single System State Machine:** Session initialization, user authentication, active agents list, debate rounds count, and skill selector values.
4. **Single Quality & Release Gate:** `ReleaseGate` scoring algorithm (0-10) and status badges.
5. **Token Accounting & Pricing:** `TokenCounter` estimation and exact cost calculation rules.

### ARCHETYPE-SPECIFIC CONTRACT (MAY Vary by Archetype Composition Policy)
1. **Composer Surface Layout & Placement:** Inline feed composer vs top query bar vs command modal vs direct task card.
2. **Navigation Surface Morphology:** Sidebar density, collapsible drawers, or minimal header navigation.
3. **Processing Visual Presentation:** Inline thread spinner vs live matrix pulse vs monospaced log lines vs clean progress bar.
4. **Information Hierarchy & Disclosure:** Immediate full feed vs tabbed evidence traversal vs progressive disclosure expanders.
5. **Spatial Placement & Column Ratios:** Centered reading sanctuary vs grid workspace vs terminal stream.

---

## 7. STATE OWNERSHIP

| State Variable | State Type | Storage Location | Duplication Rule |
| :--- | :--- | :--- | :--- |
| `user_id`, `user` | **Persisted Application State** | `st.session_state` | Authoritative. No local duplication. |
| `current_session` | **Application-Session State** | `st.session_state['current_session']` | Authoritative. Derived read-only in `SessionSnapshot`. |
| `memories` | **Persisted Application State** | `st.session_state['memories']` | Authoritative. Hydrated from SQLite DB. |
| `active_archetype` | **Presentation State** | `st.session_state['active_archetype']` | Presentation-only controlling view composition. |
| `active_theme` | **Presentation State** | `st.session_state['active_theme']` | Presentation-only controlling CSS token mapping. |
| `new_chat` | **Transient Execution State** | `st.session_state['new_chat']` | Transient flag for composer surface entry. |
| `prompt_text` / `prompt_main` | **Transient Execution State** | `st.session_state['prompt_main']` | Unsubmitted prompt buffer. Discarded on submit/cancel. |
| `selected_template` / `template_variables` | **Transient Execution State** | `st.session_state['selected_template']` | Form staging buffer. |
| `active_agents`, `debate_rounds`, `selected_skill` | **Application-Session State** | `st.session_state` | Global execution configuration parameters. |
| `is_processing` | **Transient Execution State** | Transient execution wrapper | Local runtime state during `process_chat()`. |

---

## 8. STREAMLIT CAPABILITY MATRIX

| Required Interaction Behavior | Classification | Evidence / Technical Reason | Smallest Workaround / Solution |
| :--- | :--- | :--- | :--- |
| **Archetype-aware Composer Placement** | **GREEN** | Native Streamlit containers (`st.container(key=...)`) and layout primitives (`st.columns`) permit placing text areas and submit buttons anywhere in the DOM layout. | Use presentation adapter `ui/presentation/shell.py` to route composer rendering inside active archetype container. |
| **Custom Input Key Bindings (e.g., Cmd+Enter to Send)** | **YELLOW** | Streamlit `st.text_area` requires button click or ctrl+enter form submission native to browser. | Wrap prompt composer in `st.form(key=..., clear_on_submit=False)`. |
| **Distinct Processing Feedback (Non-blocking / Custom Loaders)** | **YELLOW** | Native `st.spinner()` blocks viewport execution. Custom status containers with CSS animations provide distinct visual feedback without blocking layout structure. | Render archetype-specific progress container using `st.empty()` or `st.status()` container before invoking backend execution. |
| **Responsive Column Reflow (Desktop to Mobile)** | **GREEN** | Streamlit columns automatically stack vertically on screens < 640px. CSS media queries in `ui/style.css` handle container adjustments. | Applied via `ui/style.css` custom classes (`.mm-flex-between`, responsive containers). |
| **Persistent Bottom Fixed Composer Bar (Chat-First / Terminal)** | **ORANGE** | Streamlit lacks native fixed bottom bar container API. Modifying CSS position `fixed` on `st.container` can cause overlapping content or scrollbar glitches if DOM structure changes. | Use CSS targeted container keys (`[data-testid="stVerticalBlock"] > div:has(div[key*="composer"])`) with carefully bounded padding-bottom on feed container. |
| **Real-time Live Streaming Output during Multi-Agent Debate** | **YELLOW** | `st.write_stream()` or `st.empty()` updates permit real-time text streaming per round without custom components. | Use `st.empty()` placeholders inside archetype processing containers during debate execution rounds. |
| **Full Navigation Overhaul (Replacing Streamlit Sidebar completely)** | **RED** | Streamlit sidebar is hardcoded in core frontend DOM layout (`[data-testid="stSidebar"]`). Hiding sidebar completely breaks native mobile menu toggle button and state management. | **DO NOT REPLACE SIDEBAR.** Preserve native Streamlit sidebar for application navigation; apply CSS styling and archetype presentation wrappers. |

---

## 9. IMPLEMENTATION SURFACE

### Existing Files Requiring Modification in Future Implementation Session:
1. `app.py`:
   - Refactor `main()`, `show_sidebar()`, and `show_new_chat()` to delegate shell presentation to `ui/presentation/shell.py`.
   - Keep `process_chat()` as the single authoritative backend execution method.
2. `ui/presentation/models.py`:
   - Add `InteractionContext` dataclass for immutable state snapshots.
3. `ui/presentation/resolver.py`:
   - Export shell presentation resolution utilities alongside existing session renderer resolvers.
4. `ui/style.css`:
   - Add interaction shell CSS utility rules for composer placement, command surfaces, and responsive breakpoints (1440px, 768px, 390px).

### Proposed New Modules (Presentation-Only):
1. `ui/presentation/shell.py`:
   - Main entry point for archetype-aware interaction shell rendering (`render_interaction_shell()`).
   - Dispatches to archetype-specific shell composers.
2. `ui/presentation/shells/`:
   - `chat_first_shell.py`: Bottom-anchored conversation composer and thread-integrated status.
   - `command_center_shell.py`: Operational action modal / command drawer surface.
   - `ai_workspace_shell.py`: Object-anchored action pane.
   - `ai_research_lab_shell.py`: Query surface with claim parameters.
   - `agent_canvas_shell.py`: Node input trigger surface.
   - `terminal_hacker_shell.py`: Command console prompt surface.
   - `minimal_saas_shell.py`: Direct task card composer surface.
3. `docs/s7_6_interaction_shell_architecture_report.md`:
   - Documentation of S7.6 interaction shell architecture, contracts, and state ownership models.

---

## 10. TEST OBLIGATIONS

The future implementation session must create permanent unit and integration tests under `tests/`:

1. **`tests/test_ui_interaction_shell.py`:**
   - Verify `InteractionContext` immutability and factory builder.
   - Verify that all 7 archetypes execute `render_interaction_shell()` without exceptions across all states (`new_chat=True`, `new_chat=False`, `is_processing=True`).
   - Verify fallback behavior when an unknown archetype ID is provided to the shell resolver.
2. **`tests/test_interaction_architecture_contracts.py`:**
   - Test assertion verifying `process_chat()` backend execution state and database persistence logic remain 100% identical across all 7 archetypes.
   - Test assertion confirming no duplicate database or memory mutations occur during interaction shell dispatch.
3. **`tests/test_shell_responsive_morphology.py`:**
   - Verify key container key generation and markup integrity for desktop, tablet, and mobile presentation modes.

---

## 11. RISKS / STOP CONDITIONS

### Stop Condition Check:
1. **Backend Semantics:** Did S7.6 require changing backend execution semantics? **NO.** Execution truth remains 100% single-path via `DebateOrchestrator` and `process_chat()`.
2. **PR #28 Architecture Contradiction:** Does CURRENT MAIN contradict PR #28? **NO.** Main commit `4505acc1b3a5fc235c1c377300459e332852d360` cleanly implements snapshot projections.
3. **Duplicated Implementations:** Does proposed solution duplicate execution paths seven times? **NO.** ONE backend execution handler (`process_chat`) and ONE state model (`InteractionContext`).
4. **Fragile DOM Manipulation:** Does navigation or interaction require unsupported DOM hacks? **NO.** Streamlit native containers and standard CSS overrides handle composer placement safely.
5. **Custom Component Requirement:** Does navigation replacement require custom frontend components? **NO.** Native sidebar is preserved and styled.

*Conclusion: NO STOP CONDITIONS TRIGGERED.*

---

## 12. RECOMMENDATION

### FINAL RECOMMENDATION: **A. PROCEED ON STREAMLIT**

### Justification based on Repository Evidence:
1. **Zero Architecture Violation:** The gap identified by the governor audit ( shared generic `show_new_chat()` screen obscuring archetype projection identity) can be fully resolved within supported Streamlit container APIs (`st.container`, `st.columns`, `st.form`, `st.status`) combined with clean presentation seam isolation (`ui/presentation/shell.py`).
2. **Single Interaction Truth Maintained:** No backend orchestration, database schema, memory hydration, or agent routing changes are needed.
3. **No Migration / Custom Component Needed:** All required archetype interaction shell morphologies (chat composer, command bar, workspace object pane, research query surface, node trigger, terminal prompt, and minimal task card) are cleanly achievable on native Streamlit without custom HTML/JS component bridges.
