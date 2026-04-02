"""Import JSON chapters from browser extension Downloads folders."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

_WEB_TTS = Path(__file__).parent.parent.parent / "web-tts"

_SOURCES = {
    "fictionzone": {
        "downloads": Path.home() / "Downloads" / "fictionzone-tts",
        "content": _WEB_TTS / "fictionzone" / "content",
    },
    "novelhall": {
        "downloads": Path.home() / "Downloads" / "novelhall-tts",
        "content": _WEB_TTS / "novelhall" / "content",
    },
}


def _collect_source(source: str) -> int:
    """Process all pending JSON files for one source. Returns count saved."""
    cfg = _SOURCES[source]
    downloads: Path = cfg["downloads"]
    content: Path = cfg["content"]

    if not downloads.exists():
        return 0

    json_files = sorted(downloads.glob("*.json"))
    if not json_files:
        return 0

    processed = downloads / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    saved = 0

    for json_file in json_files:
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            out_dir = content / data["novel_slug"]
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"chapter-{data['chapter_num']:04d}.txt"
            title = data["chapter_title"]
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"{title}\n{'=' * len(title)}\n\n")
                f.write(data["text"])
            shutil.move(str(json_file), processed / json_file.name)
            saved += 1
        except Exception:
            continue

    return saved


class CollectorThread(QThread):
    finished = pyqtSignal(int)   # total chapters saved across all sources

    def run(self) -> None:
        total = sum(_collect_source(src) for src in _SOURCES)
        self.finished.emit(total)
