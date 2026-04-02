"""Top URL input bar."""

from __future__ import annotations

import qtawesome as qta
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from sites import SUPPORTED_SITES


class UrlBar(QWidget):
    go_requested = pyqtSignal(str)       # url
    sidebar_toggled = pyqtSignal()

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

        # Status label
        self._status_label = QLabel("")
        self._status_label.setFixedWidth(200)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._sidebar_btn)
        layout.addWidget(self._url_edit, stretch=1)
        layout.addWidget(self._go_btn)
        layout.addWidget(self._status_label)

    def _on_go(self) -> None:
        url = self._url_edit.text().strip()
        if url:
            self.go_requested.emit(url)

    # ------------------------------------------------------------------
    # Status helpers

    def set_status(self, text: str, error: bool = False) -> None:
        self._status_label.setText(text)
        color = "#f38ba8" if error else "#a6adc8"
        self._status_label.setStyleSheet(f"color: {color};")

    def set_fetching(self, fetching: bool) -> None:
        self._go_btn.setEnabled(not fetching)
        self._go_btn.setText("..." if fetching else "Go")
        if fetching:
            self.set_status("Fetching chapter...")
        else:
            self.set_status("")

    def set_url(self, url: str) -> None:
        self._url_edit.setText(url)
