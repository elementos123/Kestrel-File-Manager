"""File / folder properties dialog."""

import os
import stat
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QTabWidget, QWidget,
    QFrame, QDialogButtonBox, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from src.utils import format_size, format_date, get_file_icon
from src.file_operations import rename_item


class _FolderSizeWorker(QThread):
    result = pyqtSignal(int, int, int)  # total_size, files, folders

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        total, files, folders = 0, 0, 0
        try:
            for entry in os.walk(self.path):
                if self._cancel:
                    return
                root, dirs, fnames = entry
                folders += len(dirs)
                for fn in fnames:
                    if self._cancel:
                        return
                    try:
                        total += os.path.getsize(os.path.join(root, fn))
                        files += 1
                    except OSError:
                        pass
        except Exception:
            pass
        self.result.emit(total, files, folders)


def _sep_line() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("border: none; background: #333; margin: 4px 0;")
    f.setFixedHeight(1)
    return f


def _row(grid: QGridLayout, row: int, label: str, value: str, bold_val=False):
    lbl = QLabel(label)
    lbl.setStyleSheet("color: #888; font-size: 12px;")
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
    val = QLabel(value)
    val.setWordWrap(True)
    val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    if bold_val:
        font = val.font()
        font.setBold(True)
        val.setFont(font)
    grid.addWidget(lbl, row, 0)
    grid.addWidget(val, row, 1)
    return val


class PropertiesDialog(QDialog):
    renamed = pyqtSignal(str)  # new path

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._path = path
        self._is_dir = os.path.isdir(path)
        self._worker: _FolderSizeWorker = None

        self.setWindowTitle("Propiedades")
        self.setMinimumWidth(420)
        self.setMinimumHeight(460)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        tabs = QTabWidget()
        root.addWidget(tabs)

        tabs.addTab(self._build_general_tab(), "General")
        if not self._is_dir:
            tabs.addTab(self._build_details_tab(), "Detalles")

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(16, 8, 16, 12)
        ok_btn = QPushButton("Aceptar")
        ok_btn.setObjectName("AccentButton")
        ok_btn.clicked.connect(self._apply_and_close)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        root.addLayout(btn_layout)

        self._start_size_worker()

    def _build_general_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 8)
        layout.setSpacing(12)

        # Icon + name
        top = QHBoxLayout()
        icon_lbl = QLabel(get_file_icon(self._path, self._is_dir))
        icon_lbl.setStyleSheet("font-size: 42px;")
        icon_lbl.setFixedSize(56, 56)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(icon_lbl)

        name_col = QVBoxLayout()
        name_lbl = QLabel("Nombre:")
        name_lbl.setStyleSheet("color: #888; font-size: 11px;")
        self._name_edit = QLineEdit(os.path.basename(self._path))
        self._name_edit.setMinimumWidth(220)
        name_col.addWidget(name_lbl)
        name_col.addWidget(self._name_edit)
        top.addLayout(name_col, 1)
        layout.addLayout(top)

        layout.addWidget(_sep_line())

        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 110)
        grid.setColumnStretch(1, 1)
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(12)

        row = 0
        try:
            st = os.stat(self._path)
            if self._is_dir:
                _row(grid, row, "Tipo:", "Carpeta de archivos"); row += 1
                self._size_val = _row(grid, row, "Tamaño:", "Calculando…"); row += 1
                self._contains_val = _row(grid, row, "Contiene:", "Calculando…"); row += 1
            else:
                ext = Path(self._path).suffix.upper().lstrip(".")
                _row(grid, row, "Tipo:", f"Archivo {ext}" if ext else "Archivo"); row += 1
                self._size_val = _row(
                    grid, row, "Tamaño:",
                    f"{format_size(st.st_size)}  ({st.st_size:,} bytes)", bold_val=True
                ); row += 1
                try:
                    disk_size = _get_disk_size(self._path)
                    _row(grid, row, "En disco:", format_size(disk_size)); row += 1
                except Exception:
                    pass

            grid.addWidget(_sep_line(), row, 0, 1, 2); row += 1
            _row(grid, row, "Ubicación:", os.path.dirname(self._path)); row += 1
            grid.addWidget(_sep_line(), row, 0, 1, 2); row += 1
            _row(grid, row, "Creado:",    format_date(st.st_ctime)); row += 1
            _row(grid, row, "Modificado:", format_date(st.st_mtime)); row += 1
            _row(grid, row, "Accedido:", format_date(st.st_atime)); row += 1
            grid.addWidget(_sep_line(), row, 0, 1, 2); row += 1

            # Attributes
            attr_widget = QWidget()
            attr_layout = QHBoxLayout(attr_widget)
            attr_layout.setContentsMargins(0, 0, 0, 0)
            mode = st.st_mode
            self._readonly_cb = QCheckBox("Solo lectura")
            self._readonly_cb.setChecked(not os.access(self._path, os.W_OK))
            self._hidden_cb = QCheckBox("Oculto")
            self._hidden_cb.setChecked(
                os.path.basename(self._path).startswith(".")
                if sys.platform != "win32"
                else bool(_get_win_attr(self._path) & 2)
            )
            attr_layout.addWidget(self._readonly_cb)
            attr_layout.addWidget(self._hidden_cb)
            attr_layout.addStretch()
            grid.addWidget(QLabel("Atributos:"), row, 0)
            grid.addWidget(attr_widget, row, 1); row += 1
        except Exception as e:
            _row(grid, row, "Error:", str(e))

        layout.addLayout(grid)
        layout.addStretch()
        return w

    def _build_details_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 8)
        layout.setSpacing(8)
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 110)
        grid.setColumnStretch(1, 1)
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(12)

        row = 0
        path = Path(self._path)
        _row(grid, row, "Nombre:", path.name); row += 1
        _row(grid, row, "Extensión:", path.suffix or "(ninguna)"); row += 1
        _row(grid, row, "Ruta completa:", str(path)); row += 1

        try:
            st = os.stat(self._path)
            _row(grid, row, "Tamaño exacto:", f"{st.st_size:,} bytes"); row += 1
        except Exception:
            pass

        layout.addLayout(grid)
        layout.addStretch()
        return w

    def _start_size_worker(self):
        if self._is_dir and hasattr(self, "_size_val"):
            self._worker = _FolderSizeWorker(self._path)
            self._worker.result.connect(self._on_folder_size)
            self._worker.start()

    def _on_folder_size(self, total: int, files: int, folders: int):
        if hasattr(self, "_size_val"):
            self._size_val.setText(
                f"{format_size(total)}  ({total:,} bytes)"
            )
        if hasattr(self, "_contains_val"):
            self._contains_val.setText(
                f"{files:,} archivo(s), {folders:,} carpeta(s)"
            )

    def _apply_and_close(self):
        new_name = self._name_edit.text().strip()
        old_name = os.path.basename(self._path)
        if new_name and new_name != old_name:
            ok, result = rename_item(self._path, new_name)
            if not ok:
                QMessageBox.warning(self, "Error al renombrar", result)
                return
            self.renamed.emit(result)
        self.accept()

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(1000)
        super().closeEvent(event)


def _get_win_attr(path: str) -> int:
    try:
        import ctypes
        return ctypes.windll.kernel32.GetFileAttributesW(path)
    except Exception:
        return 0


def _get_disk_size(path: str) -> int:
    """Approximate size on disk (cluster-aligned)."""
    try:
        if sys.platform == "win32":
            import ctypes
            low  = ctypes.c_ulong(0)
            high = ctypes.c_ulong(0)
            size = ctypes.windll.kernel32.GetCompressedFileSizeW(
                path, ctypes.byref(high)
            )
            if size == 0xFFFFFFFF:
                return os.path.getsize(path)
            return (high.value << 32) + size
        return os.path.getsize(path)
    except Exception:
        return os.path.getsize(path)
