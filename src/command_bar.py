"""Contextual command bar — appears when files are selected."""

import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QToolButton, QLabel, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor
from src import icon_provider as ico


class CommandBar(QWidget):
    """Thin bar with quick actions that morphs based on the current selection."""

    action_open       = pyqtSignal()
    action_copy       = pyqtSignal()
    action_cut        = pyqtSignal()
    action_paste      = pyqtSignal()
    action_rename     = pyqtSignal()
    action_delete     = pyqtSignal()
    action_copy_path  = pyqtSignal()
    action_properties = pyqtSignal()
    action_new_folder = pyqtSignal()

    _BTN_STYLE = """
        QToolButton {{
            background: transparent;
            border: none;
            border-radius: 5px;
            color: {color};
            font-size: 12px;
            padding: 4px 10px;
            min-height: 26px;
        }}
        QToolButton:hover   {{ background: {hover}; }}
        QToolButton:pressed {{ background: {press}; }}
        QToolButton:disabled {{ color: #444; }}
    """

    def __init__(self, theme_key: str = "dark_fluent", parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setObjectName("CommandBar")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(8, 4, 8, 4)
        outer.setSpacing(2)

        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet("color: #666; font-size: 12px; padding: 0 6px;")
        self._info_lbl.setFixedWidth(180)
        outer.addWidget(self._info_lbl)

        sep = _vsep()
        outer.addWidget(sep)

        ICON_SZ = QSize(15, 15)

        def _btn(icon_fn, label: str, signal, danger: bool = False) -> QToolButton:
            b = QToolButton()
            b.setIcon(icon_fn("#e74c3c") if danger else icon_fn())
            b.setIconSize(ICON_SZ)
            b.setText(f" {label} ")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            color = "#e74c3c" if danger else "#cccccc"
            b.setStyleSheet(self._BTN_STYLE.format(
                color=color, hover="#2a2d2e", press="#1e1e1e"
            ))
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            b.clicked.connect(signal)
            return b

        self._btn_open    = _btn(ico.open_icon,       "Abrir",        self.action_open)
        self._btn_copy    = _btn(ico.copy_icon,       "Copiar",       self.action_copy)
        self._btn_cut     = _btn(ico.cut_icon,        "Cortar",       self.action_cut)
        self._btn_paste   = _btn(ico.paste_icon,      "Pegar",        self.action_paste)
        self._btn_rename  = _btn(ico.rename_icon,     "Renombrar",    self.action_rename)
        self._btn_delete  = _btn(ico.delete_icon,     "Eliminar",     self.action_delete, danger=True)
        self._btn_cpath   = _btn(ico.copy_path_icon,  "Copiar ruta",  self.action_copy_path)
        self._btn_props   = _btn(ico.properties_icon, "Propiedades",  self.action_properties)
        self._btn_nfolder = _btn(ico.new_folder_icon, "Nueva carpeta",self.action_new_folder)

        for b in (self._btn_open, self._btn_copy, self._btn_cut, self._btn_paste,
                  self._btn_rename, self._btn_delete, self._btn_cpath,
                  self._btn_props, self._btn_nfolder):
            outer.addWidget(b)

        outer.addStretch()
        self.update_state([], has_clipboard=False)

    # ── Public API ────────────────────────────────────────

    def update_state(self, paths: list[str], has_clipboard: bool):
        n = len(paths)
        is_dir = n == 1 and os.path.isdir(paths[0]) if paths else False

        if n == 0:
            self._info_lbl.setText("")
        elif n == 1:
            name = os.path.basename(paths[0])
            self._info_lbl.setText(f"  {name[:22]}{'…' if len(name) > 22 else ''}")
        else:
            self._info_lbl.setText(f"  {n} seleccionados")

        self._btn_open.setVisible(n >= 1)
        self._btn_open.setIcon(ico.folder_open() if is_dir else ico.open_icon())
        self._btn_open.setText(f" {'Abrir' if n == 1 else f'Abrir ({n})'} ")
        self._btn_copy.setVisible(n >= 1)
        self._btn_cut.setVisible(n >= 1)
        self._btn_paste.setVisible(True)
        self._btn_paste.setEnabled(has_clipboard)
        self._btn_rename.setVisible(n == 1)
        self._btn_delete.setVisible(n >= 1)
        self._btn_cpath.setVisible(n <= 1)
        self._btn_props.setVisible(n == 1)
        self._btn_nfolder.setVisible(n == 0)

    def set_theme(self, bg: str, border: str):
        self.setStyleSheet(
            f"#CommandBar {{ background: {bg}; border-top: 1px solid {border}; }}"
        )


def _vsep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.VLine)
    f.setFixedWidth(1)
    f.setStyleSheet("background: #2d2d2d; border: none;")
    return f
