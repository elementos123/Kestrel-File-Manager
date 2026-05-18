"""Preview panel — images with zoom, text with line numbers, file info."""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QStackedWidget, QFrame, QScrollArea, QSizePolicy,
    QPushButton, QToolButton, QSlider,
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QTextCharFormat, QColor, QSyntaxHighlighter

from src.utils import is_image, is_text, format_size, format_date, get_file_icon, read_text_preview


# ── Async thumbnail loader ─────────────────────────────────

class _ImageLoader(QThread):
    loaded = pyqtSignal(QPixmap, int, int)  # pixmap, orig_w, orig_h

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            pm = QPixmap(self.path)
            if not pm.isNull():
                self.loaded.emit(pm, pm.width(), pm.height())
        except Exception:
            pass


# ── Basic syntax highlighter ──────────────────────────────

class _SyntaxHighlighter(QSyntaxHighlighter):
    """Keyword-based highlighter with expanded language support."""

    _LANGUAGES = {
        "python": (
            ["def", "class", "return", "import", "from", "if", "elif", "else",
             "for", "while", "try", "except", "finally", "with", "as", "in",
             "not", "and", "or", "is", "None", "True", "False", "pass", "break",
             "continue", "lambda", "yield", "async", "await", "raise", "del",
             "global", "nonlocal", "assert"],
            "#61afef", "#98c379", "#5c6370", "#d19a66", "#c678dd"
        ),
        "js": (
            ["function", "const", "let", "var", "return", "if", "else", "for",
             "while", "class", "new", "this", "import", "export", "from",
             "default", "async", "await", "try", "catch", "finally", "typeof",
             "instanceof", "true", "false", "null", "undefined"],
            "#61afef", "#98c379", "#5c6370", "#d19a66", "#c678dd"
        ),
        "rust": (
            ["fn", "let", "mut", "match", "impl", "trait", "struct", "enum", "pub",
             "use", "mod", "type", "where", "for", "in", "if", "else", "while",
             "loop", "return", "break", "continue", "async", "await", "dyn",
             "static", "const", "ref", "self", "Self", "crate", "super", "unsafe"],
            "#c678dd", "#98c379", "#5c6370", "#d19a66", "#61afef"
        ),
        "cpp": (
            ["int", "char", "float", "double", "void", "bool", "auto", "const",
             "static", "class", "struct", "template", "typename", "public",
             "private", "protected", "virtual", "override", "final", "new",
             "delete", "if", "else", "for", "while", "do", "switch", "case",
             "break", "continue", "return", "try", "catch", "throw", "namespace",
             "using", "include", "define"],
            "#c678dd", "#98c379", "#5c6370", "#d19a66", "#61afef"
        ),
        "go": (
            ["func", "var", "const", "type", "struct", "interface", "package",
             "import", "return", "if", "else", "for", "range", "switch", "case",
             "default", "select", "chan", "go", "defer", "map", "make", "new",
             "panic", "recover", "true", "false", "nil"],
            "#61afef", "#98c379", "#5c6370", "#d19a66", "#c678dd"
        ),
        "generic": ([], "#e5c07b", "#98c379", "#5c6370", "#d19a66", "#61afef"),
    }

    def __init__(self, doc, ext: str):
        super().__init__(doc)
        import re
        self._rules: list[tuple] = []

        profile = self._LANGUAGES.get(ext, self._LANGUAGES["generic"])
        kw_list, kw_color, str_color, cmt_color, num_color, call_color = profile

        # Keywords
        kw_fmt = QTextCharFormat()
        kw_fmt.setForeground(QColor(kw_color))
        kw_fmt.setFontWeight(700)
        for kw in kw_list:
            self._rules.append((re.compile(r"\b" + kw + r"\b"), kw_fmt))

        # Strings
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor(str_color))
        for pattern in [r'"[^"\\]*(?:\\.[^"\\]*)*"', r"'[^'\\]*(?:\\.[^'\\]*)*'"]:
            self._rules.append((re.compile(pattern), str_fmt))

        # Numbers
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor(num_color))
        self._rules.append((re.compile(r"\b\d+\.?\d*\b"), num_fmt))

        # Function calls
        call_fmt = QTextCharFormat()
        call_fmt.setForeground(QColor(call_color))
        self._rules.append((re.compile(r"\b[a-zA-Z_]\w*(?=\s*\()"), call_fmt))

        # Comments
        cmt_fmt = QTextCharFormat()
        cmt_fmt.setForeground(QColor(cmt_color))
        cmt_fmt.setFontItalic(True)
        self._rules.append((re.compile(r"#.*$"), cmt_fmt))      # Python/Shell
        self._rules.append((re.compile(r"//.*$"), cmt_fmt))     # C/JS/Rust/Go
        self._rules.append((re.compile(r"/\*.*?\*/", re.S), cmt_fmt)) # Multi-line

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# ── Image viewer with zoom controls ───────────────────────

class _ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._original: QPixmap = None
        self._zoom = 1.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background: #1a1a1a; border-bottom: 1px solid #333;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(8, 4, 8, 4)
        tl.setSpacing(4)

        def _tbtn(txt: str, tip: str) -> QToolButton:
            b = QToolButton()
            b.setText(txt)
            b.setToolTip(tip)
            b.setStyleSheet(
                "QToolButton { background: transparent; border: none; color: #aaa;"
                "font-size: 13px; padding: 3px 7px; border-radius: 4px; }"
                "QToolButton:hover { background: #333; color: white; }"
            )
            return b

        self._btn_fit  = _tbtn("⊡", "Ajustar a ventana")
        self._btn_1x   = _tbtn("1:1", "Tamaño real")
        self._btn_in   = _tbtn("+", "Ampliar")
        self._btn_out  = _tbtn("−", "Reducir")
        self._zoom_lbl = QLabel("100%")
        self._zoom_lbl.setStyleSheet("color: #666; font-size: 11px; min-width: 40px;")
        self._dim_lbl  = QLabel("")
        self._dim_lbl.setStyleSheet("color: #555; font-size: 11px;")

        self._btn_fit.clicked.connect(self._set_zoom_fit)
        self._btn_1x.clicked.connect(lambda: self._set_zoom(1.0))
        self._btn_in.clicked.connect(lambda: self._set_zoom(self._zoom * 1.25))
        self._btn_out.clicked.connect(lambda: self._set_zoom(self._zoom / 1.25))

        tl.addWidget(self._btn_fit)
        tl.addWidget(self._btn_1x)
        tl.addWidget(self._btn_out)
        tl.addWidget(self._zoom_lbl)
        tl.addWidget(self._btn_in)
        tl.addStretch()
        tl.addWidget(self._dim_lbl)
        self._exif_lbl = QLabel("")
        self._exif_lbl.setStyleSheet(
            "color: #555; font-size: 10px; padding: 0 8px;"
        )
        tl.addWidget(self._exif_lbl)
        layout.addWidget(toolbar)

        # Scroll area for image
        self._scroll = QScrollArea()
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setStyleSheet("background: #111;")
        self._img_lbl = QLabel()
        self._img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_lbl.setStyleSheet("background: transparent; padding: 8px;")
        self._scroll.setWidget(self._img_lbl)
        self._scroll.setWidgetResizable(False)
        layout.addWidget(self._scroll, 1)

    def show_image(self, pixmap: QPixmap, w: int, h: int):
        self._original = pixmap
        self._dim_lbl.setText(f"{w} × {h}")
        self._exif_lbl.setText("")
        self._set_zoom_fit()

    def set_exif_text(self, text: str):
        self._exif_lbl.setText(text)

    def _set_zoom_fit(self):
        if not self._original:
            return
        avail = self._scroll.viewport().size() - QSize(16, 16)
        scaled = self._original.scaled(
            avail,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        fit_zoom = scaled.width() / max(self._original.width(), 1)
        self._zoom = fit_zoom
        self._apply_zoom()

    def _set_zoom(self, zoom: float):
        self._zoom = max(0.05, min(zoom, 8.0))
        self._apply_zoom()

    def _apply_zoom(self):
        if not self._original:
            return
        w = int(self._original.width()  * self._zoom)
        h = int(self._original.height() * self._zoom)
        scaled = self._original.scaled(
            QSize(w, h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._img_lbl.setPixmap(scaled)
        self._img_lbl.resize(scaled.size())
        self._zoom_lbl.setText(f"{int(self._zoom * 100)}%")

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1 / 1.15
        self._set_zoom(self._zoom * factor)
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._original:
            QTimer.singleShot(50, self._set_zoom_fit)


# ── Main preview panel ────────────────────────────────────

class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewPanel")
        self.setMinimumWidth(230)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("PreviewPanel")
        header.setFixedHeight(34)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 8, 0)
        title = QLabel("VISTA PREVIA")
        title.setObjectName("PreviewTitle")
        hl.addWidget(title)
        hl.addStretch()
        root.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("border: none; background: #2d2d2d;")
        root.addWidget(sep)

        # Stack: 0=image, 1=text, 2=info, 3=empty
        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        # 0 — Image viewer
        self._image_viewer = _ImageViewer()
        self._stack.addWidget(self._image_viewer)

        # 1 — Text viewer
        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._monospace_font_name = "Consolas"
        font = QFont("Consolas", 11)
        self._text_edit.setFont(font)
        self._text_edit.setStyleSheet(
            "QTextEdit { background: #1a1a1a; color: #abb2bf;"
            "border: none; padding: 8px; }"
        )
        self._highlighter: _SyntaxHighlighter = None
        self._stack.addWidget(self._text_edit)

        # 2 — File info
        info_scroll = QScrollArea()
        info_scroll.setFrameShape(QFrame.Shape.NoFrame)
        info_scroll.setWidgetResizable(True)
        info_scroll.setStyleSheet("background: transparent;")
        self._info_widget = QWidget()
        self._info_widget.setObjectName("PreviewPanel")
        self._info_layout = QVBoxLayout(self._info_widget)
        self._info_layout.setContentsMargins(12, 12, 12, 12)
        self._info_layout.setSpacing(4)
        self._info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_scroll.setWidget(self._info_widget)
        self._stack.addWidget(info_scroll)

        # 3 — Empty state
        empty = QWidget()
        empty.setObjectName("PreviewPanel")
        el = QVBoxLayout(empty)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el_icon = QLabel("🔍")
        el_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el_icon.setStyleSheet("font-size: 32px; color: #333; padding-bottom: 8px;")
        el_lbl = QLabel("Selecciona un archivo\npara ver una vista previa")
        el_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el_lbl.setStyleSheet("color: #444; font-size: 12px; line-height: 1.5;")
        el.addWidget(el_icon)
        el.addWidget(el_lbl)
        self._stack.addWidget(empty)

        self._stack.setCurrentIndex(3)
        self._loader: _ImageLoader = None
        self._syntax_enabled = True

    # ── Public API ────────────────────────────────────────

    def set_syntax_enabled(self, enabled: bool):
        self._syntax_enabled = enabled

    def set_monospace_font(self, family: str):
        self._monospace_font_name = family
        self._text_edit.setFont(QFont(family, 11))

    def clear(self):
        self._stack.setCurrentIndex(3)

    def show_file(self, path: str):
        if not os.path.exists(path):
            self.clear()
            return
        if os.path.isdir(path):
            self._show_info(path, is_dir=True)
        elif is_image(path):
            self._show_image(path)
        elif is_text(path):
            self._show_text(path)
        else:
            self._show_info(path, is_dir=False)

    # ── Private ───────────────────────────────────────────

    def _show_image(self, path: str):
        self._stack.setCurrentIndex(0)
        if self._loader and self._loader.isRunning():
            self._loader.terminate()
        self._loader = _ImageLoader(path)
        self._loader.loaded.connect(self._on_image_loaded)
        self._loader.start()
        self._current_image_path = path

    def _on_image_loaded(self, pixmap, w: int, h: int):
        self._image_viewer.show_image(pixmap, w, h)
        self._show_image_exif(self._current_image_path, w, h)

    def _show_image_exif(self, path: str, w: int, h: int):
        """Overlay EXIF info at bottom of image panel."""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            img = Image.open(path)
            exif_raw = img._getexif() if hasattr(img, "_getexif") else None
            exif = {}
            if exif_raw:
                for tag_id, val in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(val, (str, int, float, bytes)):
                        exif[tag] = val
            parts = [f"{w}×{h}"]
            if "DateTime" in exif:
                parts.append(str(exif["DateTime"])[:16].replace(":", "/", 2).replace(":", " ", 1))
            if "Make" in exif or "Model" in exif:
                cam = f"{exif.get('Make', '')} {exif.get('Model', '')}".strip()
                if cam:
                    parts.append(cam[:30])
            if "FocalLength" in exif:
                fl = exif["FocalLength"]
                if hasattr(fl, "numerator"):
                    parts.append(f"{fl.numerator // fl.denominator}mm")
            if "ISOSpeedRatings" in exif:
                parts.append(f"ISO {exif['ISOSpeedRatings']}")
            if parts:
                self._image_viewer.set_exif_text("  ·  ".join(parts))
        except Exception:
            self._image_viewer.set_exif_text(f"{w}×{h}")

    def _show_text(self, path: str):
        content = read_text_preview(path, max_bytes=32_768)
        if content is None:
            self._show_info(path, is_dir=False)
            return
        
        ext = Path(path).suffix.lower().lstrip(".")
        
        if ext == "md":
            self._text_edit.setMarkdown(content)
            self._highlighter = None
        elif ext == "csv":
            # Simple CSV display
            self._text_edit.setPlainText(content)
            self._highlighter = None # Maybe add a specific CSV highlighter later
        else:
            self._text_edit.setPlainText(content)
            lang = {
                "py": "python", "js": "js", "ts": "js", "jsx": "js", "tsx": "js",
                "rs": "rust", "cpp": "cpp", "c": "cpp", "h": "cpp", "hpp": "cpp",
                "go": "go"
            }.get(ext, "generic")
            
            if self._syntax_enabled:
                self._highlighter = _SyntaxHighlighter(self._text_edit.document(), lang)
            else:
                self._highlighter = None
                
        self._stack.setCurrentIndex(1)

    def _show_info(self, path: str, is_dir: bool):
        # Clear old widgets
        while self._info_layout.count():
            item = self._info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        name = os.path.basename(path) or path

        # Big icon
        icon_lbl = QLabel(get_file_icon(path, is_dir))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48px; padding: 12px 0 6px 0;")
        self._info_layout.addWidget(icon_lbl)

        # Name
        name_lbl = QLabel(name)
        name_lbl.setWordWrap(True)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 600; padding: 0 8px 10px 8px;")
        self._info_layout.addWidget(name_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border: none; background: #2d2d2d;")
        sep.setFixedHeight(1)
        self._info_layout.addWidget(sep)
        self._info_layout.addSpacing(8)

        def _add_row(label: str, value: str):
            row = QWidget()
            rl  = QHBoxLayout(row)
            rl.setContentsMargins(0, 1, 0, 1)
            k = QLabel(label)
            k.setStyleSheet("color: #555; font-size: 11px; min-width: 80px;")
            k.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            v = QLabel(value)
            v.setWordWrap(True)
            v.setStyleSheet("color: #aaa; font-size: 12px; padding-left: 8px;")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            rl.addWidget(k)
            rl.addWidget(v, 1)
            self._info_layout.addWidget(row)

        try:
            st = os.stat(path)
            if is_dir:
                try:
                    items = os.listdir(path)
                    dirs  = sum(1 for i in items if os.path.isdir(os.path.join(path, i)))
                    files = len(items) - dirs
                    _add_row("Tipo",      "Carpeta")
                    _add_row("Contiene",  f"{files} archivo(s), {dirs} carpeta(s)")
                except PermissionError:
                    _add_row("Tipo", "Carpeta (sin acceso)")
            else:
                ext = Path(path).suffix.upper().lstrip(".")
                _add_row("Tipo",    f"Archivo {ext}" if ext else "Archivo")
                _add_row("Tamaño", format_size(st.st_size))

            _add_row("Modificado", format_date(st.st_mtime))
            _add_row("Creado",     format_date(st.st_ctime))
            _add_row("Ruta",       os.path.dirname(path))
        except Exception as e:
            _add_row("Error", str(e))

        self._info_layout.addStretch()
        self._stack.setCurrentIndex(2)
