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
    upload_source = inspect.getsource(surface._upload_panel)
    restore_source = inspect.getsource(surface._data_ops)

    # The composition lives in _archetype_shell(), which dispatches to a
    # per-archetype shell. Exactly one branch renders at runtime, so each zone is
    # still instantiated once. The shells themselves live in shells.py, so that is
    # where the zone calls are asserted.
    assert "_archetype_shell()" in workspace_source

    import multimind_reflex.shells as shells_mod
    shell_source = inspect.getsource(shells_mod)

    def zone_uses(src: str, name: str) -> int:
        """Count how many times a zone is composed.

        shells.py resolves zones through the lazy _zone() helper to avoid a
        circular import, so a use appears either as a direct call or as a name
        passed to _zone(). Both spellings count as one composition.
        """
        return src.count(f"{name}()") + src.count(f'_zone("{name}")')

    for name in (
        "_workspace_utility_zone",
        "_workspace_composer_zone",
        "_workspace_result_zone",
        "_workspace_history_zone",
    ):
        # At least one shell composes each zone, and no shell may compose the same
        # zone twice.
        assert zone_uses(shell_source, name) >= 1, f"{name} missing from the shells"
        for shell_fn in (f for n, f in vars(shells_mod).items() if n.startswith("shell_")):
            body = inspect.getsource(shell_fn)
            assert zone_uses(body, name) <= 1, (
                f"{name} appears more than once in {shell_fn.__name__}; a zone is "
                "being duplicated inside a shell"
            )

    # There are exactly two upload widgets in the entire production surface:
    # the existing prompt-file input and the existing restore input. Archetype
    # promotion must not create per-archetype copies of either control.
    assert source.count("rx.upload(") == 2
    assert "id=UPLOAD_ID" in upload_source
    assert "id=RESTORE_ID" in restore_source
    assert upload_source.count("rx.upload(") == 1
    assert restore_source.count("rx.upload(") == 1


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
    # SQLite filenames/MIME strings are legitimate restore UI metadata. What
    # presentation must never acquire is database connection/path ownership.
    assert "sqlite3.connect(" not in source
    assert "Config.get_db_path" not in source
    assert "database.manager" not in source
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