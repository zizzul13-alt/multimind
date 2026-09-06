# RJ-5 — TORTURE / DUAL-HOST PARITY — IMPLEMENTATION REPORT

Status: IMPLEMENTED ON REVIEW BRANCH / PENDING CI / NOT MERGED
Production cutover authorized: NO

## BASE

Starting accepted baseline: RJ-4 closure `fcc8d40bbd5d51fbf6ac0186478abe547eb4a26d`.

## TORTURE MODEL

RJ-5 adds no new application architecture. It attempts to break the migration contracts through two evidence lanes.

### Lane A — application truth A → B → A

A deterministic provider and one authoritative SQLite file are used through the shared `build_application_for_user(...)` boundary.

The probe executes:

1. host A semantic instance creates/selects a session and persists chat #1;
2. fresh host B semantic instance opens the same SQLite truth, hydrates history, and persists chat #2;
3. fresh host A semantic instance reopens the same SQLite truth and must observe both chats in deterministic order;
4. application export creates a same-schema SQLite snapshot;
5. a separate application instance restores the snapshot without conversion and invalidates stale database-derived runtime state.

No host-specific SQL, provider routing, or alternate persistence path is allowed.

### Lane B — real host boot proof

GitHub Actions starts both actual presentation hosts headlessly from the same repository/dependency set:

- Streamlit reference host on port 8501, HTTP-probed until responsive;
- Reflex production host using `reflex run --env prod`, frontend on 3000 and backend `/_health` on 8000, both HTTP-probed.

This is a host boot/readiness proof, not a pixel-identical or full browser-interaction claim. Responsive phone/tablet/desktop contracts remain covered by RJ-3 source/contract tests; adding Playwright or another browser framework solely for this gate is intentionally avoided unless evidence demands it.

## CROSS-GATE TORTURE

The dedicated RJ-5 workflow also reruns focused contracts for:

- public Design-DNA absent/broken fallback;
- RJ-1 portability/application boundary;
- RJ-2 Reflex production host;
- RJ-3 presentation parity;
- RJ-4 durable deployment.

Full Python regression remains an independent required PR gate.

## PRESERVATION

- SQLite remains authoritative;
- same DB schema/data is shared between presentation hosts;
- `MultiMindApplication` remains application truth;
- no FastAPI/REST/RPC/microservice;
- no second persistence owner;
- no provider/debate/memory rewrite;
- no Reflex version change;
- Streamlit remains available and is actually boot-tested;
- private DNA remains optional through the public bridge.

## REQUIRED VERIFICATION

Before closure:

- A→B→A persistence/history torture PASS;
- export/restore same-schema torture PASS;
- focused RJ1–RJ4 + DNA bridge regression PASS;
- Streamlit headless HTTP boot PASS;
- Reflex production frontend + backend health boot PASS;
- full Python regression + `pip check` PASS;
- bounded diff audit PASS;
- expected-head guarded merge;
- exact-main Python and RJ-5 torture push runs PASS.

## RESIDUALS

- real public internet routing/TLS/hostname remains deployment-environment work, not repository truth;
- pixel-perfect parity is not required by the frozen denominator;
- RJ-6 owns cutover/rollback rehearsal and rollback evidence;
- Final Governor Migration Gate alone owns production cutover authorization.

## VERDICT

PENDING CI / REVIEW.
