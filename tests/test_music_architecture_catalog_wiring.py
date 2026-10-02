"""Behaviour tests for the MusicDNA architecture catalog wiring.

The existing selector tests only assert that certain function names appear in
the source text, which is why a completely unwired catalog could pass. These
tests stub the optional design_dna runtime and assert real behaviour:

  - the architecture list is derived from the runtime, not a constant
  - a broken/absent runtime produces a visible error, not silence
  - the two-dropdown shape is preserved
"""
import importlib
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ARCHETYPES = (
    "chat_first",
    "command_center",
    "ai_workspace",
    "ai_research_lab",
    "agent_canvas",
    "terminal_hacker",
    "minimal_saas",
)


def _install_fake_design_dna(monkeypatch, *, archetypes=ARCHETYPES, tracks=2):
    """Install a stub design_dna.music_runtime exposing the real contract."""
    music_runtime = types.ModuleType("design_dna.music_runtime")
    music_runtime.ARCHETYPES = tuple(archetypes)
    music_runtime.list_music_architecture_options = lambda include_all=True: tuple(
        f"music:track{index}@{archetype}"
        for index in range(tracks)
        for archetype in archetypes
    )
    music_runtime.list_music_options = lambda include_all=True: tuple(
        types.SimpleNamespace(
            id=f"track{index}",
            display_name=f"Track {index}",
            artist="Artist",
            tier="reference",
            source_preview="preview",
            signature="sig",
            world="forward-inevitability",
        )
        for index in range(tracks)
    )
    music_runtime.realize_music_theme = lambda track_id, archetype_id: types.SimpleNamespace(
        track_id=track_id,
        archetype_id=archetype_id,
        display_name="Track 0",
        artist="Artist",
        reference_id="TRACK0",
        topology="forward-inevitability",
        tier="reference",
        combination_id=f"{track_id}@{archetype_id}",
        source_preview="preview",
        signature="sig",
        world="forward-inevitability",
        layout_flow="chat_first",
        mobile_strategy="responsive",
        density="comfortable",
        radius="8px",
        primary_object="panel",
        primary_action="send",
        composer_label="label",
        font_family="system-ui",
        mono_font="monospace",
        background="#000000",
        surface="#111111",
        text="#ffffff",
        primary="#6b8cff",
        accent="#9bb0ff",
        border="#2a3350",
        asset_url="",
        asset_credit="",
    )

    design_dna = types.ModuleType("design_dna")
    design_dna.__path__ = []
    design_dna.music_runtime = music_runtime
    monkeypatch.setitem(sys.modules, "design_dna", design_dna)
    monkeypatch.setitem(sys.modules, "design_dna.music_runtime", music_runtime)
    return music_runtime


def test_archetypes_come_from_runtime_not_a_hardcoded_constant(monkeypatch):
    """The runtime advertises an extra architecture the UI must pick up."""
    extended = ARCHETYPES + ("grid_canvas",)
    _install_fake_design_dna(monkeypatch, archetypes=extended)

    from ui.music_dna_bridge import list_music_archetype_ids

    ids = list_music_archetype_ids()
    assert ids == extended, (
        "architecture list must be sourced from the runtime so a package "
        "update reaches the picker without a code change"
    )
    # distinct + stable order, no duplicates from the cross-product
    assert len(ids) == len(set(ids))


def test_cross_product_is_reduced_to_unique_architectures(monkeypatch):
    _install_fake_design_dna(monkeypatch, tracks=5)
    from ui.music_dna_bridge import list_music_archetype_ids, list_music_archetypes

    # 5 tracks x 7 archetypes = 35 combinations
    assert len(list_music_archetypes()) == 35
    # reduced back to 7 for the two-dropdown picker
    assert list_music_archetype_ids() == ARCHETYPES


def test_absent_runtime_raises_instead_of_returning_empty(monkeypatch):
    """Silence is the bug being fixed: absence must be explicit."""
    monkeypatch.setitem(sys.modules, "design_dna", None)
    for name in list(sys.modules):
        if name.startswith("design_dna"):
            monkeypatch.delitem(sys.modules, name, raising=False)

    # A missing package must produce a reason, not an empty catalog.
    from ui.music_dna_bridge import MusicDNAUnavailable, list_music_archetype_ids

    with pytest.raises(MusicDNAUnavailable):
        list_music_archetype_ids()


def test_incompatible_runtime_is_reported(monkeypatch):
    """A package missing the expected function must not look like 'no data'."""
    broken = types.ModuleType("design_dna.music_runtime")
    design_dna = types.ModuleType("design_dna")
    design_dna.__path__ = []
    design_dna.music_runtime = broken
    monkeypatch.setitem(sys.modules, "design_dna", design_dna)
    monkeypatch.setitem(sys.modules, "design_dna.music_runtime", broken)

    from ui.music_dna_bridge import music_dna_unavailable_reason

    reason = music_dna_unavailable_reason()
    assert reason is not None
    assert "list_music_architecture_options" in reason


def test_selector_is_runtime_driven_and_shows_error_on_failure():
    """Guard the UI wiring itself: no hardcoded ARCHETYPES in the select."""
    source = (REPO / "multimind_reflex" / "multimind_reflex.py").read_text(
        encoding="utf-8"
    )
    assert "HostState.music_dna_archetypes" in source, (
        "the architecture select must be driven by the runtime catalog"
    )
    assert "HostState.music_dna_archetype_error" in source, (
        "the picker must render the runtime failure reason"
    )
    # the constant must not be what feeds rx.select any more
    assert "rx.select(\n                        ARCHETYPES," not in source
