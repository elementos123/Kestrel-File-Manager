import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("UltraExplorer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("UltraExplorerProject")
    app.setStyle("Fusion")

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
