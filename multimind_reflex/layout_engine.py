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
    get_track_theme = lambda _tid: None  # noqa: E731

def _load_tokens() -> dict[str, Any]:
    env = os.getenv("MULTIMIND_LAYOUT_TOKENS", "")
    candidates = [
        Path(env) if env else None,
        Path("F:/hermes/cache/scratch/layout_tokens_flat.json"),
        Path(__file__).resolve().parent.parent.parent.parent / "cache" / "scratch" / "layout_tokens_flat.json",
    ]
    for p in candidates:
        if p and p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raw = Path("F:/hermes/cache/scratch/layout_tokens.json")
    if raw.exists():
        data = json.loads(raw.read_text(encoding="utf-8"))
        out = {}
        for t in data.get("tracks_with_layout", []):
            tid = t["track_id"].lower()
            files = t.get("files", [])
            pf = files[0] if files else {}
            out[tid] = {
                "grid": (pf.get("grid_template_columns") or [""])[0],
                "sections": pf.get("grid_containers", []),
                "breakpoints": pf.get("breakpoints", []),
                "header_variant": "fullscreen" if any(".window" in str(c) for c in pf.get("grid_containers", [])) else "compact",
            }
        return out
    return {}


def _token_for(track_id: str) -> dict[str, Any]:
    cache = _LAYOUT_CACHE.setdefault("tokens", _load_tokens())
    return cache.get(track_id.lower(), {})


def layout_grid(track_id: str, archetype: str = "default") -> str:
    """Return the CSS grid-template for the app shell given a track.

    Falls through: track-specific layout -> archetype default -> safe base.
    """
    tok = _token_for(track_id)

    # 1. Track-specific grid template
    grid = tok.get("grid_template")
    if grid:
        return grid

    # 2. Archetype-derived defaults (vertical split, sidebar, full)
    arch = (archetype or "default").lower()
    arch_map = {
        "command_center": "grid-template-columns: 280px 1fr",
        "ai_workspace": "grid-template-columns: 320px minmax(0, 1fr)",
        "ai_research_lab": "grid-template-columns: minmax(0, 0.55fr) minmax(0, 1fr)",
        "agent_canvas": "grid-template-columns: 1fr",
        "terminal_hacker": "grid-template-columns: 260px 1fr",
        "minimal_saas": "grid-template-columns: 0.55fr 1fr",
    }
    return arch_map.get(arch, "grid-template-columns: 320px 1fr")


def header_variant(track_id: str) -> str:
    tok = _token_for(track_id)
    return (tok.get("header_variant") or "compact").lower()


def composer_shape(track_id: str) -> str:
    tok = _token_for(track_id)
    return (tok.get("composer_shape") or "prompt-primary").lower()


def evidence_rail(track_id: str) -> str:
    tok = _token_for(track_id)
    return (tok.get("evidence_rail") or "right").lower()


def breakpoint_presets(track_id: str) -> dict[str, str]:
    tok = _token_for(track_id)
    bp = tok.get("breakpoints") or {}
    if isinstance(bp, dict):
        return bp
    if isinstance(bp, list):
        return {f"bp{i}": v for i, v in enumerate(bp)}
    return {}


def compose_layout(track_id: str, archetype: str = "default") -> dict[str, Any]:
    """Build the full layout spec consumed by the page composer."""
    tid = str(track_id or "").strip().lower()
    return {
        "track_id": tid,
        "grid": layout_grid(tid, archetype),
        "header": header_variant(tid),
        "composer": composer_shape(tid),
        "evidence_rail": evidence_rail(tid),
        "breakpoints": breakpoint_presets(tid),
        "theme": get_track_theme(tid) if HAS_DNA else None,
    }


__all__ = [
    "layout_grid",
    "header_variant",
    "composer_shape",
    "evidence_rail",
    "breakpoint_presets",
    "compose_layout",
]
