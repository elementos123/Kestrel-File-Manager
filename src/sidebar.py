import os
import json
import shutil
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QProgressBar, QHBoxLayout, QToolButton,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QColor, QPalette

from src.utils import get_drives, get_drive_label, get_user_dirs
from src import icon_provider as ico
from src.i18n import t
from src.logger import get_logger
from src.toggle_switch import ToggleSwitch

_log = get_logger("sidebar")


BOOKMARKS_FILE = str(Path.home() / ".file_explorer_bookmarks.json")


def _load_bookmarks() -> list[str]:
    try:
        with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [p for p in data if os.path.isdir(p)]
    except Exception:
        return []


def _save_bookmarks(bm: list[str]) -> None:
    try:
        with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(bm, f, indent=2)
    except Exception:
        pass


class _SidebarItem(QPushButton):
    def __init__(self, icon_arg, label: str, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.setObjectName("SidebarItem")
        self.setToolTip(path)
        self.setAccessibleName(label)
        self.setAccessibleDescription(path)
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.setFlat(True)
        self.setMinimumHeight(32)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Accept QIcon or emoji string
        from PyQt6.QtGui import QIcon
        if isinstance(icon_arg, QIcon):
            self.setIcon(icon_arg)
            self.setIconSize(QSize(16, 16))
            self.setText(f"  {label}")
        else:
            self.setText(f"{icon_arg}  {label}" if icon_arg else f"  {label}")

        accent = ToggleSwitch._C_ON.name()
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 6px 10px 6px 9px;
                border: none;
                border-left: 3px solid transparent;
                border-radius: 6px;
                background: transparent;
                color: #b0b0b0;
                font-size: 13px;
            }}
            QPushButton:hover  {{ background: rgba(255,255,255,0.06); color: white; }}
            QPushButton:checked {{
                background: rgba({QColor(accent).red()},{QColor(accent).green()},{QColor(accent).blue()},0.18);
                border-left: 3px solid {accent};
                color: white;
                font-weight: 600;
            }}
            QPushButton:focus  {{ border: 2px solid {accent}; padding: 5px 9px 5px 8px; }}
        """)


class _SectionHeader(QWidget):
    toggled_collapsed = pyqtSignal(bool)

    def __init__(self, title: str, collapsible: bool = True, parent=None):
        super().__init__(parent)
        self._collapsed = False
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 16, 8, 6)
        layout.setSpacing(4)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {ToggleSwitch._C_ON.name()};
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.9px;
            }}
        """)
        layout.addWidget(lbl, 1)

        if collapsible:
            self._arrow = QToolButton()
            self._arrow.setText("▾")
            self._arrow.setFixedSize(18, 18)
            self._arrow.setCursor(Qt.CursorShape.PointingHandCursor)
            self._arrow.setToolTip(t("sidebar.collapse_expand"))
            self._arrow.setStyleSheet("""
                QToolButton { 
                    border: none; 
                    color: #555; 
                    font-size: 10px; 
                    background: transparent;
                }
                QToolButton:hover { color: #aaa; background: #2a2a2a; border-radius: 4px; }
            """)
            self._arrow.clicked.connect(self._toggle)
            layout.addWidget(self._arrow)

    def _toggle(self):
        self._collapsed = not self._collapsed
        self._arrow.setText("▸" if self._collapsed else "▾")
        self.toggled_collapsed.emit(self._collapsed)


class _DriveWidget(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, drive: str, parent=None):
        super().__init__(parent)
        self.drive = drive
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(drive)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(get_drive_label(drive))
        self.setAccessibleDescription(drive)

        main = QVBoxLayout(self)
        main.setContentsMargins(14, 10, 14, 10)
        main.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(10)
        self._icon_lbl = QLabel()
        self._icon_lbl.setPixmap(ico.drive_icon("#8a8a8a").pixmap(18, 18))
        self._icon_lbl.setFixedWidth(18)

        name = get_drive_label(drive)
        self._name_lbl = QLabel(name)
        self._name_lbl.setStyleSheet("color: #ddd; font-size: 13px; font-weight: 600;")
        self._name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        top.addWidget(self._icon_lbl)
        top.addWidget(self._name_lbl, 1)
        main.addLayout(top)

        self._bar = QProgressBar()
        self._bar.setFixedHeight(5)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 100)
        main.addWidget(self._bar)

        self._space_lbl = QLabel("")
        self._space_lbl.setStyleSheet("color: #808080; font-size: 10px; letter-spacing: 0.2px;")
        main.addWidget(self._space_lbl)

        self._refresh_space()

        # Timer to refresh space info periodically
        timer = QTimer(self)
        timer.timeout.connect(self._refresh_space)
        timer.start(60_000)

        self.setStyleSheet(f"""
            QWidget {{ background: transparent; border-radius: 6px; }}
            QWidget:hover {{ background: rgba(255,255,255,0.06); }}
            QWidget:focus {{ border: 2px solid {ToggleSwitch._C_ON.name()}; }}
        """)

    def _refresh_space(self):
        try:
            usage = shutil.disk_usage(self.drive)
            pct   = int((usage.used / usage.total) * 100) if usage.total else 0
            free  = usage.free  / (1024**3)
            total = usage.total / (1024**3)
            self._bar.setValue(pct)
            
            accent = ToggleSwitch._C_ON.name()
            if pct > 90: accent = "#f44747"
            elif pct > 75: accent = "#d19a66"
            
            self._bar.setStyleSheet(f"""
                QProgressBar {{ background: #1e1e1e; border-radius: 2px; border: none; }}
                QProgressBar::chunk {{ background: {accent}; border-radius: 2px; }}
            """)
            self._space_lbl.setText(t("sidebar.free_of", free=free, total=total))
        except Exception:
            _log.debug("Failed to read disk usage for %s", self.drive, exc_info=True)
            self._space_lbl.setText("")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.drive)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit(self.drive)
            return
        super().keyPressEvent(event)


class Sidebar(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(180)
        self.setMaximumWidth(300)
        self.setAcceptDrops(True)

        self._buttons:    list[_SidebarItem]  = []
        self._bookmarks:  list[str]           = _load_bookmarks()
        self._bm_buttons: list[_SidebarItem]  = []
        self._drive_widgets: list[_DriveWidget] = []

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)

        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(1)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._build_quick_access()
        self._build_drives()
        self._build_bookmarks_section()
        self._build_recent_files_section()
        self._layout.addStretch()

    # ── Quick access ──────────────────────────────────────

    def _build_quick_access(self):
        hdr = _SectionHeader(t("sidebar.quick_access"))
        hdr.toggled_collapsed.connect(lambda c, w=None: self._toggle_section("qa", c))
        self._layout.addWidget(hdr)

        self._qa_container = QWidget()
        self._qa_container.setStyleSheet("background: transparent;")
        qa_layout = QVBoxLayout(self._qa_container)
        qa_layout.setContentsMargins(0, 0, 0, 0)
        qa_layout.setSpacing(1)

        for label, path in get_user_dirs().items():
            # Strip emoji prefix to get the clean name
            clean = label.strip().split()[-1]
            qicon = ico.for_dir_label(clean)
            btn = _SidebarItem(qicon, clean, path)
            btn.clicked.connect(lambda _, p=path: self._on_navigate(p))
            self._buttons.append(btn)
            qa_layout.addWidget(btn)

        self._layout.addWidget(self._qa_container)
        self._layout.addSpacing(4)

    # ── Drives ────────────────────────────────────────────

    def _build_drives(self):
        drives = get_drives()
        if not drives:
            return

        hdr = _SectionHeader(t("sidebar.this_pc"))
        hdr.toggled_collapsed.connect(lambda c: self._toggle_section("drives", c))
        self._layout.addWidget(hdr)

        self._drives_container = QWidget()
        self._drives_container.setStyleSheet("background: transparent;")
        d_layout = QVBoxLayout(self._drives_container)
        d_layout.setContentsMargins(0, 0, 0, 0)
        d_layout.setSpacing(2)

        for drive in drives:
            dw = _DriveWidget(drive)
            dw.clicked.connect(self._on_navigate)
            self._drive_widgets.append(dw)
            d_layout.addWidget(dw)

        self._layout.addWidget(self._drives_container)
        self._layout.addSpacing(4)

    # ── Bookmarks ─────────────────────────────────────────

    def _build_bookmarks_section(self):
        self._bm_header = _SectionHeader(t("sidebar.bookmarks"))
        self._bm_header.toggled_collapsed.connect(lambda c: self._toggle_section("bm", c))
        self._layout.addWidget(self._bm_header)

        self._bm_container = QWidget()
        self._bm_container.setStyleSheet("background: transparent;")
        self._bm_layout = QVBoxLayout(self._bm_container)
        self._bm_layout.setContentsMargins(0, 0, 0, 0)
        self._bm_layout.setSpacing(1)
        self._layout.addWidget(self._bm_container)
        self._refresh_bookmarks_ui()

    def _refresh_bookmarks_ui(self):
        while self._bm_layout.count():
            item = self._bm_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._bm_buttons.clear()

        for path in self._bookmarks:
            name = Path(path).name or path
            btn  = _SidebarItem(ico.star_icon(), name, path)
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, p=path: self._bm_context_menu(p)
            )
            btn.clicked.connect(lambda _, p=path: self._on_navigate(p))
            self._bm_buttons.append(btn)
            self._bm_layout.addWidget(btn)

        if not self._bookmarks:
            hint = QLabel(t("sidebar.drag_hint"))
            hint.setStyleSheet("color: #444; font-size: 11px; padding: 6px 14px;")
            self._bm_layout.addWidget(hint)

    def _bm_context_menu(self, path: str):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        menu = QMenu(self)
        remove_act = QAction(t("sidebar.remove_bookmark"), self)
        remove_act.triggered.connect(lambda: self.remove_bookmark(path))
        menu.addAction(remove_act)
        menu.exec(self.cursor().pos())

    def add_bookmark(self, path: str) -> bool:
        path = os.path.normpath(path)
        existing = {os.path.normcase(os.path.normpath(p)) for p in self._bookmarks}
        if os.path.normcase(path) not in existing and os.path.isdir(path):
            self._bookmarks.append(path)
            _save_bookmarks(self._bookmarks)
            self._refresh_bookmarks_ui()
            return True
        return False

    def remove_bookmark(self, path: str):
        if path in self._bookmarks:
            self._bookmarks.remove(path)
            _save_bookmarks(self._bookmarks)
            self._refresh_bookmarks_ui()

    def set_active_path(self, path: str):
        norm = os.path.normcase(path)
        for btn in self._buttons + self._bm_buttons:
            active = os.path.normcase(btn.path) == norm
            btn.setChecked(active)

    # ── Recent files ──────────────────────────────────────

    def _build_recent_files_section(self):
        self._rf_header = _SectionHeader(t("sidebar.recent"))
        self._rf_header.toggled_collapsed.connect(lambda c: self._toggle_section("rf", c))
        self._layout.addWidget(self._rf_header)

        self._rf_container = QWidget()
        self._rf_container.setStyleSheet("background: transparent;")
        self._rf_layout = QVBoxLayout(self._rf_container)
        self._rf_layout.setContentsMargins(0, 0, 0, 0)
        self._rf_layout.setSpacing(1)
        self._layout.addWidget(self._rf_container)
        self._rf_visible = True
        self._refresh_recent_files()

    def _refresh_recent_files(self):
        while self._rf_layout.count():
            item = self._rf_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            from src.recent_files import load_recent_files
            files = load_recent_files()[:10]
        except Exception:
            _log.exception("Failed to load recent files")
            files = []

        if not files:
            hint = QLabel(t("sidebar.no_recent"))
            hint.setStyleSheet("color: #444; font-size: 11px; padding: 6px 14px;")
            self._rf_layout.addWidget(hint)
            return

        for path in files:
            name = Path(path).name
            btn = _SidebarItem(ico.recent_file(), name, path)
            btn.setToolTip(path)
            btn.clicked.connect(lambda _, p=path: self._on_open_file(p))
            self._rf_layout.addWidget(btn)

    def refresh_recent_files(self):
        self._refresh_recent_files()

    def set_show_recent_files(self, visible: bool):
        self._rf_visible = visible
        self._rf_header.setVisible(visible)
        self._rf_container.setVisible(visible and not getattr(self, "_rf_collapsed", False))

    def _on_open_file(self, path: str):
        from src.utils import open_file
        if os.path.isfile(path):
            open_file(path)
        elif os.path.isdir(path):
            self.navigate.emit(path)

    def _on_navigate(self, path: str):
        self.navigate.emit(path)

    # ── Section collapse ──────────────────────────────────

    def _toggle_section(self, section: str, collapsed: bool):
        target = {
            "qa":     "_qa_container",
            "drives": "_drives_container",
            "bm":     "_bm_container",
            "rf":     "_rf_container",
        }.get(section)
        if target and hasattr(self, target):
            getattr(self, target).setVisible(not collapsed)
        if section == "rf":
            self._rf_collapsed = collapsed
        elif section == "bm":
            self._bm_collapsed = collapsed

    # ── Drag & drop (to add bookmarks) ────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.add_bookmark(path)
        event.acceptProposedAction()
