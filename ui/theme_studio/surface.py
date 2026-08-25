"""
MultiMind AI - Theme Studio UI Surface
Provides an interactive, responsive presentation surface for selecting independent composition roles
(Identity DNA, Web/Information DNA, UI/UX Archetype), editing Theme-level presentation controls,
viewing isolated live previews, and applying or discarding drafts atomically.
"""
import re
from typing import List, Any
import streamlit as st
from ui.foundation import card_container, render_status_badge
from ui.presentation import render_brand_identity
from ui.presentation.resolver import list_archetypes
from ui.dna import list_dna
from ui.dna.models import DesignComposition
from ui.dna.resolver import resolve_composition
from ui.components.theme_preview_spike.preview_spike import render_theme_preview_spike
from ui.theme_studio.state import (
    get_or_create_draft,
    reset_draft_to_base,
    apply_draft_to_active_theme,
    SESSION_DRAFT_KEY
)


def ensure_option_present(options: List[Any], current_value: Any) -> List[Any]:
    """Ensures current_value exists within options list without mutating or replacing it."""
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
    with st.container(key="theme_studio_surface_container"):
        card_container(
            "<div class='mm-typo-display'>🎨 Theme Studio — Design DNA Composition</div>"
            "<div class='mm-typo-subheading mm-text-muted'>"
            "Compose independent design roles (Identity DNA, Web/Information DNA, UI/UX Archetype) with live isolated preview."
            "</div>",
            variant="elevated"
        )

        draft = get_or_create_draft()

        # ===== SECTION 1: ROLE-BASED COMPOSITION SELECTORS =====
        st.markdown("<div class='mm-typo-heading' style='margin-top: 1.5rem;'>1. Role-Based Design Composition</div>", unsafe_allow_html=True)

        all_dna = list_dna()
        identity_dnas = [d for d in all_dna if d.role == "identity"]
        web_dnas = [d for d in all_dna if d.role == "web_information"]
        archetype_options = list_archetypes()

        col_id, col_web, col_arch = st.columns(3)

        with col_id:
            st.markdown("<b>Identity / Cultural DNA</b>", unsafe_allow_html=True)
            id_ids = [d.id for d in identity_dnas]
            current_id_idx = id_ids.index(draft.identity_dna_id) if draft.identity_dna_id in id_ids else 0
            selected_id_dna = st.selectbox(
                "Identity DNA",
                identity_dnas,
                index=current_id_idx,
                format_func=lambda d: f"{d.display_name} ({d.id})",
                key="ts_composition_identity_select"
            )
            selected_id_str = getattr(selected_id_dna, "id", "rinpa-decorative-spatial")

        with col_web:
            st.markdown("<b>Web / Information DNA</b>", unsafe_allow_html=True)
            # Support None / None selector for Web DNA
            web_options = [None] + web_dnas
            current_web_idx = 0
            if draft.web_information_dna_id:
                web_ids = [getattr(w, "id", None) for w in web_options]
                if draft.web_information_dna_id in web_ids:
                    current_web_idx = web_ids.index(draft.web_information_dna_id)

            selected_web_dna = st.selectbox(
                "Web / Information DNA",
                web_options,
                index=current_web_idx,
                format_func=lambda d: f"{d.display_name} ({d.id})" if d else "None (Default Density)",
                key="ts_composition_web_select"
            )
            selected_web_str = getattr(selected_web_dna, "id", None) if selected_web_dna else None

        with col_arch:
            st.markdown("<b>UI / UX Archetype</b>", unsafe_allow_html=True)
            arch_keys = [opt[0] for opt in archetype_options]
            arch_dict = dict(archetype_options)
            current_arch_idx = arch_keys.index(draft.archetype_id) if draft.archetype_id in arch_keys else 0

            selected_arch_key = st.selectbox(
                "UI/UX Archetype",
                arch_keys,
                index=current_arch_idx,
                format_func=lambda k: arch_dict.get(k, k),
                key="ts_composition_archetype_select"
            )

        # Check if composition selection changed in draft state
        if (
            selected_id_str != draft.identity_dna_id
            or selected_web_str != draft.web_information_dna_id
            or selected_arch_key != draft.archetype_id
        ):
            from ui.theme_studio.state import init_draft_from_composition
            new_draft = init_draft_from_composition(
                identity_dna_id=selected_id_str,
                web_information_dna_id=selected_web_str,
                archetype_id=selected_arch_key
            )
            st.session_state[SESSION_DRAFT_KEY] = new_draft
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
                    "Georgia, 'Times New Roman', serif",
                    "Inter, -apple-system, sans-serif",
                    "Impact, 'Arial Black', sans-serif",
                    "system-ui, -apple-system, sans-serif",
                ]
                mono_options = [
                    "'SFMono-Regular', Consolas, monospace",
                    "JetBrains Mono, monospace",
                    "Fira Code, monospace"
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
                curr_radius_md = draft.radius.get("md", "4px")
                safe_radius_options = ensure_option_present(radius_preset, curr_radius_md)

                radius_md = st.select_slider(
                    "Medium Border Radius",
                    options=safe_radius_options,
                    value=curr_radius_md,
                    key="ts_radius_md_slider"
                )
                draft.radius["md"] = radius_md
                draft.radius["sm"] = "2px" if radius_md == "0px" else "3px"
                draft.radius["lg"] = "4px" if radius_md in ("0px", "2px") else "6px"

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
            st.markdown("<div class='mm-typo-heading'>3. Isolated Composed Live Preview</div>", unsafe_allow_html=True)
            render_status_badge("Preview Mode — Active App State Unchanged", variant="info")

            # Resolve Composed Projection for preview
            projection = draft.resolve()

            # Display Composition Policy Badge Summary
            card_container(
                f"<div class='mm-typo-label'>📐 Composition Resolution Summary:</div>"
                f"<ul class='mm-typo-body-small mm-text-muted' style='padding-left: 1.2rem; margin-bottom: 0;'>"
                f"<li><b>Identity:</b> {projection.provenance.get('identity_display_name')}</li>"
                f"<li><b>Web/Info:</b> {projection.provenance.get('web_information_display_name') or 'None'}</li>"
                f"<li><b>Archetype View:</b> {projection.provenance.get('archetype_display_name')}</li>"
                f"<li><b>Metadata Prominence:</b> {projection.presentation_policy.metadata_prominence}</li>"
                f"<li><b>Status Richness:</b> {projection.presentation_policy.status_richness}</li>"
                f"</ul>",
                variant="muted"
            )

            # Material Identity Preview (S6.3 Presentation Seam)
            render_brand_identity(draft.identity_dna_id, container_kind="theme_studio")

            # Isolated Custom Preview Spike Component
            spike_payload = {
                "primary": draft.colors.get("primary", "#B8860B"),
                "radius": draft.radius.get("md", "4px"),
                "density": "compact" if projection.presentation_policy.secondary_compactness else "comfortable"
            }
            render_theme_preview_spike(initial_payload=spike_payload, key="ts_preview_spike_comp")

            # Isolated Dynamic Token Preview Box
            p_bg = draft.colors.get("background", "#F2ECE1")
            p_surf = draft.colors.get("surface", "#E6DEC8")
            p_text = draft.colors.get("text", "#1A1714")
            p_pri = draft.colors.get("primary", "#B8860B")
            p_acc = draft.colors.get("accent", "#2E5A44")
            p_border = draft.colors.get("border", "#2B241C")
            p_font = draft.typography.get("font_family_base", "serif")
            p_rad = draft.radius.get("md", "4px")

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
                    Composed Preview: {draft.identity_dna_id} + {draft.web_information_dna_id or 'standard'}
                </div>
                <div style="
                    background-color: {p_surf};
                    padding: 1rem;
                    border-radius: {p_rad};
                    border: 1px solid {p_border};
                    margin-bottom: 0.75rem;
                ">
                    <span style="color: {p_text}; font-size: 0.9rem;">
                        Isolated card surface rendering primary visual identity and secondary information density policy.
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
            if st.button("🚀 Apply Composition", type="primary", use_container_width=True, key="ts_apply_theme_btn"):
                applied_theme = apply_draft_to_active_theme(draft)
                st.success(f"✅ Composition applied to session (Theme: '{applied_theme.display_name}', Archetype: '{draft.archetype_id}')!")
                st.rerun()

        with act_col2:
            if st.button("🔄 Discard / Reset Draft", use_container_width=True, key="ts_discard_draft_btn"):
                reset_draft_to_base(draft.identity_dna_id, "composition")
                st.info("Draft reset to composition defaults.")
                st.rerun()
