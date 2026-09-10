"""Canonical private Design-DNA public bridge boundary tests."""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import ui.canonical_dna_bridge as bridge


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_bridge_has_no_eager_private_imports():
    path = ROOT / "ui/canonical_dna_bridge.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    assert all(not name.startswith("design_dna") for name in imports)
    assert all(not name.startswith("dna_quarantine") for name in imports)


def test_missing_or_broken_private_canonical_runtime_is_safe(monkeypatch):
    monkeypatch.setattr(bridge, "import_module", lambda name: (_ for _ in ()).throw(ModuleNotFoundError(name)))
    assert bridge.canonical_dna_available() is False
    assert bridge.list_canonical_reference_options() == ()
    assert bridge.resolve_canonical_reference("CW03") is None

    monkeypatch.setattr(bridge, "import_module", lambda _name: (_ for _ in ()).throw(RuntimeError("broken")))
    assert bridge.canonical_dna_available() is False
    assert bridge.list_canonical_reference_options() == ()
    assert bridge.resolve_canonical_reference("CW03") is None


def _enum(value):
    return SimpleNamespace(value=value)


def test_catalog_and_projection_cross_bridge_as_scalar_host_safe_values(monkeypatch):
    options = [
        SimpleNamespace(
            id="CW03",
            display_name="Japan — Japanese commerce/public-service high-information lineage",
            family="Japan — Japanese commerce/public-service high-information lineage",
            category="country_web",
            lineage="country-web-scoped-digital-lineage",
        ),
        SimpleNamespace(
            id="IZA07",
            display_name="Serial Experiments Lain",
            family="IZZUL_PERSONAL_MEDIA_ANIME",
            category="izzul_anime",
            lineage="izzul-personal-media-anime-serial-experiments-lain",
        ),
    ]
    projection = SimpleNamespace(
        composition_id="IZA07|E:|P:P05,P06,P17|A:chat_first",
        fingerprint="abc123",
        archetype_id="chat_first",
        viewport=_enum("mobile"),
        interaction_state="default",
        mechanisms=(
            SimpleNamespace(
                axis=_enum("INFORMATION"),
                zone=_enum("U3_PRIMARY_WORK_SURFACE"),
                directive="mediated-presence-network-ambiguity",
                source_unit_id="IZA07",
                mechanism_id="IZA07-identity",
                ownership_rank=86,
                degradation=_enum("full"),
            ),
        ),
        asset_decisions=(),
        provenance=(
            SimpleNamespace(
                action="applied",
                source_unit_id="IZA07",
                mechanism_id="IZA07-identity",
                axis=_enum("INFORMATION"),
                zone=_enum("U3_PRIMARY_WORK_SURFACE"),
                reason="deterministic ownership winner",
            ),
        ),
        warnings=(),
        rejections=(),
        accessibility_applied=False,
        reading_sanctuary_applied=False,
        reduced_motion_applied=False,
    )
    result = SimpleNamespace(
        reference=options[1],
        projection=projection,
        primitive_ids=("P05", "P06", "P17"),
    )
    runtime = SimpleNamespace(
        list_reference_options=lambda: options,
        resolve_reference=lambda *args, **kwargs: result,
    )

    class Viewport:
        def __new__(cls, value):
            return _enum(value)

    class AssetState:
        def __new__(cls, value):
            return _enum(value)

    models = SimpleNamespace(Viewport=Viewport, AssetState=AssetState)

    def importer(name: str):
        if name == "design_dna.host_runtime":
            return runtime
        if name == "design_dna.models":
            return models
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(bridge, "import_module", importer)
    assert bridge.canonical_dna_available() is True

    catalog = bridge.list_canonical_reference_options()
    assert [item.id for item in catalog] == ["CW03", "IZA07"]
    assert catalog[1].display_name == "Serial Experiments Lain"
    assert catalog[1].category == "izzul_anime"

    resolved = bridge.resolve_canonical_reference("IZA07", viewport="mobile")
    assert isinstance(resolved, bridge.CanonicalPresentationProjection)
    assert resolved.is_valid
    assert resolved.reference.display_name == "Serial Experiments Lain"
    assert resolved.viewport == "mobile"
    assert resolved.primitive_ids == ("P05", "P06", "P17")
    assert resolved.mechanisms[0].axis == "INFORMATION"
    assert resolved.mechanisms[0].source_unit_id == "IZA07"
    assert resolved.provenance[0]["action"] == "applied"
    assert resolved.fingerprint == "abc123"


def test_private_operation_failure_degrades_without_escaping(monkeypatch):
    runtime = SimpleNamespace(
        list_reference_options=lambda: (_ for _ in ()).throw(RuntimeError("catalog boom")),
        resolve_reference=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("resolve boom")),
    )
    models = SimpleNamespace(
        Viewport=lambda value: value,
        AssetState=lambda value: value,
    )

    def importer(name: str):
        return runtime if name.endswith("host_runtime") else models

    monkeypatch.setattr(bridge, "import_module", importer)
    assert bridge.list_canonical_reference_options() == ()
    assert bridge.resolve_canonical_reference("CW03") is None
