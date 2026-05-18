from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtGui import QColor, QFileSystemModel
from src.thumbnail_cache import ThumbnailCache
from src.utils import format_date_relative

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

class FileProxyModel(QSortFilterProxyModel):
    def __init__(self, cache: ThumbnailCache, parent=None):
        super().__init__(parent)
        self._filter          = ""
        self._cache           = cache
        self._folders_first   = True
        self._show_extensions = True
        self._color_coding    = False
        self._date_relative   = False
        self._thumbnail_on    = True
        self._search_case     = False
        self._type_filter    = "all"
        self._cache.thumbnail_ready.connect(self._on_thumbnail_ready)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    # ── Config setters ────────────────────────────────────

    def set_folders_first(self, enabled: bool):
        self._folders_first = enabled
        self.invalidate()

    def set_show_extensions(self, enabled: bool):
        self._show_extensions = enabled
        self.invalidate()

    def set_color_coding(self, enabled: bool):
        self._color_coding = enabled
        self.invalidate()

    def set_date_relative(self, enabled: bool):
        self._date_relative = enabled
        self.invalidate()

    def set_thumbnail_enabled(self, enabled: bool):
        self._thumbnail_on = enabled
        self.invalidate()

    _TYPE_EXTS: dict[str, set] = {
        "images":   {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".heic", ".raw"},
        "video":    {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v", ".flv"},
        "audio":    {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma", ".opus"},
        "docs":     {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                     ".odt", ".ods", ".odp", ".txt", ".md", ".rst", ".rtf", ".csv"},
        "code":     {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
                     ".json", ".yaml", ".yml", ".toml", ".xml", ".go", ".rs", ".cpp",
                     ".c", ".h", ".java", ".cs", ".rb", ".php", ".sh", ".ps1", ".lua",
                     ".sql", ".r", ".kt", ".swift"},
        "archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    }

    def set_type_filter(self, category: str):
        self._type_filter = category
        self.invalidateFilter()

    def set_search_case(self, case_sensitive: bool):
        self._search_case = case_sensitive
        sens = Qt.CaseSensitivity.CaseSensitive if case_sensitive else Qt.CaseSensitivity.CaseInsensitive
        self.setFilterCaseSensitivity(sens)
        self.setSortCaseSensitivity(sens)
        self.invalidateFilter()

    # ── Filter ────────────────────────────────────────────

    def set_filter(self, text: str):
        self._filter = text.lower().strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if not isinstance(model, QFileSystemModel):
            return True
        idx  = model.index(source_row, 0, source_parent)
        name = model.fileName(idx)

        # Text filter
        if self._filter:
            match = (self._filter in name) if self._search_case else (self._filter.lower() in name.lower())
            if not match:
                return False

        # Type filter (skip dirs)
        if self._type_filter and self._type_filter != "all":
            if not model.isDir(idx):
                exts = self._TYPE_EXTS.get(self._type_filter, set())
                from pathlib import Path as _P
                if _P(name).suffix.lower() not in exts:
                    return False

        return True

    # ── Sort: folders first ───────────────────────────────

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        if self._folders_first:
            model = self.sourceModel()
            if isinstance(model, QFileSystemModel):
                l_dir = model.isDir(left)
                r_dir = model.isDir(right)
                if l_dir != r_dir:
                    return l_dir  # dirs sort before files
        return super().lessThan(left, right)

    # ── Data: thumbnail + hide extensions + color coding ──

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole and self._thumbnail_on:
            src_idx = self.mapToSource(index)
            model   = self.sourceModel()
            if isinstance(model, QFileSystemModel):
                path = model.filePath(src_idx)
                if ThumbnailCache.is_image(path):
                    icon = self._cache.get(path)
                    if icon:
                        return icon

        if role == Qt.ItemDataRole.DisplayRole and index.column() == 3 and self._date_relative:
            src_idx = self.mapToSource(index)
            model   = self.sourceModel()
            if isinstance(model, QFileSystemModel):
                fi = model.fileInfo(src_idx)
                ts = fi.lastModified().toSecsSinceEpoch()
                if ts > 0:
                    return format_date_relative(ts)

        if role == Qt.ItemDataRole.DisplayRole and index.column() == 0:
            if not self._show_extensions:
                src_idx = self.mapToSource(index)
                model   = self.sourceModel()
                if isinstance(model, QFileSystemModel) and not model.isDir(src_idx):
                    name = model.fileName(src_idx)
                    from pathlib import Path as _P
                    stem = _P(name).stem
                    if stem:  # keep ".gitignore" as-is
                        return stem

        if role == Qt.ItemDataRole.ForegroundRole and self._color_coding:
            src_idx = self.mapToSource(index)
            model   = self.sourceModel()
            if isinstance(model, QFileSystemModel) and not model.isDir(src_idx):
                path = model.filePath(src_idx)
                from pathlib import Path as _P
                color = _FILE_TYPE_COLORS.get(_P(path).suffix.lower())
                if color:
                    return QColor(color)

        return super().data(index, role)

    def _on_thumbnail_ready(self, path: str):
        model = self.sourceModel()
        if not isinstance(model, QFileSystemModel):
            return
        src_idx   = model.index(path)
        proxy_idx = self.mapFromSource(src_idx)
        if proxy_idx.isValid():
            self.dataChanged.emit(
                proxy_idx, proxy_idx,
                [Qt.ItemDataRole.DecorationRole]
            )
