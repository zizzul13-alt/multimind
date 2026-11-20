"""Layout engine: consume per-track layout tokens from Design-DNA
and project them into the Multimind Reflex workspace grid.

This module bridges the hand-built HTML preview layouts (parsed from
preview/lab/music-v0/*.html) into live Reflex component structure.
Each TrackTheme maps to a LayoutSpec that decides:
  - grid template columns (sidebar vs content width)
  - header variant (fullscreen / compact / compact-top)
  - composer region shape (prompt-primary / split-prompt)
  - evidence rail orientation
  - breakpoint overrides

The tokens are populated from the compiled JSON emitted by the
parsing subagent — ``layout_tokens.json`` — but the engine is
decoupled: passing a track_id yields a concrete layout dict used by
the page composer.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from design_dna.music_theme_standard import TRACK_THEMES, get_track_theme
    HAS_DNA = True
except Exception:  # pragma: no cover — DNA offline during bare tests
    HAS_DNA = False
    TRACK_THEMES = {}

    def get_track_theme(_tid: Any) -> None:  # type: ignore[misc]
        return None


_LAYOUT_CACHE: dict[str, Any] = {}
_ARCH_CACHE: dict[str, Any] = {}


def _flat_candidates() -> list[Path | None]:
    """Candidate locations for the parsed flat layout-tokens JSON."""
    env = os.getenv("MULTIMIND_LAYOUT_TOKENS", "")
    return [
        Path(env) if env else None,
        Path("F:/hermes/cache/scratch/layout_tokens_flat.json"),
        Path(__file__).resolve().parent.parent.parent.parent
        / "cache"
        / "scratch"
        / "layout_tokens_flat.json",
    ]


def _load_arch_tokens() -> dict[str, Any]:
    """Load archetype outer-grid tokens from the parsed flat JSON."""
    for candidate in _flat_candidates():
        if candidate and candidate.exists():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                return data.get("archetypes", {}) or {}
            except (OSError, ValueError, TypeError):
                continue
    return {}


def _load_tokens() -> dict[str, Any]:
    for candidate in _flat_candidates():
        if candidate and candidate.exists():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, ValueError, TypeError):
                continue
    raw = Path("F:/hermes/cache/scratch/layout_tokens.json")
    if raw.exists():
        try:
            data = json.loads(raw.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        out: dict[str, Any] = {}
        for track in data.get("tracks_with_layout", []):
            track_id = str(track.get("track_id", "")).lower()
            files = track.get("files", [])
            first_file = files[0] if files else {}
            out[track_id] = {
                "grid": (first_file.get("grid_template_columns") or [""])[0],
                "sections": first_file.get("grid_containers", []),
                "breakpoints": first_file.get("breakpoints", []),
                "header_variant": "fullscreen"
                if any(".window" in str(container) for container in first_file.get("grid_containers", []))
                else "compact",
            }
        return out
    return {}


def _token_for(track_id: str) -> dict[str, Any]:
    if "tokens" not in _LAYOUT_CACHE:
        _LAYOUT_CACHE["tokens"] = _load_tokens()
    tokens = _LAYOUT_CACHE["tokens"]
    if not isinstance(tokens, dict):
        return {}
    return tokens.get(track_id.lower(), {}) or {}


def layout_grid(track_id: str, archetype: str = "default") -> str:
    """Return the CSS grid-template for the app shell given a track.

    Falls through: track-specific layout -> archetype outer grid -> safe base.
    """
    token = _token_for(track_id)

    # 1. Track-specific grid template.
    grid = token.get("grid_template") if isinstance(token, dict) else None
    if grid:
        return grid

    # 1b. Archetype outer grid parsed from architecture-swap CSS.
    arch_key = (archetype or "default").lower()
    if not _ARCH_CACHE:
        _ARCH_CACHE.update(_load_arch_tokens())
    arch_token = _ARCH_CACHE.get(arch_key, {}) if isinstance(_ARCH_CACHE, dict) else {}
    arch_grid = arch_token.get("grid_template") if isinstance(arch_token, dict) else None
    if arch_grid:
        return arch_grid

    # 2. Archetype-derived defaults (vertical split, sidebar, full).
    arch_map = {
        "command_center": "grid-template-columns: 280px 1fr",
        "ai_workspace": "grid-template-columns: 320px minmax(0, 1fr)",
        "ai_research_lab": "grid-template-columns: minmax(0, 0.55fr) minmax(0, 1fr)",
        "agent_canvas": "grid-template-columns: 1fr",
        "terminal_hacker": "grid-template-columns: 260px 1fr",
        "minimal_saas": "grid-template-columns: 0.55fr 1fr",
    }
    return arch_map.get(arch_key, "grid-template-columns: 320px 1fr")


def header_variant(track_id: str) -> str:
    token = _token_for(track_id)
    return str((token.get("header_variant") if isinstance(token, dict) else None) or "compact").lower()


def composer_shape(track_id: str) -> str:
    token = _token_for(track_id)
    return str((token.get("composer_shape") if isinstance(token, dict) else None) or "prompt-primary").lower()


def evidence_rail(track_id: str) -> str:
    token = _token_for(track_id)
    return str((token.get("evidence_rail") if isinstance(token, dict) else None) or "right").lower()


def breakpoint_presets(track_id: str) -> dict[str, Any]:
    token = _token_for(track_id)
    breakpoints = token.get("breakpoints") if isinstance(token, dict) else None
    if isinstance(breakpoints, dict):
        return breakpoints
    if isinstance(breakpoints, list):
        return {f"bp{i}": value for i, value in enumerate(breakpoints)}
    return {}


def compose_layout(track_id: str, archetype: str = "default") -> dict[str, Any]:
    """Build the full layout spec consumed by the page composer."""
    tid = str(track_id or "").strip().lower()
    theme = get_track_theme(tid) if HAS_DNA else None
    return {
        "track_id": tid,
        "grid": layout_grid(tid, archetype),
        "header": header_variant(tid),
        "composer": composer_shape(tid),
        "evidence_rail": evidence_rail(tid),
        "breakpoints": breakpoint_presets(tid),
        "theme": theme,
    }


__all__ = [
    "layout_grid",
    "header_variant",
    "composer_shape",
    "evidence_rail",
    "breakpoint_presets",
    "compose_layout",
]