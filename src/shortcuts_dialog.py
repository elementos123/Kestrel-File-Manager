"""Keyboard shortcuts reference dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QPushButton,
)
from PyQt6.QtCore import Qt

from src.i18n import t
from src.toggle_switch import ToggleSwitch

# Each section: (title_key, [(label_key, shortcut_text), ...])
_SECTIONS = [
    ("dlg.shortcuts.section.navigation", [
        ("dlg.shortcuts.nav.back_fwd", "Alt+← / Alt+→"),
        ("dlg.shortcuts.nav.up", "Alt+↑ / Backspace"),
        ("dlg.shortcuts.nav.address", "Ctrl+L"),
        ("dlg.shortcuts.nav.bookmark", "Ctrl+D"),
        ("dlg.shortcuts.nav.search", "Ctrl+F"),
        ("dlg.shortcuts.nav.refresh", "F5"),
    ]),
    ("dlg.shortcuts.section.tabs", [
        ("dlg.shortcuts.tabs.new", "Ctrl+T"),
        ("dlg.shortcuts.tabs.close", "Ctrl+W"),
        ("dlg.shortcuts.tabs.switch", "Ctrl+Tab / Ctrl+Shift+Tab"),
        ("dlg.shortcuts.tabs.new_window", "Ctrl+N"),
    ]),
    ("dlg.shortcuts.section.files", [
        ("dlg.shortcuts.files.copy_cut_paste", "Ctrl+C / X / V"),
        ("dlg.shortcuts.files.copy_path", "Ctrl+Shift+C"),
        ("dlg.shortcuts.files.rename", "F2"),
        ("dlg.shortcuts.files.delete", "Del"),
        ("dlg.shortcuts.files.properties", "Alt+Enter"),
        ("dlg.shortcuts.files.select_all", "Ctrl+A"),
        ("dlg.shortcuts.files.new_folder", "Ctrl+Shift+N"),
    ]),
    ("dlg.shortcuts.section.view", [
        ("dlg.shortcuts.view.modes", "Ctrl+1 / 2 / 3"),
        ("dlg.shortcuts.view.preview", "Ctrl+P"),
        ("dlg.shortcuts.view.sidebar", "Ctrl+B"),
        ("dlg.shortcuts.view.typeahead", None),  # hint filled in below
        ("dlg.shortcuts.view.quicklook", None),
    ]),
    ("dlg.shortcuts.section.search", [
        ("dlg.shortcuts.search.folder", "Ctrl+F"),
        ("dlg.shortcuts.search.recursive", "Ctrl+Shift+F"),
    ]),
    ("dlg.shortcuts.section.archive", [
        ("dlg.shortcuts.archive.zip", None),
        ("dlg.shortcuts.archive.extract", None),
    ]),
]


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("dlg.shortcuts.title"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(560)
        self.setModal(True)

        accent = ToggleSwitch._C_ON

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel(t("dlg.shortcuts.title"))
        header.setStyleSheet("font-size: 17px; font-weight: 700; padding: 20px 24px 12px 24px;")
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 0, 24, 16)
        layout.setSpacing(18)

        # Hints for rows that carry a "how" instead of a fixed key combo
        hints = {
            "dlg.shortcuts.view.typeahead": t("dlg.shortcuts.view.typeahead_hint"),
            "dlg.shortcuts.view.quicklook": t("dlg.shortcuts.view.space"),
            "dlg.shortcuts.archive.zip": t("dlg.shortcuts.archive.zip_hint"),
            "dlg.shortcuts.archive.extract": t("dlg.shortcuts.archive.extract_hint"),
        }

        for title_key, rows in _SECTIONS:
            sec_lbl = QLabel(t(title_key).upper())
            sec_lbl.setStyleSheet(
                f"color: {accent.name()}; font-size: 10px; font-weight: 800; "
                f"letter-spacing: 0.9px; padding-bottom: 2px;"
            )
            layout.addWidget(sec_lbl)

            section_box = QVBoxLayout()
            section_box.setSpacing(1)
            for label_key, combo in rows:
                text = hints.get(label_key, combo) or ""
                section_box.addLayout(self._row(t(label_key), text))
            layout.addLayout(section_box)

        layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        close_row = QVBoxLayout()
        close_row.setContentsMargins(24, 10, 24, 18)
        close_btn = QPushButton(t("common.ok"))
        close_btn.setObjectName("AccentButton")
        close_btn.setMinimumHeight(34)
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        close_row.addWidget(close_btn)
        root.addLayout(close_row)

    @staticmethod
    def _row(label: str, shortcut: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 5, 0, 5)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 12px; color: #ccc;")
        row.addWidget(lbl, 1)

        if shortcut:
            badge = QLabel(shortcut)
            badge.setStyleSheet(
                "background: rgba(127,127,127,0.14); border: 1px solid rgba(127,127,127,0.25); "
                "border-radius: 5px; padding: 3px 8px; font-size: 11px; font-weight: 700; "
                "color: #ddd;"
            )
            row.addWidget(badge, 0, Qt.AlignmentFlag.AlignRight)

        return row
