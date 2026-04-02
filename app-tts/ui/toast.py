"""Floating toast notification — bottom-center, above the controls bar."""

from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget

_CONTROLS_H = 70   # must match ControlsBar.setFixedHeight
_PADDING_Y  = 16   # gap above controls bar
_PADDING_X  = 32   # horizontal inner padding


class Toast(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(_PADDING_X, 0, _PADDING_X, 0)
        layout.addWidget(self._label)

        self.setStyleSheet("""
            Toast {
                background: #313244;
                border-radius: 10px;
            }
        """)
        self.setFixedHeight(40)

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)

        self._fade_anim = QPropertyAnimation(self._effect, b"opacity")
        self._fade_anim.setDuration(220)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._start_fade_out)

        self.hide()

    # ------------------------------------------------------------------

    def show_message(self, text: str, error: bool = False, duration: int = 3000) -> None:
        if not text:
            self._start_fade_out()
            return

        color = "#f38ba8" if error else "#cdd6f4"
        self._label.setStyleSheet(f"color: {color}; background: transparent;")
        self._label.setText(text)

        self.adjustSize()
        self.setFixedHeight(40)
        self._reposition()
        self.show()
        self.raise_()

        self._hide_timer.stop()
        self._fade_anim.stop()
        self._fade_anim.setStartValue(self._effect.opacity())
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()

        self._hide_timer.start(duration)

    def _start_fade_out(self) -> None:
        self._fade_anim.stop()
        self._fade_anim.setStartValue(self._effect.opacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.finished.connect(self._on_fade_out_done)
        self._fade_anim.start()

    def _on_fade_out_done(self) -> None:
        self._fade_anim.finished.disconnect(self._on_fade_out_done)
        if self._effect.opacity() == 0.0:
            self.hide()

    # ------------------------------------------------------------------

    def _reposition(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        pw, ph = parent.width(), parent.height()
        w = min(self._label.sizeHint().width() + _PADDING_X * 2, pw - 40)
        self.setFixedWidth(w)
        x = (pw - w) // 2
        y = ph - _CONTROLS_H - _PADDING_Y - self.height()
        self.move(x, y)

    def reposition(self) -> None:
        """Call from parent's resizeEvent to keep toast centered."""
        if self.isVisible():
            self._reposition()
