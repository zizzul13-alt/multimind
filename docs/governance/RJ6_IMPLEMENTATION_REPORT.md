# RJ-6 — CUTOVER + ROLLBACK PROOF — IMPLEMENTATION REPORT

Status: IMPLEMENTED ON REVIEW BRANCH / PENDING CI / NOT MERGED
PRODUCTION CUTOVER AUTHORIZED: NO

## BASE

Starting accepted baseline: RJ-5 closure `92632a0c1689271b14f28e909971b9cb454f6b61`.

Inherited accepted state:

- private Design-DNA extraction: CLOSED;
- RJ-3 functional presentation parity: CLOSED / PASS;
- RJ-4 durable persistence + deployment: CLOSED / PASS;
- RJ-5 dual-host parity torture: CLOSED / PASS.

## MISSION

Prove that the accepted Reflex candidate can be introduced and rolled back without changing application truth, database format, provider architecture, or the Streamlit rollback host.

This is a drill only. It does not perform or authorize actual production cutover.

## DRILL MODEL

The dedicated RJ-6 workflow executes one serial rollback story over one authoritative `data/` tree:

1. boot the real Streamlit reference host headlessly;
2. create isolated user A and user B state through `MultiMindApplication` / shared composition;
3. persist normal deterministic chat operations;
4. stop Streamlit without changing data;
5. build a fresh production Reflex container from the repository Dockerfile;
6. bind the same `data/` tree at `/app/data`;
7. inject server-side runtime secret sentinel values;
8. boot and HTTP-probe Reflex frontend + backend health;
9. verify the container sees the existing Streamlit-created user/session/history truth;
10. persist an additional normal operation through the same application boundary;
11. restart the Reflex container and re-verify data;
12. remove and recreate the Reflex container against the same data and re-verify data;
13. export and restore a same-schema SQLite backup, including invalid-backup rejection and source-user isolation;
14. simulate Reflex failure by killing/removing the candidate container;
15. boot the real Streamlit reference host again;
16. verify the original same user DBs, sessions and complete cross-host history remain available.

Rollback target:

`STREAMLIT → SAME DATA → REFLEX → SAME DATA → REFLEX FAILURE → STREAMLIT → SAME DATA`

Hard rollback laws:

- NO DB CONVERSION;
- NO CORE ROLLBACK;
- NO PROVIDER MIGRATION;
- NO SECOND PERSISTENCE OWNER;
- NO FASTAPI / REST / RPC GLUE.

## PRODUCTION-BOUNDARY CONTRACTS UNDER TEST

RJ-6 verifies:

- fresh deployment image build;
- startup/health behavior;
- server-side environment secret availability contract;
- Reflex frontend/backend connectivity;
- restricted CORS configuration with no wildcard default;
- existing user DB availability from the candidate runtime;
- normal application operation before and during candidate presentation state;
- user A/B isolation;
- restart survival;
- runtime/container recreation survival;
- backup export;
- valid restore;
- invalid restore fail-closed behavior;
- same-schema restore;
- Streamlit rollback boot;
- same users/sessions/history after rollback.

Actual provider secrets, public DNS, TLS certificates and a real internet-facing hostname are deployment-environment facts and are not fabricated in repository CI.

## IMPLEMENTATION

RJ-6 is evidence-only/hardening scoped. It adds:

- `scripts/rj6_cutover_rollback_probe.py`;
- `tests/test_rj6_cutover_rollback_proof.py`;
- `.github/workflows/rj6-cutover-rollback-proof.yml`;
- this report.

No runtime application/core/provider/database implementation file is changed by the RJ-6 package.

## REQUIRED VERIFICATION

Before closure:

- RJ-6 focused contracts PASS;
- full Python regression PASS;
- dependency sanity / `pip check` PASS;
- restricted CORS sentinel contract PASS;
- server-side secret-injection contract PASS;
- Streamlit baseline host boot PASS;
- fresh Reflex image build PASS;
- Reflex frontend + backend health PASS;
- pre-existing Streamlit data visible from Reflex container PASS;
- normal Reflex-phase application write PASS;
- Reflex restart persistence PASS;
- fresh-container recreation persistence PASS;
- backup/restore + invalid restore + user isolation PASS;
- simulated Reflex failure PASS;
- Streamlit rollback host boot PASS;
- same users/sessions/history after rollback PASS;
- bounded diff audit PASS;
- expected-head guarded merge;
- exact-main Python + RJ-6 proof push runs PASS.

## RESIDUALS

Non-blocking deployment-environment facts remaining after a successful RJ-6 drill:

- real production hostname;
- real TLS/reverse-proxy termination;
- actual production provider credentials/secrets;
- actual production server/volume location;
- final operator cutover timing.

These are not evidence that the repository migration architecture is incomplete. They belong to final deployment execution and the Final Governor Migration Gate.

## VERDICT

PENDING CI / REVIEW.

Even if this report becomes PASS, actual production cutover remains unauthorized until the Final Governor Migration Gate and explicit Governor/user authorization.
