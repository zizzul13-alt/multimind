"""Per-archetype shells, replicated from the hand-built previews.

The previews in preview/lab/music-v0/architecture-swap/ are the contract. Each
declares its own geometry, palette, zone names and copy, and the shells differ
structurally rather than by colour: a three-column research desk, a canvas with
an absolutely positioned core, a chat column with a 94px role gutter. Changing
grid-template-areas on one shared grid cannot produce that, so each archetype
gets its own component tree here.

The four semantic zones (utility, composer, result, history) stay the
application truth and are reused unchanged; only the shell around them differs.
"""

import reflex as rx

from multimind_reflex.workspace_dna_state import WorkspaceDnaState as HostState
from ui.music_scenes import MusicScene


# --------------------------------------------------------------------------
# Scene-aware pieces, shared by the shells that show an A/B/C world.
# --------------------------------------------------------------------------


def _has_scene() -> bool:
    return HostState.active_music_scene is not None


def _world_photo(class_name: str = "mm-world-photo", style: dict | None = None) -> rx.Component:
    """The selected scene photo, or nothing when the track has no scenes."""
    return rx.cond(
        _has_scene(),
        rx.image(
            src=HostState.active_music_scene_photo,
            alt=HostState.active_music_display_name,
            width="100%",
            height="100%",
            object_fit="cover",
            object_position=HostState.active_music_scene_position,
            class_name=f"{class_name}-img",
            style=style or {},
        ),
    )


def _world_copy(kicker: str, title: str, show_thesis: bool = True) -> rx.Component:
    """Kicker + serif title + the scene thesis, as the previews set them."""
    return rx.vstack(
        rx.text(kicker, class_name="mm-kicker"),
        rx.heading(title, class_name="mm-world-title"),
        rx.cond(
            _has_scene() if show_thesis else False,
            rx.text(HostState.active_music_scene_thesis, class_name="mm-world-thesis"),
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def _credit() -> rx.Component:
    return rx.cond(
        _has_scene(),
        rx.text(HostState.active_music_scene_credit, class_name="mm-world-credit"),
    )


def _scene_tab_button(scene: MusicScene) -> rx.Component:
    """One A/B/C buffer button. The previews label these a/b/c plus a slug."""
    return rx.button(
        rx.hstack(
            rx.box(class_name="mm-dot", width="7px", height="7px"),
            rx.text(scene["key"].upper(), class_name="mm-buffer-key"),
            rx.text(scene["name"], class_name="mm-buffer-name"),
            spacing="2",
            align="center",
        ),
        on_click=HostState.set_music_scene(scene["key"]),
        variant="ghost",
        class_name=rx.cond(
            scene["key"] == HostState.active_music_scene_key,
            "mm-buffer mm-buffer-active",
            "mm-buffer",
        ),
        width="100%",
    )


def _scene_switcher(variant: str = "buffers") -> rx.Component:
    """The A/B/C world switcher.

    `variant` mirrors how the preview styles it: buffers is a vertical list with
    a dot per world, tabs is a bordered row, worlds is a three-up strip.
    """
    # rx.foreach takes no class_name, so the styled container wraps it.
    return rx.box(
        rx.foreach(
            HostState.active_music_scenes,
            lambda scene: _scene_tab_button(scene),
        ),
        class_name=f"mm-{variant}",
        width="100%",
    )


# --------------------------------------------------------------------------
# ai_research_lab -- three columns, left tabs, centre viewport, right evidence.
#
# .lab { grid-template-columns: minmax(190px,.78fr) minmax(0,1.7fr) minmax(220px,.9fr) }
# --------------------------------------------------------------------------

def _zone(name: str):
    """Fetch a zone component lazily.

    multimind_reflex.py imports this module, so importing it back at module
    scope would be circular. Importing the zone on first use keeps the shells
    reusing the exact same zone components without that cycle.
    """
    import multimind_reflex.multimind_reflex as host

    return getattr(host, name)()


def shell_ai_research_lab() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("MultiMind", class_name="mm-brand"),
            rx.spacer(),
            rx.text(HostState.active_music_display_name, class_name="mm-meta"),
            width="100%",
            align="center",
            class_name="mm-top",
        ),
        # .intro -- a two-up eyebrow band above the lab
        rx.box(
            _world_copy("RESEARCH LAB / MUSIC DNA × EVIDENCE", rx.cond(HostState.active_music_world != "", HostState.active_music_world, "A/B/C worlds")),
            class_name="mm-intro",
            width="100%",
        ),
        rx.box(
            rx.hstack(
                # left: the world tabs plus the claim
                rx.vstack(
                    rx.text("ACTIVE WORLD", class_name="mm-label"),
                    _scene_switcher("tabs"),
                    rx.box(_zone("_workspace_utility_zone"), class_name="mm-left-claim", width="100%"),
                    spacing="3",
                    class_name="mm-lab-left",
                    width="100%",
                ),
                # centre: the viewport, which is where the photo lives
                rx.vstack(
                    rx.box(
                        _world_photo("mm-viewport"),
                        rx.vstack(
                            rx.hstack(
                                rx.text("VIEWPORT", class_name="mm-label"),
                                rx.spacer(),
                                rx.text(HostState.active_music_scene_key.upper(), class_name="mm-view-state"),
                            ),
                            rx.text(HostState.active_music_signature, class_name="mm-view-copy"),
                            rx.cond(_has_scene(), _credit()),
                            padding="4",
                            spacing="2",
                            class_name="mm-view-ui",
                            width="100%",
                        ),
                        class_name="mm-viewport-wrap",
                        width="100%",
                    ),
                    _zone("_workspace_result_zone"),
                    spacing="4",
                    class_name="mm-lab-viewport",
                    width="100%",
                ),
                # right: evidence rows and synthesis
                rx.vstack(
                    rx.text("EVIDENCE", class_name="mm-label"),
                    rx.foreach(
                        HostState.active_music_scenes,
                        lambda s: rx.box(
                            rx.hstack(
                                rx.text(s["key"].upper(), class_name="mm-ev-key"),
                                rx.text(s["thesis"][:60], class_name="mm-evidence"),
                                spacing="2",
                                align="start",
                            ),
                            class_name="mm-evidence-row",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    class_name="mm-lab-right",
                    width="100%",
                ),
                align="start",
                class_name="mm-lab",
                width="100%",
            ),
            width="100%",
        ),
        _zone("_workspace_composer_zone"),
        _zone("_workspace_history_zone"),
        spacing="0",
        width="100%",
        class_name="mm-shell mm-shell-ai-research-lab",
    )


# --------------------------------------------------------------------------
# ai_workspace -- three columns, the middle one a two-up object desk.
#
# .workspace { grid-template-columns: 190px minmax(0,1fr) clamp(300px,26vw,360px) }
# .desk      { grid-template-columns: 1fr 1fr }  with .wide spanning both
# --------------------------------------------------------------------------


def shell_ai_workspace() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("MultiMind", class_name="mm-brand"),
            rx.spacer(),
            rx.text(HostState.active_music_combination_id, class_name="mm-meta"),
            width="100%",
            align="center",
            class_name="mm-top",
        ),
        rx.hstack(
            # shelf: the world switcher
            rx.vstack(
                rx.text("SHELF", class_name="mm-label"),
                _scene_switcher("world-buttons"),
                rx.box(_zone("_workspace_utility_zone"), width="100%"),
                spacing="3",
                class_name="mm-shelf",
                width="100%",
            ),
            # desk: the two-up object board
            rx.vstack(
                rx.hstack(
                    rx.text(rx.cond(HostState.active_music_primary_object != "", HostState.active_music_primary_object, "OBJECT"), class_name="mm-desk-head"),
                    rx.spacer(),
                    rx.text(rx.cond(HostState.active_music_primary_action != "", HostState.active_music_primary_action, ""), class_name="mm-meta"),
                    width="100%",
                    align="end",
                    class_name="mm-desk-head",
                ),
                rx.box(_zone("_workspace_result_zone"), class_name="mm-object wide", width="100%"),
                rx.box(
                    rx.text(HostState.active_music_primary_action, class_name="mm-thread"),
                    class_name="mm-object",
                    width="100%",
                ),
                rx.box(_zone("_workspace_history_zone"), class_name="mm-object wide", width="100%"),
                spacing="3",
                class_name="mm-desk",
                width="100%",
            ),
            # worldpanel: the photo and its copy
            rx.vstack(
                rx.box(_world_photo("mm-worldpanel"), class_name="mm-worldpanel-photo", width="100%"),
                rx.vstack(
                    _world_copy("WORLD PANEL", rx.cond(HostState.active_music_world != "", HostState.active_music_world, "A/B/C")),
                    _credit(),
                    spacing="3",
                    class_name="mm-worldpanel-copy",
                    width="100%",
                ),
                rx.box(_zone("_workspace_composer_zone"), width="100%"),
                spacing="3",
                class_name="mm-worldpanel",
                width="100%",
            ),
            align="start",
            class_name="mm-workspace-3",
            width="100%",
        ),
        spacing="0",
        width="100%",
        class_name="mm-shell mm-shell-ai-workspace",
    )


# --------------------------------------------------------------------------
# chat_first -- a 255px rail beside the thread; worlds sit over the composer.
#
# .chat { grid-template-columns: 255px minmax(0,1fr) }
# .message { grid-template-columns: 94px minmax(0,1fr) }
# --------------------------------------------------------------------------

_ROLE_W = "94px"


def _chat_line(role: str, copy: str, note: str = "") -> rx.Component:
    return rx.hstack(
        rx.box(rx.text(role, class_name="mm-role"), class_name="mm-role-cell", width=_ROLE_W),
        rx.vstack(
            rx.text(copy, class_name="mm-copy"),
            rx.cond(note != "", rx.text(note, class_name="mm-copy-small")),
            spacing="1",
            align="start",
            class_name="mm-copy-cell",
            width="100%",
        ),
        align="start",
        class_name=rx.cond(role == "you", "mm-message mm-message-you", "mm-message"),
        width="100%",
    )


def shell_chat_first() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("MultiMind", class_name="mm-brand"),
            rx.spacer(),
            rx.text(HostState.active_music_display_name, class_name="mm-meta"),
            width="100%",
            align="center",
            class_name="mm-top",
        ),
        rx.hstack(
            # rail: the thread summary and the world switch
            rx.vstack(
                rx.text("THREAD", class_name="mm-label"),
                rx.text(HostState.active_music_signature, class_name="mm-thread-world"),
                _scene_switcher("worlds"),
                rx.box(_zone("_workspace_history_zone"), width="100%"),
                spacing="3",
                class_name="mm-rail",
                width="100%",
            ),
            # the conversation itself
            rx.vstack(
                rx.text(HostState.active_music_display_name, class_name="mm-eyebrow"),
                _chat_line("you", HostState.active_music_primary_action, "instruction sent"),
                _chat_line(
                    "multimind",
                    HostState.active_music_signature,
                    "result / correspondence preserved",
                ),
                _chat_line("you", rx.cond(HostState.active_music_composer_label != "", HostState.active_music_composer_label, "continue"), "instruction accepted"),
                _chat_line(
                    "multimind",
                    rx.cond(HostState.active_music_world != "", HostState.active_music_world, "world held"),
                    "state held",
                ),
                rx.spacer(),
                rx.text("reply-note", class_name="mm-reply-note"),
                spacing="4",
                class_name="mm-messages",
                width="100%",
            ),
            align="start",
            class_name="mm-chat",
            width="100%",
        ),
        rx.box(_zone("_workspace_result_zone"), width="100%"),
        _zone("_workspace_composer_zone"),
        spacing="0",
        width="100%",
        class_name="mm-shell mm-shell-chat-first",
    )


# --------------------------------------------------------------------------
# agent_canvas -- an open canvas with an absolutely positioned core, a wire
# network behind it, and an inspector strip pinned to the bottom.
#
# .core    { position:absolute; left:47%; top:31%; 160px circle }
# .inspect { position:absolute; left:7%; right:7%; bottom:7%; 120px 1fr auto }
# --------------------------------------------------------------------------


def shell_agent_canvas() -> rx.Component:
    return rx.box(
        # .top
        rx.hstack(
            rx.text("MultiMind", class_name="mm-brand"),
            rx.spacer(),
            rx.text(HostState.active_music_combination_id, class_name="mm-meta"),
            width="100%",
            align="center",
            class_name="mm-top",
        ),
        # .canvas -- the open field
        rx.box(
            rx.vstack(
                rx.text("AGENT CANVAS", class_name="mm-kicker"),
                rx.heading(rx.cond(HostState.active_music_world != "", HostState.active_music_world, "CANVAS"), class_name="mm-canvas-title"),
                spacing="2",
                align="start",
                class_name="mm-canvas-copy",
            ),
            # .net -- the three wires, then the core over them
            rx.box(class_name="mm-wire mm-wire-1", width="100%", height="2px"),
            rx.box(class_name="mm-wire mm-wire-2", width="100%", height="2px"),
            rx.box(class_name="mm-wire mm-wire-3", width="100%", height="2px"),
            rx.box(
                rx.vstack(
                    rx.text(HostState.active_music_scene_key.upper(), class_name="mm-core-key"),
                    rx.text(rx.cond(HostState.active_music_primary_object != "", HostState.active_music_primary_object, ""), class_name="mm-core-obj"),
                    spacing="1",
                    align="center",
                    class_name="mm-core-ui",
                ),
                _world_photo("mm-core"),
                class_name="mm-core",
            ),
            rx.spacer(),
            width="100%",
            class_name="mm-canvas",
        ),
        # .inspect -- the strip along the bottom
        rx.hstack(
            rx.box(rx.text("LAB", class_name="mm-label"), class_name="mm-inspect-lab", width="120px"),
            rx.vstack(
                rx.text(HostState.active_music_signature, class_name="mm-inspect-claim"),
                rx.cond(_has_scene(), _credit()),
                spacing="1",
                align="start",
                class_name="mm-inspect-claim-cell",
                width="100%",
            ),
            rx.box(
                rx.hstack(rx.text("REL", class_name="mm-label"), spacing="2", align="center"),
                class_name="mm-inspect-rel",
                width="100%",
            ),
            align="start",
            gap="5",
            class_name="mm-inspect",
            width="100%",
        ),
        _zone("_workspace_composer_zone"),
        class_name="mm-shell mm-shell-agent-canvas",
    )


# --------------------------------------------------------------------------
# command_center -- a four-row board: board-head, board, then a fixed lower
# band at 42svh.
#
# .app { grid-template-rows: auto auto 1fr minmax(280px,42svh) }
# --------------------------------------------------------------------------


def shell_command_center() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("MultiMind", class_name="mm-brand"),
            rx.spacer(),
            rx.text(HostState.active_music_display_name, class_name="mm-meta"),
            width="100%",
            align="center",
            class_name="mm-top",
        ),
        # .board-head
        rx.hstack(
            rx.text("BOARD", class_name="mm-label"),
            rx.spacer(),
            rx.text(rx.cond(HostState.active_music_primary_object != "", HostState.active_music_primary_object, ""), class_name="mm-board-object"),
            width="100%",
            align="end",
            class_name="mm-board-head",
        ),
        # .board -- the switcher and the photo share the row
        rx.hstack(
            rx.box(_zone("_workspace_result_zone"), class_name="mm-board-main", width="100%"),
            rx.vstack(
                rx.box(_world_photo("mm-board-photo"), class_name="mm-board-photo-wrap", width="100%"),
                rx.text(rx.cond(HostState.active_music_world != "", HostState.active_music_world, "WORLD"), class_name="mm-board-world"),
                _scene_switcher("buffers"),
                _credit(),
                spacing="3",
                class_name="mm-board-side",
                width="100%",
            ),
            align="start",
            gap="4",
            class_name="mm-board",
            width="100%",
        ),
        # the 42svh band: controls and composer
        rx.vstack(
            rx.box(_zone("_workspace_utility_zone"), width="100%"),
            _zone("_workspace_composer_zone"),
            spacing="3",
            class_name="mm-command-band",
            width="100%",
            min_height="42svh",
        ),
        _zone("_workspace_history_zone"),
        spacing="0",
        width="100%",
        class_name="mm-shell mm-shell-command-center",
    )


# --------------------------------------------------------------------------
# terminal_hacker -- a 29vw side with buffers, beside a scrolling screen.
#
# Mirrors public/preview/lab/music-v0/architecture-swap/
# re-juliet-terminal-v1.html exactly:
# .app   { grid-template-columns: minmax(220px,29vw) 1fr }
# .side  { grid-template-rows: auto auto 1fr auto }
# .term  { grid-template-rows: auto 1fr }
# --------------------------------------------------------------------------


def _terminal_buf_button(scene) -> rx.Component:
    """One A/B/C buffer button matching the preview's .buf markup."""
    return rx.button(
        rx.hstack(
            rx.box(class_name="mm-dot", width="7px", height="7px"),
            rx.text(scene["key"].upper(), class_name="mm-buffer-key"),
            rx.text(scene["name"], class_name="mm-buffer-name"),
            spacing="2",
            align="center",
            width="100%",
        ),
        on_click=HostState.set_music_scene(scene["key"]),
        variant="ghost",
        class_name=rx.cond(
            scene["key"] == HostState.active_music_scene_key,
            "mm-buffer mm-buffer-active",
            "mm-buffer",
        ),
        width="100%",
    )


def _terminal_static_buf(key: str, slug: str) -> rx.Component:
    """Fallback buffer when the track exposes no scenes (literal preview copy)."""
    return rx.button(
        rx.hstack(
            rx.box(class_name="mm-dot", width="7px", height="7px"),
            rx.text(key, class_name="mm-buffer-key"),
            rx.text(slug, class_name="mm-buffer-name"),
            spacing="2",
            align="center",
            width="100%",
        ),
        on_click=HostState.set_music_scene(key.lower()),
        variant="ghost",
        class_name=rx.cond(
            HostState.active_music_scene_key == key.lower(),
            "mm-buffer mm-buffer-active",
            "mm-buffer",
        ),
        width="100%",
    )


def _terminal_buffers() -> rx.Component:
    """The A/B/C world switcher with the preview's literal fallback copy."""
    return rx.box(
        rx.cond(
            HostState.active_music_scenes != [],
            rx.foreach(
                HostState.active_music_scenes,
                lambda scene: _terminal_buf_button(scene),
            ),
            rx.fragment(
                _terminal_static_buf("A", "rainy.window"),
                _terminal_static_buf("B", "warm.cafe"),
                _terminal_static_buf("C", "rain.city"),
            ),
        ),
        class_name="mm-buffers",
        width="100%",
    )


def _terminal_line(
    prompt: str,
    prompt_class: str,
    out: rx.Component,
    sys: rx.Component,
    line_class: str = "mm-line",
) -> rx.Component:
    """One transcript row: a 130px prompt cell beside the output body."""
    return rx.box(
        rx.box(
            rx.text(prompt, class_name=prompt_class),
            class_name="mm-prompt-cell",
            width="130px",
        ),
        rx.box(
            out,
            sys,
            class_name="mm-line-body",
            width="100%",
        ),
        class_name=line_class,
        width="100%",
    )


def shell_terminal_hacker() -> rx.Component:
    return rx.box(
        # .photo -- the selected scene photo, full-bleed behind the shell.
        rx.box(
            rx.cond(
                HostState.active_music_scene_photo != "",
                rx.image(
                    src=HostState.active_music_scene_photo,
                    alt=rx.cond(
                        HostState.active_music_display_name != "",
                        HostState.active_music_display_name,
                        "JULIET RE EDIT",
                    ),
                    width="100%",
                    height="100%",
                    object_fit="cover",
                    object_position=rx.cond(
                        HostState.active_music_scene_position != "",
                        HostState.active_music_scene_position,
                        "center",
                    ),
                    class_name="mm-photo-img mm-world-photo-img",
                ),
            ),
            rx.box(class_name="mm-photo-shade"),
            class_name="mm-photo mm-world-photo",
        ),
        # .side
        rx.box(
            rx.text("MULTIMIND / ARCHETYPE SWAP 01", class_name="mm-brand"),
            rx.box(
                rx.text("TERMINAL / HACKER \u00d7 MUSIC DNA", class_name="mm-kicker"),
                rx.heading(
                    rx.cond(
                        HostState.active_music_display_name != "",
                        HostState.active_music_display_name,
                        "JULIET RE EDIT",
                    ),
                    class_name="mm-song-title",
                ),
                rx.text(
                    "Same session, same memories, same three emotional worlds. "
                    "The mental model changes: issue instructions, inspect output, "
                    "keep the correspondence alive.",
                    class_name="mm-song-desc",
                ),
                class_name="mm-song",
                width="100%",
            ),
            # .buffers
            _terminal_buffers(),
            rx.box(
                rx.text(
                    "archetype invariant / issue instruction \u2192 observe execution",
                    class_name="mm-foot",
                ),
                rx.text(
                    "music invariant / romantic correspondence \u00b7 warm melancholy \u00b7 A/B/C worlds",
                    class_name="mm-foot",
                ),
                class_name="mm-foot-wrap",
                width="100%",
            ),
            class_name="mm-side",
            width="100%",
        ),
        # .term
        rx.box(
            rx.box(
                rx.text(
                    "session / ",
                    rx.text(
                        rx.cond(
                            HostState.active_music_combination_id != "",
                            HostState.active_music_combination_id,
                            "REJULIET-04",
                        ),
                        class_name="mm-top-b",
                    ),
                    class_name="mm-top-line",
                ),
                rx.spacer(),
                rx.text(
                    "model / ",
                    rx.text("GPT-5.6 SOL", class_name="mm-top-b"),
                    " \u00b7 memory / ",
                    rx.text("ON", class_name="mm-top-b"),
                    class_name="mm-top-line",
                ),
                width="100%",
                align="center",
                class_name="mm-term-top",
            ),
            # .screen
            rx.box(
                rx.box(
                    rx.text(
                        "multimind@juliet:~$ session attach ",
                        rx.text(
                            rx.cond(
                                HostState.active_music_combination_id != "",
                                HostState.active_music_combination_id,
                                "REJULIET-04",
                            ),
                            class_name="mm-boot-b",
                        ),
                        class_name="mm-boot-line",
                    ),
                    rx.text(
                        rx.text("[ok]", class_name="mm-ok"),
                        " memory restored \u00b7 correspondence preserved \u00b7 world buffer ",
                        rx.text(
                            rx.cond(
                                HostState.active_music_scene_key != "",
                                HostState.active_music_scene_key.upper(),
                                "A",
                            ),
                            class_name="mm-rose",
                        ),
                        " mounted",
                        class_name="mm-boot-line",
                    ),
                    class_name="mm-boot",
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        rx.text("ACTIVE BUFFER", class_name="mm-label"),
                        class_name="mm-head-label",
                        width="130px",
                    ),
                    rx.box(
                        rx.heading(
                            rx.cond(
                                HostState.active_music_scene_name != "",
                                HostState.active_music_scene_name,
                                "Rainy Window",
                            ),
                            class_name="mm-term-name",
                        ),
                        rx.text(
                            rx.cond(
                                HostState.active_music_scene_thesis != "",
                                HostState.active_music_scene_thesis,
                                "Patah hati yang dekat dan lembut: hujan di kaca memberi jarak, "
                                "lampu kota masih hidup, dan versi band terasa hangat alih-alih dingin.",
                            ),
                            class_name="mm-term-thesis",
                        ),
                        class_name="mm-head-body",
                        width="100%",
                    ),
                    class_name="mm-head",
                    width="100%",
                ),
                _terminal_line(
                    "you@juliet:~$",
                    "mm-prompt mm-prompt-user",
                    rx.text(
                        rx.cond(
                            HostState.active_music_primary_action != "",
                            HostState.active_music_primary_action,
                            "compare --models long-context --keep-world",
                        ),
                        class_name="mm-out",
                    ),
                    rx.text(
                        "instruction accepted \u00b7 buffer ",
                        rx.text(
                            rx.cond(
                                HostState.active_music_scene_key != "",
                                HostState.active_music_scene_key.upper(),
                                "A",
                            ),
                            class_name="mm-rose",
                        ),
                        class_name="mm-sys",
                    ),
                ),
                _terminal_line(
                    "multimind>",
                    "mm-prompt mm-prompt-ai",
                    rx.text(
                        rx.cond(
                            HostState.active_music_signature != "",
                            HostState.active_music_signature,
                            "Untuk kerja panjang, pilih model yang paling stabil. Model kedua tetap "
                            "fallback; identitas model tidak boleh dipalsukan, dan world JULIET "
                            "tidak ikut hilang ketika rute berpindah.",
                        ),
                        class_name="mm-out mm-out-ai",
                    ),
                    rx.text(
                        "result / correspondence preserved",
                        class_name="mm-sys",
                    ),
                    line_class="mm-line mm-line-ai",
                ),
                _terminal_line(
                    "you@juliet:~$",
                    "mm-prompt mm-prompt-user",
                    rx.text(
                        rx.cond(
                            HostState.active_music_composer_label != "",
                            HostState.active_music_composer_label,
                            "fallback --provider auto --preserve session",
                        ),
                        class_name="mm-out",
                    ),
                    rx.text(
                        "instruction accepted \u00b7 no state reset",
                        class_name="mm-sys",
                    ),
                ),
                _terminal_line(
                    "multimind>",
                    "mm-prompt mm-prompt-ai",
                    rx.text(
                        rx.cond(
                            HostState.active_music_primary_object != "",
                            HostState.active_music_primary_object,
                            "Fallback boleh terjadi tanpa memutus hubungan antar-pesan. Yang berpindah "
                            "adalah kendaraan. Keputusan, konteks penting, dan nada percakapan tetap dibawa.",
                        ),
                        class_name="mm-out mm-out-ai",
                    ),
                    rx.text(
                        "result / state held \u00b7 world ",
                        rx.text(
                            rx.cond(
                                HostState.active_music_scene_key != "",
                                HostState.active_music_scene_key.upper(),
                                "A",
                            ),
                            class_name="mm-rose",
                        ),
                        class_name="mm-sys",
                    ),
                    line_class="mm-line mm-line-ai",
                ),
                rx.box(_zone("_workspace_result_zone"), width="100%"),
                width="100%",
                class_name="mm-screen",
            ),
            rx.box(_zone("_workspace_history_zone"), width="100%"),
            rx.box(_zone("_workspace_composer_zone"), width="100%"),
            rx.box(_zone("_workspace_utility_zone"), width="100%"),
            class_name="mm-term",
            width="100%",
        ),
        # .credit -- provenance of the visible scene.
        rx.text(
            rx.cond(
                HostState.active_music_scene_credit != "",
                HostState.active_music_scene_credit,
                "PHOTO \u00b7 RAINY WINDOW \u00b7 UNSPLASH LICENSE",
            ),
            class_name="mm-credit",
        ),
        width="100%",
        class_name="mm-shell mm-shell-terminal-hacker",
    )


SHELLS = {
    "minimal_saas": None,  # the living two-pane world rail stays where it is
    "ai_research_lab": shell_ai_research_lab,
    "ai_workspace": shell_ai_workspace,
    "chat_first": shell_chat_first,
    "agent_canvas": shell_agent_canvas,
    "command_center": shell_command_center,
    "terminal_hacker": shell_terminal_hacker,
}