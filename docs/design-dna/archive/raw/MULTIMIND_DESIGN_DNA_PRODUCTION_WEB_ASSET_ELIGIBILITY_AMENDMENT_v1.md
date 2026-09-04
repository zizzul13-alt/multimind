# MULTIMIND DESIGN DNA --- PRODUCTION-WEB ASSET ELIGIBILITY AMENDMENT v1

ROLE: DESIGN-DNA RESEARCH / MIGRATION GOVERNANCE REPORTS TO: DESIGN DNA
HQ / PROJECT GOVERNOR STATUS: GOVERNANCE AMENDMENT --- CUMULATIVE / NO
RESET

# 0. PURPOSE

Establish a conservative production deployment floor for visual assets
used by MultiMind Design DNA.

This amendment does not provide legal advice and does not replace the
actual license terms of a source. It establishes project governance:
when rights are insufficiently clear for the intended production-web
deployment, the asset does not ship.

# 1. CANONICAL PRODUCTION STATUS

Canonical positive status:

`PRODUCTION_WEB_ELIGIBLE`

An asset may receive this status only when the actual applicable rights
are sufficiently clear for the way MultiMind intends to use and deliver
it.

"Free" alone is insufficient.

`FREE != PRODUCTION_WEB_ELIGIBLE`

`FREE_FOR_PERSONAL_USE != PRODUCTION_WEB_ELIGIBLE`

# 2. REQUIRED RIGHTS CHECK

Evaluate the rights actually implicated by the intended use, including
where applicable: - web/application use; - public
serving/distribution; - copying/redistribution; - embedding/bundling; -
modification/derivative use; - attribution obligations; -
ShareAlike/copyleft-style obligations; - commercial-use permission where
relevant to deployment; - restrictions on standalone redistribution; -
restrictions on sublicensing or asset extraction; - source-specific
terms.

Do not infer permission that the license does not grant.

# 3. ELIGIBILITY CLASSES

`PRODUCTION_WEB_ELIGIBLE` Rights are explicit and compatible with
intended production use, subject to recorded obligations.

`CONDITIONALLY_PRODUCTION_WEB_ELIGIBLE` Potentially usable only if
explicit obligations/conditions are satisfied. Must not ship until those
conditions are resolved and recorded.

`RESEARCH_REFERENCE_ONLY` May be useful as evidence/reference under
applicable terms but is not approved for production deployment.

`PERSONAL_USE_ONLY` Not approved for production-web deployment.

`LICENSE_UNKNOWN_OR_UNCLEAR` Not approved for production-web deployment.

`PRODUCTION_PROHIBITED` Known terms conflict with intended deployment.

# 4. CONSERVATIVE SHIPPING LAW

`NO SUFFICIENTLY CLEAR PRODUCTION-COMPATIBLE RIGHTS → DO NOT SHIP`

For production selection:

`PERSONAL_USE_ONLY → EXCLUDE`

`RESEARCH_REFERENCE_ONLY → EXCLUDE`

`LICENSE_UNKNOWN_OR_UNCLEAR → EXCLUDE`

`PRODUCTION_PROHIBITED → EXCLUDE`

`CONDITIONALLY_PRODUCTION_WEB_ELIGIBLE → EXCLUDE UNTIL CONDITIONS SATISFIED`

This exclusion does NOT invalidate the associated Design DNA.

`ASSET EXCLUDED → REPLACEMENT OR DEGRADED/ASSET-OFF PROJECTION → DNA IDENTITY SURVIVES`

# 5. PUBLIC DOMAIN / OPEN LICENSES

Public Domain and CC0 are strong candidates where their status is
reliable.

Other open/content licenses may also be production-compatible, but must
be evaluated against their actual terms and the intended delivery model.

Attribution-required or ShareAlike assets are not automatically
rejected; their obligations must be compatible with the application and
actually fulfilled.

Do not assume a license label from a search result, thumbnail, mirror,
repost, or aggregator is authoritative. Preserve source provenance.

# 6. ASSET MANIFEST CONTRACT

For every production candidate asset, record where applicable:

`ASSET_ID` `SOURCE_URL_OR_ORIGIN` `CREATOR_OR_RIGHTSHOLDER`
`ASSET_CLASS` `REFERENCE_SCOPE` `SHARED_OR_REFERENCE_SPECIFIC`
`LICENSE_NAME` `LICENSE_SOURCE` `LICENSE_VERSION` `PRODUCTION_STATUS`
`PERMITTED_USE` `MODIFICATION_RIGHTS` `REDISTRIBUTION_OR_SERVING_RIGHTS`
`ATTRIBUTION_REQUIRED` `SHAREALIKE_OR_OTHER_OBLIGATION` `RESTRICTIONS`
`ATTRIBUTION_TEXT_OR_RECORD` `FALLBACK_ASSET_OR_MODE` `LAST_VERIFIED`
`NOTES`

Unknown fields must remain UNKNOWN, not guessed.

# 7. RUNTIME DELIVERY LAW

Asset architecture should support non-blocking/progressive theme
presentation where practical:

`THEME SELECTED` → structural DNA renders → eligible manifest resolves →
assets load progressively → partial fidelity → full fidelity

An unavailable or ineligible asset must not block the whole theme.

Production runtime should be able to distinguish: - not requested; -
loading; - loaded; - failed; - excluded by policy/license; -
unsupported; - intentionally disabled.

These states must resolve into deterministic degradation behavior.

# 8. SHARED-ASSET GOVERNANCE

Shared production assets are allowed.

Shared assets should be manifest-addressable and reusable without
conflating reference identity.

`SHARED ASSET != SHARED IDENTITY`

A shared texture/pattern/light resource can support multiple references,
but reference-specific composition, selectors, mechanisms, and
projection rules remain authoritative.

# 9. REPLACEMENT LAW

A non-eligible research/reference asset may inspire or document
mechanism research but may not be silently copied into production.

Replacement options include: - independently sourced
production-web-eligible asset; - project-created original asset; -
public-domain/CC0 alternative; - compatible licensed alternative; -
procedural/structural rendering; - degraded/asset-off projection.

Replacement must preserve reference integrity and must not falsely claim
lineage/provenance.

# 10. GLOBAL CALIBRATION CONSEQUENCE

For every visually applicable mandatory DNA, Global Calibration must
distinguish:

`STRUCTURAL_CORE_CONTRACT`

from

`ASSET_ON_ENRICHMENT_CONTRACT`

The enrichment contract should specify, where applicable: - useful asset
classes; - role of each asset class; - shared vs reference-specific
status; - required vs optional enrichment; - loading behavior; -
composition constraints; - license eligibility requirements; -
partial-failure behavior; - asset-off fallback; - performance
considerations; - acceptance tests.

`ASSET_ON_ENRICHMENT_CONTRACT` may be `NOT_APPLICABLE` only when
genuinely unnecessary for that DNA. Do not fabricate assets to satisfy
schema.

# 11. EQ3 / EQ4 BOUNDARY

EQ3 may specify the production eligibility and asset-on/degradation
contract without possessing every final production asset.

EQ4 requires proof in the actual migrated production host that selected
production assets and fallbacks behave correctly.

A missing final production asset can therefore be an
implementation/content acquisition debt without automatically
invalidating valid mechanism research, provided the EQ3 contract is
deterministic and does not depend on an unlicensed asset.

# 12. GOVERNANCE

NO RESET. NO AUTOMATIC GLOBAL REOPEN. NO LICENSE GUESSING. NO
PERSONAL-USE-ONLY ASSET IN PRODUCTION. NO UNKNOWN-LICENSE ASSET IN
PRODUCTION. NO PRODUCTION MODIFICATION IN RESEARCH. NO CANON LOCK BY
BRANCH.

Production goal:

`MAXIMUM PRACTICAL FIDELITY FROM PRODUCTION_WEB_ELIGIBLE ASSETS + DETERMINISTIC GRACEFUL DEGRADATION + RECOGNIZABLE ASSET-OFF SURVIVAL`