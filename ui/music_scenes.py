"""Per-track scene sets for the MusicDNA world rail.

The hand-built previews in the private Design-DNA repo each carry three scenes
(A/B/C) per track: a photo, a name, a thesis paragraph, a focal position and a
credit line. Switching scene swaps the whole world, which is what makes those
previews feel alive rather than merely themed.

design_dna exposes one presentation plan per (track, archetype) and no scene
concept at all, so the scene data lives here instead, keyed by track id. When
the runtime later carries scenes, this module becomes the fallback rather than
the only source.

Data transcribed from the previews so the look matches what was built by hand.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MusicScene:
    """One A/B/C correspondence world for a track."""

    key: str
    name: str
    thesis: str
    photo_url: str
    position: str
    credit: str


# Scenes transcribed from preview/lab/music-v0/architecture-swap/*.html in the
# private Design-DNA repo. Only the tracks that were hand-built have scenes;
# everything else falls back to a single neutral scene.
_SCENES_BY_TRACK: dict[str, tuple[MusicScene, ...]] = {
    "re-juliet": (
        MusicScene(
            key="a",
            name="A / Rainy Window",
            thesis=(
                "Patah hati yang dekat dan lembut: hujan di kaca memberi jarak, "
                "lampu kota masih hidup, dan versi band terasa hangat "
                "alih-alih dingin."
            ),
            photo_url=(
                "https://unsplash.com/photos/sTM-k3AtML8/download?force=true&w=1800"
            ),
            position="center 58%",
            credit="PHOTO \u00b7 RAINY WINDOW \u00b7 UNSPLASH LICENSE",
        ),
        MusicScene(
            key="b",
            name="B / Warm Cafe",
            thesis=(
                "Lebih manusiawi dan akrab: tempat yang masih hangat meski "
                "hubungan sudah selesai. Nostalgia yang hidup, bukan arsip."
            ),
            photo_url=(
                "https://unsplash.com/photos/lsIzsNFtt5Q/download?force=true&w=1800"
            ),
            position="center 52%",
            credit="PHOTO \u00b7 WARM CAFE \u00b7 UNSPLASH LICENSE",
        ),
        MusicScene(
            key="c",
            name="C / Rain City",
            thesis=(
                "Kota yang tetap jalan meski relationship sudah selesai: "
                "lalu lintas, lampu, dan ritme yang tidak menunggu."
            ),
            photo_url=(
                "https://unsplash.com/photos/1L71sPT5XKc/download?force=true&w=1800"
            ),
            position="center 54%",
            credit="PHOTO \u00b7 RAIN CITY \u00b7 UNSPLASH LICENSE",
        ),
    ),
    "you-and-i": (
        MusicScene(
            key="a",
            name="A / Brass Stage",
            thesis=(
                "Energi band yang live: beberapa voice dan instrumen terpisah, "
                "lalu menyatu di satu downbeat."
            ),
            photo_url=(
                "https://unsplash.com/photos/nzyzAUsbV0M/download?force=true&w=1800"
            ),
            position="center 50%",
            credit="PHOTO \u00b7 BRASS STAGE \u00b7 UNSPLASH LICENSE",
        ),
        MusicScene(
            key="b",
            name="B / Rehearsal Room",
            thesis=(
                "Ruang latihan: lebih dekat, lebih kasar, lebih jujur. "
                "Aransemen terdengar sebelum ia rapi."
            ),
            photo_url=(
                "https://unsplash.com/photos/J6TI6X2JigM/download?force=true&w=1800"
            ),
            position="center 46%",
            credit="PHOTO \u00b7 REHEARSAL ROOM \u00b7 UNSPLASH LICENSE",
        ),
        MusicScene(
            key="c",
            name="C / Late Set",
            thesis=(
                "Set terakhir: lebih pelan, lebih jarang, dan lebih penuh "
                "diam daripada applause."
            ),
            photo_url=(
                "https://unsplash.com/photos/oQ8Y4YQ9qC0/download?force=true&w=1800"
            ),
            position="center 55%",
            credit="PHOTO \u00b7 LATE SET \u00b7 UNSPLASH LICENSE",
        ),
    ),
}

# Neutral fallback so every track still gets a switchable world rail.
_DEFAULT_SCENES = (
    MusicScene(
        key="a",
        name="A / Current",
        thesis="",
        photo_url="",
        position="center",
        credit="",
    ),
    MusicScene(
        key="b",
        name="B / Alternate",
        thesis="",
        photo_url="",
        position="center",
        credit="",
    ),
    MusicScene(
        key="c",
        name="C / Contrast",
        thesis="",
        photo_url="",
        position="center",
        credit="",
    ),
)


def scenes_for_track(track_id: str) -> tuple[MusicScene, ...]:
    """Return the A/B/C scenes for a track, or the neutral set.

    Lookup is by track slug, so `ti01` maps to `re-juliet` only when the
    runtime id says so; unknown tracks get the neutral scenes rather than an
    empty rail.
    """
    slug = str(track_id or "").strip().casefold()
    if slug in _SCENES_BY_TRACK:
        return _SCENES_BY_TRACK[slug]

    # ti01 is the first Track T-I entry and the one the previews were built for.
    if slug in {"ti01", "ti1"}:
        return _SCENES_BY_TRACK["re-juliet"]

    return _DEFAULT_SCENES


__all__ = ["MusicScene", "scenes_for_track"]
