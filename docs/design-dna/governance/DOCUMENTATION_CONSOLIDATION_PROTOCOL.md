# MultiMind Design DNA — Documentation Consolidation Protocol

Status: GOVERNOR MASTER RULE — ACTIVE
Date: 2026-09-04

## Decision

The Design DNA corpus will be consolidated directly into the MultiMind GitHub repository as a modular, navigable knowledge base instead of relying on a growing collection of chat-local Markdown artifacts or compressing all history into one lossy monolithic summary.

Working branch:

`docs/design-dna-consolidation`

Target root:

`docs/design-dna/`

Migration Gate and production migration remain frozen while this consolidation is incomplete.

## Objective

Preserve the maximum recoverable detail from the accumulated Design DNA research while making future Governor/research/migration sessions able to navigate the corpus without rereading dozens of unordered Markdown files.

The governing requirement is:

`NO DETAIL LOSS BY CLEANUP`

Cleanup means classification, indexing, reconciliation, modularization and explicit supersession. It does NOT mean deleting inconvenient history.

## Required workflow

`DISCOVER → INVENTORY → CLASSIFY → CONTENT-COMPARE → RECONCILE → CANONICALIZE → CROSS-LINK → ZERO-LOSS AUDIT → REVIEW → PR/MERGE`

Every discovered artifact must be classified before consolidation as one of:

- AUTHORITATIVE_CURRENT
- AUTHORITATIVE_SUPPORTING
- HISTORICAL_VALID
- SUPERSEDED_TRACE
- DUPLICATE_BYTE_OR_CONTENT
- BRANCH_BRIEF / NON_CANONICAL
- UNKNOWN_REQUIRES_RECONCILIATION

## Source precedence

1. Current authoritative repository/files for implementation facts.
2. Latest explicit user/HQ decision.
3. Latest accepted MASTER LOCK/checkpoint.
4. Latest accepted research/calibration artifact.
5. Older artifacts as cumulative research/history.

A newer artifact may supersede a status, denominator, interpretation or contract field without making the older artifact worthless. The old artifact remains an audit trail unless it is proven to be a true duplicate.

## Duplicate rule

Same filename is not sufficient evidence of duplication.

Before marking duplicate, compare content or otherwise establish semantic/byte identity. If two copies differ, both remain until their relationship is reconciled.

## Supersession rule

Superseded claims are not silently rewritten out of history.

Example class: earlier residual censuses may contain pre-final denominators while the accepted Batch 9 manifest locks the current denominator at 271. Canonical docs expose the final value; archive/index records explain the historical transition.

## Cumulative research inheritance

Failed methods, dead routes, false positives, evidence traps, negative fixtures, acquisition lessons, reformulations and historical barriers remain project knowledge.

A failed research route is not documentation garbage.

## Canonical vs archive

Canonical documents answer: "What is true/current now?"

Archive/history answers: "How did we get here, what failed, what was superseded, and where can the original evidence path be recovered?"

Both are required.

## Structure policy

The curated knowledge base is modular by responsibility/family rather than by chat chronology:

- governance/
- corpora/cultural/
- corpora/country-web/
- corpora/personal-media/izzul/
- corpora/personal-media/miko/
- corpora/temporal/
- engines/material-environment/
- corpora/material-named/
- fixtures/
- calibration/
- migration/
- archive/

Operational packaging does not change ontology or canonical IDs.

## Git policy

Consolidation occurs on a dedicated documentation branch. Do not merge directly to `main` while inventory/reconciliation remains incomplete.

The existing production `docs/design_dna.md` is not overwritten merely because a new curated tree exists. Its relationship to the new corpus must first be explicitly classified/reconciled.

A PR/merge is permitted only after the documentation audit can state with evidence that authoritative current state is represented and known historical/superseded material has a traceable preservation route.

## Current closure anchor

The consolidation must preserve these locked facts unless newer explicit evidence supersedes them:

- Global additive denominator: 271.
- Global EQ3: 271/271 PASS.
- Reference: 160.
- Engine: 29.
- Primitive: 68.
- Fixture: 14.
- Manifest residual: 0.
- Research/EQ3 reopen: 0.
- Asset applicable: 207.
- Asset not applicable: 64.
- Final production assets approved: 0.
- Direct-IP gated references: 75.
- Migration Gate Review ready: YES.
- Migration authorized: NO.
- Production migration performed: NO.
- EQ4: NOT STARTED.

## Migration firewall

Documentation consolidation is NOT migration authorization.

No Design DNA implementation, Reflex production migration, EQ4 claim or production architecture mutation follows merely from the documentation branch existing.

Required order remains:

`DOCUMENTATION CONSOLIDATION → ZERO-LOSS AUDIT → GOVERNOR ACCEPTANCE → MIGRATION GATE REVIEW → SEPARATE AUTHORIZATION → IMPLEMENTATION/EQ4`

## Future-chat operating rule

Future sessions should begin at `docs/design-dna/README.md`, then load only the canonical family/governance documents relevant to the task. Historical artifacts are opened when provenance, contradiction, recovery, or forensic detail requires them.

This replaces dependence on one giant chat context without sacrificing the underlying historical corpus.
