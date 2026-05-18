"""Multi-rename dialog — batch rename with find/replace, prefix/suffix, or numbering."""

import os
import re
import functools
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialogButtonBox, QMessageBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont


class RenameDialog(QDialog):
    renamed = pyqtSignal(list)   # list[(old_path, new_path)]

    def __init__(self, paths: list[str], parent=None):
        super().__init__(parent)
        self._paths = [p for p in paths if os.path.exists(p)]
        if not self._paths:
            return

        n = len(self._paths)
        self.setWindowTitle(f"Renombrar {n} elemento{'s' if n != 1 else ''}")
        self.setMinimumWidth(640)
        self.setMinimumHeight(520)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(16, 14, 16, 12)

        # ── Mode tabs ─────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_replace_tab(),  "🔎  Buscar y reemplazar")
        self._tabs.addTab(self._build_add_tab(),      "✚  Añadir texto")
        self._tabs.addTab(self._build_number_tab(),   "🔢  Numeración")
        self._tabs.addTab(self._build_case_tab(),     "Aa  Capitalización")
        self._tabs.currentChanged.connect(self._refresh_preview)
        root.addWidget(self._tabs)

        # ── Preview table ─────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border: none; background: #2d2d2d;")
        sep.setFixedHeight(1)
        root.addWidget(sep)

        lbl = QLabel("Vista previa  —  verde = cambiado  /  rojo = conflicto")
        lbl.setStyleSheet("color: #666; font-size: 11px; padding: 4px 0 2px 0;")
        root.addWidget(lbl)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Nombre actual", "Nuevo nombre"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setMinimumHeight(170)
        self._table.setMaximumHeight(260)
        root.addWidget(self._table)

        # ── Buttons ───────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Close
        )
        apply_btn = btns.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.setObjectName("AccentButton")
        apply_btn.setText("Aplicar renombrado")
        apply_btn.clicked.connect(self._apply)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

        self._refresh_preview()

    # ── Mode tabs ──────────────────────────────────────────

    def _build_replace_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(16, 14, 16, 10)
        fl.setVerticalSpacing(10)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText("Texto a buscar…")
        self._find_edit.textChanged.connect(self._refresh_preview)
        fl.addRow("Buscar:", self._find_edit)

        self._repl_edit = QLineEdit()
        self._repl_edit.setPlaceholderText("Reemplazar con… (vacío = eliminar)")
        self._repl_edit.textChanged.connect(self._refresh_preview)
        fl.addRow("Reemplazar con:", self._repl_edit)

        self._repl_case_cb = QCheckBox("Sensible a mayúsculas / minúsculas")
        self._repl_case_cb.toggled.connect(self._refresh_preview)
        fl.addRow(self._repl_case_cb)

        self._repl_regex_cb = QCheckBox("Usar expresión regular (regex)")
        self._repl_regex_cb.toggled.connect(self._refresh_preview)
        fl.addRow(self._repl_regex_cb)

        self._repl_ext_cb = QCheckBox("Incluir extensión en la búsqueda")
        self._repl_ext_cb.toggled.connect(self._refresh_preview)
        fl.addRow(self._repl_ext_cb)

        return w

    def _build_add_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(16, 14, 16, 10)
        fl.setVerticalSpacing(10)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._prefix_edit = QLineEdit()
        self._prefix_edit.setPlaceholderText("Texto al inicio del nombre…")
        self._prefix_edit.textChanged.connect(self._refresh_preview)
        fl.addRow("Prefijo:", self._prefix_edit)

        self._suffix_edit = QLineEdit()
        self._suffix_edit.setPlaceholderText("Texto antes de la extensión…")
        self._suffix_edit.textChanged.connect(self._refresh_preview)
        fl.addRow("Sufijo:", self._suffix_edit)

        return w

    def _build_number_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(16, 14, 16, 10)
        fl.setVerticalSpacing(10)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._num_pattern_edit = QLineEdit("foto_###")
        self._num_pattern_edit.setPlaceholderText("Patrón con # para dígitos")
        self._num_pattern_edit.setToolTip(
            "# = un dígito.  ### = tres dígitos con ceros.\n"
            "Ejemplo: foto_### → foto_001, foto_002…\n"
            "La extensión se añade automáticamente."
        )
        self._num_pattern_edit.textChanged.connect(self._refresh_preview)
        fl.addRow("Patrón:", self._num_pattern_edit)

        hint = QLabel("Usa # para indicar dígitos.  ### → 001, 002…   # → 1, 2…")
        hint.setStyleSheet("color: #555; font-size: 11px;")
        fl.addRow(hint)

        self._num_start_spin = QSpinBox()
        self._num_start_spin.setRange(0, 999_999)
        self._num_start_spin.setValue(1)
        self._num_start_spin.valueChanged.connect(self._refresh_preview)
        fl.addRow("Empezar desde:", self._num_start_spin)

        self._num_step_spin = QSpinBox()
        self._num_step_spin.setRange(1, 1000)
        self._num_step_spin.setValue(1)
        self._num_step_spin.valueChanged.connect(self._refresh_preview)
        fl.addRow("Incremento:", self._num_step_spin)

        return w

    def _build_case_tab(self) -> QWidget:
        w = QWidget()
        fl = QFormLayout(w)
        fl.setContentsMargins(16, 14, 16, 10)
        fl.setVerticalSpacing(10)
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        from PyQt6.QtWidgets import QComboBox
        self._case_combo = QComboBox()
        self._case_combo.addItem("Sin cambios",                  "none")
        self._case_combo.addItem("MAYÚSCULAS",                   "upper")
        self._case_combo.addItem("minúsculas",                   "lower")
        self._case_combo.addItem("Primera letra mayúscula",      "title")
        self._case_combo.addItem("Primera letra de cada palabra","words")
        self._case_combo.currentIndexChanged.connect(self._refresh_preview)
        fl.addRow("Convertir a:", self._case_combo)

        return w

    # ── Preview logic ──────────────────────────────────────

    def _compute_names(self) -> list[str]:
        tab = self._tabs.currentIndex()
        results = []

        if tab == 0:   # Replace
            find    = self._find_edit.text()
            replace = self._repl_edit.text()
            case_s  = self._repl_case_cb.isChecked()
            use_re  = self._repl_regex_cb.isChecked()
            incl_ext = self._repl_ext_cb.isChecked()

            for path in self._paths:
                name = os.path.basename(path)
                stem, ext = os.path.splitext(name)
                target = name if incl_ext else stem
                if not find:
                    results.append(name)
                    continue
                try:
                    if use_re:
                        flags = 0 if case_s else re.IGNORECASE
                        new_target = re.sub(find, replace, target, flags=flags)
                    else:
                        if case_s:
                            new_target = target.replace(find, replace)
                        else:
                            new_target = re.sub(re.escape(find), replace, target, flags=re.IGNORECASE)
                    if incl_ext:
                        results.append(new_target)
                    else:
                        results.append(new_target + ext)
                except re.error:
                    results.append(name)

        elif tab == 1:  # Add
            prefix = self._prefix_edit.text()
            suffix = self._suffix_edit.text()
            for path in self._paths:
                name = os.path.basename(path)
                stem, ext = os.path.splitext(name)
                results.append(f"{prefix}{stem}{suffix}{ext}")

        elif tab == 2:  # Number
            pattern = self._num_pattern_edit.text() or "archivo_###"
            start   = self._num_start_spin.value()
            step    = self._num_step_spin.value()
            for i, path in enumerate(self._paths):
                ext = Path(path).suffix
                num = start + i * step
                def _rep(m, n=num):
                    return str(n).zfill(len(m.group()))
                new_stem = re.sub(r"#+", _rep, pattern)
                results.append(new_stem + ext)

        elif tab == 3:  # Case
            case_mode = self._case_combo.currentData()
            for path in self._paths:
                name = os.path.basename(path)
                stem, ext = os.path.splitext(name)
                if case_mode == "upper":
                    new_stem = stem.upper()
                elif case_mode == "lower":
                    new_stem = stem.lower()
                elif case_mode == "title":
                    new_stem = stem.capitalize()
                elif case_mode == "words":
                    new_stem = stem.title()
                else:
                    new_stem = stem
                results.append(new_stem + ext)

        return results

    def _refresh_preview(self):
        names = self._compute_names()
        self._table.setRowCount(len(self._paths))
        parent_dirs = {os.path.dirname(p) for p in self._paths}

        for i, (path, new_name) in enumerate(zip(self._paths, names)):
            old_name = os.path.basename(path)
            old_item = QTableWidgetItem(old_name)
            new_item = QTableWidgetItem(new_name)
            old_item.setForeground(QColor("#888"))

            if new_name == old_name:
                new_item.setForeground(QColor("#666"))
            else:
                # Check for conflict
                conflict = any(
                    os.path.exists(os.path.join(d, new_name)) and
                    os.path.join(d, new_name) != path
                    for d in parent_dirs
                )
                if conflict:
                    new_item.setForeground(QColor("#e74c3c"))
                    new_item.setToolTip("⚠  Ya existe un archivo con este nombre")
                else:
                    new_item.setForeground(QColor("#4ec9b0"))

            self._table.setItem(i, 0, old_item)
            self._table.setItem(i, 1, new_item)

    # ── Apply ──────────────────────────────────────────────

    def _apply(self):
        names  = self._compute_names()
        done   = []
        errors = []

        for path, new_name in zip(self._paths, names):
            old_name = os.path.basename(path)
            if new_name == old_name or not new_name:
                continue
            new_path = os.path.join(os.path.dirname(path), new_name)
            if os.path.exists(new_path):
                errors.append(f"{new_name}  (ya existe)")
                continue
            try:
                os.rename(path, new_path)
                done.append((path, new_path))
            except Exception as e:
                errors.append(f"{old_name}: {e}")

        if errors:
            QMessageBox.warning(self, "Errores al renombrar",
                "No se pudieron renombrar:\n" + "\n".join(errors[:10]))

        if done:
            self.renamed.emit(done)

        if not errors:
            self.accept()
        else:
            self._refresh_preview()
