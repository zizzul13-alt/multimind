"""
MultiMind AI - Theme Studio Draft State Management
Manages isolated composition and Theme-level draft state, role selections, editing, reset/discard, and explicit apply.
"""
import copy
import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

import streamlit as st
from ui.themes.models import Theme, ThemeMetadata
from ui.themes import get_theme, resolve_theme, register_theme
from dna_quarantine.legacy_ui_dna import get_dna
from dna_quarantine.legacy_ui_dna.models import DesignComposition, ComposedProjection
from dna_quarantine.legacy_ui_dna.mapper import dna_to_theme
from dna_quarantine.legacy_ui_dna.resolver import resolve_composition

logger = logging.getLogger(__name__)

SESSION_DRAFT_KEY = "theme_studio_draft"


@dataclass
class ThemeStudioDraft:
    """Isolated Theme & Composition draft state representation for Theme Studio."""
    base_id: str
    base_type: str  # "theme" or "dna" or "composition"
    display_name: str
    identity_dna_id: str = "japan-print-ink"
    web_information_dna_id: Optional[str] = None
    archetype_id: str = "chat_first"
    colors: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, Any] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    radius: Dict[str, str] = field(default_factory=dict)
    description: str = ""

    def get_composition(self) -> DesignComposition:
        """Returns a DesignComposition instance for the current draft role selections."""
        comp = DesignComposition(
            identity_dna_id=self.identity_dna_id,
            web_information_dna_id=self.web_information_dna_id,
            archetype_id=self.archetype_id,
        )
        comp.validate()
        return comp

    def resolve(self) -> ComposedProjection:
        """Resolves the current draft composition into a ComposedProjection."""
        return resolve_composition(self.get_composition())

    def to_theme(self, custom_id: Optional[str] = None) -> Theme:
        """Converts the draft into a valid Theme contract instance."""
        theme_id = custom_id or f"custom-draft-{uuid.uuid4().hex[:8]}"
        disp_name = f"{self.display_name} (Custom)" if not self.display_name.endswith("(Custom)") else self.display_name

        # Construct Theme metadata tracking composition provenance
        web_info_str = f" + web:{self.web_information_dna_id}" if self.web_information_dna_id else ""
        meta = ThemeMetadata(
            description=f"User-customized Theme Studio draft derived from {self.base_type}:{self.base_id}{web_info_str}",
            author="Theme Studio",
            reference=f"{self.base_type}:{self.base_id}"
        )

        theme = Theme(
            id=theme_id,
            display_name=disp_name,
            category="custom",
            description=self.description or f"Customized theme based on {self.base_id}",
            metadata=meta,
            colors=copy.deepcopy(self.colors),
            typography=copy.deepcopy(self.typography),
            spacing=copy.deepcopy(self.spacing),
            radius=copy.deepcopy(self.radius)
        )
        theme.validate()
        return theme


def init_draft_from_composition(
    identity_dna_id: str = "rinpa-decorative-spatial",
    web_information_dna_id: Optional[str] = "japan-high-density-info",
    archetype_id: str = "chat_first"
) -> ThemeStudioDraft:
    """Initializes a ThemeStudioDraft from independent composition role selections."""
    comp = DesignComposition(
        identity_dna_id=identity_dna_id,
        web_information_dna_id=web_information_dna_id,
        archetype_id=archetype_id,
    )
    projection = resolve_composition(comp)
    base_theme = projection.theme

    # Resolve base values for token overrides
    _, resolved_groups = resolve_theme(base_theme.id)

    colors = copy.deepcopy(resolved_groups["colors"])
    if base_theme.colors:
        colors.update(base_theme.colors)

    typography = copy.deepcopy(resolved_groups["typography"])
    if base_theme.typography:
        if "font_family_base" in base_theme.typography:
            typography["font_family_base"] = base_theme.typography["font_family_base"]
        if "font_family_mono" in base_theme.typography:
            typography["font_family_mono"] = base_theme.typography["font_family_mono"]

    spacing = copy.deepcopy(resolved_groups["spacing"])
    if base_theme.spacing:
        spacing.update(base_theme.spacing)

    radius = copy.deepcopy(resolved_groups["radius"])
    if base_theme.radius:
        radius.update(base_theme.radius)

    identity_dna = get_dna(identity_dna_id)
    disp_name = identity_dna.display_name if identity_dna else base_theme.display_name

    return ThemeStudioDraft(
        base_id=identity_dna_id,
        base_type="composition",
        display_name=disp_name,
        identity_dna_id=identity_dna_id,
        web_information_dna_id=web_information_dna_id,
        archetype_id=archetype_id,
        description=f"Composition of identity:{identity_dna_id} + web:{web_information_dna_id} + arch:{archetype_id}",
        colors=colors,
        typography=typography,
        spacing=spacing,
        radius=radius
    )


def init_draft_from_base(base_id: str, base_type: str = "theme") -> ThemeStudioDraft:
    """Initializes a new ThemeStudioDraft from an existing Theme or DesignDNA base."""
    if base_type == "dna":
        dna = get_dna(base_id)
        if dna:
            base_theme = dna_to_theme(dna)
            resolved_theme, resolved_groups = resolve_theme(base_theme.id)

            colors = copy.deepcopy(resolved_groups["colors"])
            if base_theme.colors:
                colors.update(base_theme.colors)

            typography = copy.deepcopy(resolved_groups["typography"])
            if base_theme.typography:
                if "font_family_base" in base_theme.typography:
                    typography["font_family_base"] = base_theme.typography["font_family_base"]
                if "font_family_mono" in base_theme.typography:
                    typography["font_family_mono"] = base_theme.typography["font_family_mono"]

            spacing = copy.deepcopy(resolved_groups["spacing"])
            if base_theme.spacing:
                spacing.update(base_theme.spacing)

            radius = copy.deepcopy(resolved_groups["radius"])
            if base_theme.radius:
                radius.update(base_theme.radius)

            return ThemeStudioDraft(
                base_id=dna.id,
                base_type="dna",
                display_name=dna.display_name,
                identity_dna_id=dna.id if dna.role == "identity" else "japan-print-ink",
                web_information_dna_id=dna.id if dna.role == "web_information" else None,
                archetype_id="chat_first",
                description=dna.description or f"Derived from Design DNA: {dna.display_name}",
                colors=colors,
                typography=typography,
                spacing=spacing,
                radius=radius
            )

    # Default to theme base lookup
    base_theme = get_theme(base_id)
    if not base_theme:
        return init_draft_from_composition()

    _, resolved_groups = resolve_theme(base_theme.id)

    colors = copy.deepcopy(resolved_groups["colors"])
    typography = copy.deepcopy(resolved_groups["typography"])
    spacing = copy.deepcopy(resolved_groups["spacing"])
    radius = copy.deepcopy(resolved_groups["radius"])

    return ThemeStudioDraft(
        base_id=base_theme.id,
        base_type="theme",
        display_name=base_theme.display_name,
        identity_dna_id=base_theme.id if get_dna(base_theme.id) else "japan-print-ink",
        web_information_dna_id=None,
        archetype_id="chat_first",
        description=base_theme.description or f"Derived from Theme: {base_theme.display_name}",
        colors=colors,
        typography=typography,
        spacing=spacing,
        radius=radius
    )


def get_or_create_draft(default_base_id: str = "default") -> ThemeStudioDraft:
    """Gets the current ThemeStudioDraft from session state, or creates one if absent."""
    if SESSION_DRAFT_KEY not in st.session_state or not isinstance(st.session_state[SESSION_DRAFT_KEY], ThemeStudioDraft):
        if default_base_id == "default" or get_theme(default_base_id):
            st.session_state[SESSION_DRAFT_KEY] = init_draft_from_base(default_base_id, "theme")
        else:
            st.session_state[SESSION_DRAFT_KEY] = init_draft_from_composition(
                identity_dna_id="rinpa-decorative-spatial",
                web_information_dna_id="japan-high-density-info",
                archetype_id="chat_first"
            )
    return st.session_state[SESSION_DRAFT_KEY]


def reset_draft_to_base(base_id: str, base_type: str = "theme") -> ThemeStudioDraft:
    """Resets the current session draft to match a base Theme, DesignDNA, or composition."""
    if base_type == "composition":
        current_draft = st.session_state.get(SESSION_DRAFT_KEY)
        if isinstance(current_draft, ThemeStudioDraft):
            draft = init_draft_from_composition(
                identity_dna_id=current_draft.identity_dna_id,
                web_information_dna_id=current_draft.web_information_dna_id,
                archetype_id=current_draft.archetype_id,
            )
        else:
            draft = init_draft_from_composition(identity_dna_id=base_id)
    else:
        draft = init_draft_from_base(base_id, base_type)
    st.session_state[SESSION_DRAFT_KEY] = draft
    return draft


def apply_draft_to_active_theme(draft: ThemeStudioDraft) -> Theme:
    """Promotes draft composition atomically to session state as active theme, archetype, and composition.

    Generates a unique theme ID per applied draft instance to guarantee isolation and prevent collisions
    across concurrent sessions sharing the process-level ThemeRegistry singleton.
    """
    unique_theme_id = f"custom-{draft.base_id}-{uuid.uuid4().hex[:8]}"
    custom_theme = draft.to_theme(custom_id=unique_theme_id)

    # Register runtime theme into global process-level ThemeRegistry
    register_theme(custom_theme)

    # Track session ownership so custom theme is discoverable only by current session
    if "session_custom_themes" not in st.session_state:
        st.session_state.session_custom_themes = set()
    elif isinstance(st.session_state.session_custom_themes, (list, tuple)):
        st.session_state.session_custom_themes = set(st.session_state.session_custom_themes)
    st.session_state.session_custom_themes.add(custom_theme.id)

    # Promote draft composition atomically to active session application state
    st.session_state.active_theme = custom_theme.id
    st.session_state.active_archetype = draft.archetype_id
    st.session_state.active_composition = draft.get_composition()

    return custom_theme
