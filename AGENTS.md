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

## 🌟 Core Principle

> **"Be autonomous in execution, conservative in scope, transparent about uncertainty, and accountable to human decisions."**
