"""Async thumbnail generation with LRU cache."""

import os
from pathlib import Path
from collections import OrderedDict
from typing import Optional

from PyQt6.QtCore import (
    Qt, QObject, QRunnable, QThreadPool, QSize, pyqtSignal, QMutex, QMutexLocker,
)
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QFont

IMAGE_EXTS = frozenset({
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".tiff", ".tif", ".ico",
})

MAX_CACHE  = 600
_POOL_SIZE = 4


class _Signals(QObject):
    ready = pyqtSignal(str, QIcon)


class _ThumbnailWorker(QRunnable):
    def __init__(self, path: str, size: QSize):
        super().__init__()
        self.path = path
        self.size = size
        self.signals = _Signals()
        self.setAutoDelete(True)

    def run(self):
        try:
            pm = QPixmap(self.path)
            if pm.isNull():
                return
            scaled = pm.scaled(
                self.size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            # Compose on a canvas with rounded rect look
            canvas = QPixmap(self.size)
            canvas.fill(Qt.GlobalColor.transparent)
            p = QPainter(canvas)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            x = (self.size.width()  - scaled.width())  // 2
            y = (self.size.height() - scaled.height()) // 2
            p.drawPixmap(x, y, scaled)
            p.end()
            self.signals.ready.emit(self.path, QIcon(canvas))
        except Exception:
            pass


class ThumbnailCache(QObject):
    """Thread-safe LRU cache for image thumbnails.

    Call `get(path)` — returns QIcon immediately if cached,
    or None and schedules background generation.
    Connect `thumbnail_ready(path)` to refresh the view.
    """

    thumbnail_ready = pyqtSignal(str)

    def __init__(self, icon_size: QSize = QSize(112, 112), parent: QObject = None):
        super().__init__(parent)
        self._size    = icon_size
        self._cache: OrderedDict[str, QIcon] = OrderedDict()
        self._pending: set[str] = set()
        self._mutex   = QMutex()
        self._pool    = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(max(_POOL_SIZE, self._pool.maxThreadCount()))

    @staticmethod
    def is_image(path: str) -> bool:
        return os.path.isfile(path) and Path(path).suffix.lower() in IMAGE_EXTS

    def get(self, path: str) -> Optional[QIcon]:
        with QMutexLocker(self._mutex):
            if path in self._cache:
                self._cache.move_to_end(path)
                return self._cache[path]
            if path not in self._pending:
                self._pending.add(path)
                self._dispatch(path)
        return None

    def invalidate(self, path: str):
        with QMutexLocker(self._mutex):
            self._cache.pop(path, None)

    def clear(self):
        with QMutexLocker(self._mutex):
            self._cache.clear()
            self._pending.clear()

    def resize(self, new_size: QSize):
        self._size = new_size
        self.clear()

    def _dispatch(self, path: str):
        worker = _ThumbnailWorker(path, self._size)
        worker.signals.ready.connect(self._on_ready)
        self._pool.start(worker)

    def _on_ready(self, path: str, icon: QIcon):
        with QMutexLocker(self._mutex):
            self._pending.discard(path)
            if len(self._cache) >= MAX_CACHE:
                self._cache.popitem(last=False)
            self._cache[path] = icon
        self.thumbnail_ready.emit(path)
