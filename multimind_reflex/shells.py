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


# --------------------------------------------------------------------------
# Shared pieces: photo plates, live scene slots, the A/B/C switchers.
#
# Every preview binds the same way: static chrome is the file's literal copy
# and the live slots read HostState with the preview string as the fallback,
# exactly like shell_terminal_hacker does.
# --------------------------------------------------------------------------

_THESIS_A = (
    "Patah hati yang dekat dan lembut: hujan di kaca memberi jarak, "
    "lampu kota masih hidup, dan versi band terasa hangat alih-alih dingin."
)


def _live_scene_name(fallback: str = "Rainy Window"):
    """The selected scene's name, or the preview's literal scene."""
    return rx.cond(
        HostState.active_music_scene_name != "",
        HostState.active_music_scene_name,
        fallback,
    )


def _live_scene_thesis(fallback: str = _THESIS_A):
    """The selected scene's thesis, or the preview's Indonesian copy."""
    return rx.cond(
        HostState.active_music_scene_thesis != "",
        HostState.active_music_scene_thesis,
        fallback,
    )


def _live_scene_credit(fallback: str):
    """The visible scene's provenance line."""
    return rx.cond(
        HostState.active_music_scene_credit != "",
        HostState.active_music_scene_credit,
        fallback,
    )


def _live_combination(fallback: str = "REJULIET-04"):
    """The session combination id, or the preview's literal session."""
    return rx.cond(
        HostState.active_music_combination_id != "",
        HostState.active_music_combination_id,
        fallback,
    )


def _photo_box(
    extra_class: str,
    fallback_src: str,
    fallback_position: str = "center",
) -> rx.Component:
    """The selected scene photo with the preview's literal fallback plate."""
    return rx.box(
        rx.image(
            src=rx.cond(
                HostState.active_music_scene_photo != "",
                HostState.active_music_scene_photo,
                fallback_src,
            ),
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
                fallback_position,
            ),
            class_name="mm-photo-img mm-world-photo-img",
        ),
        rx.box(class_name="mm-photo-shade"),
        class_name="mm-photo mm-world-photo " + extra_class,
        width="100%",
    )


def _top_bar(brand: str, lead: str) -> rx.Component:
    """The preview .top: the brand left, the track lead plus live meta right."""
    return rx.hstack(
        rx.text(brand, class_name="mm-brand"),
        rx.spacer(),
        rx.vstack(
            rx.text(lead, class_name="mm-meta-lead"),
            rx.text(
                "SESSION / ",
                rx.text(_live_combination(), class_name="mm-meta-b"),
                " \u00b7 MODEL / ",
                rx.text("GPT-5.6 SOL", class_name="mm-meta-b"),
                " \u00b7 MEMORY / ",
                rx.text("ON", class_name="mm-meta-b"),
                class_name="mm-meta",
            ),
            align="end",
            spacing="1",
        ),
        width="100%",
        align="center",
        class_name="mm-top",
    )


def _title(
    fallback: str = "JULIET\nRE EDIT",
    class_name: str = "mm-world-title",
) -> rx.Component:
    """The track title: live display name over the preview's literal title."""
    return rx.heading(
        rx.cond(
            HostState.active_music_display_name != "",
            HostState.active_music_display_name,
            fallback,
        ),
        white_space="pre-line",
        class_name=class_name,
    )


def _zone(name: str):
    """Fetch a zone component lazily.

    multimind_reflex.py imports this module, so importing it back at module
    scope would be circular. Importing the zone on first use keeps the shells
    reusing the exact same zone components without that cycle.
    """
    import multimind_reflex.multimind_reflex as host

    return getattr(host, name)()


# --------------------------------------------------------------------------
# ai_research_lab -- three columns, left tabs, centre viewport, right evidence.
#
# Mirrors re-juliet-research-lab-v1.html:
# .lab { grid-template-columns: minmax(190px,.78fr) minmax(0,1.7fr) minmax(220px,.9fr) }
# --------------------------------------------------------------------------


def _lab_live_tab(scene) -> rx.Component:
    """One evidence-set tab: the dot, the key, and the world slug."""
    return rx.button(
        rx.box(class_name="mm-dot", width="7px", height="7px"),
        rx.text(scene["key"].upper(), class_name="mm-tab-strong"),
        rx.text(scene["name"], class_name="mm-tab-slug"),
        on_click=HostState.set_music_scene(scene["key"]),
        variant="ghost",
        class_name=rx.cond(
            scene["key"] == HostState.active_music_scene_key,
            "mm-tab mm-buffer mm-tab-active",
            "mm-tab mm-buffer",
        ),
        width="100%",
    )


def _lab_static_tab(key: str, slug: str) -> rx.Component:
    """Fallback tab when the track exposes no scenes (literal preview copy)."""
    return rx.button(
        rx.box(class_name="mm-dot", width="7px", height="7px"),
        rx.text(key, class_name="mm-tab-strong"),
        rx.text(slug, class_name="mm-tab-slug"),
        on_click=HostState.set_music_scene(key.lower()),
        variant="ghost",
        class_name=rx.cond(
            HostState.active_music_scene_key == key.lower(),
            "mm-tab mm-buffer mm-tab-active",
            "mm-tab mm-buffer",
        ),
        width="100%",
    )


def _lab_tabs() -> rx.Component:
    """The evidence-set / world-buffers switcher."""
    return rx.box(
        rx.cond(
            HostState.active_music_scenes != [],
            rx.foreach(HostState.active_music_scenes, _lab_live_tab),
            rx.fragment(
                _lab_static_tab("A", "rainy.window"),
                _lab_static_tab("B", "warm.cafe"),
                _lab_static_tab("C", "rain.city"),
            ),
        ),
        class_name="mm-tabs",
        width="100%",
    )


def shell_ai_research_lab() -> rx.Component:
    return rx.vstack(
        _top_bar(
            "MULTIMIND / ARCHETYPE SWAP 03",
            "RESEARCH LAB \u00d7 MUSIC DNA",
        ),
        # .intro -- the eyebrow band above the lab
        rx.box(
            rx.box(
                rx.text(
                    "investigate evidence \u00b7 build a conclusion",
                    class_name="mm-eyebrow",
                ),
                _title(),
                class_name="mm-intro-copy",
                width="100%",
            ),
            rx.text(
                "Same correspondence, same three emotional worlds. This time "
                "the work is not arranged as a hero image or a chat column: "
                "the world itself sits in the middle as evidence to inspect.",
                class_name="mm-intro-side",
            ),
            class_name="mm-intro",
            width="100%",
        ),
        rx.box(
            rx.hstack(
                # left: the world tabs plus the working hypothesis
                rx.vstack(
                    rx.text(
                        "evidence set / world buffers",
                        class_name="mm-tag",
                    ),
                    _lab_tabs(),
                    rx.box(
                        rx.text(
                            "working hypothesis",
                            class_name="mm-note-label",
                        ),
                        rx.text(
                            "Jarak terasa lembut, bukan dingin. Hujan "
                            "berfungsi sebagai batas tipis antara dua orang "
                            "yang masih saling terbaca.",
                            class_name="mm-claim",
                        ),
                        class_name="mm-claim-box",
                        width="100%",
                    ),
                    rx.box(
                        _zone("_workspace_utility_zone"),
                        width="100%",
                    ),
                    spacing="3",
                    class_name="mm-lab-left",
                    width="100%",
                ),
                # centre: the viewport, which is where the photo lives
                rx.vstack(
                    rx.box(
                        _photo_box(
                            "mm-viewport-photo",
                            "/scenes/rainy_window.webp",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "primary evidence viewport",
                                    class_name="mm-tag mm-tag-light",
                                ),
                                rx.spacer(),
                                rx.text(
                                    "inspect / compare / annotate",
                                    class_name="mm-view-state",
                                ),
                                width="100%",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.box(
                                rx.heading(
                                    _live_scene_name(),
                                    class_name="mm-view-name",
                                ),
                                rx.text(
                                    _live_scene_thesis(),
                                    class_name="mm-view-thesis",
                                ),
                                rx.text(
                                    _live_scene_credit(
                                        "PHOTO \u00b7 RAINY WINDOW "
                                        "\u00b7 UNSPLASH LICENSE",
                                    ),
                                    class_name="mm-caption",
                                ),
                                class_name="mm-view-copy",
                                width="100%",
                            ),
                            align="stretch",
                            spacing="2",
                            class_name="mm-view-ui",
                            width="100%",
                            height="100%",
                        ),
                        class_name="mm-viewport-wrap",
                        width="100%",
                    ),
                    _zone("_workspace_result_zone"),
                    spacing="4",
                    class_name="mm-lab-viewport",
                    width="100%",
                ),
                # right: the observations and the provisional synthesis
                rx.vstack(
                    rx.text(
                        "observations / current buffer",
                        class_name="mm-tag",
                    ),
                    rx.heading(
                        "What survives the swap?",
                        class_name="mm-right-title",
                    ),
                    rx.box(
                        rx.box(
                            rx.text(
                                "emotional signal",
                                class_name="mm-ev-key",
                            ),
                            rx.text(
                                "Warm melancholy; distance without emotional "
                                "erasure.",
                                class_name="mm-evidence",
                            ),
                            class_name="mm-evidence-row",
                            width="100%",
                        ),
                        rx.box(
                            rx.text(
                                "conversation invariant",
                                class_name="mm-ev-key",
                            ),
                            rx.text(
                                "Same session, same memory, same "
                                "correspondence. Only the projection changes.",
                                class_name="mm-evidence",
                            ),
                            class_name="mm-evidence-row",
                            width="100%",
                        ),
                        rx.box(
                            rx.text(
                                "archetype invariant",
                                class_name="mm-ev-key",
                            ),
                            rx.text(
                                "Inspect evidence, compare interpretations, "
                                "then form a conclusion.",
                                class_name="mm-evidence",
                            ),
                            class_name="mm-evidence-row",
                            width="100%",
                        ),
                        class_name="mm-evidence-list",
                        width="100%",
                    ),
                    rx.box(
                        rx.text(
                            "provisional synthesis",
                            class_name="mm-synth-label",
                        ),
                        rx.text(
                            "Keep the rain visible. The interface should feel "
                            "like evidence from a relationship, not a "
                            "laboratory skin pasted over a song.",
                            class_name="mm-synth",
                        ),
                        class_name="mm-synthesis",
                        width="100%",
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
# Mirrors re-juliet-ai-workspace-v1.html:
# .workspace { grid-template-columns: 190px minmax(0,1fr) clamp(300px,26vw,360px) }
# .desk      { grid-template-columns: 1fr 1fr }  with .wide spanning both
# --------------------------------------------------------------------------


def _shelf_live_button(scene) -> rx.Component:
    """One shelf world button: the key plus the scene name."""
    return rx.button(
        rx.text(scene["key"].upper(), class_name="mm-wb-key"),
        rx.text(scene["name"], class_name="mm-wb-name"),
        on_click=HostState.set_music_scene(scene["key"]),
        variant="ghost",
        class_name=rx.cond(
            scene["key"] == HostState.active_music_scene_key,
            "mm-wb mm-buffer mm-wb-active",
            "mm-wb mm-buffer",
        ),
        width="100%",
    )


def _shelf_static_button(key: str, name: str) -> rx.Component:
    """Fallback shelf button (literal preview copy)."""
    return rx.button(
        rx.text(key, class_name="mm-wb-key"),
        rx.text(name, class_name="mm-wb-name"),
        on_click=HostState.set_music_scene(key.lower()),
        variant="ghost",
        class_name=rx.cond(
            HostState.active_music_scene_key == key.lower(),
            "mm-wb mm-buffer mm-wb-active",
            "mm-wb mm-buffer",
        ),
        width="100%",
    )


def _shelf_worlds() -> rx.Component:
    """The shelf's world switcher."""
    return rx.box(
        rx.cond(
            HostState.active_music_scenes != [],
            rx.foreach(HostState.active_music_scenes, _shelf_live_button),
            rx.fragment(
                _shelf_static_button("A", "Rainy Window"),
                _shelf_static_button("B", "Warm Cafe"),
                _shelf_static_button("C", "Rain City"),
            ),
        ),
        class_name="mm-world-buttons",
        width="100%",
    )


def shell_ai_workspace() -> rx.Component:
    return rx.vstack(
        _top_bar(
            "MULTIMIND / ARCHETYPE SWAP 06",
            "AI WORKSPACE \u00d7 MUSIC DNA",
        ),
        rx.hstack(
            # shelf: the world switcher
            rx.vstack(
                rx.text("workspace object / world", class_name="mm-label"),
                _title(),
                _shelf_worlds(),
                rx.box(_zone("_workspace_utility_zone"), width="100%"),
                spacing="3",
                class_name="mm-shelf",
                width="100%",
            ),
            # desk: the two-up object board
            rx.vstack(
                rx.box(
                    rx.text(
                        "active multi-object desk",
                        class_name="mm-label",
                    ),
                    rx.heading(
                        "One session.\nSeveral working objects.",
                        white_space="pre-line",
                        class_name="mm-desk-title",
                    ),
                    rx.text(
                        "representation changes / state held",
                        class_name="mm-chip",
                    ),
                    class_name="mm-desk-head",
                    width="100%",
                ),
                rx.box(
                    rx.hstack(
                        rx.text(
                            "Object 01 / conversation",
                            class_name="mm-obj-meta",
                        ),
                        rx.spacer(),
                        rx.text("attached", class_name="mm-chip"),
                        width="100%",
                        align="center",
                    ),
                    rx.heading("The thread", class_name="mm-object-title"),
                    rx.box(
                        rx.text("you", class_name="mm-thread-role"),
                        rx.text(
                            "\u201cKeep the feeling, but compare another "
                            "route.\u201d",
                            class_name="mm-thread-copy",
                        ),
                        class_name="mm-thread",
                        width="100%",
                    ),
                    rx.box(
                        rx.text("assistant", class_name="mm-thread-role"),
                        rx.text(
                            "\u201cI can change the working surface without "
                            "resetting what this correspondence already "
                            "knows.\u201d",
                            class_name="mm-thread-copy",
                        ),
                        class_name="mm-thread",
                        width="100%",
                    ),
                    class_name="mm-object",
                    width="100%",
                ),
                rx.box(
                    rx.hstack(
                        rx.text(
                            "Object 02 / memory",
                            class_name="mm-obj-meta",
                        ),
                        rx.spacer(),
                        rx.text("3 anchors", class_name="mm-chip"),
                        width="100%",
                        align="center",
                    ),
                    rx.heading(
                        "What must survive",
                        class_name="mm-object-title",
                    ),
                    rx.text(
                        "Warm melancholy, not cold sadness.",
                        class_name="mm-memory-line",
                    ),
                    rx.text(
                        "A / B / C remain bound worlds, not generic themes.",
                        class_name="mm-memory-line",
                    ),
                    rx.text(
                        "Model identity stays truthful across fallback.",
                        class_name="mm-memory-line",
                    ),
                    class_name="mm-object",
                    width="100%",
                ),
                rx.box(
                    rx.hstack(
                        rx.text(
                            "Object 03 / model compare",
                            class_name="mm-obj-meta",
                        ),
                        rx.spacer(),
                        rx.text("workspace view", class_name="mm-chip"),
                        width="100%",
                        align="center",
                    ),
                    rx.heading(
                        "Compare without leaving the room.",
                        class_name="mm-object-title",
                    ),
                    rx.text(
                        "The archetype is now about manipulating several "
                        "persistent objects at once: conversation, memory, "
                        "model result, files, and world state. The song is "
                        "not reduced to a decorative skin; it determines how "
                        "those objects feel and relate.",
                        class_name="mm-object-copy",
                    ),
                    class_name="mm-object wide",
                    width="100%",
                ),
                rx.box(
                    _zone("_workspace_result_zone"),
                    class_name="mm-object wide",
                    width="100%",
                ),
                rx.box(
                    _zone("_workspace_history_zone"),
                    class_name="mm-object wide",
                    width="100%",
                ),
                spacing="3",
                class_name="mm-desk",
                width="100%",
            ),
            # worldpanel: the photo and its copy
            rx.vstack(
                rx.box(
                    _photo_box(
                        "mm-worldpanel-photo",
                        "/scenes/rainy_window.webp",
                        "center 58%",
                    ),
                    rx.box(
                        rx.text(
                            "ambient world object / right edge field",
                            class_name="mm-label mm-label-light",
                        ),
                        rx.heading(
                            _live_scene_name(),
                            class_name="mm-worldpanel-name",
                        ),
                        rx.text(
                            _live_scene_thesis(),
                            class_name="mm-worldpanel-thesis",
                        ),
                        class_name="mm-world-copy",
                        width="100%",
                    ),
                    rx.text(
                        _live_scene_credit(
                            "PHOTO \u00b7 RAINY LIGHTS \u00b7 DEFI22 "
                            "\u00b7 WIKIMEDIA COMMONS \u00b7 CC BY-SA 4.0",
                        ),
                        class_name="mm-credit",
                    ),
                    class_name="mm-worldpanel-photo-wrap",
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
# chat_first -- a 255px rail beside the thread; the world lives behind it.
#
# Mirrors re-juliet-chat-first-v1.html:
# .chat { grid-template-columns: 255px minmax(0,1fr) }
# .message { grid-template-columns: 94px minmax(0,1fr) }
# --------------------------------------------------------------------------


def _chat_worlds_live_button(scene) -> rx.Component:
    """One world button over the thread: the key plus the scene name."""
    return rx.button(
        rx.text(scene["key"].upper(), class_name="mm-worlds-key"),
        rx.text(scene["name"], class_name="mm-worlds-name"),
        on_click=HostState.set_music_scene(scene["key"]),
        variant="ghost",
        class_name=rx.cond(
            scene["key"] == HostState.active_music_scene_key,
            "mm-world-btn mm-buffer mm-worlds-active",
            "mm-world-btn mm-buffer",
        ),
        width="100%",
    )


def _chat_worlds_static_button(key: str, name: str) -> rx.Component:
    """Fallback world button (literal preview copy)."""
    return rx.button(
        rx.text(key, class_name="mm-worlds-key"),
        rx.text(name, class_name="mm-worlds-name"),
        on_click=HostState.set_music_scene(key.lower()),
        variant="ghost",
        class_name=rx.cond(
            HostState.active_music_scene_key == key.lower(),
            "mm-world-btn mm-buffer mm-worlds-active",
            "mm-world-btn mm-buffer",
        ),
        width="100%",
    )


def _chat_worlds() -> rx.Component:
    """The world switcher pinned over the thread."""
    return rx.box(
        rx.cond(
            HostState.active_music_scenes != [],
            rx.foreach(
                HostState.active_music_scenes,
                _chat_worlds_live_button,
            ),
            rx.fragment(
                _chat_worlds_static_button("A", "Rainy Window"),
                _chat_worlds_static_button("B", "Warm Cafe"),
                _chat_worlds_static_button("C", "Rain City"),
            ),
        ),
        class_name="mm-worlds",
        width="100%",
    )


def _chat_message(role: str, copy: str, copy_class: str) -> rx.Component:
    """One correspondence row: the role gutter beside the copy."""
    return rx.box(
        rx.text(role, class_name="mm-role"),
        rx.text(copy, class_name=copy_class),
        class_name="mm-message",
        width="100%",
    )


def shell_chat_first() -> rx.Component:
    return rx.vstack(
        _top_bar(
            "MULTIMIND / ARCHETYPE SWAP 07",
            "CHAT-FIRST \u00d7 MUSIC DNA",
        ),
        rx.hstack(
            # rail: the conversation identity and the thread history
            rx.vstack(
                rx.text("conversation identity", class_name="mm-label"),
                _title(),
                rx.text(
                    "The architecture finally returns to the simplest mental "
                    "model: I converse. No dashboard, no canvas, no terminal. "
                    "The thread itself is the primary object.",
                    class_name="mm-rail-copy",
                ),
                rx.box(
                    rx.text("session held", class_name="mm-truth"),
                    rx.text("world bound", class_name="mm-truth"),
                    rx.text(
                        "model identity truthful",
                        class_name="mm-truth",
                    ),
                    class_name="mm-truth-box",
                    width="100%",
                ),
                rx.box(_zone("_workspace_history_zone"), width="100%"),
                spacing="3",
                class_name="mm-rail",
                width="100%",
            ),
            # the conversation itself, with the world behind it
            rx.vstack(
                rx.box(
                    rx.text(
                        "conversation / correspondence / one continuous thread",
                        class_name="mm-eyebrow",
                    ),
                    rx.heading(
                        "Stay in the thread.",
                        class_name="mm-thread-title",
                    ),
                    rx.text(
                        "Chat-first does not mean generic bubbles. Re:Juliet "
                        "treats conversation as correspondence: restrained, "
                        "intimate, and continuous, while the world lives "
                        "behind the thread instead of being forced into a "
                        "hero block.",
                        class_name="mm-thread-lede",
                    ),
                    class_name="mm-thread-head",
                    width="100%",
                ),
                rx.box(
                    _photo_box(
                        "mm-thread-world-photo",
                        "/scenes/rainy_window.webp",
                        "center 58%",
                    ),
                    rx.box(
                        rx.box(
                            rx.text(
                                "world / behind the correspondence",
                                class_name="mm-label mm-label-light",
                            ),
                            rx.heading(
                                _live_scene_name(),
                                class_name="mm-world-name",
                            ),
                            class_name="mm-world-title-copy",
                            width="100%",
                        ),
                        rx.text(
                            _live_scene_thesis(),
                            class_name="mm-world-thesis",
                        ),
                        class_name="mm-world-title",
                        width="100%",
                    ),
                    rx.box(
                        _chat_message(
                            "YOU / 21:07",
                            "\u201cIf we compare another model, keep the "
                            "same feeling. Don\u2019t reset the room.\u201d",
                            "mm-copy",
                        ),
                        _chat_message(
                            "SOL / 21:07",
                            "I\u2019ll keep the session, memory, and the "
                            "emotional world intact. The model may change "
                            "later; the correspondence does not have to "
                            "start over.",
                            "mm-copy small",
                        ),
                        _chat_message(
                            "SOL / NOW",
                            "\u201cSame thread. Different view. Nothing "
                            "important was discarded.\u201d",
                            "mm-copy",
                        ),
                        class_name="mm-messages",
                        width="100%",
                    ),
                    _chat_worlds(),
                    rx.text(
                        _live_scene_credit(
                            "PHOTO \u00b7 RAINY LIGHTS \u00b7 DEFI22 "
                            "\u00b7 WIKIMEDIA COMMONS \u00b7 CC BY-SA 4.0",
                        ),
                        class_name="mm-credit",
                    ),
                    class_name="mm-thread-world",
                    width="100%",
                ),
                rx.text(
                    "CHAT-FIRST invariant: the next action is always another "
                    "turn in the conversation. World selection changes the "
                    "atmosphere attached to the thread, not the identity of "
                    "the session.",
                    class_name="mm-reply-note",
                ),
                rx.box(_zone("_workspace_result_zone"), width="100%"),
                spacing="4",
                class_name="mm-thread",
                width="100%",
            ),
            align="start",
            class_name="mm-chat",
            width="100%",
        ),
        _zone("_workspace_composer_zone"),
        spacing="0",
        width="100%",
        class_name="mm-shell mm-shell-chat-first",
    )


# --------------------------------------------------------------------------
# agent_canvas -- an open canvas with a session core, three world nodes on
# wires, and an inspector strip pinned to the bottom.
#
# Mirrors re-juliet-agent-canvas-v1.html:
# .core    { position:absolute; left:47%; top:31%; 160px circle }
# .inspect { position:absolute; left:7%; right:7%; bottom:7%; 120px 1fr auto }
# --------------------------------------------------------------------------


def _canvas_live_node(scene) -> rx.Component:
    """One world entity on the wires, with its own scene photo."""
    key = scene["key"]
    return rx.button(
        rx.box(
            rx.image(
                src=rx.cond(
                    scene["photo_url"] != "",
                    scene["photo_url"],
                    rx.cond(
                        key == "b",
                        "/scenes/warm_cafe.webp",
                        rx.cond(
                            key == "c",
                            "/scenes/city_lights.webp",
                            "/scenes/rainy_window.webp",
                        ),
                    ),
                ),
                alt=scene["name"],
                width="100%",
                height="100%",
                object_fit="cover",
                object_position=rx.cond(
                    scene["position"] != "",
                    scene["position"],
                    "center",
                ),
                class_name="mm-photo-img mm-world-photo-img",
            ),
            rx.box(class_name="mm-photo-shade"),
            class_name="mm-node-photo mm-world-photo",
            width="100%",
            height="100%",
        ),
        rx.box(
            rx.text(
                key.upper(),
                " / world entity",
                class_name="mm-node-id",
            ),
            rx.text(scene["name"], class_name="mm-node-name"),
            class_name="mm-node-cap",
            width="100%",
        ),
        on_click=HostState.set_music_scene(key),
        variant="ghost",
        class_name=rx.cond(
            key == HostState.active_music_scene_key,
            rx.cond(
                key == "a",
                "mm-node mm-buffer mm-node-a mm-node-active",
                rx.cond(
                    key == "b",
                    "mm-node mm-buffer mm-node-b mm-node-active",
                    "mm-node mm-buffer mm-node-c mm-node-active",
                ),
            ),
            rx.cond(
                key == "a",
                "mm-node mm-buffer mm-node-a",
                rx.cond(
                    key == "b",
                    "mm-node mm-buffer mm-node-b",
                    "mm-node mm-buffer mm-node-c",
                ),
            ),
        ),
    )


def _canvas_static_node(node: str, name: str, src: str) -> rx.Component:
    """Fallback world entity (literal preview copy with the local plate)."""
    return rx.button(
        rx.box(
            rx.image(
                src=src,
                alt=name,
                width="100%",
                height="100%",
                object_fit="cover",
                class_name="mm-photo-img mm-world-photo-img",
            ),
            rx.box(class_name="mm-photo-shade"),
            class_name="mm-node-photo mm-world-photo",
            width="100%",
            height="100%",
        ),
        rx.box(
            rx.text(
                node,
                " / world entity",
                class_name="mm-node-id",
            ),
            rx.text(name, class_name="mm-node-name"),
            class_name="mm-node-cap",
            width="100%",
        ),
        on_click=HostState.set_music_scene(node.lower()),
        variant="ghost",
        class_name=rx.cond(
            HostState.active_music_scene_key == node.lower(),
            "mm-node mm-buffer mm-node-%s mm-node-active" % node.lower(),
            "mm-node mm-buffer mm-node-%s" % node.lower(),
        ),
    )


def _canvas_nodes() -> rx.Component:
    """The three world entities on the wires."""
    return rx.box(
        rx.cond(
            HostState.active_music_scenes != [],
            rx.foreach(HostState.active_music_scenes, _canvas_live_node),
            rx.fragment(
                _canvas_static_node(
                    "A",
                    "Rainy Window",
                    "/scenes/rainy_window.webp",
                ),
                _canvas_static_node(
                    "B",
                    "Warm Cafe",
                    "/scenes/warm_cafe.webp",
                ),
                _canvas_static_node(
                    "C",
                    "Rain City",
                    "/scenes/city_lights.webp",
                ),
            ),
        ),
        class_name="mm-net",
        width="100%",
    )


def shell_agent_canvas() -> rx.Component:
    return rx.box(
        # .top
        _top_bar(
            "MULTIMIND / ARCHETYPE SWAP 04",
            "AGENT CANVAS \u00d7 MUSIC DNA",
        ),
        # .canvas -- the open field
        rx.box(
            rx.box(
                rx.text(
                    "entities \u00b7 relationships \u00b7 emotional worlds",
                    class_name="mm-kicker",
                ),
                _title(class_name="mm-canvas-title"),
                rx.text(
                    "The correspondence is no longer a column. It becomes a "
                    "small relationship field: one session core, three "
                    "emotional worlds, and links that stay alive while the "
                    "active world changes.",
                    class_name="mm-canvas-lede",
                ),
                class_name="mm-canvas-copy",
            ),
            rx.box(class_name="mm-wire mm-wire-1", width="100%"),
            rx.box(class_name="mm-wire mm-wire-2", width="100%"),
            rx.box(class_name="mm-wire mm-wire-3", width="100%"),
            _canvas_nodes(),
            rx.box(
                rx.text("SESSION CORE", class_name="mm-core-title"),
                rx.text(
                    "memory held",
                    class_name="mm-core-sub",
                ),
                rx.text(
                    "identity truthful",
                    class_name="mm-core-sub",
                ),
                class_name="mm-core",
            ),
            # .inspect -- the strip along the bottom
            rx.box(
                rx.text("selected entity", class_name="mm-inspect-lab"),
                rx.box(
                    rx.heading(
                        _live_scene_name(),
                        class_name="mm-inspect-name",
                    ),
                    rx.text(
                        _live_scene_thesis(),
                        class_name="mm-inspect-thesis",
                    ),
                    class_name="mm-inspect-claim-cell",
                    width="100%",
                ),
                rx.text(
                    "RELATION / correspondence \u2192 session core",
                    class_name="mm-inspect-rel",
                ),
                rx.text(
                    "STATE / active \u00b7 preserved",
                    class_name="mm-inspect-rel",
                ),
                class_name="mm-inspect",
                width="100%",
            ),
            rx.text(
                _live_scene_credit(
                    "PHOTO \u00b7 RAINY WINDOW \u00b7 UNSPLASH LICENSE",
                ),
                class_name="mm-credit",
            ),
            width="100%",
            class_name="mm-canvas",
        ),
        _zone("_workspace_composer_zone"),
        class_name="mm-shell mm-shell-agent-canvas",
    )


# --------------------------------------------------------------------------
# command_center -- intro, control board, then the world field below.
#
# Mirrors re-juliet-command-center-v1.html:
# .app { grid-template-rows: auto auto 1fr minmax(280px,42svh) }
# --------------------------------------------------------------------------


def _command_live_world(scene) -> rx.Component:
    """One world control: the dot, the scene name, and its live state."""
    return rx.button(
        rx.box(class_name="mm-dot", width="8px", height="8px"),
        rx.text(scene["name"], class_name="mm-worlds-name"),
        rx.text(
            rx.cond(
                scene["key"] == HostState.active_music_scene_key,
                "active",
                "standby",
            ),
            class_name="mm-worlds-state",
        ),
        on_click=HostState.set_music_scene(scene["key"]),
        variant="ghost",
        class_name=rx.cond(
            scene["key"] == HostState.active_music_scene_key,
            "mm-cc-world mm-buffer mm-cc-world-active",
            "mm-cc-world mm-buffer",
        ),
        width="100%",
    )


def _command_static_world(key: str, name: str) -> rx.Component:
    """Fallback world control (literal preview copy)."""
    return rx.button(
        rx.box(class_name="mm-dot", width="8px", height="8px"),
        rx.text(name, class_name="mm-worlds-name"),
        rx.text(
            rx.cond(
                HostState.active_music_scene_key == key.lower(),
                "active",
                "standby",
            ),
            class_name="mm-worlds-state",
        ),
        on_click=HostState.set_music_scene(key.lower()),
        variant="ghost",
        class_name=rx.cond(
            HostState.active_music_scene_key == key.lower(),
            "mm-cc-world mm-buffer mm-cc-world-active",
            "mm-cc-world mm-buffer",
        ),
        width="100%",
    )


def _command_worlds() -> rx.Component:
    """The world-state switcher beside the intro copy."""
    return rx.box(
        rx.cond(
            HostState.active_music_scenes != [],
            rx.foreach(HostState.active_music_scenes, _command_live_world),
            rx.fragment(
                _command_static_world("A", "A \u00b7 Rainy Window"),
                _command_static_world("B", "B \u00b7 Warm Cafe"),
                _command_static_world("C", "C \u00b7 Rain City"),
            ),
        ),
        class_name="mm-worlds",
        width="100%",
    )


def _command_state_row(
    key: str,
    value: str,
    pill: str,
    pill_ok: bool = False,
) -> rx.Component:
    """One live-state row on the correspondence control board."""
    return rx.box(
        rx.text(key, class_name="mm-state-key"),
        rx.text(value, class_name="mm-state-value"),
        rx.text(
            pill,
            class_name="mm-pill mm-pill-ok" if pill_ok else "mm-pill",
        ),
        class_name="mm-state-row",
        width="100%",
    )


def shell_command_center() -> rx.Component:
    return rx.vstack(
        _top_bar(
            "MULTIMIND / ARCHETYPE SWAP 05",
            "COMMAND CENTER \u00d7 MUSIC DNA",
        ),
        # .intro -- the title beside the world-state switcher
        rx.box(
            rx.box(
                rx.text(
                    "observe / control / preserve correspondence",
                    class_name="mm-eyebrow",
                ),
                _title(),
                rx.text(
                    "The system is operational, but the emotional world is "
                    "not reduced to telemetry. Command Center owns system "
                    "state and intervention; JULIET still owns atmosphere, "
                    "typography, and the meaning of A / B / C.",
                    class_name="mm-intro-side",
                ),
                class_name="mm-intro-copy",
                width="100%",
            ),
            _command_worlds(),
            class_name="mm-intro",
            width="100%",
        ),
        # .control -- the board beside the operator decision
        rx.hstack(
            rx.box(
                rx.box(
                    rx.heading(
                        "Correspondence control",
                        class_name="mm-board-title",
                    ),
                    rx.text("live state", class_name="mm-label"),
                    class_name="mm-board-head",
                    width="100%",
                ),
                _command_state_row(
                    "session continuity",
                    "REJULIET-04 remains attached across provider changes",
                    "HELD",
                    pill_ok=True,
                ),
                _command_state_row(
                    "model identity",
                    "GPT-5.6 SOL shown truthfully at presentation layer",
                    "TRUE",
                    pill_ok=True,
                ),
                _command_state_row(
                    "fallback route",
                    "provider may change without resetting conversation state",
                    "AUTO",
                ),
                rx.box(
                    rx.text("world signal", class_name="mm-state-key"),
                    rx.text(
                        rx.cond(
                            HostState.active_music_scene_name != "",
                            HostState.active_music_scene_name,
                            "A / Rainy Window \u00b7 close, gentle, rain on "
                            "glass",
                        ),
                        class_name="mm-state-value",
                    ),
                    rx.text(
                        "LIVE",
                        class_name="mm-pill mm-pill-ok",
                    ),
                    class_name="mm-state-row",
                    width="100%",
                ),
                rx.box(
                    _zone("_workspace_result_zone"),
                    width="100%",
                ),
                class_name="mm-board",
                width="100%",
            ),
            rx.box(
                rx.text(
                    "operator intervention",
                    class_name="mm-label",
                ),
                rx.heading(
                    "Keep the thread.\nChange the vehicle.",
                    white_space="pre-line",
                    class_name="mm-decision-title",
                ),
                rx.text(
                    "Compare models, inspect state, or trigger fallback "
                    "without flattening the correspondence into generic "
                    "operations UI.",
                    class_name="mm-decision-copy",
                ),
                rx.text(
                    "Preserve session \u2192",
                    class_name="mm-decision-action",
                ),
                class_name="mm-decision",
                width="100%",
            ),
            align="start",
            class_name="mm-control",
            width="100%",
        ),
        # .ground -- the world field on the lower horizon
        rx.box(
            _photo_box(
                "mm-ground-photo",
                "/scenes/rainy_window.webp",
                "center 58%",
            ),
            rx.box(
                rx.box(
                    rx.text(
                        "world field / lower horizon",
                        class_name="mm-label mm-label-light",
                    ),
                    rx.heading(
                        _live_scene_name(),
                        class_name="mm-ground-name",
                    ),
                    class_name="mm-ground-title-copy",
                    width="100%",
                ),
                rx.text(
                    _live_scene_thesis(),
                    class_name="mm-ground-thesis",
                ),
                class_name="mm-ground-copy",
                width="100%",
            ),
            rx.text(
                _live_scene_credit(
                    "PHOTO \u00b7 RAINY LIGHTS \u00b7 DEFI22 "
                    "\u00b7 WIKIMEDIA COMMONS \u00b7 CC BY-SA 4.0",
                ),
                class_name="mm-credit",
            ),
            class_name="mm-ground",
            width="100%",
        ),
        rx.vstack(
            rx.box(_zone("_workspace_utility_zone"), width="100%"),
            _zone("_workspace_composer_zone"),
            _zone("_workspace_history_zone"),
            spacing="3",
            class_name="mm-command-zones",
            width="100%",
        ),
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
    """The session *is* the screen.

    The preview puts the running deliberation in `.term > .screen`: a boot line,
    the active world, then one article per turn, alternating `you@juliet:~$` and
    `multimind>`. The composer is a fixed strip at the bottom of the viewport
    rather than a panel below the content.

    So the session state lands here instead of in a separate card underneath:
    HostState.current_critiques drives the articles, the session name drives the
    header, and the composer is fixed. The semantic zones stay available for the
    session list and backup, which are the one thing the preview does not place
    inside the terminal.
    """
    return rx.hstack(
        # ---- .side: identity and the A/B/C world switcher -------------------
        rx.vstack(
            rx.text("MULTIMIND / ARCHETYPE SWAP 01", class_name="mm-brand"),
            rx.box(
                rx.text("TERMINAL / HACKER \u00d7 MUSIC DNA", class_name="mm-kicker"),
                _title(),
                rx.text(
                    "Same session, same memories, same three emotional worlds. "
                    "The mental model changes: issue instructions, inspect output, "
                    "keep the correspondence alive.",
                    class_name="mm-song-desc",
                ),
                class_name="mm-song",
                width="100%",
                spacing="2",
            ),
            rx.box(_terminal_buffers(), width="100%"),
            rx.text(
                "archetype invariant / issue instruction \u2192 observe execution",
                class_name="mm-foot",
            ),
            spacing="4",
            class_name="mm-side",
            width="100%",
        ),
        # ---- .term: the session ------------------------------------------
        rx.vstack(
            # .top -- which session is attached, and the run configuration
            rx.hstack(
                rx.hstack(
                    rx.text("session / ", class_name="mm-top-line"),
                    rx.text(
                        rx.cond(
                            HostState.current_session_name != "",
                            HostState.current_session_name,
                            "REJULIET-04",
                        ),
                        class_name="mm-top-b",
                    ),
                    spacing="1",
                    align="baseline",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.text("memory / ", class_name="mm-top-line"),
                    rx.text("ON", class_name="mm-top-b"),
                    spacing="1",
                    align="baseline",
                ),
                width="100%",
                align="center",
                class_name="mm-term-top",
            ),
            # .screen -- the session transcript
            rx.box(
                # the boot line, echoing the attached session
                rx.text(
                    "multimind@juliet:~$ session attach "
                    + rx.cond(
                        HostState.current_session_name != "",
                        HostState.current_session_name,
                        "REJULIET-04",
                    ),
                    class_name="mm-boot",
                ),
                # .head -- the active world, which is what the session is set to
                rx.hstack(
                    rx.box(rx.text("ACTIVE BUFFER", class_name="mm-label"), width="130px"),
                    rx.vstack(
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
                                "Patah hati yang dekat dan lembut: hujan di kaca memberi "
                                "jarak, lampu kota masih hidup, dan versi band terasa "
                                "hangat alih-alih dingin.",
                            ),
                            class_name="mm-term-thesis",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    gap="5",
                    align="start",
                    class_name="mm-head",
                    width="100%",
                ),
                # one article per turn of the live deliberation
                rx.box(
                    rx.foreach(HostState.current_critiques, _session_turn),
                    width="100%",
                    class_name="mm-transcript",
                ),
                # the verdict closes the transcript, as it does in the preview
                rx.cond(
                    HostState.current_system_verdict != "",
                    rx.box(
                        rx.hstack(
                            rx.box(
                                rx.text("multimind>", class_name="mm-prompt ai"),
                                width="130px",
                            ),
                            rx.vstack(
                                rx.text(
                                    HostState.current_system_verdict,
                                    class_name="mm-out",
                                ),
                                rx.text(
                                    "result / correspondence preserved",
                                    class_name="mm-sys",
                                ),
                                spacing="1",
                                align="start",
                                class_name="mm-line-body",
                                width="100%",
                            ),
                            gap="5",
                            align="start",
                            class_name="mm-line ai",
                            width="100%",
                        ),
                        width="100%",
                    ),
                ),
                width="100%",
                class_name="mm-screen",
            ),
            # the composer sits at the foot of the viewport, as in the preview
            rx.hstack(
                rx.box(rx.text("you@juliet:~$", class_name="mm-sig"), width="130px"),
                rx.text_area(
                    placeholder="Issue an instruction without breaking the correspondence\u2026",
                    value=HostState.prompt,
                    on_change=HostState.set_prompt,
                    class_name="mm-prompt-input",
                    width="100%",
                ),
                rx.button(
                    "Run \u21b5",
                    on_click=HostState.run_chat,
                    class_name="mm-run",
                ),
                align="center",
                gap="3",
                width="100%",
                class_name="mm-composer",
            ),
            # the session list and backup are the one thing the preview keeps
            # outside the terminal, so they stay addressable without displacing it
            rx.box(_zone("_workspace_history_zone"), width="100%"),
            spacing="0",
            class_name="mm-term",
            width="100%",
        ),
        align="start",
        gap="0",
        width="100%",
        class_name="mm-shell mm-shell-terminal-hacker",
    )


def _session_turn(turn: dict) -> rx.Component:
    """One turn of the live session, rendered as the preview's `.line` article.

    The preview alternates `you@juliet:~$` and `multimind>`; each row shows the
    instruction or the response, with the system status underneath.
    """
    label = rx.cond(turn["status"] == "success", turn["effective_identity_label"], "multimind>")
    prompt_text = rx.cond(
        turn["status"] == "success",
        turn["requested_identity_label"] + ":~$",
        "multimind>",
    )
    sys_line = rx.cond(
        turn["status"] == "success",
        "instruction accepted \u00b7 " + turn["actual_provider"],
        "result / " + turn["status"],
    )
    return rx.hstack(
        rx.box(rx.text(prompt_text, class_name="mm-prompt"), width="130px"),
        rx.vstack(
            rx.text(
                rx.cond(turn["status"] == "success", turn["requested_provider"], turn["text"]),
                class_name="mm-out",
            ),
            rx.text(sys_line, class_name="mm-sys"),
            spacing="1",
            align="start",
            class_name="mm-line-body",
            width="100%",
        ),
        gap="5",
        align="start",
        class_name="mm-line",
        width="100%",
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