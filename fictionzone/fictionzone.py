"""
fictionzone.py — Read saved chapter files aloud, auto-advancing to the next.

Usage:
    # Read a specific chapter file and continue from there:
    venv\Scripts\python.exe fictionzone\fictionzone.py fictionzone\content\<novel>\chapter-0001.txt

    # Or just the novel folder — starts from the first chapter:
    venv\Scripts\python.exe fictionzone\fictionzone.py fictionzone\content\<novel>
"""

import sys
from pathlib import Path

import pyttsx3

CONTENT_DIR = Path(__file__).parent / "content"


def get_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)  # Zira
    engine.setProperty("rate", 450)
    engine.setProperty("volume", 1.0)
    return engine


def read_file(engine, path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = lines[0].strip() if lines else path.stem
    body = "\n".join(lines[3:]).strip()  # skip title + === separator + blank line
    print(f"\n--- {title} ---")
    print(f"({len(body.split())} words)")
    engine.say(title)
    engine.say(body)
    engine.runAndWait()


def next_chapter(current: Path) -> Path | None:
    siblings = sorted(current.parent.glob("chapter-*.txt"))
    try:
        idx = siblings.index(current)
        return siblings[idx + 1] if idx + 1 < len(siblings) else None
    except ValueError:
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: fictionzone.py <chapter.txt | novel-folder>")
        print(f"Content is in: {CONTENT_DIR}")
        sys.exit(1)

    target = Path(sys.argv[1])

    # If a folder is given, start from the first chapter in it
    if target.is_dir():
        chapters = sorted(target.glob("chapter-*.txt"))
        if not chapters:
            print(f"No chapter files found in {target}")
            sys.exit(1)
        current = chapters[0]
    else:
        current = target

    if not current.exists():
        print(f"File not found: {current}")
        sys.exit(1)

    engine = get_engine()

    while current:
        read_file(engine, current)
        nxt = next_chapter(current)
        if nxt:
            print(f"Next: {nxt.name}")
        current = nxt

    print("\nNo more chapters.")


if __name__ == "__main__":
    main()
