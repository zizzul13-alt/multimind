# Port the previews into Reflex — task brief

You are porting hand-built HTML previews into live Reflex components. The
previews are the contract. The goal is that the Reflex shell matches the HTML
**exactly**: same colours, same filters and gradients, same copy, same fonts,
same layout geometry, same interaction. Not "inspired by" — the same thing.

## What already exists (do not delete)

- `multimind_reflex/multimind_reflex.py` — the host. Contains the four semantic
  zones: `_workspace_utility_zone`, `_workspace_composer_zone`,
  `_workspace_result_zone`, `_workspace_history_zone`. These are the application
  truth and must be reused unchanged inside every shell.
- `multimind_reflex/shells.py` — a first attempt with one component per
  archetype. **It gets the layout columns roughly right but the visual treatment
  wrong.** You are replacing it.
- `assets/shells.css` — geometry only.
- `assets/scenes/*.webp` — the scene photos, already downloaded and optimised.

## The source of truth

Read these before writing anything:

    public/preview/lab/music-v0/architecture-swap/re-juliet-<archetype>-v1.html

There is one file per archetype. For the two-track variants the `you-and-i-*`
files share the structure but use a different type stack.

Extract, per shell, all of:

1. `:root` palette variables
2. `html, body` background, colour and base font
3. `.app` / the top-level grid: `grid-template-columns`, `grid-template-rows`
4. The `.photo` treatment — `filter`, gradient overlays, `transform`
5. Every region's typography: family, size, weight, letter-spacing, line-height
6. **The literal copy** — headings, kickers, thesis, prompts, labels. Copy it
   verbatim, including Indonesian text. Do not substitute placeholder strings.
7. The A/B/C world switcher markup and its active-state styling

## Current state of the port (measured, not guessed)

`node tools/shell-check.mjs "Night Train"` reports the structure is present but
the visuals are not. Known failures:

| | HTML | current Reflex |
|---|---|---|
| terminal_hacker background | `#08090b` | light gray |
| sidebar | `minmax(220px,29vw)`, `#07080ac7` + blur(8px) | too wide, no tint |
| terminal font | IBM Plex Mono throughout | serif leaking into terminal text |
| ACTIVE BUFFER heading | `Rainy Window` (the scene name) | `forward-inevitability` (wrong value) |
| prompts | `you@juliet:~$` / `multimind>` | `YOU@JULIET` (different format) |
| scene photo | full-bleed behind the shell | missing in 5 of 7 shells |

## State access

Live values come from `WorkspaceDnaState` (imported as `HostState`):

    active_music_display_name       track title
    active_music_world              world slug
    active_music_signature          the correspondence signature
    active_music_combination_id     e.g. music:ti01@terminal_hacker
    active_music_primary_object     the object under discussion
    active_music_primary_action     the action prompt
    active_music_composer_label     composer affordance
    active_music_scenes             list[MusicScene] — the A/B/C worlds
    active_music_scene_key          which world is selected
    active_music_scene_photo        resolved photo path
    active_music_scene_thesis       the resolved scene thesis
    active_music_scene_credit       photo credit line
    active_music_scene_position     object-position

`set_music_scene(key)` switches world.

## Reflex constraints — these will bite you

- A state Var cannot be used in a Python boolean. `Var or "x"` raises
  `VarTypeError`. Use `rx.cond(var != "", var, "fallback")`.
- A Var has no `index`, `find` or `map` operation — only indexing. Searching a
  list Var during render is not possible; resolve in Python and publish a plain
  value.
- `rx.foreach` takes no `class_name`. Wrap it in an `rx.box` that carries it.
- There is no `rx.span`. Use `rx.text`.
- `multimind_reflex.py` imports `shells.py`, so `shells.py` must not import
  `multimind_reflex.py` at module scope. A `_zone(name)` helper already does a
  lazy import — keep that pattern.
- `dataclass` fields do not reach the browser. Publish plain strings.

## Scope for this run

Port **`terminal_hacker`** only, completely. Match
`public/preview/lab/music-v0/architecture-swap/re-juliet-terminal-v1.html` in
both directions:

- dark ground `#08090b`, photo filter and both gradient overlays
- `.side` at `minmax(220px,29vw)` with its tint and blur, rows `auto auto 1fr auto`
- `.term` as `auto 1fr`, the `.screen` scroll region
- IBM Plex Mono for brand, kicker, buffer, foot, top, prompt, sys, composer
- Kaisei Opti for the `h1`
- the literal copy from the file, including `multimind@juliet:~$ session attach`
  and the `you@juliet:~$` / `multimind>` prompt pairs
- the `.buf` list with `.dot`, and the active state's rose wash and glow
- ACTIVE BUFFER must show the **selected scene's name**, not the world slug
- the scene photo behind the shell, darkened per the preview's filter

Do not touch the other six shells. Do not change the four semantic zones. Do not
change any event handler or persistence path.

## Verify before you finish

Run both and report the real numbers:

    node tools/shell-check.mjs "Night Train"
    .venv/Scripts/python.exe -m pytest tests/ -q

The suite must stay at 463 passed, 1 pre-existing failure. Then state plainly
which preview properties you matched and which you did not — do not claim a
match you did not measure.