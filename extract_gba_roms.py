#!/usr/bin/env python3
"""
Download each game's GBA ROM into `games/roms/` and rewrite the HTML wrapper
so the page loads the local file instead of a remote CDN URL.

Usage:
    python extract_gba_roms.py
"""

from __future__ import annotations

import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAMES_DIR = ROOT / "games"
ROMS_DIR = GAMES_DIR / "roms"
ROMS_DIR.mkdir(parents=True, exist_ok=True)

URL_PATTERN = re.compile(r'EJS_gameUrl\s*=\s*["\'](https?://[^"\']+)["\']')


def download(url: str, destination: Path) -> None:
    if destination.exists():
        return

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as response, destination.open("wb") as out_file:
        shutil.copyfileobj(response, out_file)


def safe_name(url: str) -> str:
    name = url.split("/")[-1]
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name) or "game.gba"
    if not safe.lower().endswith(".gba"):
        safe = f"{safe}.gba"
    return safe


count = 0
for html_file in sorted(GAMES_DIR.glob("*.html")):
    text = html_file.read_text(encoding="utf-8", errors="replace")
    match = URL_PATTERN.search(text)
    if not match:
        continue

    url = match.group(1)
    local_name = safe_name(url)
    rom_path = ROMS_DIR / local_name
    download(url, rom_path)

    rewritten = text.replace(url, f"./roms/{local_name}")
    if rewritten != text:
        html_file.write_text(rewritten, encoding="utf-8")
        count += 1

print(f"Updated {count} game files to use local ROMs in {ROMS_DIR}")
