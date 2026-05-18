import os
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QTabWidget, QTabBar, QToolBar, QStatusBar,
    QLineEdit, QLabel, QMenu, QApplication, QMessageBox,
    QPushButton, QFrame, QSizePolicy, QToolButton, QCompleter,
    QComboBox,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QSettings, QStringListModel
from PyQt6.QtGui import QAction, QKeySequence, QFont, QColor

from src.sidebar import Sidebar
from src.file_panel import FilePanelTab, VIEW_DETAILS, VIEW_ICONS, VIEW_LIST
from src.themes import get_stylesheet, THEMES, get_accent_color
from src.settings_dialog import SettingsDialog, load_settings, save_settings
from src.utils import get_user_dirs
from src.recent_folders import load_recent, push_recent, clear_recent
from src.settings_dialog import save_settings
from src import icon_provider as ico

from src.widgets.tab_widget import TabWidget
from src.widgets.address_bar import AddressBar
from src.widgets.terminal_panel import TerminalPanel
from src.widgets.transfer_manager import TransferManager
from src.widgets.spotlight import SpotlightBar


# ── Main window ───────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._settings = load_settings()
        self._active_workers = []
        self._preview_visible  = self._settings.get("preview",      True)
        self._sidebar_visible  = self._settings.get("show_sidebar", True)
        self._dual_mode        = self._settings.get("dual_mode",    False)
        self._terminal_visible = self._settings.get("show_terminal", False)

        self.setWindowTitle("Explorador de Archivos")
        self.resize(1280, 780)
        self.setMinimumSize(860, 560)

        self._apply_theme(
            self._settings.get("theme",            "dark_fluent"),
            self._settings.get("accent_color",     ""),
            self._settings.get("font_size",        13),
            self._settings.get("density",          "normal"),
            self._settings.get("font_family",      "Segoe UI"),
            self._settings.get("border_radius",    "normal"),
            self._settings.get("font_weight",      "normal"),
            self._settings.get("scrollbar_style",  "thin"),
            self._settings.get("toolbar_compact",  False),
            self._settings.get("row_height",       0),
        )
        self._build_ui()
        self._build_menu()
        self._restore_geometry()

        # Startup tabs
        start_path = self._get_startup_path()
        if self._settings.get("restore_tabs") and self._settings.get("_tab_sessions"):
            opened = 0
            for path in self._settings["_tab_sessions"]:
                if os.path.isdir(path):
                    self._add_tab(path)
                    opened += 1
            if opened == 0:
                self._add_tab(start_path)
        else:
            self._add_tab(start_path)
            if self._dual_mode:
                self._add_tab(start_path, target_side="right")

    # ── UI ────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_v = QVBoxLayout(central)
        root_v.setContentsMargins(0, 0, 0, 0)
        root_v.setSpacing(0)

        self._v_splitter = QSplitter(Qt.Orientation.Vertical)
        self._v_splitter.setHandleWidth(1)
        self._v_splitter.setStyleSheet("QSplitter::handle { background: #2a2a2a; }")
        root_v.addWidget(self._v_splitter)

        # Upper area: Sidebar + Tabs + Transfer Manager
        self._upper_container = QWidget()
        root_h = QHBoxLayout(self._upper_container)
        root_h.setContentsMargins(0, 0, 0, 0)
        root_h.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.navigate.connect(self._sidebar_navigate)
        self._sidebar.setVisible(self._sidebar_visible)
        self._sidebar.setFixedWidth(self._settings.get("sidebar_width", 200))
        root_h.addWidget(self._sidebar)

        self._sidebar_sep = QFrame()
        self._sidebar_sep.setFrameShape(QFrame.Shape.VLine)
        self._sidebar_sep.setFixedWidth(1)
        self._sidebar_sep.setStyleSheet("border: none; background: #2a2a2a;")
        self._sidebar_sep.setVisible(self._sidebar_visible)
        root_h.addWidget(self._sidebar_sep)

        # Tab Splitter for Dual Panel
        self._tab_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._tab_splitter.setHandleWidth(1)
        self._tab_splitter.setStyleSheet("QSplitter::handle { background: #2a2a2a; }")
        root_h.addWidget(self._tab_splitter)

        self._left_tabs = TabWidget()
        self._setup_tabs(self._left_tabs)
        self._tab_splitter.addWidget(self._left_tabs)

        self._right_tabs = TabWidget()
        self._setup_tabs(self._right_tabs)
        self._tab_splitter.addWidget(self._right_tabs)
        self._right_tabs.setVisible(self._dual_mode)

        self._active_tabs = self._left_tabs
        
        # Transfer Manager (right sidebar)
        self._transfer_mgr = TransferManager()
        self._transfer_mgr.setVisible(False)
        root_h.addWidget(self._transfer_mgr)
        
        self._v_splitter.addWidget(self._upper_container)

        # Terminal Panel
        self._terminal = TerminalPanel()
        self._terminal.setVisible(self._terminal_visible)
        self._v_splitter.addWidget(self._terminal)
        self._v_splitter.setStretchFactor(0, 4)
        self._v_splitter.setStretchFactor(1, 1)

        self._build_toolbar()
        self._build_statusbar()
        self._update_statusbar_items()
        
        # Spotlight Bar (global command/search)
        self._spotlight = SpotlightBar(self)
        self._spotlight.hide()
        self._spotlight.command_selected.connect(self._handle_spotlight_command)

    def _handle_spotlight_command(self, cmd_type, value):
        if cmd_type == "cmd":
            if value == "theme_dark":
                self._settings["theme"] = "dark_fluent"
                self._apply_settings(self._settings)
                save_settings(self._settings)
            elif value == "theme_light":
                self._settings["theme"] = "light_fluent"
                self._apply_settings(self._settings)
                save_settings(self._settings)
            elif value == "new_tab":
                self._new_tab_from_current()
            elif value == "new_folder":
                self._new_folder()
            elif value == "open_terminal":
                self._toggle_terminal()
            elif value == "settings":
                self._open_settings()
        elif cmd_type == "path":
            if os.path.isdir(value):
                self._navigate_to(value)
            else:
                from src.utils import open_file
                open_file(value)
        elif cmd_type == "search":
            # Start search in current panel
            self._search_bar.setText(value)
            self._search_bar.setFocus()

    def _setup_tabs(self, tabs: TabWidget):
        tabs.new_tab_requested.connect(lambda p, t=tabs: self._add_tab(p, target_side=t))
        tabs.duplicate_tab_path.connect(lambda p, t=tabs: self._add_tab(p, target_side=t))
        tabs.currentChanged.connect(lambda _, t=tabs: self._on_tab_changed(t))
        tabs.tabCloseRequested.connect(lambda _, t=tabs: self._update_tabbar_visibility())
        # Track focus to set active panel
        tabs.tabBar().installEventFilter(self)

    def _build_toolbar(self):
        tb = QToolBar()
        tb.setObjectName("MainToolbar")
        tb.setMovable(False)
        tb.setFloatable(False)
        tb.setIconSize(QSize(20, 20))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        tb.setContentsMargins(0, 0, 0, 0)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)
        self._toolbar = tb

        def _act(icon_fn, tip: str, shortcut: str = "") -> QAction:
            a = QAction(self)
            a.setIcon(icon_fn())
            a.setToolTip(f"{tip}  {shortcut}" if shortcut else tip)
            if shortcut:
                a.setShortcut(shortcut)
            tb.addAction(a)
            return a

        self._act_back    = _act(ico.nav_back,  "Atrás",      "Alt+Left")
        self._act_forward = _act(ico.nav_fwd,   "Adelante",   "Alt+Right")
        self._act_up      = _act(ico.nav_up,    "Subir",      "Alt+Up")
        self._act_home    = _act(ico.nav_home,  "Inicio")
        tb.addSeparator()
        self._act_refresh = _act(ico.refresh,   "Actualizar", "F5")
        tb.addSeparator()

        self._act_back.triggered.connect(self._go_back)
        self._act_forward.triggered.connect(self._go_forward)
        self._act_up.triggered.connect(self._go_up)
        self._act_home.triggered.connect(self._go_home)
        self._act_refresh.triggered.connect(self._refresh)

        # Address bar + history dropdown
        addr_container = QWidget()
        addr_layout    = QHBoxLayout(addr_container)
        addr_layout.setContentsMargins(2, 0, 2, 0)
        addr_layout.setSpacing(2)

        self._address_bar = AddressBar()
        self._address_bar.setMinimumWidth(240)
        self._address_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._address_bar.navigate_requested.connect(self._on_address_entered)

        self._hist_btn = QToolButton()
        self._hist_btn.setText("▾")
        self._hist_btn.setToolTip("Historial reciente")
        self._hist_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hist_btn.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid #444;"
            "border-radius: 4px; color: #888; padding: 4px 6px; }"
            "QToolButton:hover { background: #333; color: #ccc; }"
        )
        self._hist_btn.clicked.connect(self._show_history_menu)

        addr_layout.addWidget(self._address_bar)
        addr_layout.addWidget(self._hist_btn)
        tb.addWidget(addr_container)
        tb.addSeparator()

        # Search bar + recursive toggle
        search_container = QWidget()
        search_layout    = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(2)

        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("🔍  Buscar…")
        self._search_bar.setMinimumWidth(160)
        self._search_bar.setMaximumWidth(280)
        self._search_bar.setClearButtonEnabled(True)
        self._search_bar.setToolTip("Buscar en carpeta actual  Ctrl+F")
        self._search_bar.textChanged.connect(self._on_search)

        self._recursive_btn = QToolButton()
        self._recursive_btn.setIcon(ico.search_recursive())
        self._recursive_btn.setIconSize(QSize(16, 16))
        self._recursive_btn.setToolTip("Buscar en subcarpetas  Ctrl+Shift+F")
        self._recursive_btn.setCheckable(True)
        self._recursive_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._recursive_btn.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid #444;"
            "border-radius: 4px; padding: 4px 6px; }"
            "QToolButton:hover { background: #333; }"
            "QToolButton:checked { background: #094771; border-color: #1a7bc4; }"
        )
        self._recursive_btn.toggled.connect(self._toggle_recursive_search)

        search_layout.addWidget(self._search_bar)
        search_layout.addWidget(self._recursive_btn)
        tb.addWidget(search_container)
        tb.addSeparator()

        # File type filter
        self._type_filter_combo = QComboBox()
        self._type_filter_combo.addItem("Todos",      "all")
        self._type_filter_combo.addItem("🖼 Imágenes", "images")
        self._type_filter_combo.addItem("🎬 Vídeo",   "video")
        self._type_filter_combo.addItem("🎵 Audio",   "audio")
        self._type_filter_combo.addItem("📄 Docs",    "docs")
        self._type_filter_combo.addItem("💻 Código",  "code")
        self._type_filter_combo.addItem("🗜 Archivos","archives")
        self._type_filter_combo.setFixedWidth(130)
        self._type_filter_combo.setToolTip("Filtrar por tipo de archivo")
        self._type_filter_combo.currentIndexChanged.connect(self._on_type_filter_changed)
        tb.addWidget(self._type_filter_combo)
        tb.addSeparator()

        # View mode buttons
        self._act_vd = _act(ico.view_details, "Vista detalles", "Ctrl+1")
        self._act_vi = _act(ico.view_icons,   "Vista iconos",   "Ctrl+2")
        self._act_vl = _act(ico.view_list,    "Vista lista",    "Ctrl+3")
        for a in (self._act_vd, self._act_vi, self._act_vl):
            a.setCheckable(True)
        self._act_vd.setChecked(True)
        self._act_vd.triggered.connect(lambda: self._set_view(VIEW_DETAILS))
        self._act_vi.triggered.connect(lambda: self._set_view(VIEW_ICONS))
        self._act_vl.triggered.connect(lambda: self._set_view(VIEW_LIST))
        tb.addSeparator()

        # Dual Panel Toggle
        self._act_dual = _act(ico.view_dual if hasattr(ico, "view_dual") else ico.view_list, 
                              "Vista panel dual  Ctrl+L", "Ctrl+L")
        self._act_dual.setCheckable(True)
        self._act_dual.setChecked(self._dual_mode)
        self._act_dual.triggered.connect(self._toggle_dual_mode)
        tb.addSeparator()

        # Terminal Toggle
        self._act_term = _act(ico.terminal_icon, "Terminal  Ctrl+`", "Ctrl+`" if sys.platform != "win32" else "Ctrl+Ñ")
        self._act_term.setCheckable(True)
        self._act_term.setChecked(self._terminal_visible)
        self._act_term.triggered.connect(self._toggle_terminal)
        tb.addSeparator()

        # Preview
        self._act_preview = _act(ico.preview_icon, "Vista previa  Ctrl+P", "Ctrl+P")
        self._act_preview.setCheckable(True)
        self._act_preview.setChecked(self._preview_visible)
        self._act_preview.triggered.connect(self._toggle_preview)
        tb.addSeparator()

        # New folder
        self._act_nf = _act(ico.folder_plus, "Nueva carpeta  Ctrl+Shift+N", "Ctrl+Shift+N")
        self._act_nf.triggered.connect(self._new_folder)
        self._act_bookmark = _act(ico.star_icon, "Añadir carpeta actual a marcadores", "Ctrl+D")
        self._act_bookmark.triggered.connect(self._bookmark_current_folder)
        tb.addSeparator()

        # Theme quick toggle
        self._act_theme_toggle = QAction(self)
        cur_theme = self._settings.get("theme", "dark_fluent")
        self._act_theme_toggle.setIcon(
            ico.theme_light() if cur_theme == "light_fluent" else ico.theme_dark()
        )
        self._act_theme_toggle.setToolTip("Cambiar tema claro/oscuro  Ctrl+Shift+T")
        self._act_theme_toggle.setShortcut("Ctrl+Shift+T")
        self._act_theme_toggle.triggered.connect(self._toggle_theme)
        tb.addAction(self._act_theme_toggle)
        tb.addSeparator()

        # Settings
        self._act_cfg = _act(ico.settings_icon, "Configuración")
        self._act_cfg.triggered.connect(self._open_settings)

        # Update buttons state
        self._update_nav_buttons()

    def _build_menu(self):
        mb = self.menuBar()

        # ── Archivo
        fm = mb.addMenu("Archivo")
        fm.addAction(QAction("Nueva ventana\tCtrl+N",  self, triggered=self._new_window))
        fm.addSeparator()
        fm.addAction(QAction("Nueva pestaña\tCtrl+T",  self, triggered=self._new_tab_from_current))
        fm.addAction(QAction("Cerrar pestaña\tCtrl+W", self, triggered=self._close_current_tab))
        fm.addSeparator()
        fm.addAction(QAction("Nueva carpeta\tCtrl+Shift+N", self, triggered=self._new_folder))
        fm.addSeparator()
        rc_menu = fm.addMenu("Carpetas recientes")
        rc_menu.aboutToShow.connect(lambda: self._populate_recent_menu(rc_menu))
        fm.addSeparator()
        fm.addAction(QAction("Salir\tAlt+F4", self, triggered=self.close))

        # ── Editar
        em = mb.addMenu("Editar")
        em.addAction(QAction("Copiar\tCtrl+C",  self,
            triggered=lambda: self._panel() and self._panel()._copy_selected(False)))
        em.addAction(QAction("Cortar\tCtrl+X",  self,
            triggered=lambda: self._panel() and self._panel()._copy_selected(True)))
        em.addAction(QAction("Pegar\tCtrl+V",   self, triggered=self._paste_current))
        em.addSeparator()
        em.addAction(QAction("Seleccionar todo\tCtrl+A", self,
            triggered=lambda: self._panel() and self._panel()._active_view().selectAll()))
        em.addSeparator()
        em.addAction(QAction("Renombrar\tF2",              self, triggered=self._rename_selected))
        em.addAction(QAction("Renombrar múltiples…\tCtrl+R", self, triggered=self._multi_rename_selected))
        em.addAction(QAction("Eliminar\tSupr",  self, triggered=self._delete_selected))
        em.addSeparator()
        em.addAction(QAction("Copiar ruta\tCtrl+Shift+C", self,
            triggered=self._copy_path))

        # ── Ver
        vm = mb.addMenu("Ver")
        vm.addAction(QAction("Vista detalles\tCtrl+1", self, triggered=lambda: self._set_view(VIEW_DETAILS)))
        vm.addAction(QAction("Vista iconos\tCtrl+2",   self, triggered=lambda: self._set_view(VIEW_ICONS)))
        vm.addAction(QAction("Vista lista\tCtrl+3",    self, triggered=lambda: self._set_view(VIEW_LIST)))
        vm.addSeparator()
        vm.addAction(QAction("Vista panel dual\tCtrl+L", self, triggered=self._toggle_dual_mode))
        vm.addAction(QAction("Terminal integrada\tCtrl+`", self, triggered=self._toggle_terminal))
        vm.addAction(QAction("Vista previa\tCtrl+P",     self, triggered=self._toggle_preview))
        vm.addAction(QAction("Barra lateral\tCtrl+B",    self, triggered=self._toggle_sidebar))
        vm.addSeparator()
        vm.addAction(QAction("Actualizar\tF5",           self, triggered=self._refresh))

        # ── Navegar
        nm = mb.addMenu("Navegar")
        nm.addAction(QAction("Atrás\tAlt+←",    self, triggered=self._go_back))
        nm.addAction(QAction("Adelante\tAlt+→",  self, triggered=self._go_forward))
        nm.addAction(QAction("Subir\tAlt+↑",     self, triggered=self._go_up))
        nm.addSeparator()
        for lbl, path in get_user_dirs().items():
            nm.addAction(QAction(lbl, self,
                triggered=lambda _, p=path: self._navigate_to(p)))
        nm.addSeparator()
        nm.addAction(QAction("Añadir carpeta actual a marcadores\tCtrl+D", self,
            triggered=self._bookmark_current_folder))

        # ── Herramientas
        tm = mb.addMenu("Herramientas")
        tm.addAction(QAction("Configuración",        self, triggered=self._open_settings))
        tm.addSeparator()
        tm.addAction(QAction("Limpiar historial reciente", self, triggered=self._clear_history))

        # ── Ayuda
        hm = mb.addMenu("Ayuda")
        hm.addAction(QAction("Atajos de teclado", self, triggered=self._show_shortcuts))
        hm.addAction(QAction("Acerca de",         self, triggered=self._show_about))

    def _build_statusbar(self):
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

        self._status_left  = QLabel("Listo")
        self._status_path  = QLabel("")
        self._status_disk  = QLabel("")
        self._status_theme = QLabel("")

        self._status_left.setMinimumWidth(200)
        self._status_path.setStyleSheet(
            "color: rgba(255,255,255,0.6); font-size: 11px; padding-right: 8px;"
        )
        self._status_disk.setStyleSheet(
            "color: rgba(255,255,255,0.45); font-size: 11px; padding-right: 12px;"
        )
        self._status_theme.setStyleSheet(
            "color: rgba(255,255,255,0.35); font-size: 11px; padding-right: 8px;"
        )

        # Make path clickable to copy
        self._status_path.setCursor(Qt.CursorShape.PointingHandCursor)
        self._status_path.setToolTip("Click para copiar ruta")
        self._status_path.mousePressEvent = lambda _: (
            QApplication.clipboard().setText(self._status_path.text()),
            self._on_status("Ruta copiada")
        )

        self._statusbar.addWidget(self._status_left, 1)
        self._statusbar.addPermanentWidget(self._status_path)
        self._statusbar.addPermanentWidget(self._status_disk)
        self._statusbar.addPermanentWidget(self._status_theme)

        theme_name = THEMES.get(self._settings.get("theme", "dark_fluent"), {}).get("name", "")
        self._status_theme.setText(theme_name)

        # Update disk info every 15s
        self._disk_timer = QTimer(self)
        self._disk_timer.timeout.connect(self._update_disk_info)
        self._disk_timer.start(15_000)

    # ── Tabs ──────────────────────────────────────────────

    def _add_tab(self, path: str = "", target_side=None) -> FilePanelTab:
        if not path:
            path = str(Path.home())
        
        # Determine target tab widget
        if target_side == "right":
            tabs = self._right_tabs
        elif isinstance(target_side, TabWidget):
            tabs = target_side
        else:
            tabs = self._active_tabs

        panel = FilePanelTab(path)
        panel.set_view_mode(self._settings.get("view_mode", VIEW_DETAILS))
        panel.set_show_hidden(self._settings.get("show_hidden", False))
        panel.set_icon_size(self._settings.get("icon_size", 96))
        panel.toggle_preview(self._preview_visible)
        panel.set_use_trash(self._settings.get("use_trash", True))
        panel.set_terminal_pref(self._settings.get("terminal", "auto"))
        panel.set_folders_first(self._settings.get("folders_first", True))
        panel.set_show_extensions(self._settings.get("show_extensions", True))
        panel.set_color_coding(self._settings.get("color_coding", False))
        panel.set_single_click(self._settings.get("single_click", False))
        panel.set_confirm_delete(self._settings.get("confirm_delete", True))
        panel.set_show_breadcrumb(self._settings.get("show_breadcrumb", True))
        panel.set_show_cmdbar(self._settings.get("show_cmdbar", True))
        panel.set_density(self._settings.get("density", "normal"))
        panel.set_date_format(self._settings.get("date_format", "absolute"))
        panel.set_size_unit(self._settings.get("size_unit", "auto"))
        panel.set_thumbnail_enabled(self._settings.get("show_thumbnails", True))
        panel.set_preview_position(self._settings.get("preview_position", "right"))
        panel.set_preview_syntax_hl(self._settings.get("preview_syntax_hl", True))
        panel.set_column_visibility(self._settings.get("column_visibility", [True, True, True, True]))
        panel.set_search_options(
            self._settings.get("search_case", False),
            self._settings.get("search_exclude", ".git,node_modules,__pycache__,.venv"),
        )
        panel.set_external_tools(self._settings.get("external_tools", []))
        panel.set_conflict_action(self._settings.get("conflict_action", "rename"))
        panel.set_monospace_font(self._settings.get("monospace_font", "Consolas"))
        panel.path_changed.connect(self._on_path_changed)
        panel.status_message.connect(self._on_status)
        panel.title_changed.connect(
            lambda title, p=panel, t=tabs: self._update_tab_title(t, p, title)
        )
        
        name = os.path.basename(path) or path
        idx  = tabs.addTab(panel, f"📁  {name}")
        tabs.setCurrentIndex(idx)
        panel.setFocus()
        self._update_tabbar_visibility()
        return panel

    def _new_tab_from_current(self, path: str = ""):
        if not path:
            p = self._panel()
            path = p.current_path() if p else str(Path.home())
        self._add_tab(path)

    def _close_current_tab(self):
        if self._active_tabs.count() > 1:
            self._active_tabs._close_tab(self._active_tabs.currentIndex())

    def _update_tab_title(self, tabs: TabWidget, panel: FilePanelTab, title: str):
        for i in range(tabs.count()):
            if tabs.widget(i) is panel:
                tabs.setTabText(i, f"📁  {title}")
                tabs.setTabToolTip(i, panel.current_path())
                break

    def _panel(self) -> Optional[FilePanelTab]:
        w = self._active_tabs.currentWidget()
        return w if isinstance(w, FilePanelTab) else None

    def _on_tab_changed(self, tabs: TabWidget):
        if tabs is not self._active_tabs:
            return
        p = self._panel()
        if p:
            self._address_bar.setText(p.current_path())
            self._status_path.setText(p.current_path())
            self._sidebar.set_active_path(p.current_path())
            self._update_nav_buttons()
            self._search_bar.clear()
            # Reset type filter combo to "All" to match the new panel's state
            self._type_filter_combo.blockSignals(True)
            self._type_filter_combo.setCurrentIndex(0)
            self._type_filter_combo.blockSignals(False)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.MouseButtonPress or event.type() == QEvent.Type.FocusIn:
            if obj is self._left_tabs.tabBar() or self._left_tabs.isAncestorOf(obj):
                self._set_active_panel(self._left_tabs)
            elif obj is self._right_tabs.tabBar() or self._right_tabs.isAncestorOf(obj):
                self._set_active_panel(self._right_tabs)
        return super().eventFilter(obj, event)

    def _set_active_panel(self, tabs: TabWidget):
        if self._active_tabs != tabs:
            # Clear style of previous active
            self._active_tabs.setStyleSheet("")
            self._active_tabs = tabs
            # Highlight new active with a subtle accent border
            self._active_tabs.setStyleSheet("QTabWidget { border: 1px solid #0078d4; border-radius: 4px; }")
            self._on_tab_changed(tabs)

    def _toggle_focus_panel(self):
        if not self._dual_mode:
            return
        target = self._right_tabs if self._active_tabs == self._left_tabs else self._left_tabs
        self._set_active_panel(target)
        p = self._panel()
        if p:
            p.setFocus()

    def _toggle_dual_mode(self):
        self._dual_mode = not self._dual_mode
        self._right_tabs.setVisible(self._dual_mode)
        self._act_dual.setChecked(self._dual_mode)
        
        if self._dual_mode and self._right_tabs.count() == 0:
            p = self._panel()
            path = p.current_path() if p else str(Path.home())
            self._add_tab(path, target_side="right")
        
        self._settings["dual_mode"] = self._dual_mode
        save_settings(self._settings)

    def _toggle_terminal(self):
        self._terminal_visible = not self._terminal_visible
        self._terminal.setVisible(self._terminal_visible)
        self._act_term.setChecked(self._terminal_visible)
        if self._terminal_visible:
            p = self._panel()
            if p:
                self._terminal.set_working_directory(p.current_path())
        self._settings["show_terminal"] = self._terminal_visible
        save_settings(self._settings)

    # ── Navigation ────────────────────────────────────────

    def _navigate_to(self, path: str):
        p = self._panel()
        if p:
            p.navigate_to(path)

    def _sidebar_navigate(self, path: str):
        p = self._panel()
        if p:
            p.navigate_to(path)
            self._sidebar.set_active_path(path)

    def _go_back(self):
        p = self._panel()
        if p:
            p.go_back()
            self._update_nav_buttons()

    def _go_forward(self):
        p = self._panel()
        if p:
            p.go_forward()
            self._update_nav_buttons()

    def _go_up(self):
        p = self._panel()
        if p:
            p.go_up()

    def _go_home(self):
        p = self._panel()
        if p:
            p.go_home()

    def _refresh(self):
        p = self._panel()
        if p:
            p.refresh()

    def _on_path_changed(self, path: str):
        self._address_bar.setText(path)
        self._status_path.setText(path)
        self._sidebar.set_active_path(path)
        self._update_nav_buttons()
        self._address_bar.update_recent(load_recent())
        self._update_disk_info()
        
        # Sync terminal
        if self._terminal_visible:
            self._terminal.set_working_directory(path)

    def _update_disk_info(self):
        p = self._panel()
        if not p:
            return
        path = p.current_path()
        try:
            import shutil
            drive = os.path.splitdrive(path)[0] or path[:1] + "/"
            usage = shutil.disk_usage(drive)
            free  = usage.free  / (1024 ** 3)
            total = usage.total / (1024 ** 3)
            self._status_disk.setText(f"💾  {free:.1f} GB libres de {total:.1f} GB")
        except Exception:
            self._status_disk.setText("")

    def _on_address_entered(self, path: str):
        if os.path.isdir(path):
            self._navigate_to(path)
            self._address_bar.setStyleSheet("")
        elif os.path.isfile(path):
            from src.utils import open_file
            open_file(path)
        else:
            self._address_bar.setStyleSheet(
                "QLineEdit { border-color: #e74c3c; }"
            )
            QTimer.singleShot(1400, lambda: self._address_bar.setStyleSheet(""))

    def _update_nav_buttons(self):
        p = self._panel()
        if p:
            self._act_back.setEnabled(p.can_go_back())
            self._act_forward.setEnabled(p.can_go_forward())

    # ── History menu ──────────────────────────────────────

    def _show_history_menu(self):
        recent = load_recent()
        if not recent:
            return
        menu = QMenu(self)
        for path in recent[:16]:
            name = os.path.basename(path) or path
            act  = QAction(f"📁  {name}", self)
            act.setToolTip(path)
            act.triggered.connect(lambda _, p=path: self._navigate_to(p))
            menu.addAction(act)
        menu.addSeparator()
        clear_act = QAction("Limpiar historial", self)
        clear_act.triggered.connect(self._clear_history)
        menu.addAction(clear_act)
        btn_pos = self._hist_btn.mapToGlobal(
            self._hist_btn.rect().bottomLeft()
        )
        menu.exec(btn_pos)

    def _populate_recent_menu(self, menu: QMenu):
        menu.clear()
        recent = load_recent()
        if not recent:
            no_act = QAction("(vacío)", self)
            no_act.setEnabled(False)
            menu.addAction(no_act)
            return
        for path in recent[:12]:
            name = os.path.basename(path) or path
            act  = QAction(f"📁  {name}", self)
            act.setToolTip(path)
            act.triggered.connect(lambda _, p=path: self._navigate_to(p))
            menu.addAction(act)

    def _clear_history(self):
        clear_recent()
        self._on_status("Historial limpiado")

    # ── Search ────────────────────────────────────────────

    def _on_search(self, text: str):
        p = self._panel()
        if p:
            if self._recursive_btn.isChecked():
                p.set_recursive_search_query(text)
            else:
                p.set_search_filter(text)

    def _toggle_recursive_search(self, enabled: bool):
        p = self._panel()
        if p:
            p.set_recursive_mode(enabled)
        if not enabled:
            self._on_search(self._search_bar.text())

    def _new_window(self):
        from src.main_window import MainWindow
        w = MainWindow()
        p = self._panel()
        if p:
            w._navigate_to(p.current_path())
        w.show()

    # ── View modes ────────────────────────────────────────

    def _set_view(self, mode: int):
        p = self._panel()
        if p:
            p.set_view_mode(mode)
        self._act_vd.setChecked(mode == VIEW_DETAILS)
        self._act_vi.setChecked(mode == VIEW_ICONS)
        self._act_vl.setChecked(mode == VIEW_LIST)
        self._settings["view_mode"] = mode
        save_settings(self._settings)

    def _toggle_preview(self):
        self._preview_visible = not self._preview_visible
        self._act_preview.setChecked(self._preview_visible)
        for tabs in (self._left_tabs, self._right_tabs):
            for i in range(tabs.count()):
                w = tabs.widget(i)
                if isinstance(w, FilePanelTab):
                    w.toggle_preview(self._preview_visible)
        self._settings["preview"] = self._preview_visible
        save_settings(self._settings)

    def _toggle_sidebar(self):
        self._sidebar_visible = not self._sidebar_visible
        self._sidebar.setVisible(self._sidebar_visible)
        self._sidebar_sep.setVisible(self._sidebar_visible)
        self._settings["show_sidebar"] = self._sidebar_visible
        save_settings(self._settings)

    # ── File ops ──────────────────────────────────────────

    def _new_folder(self):
        p = self._panel()
        if p:
            p._new_folder()

    def _bookmark_current_folder(self):
        p = self._panel()
        if not p:
            return
        path = p.current_path()
        if self._sidebar.add_bookmark(path):
            self._on_status(f"Marcador añadido: {path}")
        else:
            self._on_status("La carpeta ya está en marcadores")

    def _rename_selected(self):
        p = self._panel()
        if p:
            paths = p.selected_paths()
            if paths:
                p._rename(paths[0])

    def _multi_rename_selected(self):
        p = self._panel()
        if p:
            paths = p.selected_paths()
            if paths:
                p._multi_rename(paths)

    def _delete_selected(self):
        p = self._panel()
        if p:
            paths = p.selected_paths()
            if paths:
                p._delete(paths)

    def _paste_current(self):
        p = self._panel()
        if p:
            worker = p._paste_here()
            if worker:
                self._transfer_mgr.add_transfer(worker)

    def _copy_path(self):
        p = self._panel()
        if p:
            paths = p.selected_paths()
            text  = paths[0] if paths else p.current_path()
            QApplication.clipboard().setText(text)
            self._on_status(f"Ruta copiada: {text}")

    # ── Settings ─────────────────────────────────────────

    def _open_settings(self):
        dlg = SettingsDialog(self._settings, self)
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    def _apply_settings(self, s: dict):
        self._settings = s
        self._apply_theme(
            s.get("theme",         "dark_fluent"),
            s.get("accent_color",  ""),
            s.get("font_size",     13),
            s.get("density",       "normal"),
            s.get("font_family",   "Segoe UI"),
            s.get("border_radius", "normal"),
            s.get("font_weight",   "normal"),
            s.get("scrollbar_style", "thin"),
            s.get("toolbar_compact", False),
            s.get("row_height",    0),
        )

        # Window opacity
        self.setWindowOpacity(s.get("opacity", 100) / 100.0)

        for tabs in (self._left_tabs, self._right_tabs):
            for i in range(tabs.count()):
                w = tabs.widget(i)
                if isinstance(w, FilePanelTab):
                    w.set_show_hidden(s.get("show_hidden",     False))
                    w.set_view_mode(s.get("view_mode",         VIEW_DETAILS))
                    w.set_icon_size(s.get("icon_size",         96))
                    w.toggle_preview(s.get("preview",          True))
                    w.set_use_trash(s.get("use_trash",         True))
                    w.set_terminal_pref(s.get("terminal",      "auto"))
                    w.set_folders_first(s.get("folders_first", True))
                    w.set_show_extensions(s.get("show_extensions", True))
                    w.set_color_coding(s.get("color_coding",   False))
                    w.set_single_click(s.get("single_click",   False))
                    w.set_confirm_delete(s.get("confirm_delete", True))
                    w.set_show_breadcrumb(s.get("show_breadcrumb", True))
                    w.set_show_cmdbar(s.get("show_cmdbar",     True))
                    w.set_density(s.get("density",             "normal"))
                    w.set_date_format(s.get("date_format",     "absolute"))
                    w.set_size_unit(s.get("size_unit",         "auto"))
                    w.set_thumbnail_enabled(s.get("show_thumbnails", True))
                    w.set_preview_position(s.get("preview_position", "right"))
                    w.set_preview_syntax_hl(s.get("preview_syntax_hl", True))
                    w.set_column_visibility(s.get("column_visibility", [True, True, True, True]))
                    w.set_search_options(
                        s.get("search_case", False),
                        s.get("search_exclude", ".git,node_modules,__pycache__,.venv"),
                    )
                    w.set_external_tools(s.get("external_tools", []))
                    w.set_conflict_action(s.get("conflict_action", "rename"))
                    w.set_monospace_font(s.get("monospace_font", "Consolas"))

        self._preview_visible = s.get("preview", True)
        self._act_preview.setChecked(self._preview_visible)
        self._toolbar.setIconSize(QSize(18, 18) if s.get("toolbar_compact", False) else QSize(20, 20))

        vis = s.get("show_sidebar", True)
        self._sidebar_visible = vis
        self._sidebar.setVisible(vis)
        self._sidebar_sep.setVisible(vis)
        self._sidebar.set_show_recent_files(s.get("sidebar_recent_files", True))
        self._sidebar.refresh_recent_files()

        # Dual Mode
        new_dual = s.get("dual_mode", False)
        if new_dual != self._dual_mode:
            self._dual_mode = new_dual
            self._right_tabs.setVisible(new_dual)
            self._act_dual.setChecked(new_dual)
            if new_dual and self._right_tabs.count() == 0:
                p = self._panel()
                path = p.current_path() if p else str(Path.home())
                self._add_tab(path, target_side="right")

        # Terminal
        new_term = s.get("show_terminal", False)
        if new_term != self._terminal_visible:
            self._terminal_visible = new_term
            self._terminal.setVisible(new_term)
            self._act_term.setChecked(new_term)
            if new_term:
                p = self._panel()
                if p:
                    self._terminal.set_working_directory(p.current_path())

        # Sidebar width
        sw = s.get("sidebar_width", 200)
        self._sidebar.setFixedWidth(sw)

        # Animation speed for ToggleSwitches
        from src.toggle_switch import ToggleSwitch as _TS
        _TS.set_animation_speed(s.get("animation_speed", "normal"))

        mode = s.get("view_mode", VIEW_DETAILS)
        self._act_vd.setChecked(mode == VIEW_DETAILS)
        self._act_vi.setChecked(mode == VIEW_ICONS)
        self._act_vl.setChecked(mode == VIEW_LIST)

        theme_name = THEMES.get(s.get("theme", "dark_fluent"), {}).get("name", "")
        self._status_theme.setText(theme_name)
        self._act_theme_toggle.setIcon(
            ico.theme_light() if s.get("theme") == "light_fluent" else ico.theme_dark()
        )

        # Tab bar visibility
        self._update_tabbar_visibility()
        self._update_statusbar_items()

    def _get_startup_path(self) -> str:
        sf = self._settings.get("startup_folder", "home")
        if sf == "last":
            from src.recent_folders import load_recent
            recent = load_recent()
            if recent and os.path.isdir(recent[0]):
                return recent[0]
        elif sf == "custom":
            p = self._settings.get("startup_path", "")
            if p and os.path.isdir(p):
                return p
        return str(Path.home())

    def _on_type_filter_changed(self):
        category = self._type_filter_combo.currentData()
        p = self._panel()
        if p:
            p.set_type_filter(category)

    def _toggle_theme(self):
        dark = {"dark_fluent", "nord", "dracula", "catppuccin", "dark_purple"}
        cur  = self._settings.get("theme", "dark_fluent")
        new  = "light_fluent" if cur in dark else "dark_fluent"
        self._settings["theme"] = new
        save_settings(self._settings)
        self._apply_theme(
            new,
            self._settings.get("accent_color",  ""),
            self._settings.get("font_size",     13),
            self._settings.get("density",       "normal"),
            self._settings.get("font_family",   "Segoe UI"),
            self._settings.get("border_radius", "normal"),
            self._settings.get("font_weight",   "normal"),
            self._settings.get("scrollbar_style", "thin"),
            self._settings.get("toolbar_compact", False),
            self._settings.get("row_height",    0),
        )
        self._act_theme_toggle.setIcon(
            ico.theme_light() if new == "light_fluent" else ico.theme_dark()
        )
        theme_name = THEMES.get(new, {}).get("name", "")
        self._status_theme.setText(theme_name)

    def _update_statusbar_items(self):
        self._status_path.setVisible(self._settings.get("statusbar_path", True))
        self._status_disk.setVisible(self._settings.get("statusbar_disk", True))

    def _update_tabbar_visibility(self):
        hide_single = self._settings.get("hide_tabbar_single", False)
        for tabs in (self._left_tabs, self._right_tabs):
            show_bar = not (hide_single and tabs.count() <= 1)
            tabs.tabBar().setVisible(show_bar)

    def _apply_theme(self, key: str = "", accent: str = "",
                     font_size: int = 13, density: str = "normal",
                     font_family: str = "Segoe UI", border_radius: str = "normal",
                     font_weight: str = "normal", scrollbar_style: str = "thin",
                     toolbar_compact: bool = False, row_height: int = 0):
        k = key or self._settings.get("theme", "dark_fluent")
        from src.toggle_switch import ToggleSwitch
        ToggleSwitch.set_accent_color(get_accent_color(k, accent))
        stylesheet = get_stylesheet(
            k, accent, font_size, density, font_family, border_radius,
            font_weight, scrollbar_style, toolbar_compact, row_height,
        )
        custom = self._settings.get("custom_stylesheet", "")
        if custom:
            stylesheet = f"{stylesheet}\n\n/* Custom user stylesheet */\n{custom}"
        self.setStyleSheet(stylesheet)
        
        # Apply theme to terminal
        from src.themes import get_theme
        t = get_theme(k)
        if hasattr(self, "_terminal"):
            self._terminal.apply_theme(t["bg_primary"], t["text_primary"], t["accent"])

    # ── Status bar ────────────────────────────────────────

    def _on_status(self, msg: str):
        self._status_left.setText(msg)

    # ── Keyboard ──────────────────────────────────────────

    def keyPressEvent(self, event):
        key = event.key()
        mod = event.modifiers()
        Ctrl  = Qt.KeyboardModifier.ControlModifier
        Shift = Qt.KeyboardModifier.ShiftModifier

        if mod == Ctrl:
            if key == Qt.Key.Key_K:
                p = self._panel()
                path = p.current_path() if p else ""
                self._spotlight.show_spotlight(path)
                return
            elif key == Qt.Key.Key_I: self._toggle_focus_panel(); return
            elif key == Qt.Key.Key_T: self._new_tab_from_current(); return
            elif key == Qt.Key.Key_W: self._close_current_tab();    return
            elif key == Qt.Key.Key_Tab:
                idx = (self._active_tabs.currentIndex() + 1) % self._active_tabs.count()
                self._active_tabs.setCurrentIndex(idx); return
            elif key == Qt.Key.Key_L:
                self._toggle_dual_mode(); return
            elif key == Qt.Key.Key_F:
                self._search_bar.setFocus()
                self._search_bar.selectAll(); return
            elif key == Qt.Key.Key_B:  self._toggle_sidebar();  return
            elif key == Qt.Key.Key_P:  self._toggle_preview();  return
            elif key == Qt.Key.Key_N:  self._new_window();      return
            elif key == Qt.Key.Key_D:  self._bookmark_current_folder(); return
            elif key == Qt.Key.Key_1:  self._set_view(VIEW_DETAILS); return
            elif key == Qt.Key.Key_2:  self._set_view(VIEW_ICONS);   return
            elif key == Qt.Key.Key_3:  self._set_view(VIEW_LIST);    return
        elif mod == (Ctrl | Shift):
            if key == Qt.Key.Key_C:
                self._copy_path(); return
            elif key == Qt.Key.Key_N:
                self._new_folder(); return
            elif key == Qt.Key.Key_Tab:
                idx = (self._active_tabs.currentIndex() - 1) % self._active_tabs.count()
                self._active_tabs.setCurrentIndex(idx); return
            elif key == Qt.Key.Key_F:
                self._recursive_btn.setChecked(not self._recursive_btn.isChecked())
                self._search_bar.setFocus(); return

        if key == Qt.Key.Key_F5:
            self._refresh(); return
        if key == Qt.Key.Key_Escape:
            self._search_bar.clear()
            p = self._panel()
            if p:
                p.setFocus()
            return

        super().keyPressEvent(event)

    # ── Help ──────────────────────────────────────────────

    def _show_shortcuts(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Atajos de teclado")
        msg.setText("""
<table cellspacing='6' cellpadding='2'>
<tr><th align='left' style='color:#0078d4'>Navegación</th><th></th></tr>
<tr><td>Atrás / Adelante</td><td><b>Alt+← / Alt+→</b></td></tr>
<tr><td>Subir carpeta</td><td><b>Alt+↑ / Retroceso</b></td></tr>
<tr><td>Ir a dirección</td><td><b>Ctrl+L</b></td></tr>
<tr><td>Añadir marcador</td><td><b>Ctrl+D</b></td></tr>
<tr><td>Buscar</td><td><b>Ctrl+F</b></td></tr>
<tr><td>Actualizar</td><td><b>F5</b></td></tr>
<tr><td colspan='2'>&nbsp;</td></tr>
<tr><th align='left' style='color:#0078d4'>Pestañas</th><th></th></tr>
<tr><td>Nueva pestaña</td><td><b>Ctrl+T</b></td></tr>
<tr><td>Cerrar pestaña</td><td><b>Ctrl+W</b></td></tr>
<tr><td>Cambiar pestaña</td><td><b>Ctrl+Tab / Ctrl+Shift+Tab</b></td></tr>
<tr><td>Nueva ventana</td><td><b>Ctrl+N</b></td></tr>
<tr><td colspan='2'>&nbsp;</td></tr>
<tr><th align='left' style='color:#0078d4'>Archivos</th><th></th></tr>
<tr><td>Copiar / Cortar / Pegar</td><td><b>Ctrl+C / X / V</b></td></tr>
<tr><td>Copiar ruta</td><td><b>Ctrl+Shift+C</b></td></tr>
<tr><td>Renombrar</td><td><b>F2</b></td></tr>
<tr><td>Eliminar</td><td><b>Supr</b></td></tr>
<tr><td>Propiedades</td><td><b>Alt+Enter</b></td></tr>
<tr><td>Seleccionar todo</td><td><b>Ctrl+A</b></td></tr>
<tr><td>Nueva carpeta</td><td><b>Ctrl+Shift+N</b></td></tr>
<tr><td colspan='2'>&nbsp;</td></tr>
<tr><th align='left' style='color:#0078d4'>Vista</th><th></th></tr>
<tr><td>Detalles / Iconos / Lista</td><td><b>Ctrl+1 / 2 / 3</b></td></tr>
<tr><td>Vista previa</td><td><b>Ctrl+P</b></td></tr>
<tr><td>Barra lateral</td><td><b>Ctrl+B</b></td></tr>
<tr><td>Type-ahead (saltar a archivo)</td><td><b>Escribe la primera letra</b></td></tr>
<tr><td>Quicklook (vista previa)</td><td><b>Espacio</b></td></tr>
<tr><td colspan='2'>&nbsp;</td></tr>
<tr><th align='left' style='color:#0078d4'>Búsqueda</th><th></th></tr>
<tr><td>Buscar en carpeta</td><td><b>Ctrl+F</b></td></tr>
<tr><td>Búsqueda recursiva</td><td><b>Ctrl+Shift+F</b></td></tr>
<tr><td colspan='2'>&nbsp;</td></tr>
<tr><th align='left' style='color:#0078d4'>Archivo</th><th></th></tr>
<tr><td>Comprimir ZIP</td><td><b>Clic derecho → Comprimir en ZIP</b></td></tr>
<tr><td>Extraer archivo</td><td><b>Clic derecho → Extraer aquí</b></td></tr>
</table>
""")
        msg.exec()

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Acerca de")
        msg.setText(
            "<b style='font-size:16px'>Explorador de Archivos</b><br><br>"
            "Versión 3.0<br>"
            "Python + PyQt6 · Fluent Design<br><br>"
            "<span style='color:#666;font-size:11px'>"
            "Thumbnails · Pestañas · Vista previa · Búsqueda recursiva<br>"
            "Marcadores · Historial · ZIP · Papelera · 6 temas</span>"
        )
        msg.exec()

    # ── Persist window state ──────────────────────────────

    def _restore_geometry(self):
        qs = QSettings("FileExplorer", "MainWindow")
        geo = qs.value("geometry")
        if geo:
            self.restoreGeometry(geo)

    def closeEvent(self, event):
        qs = QSettings("FileExplorer", "MainWindow")
        qs.setValue("geometry", self.saveGeometry())
        # Save tab sessions
        if self._settings.get("restore_tabs"):
            paths = []
            for tabs in (self._left_tabs, self._right_tabs):
                for i in range(tabs.count()):
                    w = tabs.widget(i)
                    if isinstance(w, FilePanelTab):
                        paths.append(w.current_path())
            self._settings["_tab_sessions"] = paths
            save_settings(self._settings)
        super().closeEvent(event)
