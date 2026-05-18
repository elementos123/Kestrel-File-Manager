import os
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QAbstractItemView,
    QTreeView, QListView, QSplitter, QListWidget, QListWidgetItem,
    QMenu, QInputDialog, QMessageBox, QApplication, QFrame, QLabel,
    QSizePolicy, QStackedWidget, QStyledItemDelegate, QStyle,
    QStyleOptionViewItem,
)
from PyQt6.QtCore import (
    Qt, QDir, QSortFilterProxyModel, QModelIndex,
    pyqtSignal, QMimeData, QUrl, QTimer, QSize, QRect, QThread,
)
from PyQt6.QtGui import (
    QFileSystemModel, QAction, QKeySequence,
    QDrag, QIcon, QPainter, QColor, QFont, QPen,
)

_FILE_TYPE_COLORS: dict[str, str] = {
    # Images
    ".jpg": "#d4a843", ".jpeg": "#d4a843", ".png": "#d4a843",
    ".gif": "#d4a843", ".bmp": "#d4a843", ".webp": "#d4a843",
    ".svg": "#d4a843", ".ico": "#d4a843", ".heic": "#d4a843",
    # Video
    ".mp4": "#e06c75", ".mkv": "#e06c75", ".avi": "#e06c75",
    ".mov": "#e06c75", ".wmv": "#e06c75", ".webm": "#e06c75",
    # Audio
    ".mp3": "#c678dd", ".wav": "#c678dd", ".flac": "#c678dd",
    ".ogg": "#c678dd", ".aac": "#c678dd", ".m4a": "#c678dd",
    # Code
    ".py": "#98c379", ".js": "#98c379", ".ts": "#98c379",
    ".jsx": "#98c379", ".tsx": "#98c379", ".go": "#98c379",
    ".rs": "#98c379", ".cpp": "#98c379", ".c": "#98c379",
    ".java": "#98c379", ".cs": "#98c379", ".rb": "#98c379",
    # Documents
    ".pdf": "#e5c07b", ".doc": "#e5c07b", ".docx": "#e5c07b",
    ".xls": "#e5c07b", ".xlsx": "#e5c07b", ".ppt": "#e5c07b",
    # Archives
    ".zip": "#56b6c2", ".rar": "#56b6c2", ".7z": "#56b6c2",
    ".tar": "#56b6c2", ".gz": "#56b6c2",
    # Web
    ".html": "#e06c75", ".htm": "#e06c75",
    ".css": "#61afef", ".scss": "#61afef",
    ".json": "#e5c07b", ".yaml": "#e5c07b", ".yml": "#e5c07b",
}

from src.breadcrumb import BreadcrumbWidget
from src.preview import PreviewPanel
from src.thumbnail_cache import ThumbnailCache
from src.utils import (
    get_file_icon, format_size, format_date, format_date_relative,
    format_size_in_unit, open_file, open_in_terminal, is_image,
)
from src.file_operations import (
    delete_files, rename_item, create_folder, paste_files,
    get_clipboard,
)
from src.utils import compress_to_zip, extract_archive, is_archive
from src import icon_provider as ico
from src.command_bar import CommandBar
from src.models.file_proxy_model import FileProxyModel
from src.delegates.icon_delegate import IconDelegate
from src.workers.search_worker import RecursiveSearchWorker

VIEW_DETAILS = 0
VIEW_ICONS   = 1
VIEW_LIST    = 2


# ── Per-tab panel widget ───────────────────────────────────

class FilePanelTab(QWidget):
    path_changed   = pyqtSignal(str)
    status_message = pyqtSignal(str)
    title_changed  = pyqtSignal(str)

    def __init__(self, start_path: str = "", parent=None):
        super().__init__(parent)

        self._history:  list[str] = []
        self._hist_pos: int       = -1
        self._view_mode: int      = VIEW_DETAILS
        self._icon_size: int      = 96
        self._typeahead_buffer    = ""
        self._typeahead_timer     = QTimer()
        self._typeahead_timer.setSingleShot(True)
        self._typeahead_timer.setInterval(800)
        self._typeahead_timer.timeout.connect(self._clear_typeahead)
        self._recursive_mode     = False
        self._search_worker: Optional[RecursiveSearchWorker] = None
        self._search_debounce    = QTimer()
        self._search_debounce.setSingleShot(True)
        self._search_debounce.setInterval(350)
        self._search_debounce.timeout.connect(self._run_recursive_search)

        if not start_path or not os.path.isdir(start_path):
            start_path = str(Path.home())

        # Thumbnail cache shared across views
        self._thumb_cache = ThumbnailCache(QSize(self._icon_size, self._icon_size))

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Breadcrumb
        self._breadcrumb = BreadcrumbWidget()
        self._breadcrumb.navigate.connect(self.navigate_to)
        root_layout.addWidget(self._breadcrumb)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("border: none; background: #2a2a2a;")
        root_layout.addWidget(sep)

        # Main splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        root_layout.addWidget(self._splitter)

        # File system model
        self._fs_model = QFileSystemModel()
        self._fs_model.setRootPath("")
        self._fs_model.setFilter(
            QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Hidden
        )

        self._proxy = FileProxyModel(self._thumb_cache)
        self._proxy.setSourceModel(self._fs_model)

        # Views container
        view_container = QWidget()
        vl = QVBoxLayout(view_container)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        self._view_stack = QStackedWidget()
        vl.addWidget(self._view_stack)

        # Recursive search results panel (hidden by default)
        self._results_panel = QWidget()
        self._results_panel.setVisible(False)
        rp_vl = QVBoxLayout(self._results_panel)
        rp_vl.setContentsMargins(0, 0, 0, 0)
        rp_vl.setSpacing(0)
        self._results_header = QLabel("  0 resultados")
        self._results_header.setStyleSheet(
            "background: #1e2030; color: #888; font-size: 11px;"
            "padding: 4px 10px; border-top: 1px solid #333;"
        )
        self._results_header.setFixedHeight(22)
        rp_vl.addWidget(self._results_header)
        self._results_list = QListWidget()
        self._results_list.setStyleSheet(
            "QListWidget { background: #181825; color: #cdd6f4; border: none; font-size: 12px; }"
            "QListWidget::item { padding: 4px 10px; }"
            "QListWidget::item:hover { background: #313244; }"
            "QListWidget::item:selected { background: #45475a; }"
        )
        self._results_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._results_list.itemDoubleClicked.connect(self._on_result_double_click)
        rp_vl.addWidget(self._results_list, 1)
        vl.addWidget(self._results_panel)

        # Command bar (appears at bottom)
        self._cmd_bar = CommandBar()
        self._cmd_bar.set_theme("#1a1a1a", "#2d2d2d")
        self._cmd_bar.action_open.connect(
            lambda: [self.navigate_to(p) if os.path.isdir(p) else open_file(p)
                     for p in self.selected_paths()]
        )
        self._cmd_bar.action_copy.connect(lambda: self._copy_selected(False))
        self._cmd_bar.action_cut.connect(lambda: self._copy_selected(True))
        self._cmd_bar.action_paste.connect(self._paste_here)
        self._cmd_bar.action_rename.connect(
            lambda: self._rename(self.selected_paths()[0])
            if self.selected_paths() else None
        )
        self._cmd_bar.action_delete.connect(
            lambda: self._delete(self.selected_paths())
            if self.selected_paths() else None
        )
        self._cmd_bar.action_copy_path.connect(
            lambda: QApplication.clipboard().setText(
                self.selected_paths()[0] if self.selected_paths()
                else self.current_path()
            )
        )
        self._cmd_bar.action_properties.connect(
            lambda: self._show_properties(self.selected_paths()[0])
            if self.selected_paths() else None
        )
        self._cmd_bar.action_new_folder.connect(self._new_folder)
        vl.addWidget(self._cmd_bar)

        self._splitter.addWidget(view_container)

        # ── Details view ──────────────────────────────────
        self._details_view = QTreeView()
        self._setup_view(self._details_view)
        self._details_view.setSortingEnabled(True)
        self._details_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self._details_view.setAlternatingRowColors(True)
        self._details_view.setUniformRowHeights(True)
        self._details_view.setIndentation(0)
        self._details_view.setIconSize(QSize(20, 20))
        hdr = self._details_view.header()
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(0, hdr.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, hdr.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, hdr.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, hdr.ResizeMode.ResizeToContents)
        hdr.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        hdr.customContextMenuRequested.connect(self._show_column_menu)
        self._view_stack.addWidget(self._details_view)    # index 0

        # ── Icons view ────────────────────────────────────
        self._icons_view = QListView()
        self._setup_view(self._icons_view)
        self._icons_view.setViewMode(QListView.ViewMode.IconMode)
        self._icons_view.setIconSize(QSize(self._icon_size, self._icon_size))
        self._icons_view.setGridSize(QSize(self._icon_size + 32, self._icon_size + 40))
        self._icons_view.setResizeMode(QListView.ResizeMode.Adjust)
        self._icons_view.setSpacing(4)
        self._icons_view.setUniformItemSizes(True)
        self._icons_view.setWordWrap(True)
        self._icons_view.setItemDelegate(IconDelegate(self._icons_view))
        self._view_stack.addWidget(self._icons_view)      # index 1

        # ── List view ─────────────────────────────────────
        self._list_view = QListView()
        self._setup_view(self._list_view)
        self._list_view.setViewMode(QListView.ViewMode.ListMode)
        self._list_view.setIconSize(QSize(20, 20))
        self._list_view.setSpacing(1)
        self._view_stack.addWidget(self._list_view)       # index 2

        # Preview panel
        self._preview = PreviewPanel()
        self._splitter.addWidget(self._preview)
        self._preview.setVisible(False)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([700, 280])

        self.navigate_to(start_path)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Install Ctrl+scroll zoom for icon view
        self._icons_view.viewport().installEventFilter(self)

    # ── View setup helper ─────────────────────────────────

    def _setup_view(self, view: QAbstractItemView):
        view.setModel(self._proxy)
        view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        view.setDragEnabled(True)
        view.setAcceptDrops(True)
        view.setDropIndicatorShown(True)
        view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        view.customContextMenuRequested.connect(self._show_context_menu)
        view.doubleClicked.connect(self._on_double_click)  # default; toggled by set_single_click
        view.selectionModel().selectionChanged.connect(self._on_selection_changed)

    # ── Navigation ────────────────────────────────────────

    def navigate_to(self, path: str):
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            return
        self._stop_recursive_search()
        self._results_panel.setVisible(False)
        self._view_stack.setVisible(True)
        if self._hist_pos < len(self._history) - 1:
            self._history = self._history[:self._hist_pos + 1]
        if not self._history or self._history[-1] != path:
            self._history.append(path)
            self._hist_pos = len(self._history) - 1
        self._set_root(path)
        # Record in global recents
        try:
            from src.recent_folders import push_recent
            push_recent(path)
        except Exception:
            pass

    def _set_root(self, path: str):
        self._fs_model.setRootPath(path)
        src_idx   = self._fs_model.index(path)
        proxy_idx = self._proxy.mapFromSource(src_idx)
        for view in (self._details_view, self._icons_view, self._list_view):
            view.setRootIndex(proxy_idx)
        self._breadcrumb.set_path(path)
        name = os.path.basename(path) or path
        self.title_changed.emit(name)
        self.path_changed.emit(path)
        self._preview.clear()
        self._update_status()

    def current_path(self) -> str:
        return self._fs_model.rootPath()

    def go_back(self):
        if self._hist_pos > 0:
            self._hist_pos -= 1
            self._set_root(self._history[self._hist_pos])

    def go_forward(self):
        if self._hist_pos < len(self._history) - 1:
            self._hist_pos += 1
            self._set_root(self._history[self._hist_pos])

    def go_up(self):
        c = self.current_path()
        p = os.path.dirname(c)
        if p != c:
            self.navigate_to(p)

    def go_home(self):
        self.navigate_to(str(Path.home()))

    def can_go_back(self)    -> bool: return self._hist_pos > 0
    def can_go_forward(self) -> bool: return self._hist_pos < len(self._history) - 1

    def refresh(self):
        self._thumb_cache.clear()
        self._fs_model.setRootPath("")
        self._set_root(self.current_path())

    # ── View modes ────────────────────────────────────────

    def set_view_mode(self, mode: int):
        self._view_mode = mode
        self._view_stack.setCurrentIndex(mode)
        if mode == VIEW_ICONS:
            self._icons_view.setFocus()
        elif mode == VIEW_LIST:
            self._list_view.setFocus()
        else:
            self._details_view.setFocus()

    def view_mode(self) -> int:
        return self._view_mode

    def set_icon_size(self, size: int):
        self._icon_size = size
        self._thumb_cache.resize(QSize(size, size))
        self._icons_view.setIconSize(QSize(size, size))
        self._icons_view.setGridSize(QSize(size + 32, size + 40))

    # ── Search ────────────────────────────────────────────

    def set_search_filter(self, text: str):
        self._proxy.set_filter(text)

    def set_recursive_mode(self, enabled: bool):
        self._recursive_mode = enabled
        if not enabled:
            self._stop_recursive_search()
            self._results_panel.setVisible(False)
            self._view_stack.setVisible(True)

    def set_recursive_search_query(self, text: str):
        self._stop_recursive_search()
        if len(text.strip()) < 2:
            self._results_panel.setVisible(False)
            self._view_stack.setVisible(True)
            return
        self._current_query = text
        self._search_debounce.start()

    def _run_recursive_search(self):
        query = getattr(self, "_current_query", "")
        if not query:
            return
        self._results_list.clear()
        self._results_header.setText("  Buscando…")
        self._results_panel.setVisible(True)
        self._view_stack.setVisible(False)
        self._search_worker = RecursiveSearchWorker(
            self.current_path(), query,
            case_sensitive=getattr(self, "_search_case_flag", False),
            exclude=getattr(self, "_search_exclude_set", set()),
        )
        self._search_worker.found.connect(self._on_result_found)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_worker.start()

    def _on_result_found(self, path: str, name: str):
        from PyQt6.QtWidgets import QListWidgetItem
        icon = get_file_icon(path, os.path.isdir(path))
        item = QListWidgetItem(f"{icon}  {name}  —  {os.path.dirname(path)}")
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setToolTip(path)
        self._results_list.addItem(item)
        count = self._results_list.count()
        self._results_header.setText(f"  {count} resultado(s)")

    def _on_search_finished(self, count: int):
        suffix = f"  (límite {RecursiveSearchWorker.MAX_RESULTS})" if count >= RecursiveSearchWorker.MAX_RESULTS else ""
        self._results_header.setText(f"  {count} resultado(s){suffix}")

    def _stop_recursive_search(self):
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.stop()
            self._search_worker.wait(500)
        self._search_worker = None
        self._search_debounce.stop()

    def _on_result_double_click(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
        if os.path.isdir(path):
            self.navigate_to(path)
        else:
            parent_dir = os.path.dirname(path)
            self.navigate_to(parent_dir)
            open_file(path)

    # ── Preview ───────────────────────────────────────────

    def toggle_preview(self, visible: bool):
        self._preview.setVisible(visible)

    def preview_visible(self) -> bool:
        return self._preview.isVisible()

    # ── Hidden files ──────────────────────────────────────

    def set_show_hidden(self, show: bool):
        flags = QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot
        if show:
            flags |= QDir.Filter.Hidden
        self._fs_model.setFilter(flags)

    # ── Active view + selection ───────────────────────────

    def _active_view(self) -> QAbstractItemView:
        return [self._details_view, self._icons_view, self._list_view][self._view_mode]

    def selected_paths(self) -> list[str]:
        seen  = set()
        paths = []
        for proxy_idx in self._active_view().selectionModel().selectedIndexes():
            if proxy_idx.column() != 0:
                continue
            src_idx = self._proxy.mapToSource(proxy_idx)
            path    = self._fs_model.filePath(src_idx)
            if path not in seen:
                seen.add(path)
                paths.append(path)
        return paths

    # ── Slots ─────────────────────────────────────────────

    def _on_double_click(self, proxy_idx: QModelIndex):
        src_idx = self._proxy.mapToSource(proxy_idx)
        path    = self._fs_model.filePath(src_idx)
        if os.path.isdir(path):
            self.navigate_to(path)
        else:
            open_file(path)
            try:
                from src.recent_files import push_recent_file
                push_recent_file(path)
            except Exception:
                pass

    def _on_selection_changed(self, *_):
        paths = self.selected_paths()
        if len(paths) == 1:
            self._preview.show_file(paths[0])
        else:
            self._preview.clear()
        self._cmd_bar.update_state(paths, has_clipboard=get_clipboard().has_items())
        self._update_status()

    def _update_status(self):
        paths   = self.selected_paths()
        current = self.current_path()
        try:
            total = len(list(os.scandir(current)))
        except Exception:
            total = 0

        if paths:
            total_size = 0
            for p in paths:
                try:
                    if os.path.isfile(p):
                        total_size += os.path.getsize(p)
                except Exception:
                    pass
            unit = getattr(self, "_size_unit", "auto")
            size_str = f"  ·  {format_size_in_unit(total_size, unit)}" if total_size else ""
            self.status_message.emit(
                f"{len(paths)} seleccionado(s){size_str}  ·  {total} elementos"
            )
        else:
            self.status_message.emit(f"{total} elementos")

    # ── Context menu ──────────────────────────────────────

    def _show_context_menu(self, pos):
        view    = self._active_view()
        paths   = self.selected_paths()
        current = self.current_path()
        cb      = get_clipboard()

        menu = QMenu(self)

        def _a(label: str, icon_fn=None, shortcut: str = "") -> QAction:
            a = QAction(label, self)
            if icon_fn:
                a.setIcon(icon_fn())
            if shortcut:
                a.setShortcut(shortcut)
            return a

        if paths:
            is_single_dir = len(paths) == 1 and os.path.isdir(paths[0])
            open_act = _a("Abrir", ico.folder_open if is_single_dir else ico.open_icon)
            open_act.triggered.connect(
                lambda: [self.navigate_to(p) if os.path.isdir(p) else open_file(p)
                         for p in paths]
            )
            menu.addAction(open_act)

            if len(paths) == 1 and not os.path.isdir(paths[0]):
                ow_act = _a("Abrir con…", ico.open_with_icon)
                ow_act.triggered.connect(lambda: self._open_with(paths[0]))
                menu.addAction(ow_act)

            menu.addSeparator()

            copy_act = _a("Copiar\tCtrl+C", ico.copy_icon)
            copy_act.triggered.connect(lambda: self._copy_selected(False, paths))
            menu.addAction(copy_act)

            cut_act = _a("Cortar\tCtrl+X", ico.cut_icon)
            cut_act.triggered.connect(lambda: self._copy_selected(True, paths))
            menu.addAction(cut_act)

        paste_act = _a("Pegar\tCtrl+V", ico.paste_icon)
        paste_act.setEnabled(cb.has_items())
        paste_act.triggered.connect(self._paste_here)
        menu.addAction(paste_act)
        menu.addSeparator()

        if paths:
            if len(paths) == 1:
                rename_act = _a("Renombrar\tF2", ico.rename_icon)
                rename_act.triggered.connect(lambda: self._rename(paths[0]))
                menu.addAction(rename_act)
            else:
                mrename_act = _a(f"Renombrar {len(paths)} elementos…", ico.rename_multi)
                mrename_act.triggered.connect(lambda: self._multi_rename(paths))
                menu.addAction(mrename_act)

            del_act = _a("Eliminar\tSupr", ico.delete_icon)
            del_act.triggered.connect(lambda: self._delete(paths))
            menu.addAction(del_act)
            menu.addSeparator()

        cp_act = _a("Copiar ruta\tCtrl+Shift+C", ico.copy_path_icon)
        cp_act.triggered.connect(
            lambda: QApplication.clipboard().setText(paths[0] if paths else current)
        )
        menu.addAction(cp_act)
        menu.addSeparator()

        new_menu = menu.addMenu("Nuevo")
        new_menu.setIcon(ico.file_plus())
        nf_act = _a("Carpeta", ico.folder_plus)
        nf_act.triggered.connect(self._new_folder)
        new_menu.addAction(nf_act)
        ntf_act = _a("Archivo de texto", ico.file_plus)
        ntf_act.triggered.connect(self._new_text_file)
        new_menu.addAction(ntf_act)
        menu.addSeparator()

        # Compress / extract
        if paths:
            zip_act = _a("Comprimir en ZIP…", ico.compress_icon)
            zip_act.triggered.connect(lambda: self._compress_selected(paths))
            menu.addAction(zip_act)
        if len(paths) == 1 and is_archive(paths[0]):
            ext_act = _a("Extraer aquí", ico.extract_icon)
            ext_act.triggered.connect(lambda: self._extract_selected(paths[0]))
            menu.addAction(ext_act)
        menu.addSeparator()

        bookmark_selected = len(paths) == 1 and os.path.isdir(paths[0])
        bookmark_path = paths[0] if bookmark_selected else current
        bm_label = "Agregar carpeta a marcadores" if bookmark_selected else "Agregar carpeta actual a marcadores"
        bm_act = _a(bm_label, ico.bookmark_icon)

        def _add_bookmark():
            sidebar = getattr(self.window(), "_sidebar", None)
            if sidebar and sidebar.add_bookmark(bookmark_path):
                self.status_message.emit(f"Marcador añadido: {bookmark_path}")
            else:
                self.status_message.emit("La carpeta ya está en marcadores")

        bm_act.triggered.connect(_add_bookmark)
        menu.addAction(bm_act)
        if paths:
            menu.addSeparator()

        # External tools submenu
        ext_tools = getattr(self, "_external_tools", [])
        if ext_tools and paths:
            import subprocess as _sp
            tools_menu = menu.addMenu("Abrir con herramienta")
            tools_menu.setIcon(ico.ext_tool_icon())
            for tool in ext_tools:
                tool_name = tool.get("name", "Tool")
                tool_cmd  = tool.get("command", "")
                if not tool_cmd:
                    continue
                t_act = QAction(tool_name, self)
                _c = tool_cmd.replace("%s", paths[0])
                t_act.triggered.connect(lambda _, cmd=_c: _sp.Popen(cmd, shell=True))
                tools_menu.addAction(t_act)
            menu.addSeparator()

        term_act = _a("Abrir terminal aquí", ico.terminal_icon)
        _term_path = paths[0] if paths and os.path.isdir(paths[0]) else current
        _terminal_pref = getattr(self, "_terminal_pref", "auto")
        term_act.triggered.connect(lambda: open_in_terminal(_term_path, _terminal_pref))
        menu.addAction(term_act)

        if paths and len(paths) == 1:
            menu.addSeparator()
            prop_act = _a("Propiedades\tAlt+Enter", ico.properties_icon)
            prop_act.triggered.connect(lambda: self._show_properties(paths[0]))
            menu.addAction(prop_act)

        menu.exec(view.viewport().mapToGlobal(pos))

    # ── File operations ───────────────────────────────────

    def _rename(self, path: str):
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(
            self, "Renombrar", "Nuevo nombre:", text=old_name
        )
        if ok and new_name and new_name != old_name:
            success, result = rename_item(path, new_name)
            if not success:
                QMessageBox.warning(self, "Error al renombrar", result)

    def _delete(self, paths: list[str]):
        use_trash      = getattr(self, "_use_trash", True)
        confirm_delete = getattr(self, "_confirm_delete", True)
        if delete_files(paths, self, use_trash=use_trash, confirm=confirm_delete):
            self._preview.clear()
            QTimer.singleShot(150, self.refresh)

    def _copy_selected(self, cut: bool = False, paths: list[str] | None = None):
        paths = paths if paths is not None else self.selected_paths()
        cb = get_clipboard()
        if cut:
            cb.cut(paths)
            action = "cortado(s)"
        else:
            cb.copy(paths)
            action = "copiado(s)"
        if cb.has_items():
            self.status_message.emit(f"{len(cb.paths)} elemento(s) {action} al portapapeles")
        else:
            self.status_message.emit("No hay elementos válidos para copiar")
        self._cmd_bar.update_state(self.selected_paths(), has_clipboard=cb.has_items())

    def _paste_here(self):
        worker = paste_files(self.current_path(), self)
        if worker:
            def _after_paste(ok: bool, msg: str):
                QTimer.singleShot(250, self.refresh)
                self.status_message.emit("Pegado completado" if ok else (msg or "Pegado cancelado"))

            worker.finished.connect(_after_paste)

    def set_use_trash(self, enabled: bool):
        self._use_trash = enabled

    def set_terminal_pref(self, pref: str):
        self._terminal_pref = pref

    def set_folders_first(self, enabled: bool):
        self._proxy.set_folders_first(enabled)

    def set_show_extensions(self, enabled: bool):
        self._proxy.set_show_extensions(enabled)

    def set_color_coding(self, enabled: bool):
        self._proxy.set_color_coding(enabled)

    def set_single_click(self, enabled: bool):
        for view in (self._details_view, self._icons_view, self._list_view):
            try:
                view.doubleClicked.disconnect(self._on_double_click)
            except Exception:
                pass
            try:
                view.clicked.disconnect(self._on_double_click)
            except Exception:
                pass
            if enabled:
                view.clicked.connect(self._on_double_click)
            else:
                view.doubleClicked.connect(self._on_double_click)

    def set_confirm_delete(self, enabled: bool):
        self._confirm_delete = enabled

    def set_show_breadcrumb(self, visible: bool):
        self._breadcrumb.setVisible(visible)

    def set_show_cmdbar(self, visible: bool):
        self._cmd_bar.setVisible(visible)

    def set_density(self, density: str):
        sizes = {"compact": 16, "normal": 20, "comfortable": 24}
        icon_px = sizes.get(density, 20)
        self._details_view.setIconSize(QSize(icon_px, icon_px))
        self._list_view.setIconSize(QSize(icon_px, icon_px))

    def set_date_format(self, fmt: str):
        self._size_unit = getattr(self, "_size_unit", "auto")
        self._proxy.set_date_relative(fmt == "relative")

    def set_size_unit(self, unit: str):
        self._size_unit = unit

    def set_thumbnail_enabled(self, enabled: bool):
        self._proxy.set_thumbnail_enabled(enabled)

    def set_preview_position(self, position: str):
        if position == "bottom":
            self._splitter.setOrientation(Qt.Orientation.Vertical)
            self._splitter.setSizes([400, 200])
        else:
            self._splitter.setOrientation(Qt.Orientation.Horizontal)
            self._splitter.setSizes([700, 280])

    def set_preview_syntax_hl(self, enabled: bool):
        self._preview.set_syntax_enabled(enabled)

    def set_monospace_font(self, family: str):
        self._preview.set_monospace_font(family)

    def set_column_visibility(self, visibility: list):
        hdr = self._details_view.header()
        for i, visible in enumerate(visibility):
            if i == 0:
                continue  # never hide Name
            if i < 4:
                hdr.setSectionHidden(i, not visible)

    def set_search_options(self, case_sensitive: bool, exclude: str):
        self._search_case_flag = case_sensitive
        self._proxy.set_search_case(case_sensitive)
        self._search_exclude_set = set(
            p.strip() for p in exclude.split(",") if p.strip()
        )

    def set_external_tools(self, tools: list):
        self._external_tools = tools

    def set_conflict_action(self, action: str):
        self._conflict_action = action

    def set_type_filter(self, category: str):
        self._proxy.set_type_filter(category)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if (obj is self._icons_view.viewport() and
                event.type() == QEvent.Type.Wheel):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                delta = event.angleDelta().y()
                step  = 16 if delta > 0 else -16
                new_sz = max(32, min(256, self._icon_size + step))
                self.set_icon_size(new_sz)
                return True
        return super().eventFilter(obj, event)

    # ── Column header menu ────────────────────────────────

    def _show_column_menu(self, pos):
        hdr   = self._details_view.header()
        menu  = QMenu(self)
        names = ["Nombre", "Tamaño", "Tipo", "Fecha modificación"]
        for i, name in enumerate(names):
            if i == 0:
                continue
            act = QAction(name, self)
            act.setCheckable(True)
            act.setChecked(not hdr.isSectionHidden(i))
            act.triggered.connect(lambda checked, col=i: hdr.setSectionHidden(col, not checked))
            menu.addAction(act)
        menu.exec(hdr.mapToGlobal(pos))

    def _new_folder(self):
        ok, result = create_folder(self.current_path())
        if not ok:
            QMessageBox.warning(self, "Error", result)
        else:
            QTimer.singleShot(300, lambda: self._rename(result))

    def _new_text_file(self):
        base = os.path.join(self.current_path(), "Nuevo archivo.txt")
        path = base
        i = 1
        while os.path.exists(path):
            path = os.path.join(self.current_path(), f"Nuevo archivo ({i}).txt")
            i += 1
        try:
            open(path, "w").close()
            QTimer.singleShot(300, lambda: self._rename(path))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _multi_rename(self, paths: list[str]):
        from src.rename_dialog import RenameDialog
        dlg = RenameDialog(paths, self)
        dlg.renamed.connect(lambda _: self.refresh())
        dlg.exec()

    def _compress_selected(self, paths: list[str]):
        ok, result = compress_to_zip(paths, self.current_path())
        if ok:
            self.status_message.emit(f"Comprimido: {os.path.basename(result)}")
        else:
            QMessageBox.warning(self, "Error al comprimir", result)

    def _extract_selected(self, path: str):
        ok, result = extract_archive(path, self.current_path())
        if ok:
            self.status_message.emit(f"Extraído en: {self.current_path()}")
        else:
            QMessageBox.warning(self, "Error al extraer", result)

    def _open_with(self, path: str):
        if sys.platform == "win32":
            import subprocess
            try:
                subprocess.run(["rundll32", "shell32.dll,OpenAs_RunDLL", path],
                               check=False)
            except Exception:
                pass

    def _show_properties(self, path: str):
        from src.properties_dialog import PropertiesDialog
        dlg = PropertiesDialog(path, self)
        dlg.renamed.connect(lambda new_path: self.refresh())
        dlg.exec()

    # ── Keyboard ──────────────────────────────────────────

    def keyPressEvent(self, event):
        key = event.key()
        mod = event.modifiers()
        cb  = get_clipboard()
        paths = self.selected_paths()

        Ctrl   = Qt.KeyboardModifier.ControlModifier
        Shift  = Qt.KeyboardModifier.ShiftModifier
        Alt    = Qt.KeyboardModifier.AltModifier

        if mod == Ctrl:
            if   key == Qt.Key.Key_C and paths: cb.copy(paths)
            elif key == Qt.Key.Key_X and paths: cb.cut(paths)
            elif key == Qt.Key.Key_V:           paste_files(self.current_path(), self)
            elif key == Qt.Key.Key_A:           self._active_view().selectAll()
            elif key in (Qt.Key.Key_R, Qt.Key.Key_F5): self.refresh()
            elif key == Qt.Key.Key_Z:           self.go_back()
            else: super().keyPressEvent(event)
        elif mod == (Ctrl | Shift):
            if key == Qt.Key.Key_C:
                QApplication.clipboard().setText(
                    paths[0] if paths else self.current_path()
                )
            else:
                super().keyPressEvent(event)
        elif mod == Alt:
            if key == Qt.Key.Key_Return and paths:
                self._show_properties(paths[0])
            else:
                super().keyPressEvent(event)
        elif key == Qt.Key.Key_F2 and paths:   self._rename(paths[0])
        elif key == Qt.Key.Key_Delete and paths: self._delete(paths)
        elif key == Qt.Key.Key_Backspace:       self.go_up()
        elif key == Qt.Key.Key_F5:              self.refresh()
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            for p in paths:
                if os.path.isdir(p): self.navigate_to(p)
                else:                open_file(p)
        elif key == Qt.Key.Key_Space:
            paths = self.selected_paths()
            if paths:
                if not self._preview.isVisible():
                    self._preview.setVisible(True)
                self._preview.show_file(paths[0])
        elif key == Qt.Key.Key_Escape:
            if self._recursive_mode and self._results_panel.isVisible():
                self._stop_recursive_search()
                self._results_panel.setVisible(False)
                self._view_stack.setVisible(True)
            self._active_view().clearSelection()
            self._typeahead_buffer = ""
        else:
            # Type-ahead navigation
            char = event.text()
            if char and char.isprintable():
                self._typeahead(char)
            else:
                super().keyPressEvent(event)

    def _typeahead(self, char: str):
        self._typeahead_buffer += char.lower()
        self._typeahead_timer.start()
        buf = self._typeahead_buffer
        model = self._proxy
        root  = self._active_view().rootIndex()
        for r in range(model.rowCount(root)):
            idx  = model.index(r, 0, root)
            name = model.data(idx, Qt.ItemDataRole.DisplayRole) or ""
            if name.lower().startswith(buf):
                view = self._active_view()
                view.setCurrentIndex(idx)
                view.scrollTo(idx)
                break

    def _clear_typeahead(self):
        self._typeahead_buffer = ""

    # ── Drag & Drop ───────────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            paths = self.selected_paths()
            if paths:
                from src.widgets.quick_look import QuickLookDialog
                dlg = QuickLookDialog(paths[0], self)
                dlg.exec()
                return
        super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        dest  = self.current_path()
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        cb    = get_clipboard()
        cb.copy(paths)
        paste_files(dest, self)
        event.acceptProposedAction()
