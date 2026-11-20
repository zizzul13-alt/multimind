# Streamlit Fluidity PoC

This is an isolated, fake-data-only Streamlit experiment. It does not import
MultiMind's application, providers, database, or production UI modules.

## Run locally

From the repository root, with the existing virtual environment active:

```powershell
.\.venv\Scripts\streamlit.exe run .\experiments\streamlit_fluidity\app.py
```

The experiment relies on the repository environment's pinned Streamlit 1.61.0.
`experiments/streamlit_fluidity/requirements.txt` is descriptive only; do not
use it to alter the repository's root dependency policy.

## Validation record

The automated checks completed in this execution environment are:

- `app.py` compiles with Python 3.12.10.
- Streamlit 1.61.0 exposes `st.fragment`.
- `pip check` reports no broken requirements.

### Execution-environment limitation

The agent execution environment does not preserve a detached child process
after a tool command returns. A foreground diagnostic `streamlit run` process
remained alive until the command timeout and emitted no startup error, but it
was terminated by that timeout. This is an execution-environment limitation,
not a Streamlit Fluidity PoC failure. Do not interpret the absence of a later
listener on port 8511 as an application startup failure.

## Manual interactive validation required

All observations below are **UNKNOWN** until the app is run in a persistent
local terminal and inspected in a browser. They must not be inferred from the
static or startup checks above.

| Probe | What to verify interactively | Status |
| --- | --- | --- |
| F1 — theme transition | Switch between Night Shift and Paper Signal; confirm the scoped shell changes color without changing the fake session state. | **UNKNOWN** |
| F2 — archetype projection | Switch Conversation, Command Center, and Research Lab; confirm draft, selected candidate, and inspector state persist across projections. | **UNKNOWN** |
| F3 — interaction locality | Compare the native slider's rerun with the component range/color/drag controls; confirm component changes stay browser-local until **Apply to Python**. | **UNKNOWN** |
| F4 — long execution | Start the simulated execution; confirm only the fragment status refreshes while the content above remains usable, then confirm reset works. | **UNKNOWN** |
| F5 — responsive projection | At approximately 390px wide, select Command Center and confirm the order is Main, Status, Navigation, Inspector with no horizontal overflow. | **UNKNOWN** |
