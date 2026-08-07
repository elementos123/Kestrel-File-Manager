import json
import os
from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QFormLayout, QSlider,
    QDialogButtonBox, QWidget, QTabWidget, QLineEdit,
    QToolButton, QFileDialog, QFrame, QSizePolicy, QScrollArea,
    QColorDialog, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QHeaderView, QMessageBox, QButtonGroup,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QColor, QFont, QFontDatabase

from src.toggle_switch import ToggleSwitch

from src.themes import THEMES
from src.i18n import t, set_language
from src.logger import get_logger
from src import icon_provider as ico


SETTINGS_FILE = str(Path.home() / ".file_explorer_settings.json")

_UI_FONT_OPTIONS = [
    "Segoe UI", "Segoe UI Variable", "Arial", "Calibri", "Cambria", "Candara",
    "Century Gothic", "Consolas", "Corbel", "Ebrima", "Franklin Gothic Medium",
    "Georgia", "Inter", "JetBrains Sans", "Lucida Sans Unicode", "Microsoft Sans Serif",
    "Nirmala UI", "Roboto", "San Francisco", "Tahoma", "Trebuchet MS",
    "Ubuntu", "Verdana", "Yu Gothic UI", "System",
]

_MONO_FONT_OPTIONS = [
    "Cascadia Code", "Cascadia Mono", "Consolas", "Courier New", "Fira Code",
    "Hack", "IBM Plex Mono", "Inconsolata", "JetBrains Mono", "Lucida Console",
    "Menlo", "Monaco", "Roboto Mono", "Source Code Pro", "Ubuntu Mono",
]

_FONT_PREVIEW_EXCLUDE = {
    # Windows logical families can make DirectWrite log CreateFontFaceFromHDC errors.
    "decorative", "modern", "roman", "script", "system",
}

_DEFAULTS: dict[str, Any] = {
    # Appearance
    "language":           "auto",
    "theme":              "dark_fluent",
    "accent_color":       "",
    "font_family":        "Segoe UI",
    "font_weight":        "normal",
    "font_size":          13,
    "border_radius":      "normal",
    "density":            "normal",
    "row_height":         0,
    "opacity":            100,
    "toolbar_compact":    False,
    "scrollbar_style":    "thin",
    "animation_speed":    "normal",
    "monospace_font":     "Consolas",
    "sidebar_width":      200,
    "custom_stylesheet":  "",
    # View
    "view_mode":          0,
    "icon_size":          96,
    "folders_first":      True,
    "single_click":       False,
    "show_extensions":    True,
    "color_coding":       False,
    "show_hidden":        False,
    "date_format":        "absolute",
    "size_unit":          "auto",
    "show_thumbnails":    True,
    "thumbnail_cache_mb": 200,
    "column_visibility":  [True, True, True, True],
    # Panels
    "preview":            True,
    "preview_position":   "right",
    "preview_syntax_hl":  True,
    "show_sidebar":       True,
    "show_breadcrumb":    True,
    "show_cmdbar":        True,
    "statusbar_path":     True,
    "statusbar_disk":     True,
    # Behavior
    "startup_folder":     "home",
    "startup_path":       "",
    "confirm_delete":     True,
    "use_trash":          True,
    "hide_tabbar_single":   False,
    "restore_tabs":         False,
    "conflict_action":      "rename",
    "sidebar_recent_files": True,
    # Search
    "search_case":        False,
    "search_exclude":     ".git,node_modules,__pycache__,.venv,.DS_Store",
    # Tools
    "external_tools":     [],
    # System
    "terminal":           "auto",
    # Onboarding
    "onboarding_shown":   False,
}


def load_settings() -> dict[str, Any]:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            result = dict(_DEFAULTS)
            result.update(data)
            return result
    except FileNotFoundError:
        return dict(_DEFAULTS)
    except Exception:
        from src.logger import get_logger
        get_logger("settings").exception("Failed to load settings from %s", SETTINGS_FILE)
        return dict(_DEFAULTS)


def save_settings(settings: dict[str, Any]) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        from src.logger import get_logger
        get_logger("settings").exception("Failed to save settings to %s", SETTINGS_FILE)


# ── Color picker button ────────────────────────────────────

class _ColorButton(QPushButton):
    color_changed = pyqtSignal(str)

    def __init__(self, color: str = "", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(80, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh()
        self.clicked.connect(self._pick)

    def color(self) -> str:
        return self._color

    def set_color(self, color: str, emit: bool = True):
        self._color = color
        self._refresh()
        if emit:
            self.color_changed.emit(self._color)

    def _refresh(self):
        if self._color:
            self.setText("")
            self.setStyleSheet(
                f"QPushButton {{ background: {self._color}; border: 2px solid #555;"
                f"border-radius: 5px; }}"
                f"QPushButton:hover {{ border-color: #999; }}"
            )
        else:
            self.setText("Auto")
            self.setStyleSheet(
                "QPushButton { background: #333; color: #888; border: 1px solid #555;"
                "border-radius: 5px; font-size: 11px; }"
                "QPushButton:hover { background: #444; color: #ccc; }"
            )

    def _pick(self):
        initial = QColor(self._color) if self._color else QColor("#0078d4")
        c = QColorDialog.getColor(initial, self, "Elegir color de acento",
                                   QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if c.isValid():
            self._color = c.name()
            self._refresh()
            self.color_changed.emit(self._color)


# ── Separator line ────────────────────────────────────────

def _hsep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("border: none; background: #333; margin: 4px 0;")
    f.setFixedHeight(1)
    return f


# ── Settings dialog ────────────────────────────────────────

class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, current: dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("dlg.settings.title"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(520)
        self.setModal(True)
        self._original = dict(current)   # kept for Cancel revert
        self._settings = dict(current)

        # Debounce timer — batches rapid changes into one update
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(80)
        self._preview_timer.timeout.connect(self._fire_preview)

        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 12)

        self._tabs = QTabWidget()
        self._tabs.setIconSize(QSize(16, 16))
        self._tabs.addTab(self._build_appearance(),  ico.tab_appearance(), t("dlg.settings.tab.appearance"))
        self._tabs.addTab(self._build_view(),        ico.tab_files(),      t("dlg.settings.tab.files"))
        self._tabs.addTab(self._build_panels(),      ico.tab_panels(),     t("dlg.settings.tab.panels"))
        self._tabs.addTab(self._build_search(),      ico.tab_search(),     t("dlg.settings.tab.search"))
        self._tabs.addTab(self._build_behavior(),    ico.tab_behavior(),   t("dlg.settings.tab.behavior"))
        self._tabs.addTab(self._build_tools(),       ico.tab_tools(),      t("dlg.settings.tab.tools"))
        self._tabs.addTab(self._build_system(),      ico.tab_system(),     t("dlg.settings.tab.system"))
        root.addWidget(self._tabs)

        root.addSpacing(4)

        # Live preview badge + buttons row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(16, 0, 16, 0)
        btn_row.setSpacing(12)

        live_lbl = QLabel("● Cambios aplicados en tiempo real")
        live_lbl.setStyleSheet("color: #4ec9b0; font-size: 11px;")
        btn_row.addWidget(live_lbl)
        btn_row.addStretch()

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        ok_btn = btns.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setObjectName("AccentButton")
        ok_btn.setText(t("common.save"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("common.cancel"))

        btn_row.addWidget(btns)
        root.addLayout(btn_row)

        # Wire live preview AFTER all widgets are created
        self._connect_live_preview()

    # ── Live preview ──────────────────────────────────────

    def _connect_live_preview(self):
        """Connect every setting widget to the debounced preview."""
        p = self._schedule_preview

        # Appearance
        self._theme_combo.currentIndexChanged.connect(p)
        self._font_family_combo.currentIndexChanged.connect(p)
        self._monospace_combo.currentIndexChanged.connect(p)
        self._font_weight_combo.currentIndexChanged.connect(p)
        self._font_size_slider.valueChanged.connect(p)
        self._border_combo.currentIndexChanged.connect(p)
        self._accent_btn.color_changed.connect(p)
        self._density_combo.currentIndexChanged.connect(p)
        self._row_height_slider.valueChanged.connect(p)
        self._opacity_slider.valueChanged.connect(p)
        self._toolbar_compact_cb.stateChanged.connect(p)
        self._sidebar_width_slider.valueChanged.connect(p)
        self._scrollbar_combo.currentIndexChanged.connect(p)
        self._anim_speed_combo.currentIndexChanged.connect(p)
        self._accent_hex_edit.editingFinished.connect(self._set_accent_from_hex)
        self._custom_css_edit.textChanged.connect(p)

        # View / Files
        self._view_combo.currentIndexChanged.connect(p)
        self._icon_size_slider.valueChanged.connect(p)
        self._date_fmt_combo.currentIndexChanged.connect(p)
        self._size_unit_combo.currentIndexChanged.connect(p)
        for cb in [self._folders_first_cb, self._extensions_cb, self._hidden_cb,
                   self._color_cb, self._thumbnails_cb, self._single_click_cb,
                   *self._col_checks]:
            cb.stateChanged.connect(p)

        # Panels
        for cb in [self._sidebar_cb, self._breadcrumb_cb, self._cmdbar_cb,
                   self._preview_cb, self._dual_mode_cb, self._terminal_cb,
                   self._syntax_cb,
                   self._sb_path_cb, self._sb_disk_cb, self._sidebar_rf_cb]:
            cb.stateChanged.connect(p)
        self._prev_pos_combo.currentIndexChanged.connect(p)

        # Search
        self._search_case_cb.stateChanged.connect(p)
        self._search_exclude_edit.textChanged.connect(p)

        # Behavior
        for cb in [self._trash_cb, self._confirm_cb,
                   self._hide_tabbar_cb, self._restore_tabs_cb]:
            cb.stateChanged.connect(p)
        self._conflict_combo.currentIndexChanged.connect(p)
        self._startup_combo.currentIndexChanged.connect(p)
        self._startup_path_edit.textChanged.connect(p)
        self._tools_table.itemChanged.connect(p)

        # System
        self._terminal_combo.currentIndexChanged.connect(p)

    def _schedule_preview(self, *_):
        """Restart debounce timer on any widget change."""
        self._preview_timer.start()

    def _fire_preview(self):
        """Emit settings_changed with current widget state (no save)."""
        self.settings_changed.emit(self._collect_settings())

    @staticmethod
    def _font_combo(options: list[str], current: str, monospace: bool = False) -> QComboBox:
        combo = QComboBox()
        combo.setEditable(False)
        combo.setMinimumWidth(220)

        def _is_preview_safe(font: str) -> bool:
            return font.strip().lower() not in _FONT_PREVIEW_EXCLUDE

        families = []
        try:
            families = [f for f in QFontDatabase.families() if _is_preview_safe(f)]
        except Exception:
            families = []

        ordered: list[str] = []
        for font in options:
            # Keep curated names even if Qt cannot verify them; Windows can still resolve aliases.
            if _is_preview_safe(font) and font not in ordered:
                ordered.append(font)

        if monospace:
            mono_hints = (
                "mono", "code", "console", "courier", "terminal", "consolas",
                "cascadia", "jetbrains", "fira", "hack", "source code",
            )
            system_fonts = [
                f for f in families
                if any(h in f.lower() for h in mono_hints)
            ]
        else:
            system_fonts = families

        for font in sorted(system_fonts, key=str.lower):
            if font not in ordered:
                ordered.append(font)

        combo.addItems(ordered)
        for i, font in enumerate(ordered):
            if _is_preview_safe(font):
                combo.setItemData(i, QFont(font), Qt.ItemDataRole.FontRole)
        if current and current not in ordered and _is_preview_safe(current):
            combo.insertItem(0, current)
            combo.setItemData(0, QFont(current), Qt.ItemDataRole.FontRole)
        selected = current or (options[0] if options else "Segoe UI")
        idx = combo.findText(selected)
        combo.setCurrentIndex(idx if idx >= 0 else 0)

        def _apply_preview_font(text: str, c=combo):
            c.setFont(QFont(text) if _is_preview_safe(text) else QFont())

        _apply_preview_font(combo.currentText())
        combo.currentTextChanged.connect(_apply_preview_font)
        return combo

    def _collect_settings(self) -> dict:
        """Read all widgets → return settings dict (does NOT save to disk)."""
        s = dict(self._settings)
        # Appearance
        s["language"]           = self._language_combo.currentData()
        s["theme"]              = self._theme_combo.currentData()
        s["font_family"]        = self._font_family_combo.currentText().strip() or "Segoe UI"
        s["monospace_font"]     = self._monospace_combo.currentText().strip() or "Consolas"
        s["font_weight"]        = self._font_weight_combo.currentData()
        s["font_size"]          = self._font_size_slider.value()
        s["border_radius"]      = self._border_combo.currentData()
        s["accent_color"]       = self._accent_btn.color()
        s["density"]            = self._density_combo.currentData()
        s["row_height"]         = self._row_height_slider.value()
        s["opacity"]            = self._opacity_slider.value()
        s["toolbar_compact"]    = self._toolbar_compact_cb.isChecked()
        s["sidebar_width"]      = self._sidebar_width_slider.value()
        s["scrollbar_style"]    = self._scrollbar_combo.currentData()
        s["animation_speed"]    = self._anim_speed_combo.currentData()
        s["custom_stylesheet"]  = self._custom_css_edit.toPlainText().strip()
        # View / Files
        s["view_mode"]          = self._view_combo.currentData()
        s["icon_size"]          = self._icon_size_slider.value()
        s["folders_first"]      = self._folders_first_cb.isChecked()
        s["show_extensions"]    = self._extensions_cb.isChecked()
        s["show_hidden"]        = self._hidden_cb.isChecked()
        s["color_coding"]       = self._color_cb.isChecked()
        s["show_thumbnails"]    = self._thumbnails_cb.isChecked()
        s["single_click"]       = self._single_click_cb.isChecked()
        s["date_format"]        = self._date_fmt_combo.currentData()
        s["size_unit"]          = self._size_unit_combo.currentData()
        s["column_visibility"]  = [cb.isChecked() for cb in self._col_checks]
        # Panels
        s["show_sidebar"]       = self._sidebar_cb.isChecked()
        s["show_breadcrumb"]    = self._breadcrumb_cb.isChecked()
        s["show_cmdbar"]        = self._cmdbar_cb.isChecked()
        s["preview"]            = self._preview_cb.isChecked()
        s["dual_mode"]          = self._dual_mode_cb.isChecked()
        s["show_terminal"]      = self._terminal_cb.isChecked()
        s["preview_position"]   = self._prev_pos_combo.currentData()
        s["preview_syntax_hl"]  = self._syntax_cb.isChecked()
        s["statusbar_path"]     = self._sb_path_cb.isChecked()
        s["statusbar_disk"]     = self._sb_disk_cb.isChecked()
        s["sidebar_recent_files"] = self._sidebar_rf_cb.isChecked()
        # Search
        s["search_case"]        = self._search_case_cb.isChecked()
        s["search_exclude"]     = self._search_exclude_edit.text().strip()
        # Behavior
        s["startup_folder"]     = self._startup_combo.currentData()
        s["startup_path"]       = self._startup_path_edit.text().strip()
        s["use_trash"]          = self._trash_cb.isChecked()
        s["confirm_delete"]     = self._confirm_cb.isChecked()
        s["hide_tabbar_single"] = self._hide_tabbar_cb.isChecked()
        s["restore_tabs"]       = self._restore_tabs_cb.isChecked()
        s["conflict_action"]    = self._conflict_combo.currentData()
        # Tools
        tools = []
        for row in range(self._tools_table.rowCount()):
            n = (self._tools_table.item(row, 0) or QTableWidgetItem("")).text().strip()
            c = (self._tools_table.item(row, 1) or QTableWidgetItem("")).text().strip()
            if n and c:
                tools.append({"name": n, "command": c})
        s["external_tools"]     = tools
        # System
        s["terminal"]           = self._terminal_combo.currentData()
        return s

    def reject(self):
        """Cancel — revert to settings as they were before opening."""
        self._preview_timer.stop()
        self.settings_changed.emit(self._original)
        super().reject()

    # ── Layout helpers ────────────────────────────────────

    @staticmethod
    def _make_tab() -> tuple:
        """Returns (scroll_widget, inner_vbox_layout)."""
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(24, 8, 24, 20)
        layout.setSpacing(0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(inner)
        return scroll, layout

    @staticmethod
    def _sec(title: str) -> QWidget:
        """Flat section header: TITLE ────────────"""
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 18, 0, 6)
        hl.setSpacing(8)
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            "color: #5a9fd4; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;"
        )
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #2e2e2e; border: none;")
        sep.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hl.addWidget(lbl)
        hl.addWidget(sep, 1)
        return w

    @staticmethod
    def _row(label: str, widget: QWidget, hint: str = "") -> QWidget:
        """Labeled row: right-aligned label + widget."""
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(8, 3, 0, 3)
        hl.setSpacing(12)
        lbl = QLabel(label)
        lbl.setFixedWidth(158)
        lbl.setStyleSheet("color: #aaa; font-size: 12px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setWordWrap(False)
        hl.addWidget(lbl)
        hl.addWidget(widget, 1)
        if hint:
            hint_lbl = QLabel(hint)
            hint_lbl.setStyleSheet("color: #555; font-size: 10px;")
            hl.addWidget(hint_lbl)
        return w

    @staticmethod
    def _cb(toggle) -> QWidget:
        """Indented toggle row."""
        w = QWidget()
        w.setMinimumHeight(34)
        hl = QHBoxLayout(w)
        hl.setContentsMargins(20, 3, 0, 3)
        hl.setSpacing(0)
        hl.addWidget(toggle)
        hl.addStretch()
        return w

    @staticmethod
    def _hint(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #555; font-size: 11px; padding: 0 0 2px 20px;")
        return lbl

    # ── Tab: Apariencia ───────────────────────────────────

    # ── Accent preset palette ─────────────────────────────

    _ACCENT_PRESETS = [
        ("#0078d4", "Windows"),
        ("#7aa2f7", "Tokyo"),
        ("#88C0D0", "Nord"),
        ("#CBA6F7", "Catppuccin"),
        ("#BD93F9", "Dracula"),
        ("#fe8019", "Gruvbox"),
        ("#a6e22e", "Monokai"),
        ("#e06c75", "Rojo"),
        ("#4ec9b0", "Verde"),
        ("#e5c07b", "Ámbar"),
        ("#c678dd", "Morado"),
        ("#56b6c2", "Cian"),
    ]

    _VISUAL_PRESETS = [
        ("Equilibrado", "dark_fluent", "normal", 13, "normal", 0, "thin", False),
        ("Compacto pro", "dark_fluent", "sharp", 12, "compact", 20, "hidden", True),
        ("Cómodo", "light_fluent", "rounded", 14, "comfortable", 34, "normal", False),
        ("Código", "one_dark", "normal", 13, "compact", 22, "thin", True),
        ("Presentación", "dark_fluent", "rounded", 16, "comfortable", 40, "wide", False),
    ]

    def _build_appearance(self) -> QWidget:
        scroll, L = self._make_tab()

        # ── Perfiles rápidos ─────────────────────────────
        L.addWidget(self._sec("Perfiles rápidos"))

        preset_w = QWidget()
        preset_hl = QHBoxLayout(preset_w)
        preset_hl.setContentsMargins(20, 2, 0, 2)
        preset_hl.setSpacing(6)
        for name, theme, radius, font_size, density, row_height, scrollbar, compact_tb in self._VISUAL_PRESETS:
            btn = QPushButton(name)
            btn.setFixedHeight(28)
            btn.setStyleSheet("QPushButton { font-size: 11px; padding: 3px 10px; min-width: 0; }")
            btn.clicked.connect(
                lambda _, th=theme, rd=radius, fs=font_size, dn=density,
                       rh=row_height, sb=scrollbar, tb=compact_tb:
                    self._apply_visual_preset(th, rd, fs, dn, rh, sb, tb)
            )
            preset_hl.addWidget(btn)
        preset_hl.addStretch()
        L.addWidget(preset_w)
        L.addWidget(self._hint("Los perfiles ajustan tema, densidad, tamaño, bordes, filas y barra de herramientas. Puedes retocar cualquier valor después."))

        # ── Idioma ───────────────────────────────────────
        L.addWidget(self._sec(t("dlg.settings.language_label")))

        self._language_combo = QComboBox()
        self._language_combo.addItem(t("dlg.settings.language_auto"), "auto")
        self._language_combo.addItem(t("dlg.settings.language_es"),   "es")
        self._language_combo.addItem(t("dlg.settings.language_en"),   "en")
        lang_map = {"auto": 0, "es": 1, "en": 2}
        self._language_combo.setCurrentIndex(lang_map.get(self._settings.get("language", "auto"), 0))
        L.addWidget(self._row(t("dlg.settings.language_label") + ":", self._language_combo))
        L.addWidget(self._hint(t("dlg.settings.language_restart_note")))

        # ── Tema ─────────────────────────────────────────
        L.addWidget(self._sec("Tema"))

        self._theme_combo = QComboBox()
        for key, theme in THEMES.items():
            self._theme_combo.addItem(theme["name"], key)
        idx = list(THEMES.keys()).index(self._settings.get("theme", "dark_fluent"))
        self._theme_combo.setCurrentIndex(max(0, idx))
        L.addWidget(self._row("Tema:", self._theme_combo))

        self._border_combo = QComboBox()
        self._border_combo.addItem("Angular (Sharp)",  "sharp")
        self._border_combo.addItem("Normal",           "normal")
        self._border_combo.addItem("Redondeado",       "rounded")
        br_map = {"sharp": 0, "normal": 1, "rounded": 2}
        self._border_combo.setCurrentIndex(br_map.get(self._settings.get("border_radius", "normal"), 1))
        L.addWidget(self._row("Radio de bordes:", self._border_combo))

        # ── Color de acento ──────────────────────────────
        L.addWidget(self._sec("Color de acento"))

        # Preset palette chips
        palette_w = QWidget()
        palette_hl = QHBoxLayout(palette_w)
        palette_hl.setContentsMargins(20, 2, 0, 2)
        palette_hl.setSpacing(6)

        self._accent_btn = _ColorButton(self._settings.get("accent_color", ""))
        cur_accent = self._settings.get("accent_color", "")

        for hex_color, tip in self._ACCENT_PRESETS:
            chip = QToolButton()
            chip.setFixedSize(22, 22)
            chip.setToolTip(tip)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setStyleSheet(
                f"QToolButton {{ background: {hex_color}; border: 2px solid transparent;"
                f"border-radius: 11px; }}"
                f"QToolButton:hover {{ border-color: white; }}"
            )
            chip.clicked.connect(lambda _, c=hex_color: self._accent_btn.set_color(c))
            palette_hl.addWidget(chip)

        reset_chip = QToolButton()
        reset_chip.setText("×")
        reset_chip.setFixedSize(22, 22)
        reset_chip.setToolTip("Auto (color del tema)")
        reset_chip.setStyleSheet(
            "QToolButton { background: #444; border: 2px solid #666; border-radius: 11px;"
            "color: #aaa; font-size: 14px; line-height: 18px; }"
            "QToolButton:hover { border-color: white; color: white; }"
        )
        reset_chip.clicked.connect(lambda: self._accent_btn.set_color(""))
        palette_hl.addWidget(reset_chip)
        palette_hl.addStretch()
        L.addWidget(palette_w)

        custom_w = QWidget()
        custom_rl = QHBoxLayout(custom_w)
        custom_rl.setContentsMargins(0, 0, 0, 0)
        custom_rl.setSpacing(8)
        custom_rl.addWidget(self._accent_btn)
        self._accent_hex_edit = QLineEdit(cur_accent)
        self._accent_hex_edit.setPlaceholderText("#0078d4")
        self._accent_hex_edit.setMaxLength(7)
        self._accent_hex_edit.setFixedWidth(82)
        custom_rl.addWidget(self._accent_hex_edit)
        custom_lbl = QLabel("Personalizado")
        custom_lbl.setStyleSheet("color: #666; font-size: 11px;")
        custom_rl.addWidget(custom_lbl)
        custom_rl.addStretch()
        L.addWidget(self._row("Color personalizado:", custom_w))
        self._accent_btn.color_changed.connect(self._sync_hex_from_accent)

        # ── Tipografía ───────────────────────────────────
        L.addWidget(self._sec("Tipografía"))

        # UI font: broad curated list + installed system fonts, with manual entry.
        cur_ff = self._settings.get("font_family", "Segoe UI")
        self._font_family_combo = self._font_combo(_UI_FONT_OPTIONS, cur_ff)
        L.addWidget(self._row("Fuente de interfaz:", self._font_family_combo))

        # Monospace font: common coding fonts + detected mono-like system fonts.
        cur_mono = self._settings.get("monospace_font", "Consolas")
        self._monospace_combo = self._font_combo(_MONO_FONT_OPTIONS, cur_mono, monospace=True)
        L.addWidget(self._row("Fuente monoespaciada:", self._monospace_combo))

        # Font weight
        self._font_weight_combo = QComboBox()
        for lbl, val in [("Light", "light"), ("Normal", "normal"),
                          ("Medium", "medium"), ("SemiBold", "semibold"), ("Bold", "bold")]:
            self._font_weight_combo.addItem(lbl, val)
        fw_keys = ["light", "normal", "medium", "semibold", "bold"]
        cur_fw = self._settings.get("font_weight", "normal")
        self._font_weight_combo.setCurrentIndex(fw_keys.index(cur_fw) if cur_fw in fw_keys else 1)
        L.addWidget(self._row("Peso de fuente:", self._font_weight_combo))

        # Font size slider (9-20px)
        fs_w = QWidget()
        fs_rl = QHBoxLayout(fs_w)
        fs_rl.setContentsMargins(0, 0, 0, 0)
        fs_rl.setSpacing(8)
        self._font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._font_size_slider.setRange(9, 20)
        self._font_size_slider.setSingleStep(1)
        self._font_size_slider.setValue(self._settings.get("font_size", 13))
        self._font_size_label = QLabel(f"{self._settings.get('font_size', 13)}px")
        self._font_size_label.setMinimumWidth(34)
        self._font_size_slider.valueChanged.connect(lambda v: self._font_size_label.setText(f"{v}px"))
        fs_rl.addWidget(self._font_size_slider)
        fs_rl.addWidget(self._font_size_label)
        L.addWidget(self._row("Tamaño de fuente:", fs_w))

        # ── Espaciado ────────────────────────────────────
        L.addWidget(self._sec("Espaciado y densidad"))

        self._density_combo = QComboBox()
        self._density_combo.addItem("Compacto",  "compact")
        self._density_combo.addItem("Normal",    "normal")
        self._density_combo.addItem("Cómodo",    "comfortable")
        d_map = {"compact": 0, "normal": 1, "comfortable": 2}
        self._density_combo.setCurrentIndex(d_map.get(self._settings.get("density", "normal"), 1))
        L.addWidget(self._row("Densidad predefinida:", self._density_combo))

        rh_w = QWidget()
        rh_rl = QHBoxLayout(rh_w)
        rh_rl.setContentsMargins(0, 0, 0, 0)
        rh_rl.setSpacing(8)
        self._row_height_slider = QSlider(Qt.Orientation.Horizontal)
        self._row_height_slider.setRange(0, 48)
        self._row_height_slider.setSingleStep(1)
        self._row_height_slider.setValue(self._settings.get("row_height", 0))
        self._row_height_label = QLabel()
        self._row_height_label.setMinimumWidth(50)
        def _rh_lbl(v): self._row_height_label.setText("Auto" if v == 0 else f"{v}px")
        _rh_lbl(self._settings.get("row_height", 0))
        self._row_height_slider.valueChanged.connect(_rh_lbl)
        rh_rl.addWidget(self._row_height_slider)
        rh_rl.addWidget(self._row_height_label)
        L.addWidget(self._row("Altura de filas:", rh_w))
        L.addWidget(self._hint("0 = usar densidad predefinida  |  1-48 px = valor exacto"))

        # ── Ventana y chrome ─────────────────────────────
        L.addWidget(self._sec("Ventana y chrome"))

        opacity_w = QWidget()
        opacity_rl = QHBoxLayout(opacity_w)
        opacity_rl.setContentsMargins(0, 0, 0, 0)
        opacity_rl.setSpacing(8)
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(60, 100)
        self._opacity_slider.setValue(self._settings.get("opacity", 100))
        self._opacity_label = QLabel(f"{self._settings.get('opacity', 100)}%")
        self._opacity_label.setMinimumWidth(36)
        self._opacity_slider.valueChanged.connect(lambda v: self._opacity_label.setText(f"{v}%"))
        opacity_rl.addWidget(self._opacity_slider)
        opacity_rl.addWidget(self._opacity_label)
        L.addWidget(self._row("Opacidad:", opacity_w))

        sidebar_w = QWidget()
        sw_rl = QHBoxLayout(sidebar_w)
        sw_rl.setContentsMargins(0, 0, 0, 0)
        sw_rl.setSpacing(8)
        self._sidebar_width_slider = QSlider(Qt.Orientation.Horizontal)
        self._sidebar_width_slider.setRange(120, 320)
        self._sidebar_width_slider.setValue(self._settings.get("sidebar_width", 200))
        self._sidebar_width_label = QLabel(f"{self._settings.get('sidebar_width', 200)}px")
        self._sidebar_width_label.setMinimumWidth(40)
        self._sidebar_width_slider.valueChanged.connect(
            lambda v: self._sidebar_width_label.setText(f"{v}px"))
        sw_rl.addWidget(self._sidebar_width_slider)
        sw_rl.addWidget(self._sidebar_width_label)
        L.addWidget(self._row("Ancho de sidebar:", sidebar_w))

        self._toolbar_compact_cb = ToggleSwitch("Barra de herramientas compacta")
        self._toolbar_compact_cb.setChecked(self._settings.get("toolbar_compact", False))
        L.addWidget(self._cb(self._toolbar_compact_cb))

        # ── Barras de desplazamiento ─────────────────────
        L.addWidget(self._sec("Barras de desplazamiento"))

        self._scrollbar_combo = QComboBox()
        self._scrollbar_combo.addItem("Oculta  (solo visible al pasar)",  "hidden")
        self._scrollbar_combo.addItem("Fina  (6px)",                       "thin")
        self._scrollbar_combo.addItem("Normal  (10px)",                    "normal")
        self._scrollbar_combo.addItem("Ancha  (14px)",                     "wide")
        sb_map = {"hidden": 0, "thin": 1, "normal": 2, "wide": 3}
        self._scrollbar_combo.setCurrentIndex(sb_map.get(self._settings.get("scrollbar_style", "thin"), 1))
        L.addWidget(self._row("Estilo:", self._scrollbar_combo))

        # ── Animaciones ──────────────────────────────────
        L.addWidget(self._sec("Animaciones"))

        self._anim_speed_combo = QComboBox()
        self._anim_speed_combo.addItem("Sin animación",   "none")
        self._anim_speed_combo.addItem("Rápido",          "fast")
        self._anim_speed_combo.addItem("Normal",          "normal")
        self._anim_speed_combo.addItem("Lento",           "slow")
        asp_map = {"none": 0, "fast": 1, "normal": 2, "slow": 3}
        self._anim_speed_combo.setCurrentIndex(asp_map.get(self._settings.get("animation_speed", "normal"), 2))
        L.addWidget(self._row("Velocidad:", self._anim_speed_combo))

        # ── CSS avanzado ─────────────────────────────────
        L.addWidget(self._sec("CSS avanzado"))
        self._custom_css_edit = QTextEdit()
        self._custom_css_edit.setAcceptRichText(False)
        self._custom_css_edit.setPlaceholderText("QTreeView::item:selected { background-color: #264f78; }")
        self._custom_css_edit.setMinimumHeight(96)
        self._custom_css_edit.setPlainText(self._settings.get("custom_stylesheet", ""))
        L.addWidget(self._row("Estilo extra:", self._custom_css_edit))
        L.addWidget(self._hint("Se añade al final del tema. Úsalo para retoques finos de Qt StyleSheet; si algo queda raro, borra este campo."))

        L.addStretch()
        return scroll

    def _apply_visual_preset(self, theme: str, radius: str, font_size: int,
                             density: str, row_height: int,
                             scrollbar: str, compact_toolbar: bool):
        theme_keys = list(THEMES.keys())
        if theme in theme_keys:
            self._theme_combo.setCurrentIndex(theme_keys.index(theme))
        self._border_combo.setCurrentIndex({"sharp": 0, "normal": 1, "rounded": 2}.get(radius, 1))
        self._font_size_slider.setValue(font_size)
        self._density_combo.setCurrentIndex({"compact": 0, "normal": 1, "comfortable": 2}.get(density, 1))
        self._row_height_slider.setValue(row_height)
        self._scrollbar_combo.setCurrentIndex({"hidden": 0, "thin": 1, "normal": 2, "wide": 3}.get(scrollbar, 1))
        self._toolbar_compact_cb.setChecked(compact_toolbar)
        self._schedule_preview()

    def _sync_hex_from_accent(self, color: str):
        self._accent_hex_edit.setText(color)
        self._schedule_preview()

    def _set_accent_from_hex(self):
        value = self._accent_hex_edit.text().strip()
        if not value:
            self._accent_btn.set_color("")
            return
        if not value.startswith("#"):
            value = f"#{value}"
        if len(value) == 7 and QColor(value).isValid():
            self._accent_btn.set_color(value.lower())
            self._accent_hex_edit.setStyleSheet("")
        else:
            self._accent_hex_edit.setStyleSheet("QLineEdit { border-color: #e06c75; }")

    # ── Tab: Archivos ────────────────────────────────────

    def _build_view(self) -> QWidget:
        scroll, L = self._make_tab()

        # ── Visualización ────────────────────────────────
        L.addWidget(self._sec("Visualización"))

        self._view_combo = QComboBox()
        self._view_combo.addItem("Detalles",       0)
        self._view_combo.addItem("Iconos grandes", 1)
        self._view_combo.addItem("Lista",          2)
        self._view_combo.setCurrentIndex(self._settings.get("view_mode", 0))
        L.addWidget(self._row("Vista por defecto:", self._view_combo))

        icon_w = QWidget()
        icon_rl = QHBoxLayout(icon_w)
        icon_rl.setContentsMargins(0, 0, 0, 0)
        icon_rl.setSpacing(8)
        self._icon_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._icon_size_slider.setRange(48, 256)
        self._icon_size_slider.setSingleStep(16)
        self._icon_size_slider.setValue(self._settings.get("icon_size", 96))
        self._icon_size_label = QLabel(f"{self._settings.get('icon_size', 96)}px")
        self._icon_size_label.setMinimumWidth(40)
        self._icon_size_slider.valueChanged.connect(lambda v: self._icon_size_label.setText(f"{v}px"))
        icon_rl.addWidget(self._icon_size_slider)
        icon_rl.addWidget(self._icon_size_label)
        L.addWidget(self._row("Tamaño de iconos:", icon_w))

        # ── Archivos ─────────────────────────────────────
        L.addWidget(self._sec("Archivos"))

        self._folders_first_cb = ToggleSwitch("Mostrar carpetas primero")
        self._folders_first_cb.setChecked(self._settings.get("folders_first", True))
        L.addWidget(self._cb(self._folders_first_cb))

        self._extensions_cb = ToggleSwitch("Mostrar extensiones de archivo  (.txt, .py…)")
        self._extensions_cb.setChecked(self._settings.get("show_extensions", True))
        L.addWidget(self._cb(self._extensions_cb))

        self._hidden_cb = ToggleSwitch("Mostrar archivos ocultos")
        self._hidden_cb.setChecked(self._settings.get("show_hidden", False))
        L.addWidget(self._cb(self._hidden_cb))

        self._color_cb = ToggleSwitch("Colorear nombres por tipo de archivo")
        self._color_cb.setChecked(self._settings.get("color_coding", False))
        L.addWidget(self._cb(self._color_cb))

        self._thumbnails_cb = ToggleSwitch("Mostrar miniaturas de imágenes")
        self._thumbnails_cb.setChecked(self._settings.get("show_thumbnails", True))
        L.addWidget(self._cb(self._thumbnails_cb))

        # ── Formato ──────────────────────────────────────
        L.addWidget(self._sec("Formato de fecha y tamaño"))

        self._date_fmt_combo = QComboBox()
        self._date_fmt_combo.addItem("Absoluto  (15/05/2026  14:30)", "absolute")
        self._date_fmt_combo.addItem("Relativo  (Hace 3 días)",        "relative")
        df_map = {"absolute": 0, "relative": 1}
        self._date_fmt_combo.setCurrentIndex(df_map.get(self._settings.get("date_format", "absolute"), 0))
        L.addWidget(self._row("Formato de fecha:", self._date_fmt_combo))

        self._size_unit_combo = QComboBox()
        self._size_unit_combo.addItem("Automático",     "auto")
        self._size_unit_combo.addItem("Bytes (B)",      "b")
        self._size_unit_combo.addItem("Kilobytes (KB)", "kb")
        self._size_unit_combo.addItem("Megabytes (MB)", "mb")
        self._size_unit_combo.addItem("Gigabytes (GB)", "gb")
        su_map = {"auto": 0, "b": 1, "kb": 2, "mb": 3, "gb": 4}
        self._size_unit_combo.setCurrentIndex(su_map.get(self._settings.get("size_unit", "auto"), 0))
        L.addWidget(self._row("Unidad de tamaño:", self._size_unit_combo))

        # ── Columnas (vista Detalles) ─────────────────────
        L.addWidget(self._sec("Columnas visibles (vista Detalles)"))

        col_vis = self._settings.get("column_visibility", [True, True, True, True])
        self._col_checks = []
        for i, name in enumerate(["Nombre", "Tamaño", "Tipo", "Fecha modificación"]):
            cb = ToggleSwitch(name)
            cb.setChecked(col_vis[i] if i < len(col_vis) else True)
            cb.setEnabled(i != 0)
            L.addWidget(self._cb(cb))
            self._col_checks.append(cb)

        # ── Interacción ──────────────────────────────────
        L.addWidget(self._sec("Interacción"))

        self._single_click_cb = ToggleSwitch("Abrir con un solo clic  (por defecto: doble clic)")
        self._single_click_cb.setChecked(self._settings.get("single_click", False))
        L.addWidget(self._cb(self._single_click_cb))

        L.addStretch()
        return scroll

    # ── Tab: Paneles ─────────────────────────────────────

    def _build_panels(self) -> QWidget:
        scroll, L = self._make_tab()

        # ── Visibilidad ──────────────────────────────────
        L.addWidget(self._sec("Visibilidad de paneles"))

        self._sidebar_cb = ToggleSwitch("Barra lateral  (acceso rápido, unidades, marcadores)")
        self._sidebar_cb.setChecked(self._settings.get("show_sidebar", True))
        L.addWidget(self._cb(self._sidebar_cb))

        self._breadcrumb_cb = ToggleSwitch("Barra de ruta  (breadcrumb)")
        self._breadcrumb_cb.setChecked(self._settings.get("show_breadcrumb", True))
        L.addWidget(self._cb(self._breadcrumb_cb))

        self._cmdbar_cb = ToggleSwitch("Barra de comandos  (Abrir, Copiar, Pegar…)")
        self._cmdbar_cb.setChecked(self._settings.get("show_cmdbar", True))
        L.addWidget(self._cb(self._cmdbar_cb))

        self._preview_cb = ToggleSwitch("Panel de vista previa")
        self._preview_cb.setChecked(self._settings.get("preview", True))
        L.addWidget(self._cb(self._preview_cb))

        self._dual_mode_cb = ToggleSwitch("Vista de panel dual")
        self._dual_mode_cb.setChecked(self._settings.get("dual_mode", False))
        L.addWidget(self._cb(self._dual_mode_cb))

        self._terminal_cb = ToggleSwitch("Terminal integrada")
        self._terminal_cb.setChecked(self._settings.get("show_terminal", False))
        L.addWidget(self._cb(self._terminal_cb))

        # ── Vista previa ─────────────────────────────────
        L.addWidget(self._sec("Opciones de vista previa"))

        self._prev_pos_combo = QComboBox()
        self._prev_pos_combo.addItem("Derecha (vertical)",  "right")
        self._prev_pos_combo.addItem("Abajo (horizontal)",  "bottom")
        pp_map = {"right": 0, "bottom": 1}
        self._prev_pos_combo.setCurrentIndex(pp_map.get(self._settings.get("preview_position", "right"), 0))
        L.addWidget(self._row("Posición:", self._prev_pos_combo))

        self._syntax_cb = ToggleSwitch("Resaltado de sintaxis en texto y código")
        self._syntax_cb.setChecked(self._settings.get("preview_syntax_hl", True))
        L.addWidget(self._cb(self._syntax_cb))

        # ── Barra de estado ──────────────────────────────
        L.addWidget(self._sec("Barra de estado"))

        self._sb_path_cb = ToggleSwitch("Mostrar ruta actual")
        self._sb_path_cb.setChecked(self._settings.get("statusbar_path", True))
        L.addWidget(self._cb(self._sb_path_cb))

        self._sb_disk_cb = ToggleSwitch("Mostrar espacio en disco")
        self._sb_disk_cb.setChecked(self._settings.get("statusbar_disk", True))
        L.addWidget(self._cb(self._sb_disk_cb))

        # ── Sidebar ──────────────────────────────────────
        L.addWidget(self._sec("Barra lateral"))

        self._sidebar_rf_cb = ToggleSwitch("Mostrar sección de archivos recientes")
        self._sidebar_rf_cb.setChecked(self._settings.get("sidebar_recent_files", True))
        L.addWidget(self._cb(self._sidebar_rf_cb))

        L.addStretch()
        return scroll

    # ── Tab: Comportamiento ──────────────────────────────

    def _build_behavior(self) -> QWidget:
        scroll, L = self._make_tab()

        # ── Inicio ───────────────────────────────────────
        L.addWidget(self._sec("Carpeta de inicio"))

        self._startup_combo = QComboBox()
        self._startup_combo.addItem("Carpeta personal (Inicio)", "home")
        self._startup_combo.addItem("Última carpeta visitada",   "last")
        self._startup_combo.addItem("Carpeta personalizada…",    "custom")
        sf = self._settings.get("startup_folder", "home")
        sf_map = {"home": 0, "last": 1, "custom": 2}
        self._startup_combo.setCurrentIndex(sf_map.get(sf, 0))
        self._startup_combo.currentIndexChanged.connect(self._on_startup_combo_changed)
        L.addWidget(self._row("Al iniciar, abrir:", self._startup_combo))

        custom_row = QWidget()
        custom_rl = QHBoxLayout(custom_row)
        custom_rl.setContentsMargins(0, 0, 0, 0)
        custom_rl.setSpacing(6)
        self._startup_path_edit = QLineEdit(self._settings.get("startup_path", ""))
        self._startup_path_edit.setPlaceholderText("Ruta de carpeta…")
        browse_btn = QToolButton()
        browse_btn.setText("…")
        browse_btn.clicked.connect(self._browse_startup)
        custom_rl.addWidget(self._startup_path_edit)
        custom_rl.addWidget(browse_btn)
        self._startup_path_row = self._row("Carpeta:", custom_row)
        self._startup_path_row.setVisible(sf == "custom")
        L.addWidget(self._startup_path_row)

        # ── Eliminación ──────────────────────────────────
        L.addWidget(self._sec("Eliminación"))

        self._trash_cb = ToggleSwitch("Mover a la papelera de reciclaje  (recomendado)")
        self._trash_cb.setChecked(self._settings.get("use_trash", True))
        L.addWidget(self._cb(self._trash_cb))

        self._confirm_cb = ToggleSwitch("Pedir confirmación antes de eliminar")
        self._confirm_cb.setChecked(self._settings.get("confirm_delete", True))
        L.addWidget(self._cb(self._confirm_cb))

        # ── Pestañas ─────────────────────────────────────
        L.addWidget(self._sec("Pestañas"))

        self._hide_tabbar_cb = ToggleSwitch("Ocultar barra de pestañas con una sola pestaña")
        self._hide_tabbar_cb.setChecked(self._settings.get("hide_tabbar_single", False))
        L.addWidget(self._cb(self._hide_tabbar_cb))

        # ── Sesión ───────────────────────────────────────
        L.addWidget(self._sec("Sesión"))

        self._restore_tabs_cb = ToggleSwitch("Restaurar pestañas abiertas al iniciar")
        self._restore_tabs_cb.setChecked(self._settings.get("restore_tabs", False))
        L.addWidget(self._cb(self._restore_tabs_cb))

        # ── Conflictos al copiar/mover ───────────────────
        L.addWidget(self._sec("Conflictos al copiar / mover"))

        self._conflict_combo = QComboBox()
        self._conflict_combo.addItem("Renombrar automáticamente  (archivo (1).txt)", "rename")
        self._conflict_combo.addItem("Saltar  (no sobrescribir)",                    "skip")
        self._conflict_combo.addItem("Preguntar al usuario",                         "ask")
        ca_map = {"rename": 0, "skip": 1, "ask": 2}
        self._conflict_combo.setCurrentIndex(ca_map.get(self._settings.get("conflict_action", "rename"), 0))
        L.addWidget(self._row("Si el destino existe:", self._conflict_combo))

        L.addStretch()
        return scroll

    def _on_startup_combo_changed(self, idx: int):
        is_custom = self._startup_combo.currentData() == "custom"
        self._startup_path_row.setVisible(is_custom)

    def _browse_startup(self):
        path = QFileDialog.getExistingDirectory(
            self, "Elegir carpeta de inicio",
            self._startup_path_edit.text() or str(Path.home())
        )
        if path:
            self._startup_path_edit.setText(path)

    # ── Tab: Búsqueda ────────────────────────────────────

    def _build_search(self) -> QWidget:
        scroll, L = self._make_tab()

        L.addWidget(self._sec("Opciones de búsqueda"))

        self._search_case_cb = ToggleSwitch("Búsqueda sensible a mayúsculas / minúsculas")
        self._search_case_cb.setChecked(self._settings.get("search_case", False))
        L.addWidget(self._cb(self._search_case_cb))

        L.addWidget(self._sec("Carpetas excluidas en búsqueda recursiva"))

        self._search_exclude_edit = QLineEdit(self._settings.get("search_exclude", ".git,node_modules"))
        self._search_exclude_edit.setPlaceholderText(".git, node_modules, __pycache__")
        self._search_exclude_edit.setToolTip("Carpetas separadas por comas")
        L.addWidget(self._row("Excluir:", self._search_exclude_edit))
        L.addWidget(self._hint("Separa los nombres de carpeta con comas.  Ejemplo: .git, node_modules, __pycache__, .venv"))

        L.addStretch()
        return scroll

    # ── Tab: Herramientas ────────────────────────────────

    def _build_tools(self) -> QWidget:
        scroll, L = self._make_tab()
        L.addWidget(self._sec("Herramientas externas  (menú contextual → Abrir con)"))
        L.addWidget(self._hint("Usa %s como marcador para la ruta del archivo.  Ejemplo: code \"%s\"  |  notepad++ \"%s\""))
        L.addSpacing(6)

        tl = L

        self._tools_table = QTableWidget()
        self._tools_table.setColumnCount(2)
        self._tools_table.setHorizontalHeaderLabels(["Nombre", "Comando"])
        self._tools_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._tools_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._tools_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tools_table.setAlternatingRowColors(True)
        self._tools_table.verticalHeader().setVisible(False)
        self._tools_table.setMinimumHeight(160)

        tools = self._settings.get("external_tools", [])
        self._tools_table.setRowCount(len(tools))
        for i, tool in enumerate(tools):
            self._tools_table.setItem(i, 0, QTableWidgetItem(tool.get("name", "")))
            self._tools_table.setItem(i, 1, QTableWidgetItem(tool.get("command", "")))
        tl.addWidget(self._tools_table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Agregar")
        add_btn.setFixedWidth(100)
        add_btn.clicked.connect(self._add_tool_row)
        del_btn = QPushButton("− Eliminar")
        del_btn.setFixedWidth(100)
        del_btn.clicked.connect(self._del_tool_row)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        tl.addLayout(btn_row)

        # Preset tools
        preset_lbl = QLabel("Agregar rápido:")
        preset_lbl.setStyleSheet("color: #888; font-size: 11px;")
        tl.addWidget(preset_lbl)

        presets_row = QHBoxLayout()
        for name, cmd in [
            ("VSCode",      'code "%s"'),
            ("Notepad++",   'notepad++ "%s"'),
            ("7-Zip",       '"C:\\Program Files\\7-Zip\\7z.exe" e "%s"'),
            ("Explorador",  'explorer /select,"%s"'),
        ]:
            pb = QPushButton(name)
            pb.setFixedHeight(26)
            pb.setStyleSheet("QPushButton { font-size: 11px; padding: 2px 8px; }")
            pb.clicked.connect(lambda _, n=name, c=cmd: self._add_preset_tool(n, c))
            presets_row.addWidget(pb)
        presets_row.addStretch()
        tl.addLayout(presets_row)

        L.addStretch()
        return scroll

    def _add_tool_row(self):
        r = self._tools_table.rowCount()
        self._tools_table.insertRow(r)
        self._tools_table.setItem(r, 0, QTableWidgetItem(""))
        self._tools_table.setItem(r, 1, QTableWidgetItem(""))
        self._tools_table.editItem(self._tools_table.item(r, 0))

    def _del_tool_row(self):
        rows = sorted({i.row() for i in self._tools_table.selectedItems()}, reverse=True)
        for r in rows:
            self._tools_table.removeRow(r)

    def _add_preset_tool(self, name: str, command: str):
        r = self._tools_table.rowCount()
        self._tools_table.insertRow(r)
        self._tools_table.setItem(r, 0, QTableWidgetItem(name))
        self._tools_table.setItem(r, 1, QTableWidgetItem(command))

    # ── Tab: Sistema ──────────────────────────────────────

    def _build_system(self) -> QWidget:
        scroll, L = self._make_tab()

        # ── Terminal ─────────────────────────────────────
        L.addWidget(self._sec("Terminal preferida"))

        self._terminal_combo = QComboBox()
        self._terminal_combo.addItem("Automático  (wt → PowerShell → cmd)", "auto")
        self._terminal_combo.addItem("Windows Terminal  (wt)",               "wt")
        self._terminal_combo.addItem("PowerShell Core  (pwsh)",              "pwsh")
        self._terminal_combo.addItem("PowerShell  (powershell.exe)",         "powershell")
        self._terminal_combo.addItem("Símbolo del sistema  (cmd.exe)",       "cmd")
        pref = self._settings.get("terminal", "auto")
        keys = ["auto", "wt", "pwsh", "powershell", "cmd"]
        self._terminal_combo.setCurrentIndex(keys.index(pref) if pref in keys else 0)
        L.addWidget(self._row("Terminal:", self._terminal_combo))

        # ── Importar / Exportar ──────────────────────────
        L.addWidget(self._sec("Importar / Exportar configuración"))

        io_w = QWidget()
        io_rl = QHBoxLayout(io_w)
        io_rl.setContentsMargins(20, 4, 0, 4)
        io_rl.setSpacing(8)
        export_btn = QPushButton("📤  Exportar…")
        export_btn.setFixedWidth(130)
        export_btn.clicked.connect(self._export_settings)
        import_btn = QPushButton("📥  Importar…")
        import_btn.setFixedWidth(130)
        import_btn.clicked.connect(self._import_settings)
        io_rl.addWidget(export_btn)
        io_rl.addWidget(import_btn)
        io_rl.addStretch()
        L.addWidget(io_w)

        # ── Información ──────────────────────────────────
        L.addWidget(self._sec("Información"))

        cfg_lbl = QLabel(SETTINGS_FILE)
        cfg_lbl.setWordWrap(True)
        cfg_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cfg_lbl.setStyleSheet("color: #555; font-size: 11px; padding: 2px 0 2px 20px;")
        L.addWidget(cfg_lbl)

        reset_btn = QPushButton("⚠  Restablecer todos los ajustes a sus valores por defecto")
        reset_btn.setStyleSheet(
            "QPushButton { background: #3c1a1a; color: #e06c75; border: 1px solid #5a2a2a;"
            "border-radius: 5px; padding: 7px 16px; margin: 8px 20px 0 20px; }"
            "QPushButton:hover { background: #4a2020; }"
        )
        reset_btn.clicked.connect(self._reset_defaults)
        L.addWidget(reset_btn)

        L.addStretch()
        return scroll

    def _export_settings(self):
        import shutil
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar configuración", "file_explorer_settings.json",
            "JSON (*.json)"
        )
        if path:
            try:
                shutil.copy2(SETTINGS_FILE, path)
                QMessageBox.information(self, t("settings.exported_title"), t("settings.exported_body", path=path))
            except Exception as e:
                get_logger("settings").exception("Failed to export settings to %s", path)
                QMessageBox.warning(self, t("err.settings_export_title"), str(e))

    def _import_settings(self):
        import shutil
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar configuración", str(Path.home()),
            "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            shutil.copy2(path, SETTINGS_FILE)
            merged = dict(_DEFAULTS)
            merged.update(data)
            self._settings = merged
            save_settings(merged)
            self.settings_changed.emit(merged)
            QMessageBox.information(self, t("settings.imported_title"), t("settings.imported_body"))
            self.accept()
        except Exception as e:
            get_logger("settings").exception("Failed to import settings from %s", path)
            QMessageBox.warning(self, t("err.settings_import_title"), str(e))

    def _reset_defaults(self):
        r = QMessageBox.question(
            self, t("settings.reset_title"),
            t("settings.reset_body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        save_settings(_DEFAULTS)
        self.settings_changed.emit(dict(_DEFAULTS))
        self.accept()

    # ── Accept ────────────────────────────────────────────

    def _on_accept(self):
        self._preview_timer.stop()
        s = self._collect_settings()
        save_settings(s)
        self._settings = s
        self.settings_changed.emit(s)
        self.accept()
