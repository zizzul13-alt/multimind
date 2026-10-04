"""The photographic plate each track's preview declares.

The previews credit one specific Wikimedia Commons file per track, with its
author and licence, so those are the plates used here -- self-hosted under
assets/tracks, darkened so type stays readable over them. Nothing is hotlinked
and no image was generated.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrackPlate:
    track: str
    image: str
    credit: str
    source: str


PLATES: dict[str, TrackPlate] = {
    'ti01': TrackPlate(
        track='ti01', image="/tracks/ti01.webp",
        credit="", source="https://commons.wikimedia.org/wiki/Special:Redirect/file/Nightview%20Shonan%20from%20Shonandaira.jpg",
    ),
    'ti02': TrackPlate(
        track='ti02', image="/tracks/ti02.webp",
        credit="Photo: “Tokyo Night” by Danny15 · Wikimedia Commons · CC BY-SA 3.0", source="https://commons.wikimedia.org/wiki/Special:Redirect/file/Tokyo%20Night.jpg",
    ),
    'ti08': TrackPlate(
        track='ti08', image="/tracks/ti08.webp",
        credit="Photo: “Tokyo Alley” · Nir Yaniv · Wikimedia Commons · CC BY-SA 4.0", source="https://commons.wikimedia.org/wiki/Special:Redirect/file/Tokyo%20Alley.jpg",
    ),
    'ti11': TrackPlate(
        track='ti11', image="/tracks/ti11.webp",
        credit="Photo: “Sunflower field at sunset.jpg” · Summer Stock · Wikimedia Commons · CC0 1.0", source="https://commons.wikimedia.org/wiki/Special:Redirect/file/Sunflower%20field%20at%20sunset.jpg",
    ),
}


def plate_for_track(track_id: str) -> TrackPlate | None:
    """The plate a track declares, when one was downloaded."""
    return PLATES.get(str(track_id or "").strip().casefold())


__all__ = ["TrackPlate", "PLATES", "plate_for_track"]