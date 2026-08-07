import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.main_window import MainWindow
from src.logger import get_logger, LOG_FILE
from src.i18n import t, set_language
from src.settings_dialog import load_settings

_logger = get_logger("main")


def _install_excepthook():
    def _handle(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        _logger.critical(
            "Unhandled exception:\n%s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        )
        try:
            QMessageBox.critical(
                None,
                t("err.crash_title"),
                t("err.crash_body", log_path=str(LOG_FILE), error=str(exc_value)),
            )
        except Exception:
            pass

    sys.excepthook = _handle


def main():
    _install_excepthook()

    app = QApplication(sys.argv)
    app.setApplicationName("UltraExplorer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("UltraExplorerProject")
    app.setStyle("Fusion")

    settings = load_settings()
    set_language(settings.get("language", "auto"))

    # Handle command line argument (path to open)
    start_path = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.exists(arg):
            start_path = arg

    # Default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    if start_path:
        window._add_tab(start_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
