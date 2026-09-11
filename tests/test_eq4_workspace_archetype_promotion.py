"""EQ4 regression locks for production-workspace archetype promotion."""
from __future__ import annotations

import inspect

import multimind_reflex.multimind_reflex as surface


ARCHETYPES = (
    "chat_first",
    "command_center",
    "ai_workspace",
    "ai_research_lab",
    "agent_canvas",
    "terminal_hacker",
    "minimal_saas",
)


def test_workspace_structurally_consumes_all_seven_archetypes():
    source = inspect.getsource(surface)
    for archetype in ARCHETYPES:
        assert f'HostState.active_archetype == "{archetype}"' in source or archetype == "minimal_saas"

    assert "_workspace_desktop_areas" in source
    assert "_workspace_mobile_areas" in source
    assert "grid_template_areas=rx.breakpoints" in source
    assert "grid_template_columns=rx.breakpoints" in source


def test_workspace_uses_one_set_of_real_semantic_zones():
    source = inspect.getsource(surface)
    workspace_source = inspect.getsource(surface._workspace)

    # Four application-facing zones are instantiated exactly once by the real
    # workspace. Archetype changes composition, not ownership or event paths.
    for call in (
        "_workspace_utility_zone()",
        "_workspace_composer_zone()",
        "_workspace_result_zone()",
        "_workspace_history_zone()",
    ):
        assert workspace_source.count(call) == 1

    # Upload/restore identifiers remain single canonical controls rather than
    # seven archetype-specific copies.
    assert source.count('id=UPLOAD_ID') == 1
    assert source.count('id=RESTORE_ID') == 1


def test_mobile_archetype_layout_is_not_desktop_crop():
    source = inspect.getsource(surface._workspace_mobile_areas)
    assert 'HostState.active_archetype == "command_center"' in source
    assert 'HostState.active_archetype == "ai_research_lab"' in source
    assert 'HostState.active_archetype == "agent_canvas"' in source
    assert '"result" "composer" "history" "utility"' in source
    assert '"result" "history" "composer" "utility"' in source
    assert '"composer" "result" "utility" "history"' in source


def test_workspace_promotion_stays_presentation_only_and_reference_neutral():
    source = inspect.getsource(surface)
    assert "MultiMindApplication" not in source
    assert "DebateOrchestrator" not in source
    assert "sqlite3" not in source
    assert "design_dna" not in source

    for forbidden in (
        "CW01",
        "CW02",
        "CW03",
        "CW04",
        "CW05",
        "CS07",
        "CS08",
        "CS10",
        "CS17",
        "IZA07",
        "MR-023",
    ):
        assert forbidden not in source


def test_terminal_and_minimal_saas_have_distinct_host_treatment():
    source = inspect.getsource(surface._workspace)
    assert 'HostState.active_archetype == "minimal_saas"' in source
    assert 'HostState.active_archetype == "terminal_hacker"' in source
    assert "HostState.active_mono_font" in source
    assert '"68rem"' in source
    assert '"76rem"' in source
