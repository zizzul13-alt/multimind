"""The session regions render the live deliberation, per shell shape.

No provider keys are configured in this environment, so a real debate cannot run.
These tests exercise the other half of the chain instead: that the projection a
completed run produces is exactly what the shell renderers read, and that each
renderer's output carries the shell's own region classes.
"""

import pytest

from multimind_reflex.deliberation_projection import (
    critique_snapshots,
    participant_snapshots,
    run_summary,
)

RAW = {
    "deliberation": [
        {
            "round": "1",
            "participant_id": "p1",
            "requested_identity": "analyst",
            "effective_identity": "analyst",
            "requested_provider": "gemini",
            "actual_provider": "gemini",
            "route_provider": "gemini",
            "status": "success",
            "text": "Model kedua tetap fallback; identitas model tidak boleh dipalsukan.",
        },
        {
            "round": "1",
            "participant_id": "p2",
            "requested_identity": "skeptic",
            "effective_identity": "skeptic",
            "requested_provider": "deepseek",
            "actual_provider": "deepseek",
            "route_provider": "deepseek",
            "status": "success",
            "text": "Fallback boleh terjadi tanpa memutus hubungan antar-pesan.",
        },
    ],
    "participants": [
        {
            "participant_id": "p1",
            "requested_identity": "analyst",
            "effective_identity": "analyst",
            "requested_provider": "gemini",
            "actual_provider": "gemini",
            "route_provider": "gemini",
            "model": "gemini-2.5-pro",
            "role": "analyst",
        },
        {
            "participant_id": "p2",
            "requested_identity": "skeptic",
            "effective_identity": "skeptic",
            "requested_provider": "deepseek",
            "actual_provider": "deepseek",
            "route_provider": "deepseek",
            "model": "",
            "role": "skeptic",
        },
    ],
    "judge": {"provider": "gemini", "status": "success"},
    "selected_participants": 2,
}


def test_projection_is_what_the_renderers_read():
    critiques = critique_snapshots(RAW)
    assert len(critiques) == 2
    # the keys the renderers index must exist on every row
    for c in critiques:
        for key in (
            "round",
            "participant_id",
            "requested_identity_label",
            "effective_identity_label",
            "requested_provider",
            "actual_provider",
            "status",
            "text",
        ):
            assert key in c, f"renderer reads {key}"
    summary = run_summary(RAW)
    assert "judge_provider" in summary
    assert "system_verdict" in summary


def test_participant_snapshot_has_the_fields_the_canvas_reads():
    parts = participant_snapshots(RAW)
    assert len(parts) == 2
    for p in parts:
        for key in ("participant_id", "model", "requested_provider"):
            assert key in p


# (renderer, region class, which projection feeds it)
RENDERERS = [
    ("_chat_turn", "mm-message", "critique"),
    ("_evidence_turn", "mm-evidence-row", "critique"),
    ("_thread_turn", "mm-thread", "critique"),
    ("_state_row", "mm-state-row", "critique"),
    ("_agent_card", "mm-cap", "participant"),
]


@pytest.mark.parametrize("renderer,expected_class,source", RENDERERS)
def test_each_renderer_emits_its_previews_region_class(renderer, expected_class, source):
    """Each session renderer must emit the region class its preview declares.

    Asserted against the renderer source because the class may sit inside an
    rx.cond branch, which a render-tree walk does not reach. The browser harness
    (tools/session-regions.mjs) confirms the class actually lands in the DOM.
    """
    import inspect

    import multimind_reflex.shells as shells

    fn = getattr(shells, renderer, None)
    assert fn is not None, f"{renderer} missing"
    body = inspect.getsource(fn)
    assert expected_class in body, (
        f"{renderer} does not emit .{expected_class}; the preview's region would "
        "have no hook for the live state"
    )
    # and it must read the projection, not just hold static copy
    assert "turn[" in body or "participant[" in body, (
        f"{renderer} does not read the projection row"
    )


def test_projection_keys_cover_every_field_a_renderer_indexes():
    """Any turn[key] a renderer uses must exist on a real snapshot."""
    import inspect
    import re

    import multimind_reflex.shells as shells

    turn = critique_snapshots(RAW)[0]
    part = participant_snapshots(RAW)[0]
    for name, _cls, source in RENDERERS:
        body = inspect.getsource(getattr(shells, name))
        row = part if source == "participant" else turn
        for key in re.findall(r'(?:turn|participant)\["([a-z_]+)"\]', body):
            assert key in row, f"{name} reads {key}, absent from the projection"
