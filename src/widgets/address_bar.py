from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtCore import Qt, pyqtSignal, QDir
from PyQt6.QtGui import QFileSystemModel

class AddressBar(QLineEdit):
    navigate_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ruta…")
        self.returnPressed.connect(self._on_enter)

        # File system path completer
        self._fs_model = QFileSystemModel(self)
        self._fs_model.setRootPath("")
        self._fs_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        self._completer = QCompleter(self._fs_model, self)
        self._completer.setCompletionColumn(0)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(10)
        self.setCompleter(self._completer)

    def update_recent(self, _paths: list[str]):
        pass  # completer now uses real file system

    def _on_enter(self):
        path = self.text().strip()
        if path:
            self.navigate_requested.emit(path)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()
