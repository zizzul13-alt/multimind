"""Identity-bound Streamlit runtime state management."""

from copy import deepcopy


# These keys can contain identity, conversation content, uploaded material, or
# user-specific operating choices. They must not cross an identity transition.
IDENTITY_BOUND_DEFAULTS = {
    "user": None,
    "user_id": None,
    "current_session": None,
    "sessions": {},
    "memories": {},
    "new_chat": False,
    "chat_mode": "continue",
    "compressor_enabled": False,
    "debate_rounds": 1,
    "active_agents": ["gemini"],
    "selected_skill": "default",
    "selected_template": None,
    "template_variables": {},
    "prompt_text": "",
    "prompt_main": "",
    "last_generated": "",
}

IDENTITY_BOUND_WIDGET_KEYS = {
    "login_username_input",
    "sidebar_new_session_name",
    "sidebar_new_session_mode",
    "settings_compressor",
    "settings_rounds",
    "settings_skill",
    "settings_agents",
    "chat_mode_radio",
    "template_selector",
    "new_chat_files",
}

IDENTITY_BOUND_KEY_PREFIXES = ("var_",)


def initialize_identity_state(state):
    """Set missing identity-bound state to safe defaults."""
    for key, value in IDENTITY_BOUND_DEFAULTS.items():
        if key not in state:
            state[key] = deepcopy(value)


def reset_identity_bound_state(state):
    """Remove all identity-bound data and recreate only safe empty defaults.

    Presentation-only state is intentionally not enumerated here, so theme,
    navigation, archetype, and Theme Studio presentation choices survive.
    """
    keys_to_remove = set(IDENTITY_BOUND_DEFAULTS) | IDENTITY_BOUND_WIDGET_KEYS
    keys_to_remove.update(
        key for key in state if key.startswith(IDENTITY_BOUND_KEY_PREFIXES)
    )
    for key in keys_to_remove:
        if key in state:
            del state[key]
    initialize_identity_state(state)
