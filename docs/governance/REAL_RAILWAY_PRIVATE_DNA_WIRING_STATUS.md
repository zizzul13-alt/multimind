# MULTIMIND — REAL RAILWAY PRIVATE DESIGN-DNA WIRING STATUS

Status date: 2026-09-08
Owning workstream: REAL DEPLOYMENT EXECUTION / PRIVATE DNA ENABLEMENT
Production cutover authorized by this document: NO

## 1. GOVERNOR TASK

Connect the accepted private `multimind-design-dna` package through the existing public `ui/dna_bridge.py` seam on the real Railway Reflex candidate, prove the enabled path and the safe fallback path, and do not redesign architecture.

## 2. AUTHORITATIVE BASELINES

Public MultiMind baseline inspected for this task:

```text
ac3869a0bc6be08eea413de58b81f639b7de1e65
```

Private Design-DNA authoritative main:

```text
621a3a51bb04d14c91fc09701ce40988af951bcf
```

The private extraction remains Governor-accepted, CLOSED, and INTEGRATED. The canonical boundary remains:

```text
PUBLIC MULTIMIND
→ ui/dna_bridge.py
→ optional installed multimind-design-dna package
```

The private distribution remains `multimind-design-dna` and exports the proven Python namespaces `design_dna` and `dna_quarantine`.

## 3. REAL RAILWAY CANDIDATE INSPECTION

The real Railway production environment was inspected through the connected Railway control plane.

Observed candidate facts:

```text
SERVICE = multimind
ENVIRONMENT = production
SOURCE = zizzul13-alt/multimind:main
BUILD MODE = RAILPACK / no private-DNA Dockerfile override configured
PRIVATE_DNA_VARIABLE_OR_SECRET_HOOK = ABSENT
```

Existing application/provider/Turso variables remain configured. No private Git credential or private-DNA installation variable is currently present.

The service was also observed in Railway `SLEEPING` state during this investigation. That is separate Step-5 runtime evidence and is not used to widen this private-DNA task.

## 4. BRIDGE AND PACKAGE READINESS

The public bridge is already the correct seam and must not be redesigned.

`ui/dna_bridge.py` lazily imports:

```text
dna_quarantine.legacy_ui_dna.resolver
dna_quarantine.legacy_ui_dna.bootstrap
dna_quarantine.theme_studio.surface
```

and degrades to neutral host-safe behavior when those imports or runtime calls fail.

The private package is installable as a normal Python distribution and includes `design_dna*` and `dna_quarantine*` packages.

Existing accepted cross-repository evidence already proves:

```text
ABSENT_PRIVATE_DNA_FALLBACK = PASS
PRIVATE_PACKAGE_INSTALL = PASS
PRESENT_PRIVATE_DNA_BRIDGE = PASS
PRIVATE_BOOTSTRAP = PASS
THEME_STUDIO_MODULE_AVAILABILITY = PASS
FULL_PUBLIC_HOST_REGRESSION_WITH_PRIVATE_DNA = PASS
```

This repository/CI evidence proves the seam and package compatibility. It does not fabricate a real Railway enabled-path proof.

## 5. ACCEPTED PRIVATE BUILD CONTRACT

The repository already contains the bounded private build path:

```text
compose.private-dna.yml
→ Dockerfile.private-dna
→ BuildKit secret id=github_token
→ clone private repository
→ pip install private distribution
```

The accepted `Dockerfile.private-dna` requires:

```text
RUN --mount=type=secret,id=github_token,required=true
```

and the Compose override supplies that secret from a server-side file rather than source, browser storage, or Docker build arguments.

This is intentional: repository governance explicitly forbids placing the real private Git credential in source, image metadata, browser state, or secret-bearing Docker build arguments.

## 6. REAL RAILWAY HOST CAPABILITY RESULT

The current Railway source build does not expose the accepted Compose/BuildKit secret-file contract to this connected deployment path.

Railway's documented Dockerfile build-variable mechanism requires explicit Dockerfile `ARG` use for Railway variables. Using a GitHub credential that way would violate the accepted MultiMind secret-delivery contract.

The other obvious host path, deploying a private prebuilt container image with private registry credentials, is not accepted here because Railway private-registry credentials require a paid tier and the project has a hard Rp0 / no-credit-card constraint.

Therefore the following tempting workarounds are explicitly rejected:

```text
GITHUB_TOKEN as Docker ARG                = REJECTED
credential embedded in private Git URL   = REJECTED
runtime ad-hoc pip/git installation       = REJECTED
new DNA network/microservice              = REJECTED
publicly vendoring private DNA            = REJECTED
paid private registry solely for this     = REJECTED UNDER CURRENT BUDGET LAW
```

## 7. CURRENT VERDICT

```text
PUBLIC_BRIDGE_READY = PASS
PRIVATE_PACKAGE_READY = PASS
CROSS_REPO_PRESENT_PATH = PASS
SAFE_FALLBACK_CONTRACT = PASS
REAL_RAILWAY_SAFE_FALLBACK = PRESERVED
REAL_RAILWAY_PRIVATE_DNA_ENABLED = NOT PROVEN

BLOCKER = MISSING_SECURE_BUILD_SECRET_TRANSPORT
BLOCKER_OWNER = DEPLOYMENT HOST CAPABILITY / SECRET DELIVERY
ARCHITECTURE_REDESIGN_REQUIRED = FALSE
CORE_CHANGE_REQUIRED = FALSE
PERSISTENCE_CHANGE_REQUIRED = FALSE
PROVIDER_CHANGE_REQUIRED = FALSE
```

No mutation was made to the Railway candidate because every currently available direct mutation would either fail the accepted private build contract or weaken secret handling.

## 8. EXIT CONDITION FOR THIS RESIDUAL

This residual closes only when the real host can supply the existing `github_token` BuildKit secret contract, or another Governor-accepted server-side secret-delivery mechanism that preserves the same security and optional-package semantics becomes available without violating the Rp0/no-card deployment law.

Once such a host path exists, the bounded proof remains:

```text
install private package
→ start same Reflex candidate
→ ui.dna_bridge.dna_available() == True
→ bootstrap succeeds
→ Theme Studio private module available
→ browser candidate remains healthy
→ remove/withhold private package delivery
→ same public candidate starts neutral
→ core/provider/persistence truth unchanged
```

Until then:

```text
PRIVATE_DNA_PRODUCTION = DISABLED BY HOST CAPABILITY
NEUTRAL_SAFE_PRESENTATION = AUTHORITATIVE REAL CANDIDATE MODE
PRODUCTION_CUTOVER_AUTHORIZED = FALSE
```
