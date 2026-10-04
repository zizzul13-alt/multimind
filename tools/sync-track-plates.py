"""Fetch the remaining track plates, then regenerate the plate table.

Script-only: Commons rate-limits hard, so the fetch is paced and resumes, and the
table is rebuilt whenever the manifest changes. Prints one line so a scheduler
with no_agent can deliver it verbatim, and nothing at all when nothing changed.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"F:/hermes/scratch/mm/be")
MANIFEST = ROOT.parent / "photo_manifest.json"
PLATES = ROOT / "ui" / "track_plates.py"
TRACKS = ROOT / "assets" / "tracks"


def lit(x):
    x = str(x or "")
    return '""' if not x else '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(manifest):
    lines = [
        '"""The photographic plate each track\'s preview declares.',
        "",
        "The previews credit one specific Wikimedia Commons file per track, with its",
        "author and licence, so those are the plates used here -- self-hosted under",
        "assets/tracks, darkened so type stays readable over them. Nothing is",
        "hotlinked and no image was generated.",
        '"""',
        "",
        "from dataclasses import dataclass",
        "",
        "",
        "@dataclass(frozen=True)",
        "class TrackPlate:",
        "    track: str",
        "    image: str",
        "    credit: str",
        "    source: str",
        "",
        "",
        "PLATES: dict[str, TrackPlate] = {",
    ]
    for m in manifest:
        lines += [
            f"    {m['track']!r}: TrackPlate(",
            f"        track={m['track']!r}, image={lit('/tracks/' + m['file'])},",
            f"        credit={lit(m['credit'])}, source={lit(m['source'])},",
            "    ),",
        ]
    lines += [
        "}",
        "",
        "",
        "def plate_for_track(track_id: str) -> TrackPlate | None:",
        '    """The plate a track declares, when one was downloaded."""',
        '    return PLATES.get(str(track_id or "").strip().casefold())',
        "",
        "",
        '__all__ = ["TrackPlate", "PLATES", "plate_for_track"]',
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    before = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []

    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "fetch-track-photos.py")],
        capture_output=True,
        text=True,
        timeout=280,
    )
    after = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []

    added = len(after) - len(before)
    if added:
        src = render(after)
        ast_ok = True
        try:
            compile(src, str(PLATES), "exec")
        except SyntaxError:
            ast_ok = False
        if ast_ok:
            PLATES.write_text(src, encoding="utf-8")

    on_disk = len(list(TRACKS.glob("*.webp"))) if TRACKS.exists() else 0
    # Silent when nothing moved, so a scheduler does not spam for no reason.
    if added or on_disk != len(before):
        print(f"{on_disk}/18 plates. {added} new. table regenerated: {bool(added)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())