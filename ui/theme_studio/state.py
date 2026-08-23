"""
MultiMind AI - Theme Studio Draft State Management
Manages isolated Theme-level draft state, base selection, editing, reset/discard, and explicit apply.
"""
import copy
import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

import streamlit as st
from ui.themes.models import Theme, ThemeMetadata
from ui.themes import get_theme, resolve_theme, register_theme
from ui.dna import get_dna
from ui.dna.mapper import dna_to_theme

logger = logging.getLogger(__name__)

SESSION_DRAFT_KEY = "theme_studio_draft"


@dataclass
class ThemeStudioDraft:
    """Isolated Theme-level draft state representation for Theme Studio."""
    base_id: str
    base_type: str  # "theme" or "dna"
    display_name: str
    colors: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, Any] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    radius: Dict[str, str] = field(default_factory=dict)
    description: str = ""

    def to_theme(self, custom_id: Optional[str] = None) -> Theme:
        """Converts the draft into a valid Theme contract instance."""
        theme_id = custom_id or f"custom-draft-{uuid.uuid4().hex[:8]}"
        disp_name = f"{self.display_name} (Custom)" if not self.display_name.endswith("(Custom)") else self.display_name

        # Construct Theme metadata tracking base provenance
        meta = ThemeMetadata(
            description=f"User-customized Theme Studio draft derived from {self.base_type}:{self.base_id}",
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


def init_draft_from_base(base_id: str, base_type: str = "theme") -> ThemeStudioDraft:
    """Initializes a new ThemeStudioDraft from an existing Theme or DesignDNA base."""
    if base_type == "dna":
        dna = get_dna(base_id)
        if dna:
            base_theme = dna_to_theme(dna)
            resolved_theme, resolved_groups = resolve_theme(base_theme.id)
            # Combine resolved base values with mapped DNA overrides
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
                description=dna.description or f"Derived from Design DNA: {dna.display_name}",
                colors=colors,
                typography=typography,
                spacing=spacing,
                radius=radius
            )

    # Default to theme base lookup
    base_theme = get_theme(base_id)
    _, resolved_groups = resolve_theme(base_theme.id)

    colors = copy.deepcopy(resolved_groups["colors"])
    typography = copy.deepcopy(resolved_groups["typography"])
    spacing = copy.deepcopy(resolved_groups["spacing"])
    radius = copy.deepcopy(resolved_groups["radius"])

    return ThemeStudioDraft(
        base_id=base_theme.id,
        base_type="theme",
        display_name=base_theme.display_name,
        description=base_theme.description or f"Derived from Theme: {base_theme.display_name}",
        colors=colors,
        typography=typography,
        spacing=spacing,
        radius=radius
    )


def get_or_create_draft(default_base_id: str = "default") -> ThemeStudioDraft:
    """Gets the current ThemeStudioDraft from session state, or creates one if absent."""
    if SESSION_DRAFT_KEY not in st.session_state or not isinstance(st.session_state[SESSION_DRAFT_KEY], ThemeStudioDraft):
        st.session_state[SESSION_DRAFT_KEY] = init_draft_from_base(default_base_id, "theme")
    return st.session_state[SESSION_DRAFT_KEY]


def reset_draft_to_base(base_id: str, base_type: str = "theme") -> ThemeStudioDraft:
    """Resets the current session draft to match a base Theme or DesignDNA."""
    draft = init_draft_from_base(base_id, base_type)
    st.session_state[SESSION_DRAFT_KEY] = draft
    return draft


def apply_draft_to_active_theme(draft: ThemeStudioDraft) -> Theme:
    """Promotes draft to ThemeRegistry as a runtime theme and sets active_theme for the current session.

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

    # Set as active application theme for this session
    st.session_state.active_theme = custom_theme.id
    return custom_theme
