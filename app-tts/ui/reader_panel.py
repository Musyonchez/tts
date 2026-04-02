"""Center panel: chapter title + text display with paragraph highlighting."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QTextBlockFormat, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from .theme import COLORS, PARA_HIGHLIGHT_BG, PARA_HIGHLIGHT_FG


class _ClickableTextEdit(QTextEdit):
    """QTextEdit that emits the character position of each click."""
    char_clicked = pyqtSignal(int)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        super().mousePressEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(e.pos())
            self.char_clicked.emit(cursor.position())


class ReaderPanel(QWidget):
    paragraph_clicked = pyqtSignal(int)  # paragraph index
    def __init__(self, parent=None):
        super().__init__(parent)
        self._para_ranges: list[tuple[int, int]] = []
        self._current_para = -1
        self._build_ui()
        self._build_formats()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._title_label = QLabel("—")
        self._title_label.setObjectName("chapterTitle")
        self._title_label.setWordWrap(True)

        self._text_edit = _ClickableTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.char_clicked.connect(self._on_char_clicked)
        self._text_edit.setFont(QFont("Segoe UI", 11))
        self._text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._text_edit.setStyleSheet(
            f"QTextEdit {{ background-color: {COLORS['mantle']}; "
            f"color: {COLORS['text']}; border: none; "
            f"padding: 16px 24px; line-height: 1.6; }}"
        )

        # Placeholder text
        self._text_edit.setPlaceholderText(
            "Paste a chapter URL above and click Go, or select a chapter from the library."
        )

        layout.addWidget(self._title_label)
        layout.addWidget(self._text_edit, stretch=1)

    def _build_formats(self) -> None:
        self._default_fmt = QTextCharFormat()
        self._default_fmt.setBackground(QColor(COLORS["mantle"]))
        self._default_fmt.setForeground(QColor(COLORS["text"]))

        self._highlight_fmt = QTextCharFormat()
        self._highlight_fmt.setBackground(QColor(PARA_HIGHLIGHT_BG))
        self._highlight_fmt.setForeground(QColor(PARA_HIGHLIGHT_FG))

    # ------------------------------------------------------------------
    # Public API

    def load_chapter(self, title: str, paragraphs: list[str]) -> None:
        self._title_label.setText(title)
        self._para_ranges = []
        self._current_para = -1

        doc = self._text_edit.document()
        self._text_edit.clear()

        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # Block format for comfortable reading
        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(160, 1)  # 160% = 1 (ProportionalHeight)
        block_fmt.setBottomMargin(10)

        char_fmt = QTextCharFormat()
        char_fmt.setFont(QFont("Segoe UI", 11))
        char_fmt.setForeground(QColor(COLORS["text"]))

        for i, para in enumerate(paragraphs):
            start = cursor.position()
            cursor.insertBlock(block_fmt, char_fmt)
            # Remove the extra leading newline from insertBlock on first para
            if i == 0:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                start = 0
            cursor.movePosition(QTextCursor.MoveOperation.End)
            # Re-position to actual start of this block
            start = doc.findBlockByNumber(i).position()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(para, char_fmt)
            end = cursor.position()
            self._para_ranges.append((start, end))
            cursor.movePosition(QTextCursor.MoveOperation.End)

        self._text_edit.moveCursor(QTextCursor.MoveOperation.Start)

    def highlight_paragraph(self, index: int) -> None:
        if not self._para_ranges or index >= len(self._para_ranges):
            return

        # Clear previous highlight
        if 0 <= self._current_para < len(self._para_ranges):
            self._apply_format(self._current_para, self._default_fmt)

        self._current_para = index
        self._apply_format(index, self._highlight_fmt)

        # Scroll to keep it visible
        start, _ = self._para_ranges[index]
        cursor = QTextCursor(self._text_edit.document())
        cursor.setPosition(start)
        self._text_edit.setTextCursor(cursor)
        self._text_edit.ensureCursorVisible()

    def clear_highlight(self) -> None:
        if 0 <= self._current_para < len(self._para_ranges):
            self._apply_format(self._current_para, self._default_fmt)
        self._current_para = -1

    def clear(self) -> None:
        self._title_label.setText("—")
        self._text_edit.clear()
        self._para_ranges = []
        self._current_para = -1

    # ------------------------------------------------------------------

    def _on_char_clicked(self, pos: int) -> None:
        for i, (start, end) in enumerate(self._para_ranges):
            if start <= pos <= end:
                self.paragraph_clicked.emit(i)
                return

    def _apply_format(self, index: int, fmt: QTextCharFormat) -> None:
        start, end = self._para_ranges[index]
        cursor = QTextCursor(self._text_edit.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(fmt)
