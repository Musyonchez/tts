"""Offline library: scan fictionzone/novelhall content dirs + bookmark persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Resolve paths relative to app-tts/ → ../web-tts/
_APP_DIR = Path(__file__).parent.parent
_WEB_TTS = _APP_DIR.parent / "web-tts"

SOURCES: dict[str, Path] = {
    "fictionzone": _WEB_TTS / "fictionzone" / "content",
    "novelhall": _WEB_TTS / "novelhall" / "content",
}

_BOOKMARKS_FILE = _APP_DIR / "data" / "bookmarks.json"
_SETTINGS_FILE = _APP_DIR / "data" / "settings.json"


@dataclass
class ChapterInfo:
    path: Path
    display_name: str  # e.g. "Chapter 0042"
    number: int


@dataclass
class NovelInfo:
    slug: str
    source: str
    display_name: str
    chapter_count: int
    chapters: list[ChapterInfo] = field(default_factory=list)
    bookmarked_chapter: str | None = None  # filename like "chapter-0042.txt"


# ---------------------------------------------------------------------------
# Library scanning
# ---------------------------------------------------------------------------

def list_novels(source: str) -> list[NovelInfo]:
    root = SOURCES.get(source)
    if not root or not root.exists():
        return []

    novels = []
    for novel_dir in sorted(root.iterdir()):
        if not novel_dir.is_dir():
            continue
        chapters = _scan_chapters(novel_dir)
        bookmark = _load_bookmark(f"{source}/{novel_dir.name}")
        novels.append(NovelInfo(
            slug=novel_dir.name,
            source=source,
            display_name=novel_dir.name.replace("-", " ").title(),
            chapter_count=len(chapters),
            chapters=chapters,
            bookmarked_chapter=bookmark.get("chapter_file") if bookmark else None,
        ))
    return novels


def _scan_chapters(novel_dir: Path) -> list[ChapterInfo]:
    chapters = []
    for f in sorted(novel_dir.glob("chapter-*.txt")):
        # Extract number from "chapter-0042.txt"
        try:
            num = int(f.stem.split("-")[1])
        except (IndexError, ValueError):
            num = 0
        chapters.append(ChapterInfo(
            path=f,
            display_name=f"Chapter {num:04d}",
            number=num,
        ))
    return chapters


def load_chapter_text(path: Path) -> tuple[str, list[str]]:
    """Read a saved .txt file. Returns (title, paragraphs)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = lines[0].strip() if lines else path.stem
    # Format: title / separator / blank line / body
    body_lines = lines[3:] if len(lines) > 3 else []
    body = "\n".join(body_lines)
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    # Fallback: split by single newlines if no double-newlines found
    if not paragraphs:
        paragraphs = [line.strip() for line in body_lines if line.strip()]
    return title, paragraphs


def next_chapter(current: Path) -> Path | None:
    siblings = sorted(current.parent.glob("chapter-*.txt"))
    try:
        idx = siblings.index(current)
        return siblings[idx + 1] if idx + 1 < len(siblings) else None
    except ValueError:
        return None


def prev_chapter(current: Path) -> Path | None:
    siblings = sorted(current.parent.glob("chapter-*.txt"))
    try:
        idx = siblings.index(current)
        return siblings[idx - 1] if idx > 0 else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Bookmarks
# ---------------------------------------------------------------------------

def _load_all_bookmarks() -> dict:
    if not _BOOKMARKS_FILE.exists():
        return {}
    try:
        return json.loads(_BOOKMARKS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_all_bookmarks(data: dict) -> None:
    _BOOKMARKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _BOOKMARKS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_bookmark(key: str) -> dict | None:
    return _load_all_bookmarks().get(key)


def save_bookmark(key: str, data: dict) -> None:
    all_bm = _load_all_bookmarks()
    all_bm[key] = {**data, "updated": datetime.now().isoformat(timespec="seconds")}
    _save_all_bookmarks(all_bm)


def save_offline_bookmark(source: str, novel_slug: str, chapter_file: str) -> None:
    key = f"{source}/{novel_slug}"
    save_bookmark(key, {"chapter_file": chapter_file})


def load_offline_bookmark(source: str, novel_slug: str) -> str | None:
    key = f"{source}/{novel_slug}"
    bm = _load_bookmark(key)
    return bm.get("chapter_file") if bm else None


def save_web_bookmark(url: str, next_url: str = "") -> None:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    key = f"web/{parsed.netloc}{parsed.path}"
    save_bookmark(key, {"last_url": url, "next_url": next_url})


def load_web_bookmark(url: str) -> dict | None:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    key = f"web/{parsed.netloc}{parsed.path}"
    return _load_bookmark(key)


# ------------------------------------------------------------------
# Settings persistence
# ------------------------------------------------------------------

def load_settings() -> dict:
    try:
        return json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(data: dict) -> None:
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = load_settings()
    existing.update(data)
    _SETTINGS_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
