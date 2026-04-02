"""Main application window: assembles all panels and wires signals."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.collector import CollectorThread
from core.fetcher import FetcherThread
from core.library import (
    ChapterInfo,
    load_chapter_text,
    load_settings,
    next_chapter,
    prev_chapter,
    save_offline_bookmark,
    save_settings,
    save_web_bookmark,
)
from core.tts_worker import TTSWorker, get_available_voices
from sites import site_for_url

from .controls_bar import ControlsBar
from .reader_panel import ReaderPanel
from .sidebar import LibrarySidebar
from .toast import Toast
from .url_bar import UrlBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TTS Reader")
        self.setMinimumSize(1050, 680)
        self.resize(1200, 750)

        # State
        self._paragraphs: list[str] = []
        self._current_para_idx = 0
        self._next_url = ""
        self._prev_url = ""
        self._current_url = ""
        self._current_chapter_path: Path | None = None
        self._current_novel_source: str = ""
        self._current_novel_slug: str = ""
        self._worker: TTSWorker | None = None
        self._fetcher: FetcherThread | None = None
        self._collector: CollectorThread | None = None
        self._voices = get_available_voices()

        self._build_ui()
        self._wire_signals()

        # Populate voice selector with saved preference
        saved_voice = load_settings().get("voice", self._pick_voice())
        self._controls.populate_voices(self._voices, selected=saved_voice)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        self._url_bar = UrlBar()
        root.addWidget(self._url_bar)

        # Thin separator line
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        root.addWidget(sep)

        # Middle: sidebar + reader in a splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)

        self._sidebar = LibrarySidebar()
        self._reader = ReaderPanel()

        self._splitter.addWidget(self._sidebar)
        self._splitter.addWidget(self._reader)
        self._splitter.setSizes([230, 970])
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        root.addWidget(self._splitter, stretch=1)

        # Bottom separator
        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        root.addWidget(sep2)

        # Controls bar
        self._controls = ControlsBar()
        root.addWidget(self._controls)

        # Floating toast — child of central widget so it overlaps everything
        self._toast = Toast(central)

    def _wire_signals(self) -> None:
        # URL bar
        self._url_bar.go_requested.connect(self._on_go)
        self._url_bar.sidebar_toggled.connect(self._toggle_sidebar)
        self._url_bar.collect_requested.connect(self._on_collect)

        # Controls
        self._controls.play_clicked.connect(self._on_play)
        self._controls.pause_clicked.connect(self._on_pause)
        self._controls.stop_clicked.connect(self._on_stop)
        self._controls.prev_clicked.connect(self._on_prev_chapter)
        self._controls.next_clicked.connect(self._on_next_chapter)
        self._controls.rate_changed.connect(self._on_rate_changed)
        self._controls.volume_changed.connect(self._on_volume_changed)
        self._controls.voice_changed.connect(self._on_voice_changed)

        # Sidebar
        self._sidebar.chapter_selected.connect(self._on_offline_chapter_selected)

        # Reader click-to-seek
        self._reader.paragraph_clicked.connect(self._on_paragraph_clicked)

    # ------------------------------------------------------------------
    # URL fetch workflow
    # ------------------------------------------------------------------

    def _on_go(self, url: str) -> None:
        site = site_for_url(url)
        if site is None:
            self._toast.show_message("Unsupported site.", error=True)
            return

        self._stop_worker()
        self._url_bar.set_fetching(True)
        self._current_url = url

        self._fetcher = FetcherThread(url, site)
        self._fetcher.chapter_ready.connect(self._on_chapter_ready_web)
        self._fetcher.fetch_error.connect(self._on_fetch_error)
        self._fetcher.start()

    def _on_chapter_ready_web(self, title: str, paragraphs: list, next_url: str, prev_url: str) -> None:
        self._url_bar.set_fetching(False)
        self._toast.show_message(f"Loaded: {title[:60]}")
        self._next_url = next_url
        self._prev_url = prev_url
        self._current_chapter_path = None
        self._load_chapter(title, paragraphs)
        self._start_worker()

    def _on_collect(self) -> None:
        if self._collector and self._collector.isRunning():
            return
        self._url_bar._collect_btn.setEnabled(False)
        self._url_bar._collect_btn.setText("...")
        self._collector = CollectorThread()
        self._collector.finished.connect(self._on_collect_done)
        self._collector.start()

    def _on_collect_done(self, total: int) -> None:
        self._url_bar._collect_btn.setEnabled(True)
        self._url_bar._collect_btn.setText("Collect")
        if total:
            self._toast.show_message(f"Collected {total} chapter(s).")
            self._sidebar.refresh()
        else:
            self._toast.show_message("No new chapters found in Downloads.")

    def _on_fetch_error(self, msg: str) -> None:
        self._url_bar.set_fetching(False)
        self._toast.show_message(msg[:80], error=True)

    # ------------------------------------------------------------------
    # Offline library workflow
    # ------------------------------------------------------------------

    def _on_offline_chapter_selected(self, ch: ChapterInfo) -> None:
        self._stop_worker()
        title, paragraphs = load_chapter_text(ch.path)
        self._current_chapter_path = ch.path
        self._current_novel_source = self._sidebar._source_combo.currentText()
        self._current_novel_slug = ch.path.parent.name
        self._next_url = ""
        self._prev_url = ""
        self._url_bar.set_url("")
        self._toast.show_message(f"Offline: {title[:60]}")
        self._load_chapter(title, paragraphs)
        self._start_worker()
        self._sidebar.highlight_chapter(ch.path)

    # ------------------------------------------------------------------
    # Shared chapter loading
    # ------------------------------------------------------------------

    def _load_chapter(self, title: str, paragraphs: list[str]) -> None:
        self._paragraphs = paragraphs
        self._current_para_idx = 0
        self._reader.load_chapter(title, paragraphs)
        self._controls.set_progress(0, len(paragraphs))
        self._update_nav_buttons()

    # ------------------------------------------------------------------
    # TTS worker management
    # ------------------------------------------------------------------

    def _start_worker(self, start_index: int = 0) -> None:
        if not self._paragraphs:
            return
        self._stop_worker()

        voice = self._pick_voice()
        self._worker = TTSWorker(
            paragraphs=self._paragraphs,
            rate=self._controls.rate,
            volume=self._controls.volume,
            voice_name=voice,
            start_index=start_index,
        )
        self._worker.paragraph_started.connect(self._on_paragraph_started)
        self._worker.chapter_finished.connect(self._on_chapter_finished)
        self._worker.error.connect(self._on_tts_error)
        self._worker.start()
        self._controls.set_playing(True)

    def _stop_worker(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(2000)
        self._worker = None
        self._controls.set_playing(False)
        self._reader.clear_highlight()

    def _pick_voice(self) -> str:
        selected = self._controls.selected_voice
        if selected:
            return selected
        for name in self._voices:
            if "zira" in name.lower():
                return name
        for name in self._voices:
            if "en-us" in name.lower():
                return name
        return self._voices[0] if self._voices else ""

    def _on_voice_changed(self, voice: str) -> None:
        save_settings({"voice": voice})

    def _on_paragraph_clicked(self, index: int) -> None:
        self._current_para_idx = index
        self._start_worker(start_index=index)

    # ------------------------------------------------------------------
    # Controls callbacks
    # ------------------------------------------------------------------

    def _on_play(self) -> None:
        if self._worker and self._worker.isRunning():
            # Resume from pause
            self._worker.resume()
            self._controls.set_playing(True)
        else:
            # Start/restart from current position
            self._start_worker(start_index=self._current_para_idx)

    def _on_pause(self) -> None:
        if self._worker:
            self._worker.pause()
        self._controls.set_playing(False)

    def _on_stop(self) -> None:
        self._stop_worker()
        self._current_para_idx = 0
        self._controls.set_progress(0, len(self._paragraphs))

    def _on_prev_chapter(self) -> None:
        if self._current_chapter_path:
            prev = prev_chapter(self._current_chapter_path)
            if prev:
                self._on_offline_chapter_selected(_make_chapter_info(prev))
        elif self._prev_url:
            self._url_bar.set_url(self._prev_url)
            self._on_go(self._prev_url)

    def _on_next_chapter(self) -> None:
        if self._current_chapter_path:
            nxt = next_chapter(self._current_chapter_path)
            if nxt:
                self._on_offline_chapter_selected(_make_chapter_info(nxt))
        elif self._next_url:
            self._url_bar.set_url(self._next_url)
            self._on_go(self._next_url)

    def _on_rate_changed(self, rate: int) -> None:
        if self._worker:
            self._worker.set_rate(rate)

    def _on_volume_changed(self, volume: int) -> None:
        if self._worker:
            self._worker.set_volume(volume)

    # ------------------------------------------------------------------
    # Worker signal handlers
    # ------------------------------------------------------------------

    def _on_paragraph_started(self, index: int) -> None:
        self._current_para_idx = index
        self._reader.highlight_paragraph(index)
        self._controls.set_progress(index, len(self._paragraphs))

    def _on_chapter_finished(self) -> None:
        self._controls.set_playing(False)
        self._reader.clear_highlight()
        self._save_current_bookmark()

        # Auto-advance
        if self._current_chapter_path:
            nxt = next_chapter(self._current_chapter_path)
            if nxt:
                self._on_offline_chapter_selected(_make_chapter_info(nxt))
                return
        elif self._next_url:
            self._url_bar.set_url(self._next_url)
            self._on_go(self._next_url)
            return

        self._toast.show_message("Finished — no more chapters.")

    def _on_tts_error(self, msg: str) -> None:
        self._controls.set_playing(False)
        self._toast.show_message(f"TTS error: {msg[:80]}", error=True)

    # ------------------------------------------------------------------
    # Bookmarks
    # ------------------------------------------------------------------

    def _save_current_bookmark(self) -> None:
        if self._current_chapter_path:
            save_offline_bookmark(
                self._current_novel_source,
                self._current_novel_slug,
                self._current_chapter_path.name,
            )
            self._sidebar.refresh()
        elif self._current_url:
            save_web_bookmark(self._current_url, self._next_url)

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def _toggle_sidebar(self) -> None:
        visible = self._sidebar.isVisible()
        self._sidebar.setVisible(not visible)

    def _update_nav_buttons(self) -> None:
        has_prev = has_next = False
        if self._current_chapter_path:
            has_prev = prev_chapter(self._current_chapter_path) is not None
            has_next = next_chapter(self._current_chapter_path) is not None
        elif self._current_url:
            has_prev = bool(self._prev_url)
            has_next = bool(self._next_url)
        self._controls.set_chapter_nav_enabled(has_prev, has_next)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._toast.reposition()

    def closeEvent(self, event) -> None:
        self._save_current_bookmark()
        self._stop_worker()
        super().closeEvent(event)


def _make_chapter_info(path: Path):
    """Create a minimal ChapterInfo from a path for internal navigation."""
    from core.library import ChapterInfo
    try:
        num = int(path.stem.split("-")[1])
    except (IndexError, ValueError):
        num = 0
    return ChapterInfo(path=path, display_name=f"Chapter {num:04d}", number=num)
