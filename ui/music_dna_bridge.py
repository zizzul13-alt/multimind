"""Optional public bridge for private MusicDNA × architecture runtime.

The public host receives frozen scalar projections only. MusicDNA remains
private-package owned and MultiMind remains fully operational when the optional
runtime is absent or incompatible.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
import logging
from typing import Optional


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MusicThemeOption:
    id: str
    display_name: str
    artist: str
    tier: str
    reference_id: str
    topology: str
    source_preview: str
    signature: str
    world: str
    font_family: str
    mono_font: str
    background: str
    surface: str
    text: str
    primary: str
    accent: str
    border: str
    asset_url: str
    asset_credit: str


@dataclass(frozen=True)
class MusicArchitecturePlan:
    track_id: str
    display_name: str
    artist: str
    reference_id: str
    topology: str
    tier: str
    archetype_id: str
    combination_id: str
    source_preview: str
    signature: str
    world: str
    layout_flow: str
    mobile_strategy: str
    density: str
    radius: str
    primary_object: str
    primary_action: str
    composer_label: str
    font_family: str
    mono_font: str
    background: str
    surface: str
    text: str
    primary: str
    accent: str
    border: str
    asset_url: str
    asset_credit: str


def _optional_import():
    try:
        return import_module("design_dna.music_runtime")
    except Exception as exc:
        logger.warning("Optional MusicDNA runtime unavailable; safe presentation retained: %s", exc)
        return None


def music_dna_available() -> bool:
    return _optional_import() is not None


def list_music_theme_options(*, include_all: bool = True) -> tuple[MusicThemeOption, ...]:
    module = _optional_import()
    if module is None:
        return ()
    try:
        return tuple(
            MusicThemeOption(
                id=str(item.id),
                display_name=str(item.display_name),
                artist=str(item.artist),
                tier=str(item.tier),
                reference_id=str(item.id).upper(),
                topology=str(item.world),
                source_preview=str(item.source_preview),
                signature=str(item.signature),
                world=str(item.world),
                font_family=str(getattr(item, "font_family", "")),
                mono_font=str(getattr(item, "mono_font", "")),
                background=str(getattr(item, "background", "")),
                surface=str(getattr(item, "surface", "")),
                text=str(getattr(item, "text", "")),
                primary=str(getattr(item, "primary", "")),
                accent=str(getattr(item, "accent", "")),
                border=str(getattr(item, "border", "")),
                asset_url=str(getattr(item, "asset_url", "")),
                asset_credit=str(getattr(item, "asset_credit", "")),
            )
            for item in module.list_music_options(include_all=bool(include_all))
        )
    except Exception as exc:
        logger.warning("Optional MusicDNA catalog failed safely: %s", exc)
        return ()


def list_music_architecture_combinations(*, include_all: bool = True) -> tuple[str, ...]:
    module = _optional_import()
    if module is None:
        return ()
    try:
        return tuple(str(item) for item in module.list_music_architecture_options(include_all=bool(include_all)))
    except Exception as exc:
        logger.warning("Optional MusicDNA cross-product failed safely: %s", exc)
        return ()


class MusicDNAUnavailable(RuntimeError):
    """The optional private MusicDNA runtime is absent or failed to load.

    Raised instead of degrading silently so the theme picker can surface a
    visible error rather than presenting an empty catalog.
    """


def music_dna_unavailable_reason() -> Optional[str]:
    """Return why MusicDNA is unavailable, or None when it loads cleanly.

    The runtime is an optional private package, so absence is a legitimate
    deployment state -- but it must never be silent, or a broken install
    presents as an empty picker with no explanation.
    """
    try:
        module = import_module("design_dna.music_runtime")
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    if not hasattr(module, "list_music_architecture_options"):
        return (
            "design_dna.music_runtime does not expose "
            "list_music_architecture_options (incompatible package version)"
        )
    return None


def list_music_archetypes(*, include_all: bool = True) -> tuple[str, ...]:
    """Return the architecture ids that pair with MusicDNA references.

    Sourced from the private runtime so the picker stays in step with the
    package rather than a hardcoded list. Raises MusicDNAUnavailable when the
    runtime cannot be loaded, so callers can show the reason.
    """
    reason = music_dna_unavailable_reason()
    if reason is not None:
        raise MusicDNAUnavailable(f"MusicDNA runtime unavailable -- {reason}")
    module = import_module("design_dna.music_runtime")
    return tuple(
        str(item)
        for item in module.list_music_architecture_options(include_all=bool(include_all))
    )


def list_music_archetype_ids() -> tuple[str, ...]:
    """Return the distinct architecture ids, in stable order.

    The runtime exposes the full cross-product ("music:<track>@<archetype>");
    this reduces it to the unique architectures so the picker can keep its
    two-dropdown shape.
    """
    ids: list[str] = []
    for combination in list_music_archetypes():
        if "@" not in combination:
            continue
        archetype = combination.rsplit("@", 1)[1].strip()
        if archetype and archetype not in ids:
            ids.append(archetype)
    return tuple(ids)


def realize_music_theme(track_id: str, archetype_id: str) -> Optional[MusicArchitecturePlan]:
    module = _optional_import()
    if module is None:
        return None
    try:
        plan = module.realize_music_theme(str(track_id), str(archetype_id))
        if plan is None:
            return None
        return MusicArchitecturePlan(
            track_id=str(plan.track_id),
            display_name=str(plan.display_name),
            artist=str(plan.artist),
            reference_id=str(plan.reference_id),
            topology=str(plan.topology),
            tier=str(plan.tier),
            archetype_id=str(plan.archetype_id),
            combination_id=str(plan.combination_id),
            source_preview=str(plan.source_preview),
            signature=str(plan.signature),
            world=str(plan.world),
            layout_flow=str(plan.layout_flow),
            mobile_strategy=str(plan.mobile_strategy),
            density=str(plan.density),
            radius=str(plan.radius),
            primary_object=str(plan.primary_object),
            primary_action=str(plan.primary_action),
            composer_label=str(plan.composer_label),
            font_family=str(plan.font_family),
            mono_font=str(plan.mono_font),
            background=str(plan.background),
            surface=str(plan.surface),
            text=str(plan.text),
            primary=str(plan.primary),
            accent=str(plan.accent),
            border=str(plan.border),
            asset_url=str(plan.asset_url),
            asset_credit=str(plan.asset_credit),
        )
    except Exception as exc:
        logger.warning("Optional MusicDNA realization failed safely: %s", exc)
        return None


__all__ = [
    "MusicArchitecturePlan",
    "MusicDNAUnavailable",
    "MusicThemeOption",
    "list_music_architecture_combinations",
    "list_music_archetype_ids",
    "list_music_archetypes",
    "list_music_theme_options",
    "music_dna_available",
    "music_dna_unavailable_reason",
    "realize_music_theme",
]
