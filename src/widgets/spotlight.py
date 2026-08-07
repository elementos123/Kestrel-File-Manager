import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QColor, QKeyEvent

from src.i18n import t
from src.logger import get_logger
from src import icon_provider as ico
from src.toggle_switch import ToggleSwitch

_log = get_logger("spotlight")


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
        accent = ToggleSwitch._C_ON
        self.setStyleSheet(f"""
            #SpotlightBar {{
                background: #252526;
                border: 1px solid #3a3a3a;
                border-radius: 14px;
            }}
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(14)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.input = QLineEdit()
        self.input.setPlaceholderText(t("spotlight.placeholder"))
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: #1e1e1e;
                border: 1px solid {accent.name()};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                color: white;
            }}
        """)
        self.input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input)

        self.results = QListWidget()
        self.results.setIconSize(QSize(18, 18))
        self.results.setSpacing(2)
        self.results.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 8px;
                color: #ccc;
            }}
            QListWidget::item:selected {{
                background: rgba({accent.red()},{accent.green()},{accent.blue()},0.30);
                color: white;
            }}
            QListWidget::item:hover {{
                background: rgba(255,255,255,0.06);
            }}
        """)
        self.results.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self.results)
        
        self._commands = [
            (t("spotlight.cmd.theme_dark"), "cmd:theme_dark"),
            (t("spotlight.cmd.theme_light"), "cmd:theme_light"),
            (t("spotlight.cmd.new_tab"), "cmd:new_tab"),
            (t("spotlight.cmd.new_folder"), "cmd:new_folder"),
            (t("spotlight.cmd.open_terminal"), "cmd:open_terminal"),
            (t("spotlight.cmd.settings"), "cmd:settings"),
            (t("spotlight.cmd.show_shortcuts"), "cmd:show_shortcuts"),
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
            item = QListWidgetItem(ico.bolt_icon("#61afef"), label)
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
                item = QListWidgetItem(ico.bolt_icon("#61afef"), label)
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
                            icon = ico.folder() if entry.is_dir() else ico.file_icon()
                            item = QListWidgetItem(icon, entry.name)
                            item.setData(Qt.ItemDataRole.UserRole, f"path:{entry.path}")
                            self.results.addItem(item)
                            count += 1
                            if count >= 20: break
            except Exception:
                _log.debug("Failed to scan %s for spotlight results", self._current_path, exc_info=True)

        # 3. Global search placeholder
        item = QListWidgetItem(ico.search_icon("#98c379"), t("spotlight.search_recursive", text=text))
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
