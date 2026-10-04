"""Download the track plates declared by the previews, politely.

Each preview credits a specific Wikimedia Commons file with its author and
licence, so those are the sources. Commons rate-limits aggressively, so this
paces itself, retries with backoff, and records what it got so a re-run resumes
rather than starting over.

Usage: python tools/fetch-track-photos.py
"""

import io
import json
import os
import random
import time
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT.parent / "photo_raw"
OUT = ROOT / "assets" / "tracks"
PLAN = ROOT.parent / "photo_plan.json"
MANIFEST = ROOT.parent / "photo_manifest.json"
UA = "multimind-track-assets/1.0 (local build)"
WIDTH = 1600
EXPOSURE = 0.82   # text sits on the plate, so the image is darkened to carry it


def load(path, default):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default


def fetch(url, dest: Path, attempts=2):
    if dest.exists() and dest.stat().st_size > 4000:
        return dest.read_bytes()
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            dest.write_bytes(data)
            return data
        except Exception as exc:  # noqa: BLE001 - report and retry
            wait = 5 * (i + 1)
            print(f"    retry in {wait}s ({type(exc).__name__})", flush=True)
            time.sleep(wait)
    return None


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    plan = load(PLAN, [])
    manifest = load(MANIFEST, [])
    done = {m["track"] for m in manifest}
    todo = [p for p in plan if p["track"] not in done]

    print(f"{len(todo)} of {len(plan)} plates remaining\n", flush=True)
    for p in todo:
        slug = p["track"].replace(":", "-")
        raw = fetch(p["url"], RAW / f"{slug}.img")
        if raw is None:
            print(f"FAIL {slug}: giving up", flush=True)
            time.sleep(20)
            continue
        try:
            im = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception:
            print(f"SKIP {slug}: not decodable", flush=True)
            continue

        if im.width > WIDTH:
            im = im.resize((WIDTH, int(WIDTH * im.height / im.width)), Image.LANCZOS)
        im = Image.eval(im, lambda v: int(min(255, (v / 255.0) ** EXPOSURE * 255)))
        webp = OUT / f"{slug}.webp"
        im.save(webp, "WEBP", quality=76, method=5)
        manifest.append({
            "track": p["track"],
            "file": f"{slug}.webp",
            "bytes": webp.stat().st_size,
            "credit": p["credit"],
            "source": p["url"],
        })
        MANIFEST.write_text(json.dumps(manifest, indent=1))
        print(f"OK   {slug:14s} {webp.stat().st_size // 1024:>4d}KB", flush=True)
        time.sleep(4 + random.random() * 3)

    print(f"\n{len(manifest)}/{len(plan)} plates, "
          f"{sum(m['bytes'] for m in manifest) // 1024}KB", flush=True)


if __name__ == "__main__":
    main()