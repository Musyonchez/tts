"""
collect.py — Pick up JSON files saved by the browser extension and save as text.

The extension saves to: Downloads\fictionzone-tts\
This script saves chapter text to fictionzone\content\ and moves JSONs to processed\.

Usage:
    venv\Scripts\python.exe fictionzone\collect.py
"""

import json
import shutil
from pathlib import Path

DOWNLOADS_DIR = Path.home() / "Downloads" / "fictionzone-tts"
CONTENT_DIR = Path(__file__).parent / "content"
PROCESSED_DIR = DOWNLOADS_DIR / "processed"


def save_chapter(data: dict) -> Path:
    out_dir = CONTENT_DIR / data["novel_slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"chapter-{data['chapter_num']:04d}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        title = data["chapter_title"]
        f.write(f"{title}\n{'=' * len(title)}\n\n")
        f.write(data["text"])
    print(f"  Saved: {out_path}")
    return out_path


def main():
    if not DOWNLOADS_DIR.exists():
        print(f"No pending chapters — {DOWNLOADS_DIR} does not exist yet.")
        return

    json_files = sorted(DOWNLOADS_DIR.glob("*.json"))
    if not json_files:
        print(f"No pending chapters in {DOWNLOADS_DIR}")
        return

    print(f"Found {len(json_files)} chapter(s).\n")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for json_file in json_files:
        print(f"Processing: {json_file.name}")
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ERROR reading {json_file.name}: {e}")
            continue

        save_chapter(data)
        shutil.move(str(json_file), PROCESSED_DIR / json_file.name)

    print("\nDone.")


if __name__ == "__main__":
    main()
