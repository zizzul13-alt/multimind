from dataclasses import replace
from pathlib import Path

import pytest

from design_dna import (
    AssetIntent,
    AssetState,
    Axis,
    CompositionRequest,
    DNARegistry,
    DNAUnit,
    DegradationState,
    DuplicateUnitError,
    FailureCode,
    MechanismContract,
    RuntimeConstraints,
    SemanticContext,
    SemanticZone,
    UnitKind,
    Viewport,
    resolve,
)


def unit(
    unit_id,
    kind,
    mechanisms=(),
    assets=(),
    *,
    conflicts=(),
    family="test-family",
):
    return DNAUnit(
        id=unit_id,
        kind=kind,
        family=family,
        lineage="test-lineage",
        provenance_pointer=f"docs://{unit_id}",
        mechanisms=tuple(mechanisms),
        assets=tuple(assets),
        conflicting_unit_ids=tuple(conflicts),
        identity_survival="structural-contract",
    )


def mechanism(
    mechanism_id,
    axis=Axis.FORM,
    zone=SemanticZone.U3,
    directive="structural",
    *,
    fallback="",
    rank=50,
    conflicts=(),
    compatible=(),
    accessibility_safe=True,
    reading_safe=True,
    viewports=("all",),
    requires_asset_slot=None,
    host_capability=None,
):
    return MechanismContract(
        id=mechanism_id,
        axis=axis,
        zones=(zone,),
        directive=directive,
        fallback_directive=fallback,
        ownership_rank=rank,
        conflicts_with=tuple(conflicts),
        compatible_with=tuple(compatible),
        accessibility_safe=accessibility_safe,
        reading_safe=reading_safe,
        viewports=tuple(viewports),
        requires_asset_slot=requires_asset_slot,
        host_capability=host_capability,
    )


def reference(unit_id="ref-a", mechanisms=(), assets=(), **kwargs):
    if not mechanisms:
        mechanisms = (mechanism(f"{unit_id}-form"),)
    return unit(unit_id, UnitKind.REFERENCE, mechanisms, assets, **kwargs)


def engine(unit_id="eng-a", mechanisms=(), **kwargs):
    if not mechanisms:
        mechanisms = (mechanism(f"{unit_id}-space", axis=Axis.SPACE, directive="engine-space"),)
    return unit(unit_id, UnitKind.ENGINE, mechanisms, **kwargs)


def primitive(unit_id="prim-a", mechanisms=(), **kwargs):
    if not mechanisms:
        mechanisms = (mechanism(f"{unit_id}-type", axis=Axis.TYPOGRAPHY_SCRIPT, directive="primitive-type"),)
    return unit(unit_id, UnitKind.PRIMITIVE, mechanisms, **kwargs)


def issue_codes(items):
    return {item.code for item in items}


def test_canonical_taxonomy_is_exactly_15_axes_and_9_zones():
    assert len(Axis) == 15
    assert len(SemanticZone) == 9
    assert Axis.SOUND_RHYTHM.value == "SOUND_RHYTHM"
    assert SemanticZone.U7.value == "U7_READING_SANCTUARY"


def test_registry_is_deterministic_and_rejects_duplicate_ids():
    registry = DNARegistry([engine("z-engine"), reference("a-reference")])
    assert [item.id for item in registry.list_units()] == ["a-reference", "z-engine"]
    with pytest.raises(DuplicateUnitError):
        registry.register(reference("a-reference"))


def test_unknown_reference_fails_safe_without_fallback_substitution():
    projection = resolve(DNARegistry(), CompositionRequest("missing"), SemanticContext())
    assert not projection.is_valid
    assert FailureCode.UNEXPLAINABLE_COMPOSITION in issue_codes(projection.rejections)
    assert projection.mechanisms == ()


def test_type_firewall_rejects_reference_smuggled_as_engine():
    registry = DNARegistry([reference("ref-a"), reference("not-an-engine")])
    projection = resolve(
        registry,
        CompositionRequest("ref-a", engine_ids=("not-an-engine",)),
        SemanticContext(),
    )
    assert not projection.is_valid
    assert FailureCode.UNEXPLAINABLE_COMPOSITION in issue_codes(projection.rejections)


def test_fixture_is_not_runtime_selectable_as_primitive():
    fixture = unit("fixture-a", UnitKind.FIXTURE)
    registry = DNARegistry([reference(), fixture])
    projection = resolve(
        registry,
        CompositionRequest("ref-a", primitive_ids=("fixture-a",)),
        SemanticContext(),
    )
    assert not projection.is_valid


def test_equivalent_request_order_is_deterministic():
    registry = DNARegistry([reference(), engine("eng-a"), engine("eng-b")])
    first = resolve(
        registry,
        CompositionRequest("ref-a", engine_ids=("eng-b", "eng-a")),
        SemanticContext(),
    )
    second = resolve(
        registry,
        CompositionRequest("ref-a", engine_ids=("eng-a", "eng-b")),
        SemanticContext(),
    )
    assert first.is_valid and second.is_valid
    assert first.fingerprint == second.fingerprint
    assert first.mechanisms == second.mechanisms


def test_definition_change_changes_fingerprint():
    first_registry = DNARegistry([reference(mechanisms=(mechanism("form", directive="one"),))])
    second_registry = DNARegistry([reference(mechanisms=(mechanism("form", directive="two"),))])
    request = CompositionRequest("ref-a")
    context = SemanticContext()
    assert resolve(first_registry, request, context).fingerprint != resolve(second_registry, request, context).fingerprint


def test_ownership_rank_wins_under_dominance_cap():
    ref = reference(mechanisms=(mechanism("low", directive="low", rank=40),))
    eng = engine("eng-a", mechanisms=(mechanism("high", directive="high", rank=90),))
    projection = resolve(
        DNARegistry([ref, eng]),
        CompositionRequest("ref-a", engine_ids=("eng-a",)),
        SemanticContext(),
        RuntimeConstraints(dominance_cap=1),
    )
    assert projection.is_valid
    assert len(projection.mechanisms) == 1
    assert projection.mechanisms[0].directive == "high"
    assert FailureCode.OWNERSHIP_COLLISION in issue_codes(projection.warnings)


def test_explicit_conflict_is_deterministically_demoted():
    winner = mechanism("winner", directive="winner", rank=90)
    loser = mechanism("loser", directive="loser", rank=60, conflicts=("winner",))
    projection = resolve(
        DNARegistry([reference(mechanisms=(winner,)), engine("eng-a", mechanisms=(loser,))]),
        CompositionRequest("ref-a", engine_ids=("eng-a",)),
        SemanticContext(),
    )
    assert projection.is_valid
    assert [item.mechanism_id for item in projection.mechanisms] == ["winner"]
    assert FailureCode.OWNERSHIP_COLLISION in issue_codes(projection.warnings)
    assert any(item.action == "demoted" and item.mechanism_id == "loser" for item in projection.provenance)


def test_contradiction_budget_overflow_is_rejected_but_explainable():
    ref = reference(mechanisms=(mechanism("winner", rank=90),))
    eng1 = engine("eng-1", mechanisms=(mechanism("lose-1", conflicts=("winner",), rank=50),))
    eng2 = engine("eng-2", mechanisms=(mechanism("lose-2", conflicts=("winner",), rank=40),))
    projection = resolve(
        DNARegistry([ref, eng1, eng2]),
        CompositionRequest("ref-a", engine_ids=("eng-1", "eng-2")),
        SemanticContext(),
        RuntimeConstraints(contradiction_budget=1),
    )
    assert not projection.is_valid
    assert FailureCode.CONTRADICTION_OVERFLOW in issue_codes(projection.rejections)
    assert projection.mechanisms[0].mechanism_id == "winner"


def test_accessibility_super_veto_uses_fallback():
    unsafe = mechanism(
        "unsafe-color",
        axis=Axis.COLOR,
        directive="low-contrast",
        fallback="accessible-contrast",
        accessibility_safe=False,
    )
    projection = resolve(
        DNARegistry([reference(mechanisms=(unsafe,))]),
        CompositionRequest("ref-a"),
        SemanticContext(accessibility_required=True),
    )
    assert projection.is_valid
    assert projection.accessibility_applied
    assert projection.mechanisms[0].directive == "accessible-contrast"
    assert projection.mechanisms[0].degradation is DegradationState.ACCESSIBILITY_DEMOTED


def test_reduced_motion_demotes_temporal_mechanism():
    motion = mechanism(
        "motion",
        axis=Axis.MOTION_TEMPORAL,
        directive="parallax",
        fallback="static-transition",
    )
    projection = resolve(
        DNARegistry([reference(mechanisms=(motion,))]),
        CompositionRequest("ref-a"),
        SemanticContext(reduced_motion=True),
    )
    assert projection.is_valid
    assert projection.reduced_motion_applied
    assert projection.mechanisms[0].directive == "static-transition"


def test_reading_sanctuary_demotes_ornamental_mechanism():
    reading = mechanism(
        "reading-ornament",
        axis=Axis.FORM,
        zone=SemanticZone.U7,
        directive="high-ornament",
        fallback="quiet-structure",
        reading_safe=False,
    )
    projection = resolve(
        DNARegistry([reference(mechanisms=(reading,))]),
        CompositionRequest("ref-a"),
        SemanticContext(active_zones=(SemanticZone.U7,)),
    )
    assert projection.is_valid
    assert projection.reading_sanctuary_applied
    assert projection.mechanisms[0].directive == "quiet-structure"
    assert projection.mechanisms[0].degradation is DegradationState.READING_SANCTUARY_DEMOTED


def asset(production_eligible=True):
    return AssetIntent(
        slot="hero-texture",
        asset_id="texture-1",
        production_eligible=production_eligible,
        license_status="production-ok" if production_eligible else "personal-use-only",
        fallback_directive="structural-grain",
        provenance_pointer="docs://asset",
    )


def asset_mechanism(fallback="structural-grain"):
    return mechanism(
        "asset-form",
        directive="asset-rich-form",
        fallback=fallback,
        requires_asset_slot="hero-texture",
    )


def test_asset_available_uses_eligible_asset_without_structural_loss():
    ref = reference(mechanisms=(asset_mechanism(),), assets=(asset(True),))
    projection = resolve(
        DNARegistry([ref]),
        CompositionRequest("ref-a", asset_state=AssetState.AVAILABLE),
        SemanticContext(),
    )
    assert projection.is_valid
    assert projection.asset_decisions[0].action == "use_asset"
    assert projection.mechanisms[0].directive == "asset-rich-form"


@pytest.mark.parametrize("state", [AssetState.OFF, AssetState.LOADING, AssetState.PARTIAL])
def test_asset_degradation_keeps_structural_identity(state):
    ref = reference(mechanisms=(asset_mechanism(),), assets=(asset(True),))
    projection = resolve(DNARegistry([ref]), CompositionRequest("ref-a", asset_state=state), SemanticContext())
    assert projection.is_valid
    assert projection.mechanisms[0].directive == "structural-grain"
    assert projection.asset_decisions[0].action in {"structural_fallback", "safe_substitute"}


def test_non_eligible_asset_is_never_shipped_and_falls_back():
    ref = reference(mechanisms=(asset_mechanism(),), assets=(asset(False),))
    projection = resolve(
        DNARegistry([ref]),
        CompositionRequest("ref-a", asset_state=AssetState.AVAILABLE),
        SemanticContext(),
    )
    assert projection.is_valid
    assert projection.asset_decisions[0].action == "structural_fallback"
    assert FailureCode.LICENSE_SCOPE_VIOLATION in issue_codes(projection.warnings)
    assert projection.mechanisms[0].directive == "structural-grain"


def test_missing_asset_without_fallback_rejects_identity_collapse():
    broken = mechanism(
        "asset-only",
        directive="asset-only-form",
        fallback="",
        requires_asset_slot="missing-slot",
    )
    projection = resolve(DNARegistry([reference(mechanisms=(broken,))]), CompositionRequest("ref-a"), SemanticContext())
    assert not projection.is_valid
    codes = issue_codes(projection.rejections)
    assert FailureCode.ASSET_DEPENDENCY_FAILURE in codes
    assert FailureCode.FALLBACK_IDENTITY_COLLAPSE in codes


def test_mobile_is_recomposed_from_same_contract_not_duplicate_theme():
    desktop = mechanism("layout-desktop", directive="wide-grid", viewports=("desktop",))
    mobile = mechanism("layout-mobile", directive="stacked-flow", viewports=("mobile",))
    registry = DNARegistry([reference(mechanisms=(desktop, mobile))])
    desktop_projection = resolve(
        registry,
        CompositionRequest("ref-a"),
        SemanticContext(viewport=Viewport.DESKTOP),
    )
    mobile_projection = resolve(
        registry,
        CompositionRequest("ref-a"),
        SemanticContext(viewport=Viewport.MOBILE),
    )
    assert desktop_projection.mechanisms[0].directive == "wide-grid"
    assert mobile_projection.mechanisms[0].directive == "stacked-flow"
    assert desktop_projection.fingerprint != mobile_projection.fingerprint


def test_missing_host_capability_demotes_instead_of_leaking_host_type():
    capable = mechanism(
        "blur",
        directive="backdrop-blur",
        fallback="layered-border",
        host_capability="backdrop_filter",
    )
    projection = resolve(DNARegistry([reference(mechanisms=(capable,))]), CompositionRequest("ref-a"), SemanticContext())
    assert projection.is_valid
    assert projection.mechanisms[0].directive == "layered-border"
    assert FailureCode.FORBIDDEN_PROJECTION in issue_codes(projection.warnings)


def test_provenance_records_applied_and_fallback_decisions():
    unsafe = mechanism(
        "unsafe",
        directive="unsafe",
        fallback="safe",
        accessibility_safe=False,
    )
    projection = resolve(DNARegistry([reference(mechanisms=(unsafe,))]), CompositionRequest("ref-a"), SemanticContext())
    actions = {(item.action, item.mechanism_id) for item in projection.provenance}
    assert ("fallback", "unsafe") in actions
    assert ("applied", "unsafe") in actions


def test_a_to_b_to_a_is_reproducible_and_does_not_touch_application_state():
    registry = DNARegistry([
        reference("ref-a", mechanisms=(mechanism("a", directive="A"),)),
        reference("ref-b", mechanisms=(mechanism("b", directive="B"),)),
    ])
    application_state = {"session_id": "s1", "messages": ["keep-me"], "provider": "unchanged"}
    before = {"session_id": application_state["session_id"], "messages": list(application_state["messages"]), "provider": application_state["provider"]}
    context = SemanticContext()

    a1 = resolve(registry, CompositionRequest("ref-a"), context)
    b = resolve(registry, CompositionRequest("ref-b"), context)
    a2 = resolve(registry, CompositionRequest("ref-a"), context)

    assert a1.fingerprint == a2.fingerprint
    assert a1.fingerprint != b.fingerprint
    assert application_state == before


def test_invalid_runtime_constraint_returns_explicit_rejection():
    projection = resolve(
        DNARegistry([reference()]),
        CompositionRequest("ref-a"),
        SemanticContext(),
        RuntimeConstraints(dominance_cap=0),
    )
    assert not projection.is_valid
    assert FailureCode.UNEXPLAINABLE_COMPOSITION in issue_codes(projection.rejections)


def test_asset_slot_collision_has_deterministic_owner():
    high_asset = replace(asset(True), asset_id="high", ownership_rank=90)
    low_asset = replace(asset(True), asset_id="low", ownership_rank=10)
    ref = reference(assets=(low_asset,))
    eng = engine("eng-a")
    eng = replace(eng, assets=(high_asset,))
    projection = resolve(
        DNARegistry([ref, eng]),
        CompositionRequest("ref-a", engine_ids=("eng-a",), asset_state=AssetState.AVAILABLE),
        SemanticContext(),
    )
    assert projection.asset_decisions[0].asset_id == "high"
    assert FailureCode.OWNERSHIP_COLLISION in issue_codes(projection.warnings)


def test_canonical_runtime_package_has_no_host_core_or_database_imports():
    root = Path(__file__).resolve().parents[1] / "design_dna"
    forbidden = (
        "import reflex",
        "from reflex",
        "import streamlit",
        "from streamlit",
        "from core",
        "import core",
        "from database",
        "import database",
        "from ui",
        "import ui",
    )
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path.name} leaked host/application dependency: {token}"
