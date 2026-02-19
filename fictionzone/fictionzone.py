"""
fictionzone.py — Save and read aloud a chapter from fictionzone.net

Reads JSON copied to clipboard by the browser extension.

Usage (PowerShell):
    Get-Clipboard | venv\Scripts\python.exe fictionzone\fictionzone.py

Save path:
    fictionzone\content\<novel-slug>\chapter-XXXX.txt
"""

import json
import sys
from pathlib import Path

import pyttsx3

# Save content next to this script: fictionzone/content/<novel>/<chapter>.txt
CONTENT_DIR = Path(__file__).parent / "content"


def save_chapter(data: dict) -> Path:
    novel_slug = data["novel_slug"]
    chapter_num = data["chapter_num"]
    chapter_title = data["chapter_title"]
    text = data["text"]

    out_dir = CONTENT_DIR / novel_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"chapter-{chapter_num:04d}.txt"
    out_path = out_dir / filename

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{chapter_title}\n{'=' * len(chapter_title)}\n\n")
        f.write(text)

    print(f"Saved: {out_path}")
    return out_path


def speak(chapter_title: str, text: str):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)  # Zira
    engine.setProperty("rate", 450)
    engine.setProperty("volume", 1.0)

    word_count = len(text.split())
    print(f"Reading '{chapter_title}' ({word_count} words)...")

    engine.say(chapter_title)
    engine.say(text)
    engine.runAndWait()


def main():
    print("Reading JSON from stdin...")
    raw = sys.stdin.read().strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse JSON — {e}")
        sys.exit(1)

    required = {"novel_slug", "chapter_num", "chapter_title", "text"}
    missing = required - data.keys()
    if missing:
        print(f"ERROR: JSON missing fields: {missing}")
        sys.exit(1)

    save_chapter(data)
    speak(data["chapter_title"], data["text"])


if __name__ == "__main__":
    main()
