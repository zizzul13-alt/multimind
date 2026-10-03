# Port the previews into Reflex — round 2

You already ported `terminal_hacker` with real visual fidelity: the photo
filter, both gradient overlays, the side tint and blur, the buffer dot and its
active glow, the scene-name heading and the literal prompt copy. Keep that
standard for the remaining six.

## Measured gaps — read gap-report.md, but verify against the HTML

    node tools/preview-gap.mjs "Night Train"

writes `gap-report.md`: 40 properties checked, 38 gaps. The rows that repeat
across nearly every shell are the real signal:

- **chrome face renders `Segoe UI`, the previews declare `IBM Plex Mono`**
- **h1 face renders `Segoe UI` or `Didot`, the previews declare `Kaisei Opti`**
- **photo filter resolves to `none`, the previews declare saturate/brightness/contrast**
- body background falls back to `000000` instead of the preview's ground
- the preview's literal copy is missing: `JULIET RE EDIT`, `TERMINAL / HACKER ×
  MUSIC DNA`, `WORLD / BEHIND THE CONVERSATION`, `ENTITIES · RELATIONSHIPS`,
  `CONVERSATION IDENTITY`, `LIVE STATE`, `OPERATOR INTERVENTION`,
  `ACTIVE MULTI-OBJECT DESK`

Ignore the `h1 face` row's declared value — the extractor picks the wrong face
from the stylesheet. Read the real value from the HTML yourself.

### The font problem is global and probably the largest single win

Every shell renders Segoe UI, so nothing looks like its preview. The previews
load the family from Google Fonts:

    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Kaisei+Opti:wght@500;600;700&family=M+PLUS+1p:wght@400;500;600&display=swap" rel="stylesheet">

Reflex renders without it, so the stacks in `assets/shells.css` fall through to
the system sans. Decide how to serve those faces (vendored woff2 under
`public/`, or the existing font css under `design_dna/assets/fonts/`) and apply
them. The `you-and-i-*` previews use a different stack — `Bowlby One SC` and
`DM Mono` — so per-track type may be part of this.

## Source of truth, per archetype

    public/preview/lab/music-v0/architecture-swap/re-juliet-<stem>-v1.html

stems: `minimal-saas`, `terminal`, `research-lab`, `ai-workspace`, `chat-first`,
`agent-canvas`, `command-center`

For each, extract the `:root` palette, the `html, body` ground, the `.photo`
treatment with its filters and both `:after` gradients, every region's
typography, the top-level grid, and the **literal copy**. Copy the strings
verbatim, including the Indonesian text. `terminal_hacker` is already done — read
your own port of it and match that level.

## Scope

Port the remaining six: `minimal_saas`, `ai_research_lab`, `ai_workspace`,
`chat_first`, `agent_canvas`, `command_center`.

Do not change `terminal_hacker`. Do not change the four semantic zones, any event
handler, or any persistence path.

## Rules that will bite you

- A state Var cannot be used in a Python boolean. `Var or "x"` raises
  `VarTypeError`; use `rx.cond(var != "", var, "fallback")`.
- A Var has no `index`, `find` or `map`. Resolve in Python, publish a plain value.
- `rx.foreach` takes no `class_name`. Wrap it in an `rx.box`.
- There is no `rx.span`. Use `rx.text`.
- `multimind_reflex.py` imports `shells.py`, so do not import it back at module
  scope; the `_zone(name)` helper does a lazy import. Keep that.
- Dataclass fields do not reach the browser. Publish plain strings.

## Contract you must not break

`multimind_reflex.py` was regressed last time by deleting the responsive fallback.
Keep `_shell_fallback_grid()`, its `grid_template_areas=rx.breakpoints` and
`grid_template_columns=rx.breakpoints`, and the `_workspace_desktop_areas` /
`_workspace_mobile_areas` helpers. Every zone must be composed at most once per
shell — `shell_ai_research_lab` previously composed the result zone twice.

## Verify before reporting done

Run all three and report the real numbers:

    node tools/preview-gap.mjs "Night Train"
    node tools/shell-check.mjs "Night Train"
    .venv/Scripts/python.exe -m pytest tests/ -q

The suite must be **463 passed, 1 failed**, the single failure being
`test_rj3_functional_presentation_parity.py::test_theme_studio_live_preview_consumes_resolved_draft_tokens`,
which was already failing before this work. A larger failure count means you
broke the contract above — fix that before anything else.

Then report, as separate lists, which preview properties you matched and which
you did not. Do not claim a match you did not measure. If something is still
wrong, say so plainly rather than describing the intent.