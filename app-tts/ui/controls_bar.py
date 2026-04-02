"""Bottom playback controls bar."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QWidget,
)


class ControlsBar(QWidget):
    # Signals emitted to MainWindow
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    rate_changed = pyqtSignal(int)     # -10..10
    volume_changed = pyqtSignal(int)   # 0..100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self._playing = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)

        # Prev
        self._prev_btn = QPushButton("⏮")
        self._prev_btn.setFixedSize(36, 36)
        self._prev_btn.setToolTip("Previous chapter")
        self._prev_btn.clicked.connect(self.prev_clicked)

        # Play/Pause
        self._play_btn = QPushButton("▶  Play")
        self._play_btn.setObjectName("playBtn")
        self._play_btn.setFixedHeight(36)
        self._play_btn.setToolTip("Play / Pause")
        self._play_btn.clicked.connect(self._on_play_pause)

        # Stop
        self._stop_btn = QPushButton("⏹")
        self._stop_btn.setFixedSize(36, 36)
        self._stop_btn.setToolTip("Stop")
        self._stop_btn.clicked.connect(self.stop_clicked)

        # Next
        self._next_btn = QPushButton("⏭")
        self._next_btn.setFixedSize(36, 36)
        self._next_btn.setToolTip("Next chapter")
        self._next_btn.clicked.connect(self.next_clicked)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(30)

        # Rate slider
        rate_label = QLabel("Speed")
        rate_label.setFixedWidth(42)
        self._rate_slider = QSlider(Qt.Orientation.Horizontal)
        self._rate_slider.setRange(-10, 10)
        self._rate_slider.setValue(6)
        self._rate_slider.setFixedWidth(130)
        self._rate_slider.setToolTip("Speech rate (-10 to +10)")
        self._rate_val_label = QLabel(f"+{self._rate_slider.value()}")
        self._rate_val_label.setFixedWidth(28)
        self._rate_slider.valueChanged.connect(self._on_rate_changed)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setFixedHeight(30)

        # Volume slider
        vol_label = QLabel("Vol")
        vol_label.setFixedWidth(26)
        self._vol_slider = QSlider(Qt.Orientation.Horizontal)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(100)
        self._vol_slider.setFixedWidth(110)
        self._vol_slider.setToolTip("Volume (0–100)")
        self._vol_val_label = QLabel("100")
        self._vol_val_label.setFixedWidth(28)
        self._vol_slider.valueChanged.connect(self._on_volume_changed)

        # Progress label (right side)
        self._progress_label = QLabel("")
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._prev_btn)
        layout.addWidget(self._play_btn)
        layout.addWidget(self._stop_btn)
        layout.addWidget(self._next_btn)
        layout.addWidget(sep)
        layout.addWidget(rate_label)
        layout.addWidget(self._rate_slider)
        layout.addWidget(self._rate_val_label)
        layout.addWidget(sep2)
        layout.addWidget(vol_label)
        layout.addWidget(self._vol_slider)
        layout.addWidget(self._vol_val_label)
        layout.addStretch()
        layout.addWidget(self._progress_label)

    # ------------------------------------------------------------------

    def _on_play_pause(self) -> None:
        if self._playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()

    def _on_rate_changed(self, value: int) -> None:
        sign = "+" if value >= 0 else ""
        self._rate_val_label.setText(f"{sign}{value}")
        self.rate_changed.emit(value)

    def _on_volume_changed(self, value: int) -> None:
        self._vol_val_label.setText(str(value))
        self.volume_changed.emit(value)

    # ------------------------------------------------------------------
    # State updates called by MainWindow

    def set_playing(self, playing: bool) -> None:
        self._playing = playing
        if playing:
            self._play_btn.setText("⏸  Pause")
        else:
            self._play_btn.setText("▶  Play")

    def set_progress(self, current: int, total: int) -> None:
        if total > 0:
            self._progress_label.setText(f"Para {current + 1} / {total}")
        else:
            self._progress_label.clear()

    def set_chapter_nav_enabled(self, prev: bool, next_: bool) -> None:
        self._prev_btn.setEnabled(prev)
        self._next_btn.setEnabled(next_)

    @property
    def rate(self) -> int:
        return self._rate_slider.value()

    @property
    def volume(self) -> int:
        return self._vol_slider.value()
