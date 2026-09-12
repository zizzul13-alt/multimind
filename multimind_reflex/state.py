"""RJ-3 Reflex state for production presentation parity.

Presentation state stays host-owned. Application/provider/persistence truth remains
behind MultiMindApplication and the shared composition root.
"""

from __future__ import annotations

import asyncio
import json
import re

import reflex as rx

from core.application import ChatRequest
from core.file_handler import FileHandler
from core.templates import TemplateManager
from multimind_reflex.bridge import BufferedUpload, build_host_application
from multimind_reflex.deliberation_projection import (
    critique_snapshots,
    history_snapshots,
    participant_snapshots,
    run_summary,
)
from ui.dna_bridge import (
    dna_available,
    ensure_dna_registered,
    list_theme_studio_dna_options,
    resolve_theme_studio_composition,
    theme_studio_available,
)
from utils.config import Config, InvalidUserIdError
from utils.token_counter import TokenCounter


ARCHETYPES = [
    "chat_first",
    "command_center",
    "ai_workspace",
    "ai_research_lab",
    "agent_canvas",
    "terminal_hacker",
    "minimal_saas",
]
AGENT_OPTIONS = ["gemini", "deepseek", "groq", "cloudflare", "openrouter", "huggingface"]
SKILL_OPTIONS = ["default", "coding", "research", "thinking"]
_TEMPLATE_MANAGER = TemplateManager()
TEMPLATE_OPTIONS = [""] + [item[0] for item in _TEMPLATE_MANAGER.get_template_names()]
_TEMPLATE_VARIABLE_RE = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")

_DEFAULT_IDENTITY_DNA = "rinpa-decorative-spatial"
_DEFAULT_WEB_DNA = "japan-high-density-info"
_NONE_WEB_CHOICE = "None (Default information density)"
_NEUTRAL_IDENTITY_CHOICE = "Neutral safe presentation"
_CHOICE_SEPARATOR = " · "
_NEUTRAL_COLORS = {
    "background": "#ffffff",
    "surface": "#ffffff",
    "text": "#1f2937",
    "primary": "#2563eb",
    "accent": "#0f766e",
    "border": "#d1d5db",
}
_RADIUS_PRESETS = {
    "none": "0px",
    "small": "4px",
    "medium": "8px",
    "large": "12px",
}
_SPACING_PRESETS = {
    "compact": "0.75rem",
    "comfortable": "1rem",
    "spacious": "1.25rem",
}


def _session_snapshots(rows):
    return [
        {
            "id": str(row.get("id", "")),
            "name": str(row.get("name", "Session")),
            "mode": str(row.get("mode", "coding")),
        }
        for row in rows
    ]


def _dna_choice(option) -> str:
    return f"{option.display_name}{_CHOICE_SEPARATOR}{option.id}"


def _choice_id(value: str) -> str:
    value = str(value or "").strip()
    if not value or value in {_NONE_WEB_CHOICE, _NEUTRAL_IDENTITY_CHOICE}:
        return ""
    if _CHOICE_SEPARATOR in value:
        return value.rsplit(_CHOICE_SEPARATOR, 1)[-1].strip()
    return value


def _choice_for_id(choices: list[str], unit_id: str, fallback: str) -> str:
    unit_id = str(unit_id or "").strip()
    for choice in choices:
        if _choice_id(choice) == unit_id:
            return choice
    return fallback


def _radius_preset(value: str) -> str:
    text = str(value or "").strip().lower()
    if text in {"0", "0px"}:
        return "none"
    match = re.match(r"^([0-9.]+)px$", text)
    if not match:
        return "medium"
    try:
        px = float(match.group(1))
    except ValueError:
        return "medium"
    if px <= 4:
        return "small"
    if px <= 10:
        return "medium"
    return "large"


def _density_preset(value: str, compact: bool = False) -> str:
    if compact:
        return "compact"
    text = str(value or "").strip().lower()
    match = re.match(r"^([0-9.]+)rem$", text)
    if not match:
        return "comfortable"
    try:
        rem = float(match.group(1))
    except ValueError:
        return "comfortable"
    if rem < 0.9:
        return "compact"
    if rem > 1.1:
        return "spacious"
    return "comfortable"


class HostState(rx.State):
    """Reflex presentation state projecting application-owned MultiMind truth."""

    # Identity / navigation.
    username: str = ""
    display_username: str = ""
    user_id: str = ""
    logged_in: bool = False
    current_surface: str = "theme"  # theme | workspace

    # Theme Studio presentation state. Draft never changes application truth.
    theme_studio_open: bool = True
    dna_runtime_available: bool = False
    private_theme_studio_available: bool = False
    identity_dna_choices: list[str] = [_NEUTRAL_IDENTITY_CHOICE]
    web_dna_choices: list[str] = [_NONE_WEB_CHOICE]
    draft_identity_choice: str = _NEUTRAL_IDENTITY_CHOICE
    draft_web_choice: str = _NONE_WEB_CHOICE
    draft_archetype: str = "chat_first"
    active_archetype: str = "chat_first"
    draft_identity_dna: str = ""
    draft_web_dna: str = ""
    draft_identity_display_name: str = "Neutral"
    draft_web_display_name: str = "None"
    draft_density: str = "comfortable"
    draft_radius: str = "medium"
    draft_background: str = _NEUTRAL_COLORS["background"]
    draft_surface: str = _NEUTRAL_COLORS["surface"]
    draft_text_color: str = _NEUTRAL_COLORS["text"]
    draft_primary: str = _NEUTRAL_COLORS["primary"]
    draft_accent: str = _NEUTRAL_COLORS["accent"]
    draft_border: str = _NEUTRAL_COLORS["border"]
    draft_font_family: str = "system-ui, -apple-system, sans-serif"
    draft_mono_font: str = "monospace"
    draft_radius_value: str = _RADIUS_PRESETS["medium"]
    draft_spacing_value: str = _SPACING_PRESETS["comfortable"]
    draft_metadata_prominence: str = "standard"
    draft_status_richness: str = "standard"
    draft_navigation_density: str = "standard"
    draft_secondary_compactness: bool = False
    draft_information_discoverability: str = "standard"
    draft_utility_grouping: str = "standard"
    draft_hierarchy_contrast: str = "strong"
    draft_border_style: str = "solid"
    draft_energy_emphasis: str = "balanced"
    draft_surface_treatment: str = "flat"
    draft_transition_speed: str = "deliberate"

    active_identity_dna: str = ""
    active_web_dna: str = ""
    active_identity_display_name: str = "Neutral"
    active_web_display_name: str = "None"
    active_density: str = "comfortable"
    active_radius: str = "medium"
    active_background: str = _NEUTRAL_COLORS["background"]
    active_surface: str = _NEUTRAL_COLORS["surface"]
    active_text_color: str = _NEUTRAL_COLORS["text"]
    active_primary: str = _NEUTRAL_COLORS["primary"]
    active_accent: str = _NEUTRAL_COLORS["accent"]
    active_border: str = _NEUTRAL_COLORS["border"]
    active_font_family: str = "system-ui, -apple-system, sans-serif"
    active_mono_font: str = "monospace"
    active_radius_value: str = _RADIUS_PRESETS["medium"]
    active_spacing_value: str = _SPACING_PRESETS["comfortable"]
    active_metadata_prominence: str = "standard"
    active_status_richness: str = "standard"
    active_navigation_density: str = "standard"
    active_secondary_compactness: bool = False
    active_information_discoverability: str = "standard"
    active_utility_grouping: str = "standard"
    active_hierarchy_contrast: str = "strong"
    active_border_style: str = "solid"
    active_energy_emphasis: str = "balanced"
    active_surface_treatment: str = "flat"
    active_transition_speed: str = "deliberate"
    theme_status: str = "Safe neutral presentation"

    # Session lifecycle.
    sessions: list[dict[str, str]] = []
    new_session_name: str = ""
    new_session_mode: str = "coding"
    current_session_id: str = ""
    current_session_name: str = ""
    current_session_mode: str = "coding"
    history: list[dict[str, str]] = []

    # Composer / template / execution controls.
    prompt: str = ""
    selected_template: str = ""
    template_description: str = ""
    template_variables: list[str] = []
    template_variables_json: str = "{}"
    template_preview: str = ""
    context_mode: str = "continue"
    compressor_enabled: bool = Config.COMPRESSOR_ENABLED
    active_agents: list[str] = list(Config.DEFAULT_AGENTS)
    debate_rounds: int = Config.DEBATE_ROUNDS_DEFAULT
    selected_skill: str = "default"

    # Pre-send usage feedback.
    estimated_prompt_tokens: int = 0
    estimated_file_tokens: int = 0
    estimated_total_tokens: int = 0
    estimated_provider_calls: int = 0
    estimated_cost: float = 0.0
    token_warning_level: str = "low"

    # Execution/result state.
    busy: bool = False
    status_message: str = ""
    error_message: str = ""
    success_message: str = ""
    final_answer: str = ""
    warnings: list[str] = []
    upload_names: list[str] = []
    restore_name: str = ""

    # Read-only projection of application-owned deliberation truth.
    current_participants: list[dict[str, str]] = []
    current_critiques: list[dict[str, str]] = []
    current_system_verdict: str = ""
    current_judge_provider: str = ""
    current_judge_status: str = ""

    _runtime_memories: dict = {}
    _pending_uploads: list[dict] = []
    _pending_restore: bytes = b""

    def _application(self):
        if not self.user_id:
            raise RuntimeError("A validated user identity is required.")
        return build_host_application(self.user_id, self._runtime_memories)

    def _refresh_sessions(self):
        self.sessions = _session_snapshots(self._application().list_sessions())

    def _refresh_history(self):
        if not self.current_session_id:
            self.history = []
            return
        self.history = history_snapshots(
            self._application().get_session_chats(self.current_session_id, limit=50)
        )

    def _refresh_estimate(self):
        estimate = TokenCounter.estimate_total(
            self.prompt or "",
            files_count=len(self._pending_uploads),
            mode=self.current_session_mode or self.new_session_mode,
            rounds=self.debate_rounds,
            compressor_on=self.compressor_enabled,
            participants=max(1, len(self.active_agents)),
        )
        self.estimated_prompt_tokens = int(estimate["prompt_tokens"])
        self.estimated_file_tokens = int(estimate["file_tokens"])
        self.estimated_total_tokens = int(estimate["total_estimate"])
        self.estimated_provider_calls = int(estimate["provider_calls_estimate"])
        self.estimated_cost = float(TokenCounter.estimate_cost(self.estimated_total_tokens))
        self.token_warning_level = TokenCounter.get_warning_level(self.estimated_total_tokens)["level"]

    def _clear_deliberation_projection(self):
        self.current_participants = []
        self.current_critiques = []
        self.current_system_verdict = ""
        self.current_judge_provider = ""
        self.current_judge_status = ""

    def _set_deliberation_projection(self, debate_data):
        self.current_participants = participant_snapshots(debate_data)
        self.current_critiques = critique_snapshots(debate_data)
        summary = run_summary(debate_data)
        self.current_system_verdict = summary["system_verdict"]
        self.current_judge_provider = summary["judge_provider"]
        self.current_judge_status = summary["judge_status"]

    def _set_neutral_theme_draft(self):
        self.draft_identity_dna = ""
        self.draft_web_dna = ""
        self.draft_identity_display_name = "Neutral"
        self.draft_web_display_name = "None"
        self.draft_identity_choice = _NEUTRAL_IDENTITY_CHOICE
        self.draft_web_choice = _NONE_WEB_CHOICE
        self.draft_archetype = "chat_first"
        self.draft_density = "comfortable"
        self.draft_radius = "medium"
        self.draft_background = _NEUTRAL_COLORS["background"]
        self.draft_surface = _NEUTRAL_COLORS["surface"]
        self.draft_text_color = _NEUTRAL_COLORS["text"]
        self.draft_primary = _NEUTRAL_COLORS["primary"]
        self.draft_accent = _NEUTRAL_COLORS["accent"]
        self.draft_border = _NEUTRAL_COLORS["border"]
        self.draft_font_family = "system-ui, -apple-system, sans-serif"
        self.draft_mono_font = "monospace"
        self.draft_radius_value = _RADIUS_PRESETS["medium"]
        self.draft_spacing_value = _SPACING_PRESETS["comfortable"]
        self.draft_metadata_prominence = "standard"
        self.draft_status_richness = "standard"
        self.draft_navigation_density = "standard"
        self.draft_secondary_compactness = False
        self.draft_information_discoverability = "standard"
        self.draft_utility_grouping = "standard"
        self.draft_hierarchy_contrast = "strong"
        self.draft_border_style = "solid"
        self.draft_energy_emphasis = "balanced"
        self.draft_surface_treatment = "flat"
        self.draft_transition_speed = "deliberate"

    def _copy_draft_to_active(self):
        self.active_archetype = self.draft_archetype
        self.active_identity_dna = self.draft_identity_dna
        self.active_web_dna = self.draft_web_dna
        self.active_identity_display_name = self.draft_identity_display_name
        self.active_web_display_name = self.draft_web_display_name
        self.active_density = self.draft_density
        self.active_radius = self.draft_radius
        self.active_background = self.draft_background
        self.active_surface = self.draft_surface
        self.active_text_color = self.draft_text_color
        self.active_primary = self.draft_primary
        self.active_accent = self.draft_accent
        self.active_border = self.draft_border
        self.active_font_family = self.draft_font_family
        self.active_mono_font = self.draft_mono_font
        self.active_radius_value = self.draft_radius_value
        self.active_spacing_value = self.draft_spacing_value
        self.active_metadata_prominence = self.draft_metadata_prominence
        self.active_status_richness = self.draft_status_richness
        self.active_navigation_density = self.draft_navigation_density
        self.active_secondary_compactness = self.draft_secondary_compactness
        self.active_information_discoverability = self.draft_information_discoverability
        self.active_utility_grouping = self.draft_utility_grouping
        self.active_hierarchy_contrast = self.draft_hierarchy_contrast
        self.active_border_style = self.draft_border_style
        self.active_energy_emphasis = self.draft_energy_emphasis
        self.active_surface_treatment = self.draft_surface_treatment
        self.active_transition_speed = self.draft_transition_speed

    def _copy_active_to_draft(self):
        self.draft_archetype = self.active_archetype
        self.draft_identity_dna = self.active_identity_dna
        self.draft_web_dna = self.active_web_dna
        self.draft_identity_display_name = self.active_identity_display_name
        self.draft_web_display_name = self.active_web_display_name
        self.draft_identity_choice = _choice_for_id(
            self.identity_dna_choices,
            self.active_identity_dna,
            _NEUTRAL_IDENTITY_CHOICE,
        )
        self.draft_web_choice = _choice_for_id(
            self.web_dna_choices,
            self.active_web_dna,
            _NONE_WEB_CHOICE,
        )
        self.draft_density = self.active_density
        self.draft_radius = self.active_radius
        self.draft_background = self.active_background
        self.draft_surface = self.active_surface
        self.draft_text_color = self.active_text_color
        self.draft_primary = self.active_primary
        self.draft_accent = self.active_accent
        self.draft_border = self.active_border
        self.draft_font_family = self.active_font_family
        self.draft_mono_font = self.active_mono_font
        self.draft_radius_value = self.active_radius_value
        self.draft_spacing_value = self.active_spacing_value
        self.draft_metadata_prominence = self.active_metadata_prominence
        self.draft_status_richness = self.active_status_richness
        self.draft_navigation_density = self.active_navigation_density
        self.draft_secondary_compactness = self.active_secondary_compactness
        self.draft_information_discoverability = self.active_information_discoverability
        self.draft_utility_grouping = self.active_utility_grouping
        self.draft_hierarchy_contrast = self.active_hierarchy_contrast
        self.draft_border_style = self.active_border_style
        self.draft_energy_emphasis = self.active_energy_emphasis
        self.draft_surface_treatment = self.active_surface_treatment
        self.draft_transition_speed = self.active_transition_speed

    def _refresh_theme_draft_from_composition(self) -> bool:
        if not self.draft_identity_dna:
            self._set_neutral_theme_draft()
            return False
        projection = resolve_theme_studio_composition(
            self.draft_identity_dna,
            self.draft_web_dna or None,
            self.draft_archetype,
        )
        if projection is None:
            self._set_neutral_theme_draft()
            self.theme_status = "Private Design-DNA available; composition fallback active"
            return False

        self.draft_identity_dna = projection.identity_dna_id
        self.draft_web_dna = projection.web_information_dna_id or ""
        self.draft_archetype = projection.archetype_id
        self.draft_identity_display_name = projection.identity_display_name
        self.draft_web_display_name = projection.web_information_display_name or "None"
        self.draft_identity_choice = _choice_for_id(
            self.identity_dna_choices,
            self.draft_identity_dna,
            self.draft_identity_dna,
        )
        self.draft_web_choice = _choice_for_id(
            self.web_dna_choices,
            self.draft_web_dna,
            _NONE_WEB_CHOICE,
        )

        colors = projection.colors
        self.draft_background = colors.get("background", _NEUTRAL_COLORS["background"])
        self.draft_surface = colors.get("surface", _NEUTRAL_COLORS["surface"])
        self.draft_text_color = colors.get("text", _NEUTRAL_COLORS["text"])
        self.draft_primary = colors.get("primary", _NEUTRAL_COLORS["primary"])
        self.draft_accent = colors.get("accent", _NEUTRAL_COLORS["accent"])
        self.draft_border = colors.get("border", _NEUTRAL_COLORS["border"])
        self.draft_font_family = str(
            projection.typography.get("font_family_base")
            or "system-ui, -apple-system, sans-serif"
        )
        self.draft_mono_font = str(projection.typography.get("font_family_mono") or "monospace")
        self.draft_radius_value = projection.radius.get("md", _RADIUS_PRESETS["medium"])
        self.draft_spacing_value = projection.spacing.get("md", _SPACING_PRESETS["comfortable"])

        policy = projection.presentation_policy
        self.draft_metadata_prominence = str(policy.get("metadata_prominence", "standard"))
        self.draft_status_richness = str(policy.get("status_richness", "standard"))
        self.draft_navigation_density = str(policy.get("navigation_density", "standard"))
        self.draft_secondary_compactness = bool(policy.get("secondary_compactness", False))
        self.draft_information_discoverability = str(policy.get("information_discoverability", "standard"))
        self.draft_utility_grouping = str(policy.get("utility_grouping", "standard"))

        identity = projection.identity_projection
        self.draft_hierarchy_contrast = str(identity.get("hierarchy_contrast", "strong"))
        self.draft_border_style = str(identity.get("border_stroke_style", "solid"))
        self.draft_energy_emphasis = str(identity.get("energy_emphasis", "balanced"))
        self.draft_surface_treatment = str(identity.get("surface_treatment", "flat"))
        self.draft_transition_speed = str(identity.get("transition_speed", "deliberate"))

        self.draft_radius = _radius_preset(self.draft_radius_value)
        self.draft_density = _density_preset(
            self.draft_spacing_value,
            compact=self.draft_secondary_compactness,
        )
        self.theme_status = "Private Design-DNA available"
        return True

    def _load_theme_studio_catalog(self):
        if not self.dna_runtime_available or not ensure_dna_registered():
            self.identity_dna_choices = [_NEUTRAL_IDENTITY_CHOICE]
            self.web_dna_choices = [_NONE_WEB_CHOICE]
            self._set_neutral_theme_draft()
            self._copy_draft_to_active()
            self.theme_status = "Safe neutral presentation"
            return

        identity_options = list_theme_studio_dna_options("identity")
        web_options = list_theme_studio_dna_options("web_information")
        self.identity_dna_choices = [_dna_choice(option) for option in identity_options]
        self.web_dna_choices = [_NONE_WEB_CHOICE] + [_dna_choice(option) for option in web_options]
        if not identity_options:
            self.identity_dna_choices = [_NEUTRAL_IDENTITY_CHOICE]
            self._set_neutral_theme_draft()
            self._copy_draft_to_active()
            self.theme_status = "Private Design-DNA available; compatible Theme Studio catalog is empty"
            return

        identity_ids = [option.id for option in identity_options]
        web_ids = [option.id for option in web_options]
        self.draft_identity_dna = (
            _DEFAULT_IDENTITY_DNA if _DEFAULT_IDENTITY_DNA in identity_ids else identity_ids[0]
        )
        self.draft_web_dna = _DEFAULT_WEB_DNA if _DEFAULT_WEB_DNA in web_ids else ""
        self.draft_archetype = "chat_first"
        self.draft_identity_choice = _choice_for_id(
            self.identity_dna_choices,
            self.draft_identity_dna,
            self.identity_dna_choices[0],
        )
        self.draft_web_choice = _choice_for_id(
            self.web_dna_choices,
            self.draft_web_dna,
            _NONE_WEB_CHOICE,
        )
        if not self._refresh_theme_draft_from_composition():
            self._copy_draft_to_active()
            return
        # The initial active presentation is the resolved safe starting base.
        # Later draft edits remain isolated until explicit Apply.
        self._copy_draft_to_active()

    @rx.event
    def set_username(self, value: str):
        self.username = value

    @rx.event
    def set_new_session_name(self, value: str):
        self.new_session_name = value

    @rx.event
    def set_new_session_mode(self, value: str):
        self.new_session_mode = value
        self._refresh_estimate()

    @rx.event
    def set_prompt(self, value: str):
        self.prompt = value
        self._refresh_estimate()

    @rx.event
    def set_context_mode(self, value: str):
        self.context_mode = value

    @rx.event
    def set_compressor_enabled(self, value: bool):
        self.compressor_enabled = bool(value)
        self._refresh_estimate()

    @rx.event
    def set_debate_rounds(self, value: str):
        try:
            self.debate_rounds = max(1, min(5, int(value)))
        except (TypeError, ValueError):
            self.debate_rounds = Config.DEBATE_ROUNDS_DEFAULT
        self._refresh_estimate()

    @rx.event
    def set_selected_skill(self, value: str):
        self.selected_skill = value or "default"

    @rx.event
    def set_agent_enabled(self, agent: str, enabled: bool):
        if agent not in AGENT_OPTIONS:
            return
        selected = list(self.active_agents)
        if enabled and agent not in selected:
            selected.append(agent)
        elif not enabled and agent in selected:
            selected.remove(agent)
        self.active_agents = selected or ["gemini"]
        self._refresh_estimate()

    @rx.event
    def login(self):
        self.error_message = ""
        self.success_message = ""
        try:
            display_username, user_id = Config.resolve_supplied_identity(self.username)
        except InvalidUserIdError as exc:
            self.error_message = str(exc)
            return

        self.display_username = display_username
        self.user_id = user_id
        self.logged_in = True
        self.current_surface = "theme"
        self.theme_studio_open = True
        self.dna_runtime_available = dna_available()
        self.private_theme_studio_available = theme_studio_available()
        self._load_theme_studio_catalog()
        self.current_session_id = ""
        self.current_session_name = ""
        self.current_session_mode = "coding"
        self.history = []
        self.final_answer = ""
        self._clear_deliberation_projection()
        self.warnings = []
        self._runtime_memories = {}
        self._pending_uploads = []
        self.upload_names = []
        self._refresh_sessions()
        self._refresh_estimate()

    @rx.event
    def logout(self):
        if self.busy:
            self.error_message = "A run is still active."
            return
        self.username = ""
        self.display_username = ""
        self.user_id = ""
        self.logged_in = False
        self.current_surface = "theme"
        self.sessions = []
        self.current_session_id = ""
        self.current_session_name = ""
        self.current_session_mode = "coding"
        self.history = []
        self.prompt = ""
        self.status_message = ""
        self.error_message = ""
        self.success_message = ""
        self.final_answer = ""
        self._clear_deliberation_projection()
        self.warnings = []
        self.upload_names = []
        self._runtime_memories = {}
        self._pending_uploads = []
        self._pending_restore = b""
        self.identity_dna_choices = [_NEUTRAL_IDENTITY_CHOICE]
        self.web_dna_choices = [_NONE_WEB_CHOICE]
        self._set_neutral_theme_draft()
        self._copy_draft_to_active()

    # Theme Studio draft/apply/discard/reset/handoff.
    @rx.event
    def set_draft_archetype(self, value: str):
        if value in ARCHETYPES:
            previous = self.draft_archetype
            self.draft_archetype = value
            if self.draft_identity_dna and not self._refresh_theme_draft_from_composition():
                self.draft_archetype = previous

    @rx.event
    def set_draft_identity_choice(self, value: str):
        unit_id = _choice_id(value)
        available = {_choice_id(choice) for choice in self.identity_dna_choices}
        if not unit_id or unit_id not in available:
            return
        self.draft_identity_choice = value
        self.draft_identity_dna = unit_id
        self._refresh_theme_draft_from_composition()

    @rx.event
    def set_draft_web_choice(self, value: str):
        unit_id = _choice_id(value)
        available = {_choice_id(choice) for choice in self.web_dna_choices}
        if unit_id and unit_id not in available:
            return
        self.draft_web_choice = value or _NONE_WEB_CHOICE
        self.draft_web_dna = unit_id
        self._refresh_theme_draft_from_composition()

    @rx.event
    def set_draft_identity_dna(self, value: str):
        """Compatibility event: accept only a catalog-backed identity ID."""
        choice = _choice_for_id(self.identity_dna_choices, value, "")
        if choice:
            self.set_draft_identity_choice(choice)

    @rx.event
    def set_draft_web_dna(self, value: str):
        """Compatibility event: accept only a catalog-backed Web/Information ID."""
        if not value:
            self.set_draft_web_choice(_NONE_WEB_CHOICE)
            return
        choice = _choice_for_id(self.web_dna_choices, value, "")
        if choice:
            self.set_draft_web_choice(choice)

    @rx.event
    def set_draft_density(self, value: str):
        if value in _SPACING_PRESETS:
            self.draft_density = value
            self.draft_spacing_value = _SPACING_PRESETS[value]

    @rx.event
    def set_draft_radius(self, value: str):
        if value in _RADIUS_PRESETS:
            self.draft_radius = value
            self.draft_radius_value = _RADIUS_PRESETS[value]

    @rx.event
    def set_draft_background(self, value: str):
        self.draft_background = value

    @rx.event
    def set_draft_surface(self, value: str):
        self.draft_surface = value

    @rx.event
    def set_draft_text_color(self, value: str):
        self.draft_text_color = value

    @rx.event
    def set_draft_primary(self, value: str):
        self.draft_primary = value

    @rx.event
    def set_draft_accent(self, value: str):
        self.draft_accent = value

    @rx.event
    def set_draft_border(self, value: str):
        self.draft_border = value

    @rx.event
    def set_draft_font_family(self, value: str):
        self.draft_font_family = value

    @rx.event
    def set_draft_mono_font(self, value: str):
        self.draft_mono_font = value

    @rx.event
    def apply_theme(self):
        self._copy_draft_to_active()
        self.theme_studio_open = False
        self.current_surface = "workspace"
        self.success_message = "Theme composition applied."

    @rx.event
    def discard_theme(self):
        self._copy_active_to_draft()
        self.success_message = "Draft discarded."

    @rx.event
    def reset_theme(self):
        identity_ids = {_choice_id(choice) for choice in self.identity_dna_choices}
        web_ids = {_choice_id(choice) for choice in self.web_dna_choices}
        if _DEFAULT_IDENTITY_DNA in identity_ids:
            self.draft_identity_dna = _DEFAULT_IDENTITY_DNA
        else:
            candidates = [item for item in identity_ids if item]
            if not candidates:
                self._set_neutral_theme_draft()
                self.success_message = "Draft reset to safe defaults."
                return
            self.draft_identity_dna = sorted(candidates)[0]
        self.draft_web_dna = _DEFAULT_WEB_DNA if _DEFAULT_WEB_DNA in web_ids else ""
        self.draft_archetype = "chat_first"
        self.draft_identity_choice = _choice_for_id(
            self.identity_dna_choices,
            self.draft_identity_dna,
            _NEUTRAL_IDENTITY_CHOICE,
        )
        self.draft_web_choice = _choice_for_id(
            self.web_dna_choices,
            self.draft_web_dna,
            _NONE_WEB_CHOICE,
        )
        self._refresh_theme_draft_from_composition()
        self.success_message = "Draft reset to resolved defaults."

    @rx.event
    def open_theme_studio(self):
        if self.busy:
            self.error_message = "Finish the active run before changing presentation."
            return
        self.theme_studio_open = True
        self.current_surface = "theme"

    @rx.event
    def return_to_workspace(self):
        self.theme_studio_open = False
        self.current_surface = "workspace"

    # Templates.
    @rx.event
    def select_template(self, template_id: str):
        self.selected_template = template_id
        template = _TEMPLATE_MANAGER.get_template(template_id) if template_id else None
        if not template:
            self.template_description = ""
            self.template_variables = []
            self.template_preview = ""
            return
        self.template_description = str(template.get("description", ""))
        self.template_variables = list(dict.fromkeys(_TEMPLATE_VARIABLE_RE.findall(template.get("prompt", ""))))
        self.template_variables_json = "{}"
        self.template_preview = str(template.get("prompt", ""))

    @rx.event
    def set_template_variables_json(self, value: str):
        self.template_variables_json = value
        if not self.selected_template:
            return
        try:
            variables = json.loads(value or "{}")
            if not isinstance(variables, dict):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            self.template_preview = "Invalid JSON variables."
            return
        applied = _TEMPLATE_MANAGER.apply_template(self.selected_template, variables) or {}
        self.template_preview = str(applied.get("prompt", ""))

    @rx.event
    def use_template_preview(self):
        if self.template_preview and self.template_preview != "Invalid JSON variables.":
            self.prompt = self.template_preview
            self._refresh_estimate()

    # Sessions.
    @rx.event
    def create_session(self):
        if not self.logged_in:
            self.error_message = "Login required."
            return
        name = self.new_session_name.strip()
        if not name:
            self.error_message = "Session name is required."
            return

        application = self._application()
        session_id = application.create_session(name, self.new_session_mode)
        self._refresh_sessions()
        session = next((item for item in self.sessions if item["id"] == session_id), None)
        if session is not None:
            application.select_session(session)
            self.current_session_id = session["id"]
            self.current_session_name = session.get("name", name)
            self.current_session_mode = session.get("mode", self.new_session_mode)
        self.new_session_name = ""
        self.error_message = ""
        self.success_message = "Session created."
        self._clear_deliberation_projection()
        self._refresh_history()
        self._refresh_estimate()

    @rx.event
    def select_session(self, session_id: str):
        if self.busy:
            self.error_message = "Finish the active run before switching sessions."
            return
        session = next((item for item in self.sessions if item["id"] == session_id), None)
        if session is None:
            self.error_message = "Session not found."
            return

        self._application().select_session(session)
        self.current_session_id = session["id"]
        self.current_session_name = session.get("name", "Session")
        self.current_session_mode = session.get("mode", "coding")
        self.error_message = ""
        self.success_message = ""
        self.final_answer = ""
        self._clear_deliberation_projection()
        self.warnings = []
        self._refresh_history()
        self._refresh_estimate()

    # Uploads and restore staging must consume UploadFile outside background work.
    @rx.event
    async def stage_uploads(self, files: list[rx.UploadFile]):
        staged = []
        warnings = []
        for upload in files[: FileHandler.MAX_FILES]:
            name = upload.filename or "upload"
            declared_size = getattr(upload, "size", None)
            if declared_size is not None and declared_size > FileHandler.MAX_SIZE:
                warnings.append(f"{name}: file too large (max 10MB)")
                continue
            data = await upload.read()
            if len(data) > FileHandler.MAX_SIZE:
                warnings.append(f"{name}: file too large (max 10MB)")
                continue
            staged.append({"name": name, "data": data})

        self._pending_uploads = staged
        self.upload_names = [item["name"] for item in staged]
        self.warnings = warnings
        self._refresh_estimate()

    @rx.event
    def clear_uploads(self):
        if self.busy:
            return
        self._pending_uploads = []
        self.upload_names = []
        self._refresh_estimate()

    @rx.event
    async def stage_restore(self, files: list[rx.UploadFile]):
        self._pending_restore = b""
        self.restore_name = ""
        if not files:
            return
        upload = files[0]
        self.restore_name = upload.filename or "backup.db"
        self._pending_restore = await upload.read()

    @rx.event
    def restore_database(self):
        if self.busy:
            self.error_message = "Finish the active run before restore."
            return
        if not self._pending_restore:
            self.error_message = "Stage a backup first."
            return
        result = self._application().restore_database(self._pending_restore)
        self.error_message = ""
        if result.status == "success":
            self.current_session_id = ""
            self.current_session_name = ""
            self.history = []
            self.final_answer = ""
            self._clear_deliberation_projection()
            self._runtime_memories = {}
            self._refresh_sessions()
            self.success_message = "Database restored safely."
        elif result.status == "invalid_backup":
            self.error_message = "Backup is invalid."
        else:
            self.error_message = "Restore operation failed."
        self._pending_restore = b""
        self.restore_name = ""

    @rx.event
    def export_database(self):
        if not self.logged_in:
            return
        return rx.download(
            data=self._application().export_database(),
            filename=f"multimind-{self.user_id}.db",
        )

    @rx.event(background=True)
    async def run_chat(self):
        """Execute the real app while preserving persistent busy/duplicate-run safety."""
        async with self:
            if self.busy:
                return
            if not self.logged_in:
                self.error_message = "Login required."
                return
            if not self.current_session_id:
                self.error_message = "Select or create a session first."
                return
            prompt = self.prompt.strip()
            if not prompt and not self._pending_uploads:
                self.error_message = "Enter a prompt or stage at least one file."
                return
            if not self.active_agents:
                self.error_message = "Select at least one agent."
                return

            self.busy = True
            self.status_message = "Running…"
            self.error_message = ""
            self.success_message = ""
            self.final_answer = ""
            self._clear_deliberation_projection()
            self.warnings = []

            user_id = self.user_id
            session_id = self.current_session_id
            session_mode = self.current_session_mode
            runtime_memories = self._runtime_memories
            staged_uploads = [dict(item) for item in self._pending_uploads]
            request = ChatRequest(
                original_prompt=prompt,
                uploads=[BufferedUpload(item["name"], item["data"]) for item in staged_uploads],
                context_mode=self.context_mode,
                session_id=session_id,
                session_mode=session_mode,
                compressor_enabled=self.compressor_enabled,
                active_agents=list(self.active_agents),
                debate_rounds=self.debate_rounds,
                selected_skill=self.selected_skill,
            )

        try:
            application = build_host_application(user_id, runtime_memories)
            result = await asyncio.to_thread(application.execute_chat, request)
            history = await asyncio.to_thread(application.get_session_chats, session_id, 50)
        except Exception:
            result = None
            history = None

        async with self:
            self.busy = False
            self.status_message = ""
            if result is None:
                self.error_message = "Chat execution failed. Please try again."
                return

            self.warnings = list(result.warnings)
            self._set_deliberation_projection(result.debate_data)
            if result.status != "success":
                self.error_message = "No usable provider response was returned."
                return

            self.final_answer = result.final_answer
            self.history = history_snapshots(history or [])
            self.prompt = ""
            self._pending_uploads = []
            self.upload_names = []
            self.success_message = "Response saved to session history."
            self._refresh_estimate()
