"""Background thread for fetching and parsing a web chapter."""

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from sites import BaseSite, site_for_url


class FetcherThread(QThread):
    chapter_ready = pyqtSignal(str, list, str, str)  # title, paragraphs, next_url, prev_url
    fetch_error = pyqtSignal(str)

    def __init__(self, url: str, site: BaseSite | None = None):
        super().__init__()
        self._url = url
        self._site = site or site_for_url(url)

    def run(self) -> None:
        if self._site is None:
            self.fetch_error.emit(f"Unsupported site: {self._url}")
            return
        try:
            soup = self._site.fetch_chapter(self._url)
            title, text = self._site.extract_content(soup)
            if not text:
                self.fetch_error.emit("No chapter content found on page.")
                return
            paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
            next_url = self._site.find_next_url(soup, self._url) or ""
            prev_url = self._site.find_prev_url(soup, self._url) or ""
            self.chapter_ready.emit(title, paragraphs, next_url, prev_url)
        except Exception as e:
            self.fetch_error.emit(str(e))
