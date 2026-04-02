"""Catppuccin Mocha dark theme via Fusion style + QPalette."""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


# Catppuccin Mocha
_C = {
    "base":    "#1e1e2e",
    "mantle":  "#181825",
    "crust":   "#11111b",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "text":    "#cdd6f4",
    "subtext": "#a6adc8",
    "blue":    "#89b4fa",
    "lavender":"#b4befe",
    "red":     "#f38ba8",
    "green":   "#a6e3a1",
    "yellow":  "#f9e2af",
    "peach":   "#fab387",
}


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    pal = QPalette()

    def c(key: str) -> QColor:
        return QColor(_C[key])

    pal.setColor(QPalette.ColorRole.Window,          c("base"))
    pal.setColor(QPalette.ColorRole.WindowText,      c("text"))
    pal.setColor(QPalette.ColorRole.Base,            c("mantle"))
    pal.setColor(QPalette.ColorRole.AlternateBase,   c("surface0"))
    pal.setColor(QPalette.ColorRole.ToolTipBase,     c("surface1"))
    pal.setColor(QPalette.ColorRole.ToolTipText,     c("text"))
    pal.setColor(QPalette.ColorRole.Text,            c("text"))
    pal.setColor(QPalette.ColorRole.Button,          c("surface0"))
    pal.setColor(QPalette.ColorRole.ButtonText,      c("text"))
    pal.setColor(QPalette.ColorRole.BrightText,      c("red"))
    pal.setColor(QPalette.ColorRole.Link,            c("blue"))
    pal.setColor(QPalette.ColorRole.Highlight,       c("blue"))
    pal.setColor(QPalette.ColorRole.HighlightedText, c("base"))
    pal.setColor(QPalette.ColorRole.PlaceholderText, c("overlay0"))

    # Disabled
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, c("surface2"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       c("surface2"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, c("surface2"))

    app.setPalette(pal)

    # Extra stylesheet tweaks
    app.setStyleSheet("""
        QScrollBar:vertical {
            background: #181825;
            width: 8px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #45475a;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover { background: #585b70; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

        QScrollBar:horizontal {
            background: #181825;
            height: 8px;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background: #45475a;
            border-radius: 4px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover { background: #585b70; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

        QToolTip {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            padding: 4px;
        }

        QPushButton {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 5px 14px;
        }
        QPushButton:hover  { background-color: #45475a; }
        QPushButton:pressed { background-color: #585b70; }
        QPushButton:disabled { color: #585b70; border-color: #313244; }

        QPushButton#playBtn {
            background-color: #89b4fa;
            color: #1e1e2e;
            font-weight: bold;
            border: none;
            border-radius: 6px;
            min-width: 80px;
        }
        QPushButton#playBtn:hover  { background-color: #b4befe; }
        QPushButton#playBtn:pressed { background-color: #74c7ec; }

        QLineEdit {
            background-color: #181825;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 5px 10px;
            selection-background-color: #89b4fa;
            selection-color: #1e1e2e;
        }
        QLineEdit:focus { border-color: #89b4fa; }

        QListWidget {
            background-color: #181825;
            border: none;
            outline: none;
        }
        QListWidget::item {
            padding: 6px 10px;
            border-radius: 4px;
            color: #cdd6f4;
        }
        QListWidget::item:hover     { background-color: #313244; }
        QListWidget::item:selected  { background-color: #45475a; color: #cdd6f4; }

        QSlider::groove:horizontal {
            background: #313244;
            height: 4px;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #89b4fa;
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        QSlider::handle:horizontal:hover { background: #b4befe; }
        QSlider::sub-page:horizontal { background: #89b4fa; border-radius: 2px; }

        QComboBox {
            background-color: #313244;
            color: #cdd6f4;
            border: 1px solid #45475a;
            border-radius: 6px;
            padding: 4px 8px;
        }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            background-color: #313244;
            color: #cdd6f4;
            selection-background-color: #45475a;
        }

        QSplitter::handle { background: #313244; width: 1px; }

        QLabel#sectionLabel {
            color: #89b4fa;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 10px 2px;
        }

        QLabel#chapterTitle {
            color: #cdd6f4;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 20px 4px;
        }

        QFrame#separator {
            background: #313244;
            max-height: 1px;
        }
    """)


COLORS = _C
PARA_HIGHLIGHT_BG = "#2a3f5f"   # muted blue for current paragraph background
PARA_HIGHLIGHT_FG = "#cdd6f4"   # keep text color the same
