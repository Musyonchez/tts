"""
fictionzone.py — Extract, save, and read aloud a chapter from fictionzone.net

Usage:
    # Pipe clipboard HTML (PowerShell):
    Get-Clipboard | venv\Scripts\python.exe fictionzone\fictionzone.py <save_dir>

    # Or from a saved HTML file:
    venv\Scripts\python.exe fictionzone\fictionzone.py <save_dir> chapter.html
"""

import re
import sys
import textwrap
from pathlib import Path

import pyttsx3
from bs4 import BeautifulSoup


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def parse_html(html: str):
    soup = BeautifulSoup(html, "lxml")

    # Novel title → folder name
    novel_tag = soup.select_one("span.novel-title")
    novel_title = novel_tag.get_text(strip=True) if novel_tag else "unknown-novel"
    novel_slug = slugify(novel_title)

    # Chapter title
    title_tag = (
        soup.select_one("h1.chapter-article-title")
        or soup.select_one("h1.chapter-title")
    )
    chapter_title = title_tag.get_text(strip=True) if title_tag else "Unknown Chapter"

    # Chapter number from progress indicator e.g. "1 / 325"
    progress_tag = soup.select_one("span.chapter-progress")
    chapter_num = 1
    if progress_tag:
        m = re.match(r"(\d+)", progress_tag.get_text(strip=True))
        if m:
            chapter_num = int(m.group(1))

    # Chapter text — grab all <p> inside div.chapter-text, skip ad divs
    content_div = soup.select_one("div.chapter-text")
    if not content_div:
        print("ERROR: Could not find div.chapter-text in the HTML.")
        sys.exit(1)

    for ad in content_div.select("div.ad-slot"):
        ad.decompose()

    paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p") if p.get_text(strip=True)]
    text = "\n\n".join(paragraphs)

    return novel_slug, chapter_num, chapter_title, text


def save_chapter(save_dir: str, novel_slug: str, chapter_num: int, chapter_title: str, text: str) -> Path:
    out_dir = Path(save_dir) / "content" / novel_slug
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
    if len(sys.argv) < 2:
        print("Usage: fictionzone.py <save_dir> [html_file]")
        print("       If html_file is omitted, HTML is read from stdin.")
        sys.exit(1)

    save_dir = sys.argv[1]

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            html = f.read()
    else:
        print("Reading HTML from stdin...")
        html = sys.stdin.read()

    novel_slug, chapter_num, chapter_title, text = parse_html(html)

    if not text:
        print("ERROR: No chapter text found.")
        sys.exit(1)

    save_chapter(save_dir, novel_slug, chapter_num, chapter_title, text)
    speak(chapter_title, text)


if __name__ == "__main__":
    main()
