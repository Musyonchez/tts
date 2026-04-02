"""Left sidebar: offline library browser."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.library import NovelInfo, list_novels, load_offline_bookmark


class LibrarySidebar(QWidget):
    chapter_selected = pyqtSignal(object)   # ChapterInfo (has .path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self._novels: list[NovelInfo] = []
        self._current_novel: NovelInfo | None = None
        self._build_ui()
        self._load_source("fictionzone")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)

        # Source picker
        self._source_combo = QComboBox()
        self._source_combo.addItems(["fictionzone", "novelhall"])
        self._source_combo.setContentsMargins(8, 0, 8, 0)
        self._source_combo.currentTextChanged.connect(self._load_source)

        novel_label = QLabel("Novels")
        novel_label.setObjectName("sectionLabel")

        self._novel_list = QListWidget()
        self._novel_list.setAlternatingRowColors(False)
        self._novel_list.currentItemChanged.connect(self._on_novel_selected)

        chapter_label = QLabel("Chapters")
        chapter_label.setObjectName("sectionLabel")

        self._chapter_list = QListWidget()
        self._chapter_list.setAlternatingRowColors(False)
        self._chapter_list.itemDoubleClicked.connect(self._on_chapter_double_clicked)

        layout.addWidget(self._source_combo)
        layout.addWidget(novel_label)
        layout.addWidget(self._novel_list, stretch=2)
        layout.addWidget(chapter_label)
        layout.addWidget(self._chapter_list, stretch=3)

    # ------------------------------------------------------------------

    def _load_source(self, source: str) -> None:
        self._novels = list_novels(source)
        self._novel_list.clear()
        self._chapter_list.clear()
        self._current_novel = None

        for novel in self._novels:
            item = QListWidgetItem(novel.display_name)
            item.setData(Qt.ItemDataRole.UserRole, novel)
            item.setToolTip(f"{novel.chapter_count} chapters")
            self._novel_list.addItem(item)

    def refresh(self) -> None:
        source = self._source_combo.currentText()
        # Re-read bookmarks for current novels
        self._novels = list_novels(source)
        self._refresh_chapter_list()

    def _on_novel_selected(self, current: QListWidgetItem | None, _prev) -> None:
        if current is None:
            return
        novel: NovelInfo = current.data(Qt.ItemDataRole.UserRole)
        self._current_novel = novel
        self._refresh_chapter_list()

    def _refresh_chapter_list(self) -> None:
        self._chapter_list.clear()
        if self._current_novel is None:
            return

        # Re-load bookmark for this novel
        bookmarked = load_offline_bookmark(
            self._current_novel.source, self._current_novel.slug
        )

        for ch in self._current_novel.chapters:
            name = ch.display_name
            if bookmarked and ch.path.name == bookmarked:
                name = f"🔖 {name}"
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, ch)
            self._chapter_list.addItem(item)

    def _on_chapter_double_clicked(self, item: QListWidgetItem) -> None:
        from core.library import ChapterInfo
        ch: ChapterInfo = item.data(Qt.ItemDataRole.UserRole)
        self.chapter_selected.emit(ch)

    def highlight_chapter(self, path: Path) -> None:
        """Visually select the chapter row matching path."""
        for i in range(self._chapter_list.count()):
            item = self._chapter_list.item(i)
            ch = item.data(Qt.ItemDataRole.UserRole)
            if ch and ch.path == path:
                self._chapter_list.setCurrentItem(item)
                self._chapter_list.scrollToItem(item)
                break
