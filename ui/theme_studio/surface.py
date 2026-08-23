"""
MultiMind AI - Theme Studio UI Surface
Provides an interactive, responsive presentation surface for selecting a base Theme/DesignDNA,
editing Theme-level presentation controls, viewing isolated live previews, and applying or discarding drafts.
"""
import re
from typing import List, Any
import streamlit as st
from ui.foundation import card_container, render_status_badge
from ui.themes import list_themes
from ui.dna import list_dna
from ui.components.theme_preview_spike.preview_spike import render_theme_preview_spike
from ui.theme_studio.state import (
    get_or_create_draft,
    reset_draft_to_base,
    apply_draft_to_active_theme,
    SESSION_DRAFT_KEY
)


def ensure_option_present(options: List[Any], current_value: Any) -> List[Any]:
    """Ensures current_value exists within options list without mutating or replacing it.

    If current_value is not in options, dynamically extends options while preserving
    numeric/unit order (e.g. px, rem) when possible.
    """
    if current_value is None or current_value in options:
        return list(options)

    opts = list(options)

    def _parse_numeric(val):
        if not isinstance(val, str):
            return None
        match = re.match(r"^([0-9.]+)\s*(px|rem|em|%|pt)?$", val.strip())
        if match:
            try:
                num = float(match.group(1))
                unit = match.group(2) or ""
                return num, unit
            except ValueError:
                return None
        return None

    curr_parsed = _parse_numeric(current_value)
    if curr_parsed:
        curr_num, curr_unit = curr_parsed
        inserted = False
        for idx, opt in enumerate(opts):
            opt_parsed = _parse_numeric(opt)
            if opt_parsed:
                opt_num, opt_unit = opt_parsed
                if opt_unit == curr_unit and curr_num < opt_num:
                    opts.insert(idx, current_value)
                    inserted = True
                    break
        if not inserted:
            opts.append(current_value)
    else:
        opts.append(current_value)

    return opts


def render_theme_studio_surface():
    """Renders the user-facing Theme Studio interactive editor surface."""
    card_container(
        "<div class='mm-typo-display'>🎨 Theme Studio</div>"
        "<div class='mm-typo-subheading mm-text-muted'>"
        "Customize visual presentation tokens with live isolated preview before applying to active app session."
        "</div>",
        variant="elevated"
    )

    draft = get_or_create_draft()

    # ===== SECTION 1: BASE THEME / DESIGN DNA SELECTION =====
    st.markdown("<div class='mm-typo-heading' style='margin-top: 1.5rem;'>1. Starting Base Selection</div>", unsafe_allow_html=True)
    col_type, col_select = st.columns([1, 2])

    with col_type:
        base_type = st.radio(
            "Base Type Source",
            options=["Theme", "Design DNA"],
            index=0 if draft.base_type == "theme" else 1,
            key="ts_base_type_radio"
        )
        selected_base_type = "theme" if base_type == "Theme" else "dna"

    with col_select:
        if selected_base_type == "theme":
            available_themes = list_themes()
            theme_ids = [t.id for t in available_themes]
            current_idx = theme_ids.index(draft.base_id) if draft.base_id in theme_ids else 0
            selected_theme = st.selectbox(
                "Select Base Theme",
                available_themes,
                index=current_idx,
                format_func=lambda t: f"{t.display_name} ({t.id})",
                key="ts_base_theme_select"
            )
            selected_id = getattr(selected_theme, "id", "default")
        else:
            available_dna = list_dna()
            dna_ids = [d.id for d in available_dna]
            current_idx = dna_ids.index(draft.base_id) if draft.base_id in dna_ids else 0
            if available_dna:
                selected_dna = st.selectbox(
                    "Select Base Design DNA",
                    available_dna,
                    index=current_idx,
                    format_func=lambda d: f"{d.display_name} ({d.id})",
                    key="ts_base_dna_select"
                )
                selected_id = getattr(selected_dna, "id", dna_ids[0])
            else:
                st.info("No Design DNA registered.")
                selected_id = "default"

        if selected_id != draft.base_id or selected_base_type != draft.base_type:
            draft = reset_draft_to_base(selected_id, selected_base_type)
            st.rerun()

    st.divider()

    # ===== SECTION 2: EDITABLE PRESENTATION CONTROLS & LIVE PREVIEW =====
    ctrl_col, preview_col = st.columns([1.1, 1.2])

    with ctrl_col:
        st.markdown("<div class='mm-typo-heading'>2. Editable Presentation Controls</div>", unsafe_allow_html=True)
        st.caption("Adjust supported theme tokens. Changes are kept in draft state until explicitly applied.")

        # ----- COLORS -----
        with st.expander("🎨 Semantic Colors", expanded=True):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                draft.colors["primary"] = st.color_picker(
                    "Primary Color",
                    value=draft.colors.get("primary", "#3B82F6"),
                    key="ts_color_primary"
                )
                draft.colors["surface"] = st.color_picker(
                    "Surface Color",
                    value=draft.colors.get("surface", "#18181B"),
                    key="ts_color_surface"
                )
                draft.colors["text"] = st.color_picker(
                    "Text Color",
                    value=draft.colors.get("text", "#FAFAFA"),
                    key="ts_color_text"
                )
            with col_c2:
                draft.colors["accent"] = st.color_picker(
                    "Accent Color",
                    value=draft.colors.get("accent", "#10B981"),
                    key="ts_color_accent"
                )
                draft.colors["background"] = st.color_picker(
                    "Background Color",
                    value=draft.colors.get("background", "#09090B"),
                    key="ts_color_bg"
                )
                draft.colors["border"] = st.color_picker(
                    "Border Color",
                    value=draft.colors.get("border", "#3F3F46"),
                    key="ts_color_border"
                )

        # ----- TYPOGRAPHY -----
        with st.expander("🔤 Typography Font Families", expanded=False):
            font_options = [
                "Inter, -apple-system, sans-serif",
                "Georgia, 'Times New Roman', serif",
                "Impact, 'Arial Black', sans-serif",
                "system-ui, -apple-system, sans-serif",
            ]
            mono_options = [
                "JetBrains Mono, monospace",
                "Fira Code, monospace",
                "Courier New, monospace"
            ]

            curr_base_font = draft.typography.get("font_family_base", font_options[0])
            safe_font_options = ensure_option_present(font_options, curr_base_font)
            base_idx = safe_font_options.index(curr_base_font)
            draft.typography["font_family_base"] = st.selectbox(
                "Base Font Stack",
                safe_font_options,
                index=base_idx,
                key="ts_typo_base_font"
            )

            curr_mono_font = draft.typography.get("font_family_mono", mono_options[0])
            safe_mono_options = ensure_option_present(mono_options, curr_mono_font)
            mono_idx = safe_mono_options.index(curr_mono_font)
            draft.typography["font_family_mono"] = st.selectbox(
                "Monospace Font Stack",
                safe_mono_options,
                index=mono_idx,
                key="ts_typo_mono_font"
            )

        # ----- BORDER RADIUS & SPACING -----
        with st.expander("📐 Shape Radius & Spacing Density", expanded=False):
            radius_preset = ["0px", "2px", "4px", "8px", "12px", "16px", "24px"]
            curr_radius_md = draft.radius.get("md", "8px")
            safe_radius_options = ensure_option_present(radius_preset, curr_radius_md)

            radius_md = st.select_slider(
                "Medium Border Radius",
                options=safe_radius_options,
                value=curr_radius_md,
                key="ts_radius_md_slider"
            )
            draft.radius["md"] = radius_md
            draft.radius["sm"] = "2px" if radius_md == "0px" else "4px"
            draft.radius["lg"] = "4px" if radius_md in ("0px", "2px") else "12px"

            spacing_preset = ["0.5rem", "0.75rem", "1rem", "1.25rem", "1.5rem"]
            curr_spacing_md = draft.spacing.get("md", "1rem")
            safe_spacing_options = ensure_option_present(spacing_preset, curr_spacing_md)

            spacing_md = st.select_slider(
                "Medium Spacing Unit",
                options=safe_spacing_options,
                value=curr_spacing_md,
                key="ts_spacing_md_slider"
            )
            draft.spacing["md"] = spacing_md

        # Update draft in session state
        st.session_state[SESSION_DRAFT_KEY] = draft

    with preview_col:
        st.markdown("<div class='mm-typo-heading'>3. Isolated Live Preview</div>", unsafe_allow_html=True)
        render_status_badge("Preview Mode — Active Theme Unchanged", variant="info")

        # Isolated Custom Preview Spike Component
        spike_payload = {
            "primary": draft.colors.get("primary", "#3B82F6"),
            "radius": draft.radius.get("md", "8px"),
            "density": "comfortable"
        }
        render_theme_preview_spike(initial_payload=spike_payload, key="ts_preview_spike_comp")

        # Isolated Dynamic Token Preview Box
        p_bg = draft.colors.get("background", "#09090B")
        p_surf = draft.colors.get("surface", "#18181B")
        p_text = draft.colors.get("text", "#FAFAFA")
        p_pri = draft.colors.get("primary", "#3B82F6")
        p_acc = draft.colors.get("accent", "#10B981")
        p_border = draft.colors.get("border", "#3F3F46")
        p_font = draft.typography.get("font_family_base", "sans-serif")
        p_rad = draft.radius.get("md", "8px")

        preview_html = f"""
        <div style="
            background-color: {p_bg};
            color: {p_text};
            font-family: {p_font};
            padding: 1.25rem;
            border-radius: {p_rad};
            border: 1px solid {p_border};
            margin-top: 1rem;
        ">
            <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem;">
                Draft Theme Preview: {draft.display_name}
            </div>
            <div style="
                background-color: {p_surf};
                padding: 1rem;
                border-radius: {p_rad};
                border: 1px solid {p_border};
                margin-bottom: 0.75rem;
            ">
                <span style="color: {p_text}; font-size: 0.9rem;">
                    This is an isolated card surface showing current draft tokens.
                </span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button style="
                    background-color: {p_pri};
                    color: #FFFFFF;
                    border: none;
                    padding: 0.4rem 0.8rem;
                    border-radius: {p_rad};
                    font-weight: 600;
                    cursor: pointer;
                ">Primary Action</button>
                <button style="
                    background-color: transparent;
                    color: {p_acc};
                    border: 1px solid {p_acc};
                    padding: 0.4rem 0.8rem;
                    border-radius: {p_rad};
                    font-weight: 600;
                    cursor: pointer;
                ">Accent Action</button>
            </div>
        </div>
        """
        st.markdown(preview_html, unsafe_allow_html=True)

    st.divider()

    # ===== SECTION 3: ACTIONS (APPLY / DISCARD) =====
    act_col1, act_col2, _ = st.columns([1, 1, 2])

    with act_col1:
        if st.button("🚀 Apply Theme", type="primary", use_container_width=True, key="ts_apply_theme_btn"):
            applied_theme = apply_draft_to_active_theme(draft)
            st.success(f"✅ Theme '{applied_theme.display_name}' applied to session!")
            st.rerun()

    with act_col2:
        if st.button("🔄 Discard / Reset Draft", use_container_width=True, key="ts_discard_draft_btn"):
            reset_draft_to_base(draft.base_id, draft.base_type)
            st.info("Draft reset to base defaults.")
            st.rerun()
