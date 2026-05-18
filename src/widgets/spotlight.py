import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QColor, QKeyEvent

class SpotlightBar(QFrame):
    """Global search and command bar (Ctrl+K)."""
    command_selected = pyqtSignal(str, str) # type ('path', 'cmd'), value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 400)
        self.setObjectName("SpotlightBar")
        self._current_path = ""
        
        from PyQt6.QtCore import QTimer
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(150) # 150ms debounce
        self._search_timer.timeout.connect(self._do_search)
        self.setStyleSheet("""
            #SpotlightBar {
                background: #252526;
                border: 1px solid #444;
                border-radius: 12px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Buscar archivos o comandos...  (Esc para cerrar)")
        self.input.setStyleSheet("""
            QLineEdit {
                background: #1e1e1e;
                border: 1px solid #0078d4;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 16px;
                color: white;
            }
        """)
        self.input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input)
        
        self.results = QListWidget()
        self.results.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                color: #ccc;
            }
            QListWidget::item:selected {
                background: #094771;
                color: white;
            }
            QListWidget::item:hover {
                background: #2a2d2e;
            }
        """)
        self.results.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self.results)
        
        self._commands = [
            ("Tema Oscuro", "cmd:theme_dark"),
            ("Tema Claro", "cmd:theme_light"),
            ("Nueva Pestaña", "cmd:new_tab"),
            ("Nueva Carpeta", "cmd:new_folder"),
            ("Abrir Terminal", "cmd:open_terminal"),
            ("Ver Configuración", "cmd:settings"),
        ]
        
        self.setFocusProxy(self.input)
        self.installEventFilter(self)

    def show_spotlight(self, current_path: str = ""):
        self._current_path = current_path
        self.input.clear()
        self._populate_initial()
        self.show()
        self.raise_()
        self.input.setFocus()
        
        # Center in parent
        if self.parentWidget():
            p = self.parentWidget().rect().center()
            self.move(p.x() - self.width() // 2, p.y() - self.height() // 2 - 100)

    def _populate_initial(self):
        self.results.clear()
        for label, cmd in self._commands:
            item = QListWidgetItem(f"⚡  {label}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            self.results.addItem(item)
        self.results.setCurrentRow(0)

    def _on_text_changed(self, text):
        self._search_timer.start()

    def _do_search(self):
        text = self.input.text().strip()
        if not text:
            self._populate_initial()
            return
            
        self.results.clear()
        query = text.lower()
        
        # 1. Commands matching
        for label, cmd in self._commands:
            if query in label.lower():
                item = QListWidgetItem(f"⚡  {label}")
                item.setData(Qt.ItemDataRole.UserRole, cmd)
                item.setForeground(QColor("#61afef"))
                self.results.addItem(item)
        
        # 2. Local File/Folder matching
        if self._current_path and os.path.isdir(self._current_path):
            try:
                # Use scandir for faster file enumeration
                with os.scandir(self._current_path) as it:
                    count = 0
                    for entry in it:
                        if query in entry.name.lower():
                            icon = "📁" if entry.is_dir() else "📄"
                            item = QListWidgetItem(f"{icon}  {entry.name}")
                            item.setData(Qt.ItemDataRole.UserRole, f"path:{entry.path}")
                            self.results.addItem(item)
                            count += 1
                            if count >= 20: break
            except Exception:
                pass

        # 3. Global search placeholder
        item = QListWidgetItem(f"🔍  Buscar '{text}' recursivamente...")
        item.setData(Qt.ItemDataRole.UserRole, f"search:{text}")
        item.setForeground(QColor("#98c379"))
        self.results.addItem(item)
        
        self.results.setCurrentRow(0)

    def _on_item_activated(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data.startswith("cmd:"):
            self.command_selected.emit("cmd", data[4:])
        elif data.startswith("path:"):
            self.command_selected.emit("path", data[5:])
        elif data.startswith("search:"):
            self.command_selected.emit("search", data[7:])
        self.hide()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key.Key_Escape:
                self.hide()
                return True
            if key_event.key() == Qt.Key.Key_Down:
                self.results.setCurrentRow((self.results.currentRow() + 1) % self.results.count())
                return True
            if key_event.key() == Qt.Key.Key_Up:
                self.results.setCurrentRow((self.results.currentRow() - 1) % self.results.count())
                return True
            if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                if self.results.currentItem():
                    self._on_item_activated(self.results.currentItem())
                return True
        return super().eventFilter(obj, event)
