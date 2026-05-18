from PyQt6.QtWidgets import QTabWidget, QToolButton, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QAction

class TabWidget(QTabWidget):
    new_tab_requested  = pyqtSignal(str)   # path ("" = use current)
    duplicate_tab_path = pyqtSignal(str)   # path of the right-clicked tab

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)

        new_btn = QToolButton()
        new_btn.setText(" + ")
        new_btn.setToolTip("Nueva pestaña  Ctrl+T")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(
            "QToolButton { background: transparent; border: none;"
            "color: #666; font-size: 16px; padding: 0 8px; }"
            "QToolButton:hover { color: #ccc; background: #333; border-radius: 4px; }"
        )
        new_btn.clicked.connect(lambda: self.new_tab_requested.emit(""))
        self.setCornerWidget(new_btn, Qt.Corner.TopRightCorner)

        self.tabCloseRequested.connect(self._close_tab)
        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self._tab_context_menu)
        self.tabBar().installEventFilter(self)

    def _close_tab(self, index: int):
        if self.count() > 1:
            w = self.widget(index)
            self.removeTab(index)
            if w:
                w.deleteLater()

    def eventFilter(self, obj, event):
        if obj is self.tabBar() and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.MiddleButton:
                idx = self.tabBar().tabAt(event.position().toPoint())
                if idx >= 0:
                    self._close_tab(idx)
                    return True
        return super().eventFilter(obj, event)

    def _tab_context_menu(self, pos):
        index = self.tabBar().tabAt(pos)
        if index < 0:
            return
        menu = QMenu(self)

        # Get path of the right-clicked tab (not necessarily the active one)
        from src.file_panel import FilePanelTab
        w = self.widget(index)
        tab_path = w.current_path() if isinstance(w, FilePanelTab) else ""

        dup = QAction("Duplicar pestaña", self)
        dup.triggered.connect(lambda: self.duplicate_tab_path.emit(tab_path))
        menu.addAction(dup)

        close_others = QAction("Cerrar otras pestañas", self)
        close_others.triggered.connect(lambda: self._close_others(index))
        close_others.setEnabled(self.count() > 1)
        menu.addAction(close_others)

        close_right = QAction("Cerrar pestañas a la derecha", self)
        close_right.triggered.connect(lambda: self._close_right(index))
        close_right.setEnabled(index < self.count() - 1)
        menu.addAction(close_right)

        menu.addSeparator()
        close_act = QAction("Cerrar pestaña\tCtrl+W", self)
        close_act.triggered.connect(lambda: self._close_tab(index))
        close_act.setEnabled(self.count() > 1)
        menu.addAction(close_act)

        menu.exec(self.tabBar().mapToGlobal(pos))

    def _close_others(self, keep_index: int):
        for i in range(self.count() - 1, -1, -1):
            if i != keep_index:
                self._close_tab(i)

    def _close_right(self, from_index: int):
        for i in range(self.count() - 1, from_index, -1):
            self._close_tab(i)
