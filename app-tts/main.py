"""Entry point for the TTS Reader desktop app."""

import sys
from pathlib import Path

# Ensure app-tts/ is on sys.path so imports work regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
except ImportError:
    print("ERROR: PyQt6 not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    import win32com.client  # noqa: F401
except ImportError:
    app = QApplication(sys.argv)
    QMessageBox.critical(
        None,
        "Missing dependency",
        "pywin32 is required for speech synthesis.\n\nRun: pip install pywin32",
    )
    sys.exit(1)

from ui.main_window import MainWindow
from ui.theme import apply_dark_theme


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("TTS Reader")
    app.setApplicationDisplayName("TTS Reader")

    apply_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
