"""Top URL input bar."""

from __future__ import annotations

import qtawesome as qta
from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

from sites import SUPPORTED_SITES


class UrlBar(QWidget):
    go_requested = pyqtSignal(str)       # url
    sidebar_toggled = pyqtSignal()
    collect_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Sidebar toggle
        self._sidebar_btn = QPushButton()
        self._sidebar_btn.setIcon(qta.icon("fa5s.book-open", color="#cdd6f4"))
        self._sidebar_btn.setIconSize(QSize(16, 16))
        self._sidebar_btn.setFixedSize(36, 36)
        self._sidebar_btn.setToolTip("Toggle library sidebar")
        self._sidebar_btn.clicked.connect(self.sidebar_toggled)

        # URL input
        supported = ", ".join(SUPPORTED_SITES)
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(f"Paste chapter URL ({supported})...")
        self._url_edit.returnPressed.connect(self._on_go)

        # Go button
        self._go_btn = QPushButton("Go")
        self._go_btn.setFixedWidth(60)
        self._go_btn.setFixedHeight(36)
        self._go_btn.clicked.connect(self._on_go)

        # Collect button
        self._collect_btn = QPushButton("Collect")
        self._collect_btn.setFixedHeight(36)
        self._collect_btn.setToolTip("Import downloaded chapters from fictionzone-tts / novelhall-tts in Downloads")
        self._collect_btn.clicked.connect(self.collect_requested)

        layout.addWidget(self._sidebar_btn)
        layout.addWidget(self._url_edit, stretch=1)
        layout.addWidget(self._go_btn)
        layout.addWidget(self._collect_btn)

    def _on_go(self) -> None:
        url = self._url_edit.text().strip()
        if url:
            self.go_requested.emit(url)

    # ------------------------------------------------------------------
    # Status helpers

    def set_fetching(self, fetching: bool) -> None:
        self._go_btn.setEnabled(not fetching)
        self._go_btn.setText("..." if fetching else "Go")

    def set_url(self, url: str) -> None:
        self._url_edit.setText(url)
