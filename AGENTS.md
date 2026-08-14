# 🤖 MultiMind AI Agent Rules & Principles

Welcome, Agent. This document establishes the shared engineering rules and principles for AI-assisted development (including Jules and others) within this repository.

Read and obey these instructions meticulously.

---

## ⚖️ Human Governance & Explicit Scope

1. **Highest Authority**: Human intent and the explicit task scope are the highest authority.
2. **HOW vs. WHAT**: AI agents decide **HOW** to implement, but must **never silently change WHAT** is requested.
3. **Approval Triggers**: Significant decisions regarding product design, API schemas, databases, security, architecture, destructive operations, external dependencies, or scope expansion **require explicit human approval**.
4. **Conservative Scope**: Do not expand scope because an improvement seems interesting. Do not fix unrelated issues unless they directly block the current task.

---

## 🛠️ Code Quality & Minimal Necessary Change

1. **Understand & Inspect**: Always thoroughly inspect the repository, dependencies, and existing architecture before making any changes.
2. **Prefer Existing Architecture**: Utilize existing classes, abstractions, and conventions. Avoid creating duplicating layers or redundant structures.
3. **Smallest Necessary Change**: Implement the smallest possible change to complete the task while maintaining compatibility and code cleanliness.
4. **Preserve Existing Behavior**: Ensure existing single-provider, legacy, and sequential flows continue to run seamlessly without breaking.

---

## 🔁 Engineering Workflow

Follow this iterative development lifecycle:
`Understand` ➔ `Inspect` ➔ `Plan` ➔ `Implement` ➔ `Test` ➔ `Review` ➔ `Refine` ➔ `Verify`

- **Practice Proactive Testing**: Write tests for new behaviors and run the test suite to ensure zero regressions.
- **Never Commit Secrets**: Never commit API keys, credentials, or credentials files.
- **Never Hide Failures**: Report any test or lint failures honestly.
- **Transparency**: Report implemented changes, verification, limitations, and out-of-scope observations clearly.

---

## 🛡️ UI/UX & Session Guardrails

1. **Scope Discipline**
   - Strictly follow the explicitly approved scope; do not expand the task into adjacent features or areas.
   - If useful work or potential improvements outside the scope are discovered, report them instead of implementing them.
   - Always prefer the smallest, most targeted necessary change to accomplish the task.

2. **Focused Session Workflow**
   - Treat each session/task as a single focused, self-contained unit of work.
   - Do not proceed into subsequent phases or next tasks simply because the current task is completed.
   - Stop immediately when the requested scope is complete, and wait for a new task/session before starting any new scope.

3. **Phase Boundaries**
   - MultiMind UI/UX work is divided into distinct, structured phases (typically progressing: UI Foundation → Design Tokens → Theme Engine → Responsive/advanced theming → Design DNA → Theme Studio → AI integration → GitHub publishing).
   - Never implement a later phase or pre-build/anticipate future systems in the progression unless explicitly requested and approved.

4. **UI/UX Safety**
   - UI/UX changes must never modify core application behavior or logic unless explicitly approved.
   - Do not perform unrelated architectural refactors or file restructurings during styling/UI tasks.
   - Thoroughly inspect existing implementations before modifying them to ensure 100% backward compatibility and preservation of functionality.

5. **CSS / Styling Discipline**
   - Avoid creating large, monolithic CSS blocks. Prefer reusable, modular, and maintainable styling rules.
   - Avoid excessive dependence on internal or generated Streamlit class names when stable, native alternatives exist.
   - Do not introduce a theme engine or design-token system unless the current task explicitly requests it.
   - Avoid unnecessary visual effects or styling dependencies that could hurt mobile or Streamlit rendering performance.

6. **Responsive Requirement**
   - When a UI task explicitly includes responsive design work, carefully consider desktop, tablet, and mobile behaviors.
   - Avoid redundant duplication of desktop and mobile implementations. Prevent normal horizontal layout overflow and preserve small-screen usability.

7. **Asset / Design Material Rules**
   - Never assume any asset or design material is free to use; verify its license before including it in the repository.
   - Do not use AI-generated visual assets unless explicitly approved. Prefer human-created resources with clear, appropriate licensing.
   - Keep material/design resources locked to their intended reference/theme; do not casually reuse them across unrelated themes.
   - Shared resources are allowed only if they are genuinely generic/limited resources (e.g., standard web fonts) and their licenses permit reuse.

8. **PR Discipline**
   - Keep pull requests focused, concise, and easy to review. Do not combine unrelated phases or features in a single PR.
   - Clearly document and report all files changed, including the reasoning for each change.
   - Do not silently bundle out-of-scope changes. If a task requires a scope expansion, stop immediately and report it to the human operator.

---

## 🌟 Core Principle

> **"Be autonomous in execution, conservative in scope, transparent about uncertainty, and accountable to human decisions."**
