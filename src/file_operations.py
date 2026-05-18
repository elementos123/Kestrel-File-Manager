import os
import shutil
from typing import List, Optional

from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QSize
from PyQt6.QtWidgets import (
    QMessageBox, QProgressDialog, QApplication, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QDialogButtonBox, QCheckBox, QFrame, QWidget,
)

from src.utils import format_size


class FileOperationWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(
        self,
        operation: str,
        sources: List[str],
        destination: str,
        conflict_action: str = "rename",
        parent: QObject = None,
    ):
        super().__init__(parent)
        self.operation = operation
        self.sources = sources
        self.destination = destination
        self.conflict_action = conflict_action
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            total = len(self.sources)
            for i, src in enumerate(self.sources):
                if self._cancelled:
                    self.finished.emit(False, "Operación cancelada")
                    return

                name = os.path.basename(src)
                self.progress.emit(int((i / total) * 100), name)

                dest_path = os.path.join(self.destination, name)
                dest_path = self._resolve_conflict(dest_path)
                if not dest_path:
                    continue

                if self.operation == "copy":
                    if os.path.isdir(src):
                        shutil.copytree(src, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dest_path)
                elif self.operation == "move":
                    shutil.move(src, dest_path)

            self.progress.emit(100, "Completado")
            self.finished.emit(True, "")
        except PermissionError as e:
            self.finished.emit(False, f"Permiso denegado: {e}")
        except Exception as e:
            self.finished.emit(False, str(e))

    def _resolve_conflict(self, dest_path: str) -> Optional[str]:
        if not os.path.exists(dest_path):
            return dest_path
        if self.conflict_action == "skip":
            return None
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while True:
            new_path = f"{base} ({counter}){ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1


class ClipboardState:
    def __init__(self):
        self.paths: List[str] = []
        self.operation: str = ""  # "copy" or "cut"

    def copy(self, paths: List[str]):
        self.paths = [p for p in paths if os.path.exists(p)]
        self.operation = "copy" if self.paths else ""

    def cut(self, paths: List[str]):
        self.paths = [p for p in paths if os.path.exists(p)]
        self.operation = "cut" if self.paths else ""

    def clear(self):
        self.paths = []
        self.operation = ""

    def has_items(self) -> bool:
        return bool(self.paths)


_clipboard = ClipboardState()


def get_clipboard() -> ClipboardState:
    return _clipboard


try:
    import send2trash as _send2trash
    _HAS_TRASH = True
except ImportError:
    _HAS_TRASH = False


class DeleteConfirmDialog(QDialog):
    """Focused confirmation dialog for trash/permanent delete operations."""

    def __init__(self, paths: List[str], to_trash: bool, parent=None):
        super().__init__(parent)
        self._paths = paths
        self._to_trash = to_trash

        self.setWindowTitle("Eliminar elementos")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setMinimumHeight(420)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(12)

        files, folders, total_size, unknown_dirs = self._summarize(paths)
        action = "Mover a la papelera" if to_trash else "Eliminar permanentemente"
        accent = "#dcdcaa" if to_trash else "#f44747"
        bg = "rgba(220, 220, 170, 0.10)" if to_trash else "rgba(244, 71, 71, 0.12)"

        header = QWidget()
        header_l = QHBoxLayout(header)
        header_l.setContentsMargins(0, 0, 0, 0)
        header_l.setSpacing(12)

        icon = QLabel("🗑" if to_trash else "⚠")
        icon.setFixedSize(44, 44)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"font-size: 24px; border-radius: 8px; background: {bg}; color: {accent};"
        )
        header_l.addWidget(icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel(action)
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        subtitle = QLabel(self._subtitle(paths, files, folders, total_size, unknown_dirs, to_trash))
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #888; font-size: 12px;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_l.addLayout(title_box, 1)
        root.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border: none; background: #333;")
        sep.setFixedHeight(1)
        root.addWidget(sep)

        list_label = QLabel("Elementos seleccionados")
        list_label.setStyleSheet("color: #aaa; font-size: 11px; font-weight: 700;")
        root.addWidget(list_label)

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        self._list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self._list.setMinimumHeight(180)
        for path in paths[:200]:
            item = QListWidgetItem(self._item_label(path))
            item.setToolTip(path)
            item.setSizeHint(QSize(0, 42))
            self._list.addItem(item)
        if len(paths) > 200:
            self._list.addItem(QListWidgetItem(f"... y {len(paths) - 200} elementos más"))
        root.addWidget(self._list, 1)

        if to_trash:
            note = QLabel("Podrás restaurarlos desde la papelera mientras sigan allí.")
            note.setStyleSheet("color: #888; font-size: 11px;")
            root.addWidget(note)
            self._confirm_cb = None
        else:
            warning = QLabel("Esta acción no usa la papelera y no se puede deshacer desde la app.")
            warning.setWordWrap(True)
            warning.setStyleSheet(
                "color: #ffb3b3; background: rgba(244,71,71,0.10);"
                "border: 1px solid rgba(244,71,71,0.35); border-radius: 6px;"
                "padding: 8px 10px; font-size: 12px;"
            )
            root.addWidget(warning)
            self._confirm_cb = QCheckBox("Entiendo que se eliminarán permanentemente")
            root.addWidget(self._confirm_cb)

        buttons = QDialogButtonBox()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        self._delete_btn = QPushButton(action)
        self._delete_btn.setObjectName("AccentButton")
        self._delete_btn.clicked.connect(self.accept)
        if not to_trash:
            self._delete_btn.setEnabled(False)
            self._confirm_cb.stateChanged.connect(
                lambda _: self._delete_btn.setEnabled(self._confirm_cb.isChecked())
            )
        buttons.addButton(cancel, QDialogButtonBox.ButtonRole.RejectRole)
        buttons.addButton(self._delete_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        root.addWidget(buttons)

    @staticmethod
    def _summarize(paths: List[str]) -> tuple[int, int, int, bool]:
        files = 0
        folders = 0
        total_size = 0
        unknown_dirs = False
        for path in paths:
            try:
                if os.path.isdir(path):
                    folders += 1
                    unknown_dirs = True
                else:
                    files += 1
                    total_size += os.path.getsize(path)
            except OSError:
                pass
        return files, folders, total_size, unknown_dirs

    @staticmethod
    def _subtitle(paths: List[str], files: int, folders: int, total_size: int,
                  unknown_dirs: bool, to_trash: bool) -> str:
        parts = [f"{len(paths)} elemento(s)"]
        detail = []
        if files:
            detail.append(f"{files} archivo(s)")
        if folders:
            detail.append(f"{folders} carpeta(s)")
        if detail:
            parts.append(", ".join(detail))
        if total_size:
            size_text = format_size(total_size)
            if unknown_dirs:
                size_text += " + contenido de carpetas"
            parts.append(size_text)
        target = "a la papelera" if to_trash else "de forma definitiva"
        return f"Se eliminarán {', '.join(parts)} {target}."

    @staticmethod
    def _item_label(path: str) -> str:
        name = os.path.basename(path) or path
        kind = "Carpeta" if os.path.isdir(path) else "Archivo"
        parent = os.path.dirname(path)
        return f"{kind}  ·  {name}\n{parent}"


def delete_files(paths: List[str], parent=None, use_trash: bool = True,
                 confirm: bool = True) -> bool:
    to_trash = use_trash and _HAS_TRASH

    if confirm:
        dlg = DeleteConfirmDialog(paths, to_trash, parent)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return False

    errors = []
    for p in paths:
        try:
            if to_trash:
                _send2trash.send2trash(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
        except Exception as e:
            errors.append(f"{os.path.basename(p)}: {e}")

    if errors:
        QMessageBox.warning(
            parent,
            "Errores al eliminar",
            "No se pudieron eliminar:\n" + "\n".join(errors),
        )
    return True


def rename_item(old_path: str, new_name: str) -> tuple[bool, str]:
    parent_dir = os.path.dirname(old_path)
    new_path = os.path.join(parent_dir, new_name)
    if os.path.exists(new_path):
        return False, "Ya existe un elemento con ese nombre"
    try:
        os.rename(old_path, new_path)
        return True, new_path
    except Exception as e:
        return False, str(e)


def create_folder(parent_dir: str, name: str = "Nueva carpeta") -> tuple[bool, str]:
    base = os.path.join(parent_dir, name)
    path = base
    counter = 1
    while os.path.exists(path):
        path = f"{base} ({counter})"
        counter += 1
    try:
        os.makedirs(path)
        return True, path
    except Exception as e:
        return False, str(e)


def paste_files(destination: str, parent_widget=None) -> Optional[FileOperationWorker]:
    cb = get_clipboard()
    if not cb.has_items():
        return None

    valid = [p for p in cb.paths if os.path.exists(p)]
    if not valid:
        cb.clear()
        return None

    conflict_action = getattr(parent_widget, "_conflict_action", "rename")
    conflicts = [
        os.path.basename(p)
        for p in valid
        if os.path.exists(os.path.join(destination, os.path.basename(p)))
    ]
    if conflicts and conflict_action == "ask":
        msg = QMessageBox(parent_widget)
        msg.setWindowTitle("Conflictos al pegar")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(f"{len(conflicts)} elemento(s) ya existen en el destino.")
        shown = "\n".join(f"  • {name}" for name in conflicts[:8])
        if len(conflicts) > 8:
            shown += f"\n  ... y {len(conflicts) - 8} más"
        msg.setInformativeText(shown)
        rename_btn = msg.addButton("Renombrar copias", QMessageBox.ButtonRole.AcceptRole)
        skip_btn = msg.addButton("Saltar existentes", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(rename_btn)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked is cancel_btn:
            return None
        conflict_action = "skip" if clicked is skip_btn else "rename"

    clipboard_operation = cb.operation
    worker_operation = "move" if clipboard_operation == "cut" else "copy"
    worker = FileOperationWorker(worker_operation, valid, destination, conflict_action)

    # We no longer use modal QProgressDialog here. 
    # The caller (MainWindow) should register this worker with TransferManager.
    
    def on_finished(ok, _msg):
        if ok and clipboard_operation == "cut":
            cb.clear()

    worker.finished.connect(on_finished)
    worker.start()
    return worker
