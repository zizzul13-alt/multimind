"""MultiMind Streamlit fluidity experiment.  Run only from this directory."""
from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).parent
LOCAL_SURFACE = components.declare_component(
    "fluidity_local_surface", path=str(ROOT / "component")
)
THEMES = {
    "night-shift": {"name": "Night Shift", "accent": "#7c3aed", "surface": "#171821", "canvas": "#0d0e14", "ink": "#f4f1ff", "muted": "#b9b2cb"},
    "paper-signal": {"name": "Paper Signal", "accent": "#c2410c", "surface": "#fffaf3", "canvas": "#f6efe4", "ink": "#211a14", "muted": "#665c51"},
}
ARCHETYPES = {
    "conversation": "Conversation — feed and composer first",
    "command": "Command center — status, work, inspector",
    "research": "Research lab — evidence, synthesis, agents",
}
STAGES = ("Researcher", "Candidate A", "Candidate B", "Candidate C", "Judge")


def init_state() -> None:
    defaults = {
        "fluid_theme": "night-shift",
        "fluid_archetype": "conversation",
        "fluid_selected": "Candidate B",
        "fluid_context_open": True,
        "fluid_draft": "Keep the existing session semantics while changing the presentation shell.",
        "fluid_history": [
            ("You", "Compare three safe ways to present the same debate."),
            ("MultiMind", "The conversation, session identity, selected candidate, and contextual inspector remain available in each projection."),
        ],
        "fluid_run_started": None,
        "fluid_local_event": "No component value applied to Python yet.",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def apply_theme() -> None:
    t = THEMES[st.session_state.fluid_theme]
    st.markdown(
        f"""<style>
        :root {{ --fx-accent:{t['accent']}; --fx-surface:{t['surface']}; --fx-canvas:{t['canvas']}; --fx-ink:{t['ink']}; --fx-muted:{t['muted']}; }}
        .stApp {{ background:var(--fx-canvas); color:var(--fx-ink); }}
        .stApp, .stApp * {{ transition: background-color .18s ease, color .18s ease, border-color .18s ease; }}
        .fx-card {{ background:var(--fx-surface); color:var(--fx-ink); border:1px solid color-mix(in srgb, var(--fx-accent) 40%, transparent); border-radius:14px; padding:1rem; margin:.35rem 0; }}
        .fx-kicker {{ color:var(--fx-muted); font-size:.8rem; text-transform:uppercase; letter-spacing:.08em; }}
        .fx-accent {{ color:var(--fx-accent); }}
        .fx-shell {{ display:grid; grid-template-columns:minmax(140px,.7fr) minmax(280px,2fr) minmax(180px,.9fr); gap:.75rem; }}
        .fx-shell > section {{ min-width:0; }}
        .fx-hover {{ padding:.75rem; border:1px dashed var(--fx-muted); border-radius:10px; }}
        .fx-hover:hover {{ background:color-mix(in srgb, var(--fx-accent) 16%, var(--fx-surface)); border-style:solid; }}
        @media (max-width: 640px) {{
          .fx-shell {{ display:flex; flex-direction:column; }}
          .fx-shell .fx-main {{ order:1; }}
          .fx-shell .fx-status {{ order:2; }}
          .fx-shell .fx-nav {{ order:3; }}
          .fx-shell .fx-inspector {{ order:4; }}
        }}
        </style>""",
        unsafe_allow_html=True,
    )


def shell_header() -> None:
    st.caption("ISOLATED RUNTIME EXPERIMENT · fake local data only")
    st.title("MultiMind Fluidity Lab")
    left, right = st.columns([2, 1])
    with left:
        st.selectbox("Presentation theme", THEMES, format_func=lambda x: THEMES[x]["name"], key="fluid_theme")
    with right:
        st.selectbox("Archetype projection", ARCHETYPES, format_func=lambda x: ARCHETYPES[x], key="fluid_archetype")
    st.caption("Semantic state: Session MM-FLUID-042 · selected candidate: " + st.session_state.fluid_selected + " · contextual area: " + ("open" if st.session_state.fluid_context_open else "closed"))


def history_html() -> str:
    return "".join(f"<div class='fx-card'><b>{who}</b><br>{text}</div>" for who, text in st.session_state.fluid_history)


def render_conversation() -> None:
    st.subheader("Conversation projection")
    st.markdown(history_html(), unsafe_allow_html=True)
    st.text_area("Draft input", key="fluid_draft", height=90)
    if st.button("Append fake response", key="fluid_append"):
        st.session_state.fluid_history.append(("You", st.session_state.fluid_draft or "Untitled input"))
        st.session_state.fluid_history.append(("MultiMind", "Fake response added locally; no provider or persistence layer was used."))
        st.rerun()
    with st.expander("Contextual inspector", expanded=st.session_state.fluid_context_open):
        st.toggle("Keep inspector open", key="fluid_context_open")
        st.write("Selected candidate:", st.session_state.fluid_selected)


def render_command() -> None:
    st.subheader("Command center projection")
    st.markdown("""<div class='fx-shell'>
      <section class='fx-card fx-nav'><div class='fx-kicker'>Navigation</div><b>Session MM-FLUID-042</b><br>Timeline<br>Artifacts</section>
      <section class='fx-card fx-main'><div class='fx-kicker'>Main work</div><b>Candidate comparison</b><br>Same fake debate content is primary here.</section>
      <section class='fx-card fx-inspector'><div class='fx-kicker'>Inspector</div><b>Candidate B</b><br>Confidence 82%</section>
      <section class='fx-card fx-status'><div class='fx-kicker'>Status</div>Research ready · 3 candidates</section>
    </div>""", unsafe_allow_html=True)
    st.radio("Selected candidate", ("Candidate A", "Candidate B", "Candidate C"), key="fluid_selected", horizontal=True)
    st.text_area("Draft input", key="fluid_draft", height=90)


def render_research() -> None:
    st.subheader("Research lab projection")
    evidence, synthesis = st.columns([1, 1.4])
    with evidence:
        st.markdown("<div class='fx-card'><div class='fx-kicker'>Evidence</div>Researcher notes<br>Candidate A — feasibility<br>Candidate B — usability</div>", unsafe_allow_html=True)
    with synthesis:
        st.markdown("<div class='fx-card'><div class='fx-kicker'>Synthesis</div><b>Same session, different hierarchy.</b><br>Candidate B is selected because it preserves local responsiveness.</div>", unsafe_allow_html=True)
    st.text_area("Draft input", key="fluid_draft", height=90)


def render_high_frequency() -> None:
    st.divider()
    st.header("F3 · high-frequency interaction")
    st.caption("The native slider is intentionally a rerun path. The iframe preview is intentionally browser-local until Apply.")
    native = st.slider("Native spacing preview (reruns Streamlit)", 4, 32, 12, key="fluid_native_spacing")
    st.markdown(f"<div class='fx-card' style='padding:{native}px'><b>Native preview</b><br>This value is rendered by Python after widget interaction.</div>", unsafe_allow_html=True)
    st.markdown("<div class='fx-hover'><b>Hover-local interaction</b><br>Hover this card: CSS responds without a Python request.</div>", unsafe_allow_html=True)
    value = LOCAL_SURFACE(initial={"color": "#7c3aed", "radius": 14}, key="fluid_local_surface", default=None)
    if isinstance(value, dict):
        st.session_state.fluid_local_event = f"Applied local value: color={value.get('color')}, radius={value.get('radius')}, x={value.get('x')}"
    st.caption(st.session_state.fluid_local_event)


@st.fragment(run_every="1s")
def execution_fragment() -> None:
    started = st.session_state.fluid_run_started
    if started is None:
        if st.button("Start simulated execution", key="fluid_start_execution"):
            st.session_state.fluid_run_started = time.time()
            st.rerun(scope="fragment")
        return
    elapsed = time.time() - started
    index = min(int(elapsed // 2), len(STAGES) - 1)
    progress = min(elapsed / (2 * len(STAGES)), 1.0)
    st.progress(progress, text=f"Running: {STAGES[index]}")
    st.caption("Fragment refreshes this status region only; existing content above remains readable.")
    with st.expander("Non-conflicting presentation control", expanded=False):
        st.toggle("Dense status labels", key="fluid_dense_status")
    if progress >= 1:
        st.success("Judge complete. Simulated execution ended.")
        if st.button("Reset simulation", key="fluid_reset_execution"):
            st.session_state.fluid_run_started = None
            st.rerun(scope="fragment")


def main() -> None:
    st.set_page_config(page_title="MultiMind Fluidity PoC", layout="wide")
    init_state()
    apply_theme()
    shell_header()
    if st.session_state.fluid_archetype == "conversation":
        render_conversation()
    elif st.session_state.fluid_archetype == "command":
        render_command()
    else:
        render_research()
    render_high_frequency()
    st.divider()
    st.header("F4 · simulated long execution")
    execution_fragment()
    st.caption("F5 mobile check: resize to about 390px. The command shell changes from NAV | MAIN | INSPECTOR to MAIN, STATUS, navigation, inspector via the scoped experiment CSS.")


if __name__ == "__main__":
    main()
