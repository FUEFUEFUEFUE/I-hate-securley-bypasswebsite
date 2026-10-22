#!/usr/bin/env python3
"""Rewrite game wrappers to use local ROM files in games/roms/.

This script is intentionally safe: it never downloads ROMs, and it only rewrites
HTML wrappers that point to remote CDN URLs so they load a local ROM file instead.

Place your legal ROM files in games/roms/ and then run this script once.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAMES_DIR = ROOT / "games"
ROMS_DIR = GAMES_DIR / "roms"
ROMS_DIR.mkdir(parents=True, exist_ok=True)

URL_PATTERN = re.compile(r'EJS_gameUrl\s*=\s*["\']([^"\']+)["\']')


def safe_rom_name(value: str) -> str:
    name = value.split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    if not name.lower().endswith(".gba"):
        name = f"{name}.gba"
    return name


changed = 0
missing_roms: list[str] = []
for html_file in sorted(GAMES_DIR.glob("*.html")):
    text = html_file.read_text(encoding="utf-8", errors="replace")
    match = URL_PATTERN.search(text)
    if not match:
        continue

    original = match.group(1)
    local_name = safe_rom_name(original)
    local_path = f"./roms/{local_name}"
    expected = ROMS_DIR / local_name

    if not expected.exists():
        missing_roms.append(f"{html_file.name} -> {local_name}")

    if original != local_path:
        text = text.replace(original, local_path)
        html_file.write_text(text, encoding="utf-8")
        changed += 1

print(f"Updated {changed} game wrapper(s) to local paths.")
if missing_roms:
    print("\nThese ROM files still need to be placed in games/roms/:")
    for item in missing_roms:
        print(f"  - {item}")
    print("\nThen serve the site from a local static server and refresh the page.")
else:
    print("All discovered game wrappers now point to a local ROM path.")
