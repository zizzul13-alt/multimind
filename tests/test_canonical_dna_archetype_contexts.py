import inspect

import multimind_reflex.canonical_archetype_proving as proving
import multimind_reflex.canonical_contexts as contexts
import multimind_reflex.canonical_dna_state as state


EXPECTED_ARCHETYPES = (
    "chat_first",
    "command_center",
    "ai_workspace",
    "ai_research_lab",
    "agent_canvas",
    "terminal_hacker",
    "minimal_saas",
)


def test_exact_seven_archetype_contexts_are_present_and_unique():
    assert contexts.CANONICAL_ARCHETYPE_IDS == EXPECTED_ARCHETYPES
    assert len(contexts.ARCHETYPE_CONTEXTS) == 7
    assert len({item.id for item in contexts.ARCHETYPE_CONTEXTS}) == 7
    assert len({item.primary_object for item in contexts.ARCHETYPE_CONTEXTS}) == 7


def test_each_archetype_has_complete_semantic_fixture_without_application_truth():
    for item in contexts.ARCHETYPE_CONTEXTS:
        for value in (
            item.display_name,
            item.primary_object,
            item.context_title,
            item.context_body,
            item.work_title,
            item.work_body,
            item.action_title,
            item.action_body,
            item.state_title,
            item.state_body,
            item.auxiliary_title,
            item.auxiliary_body,
        ):
            assert isinstance(value, str) and value.strip()
    source = inspect.getsource(contexts).lower()
    for forbidden in ("from core", "from providers", "from database", "multimindapplication", "sqlite", "turso"):
        assert forbidden not in source


def test_canonical_resolution_uses_selected_archetype_instead_of_chat_first_constant():
    source = inspect.getsource(state.CanonicalDnaState._refresh_plan)
    assert "archetype_id=self.preview_archetype" in source
    assert 'archetype_id="chat_first"' not in source
    assert "set_preview_archetype" in inspect.getsource(state.CanonicalDnaState)


def test_archetype_renderer_branches_only_on_archetype_not_dna_identity():
    source = inspect.getsource(proving)
    for archetype_id in EXPECTED_ARCHETYPES[:-1]:
        assert f'preview_archetype == "{archetype_id}"' in source
    for forbidden_id in (
        "CW01", "CW02", "CW03", "CW04", "CW05", "CS07", "CS08", "CS10", "CS17",
        "IZA07", "IZM02", "IZW05", "MR-023",
    ):
        assert forbidden_id not in source
    assert "selected_reference_id ==" not in source


def test_archetype_scaffolds_are_structurally_distinct():
    source = inspect.getsource(proving)
    for helper in (
        "_chat_first",
        "_command_center",
        "_ai_workspace",
        "_research_lab",
        "_agent_canvas",
        "_terminal_hacker",
        "_minimal_saas",
    ):
        assert f"def {helper}" in source
    assert "Agent" not in source or "Agent Canvas" not in source  # no per-agent application data fixture


def test_unknown_archetype_context_falls_back_boringly():
    assert contexts.get_archetype_context("not-real") == contexts.get_archetype_context("chat_first")
