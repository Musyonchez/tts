"""
collect.py — Pick up JSON files saved by the browser extension and process them.

The extension saves to: Downloads\fictionzone-tts\
This script:  reads each JSON, saves chapter text to fictionzone\content\, reads aloud, moves JSON to processed\.

Usage:
    venv\Scripts\python.exe fictionzone\collect.py
"""

import json
import shutil
from pathlib import Path

import pyttsx3

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


def speak(engine, chapter_title: str, text: str):
    print(f"  Reading '{chapter_title}' ({len(text.split())} words)...")
    engine.say(chapter_title)
    engine.say(text)
    engine.runAndWait()


def main():
    if not DOWNLOADS_DIR.exists():
        print(f"No pending chapters — {DOWNLOADS_DIR} does not exist yet.")
        return

    json_files = sorted(DOWNLOADS_DIR.glob("*.json"))
    if not json_files:
        print(f"No pending chapters in {DOWNLOADS_DIR}")
        return

    print(f"Found {len(json_files)} chapter(s) to process.\n")

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)  # Zira
    engine.setProperty("rate", 450)
    engine.setProperty("volume", 1.0)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for json_file in json_files:
        print(f"Processing: {json_file.name}")
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ERROR reading {json_file.name}: {e}")
            continue

        save_chapter(data)
        speak(engine, data["chapter_title"], data["text"])

        # Move to processed so it won't be picked up again
        shutil.move(str(json_file), PROCESSED_DIR / json_file.name)
        print(f"  Done.\n")

    print("All chapters processed.")


if __name__ == "__main__":
    main()
