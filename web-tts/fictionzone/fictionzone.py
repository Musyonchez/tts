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

import win32com.client

CONTENT_DIR = Path(__file__).parent / "content"

# SAPI rate: -10 (slowest) to 10 (fastest), 0 = ~180 wpm
RATE = 10
VOLUME = 100  # 0-100


def get_speaker():
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    # Find Zira
    voices = speaker.GetVoices()
    for i in range(voices.Count):
        if "Zira" in voices.Item(i).GetDescription():
            speaker.Voice = voices.Item(i)
            break
    speaker.Rate = RATE
    speaker.Volume = VOLUME
    return speaker


def read_file(speaker, path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = lines[0].strip() if lines else path.stem
    body = "\n".join(lines[3:]).strip()  # skip title + === separator + blank line
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    print(f"\n--- {title} ---")
    print(f"({len(body.split())} words, {len(paragraphs)} paragraphs)")
    speaker.Speak(title)
    for para in paragraphs:
        speaker.Speak(para)


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

    speaker = get_speaker()

    while current:
        read_file(speaker, current)
        nxt = next_chapter(current)
        if nxt:
            print(f"Next: {nxt.name}")
        current = nxt

    print("\nNo more chapters.")


if __name__ == "__main__":
    main()
