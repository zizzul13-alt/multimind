"""Canonical EQ4 public bridge/search/renderer boundary tests."""
from __future__ import annotations

import inspect
from types import SimpleNamespace

import multimind_reflex.canonical_dna_state as canonical_state
import multimind_reflex.canonical_theme_studio as canonical_surface
import ui.canonical_dna_bridge as bridge


def _enum(value):
    return SimpleNamespace(value=value)


def test_search_finds_title_id_category_and_family_without_reference_specific_logic():
    options = [
        {
            "id": "CW03",
            "display_name": "Japan high-information",
            "family": "Japan commerce public service",
            "category": "country_web",
            "lineage": "country-web-lineage",
        },
        {
            "id": "IZA07",
            "display_name": "Serial Experiments Lain",
            "family": "IZZUL_PERSONAL_MEDIA_ANIME",
            "category": "izzul_anime",
            "lineage": "izzul-personal-media-anime-serial-experiments-lain",
        },
    ]
    assert [x["id"] for x in canonical_state._filter_catalog(options, "lain")] == ["IZA07"]
    assert [x["id"] for x in canonical_state._filter_catalog(options, "CW03")] == ["CW03"]
    assert [x["id"] for x in canonical_state._filter_catalog(options, "izzul anime")] == ["IZA07"]
    assert [x["id"] for x in canonical_state._filter_catalog(options, "commerce service")] == ["CW03"]


def test_realization_bridge_exposes_only_scalar_vocab_and_fails_safe(monkeypatch):
    option = SimpleNamespace(
        id="CS10",
        display_name="Futurist Typography",
        family="Futurist Typography",
        category="cultural_tier_s",
        lineage="cultural-tier-s-futurist-typography",
    )
    projection = SimpleNamespace(
        fingerprint="fp-cs10",
        viewport=_enum("mobile"),
        archetype_id="chat_first",
        mechanisms=(),
        asset_decisions=(),
        provenance=(),
        warnings=(),
        rejections=(),
        accessibility_applied=True,
        reading_sanctuary_applied=True,
        reduced_motion_applied=True,
        composition_id="CS10|E:|P:|A:chat_first",
        interaction_state="default",
    )
    resolved = SimpleNamespace(reference=option, projection=projection, primitive_ids=())
    runtime = SimpleNamespace(
        resolve_reference=lambda *args, **kwargs: resolved,
        list_reference_options=lambda: (option,),
    )
    profile = SimpleNamespace(
        layout_flow=_enum("directional"),
        balance=_enum("asymmetric"),
        density=_enum("comfortable"),
        hierarchy=_enum("dramatic"),
        continuity=_enum("none"),
        motion=_enum("static"),
        typography=_enum("directional"),
        mobile_strategy=_enum("vertical_punctuation"),
    )
    plan = SimpleNamespace(
        reference_id="CS10",
        display_name="Futurist Typography",
        source_fingerprint="fp-cs10",
        viewport="mobile",
        archetype_id="chat_first",
        profile=profile,
        active_axes=("FORM", "SPACE", "TYPOGRAPHY_SCRIPT"),
        active_zones=("U3_PRIMARY_WORK_SURFACE",),
        degraded_mechanism_count=3,
        accessibility_applied=True,
        reading_sanctuary_applied=True,
        reduced_motion_applied=True,
    )
    realizer = SimpleNamespace(
        list_host_realizable_reference_ids=lambda: ("CW01", "CW02", "CW03", "CW04", "CW05", "CS07", "CS08", "CS10", "CS17"),
        realize_for_host=lambda _resolved: plan,
    )
    models = SimpleNamespace(Viewport=lambda value: value, AssetState=lambda value: value)

    def importer(name: str):
        if name == "design_dna.host_runtime":
            return runtime
        if name == "design_dna.host_realization":
            return realizer
        if name == "design_dna.models":
            return models
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(bridge, "import_module", importer)
    assert len(bridge.list_host_realizable_reference_ids()) == 9
    result = bridge.realize_canonical_reference("CS10", viewport="mobile", reduced_motion=True)
    assert result is not None
    assert result.reference_id == "CS10"
    assert result.layout_flow == "directional"
    assert result.motion == "static"
    assert result.mobile_strategy == "vertical_punctuation"
    assert result.reduced_motion_applied is True

    monkeypatch.setattr(bridge, "import_module", lambda _name: (_ for _ in ()).throw(RuntimeError("broken")))
    assert bridge.list_host_realizable_reference_ids() == ()
    assert bridge.realize_canonical_reference("CS10") is None


def test_canonical_state_and_surface_do_not_import_application_provider_persistence_or_private_dna():
    combined = inspect.getsource(canonical_state) + inspect.getsource(canonical_surface)
    forbidden = (
        "core.application",
        "providers.",
        "database.",
        "dna_quarantine",
        "design_dna.",
        "sqlite3",
        "requests.",
    )
    assert not any(item in combined for item in forbidden)


def test_generic_surface_has_no_canonical_reference_name_or_id_branches():
    source = inspect.getsource(canonical_surface)
    for forbidden in (
        "CW01", "CW02", "CW03", "CW04", "CW05", "CS07", "CS08", "CS10", "CS17",
        "Serial Experiments Lain", "Japan Print", "Chainsaw Man",
    ):
        assert forbidden not in source
    assert "Search 160 canonical references" in source
    assert "Reduced motion" in source
    assert "Apply canonical proving presentation" in source
