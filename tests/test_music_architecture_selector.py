from pathlib import Path

STATE = Path("multimind_reflex/workspace_dna_state.py").read_text(encoding="utf-8")
SURFACE = Path("multimind_reflex/multimind_reflex.py").read_text(encoding="utf-8")
BRIDGE = Path("ui/music_dna_bridge.py").read_text(encoding="utf-8")


def test_entry_selector_uses_musicdna_catalog_and_architecture_axis():
    assert "music_dna_choices" in STATE
    assert "startswith(\"music:\")" in STATE
    assert "ARCHETYPES" in SURFACE
    assert "HostState.music_dna_choices" in SURFACE
    assert "HostState.set_composed_identity_choice" in SURFACE
    assert "HostState.set_composed_archetype" in SURFACE


def test_music_architecture_remains_private_runtime_owned():
    assert "import_module(\"design_dna.music_runtime\")" in BRIDGE
    assert "list_music_architecture_combinations" in BRIDGE
    assert "realize_music_theme" in BRIDGE
    assert "MusicArchitecturePlan" in BRIDGE


def test_old_canonical_160_picker_is_not_the_entry_surface():
    assert "Canonical Reference DNA" not in SURFACE
    assert "Canonical 160" not in SURFACE
    assert "MusicDNA × Architecture" in SURFACE
