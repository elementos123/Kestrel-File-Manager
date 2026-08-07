import os
from PyQt6.QtCore import QThread, pyqtSignal

from src.logger import get_logger

_log = get_logger("search_worker")


class RecursiveSearchWorker(QThread):
    found    = pyqtSignal(str, str)  # full_path, display_name
    finished = pyqtSignal(int)
    error    = pyqtSignal(str)

    MAX_RESULTS = 2_000

    def __init__(self, root: str, query: str, case_sensitive: bool = False,
                 exclude: set = None):
        super().__init__()
        self._root   = root
        self._query  = query.strip() if case_sensitive else query.strip().lower()
        self._case   = case_sensitive
        self._exclude = exclude or set()
        self._stop   = False

    def stop(self):
        self._stop = True

    def _matches(self, name: str) -> bool:
        if self._case:
            return self._query in name
        return self._query in name.lower()

    def run(self):
        count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(self._root):
                if self._stop:
                    break
                # Prune excluded directories in-place
                dirnames[:] = [d for d in dirnames if d not in self._exclude]
                for name in dirnames + filenames:
                    if self._stop:
                        break
                    if self._matches(name):
                        self.found.emit(os.path.join(dirpath, name), name)
                        count += 1
                        if count >= self.MAX_RESULTS:
                            break
                if count >= self.MAX_RESULTS:
                    break
        except Exception as e:
            _log.exception("Recursive search failed under %s", self._root)
            self.error.emit(str(e))
        self.finished.emit(count)
